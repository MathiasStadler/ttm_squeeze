#!/usr/bin/env python3
"""
Nasdaq-100 TTM Squeeze Scanner - Vollständige historische Analyse für die letzten 5 Handelstage
Erstellt ausführliche BB/KC/Squeeze-Logdateien für alle verfügbaren Nasdaq-100 ConIDs
"""

import csv
import time
import json
from datetime import datetime
from ib_insync import IB, Stock, util
import pandas as pd
import numpy as np

# ===== CONFIGURATION =====
HOST = '127.0.0.1'
PORT = 7496
CLIENT_ID = 1

# ===== CONFIGURATION =====
HOST = '127.0.0.1'
PORT = 7496
CLIENT_ID = 1

# Number of calendar days to look back - need enough for BB/KC calculation (20+ period)
HIST_DAYS = 60  # Kürzere Historie für schnellere Erkennung, immer noch ausreichend für Indikatoren
OUTPUT_FILE = f'/home/hermes/ttm_squeeze/nasdaq100_tmmsqueeze_log_{datetime.now().strftime("%Y%m%d")}.csv'

# Technical indicator parameters - AGGRESSIVE TOLERANZEN für bessere Erkennung
BB_PERIOD = 20
BB_STD = 2.5  # Erhöht für breitere Bänder und bessere Ergonomie
KC_PERIOD = 20
KC_MULTIPLIER = 2.0  # Erhöht für aggressive Squeeze-Erkennung

def calculate_true_range(high, low, close):
    """Berechnet die True Range für einen gegebenen DataFrame"""
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    return pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

def ttm_squeeze_analysis(ib, symbol, conid):
    """Führt vollständige TTM Squeeze Analyse für ein Symbol durch"""
    contract = Stock(symbol, 'SMART', 'USD')
    contract.conId = conid
    
    print(f"  Analysiere {symbol} (ConId: {conid})...")
    
    try:
        # Holt ONLY the last HIST_DAYS of daily data
        bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr=f'{HIST_DAYS} D',
            barSizeSetting='1 day',
            whatToShow='BAR',  # Changed from 'TRADES' to 'BAR' for OHLC data
            useRTH=True,
            formatDate=1,
        )
        
        if not bars:
            print(f"    Keine Daten für {symbol} gefunden")
            return None
            
        df = util.df(bars)
        
        close = df['close']
        high = df['high'] 
        low = df['low']
        
        # Bollinger Bands Berechnung
        ma = close.rolling(BB_PERIOD).mean()
        std = close.rolling(BB_PERIOD).std(ddof=0)
        bb_upper = ma + BB_STD * std
        bb_lower = ma - BB_STD * std
        
        # Keltner-Kanal Berechnung
        atr = calculate_true_range(high, low, close).rolling(KC_PERIOD).mean()
        kc_upper = ma + KC_MULTIPLIER * atr
        kc_lower = ma - KC_MULTIPLIER * atr
        
        # Aktueller Zustand (letztes verfügbares Datenpunkt)
        last_bb_u = bb_upper.iloc[-1]
        last_bb_l = bb_lower.iloc[-1]
        last_ma = ma.iloc[-1]
        last_kc_u = kc_upper.iloc[-1]
        last_kc_l = kc_lower.iloc[-1]
        last_atr = atr.iloc[-1]
        
        # Squeeze-On-Status
        squeeze_on = (last_bb_u < last_kc_u) and (last_bb_l > last_kc_l)
        
        # Analysedaten
        analysis = {
            'Symbol': symbol,
            'ConId': conid,
            'Timestamp': datetime.now().isoformat(),
            
            # BB-Daten
            'BB_Period': BB_PERIOD,
            'BB_Std': BB_STD,
            'BB_Upper': round(last_bb_u, 4),
            'BB_Middle': round(last_ma, 4),
            'BB_Lower': round(last_bb_l, 4),
            'BB_Width': round(last_bb_u - last_bb_l, 4),
            
            # Keltner-Kanal-Daten
            'KC_Period': KC_PERIOD,
            'KC_Multiplier': KC_MULTIPLIER,
            'KC_Upper': round(last_kc_u, 4),
            'KC_Middle': round(last_ma, 4),
            'KC_Lower': round(last_kc_l, 4),
            'KC_Width': round(last_kc_u - last_kc_l, 4),
            'ATR': round(last_atr, 4),
            
            # Squeeze-Berechnungen
            'Squeeze_on': squeeze_on,
            'BB_Inside_KC': squeeze_on,
            'BB_Outside_KC_Upper': (last_bb_u > last_kc_u),
            'BB_Outside_KC_Lower': (last_bb_l < last_kc_l),
            
            # Volatilität und Trend-strength
            'Volatility_index': round(std.iloc[-1], 4),
            
            # Chart-Datenpunkte (letzte HIST_DAYS) - Listenelemente gerundet
            'Recent_High': [round(x, 4) for x in high.tail(5).tolist()],
            'Recent_Low': [round(x, 4) for x in low.tail(5).tolist()],
            'Recent_Close': [round(x, 4) for x in close.tail(5).tolist()],
            
            # Momentum-Daten (5-Tage-Richtung)
            'Momentum_Value': round(close.tail(5).iloc[-1] - close.tail(5).iloc[0], 4),
            'Momentum_Direction': 'up' if close.tail(5).iloc[-1] > close.tail(5).iloc[0] else 'down'
        }
        
        return analysis
        
    except Exception as e:
        print(f"    Fehler bei {symbol}: {e}")
        return None

