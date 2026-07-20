# A-share company tracking run status

- run_date_beijing: 2026-07-20
- run_started_at_beijing: 2026-07-20 20:33:10 +08:00
- run_finished_at_beijing: 2026-07-20 21:08:32 +08:00
- automation_id: a-grok
- run_status: completed
- enabled_company_count: 13
- completed_company_count: 13
- failed_company_count: 0
- baseline_created_or_refreshed_count: 0
- state_updated_company_count: 9
- events_appended_count: 15
- announcement_window_checked: T_and_T_plus_1
- announcement_query_window: 2026-07-17 to 2026-07-21
- trading_event_dates_checked: 2026-07-17, 2026-07-20
- collection_scope: controller_plus_bounded_single_company_subagents
- multi_agent_status: used_by_explicit_user_permission
- company_worker_queue: completed; 3 isolated read-only subagents handled 002428.SZ, 603256.SH, 601869.SH; controller independently handled the remaining 10 companies and all source ranking, deduplication, writeback and reconciliation; peak active agents 4 including controller, below maximum 6
- open_web_policy: Codex open-web per company; observation/discovery only; non-official results require official or issuer-source confirmation before fact status
- source_priority: official disclosure -> company-authored IR -> exchange trading data -> vendor cross-check -> reputable media -> open-web observation
- source_limitations: 002428 SZSE announcement API returned 500 and issuer site timed out but CNINFO/official IR covered the window; isolated SSE/SZSE requests needed retries; T+1 pages can refresh after this snapshot

## Company order current run

1. 002428.SZ 云南锗业
2. 603256.SH 宏和科技
3. 601869.SH 长飞光纤
4. 301511.SZ 德福科技
5. 002384.SZ 东山精密
6. 300308.SZ 中际旭创
7. 688498.SH 源杰科技
8. 688668.SH 鼎通科技
9. 300394.SZ 天孚通信
10. 002851.SZ 麦格米特
11. 000636.SZ 风华高科
12. 688048.SH 长光华芯
13. 301217.SZ 铜冠铜箔

## Material results

- Official earnings forecasts: 天孚通信（归母 +25%至+45%，个别物料与汇率约束）；铜冠铜箔（归母 +486.49%至+543.70%，高频高速铜箔量价/结构正式进入利润驱动）。
- Official capital/governance events: 东山精密（2亿至3亿元回购）；中际旭创（H股通过上市聆讯并发布聆讯后资料集，非最终批准）；德福科技（琥珀新材进口代理担保）。
- Official abnormal-volatility event: 宏和科技（三日跌幅偏离累计超过20%，公司及股东确认无未披露重大事项）。
- Dragon-tiger events: 宏和科技、德福科技、东山精密、鼎通科技、长光华芯、铜冠铜箔。
- Block-trade events: 中际旭创（3.867917亿元平价）；东山精密（326.60万元平价）；风华高科（248.94万元平价）。
- No new company-level hard event: 云南锗业、长飞光纤、源杰科技、麦格米特。

