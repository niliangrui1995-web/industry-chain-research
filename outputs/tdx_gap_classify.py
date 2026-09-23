# -*- coding: utf-8 -*-
"""按涨跌幅限制精确甄别除权事件（硬判据）。

A股涨跌幅限制:
  沪主板 60xxxx     ±10%
  深主板 000/001/002/003  ±10%
  科创板 688xxx     ±20%
  创业板 300/301    ±20%
  北交所 92/83/87/43 ±30%
  ETF 51x/15x/56x/58x ±10% (份额折算除外)
单日跌幅绝对值超过限制 +0.5pp -> 必然为除权/份额折算。
"""
import os, json

OUT = os.path.dirname(os.path.abspath(__file__))


def limit_of(code):
    if code.startswith(('51', '15', '56', '58')):
        return 10.0
    if code.startswith(('92', '83', '87', '43', '8')):
        return 30.0
    if code.startswith('688'):
        return 20.0
    if code.startswith(('30', '30')):
        return 20.0
    if code.startswith(('300', '301')):
        return 20.0
    if code.startswith(('60', '000', '001', '002', '003')):
        return 10.0
    return 10.0


rows = json.load(open(os.path.join(OUT, 'resonance_rows.json'), encoding='utf-8'))

print('=== 超涨跌幅限制 -> 确认为除权/份额折算 ===')
confirmed = {}
for r in rows:
    lim = limit_of(r['code'])
    for g in r.get('gaps') or []:
        if abs(g['ret']) > lim + 0.5:
            confirmed.setdefault(r['code'], {'name': r['name'], 'lim': lim, 'events': []})
            confirmed[r['code']]['events'].append({'date': g['date'], 'ret': g['ret']})
            print('  %s %-10s %s  %+7.2f%%  (限制±%.0f%%)' %
                  (r['code'], r['name'], g['date'], g['ret'], lim))

print('\n=== 汇总: %d 只确认有除权事件 ===' % len(confirmed))
for c, v in confirmed.items():
    print('  %s %-10s' % (c, v['name']), [(e['date'], e['ret']) for e in v['events']])

json.dump(confirmed, open(os.path.join(OUT, 'confirmed_split.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\n已写出 confirmed_split.json')
