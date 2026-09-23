# -*- coding: utf-8 -*-
"""多周期共振分析引擎（本地 vipdoc 日线 -> 日/周/月三周期指标 + 共振矩阵）。

数据来源: D:\\HT\\vipdoc\\{sh,sz,bj}\\lday\\*.day  (通达信本地日线, 不复权)
最后交易日通过本脚本动态识别。
"""
import os, re, json, struct, math, datetime, collections

VIP = r'D:\HT\vipdoc'
OUT = os.path.dirname(os.path.abspath(__file__))
REC = 32
DAILY_N = 300          # 日线取最近根数
WEEK_N = 156           # 合成周线取最近根数（=3年）
MONTH_N = 80           # 合成月线取最近根数


# ---------- IO ----------
def day_path(mkt, code):
    sub = {'SH': 'sh', 'SZ': 'sz', 'BJ': 'bj'}[mkt]
    return os.path.join(VIP, sub, 'lday', '%s%s.day' % (sub, code))


def read_day(path):
    if not os.path.isfile(path):
        return []
    b = open(path, 'rb').read()
    n = len(b) // REC
    out = []
    for i in range(n):
        raw = b[i * REC:(i + 1) * REC]
        if len(raw) < REC:
            break
        d, o, h, l, c, amt, vol, _ = struct.unpack('<iiiiifii', raw)
        if d <= 0 or c <= 0:
            continue
        out.append({'d': '%08d' % d, 'o': o / 100.0, 'h': h / 100.0, 'l': l / 100.0,
                    'c': c / 100.0, 'amt': amt, 'v': vol})
    out.sort(key=lambda x: x['d'])
    return out


# ---------- 前复权因子 ----------
# 通过通达信MCP前复权日线标定：f = fq_close / raw_close
# f_prev 应用于除权日之前(含前一日)，f_cur 应用于除权日及之后
ADJ = {
    '688498': {'date': '20260518', 'prev': '20260515', 'f_prev': 1074.689941 / 1559.00, 'f_cur': 1.0},
    '300394': {'date': '20260612', 'prev': '20260611', 'f_prev': 293.500000 / 412.30, 'f_cur': 280.450012 / 280.95},
    '688167': {'date': '20260610', 'prev': '20260609', 'f_prev': 304.049988 / 440.87, 'f_cur': 1.0},
    '300502': {'date': '20260611', 'prev': '20260610', 'f_prev': 551.070007 / 772.50, 'f_cur': 1.0},
    '688195': {'date': '20260529', 'prev': '20260528', 'f_prev': 243.750000 / 341.42, 'f_cur': 1.0},
    '301591': {'date': '20260527', 'prev': '20260526', 'f_prev': 45.009998 / 58.68, 'f_cur': 40.520000 / 40.60},
    '688800': {'date': '20260617', 'prev': '20260616', 'f_prev': 88.739998 / 124.54, 'f_cur': 1.0},
    '688256': {'date': '20260508', 'prev': '20260507', 'f_prev': 1252.680054 / 1868.00, 'f_cur': 1.0},
    '002975': {'date': '20260511', 'prev': '20260508', 'f_prev': 95.730003 / 124.45, 'f_cur': 1.0},
    '002837': {'date': '20260601', 'prev': '20260529', 'f_prev': 69.870003 / 91.00, 'f_cur': 1.0},
    '301128': {'date': '20260519', 'prev': '20260518', 'f_prev': 135.460007 / 190.45, 'f_cur': 1.0},
}


def apply_adj(days, code):
    a = ADJ.get(code)
    if not a:
        return days, None
    idx = {r['d']: i for i, r in enumerate(days)}
    pi = idx.get(a['prev'])
    if pi is None:
        return days, 'warn:prev_not_found'
    out = []
    for i, r in enumerate(days):
        f = a['f_prev'] if i <= pi else a['f_cur']
        rr = dict(r)
        for k in ('o', 'h', 'l', 'c'):
            rr[k] = r[k] * f
        out.append(rr)
    return out, {'date': a['date'], 'f_prev': round(a['f_prev'], 5), 'f_cur': round(a['f_cur'], 5)}


