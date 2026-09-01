import pandas as pd
import urllib.request
import json

csv_file = 'artifacts/ai_stocks_performance_0730_to_now.csv'
df = pd.read_csv(csv_file)

# 补充 603163, 603601, 300429
manual_updates = {
    '603163': {'0730': 69.95, 'latest': 77.87, 'date': '2026-08-05'},  # 80.61 on 08-06
    '603601': {'0730': 7.66, 'latest': 9.16, 'date': '2026-08-05'},    # 10.08 on 08-06
    '300429': {'0730': 8.98, 'latest': 10.33, 'date': '2026-08-05'},   # 10.43 on 08-06
}

# 历史 CSV 仍以旧代码 430139 记录华岭股份；按切换后的 920139 取数再写回该历史行。
source_code = '920139'
target_code = '430139'
secid = f'0.{source_code}'
url = f'https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=20260730&end=20260810'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        if data.get('data') and data['data'].get('klines'):
            klines = data['data']['klines']
            k_map = {k.split(',')[0]: float(k.split(',')[2]) for k in klines}
            if '2026-07-30' in k_map:
                dates = sorted(k_map.keys())
                manual_updates[target_code] = {'0730': k_map['2026-07-30'], 'latest': k_map[dates[-1]], 'date': dates[-1]}
except Exception as e:
    pass

# 更新 df
for idx, row in df.iterrows():
    code = str(row['代码']).zfill(6)
    if code in manual_updates:
        info = manual_updates[code]
        p_0730 = info['0730']
        p_latest = info['latest']
        pct = round((p_latest - p_0730) / p_0730 * 100, 2)
        df.loc[idx, '0730收盘价'] = p_0730
        df.loc[idx, '最新收盘价'] = p_latest
        df.loc[idx, '最新日期'] = info['date']
        df.loc[idx, '涨跌幅(%)'] = pct

# 重新保存
df.to_csv(csv_file, index=False, encoding='utf-8-sig')
print("全表数据填充完成，总记录数:", len(df), "有效涨跌幅记录数:", df['涨跌幅(%)'].notna().sum())
