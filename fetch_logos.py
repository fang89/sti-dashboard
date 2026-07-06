#!/usr/bin/env python3
"""Fetch company favicons and embed them as data URIs in logos.js."""
import base64
import json
import time

import requests

DOMAINS = {
    "D05.SI": "dbs.com", "O39.SI": "ocbc.com", "U11.SI": "uobgroup.com",
    "Z74.SI": "singtel.com", "S63.SI": "stengg.com", "C6L.SI": "singaporeair.com",
    "S68.SI": "sgx.com", "U96.SI": "sembcorp.com", "BN4.SI": "keppel.com",
    "5E2.SI": "seatrium.com", "BS6.SI": "yzjship.com", "S58.SI": "sats.com.sg",
    "V03.SI": "venture.com.sg", "F34.SI": "wilmar-international.com",
    "Y92.SI": "thaibev.com", "G13.SI": "gentingsingapore.com",
    "C52.SI": "comfortdelgro.com", "D01.SI": "dfiretailgroup.com",
    "J36.SI": "jardines.com", "C07.SI": "jcclgroup.com", "H78.SI": "hongkongland.com",
    "9CI.SI": "capitaland.com", "C09.SI": "cdl.com.sg", "U14.SI": "uol.com.sg",
    "C38U.SI": "cict.com.sg", "A17U.SI": "capitaland.com",
    "M44U.SI": "mapletree.com.sg", "ME8U.SI": "mapletree.com.sg",
    "N2IU.SI": "mpact.com.sg", "J69U.SI": "frasersproperty.com",
}

out, cache = {}, {}
for sym, dom in DOMAINS.items():
    if dom not in cache:
        sources = [
            (f"https://www.google.com/s2/favicons?domain={dom}&sz=64", "image/png"),
            (f"https://icons.duckduckgo.com/ip3/{dom}.ico", "image/x-icon"),
        ]
        cache[dom] = None
        for url, mime in sources:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            if r.ok and len(r.content) > 100:
                cache[dom] = f"data:{mime};base64," + base64.b64encode(r.content).decode()
                break
        print(f"{dom:28s} {len(r.content):6d} bytes {'ok' if cache[dom] else 'SKIP'}")
        time.sleep(0.3)
    if cache[dom]:
        out[sym] = cache[dom]

with open("logos.js", "w") as f:
    f.write("window.STI_LOGOS=" + json.dumps(out, separators=(",", ":")) + ";\n")
print(f"wrote logos.js: {len(out)} logos, {sum(len(v) for v in out.values())/1024:.0f} KB")
