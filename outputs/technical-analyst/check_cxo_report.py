from pathlib import Path
import re
p=Path(r'D:\vcp_hunter\产业链投研\outputs\CXO四大细分环节深度投研_20260922.html')
s=p.read_text(encoding='utf-8')
for bad in ['??','None','%s','\ufffd']:
    if bad in s: raise SystemExit('bad token: '+bad)
if re.search(r'(?<![A-Za-z])nan(?![A-Za-z])',s,re.I): raise SystemExit('bad token: nan')
for tag in ['html','head','body','section','table','tr','td','h2']:
    a=len(re.findall(r'<'+tag+r'(?:\s|>)',s,re.I)); b=len(re.findall(r'</'+tag+r'>',s,re.I))
    if a!=b: raise SystemExit(f'tag mismatch {tag}: {a}/{b}')
ids=re.findall(r'\bid="([^"]+)"',s)
if len(ids)!=len(set(ids)): raise SystemExit('duplicate ids')
if not re.search(r'<meta charset="utf-8">',s,re.I): raise SystemExit('missing utf8')
if not re.search(r'<meta name="viewport"',s,re.I): raise SystemExit('missing viewport')
print('PASS',len(s.encode('utf-8')),'bytes','sections',len(re.findall(r'<section',s,re.I)))
