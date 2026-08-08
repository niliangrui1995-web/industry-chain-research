import pandas as pd
import urllib.request
import json
import time
import sys

# 1. 读取 Excel
excel_path = 'AI产业链.xlsx'
df = pd.read_excel(excel_path, sheet_name='AI产业链')
valid_df = df[df['代码'].astype(str).str.contains(r'^\d{6}$')]

print(f"有效股票总数: {len(valid_df)}")

results = []

def get_secid(code):
    code_str = str(code).zfill(6)
    if code_str.startswith('6') or code_str.startswith('9'):
        return f"1.{code_str}"
    elif code_str.startswith('0') or code_str.startswith('3'):
        return f"0.{code_str}"
    elif code_str.startswith('8') or code_str.startswith('4'):
        return f"0.{code_str}"
    return f"0.{code_str}"

for idx, row in valid_df.iterrows():
    code = str(row['代码']).zfill(6)
    name = row['公司名称']
    sector = row['细分板块']
    secid = get_secid(code)

    # 尝试从东财获取日线
    url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=20260730&end=20260810"

    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    p_0730 = None
    p_latest = None
    date_latest = None

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('data') and data['data'].get('klines'):
                klines = data['data']['klines']
                k_map = {}
                for k in klines:
                    parts = k.split(',')
                    d_str = parts[0]
                    close_p = float(parts[2])
                    k_map[d_str] = close_p

                if '2026-07-30' in k_map:
                    p_0730 = k_map['2026-07-30']

                # 获取最新一天的收盘价
                sorted_dates = sorted(k_map.keys())
                if sorted_dates:
                    date_latest = sorted_dates[-1]
                    p_latest = k_map[date_latest]
    except Exception as e:
        print(f"Error fetching {code} {name}: {e}")

    pct_chg = None
    if p_0730 is not None and p_latest is not None and p_0730 > 0:
        pct_chg = round((p_latest - p_0730) / p_0730 * 100, 2)

    results.append({
        '代码': code,
        '公司名称': name,
        '细分板块': sector,
        '0730收盘价': p_0730,
        '最新收盘价': p_latest,
        '最新日期': date_latest,
        '涨跌幅(%)': pct_chg
    })

    if (len(results)) % 50 == 0:
        print(f"已处理 {len(results)}/{len(valid_df)} 个标的...")

res_df = pd.DataFrame(results)
res_df.to_csv('artifacts/ai_stocks_performance_0730_to_now.csv', index=False, encoding='utf-8-sig')
print("数据抓取与计算完成，保存在 artifacts/ai_stocks_performance_0730_to_now.csv")
