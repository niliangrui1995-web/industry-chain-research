# -*- coding: utf-8 -*-
# AI硬件板块（AIYJ.blk）技术面量化初筛
# 数据源：D:\HT 本地通达信 .day 日线文件（截至 2026-09-18）
import os, struct, json

HT = r'D:\HT'
BLK = os.path.join(HT, r'T0002\blocknew\AIYJ.blk')
OUT_DIR = r'D:\vcp_hunter\产业链投研\outputs'

def parse_blk(path):
    stocks = []
    with open(path, 'r', encoding='ascii', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if len(line) != 7 or not line.isdigit():
                continue
            mkt, code = line[0], line[1:]
            stocks.append(({'0': 'sz', '1': 'sh', '2': 'bj'}.get(mkt, '?'), code))
    return stocks

def load_names():
    # hq_cache\{shs,szs,bjs}.tnf：记录特征 = 6位代码 + 25个\x00 + GBK名称(以\x00结尾)
    # 按市场分开建表，避免 sh000001上证指数 与 sz000001平安银行 这类跨市场同码冲突
    import re
    names = {}
    pat = re.compile(rb'(\d{6})\x00{25}([\x20-\x7e\x80-\xff]+?)\x00')
    for mkt, fn in (('sh', 'shs.tnf'), ('sz', 'szs.tnf'), ('bj', 'bjs.tnf')):
        p = os.path.join(HT, 'T0002', 'hq_cache', fn)
        if not os.path.exists(p):
            continue
        data = open(p, 'rb').read()
        for m in pat.finditer(data):
            code = m.group(1).decode('ascii')
            name = m.group(2).decode('gbk', errors='ignore').strip()
            if name:
                names.setdefault((mkt, code), name)
    return names

def read_day(mkt, code):
    p = os.path.join(HT, 'vipdoc', mkt, 'lday', '%s%s.day' % (mkt, code))
    if not os.path.exists(p):
        return None
    data = open(p, 'rb').read()
    n = len(data) // 32
    bars = []
    for i in range(n):
        d, o, h, l, c, amt, vol, _ = struct.unpack_from('IIIIIfII', data, i*32)
        mult = 100.0  # A股股票/ETF
        bars.append(dict(date=d, open=o/mult, high=h/mult, low=l/mult, close=c/mult, vol=vol, amt=amt))
    return bars

def ema(vals, n):
    out, k = [], 2.0/(n+1)
    e = vals[0]
    for v in vals:
        e = v*k + e*(1-k)
        out.append(e)
    return out

def sma(vals, n):
    out = []
    for i in range(len(vals)):
        if i+1 < n:
            out.append(sum(vals[:i+1])/(i+1))
        else:
            out.append(sum(vals[i-n+1:i+1])/n)
    return out

def analyze(bars):
    closes = [b['close'] for b in bars]
    highs = [b['high'] for b in bars]
    lows = [b['low'] for b in bars]
    vols = [b['vol'] for b in bars]
    n = len(closes)
    if n < 65:
        return None
    ma5, ma10, ma20, ma60 = sma(closes,5)[-1], sma(closes,10)[-1], sma(closes,20)[-1], sma(closes,60)[-1]
    vma5, vma20 = sma(vols,5)[-1], sma(vols,20)[-1]
    e12, e26 = ema(closes,12), ema(closes,26)
    dif = [a-b for a, b in zip(e12, e26)]
    dea = ema(dif, 9)
    macd = [2*(a-b) for a, b in zip(dif, dea)]
    # KDJ(9,3,3)
    K = D = 50.0
    for i in range(n):
        lo = min(lows[max(0,i-8):i+1]); hi = max(highs[max(0,i-8):i+1])
        rsv = 50.0 if hi == lo else (closes[i]-lo)/(hi-lo)*100
        K = (2*K + rsv)/3; D = (2*D + K)/3
    J = 3*K - 2*D
    c = closes[-1]
    ret = lambda m: (c/closes[-1-m]-1)*100 if n > m else None
    h20, l20 = max(highs[-20:]), min(lows[-20:])
    h60, l60 = max(highs[-60:]), min(lows[-60:])
    l10 = min(lows[-10:])
    ma20_prev = sma(closes,20)[-6]
    ma60_prev = sma(closes,60)[-6]
    vol_ratio = vols[-1]/vma5 if vma5 else 0
    macd_cross = None
    if dif[-1] > dea[-1] and dif[-2] <= dea[-2]: macd_cross = 'gold_today'
    elif dif[-1] > dea[-1] and min(dif[-5:]) > min(dea[-5:]) and any(dif[-5+i] <= dea[-5+i] for i in range(1,5)): macd_cross = 'gold_recent'
    elif dif[-1] < dea[-1] and dif[-2] >= dea[-2]: macd_cross = 'dead_today'
    elif dif[-1] < dea[-1]: macd_cross = 'dead'
    else: macd_cross = 'gold'
    # 综合评分 0-100
    s = 0.0; notes = []
    # 均线排列 25
    if c > ma5 > ma10 > ma20 > ma60: s += 25; notes.append('完美多头排列')
    elif c > ma10 > ma20 > ma60: s += 20; notes.append('多头排列(短线略弱)')
    elif c > ma20 > ma60: s += 14; notes.append('中期多头')
    elif c > ma60 and ma20 > ma60: s += 10; notes.append('站上60日线')
    elif c > ma20: s += 6
    elif c < ma20 and c < ma60: s += 0; notes.append('跌破20/60日线')
    else: s += 3
    # 趋势斜率 15
    if ma20 > ma20_prev and ma60 > ma60_prev: s += 15; notes.append('20/60日线向上')
    elif ma20 > ma20_prev: s += 10; notes.append('20日线向上')
    elif ma60 > ma60_prev: s += 6
    # MACD 15
    if dif[-1] > dea[-1] and dif[-1] > 0:
        s += 12; notes.append('MACD零上金叉区')
        if macd[-1] > macd[-2]: s += 3; notes.append('红柱放大')
    elif dif[-1] > dea[-1]:
        s += 9; notes.append('MACD零下金叉')
    elif dif[-1] < dea[-1] and dif[-1] > 0: s += 4; notes.append('零上死叉/回落')
    if macd_cross == 'gold_today': s += 3; notes.append('当日金叉')
    # KDJ 10
    if K > D and K < 80: s += 10; notes.append('KDJ金叉区未超买')
    elif K > D and K >= 80: s += 5; notes.append('KDJ高位(超买风险)')
    elif K < D and K < 30: s += 6; notes.append('KDJ超卖区')
    elif K < D: s += 2
    # 量价 15
    up5 = sum(1 for i in range(-5,0) if closes[i] >= closes[i-1])
    if vma5 > vma20: s += 6; notes.append('5日均量>20日均量')
    if 1.2 <= vol_ratio <= 2.8 and closes[-1] >= bars[-2]['close']: s += 5; notes.append('温和放量上涨')
    elif vol_ratio > 4: s += 1; notes.append('巨量(警惕)')
    else: s += 3
    if up5 >= 3: s += 4
    # 动量与位置 20
    r5, r20 = ret(5), ret(20)
    pos20 = (c-l20)/(h20-l20)*100 if h20 > l20 else 50
    dist_h20 = (c/h20-1)*100
    if r20 is not None and 3 <= r20 <= 25: s += 6; notes.append('20日动量健康(+%.1f%%)' % r20)
    elif r20 is not None and r20 > 40: s += 1; notes.append('短期涨幅过大(+%.1f%%)' % r20)
    elif r20 is not None and r20 < -10: s += 2; notes.append('20日跌幅较深')
    else: s += 4
    if -3 <= dist_h20 <= 0: s += 7; notes.append('贴近20日新高')
    elif -8 <= dist_h20 < -3 and c > ma20: s += 5; notes.append('小幅回踩趋势未破')
    elif dist_h20 < -15: s += 1
    else: s += 3
    if r5 is not None and r5 > 15: s += 1; notes.append('5日涨幅过热')
    elif r5 is not None and 0 <= r5 <= 10: s += 7
    elif r5 is not None and -5 <= r5 < 0 and c > ma20: s += 6; notes.append('回踩5日')
    else: s += 3
    # 阶段判定
    if dist_h20 >= -2 and vma5 > vma20 and dif[-1] > dea[-1]:
        stage = '突破/攻击'
    elif c > ma20 and r5 is not None and r5 < 0:
        stage = '上升趋势中回踩'
    elif c < ma20 and c > ma60:
        stage = '中期回调'
    elif c < ma60:
        stage = '弱势/下降通道'
    else:
        stage = '横盘整理'
    support = round(max(ma20 if c > ma20 else ma60, l10), 2)
    resist = round(h20 if dist_h20 < -0.5 else h60, 2)
    return dict(
        last_date=bars[-1]['date'], close=round(c,2),
        ma5=round(ma5,2), ma10=round(ma10,2), ma20=round(ma20,2), ma60=round(ma60,2),
        ret1=round(ret(1),2), ret5=round(ret(5),2), ret10=round(ret(10),2), ret20=round(ret(20),2),
        dif=round(dif[-1],3), dea=round(dea[-1],3), macd=round(macd[-1],3), macd_state=macd_cross,
        K=round(K,1), D=round(D,1), J=round(J,1),
        vol_ratio=round(vol_ratio,2), vma5_gt_vma20=bool(vma5 > vma20),
        h20=round(h20,2), l20=round(l20,2), dist_h20=round(dist_h20,2),
        support=support, resistance=resist, stage=stage,
        score=round(s,1), notes=';'.join(notes))

def main():
    import sys
    # 用法: python ai_hardware_screen.py AIYJ GZGG  (默认 AIYJ)
    tags = sys.argv[1:] or ['AIYJ']
    out_prefix = 'screen_' + '_'.join(t.lower() for t in tags) if len(tags) > 1 else 'ai_hardware_screen'
    stocks, seen = [], set()
    membership = {}
    for tag in tags:
        for mkt, code in parse_blk(os.path.join(HT, r'T0002\blocknew\%s.blk' % tag)):
            membership.setdefault((mkt, code), []).append(tag)
            if (mkt, code) not in seen:
                seen.add((mkt, code)); stocks.append((mkt, code))
    names = load_names()
    results, missing = [], []
    for mkt, code in stocks:
        bars = read_day(mkt, code)
        if bars is None:
            missing.append('%s%s' % (mkt, code)); continue
        a = analyze(bars)
        if a is None:
            missing.append('%s%s(历史不足)' % (mkt, code)); continue
        a['market'], a['code'], a['name'] = mkt, code, names.get((mkt, code), 'N/A')
        a['blocks'] = '+'.join(membership[(mkt, code)])
        results.append(a)
    results.sort(key=lambda x: -x['score'])
    with open(os.path.join(OUT_DIR, out_prefix + '.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(total=len(stocks), analyzed=len(results), missing=missing, results=results), f, ensure_ascii=False, indent=1)
    # 文本总表
    lines = ['代码\t名称\t板块\t收盘\tMA5\tMA10\tMA20\tMA60\t5日%\t20日%\tMACD\tK/D\t量比\t阶段\t评分']
    for r in results:
        lines.append('%s%s\t%s\t%s\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%s\t%s\t%s\t%.1f/%.1f\t%.2f\t%s\t%.1f' % (
            r['market'], r['code'], r['name'], r['blocks'], r['close'], r['ma5'], r['ma10'], r['ma20'], r['ma60'],
            r['ret5'], r['ret20'], r['macd_state'], r['K'], r['D'], r['vol_ratio'], r['stage'], r['score']))
    with open(os.path.join(OUT_DIR, out_prefix + '_table.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('prefix=%s stocks=%d analyzed=%d missing=%d names_hit=%d' % (
        out_prefix, len(stocks), len(results), len(missing), sum(1 for r in results if r['name'] != 'N/A')))
    print('last_dates:', sorted(set(r['last_date'] for r in results)))

main()
