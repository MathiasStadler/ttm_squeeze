#!/usr/bin/env python3
"""
Filtert Squeeze-Symbole aus der CSV-Logdatei und erstellt eine saubere Übersicht
"""

import pandas as pd
import csv
from datetime import datetime

INPUT_FILE = '/home/hermes/ttm_squeeze/nasdaq100_tmmsqueeze_log_20260709.csv'
OUTPUT_FILE = '/home/hermes/ttm_squeeze/squeeze_symbols_filtered.csv'

# Lade die Logdatei
df = pd.read_csv(INPUT_FILE)

# Filtere nur Squeeze-Symbole
squeeze_df = df[df['Squeeze_on'] == True][['Symbol', 'ConId', 'Squeeze_on', 'Momentum_Direction', 'BB_Upper', 'KC_Upper', 'BB_Lower', 'KC_Lower', 'ATR', 'Momentum_Value', 'Recent_Close']]

# Speichere als neue CSV
squeeze_df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Gefilterte Squeeze-Symbole gespeichert in: {OUTPUT_FILE}")
print(f"📊 Anzahl Squeeze-Symbole: {len(squeeze_df)}")