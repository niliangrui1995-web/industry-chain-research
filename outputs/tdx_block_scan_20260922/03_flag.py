# -*- coding: utf-8 -*-
"""标注数据不足 / 长期停牌 / 非个股标的"""
import json, os, struct

BASE = 'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260921/'
lab = {r['full']: r for r in json.load(open(BASE + 'labeled.json', encoding='utf-8'))['rows']}
VIP = 'D:/HT/vipdoc'

targets = ['SH515880', 'SH688432', 'SH688143', 'SH688146', 'SZ000504', 'SH688825', 'BJ920045', 'SH688783', 'SH688796']
for c in targets:
    mkt = c[:2].lower()
    p = os.path.join(VIP, mkt, 'lday', c.lower() + '.day')
    n = os.path.getsize(p) // 32 if os.path.exists(p) else 0
    r = lab.get(c, {})
    dates = []
    if os.path.exists(p):
        raw = open(p, 'rb').read()
        for i in range(0, len(raw) - 31, 32):
            d, o, h, l, cl, amt, vol, _ = struct.unpack('<IIIIIfII', raw[i:i + 32])
            dates.append(d)
    last = sorted(dates)[-5:] if dates else []
    # 相邻交易日间隔(自然日)统计 -> 粗略判断停牌
    print('%s %-6s bars=%-4d 文件K线=%-4d 近5日=%s' % (c, r.get('name', ''), r.get('ind', {}).get('n_bars', 0), n, last))
