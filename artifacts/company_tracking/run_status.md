# Company Tracking Run Status

metadata:
- run_date: 2026-05-13
- run_time_beijing: 2026-05-13 20:03:58 +08:00
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

本轮新增或更新的公司级硬事件集中在 3 家：云南锗业新增官方异常波动公告；宏和科技新增官方董高减持结果公告并关闭上一轮媒体线索来源缺口；中际旭创新增 2026-05-13 三笔小规模大宗交易。源杰科技上轮公告镜像已补到上交所官方源，但没有新增经营硬披露。其余公司未发现新增公告、龙虎榜或大宗交易硬事件。

## Files Updated

- `artifacts/company_tracking/2026-05-13.md`
- `artifacts/company_tracking/run_status.md`
- `watchlists/a_share_company_watchlist.xlsx`
- `artifacts/company_tracking/002428.SZ/events.jsonl`
- `artifacts/company_tracking/002428.SZ/state.md`
- `artifacts/company_tracking/002222.SZ/state.md`
- `artifacts/company_tracking/300476.SZ/state.md`
- `artifacts/company_tracking/603256.SH/events.jsonl`
- `artifacts/company_tracking/603256.SH/state.md`
- `artifacts/company_tracking/601869.SH/state.md`
- `artifacts/company_tracking/301511.SZ/state.md`
- `artifacts/company_tracking/002384.SZ/state.md`
- `artifacts/company_tracking/300308.SZ/events.jsonl`
- `artifacts/company_tracking/300308.SZ/state.md`
- `artifacts/company_tracking/688498.SH/state.md`
- `C:\Users\Administrator\.codex\automations\a-grok\memory.md`

No Git backup was run, per user instruction.

## Per-company completion table

| ticker | name | batch_no | queue_status | browser_scope | announcements_checked | lhb_checked | block_trade_checked | grok_status | open_web_fallback_status | state_change | miss_risk_notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed | fallback_no_browser | done_added_1_official_announcement | done_no_2026-05-13_record | done_no_2026-05-13_record | unavailable_chrome_plugin_not_exposed | searched_one_official_risk_announcement_added | updated | 业绩说明会后正式问答/IR记录尚未找到；Grok/X缺口保留 |
| 002222.SZ | 福晶科技 | 1 | completed | fallback_no_browser | done_no_new | done_empty | done_empty | unavailable_chrome_plugin_not_exposed | searched_no_new_hard_signal | updated_state_only | SZSE API 50x；已用 CNINFO、东方财富、公司官网 IR、open-web 补位 |
| 300476.SZ | 胜宏科技 | 1 | completed | fallback_no_browser | checked_no_new_official_announcement_2026-05-13 | checked_empty_2026-05-11_to_2026-05-13 | checked_no_new_after_existing_2026-05-11 | unavailable_chrome_plugin_not_exposed | searched_no_new_hard_event | updated_state_only | CNINFO 05-08 至 05-13 未返回公告，东方财富公告仅复现已入账 05-08 IR |
| 603256.SH | 宏和科技 | 1 | completed | fallback_no_browser | done_added_official_pdf | done_no_new | done_no_new | unavailable_chrome_plugin_not_exposed | searched_official_gap_closed | updated | 上轮媒体减持线索已补官方 PDF；未发现新增龙虎榜/大宗交易 |
| 601869.SH | 长飞光纤 | 1 | completed | fallback_no_browser | yes | yes | yes | unavailable_chrome_plugin_not_exposed | searched_no_new_hard_event | updated_no_event | 公司官网 IR 命令行直连失败；HKEX 未结构化抓取；无 Chrome/Grok 登录态发现层 |
| 301511.SZ | 德福科技 | 1 | completed | fallback_no_browser | yes | yes | yes | unavailable_chrome_plugin_not_exposed | searched_no_new_hard_signal | updated_state_only | 普通网页不能覆盖 X/Grok 登录态，HVLP/RTF 收入量化仍缺口 |
| 002384.SZ | 东山精密 | 2 | completed | fallback_no_browser | yes_existing_sponsor_report_only | yes_latest_still_2026-05-07 | yes_latest_still_2026-03-10 | unavailable_chrome_plugin_not_exposed | searched_observation_pool_only | updated_source_gap_no_new_hard_event | open-web 有索尔思/Meta/800G/AI PCB 强叙事，但未见公告、IR、客户或订单硬证据 |
| 300308.SZ | 中际旭创 | 2 | completed_with_grok_unavailable | fallback_no_browser | done_cninfo_0_ir_no_new | done_no_lhb | done_added_3_block_trades | unavailable_chrome_plugin_not_exposed | searched_block_trade_signal_only | updated_state_and_appended_1_event | CNINFO 504 未复现；经营硬披露仍缺 1.6T/800G/硅光/物料/毛利率拆分 |
| 688498.SH | 源杰科技 | 2 | completed | fallback_no_browser | done_official_source_resolved | done_empty | done_empty | unavailable_chrome_plugin_not_exposed | searched_official_source_resolved_no_new_operating_signal | updated | 上轮公告镜像已补到上交所官方源；CNINFO 同窗口仍为 0；无新增经营硬披露 |

## Material Changes

- 云南锗业：新增官方异常波动公告，确认 2026-05-08、2026-05-11、2026-05-12 三日涨幅偏离累计超过 20%，并提示极高 PE/PB、化合物半导体材料收入占比 12.93%、毛利占比 14.29%、不存在应披露未披露重大事项。该公告强化交易拥挤和风险提示，不验证 InP/GaAs 基本面兑现。
- 宏和科技：新增官方董高减持结果公告，确认毛嘉明和邹新娥减持计划实施完毕，关闭上一轮媒体观察的官方源缺口。减持比例小，但在高涨幅阶段继续强化交易风险观察。
- 中际旭创：新增 2026-05-13 三笔大宗交易，合计 1122.65 万元，买卖双方均为机构专用。该事件属于交易数据，不是 800G/1.6T、硅光或毛利率经营硬披露。
- 源杰科技：上轮公告镜像已补到上交所官方 PDF，但本轮无新增经营类硬事件。

## Trading-event highlights

- 中际旭创：新增三笔小规模大宗交易。
- 云南锗业：5 月 13 日无新增龙虎榜或大宗交易；最近交易硬事件仍为 5 月 12 日龙虎榜和两笔折价大宗交易。
- 其余公司：本轮窗口无新增龙虎榜或大宗交易硬记录。

## Validation

- Enabled watchlist count: 9.
- Completion table count: 9.
- Missing enabled companies: none.
- JSONL validation: all company `events.jsonl` files parse successfully.
- Batch validation: batch 1 had 6 companies; batch 2 had 3 companies; all completed.
- Watchlist validation: enabled rows `last_update_date` set to 2026-05-13; `baseline_status` and `last_baseline_date` unchanged.
- Git backup: not run, per user instruction.

## Notes

Next high-value checks are 云南锗业 2026-05-13 业绩说明会问答、源杰科技 2026-05-20 业绩说明会、宏和科技减持后的电子布经营数据验证、中际旭创 H 股招股书/Q2 经营口径、东山精密索尔思硬证据和德福科技 HVLP/RTF 收入量化。
