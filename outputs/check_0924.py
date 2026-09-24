import csv
p=r"D:\vcp_hunter\产业链投研\deliverables\technical-analyst\20260924\blocknew_gzgg_aiyj_weekly_snapshot.csv"
rows=list(csv.DictReader(open(p,encoding='utf-8-sig')))
out=[]
out.append(f"total={len(rows)}")
out.append("last_date分布: "+str({d:sum(1 for r in rows if r['last_date']==d) for d in sorted(set(r['last_date'] for r in rows))}))
out.append("stale=True: "+str([(r['code'],r['name'],r['last_date']) for r in rows if r.get('stale')=='True']))
out.append("515880 name: "+str([r['name'] for r in rows if r['code']=='515880']))
out.append("688825 row: "+str([(r['close'],r['error']) for r in rows if r['code']=='688825']))
open(r"D:\vcp_hunter\产业链投研\outputs\check_0924.txt","w",encoding="utf-8").write("\n".join(out))