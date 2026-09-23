# -*- coding: utf-8 -*-
"""接入 2026-09-22 盘中数据，重算日线与周线指标、周线阈值达成情况"""
import json, os
from datetime import date

BASE = 'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260921/'
OUT = 'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260922/'

R = json.load(open(BASE + 'bars_raw.json', encoding='utf-8'))
BARS = R['bars']
lab = {r['full']: r for r in json.load(open(BASE + 'labeled.json', encoding='utf-8'))['rows']}

# 2026-09-22 14:51-14:52 盘中快照（大智慧实时行情）
# code: open, high, low, close, vol(股), 换手%, 量比
TODAY = {
    'SH688271': (103.05, 103.49, 101.80, 102.22, 3103272, 0.38, 1.13),
    'SZ002821': (188.03, 192.25, 185.47, 186.93, 7741700, 2.43, 0.78),
    'SH601699': (15.52, 15.83, 15.25, 15.76, 25629200, 0.86, 1.23),
    'SZ301205': (324.99, 335.12, 317.16, 327.78, 6095600, 7.28, 0.96),
    'SH688498': (1850.00, 1859.00, 1753.00, 1755.99, 3096244, 2.52, 1.09),
    'SH600487': (74.50, 76.35, 71.84, 72.81, 206393400, 8.41, 1.16),
    'SH688428': (30.10, 32.32, 30.09, 32.10, 17056200, 6.24, 1.76),
    'SZ300308': (968.00, 974.99, 921.00, 928.80, 22726900, 2.05, 1.02),
    'SH688025': (457.00, 458.88, 439.00, 441.45, 2218452, 2.33, 0.62),
    'SZ002463': (128.00, 129.94, 124.66, 125.29, 42822300, 2.23, 0.95),
    'SH601225': (25.45, 26.11, 25.10, 26.07, 32857800, 0.34, 1.27),
    'SH601101': (13.30, 13.70, 13.15, 13.57, 18927300, 1.31, 1.11),
    'SH600546': (13.44, 13.71, 13.31, 13.65, 17547400, 0.89, 0.98),
    'SZ300548': (244.00, 245.65, 235.43, 236.33, 12017500, 4.08, 0.86),
    'SH688313': (174.00, 174.90, 164.50, 165.19, 21096044, 4.67, 1.06),
    'SZ002886': (27.24, 27.47, 26.15, 26.21, 28936600, 13.84, 0.77),
    'SH600330': (30.26, 30.50, 29.30, 29.73, 99781500, 8.09, 0.95),
    'SZ300394': (284.93, 284.93, 275.00, 276.02, 27560800, 2.53, 0.71),
    'SH688796': (135.50, 139.15, 131.51, 134.00, 2992736, 7.75, 0.97),
    'SH688690': (46.95, 49.16, 46.43, 47.85, 11296060, 2.80, 1.03),
}

LIMIT = {'SH': 0.105, 'SZ': 0.105, 'BJ': 0.305}


def ema(vals, n):
    a = 2.0 / (n + 1)
    out = []
    e = vals[0]
    for v in vals:
        e = v * a + e * (1 - a)
        out.append(e)
    return out


def macd(closes, f=12, s=26, sig=9):
    ef, es = ema(closes, f), ema(closes, s)
    dif = [a - b for a, b in zip(ef, es)]
    dea = ema(dif, sig)
    hist = [(a - b) * 2 for a, b in zip(dif, dea)]
    return dif, dea, hist


def rsi_wilder(closes, n):
    if len(closes) < n + 1:
        return [50.0] * len(closes)
    gains, losses = [], []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, 0.0))
        losses.append(max(-d, 0.0))
    ag = sum(gains[:n]) / n
    al = sum(losses[:n]) / n
    out = [50.0]
    for i in range(n, len(gains)):
        ag = (ag * (n - 1) + gains[i]) / n
        al = (al * (n - 1) + losses[i]) / n
        out.append(100.0 if al == 0 else 100 - 100 / (1 + ag / al))
    while len(out) < len(closes):
        out.append(out[-1])
    return out


def kdj(highs, lows, closes, n=9, m1=3, m2=3):
    k, d = 50.0, 50.0
    ks, ds, js = [], [], []
    for i in range(len(closes)):
        lo = min(lows[max(0, i - n + 1):i + 1])
        hi = max(highs[max(0, i - n + 1):i + 1])
        rsv = 50.0 if hi == lo else (closes[i] - lo) / (hi - lo) * 100
        k = (m1 - 1) / m1 * k + 1.0 / m1 * rsv
        d = (m2 - 1) / m2 * d + 1.0 / m2 * k
        ks.append(k); ds.append(d); js.append(3 * k - 2 * d)
    return ks, ds, js


def iso_key(datestr):
    y, m, d = int(datestr[:4]), int(datestr[4:6]), int(datestr[6:8])
    return date(y, m, d).isocalendar()[:2]


def weekly(bars):
    """按 ISO 周聚合，返回 [{key, open, high, low, close, vol}]"""
    g = {}
    order = []
    for b in bars:
        k = iso_key(b['date'])
        if k not in g:
            g[k] = dict(key=k, open=b['open'], high=b['high'], low=b['low'],
                        close=b['close'], vol=b['vol'])
            order.append(k)
        else:
            c = g[k]
            c['high'] = max(c['high'], b['high'])
            c['low'] = min(c['low'], b['low'])
            c['close'] = b['close']
            c['vol'] += b['vol']
    return [g[k] for k in order]