# ---------- 周期合成 ----------
def to_week(days):
    out = collections.OrderedDict()
    for r in days:
        dt = datetime.datetime.strptime(r['d'], '%Y%m%d').date()
        key = dt.isocalendar()[:2]          # (iso_year, iso_week)
        if key not in out:
            out[key] = dict(r)
            out[key]['d'] = r['d']
        else:
            g = out[key]
            g['h'] = max(g['h'], r['h'])
            g['l'] = min(g['l'], r['l'])
            g['c'] = r['c']
            g['v'] += r['v']
            g['amt'] += r['amt']
            g['d'] = r['d']
    return list(out.values())


def to_month(days):
    out = collections.OrderedDict()
    for r in days:
        key = r['d'][:6]
        if key not in out:
            out[key] = dict(r)
            out[key]['d'] = r['d']
        else:
            g = out[key]
            g['h'] = max(g['h'], r['h'])
            g['l'] = min(g['l'], r['l'])
            g['c'] = r['c']
            g['v'] += r['v']
            g['amt'] += r['amt']
            g['d'] = r['d']
    return list(out.values())


# ---------- 指标 ----------
def sma(xs, n):
    if len(xs) < n:
        return None
    return sum(xs[-n:]) / n


def ema_series(xs, n):
    """通达信 EMA: Y = (2*X + (N-1)*Y') / (N+1)，首值取 X0"""
    if not xs:
        return []
    a = 2.0 / (n + 1)
    out = [xs[0]]
    for x in xs[1:]:
        out.append(a * x + (1 - a) * out[-1])
    return out


def macd(closes, f=12, s=26, sig=9):
    if len(closes) < s + sig:
        return None
    ef = ema_series(closes, f)
    es = ema_series(closes, s)
    dif = [a - b for a, b in zip(ef, es)]
    dea = ema_series(dif, sig)
    hist = [2 * (a - b) for a, b in zip(dif, dea)]
    return {'dif': dif[-1], 'dea': dea[-1], 'hist': hist[-1],
            'dif_prev': dif[-2], 'dea_prev': dea[-2], 'hist_prev': hist[-2],
            'hist_series': hist}


def rsi(closes, n=14):
    if len(closes) < n + 1:
        return None
    up = dn = 0.0
    for i in range(len(closes) - n, len(closes)):
        ch = closes[i] - closes[i - 1]
        if ch > 0:
            up += ch
        else:
            dn -= ch
    if dn == 0:
        return 100.0
    rs = (up / n) / (dn / n)
    return 100 - 100 / (1 + rs)


def kdj(hs, ls, cs, n=9):
    if len(cs) < n:
        return None
    k, d = 50.0, 50.0
    for i in range(len(cs)):
        lo = min(ls[max(0, i - n + 1):i + 1])
        hi = max(hs[max(0, i - n + 1):i + 1])
        rsv = 50.0 if hi == lo else (cs[i] - lo) / (hi - lo) * 100
        k = 2 / 3 * k + 1 / 3 * rsv
        d = 2 / 3 * d + 1 / 3 * k
    return {'k': k, 'd': d, 'j': 3 * k - 2 * d}


def boll(closes, n=20, k=2):
    if len(closes) < n:
        return None
    w = closes[-n:]
    mid = sum(w) / n
    var = sum((x - mid) ** 2 for x in w) / n
    sd = math.sqrt(var)
    return {'mid': mid, 'up': mid + k * sd, 'dn': mid - k * sd, 'width': 4 * k * sd / mid if mid else None}


def atr(hs, ls, cs, n=14):
    if len(cs) < n + 1:
        return None
    trs = []
    for i in range(len(cs) - n, len(cs)):
        trs.append(max(hs[i] - ls[i], abs(hs[i] - cs[i - 1]), abs(ls[i] - cs[i - 1])))
    return sum(trs) / n


def mas_of(closes, ns):
    r = {}
    for n in ns:
        r['ma%d' % n] = sma(closes, n)
    return r


def trend_of(closes, mas, use4=False):
    """判定均线排列: bull / bear / cross(交织)"""
    keys = ['ma5', 'ma10', 'ma20', 'ma60'] if use4 else ['ma5', 'ma10', 'ma20']
    vals = [mas.get(k) for k in keys]
    if any(v is None for v in vals):
        return 'na', None
    c = closes[-1]
    if all(vals[i] > vals[i + 1] for i in range(len(vals) - 1)):
        return ('bull' if c > vals[0] else 'bull_pull'), '多头排列'
    if all(vals[i] < vals[i + 1] for i in range(len(vals) - 1)):
        return ('bear' if c < vals[0] else 'bear_bounce'), '空头排列'
    return 'cross', '均线交织'


