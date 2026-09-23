# -*- coding: utf-8 -*-
"""定性标签化 + 大盘背景 + 分层筛选（不使用任何综合评分）。"""
import os, json

OUTDIR = r'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260921'
IND = json.load(open(os.path.join(OUTDIR, 'indicators.json'), encoding='utf-8'))
MEM = json.load(open(os.path.join(OUTDIR, 'block_members.json'), encoding='utf-8'))
NAME = {}
for t, v in MEM.items():
    for m in v['members']:
        NAME[m['full']] = m['name']
BLO = {m['full']: t for t, v in MEM.items() for m in v['members']}


def label(r):
    c, ma = r['close'], r['ma']
    m5, m10, m20, m60 = ma['5'], ma['10'], ma['20'], ma['60']
    m120 = ma.get('120')
    w = r['weekly']
    wma = w['ma']
    out = {}
    # 日线趋势
    if m5 and m20 and m60:
        if c > m20 and m20 > m60 and m5 >= m10:
            out['trend_d'] = 'up'
        elif c < m20 and m20 < m60 and m5 <= m10:
            out['trend_d'] = 'down'
        else:
            out['trend_d'] = 'range'
    else:
        out['trend_d'] = 'n/a'
    # 周线趋势
    if wma['4'] and wma['12']:
        if c > wma['4'] and wma['4'] > wma['12']:
            out['trend_w'] = 'up'
        elif c < wma['4'] and wma['4'] < wma['12']:
            out['trend_w'] = 'down'
        else:
            out['trend_w'] = 'range'
    else:
        out['trend_w'] = 'n/a'
    # 量价
    vr5, vr20 = r['vr5'] or 0, r['vr20'] or 0
    chg5 = r['chg5'] or 0
    if chg5 > 0 and vr5 >= 1.2:
        out['volprice'] = '放量上涨'
    elif chg5 > 0 and vr5 < 1.0:
        out['volprice'] = '缩量上涨'
    elif chg5 <= 0 and vr5 >= 1.2:
        out['volprice'] = '放量下跌'
    else:
        out['volprice'] = '缩量回调'
    # 动量（日线 MACD）
    mc = r['macd']
    if mc:
        dif, dea, h, hp = mc['dif'], mc['dea'], mc['hist'], mc['hist_prev']
        if h > 0 and hp <= 0:
            out['mom_d'] = 'MACD零上金叉' if dif > 0 else 'MACD零下金叉'
        elif h > 0 and h > hp:
            out['mom_d'] = '多头动能放大'
        elif h > 0:
            out['mom_d'] = '多头动能收敛'
        elif h < 0 and hp >= 0:
            out['mom_d'] = 'MACD死叉' + ('（零上）' if dif > 0 else '（零下）')
        elif h < 0 and h > hp:
            out['mom_d'] = '空头动能收敛'
        else:
            out['mom_d'] = '空头动能放大'
        out['macd_zone'] = '零上' if dif > 0 and dea > 0 else ('零下' if dif < 0 and dea < 0 else '跨零')
    else:
        out['mom_d'] = 'n/a'; out['macd_zone'] = 'n/a'
    # 周线动量
    wm = w.get('macd')
    if wm:
        if wm['hist'] > 0 and wm['dif'] > 0:
            out['mom_w'] = '周线多头' + ('（走强）' if wm['dif'] > wm['dea'] else '')
        elif wm['hist'] > 0:
            out['mom_w'] = '周线零下金叉'
        else:
            out['mom_w'] = '周线空头' + ('（收敛）' if wm['dif'] < wm['dea'] else '')
    else:
        out['mom_w'] = 'n/a'
    # 位置
    p60 = r['pos60']
    if p60 is None:
        out['position'] = 'n/a'
    elif p60 >= 90:
        out['position'] = '60日区间高位'
    elif p60 >= 65:
        out['position'] = '中高位'
    elif p60 >= 35:
        out['position'] = '中位'
    elif p60 >= 15:
        out['position'] = '中低位'
    else:
        out['position'] = '60日区间低位'
    # 风险标记
    risks = []
    if r['rsi14'] and r['rsi14'] >= 75: risks.append('RSI超买')
    if r['rsi14'] and r['rsi14'] <= 30: risks.append('RSI超卖')
    if m20 and (c / m20 - 1) * 100 >= 20: risks.append('乖离MA20过大')
    if r['atr_pct'] and r['atr_pct'] >= 7: risks.append('波动率极高')
    if r['pos60'] is not None and r['pos60'] >= 97: risks.append('贴60日高点')
    if out['trend_d'] == 'down': risks.append('日线空头排列')
    out['risks'] = risks
    out['bias20'] = round((c / m20 - 1) * 100, 2) if m20 else None
    # 关键位（近60日分形极值）
    sh = [p for d, p in r['swing_highs'] if p > c]
    sl = [p for d, p in r['swing_lows'] if p < c]
    out['res_near'] = round(min(sh), 2) if sh else round(r['hi60'], 2)
    out['sup_near'] = round(max(sl), 2) if sl else round(r['lo60'], 2)
    out['res_space'] = round((min(sh) / c - 1) * 100, 2) if sh else round((r['hi60'] / c - 1) * 100, 2)
    out['sup_space'] = round((c / max(sl) - 1) * 100, 2) if sl else round((c / r['lo60'] - 1) * 100, 2)
    return out


