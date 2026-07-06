#!/usr/bin/env python3
"""Build profiles.js: a curated one-line blurb per ticker plus a live market
cap from Yahoo Finance. The STI entry gets the combined cap of all 30
constituents (USD-quoted ones converted at the current USDSGD rate).

Format: window.STI_PROFILES = { "D05.SI": {"blurb": ..., "mcap": 142e9, "cur": "SGD"}, ... }
"""
import json
import time

import yfinance as yf

BLURBS = {
    "^STI":    "Singapore's benchmark index — the 30 largest, most liquid blue chips on SGX, FTSE-run since 2008.",
    "D05.SI":  "Southeast Asia's largest bank by assets and the STI's heaviest weight; digital-forward lender.",
    "O39.SI":  "Singapore's second-largest bank; wealth arm Bank of Singapore and insurer Great Eastern.",
    "U11.SI":  "Family-steered bank with a deep ASEAN branch network — third of Singapore's banking trio.",
    "Z74.SI":  "Incumbent telco with regional associates (Airtel, Telkomsel, AIS, Globe) and Optus in Australia.",
    "S63.SI":  "Defence and engineering group spanning aerospace MRO, smart-city tech and munitions.",
    "C6L.SI":  "Flag carrier consistently rated among the world's best airlines; owns budget arm Scoot.",
    "S68.SI":  "The exchange itself — equities, derivatives, FX and commodities; Asia's largest FX futures venue.",
    "U96.SI":  "Utilities and urban solutions group pivoting from fossil power to renewables across Asia.",
    "BN4.SI":  "Asset manager and operator in infrastructure, real estate and connectivity; exited rigs in 2023.",
    "5E2.SI":  "Offshore & marine engineering giant formed from the 2023 Keppel O&M–Sembcorp Marine merger.",
    "BS6.SI":  "One of China's largest private shipbuilders; order book spans containerships to LNG carriers.",
    "S58.SI":  "Ground handling and airline catering leader; global air-cargo reach via the 2023 WFS deal.",
    "V03.SI":  "Contract manufacturer and design partner for life-science, networking and industrial tech firms.",
    "F34.SI":  "Asia's leading agribusiness — palm oil, oilseeds, sugar and packaged foods in 50+ countries.",
    "Y92.SI":  "Thailand's largest brewer and distiller (Chang beer) with an F&B footprint across Southeast Asia.",
    "G13.SI":  "Operates Resorts World Sentosa, one of Singapore's two casino integrated resorts.",
    "C52.SI":  "One of the world's largest land-transport groups: buses, rail and taxis in SG, UK and Australia.",
    "D01.SI":  "Pan-Asian retailer behind Wellcome, Guardian, 7-Eleven and Cold Storage; Jardine-controlled.",
    "J36.SI":  "185-year-old pan-Asian conglomerate: Hongkong Land, DFI Retail, Astra and JC&C sit beneath it.",
    "C07.SI":  "Jardine's Southeast Asian motor and industrials arm; controls Indonesia's Astra International.",
    "H78.SI":  "Prime commercial landlord in Hong Kong's Central district and Singapore's Marina Bay.",
    "9CI.SI":  "Global real-asset manager spun out of CapitaLand in 2021; runs the CapitaLand REIT family.",
    "C09.SI":  "Veteran Singapore developer with hotels worldwide through Millennium & Copthorne.",
    "U14.SI":  "Wee-family property group: developments, investments and Pan Pacific hotels.",
    "C38U.SI": "Singapore's largest REIT — retail and office landmarks like Raffles City and Funan.",
    "A17U.SI": "Singapore's largest industrial REIT: business parks, logistics and data centres.",
    "M44U.SI": "Pan-Asian logistics REIT under Mapletree with 180+ warehouses across nine markets.",
    "ME8U.SI": "Industrial REIT tilted toward data centres in Singapore and North America.",
    "N2IU.SI": "Owns VivoCity and Mapletree Business City plus commercial assets across Asia.",
    "J69U.SI": "Suburban mall specialist — Causeway Point, Northpoint City and other heartland centres.",
}

out = {}
total_sgd = 0.0
usdsgd = None
try:
    fx = yf.Ticker("USDSGD=X").history(period="5d")
    usdsgd = float(fx["Close"].iloc[-1])
    print(f"USDSGD = {usdsgd:.4f}")
except Exception as exc:
    print(f"FX fetch failed ({exc}); USD caps will not fold into the index total.")

for i, (sym, blurb) in enumerate(BLURBS.items(), 1):
    entry = {"blurb": blurb}
    if sym != "^STI":
        try:
            info = yf.Ticker(sym).info or {}
            mcap = info.get("marketCap")
            cur = info.get("currency") or "SGD"
            if mcap:
                entry["mcap"] = mcap
                entry["cur"] = cur
                if cur == "SGD":
                    total_sgd += mcap
                elif cur == "USD" and usdsgd:
                    total_sgd += mcap * usdsgd
            print(f"[{i:2d}/31] {sym:8s} {cur} {mcap/1e9 if mcap else 0:8.1f}b")
        except Exception as exc:
            print(f"[{i:2d}/31] {sym:8s} FAILED: {exc}")
        time.sleep(0.4)
    out[sym] = entry

if total_sgd:
    out["^STI"]["mcap"] = round(total_sgd)
    out["^STI"]["cur"] = "SGD"
    print(f"index combined cap: S${total_sgd/1e9:.0f}b")

with open("profiles.js", "w") as f:
    f.write("window.STI_PROFILES=" + json.dumps(out, separators=(",", ":")) + ";\n")
print("wrote profiles.js")
