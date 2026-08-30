# 09-00-2 自动化提示词

运行版本：`prompt_contract_version=2026-07-27.1`；`two_rong_refresh_protocol_version=2026-08-28.1`；`daily_market_data_publish_protocol_version=2026-08-30.1`。

本任务只在工作日北京时间 09:00 运行。先读取 `AGENTS.md`、`docs/automation/AUTOMATION_RUN_CONTRACT.md`、`docs/automation/LEVERAGE_INCREMENTAL_REFRESH_CONTRACT.md` 与 `docs/automation/DAILY_MARKET_DATA_PUBLISH_CONTRACT.md`，再严格按后者执行。它是唯一的三链路、AI 成分集合、白名单备份、Cloudflare Pages 发布与线上原始字节核验合同。

两融唯一业务入口为 `scripts/refresh_leverage_dashboard_incremental.py`；C5 与 AI 唯一业务入口为 `trading_concentration/refresh_tdx_trading_concentration_daily.py`。不得绕过这两个入口直接改写历史产物。

必须在业务读取前运行 `automation_run_metadata.py`，使用 `a-share-leverage-capitulation-analyst` 和 `ht-local-market-data`，并持久化全部版本字段。已有两融与 C5 历史保持只读基线；AI 工作簿成分集合变更时，只从 2025-01-01 起重算 `ai_chain_series`，绝不重算或改写 C5 历史 records/CSV。

两融、C5 与 AI 链路独立运行：一条链路无新增或来源待发不得阻止另一条通过验证的链路更新、备份和发布；任何硬完整性失败必须明确记录，且不得发布该失败链路的产物。最终必须使用中文报告三链路状态、AI 动作、提交、部署地址、线上 SHA-256 与失败原因。
