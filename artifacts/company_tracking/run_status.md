# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-06-05
- run_started_at_beijing: 2026-06-05 20:37:23 +08:00
- run_finished_at_beijing: 2026-06-05 21:54:43 +08:00
- automation_id: a-grok
- enabled_company_count: 12
- completed_company_count: 12
- baseline_created_or_refreshed_count: 0
- current_run_multi_agent_status: completed_with_workers_before_prompt_policy_change
- next_run_multi_agent_policy: not_used_by_policy
- prompt_policy_change: 2026-06-05 user requested cancel sub-agent permission because workers are too slow; docs/company_tracking/A_SHARE_COMPANY_TRACKING_PROMPT.md and skills/a-share-company-tracking/SKILL.md updated
- worker_model_policy_current_run: model=gpt-5.5; reasoning_effort=xhigh; explicitly passed for each company worker before policy change
- logical_company_worker_limit_current_run: 6
- actual_company_workers_spawned_current_run: 12
- actual_company_workers_completed_current_run: 12
- controller_fallback_companies: none
- grok_chrome_status: unavailable_native_host_registry_missing
- chrome_diagnostic_status: chrome_running_yes; extension_installed_enabled_yes; native_host_manifest_missing_registry_key; browser_client_extension_unavailable
- browser_substitution_policy: Browser/Playwright not used as Grok/X substitute
- open_web_fallback_status: searched_per_company_observation_only
- announcement_window_policy: T_and_T_plus_1 because run is after 20:00 Beijing time

## worker_batches_current_run

- batch_1: 002428.SZ, 002222.SZ, 300476.SZ, 603256.SH, 601869.SH, 301511.SZ
- batch_2: 002384.SZ, 300308.SZ, 688498.SH, 688668.SH, 300394.SZ, 603738.SH
- next_run_batching_policy: no sub-agents; controller processes isolated company task blocks directly in watchlist order

## source_notes

- New events appended: 301511.SZ 2026-06-05 block trade; 300394.SZ 2025 annual rights distribution implementation.
- Observation-only item not appended as hard event: 300308.SZ 2026-06-05 open-web observation of record turnover / sharp decline, treated as trading-crowding watch only.
- Existing events not duplicated: 601869.SH abnormal volatility; 002384.SZ abnormal volatility / pledge release; 688668.SH convertible bond registration and abnormal volatility.
- No new baselines were required.
- Chrome/Grok lane unavailable because Chrome extension communication failed and native host registry key is missing. Open-web fallback stayed observation-only.
- Some official/market data endpoints returned timeout, SSL, 50x, or dynamic-page source gaps; per-company notes record the affected source.

## completion_table

