# -*- coding: utf-8 -*-
"""Parse 144-stock intraday scan md -> breadth stats"""
import re, json, io, sys

md = open(r"D:\vcp_hunter\产业链投研\deliverables\block-scan\technical_scan_20260921_intraday.md", encoding="utf-8").read()

rows = re.findall(r"^\|\s*(SH|SZ|BJ)\d+\s*\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|\s*$", md, re.M)
stats = {"total": len(rows), "up": 0, "down": 0, "chg": [], "trend": {}, "strength": {},
         "rsi": [], "j": [], "score": [], "overbought_rsi": 0, "j_over100": 0,
         "breakout": 0, "breakdown": 0, "newhigh": 0, "vol_up_healthy": 0, "vol_down_warn": 0}
for m in re.finditer(r"^\|\s*(?:SH|SZ|BJ)(\d+)\s*\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|", md, re.M):
    code, name, price, chg, trend, strength, score, diag = [x.strip() for x in m.groups()]
    mchg = re.search(r"([+-]?\d+\.?\d*)%", chg)
    if not mchg:
        continue
    chgv = float(mchg.group(1))
    stats["chg"].append(chgv)
    if chgv > 0: stats["up"] += 1
    elif chgv < 0: stats["down"] += 1
    t = trend.split("(")[0]
    stats["trend"][t] = stats["trend"].get(t, 0) + 1
    stats["strength"][strength] = stats["strength"].get(strength, 0) + 1
    stats["score"].append(float(score))
    r = re.search(r"RSI(\d+\.?\d*)", diag)
    if r: 
        rv = float(r.group(1)); stats["rsi"].append(rv)
        if rv > 70: stats["overbought_rsi"] += 1
    j = re.search(r"J(-?\d+\.?\d*)", diag)
    if j:
        jv = float(j.group(1)); stats["j"].append(jv)
        if jv > 100: stats["j_over100"] += 1
    if "突破压力" in trend: stats["breakout"] += 1
    if "破支" in trend: stats["breakdown"] += 1
    if "新高" in trend: stats["newhigh"] += 1
    if "放量上涨(健康)" in diag: stats["vol_up_healthy"] += 1
    if "放量下跌(警示)" in diag: stats["vol_down_warn"] += 1

n = stats["total"]
out = {
    "total": n,
    "up": stats["up"], "down": stats["down"], "flat": n - stats["up"] - stats["down"],
    "up_ratio": round(stats["up"]/n, 3),
    "avg_chg": round(sum(stats["chg"])/len(stats["chg"]), 2),
    "median_chg": sorted(stats["chg"])[len(stats["chg"])//2],
    "trend_dist": stats["trend"],
    "strength_dist": stats["strength"],
    "avg_score": round(sum(stats["score"])/len(stats["score"]), 1),
    "score_ge80": sum(1 for s in stats["score"] if s >= 80),
    "score_lt50": sum(1 for s in stats["score"] if s < 50),
    "overbought_rsi70": stats["overbought_rsi"],
    "kdj_j_over100": stats["j_over100"],
    "breakout_pressure": stats["breakout"],
    "breakdown_support": stats["breakdown"],
    "newhigh20": stats["newhigh"],
    "vol_up_healthy": stats["vol_up_healthy"],
    "vol_down_warn": stats["vol_down_warn"],
    "chg_gt3pct": sum(1 for c in stats["chg"] if c > 3),
    "chg_lt_minus2pct": sum(1 for c in stats["chg"] if c < -2),
}
print(json.dumps(out, ensure_ascii=False, indent=1))
