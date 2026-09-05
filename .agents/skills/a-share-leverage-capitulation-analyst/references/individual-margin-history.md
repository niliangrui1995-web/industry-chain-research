# DFCF 个股融资余额历史库

仅在用户明确要求逐只证券融资余额历史时读取。本模式沿用 [技能入口](../SKILL.md) 的厂商证据与受控产物边界；不随两融汇总日更自动运行。`artifacts/...` 与 `.agents/...` 路径相对项目根，命令从项目根运行。

## DFCF 个股融资余额历史库

用户明确要求逐只证券的融资余额历史时，使用东方财富数据中心 `RPTA_WEB_RZRQ_GGMX`，并与市场汇总日更表物理隔离：

- 首次抓取范围固定为 `2016-01-01` 至东方财富最新已发布日；后续默认回看 14 个日历日并断点续传。
- 原始接口同时包含 A 股股票和 ETF。数据库必须保留原始全量，通过 `a_share_stock_margin_daily` 视图排除交易市场代码为 `069001001`、`069001002` 的 ETF；不得把 ETF 记录计为个股样本。
- 每个交易日必须核对接口声明的 `count`、`pages` 与实际落库行数，并以 `(trade_date, secu_code)` 为唯一键。任一日期分页不完整、重复或融资余额为空时，`vendor_pagination_complete=false`。
- 若东方财富对交易日明确返回代码 `9201`“数据为空”，必须记录为 `vendor_no_data` 固定缺口，不得反复当作网络失败、插值或补造。此时可用日期的分页仍可完整，但 `calendar_coverage_complete=false`，并单列日期覆盖率和缺口日期。
- 分页完整只证明东方财富明细接口已被完整读取，不证明明细求和等于交易所或东方财富市场汇总。必须与 `dfcf_daily/dfcf_margin_balances.csv` 逐日对账；若不精确相等，明细库只能用于证券级历史，禁止汇总后替代市场两融因子。
- 个股库统一标记 `dfcf_vendor_individual_detail_unverified_by_exchange`，不得写成交易所官方逐股原始数据，也不得覆盖 `dfcf_daily` 或 `verified_*` 产物。

固定入口：`powershell -NoProfile -ExecutionPolicy Bypass -File ".agents\skills\a-share-leverage-capitulation-analyst\scripts\fetch_eastmoney_individual_margin_2016_present.ps1" -Python "C:\Python314\python.exe" -Workers 8`

固定产物：`artifacts/leverage_capitulation/individual_margin_2016_present/eastmoney_individual_margin.sqlite`、`latest_a_share_stock_margin.csv`、`individual_margin_audit.json`。
