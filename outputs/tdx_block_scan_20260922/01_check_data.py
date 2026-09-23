# -*- coding: utf-8 -*-
"""检查 2026-09-22 本地日线是否已写入今日数据。"""
import os, struct, json

VD = r'D:/HT/vipdoc'
OUTDIR = r'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260922'
os.makedirs(OUTDIR, exist_ok=True)

MEM = json.load(open(r'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260921/block_members.json', encoding='utf-8'))
codes = []
for t, v in MEM.items():
    for m in v['members']:
        if m['full'] not in [c['full'] for c in codes]:
            codes.append(m)
print('标的数:', len(codes))

def tail_day(path, n=3):
    raw = open(path, 'rb').read()
    cnt = len(raw) // 32
    out = []
    for i in range(max(0, cnt - n), cnt):
        o = i * 32
        d, op, hi, lo, cl, amt, vol, _ = struct.unpack('<IIIIIfII', raw[o:o + 32])
        out.append((str(d), cl / 100.0, vol))
    return out

lasts = {}
samples = ['SH603259', 'SZ300308', 'SH688271', 'SZ002463', 'SH600487', 'SZ300408']
for c in samples:
    mkt, code = c[:2], c[2:]
    p = os.path.join(VD, {'SH': 'sh', 'SZ': 'sz', 'BJ': 'bj'}[mkt], 'lday',
                     f"{ {'SH':'sh','SZ':'sz','BJ':'bj'}[mkt] }{code}.day")
    t = tail_day(p, 3)
    print(c, '->', t)
    lasts[c] = t[-1][0]

print('\n样本最后日期:', set(lasts.values()))

# 全市场：统计最后日期分布
dist = {}
for m in codes:
    mkt, code = m['full'][:2], m['full'][2:]
    sub = {'SH': 'sh', 'SZ': 'sz', 'BJ': 'bj'}[mkt]
    p = os.path.join(VD, sub, 'lday', f'{sub}{code}.day')
    if not os.path.exists(p):
        continue
    t = tail_day(p, 1)
    dist[t[0][0]] = dist.get(t[0][0], 0) + 1
print('\n126 只最后交易日分布:', dist)
