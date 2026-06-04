# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-06-04
- run_started_at_beijing: 2026-06-04 20:38:21 +08:00
- run_finished_at_beijing: 2026-06-04 21:19:45 +08:00
- automation_id: a-grok
- enabled_company_count: 12
- completed_company_count: 12
- baseline_created_or_refreshed_count: 0
- multi_agent_status: completed_with_one_worker_timeout_controller_fallback
- worker_model_policy: model=gpt-5.5; reasoning_effort=xhigh; explicitly passed for each company worker
- logical_company_worker_limit: 6
- actual_company_workers_spawned: 12
- actual_company_workers_completed: 11
- actual_company_workers_timed_out: 1
- controller_fallback_companies: 300394.SZ
- grok_chrome_status: unavailable_extension_transport_unavailable_after_two_retries
- chrome_diagnostic_status: chrome_running_yes; extension_installed_enabled_yes; native_host_manifest_correct_yes; browser_client_extension_unavailable
- browser_substitution_policy: Browser/Playwright not used as Grok/X substitute
- open_web_fallback_status: searched_per_company_observation_only_no_standalone_material_signal
- announcement_window_policy: T_and_T_plus_1 because run is after 20:00 Beijing time

## worker_batches

- batch_1: 002428.SZ, 002222.SZ, 300476.SZ, 603256.SH, 601869.SH, 301511.SZ
- batch_2: 002384.SZ, 300308.SZ, 688498.SH, 688668.SH, 300394.SZ, 603738.SH

## source_notes

- New events appended: 601869.SH abnormal volatility and dragon-tiger; 301511.SZ shareholder reduction, block trade, subsidiary guarantee; 002384.SZ abnormal volatility with Solers contribution, pledge release, dragon-tiger, block trade; 300308.SZ incentive vesting and two block trades; 688668.SH convertible bond registration, abnormal volatility, two dragon-tiger rows.
- Routine or non-material new disclosures not appended as material events: 601869.SH annual meeting materials; 002384.SZ English ESG report.
- No new baselines were required.
- 300394.SZ company worker timed out and was closed; the controller completed an isolated company task block with CNINFO/SZSE/Eastmoney trading data and open-web fallback, finding no material event.
- Open-web fallback did not add standalone new observation-only items beyond official disclosures and trading-data events.

## completion_table

