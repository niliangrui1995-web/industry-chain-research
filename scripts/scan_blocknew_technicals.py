# -*- coding: utf-8 -*-
"""
扫描通达信自建板块「关注个股 GZGG.blk」与「AI硬件 AIYJ.blk」全部个股的纯技术面快照。
板块成分来源: D:\\HT\\T0002\\blocknew\\*.blk (每行7位: 首位市场 0=SZ 1=SH 2=BJ + 6位代码)
名称来源: D:\\HT\\T0002\\hq_cache\\infoharbor_ex.code
行情来源: D:\\HT\\vipdoc 本地日线(不复权, 最新至20260922) -> 除权缺口识别 + 前复权近似。
输出: deliverables/technical-analyst/20260923/blocknew_gzgg_aiyj_snapshot.csv + 板块成分清单 CSV。
注意: 本地日线为不复权数据, 除权识别为近似方法, 结果仅供技术面筛选参考。
"""
import os, struct, sys, csv, math, re

sys.stdout.reconfigure(encoding='utf-8')

BLOCKNEW = r'D:\HT\T0002\blocknew'
CACHE = r'D:\HT\T0002\hq_cache'
VIPDOC = r'D:\HT\vipdoc'
OUT_DIR = r'D:\vcp_hunter\产业链投研\deliverables\technical-analyst\20260923'
os.makedirs(OUT_DIR, exist_ok=True)

LAST_DATE_EXPECT = 20260923
BLOCKS = [('关注个股', 'GZGG.blk'), ('AI硬件', 'AIYJ.blk')]

# ---------- 板块成分解析(.blk) ----------
def parse_blk(fname):
    data = open(os.path.join(BLOCKNEW, fname), 'rb').read().decode('gbk', errors='ignore')
    members = re.findall(r'(\d)(\d{6})', data)
    seen, roster = set(), []
    for mkt_p, sc in members:
        if sc in seen:
            continue
        seen.add(sc)
        mkt = {'0': 'sz', '1': 'sh', '2': 'bj'}[mkt_p]
        roster.append((mkt, sc))
    return roster

# ---------- 名称 ----------
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
        out[(sc, dm)] = ltag
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
    cross = ''
    for i in range(-5, 0):
        if dif[i-1] <= dea[i-1] and dif[i] > dea[i]:
            cross = f'金叉({-i}日前)'
        elif dif[i-1] >= dea[i-1] and dif[i] < dea[i]:
            cross = f'死叉({-i}日前)'
    row['macd_cross5'] = cross
    row['dif_above0'] = dif[-1] > 0
    # MACD柱连续性: 近5日柱值序列
    row['bar_seq5'] = ','.join(f"{bar[i]:.3f}" for i in range(-5, 0))
    row['rsi6'] = round(rsi(closes, 6), 1)
    row['rsi14'] = round(rsi(closes, 14), 1)
    k, d, j = kdj(recs[-40:])
    row['kdj_k'], row['kdj_d'], row['kdj_j'] = round(k,1), round(d,1), round(j, 1)
    b = boll(closes)
    if b:
        mid, up, lo = b
        row['boll_pos'] = round((c-lo)/(up-lo)*100, 0) if up > lo else None
        row['boll_up'] = round(up, 2)
        row['boll_lo'] = round(lo, 2)
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
    # 支撑压力: 近20日密集成交区近似(高低点)
    row['sup20'] = row['lo20']
    row['res20'] = row['hi20']
    lim = limit_pct(mkt, code)*100
    th = lim - 0.3
    row['limitups_20'] = sum(1 for i in range(-20, 0)
                             if closes[i-1] > 0 and (closes[i]/closes[i-1]-1)*100 >= th)
    ltag = ltag_map.get(({'sh': '1', 'sz': '0', 'bj': '2'}[mkt], code), float('nan'))
    row['turnover'] = round(vols[-1]/(ltag*10000)*100, 2) if ltag == ltag and ltag > 0 else None
    row['chg5'] = round((c/closes[-6]-1)*100, 1) if n > 5 else None
    row['chg10'] = round((c/closes[-11]-1)*100, 1) if n > 11 else None
    row['chg20'] = round((c/closes[-21]-1)*100, 1) if n > 21 else None
    # 量价背离粗判: 近10日价格新高但量能低于前10日均量
    if n > 22:
        p_hi10 = max(closes[-10:]); p_hi_prev = max(closes[-20:-10])
        v_10 = sum(vols[-10:])/10; v_prev = sum(vols[-20:-10])/10
        row['pv_diverge'] = (p_hi10 >= p_hi_prev*0.999) and (v_10 < v_prev*0.85)
    # 缩量回踩: 5日跌但量缩(近3日均量<近10日均量70%)且趋势仍多
    row['shrink_pullback'] = bool(row['chg5'] is not None and row['chg5'] < -3
                                 and sum(vols[-3:])/3 < v20*0.7)
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
rosters = {}
for bname, fname in BLOCKS:
    roster = parse_blk(fname)
    rosters[bname] = roster
    print(f'{bname}({fname}): 解析 {len(roster)} 只(去重后)')
    for mkt, sc in roster:
        results.append(analyze(mkt, sc, bname))

