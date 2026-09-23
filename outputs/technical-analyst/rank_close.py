import csv
p=r"D:\vcp_hunter\产业链投研\deliverables\technical-analyst\20260923\blocknew_gzgg_aiyj_snapshot.csv"
rows=list(csv.DictReader(open(p,encoding='utf-8-sig')))
def f(r,k):
    try:return float(r[k])
    except:return -999
for block in ['关注个股','AI硬件']:
    rs=[r for r in rows if r['block']==block and not r['error']]
    def score(r):
        trend={'强多头':4,'多头':3,'震荡':1,'空头':0}.get(r['trend'],0)
        return trend*10+max(-20,min(60,f(r,'chg20')))*0.12+max(-20,min(20,f(r,'macd_bar')))*0.3+max(-10,min(10,f(r,'vol5_vs20')-1))*2 - max(0,f(r,'rsi6')-82)*0.12
    for r in sorted(rs,key=score,reverse=True)[:20]:
        print(block, r['code'],r['name'],r['trend'],'close',r['close'],'day',r['pct_chg'],'5d',r['chg5'],'20d',r['chg20'],'ma20',r['vs_ma20'],'ma60',r['vs_ma60'],'macd',r['macd_bar'],'cross',r['macd_cross5'],'rsi6',r['rsi6'],'j',r['kdj_j'],'vol5',r['vol5_vs20'],'fromhi',r['from_hi60'])
    print('---')
print('counts',len(rows),sum(1 for r in rows if r['error']))