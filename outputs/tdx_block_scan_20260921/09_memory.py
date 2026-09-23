# -*- coding: utf-8 -*-
"""追加工作日志 + 更新项目长期记忆（本地 vipdoc 取数契约）。"""
import os, io

DAILY = r'D:/vcp_hunter/产业链投研/.workbuddy/memory/2026-09-21.md'
MEM = r'D:/vcp_hunter/产业链投研/.workbuddy/memory/MEMORY.md'

log = """

## 通达信板块扫描：关注个股(GZGG) + AI硬件(AIYJ) 126 只技术面（2026-09-21）

**任务**：定位 D:\\HT 板块文件 → 解析成分股 → 126 只纯技术面分析 → 每板块筛出下周重点观察名单。

**产出**
- `deliverables/technical-analyst/2026-09-21/关注个股与AI硬件-技术面扫描报告.md`（含 126 只完整清单表）
- `deliverables/technical-analyst/2026-09-21/关注个股与AI硬件-板块技术面扫描.html`（render.py 套壳，245KB，9 个 data-nav section）
- 中间产物：`outputs/tdx_block_scan_20260921/`（01 解析板块 → 08 生成报告，共 9 个脚本）

**关键结论（技术面）**
- 关注个股（42 只，医药CXO为主）：日线+周线双多头为主，趋势延续中段；但 7 只贴 60 日区间顶点（南华生物100%、普洛药业99.3%），追高代价大。
- AI硬件（84 只）：过半周线 MACD 仍在零下收敛、日线已转多 ⇒ **周线级别调整中的日线反弹**，非反转；34 只已到压力位 3% 内的临界区。
- 大盘：五大指数全线站上 MA20，深成/创业板/科创50/中证1000 日线 MACD 柱翻正，科创50 近5日 +8.45% 领涨。

**方法论沉淀（可复用）**
1. 批量扫描**不要用 neodata 抓日线**——本地 vipdoc 更快更全（见 MEMORY.md 新增契约）。
2. 本周只有 1 个交易日时，**周线最后一根 K 线不完整，周线量能指标必须弃用**（周量比会假性显示为 0.2~0.4）。
3. 筛选坚持"不打分"：按趋势/动量/位置/量价四类定性条件共振分层（核心/次级/备选），代价单列。
"""

new_mem_section = """
## 通达信本地 vipdoc 日线 = 批量技术面扫描首选源（2026-09-21 实证）

**结论优先级：本地 vipdoc > neodata 接口。** 已用 126 只实测对比：本地数据 126/126 读取成功、最后交易日全部对齐当日、
按交易日历校验最近 130 日仅 5 只缺数且全为真实停牌/次新；而 neodata 缓存此前 144 只各系统性缺 12 天（见上文"neodata 日线缓存严重缺陷"）。
**交叉验证**：本地算出的 SH603228 MACD（DIF 5.1953 / DEA 5.283 / 柱 −0.177，柱＝(DIF−DEA)×2）与完整序列基准一致；
SH688131 收盘价 102.18 与 tdx_quotes 实时接口完全一致。

- **路径**：`D:\\HT\\vipdoc\\{sh|sz|bj}\\lday\\{mkt}{code}.day`（sh 6034 / sz 5875 / bj 361 个文件，含指数）。
- **格式**：每根 32 字节定长，`struct.unpack('<IIIIIfII')` → 日期(YYYYMMDD int) / 开 / 高 / 低 / 收（均为 **价格×100 的 int**）/ 成交额(float 元) / 成交量(uint32 股) / 保留。
  校验式：`len(raw) % 32 == 0`。
- **不复权** ⇒ 必须自己做除权检测：按各板块涨跌幅上限设阈值（主板 10.5%、科创/创业 20.5%、北交所 30.5%），
  从后往前扫描 `|今收/昨收−1| > 阈值` 即判除权，累积因子对历史价格做前复权（本次 126 只命中 16 只，含 688256 −36.7%、688498 −32.1% 等高送转）。
- **blocknew.cfg 结构**：**88 字节定长记录** = 板块名(GBK，`\\x00` 填充) + 文件名(ASCII，如 `GZGG.blk`)；
  已确认映射：关注个股=GZGG.blk(42只)、AI硬件=AIYJ.blk(84只)。名称带 `XD` 前缀表示当日除息（如 XD皓元医=皓元医药 688131、XD柏诚股=柏诚股份 601133）。
- **本机 bash 无 coreutils**（head/wc/dirname 全缺失）⇒ 目录探查一律用 Python `os.listdir`；PowerShell stdout 常被吞，产出后用 Python 读文件确认。
"""

with io.open(DAILY, 'a', encoding='utf-8') as f:
    f.write(log)

s = io.open(MEM, encoding='utf-8').read()
anchor = '## 评分框架口径'
assert s.count(anchor) == 1, s.count(anchor)
s2 = s.replace(anchor, new_mem_section.strip() + '\n\n' + anchor)
with io.open(MEM, 'w', encoding='utf-8') as f:
    f.write(s2)

# 回读校验
s3 = io.open(MEM, encoding='utf-8').read()
assert 'vipdoc 日线 = 批量技术面扫描首选源' in s3, 'MEMORY 未落盘'
assert s3.count('\ufffd') == 0
d3 = io.open(DAILY, encoding='utf-8').read()
assert '通达信板块扫描' in d3, 'DAILY 未落盘'
print('memory updated. MEMORY.md size:', len(s3), '| daily size:', len(d3))