def main():
    print("🚀 Starte Nasdaq-100 TTM Squeeze Scanner für die letzten 5 Handelstage...")
    print(f"📅 Run am: {datetime.now()}")
    print(f"📁 Log-Datei: {OUTPUT_FILE}")
    print(f"🔢 Hist_DAYS eingestellt auf: {HIST_DAYS}")
    print(f"📊 BB_PERIOD={BB_PERIOD}, BB_STD={BB_STD}, KC_PERIOD={KC_PERIOD}, KC_MULTIPLIER={KC_MULTIPLIER}")
    
    # Lade ConID-Daten
    conids = []
    with open('/home/hermes/ttm_squeeze/nasdaq100_conids.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ConId']:  # Nur Symbole mit ConId verwenden
                conids.append({
                    'Symbol': row['Symbol'],
                    'ConId': int(row['ConId'])
                })
    
    print(f"✅ Geladene {len(conids)} ConIDs (mit Daten)")
    
    ib = IB()
    try:
        print(f"🔌 Verbinde zu {HOST}:{PORT} (Client {CLIENT_ID})...")
        ib.connect(HOST, PORT, clientId=CLIENT_ID)
        print("✅ Verbindung hergestellt!")
    except Exception as e:
        print(f"❌ Verbindung fehlgeschlagen: {e}")
        return
    
    # Initialisiere CSV-Log-Datei
    csv_headers = [
        'Symbol', 'ConId', 'Timestamp', 'BB_Upper', 'BB_Middle', 'BB_Lower',
        'BB_Width', 'KC_Upper', 'KC_Middle', 'KC_Lower', 'KC_Width', 'ATR',
        'Squeeze_on', 'BB_Inside_KC', 'BB_Outside_KC_Upper', 'BB_Outside_KC_Lower',
        'Volatility_index', 'Recent_High', 'Recent_Low', 'Recent_Close'
    ]
    
    # Zähle die Ergebnisse
    results = []
    squeeze_count = 0
    total_analyzed = 0
    
    print(f"\n🔍 Beginne Analyse von {len(conids)} Symbolen...")
    
    for i, sym_data in enumerate(conids, 1):
        if i % 10 == 0 or i == 1:
            print(f"\n📊 Fortschritt: {i}/{len(conids)} Symbole verarbeitet...")
        
        analysis = ttm_squeeze_analysis(ib, sym_data['Symbol'], sym_data['ConId'])
        
        if analysis:
            results.append(analysis)
            total_analyzed += 1
            if analysis['Squeeze_on']:
                squeeze_count += 1
                print(f"🚨 SQUEEZE ERMITTELT: {analysis['Symbol']}!")
            
        # Vermeide Rate-Limits (sanfte Verzögerung)
        if i < len(conids):
            time.sleep(0.5)
    
    ib.disconnect()
    
    # Schreibe Ergebnisse in CSV-Datei
    print(f"\n📝 Schreibe Ergebnisse in {OUTPUT_FILE}...")
    
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writeheader()
        
        for result in results:
            row = {k: result.get(k, '') for k in csv_headers}
            writer.writerow(row)
    
    # Zusammenfassungs-Statistiken
    print(f"\n📊 ANALYSIS ZUSAMMENFASSUNG")
    print("=" * 50)
    print(f"Verarbeitete Symbole: {total_analyzed}")
    print(f"Symbole mit Squeeze:  {squeeze_count}")
    print(f"Squeeze-Prozent:      {(squeeze_count/total_analyzed*100):.1f}%")
    print(f"Erfolgreiche Analysen:  {len(results)}/{len(conids)}")
    print(f"\n✅ Analyse abgeschlossen! Ergebnisse gespeichert in:")
    print(f"   {OUTPUT_FILE}")
    
    if squeeze_count > 0:
        print(f"\n🚨 AKTIVE SQUEEZE-SYMBOLE:")
        for r in results:
            if r['Squeeze_on']:
                print(f"   • {r['Symbol']} (BB_U:{r['BB_Upper']:.2f} KC_U:{r['KC_Upper']:.2f})")

if __name__ == '__main__':
    main()