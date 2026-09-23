# -*- coding: utf-8 -*-
"""
扫描通达信自定义板块(关注个股 GZGG / AI硬件 AIYJ)全部个股的纯技术面快照。
数据来源: D:\\HT\\vipdoc 本地日线(不复权) -> 脚本内做除权缺口识别与前复权近似处理。
输出: deliverables/technical-analyst/2026-09-22/block_technical_snapshot.csv + 控制台分组摘要。
注意: 本地日线为不复权数据, 除权缺口识别为近似方法(超出涨跌停的跳空视为除权), 结果仅供技术面筛选参考。
"""
import os, struct, sys, csv, math

sys.stdout.reconfigure(encoding='utf-8')

BLK_DIR = r'D:\HT\T0002\blocknew'
CACHE = r'D:\HT\T0002\hq_cache'
VIPDOC = r'D:\HT\vipdoc'
OUT_DIR = r'D:\vcp_hunter\产业链投研\deliverables\technical-analyst\2026-09-22'
os.makedirs(OUT_DIR, exist_ok=True)

LAST_DATE_EXPECT = 20260922

# ---------- 板块与名称 ----------
def read_blk(fn):
    with open(os.path.join(BLK_DIR, fn), 'r') as f:
        return [l.strip() for l in f if l.strip()]

name_map = {}
with open(os.path.join(CACHE, 'infoharbor_ex.code'), 'rb') as f:
    for line in f.read().decode('gbk', errors='replace').splitlines():
        p = line.split('|')
        if len(p) >= 2 and len(p[0]) == 6:
            name_map[p[0]] = p[1].strip()

# 流通A股(万股) from base.dbf
def read_dbf_ltag(path):
    with open(path, 'rb') as f:
        data = f.read()
    num = struct.unpack('<I', data[4:8])[0]
    hlen = struct.unpack('<H', data[8:10])[0]
    rlen = struct.unpack('<H', data[10:12])[0]
    fields, off = [], 32
    while data[off] != 0x0D:
        fields.append((data[off:off+11].split(b'\x00')[0].decode('ascii'), data[off+16]))
        off += 32
    idx = {n: i for i, (n, l) in enumerate(fields)}
    out = {}
    pos = hlen
    for _ in range(num):
        rec = data[pos:pos+rlen]; pos += rlen
        if rec[0:1] == b'*':
            continue
        p, vals = 1, []
        for n, l in fields:
            vals.append(rec[p:p+l]); p += l
        sc = vals[idx['SC']].decode().strip()
        dm = vals[idx['GPDM']].decode().strip()
        try:
            ltag = float(vals[idx['LTAG']].decode().strip() or 'nan')
        except ValueError:
            ltag = float('nan')
        out[(sc, dm)] = ltag  # 万股
    return out

ltag_map = read_dbf_ltag(os.path.join(CACHE, 'base.dbf'))

# ---------- 日线读取 ----------
def read_lday(mkt, code):
    p = os.path.join(VIPDOC, mkt, 'lday', f'{mkt}{code}.day')
    if not os.path.exists(p):
        return None
    with open(p, 'rb') as f:
        data = f.read()
    n = len(data) // 32
    recs = []
    for i in range(n):
        d, o, h, l, c, amt, vol, _ = struct.unpack('<IIIIIfII', data[i*32:(i+1)*32])
        recs.append([d, o/100.0, h/100.0, l/100.0, c/100.0, amt, vol])
    return recs

def limit_pct(mkt, code):
    if mkt == 'bj':
        return 0.30
    if code.startswith(('688', '300', '301')):
        return 0.20
    return 0.10

def adjust(recs, mkt, code):
    """除权缺口识别 + 前复权近似: 跳空超过涨跌停幅度视为除权, 历史价格乘以累计因子, 量除以因子。"""
    lim = limit_pct(mkt, code)
    factors = [1.0] * len(recs)
    cum = 1.0
    gaps = []
    for i in range(len(recs) - 1, 0, -1):
        prev_c, today_o = recs[i-1][4], recs[i][1]
        if prev_c > 0:
            gap = today_o / prev_c - 1
            if abs(gap) > lim + 0.011:
                f = today_o / prev_c
                cum *= f
                gaps.append((recs[i][0], round(gap*100, 1)))
        factors[i-1] = cum
    adj = []
    for r, f in zip(recs, factors):
        adj.append([r[0], r[1]*f, r[2]*f, r[3]*f, r[4]*f, r[5], r[6]/f if f > 0 else r[6]])
    return adj, gaps

# ---------- 指标 ----------
def sma(xs, n):
    out, s = [], 0.0
    for i, x in enumerate(xs):
        s += x
        if i >= n:
            s -= xs[i-n]
        out.append(s/n if i >= n-1 else None)
    return out

