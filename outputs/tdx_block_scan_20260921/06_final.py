# -*- coding: utf-8 -*-
"""导出最终入选名单的详细数据包（含近20日走势、关键位、指标），供 md 与 HTML 使用。"""
import os, json

OUTDIR = r'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260921'
L = json.load(open(os.path.join(OUTDIR, 'labeled.json'), encoding='utf-8'))
BARS = json.load(open(os.path.join(OUTDIR, 'bars_raw.json'), encoding='utf-8'))['bars']
rows = {r['full']: r for r in L['rows']}
IND = json.load(open(os.path.join(OUTDIR, 'indicators.json'), encoding='utf-8'))

PICK = {
    '关注个股': {
        '核心关注': ['SH603259', 'SZ300759', 'SZ002821'],
        '次级关注': ['SZ300725', 'SZ300298', 'SH688428'],
        '观察备选': ['SH688796', 'SZ301047', 'SH688131'],
    },
    'AI硬件': {
        '核心关注': ['SZ002463', 'SH600487', 'SZ300408'],
        '次级关注': ['SZ301205', 'SZ300308', 'SH688498'],
        '观察备选': ['SZ300476', 'SH688256', 'SZ300489'],
    },
}
AVOID = {
    '关注个股': ['SZ000504', 'SH688222', 'SZ301080', 'SH688293', 'SZ000739', 'SH688621', 'SH688758',
                'SH688271', 'SH688578', 'SH688016'],
    'AI硬件': ['SH688205', 'SH688143', 'SZ002080', 'SZ002415'],
}

out = {}
for blk, tiers in PICK.items():
    for tier, codes in tiers.items():
        for c in codes:
            r = rows[c]; i = r['ind']; l = r['lab']
            b = sorted(BARS[c], key=lambda x: x['date'])[-20:]
            out[c] = {
                'code': c, 'name': r['name'], 'block': blk, 'tier': tier,
                'close': i['close'], 'ma': i['ma'], 'macd': i['macd'],
                'rsi14': i['rsi14'], 'kdj': i['kdj'], 'boll': i['boll'],
                'atr_pct': i['atr_pct'], 'bias20': l['bias20'], 'pos60': i['pos60'],
                'vr5': i['vr5'], 'chg5': i['chg5'], 'chg20': i['chg20'],
                'res_near': l['res_near'], 'res_space': l['res_space'],
                'sup_near': l['sup_near'], 'sup_space': l['sup_space'],
                'mom_d': l['mom_d'], 'mom_w': l['mom_w'], 'volprice': l['volprice'],
                'trend_d': l['trend_d'], 'trend_w': l['trend_w'], 'position': l['position'],
                'risks': l['risks'], 'weekly': i['weekly'],
                'k20': [[x['date'], x['open'], x['close'], x['high'], x['low'], x['vol']] for x in b],
                'div': i['div_events'],
            }

json.dump(out, open(os.path.join(OUTDIR, 'final_picks.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

for blk in PICK:
    print(f'\n===== {blk} =====')
    for tier in ['核心关注', '次级关注', '观察备选']:
        print(f'\n-- {tier} --')
        for c in PICK[blk][tier]:
            d = out[c]
            print(f"{c} {d['name']:<8} {d['close']:>9.2f} | MA20={d['ma']['20']} MA60={d['ma']['60']} "
                  f"| 压{d['res_near']}(+{d['res_space']}%) 支{d['sup_near']}(-{d['sup_space']}%) "
                  f"| {d['mom_d']} | {d['mom_w']} | {d['volprice']} VR5={d['vr5']} "
                  f"| RSI{d['rsi14']} J={d['kdj']['j']} BIAS={d['bias20']} pos60={d['pos60']} ATR%={d['atr_pct']}")

print('\n===== 规避名单 =====')
for blk, cs in AVOID.items():
    for c in cs:
        r = rows[c]; i = r['ind']; l = r['lab']
        print(f"{blk} {c} {r['name']:<8} {i['close']:>9.2f} BIAS20={l['bias20']} pos60={i['pos60']} "
              f"RSI={i['rsi14']} J={i['kdj']['j']} | {l['trend_d']}/{l['trend_w']} | {l['mom_d']} | {l['risks']}")
