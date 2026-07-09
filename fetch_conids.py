#!/usr/bin/env python3
"""
Erstellt nasdaq100_conids.csv indem es ConIds von IBKR/TWS abruft
"""

import csv
import sys
import time
from ib_insync import IB, Stock, util

# Symbole laden
sys.path.insert(0, '/home/hermes/ttm_squeeze')
from nasdaq100_symbols import get_unique_symbols

SYMBOLS = get_unique_symbols()
HOST = '127.0.0.1'
PORT = 7496
CLIENT_ID = 1
OUTPUT_FILE = '/home/hermes/ttm_squeeze/nasdaq100_conids.csv'

def fetch_conids():
    ib = IB()
    try:
        print(f"Verbinde zu TWS/Gateway auf {HOST}:{PORT}...")
        ib.connect(HOST, PORT, clientId=CLIENT_ID)
        print("Verbunden!")
    except Exception as e:
        print(f"FEHLER: Verbindung fehlgeschlagen: {e}")
        return False

    results = []
    
    for i, sym in enumerate(SYMBOLS, 1):
        print(f"[{i}/{len(SYMBOLS)}] Hole ConId für {sym}...")
        contract = Stock(sym, 'SMART', 'USD')
        try:
            # Contract qualifizieren um ConId zu erhalten
            qualified = ib.qualifyContracts(contract)
            if qualified and qualified[0].conId:
                conid = qualified[0].conId
                results.append({'Symbol': sym, 'ConId': conid})
                print(f"  -> {sym}: ConId = {conid}")
            else:
                print(f"  -> {sym}: NICHT GEFUNDEN")
                results.append({'Symbol': sym, 'ConId': ''})
        except Exception as e:
            print(f"  -> {sym}: FEHLER - {e}")
            results.append({'Symbol': sym, 'ConId': ''})
        
        # Small delay to not hammer the API
        time.sleep(0.1)
    
    ib.disconnect()
    
    # CSV schreiben
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Symbol', 'ConId'])
        writer.writeheader()
        writer.writerows(results)
    
    found = sum(1 for r in results if r['ConId'])
    print(f"\nFertig! {found}/{len(results)} ConIds gefunden.")
    print(f"Datei gespeichert: {OUTPUT_FILE}")
    return True

if __name__ == '__main__':
    fetch_conids()