def ma(v, n):
    return sum(v[-n:]) / n if len(v) >= n else None


res = {}
for code, t in TODAY.items():
    bars = [dict(b) for b in BARS[code]]
    prev_close = bars[-1]['close']
    # 除权探测（近 60 根有无超板限跳空）
    lim = LIMIT[code[:2]]
    div = []
    for i in range(max(1, len(bars) - 60), len(bars)):
        r = bars[i]['close'] / bars[i - 1]['close'] - 1
        if abs(r) > lim:
            div.append((bars[i]['date'], round(r * 100, 2)))
    # 追加今日
    o, h, l, c, v, hsl, lb = t
    bars.append(dict(date='20260922', open=o, high=h, low=l, close=c, amount=0.0, vol=v))

    cl = [b['close'] for b in bars]
    hi = [b['high'] for b in bars]
    lo = [b['low'] for b in bars]
    vo = [b['vol'] for b in bars]

    dif, dea, hist = macd(cl)
    r6, r14 = rsi_wilder(cl, 6), rsi_wilder(cl, 14)
    K, D, J = kdj(hi, lo, cl)
    m5, m10, m20, m60 = ma(cl, 5), ma(cl, 10), ma(cl, 20), ma(cl, 60)
    vr5 = vo[-1] / (sum(vo[-6:-1]) / 5) if len(vo) > 6 else None
    vr20 = vo[-1] / (sum(vo[-21:-1]) / 20) if len(vo) > 21 else None
    mid = ma(cl, 20)
    sd = (sum((x - mid) ** 2 for x in cl[-20:]) / 20) ** 0.5 if mid else 0
    up, dn = (mid + 2 * sd, mid - 2 * sd) if mid else (None, None)

    w = weekly(bars)
    wc = [x['close'] for x in w]
    wdif, wdea, whist = macd(wc)
    wma4 = sum(wc[-4:]) / 4 if len(wc) >= 4 else None
    wma12 = sum(wc[-12:]) / 12 if len(wc) >= 12 else None
    # 上周高点 = 倒数第二周
    prev_w_high = w[-2]['high'] if len(w) >= 2 else None

    # 阈值求解：本周收盘价 P 线性 → 柱翻正价
    def hist_at(p):
        return macd(wc[:-1] + [p])[2][-1]
    h0, h1 = hist_at(0.0), hist_at(1.0)
    p_macd0 = -h0 / (h1 - h0) if h1 != h0 else None
    p_ma4 = sum(wc[-4:-1]) / 3.0 if len(wc) >= 4 else None
    p_ma12 = sum(wc[-12:-1]) / 11.0 if len(wc) >= 12 else None

    res[code] = dict(
        name=lab[code]['name'], block=lab[code]['block'], prev_close=prev_close,
        today=dict(open=o, high=h, low=l, close=c, hsl=hsl, liangbi=lb,
                   chg=round((c / prev_close - 1) * 100, 2)),
        div=div,
        ma5=m5, ma10=m10, ma20=m20, ma60=m60,
        macd=dict(dif=dif[-1], dea=dea[-1], hist=hist[-1], hist_prev=hist[-2]),
        rsi6=r6[-1], rsi14=r14[-1], kdj=dict(k=K[-1], d=D[-1], j=J[-1]),
        boll=dict(mid=mid, up=up, dn=dn), vr5=vr5, vr20=vr20,
        wk=dict(hist_now=whist[-1], hist_last=whist[-2], wma4=wma4, wma12=wma12,
                prev_high=prev_w_high, p_macd0=p_macd0, p_ma4=p_ma4, p_ma12=p_ma12,
                n_week=len(w)),
    )

json.dump(res, open(OUT + 'recalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('%-9s %-6s %8s %7s %7s | %7s %7s %7s | %9s %9s | %8s %8s %8s | %s' % (
    '代码', '名称', '现价', '涨幅%', '换手%', 'MA5', 'MA10', 'MA20', '周柱(今)', '周柱(上周)', '周MA4', 'P*翻正', '上周高', '板块'))
for code, r in sorted(res.items(), key=lambda x: -x[1]['today']['chg']):
    w = r['wk']
    t = r['today']
    print('%-9s %-6s %8.2f %7.2f %7.2f | %7.2f %7.2f %7.2f | %9.3f %9.3f | %8.2f %8.2f %8.2f | %s%s' % (
        code, r['name'], t['close'], t['chg'], t['hsl'],
        r['ma5'], r['ma10'], r['ma20'],
        w['hist_now'], w['hist_last'], w['wma4'] or 0, w['p_macd0'] or 0, w['prev_high'] or 0,
        r['block'], '  [除权:%s]' % r['div'] if r['div'] else ''))

print()
print('=== 周线阈值达成判定（以今日盘中价代入本周收盘） ===')
print('%-9s %-6s %8s | %-22s | %-22s | %-22s' % ('代码', '名称', '现价', '柱翻正P* (差%)', '周MA4阈值(差%)', '上周高(差%)'))
for code, r in sorted(res.items(), key=lambda x: -x[1]['today']['chg']):
    w = r['wk']; c = r['today']['close']
    def g(p):
        return 'N/A' if not p else '%8.2f (%+6.2f%%)' % (p, (p / c - 1) * 100)
    print('%-9s %-6s %8.2f | %-22s | %-22s | %-22s' % (
        code, r['name'], c, g(w['p_macd0']), g(w['p_ma4']), g(w['prev_high'])))
