# 🚀 TTM Squeeze Scanner - Prompt Anleitung

## 🎯 **Was das Skript macht**

Dieses vollautomatische Skript entdeckt TTM Squeeze-Muster in NASDAQ-100 Aktien und liefert detaillierte Analyse für Handelsentscheidungen.

**Hauptfunktionen:**
- 🔄 Lädt historische Daten (250 Tage für vollständige Indikatoren)
- 📊 Führt Bollinger Bands (20 periode, 2.5 std) durch
- 🌊 Führt Keltner Kanäle durch (20 periode, 2.0 Multiplikator)
- 🔍 Identifiziert TTM Squeeze (BB < KC)
- 📈 Berücksichtigt Momentum (5-Tage-Richtung)
- 📄 Exportiert vollständige Ergebnisse und gefilterte Squeeze-Symbole

---

## 📖 **Schnellstart-Anleitung**

```bash
# TTM Squeeze Scanner starten
python nasdaq100_tmmsqueeze_scanner.py
```

**Ergebnis:**
- `nasdaq100_tmmsqueeze_log_YYYYMMDD.csv` (vollständige Analyse)
- `squeeze_symbols_filtered.csv` (nur Squeeze-Symbole)

---

## ⚙️ **Skript-Funktion-Übersicht**

| Funktion | Befehl | Ergebnis |
|----------|---------|----------|
| **Full Scan** | `python nasdaq100_tmmsqueeze_scanner.py` | Alle NASDAQ-100-Aktien analysiert |
| **Alle Squeezes filtern** | `awk -F',' 'NR>1 && $13=="True"' squeeze_symbols_filtered.csv` | Nur Squeeze-Symbole |
| **Bullische Squeezes** | `awk -F',' 'NR>1 && $4=="up" {print $1,$13}' squeeze_symbols_filtered.csv` | Nur bullische Momentum-Squeeese |
| **Cone-High-Momentum** | `awk -F',' 'NR>1 && $11>50 {print $1,$11}' squeeze_symbols_filtered.csv` | Hohe Momentum-Werte |

---

## 📊 **Parameter-Erklärung**

```python
# Die Technologie hinter den Indikatoren

BB_PERIOD = 20                     # Bollinger Bands Periode (20 Kerzen)
BB_STD = 2.5                      # Standardabweichung (breitere Bänder = mehr Signale)
KC_PERIOD = 20                     # Keltner Periode (20 Kerzen)
KC_MULTIPLIER = 2.0               # Keltner Multiplikator (höher = aggressiver)
HIST_DAYS = 250                   # Benötigte Historie (min. 20 für Indikatoren)
```

**Indikator-Formeln:**
- **BB Upper**: MA + (BB_STD × STD)
- **BB Lower**: MA - (BB_STD × STD)
- **KC Upper**: MA + (KC_MULTIPLIER × ATR)
- **KC Lower**: MA - (KC_MULTIPLIER × ATR)

**Squeeze-Bedingung:** `BB_Outside_KC_Upper AND BB_Outside_KC_Lower`

---

## 🏷️ **Einkunftsoption der Spaltenbezeichnung**

| Spalte | Bedeutung | Beispiel |
|---------|----------|----------|
| `Symbol` | Aktien-Ticker | `AAPL` |
| `ConId` | Interactive Brokers ID | `265598` |
| `Squeeze_on` | Squeeze-Signal wahr/falsch | `True` |
| `Momentum_Direction` | Preis-Richtung (last 5 Tage) | `up/down` |
| `BB_Upper` | Bollinger Bands Maximum | `323.18` |
| `KC_Upper` | Keltner Maximum | `313.63` |
| `Momentum_Value` | Änderung der letzten 5 Tage | `+28.05` |

---

## 🎯 **Aktion-Strategie-Matrix**

| Situation | Signal | Aktion |
|-----------|--------|--------|
| **Strong Bullish** | `up` + `High Momentum` + `Squeeze` | 🚀 **Kaufe** |
| **Weak Bullish** | `up` + Niedriges Momentum + `Squeeze` | ⚖️ **Halten/Abwarten** |
| **Strong Bearish** | `down` + `High Momentum` + `Squeeze` | 📉 **Verkaufe** |
| **Weak Bearish** | `down` + Niedriges Momentum + `Squeeze` | ⚖️ **Beobachten** |
| **Kein Momentum** | `squeeze = False` | ⏳ **Warten** |

---

## 📈 **Wie man den Handel durchführt**

### 1. Entry-Level
```bash
# Zeigt Top-5 bullische Squeezes
awk -F',' 'NR>1 && $4=="up" {print $1,$11,$13,$15}' squeeze_symbols_filtered.csv | sort -k4nr | head -5
```

### 2. Risk-Management
```bash
# Zeigt Top-5 bearische Squeezes (Exit-Signale)
awk -F',' 'NR>1 && $4=="down" {print $1,$11,$13,$15}' squeeze_symbols_filtered.csv | sort -k4nr | head -5
```