## Per-company completion table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | lhb_checked | block_trade_checked | announcement_window_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed | subagent_read_only_official_plus_open_web | CNINFO/互动易：7/17-7/21 no_hit | 7/17,7/20 no_hit | 7/17,7/20 no_hit | T_and_T_plus_1 | searched_no_new_company_signal | no_fundamental_change_secondary_price_only | 深交所公告接口500、官网超时；T+1迟发风险 | used_by_explicit_user_permission |
| 603256.SH | 宏和科技 | 2 | completed | subagent_read_only_official_plus_open_web | SSE/CNINFO：T+1异动公告及回复 | 7/20 hit_three_day_downside | 7/17,7/20 no_hit | T_and_T_plus_1 | searched_market_context_no_new_operating_signal | trading_risk_materialized_fundamental_unchanged | T+1后续晚间仍可能刷新 | used_by_explicit_user_permission |
| 601869.SH | 长飞光纤 | 3 | completed | subagent_read_only_official_plus_open_web | CNINFO/SSE/IR/HKEX：7/17-7/21 no_hit | 7/17,7/20 no_hit | 7/17,7/20 no_hit | T_and_T_plus_1 | searched_media_restate_no_new_hard_signal | no_change | IR/HKEX异步更新风险 | used_by_explicit_user_permission |
| 301511.SZ | 德福科技 | 4 | completed | controller_official_plus_open_web | CNINFO：7/20担保 | 7/20 hit_limit_down | 7/17,7/20 no_hit | T_and_T_plus_1 | no_signal | higher_guarantee_fx_and_trading_risk | 担保汇率/实际余额及剩余减持额度待跟踪 | controller |
| 002384.SZ | 东山精密 | 5 | completed | controller_official_plus_open_web | CNINFO：T+1回购及董事会 | 7/20 hit_downside | 7/20 hit_1_flat_trade | T_and_T_plus_1 | no_signal | repurchase_signal_and_higher_trading_volatility | 回购执行、产能/良率/订单 N/A | controller |
| 300308.SZ | 中际旭创 | 6 | completed | controller_official_plus_open_web | CNINFO/HKEX：H股聆讯后进展 | 7/17,7/20 no_hit | 7/17 hit_1_flat_trade | T_and_T_plus_1 | searched_social_observation_no_verified_signal | h_share_progress_and_flat_block_turnover | 聆讯非批准；发行规模和摊薄待定 | controller |
| 688498.SH | 源杰科技 | 7 | completed | controller_official_plus_open_web | CNINFO/SSE/IR：7/17-7/21 no_hit | 7/17,7/20 no_hit | 7/17,7/20 no_hit | T_and_T_plus_1 | no_signal | no_change | 200G EML量产与客户 N/A | controller |
| 688668.SH | 鼎通科技 | 8 | completed | controller_official_plus_open_web | 7/17预告已入账；其后no_hit | 7/17 hit_limit_down | 7/17,7/20 no_hit | T_and_T_plus_1 | no_signal | higher_downside_crowding | 液冷仍小批试产；转债风险待跟踪 | controller |
| 300394.SZ | 天孚通信 | 9 | completed | controller_official_plus_open_web | CNINFO：7/18 H1预告 | 7/17,7/20 no_hit | 7/17,7/20 no_hit | T_and_T_plus_1 | no_signal | strengthened_h1_profit_with_supply_fx_constraints | 1.6T/CPO拆分和客户结构 N/A | controller |
| 002851.SZ | 麦格米特 | 10 | completed | controller_official_plus_open_web | CNINFO/SZSE/IR：7/17-7/21 no_hit | 7/17,7/20 no_hit | 7/17,7/20 no_hit | T_and_T_plus_1 | no_signal | no_change | GB300客户/订单金额/AIDC利润 N/A | controller |
| 000636.SZ | 风华高科 | 11 | completed | controller_official_plus_open_web | CNINFO/IR：7/17-7/21 no_hit | 7/17,7/20 no_hit | 7/17 hit_small_flat_trade | T_and_T_plus_1 | no_signal | small_flat_block_only | AI MLCC公司级兑现仍缺 | controller |
| 688048.SH | 长光华芯 | 12 | completed | controller_official_plus_open_web | SSE/CNINFO/IR：7/17-7/21 no_hit | 7/17 hit_limit_down | 7/17,7/20 no_hit | T_and_T_plus_1 | searched_market_context_no_new_company_signal | higher_downside_crowding | 客户名称/200G EML量产/扣非盈利 N/A | controller |
| 301217.SZ | 铜冠铜箔 | 13 | completed | controller_official_plus_open_web | CNINFO：7/20 H1预告 | 7/20 hit_limit_down | 7/17,7/20 no_hit | T_and_T_plus_1 | no_signal | strengthened_hf_hs_copper_foil_profit_driver_and_higher_trading_risk | HVLP分代收入毛利/具名客户 N/A | controller |

## Final reconciliation

- enabled_watchlist_count: 13
- completion_table_count: 13
- missing_enabled_tickers: none
- duplicate_completion_tickers: none
- watchlist_order_match: true
- pending_or_refresh_needed_baselines: 0
- baseline_files_changed: 0
- project_files_only: true
- git_commit_or_push: false
- final_validation: passed; enabled/completion exact-order 13/13, 15 new JSONL events parsed with required fields and unique identities, 9 state updates present, workbook reopened with only 13 target cells changed and styles preserved, UTF-8 and git diff checks passed
