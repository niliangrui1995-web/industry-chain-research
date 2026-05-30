# A股公司持续跟踪 run_status

## latest_run
- run_date: 2026-05-30
- run_finished_at_beijing: 2026-05-30 20:58:05 +08:00
- automation_id: a-grok
- enabled_company_count: 12
- completed_company_count: 12
- baseline_created_or_refreshed_count: 0
- multi_agent_status: completed
- worker_model_policy: model=gpt-5.5; reasoning_effort=xhigh; explicitly passed for each successful company worker
- logical_company_worker_limit: 6
- actual_company_workers_spawned: 12
- actual_company_workers_completed: 12
- grok_chrome_status: unavailable_no_callable_chrome_tool
- browser_substitution_policy: Browser/Playwright not used as Grok/X substitute
- open_web_fallback_status: searched_per_company_observation_only
- announcement_window_policy: T_and_T_plus_1 because run is after 20:00 Beijing time

## worker_batches
- batch_1: 002428.SZ, 002222.SZ, 300476.SZ, 603256.SH, 601869.SH, 301511.SZ
- batch_2: 002384.SZ, 300308.SZ, 688498.SH, 688668.SH, 300394.SZ, 603738.SH

## source_notes
- CNINFO live API returned no 2026-05-30~2026-05-31 formal announcements for all enabled companies except already-recorded 002384.SZ 2026-05-30 pledge-related event found in the local event ledger.
- Eastmoney latest-trading-day trading checks confirmed existing 2026-05-29 observations: 603738.SH LHB, 002222.SZ one block trade, 300308.SZ three block trades.
- New appended events: 002222.SZ:投资者关系活动信息：法拉第旋光片已通过部分客户认证并实现供货，2025年营收占比不足1%, 601869.SH:2026-05-22投资者关系记录取得CNINFO官方PDF源, 301511.SZ:关于收购安徽慧儒科技有限公司部分股权并增资的进展暨完成工商变更登记的公告, 301511.SZ:高负债扩张，德福科技乘风31亿押注高端AI铜箔, 688498.SH:源杰科技调入科创50指数样本，2026年6月12日收市后生效

