# -*- coding: utf-8 -*-
"""计算技术指标（日线 + 周线），含除权跳空检测与前向复权处理。"""
import os, json, math, datetime as dt

OUTDIR = r'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260921'
D = json.load(open(os.path.join(OUTDIR, 'bars_raw.json'), encoding='utf-8'))
bars_all = D['bars']
members = json.load(open(os.path.join(OUTDIR, 'block_members.json'), encoding='utf-8'))

AS_OF = '20260921'
ETF = {'SH515880'}

def limit_of(full):
    mkt, code = full[:2], full[2:]
    if mkt == 'BJ':
        return 0.305
    if code.startswith(('688', '300', '301')):
        return 0.205
    if code.startswith(('8', '4', '920')):
        return 0.305
    return 0.105

def adjust(bars, full):
    """检测超过涨跌停限制的跳空 → 判定除权，做前复权（锚定最新价格）。返回(复权bars, 除权日期列表)"""
    lim = limit_of(full)
    n = len(bars)
    fac = [1.0] * n
    events = []
    f = 1.0
    for i in range(n - 1, 0, -1):
        prev = bars[i - 1]['close']
        cur = bars[i]['close']
        if prev <= 0:
            continue
        r = cur / prev - 1
        if abs(r) > lim:
            g = cur / prev          # 除权导致的价格比例
            f *= g
            events.append((bars[i]['date'], round(r * 100, 2)))
        fac[i - 1] = f
    out = []
    for i, b in enumerate(bars):
        k = fac[i]
        out.append({'date': b['date'], 'open': b['open'] * k, 'high': b['high'] * k,
                    'low': b['low'] * k, 'close': b['close'] * k,
                    'amount': b['amount'], 'vol': b['vol']})
    return out, events

# ---------- 指标 ----------
def sma(x, n):
    if len(x) < n: return None
    return sum(x[-n:]) / n

def ema_series(x, n):
    a = 2.0 / (n + 1)
    out, prev = [], None
    for v in x:
        prev = v if prev is None else a * v + (1 - a) * prev
        out.append(prev)
    return out

def macd(closes, f=12, s=26, sig=9):
    if len(closes) < s + sig: return None
    ef = ema_series(closes, f); es = ema_series(closes, s)
    dif = [a - b for a, b in zip(ef, es)]
    dea = ema_series(dif, sig)
    return {'dif': dif[-1], 'dea': dea[-1], 'hist': (dif[-1] - dea[-1]) * 2,
            'dif_prev': dif[-2], 'dea_prev': dea[-2], 'hist_prev': (dif[-2] - dea[-2]) * 2,
            'hist5': [(dif[i] - dea[i]) * 2 for i in range(-5, 0)]}

def rsi(closes, n=14):
    if len(closes) < n + 1: return None
    gains, losses = [], []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, 0.0)); losses.append(max(-d, 0.0))
    ag = sum(gains[:n]) / n; al = sum(losses[:n]) / n
    for i in range(n, len(gains)):
        ag = (ag * (n - 1) + gains[i]) / n
        al = (al * (n - 1) + losses[i]) / n
    if al == 0: return 100.0
    rs = ag / al
    return 100 - 100 / (1 + rs)

def kdj(bars, n=9):
    if len(bars) < n + 3: return None
    k, d = 50.0, 50.0
    for i in range(n - 1, len(bars)):
        hh = max(b['high'] for b in bars[i - n + 1:i + 1])
        ll = min(b['low'] for b in bars[i - n + 1:i + 1])
        rsv = 50.0 if hh == ll else (bars[i]['close'] - ll) / (hh - ll) * 100
        k = 2 / 3 * k + 1 / 3 * rsv
        d = 2 / 3 * d + 1 / 3 * k
    return {'k': k, 'd': d, 'j': 3 * k - 2 * d}

def boll(closes, n=20, k=2):
    if len(closes) < n: return None
    mid = sum(closes[-n:]) / n
    var = sum((c - mid) ** 2 for c in closes[-n:]) / n
    sd = math.sqrt(var)
    return {'mid': mid, 'up': mid + k * sd, 'dn': mid - k * sd, 'width': (2 * k * sd) / mid * 100}

def atr(bars, n=14):
    if len(bars) < n + 1: return None
    trs = []
    for i in range(1, len(bars)):
        h, l, pc = bars[i]['high'], bars[i]['low'], bars[i - 1]['close']
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    a = sum(trs[:n]) / n
    for i in range(n, len(trs)):
        a = (a * (n - 1) + trs[i]) / n
    return a

def weekly(bars):
    """按自然周聚合日线 -> 周线"""
    wk = {}
    for b in bars:
        d = dt.datetime.strptime(b['date'], '%Y%m%d').date()
        key = d.isocalendar()[:2]
        w = wk.setdefault(key, {'date': b['date'], 'open': b['open'], 'high': b['high'],
                                'low': b['low'], 'close': b['close'], 'vol': 0, 'amount': 0})
        w['high'] = max(w['high'], b['high']); w['low'] = min(w['low'], b['low'])
        w['close'] = b['close']; w['date'] = b['date']
        w['vol'] += b['vol']; w['amount'] += b['amount']
    return [wk[k] for k in sorted(wk)]

def swing_levels(bars, look=60):
    """近 look 日的重要高低点（分形极值法）"""
    seg = bars[-look:] if len(bars) >= look else bars
    highs, lows = [], []
    for i in range(2, len(seg) - 2):
        c = seg[i]
        if c['high'] >= max(x['high'] for x in seg[i - 2:i + 3]) and c['high'] == max(x['high'] for x in seg[i - 2:i + 3]):
            highs.append((c['date'], c['high']))
        if c['low'] == min(x['low'] for x in seg[i - 2:i + 3]):
            lows.append((c['date'], c['low']))
    return highs[-6:], lows[-6:]

