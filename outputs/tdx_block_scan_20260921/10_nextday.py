# -*- coding: utf-8 -*-
"""明日盯盘视角：短期临界度指标（K线形态 / 量能异动 / 指标临界翻转 / 缺口 / 连涨跌）。"""
import os, json, math

OUTDIR = r'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260921'
BARS = json.load(open(os.path.join(OUTDIR, 'bars_raw.json'), encoding='utf-8'))['bars']
LAB = json.load(open(os.path.join(OUTDIR, 'labeled.json'), encoding='utf-8'))
rows = {r['full']: r for r in LAB['rows']}
ETF = {'SH515880'}


def limit_of(full):
    mkt, code = full[:2], full[2:]
    if mkt == 'BJ':
        return 0.305
    if code.startswith(('688', '300', '301')):
        return 0.205
    return 0.105


def adjust(bars, full):
    lim = limit_of(full)
    n = len(bars)
    fac = [1.0] * n
    f = 1.0
    for i in range(n - 1, 0, -1):
        prev, cur = bars[i - 1]['close'], bars[i]['close']
        if prev <= 0:
            continue
        if abs(cur / prev - 1) > lim:
            f *= cur / prev
        fac[i - 1] = f
    return [{'date': b['date'], 'open': b['open'] * fac[i], 'high': b['high'] * fac[i],
             'low': b['low'] * fac[i], 'close': b['close'] * fac[i], 'vol': b['vol']}
            for i, b in enumerate(bars)]


def candle(b, p):
    """识别单根 K 线形态（b=今日, p=昨日）"""
    o, h, l, c = b['open'], b['high'], b['low'], b['close']
    rng = h - l
    body = abs(c - o)
    tags = []
    if rng <= 0:
        return ['一字/停牌']
    if body / rng < 0.10:
        tags.append('十字星')
    up_sh = (h - max(o, c)) / rng
    dn_sh = (min(o, c) - l) / rng
    if up_sh > 0.5:
        tags.append('长上影')
    if dn_sh > 0.5:
        tags.append('长下影')
    if body / p['close'] > 0.05:
        tags.append('大阳线' if c > o else '大阴线')
    # 吞没 / 孕线
    pb_hi, pb_lo = max(p['open'], p['close']), min(p['open'], p['close'])
    b_hi, b_lo = max(o, c), min(o, c)
    if (c > o) and (p['close'] < p['open']) and b_hi >= pb_hi and b_lo <= pb_lo:
        tags.append('看涨吞没')
    if (c < o) and (p['close'] > p['open']) and b_hi >= pb_hi and b_lo <= pb_lo:
        tags.append('看跌吞没')
    if b_hi <= pb_hi and b_lo >= pb_lo and body / rng < 0.6:
        tags.append('孕线')
    return tags


def sma(x, n):
    return sum(x[-n:]) / n if len(x) >= n else None