def ema_series(xs, n):
    out, k = [], 2.0/(n+1)
    e = None
    for x in xs:
        e = x if e is None else x*k + e*(1-k)
        out.append(e)
    return out

def macd(closes):
    e12, e26 = ema_series(closes, 12), ema_series(closes, 26)
    dif = [a-b for a, b in zip(e12, e26)]
    dea = ema_series(dif, 9)
    bar = [(d-e)*2 for d, e in zip(dif, dea)]
    return dif, dea, bar

def rsi(closes, n):
    gains, losses = [], []
    for i in range(1, len(closes)):
        ch = closes[i] - closes[i-1]
        gains.append(max(ch, 0)); losses.append(max(-ch, 0))
    if len(gains) < n:
        return None
    ag = sum(gains[:n])/n; al = sum(losses[:n])/n
    for i in range(n, len(gains)):
        ag = (ag*(n-1) + gains[i])/n
        al = (al*(n-1) + losses[i])/n
    return 100.0 if al == 0 else 100 - 100/(1 + ag/al)

def kdj(recs, n=9):
    k, d = 50.0, 50.0
    for i in range(len(recs)):
        lo = min(r[3] for r in recs[max(0, i-n+1):i+1])
        hi = max(r[2] for r in recs[max(0, i-n+1):i+1])
        rsv = 50.0 if hi == lo else (recs[i][4]-lo)/(hi-lo)*100
        k = k*2/3 + rsv/3
        d = d*2/3 + k/3
    j = 3*k - 2*d
    return k, d, j

def boll(closes, n=20, k=2):
    if len(closes) < n:
        return None
    win = closes[-n:]
    mid = sum(win)/n
    sd = math.sqrt(sum((x-mid)**2 for x in win)/n)
    return mid, mid+k*sd, mid-k*sd

# ---------- 主流程 ----------
def analyze(mkt, code, block):
    raw = read_lday(mkt, code)
    row = {'block': block, 'mkt': mkt.upper(), 'code': code,
           'name': name_map.get(code, 'N/A')}
    if not raw or len(raw) < 70:
        row['error'] = 'no_data' if not raw else f'insufficient({len(raw)})'
        return row
    recs, gaps = adjust(raw, mkt, code)
    closes = [r[4] for r in recs]
    vols = [r[6] for r in recs]
    n = len(recs)
    last = recs[-1]
    row['last_date'] = last[0]
    row['stale'] = last[0] != LAST_DATE_EXPECT
    # 交易日历完整性: 最近60日记录数(粗校验停牌)
    row['n_last60'] = min(60, n)
    c = closes[-1]
    prev = closes[-2]
    row['close'] = round(c, 2)
    row['pct_chg'] = round((c/prev - 1)*100, 2)
    ma5, ma10, ma20, ma60 = sma(closes, 5)[-1], sma(closes, 10)[-1], sma(closes, 20)[-1], sma(closes, 60)[-1]
    row['ma5'], row['ma10'], row['ma20'], row['ma60'] = [round(x, 2) if x else None for x in (ma5, ma10, ma20, ma60)]
    row['vs_ma20'] = round((c/ma20-1)*100, 1) if ma20 else None
    row['vs_ma60'] = round((c/ma60-1)*100, 1) if ma60 else None
    row['ma20_slope'] = round((ma20/sma(closes, 20)[-6]-1)*100, 1) if len(closes) > 25 else None
    dif, dea, bar = macd(closes)
    row['dif'], row['dea'], row['macd_bar'] = round(dif[-1], 3), round(dea[-1], 3), round(bar[-1], 3)
    # 近5日金叉/死叉
    cross = ''
    for i in range(-5, 0):
        if dif[i-1] <= dea[i-1] and dif[i] > dea[i]:
            cross = f'金叉({-i}日前)'
        elif dif[i-1] >= dea[i-1] and dif[i] < dea[i]:
            cross = f'死叉({-i}日前)'
    row['macd_cross5'] = cross
    row['rsi6'] = round(rsi(closes, 6), 1)
    row['rsi14'] = round(rsi(closes, 14), 1)
    k, d, j = kdj(recs[-40:])
    row['kdj_j'] = round(j, 1)
    b = boll(closes)
    if b:
        mid, up, lo = b
        row['boll_pos'] = round((c-lo)/(up-lo)*100, 0) if up > lo else None  # 0=下轨 100=上轨
    v5 = sum(vols[-5:])/5
    v20 = sum(vols[-20:])/20
    row['vol_ratio'] = round(vols[-1]/v20, 2) if v20 else None
    row['vol5_vs20'] = round(v5/v20, 2) if v20 else None
    hi60 = max(r[2] for r in recs[-60:])
    lo60 = min(r[3] for r in recs[-60:])
    row['hi60'] = round(hi60, 2)
    row['lo60'] = round(lo60, 2)
    row['from_hi60'] = round((c/hi60-1)*100, 1)
    row['range_pos60'] = round((c-lo60)/(hi60-lo60)*100, 0) if hi60 > lo60 else None
    hi20 = max(r[2] for r in recs[-20:])
    lo20 = min(r[3] for r in recs[-20:])
    row['hi20'], row['lo20'] = round(hi20, 2), round(lo20, 2)
    # 近20日涨停次数(主板10/创业科创20/北30, 近似按9.8/19.8/29.5)
    lim = limit_pct(mkt, code)*100
    th = lim - 0.3
    row['limitups_20'] = sum(1 for i in range(-20, 0)
                             if closes[i-1] > 0 and (closes[i]/closes[i-1]-1)*100 >= th)
    # 换手率
    ltag = ltag_map.get(({'sh': '1', 'sz': '0', 'bj': '2'}[mkt], code), float('nan'))
    # 本数据集 lday 成交量单位为股(已用 amount≈vol*close 验证), LTAG 为万股
    row['turnover'] = round(vols[-1]/(ltag*10000)*100, 2) if ltag == ltag and ltag > 0 else None
    # 5日/20日涨跌
    row['chg5'] = round((c/closes[-6]-1)*100, 1) if n > 5 else None
    row['chg20'] = round((c/closes[-21]-1)*100, 1) if n > 21 else None
    row['ex_gaps_recent'] = ';'.join(f'{d}:{g}%' for d, g in gaps[:3])
    return row

