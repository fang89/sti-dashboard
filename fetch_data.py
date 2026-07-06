#!/usr/bin/env python3
"""
Fetch long-range price history for the Straits Times Index and its
30 constituents from Yahoo Finance, and write a compact data.js for
the dashboard.

Output format (data.js):
    window.STI_DATA = {
      "generated": "2026-07-06",
      "series": {
        "^STI": {"name": "Straits Times Index", "d": [epoch-days...], "c": [closes...]},
        "D05.SI": {...}, ...
      }
    }

Usage:
    python3 fetch_data.py
"""

import json
import time
import datetime as dt

import yfinance as yf

TICKERS = {
    "^STI": "Straits Times Index",
    "D05.SI": "DBS Group",
    "O39.SI": "OCBC Bank",
    "U11.SI": "UOB",
    "Z74.SI": "Singtel",
    "S63.SI": "ST Engineering",
    "C6L.SI": "Singapore Airlines",
    "S68.SI": "Singapore Exchange",
    "U96.SI": "Sembcorp Industries",
    "BN4.SI": "Keppel",
    "5E2.SI": "Seatrium",
    "BS6.SI": "Yangzijiang Shipbuilding",
    "S58.SI": "SATS",
    "V03.SI": "Venture Corporation",
    "F34.SI": "Wilmar International",
    "Y92.SI": "Thai Beverage",
    "G13.SI": "Genting Singapore",
    "C52.SI": "ComfortDelGro",
    "D01.SI": "DFI Retail Group",
    "J36.SI": "Jardine Matheson",
    "C07.SI": "Jardine Cycle & Carriage",
    "H78.SI": "Hongkong Land",
    "9CI.SI": "CapitaLand Investment",
    "C09.SI": "City Developments",
    "U14.SI": "UOL Group",
    "C38U.SI": "CapitaLand Integrated Commercial Trust",
    "A17U.SI": "CapitaLand Ascendas REIT",
    "M44U.SI": "Mapletree Logistics Trust",
    "ME8U.SI": "Mapletree Industrial Trust",
    "N2IU.SI": "Mapletree Pan Asia Commercial Trust",
    "J69U.SI": "Frasers Centrepoint Trust",
}

EPOCH = dt.date(1970, 1, 1)


def fetch_one(symbol):
    tk = yf.Ticker(symbol)
    hist = tk.history(period="max", auto_adjust=False)  # raw closes, not dividend-adjusted
    if hist.empty:
        return None
    days, closes = [], []
    for ts, close in hist["Close"].items():
        if close != close:  # NaN
            continue
        days.append((ts.date() - EPOCH).days)
        closes.append(round(float(close), 4))
    return days, closes


def main():
    series = {}
    for i, (symbol, name) in enumerate(TICKERS.items(), 1):
        print(f"[{i:2d}/{len(TICKERS)}] {symbol:8s} {name} ... ", end="", flush=True)
        try:
            result = fetch_one(symbol)
        except Exception as exc:
            print(f"FAILED: {exc}")
            continue
        if not result:
            print("no data")
            continue
        days, closes = result
        first = EPOCH + dt.timedelta(days=days[0])
        last = EPOCH + dt.timedelta(days=days[-1])
        print(f"{len(days)} pts  {first} -> {last}")
        series[symbol] = {"name": name, "d": days, "c": closes}
        time.sleep(0.4)

    payload = {
        "generated": dt.date.today().isoformat(),
        "series": series,
    }
    out = json.dumps(payload, separators=(",", ":"))
    with open("data.js", "w") as f:
        f.write("window.STI_DATA=" + out + ";\n")
    print(f"\nWrote data.js ({len(out) / 1e6:.2f} MB, {len(series)} series)")


if __name__ == "__main__":
    main()
