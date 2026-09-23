# -*- coding: utf-8 -*-
"""汇总多周期共振结果：分级、过滤、排序（定性分层，不做综合加权打分）。"""
import json, os, collections

OUT = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(os.path.join(OUT, 'resonance_raw.json'), encoding='utf-8'))

TR_SYMBOL = {'bull': '↑', 'bull_pull': '↑*', 'bear': '↓', 'bear_bounce': '↓*', 'cross': '→', 'na': '?'}
CONF = {'res3_up': 90, 'res2_up': 70, 'res3_dn': 85, 'res2_dn': 68, 'mixed': 50}


def cls2dir(t):
    if t in ('bull', 'bull_pull'):
        return 'up'
    if t in ('bear', 'bear_bounce'):
        return 'dn'
    return 'osc'


def resonance_of(it):
    """返回 (状态标签, 类型key, 置信度)"""
    a, b, c = (cls2dir(it['daily']['trend_class']),
               cls2dir(it['weekly']['trend_class']),
               cls2dir(it['monthly']['trend_class']))
    if 'na' in (it['daily']['trend_class'], it['weekly']['trend_class'], it['monthly']['trend_class']):
        return (a, b, c), 'data_na', None, '数据不足'
    if a == 'up' and b == 'up' and c == 'up':
        return (a, b, c), 'res3_up', CONF['res3_up'], '三周期共振向上'
    if a == 'dn' and b == 'dn' and c == 'dn':
        return (a, b, c), 'res3_dn', CONF['res3_dn'], '三周期共振向下'
    if a == 'up' and b == 'up':
        return (a, b, c), 'res2_up', CONF['res2_up'], '日月/周共振多头' if c == 'dn' else '双周期多头'
    if a == 'dn' and b == 'dn':
        return (a, b, c), 'res2_dn', CONF['res2_dn'], '日周双空'
    return (a, b, c), 'mixed', CONF['mixed'], '周期错位/震荡'


def macd_sync(it):
    s = []
    for k, lab in (('daily', '日'), ('weekly', '周'), ('monthly', '月')):
        m = it.get(k, {}).get('macd')
        if not m:
            s.append(lab + 'NA')
            continue
        s.append('%s%s' % (lab, m['state']))
    return '/'.join(s)


rows = []
for bk, info in raw.items():
    for it in info['members']:
        if not it.get('ok'):
            rows.append({'block': bk, 'name': it['name'], 'code': it['code'], 'mkt': it['mkt'],
                         'err': it.get('err'), 'grp': 'NA', 'conf': 0, 'dirs': (None,) * 3,
                         'rlabel': '数据缺失', 'macd': '', 'is_etf': it.get('is_etf'), 'xd': it.get('xd_flag')})
            continue
        dirs, key, conf, lab = resonance_of(it)
        rows.append({'block': bk, 'name': it['name'], 'code': it['code'], 'mkt': it['mkt'],
                     'grp': key, 'conf': conf, 'dirs': dirs, 'rlabel': lab,
                     'macd': macd_sync(it), 'is_etf': it.get('is_etf'), 'xd': it.get('xd_flag'),
                     'close': it['daily']['close'], 'rsi': it['daily'].get('rsi14'),
                     'bias20': it['daily']['bias'].get('ma20'),
                     'ret_m1': it['daily']['ret'].get('m1'), 'ret_m3': it['daily']['ret'].get('m3'),
                     'vr5': it['daily']['vol'].get('vr5'), 'v5o20': it['daily']['vol'].get('v5_over_v20'),
                     'pos250': it['daily']['range250'].get('pos'),
                     'dd': it['daily']['range250'].get('drawdown'),
                     'atrp': it['daily'].get('atr_pct'),
                     'div': (it['daily'].get('divergence') or {}).get('type'),
                     'gaps': it.get('gaps') or [],
                     'miss': it['cov'].get('miss130') or [],
                     'k': it['daily']['kdj'].get('k'), 'j': it['daily']['kdj'].get('j'),
                     'dtrend': it['daily']['trend_class'], 'wtrend': it['weekly']['trend_class'],
                     'mtrend': it['monthly']['trend_class']})

print('== 板块共振类型分布 ==')
cnt = collections.Counter((r['block'], r['rlabel']) for r in rows)
for (b, l), n in sorted(cnt.items()):
    print('  %-8s %-16s %d' % (b, l, n))

print('\n== 数据标记 ==')
etf = [r for r in rows if r.get('is_etf')]
xd = [r for r in rows if r.get('xd')]
gp = [r for r in rows if r.get('gaps')]
ms = [r for r in rows if r.get('miss')]
print('ETF/基金(%d): %s' % (len(etf), ', '.join('%s%s' % (x['code'], x['name']) for x in etf)))
print('XD/XR标记(%d): %s' % (len(xd), ', '.join('%s%s' % (x['code'], x['name']) for x in xd)))
print('近130日向下跳空>11%%(%d只):' % len(gp))
for r in gp:
    print('   %s %s : %s' % (r['code'], r['name'], [(g['date'], g['ret']) for g in r['gaps']]))
print('130日窗口缺数据(%d只): %s' % (len(ms), ', '.join('%s%s(%d)' % (x['code'], x['name'], len(x['miss'])) for x in ms)))

print('\n== 三周期共振向上 名单 ==')
for r in sorted([x for x in rows if x['grp'] == 'res3_up'], key=lambda x: -(x['ret_m3'] or -99)):
    print('  %-8s %s%s  收%.2f  RSI%.1f  BIAS20 %.1f%%  月涨%.1f%%  3月%.1f%%  VR5 %.2f  位置%.0f%% 回撤%.1f%%  MACD:%s' %
          (r['block'], r['code'], r['name'], r['close'], r['rsi'], r['bias20'],
           r['ret_m1'], r['ret_m3'], r['vr5'], r['pos250'], r['dd'], r['macd']))

json.dump(rows, open(os.path.join(OUT, 'resonance_rows.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\n已写出 resonance_rows.json (%d 行)' % len(rows))