rows = []
for k, r in IND.items():
    lab = label(r)
    rows.append({'full': k, 'name': NAME.get(k, '?'), 'block': BLO.get(k, '?'), 'ind': r, 'lab': lab})

rows.sort(key=lambda x: (x['block'], -(x['ind']['chg20'] or 0)))

# 大盘背景
import struct
def read_idx(p, n=200):
    raw = open(p, 'rb').read()
    cnt = len(raw) // 32
    out = []
    for i in range(max(0, cnt - n), cnt):
        o = i * 32
        d, op, hi, lo, cl, amt, vol, _ = struct.unpack('<IIIIIfII', raw[o:o + 32])
        out.append({'date': str(d), 'close': cl / 100.0, 'vol': vol})
    return out

def sma(x, n):
    return sum(x[-n:]) / n if len(x) >= n else None

def macd_simple(cl, f=12, s=26, sg=9):
    def ema(v, n):
        a = 2 / (n + 1); p = None; o = []
        for x in v:
            p = x if p is None else a * x + (1 - a) * p
            o.append(p)
        return o
    ef, es = ema(cl, f), ema(cl, s)
    dif = [a - b for a, b in zip(ef, es)]
    dea = ema(dif, sg)
    return dif[-1], dea[-1], (dif[-1] - dea[-1]) * 2

idx = {}
for nm, p in [('上证指数', r'D:/HT/vipdoc/sh/lday/sh000001.day'),
              ('深证成指', r'D:/HT/vipdoc/sz/lday/sz399001.day'),
              ('创业板指', r'D:/HT/vipdoc/sz/lday/sz399006.day'),
              ('科创50', r'D:/HT/vipdoc/sh/lday/sh000688.day'),
              ('中证1000', r'D:/HT/vipdoc/sh/lday/sh000852.day')]:
    try:
        b = read_idx(p)
        cl = [x['close'] for x in b]
        vo = [x['vol'] for x in b]
        idx[nm] = {'close': round(cl[-1], 2), 'ma20': round(sma(cl, 20), 2), 'ma60': round(sma(cl, 60), 2),
                   'chg5': round((cl[-1] / cl[-6] - 1) * 100, 2), 'chg20': round((cl[-1] / cl[-21] - 1) * 100, 2),
                   'vr5': round(vo[-1] / sma(vo, 5), 2), 'macd': [round(x, 2) for x in macd_simple(cl)],
                   'as_of': b[-1]['date']}
    except Exception as e:
        idx[nm] = 'ERR ' + str(e)

print('=== 大盘背景 ===')
for k, v in idx.items():
    print(k, v)

print('\n=== 关注个股板块 ===')
print(f"{'代码':<10}{'名称':<10}{'收盘':>9}{'趋势':>6}{'周趋势':>7}{'量价':>9}{'MACD':>14}{'周线':>10}{'位置':>12}{'pos60':>7}{'BIAS20':>8}{'RSI':>6}{'J':>7}{'VR5':>6}{'压力空间':>8}{'支撑空间':>8}")
for r in rows:
    if r['block'] != '关注个股': continue
    i, l = r['ind'], r['lab']
    print(f"{r['full']:<10}{r['name']:<10}{i['close']:>9.2f}{l['trend_d']:>6}{l['trend_w']:>7}{l['volprice']:>11}"
          f"{l['mom_d']:>14}{l['mom_w']:>13}{l['position']:>12}{str(i['pos60']):>7}{str(l['bias20']):>8}"
          f"{str(i['rsi14']):>6}{str(i['kdj']['j']):>7}{str(i['vr5']):>6}{str(l['res_space'])+'%':>9}{str(l['sup_space'])+'%':>9}")

print('\n=== AI硬件板块 ===')
print(f"{'代码':<10}{'名称':<10}{'收盘':>9}{'趋势':>6}{'周趋势':>7}{'量价':>11}{'MACD':>14}{'周线':>13}{'位置':>12}{'pos60':>7}{'BIAS20':>8}{'RSI':>6}{'J':>7}{'VR5':>6}{'压力空间':>9}{'支撑空间':>9}")
for r in rows:
    if r['block'] != 'AI硬件': continue
    i, l = r['ind'], r['lab']
    print(f"{r['full']:<10}{r['name']:<10}{i['close']:>9.2f}{l['trend_d']:>6}{l['trend_w']:>7}{l['volprice']:>11}"
          f"{l['mom_d']:>14}{l['mom_w']:>13}{l['position']:>12}{str(i['pos60']):>7}{str(l['bias20']):>8}"
          f"{str(i['rsi14']):>6}{str(i['kdj']['j']):>7}{str(i['vr5']):>6}{str(l['res_space'])+'%':>9}{str(l['sup_space'])+'%':>9}")

json.dump({'rows': rows, 'index': idx}, open(os.path.join(OUTDIR, 'labeled.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('\n已保存 labeled.json')