results = {}
for full, raw in bars_all.items():
    raw = sorted(raw, key=lambda r: r['date'])
    adj, ev = adjust(raw, full)
    closes = [b['close'] for b in adj]
    vols = [b['vol'] for b in adj]
    c = closes[-1]
    if c <= 0:
        continue
    ma = {n: sma(closes, n) for n in (5, 10, 20, 30, 60, 120, 250)}
    m = macd(closes)
    kd = kdj(adj)
    bl = boll(closes)
    a14 = atr(adj)
    w = weekly(adj)
    wc = [x['close'] for x in w]
    wma = {n: sma(wc, n) for n in (4, 8, 12, 20)}
    wm = macd(wc) if len(wc) >= 35 else None
    wv = [x['vol'] for x in w]
    hi60 = max(b['high'] for b in adj[-60:]) if len(adj) >= 60 else max(b['high'] for b in adj)
    lo60 = min(b['low'] for b in adj[-60:]) if len(adj) >= 60 else min(b['low'] for b in adj)
    win = min(250, len(adj))
    hi52 = max(b['high'] for b in adj[-win:]); lo52 = min(b['low'] for b in adj[-win:])
    v5 = sma(vols, 5); v20 = sma(vols, 20); v60 = sma(vols, 60)
    highs, lows = swing_levels(adj, 60)
    # 近 5/10/20 日涨幅（复权后）
    def chg(n):
        return (c / closes[-1 - n] - 1) * 100 if len(closes) > n else None
    results[full] = {
        'as_of': AS_OF, 'close': round(c, 2), 'n_bars': len(adj),
        'chg1': round(adj[-1]['close'] / adj[-2]['close'] * 100 - 100, 2) if len(adj) > 1 else None,
        'chg5': round(chg(5), 2) if chg(5) is not None else None,
        'chg10': round(chg(10), 2) if chg(10) is not None else None,
        'chg20': round(chg(20), 2) if chg(20) is not None else None,
        'chg60': round(chg(60), 2) if chg(60) is not None else None,
        'ma': {k: (round(v, 2) if v else None) for k, v in ma.items()},
        'macd': {k: (round(v, 3) if isinstance(v, float) else ([round(x, 3) for x in v] if isinstance(v, list) else v))
                 for k, v in m.items()} if m else None,
        'rsi6': round(rsi(closes, 6), 1) if len(closes) > 7 else None,
        'rsi14': round(rsi(closes, 14), 1) if len(closes) > 15 else None,
        'kdj': {k: round(v, 1) for k, v in kd.items()} if kd else None,
        'boll': {k: round(v, 2) for k, v in bl.items()} if bl else None,
        'atr14': round(a14, 2) if a14 else None,
        'atr_pct': round(a14 / c * 100, 2) if a14 else None,
        'vol': vols[-1], 'vma5': int(v5) if v5 else None, 'vma20': int(v20) if v20 else None,
        'vma60': int(v60) if v60 else None,
        'vr5': round(vols[-1] / v5, 2) if v5 else None,
        'vr20': round(vols[-1] / v20, 2) if v20 else None,
        'hi60': round(hi60, 2), 'lo60': round(lo60, 2),
        'hi52': round(hi52, 2), 'lo52': round(lo52, 2),
        'pos60': round((c - lo60) / (hi60 - lo60) * 100, 1) if hi60 > lo60 else None,
        'pos52': round((c - lo52) / (hi52 - lo52) * 100, 1) if hi52 > lo52 else None,
        'from_hi52': round((c / hi52 - 1) * 100, 2),
        'from_lo52': round((c / lo52 - 1) * 100, 2),
        'swing_highs': [[d, round(v, 2)] for d, v in highs],
        'swing_lows': [[d, round(v, 2)] for d, v in lows],
        'weekly': {'n': len(w), 'ma': {k: (round(v, 2) if v else None) for k, v in wma.items()},
                   'macd': {k: round(v, 3) for k, v in wm.items() if k in ('dif', 'dea', 'hist')} if wm else None,
                   'vol_last': wv[-1] if wv else None,
                   'vma4': int(sma(wv, 4)) if len(wv) >= 4 else None,
                   'vma12': int(sma(wv, 12)) if len(wv) >= 12 else None,
                   'chg1w': round((wc[-1] / wc[-2] - 1) * 100, 2) if len(wc) > 1 else None,
                   'chg4w': round((wc[-1] / wc[-5] - 1) * 100, 2) if len(wc) > 4 else None},
        'div_events': ev[-5:],
        'is_etf': full in ETF,
        'incomplete_days': D['incomplete'].get(full, 0),
    }

json.dump(results, open(os.path.join(OUTDIR, 'indicators.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('计算完成:', len(results))
ev_all = {k: v['div_events'] for k, v in results.items() if v['div_events']}
print('\n检测到除权跳空的标的:', len(ev_all))
for k, v in list(ev_all.items())[:12]:
    print('  ', k, v)
# 抽样
for k in ['SH603228', 'SZ300308', 'SH688256']:
    r = results[k]
    print('\n---', k, '---')
    print(' close', r['close'], 'MA', r['ma'], 'MACD', r['macd']['dif'], r['macd']['dea'], r['macd']['hist'])
    print(' rsi14', r['rsi14'], 'kdj', r['kdj'], 'boll', r['boll'], 'atr%', r['atr_pct'])
    print(' pos60', r['pos60'], 'from_hi52', r['from_hi52'], 'vr5', r['vr5'], 'weekly', r['weekly'])
