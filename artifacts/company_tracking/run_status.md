# Company Tracking Run Status

metadata:
- run_date: 2026-05-12
- run_time_beijing: 2026-05-12 20:25:29 +08:00
- run_type: multi_agent_daily_update
- status: completed_with_grok_unavailable_open_web_fallback
- company_count: 9
- baseline_created_count: 0
- daily_updated_count: 9
- watchlist_updated: true
- multi_agent_status: completed
- multi_agent_workers_successful: 9
- multi_agent_worker_errors: 0
- logical_batches: 2
- chrome_grok_status: unavailable_chrome_plugin_not_exposed
- chrome_probe_detail: "Chrome plugin/tool surface was not exposed in this automation turn; no Browser Use or Playwright fallback was used as a substitute for logged-in Chrome/Grok"
- open_web_fallback_status: completed_observation_only

## Summary

9 家 enabled 公司均已完成公司级 worker 跟踪研究。逻辑并行上限为 6；第一批 6 家启动后，已完成 worker 关闭释放槽位，再补入第二批 3 家。没有 enabled 公司遗漏，没有 company worker 失败。

Chrome/Grok 登录态浏览器工具未暴露，全部公司按规则使用普通 open-web fallback。普通网页搜索、媒体转载、行情页和公告镜像均未被标记为 Grok/X 或 Chrome 登录态结果。

本轮新增或更新的公司级事件集中在 4 家：云南锗业新增 2026-05-12 龙虎榜和两笔大宗交易；源杰科技新增权益分派、业绩说明会和股票交易风险提示公告镜像；宏和科技新增董高减持计划实施完毕的媒体观察，待官方 PDF 复核；福晶科技新增“目前未生产磷化铟光芯片”的二级转载互动观察。其余 5 家未发现新增公告、龙虎榜或大宗交易硬事件。

## Files Updated

- `artifacts/company_tracking/2026-05-12.md`
- `artifacts/company_tracking/run_status.md`
- `watchlists/a_share_company_watchlist.xlsx`
- `artifacts/company_tracking/002428.SZ/events.jsonl`
- `artifacts/company_tracking/002428.SZ/state.md`
- `artifacts/company_tracking/002222.SZ/events.jsonl`
- `artifacts/company_tracking/002222.SZ/state.md`
- `artifacts/company_tracking/603256.SH/events.jsonl`
- `artifacts/company_tracking/603256.SH/state.md`
- `artifacts/company_tracking/688498.SH/events.jsonl`
- `artifacts/company_tracking/688498.SH/state.md`
- `C:\Users\Administrator\.codex\automations\a-grok\memory.md`

No Git backup was run, per user instruction.

## Per-company completion table

| ticker | name | batch_no | queue_status | browser_scope | announcements_checked | lhb_checked | block_trade_checked | grok_status | open_web_fallback_status | state_change | miss_risk_notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed | fallback_no_browser | checked_no_new | new_record_found | new_record_found | unavailable_chrome_plugin_not_exposed | searched_trading_events_found_no_new_fundamental_signal | updated | 交易事件不等于 InP/GaAs 基本面兑现；等待 2026-05-13 业绩说明会 |
| 002222.SZ | 福晶科技 | 1 | completed | fallback_no_browser | checked_no_new | checked_no_new | checked_no_new | unavailable_chrome_plugin_not_exposed | searched_secondary_ir_repost_found | updated | 互动易原文未直接打开；二级转载只作观察 |
| 300476.SZ | 胜宏科技 | 1 | completed_no_new_hard_event | fallback_no_browser | checked_no_new | checked_empty | checked_empty | unavailable_chrome_plugin_not_exposed | searched_no_new_hard_event | none | 2026-05-11 小额大宗交易已入账，本轮不重复 |
| 603256.SH | 宏和科技 | 1 | completed_with_state_update | fallback_no_browser | checked_partial | checked_no_new | checked_no_new | unavailable_chrome_plugin_not_exposed | searched_with_pending_official_item | updated | 减持完成来自媒体，需下轮官方 PDF 复核 |
| 601869.SH | 长飞光纤 | 1 | completed | fallback_no_browser | checked_no_new | checked_no_new | checked_no_new | unavailable_chrome_plugin_not_exposed | searched_no_new_verified_event | none | 中文官网部分页面访问不稳，已用英文 IR/CNINFO/东方财富补位 |
| 301511.SZ | 德福科技 | 1 | completed_no_new_hard_event | fallback_no_browser | checked_no_new | checked_no_new | checked_no_new | unavailable_chrome_plugin_not_exposed | searched_one_low_novelty_ir_observation_no_new_hard_signal | none | HVLP5/RTF 仍缺客户、订单、收入和毛利率量化 |
| 002384.SZ | 东山精密 | 2 | completed | fallback_no_browser | checked_no_new | checked_no_new | checked_no_new | unavailable_chrome_plugin_not_exposed | searched_observation_pool_only | none | 索尔思强叙事未获公司公告、CNINFO、深交所或 IR 确认 |
| 300308.SZ | 中际旭创 | 2 | completed | fallback_no_browser | checked_no_new | checked_no_record | checked_no_record | unavailable_chrome_plugin_not_exposed | searched_no_new_confirmed_signal | none | CNINFO 查询 504，需下轮复扫；股价强势未对应新增硬事件 |
| 688498.SH | 源杰科技 | 2 | completed_with_grok_unavailable_open_web_fallback | fallback_no_browser | new_announcement_mirror_found | checked_no_record | checked_no_record | unavailable_chrome_plugin_not_exposed | searched_with_official_announcement_signal | updated | 上交所查询超时、CNINFO 为空；公告镜像需下轮补官方源 |

## Material Changes

- 云南锗业：新增 2026-05-12 龙虎榜和两笔折价大宗交易。性质是交易硬事件，确认交易弹性与拥挤度升高，不确认 InP/GaAs 基本面兑现。
- 源杰科技：新增权益分派、业绩说明会和股票交易风险提示公告镜像。权益分派影响股本和估值口径，风险提示强化短线涨幅和高 PE 风险，业绩说明会提供后续追问窗口。
- 宏和科技：媒体称董高减持计划已实施完毕。该事件比例小但在高涨幅阶段有交易情绪意义；官方 PDF 待下轮复核。
- 福晶科技：二级转载称公司目前未生产磷化铟光芯片。该线索约束概念外推，但不是官方公告或经营硬事件。

## Trading-event highlights

- 云南锗业：新增龙虎榜和两笔大宗交易。
- 胜宏科技：2026-05-12 无新增龙虎榜或大宗交易，2026-05-11 小额大宗交易不重复入账。
- 其余公司：本轮窗口无新增龙虎榜或大宗交易硬记录。

## Validation

- Enabled watchlist count: 9.
- Completion table count: 9.
- Missing enabled companies: none.
- JSONL validation: all company `events.jsonl` files parse successfully.
- Batch validation: batch 1 had 6 companies; batch 2 had 3 companies; all completed.
- Watchlist validation: enabled rows `last_update_date` set to 2026-05-12; `baseline_status` and `last_baseline_date` unchanged.
- Git backup: not run, per user instruction.

## Notes

Next high-value checks are 云南锗业 2026-05-13 业绩说明会、源杰科技 2026-05-20 业绩说明会和权益分派后的估值口径、宏和科技减持完成官方 PDF、福晶科技互动易原文、东山精密索尔思叙事与中际旭创强势股价是否获得官方硬证据。
