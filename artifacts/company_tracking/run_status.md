# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-06-25
- run_started_at_beijing: 2026-06-25 20:34:28 +08:00
- run_finished_at_beijing: 2026-06-25 20:44:55 +08:00
- automation_id: a-grok
- enabled_company_count: 10
- completed_company_count: 10
- baseline_created_or_refreshed_count: 0
- current_run_multi_agent_status: not_used_by_policy
- collection_scope: controller_open_web_only
- announcement_window_policy: T_and_T_plus_1 because run is after 20:00 Beijing time
- announcement_query_window: 2026-06-25 to 2026-06-26
- trading_event_date_checked: 2026-06-25
- open_web_search_policy: Codex own open-web search only; observation layer, non-blocking
- browser_or_external_model_status: not_used_by_policy

## company_order_current_run

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

## company_task_blocks

| ticker | name | baseline_read | announcements_checked | lhb_checked | block_trade_checked | open_web_checked | state_updated | events_appended |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | done | done | done | done | done | updated_abnormal_volatility_and_dividend | yes |
| 603256.SH | 宏和科技 | done | done | done | done | done | updated_open_web_observation_only | yes |
| 601869.SH | 长飞光纤 | done | done | done | done | done | no_change | no |
| 301511.SZ | 德福科技 | done | done | done | done | done | updated_shareholder_reduction_and_block_trade | yes |
| 002384.SZ | 东山精密 | done | done | done | done | done | no_change | no |
| 300308.SZ | 中际旭创 | done | done | done | done | done | no_change | no |
| 688498.SH | 源杰科技 | done | done | done | done | done | no_change | no |
| 688668.SH | 鼎通科技 | done | done | done | done | done | updated_convertible_bond_allocation_lottery | yes |
| 300394.SZ | 天孚通信 | done | done | done | done | done | no_change | no |
| 002851.SZ | 麦格米特 | done | done | done | done | done | updated_h_share_shareholder_approval | yes |

## source_notes

- New official announcements appended: 云南锗业股票交易异常波动公告和权益分派实施公告；德福科技持股 5% 以上股东权益变动公告；鼎通科技可转债中签率/配售结果和中签结果公告；麦格米特 H 股股东会决议公告。
- New trading events appended: 德福科技 2026-06-25 1 笔大宗交易。
- Open-web observation appended: 宏和科技 80 亿元项目预计高端电子布设计产能约 1.5 亿米的投资者问答转载，标记 observation_only。
- No tracked-company dragon-tiger list events were found for 2026-06-25.
- No baseline was created or refreshed.
- CNINFO company-name and code queries were both used; issuer filtering by `secCode/secName` was applied to avoid code-query noise.
- No sub-agents, company workers, external browsers, browser plugins, Grok, Gemini, X, or social search tools were used.

## per_company_completion_table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_with_official_announcements | controller_open_web_only | CNINFO 2 issuer hits 2026-06-25/26 | T_and_T_plus_1 | 2026-06-25 no_hit | 2026-06-25 no_hit | searched_official_mirrors_no_independent_signal | updated_abnormal_volatility_and_dividend | InP/GaAs客户、订单、良率、6英寸量产、出口许可和利润兑现仍缺 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed_with_open_web_observation | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-25/26 | T_and_T_plus_1 | 2026-06-25 no_hit | 2026-06-25 no_hit | searched_observation_added | updated_open_web_observation_only | 80亿项目和1.5亿米产能需回到H股资料/公告复核，Low CTE/T-glass订单和毛利仍缺 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-25/26 | T_and_T_plus_1 | 2026-06-25 no_hit | 2026-06-25 no_hit | searched_market_pages_no_new_signal | no_change | AI数据中心光纤价格波动仍需业务结构、订单、收入拆分和毛利率确认 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed_with_official_announcement_and_block_trade | controller_open_web_only | CNINFO 1 issuer hit 2026-06-25 | T_and_T_plus_1 | 2026-06-25 no_hit | 2026-06-25 1_hit | searched_no_new_beyond_hard_events | updated_shareholder_reduction_and_block_trade | 6/25大宗归属和剩余额度待后续减持进展公告，HVLP/RTF订单和毛利仍缺 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-25/26 | T_and_T_plus_1 | 2026-06-25 no_hit | 2026-06-25 no_hit | searched_old_reports_no_new_signal | no_change | AI PCB/光模块客户、订单、毛利和索尔思项目仍需公告或财报验证 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-25/26 | T_and_T_plus_1 | 2026-06-25 no_hit | 2026-06-25 no_hit | searched_market_chatter_no_hard_signal | no_change | 1.6T/硅光/毛利率和上游物料紧张仍需官方或财报验证 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-25/26 | T_and_T_plus_1 | 2026-06-25 no_hit | 2026-06-25 no_hit | searched_old_reports_no_new_signal | no_change | 200G EML、CW客户、二期扩产和收入占比仍需硬证据 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed_with_official_announcements | controller_open_web_only | CNINFO 2 issuer hits 2026-06-25/26 | T_and_T_plus_1 | 2026-06-25 no_hit | 2026-06-25 no_hit | searched_convertible_bond_mirrors | updated_convertible_bond_allocation_lottery | 融资推进不等于高速连接器/液冷客户订单、产能消化或毛利兑现 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-25/26 | T_and_T_plus_1 | 2026-06-25 no_hit | 2026-06-25 no_hit | searched_market_pages_no_new_signal | no_change | 1.6T/CPO/FAU/ELS订单、收入占比、物料缺口和H股进展仍需硬证据 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed_with_official_announcement | controller_open_web_only | CNINFO 2 issuer hits 2026-06-26 | T_and_T_plus_1 | 2026-06-25 no_hit | 2026-06-25 no_hit | searched_h_share_mirrors_no_new_beyond_official | updated_h_share_shareholder_approval | H股仍需监管/交易所程序，AI电源客户、订单、收入占比和毛利率仍缺 | not_used_by_policy |

## reconciliation

- enabled_watchlist_count: 10
- completion_table_count: 10
- completed_enabled_tickers: 002428.SZ, 603256.SH, 601869.SH, 301511.SZ, 002384.SZ, 300308.SZ, 688498.SH, 688668.SH, 300394.SZ, 002851.SZ
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
- watchlist_last_update_date: 2026-06-25 for all enabled rows
- events_appended_count: 8
