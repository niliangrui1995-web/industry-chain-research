# -*- coding: utf-8 -*-
"""从 D:/HT/vipdoc 本地 .day 二进制日线读取两个板块成分股数据，并做交易日历完整性校验。"""
import os, json, struct, datetime as dt

VD = r'D:/HT/vipdoc'
OUTDIR = r'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260921'
members = json.load(open(os.path.join(OUTDIR, 'block_members.json'), encoding='utf-8'))

codes = []
for t, v in members.items():
    for m in v['members']:
        if (m['market'], m['code']) not in [(c['market'], c['code']) for c in codes]:
            codes.append(m)
print('待取数标的数:', len(codes))

def day_path(mkt, code):
    sub = {'SH': 'sh', 'SZ': 'sz', 'BJ': 'bj'}[mkt]
    return os.path.join(VD, sub, 'lday', f'{sub}{code}.day')

def read_day(path, limit=300):
    if not os.path.exists(path):
        return None
    raw = open(path, 'rb').read()
    if len(raw) % 32 != 0 or len(raw) == 0:
        return None
    n = len(raw) // 32
    out = []
    for i in range(max(0, n - limit), n):
        o = i * 32
        d, op, hi, lo, cl, amt, vol, _ = struct.unpack('<IIIIIfII', raw[o:o + 32])
        out.append({'date': str(d), 'open': op / 100.0, 'high': hi / 100.0,
                    'low': lo / 100.0, 'close': cl / 100.0, 'amount': float(amt),
                    'vol': int(vol)})
    return out

bars = {}
missing = []
for m in codes:
    p = day_path(m['market'], m['code'])
    b = read_day(p)
    if b is None:
        missing.append(m['full'])
        continue
    bars[m['full']] = b

print('成功读取:', len(bars), ' 缺失:', missing)

# 最后交易日分布
lasts = {}
for k, b in bars.items():
    lasts.setdefault(b[-1]['date'], []).append(k)
print('\n最后交易日分布 (top10):')
for d in sorted(lasts, reverse=True)[:10]:
    print('  ', d, len(lasts[d]))

# 基准交易日历：取最后交易日最新且样本最多的日期集合（用出现次数>=5的日期）
cal = sorted([d for d, v in lasts.items()], reverse=False)
# 用全市场并集日期中出现频次 >= 总标的 30% 的日期作为基准日历
cnt = {}
for k, b in bars.items():
    for r in b:
        cnt[r['date']] = cnt.get(r['date'], 0) + 1
thresh = max(3, int(len(bars) * 0.3))
calendar = sorted([d for d, c in cnt.items() if c >= thresh])
print('\n基准交易日历长度:', len(calendar), '首:', calendar[0], '末:', calendar[-1])

# 完整性校验（最近 130 个日历日窗口）
win = calendar[-130:]
print('校验窗口(最近130个交易日):', win[0], '~', win[-1])
incomplete = {}
for k, b in bars.items():
    bd = set(r['date'] for r in b)
    miss = [d for d in win if d not in bd]
    if miss:
        incomplete[k] = miss
print('\n窗口内缺数据的标的数:', len(incomplete))
for k, v in list(incomplete.items())[:20]:
    print('  ', k, '缺', len(v), '日', v[:6], '...' if len(v) > 6 else '')

json.dump({'bars': bars, 'calendar': calendar, 'missing': missing, 'incomplete': {k: len(v) for k, v in incomplete.items()}},
          open(os.path.join(OUTDIR, 'bars_raw.json'), 'w', encoding='utf-8'))
print('\n已保存 bars_raw.json')
