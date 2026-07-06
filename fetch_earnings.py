#!/usr/bin/env python3
"""Fetch historical earnings dates (with EPS estimate vs reported) for all
STI constituents from Yahoo Finance and write earnings.js.

Format: window.STI_EARNINGS = { "D05.SI": [[epochDay, est, actual, surprisePct], ...], ... }
Past releases only; entries sorted ascending.
"""
import datetime as dt
import json
import math
import time

import yfinance as yf

from fetch_data import TICKERS

EPOCH = dt.date(1970, 1, 1)
today = dt.date.today()

def clean(v):
    try:
        f = float(v)
        return None if math.isnan(f) else round(f, 4)
    except (TypeError, ValueError):
        return None

out = {}
for i, sym in enumerate([t for t in TICKERS if t != "^STI"], 1):
    print(f"[{i:2d}/30] {sym:8s} ... ", end="", flush=True)
    try:
        df = yf.Ticker(sym).get_earnings_dates(limit=80)
    except Exception as exc:
        print(f"FAILED: {exc}")
        continue
    rows = []
    if df is not None:
        for ts, row in df.iterrows():
            d = ts.date()
            if d >= today:
                continue  # skip scheduled/upcoming
            rows.append([(d - EPOCH).days,
                         clean(row.get("EPS Estimate")),
                         clean(row.get("Reported EPS")),
                         clean(row.get("Surprise(%)"))])
    rows.sort()
    # dedupe same-day rows (Yahoo sometimes doubles them)
    dedup = {r[0]: r for r in rows}
    out[sym] = list(dedup.values())
    print(f"{len(out[sym])} releases")
    time.sleep(0.4)

with open("earnings.js", "w") as f:
    f.write("window.STI_EARNINGS=" + json.dumps(out, separators=(",", ":")) + ";\n")
print(f"wrote earnings.js ({sum(len(v) for v in out.values())} releases)")
