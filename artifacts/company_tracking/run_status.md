# Company Tracking Run Status

metadata:
- run_date: 2026-05-14
- run_time_beijing: 2026-05-14 20:14:47 +08:00
- run_type: multi_agent_daily_update_with_baseline_plus_manual_company_add
- status: completed_with_grok_unavailable_open_web_fallback
- company_count: 11
- baseline_created_count: 2
- daily_updated_count: 11
- watchlist_updated: true
- multi_agent_status: completed_for_original_daily_batch; manual_followup_completed_for_300394.SZ
- multi_agent_workers_successful: 10
- multi_agent_worker_errors: 0
- logical_batches: 2 + manual_followup
- manual_company_followup_count: 1
- chrome_grok_status: unavailable_chrome_plugin_not_exposed
- chrome_probe_detail: "Chrome/@chrome plugin tool surface was not exposed in this automation turn; no Browser Use or Playwright fallback was used as a substitute for logged-in Chrome/Grok"
- open_web_fallback_status: completed_observation_only

## Summary

原日更 10 家 enabled 公司均已完成公司级 worker 跟踪研究。逻辑并行上限为 6；第一批 6 家完成后释放槽位，第二批 4 家全部启动并完成。随后按用户新增关注请求，手工追加天孚通信（300394.SZ）并完成首次基线、状态和事件账本。当前 enabled 公司 11 家均已在 completion table 中有记录。

Chrome/Grok 登录态浏览器工具未暴露，全部公司按规则使用普通 open-web fallback。普通网页搜索、媒体转载、行情页和公告镜像均未被标记为 Grok/X 或 Chrome 登录态结果。

本轮新增或更新的公司级事项集中在四类：天孚通信按用户请求新增为关注公司并完成首次基线，最近硬事件为 2026-05-14 IR 披露 CPO 配套 FAU/ELS 已实现稳定交付且个别物料仍阶段性缺货；鼎通科技作为新增待建基线公司完成完整基线，最近硬事件为 2026-05-09 可转债申请获上交所上市审核委审核通过、仍待证监会注册；中际旭创新增 2026-05-14 一笔小额大宗交易；云南锗业新增业绩说明会 open-web fallback 会后观察，但未形成客户、订单、良率或量产硬证据。

## Files Updated

- `artifacts/company_tracking/2026-05-14.md`
- `artifacts/company_tracking/run_status.md`
- `watchlists/a_share_company_watchlist.xlsx`
- `artifacts/company_tracking/002428.SZ/events.jsonl`
- `artifacts/company_tracking/002428.SZ/state.md`
- `artifacts/company_tracking/300476.SZ/state.md`
- `artifacts/company_tracking/300308.SZ/events.jsonl`
- `artifacts/company_tracking/300308.SZ/state.md`
- `artifacts/company_tracking/688668.SH/baseline.md`
- `artifacts/company_tracking/688668.SH/state.md`
- `artifacts/company_tracking/688668.SH/events.jsonl`
- `artifacts/company_tracking/300394.SZ/baseline.md`
- `artifacts/company_tracking/300394.SZ/state.md`
- `artifacts/company_tracking/300394.SZ/events.jsonl`
- `C:\Users\Administrator\.codex\automations\a-grok\memory.md`

No Git backup was run, per user instruction.

## Per-company completion table

