# -*- coding: utf-8 -*-
"""读取通达信 vipdoc 本地日线(.day)，做交易日历完整性校验，并输出每只股的数据概况。

.day 记录格式(32字节):
  [0:4]  int32 日期 YYYYMMDD
  [4:8]  uint32 开盘价 *100
  [8:12] uint32 最高价 *100
  [12:16]uint32 最低价 *100
  [16:20]uint32 收盘价 *100
  [20:24]float32 成交额(元)
  [24:28]uint32 成交量(股)
  [28:32]uint32 保留
"""
import os, re, json, struct, datetime, collections

VIP = r'D:\HT\vipdoc'
BLK = r'D:\HT\T0002\blocknew'
OUT = os.path.dirname(os.path.abspath(__file__))
REC = 32


def day_path(mkt, code):
    sub = {'SH': 'sh', 'SZ': 'sz', 'BJ': 'bj'}[mkt]
    return os.path.join(VIP, sub, 'lday', '%s%s.day' % (sub, code))


def read_day(path):
    """返回 [(date_str, o,h,l,c, amount, vol), ...] 升序"""
    if not os.path.isfile(path):
        return []
    b = open(path, 'rb').read()
    n = len(b) // REC
    out = []
    for i in range(n):
        raw = b[i * REC:(i + 1) * REC]
        if len(raw) < REC:
            break
        d, o, h, l, c, amt, vol, _ = struct.unpack('<iiiiifii', raw)
        if d <= 0:
            continue
        ds = '%08d' % d
        out.append((ds, o / 100.0, h / 100.0, l / 100.0, c / 100.0, amt, vol))
    out.sort(key=lambda x: x[0])
    return out


def load_targets():
    src = json.load(open(os.path.join(OUT, 'blocks_parsed.json'), encoding='utf-8'))
    res = {}
    for bk, info in src.items():
        res[bk] = [(x['mkt'], x['code'], x['name']) for x in info['members']]
    return res


if __name__ == '__main__':
    targets = load_targets()
    allst = {}
    for bk, lst in targets.items():
        for mkt, code, name in lst:
            allst[(mkt, code)] = (name, bk)

    # 1) 基准日历：以上证指数为准，取近 300 个交易日日历
    sh_idx = read_day(day_path('SH', '000001'))
    cal = [r[0] for r in sh_idx]
    print('指数基准: 共 %d 根, 最新 %s, 最旧 %s' % (len(cal), cal[-1], cal[0]))

    # 校验窗口：最近 260 个交易日 / 最近 130 个交易日 / 最近 30 个交易日
    def coverage(codes_dates, win):
        base = set(cal[-win:])
        miss = sorted(base - set(codes_dates))
        return miss

    rows = []
    for (mkt, code), (name, bk) in sorted(allst.items()):
        rs = read_day(day_path(mkt, code))
        if not rs:
            rows.append({'mkt': mkt, 'code': code, 'name': name, 'block': bk,
                         'n': 0, 'last': None, 'first': None,
                         'miss130': None, 'miss60': None, 'ok': False})
            continue
        dates = [r[0] for r in rs]
        rows.append({'mkt': mkt, 'code': code, 'name': name, 'block': bk,
                     'n': len(rs), 'last': dates[-1], 'first': dates[0],
                     'miss130': coverage(dates, 130), 'miss60': coverage(dates, 60),
                     'ok': True})

    # 汇总
    last_all = collections.Counter(r['last'] for r in rows if r['ok'])
    print('\n最新交易日分布:', dict(last_all))
    bad = [r for r in rows if not r['ok'] or r['n'] < 260]
    print('数据不足(<260根)或无文件: %d 只' % len(bad))
    for r in bad:
        print('   %s %s %s n=%s last=%s' % (r['mkt'], r['code'], r['name'], r['n'], r['last']))

    print('\n近130日窗口缺失交易日统计(>0 的列出):')
    for r in rows:
        if r['ok'] and r['miss130']:
            print('   %s %s %s 缺%d天: %s' % (r['mkt'], r['code'], r['name'],
                                             len(r['miss130']), ','.join(r['miss130'][:15])))

    json.dump({'calendar_last': cal[-1], 'calendar_n': len(cal), 'rows': rows},
              open(os.path.join(OUT, 'day_coverage.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('\n已写出 day_coverage.json')
