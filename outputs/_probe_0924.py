import os, struct, re
out=[]
# 1) 板块文件与成分数
for fn in ('GZGG.blk','AIYJ.blk'):
    p=rf"D:\HT\T0002\blocknew\{fn}"
    data=open(p,'rb').read().decode('gbk',errors='ignore')
    m=re.findall(r'(\d)(\d{6})',data)
    out.append(f"{fn}: {len(m)} 条, 去重 {len(set(c for _,c in m))} 只, 大小 {os.path.getsize(p)}B")
# 2) 映射确认
cfg=open(r"D:\HT\T0002\blocknew\blocknew.cfg",'rb').read().decode('gbk',errors='ignore').replace('\x00','')
for seg in cfg.split():
    if seg in ('GZGG','AIYJ'): out.append("cfg hit: "+seg)
# 3) 日线新鲜度
for mkt,code in [("sh","600519"),("sh","688293"),("sz","300308"),("bj","920045")]:
    p=rf"D:\HT\vipdoc\{mkt}\lday\{mkt}{code}.day"
    with open(p,'rb') as f: d=f.read()
    n=len(d)//32
    last=struct.unpack('<I', d[(n-1)*32:(n-1)*32+4])[0]
    c=struct.unpack('<I', d[(n-1)*32+16:(n-1)*32+20])[0]/100
    out.append(f"{code}: recs={n} last_date={last} close={c}")
open(r"D:\vcp_hunter\产业链投研\outputs\_probe_0924.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")