# -*- coding: utf-8 -*-
"""生成两个板块的完整清单表 + 数据异常个股标注"""
import json, os

BASE = 'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260921/'
OUT = 'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260922/'
os.makedirs(OUT, exist_ok=True)

bm = json.load(open(BASE + 'block_members.json', encoding='utf-8'))
lab = {r['full']: r for r in json.load(open(BASE + 'labeled.json', encoding='utf-8'))['rows']}
nd = json.load(open(BASE + 'nextday.json', encoding='utf-8'))
MK = {'SH': '沪', 'SZ': '深', 'BJ': '京'}

for b in ['关注个股', 'AI硬件']:
    d = bm[b]
    ms = d['members']
    lines = ['| # | 代码 | 全称 | 名称 | 市场 |', '|---:|---|---|---|---|']
    for i, m in enumerate(ms, 1):
        lines.append('| %d | %s | %s | %s | %s |' % (i, m['code'], m['full'], m['name'], MK[m['market']]))
    t = '\n'.join(lines)
    open(OUT + 'tbl_%s.md' % b, 'w', encoding='utf-8').write(t)
    print('### %s | 文件=%s | 数量=%d' % (b, d['file'], len(ms)))

print('\n=== 数据异常/需单独标注个股 ===')
for c, r in sorted(lab.items()):
    i = r.get('ind', {})
    nb = i.get('n_bars', 0)
    if nb < 250 or r.get('is_etf'):
        print('%s %s [%s] bars=%d etf=%s' % (c, r.get('name'), r.get('block'), nb, r.get('is_etf')))

print('\n=== 缺失交易日明细(近130日) ===')
miss = json.load(open(BASE + 'bars_raw.json', encoding='utf-8')) if os.path.exists(BASE + 'bars_raw.json') else None
print('bars_raw keys:', type(miss))