| ticker | name | batch_no | queue_status | browser_scope | announcements_checked | lhb_checked | block_trade_checked | grok_status | open_web_fallback_status | state_change | miss_risk_notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300394.SZ | 天孚通信 | manual_add | completed_manual_baseline | fallback_no_browser | done_ir_2026-05-14_and_baseline | done_no_recent_1m | done_latest_2026-05-08_no_today | not_run_manual_add_chrome_plugin_not_exposed | searched_official_and_trading_pages | baseline_initialized | CPO/1.6T/客户/物料仍需财报量化；未取得Grok/X原生线索 |
| 002428.SZ | 云南锗业 | 1 | completed | fallback_no_browser | done_no_new_official_2026-05-14 | done_no_new | done_no_new | unavailable_chrome_plugin_not_exposed | searched_post_meeting_observation_found | updated_event_and_state | 正式IR问答全文仍缺；会议摘要不是订单/良率硬证据 |
| 002222.SZ | 福晶科技 | 1 | completed | fallback_no_browser | done_no_new_official | done_empty | done_empty | unavailable_chrome_plugin_not_exposed | searched_no_new_hard_signal | unchanged | 深交所公告API超时，已用CNINFO/东方财富/公司IR补位 |
| 300476.SZ | 胜宏科技 | 1 | completed | fallback_no_browser | done_no_new_after_2026-05-08 | done_empty | done_empty | unavailable_chrome_plugin_not_exposed | searched_no_new_verified_operating_signal | updated_state_only | open-web客户/市占率/排产说法多为二手或AI生成 |
| 603256.SH | 宏和科技 | 1 | completed | fallback_no_browser | done_no_new_2026-05-14 | done_no_new | done_no_new | unavailable_chrome_plugin_not_exposed | searched_media_duplicate_only | unchanged | 5月15日股东会后需补扫决议公告 |
| 601869.SH | 长飞光纤 | 1 | completed | fallback_no_browser | done_no_new | done_no_new | done_no_new | unavailable_chrome_plugin_not_exposed | searched_secondary_observation_only | unchanged | H股公告列表未完全结构化抓取；光纤价格讨论偏二级来源 |
| 301511.SZ | 德福科技 | 1 | completed | fallback_no_browser | done_no_new_material | done_no_new | done_no_2026_new_block_trade | unavailable_chrome_plugin_not_exposed | searched_no_new_hard_signal | unchanged | 动态IR页可能需后续交互式浏览；HVLP/RTF收入量化仍缺 |
| 002384.SZ | 东山精密 | 2 | completed | fallback_no_browser | done_no_new | done_no_new | done_no_new | unavailable_chrome_plugin_not_exposed | searched_observation_pool_only | unchanged | AI PCB/索尔思叙事未见新增公告、订单、收入或毛利硬证据 |
| 300308.SZ | 中际旭创 | 2 | completed | fallback_no_browser | done_cninfo_0 | done_no_lhb | done_added_1_block_trade | unavailable_chrome_plugin_not_exposed | searched_trading_event_only | updated_event_and_state | 经营硬披露仍缺，新增仅为小额交易事件 |
| 688498.SH | 源杰科技 | 2 | completed | fallback_no_browser | done_no_new_official | done_empty | done_empty | unavailable_chrome_plugin_not_exposed | searched_no_new_confirmed_operating_signal | unchanged | SSE官方查询超时；200G EML传闻未升级为确认事实 |
| 688668.SH | 鼎通科技 | 2 | completed | fallback_no_browser | done_baseline_latest_2026-05-09_cb_review_passed | done_no_today_latest_history_2026-04-16 | done_no_today_latest_history_2025-05-16 | unavailable_chrome_plugin_not_exposed | completed_company_specific | baseline_initialized | 可转债仍待注册；IR订单和产线口径需财报验证 |

## Material Changes

- 天孚通信：按用户请求新增为 enabled 关注公司并完成首次完整基线。基线确认公司主线为精密无源/高速有源光器件、1.6T 光引擎、CPO 配套 FAU/ELS、泰国产能、客户集中和 H 股发行申请。2026-05-14 IR 称 CPO 配套 FAU、ELS 外置光源等产品已实现稳定交付，同时个别物料仍阶段性缺货。
- 鼎通科技：完成首次完整基线；最近硬事件为 2026-05-09 可转债申请获上交所上市审核委审核通过，仍待证监会注册。跟踪主线为高速通讯连接器/CAGE、112G/224G、液冷散热、汽车 BMS 连接器、蓝海视界机器视觉协同和海外产能。
- 中际旭创：新增 2026-05-14 一笔大宗交易，0.50 万股、539.00 万元，机构专用对机构专用，折溢价率约 0%。该事件仅为交易层信号。
- 云南锗业：业绩说明会 open-web fallback 观察显示公司继续强调 InP 扩产和客户认证，但未披露客户、订单、良率或 6 英寸稳定量产硬证据。

## Trading-event highlights

- 中际旭创：新增一笔小规模大宗交易。
- 天孚通信：未见 2026-05-14 新增龙虎榜或大宗交易；最近公开大宗交易为 2026-05-08 两笔。
- 其余公司：本轮窗口无新增 2026-05-14 龙虎榜或大宗交易硬记录。

## Validation

- Enabled watchlist count: 11.
- Completion table count: 11.
- Missing enabled companies: none.
- Batch validation: original daily run batch 1 had 6 companies and batch 2 had 4 companies; 天孚通信 was added after user request as a manual follow-up baseline.
- Watchlist validation: enabled rows `last_update_date` set to 2026-05-14; 鼎通科技 and 天孚通信 `baseline_status=done` and `last_baseline_date=2026-05-14`.
- JSONL validation: all company `events.jsonl` files parse successfully.
- Git backup: not run, per user instruction.

## Notes

Next high-value checks are 天孚通信 CPO 配套/1.6T 光引擎量化、鼎通科技可转债注册/液冷产线/224G订单兑现、云南锗业正式 IR 问答、中际旭创 H 股招股书或 Q2 经营口径、源杰科技 2026-05-20 业绩说明会、东山精密索尔思硬证据和德福科技 HVLP/RTF 收入量化。