for r in results:
    r['trend'] = trend_tag(r)

# ---------- 输出 ----------
cols = ['block', 'mkt', 'code', 'name', 'last_date', 'close', 'pct_chg', 'chg5', 'chg10', 'chg20',
        'trend', 'ma5', 'ma10', 'ma20', 'ma60', 'vs_ma20', 'vs_ma60', 'ma20_slope',
        'dif', 'dea', 'macd_bar', 'macd_cross5', 'bar_seq5', 'dif_above0', 'rsi6', 'rsi14',
        'kdj_k', 'kdj_d', 'kdj_j', 'boll_pos', 'boll_up', 'boll_lo', 'vol_ratio', 'vol5_vs20', 'turnover',
        'hi20', 'lo20', 'sup20', 'res20', 'hi60', 'lo60', 'from_hi60', 'range_pos60', 'limitups_20',
        'pv_diverge', 'shrink_pullback', 'stale', 'ex_gaps_recent', 'error']
csv_path = os.path.join(OUT_DIR, 'blocknew_gzgg_aiyj_snapshot.csv')
with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
    w.writeheader()
    for r in results:
        w.writerow(r)
print('CSV ->', csv_path)

for bname, roster in rosters.items():
    rp = os.path.join(OUT_DIR, f'roster_{bname}.csv')
    with open(rp, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['mkt', 'code', 'name'])
        for mkt, sc in roster:
            w.writerow([mkt.upper(), sc, name_map.get(sc, 'N/A')])
    print('ROSTER ->', rp)

ok = [r for r in results if not r.get('error')]
bad = [r for r in results if r.get('error')]
print(f'\n有效 {len(ok)} / 共 {len(results)}; 异常: {[(r["code"], r.get("error")) for r in bad]}')
stale = [r for r in ok if r.get('stale')]
print('数据滞后(<20260922):', [(r['code'], r['name'], r['last_date']) for r in stale])

s1 = {c for _, c in rosters[BLOCKS[0][0]]}
s2 = {c for _, c in rosters[BLOCKS[1][0]]}
print(f'两板块交集 {len(s1 & s2)} 只: {sorted(s1 & s2)}')

for bname, _ in BLOCKS:
    print(f'\n===== {bname} =====')
    grp = [r for r in ok if r['block'] == bname]
    for t in ['强多头', '多头', '震荡', '空头', '数据不足']:
        sub = [r for r in grp if r['trend'] == t]
        if not sub:
            continue
        print(f'-- {t} ({len(sub)}) --')
        for r in sorted(sub, key=lambda x: -(x['chg20'] or -999)):
            print(f"{r['code']} {r['name']:<8} 收{r['close']:>8} 日{r['pct_chg']:>6}% 5日{r['chg5']:>6}% 20日{r['chg20']:>6}% "
                  f"MA20偏{r['vs_ma20']:>6}% 量比{r['vol_ratio']:>5} "
                  f"RSI6={r['rsi6']:>5} J={r['kdj_j']:>6} 距60高{r['from_hi60']:>6}% "
                  f"MACD柱{r['macd_bar']:>7} {r['macd_cross5']}")