| ticker | name | batch_no | queue_status | browser_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | grok_status | open_web_fallback_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_no_material_change | fallback_no_browser | CNINFO/name/Eastmoney/company IR no_hit; SZSE annList source_gap | T_and_T_plus_1 | 2026-06-05 no_hit | 2026-06-05 no_hit | unavailable_native_host_registry_missing | searched_observation_only_no_new_hard_signal | no_change | 无InP/GaAs客户、订单、良率、6英寸量产、出口许可或利润兑现新增证据 | completed_worker |
| 002222.SZ | 福晶科技 | 1 | completed_no_material_change | fallback_no_browser | CNINFO/SZSE/Eastmoney/company IR no_hit | T_and_T_plus_1 | 2026-06-05 no_hit | 2026-06-05 no_hit | unavailable_native_host_registry_missing | searched_observation_only_no_new_hard_signal | no_change | 无WSS、法拉第旋光片、晶体订单、扩产或收入拆分新增证据 | completed_worker |
| 300476.SZ | 胜宏科技 | 1 | completed_with_source_gap_no_material_change | fallback_no_browser | company IR/Eastmoney no_hit; CNINFO/SZSE source_gap | T_and_T_plus_1 | Eastmoney no_hit; SZSE source_gap | Eastmoney no_hit; SZSE source_gap | unavailable_native_host_registry_missing | searched_observation_only_no_verified_material_delta | no_change | 官方接口有超时/50x；无AI服务器PCB客户、订单、产能或毛利率新增硬信号 | completed_worker |
| 603256.SH | 宏和科技 | 1 | completed_no_material_change | fallback_no_browser | CNINFO/SSE no_hit; company IR timeout | T_and_T_plus_1 | 2026-06-05 no_hit | 2026-06-05 no_hit | unavailable_native_host_registry_missing | searched_observation_only_no_material_new_hit | no_change | 无Low CTE/T-glass客户认证、订单、涨价或参数新增证据 | completed_worker |
| 601869.SH | 长飞光纤 | 1 | completed_no_new_material_change | fallback_no_browser | CNINFO hit 6/5 items already recorded or routine; 6/6 no_hit | T_and_T_plus_1 | 2026-06-05 no_hit; latest 6/4 already recorded | 2026-06-05 no_hit secondary; API timeout risk | unavailable_native_host_registry_missing | searched_observation_only_no_new_material_verified_event | no_change | 异常波动已入账；股东会材料属治理流程；无订单/价格/特种光纤新增硬证据 | completed_worker |
| 301511.SZ | 德福科技 | 1 | completed_with_block_trade | fallback_no_browser | CNINFO/Eastmoney no_hit; SZSE annList source_gap; company IR no_new | T_and_T_plus_1 | 2026-06-05 no_hit | 2026-06-05 hit_1_block_trade_5897.50w | unavailable_native_host_registry_missing | searched_observation_only_hit_block_trade_media_no_new_hvlp_rtf_signal | block_trade_appended | 6/5大宗交易归属待后续官方减持进展确认 | completed_worker |
| 002384.SZ | 东山精密 | 2 | completed_no_new_material_delta | fallback_no_browser | 2026-06-05 hit existing 3; 2026-06-06 no_hit | T_and_T_plus_1 | 2026-06-05 no_hit with API timeout gap | 2026-06-05 no_hit with API timeout gap | unavailable_native_host_registry_missing | searched_observation_only_no_new_material_event | no_change | 6/5异动公告和解押已入账；无AI PCB/FPC订单、客户、毛利率新披露 | completed_worker |
| 300308.SZ | 中际旭创 | 2 | completed_with_source_gap | fallback_no_browser | 2026-06-05 hit known incentive vesting; 2026-06-06 no_hit | T_and_T_plus_1 | checked no_hit with official API timeout gap | checked no_hit with official API timeout gap | unavailable_native_host_registry_missing | searched_observation_only_record_turnover_no_operating_signal | trading_risk_watch_only | 放量下跌仅观察层；无800G/1.6T、硅光、客户、物料或毛利率新硬披露 | completed_worker |
| 688498.SH | 源杰科技 | 2 | completed_no_material_change | fallback_no_browser | SSE/CNINFO/Eastmoney/company IR no_hit | T_and_T_plus_1 | 2026-06-05 no_hit | 2026-06-05 no_hit | unavailable_native_host_registry_missing | searched_observation_only_no_new_company_hard_signal | no_change | 无200G EML客户定点、批量订单或收入占比新增证据 | completed_worker |
| 688668.SH | 鼎通科技 | 2 | completed_no_new_material_change | fallback_no_browser | CNINFO hit existing 2; 2026-06-06 no_hit | T_and_T_plus_1 | 2026-06-05 no_hit | 2026-06-05 no_hit | unavailable_native_host_registry_missing | completed_observation_only_no_new_material | no_change | 6/5可转债批复和异常波动已入账；无新增订单/液冷长期合同证据 | completed_worker |
| 300394.SZ | 天孚通信 | 2 | completed_with_rights_distribution | fallback_no_browser | CNINFO hit rights distribution; T+1 no extra | T_and_T_plus_1 | checked no_hit secondary; SZSE source_gap | checked no_hit secondary; SZSE source_gap | unavailable_native_host_registry_missing | searched_observation_only_hit_rights_distribution_no_operating_evidence | rights_distribution_appended | 权益分派影响股本和交易口径，不改变1.6T/CPO/H股主线 | completed_worker |
| 603738.SH | 泰晶科技 | 2 | completed_no_material_change | fallback_no_browser | CNINFO/SSE no_hit; company site hit nonmaterial article | T_and_T_plus_1 | 2026-06-05 no_hit | 2026-06-05 no_hit | unavailable_native_host_registry_missing | searched_observation_only_no_new_hard_signal | no_change | 官网科普文章非IR/公告；无312.5MHz/625MHz订单、价格或毛利率新增证据 | completed_worker |

## reconciliation

- enabled_watchlist_count: 12
- completion_table_count: 12
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
- watchlist_last_update_date: 2026-06-05 for all enabled rows