## completion_table
| ticker | name | batch_no | queue_status | browser_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | grok_status | open_web_fallback_status | state_change | miss_risk_notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed | chrome_grok_unavailable_no_callable_tool | CNINFO 2026-05-30~2026-05-31 zero | T_and_T_plus_1 | Eastmoney latest trading day 2026-05-29 no_hit | Eastmoney latest trading day 2026-05-29 no_hit | unavailable_no_callable_chrome_tool | searched_no_signal | no_change | 可能遗漏非公告论坛热度；官方与交易数据未见新增。 |
| 002222.SZ | 福晶科技 | 1 | completed | chrome_grok_unavailable_no_callable_tool | CNINFO 2026-05-30~2026-05-31 zero | T_and_T_plus_1 | Eastmoney latest trading day 2026-05-29 no_hit | hit_1_trade_201.12万_already_recorded | unavailable_no_callable_chrome_tool | searched_signal_found | secondary_ir_observation_appended | 官方IR原文/PDF未定位，法拉第旋光片线索仍为二级转述观察。 |
| 300476.SZ | 胜宏科技 | 1 | completed | chrome_grok_unavailable_no_callable_tool | CNINFO 2026-05-30~2026-05-31 zero | T_and_T_plus_1 | Eastmoney latest trading day 2026-05-29 no_hit | Eastmoney latest trading day 2026-05-29 no_hit | unavailable_no_callable_chrome_tool | searched_no_signal | no_change | 未见订单/客户/毛利率新增披露。 |
| 603256.SH | 宏和科技 | 1 | completed | chrome_grok_unavailable_no_callable_tool | CNINFO 2026-05-30~2026-05-31 zero | T_and_T_plus_1 | Eastmoney latest trading day 2026-05-29 no_hit | Eastmoney latest trading day 2026-05-29 no_hit | unavailable_no_callable_chrome_tool | searched_no_signal | no_change | 上证380调入为既有交易结构事件；无新客户认证硬证据。 |
| 601869.SH | 长飞光纤 | 1 | completed | chrome_grok_unavailable_no_callable_tool | CNINFO 2026-05-30~2026-05-31 zero | T_and_T_plus_1 | Eastmoney latest trading day 2026-05-29 no_hit | Eastmoney latest trading day 2026-05-29 no_hit | unavailable_no_callable_chrome_tool | searched_source_upgrade | official_ir_source_upgrade_appended | 来源升级不等同新增经营变化；订单排期仍未披露。 |
| 301511.SZ | 德福科技 | 1 | completed | chrome_grok_unavailable_no_callable_tool | CNINFO 2026-05-30~2026-05-31 zero; backfill_2026-04-28 official found | T_and_T_plus_1 | Eastmoney latest trading day 2026-05-29 no_hit | Eastmoney latest trading day 2026-05-29 no_hit | unavailable_no_callable_chrome_tool | searched_signal_found | official_backfill_and_media_observation_appended | 5月30日媒体观察需官方确认；资本开支与负债压力上升。 |
| 002384.SZ | 东山精密 | 2 | completed | chrome_grok_unavailable_no_callable_tool | CNINFO 2026-05-30 hit_existing_1225338102_deduped; 2026-05-31 zero | T_and_T_plus_1 | Eastmoney latest trading day 2026-05-29 no_hit | Eastmoney latest trading day 2026-05-29 no_hit | unavailable_no_callable_chrome_tool | searched_no_new_operating_signal | no_change_existing_pledge_event | 质押事项已记录；不代表AI PCB经营变化。 |
| 300308.SZ | 中际旭创 | 2 | completed | chrome_grok_unavailable_no_callable_tool | CNINFO 2026-05-30~2026-05-31 zero | T_and_T_plus_1 | Eastmoney latest trading day 2026-05-29 no_hit | hit_3_trades_1288.89万_already_recorded | unavailable_no_callable_chrome_tool | searched_no_signal | no_change_existing_block_trades | 大宗交易为既有平价交易；未见800G/1.6T新硬证据。 |
| 688498.SH | 源杰科技 | 2 | completed | chrome_grok_unavailable_no_callable_tool | CNINFO 2026-05-30~2026-05-31 zero | T_and_T_plus_1 | Eastmoney latest trading day 2026-05-29 no_hit | Eastmoney latest trading day 2026-05-29 no_hit | unavailable_no_callable_chrome_tool | searched_signal_found | official_index_event_appended | 指数调入提升交易弹性，不构成200G EML订单或收入证明。 |
| 688668.SH | 鼎通科技 | 2 | completed | chrome_grok_unavailable_no_callable_tool | CNINFO 2026-05-30~2026-05-31 zero | T_and_T_plus_1 | Eastmoney latest trading day 2026-05-29 no_hit | Eastmoney latest trading day 2026-05-29 no_hit | unavailable_no_callable_chrome_tool | searched_no_signal | no_change | 6月2日业绩说明会前无新增硬证据。 |
| 300394.SZ | 天孚通信 | 2 | completed | chrome_grok_unavailable_no_callable_tool | CNINFO 2026-05-30~2026-05-31 zero | T_and_T_plus_1 | Eastmoney latest trading day 2026-05-29 no_hit | Eastmoney latest trading day 2026-05-29 no_hit | unavailable_no_callable_chrome_tool | searched_no_signal | no_change | H股发行和1.6T/CPO订单仍无新披露。 |
| 603738.SH | 泰晶科技 | 2 | completed | chrome_grok_unavailable_no_callable_tool | CNINFO 2026-05-30~2026-05-31 zero | T_and_T_plus_1 | hit_2026-05-29_already_recorded | Eastmoney latest trading day 2026-05-29 no_hit | unavailable_no_callable_chrome_tool | searched_no_signal | no_change_existing_lhb | 龙虎榜已记录；未见高频晶体订单/客户硬证据。 |

## reconciliation
- enabled_watchlist_count: 12
- completion_table_count: 12
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
