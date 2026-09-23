# -*- coding: utf-8 -*-
"""纳微科技 vs 赛分科技 技术面量化指标统一计算
数据源: 通达信 MCP tdx_kline 周线(前复权, tqFlag=1), 快照时间 2026-09-21 盘中
纳微/科创50 来自工具落盘文件, 赛分科技 89 根周线内嵌(与 MCP 返回一致)
"""
import re, json, math

TOOLDIR = r"C:\Users\Administrator\.workbuddy\projects\d-vcp_hunter-产业链投研\9f0cd1c1-69bf-42e0-a262-cb912e235f41\tool-results"
F_NW = TOOLDIR + r"\mcp-tdx-connector-tdx_kline-1789958429278-c539a9.txt"   # 纳微科技
F_KC50 = TOOLDIR + r"\mcp-tdx-connector-tdx_kline-1789958508327-f5d6a2.txt" # 科创50

ROW_RE = re.compile(
    r'"Data": "(\d{8})".*?"Open": "([\d.]+)".*?"High": "([\d.]+)".*?"Low": "([\d.]+)".*?'
    r'"Close": "([\d.]+)".*?"Volume": ([\d.eE+]+).*?"Settle": "(-?[\d.]+)"', re.S)

def parse_file(path):
    s = open(path, encoding="utf-8", errors="replace").read()
    rows = []
    for m in ROW_RE.finditer(s):
        d, o, h, l, c, v, st = m.groups()
        rows.append(dict(date=d, open=float(o), high=float(h), low=float(l),
                         close=float(c), vol=float(v), settle=abs(float(st))))
    return rows

# 赛分科技 688758 周线(date,high,low,close,volume手,settle流通股本万股) —— 与 MCP 返回逐行一致
SF_RAW = """20250110,28.86,19.57,20.56,311374,3950.43
20250117,19.74,15.47,15.49,835042,3950.43
20250124,16.24,14.87,15.04,301803,3950.43
20250127,15.20,14.65,14.65,33997,3950.43
20250207,15.51,14.52,15.37,162562,3950.43
20250214,16.00,15.07,15.59,245855,3950.43
20250221,15.93,15.30,15.60,208056,3950.43
20250228,17.96,15.36,16.65,442137,3950.43
20250307,17.26,16.47,16.74,232942,3950.43
20250314,18.36,16.55,17.39,273963,3950.43
20250321,18.35,17.26,17.61,238412,3950.43
20250328,17.65,16.13,16.72,183069,3950.43
20250403,17.54,16.37,17.46,126591,3950.43
20250411,17.04,14.07,16.20,240913,3950.43
20250418,17.37,15.91,15.99,130696,3950.43
20250425,16.49,15.46,15.66,93579,3950.43
20250430,15.81,15.26,15.52,38481,3950.43
20250509,16.56,15.61,16.06,80289,3950.43
20250516,16.72,15.96,16.10,109317,3950.43
20250523,16.73,15.88,16.17,101933,3950.43
20250530,16.32,15.68,15.89,77116,3950.43
20250606,16.40,15.84,15.91,61172,3950.43
20250613,16.45,15.81,15.90,112207,3950.43
20250620,16.11,15.50,15.56,66888,3950.43
20250627,17.18,15.44,16.90,129082,3950.43
20250704,17.27,16.30,16.33,127457,3950.43
20250711,17.03,16.20,16.78,123781,4247.93
20250718,17.77,16.79,17.33,191108,4247.93
20250725,19.23,17.20,18.86,264087,4247.93
20250801,19.79,18.26,18.35,244852,4247.93
20250808,18.74,17.92,18.31,130988,4247.93
20250815,19.00,18.23,19.00,159090,4247.93
20250822,21.40,19.01,20.05,225369,4247.93
20250829,20.98,19.07,19.27,219665,4247.93
20250905,19.64,17.53,18.28,140096,4247.93
20250912,18.70,17.35,18.07,103656,4247.93
20250919,18.66,17.86,18.23,110322,4247.93
20250926,18.50,17.35,17.74,94084,4247.93
20250930,18.08,17.53,17.68,23734,4247.93
20251010,17.85,17.30,17.43,35411,4247.93
20251017,19.91,16.74,18.78,282920,4247.93
20251024,20.03,18.32,19.57,276512,4247.93
20251031,20.67,19.34,19.66,244446,4247.93
20251107,19.84,18.75,19.36,114084,4247.93
20251114,23.33,18.97,22.61,283099,4247.93
20251121,22.81,20.23,20.23,213060,4247.93
20251128,22.38,19.43,21.40,163730,4247.93
20251205,21.49,18.68,19.09,126005,4247.93
20251212,19.65,18.76,19.52,126392,4247.93
20251219,19.39,17.82,18.35,94711,4247.93
20251226,18.50,17.80,18.09,96241,4247.93
20251231,18.16,17.43,17.66,45767,4247.93
20260109,18.88,17.60,18.32,147087,4247.93
20260116,19.61,17.98,19.33,309354,29818.37
20260123,19.48,18.73,19.38,146448,29818.37
20260130,20.06,17.84,18.30,236179,29818.37
20260206,19.32,17.99,18.81,190861,29818.37
20260213,20.63,18.75,20.20,258804,29818.37
20260227,20.77,19.98,20.04,159151,29818.37
20260306,20.53,17.76,18.58,215583,29818.37
20260313,19.53,18.39,18.95,136093,29818.37
20260320,19.30,17.32,17.37,105932,29818.37
20260327,17.42,15.78,17.28,129029,29818.37
20260403,20.26,17.18,19.21,282971,29818.37
20260410,21.41,18.73,20.72,199210,29818.37
20260417,21.12,19.53,21.00,281647,29818.37
20260424,21.92,19.70,20.09,308120,29818.37
20260430,20.30,19.35,19.40,116758,29818.37
20260508,20.23,19.33,19.74,120998,29818.37
20260515,20.67,18.99,19.59,253377,29818.37
20260522,20.33,18.98,19.92,188469,29818.37
20260529,20.13,18.17,18.41,205991,29818.37
20260605,18.90,16.94,17.33,120563,29818.37
20260612,19.97,16.24,19.78,260045,29818.37
20260618,20.72,19.13,19.84,240174,29818.37
20260626,20.21,18.59,19.13,251196,29818.37
20260703,22.90,18.87,21.79,494057,29818.37
20260710,23.23,19.13,21.15,321199,29818.37
20260717,24.60,20.24,23.49,671111,29818.37
20260724,28.59,22.54,24.83,852007,29818.37
20260731,25.58,22.08,22.15,516325,29818.37
20260807,29.29,21.90,28.97,667802,29818.37
20260814,31.97,27.66,29.40,800862,29818.37
20260821,29.80,26.51,27.33,614950,29818.37
20260828,28.33,25.55,27.08,501452,29818.37
20260904,28.87,25.52,26.40,466657,29818.37
20260911,29.08,25.60,26.81,401965,29818.37
20260918,33.33,26.34,32.80,562901,29818.37
20260921,33.30,31.68,33.05,92612,29818.37"""

