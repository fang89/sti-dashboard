#!/usr/bin/env python3
"""Fetch comparison benchmark history (S&P 500, Nasdaq, Hang Seng, Nikkei,
Bitcoin, Gold) and write benchmarks.js in the same compact format as data.js.
History is clamped to the STI's start (1987-12-28) to keep the file small.

Usage:
    python3 fetch_benchmarks.py
"""
import json
import time
import datetime as dt

import yfinance as yf

BENCHMARKS = {
    "^GSPC":   "S&P 500",
    "^IXIC":   "Nasdaq",
    "^HSI":    "Hang Seng",
    "^N225":   "Nikkei 225",
    "BTC-USD": "Bitcoin",
    "GC=F":    "Gold",
}

EPOCH = dt.date(1970, 1, 1)
STI_START = (dt.date(1987, 12, 28) - EPOCH).days


def fetch_one(symbol):
    hist = yf.Ticker(symbol).history(period="max", auto_adjust=False)
    if hist.empty:
        return None
    days, closes = [], []
    for ts, close in hist["Close"].items():
        if close != close:  # NaN
            continue
        day = (ts.date() - EPOCH).days
        if day < STI_START:
            continue
        days.append(day)
        closes.append(round(float(close), 4))
    return days, closes


def main():
    series = {}
    for i, (symbol, name) in enumerate(BENCHMARKS.items(), 1):
        print(f"[{i}/{len(BENCHMARKS)}] {symbol:8s} {name} ... ", end="", flush=True)
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

    payload = {"generated": dt.date.today().isoformat(), "series": series}
    out = json.dumps(payload, separators=(",", ":"))
    with open("benchmarks.js", "w") as f:
        f.write("window.STI_BENCH=" + out + ";\n")
    print(f"\nWrote benchmarks.js ({len(out) / 1e6:.2f} MB, {len(series)} series)")


if __name__ == "__main__":
    main()
