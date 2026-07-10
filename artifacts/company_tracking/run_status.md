# A股公司持续跟踪运行状态

## Latest run
- automation_id: a-grok
- run_date: 2026-07-10
- run_started_at_beijing: 2026-07-10 20:31:53 +08:00
- run_finished_at_beijing: 2026-07-10 20:50:34 +08:00
- enabled_company_count: 11
- completed_enabled_count: 11
- missing_enabled_tickers: none
- baseline_created_or_refreshed_count: 0
- state_updated_company_count: 5
- events_appended_count: 5
- collection_scope: controller_open_web_only
- announcement_window_checked: T_and_T_plus_1
- announcement_query_window: 2026-07-10 to 2026-07-11
- trading_event_date_checked: 2026-07-10
- delayed_trading_event_catchup_window: 2026-07-09
- multi_agent_status: not_used_by_policy
- company_worker_queue: cancelled_by_policy
- open_web_policy: Codex open-web search only; no browser plugin, no external browser, no third-party web model, no social-search tool as discovery layer
- source_priority: official disclosure -> exchange/trading data -> credible media -> open-web observation pool

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

## Company task blocks
- 11 家 enabled 公司均按 watchlist 顺序建立独立任务块；每块均读取 baseline、state 和 events，并分别完成 CNINFO T/T+1、龙虎榜、大宗交易、Codex open-web 观察与状态判断。
- 未使用子智能体、worker、公司并行队列、外部浏览器、浏览器插件、第三方网页模型或社交搜索工具。
- CNINFO、深交所 ShowReport 和东方财富交易数据请求均成功；open-web 逐公司查询均成功，无阻断失败。
- 7 月 9 日天孚通信可信媒体线索触发 6 月 28 日官方 IR 延迟补录；其余观察池内容未越级写成正式事实。

## Per-company completion table
| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_no_new_material_change | controller_open_web_only | CNINFO no issuer hit 2026-07-10/11 | T_and_T_plus_1 | 2026-07-10 no_hit; 2026-07-09 catchup no_new | 2026-07-10 no_hit; 2026-07-09 catchup no_new | no_signal | no_change | InP/GaAs客户、订单、良率、出口许可仍缺硬证据 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed_no_new_material_change | controller_open_web_only | CNINFO no issuer hit 2026-07-10/11 | T_and_T_plus_1 | 2026-07-10 no_hit; 2026-07-09 catchup no_new | 2026-07-10 no_hit; 2026-07-09的22笔交易已记录 | no_signal | no_change | Low CTE/T-glass客户、订单、收入占比、毛利率仍待验证 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed_with_official_governance_announcement | controller_open_web_only | CNINFO T+1 hit: 9份换届/候选人/股东会文件；7/10减持结果已记录 | T_and_T_plus_1 | 2026-07-10 no_hit; 2026-07-09 catchup no_new | 2026-07-10 no_hit; 2026-07-09 catchup no_new | no_signal | updated_board_transition | 董事候选人尚待股东会；经营量化仍看光纤价格、订单、海外收入和毛利率 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed_with_block_trade | controller_open_web_only | CNINFO no issuer hit 2026-07-10/11 | T_and_T_plus_1 | 2026-07-10 no_hit; 2026-07-09 catchup no_new | 2026-07-10 hit: 12.64万股、1455.58万元、折价约1.20% | no_signal | updated_block_trade_continued | 减持归属、定增审核、客户、订单、收入占比、毛利率仍待验证 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed_with_open_web_observation_only | controller_open_web_only | CNINFO no issuer hit 2026-07-10/11 | T_and_T_plus_1 | 2026-07-10 no_hit; 2026-07-09 LHB already_recorded | 2026-07-10 no_hit; 2026-07-09 catchup no_new | searched | no_change | AWS/Coherent订单传闻未获确认；索尔思/AI PCB客户、订单、收入、毛利仍待验证 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed_with_block_trade | controller_open_web_only | CNINFO 7/10现金管理已记录；7/11 no_new | T_and_T_plus_1 | 2026-07-10 no_hit; 2026-07-09 catchup no_new | 2026-07-10 hit: 51.42万股、56256.83万元、平价 | no_signal | updated_large_flat_block_trade | 1.6T、硅光、物料锁定、毛利率仍待半年报或IR验证 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed_no_new_material_change | controller_open_web_only | CNINFO no issuer hit 2026-07-10/11 | T_and_T_plus_1 | 2026-07-10 no_hit; 2026-07-09 catchup no_new | 2026-07-10 no_hit; 2026-07-09 catchup no_new | no_signal | no_change | 200G EML/CW客户扩散、收入占比、毛利率仍待验证 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed_no_new_material_change | controller_open_web_only | CNINFO no issuer hit 2026-07-10/11 | T_and_T_plus_1 | 2026-07-10 no_hit; 2026-07-09 catchup no_new | 2026-07-10 no_hit; 2026-07-09 catchup no_new | no_signal | no_change | 高速连接器、液冷、客户订单、毛利率仍待验证 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed_with_official_ir_catchup | controller_open_web_only | CNINFO no issuer hit 2026-07-10/11; delayed official IR catchup 2026-06-28 | T_and_T_plus_1 | 2026-07-10 no_hit; 2026-07-09 catchup no_new | 2026-07-10 no_hit; 2026-07-09 catchup no_new | searched | updated_official_ir_catchup | 媒体更细颗粒信息仍待原文；泰国产能、CPO/1.6T收入与毛利率仍待量化 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed_with_open_web_observation_only | controller_open_web_only | CNINFO no issuer hit 2026-07-10/11 | T_and_T_plus_1 | 2026-07-10 no_hit; 2026-07-09 catchup no_new | 2026-07-10 no_hit; 2026-07-09 catchup no_new | searched | no_change | 英伟达/北美批量交付说法未获确认；H股、AIDC客户、订单、收入占比仍待验证 | not_used_by_policy |
| 000636.SZ | 风华高科 | 11 | completed_with_official_earnings_forecast | controller_open_web_only | CNINFO T+1 hit: 2026年半年度业绩预告 | T_and_T_plus_1 | 2026-07-10 no_hit; 2026-07-09 catchup no_new | 2026-07-10 no_hit; 2026-07-09 catchup no_new | no_signal | updated_earnings_forecast | 高端/AI MLCC收入、ASP、毛利率和现金流仍待半年报；英伟达传闻继续按官方否认 | not_used_by_policy |

## Reconciliation
- enabled_watchlist_count: 11
- completion_table_count: 11
- completed_enabled_count: 11
- missing_enabled_tickers: none
- duplicated_completion_tickers: none
- watchlist_order_preserved: yes
- baseline_pending_or_refresh_needed: none
- all_company_baseline_state_events_read: yes
- company_worker_queue: cancelled_by_policy
- multi_agent_status: not_used_by_policy
- watchlist_last_update_date: 2026-07-10 for all enabled rows