def parse_sf():
    rows = []
    for line in SF_RAW.strip().splitlines():
        d, h, l, c, v, st = line.split(",")
        rows.append(dict(date=d, high=float(h), low=float(l), close=float(c),
                         vol=float(v), settle=float(st)))
    return rows

def ret(a, b):  # b -> a
    return a / b - 1.0

def stats(rows, name):
    closes = [r["close"] for r in rows]
    dates = [r["date"] for r in rows]
    n = len(rows)
    out = {"name": name, "n_weeks": n, "first_date": dates[0], "last_date": dates[-1],
           "first_close": closes[0], "last_close": closes[-1]}
    # 区间收益(首周收盘->最新)
    out["total_ret"] = ret(closes[-1], closes[0])
    yrs = n / 52.0
    out["years"] = round(yrs, 2)
    out["ann_ret"] = (closes[-1] / closes[0]) ** (1 / yrs) - 1 if yrs > 0 else None
    # 最高/最低
    hi = max(rows, key=lambda r: r["high"]); lo = min(rows, key=lambda r: r["low"])
    out["max_high"] = (hi["high"], hi["date"]); out["min_low"] = (lo["low"], lo["date"])
    out["dd_from_high"] = ret(closes[-1], hi["high"])
    # 最大回撤(周收盘)
    peak = closes[0]; mdd = 0.0; mdd_pair = None; peak_d = dates[0]
    cur_peak = closes[0]; cur_peak_d = dates[0]
    for d, c in zip(dates, closes):
        if c > cur_peak:
            cur_peak = c; cur_peak_d = d
        dd = c / cur_peak - 1
        if dd < mdd:
            mdd = dd; mdd_pair = (cur_peak_d, d, cur_peak, c)
    out["mdd"] = mdd; out["mdd_detail"] = mdd_pair
    # 周收益波动率(年化)
    wk = [math.log(closes[i] / closes[i - 1]) for i in range(1, n)]
    mu = sum(wk) / len(wk)
    var = sum((x - mu) ** 2 for x in wk) / (len(wk) - 1)
    out["ann_vol"] = math.sqrt(var) * math.sqrt(52)
    out["ann_vol_2026"] = None
    w26 = [math.log(closes[i] / closes[i - 1]) for i in range(1, n) if dates[i] >= "20260101"]
    if len(w26) > 2:
        mu2 = sum(w26) / len(w26); var2 = sum((x - mu2) ** 2 for x in w26) / (len(w26) - 1)
        out["ann_vol_2026"] = math.sqrt(var2) * math.sqrt(52)
    # 年度收益(上年最后收盘->本年最后收盘; 首年用首周收盘)
    yr_ret = {}
    by_year = {}
    for d, c in zip(dates, closes):
        by_year.setdefault(d[:4], []).append((d, c))
    years = sorted(by_year)
    for i, y in enumerate(years):
        last_c = by_year[y][-1][1]
        base = by_year[years[i - 1]][-1][1] if i > 0 else by_year[y][0][1]
        yr_ret[y] = ret(last_c, base)
    out["yearly"] = yr_ret
    # 近13/26周收益
    if n > 13: out["ret_13w"] = ret(closes[-1], closes[-14])
    if n > 26: out["ret_26w"] = ret(closes[-1], closes[-27])
    # 52周高低
    last52 = rows[-52:] if n >= 52 else rows
    out["hi_52w"] = max(r["high"] for r in last52); out["lo_52w"] = min(r["low"] for r in last52)
    out["pos_in_52w_range"] = (closes[-1] - out["lo_52w"]) / (out["hi_52w"] - out["lo_52w"])
    # 换手率(仅个股: vol手*100 / settle万股*1e4)
    if name != "科创50":
        tos = []
        for r in rows:
            if r["settle"] and r["settle"] > 500:
                tos.append(r["vol"] * 100 / (r["settle"] * 1e4))
        if tos:
            out["avg_weekly_to"] = sum(tos) / len(tos)
            out["avg_weekly_to_13w"] = sum(tos[-13:]) / len(tos[-13:])
            out["avg_weekly_to_4w"] = sum(tos[-4:]) / len(tos[-4:])
        # 周振幅均值
        amps = [(rows[i]["high"] - rows[i]["low"]) / rows[i - 1]["close"] for i in range(1, n)]
        out["avg_weekly_amp"] = sum(amps) / len(amps)
        amps13 = amps[-13:]
        out["avg_weekly_amp_13w"] = sum(amps13) / len(amps13)
    return out