res = {}
for full, raw in BARS.items():
    raw = sorted(raw, key=lambda r: r['date'])
    a = adjust(raw, full)
    if len(a) < 30:
        continue
    t, p = a[-1], a[-2]
    c = t['close']
    closes = [x['close'] for x in a]
    vols = [x['vol'] for x in a]
    lab = rows[full]['lab']
    ind = rows[full]['ind']
    # 量能
    v5 = sma(vols, 5); v20 = sma(vols, 20)
    vr5 = vols[-1] / v5 if v5 else None
    vr20 = vols[-1] / v20 if v20 else None
    # 量能趋势：近3日均量 / 近10日均量
    vt = sma(vols, 3) / sma(vols, 10) if len(vols) >= 10 else None
    # 指标临界
    kd = ind['kdj']
    kd_gap = round(kd['k'] - kd['d'], 2) if kd else None
    mc = ind['macd']
    hist_ratio = round(abs(mc['hist']) / (abs(mc['dif']) + abs(mc['dea']) + 1e-9), 4) if mc else None
    bl = ind['boll']
    boll_pos = None
    if bl:
        w = bl['up'] - bl['dn']
        boll_pos = round((c - bl['dn']) / w * 100, 1) if w > 0 else None
    # 连涨跌
    up = dn = 0
    for i in range(len(a) - 1, 0, -1):
        if a[i]['close'] > a[i - 1]['close']:
            if dn: break
            up += 1
        elif a[i]['close'] < a[i - 1]['close']:
            if up: break
            dn += 1
        else:
            break
    # 缺口
    gap = None
    if t['low'] > p['high']:
        gap = ('向上跳空', round((t['low'] / p['high'] - 1) * 100, 2), round(p['high'], 2))
    elif t['high'] < p['low']:
        gap = ('向下跳空', round((t['high'] / p['low'] - 1) * 100, 2), round(p['low'], 2))
    # 阶段新高/新低
    hi20 = max(x['high'] for x in a[-20:]); lo20 = min(x['low'] for x in a[-20:])
    new_hi20 = c >= hi20 * 0.999
    new_lo20 = c <= lo20 * 1.001
    # 临界位距离
    d_res = lab['res_space']; d_sup = lab['sup_space']
    near_res = d_res is not None and d_res <= 1.5
    near_sup = d_sup is not None and d_sup <= 1.5
    res[full] = {
        'name': rows[full]['name'], 'block': rows[full]['block'], 'close': c,
        'chg1': round((c / p['close'] - 1) * 100, 2),
        'candle': candle(t, p), 'vr5': round(vr5, 2) if vr5 else None,
        'vr20': round(vr20, 2) if vr20 else None, 'vtrend': round(vt, 2) if vt else None,
        'kd_gap': kd_gap, 'hist_ratio': hist_ratio, 'boll_pos': boll_pos,
        'rsi14': ind['rsi14'], 'j': kd['j'] if kd else None,
        'consec_up': up, 'consec_dn': dn, 'gap': gap,
        'new_hi20': new_hi20, 'new_lo20': new_lo20,
        'res_near': lab['res_near'], 'res_space': d_res,
        'sup_near': lab['sup_near'], 'sup_space': d_sup,
        'ma5': ind['ma']['5'], 'ma10': ind['ma']['10'], 'ma20': ind['ma']['20'], 'ma60': ind['ma']['60'],
        'pos60': ind['pos60'], 'bias20': lab['bias20'], 'atr_pct': ind['atr_pct'],
        'mom_d': lab['mom_d'], 'volprice': lab['volprice'], 'trend_d': lab['trend_d'],
        'is_etf': full in ETF, 'n_bars': len(a),
    }

json.dump(res, open(os.path.join(OUTDIR, 'nextday.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ===== 明日盯盘价值分组 =====
def grade(r):
    """临界度条件计数（观察价值，非涨幅预测）"""
    cond = {}
    cond['临界位'] = (r['res_space'] is not None and r['res_space'] <= 1.5) or \
                     (r['sup_space'] is not None and r['sup_space'] <= 1.5)
    cond['量能异动'] = (r['vr5'] is not None and (r['vr5'] >= 1.5 or r['vr5'] <= 0.6))
    cond['指标临界'] = (r['kd_gap'] is not None and abs(r['kd_gap']) <= 3) or \
                      (r['hist_ratio'] is not None and r['hist_ratio'] <= 0.03)
    cond['变盘K线'] = bool(set(r['candle']) & {'十字星', '看涨吞没', '看跌吞没', '孕线', '长上影', '长下影'})
    cond['缺口未定'] = r['gap'] is not None
    cond['阶段新高/低'] = r['new_hi20'] or r['new_lo20']
    return cond, sum(cond.values())


for blk in ['关注个股', 'AI硬件']:
    sel = [(k, v) for k, v in res.items() if v['block'] == blk and not v['is_etf'] and v['n_bars'] >= 60]
    out = []
    for k, v in sel:
        cond, n = grade(v)
        out.append((n, k, v, cond))
    out.sort(key=lambda x: (-x[0], x[1]))
    print(f'\n{"="*110}\n【{blk}】明日盯盘临界度排序（命中条件数）  共 {len(out)} 只')
    for n, k, v, cond in out[:22]:
        hit = ' '.join([c for c, b in cond.items() if b])
        print(f"{n}项 {k} {v['name']:<8} 收{v['close']:>9.2f} 昨涨{v['chg1']:>6.2f}% | {hit}")
        print(f"     K线={'+'.join(v['candle']) or '—'} 量比5={v['vr5']} 量比20={v['vr20']} 量能趋势={v['vtrend']} | "
              f"KD差={v['kd_gap']} J={v['j']} MACD柱比={v['hist_ratio']} BOLL位置={v['boll_pos']}% | "
              f"连涨{v['consec_up']}/连跌{v['consec_dn']} 缺口={v['gap']} 新高20={v['new_hi20']} 新低20={v['new_lo20']}")
        print(f"     压{v['res_near']}(+{v['res_space']}%) 支{v['sup_near']}(-{v['sup_space']}%) | "
              f"MA5={v['ma5']} MA10={v['ma10']} MA20={v['ma20']} | {v['mom_d']} {v['volprice']} pos60={v['pos60']}")