def pct(a, b):
    return None if not b else (a - b) / b * 100


def analyze_period(rows, ns, use4=False, label=''):
    """rows: 升序 [{d,o,h,l,c,v}]"""
    cs = [r['c'] for r in rows]
    hs = [r['h'] for r in rows]
    ls = [r['l'] for r in rows]
    vs = [r['v'] for r in rows]
    mas = mas_of(cs, ns)
    tr, tr_desc = trend_of(cs, mas, use4)
    d = {
        'label': label, 'n': len(rows), 'date': rows[-1]['d'], 'close': cs[-1],
        'mas': {k: (round(v, 4) if v is not None else None) for k, v in mas.items()},
        'ma_order': tr_desc, 'trend_class': tr,
    }
    m = macd(cs)
    if m:
        cross_state = '金叉' if m['dif'] > m['dea'] else '死叉'
        # 交叉时点判定
        if m['dif'] > m['dea'] and m['dif_prev'] <= m['dea_prev']:
            cross_state = '刚金叉'
        elif m['dif'] < m['dea'] and m['dif_prev'] >= m['dea_prev']:
            cross_state = '刚死叉'
        d['macd'] = {'dif': round(m['dif'], 4), 'dea': round(m['dea'], 4),
                     'hist': round(m['hist'], 4), 'state': cross_state,
                     'above0': m['dif'] > 0 and m['dea'] > 0,
                     'below0': m['dif'] < 0 and m['dea'] < 0}
    return d


def gap_scan(days, limit=11.0, win=130):
    """检测疑似除权/异常跳空: |涨跌幅| 超过 limit% 的交易日"""
    hits = []
    rows = days[-win:]
    for i in range(1, len(rows)):
        prev = rows[i - 1]['c']
        cur = rows[i]['c']
        if prev <= 0:
            continue
        r = (cur - prev) / prev * 100
        # 只看向下跳空（除息/除权导致，涨停不可能超过 limit 太多）
        if r < -limit:
            hits.append({'date': rows[i]['d'], 'ret': round(r, 2),
                         'prev_c': prev, 'c': cur})
    return hits


