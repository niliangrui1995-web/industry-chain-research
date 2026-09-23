# -*- coding: utf-8 -*-
"""
对 gxt_cpo_technical_snapshot.csv 做透明规则综合打分(0-100), 输出各板块 Top 排名;
并对指定个股输出近 60 日明细(支撑/压力位、平台、量价), 供撰写入选理由。
打分规则(纯技术面, 短线 1-2 交易日视角):
  趋势: 强多头30 / 多头20 / 震荡8 / 空头0
  MACD: 近5日金叉+12; DIF>0且柱>0+8; 仅柱>0+4; 近5日死叉-12
  量比: 1.2~3.0 +10; 0.8~1.2 +5; >3.0 +3; <0.8 +1
  RSI6: 50~80 +10; 80~88 +5; >88 +0; <50 +2
  位置(距60日高): >-5% +12; -5~-15% +8; -15~-30% +4; <-30% +1
  KDJ-J: 60~100 +6; >100 +2; <60 +3
  惩罚: chg20>50% -8; 单日跌>5%且量比>1.5 -10; 量比>2且当日跌 -6
"""
import os, csv, sys, struct, math

sys.stdout.reconfigure(encoding='utf-8')
OUT_DIR = r'D:\vcp_hunter\产业链投研\deliverables\technical-analyst\2026-09-23'
VIPDOC = r'D:\HT\vipdoc'

rows = list(csv.DictReader(open(os.path.join(OUT_DIR, 'gxt_cpo_technical_snapshot.csv'), encoding='utf-8-sig')))

def f(x, d=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d

def score(r):
    if r.get('error'):
        return None
    s = 0
    s += {'强多头': 30, '多头': 20, '震荡': 8, '空头': 0}.get(r['trend'], 0)
    cross = r.get('macd_cross5', '')
    dif, bar = f(r['dif']), f(r['macd_bar'])
    if '金叉' in cross:
        s += 12
    elif '死叉' in cross:
        s -= 12
    if dif is not None and dif > 0 and bar and bar > 0:
        s += 8
    elif bar and bar > 0:
        s += 4
    vr = f(r['vol_ratio'], 1.0)
    if 1.2 <= vr <= 3.0:
        s += 10
    elif 0.8 <= vr < 1.2:
        s += 5
    elif vr > 3.0:
        s += 3
    else:
        s += 1
    rsi6 = f(r['rsi6'], 50)
    if 50 <= rsi6 <= 80:
        s += 10
    elif 80 < rsi6 <= 88:
        s += 5
    elif rsi6 > 88:
        s += 0
    else:
        s += 2
    fh = f(r['from_hi60'], -50)
    if fh > -5:
        s += 12
    elif fh > -15:
        s += 8
    elif fh > -30:
        s += 4
    else:
        s += 1
    j = f(r['kdj_j'], 50)
    if 60 <= j <= 100:
        s += 6
    elif j > 100:
        s += 2
    else:
        s += 3
    chg20 = f(r['chg20'], 0)
    if chg20 > 50:
        s -= 8
    pct = f(r['pct_chg'], 0)
    if pct < -5 and vr > 1.5:
        s -= 10
    if vr > 2 and pct < 0:
        s -= 6
    return s

for r in rows:
    r['score'] = score(r)

for bname in ['光通信', 'CPO概念']:
    grp = [r for r in rows if r['block'] == bname and r['score'] is not None]
    grp.sort(key=lambda x: -x['score'])
    print(f'\n===== {bname} Top15 =====')
    for r in grp[:15]:
        print(f"{r['score']:>4} {r['code']} {r['name']:<7} {r['trend']:<3} 收{r['close']:>8} 日{r['pct_chg']:>6}% "
              f"5日{r['chg5']:>6}% 20日{r['chg20']:>6}% 量比{r['vol_ratio']:>5} RSI6={r['rsi6']:>5} "
              f"J={r['kdj_j']:>6} 距60高{r['from_hi60']:>6}% {r['macd_cross5']}")

# ---------- 明细: 支撑压力 ----------
def read_lday(mkt, code):
    p = os.path.join(VIPDOC, mkt.lower(), 'lday', f'{mkt.lower()}{code}.day')
    data = open(p, 'rb').read()
    n = len(data) // 32
    recs = []
    for i in range(n):
        d, o, h, l, c, amt, vol, _ = struct.unpack('<IIIIIfII', data[i*32:(i+1)*32])
        recs.append([d, o/100.0, h/100.0, l/100.0, c/100.0, amt, vol])
    return recs

def limit_pct(mkt, code):
    if mkt.lower() == 'bj':
        return 0.30
    if code.startswith(('688', '300', '301')):
        return 0.20
    return 0.10

def adjust(recs, mkt, code):
    lim = limit_pct(mkt, code)
    factors = [1.0] * len(recs)
    cum = 1.0
    for i in range(len(recs) - 1, 0, -1):
        prev_c, today_o = recs[i-1][4], recs[i][1]
        if prev_c > 0:
            gap = today_o / prev_c - 1
            if abs(gap) > lim + 0.011:
                cum *= today_o / prev_c
        factors[i-1] = cum
    return [[r[0], r[1]*f, r[2]*f, r[3]*f, r[4]*f, r[5], r[6]/f if f > 0 else r[6]] for r, f in zip(recs, factors)]

def sma(xs, n):
    return sum(xs[-n:]) / n if len(xs) >= n else None

def detail(mkt, code, name):
    recs = adjust(read_lday(mkt, code), mkt, code)
    closes = [r[4] for r in recs]
    vols = [r[6] for r in recs]
    c = closes[-1]
    ma5, ma10, ma20, ma60 = sma(closes,5), sma(closes,10), sma(closes,20), sma(closes,60)
    r60 = recs[-60:]
    # 近60日局部高点(压力位): 前高聚类
    highs = sorted([r[2] for r in r60], reverse=True)
    hi60 = highs[0]
    # 近20日平台上沿/下沿: 5-20日前区间
    seg = recs[-20:-5]
    plat_hi = max(r[2] for r in seg); plat_lo = min(r[3] for r in seg)
    lo20 = min(r[3] for r in recs[-20:])
    lo10 = min(r[3] for r in recs[-10:])
    v5 = sum(vols[-5:])/5; v20 = sum(vols[-20:])/20
    print(f'\n--- {code} {name} 收{c:.2f} ---')
    print(f'  MA5={ma5:.2f} MA10={ma10:.2f} MA20={ma20:.2f} MA60={ma60:.2f}')
    print(f'  60日高={hi60:.2f}({(c/hi60-1)*100:.1f}%) 20日平台={plat_lo:.2f}~{plat_hi:.2f} '
          f'10日低={lo10:.2f} 20日低={lo20:.2f}')
    print(f'  量: 昨量/20日均={vols[-1]/v20:.2f} 5日均/20日均={v5/v20:.2f}')
    print('  近10日:')
    for r in recs[-10:]:
        print(f'    {r[0]} O{r[1]:.2f} H{r[2]:.2f} L{r[3]:.2f} C{r[4]:.2f} 量比{r[6]/v20:.2f}')

PICKS = [('sz','300570'),('sz','300516'),('sz','301041'),('sz','300504'),('sz','002792'),
         ('sz','301205'),('sz','300684'),('sh','600601'),('sz','300698'),('sz','301085'),
         ('sh','688628'),('sz','301419'),('sh','603328')]
names = {r['code']: r['name'] for r in rows}
print('\n\n########## 候选明细 ##########')
for mkt, code in PICKS:
    detail(mkt, code, names.get(code, ''))
