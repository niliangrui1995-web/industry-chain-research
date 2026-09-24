import csv, traceback
from collections import Counter
p=r"D:\vcp_hunter\产业链投研\deliverables\technical-analyst\20260924\blocknew_gzgg_aiyj_weekly_snapshot.csv"
out=[]
def f(r,k):
    try:return float(r[k])
    except:return None
def s(r,k,w=6,d=1):
    v=f(r,k)
    return "N/A".rjust(w) if v is None else f"{v:.{d}f}".rjust(w)
def si(r,k,w=4):
    v=f(r,k)
    return "N/A".rjust(w) if v is None else f"{v:.0f}".rjust(w)
try:
    rows=list(csv.DictReader(open(p,encoding='utf-8-sig')))
    out.append(f"total={len(rows)} error={sum(1 for r in rows if r['error'])} wnote={sum(1 for r in rows if r.get('w_note'))}")
    out.append("errors: "+str([(r['code'],r['error']) for r in rows if r['error']]))
    out.append("wnote: "+str([(r['code'],r['name'],r['w_note']) for r in rows if r.get('w_note')]))
    for block in ['关注个股','AI硬件']:
        grp=[r for r in rows if r['block']==block]
        out.append("")
        out.append(f"===== {block} ({len(grp)}) =====")
        out.append("resonance: "+str(dict(Counter(r['resonance'] for r in grp))))
        for t in ['日周共振向上','日强周平','周多日震(回踩确认)','日多周空(反弹性质)','周多日空(深度回调)','双周期震荡','双周期偏弱','样本不足']:
            sub=[r for r in grp if r['resonance']==t]
            if not sub: continue
            out.append(f"-- {t} ({len(sub)}) --")
            for r in sorted(sub,key=lambda x:-(f(x,'chg20') or -999)):
                out.append(f"{r['code']} {r['name']:<8} 收{r['close']:>8} 日{r['pct_chg']:>6}% 5日{s(r,'chg5')}% 20日{s(r,'chg20')}% | 日{r['trend']:<4} 周{r['w_trend']:<5} 周MA10偏{s(r,'w_vs_ma10')}% 周位置{si(r,'w_pos20')}% 周距高{s(r,'w_from_hi20')}% 周MACD{s(r,'w_macd_bar',7,2)} {r['w_macd_cross5']:<10} | RSI6={s(r,'rsi6',5)} J={s(r,'kdj_j',6)} 量比{s(r,'vol_ratio',5,2)} 日MA20偏{s(r,'vs_ma20')}% 距60高{s(r,'from_hi60')}% | 周支撑{r['w_sup']} 周压力{r['w_res']} 日支撑{r['lo20']} 日压力{r['hi20']}")
except Exception:
    out.append(traceback.format_exc())
open(r"D:\vcp_hunter\产业链投研\outputs\weekly_summary.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")