import pandas as pd
import json

csv_file = 'artifacts/ai_stocks_performance_0730_to_now.csv'

try:
    df = pd.read_csv(csv_file)
    print(f"成功读取数据，共 {len(df)} 行记录")

    # 过滤有有效涨跌幅的股票
    valid = df.dropna(subset=['涨跌幅(%)']).copy()
    valid = valid.sort_values(by='涨跌幅(%)', ascending=False)

    print("\n=== AI产业链 0730 至今 涨幅 Top 20 ===")
    top20 = valid.head(20)[['代码', '公司名称', '细分板块', '0730收盘价', '最新收盘价', '涨跌幅(%)']]
    print(top20.to_string(index=False))

    print("\n=== AI产业链 0730 至今 跌幅 Top 10 ===")
    bottom10 = valid.tail(10)[['代码', '公司名称', '细分板块', '0730收盘价', '最新收盘价', '涨跌幅(%)']]
    print(bottom10.to_string(index=False))

    print("\n=== 按细分板块统计平均涨跌幅 ===")
    sector_summary = valid.groupby('细分板块')['涨跌幅(%)'].agg(['count', 'mean', 'median', 'max', 'min']).reset_index()
    sector_summary = sector_summary.sort_values(by='mean', ascending=False)
    sector_summary.columns = ['细分板块', '样本数', '平均涨幅(%)', '中位数(%)', '最大涨幅(%)', '最大跌幅(%)']
    print(sector_summary.to_string(index=False))

except Exception as e:
    print(f"读取或处理数据时出错: {e}")
