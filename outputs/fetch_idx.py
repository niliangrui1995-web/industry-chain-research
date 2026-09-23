# -*- coding: utf-8 -*-
"""Batch-fetch index daily kline chunks via neodata query.py"""
import os, subprocess, sys, json, time

PY = r"C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe"
Q = r"C:\Users\Administrator\.workbuddy\plugins\cache\cb_teams_marketplace\finance-data\1.6.0\skills\neodata-financial-search\scripts\query.py"
T = "tk_fRQvBxVLKX3f9y7SU1kDmsEdV2C4sch5"
OUT = r"D:\vcp_hunter\产业链投研\outputs\idx_raw"
os.makedirs(OUT, exist_ok=True)

IDX = [
    ("上证指数", "000001.SH", "sh", True),
    ("创业板指", "399006.SZ", "cyb", True),
    ("科创50", "000688.SH", "kc", True),
    ("沪深300", "000300.SH", "hs300", False),
    ("深证成指", "399001.SZ", "szcz", False),
]
CHUNKS = [
    ("A", "2026-06-22至2026-07-01"),
    ("B", "2026-07-02至2026-07-13"),
    ("C", "2026-07-14至2026-07-23"),
    ("D", "2026-07-24至2026-08-04"),
    ("E", "2026-08-05至2026-08-14"),
    ("F", "2026-08-17至2026-08-26"),
    ("G", "2026-08-27至2026-09-07"),
    ("H", "2026-09-08至2026-09-11"),
    ("I", "2026-09-14至2026-09-18"),
]

for name, code, short, full in IDX:
    for key, rng in CHUNKS:
        if not full and key in ("A", "B", "C", "D"):
            continue
        f = os.path.join(OUT, "%s_%s.json" % (short, key))
        if os.path.exists(f) and os.path.getsize(f) > 200:
            print("skip", short, key)
            continue
        query = "%s %s %s 日线行情 开盘价 收盘价 最高价 最低价 成交额" % (name, code, rng)
        for attempt in range(2):
            r = subprocess.run([PY, Q, "--query", query, "--token", T],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
            if r.returncode == 0 and len(r.stdout) > 200:
                with open(f, "w", encoding="utf-8") as fh:
                    fh.write(r.stdout)
                print("done", short, key, len(r.stdout))
                break
            time.sleep(2)
        else:
            print("FAIL", short, key)
print("ALL_DONE")
