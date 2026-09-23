# -*- coding: utf-8 -*-
"""最终筛选：多周期共振分层 + 过热/数据质量硬过滤（定性分层，不做加权打分）。"""
import json, os, collections

OUT = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(os.path.join(OUT, 'resonance_raw.json'), encoding='utf-8'))


def cls2dir(t):
    if t in ('bull', 'bull_pull'):
        return 'up'
    if t in ('bear', 'bear_bounce'):
        return 'dn'
    return 'osc'


def build():
    rows = []
    for bk, info in raw.items():
        for it in info['members']:
            mkt, code, name = it['mkt'], it['code'], it['name']
            base = {'block': bk, 'code': code, 'name': name, 'mkt': mkt,
                    'is_etf': it.get('is_etf'), 'xd': it.get('xd_flag'),
                    'adj': it.get('adj')}
            if not it.get('ok'):
                rows.append(dict(base, ok=False))
                continue
            d, w, m = it['daily'], it['weekly'], it['monthly']
            a, b, c = cls2dir(d['trend_class']), cls2dir(w['trend_class']), cls2dir(m['trend_class'])
            r = dict(base, ok=True, dirs=(a, b, c),
                     close=d['close'], close_w=w['close'],
                     dcls=d['trend_class'], wcls=w['trend_class'], mcls=m['trend_class'],
                     dma=d['mas'], wma=w['mas'], mma=m['mas'],
                     dmacd=d.get('macd'), wmacd=w.get('macd'), mmacd=m.get('macd'),
                     rsi=d.get('rsi14'), kdj=d.get('kdj'), boll=d.get('boll'),
                     atrp=d.get('atr_pct'), vol=d.get('vol'), ret=d.get('ret'),
                     bias=d.get('bias'), rng=d.get('range250'),
                     div=d.get('divergence'), date=d['date'],
                     cov=it.get('cov'))
            rows.append(r)
    return rows


rows = build()
print('总 %d 只，其中有效 %d 只' % (len(rows), sum(1 for r in rows if r.get('ok'))))

DIRN = {'up': '↑', 'dn': '↓', 'osc': '→'}
print('\n=== 三周期方向组合分布 (日/周/月) ===')
cnt = collections.Counter('%s%s%s' % tuple(DIRN[x] for x in r['dirs']) for r in rows if r.get('ok'))
for k, v in sorted(cnt.items(), key=lambda x: -x[1]):
    print('  日%s周%s月%s : %d' % (k[0], k[1], k[2], v))


def brief(r):
    return ('%-8s %-10s 收%8.2f | RSI%5.1f BIAS20 %6.1f%% | 52周位%3s%% 回撤%6s%% '
            '| 月涨%6.1f%% 3月%7.1f%% | VR5 %.2f | ATR%% %s' % (
                r['code'], r['name'], r['close'], r['rsi'], r['bias']['ma20'],
                r['rng']['pos'], r['rng']['drawdown'], r['ret']['m1'], r['ret']['m3'],
                r['vol']['vr5'], r['atrp']))


# ---- 硬过滤 ----
def hard_exclude(r):
    if not r.get('ok'):
        return '数据不可用(%s)' % (r.get('err', '缺日线文件'))
    if r.get('is_etf'):
        return '基金/ETF，不参与个股技术面筛选'
    if r['cov']['n'] and r['cov']['n'] < 60:
        return '上市不足60个交易日，MA60/月线不可靠'
    return None


keys = {('up', 'up', 'up'): 'A_共振向上',
        ('dn', 'up', 'up'): 'B_回调',
        ('up', 'up', 'dn'): 'C_反弹(月空)',
        ('up', 'up', 'osc'): 'C_反弹(月震荡)',
        ('dn', 'dn', 'dn'): 'D_共振向下'}

grp = collections.defaultdict(list)
for r in rows:
    ex = hard_exclude(r)
    if ex:
        grp['X_排除'].append((r, ex))
        continue
    k = keys.get(r['dirs'], 'E_其他/错位')
    grp[k].append((r, ''))

print('\n================ 分组明细 ================')
for k in ['A_共振向上', 'B_回调', 'C_反弹(月空)', 'C_反弹(月震荡)', 'D_共振向下', 'E_其他/错位', 'X_排除']:
    lst = grp.get(k, [])
    print('\n--- %s : %d 只 ---' % (k, len(lst)))
    if k == 'X_排除':
        for r, ex in lst:
            print('   %-8s %-10s  %s' % (r['code'], r['name'], ex))
        continue
    for r, _ in sorted(lst, key=lambda x: -(x[0]['ret']['m3'] or -99)):
        print('   ' + brief(r))

# ---- A 档过热再过滤 ----
print('\n\n================ A档(三周期共振向上) 质量甄别 ================')
print('%-8s %-10s %8s %7s %8s %8s %8s  %s' % ('代码', '名称', 'BIAS20', 'RSI14', '52周位', '回撤', 'VR5', '甄别'))
A_ok = []
for r, _ in grp['A_共振向上']:
    tags = []
    if r['bias']['ma20'] > 25:
        tags.append('过度偏离MA20>25%')
    if r['rsi'] > 80:
        tags.append('RSI>80超买')
    if r['rng']['pos'] is not None and r['rng']['pos'] >= 98 and r['rng']['drawdown'] > -1.5:
        tags.append('贴顶创新高')
    if r['vol']['v5_over_v20'] and r['vol']['v5_over_v20'] < 0.8:
        tags.append('量能萎缩')
    tag = '、'.join(tags) if tags else '✅通过'
    print('%-8s %-10s %7.1f%% %7.1f %7s%% %7.1f%% %8.2f  %s' % (
        r['code'], r['name'], r['bias']['ma20'], r['rsi'], r['rng']['pos'],
        r['rng']['drawdown'], r['vol']['vr5'], tag))
    if not tags:
        A_ok.append(r)

print('\nA档通过甄别: %s' % [r['code'] + r['name'] for r in A_ok])

json.dump({'rows': rows}, open(os.path.join(OUT, 'final_rows.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, default=str)
print('\n已写出 final_rows.json')
