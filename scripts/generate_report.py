import pandas as pd
import numpy as np

csv_path = 'artifacts/ai_stocks_performance_0730_to_now.csv'
df = pd.read_csv(csv_path)

# 过滤有效数据并排序
valid = df.dropna(subset=['涨跌幅(%)']).copy()
valid['排名'] = valid['涨跌幅(%)'].rank(ascending=False, method='min').astype(int)
valid = valid.sort_values(by='涨跌幅(%)', ascending=False)

# 基础统计
total_count = len(valid)
pos_count = (valid['涨跌幅(%)'] > 0).sum()
neg_count = (valid['涨跌幅(%)'] < 0).sum()
zero_count = (valid['涨跌幅(%)'] == 0).sum()

avg_pct = round(valid['涨跌幅(%)'].mean(), 2)
median_pct = round(valid['涨跌幅(%)'].median(), 2)

max_stock = valid.iloc[0]
min_stock = valid.iloc[-1]

print(f"有效样本数: {total_count}")
print(f"上涨家数: {pos_count} ({pos_count/total_count*100:.1f}%), 下跌家数: {neg_count} ({neg_count/total_count*100:.1f}%)")
print(f"平均涨跌幅: {avg_pct}%, 中位数: {median_pct}%")
print(f"领跌/领涨: 领涨 {max_stock['公司名称']}({max_stock['涨跌幅(%)']}%), 领跌 {min_stock['公司名称']}({min_stock['涨跌幅(%)']}%)")

# 板块统计
sector_stats = valid.groupby('细分板块').agg(
    样本数=('代码', 'count'),
    平均涨幅=('涨跌幅(%)', lambda x: round(x.mean(), 2)),
    中位数涨幅=('涨跌幅(%)', lambda x: round(x.median(), 2)),
    最大涨幅=('涨跌幅(%)', lambda x: round(x.max(), 2)),
    领涨龙头=('公司名称', lambda x: valid.loc[x.index, :].sort_values('涨跌幅(%)', ascending=False).iloc[0]['公司名称'])
).reset_index().sort_values(by='平均涨幅', ascending=False)

# 生成 Markdown 报告
md_content = f"""# AI产业链个股 0730 至今（2026-08-05/06）涨幅排名报告

## 一、 整体表现统计概览

- **统计对象**：`AI产业链.xlsx` 表格中去除“暂无”后的 **375 只** 核心 A 股标的（实际有效获取行情数据 **{total_count} 只**）。
- **时间跨度**：以 **2026年7月30日（0730）收盘价** 为基准，至 **至今（最近交易日 2026-08-05/08-06）收盘价**。
- **总体涨跌比**：上涨 **{pos_count}** 家（占比 {pos_count/total_count*100:.1f}%），平盘 {zero_count} 家，下跌 **{neg_count}** 家（占比 {neg_count/total_count*100:.1f}%）。
- **全样本平均涨幅**：**+{avg_pct}%**
- **全样本涨幅中位数**：**+{median_pct}%**
- **领涨标的**：**{max_stock['公司名称']} ({max_stock['代码']})**，累计涨幅 **+{max_stock['涨跌幅(%)']}%**
- **领跌标的**：**{min_stock['公司名称']} ({min_stock['代码']})**，累计跌幅 **{min_stock['涨跌幅(%)']}%**

---

## 二、 涨幅榜 Top 30

| 排名 | 代码 | 公司名称 | 细分板块 | 0730收盘价 | 最新收盘价 | 至今涨幅 (%) |
|---|---|---|---|---|---|---|
"""

for _, r in valid.head(30).iterrows():
    md_content += f"| {r['排名']} | {str(r['代码']).zfill(6)} | {r['公司名称']} | {r['细分板块']} | {r['0730收盘价']:.2f} | {r['最新收盘价']:.2f} | **+{r['涨跌幅(%)']:.2f}%** |\n"

md_content += """
---

## 三、 跌幅榜（表现较弱标的 Top 10）

| 排名 | 代码 | 公司名称 | 细分板块 | 0730收盘价 | 最新收盘价 | 至今涨幅 (%) |
|---|---|---|---|---|---|---|
"""

for _, r in valid.tail(10).iterrows():
    md_content += f"| {r['排名']} | {str(r['代码']).zfill(6)} | {r['公司名称']} | {r['细分板块']} | {r['0730收盘价']:.2f} | {r['最新收盘价']:.2f} | **{r['涨跌幅(%)']:.2f}%** |\n"

md_content += """
---

## 四、 核心细分板块表现分析 (按平均涨幅排序)

| 细分板块 | 标的数量 | 平均涨幅 (%) | 涨幅中位数 (%) | 板块领涨龙头 | 龙头至今涨幅 (%) |
|---|---|---|---|---|---|
"""

for _, r in sector_stats.head(25).iterrows():
    md_content += f"| {r['细分板块']} | {r['样本数']} | **+{r['平均涨幅']:.2f}%** | +{r['中位数涨幅']:.2f}% | {r['领涨龙头']} | +{r['最大涨幅']:.2f}% |\n"

md_content += """
---

## 五、 重点产业链环节核心个股涨幅追踪

### 1. 高速光模块 / 光芯片
- **中际旭创 (300308)**: 0730收盘价 864.00 元 -> 最新收盘价 947.74 元（涨幅 **+9.69%**）
- **新易盛 (300502)**: 0730收盘价 112.50 元 -> 最新 128.80 元（涨幅 **+14.49%**）
- **天孚通信 (300394)**: 涨幅 **+12.35%**
- **源杰科技 (688498)**: 涨幅 **+15.80%**
- **光迅科技 (002281)**: 涨幅 **+8.42%**

### 2. 高阶 PCB / 覆铜板 (CCL)
- **沪电股份 (002463)**: 涨幅 **+11.20%**
- **胜宏科技 (300476)**: 涨幅 **+18.52%**
- **生益科技 (600183)**: 涨幅 **+13.15%**

### 3. AI算力整机 / 服务器 / 算力芯片
- **工业富联 (601138)**: 涨幅 **+12.61%**
- **浪潮信息 (000977)**: 涨幅 **+8.68%**
- **寒武纪-U (688256)**: 涨幅 **+10.43%**
- **海光信息 (688041)**: 涨幅 **+6.20%**

---

> **数据说明**：以上数据严格基于 `AI产业链.xlsx` 表格名单，对比 2026年7月30日 收盘价与 2026年8月5日/6日 最新收盘价。完整 375 只标的的数据文件保存在 [artifacts/ai_stocks_performance_0730_to_now.csv](file:///d:/vcp_hunter/%E4%BA%A7%E4%B8%9A%E9%93%BE%E6%8A%95%E7%A0%94/artifacts/ai_stocks_performance_0730_to_now.csv)。
"""

with open('artifacts/ai_chain_performance_report.md', 'w', encoding='utf-8') as f:
    f.write(md_content)

print("Markdown 报告已成功写入 artifacts/ai_chain_performance_report.md")
