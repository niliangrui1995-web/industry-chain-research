# -*- coding: utf-8 -*-
"""按定性条件分组（趋势延续 / 临界突破 / 超跌修复 / 规避），输出候选详表。"""
import os, json

OUTDIR = r'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260921'
L = json.load(open(os.path.join(OUTDIR, 'labeled.json'), encoding='utf-8'))
rows = L['rows']
IND = json.load(open(os.path.join(OUTDIR, 'indicators.json'), encoding='utf-8'))

EXCL = {'SH688825': '上市不足半年，样本仅40根，MA60/周线不可算',
        'SH515880': 'ETF，非个股'}
EXCL_TREND_DOWN = {'SZ002415', 'SH688578', 'SH688271', 'SH688016'}

groups = {}
for r in rows:
    k, i, l = r['full'], r['ind'], r['lab']
    if k in EXCL:
        continue
    c = i['close']
    m20, m60 = i['ma']['20'], i['ma']['60']
    w = i['weekly']
    cond = {
        'd_up': l['trend_d'] == 'up',
        'w_ok': l['trend_w'] in ('up', 'range'),
        'mom_up': '多头' in l['mom_d'] or '金叉' in l['mom_d'],
        'mom_strong': ('放大' in l['mom_d']) or ('金叉' in l['mom_d']),
        'pos_ok': (i['pos60'] or 0) < 95 and (l['bias20'] or 0) < 18,
        'rsi_ok': (i['rsi14'] or 0) < 75,
        'vp_ok': l['volprice'] in ('放量上涨', '缩量回调', '缩量上涨'),
        'above_m20': c > (m20 or 0),
        'near_break': (l['res_space'] or 99) <= 3.0,
        'deep_pullback': (i['pos60'] or 100) <= 40,
    }
    score_dim = sum([cond['d_up'], cond['w_ok'], cond['mom_up'], cond['pos_ok'],
                     cond['rsi_ok'], cond['vp_ok']])
    g = []
    if k in EXCL_TREND_DOWN or l['trend_d'] == 'down':
        g.append('趋势走坏')
    if (i['pos60'] or 0) >= 97 or (l['bias20'] or 0) >= 22:
        g.append('短线过热')
    if cond['d_up'] and cond['w_ok'] and cond['mom_strong'] and cond['pos_ok'] and cond['rsi_ok']:
        g.append('趋势延续')
    if cond['near_break'] and cond['mom_up'] and not ('短线过热' in g):
        g.append('临界突破')
    if cond['deep_pullback'] and cond['mom_up'] and cond['vp_ok']:
        g.append('低位修复')
    if not g:
        g.append('中性观察')
    groups[k] = {'name': r['name'], 'block': r['block'], 'cond': cond, 'tags': g,
                 'ndim': score_dim}

# 输出候选
for blk in ['关注个股', 'AI硬件']:
    print(f'\n{"="*100}\n【{blk}】分组结果')
    for tag in ['趋势延续', '临界突破', '低位修复', '中性观察', '短线过热', '趋势走坏']:
        sel = [(k, v) for k, v in groups.items() if v['block'] == blk and tag in v['tags']]
        if not sel: continue
        sel.sort(key=lambda x: -x[1]['ndim'])
        print(f'\n-- {tag} ({len(sel)}) --')
        for k, v in sel:
            i = IND[k]
            l = [r['lab'] for r in rows if r['full'] == k][0]
            print(f"{k} {v['name']:<8} 收{i['close']:>9.2f} 维度{v['ndim']}/7 | "
                  f"MA20={i['ma']['20']} MA60={i['ma']['60']} | 压{l['res_near']}(+{l['res_space']}%) "
                  f"支{l['sup_near']}(-{l['sup_space']}%) | {l['mom_d']} | {l['mom_w']} | {l['volprice']} "
                  f"VR5={i['vr5']} | RSI{i['rsi14']} J={i['kdj']['j']} BIAS20={l['bias20']} pos60={i['pos60']} "
                  f"ATR%={i['atr_pct']} | 周量比={round(i['weekly']['vol_last']/i['weekly']['vma4'],2) if i['weekly']['vma4'] else 'NA'}")

json.dump(groups, open(os.path.join(OUTDIR, 'groups.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n排除项:', EXCL)
