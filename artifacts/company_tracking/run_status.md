# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-06-26
- run_started_at_beijing: 2026-06-26 20:35:03 +08:00
- run_finished_at_beijing: 2026-06-26 20:46:35 +08:00
- automation_id: a-grok
- enabled_company_count: 10
- completed_company_count: 10
- baseline_created_or_refreshed_count: 0
- current_run_multi_agent_status: not_used_by_policy
- collection_scope: controller_open_web_only
- announcement_window_policy: T_and_T_plus_1 because run is after 20:00 Beijing time
- announcement_query_window: 2026-06-26 to 2026-06-27
- trading_event_date_checked: 2026-06-26
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
| 002428.SZ | 云南锗业 | done | done_already_recorded | done | done | done | no_change | no |
| 603256.SH | 宏和科技 | done | done | done | done | done | updated_abnormal_volatility_reduction_lhb | yes |
| 601869.SH | 长飞光纤 | done | done | done | done | done | no_change | no |
| 301511.SZ | 德福科技 | done | done | done | done | done | updated_continued_block_trade | yes |
| 002384.SZ | 东山精密 | done | done | done | done | done | no_change | no |
| 300308.SZ | 中际旭创 | done | done | done | done | done | updated_block_trade_observation | yes |
| 688498.SH | 源杰科技 | done | done | done | done | done | no_change | no |
| 688668.SH | 鼎通科技 | done | done_already_recorded | done | done | done | no_change | no |
| 300394.SZ | 天孚通信 | done | done | done | done | done | no_change | no |
| 002851.SZ | 麦格米特 | done | done | done | done | done | updated_h_share_application_filing | yes |

## source_notes

- New official announcements appended: 宏和科技股票交易异常波动/控股股东及实际控制人回复/股东调减拟减持数量；麦格米特 H 股递表及申请资料刊发。
- New trading events appended: 宏和科技 2026-06-26 龙虎榜；德福科技 2026-06-26 1 笔大宗交易；中际旭创 2026-06-26 2 笔大宗交易。
- Already recorded in previous T+1 window and not duplicated: 云南锗业 2025 年度权益分派实施公告；鼎通科技可转债网上中签结果公告。
- No independent open-web observation was promoted this run; useful search results were official announcements, official mirrors, trading data pages, old reports, or market pages.
- CNINFO company-name and code queries were both used; issuer filtering by `secCode/secName` was applied to avoid code-query noise.
- Dragon-tiger and block-trade checks used market/trading data filtered by enabled tickers; trading events remain trading-structure evidence, not business-quality proof.
- No sub-agents, company workers, external browsers, browser plugins, Grok, Gemini, X, or social search tools were used.

## per_company_completion_table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_no_new_material_change | controller_open_web_only | CNINFO 1 issuer hit 2026-06-26 already_recorded | T_and_T_plus_1 | 2026-06-26 no_hit | 2026-06-26 no_hit | searched_official_mirror_no_new_signal | no_change | InP/GaAs客户、订单、良率、6英寸量产、出口许可和利润兑现仍缺 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed_with_official_announcements_and_lhb | controller_open_web_only | CNINFO 3 issuer hits 2026-06-27 | T_and_T_plus_1 | 2026-06-26 1_hit | 2026-06-26 no_hit | searched_official_trading_signal | updated_abnormal_volatility_reduction_lhb | 估值极端化、减持执行、H股/扩产资金链、Low CTE/T-glass订单和毛利仍需复核 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-26/27 | T_and_T_plus_1 | 2026-06-26 no_hit | 2026-06-26 no_hit | searched_market_pages_no_new_signal | no_change | AI数据中心光纤价格、订单、收入拆分和毛利率仍需硬证据 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed_with_block_trade | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-26/27 | T_and_T_plus_1 | 2026-06-26 no_hit | 2026-06-26 1_hit | searched_trading_mirrors_no_new_operating_signal | updated_continued_block_trade | 6/26大宗归属和剩余额度待后续减持进展公告，HVLP/RTF订单和毛利仍缺 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-26/27 | T_and_T_plus_1 | 2026-06-26 no_hit | 2026-06-26 no_hit | searched_old_reports_no_new_signal | no_change | AI PCB/光模块客户、订单、毛利和索尔思项目仍需公告或财报验证 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed_with_block_trade | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-26/27 | T_and_T_plus_1 | 2026-06-26 no_hit | 2026-06-26 2_hit | searched_market_pages_no_new_operating_signal | updated_block_trade_observation | 1.6T/硅光/毛利率和上游物料紧张仍需官方或财报验证 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-26/27 | T_and_T_plus_1 | 2026-06-26 no_hit | 2026-06-26 no_hit | searched_old_reports_no_new_signal | no_change | 200G EML、CW客户、二期扩产和收入占比仍需硬证据 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed_no_new_material_change | controller_open_web_only | CNINFO 1 issuer hit 2026-06-26 already_recorded | T_and_T_plus_1 | 2026-06-26 no_hit | 2026-06-26 no_hit | searched_convertible_bond_mirrors_no_new_beyond_recorded | no_change | 可转债发行不等于高速连接器/液冷订单、产能消化或毛利兑现 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-26/27 | T_and_T_plus_1 | 2026-06-26 no_hit | 2026-06-26 no_hit | searched_market_pages_no_new_signal | no_change | 1.6T/CPO/FAU/ELS订单、收入占比、物料缺口和H股进展仍需硬证据 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed_with_official_announcement | controller_open_web_only | CNINFO 3 issuer hits 2026-06-26/27, 1 new H-share filing | T_and_T_plus_1 | 2026-06-26 no_hit | 2026-06-26 no_hit | searched_h_share_mirrors_no_new_beyond_official | updated_h_share_application_filing | H股仍需监管/交易所程序，AI电源客户、订单、收入占比和毛利率仍缺 | not_used_by_policy |

## reconciliation

- enabled_watchlist_count: 10
- completion_table_count: 10
- completed_enabled_tickers: 002428.SZ, 603256.SH, 601869.SH, 301511.SZ, 002384.SZ, 300308.SZ, 688498.SH, 688668.SH, 300394.SZ, 002851.SZ
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
- watchlist_last_update_date: 2026-06-26 for all enabled rows
- events_appended_count: 6