| ticker | name | batch_no | queue_status | browser_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | grok_status | open_web_fallback_status | state_change | miss_risk_notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_no_material_change | fallback_no_browser | CNINFO/name/company site zero 2026-06-04~2026-06-05; SZSE annList 500 source_gap | T_and_T_plus_1 | 2026-06-04 no_hit | 2026-06-04 no_hit | unavailable_extension_transport_unavailable | searched_observation_only_no_new_hard_signal | no_change | 无InP/锗资源/产能/订单新增硬证据 |
| 002222.SZ | 福晶科技 | 1 | completed_no_material_change | fallback_no_browser | CNINFO/Eastmoney/P5W/company IR zero 2026-06-04~2026-06-05; SZSE annList 500 source_gap | T_and_T_plus_1 | 2026-06-04 no_hit | 2026-06-04 no_hit | unavailable_extension_transport_unavailable | searched_observation_only_no_new_hard_signal | no_change | 无WSS/Faraday rotator/晶体订单或毛利率新证据 |
| 300476.SZ | 胜宏科技 | 1 | completed_no_material_change | fallback_no_browser | CNINFO/Eastmoney/company IR zero 2026-06-04~2026-06-05; SZSE annList 500 source_gap | T_and_T_plus_1 | 2026-06-04 no_hit | 2026-06-04 no_hit | unavailable_extension_transport_unavailable | searched_observation_only_no_new_verified_operating_signal | no_change | 无AI服务器PCB客户/订单/产能/毛利率新增硬披露 |
| 603256.SH | 宏和科技 | 1 | completed_no_material_change | fallback_no_browser | CNINFO/SSE/Eastmoney zero 2026-06-04~2026-06-05; prior 2026-06-03 dividend already in ledger | T_and_T_plus_1 | 2026-06-04 no_hit | 2026-06-04 no_hit | unavailable_extension_transport_unavailable | searched_observation_only_no_new_material_signal | no_change | 无Low CTE/T-glass/电子布客户认证、订单、价格或H股进度新增 |
| 601869.SH | 长飞光纤 | 1 | completed_with_abnormal_lhb | fallback_no_browser | CNINFO/SSE hit 2026-06-05 abnormal volatility and AGM materials | T_and_T_plus_1 | 2026-06-04 hit_lhb_three_day_22.69pct | 2026-06-04 no_hit | unavailable_extension_transport_unavailable | searched_observation_only_no_new_order_signal | trading_risk_up | 异常波动公告承认数据中心/价格关注但未确认订单或业绩兑现 |
| 301511.SZ | 德福科技 | 1 | completed_with_reduction_guarantee_block_trade | fallback_no_browser | CNINFO name query hit 2 official announcements; code/mirror missed; SZSE annList 500 source_gap | T_and_T_plus_1 | 2026-06-04 no_hit | 2026-06-04 one_block_trade_6024w | unavailable_extension_transport_unavailable | searched_observation_only_no_hvlp_rtf_signal | reduction_and_guarantee_appended | 减持计划实施和担保进展新增；HVLP/RTF商业化未变化 |
| 002384.SZ | 东山精密 | 2 | completed_with_abnormal_lhb_block_trade | fallback_no_browser | CNINFO hit abnormal volatility, pledge release, ESG English report | T_and_T_plus_1 | 2026-06-04 hit_lhb_three_day_23.39pct | 2026-06-04 one_discount_block_trade_1211w | unavailable_extension_transport_unavailable | searched_observation_only_no_new_customer_order | solers_quantified_and_trading_risk_up | 索尔思贡献比例官方量化；仍缺客户/订单/毛利率/良率 |
| 300308.SZ | 中际旭创 | 2 | completed_with_incentive_and_block_trades | fallback_no_browser | CNINFO/Eastmoney hit 2026-06-05 incentive vesting listing announcement; SZSE annList 500 source_gap | T_and_T_plus_1 | 2026-06-04 no_hit | 2026-06-04 two_flat_institution_block_trades_25088w | unavailable_extension_transport_unavailable | searched_observation_only_duplicate_official_trading_only | incentive_and_block_trades_appended | 连续机构大宗交易需跟踪；经营主线未变化 |
| 688498.SH | 源杰科技 | 2 | completed_no_material_change | fallback_no_browser | CNINFO/SSE/Eastmoney/company IR zero 2026-06-04~2026-06-05 | T_and_T_plus_1 | 2026-06-04 no_hit | 2026-06-04 no_hit | unavailable_extension_transport_unavailable | searched_observation_only_no_new_company_hard_signal | no_change | 6月3日龙虎榜已入账，本轮无风险提示或200G EML新证据 |
| 688668.SH | 鼎通科技 | 2 | completed_with_convertible_abnormal_lhb | fallback_no_browser | CNINFO hit convertible bond registration and abnormal volatility announcement | T_and_T_plus_1 | 2026-06-04 two_lhb_records | 2026-06-04 no_hit | unavailable_extension_transport_unavailable | searched_observation_only_official_risk_warning_only | convertible_positive_but_liquid_cooling_risk_up | 液冷仅少量阶段性交付、无大额长期锁定订单，交易风险上调 |
| 300394.SZ | 天孚通信 | 2 | completed_by_controller_fallback_after_worker_timeout | fallback_no_browser | Controller CNINFO dual query zero 2026-06-04~2026-06-05 | T_and_T_plus_1 | 2026-06-04 no_hit | 2026-06-04 no_hit | unavailable_extension_transport_unavailable | searched_controller_fallback_observation_only_no_new_hard_signal | no_change | worker超时后总控补做；无1.6T/CPO/FAU/ELS/H股进展新披露 |
| 603738.SH | 泰晶科技 | 2 | completed_no_material_change | fallback_no_browser | CNINFO/SSE/Eastmoney zero 2026-06-04~2026-06-05 | T_and_T_plus_1 | 2026-06-04 no_hit | 2026-06-04 no_hit | unavailable_extension_transport_unavailable | searched_observation_only_no_new_material_signal | no_change | 无312.5MHz/625MHz客户订单、产能、价格或收入占比新披露 |

## reconciliation

- enabled_watchlist_count: 12
- completion_table_count: 12
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
