---
name: a-share-leverage-capitulation-analyst
description: 更新 DFCF 沪深两融余额，分析三因子去杠杆压力或抱团顶部风险。适用于两融日更、压力信号、逐股融资历史和相关回测；按请求选择模式，不自动刷新历史研究。
---

# A 股两融去杠杆压力分析

用于每日更新东方财富（DFCF）两融余额表，并分析市场急跌时的两融余额收缩与普跌共振。该模型识别的是**去杠杆压力代理信号**，不能仅凭融资余额下降证明被动强平、爆仓、市场底或未来反弹。

## 模式与路径

先按本次请求选择模式，只读取对应参考；日更不会自动触发逐股库抓取、抱团重算或正式回测。

| 请求 | 使用范围 |
|---|---|
| 沪深两融日更、当日 DFCF 三因子压力 | 按本入口执行；若只问已有数据或方法，不运行更新脚本。 |
| 明确要求逐只证券融资余额历史 | 读取 [逐股历史库](references/individual-margin-history.md)。 |
| 抱团、融资集中、顶部研究或当前顶部风险 | 读取 [抱团研究](references/crowding-margin-top-risk.md)，先区分历史解释、当前状态和研究更新。 |
| 历史信号/回测、市场收益中位数、平均股价指数或盘中最大跌幅 | 读取 [回测与严重度审计](references/backtest-and-severity-audit.md) 中对应章节；仅问历史结论时按该页链接读取日期快照。 |

`artifacts/...` 与 `.agents/...` 路径相对项目根；本入口中的 `scripts/...` 指本技能目录。命令统一从项目根运行；Markdown 相对链接按所在文档定位。

## 用户应用总结

如果在上升趋势中出现信号，短期继续上涨的可能性比较高；如果处于下跌趋势或大熊市，往往会出现两次以上信号。应用该信号时，必须同时判断当前市场趋势和市场环境，不能把任意一次信号机械地当作底部或买点。

这是一条应用层经验总结，不是当前三因子回测已经验证的第四个因子。若进一步量化“上升趋势”“下跌趋势”或“熊市环境”，趋势分类只能使用信号可得时及以前的数据，并单独报告不同市场环境下的样本；不得根据后续走势事后划分牛熊市，也不得改变原三因子的正式信号日期。

## 数据硬门槛

1. 先确认行情和两融数据的截止日期，不得补写尚未公布的数据。
2. 日更任务只使用东方财富数据中心 `RPTA_WEB_RZRQ_LSSH`，沪市代码 `007`、深市代码 `001`；禁止请求上交所、深交所网站或 API。DFCF 属于行情厂商数据，必须保留来源、抓取时间和哈希，不得写成交易所官方原始数据。
3. 指数对比使用深证综指 `399106`、创业板指 `399006`、创业板综指 `399102`；三者必须分别读取和标注，不得混用序列或名称。
4. 市场宽度可使用只读的本地 TDX 日线，但必须披露当前证券池带来的幸存者偏差及停牌样本处理。
5. 必须先确认 DFCF 沪、深最新日期一致，再计算两市合计；任一市场缺失或日期不同则合计和信号输出 `N/A`，不得估算或沿用旧值。
6. DFCF 日更结果统一标记 `dfcf_vendor_only_unverified_by_exchange`。数据不完整或样本过小时写 `N/A` 或“证据不足”，不得给确定性胜率。

## DFCF 日更唯一输入

- 项目根目录旧文件 `ashare_daily_margin_history.csv` 已删除并永久停用，不得恢复、读取或作为失败回退。
- 每日日更只运行 `scripts/update_dfcf_margin_daily.py`。该入口只能访问 DFCF，不得调用 `fetch_official_margin_2016_present.ps1`、`fetch_eastmoney_margin_2016_present.ps1`、`audit_margin_history.py` 或 `run_verified_leverage_backtest.ps1`。
- 日更表固定写入 `artifacts/leverage_capitulation/dfcf_daily/dfcf_margin_balances.csv`，原始分市场快照写入同目录 `dfcf_sse_margin.csv` 和 `dfcf_szse_margin.csv`，审计写入 `dfcf_margin_audit.json`。
- 日更表必须按日期升序、去重，包含沪市、深市、两市融资余额及各自日变动金额和比例；只输出沪深共同日期。求差须先保留沪深日期并集中的单边缺失日；前一并集日期任一市场缺失时，该市场及两市合计的当日日变动置为 `N/A`，并标记 `change_status=previous_session_incomplete`；另一市场保留有完整相邻观测的日变动，不得跨缺口累计。周末和长假不按日历天数判为缺失。无新共同日期时不得重复旧报告。
- 不得用 DFCF 日更覆盖或改写 `verified_margin_balances.csv`、`margin_audit.json`、`official_sse_margin.csv`、`official_szse_margin.csv` 或任何既有正式回测产物。
- 既有 `verified_*` 产物仅作为冻结的历史受控结果；除非用户另行明确要求恢复官方审计流程，否则本技能不得刷新它们。