def trend_tag(r):
    if r.get('error') or r.get('ma60') is None:
        return '数据不足'
    c = r['close']
    above = sum([c > r['ma5'], c > r['ma10'], c > r['ma20'], c > r['ma60']])
    aligned = r['ma5'] > r['ma10'] > r['ma20'] > r['ma60']
    if aligned and c > r['ma5']:
        return '强多头'
    if above >= 3 and (r['ma20_slope'] or 0) > 0:
        return '多头'
    if above <= 1 and (r['ma20_slope'] or 0) < 0:
        return '空头'
    return '震荡'

results = []
for block, fn, mktmap in [('关注个股', 'GZGG.blk', None), ('AI硬件', 'AIYJ.blk', None)]:
    for c in read_blk(fn):
        mkt = {'0': 'sz', '1': 'sh', '2': 'bj'}[c[0]]
        results.append(analyze(mkt, c[1:], block))

for r in results:
    r['trend'] = trend_tag(r)

# ---------- 输出 ----------
cols = ['block', 'mkt', 'code', 'name', 'last_date', 'close', 'pct_chg', 'chg5', 'chg20',
        'trend', 'ma5', 'ma10', 'ma20', 'ma60', 'vs_ma20', 'vs_ma60', 'ma20_slope',
        'dif', 'dea', 'macd_bar', 'macd_cross5', 'rsi6', 'rsi14', 'kdj_j', 'boll_pos',
        'vol_ratio', 'vol5_vs20', 'turnover', 'hi20', 'lo20', 'hi60', 'lo60',
        'from_hi60', 'range_pos60', 'limitups_20', 'stale', 'ex_gaps_recent', 'error']
csv_path = os.path.join(OUT_DIR, 'block_technical_snapshot.csv')
with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
    w.writeheader()
    for r in results:
        w.writerow(r)
print('CSV ->', csv_path)

ok = [r for r in results if not r.get('error')]
bad = [r for r in results if r.get('error')]
print(f'有效 {len(ok)} / 共 {len(results)}; 异常: {[(r["code"], r.get("error")) for r in bad]}')
stale = [r for r in ok if r.get('stale')]
print('停牌/数据滞后:', [(r['code'], r['name'], r['last_date']) for r in stale])

for block in ['关注个股', 'AI硬件']:
    print(f'\n===== {block} =====')
    grp = [r for r in ok if r['block'] == block]
    for t in ['强多头', '多头', '震荡', '空头', '数据不足']:
        sub = [r for r in grp if r['trend'] == t]
        if not sub:
            continue
        print(f'-- {t} ({len(sub)}) --')
        for r in sorted(sub, key=lambda x: -(x['chg20'] or -999)):
            print(f"{r['code']} {r['name']:<8} 收{r['close']:>8} 日{r['pct_chg']:>6}% 5日{r['chg5']:>6}% 20日{r['chg20']:>6}% "
                  f"MA20偏{r['vs_ma20']:>6}% MA60偏{r['vs_ma60']:>6}% 量比{r['vol_ratio']:>5} "
                  f"RSI6={r['rsi6']:>5} J={r['kdj_j']:>6} 距60高{r['from_hi60']:>6}% 60区位{r['range_pos60']:>4}% "
                  f"MACD柱{r['macd_bar']:>7} {r['macd_cross5']}")
