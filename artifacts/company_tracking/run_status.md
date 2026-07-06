# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-07-06
- run_started_at_beijing: 2026-07-06 20:34:22 +08:00
- run_finished_at_beijing: 2026-07-06 20:44:18 +08:00
- automation_id: a-grok
- enabled_company_count: 11
- completed_company_count: 11
- baseline_created_or_refreshed_count: 0
- current_run_multi_agent_status: not_used_by_policy
- collection_scope: controller_open_web_only
- announcement_window_policy: T_and_T_plus_1 because run is after 20:00 Beijing time
- announcement_query_window: 2026-07-05 to 2026-07-07 (weekend catch-up plus T/T+1 hard gate)
- trading_event_date_checked: 2026-07-06
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
11. 000636.SZ 风华高科

## company_task_blocks

| ticker | name | baseline_read | announcements_checked | lhb_checked | block_trade_checked | open_web_checked | state_updated | events_appended |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | done | done | done | done | done | no_change | no |
| 603256.SH | 宏和科技 | done | done | done | done | done | no_change | no |
| 601869.SH | 长飞光纤 | done | done | done | done | done | no_change | no |
| 301511.SZ | 德福科技 | done | done | done | done | done | updated_private_placement_and_block_trade | yes |
| 002384.SZ | 东山精密 | done | done | done | done | done | no_change | no |
| 300308.SZ | 中际旭创 | done | done | done | done | done | updated_large_block_trades_and_rumor_response_observation | yes |
| 688498.SH | 源杰科技 | done | done | done | done | done | no_change | no |
| 688668.SH | 鼎通科技 | done | done | done | done | done | no_change | no |
| 300394.SZ | 天孚通信 | done | done | done | done | done | updated_governance_housekeeping | yes |
| 002851.SZ | 麦格米特 | done | done | done | done | done | no_change | no |
| 000636.SZ | 风华高科 | done | done | done | done | done | no_change | no |

## source_notes

- New official announcements appended: 德福科技 2026 年度向特定对象发行 A 股股票预案及募投项目文件组；天孚通信独立董事取得独立董事资格证书公告。
- New trading events appended: 德福科技 2026-07-06 50 万股折价大宗交易；中际旭创 2026-07-06 两笔平价大宗交易合计 7.788958 亿元。
- Open-web observation appended: 中际旭创通过证券时报报道口径回应核心物料封锁、光模块组装属性和康宁玻璃桥替代传闻；本轮按可信媒体/互动平台观察池处理，不升级为正式公告事实。
- CNINFO company-name and code queries were used for each enabled company across 2026-07-05 to 2026-07-07; issuer filtering by `secCode/secName/title` was applied to avoid code-query noise.
- Dragon-tiger and block-trade checks used Eastmoney/AKShare for full-market screening; SZSE ShowReport 1265 confirmed 2026-07-06 block trades for 301511.SZ and 300308.SZ.
- No sub-agents, company workers, external browsers, browser plugins, Grok, Gemini, X, or social search tools were used.

## per_company_completion_table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-05/06/07 | T_and_T_plus_1 | 2026-07-06 no_hit | 2026-07-06 no_hit | searched_no_new_operating_signal | no_change | InP/GaAs客户、订单、良率、6英寸量产、出口许可和利润兑现仍缺 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-05/06/07 | T_and_T_plus_1 | 2026-07-06 no_hit | 2026-07-06 no_hit | searched_no_new_signal_after_prior_reduction | no_change | 减持计划后续进展、Low CTE/T-glass订单、收入占比和毛利仍需硬证据 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-05/06/07 | T_and_T_plus_1 | 2026-07-06 no_hit | 2026-07-06 no_hit | searched_no_new_company_signal | no_change | 光纤价格、数据中心光纤/空芯/新型光纤收入拆分和毛利率仍需硬证据 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed_with_official_announcement_and_block_trade | controller_open_web_only | CNINFO 12 issuer hits 2026-07-06 | T_and_T_plus_1 | 2026-07-06 no_hit | 2026-07-06 1_hit | searched_official_and_block_trade_mirrors | updated_private_placement_and_block_trade | 定增尚待股东会、深交所审核和证监会注册；HVLP/RTF订单、收入占比和毛利仍缺 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-05/06/07 | T_and_T_plus_1 | 2026-07-06 no_hit | 2026-07-06 no_hit | searched_no_independent_new_operating_signal | no_change | AI PCB/索尔思客户、订单、毛利、现金流和项目审批仍需公告或财报验证 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed_with_block_trade_and_open_web_observation | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-05/06/07 | T_and_T_plus_1 | 2026-07-06 no_hit | 2026-07-06 2_hits | searched_credible_media_company_response_observation | updated_large_block_trades_and_rumor_response_observation | 1.6T/硅光/毛利率、核心物料供应和客户需求仍需官方或财报验证 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-05/06/07 | T_and_T_plus_1 | 2026-07-06 no_hit | 2026-07-06 no_hit | searched_no_new_signal | no_change | 200G EML、CW客户扩散、二期扩产资金和收入占比仍需硬证据 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-05/06/07 | T_and_T_plus_1 | 2026-07-06 no_hit | 2026-07-06 no_hit | searched_market_pages_no_new_signal | no_change | 可转债募资落地不等于高速通讯连接器/液冷订单、产能消化或毛利兑现 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed_with_low_materiality_governance_announcement | controller_open_web_only | CNINFO 1 issuer hit 2026-07-07 | T_and_T_plus_1 | 2026-07-06 no_hit | 2026-07-06 no_hit | searched_social_leads_only_no_confirmed_signal | updated_governance_housekeeping | 独董资格证书公告不改变CPO/FAU/ELS/1.6T订单、收入占比、客户和毛利率缺口 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-05/06/07 | T_and_T_plus_1 | 2026-07-06 no_hit | 2026-07-06 no_hit | searched_old_h_share_and_data_pages_no_new_signal | no_change | H股/AIDC电源仍需监管进度、具名客户、订单、收入占比和毛利率验证 | not_used_by_policy |
| 000636.SZ | 风华高科 | 11 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-05/06/07 | T_and_T_plus_1 | 2026-07-06 no_hit | 2026-07-06 no_hit | searched_market_pages_prior_risk_mirrors | no_change | AI算力/高端MLCC仍缺客户、订单、收入占比、ASP、毛利率；官方已否认英伟达直接供货和认证 | not_used_by_policy |

## reconciliation

- enabled_watchlist_count: 11
- completion_table_count: 11
- completed_enabled_tickers: 002428.SZ, 603256.SH, 601869.SH, 301511.SZ, 002384.SZ, 300308.SZ, 688498.SH, 688668.SH, 300394.SZ, 002851.SZ, 000636.SZ
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
- watchlist_last_update_date: 2026-07-06 for all enabled rows
- events_appended_count: 5
