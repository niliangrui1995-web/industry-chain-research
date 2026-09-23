# -*- coding: utf-8 -*-
"""赛分科技 SH688758 专项技术档案（含 2026-09-22 收盘）"""
import json, os, struct
from datetime import date

BASE = 'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260921/'
OUT = 'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260922/'
VIP = 'D:/HT/vipdoc'

R = json.load(open(BASE + 'bars_raw.json', encoding='utf-8'))
BARS = R['bars']
lab = {r['full']: r for r in json.load(open(BASE + 'labeled.json', encoding='utf-8'))['rows']}
nd = json.load(open(BASE + 'nextday.json', encoding='utf-8'))
wt = json.load(open(BASE + 'week_thresholds.json', encoding='utf-8'))

CODE = 'SH688758'
# 2026-09-22 收盘（大智慧实时行情 15:00:02）
T = dict(open=32.77, high=34.30, low=32.31, close=33.96, vol=12661161, hsl=4.25, liangbi=1.00)


def ema(vals, n):
    a = 2.0 / (n + 1); out = []; e = vals[0]
    for v in vals:
        e = v * a + e * (1 - a); out.append(e)
    return out


def macd(cl, f=12, s=26, sig=9):
    ef, es = ema(cl, f), ema(cl, s)
    dif = [a - b for a, b in zip(ef, es)]
    dea = ema(dif, sig)
    return dif, dea, [(a - b) * 2 for a, b in zip(dif, dea)]


def rsi_w(cl, n):
    g = [max(cl[i] - cl[i - 1], 0) for i in range(1, len(cl))]
    l = [max(cl[i - 1] - cl[i], 0) for i in range(1, len(cl))]
    ag, al = sum(g[:n]) / n, sum(l[:n]) / n
    out = [50.0]
    for i in range(n, len(g)):
        ag = (ag * (n - 1) + g[i]) / n; al = (al * (n - 1) + l[i]) / n
        out.append(100.0 if al == 0 else 100 - 100 / (1 + ag / al))
    while len(out) < len(cl):
        out.append(out[-1])
    return out


def kdj(hi, lo, cl, n=9):
    k, d = 50.0, 50.0; R = []
    for i in range(len(cl)):
        a = min(lo[max(0, i - n + 1):i + 1]); b = max(hi[max(0, i - n + 1):i + 1])
        rsv = 50.0 if b == a else (cl[i] - a) / (b - a) * 100
        k = 2 / 3 * k + 1 / 3 * rsv; d = 2 / 3 * d + 1 / 3 * k
        R.append((k, d, 3 * k - 2 * d))
    return R


def atr(hi, lo, cl, n=14):
    tr = []
    for i in range(1, len(cl)):
        tr.append(max(hi[i] - lo[i], abs(hi[i] - cl[i - 1]), abs(lo[i] - cl[i - 1])))
    a = sum(tr[:n]) / n
    for i in range(n, len(tr)):
        a = (a * (n - 1) + tr[i]) / n
    return a


def isokey(d):
    y, m, dd = int(d[:4]), int(d[4:6]), int(d[6:8])
    return date(y, m, dd).isocalendar()[:2]


def weekly(bars):
    g = {}; order = []
    for b in bars:
        k = isokey(b['date'])
        if k not in g:
            g[k] = dict(open=b['open'], high=b['high'], low=b['low'], close=b['close'], vol=b['vol'])
            order.append(k)
        else:
            c = g[k]; c['high'] = max(c['high'], b['high']); c['low'] = min(c['low'], b['low'])
            c['close'] = b['close']; c['vol'] += b['vol']
    return [g[k] for k in order]


bars = [dict(b) for b in BARS[CODE]]
prev_close = bars[-1]['close']
lim = 0.205  # 科创板
div = [(bars[i]['date'], round((bars[i]['close'] / bars[i - 1]['close'] - 1) * 100, 2))
       for i in range(max(1, len(bars) - 120), len(bars))
       if abs(bars[i]['close'] / bars[i - 1]['close'] - 1) > lim]
bars.append(dict(date='20260922', open=T['open'], high=T['high'], low=T['low'],
                 close=T['close'], amount=0.0, vol=T['vol']))

cl = [b['close'] for b in bars]; hi = [b['high'] for b in bars]; lo = [b['low'] for b in bars]
vo = [b['vol'] for b in bars]
dif, dea, hist = macd(cl)
r6, r14 = rsi_w(cl, 6), rsi_w(cl, 14)
K = kdj(hi, lo, cl)
a14 = atr(hi, lo, cl)
mid = sum(cl[-20:]) / 20
sd = (sum((x - mid) ** 2 for x in cl[-20:]) / 20) ** 0.5
vr5 = vo[-1] / (sum(vo[-6:-1]) / 5)
vr20 = vo[-1] / (sum(vo[-21:-1]) / 20)

w = weekly(bars); wc = [x['close'] for x in w]
wdif, wdea, whist = macd(wc)


def hist_at(p):
    return macd(wc[:-1] + [p])[2][-1]