### 3. Scan-Häufigkeit
```bash
# Einmal täglich (18:00 UTC)
0 18 * * 1-5 /path/to/nasdaq100_tmmsqueeze_scanner.py
```

---

## 🛠️ **Script-Anpassungen**

```python
# Parameter in nasdaq100_tmmsqueeze_scanner.py:
# (Bearbeiten Sie diese Variablen für Ihre Strategie)

# ❌ Für konservativere Signale:
# BB_STD = 3.0
# KC_MULTIPLIER = 1.5

# ⚡ Für aggressivere Signale:
# BB_STD = 2.0  # Engere Bänder = weniger Signale
# KC_MULTIPLIER = 2.5  # Höheres Multiplikator = mehr Signale

# 🔄 Für schnellere Scans:
# HIST_DAYS = 60  # Weniger historische Daten (shorter)
```

---

## 📊 **Interpretation eines Squeeze-Symbols**

```bash
# Single-Symbol-Analyse
# Beispielzeile für AMD:
AMD,4391,True,up,591.00,601.14,460.27,450.13,37.754,28.05
```

**Was bedeutet das?**
- ✅ **Squeeze aktiv**: BB (591→460) liegen innerhalb KC (601→450)
- 📈 **Bullisches Momentum**: +28.05 (letzte 5 Tage)
- 🎯 **Handelsentscheidung**: Kaufen / Long-Position eröffnen

---

## 🔍 **Fehlerbehebung**

### Problem: "Keine Daten gefunden"
**Lösung:** Verwenden Sie längere `HIST_DAYS` oder überprüfen Sie ConIDs

### Problem: "Bitte wartete auf Verbindung"
**Lösung:** Stellen Sie sicher, dass TWS läuft und API aktiviert ist

### Problem: "Squeeze nicht gefunden"
**Lösung:** Passen Sie `BB_STD` oder `KC_MULTIPLIER` an

---

## 📊 **Aktuelle Scan-Ergebnisse**

| **#** | **Symbol** | **Squeeze** | **Momentum** | **BB_Upper** | **KC_Upper** | **Momentum** |
|-------|------------|------------|--------------|--------------|--------------|--------------|
| 1 | **AMD** | ✅ | 📈 up | 591.00 | 601.14 | +28.05 |
| 2 | **AMZN** | ✅ | 📈 up | 252.69 | 255.66 | +1.48 |
| 3 | **ANET** | ✅ | 📈 up | 185.76 | 185.77 | +24.61 |
| ... | ... | 🔲 | ⏳ | ... | ... | ... |

**Statistik:** 23/90 Squeeze-Symbole (25,6%)

---

## 🌐 **Web-Oberfläche Integration**

```python
# Wenn Sie eine Web-Oberfläche benötigen:
# 1. Verwenden Sie FastAPI/Flask
# 2. Fügen Sie Endpoints hinzu:
#    - /scan - Startet manuellen Scan
#    - /results - Gibt JSON-Squeeze-Ergebnisse zurück
#    - /health - Gesundheitsprüfung des Systems
# 3. CORS für Frontend-Zugriff zulassen
```

---

## 📈 **Geschwindigkeits-Optimierung**

```bash
# Serielle Ausführung vs. parallele Ausführung
# Aktuell serielle (0.5s Verzögerung zwischen Symbolen) → Stabil
# Für Batch-Beschleunigung:
# macOS/Windows: 
#   nice -n 19 python nasdaq100_tmmsqueeze_scanner.py
# Linux:
#   taskset -c 0-7 python nasdaq100_tmmsqueeze_scanner.py
```

---

## 📍 **Letzte Aktualisierung**

**2026-07-09 20:20:10 UTC**

**Version:** 1.0.0
**Features:** 250-Tage-Historie, Momentum-Erkennung, vollständige Analyse

---

## 🎯 **Hauptbefehle für den Erfolg**

```bash
# 1. Initialer Setup
./setup.sh

# 2. Täglichen Scan starten
./run_daily_scan.sh

# 3. Squeeze-Symbole überprüfen
./show_active_squeezes.sh

# 4. Trading-Einstelldateien überprüfen
./check_config.sh

# 5. Überwachung des Systems
top -i
```

---

**Bereit für den Handel? 🚀**

```bash
# Starten Sie Ihren TTM Squeeze Scanner:
source venv/bin/activate
python nasdaq100_tmmsqueeze_scanner.py
```

> **Tipp:** Lassen Sie den Scan einmal täglich laufen und beobachten Sie die Squeeze-Aktivität!
> **Code-Snippet für Bull Squeezes:**
```bash
awk -F',' 'NR>1 && $4=="up" {print "BUY:", $1, "Momentum:", $11}' squeeze_symbols_filtered.csv
```