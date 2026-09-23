# -*- coding: utf-8 -*-
"""次级候选：大周期多头 + 中短期休整充分（区别于 A 档的即时共振向上）。"""
import json, os

OUT = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(os.path.join(OUT, 'resonance_raw.json'), encoding='utf-8'))


def cls2dir(t):
    if t in ('bull', 'bull_pull'):
        return 'up'
    if t in ('bear', 'bear_bounce'):
        return 'dn'
    return 'osc'


rows = []
for bk, info in raw.items():
    for it in info['members']:
        if not it.get('ok') or it.get('is_etf'):
            continue
        if it['cov']['n'] and it['cov']['n'] < 60:
            continue
        d, w, m = it['daily'], it['weekly'], it['monthly']
        rows.append({'block': bk, 'code': it['code'], 'name': it['name'], 'mkt': it['mkt'],
                     'dirs': (cls2dir(d['trend_class']), cls2dir(w['trend_class']), cls2dir(m['trend_class'])),
                     'close': d['close'], 'rsi': d['rsi14'], 'bias': d['bias'], 'rng': d['range250'],
                     'ret': d['ret'], 'vol': d['vol'], 'atrp': d['atr_pct'],
                     'dmacd': d.get('macd'), 'wmacd': w.get('macd'), 'mmacd': m.get('macd'),
                     'dma': d['mas'], 'wma': w['mas'], 'mma': m['mas'],
                     'dcls': d['trend_class'], 'wcls': w['trend_class'], 'mcls': m['trend_class'],
                     'div': d.get('divergence'), 'xd': it.get('xd_flag'), 'adj': it.get('adj')})

SY = {'up': '↑', 'dn': '↓', 'osc': '→'}


def line(r):
    return ('%-8s %-9s 日%s周%s月%s | 收%8.2f | BIAS20 %6.1f%% | RSI %5.1f | 回撤%6.1f%% | 52周位%5s%% '
            '| 月涨%6s%% 3月%7s%% | VR5 %.2f | 周MACD %s' % (
                r['code'], r['name'], SY[r['dirs'][0]], SY[r['dirs'][1]], SY[r['dirs'][2]],
                r['close'], r['bias']['ma20'], r['rsi'], r['rng']['drawdown'], r['rng']['pos'],
                r['ret']['m1'], r['ret']['m3'], r['vol']['vr5'],
                (r['wmacd'] or {}).get('state', 'NA')))


# 集合1: 周↑ 且 月↑ (大周期双多)，日线非共振向上(已在A档)
s1 = [r for r in rows if r['dirs'][1] == 'up' and r['dirs'][2] == 'up' and r['dirs'][0] != 'up']
print('=== 集合1: 周线↑ + 月线↑，日线未同步向上 (%d 只) ===' % len(s1))
for r in sorted(s1, key=lambda x: x['rng']['drawdown'] or 0):
    flags = []
    if r['bias']['ma20'] > 25:
        flags.append('偏离大')
    if r['rsi'] > 80:
        flags.append('RSI超买')
    if (r['rng']['drawdown'] or 0) < -45:
        flags.append('回撤过深')
    if r['vol']['v5_over_v20'] and r['vol']['v5_over_v20'] < 0.8:
        flags.append('量缩')
    print('  ' + line(r) + '  | %s' % ('、'.join(flags) or '✅'))

# 集合2: 日↑ + 月↑，周线整理
s2 = [r for r in rows if r['dirs'][0] == 'up' and r['dirs'][2] == 'up' and r['dirs'][1] == 'osc']
print('\n=== 集合2: 日线↑ + 月线↑，周线整理 (%d 只) ===' % len(s2))
for r in sorted(s2, key=lambda x: x['rng']['drawdown'] or 0):
    flags = []
    if r['bias']['ma20'] > 25:
        flags.append('偏离大')
    if r['rsi'] > 80:
        flags.append('RSI超买')
    if (r['rng']['drawdown'] or 0) < -45:
        flags.append('回撤过深')
    print('  ' + line(r) + '  | %s' % ('、'.join(flags) or '✅'))

# 集合3: 月↑ 但周线走弱，且日线已企稳/反弹、回撤充分 —— 反转观察
s3 = [r for r in rows if r['dirs'][2] == 'up' and r['dirs'][1] == 'dn'
      and r['dirs'][0] in ('up', 'osc')]
print('\n=== 集合3: 月线↑ + 周线↓ + 日线↑/→ (%d 只) ===' % len(s3))
for r in sorted(s3, key=lambda x: x['rng']['drawdown'] or 0):
    flags = []
    if (r['rng']['drawdown'] or 0) < -45:
        flags.append('回撤过深')
    if r['rsi'] > 80:
        flags.append('RSI超买')
    print('  ' + line(r) + '  | %s' % ('、'.join(flags) or '✅'))

json.dump(rows, open(os.path.join(OUT, 'cand_rows.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, default=str)
print('\n已写出 cand_rows.json')
