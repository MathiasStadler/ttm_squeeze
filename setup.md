# 🚀 TTM Squeeze Scanner - Setup-Anleitung

## 📋 Überblick
Diese Anleitung führt Sie durch die komplette Einrichtung des TTM Squeeze Scanners für NASDAQ-100 Aktien.

---

## 🔧 1. Systemvoraussetzungen

### Python 3.11 (verwendet auf Raspberry Pi 4)
```bash
# Prüfen der Python-Version
python3 --version
# Erwartet: Python 3.11.x

# Virtuelle Umgebung erstellen
cd ~/ttm_squeeze
python3 -m venv venv
source venv/bin/activate

# Benötigte Pakete installieren
pip install ib_insync pandas numpy
```

---

## 🏦 2. TWS (Trader Workstation) starten

### Paper Trading (Testumgebung)
```bash
# Starten der Paper TWS
ib-tws-paper &

# Oder manuell:
# - Öffnen Sie das TWS (Trader Workstation)
# - Wählen Sie "Paper Trading" beim Start
# - Melden Sie sich mit Ihren IBKR-Zugangsdaten an
```

### Live Trading (echter Handel)
```bash
# Starten der Live TWS
ib-tws &
# - Wählen Sie "Live Trading" beim Start
```

---

## ⚙️ 3. API Konfiguration in TWS

### Schritt-für-Schritt Anleitung:
1. **TWS öffnen und verbinden**
2. **Menü: Edit → Global Configuration**
3. **Links: API → Settings**
4. **Setzen Sie folgende Einstellungen:**
   - ✅ **Enable ActiveX and Socket Clients** (MUSS aktiviert sein!)
   - ✅ **Download Open Orders on Connection**
   - ✅ **Allow Connections from Localhost Only**
   - Port: **7496** (Paper Trading) oder **7497** (Live Trading)

5. **Apply → OK klicken**

---

## 🔌 4. API-Verbindung testen

### Schnelles Verbindungstest-Skript:
```python
# test_connection.py
from ib_insync import IB

ib = IB()
try:
    ib.connect('127.0.0.1', 7496, clientId=1)
    print("✅ Erfolgreich mit TWS verbunden!")
    ib.disconnect()
except Exception as e:
    print(f"❌ Verbindungsfehler: {e}")
```

```bash
# Testen mit:
python test_connection.py
```

---

## 📊 5. ConID-Abruf durchführen

### Vollständige NASDAQ-100 ConIDs abrufen:
```bash
# ConIDs ermitteln (einmalig durchführen)
python fetch_conids.py

# Ergebnis: nasdaq100_conids.csv
# Enthält: Symbol,ConId
# Beispiel: AMD,4391
```

### Hinweis:
- Es werden 90 von 95 Symbolen gefunden (einige sind nicht handelbar)
- Die CSV-Datei wird im selben Verzeichnis abgelegt

---

## 🎯 6. TTM Squeeze Scanner starten

### Einzelner Scan:
```bash
# Scanner starten
python nasdaq100_tmmsqueeze_scanner.py

# Ergebnis:
# - nasdaq100_tmmsqueeze_log_YYYYMMDD.csv (vollständige Daten)
# - squeeze_symbols_filtered.csv (nur Squeeze-Signale)
```

### Parameter-Einstellungen (anpassbar):
```python
HIST_DAYS = 250        # Historie-Tage (250 für vollständige Indikatoren)
BB_PERIOD = 20         # Bollinger Bands Periode
BB_STD = 2.5         # Bollinger Bands Standardabweichung
KC_PERIOD = 20         # Keltner Kanäle Periode
KC_MULTIPLIER = 2.0    # Keltner Multiplier (aggressiver = mehr Signale)
```

---

## 📈 7. Ergebnis-Interpretation

### Squeeze-Signale:
- **Squeeze_on = True**: BB liegen innerhalb KC → Squeeze aktiv
- **Momentum_Direction = up**: Kaufsignal (bullish)
- **Momentum_Direction = down**: Verkaufssignal (bearish)

### Beispiel-Ausgabe:
```csv
Symbol,ConId,Squeeze_on,Momentum_Direction,BB_Upper,KC_Upper,Momentum_Value
AMD,4391,True,up,591.00,601.14,+28.05
```

---

## ⏰ 8. Automatischer Tages-Scan (Cron)

### Cron-Job einrichten:
```bash
# Crontab öffnen
crontab -e

# Fügen Sie hinzu (täglich um 18:00 Uhr):
0 18 * * 1-5 /home/hermes/ttm_squeeze/venv/bin/python /home/hermes/ttm_squeeze/nasdaq100_tmmsqueeze_scanner.py >> /home/hermes/ttm_squeeze/cron.log 2>&1
```

---

## ⚡ 9. Häufige Probleme & Lösungen

### Problem: "Verbindung fehlgeschlagen"
```bash
# Lösung:
# 1. TWS muss laufen
# 2. API mus ze aktiviert sein (siehe Schritt 3)
# 3. Port 7496/7497 offen sein
```

### Problem: "type list doesn't define __round__ method"
```bash
# Lösung: Im Skript wurden Listen korrekt gerundet:
[round(x, 4) for x in high.tail(5).tolist()]
```

### Problem: "No security definition found"
```bash
# Lösung:
# - Symbol existiert nicht oder ist nicht handelbar
# - ConID-Liste ggf. aktualisieren
```

### Problem: NaN-Werte in Indikatoren
```bash
# Lösung:
# - HIST_DAYS erhöhen (min. 20 Tage für BB/KC)
# - Aktuell: HIST_DAYS = 250 (empfohlen)
```

---

## 📁 10. Dateistruktur

```
/home/hermes/ttm_squeeze/
├── venv/                          # Virtuelle Umgebung
├── nasdaq100_conids.csv          # ConID-Liste (einmalig erstellt)
├── nasdaq100_tmmsqueeze_scanner.py # Haupt-Scanner
├── nasdaq100_tmmsqueeze_log_*.csv  # Vollständige Scan-Ergebnisse
├── squeeze_symbols_filtered.csv    # Gefilterte Squeeze-Signale
├── fetch_conids.py               # ConID-Abruf-Skript
└── ttm_squeeze_scanner.py        # Einstiegspunkt
```

---

## ✅ 11. Schnellstart-Befehle

```bash
# 1. Terminal öffnen
cd ~/ttm_squeeze

# 2. Virtuelle Umgebung aktivieren
source venv/bin/activate

# 3. Verbindung testen (optional)
python test_connection.py

# 4. Scan starten
python nasdaq100_tmmsqueeze_scanner.py

# 5. Squeeze-Symbole anzeigen
cat squeeze_symbols_filtered.csv | column -t -s','
```

---

## 📊 12. Letzte Scan-Ergebnisse

| Metrik | Wert |
|--------|------|
| Durchsuchte Symbole | 90 |
| Squeeze-Signale | 23 (25,6%) |
| Bullische Squeezes (up) | 14 |
| Bearische Squeezes (down) | 9 |

---

## 🎯 Tipp für den Handel

Filteren Sie nach **bullischen Squeezen mit starkem Momentum**:
```bash
# Top-Squeeze-Kandidaten mit Momentum > 10
awk -F',' 'NR>1 && $4=="up" && $11>10 {print $1,$11}' /home/hermes/ttm_squeeze/squeeze_symbols_filtered.csv
```

---

**Viel Erfolg beim Squeeze-Trading!** 🚀