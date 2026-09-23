# -*- coding: utf-8 -*-
"""解析 blocknew.cfg 中的板块名->blk 映射，并解析成分股代码+名称。"""
import os, re, json

BLK = r'D:\HT\T0002\blocknew'
HQ = r'D:\HT\T0002\hq_cache'
OUT = os.path.dirname(os.path.abspath(__file__))


def decode_gbk(b):
    return b.decode('gbk', errors='ignore')


def read_cfg_map(path):
    """cfg: 每条记录 = 显示名(GBK, \x00 填充) + 文件名(GBK, \x00 填充)"""
    s = decode_gbk(open(path, 'rb').read())
    # 按 \x00+ 切段
    toks = [t for t in re.split(r'\x00+', s) if t.strip()]
    # 成对出现：显示名, 文件名
    pairs = []
    i = 0
    while i < len(toks) - 1:
        name, fn = toks[i], toks[i + 1]
        if re.fullmatch(r'[A-Za-z0-9%_\+\-]{1,32}', fn):
            pairs.append((fn, name))
            i += 2
        else:
            i += 1
    return pairs


def load_names():
    names = {}
    for f in ('shs.tnf', 'szs.tnf', 'bjs.tnf'):
        p = os.path.join(HQ, f)
        if not os.path.isfile(p):
            continue
        b = open(p, 'rb').read()
        for m in re.finditer(rb'(?<![\x30-\x39])(\d{6})(?![\x30-\x39])', b):
            code = m.group(1).decode()
            tail = b[m.end():m.end() + 64]
            i = 0
            while i < len(tail) and tail[i] == 0:
                i += 1
            seg = tail[i:].split(b'\x00')[0]
            nm = re.sub(r'[^A-Za-z0-9\u4e00-\u9fa5\*]', '', decode_gbk(seg))
            if nm and code not in names:
                names[code] = nm
    return names


MKT = {'0': 'SZ', '1': 'SH', '2': 'BJ'}


def parse_blk(path):
    rows = []
    for line in decode_gbk(open(path, 'rb').read()).splitlines():
        line = line.strip()
        if len(line) == 7 and line.isdigit():
            rows.append(line)
        elif line:
            rows.append(line)  # 异常行单独标记
    return rows


if __name__ == '__main__':
    pairs = read_cfg_map(os.path.join(BLK, 'blocknew.cfg'))
    mp = {}
    for fn, name in pairs:
        mp.setdefault(name, set()).add(fn + '.blk')
    print('== cfg 板块映射 ==')
    for name in sorted(mp):
        print('  %-14s -> %s' % (name, sorted(mp[name])))

    names = load_names()
    print('\n名称表条数: %d' % len(names))

    targets = ['关注个股', 'AI硬件']
    res = {}
    for t in targets:
        fns = sorted(mp.get(t, []))
        assert fns, '未找到板块: ' + t
        for fn in fns:
            rows = parse_blk(os.path.join(BLK, fn))
            lst = []
            for raw in rows:
                if len(raw) == 7 and raw.isdigit():
                    mk, c6 = raw[0], raw[1:]
                    mkt = MKT.get(mk, '?')
                else:
                    mkt, c6 = '?', raw
                lst.append({'raw': raw, 'mkt': mkt, 'code': c6,
                            'name': names.get(c6, '?'),
                            'tsym': ('%s%s' % (mkt.lower(), c6)) if mkt != '?' else '?'})
            res[t] = {'blk': fn, 'count': len(lst), 'members': lst}
            print('\n== %s (%s) 共 %d 条 ==' % (t, fn, len(lst)))
            for k, x in enumerate(lst, 1):
                print('  %2d. %-7s %-3s %s %s' % (k, x['raw'], x['mkt'], x['code'], x['name']))
    json.dump(res, open(os.path.join(OUT, 'blocks_parsed.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('\n已写出 blocks_parsed.json')