# ---------- 主流程 ----------
def run():
    src = json.load(open(os.path.join(OUT, 'blocks_parsed.json'), encoding='utf-8'))
    cov = {r['mkt'] + r['code']: r for r in
           json.load(open(os.path.join(OUT, 'day_coverage.json'), encoding='utf-8'))['rows']}

    res = {}
    for bk, info in src.items():
        members = []
        for x in info['members']:
            mkt, code, name = x['mkt'], x['code'], x['name']
            key = mkt + code
            days = read_day(day_path(mkt, code))
            item = {'mkt': mkt, 'code': code, 'name': name, 'blk_raw': x['raw'],
                    'is_etf': (mkt == 'SH' and code.startswith(('5', '1'))) or code.startswith('15'),
                    'xd_flag': name.startswith(('XD', 'XR', 'DR'))}
            c = cov.get(key, {})
            item['cov'] = {'n': c.get('n'), 'last': c.get('last'),
                           'miss130': c.get('miss130') or []}
            if not days:
                item['ok'] = False
                item['err'] = '无日线文件'
                members.append(item)
                continue

            days, adj = apply_adj(days, code)
            item['adj'] = adj

            d = days[-DAILY_N:]
            w = to_week(days)[-WEEK_N:]
            m = to_month(days)[-MONTH_N:]

            item['ok'] = True
            item['daily'] = analyze_period(d, [5, 10, 20, 60, 120], use4=True, label='日线')
            item['daily']['rsi14'] = round(rsi([r['c'] for r in d]), 2) if rsi([r['c'] for r in d]) is not None else None
            item['daily']['kdj'] = {k: round(v, 2) for k, v in
                                    kdj([r['h'] for r in d], [r['l'] for r in d], [r['c'] for r in d]).items()}
            bb = boll([r['c'] for r in d])
            item['daily']['boll'] = {k: (round(v, 4) if v is not None else None) for k, v in bb.items()} if bb else None
            item['daily']['atr14'] = round(atr([r['h'] for r in d], [r['l'] for r in d], [r['c'] for r in d]), 3)
            item['daily']['atr_pct'] = round(item['daily']['atr14'] / d[-1]['c'] * 100, 2) if item['daily']['atr14'] else None
            # 量能
            vs = [r['v'] for r in d]
            v5, v20, v60 = sma(vs, 5), sma(vs, 20), sma(vs, 60)
            item['daily']['vol'] = {
                'v': d[-1]['v'], 'v5': round(v5) if v5 else None,
                'v20': round(v20) if v20 else None, 'v60': round(v60) if v60 else None,
                'vr5': round(d[-1]['v'] / v5, 2) if v5 else None,
                'vr20': round(d[-1]['v'] / v20, 2) if v20 else None,
                'v5_over_v20': round(v5 / v20, 2) if (v5 and v20) else None,
                'amt': d[-1]['amt']}
            # 收益率
            cs = [r['c'] for r in d]
            item['daily']['ret'] = {'d1': round(pct(cs[-1], cs[-2]), 2) if len(cs) > 1 else None,
                                    'w1': round(pct(cs[-1], cs[-6]), 2) if len(cs) > 6 else None,
                                    'm1': round(pct(cs[-1], cs[-21]), 2) if len(cs) > 21 else None,
                                    'm3': round(pct(cs[-1], cs[-61]), 2) if len(cs) > 61 else None}
            # 位置
            mas = item['daily']['mas']
            item['daily']['bias'] = {'ma5': round(pct(cs[-1], mas['ma5']), 2) if mas.get('ma5') else None,
                                     'ma20': round(pct(cs[-1], mas['ma20']), 2) if mas.get('ma20') else None,
                                     'ma60': round(pct(cs[-1], mas['ma60']), 2) if mas.get('ma60') else None}
            # 52周高低
            hi520 = max(h for h in [r['h'] for r in d[-250:]]) if len(d) >= 100 else None
            lo520 = min(l for l in [r['l'] for r in d[-250:]]) if len(d) >= 100 else None
            item['daily']['range250'] = {'high': hi520, 'low': lo520,
                                         'pos': round((cs[-1] - lo520) / (hi520 - lo520) * 100, 1) if hi520 and hi520 > lo520 else None,
                                         'drawdown': round(pct(cs[-1], hi520), 2) if hi520 else None}
            item['gaps'] = gap_scan(days, limit=11.0, win=130)
            item['weekly'] = analyze_period(w, [5, 10, 20], label='周线')
            item['monthly'] = analyze_period(m, [5, 10, 20], label='月线')

            # MACD 背离（日线, 近60日）
            div = detect_divergence(d)
            item['daily']['divergence'] = div
            members.append(item)
        res[bk] = {'blk': info['blk'], 'members': members}
    json.dump(res, open(os.path.join(OUT, 'resonance_raw.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    n = sum(len(v['members']) for v in res.values())
    print('完成，共 %d 只，已写出 resonance_raw.json' % n)


def detect_divergence(days, look=60):
    """近 look 日内：价格创新高但 MACD hist/DIF 未创新高 -> 顶背离；反之底背离"""
    if len(days) < 40:
        return None
    seg = days[-look:]
    m = macd([r['c'] for r in seg])
    if not m:
        return None
    hs = m['hist_series']
    cs = [r['c'] for r in seg]
    # 顶背离：最近创新高
    top_cnt = sum(1 for i in range(1, len(cs)) if cs[i] >= max(cs) * 0.995)
    if cs[-1] >= max(cs) - 1e-9:
        prev_high_i = None
        prev_max = -1e18
        for i in range(len(cs) - 20):
            if cs[i] > prev_max:
                prev_max, prev_high_i = cs[i], i
        if prev_high_i is not None and cs[-1] > cs[prev_high_i] and hs[-1] < hs[prev_high_i]:
            return {'type': '顶背离', 'note': '价格新高而MACD柱未同步走高'}
    if cs[-1] <= min(cs) + 1e-9:
        prev_min = 1e18
        pi = None
        for i in range(len(cs) - 20):
            if cs[i] < prev_min:
                prev_min, pi = cs[i], i
        if pi is not None and cs[-1] < cs[pi] and hs[-1] > hs[pi]:
            return {'type': '底背离', 'note': '价格新低而MACD柱未同步走低'}
    return None


if __name__ == '__main__':
    run()
