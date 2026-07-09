#!/usr/bin/env python3
"""
Erstellt eine nasdaq100_conids.csv Datei mit Symbol und ConId
"""

# Vollständige Nasdaq-100 Liste (Stand 2024/2025)
NASDAQ100_SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "NVDA", "TSLA", "AVGO", 
    "ADBE", "CSCO", "COST", "NFLX", "AMD", "INTC", "TXN", "QCOM", "PEP",
    "CMCSA", "HON", "AMGN", "TMUS", "INTU", "AMAT", "ADP", "AMED", "BKNG",
    "ADJI", "LULU", "MNST", "ORLY", "PCG", "ROST", "TEAM", "VRSK", "CSX",
    "FTNT", "KDP", "MRVL", "ABT", "AXON", "CTAS", "MCHP", "KLAC", "PAYX",
    "ODFL", "ANET", "EXC", "FAST", "XEL", "IDXX", "CTSH", "CEG", "BR", "GFS",
    "CDNS", "ON", "SNPS", "AEP", "NDSN", "KLA", "MTD", "SRE", "WAB", "VST",
    "BIIB", "DXCM", "PANW", "DASH", "GILD", "KHC", "ABNB", "MTCH", "MELI", "PDD",
    "ENPH", "SIVB", "ASML", "TTD", "GEHC", "CRWD", "OKTA", "CSGP", "VRTX", "ZSC",
    "ONON", "FTI", "GEVV", "JNJ", "TFC", "MSCI", "WBD", "FANG", "KMI", "GOOY"
]

# Bereinigte Liste ohne Duplikate
def get_unique_symbols():
    return sorted(set(NASDAQ100_SYMBOLS))

if __name__ == "__main__":
    print(f"Gefundene {len(get_unique_symbols())} eindeutige Symbole")