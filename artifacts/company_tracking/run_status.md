# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-06-03
- run_started_at_beijing: 2026-06-03 20:35:19 +08:00
- run_finished_at_beijing: 2026-06-03 21:03:27 +08:00
- automation_id: a-grok
- enabled_company_count: 12
- completed_company_count: 12
- baseline_created_or_refreshed_count: 0
- multi_agent_status: completed_with_two_worker_timeouts_controller_fallback
- worker_model_policy: model=gpt-5.5; reasoning_effort=xhigh; explicitly passed for each company worker
- logical_company_worker_limit: 6
- actual_company_workers_spawned: 12
- actual_company_workers_completed: 10
- actual_company_workers_timed_out: 2
- controller_fallback_companies: 688668.SH, 300394.SZ
- grok_chrome_status: unavailable_extension_transport_unavailable_after_two_retries
- chrome_diagnostic_status: chrome_running_yes; extension_installed_enabled_yes; native_host_manifest_correct_yes; browser_client_extension_unavailable
- browser_substitution_policy: Browser/Playwright not used as Grok/X substitute
- open_web_fallback_status: searched_per_company_observation_only
- announcement_window_policy: T_and_T_plus_1 because run is after 20:00 Beijing time

## worker_batches

- batch_1: 002428.SZ, 002222.SZ, 300476.SZ, 603256.SH, 601869.SH, 301511.SZ
- batch_2: 002384.SZ, 300308.SZ, 688498.SH, 688668.SH, 300394.SZ, 603738.SH

## source_notes

- New events appended: 002384.SZ 2026-06-02 investor-relations record; 002384.SZ 2026-06-03 small block trade; 300308.SZ 2026-06-03 block trade; 688498.SH 2026-06-03 dragon-tiger list.
- Routine or duplicate official items not re-appended: 300476.SZ H-share monthly return; 603256.SH dividend implementation already written in prior T+1 run; 002384.SZ pledge/release announcement already written in prior T+1 run.
- No new baselines were required.
- 688668.SH and 300394.SZ company workers timed out and were closed; the controller completed isolated company task blocks with CNINFO/SSE/SZSE/Eastmoney trading feeds and open-web fallback, finding no material event.
- Open-web fallback did not add standalone new observation-only items beyond official disclosures and trading-data events.

## completion_table

