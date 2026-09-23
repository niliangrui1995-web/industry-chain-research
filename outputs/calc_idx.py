# -*- coding: utf-8 -*-
"""Parse fetched index chunk JSONs, merge, compute technical indicators."""
import os, re, json, glob

RAW = r"D:\vcp_hunter\产业链投研\outputs\idx_raw"

LIVE = {  # 2026-09-21 14:19 intraday snapshot (open, high, low, last, amount CNY)
    "sh":   (3920.27, 3940.57, 3918.13, 3940.41, 807893637551.0),
    "szcz": (13716.22, 13779.00, 13643.95, 13686.87, 919526587960.0),
    "hs300":(4524.34, 4538.55, 4512.15, 4526.03, 419939002507.0),
    "cyb":  (3403.90, 3429.27, 3373.93, 3384.69, 444503849983.0),
    "kc":   (1669.20, 1678.59, 1643.17, 1650.40, 77051168337.0),
}
NAMES = {"sh": "上证指数", "szcz": "深证成指", "hs300": "沪深300", "cyb": "创业板指", "kc": "科创50"}

def parse_rows(txt):
    rows = []
    for line in txt.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 12 or not re.match(r"^2026-\d{2}-\d{2}$", parts[1]):
            continue
        try:
            d = parts[1]
            o, h, l, c = float(parts[2]), float(parts[3]), float(parts[4]), float(parts[5])
            amount = float(parts[11])
        except Exception:
            continue
        rows.append((d, o, h, l, c, amount))
    return rows

def load_index(short):
    rows = {}
    for f in glob.glob(os.path.join(RAW, "%s_*.json" % short)):
        try:
            j = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        try:
            content = j["data"]["apiData"]["apiRecall"][0]["content"]
        except Exception:
            continue
        for r in parse_rows(content):
            rows[r[0]] = r
    # today's live bar
    if short in LIVE:
        o, h, l, c, a = LIVE[short]
        rows["2026-09-21"] = ("2026-09-21", o, h, l, c, a)
    return [rows[k] for k in sorted(rows)]

def ema(vals, n):
    a = 2.0 / (n + 1)
    e = vals[0]
    out = [e]
    for v in vals[1:]:
        e = v * a + e * (1 - a)
        out.append(e)
    return out

def analyze(short):
    rows = load_index(short)
    closes = [r[4] for r in rows]
    highs = [r[2] for r in rows]
    lows = [r[3] for r in rows]
    amounts = [r[5] for r in rows]
    n = len(rows)
    res = {"name": NAMES[short], "bars": n, "first": rows[0][0], "last": rows[-1][0], "close": closes[-1]}
    if n >= 5:  res["ma5"] = sum(closes[-5:]) / 5
    if n >= 10: res["ma10"] = sum(closes[-10:]) / 10
    if n >= 20: res["ma20"] = sum(closes[-20:]) / 20
    if n >= 60: res["ma60"] = sum(closes[-60:]) / 60
    # MACD (EMA seeded from first value; ~60-90 bars => reasonably converged)
    e12 = ema(closes, 12); e26 = ema(closes, 26)
    dif = [a - b for a, b in zip(e12, e26)]
    dea = ema(dif, 9)
    res["dif"] = dif[-1]; res["dea"] = dea[-1]; res["macd_hist"] = (dif[-1] - dea[-1]) * 2
    res["dif_prev"] = dif[-2]; res["hist_prev"] = (dif[-2] - dea[-2]) * 2
    res["gold_cross_recent"] = (dif[-2] <= dea[-2] and dif[-1] > dea[-1])
    res["dead_cross_recent"] = (dif[-2] >= dea[-2] and dif[-1] < dea[-1])
    # RSI14 (Wilder)
    if n >= 15:
        gains, losses = [], []
        for i in range(1, n):
            ch = closes[i] - closes[i-1]
            gains.append(max(ch, 0)); losses.append(max(-ch, 0))
        ag = sum(gains[:14]) / 14; al = sum(losses[:14]) / 14
        for i in range(14, len(gains)):
            ag = (ag * 13 + gains[i]) / 14
            al = (al * 13 + losses[i]) / 14
        res["rsi14"] = 100 - 100 / (1 + (ag / al if al else 999))
    # volume: today's amount vs 5/20-day avg (excluding today)
    if amounts[-1] and n >= 21 and all(amounts[-20:-1]):
        res["amt_today"] = amounts[-1]
        res["amt_avg5"] = sum(a for a in amounts[-6:-1]) / 5
        res["amt_avg20"] = sum(a for a in amounts[-21:-1]) / 20
        # intraday: today's amount is as of ~14:20 (78% of session elapsed)
        res["amt_est_full"] = amounts[-1] / 0.78
        res["est_vol_ratio"] = res["amt_est_full"] / res["amt_avg20"]
    # key levels
    res["hi20"] = max(highs[-20:]); res["lo20"] = min(lows[-20:])
    res["hi60"] = max(highs[-60:]); res["lo60"] = min(lows[-60:]) if n >= 60 else min(lows)
    if n >= 60:
        res["ma60_prev5"] = sum(closes[-65:-5]) / 60
    res["ma20_prev5"] = sum(closes[-25:-5]) / 20 if n >= 25 else None
    return res, rows

out = {}
for short in ["sh", "szcz", "hs300", "cyb", "kc"]:
    res, rows = analyze(short)
    out[short] = res
    r = dict(res)
    for k in ("ma5","ma10","ma20","ma60","hi20","lo20","hi60","lo60","dif","dea","rsi14"):
        if k in r: r[k] = round(r[k], 2)
    print(json.dumps(r, ensure_ascii=False, default=str))
json.dump(out, open(os.path.join(RAW, "..", "idx_indicators.json"), "w", encoding="utf-8"), ensure_ascii=False, default=str)
print("SAVED")