h0, h1 = hist_at(0.0), hist_at(1.0)
p0 = -h0 / (h1 - h0)
p_ma4 = sum(wc[-4:-1]) / 3.0
p_ma12 = sum(wc[-12:-1]) / 11.0
prev_wh = w[-2]['high']

c = T['close']
lo60 = min(lo[-60:]); hi60 = max(hi[-60:])
lo250 = min(lo[-250:]) if len(lo) >= 250 else min(lo)
hi250 = max(hi[-250:]) if len(hi) >= 250 else max(hi)
pos60 = (c - lo60) / (hi60 - lo60) * 100
pos250 = (c - lo250) / (hi250 - lo250) * 100

print('=' * 70)
print('赛分科技 SH688758 [%s]  数据根数 %d（含今日）' % (lab[CODE]['block'], len(bars)))
print(' 真实除权(近120日, 科创板限20.5%%): %s' % (div if div else '无'))
print()
print('【今日 2026-09-22 收盘】')
print('  开 %.2f / 高 %.2f / 低 %.2f / 收 %.2f   昨收 %.2f   涨幅 %+.2f%%   振幅 %.2f%%' % (
    T['open'], T['high'], T['low'], c, prev_close,
    (c / prev_close - 1) * 100, (T['high'] - T['low']) / prev_close * 100))
print('  成交量 %d 股  换手 %.2f%%  量比 %.2f  vr5=%.2f vr20=%.2f' % (T['vol'], T['hsl'], T['liangbi'], vr5, vr20))
print()
print('【日线指标（含今日）】')
for n in (5, 10, 20, 30, 60, 120, 250):
    v = sum(cl[-n:]) / n if len(cl) >= n else None
    print('  MA%-3d = %s   价偏离 %s' % (n, ('%.2f' % v) if v else 'N/A',
                                    ('%+.2f%%' % ((c / v - 1) * 100)) if v else 'N/A'))
print('  MACD dif=%.3f dea=%.3f hist=%.3f(前%.3f)  连续柱状: %s' % (
    dif[-1], dea[-1], hist[-1], hist[-2], [round(x, 2) for x in hist[-6:]]))
print('  RSI6=%.1f  RSI14=%.1f  KDJ k=%.1f d=%.1f j=%.1f' % (r6[-1], r14[-1], K[-1][0], K[-1][1], K[-1][2]))
print('  BOLL mid=%.2f up=%.2f dn=%.2f   ATR14=%.2f (%.2f%%)' % (mid, mid + 2 * sd, mid - 2 * sd, a14, a14 / c * 100))
print()
print('【周线（含今日，本周第2根）】')
print('  周柱 本周=%.3f  上周=%.3f  上上周=%s' % (whist[-1], whist[-2], ('%.3f' % whist[-3]) if len(whist) > 3 else 'N/A'))
print('  柱翻正阈值 P* = %.2f（现价 %+.2f%%）' % (p0, (p0 / c - 1) * 100))
print('  周MA4阈值 = %.2f（%+.2f%%）  周MA12阈值 = %.2f（%+.2f%%）' % (
    p_ma4, (p_ma4 / c - 1) * 100, p_ma12, (p_ma12 / c - 1) * 100))
print('  上周最高 %.2f（%+.2f%%）  上周最低 %s' % (prev_wh, (prev_wh / c - 1) * 100, ('%.2f' % w[-2]['low'])))
print('  周MA4=%.2f  周MA12=%.2f' % (sum(wc[-4:]) / 4, sum(wc[-12:]) / 12))
print()
print('【位置与区间】')
print('  60日: 低%.2f 高%.2f → pos60=%.1f' % (lo60, hi60, pos60))
print('  250日: 低%.2f 高%.2f → pos250=%.1f' % (lo250, hi250, pos250))
print('  距60日高 %+.2f%%   距250日高 %+.2f%%' % ((c / hi60 - 1) * 100, (c / hi250 - 1) * 100))
print('  chg5=%.2f%% chg20=%.2f%% chg60=%.2f%%' % (
    lab[CODE]['ind']['chg5'], lab[CODE]['ind']['chg20'], lab[CODE]['ind']['chg60']))
print('  9/21口径: pos60=%.1f bias20=%.2f 支撑%.2f(%.2f%%) 压力%.2f(%.2f%%)' % (
    lab[CODE]['ind']['pos60'], wt[CODE]['bias20'],
    nd[CODE]['sup_near'], nd[CODE]['sup_space'], nd[CODE]['res_near'], nd[CODE]['res_space']))
print()
print('【近12根日线】')
print('  日期      开     高     低     收     涨跌%   量(万手)')
for i in range(len(bars) - 12, len(bars)):
    b = bars[i]
    pc = bars[i - 1]['close']
    print('  %s %6.2f %6.2f %6.2f %6.2f %+7.2f %8.1f' % (
        b['date'], b['open'], b['high'], b['low'], b['close'],
        (b['close'] / pc - 1) * 100, b['vol'] / 1e4))
