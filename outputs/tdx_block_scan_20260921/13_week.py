# -*- coding: utf-8 -*-
"""本周剩余交易日视角：计算"本周收盘价阈值"——周线 MACD 柱翻正 / 周线站上 MA4·MA12 / 收复上周高点所需价格。"""
import os, json, datetime as dt

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


def ema_series(x, n):
    a = 2.0 / (n + 1)
    out, prev = [], None
    for v in x:
        prev = v if prev is None else a * v + (1 - a) * prev
        out.append(prev)
    return out


def macd_last(cl):
    ef, es = ema_series(cl, 12), ema_series(cl, 26)
    dif = [a - b for a, b in zip(ef, es)]
    dea = ema_series(dif, 9)
    return dif[-1], dea[-1], (dif[-1] - dea[-1]) * 2


def weekly(bars):
    wk = {}
    for b in bars:
        d = dt.datetime.strptime(b['date'], '%Y%m%d').date()
        key = d.isocalendar()[:2]
        w = wk.setdefault(key, {'open': b['open'], 'high': b['high'], 'low': b['low'],
                                'close': b['close'], 'vol': 0})
        w['high'] = max(w['high'], b['high']); w['low'] = min(w['low'], b['low'])
        w['close'] = b['close']; w['vol'] += b['vol']
    return [wk[k] for k in sorted(wk)]


res = {}
for full, raw in BARS.items():
    raw = sorted(raw, key=lambda r: r['date'])
    a = adjust(raw, full)
    if len(a) < 150:
        continue
    w = weekly(a)
    if len(w) < 35:
        continue
    P = w[-1]['close']                      # 本周（不完整）当前价
    wc_prev = [x['close'] for x in w[:-1]]  # 截至上周的完整周收盘序列
    # --- 周线 MACD 柱翻正阈值：hist(Px) 关于 Px 线性 ---
    def hist_at(px):
        return macd_last(wc_prev + [px])[2]
    h0, h1 = hist_at(0.0), hist_at(1.0)
    p_macd0 = -h0 / (h1 - h0) if abs(h1 - h0) > 1e-12 else None
    dif_now, dea_now, hist_now = macd_last(wc_prev + [P])
    dif_prev, dea_prev, hist_prev = macd_last(wc_prev)   # 剔除本周（上周收盘时的周线状态）
    # --- 周线 MA4 / MA12 阈值：P > S/(n-1) ---
    s3 = sum(wc_prev[-3:])          # 前 3 周
    s11 = sum(wc_prev[-11:])        # 前 11 周
    p_ma4 = s3 / 3.0
    p_ma12 = s11 / 11.0
    # --- 上周高低点 ---
    last_w = w[-2]
    p_upper = last_w['high']
    p_lower = last_w['low']
    wk_open = w[-1]['open']         # 本周开盘（周一）
    ind = rows[full]['ind']
    lab = rows[full]['lab']
    d = {
        'name': rows[full]['name'], 'block': rows[full]['block'], 'close': P,
        'wk_open': round(wk_open, 2), 'wk_chg': round((P / wk_open - 1) * 100, 2),
        'p_macd0': round(p_macd0, 2) if p_macd0 is not None else None,
        'macd_hist_now': round(hist_now, 3), 'macd_hist_lastwk': round(hist_prev, 3),
        'dif_now': round(dif_now, 2), 'dea_now': round(dea_now, 2),
        'p_ma4': round(p_ma4, 2), 'p_ma12': round(p_ma12, 2),
        'p_upper': round(p_upper, 2), 'p_lower': round(p_lower, 2),
        'gap_macd0': round((p_macd0 / P - 1) * 100, 2) if p_macd0 else None,
        'gap_ma4': round((p_ma4 / P - 1) * 100, 2),
        'gap_ma12': round((p_ma12 / P - 1) * 100, 2),
        'gap_upper': round((p_upper / P - 1) * 100, 2),
        'above_ma4': P > p_ma4, 'above_ma12': P > p_ma12,
        'hist_pos': hist_now > 0, 'hist_pos_lastwk': hist_prev > 0,
        'wma4': ind['weekly']['ma']['4'], 'wma12': ind['weekly']['ma']['12'],
        'res_near': lab['res_near'], 'res_space': lab['res_space'],
        'sup_near': lab['sup_near'], 'sup_space': lab['sup_space'],
        'pos60': ind['pos60'], 'bias20': lab['bias20'], 'rsi14': ind['rsi14'],
        'vr5': ind['vr5'], 'chg5': ind['chg5'], 'chg20': ind['chg20'],
        'mom_d': lab['mom_d'], 'mom_w': lab['mom_w'], 'trend_d': lab['trend_d'],
        'trend_w': lab['trend_w'], 'atr_pct': ind['atr_pct'], 'volprice': lab['volprice'],
        'kdj_j': ind['kdj']['j'], 'is_etf': full in ETF,
    }
    res[full] = d

json.dump(res, open(os.path.join(OUTDIR, 'week_thresholds.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('计算完成:', len(res))

for blk in ['关注个股', 'AI硬件']:
    sel = [(k, v) for k, v in res.items() if v['block'] == blk and not v['is_etf']]
    print(f'\n{"="*118}\n【{blk}】周线阈值一览（现价 vs 本周收盘需达到的价位）  共 {len(sel)} 只')
    print(f"{'代码':<10}{'名称':<9}{'现价':>9}{'周内%':>7}{'周线柱(上周)':>13}{'柱翻正需':>10}{'距%':>7}"
          f"{'站上周MA4需':>12}{'距%':>7}{'站上周MA12需':>13}{'距%':>7}{'收复上周高需':>13}{'距%':>7}")
    for k, v in sorted(sel, key=lambda x: abs(x[1]['gap_macd0'] or 99)):
        print(f"{k:<10}{v['name']:<9}{v['close']:>9.2f}{v['wk_chg']:>7.2f}{v['macd_hist_lastwk']:>13.3f}"
              f"{(v['p_macd0'] if v['p_macd0'] else 0):>10.2f}{str(v['gap_macd0']):>7}"
              f"{v['p_ma4']:>12.2f}{v['gap_ma4']:>7}{v['p_ma12']:>13.2f}{v['gap_ma12']:>7}"
              f"{v['p_upper']:>13.2f}{v['gap_upper']:>7}")
