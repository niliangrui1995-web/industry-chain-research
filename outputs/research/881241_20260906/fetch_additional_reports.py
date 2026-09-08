from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import requests
import fitz

ROOT = Path(__file__).parent / 'additional_reports'
ROOT.mkdir(exist_ok=True)
URLS = {
    'snibe_2026h1': 'https://static.cninfo.com.cn/finalpage/2026-08-14/1225471103.PDF',
    'snibe_2025fy': 'https://static.cninfo.com.cn/finalpage/2026-04-28/1225208420.PDF',
    'autobio_2026h1': 'https://www.autobio.com.cn/Uploads/ProductDocPdfFile/2026-08-26/6a8e8650e58fa.pdf',
    'microtech_2026h1': 'https://static.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-08-27/688029_20260827_9EXF.pdf',
    'endovastec_2026h1': 'https://static.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-08-27/688016_20260827_DQ1Q.pdf',
}

def fetch(pair):
    name, url = pair
    try:
        r = requests.get(url, timeout=40)
        r.raise_for_status()
        if not r.content.startswith(b'%PDF'):
            raise ValueError('not PDF')
        path = ROOT / (name + '.pdf')
        path.write_bytes(r.content)
        doc = fitz.open(path)
        texts = [f'\n=== PAGE {i + 1} ===\n' + p.get_text() for i, p in enumerate(doc)]
        path.with_suffix('.txt').write_text(''.join(texts), encoding='utf-8')
        return {'name': name, 'url': url, 'pages': len(doc), 'status': 'ok'}
    except Exception as e:
        return {'name': name, 'url': url, 'status': 'error', 'error': str(e)}

if __name__ == '__main__':
    results = list(ThreadPoolExecutor(max_workers=4).map(fetch, URLS.items()))
    (ROOT / 'manifest.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(results, ensure_ascii=False))