| ticker | name | batch_no | queue_status | browser_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | grok_status | open_web_fallback_status | state_change | miss_risk_notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_no_material_change | fallback_no_browser | CNINFO/company site zero 2026-06-03~2026-06-04; SZSE annList 50x source_gap | T_and_T_plus_1 | 2026-06-03 no_hit | 2026-06-03 no_hit | unavailable_extension_transport_unavailable | searched_observation_only_no_material_signal | no_change | open-web 仅见小金属板块行情观察，不构成 InP/锗资源/产能/订单硬事件。 |
| 002222.SZ | 福晶科技 | 1 | completed_no_material_change | fallback_no_browser | CNINFO/SZSE/company IR/Eastmoney zero 2026-06-03~2026-06-04 | T_and_T_plus_1 | 2026-06-03 no_hit | 2026-06-03 no_hit | unavailable_extension_transport_unavailable | searched_observation_only_no_new_hard_signal | no_change | 法拉第旋光片/WSS/晶体订单、客户、毛利和回款仍待验证。 |
| 300476.SZ | 胜宏科技 | 1 | completed_routine_announcement_no_material_change | fallback_no_browser | CNINFO found routine H-share monthly return; Eastmoney 0; company IR no operating update | T_and_T_plus_1 | 2026-06-03 no_hit | 2026-06-03 no_hit | unavailable_extension_transport_unavailable | searched_observation_only_no_new_verified_operating_signal | no_change | H 股证券变动月报不改变 AI 服务器 PCB、海外客户、订单、产能或毛利率状态。 |
| 603256.SH | 宏和科技 | 1 | completed_no_new_material_change_existing_event | fallback_no_browser | CNINFO/SSE found existing dividend implementation already in ledger; no newer item | T_and_T_plus_1 | 2026-06-03 no_hit | 2026-06-03 no_hit | unavailable_extension_transport_unavailable | searched_no_new_material_signal_observation_only | no_change | 2026-06-03 分红实施已由上一轮 T+1 入账；无 Low CTE/T-glass 新证据。 |
| 601869.SH | 长飞光纤 | 1 | completed_no_material_change | fallback_no_browser | CNINFO/SSE/YOFC IR/Eastmoney zero 2026-06-03~2026-06-04 | T_and_T_plus_1 | 2026-06-03 no_hit | 2026-06-03 no_hit | unavailable_extension_transport_unavailable | searched_observation_only_market_heat_no_confirmed_hard_event | no_change | 仅有光纤光缆/CPO行情热度观察，不构成订单、客户或业绩确认。 |
| 301511.SZ | 德福科技 | 1 | completed_no_material_change | fallback_no_browser | CNINFO/Eastmoney zero 2026-06-03~2026-06-04; SZSE 500 source_gap | T_and_T_plus_1 | 2026-06-03 no_hit | 2026-06-03 no_hit | unavailable_extension_transport_unavailable | searched_observation_only_no_new_hard_signal | no_change | 未发现 HVLP/RTF 客户认证、批量交付、订单、收入占比或毛利率新增证据。 |
| 002384.SZ | 东山精密 | 2 | completed_with_ir_and_block_trade | fallback_no_browser_open_web_only | CNINFO found IR record and existing pledge announcement; pledge skipped duplicate | T_and_T_plus_1 | 2026-06-03 no_hit | 2026-06-03 one_small_block_trade | unavailable_extension_transport_unavailable | searched_observation_only | ir_update_and_minor_block_trade_appended | CNINFO API/镜像口径对 IR 有差异；仍缺客户、订单、收入、毛利率、良率和产能量化。 |
| 300308.SZ | 中际旭创 | 2 | completed_with_block_trade | fallback_no_browser | CNINFO zero 2026-06-03~2026-06-04; latest remains 2026-06-01 clarification | T_and_T_plus_1 | 2026-06-03 no_hit | 2026-06-03 one_large_block_trade | unavailable_extension_transport_unavailable | searched_observation_only_trading_liquidity_signal_only | block_trade_appended | 3.315 亿元平价机构换手为交易结构信号，不证明 800G/1.6T/硅光经营兑现。 |
| 688498.SH | 源杰科技 | 2 | completed_with_lhb | fallback_no_browser | CNINFO/SSE/company IR zero 2026-06-03~2026-06-04 | T_and_T_plus_1 | 2026-06-03 hit_lhb_gain_15pct | 2026-06-03 no_hit | unavailable_extension_transport_unavailable | searched_observation_only_no_new_company_hard_signal_except_lhb | lhb_appended | 龙虎榜改变交易拥挤风险，不改变 CW/200G EML 硬证据缺口。 |
| 688668.SH | 鼎通科技 | 2 | completed_by_controller_fallback_after_worker_timeout | fallback_no_browser | CNINFO/SSE/Eastmoney zero 2026-06-03~2026-06-04 | T_and_T_plus_1 | 2026-06-03 no_hit | 2026-06-03 no_hit | unavailable_extension_transport_unavailable | searched_controller_fallback_observation_only | no_change | 公司 worker 超时后由总控补做；无高速连接器/液冷/客户/订单新增硬证据。 |
| 300394.SZ | 天孚通信 | 2 | completed_by_controller_fallback_after_worker_timeout | fallback_no_browser | CNINFO/SZSE/company IR/HKEX zero 2026-06-03~2026-06-04 | T_and_T_plus_1 | 2026-06-03 no_hit | 2026-06-03 no_hit | unavailable_extension_transport_unavailable | searched_controller_fallback_observation_only | no_change | 公司 worker 超时后由总控补做；无 1.6T/CPO/FAU/ELS、泰国产能或 H 股进展新硬披露。 |
| 603738.SH | 泰晶科技 | 2 | completed_no_material_change | fallback_no_browser | CNINFO/SSE/company site zero 2026-06-03~2026-06-04 | T_and_T_plus_1 | 2026-06-03 no_hit | 2026-06-03 no_hit | unavailable_extension_transport_unavailable | searched_observation_only_no_new_hard_signal | no_change | open-web 仅见行情、股吧情绪和既有晶振叙事；无客户、订单、产能、价格或收入占比硬披露。 |

## reconciliation

- enabled_watchlist_count: 12
- completion_table_count: 12
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
