from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests
import fitz
import json

ROOT = Path(__file__).parent / 'edan'
ROOT.mkdir(exist_ok=True)
def query(dates):
    r=requests.post('https://www.cninfo.com.cn/new/hisAnnouncement/query', data={'pageNum':'1','pageSize':'30','tabName':'fulltext','column':'szse','stock':'','searchkey':'理邦仪器','secid':'','plate':'','category':'','trade':'','seDate':dates,'sortName':'','sortType':'','isHLtitle':'true'}, headers={'Referer':'https://www.cninfo.com.cn/'}, timeout=30)
    r.raise_for_status()
    data=r.json()
    return [x for x in (data.get('announcements') or []) if x.get('secCode')=='300206']

items=[]
for dates in ['2026-08-25~2026-09-06','2026-03-30~2026-03-31']:
    items.extend(query(dates))
(ROOT/'announcement_index.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
selected=[]
for item in items:
    t=item['announcementTitle']
    if ('半年度报告' in t and '摘要' not in t) or ('2025年年度报告' in t and '摘要' not in t) or '8月27日投资者关系' in t:
        selected.append(item)

def fetch(item):
    url='https://static.cninfo.com.cn/'+item['adjunctUrl']
    key='edan_2025fy' if '2025年年度报告' in item['announcementTitle'] else ('edan_2026h1' if '半年度报告' in item['announcementTitle'] else 'edan_ir_20260828')
    r=requests.get(url,timeout=40);r.raise_for_status()
    p=ROOT/(key+'.pdf');p.write_bytes(r.content)
    doc=fitz.open(p)
    p.with_suffix('.txt').write_text(''.join(f'\n=== PAGE {i+1} ===\n'+page.get_text() for i,page in enumerate(doc)),encoding='utf-8')
    return {'key':key,'title':item['announcementTitle'],'url':url,'pages':len(doc),'status':'ok'}

results=list(ThreadPoolExecutor(max_workers=3).map(fetch,selected))
(ROOT/'manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False))
