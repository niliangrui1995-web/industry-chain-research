# -*- coding: utf-8 -*-
"""解析 blocknew.cfg（88字节定长记录：名称GBK + 文件名ASCII）与两个目标 .blk 成分股。"""
import os, json

BASE = r'D:/HT/T0002/blocknew'
OUTDIR = r'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260921'
os.makedirs(OUTDIR, exist_ok=True)
RECL = 88

raw = open(os.path.join(BASE, 'blocknew.cfg'), 'rb').read()
assert len(raw) % RECL == 0, (len(raw), RECL)
mapping = {}
for i in range(0, len(raw), RECL):
    rec = raw[i:i + RECL]
    name = rec.split(b'\x00')[0].decode('gbk', 'replace').strip()
    tail = rec.rstrip(b'\x00')
    # 文件名在记录后段的 ASCII 区
    fn = None
    for j in range(len(rec)):
        seg = rec[j:].split(b'\x00')[0]
        if len(seg) >= 3 and all(65 <= c <= 122 and chr(c).isalnum() or c in b'_' for c in seg):
            if seg.decode('ascii', 'replace').isupper() or b'.' in seg:
                fn = fn or seg.decode('ascii', 'replace')
    mapping[name] = fn
    print(f'{name:<16} -> {fn}')

json.dump(mapping, open(os.path.join(OUTDIR, 'block_mapping.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

# 名称表：从 hq_cache/*.tnf 提取 code->name
def load_names():
    names = {}
    for mkt, fn in (('SH', 'shs.tnf'), ('SZ', 'szs.tnf'), ('BJ', 'bjs.tnf')):
        p = os.path.join(r'D:/HT/T0002/hq_cache', fn)
        b = open(p, 'rb').read()
        for code6 in None or []:
            pass
        # 扫描：找 \x00 + 6位数字代码 + \x00 的位置，随后首段 GBK 即名称
        import re
        for m in re.finditer(b'\x00([0-9]{6})\x00', b):
            code = m.group(1).decode()
            pos = m.end()
            # 跳过连续的 \x00
            while pos < len(b) and b[pos] == 0:
                pos += 1
            end = pos
            while end < len(b) and b[end] != 0:
                end += 1
            nm = b[pos:end].decode('gbk', 'replace').strip()
            if nm and not nm.startswith('\x00'):
                names.setdefault(mkt + code, nm)
    return names

print('loading names...')
NAMES = load_names()
print('names loaded:', len(NAMES))
json.dump(NAMES, open(os.path.join(OUTDIR, 'code2name_cache.json'), 'w', encoding='utf-8'),
          ensure_ascii=False)

MKT = {'0': 'SZ', '1': 'SH', '2': 'BJ'}

def parse_blk(fn):
    p = os.path.join(BASE, fn)
    b = open(p, 'rb').read()
    txt = b.decode('gbk', 'replace')
    out = []
    for line in txt.replace('\r', '').split('\n'):
        line = line.strip()
        if len(line) < 7:
            continue
        flag, code6 = line[0], line[1:7]
        if not code6.isdigit():
            continue
        mkt = MKT.get(flag)
        if mkt is None:
            mkt = 'SH' if code6[0] in '56' else 'SZ'
        full = mkt + code6
        out.append({'raw': line, 'market': mkt, 'code': code6,
                    'full': full, 'name': NAMES.get(full, 'N/A')})
    return out

targets = {'关注个股': 'GZGG.blk', 'AI硬件': 'AIYJ.blk'}
result = {}
for t, fn in targets.items():
    lst = parse_blk(fn)
    result[t] = {'file': fn, 'members': lst}
    print(f'\n=== {t} ({fn}) : {len(lst)} 只 ===')
    for x in lst:
        print(f"  {x['full']}  {x['name']}")

json.dump(result, open(os.path.join(OUTDIR, 'block_members.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
miss = [(t, x['full']) for t, v in result.items() for x in v['members'] if x['name'] == 'N/A']
print('\n缺名称:', miss)
