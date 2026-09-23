# -*- coding: utf-8 -*-
"""检查本地 vipdoc 是否已写入 2026-09-22 日线"""
import os, struct, json

VIP = 'D:/HT/vipdoc'
BASE = 'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260921/'
lab = {r['full']: r for r in json.load(open(BASE + 'labeled.json', encoding='utf-8'))['rows']}

dist = {}
have922 = []
for c in lab:
    mkt = c[:2].lower()
    p = os.path.join(VIP, mkt, 'lday', c.lower() + '.day')
    if not os.path.exists(p):
        dist['MISSING'] = dist.get('MISSING', 0) + 1
        continue
    raw = open(p, 'rb').read()
    n = len(raw) // 32
    if n == 0:
        continue
    last = struct.unpack('<IIIIIfII', raw[(n - 1) * 32:n * 32])[0]
    dist[str(last)] = dist.get(str(last), 0) + 1
    if last >= 20260922:
        d, o, h, l, cl, amt, vol, _ = struct.unpack('<IIIIIfII', raw[(n - 1) * 32:n * 32])
        have922.append((c, lab[c]['name'], cl / 100.0, vol))

print('最后交易日分布:', dist)
print('已含 9/22 的标的数:', len(have922))
for x in have922[:20]:
    print('   ', x)
