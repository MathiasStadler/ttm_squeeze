#!/usr/bin/env python3
"""
TTM Squeeze Scanner fuer TWS / IBKR (Lynx)
Berechnet den TTM Squeeze (Bollinger Bands vs. Keltner Channels)
fuer eine Liste von Ticker-Symbolen ueber die IBKR API (ib_insync).

Voraussetzungen:
  - TWS oder IBKR Gateway laeuft mit aktivierter API (Socket Clients erlaubt)
  - Verbindung auf Port 7497 (TWS Live) / 7496 (Paper) bzw. Gateway 4001/4002

Nutzung:
  source ~/ttm_squeeze/venv/bin/activate
  python ttm_squeeze_scanner.py
"""

import sys
import pandas as pd
import numpy as np
from ib_insync import IB, Stock, util

# --- Konfiguration ---------------------------------------------------------
HOST = '127.0.0.1'
PORT = 7496          # Paper‑TWS; Gateway = 4001/4002
CLIENT_ID = 1

# Symbole, die geprueft werden sollen
SYMBOLS = ['SPY', 'QQQ', 'AAPL', 'TSLA', 'NVDA']

BB_PERIOD = 20
BB_STD = 2.0
KC_PERIOD = 20
KC_MULT = 1.5
HIST_DAYS = 300      # genug Tage fuer stabile BB/KC-Werte
# ---------------------------------------------------------------------------


def true_range(high, low, close):
    """Echte Range (ATR-Berechnung) als pandas-Series."""
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr


def ttm_squeeze(ib, symbol):
    contract = Stock(symbol, 'SMART', 'USD')
    bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr=f'{HIST_DAYS} D',
        barSizeSetting='1 day',
        whatToShow='TRADES',
        useRTH=True,
        formatDate=1,
    )
    if not bars or len(bars) < max(BB_PERIOD, KC_PERIOD) + 1:
        return None

    df = util.df(bars)
    close = df['close']
    high = df['high']
    low = df['low']

    # Bollinger Bands
    ma = close.rolling(BB_PERIOD).mean()
    std = close.rolling(BB_PERIOD).std(ddof=0)
    bb_upper = ma + BB_STD * std
    bb_lower = ma - BB_STD * std

    # Keltner Channels (SMA +/- Multiplikator * ATR)
    atr = true_range(high, low, close).rolling(KC_PERIOD).mean()
    kc_upper = ma + KC_MULT * atr
    kc_lower = ma - KC_MULT * atr

    # Squeeze-On: BB liegen komplett innerhalb der KC
    last_bb_u = bb_upper.iloc[-1]
    last_bb_l = bb_lower.iloc[-1]
    last_kc_u = kc_upper.iloc[-1]
    last_kc_l = kc_lower.iloc[-1]

    squeeze_on = (last_bb_u < last_kc_u) and (last_bb_l > last_kc_l)
    return squeeze_on


def main():
    ib = IB()
    try:
        ib.connect(HOST, PORT, clientId=CLIENT_ID)
    except Exception as e:
        print(f"FEHLER: Verbindung zu TWS/Gateway auf {HOST}:{PORT} fehlgeschlagen: {e}")
        print("Bitte TWS/IBKR Gateway starten und API-Socket-Clients erlaubt.")
        sys.exit(1)

    print(f"Verbunden. Pruefe {len(SYMBOLS)} Symbole auf TTM Squeeze...\n")
    for sym in SYMBOLS:
        try:
            result = ttm_squeeze(ib, sym)
        except Exception as e:
            print(f"{sym:6} -> Fehler: {e}")
            continue
        if result is None:
            print(f"{sym:6} -> nicht genug Daten")
        elif result:
            print(f"{sym:6} -> SQUEEZE AKTIV")
        else:
            print(f"{sym:6} -> kein Squeeze")
    ib.disconnect()


if __name__ == '__main__':
    main()