nw = parse_file(F_NW)
kc = parse_file(F_KC50)
sf = parse_sf()
assert len(nw) > 200, f"纳微解析异常: {len(nw)}"
assert len(kc) > 200, f"科创50解析异常: {len(kc)}"
assert len(sf) == 89, f"赛分行数异常: {len(sf)}"

res = {"纳微科技": stats(nw, "纳微科技"), "赛分科技": stats(sf, "赛分科技"), "科创50": stats(kc, "科创50")}

# 对齐窗口的超额收益: 科创50 取与个股共同起点
def aligned_excess(stock_rows, stock_name):
    d0 = stock_rows[0]["date"]
    kc_al = [r for r in kc if r["date"] >= d0]
    if not kc_al:
        return None
    s0 = stock_rows[0]["close"]; s1 = stock_rows[-1]["close"]
    k0 = kc_al[0]["close"]; k1 = kc_al[-1]["close"]
    return {"kc50_ret": ret(k1, k0), "stock_ret": ret(s1, s0),
            "excess": ret(s1, s0) - ret(k1, k0), "kc_from": kc_al[0]["date"]}

res["纳微科技"]["vs_kc50"] = aligned_excess(nw, "纳微科技")
res["赛分科技"]["vs_kc50"] = aligned_excess(sf, "赛分科技")

# 纳微流通股本变迁(解禁史)
settle_changes = []
prev = None
for r in nw:
    if r["settle"] and r["settle"] > 500 and r["settle"] != prev:
        settle_changes.append((r["date"], r["settle"])); prev = r["settle"]
res["纳微科技"]["float_history"] = settle_changes

with open(r"D:\vcp_hunter\产业链投研\research_outputs\bio_upstream_20260921\tech_stats.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)

print("OK rows:", len(nw), len(sf), len(kc))
print("纳微 float history:", settle_changes[:12])