## 因子定义

默认参数仅是待验证基准，不是“黄金模型”。滚动排名只能使用当日及之前的数据；窗口必须覆盖完整的 3 个日历年并至少有 600 个有效观测。

T 日完整信号须等待 DFCF 沪深同日融资数据均发布，并记录实际 `signal_available_date`，不能机械写成 T 日收盘可得。最早执行时点为 T+1；若数据更晚发布，则按实际可得时点延后。

三因子及长假噪声控制如下：

1. **指数跌幅极值**：深证综指、创业板指和创业板综指的单日收益率，分别计算截至当日的滚动 3 个日历年最差排名，基准阈值为前 15 名。
2. **融资流出比例（DFCF 厂商口径）**：`-(当日两市融资余额 - 前一交易日两市融资余额) / 前一交易日两市融资余额`，计算截至当日的滚动 3 个日历年最大排名，基准阈值为前 15 名。绝对流出金额只作描述，不替代比例因子；结果必须标记为 DFCF 厂商口径，不能称交易所正式信号。
3. **普跌宽度**：当日收跌股票数 / 当日有可比收盘价股票数，基准阈值为 `>= 80%`。
4. **长假噪声控制**：若信号日到下一交易日间隔至少 5 个日历日，则排除该日。此规则只能降低长假前主动还款噪声，不能识别“主动还款”与“被动强平”。

比较时分别将三个指数的跌幅排名与同一融资流出比例、同一普跌宽度组合；每组信号都必须是这三个因子同时满足，不能额外加入另一指数条件后冒充三因子结果。每个满足条件的交易日都计入对应指数的信号样本，并使用相同持有期统计检查指数选择带来的差异。

## 确定性流程

每日从项目根运行专用 DFCF 日更入口：`python .agents/skills/a-share-leverage-capitulation-analyst/scripts/update_dfcf_margin_daily.py --project-root "D:\vcp_hunter\产业链投研"`

脚本执行以下固定流程：

- 仅请求 DFCF 数据中心接口；审计字段必须保持 `dfcf_only=true`、`exchange_requests=0`。
- 首次运行从 2016-01-01 建表；后续默认回看14个日历日，合并可能的修订值并去重。
- 只有沪深共同日期进入合并表；日期不一致时记录 `sh_only_dates` / `sz_only_dates`，不得计算缺失日合计。
- 求差时间轴复用现有刷新流程的只读日历哨兵 `D:\HT\vipdoc\sh\lday\sh000001.day`（可用 `--trading-calendar-file` 指定同类已核验文件），加入沪深日期并集以发现覆盖内双边同时缺失；它只提供日期，两融余额仍仅来自 DFCF，不增加网络数据源。审计保留日历哈希、起止日、覆盖状态及 `incomplete_previous_session_dates`。日历缺失时明确退回 `change_calendar_basis=observed_sh_sz_date_union`；本地日历覆盖外的双边缺失无法识别，不得声称已核验完整交易所日历。无效日历或 reparse point 阻断运行。
- 使用临时文件和原子替换更新 CSV/JSON；不改变项目代码、watchlist、账户和交易状态。
- 检查 `dfcf_margin_audit.json` 中原始快照及合并表 SHA-256；若哈希、重复、空值或正数检查失败，阻断分析。
- 若 `new_common_dates=0`，简要报告 DFCF 暂无新共同日期并结束，不重复旧报告。

合并表字段至少包括：`date`；`sh_margin_y`、`sz_margin_y`、`total_margin_y`；`sh_change_y`、`sh_change_pct`；`sz_change_y`、`sz_change_pct`；`total_change_y`、`total_change_pct`；`change_status`、`source`、`sample_status`。首个观测没有可比前值时标记 `no_previous_observation`，有效日变动标记 `complete`。

## 受控历史产物保护

`artifacts/leverage_capitulation/verified_2016_present/` 下的融资审计、因子面板、信号明细、敏感性分析和工作簿均为冻结的受控历史产物。DFCF 日更不得覆盖、追加或重算这些文件，也不得把厂商口径日更结果包装为既有正式回测的延伸。

抱团与顶部风险研究只能写入 `crowding_margin_top_risk_2016_present/` 独立目录；其 DFCF 厂商数据结论不得升级为交易所官方数据，也不得覆盖、追加或解释为 `verified_2016_present/` 的正式三因子结果。
