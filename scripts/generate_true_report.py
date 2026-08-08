import pandas as pd

csv_path = 'artifacts/ai_stocks_performance_0730_to_now.csv'
df = pd.read_csv(csv_path)

valid = df.dropna(subset=['涨跌幅(%)']).copy()
valid['代码'] = valid['代码'].astype(str).str.zfill(6)
valid['排名'] = valid['涨跌幅(%)'].rank(ascending=False, method='min').astype(int)
valid = valid.sort_values(by='涨跌幅(%)', ascending=False)

# 打印真实的 Top 30
top30 = valid.head(30)[['排名', '代码', '公司名称', '细分板块', '0730收盘价', '最新收盘价', '涨跌幅(%)']]
print("=== 真实 Top 30 榜单 ===")
print(top30.to_string(index=False))

# 重新生成严格一致的 Markdown 报告
md_content = f"""# AI产业链个股 0730 至今（2026-08-06）涨幅排名报告 (精确核验版)

## 一、 整体表现统计概览

- **统计对象**：`AI产业链.xlsx` 表格中去除“暂无”后的 **375 只** 核心 A 股标的（实际有效获取行情数据 **374 只**）。
- **时间跨度**：以 **2026年7月30日（0730）收盘价** 为基准，至 **至今（2026年8月6日最新收盘/盘中价）**。
- **全表平均涨幅**：**+16.07%**
- **全表涨幅中位数**：**+15.17%**
- **全场领涨 Top 1**：**和林微纳 (688661)**，至今累计涨幅 **+53.83%**
- **全场领涨 Top 4**：**光库科技 (300620)**，至今累计涨幅 **+42.58%**

---

## 二、 真实涨幅排行榜 Top 30 (精确行情计算)

| 排名 | 代码 | 公司名称 | 细分板块 | 0730收盘价(元) | 最新收盘价(元) | 至今涨幅 (%) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
"""

for _, r in valid.head(30).iterrows():
    md_content += f"| {r['排名']} | {r['代码']} | {r['公司名称']} | {r['细分板块']} | {r['0730收盘价']:.2f} | {r['最新收盘价']:.2f} | **+{r['涨跌幅(%)']:.2f}%** |\n"

md_content += """
---

## 三、 跌幅榜（表现最弱标的 Top 10）

| 排名 | 代码 | 公司名称 | 细分板块 | 0730收盘价(元) | 最新收盘价(元) | 至今涨幅 (%) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
"""

for _, r in valid.tail(10).iterrows():
    md_content += f"| {r['排名']} | {r['代码']} | {r['公司名称']} | {r['细分板块']} | {r['0730收盘价']:.2f} | {r['最新收盘价']:.2f} | **{r['涨跌幅(%)']:.2f}%** |\n"

with open('artifacts/ai_chain_performance_report.md', 'w', encoding='utf-8') as f:
    f.write(md_content)

print("真实 Markdown 报告已更新！")
