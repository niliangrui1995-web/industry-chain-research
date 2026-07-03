# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-07-03
- run_started_at_beijing: 2026-07-03 22:06:41 +08:00
- run_finished_at_beijing: 2026-07-03 22:23:33 +08:00
- automation_id: a-grok
- enabled_company_count: 11
- completed_company_count: 11
- baseline_created_or_refreshed_count: 0
- current_run_multi_agent_status: not_used_by_policy
- collection_scope: controller_open_web_only
- announcement_window_policy: T_and_T_plus_1 because run is after 20:00 Beijing time
- announcement_query_window: 2026-07-03 to 2026-07-04
- trading_event_date_checked: 2026-07-03
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
| 002428.SZ | 云南锗业 | done | done | done | done | done | updated_management_change | yes |
| 603256.SH | 宏和科技 | done | done | done | done | done | updated_reduction_execution_and_block_trades | yes |
| 601869.SH | 长飞光纤 | done | done | done | done | done | no_change | no |
| 301511.SZ | 德福科技 | done | done | done | done | done | updated_continued_block_trade | yes |
| 002384.SZ | 东山精密 | done | done | done | done | done | updated_high_amplitude_lhb | yes |
| 300308.SZ | 中际旭创 | done | done | done | done | done | updated_large_block_trades | yes |
| 688498.SH | 源杰科技 | done | done | done | done | done | no_change | no |
| 688668.SH | 鼎通科技 | done | done | done | done | done | no_change | no |
| 300394.SZ | 天孚通信 | done | done | done | done | done | no_change | no |
| 002851.SZ | 麦格米特 | done | done | done | done | done | no_change_already_recorded | no |
| 000636.SZ | 风华高科 | done | done | done | done | done | updated_dividend_calendar | yes |

## source_notes

- New official announcements appended: 云南锗业高管离任；宏和科技股东减持进展暨权益变动触及 1% 整数倍；风华高科 2025 年度分红派息实施。
- New trading events appended: 宏和科技 2026-07-03 折价大宗交易及减持执行；德福科技 2026-07-03 50 万股同卖方席位大宗交易；东山精密 2026-07-03 龙虎榜；中际旭创 2026-07-03 两笔平价大宗交易。
- 麦格米特 2026-07-03 两条公告已在上一轮 T+1 窗口落账，本轮复核不重复追加。
- No independent open-web observation was promoted as a formal fact this run; useful search results were official announcements, trading data pages, credible media mirrors, old reports, market pages, or official mirrors.
- CNINFO company-name and code queries were both used; issuer filtering by `secCode/secName/title` was applied to avoid code-query noise.
- Dragon-tiger and block-trade checks used SZSE direct pages where available and Eastmoney trading data for cross-check; trading events remain trading-structure evidence, not business-quality proof.
- No sub-agents, company workers, external browsers, browser plugins, Grok, Gemini, X, or social search tools were used.

## per_company_completion_table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_with_official_announcement | controller_open_web_only | CNINFO 1 issuer hit 2026-07-04 | T_and_T_plus_1 | 2026-07-03 no_hit | 2026-07-03 no_hit | searched_no_new_operating_signal | updated_management_change | InP/GaAs客户、订单、良率、6英寸量产、出口许可和利润兑现仍缺 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed_with_official_announcement_and_block_trade | controller_open_web_only | CNINFO 1 issuer hit 2026-07-04 | T_and_T_plus_1 | 2026-07-03 no_hit | 2026-07-03 30_hits | searched_credible_media_duplicate_official_reduction | updated_reduction_execution_and_block_trades | 减持计划尚未完毕；Low CTE/T-glass订单、收入占比和毛利仍需硬证据 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-03/04 | T_and_T_plus_1 | 2026-07-03 no_hit | 2026-07-03 no_hit | searched_sector_pullback_media_no_new_company_signal | no_change | 光纤价格、光互联组件、海外收入、空芯/新型光纤收入拆分和毛利率仍需硬证据 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed_with_block_trade | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-03/04 | T_and_T_plus_1 | 2026-07-03 no_hit | 2026-07-03 1_hit | searched_trading_page_no_new_customer_revenue_signal | updated_continued_block_trade | 大宗交易归属和剩余额度待后续减持进展公告，HVLP/RTF订单和毛利仍缺 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed_with_dragon_tiger | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-03/04 | T_and_T_plus_1 | 2026-07-03 1_hit | 2026-07-03 no_hit | searched_no_independent_new_operating_signal | updated_high_amplitude_lhb | AI PCB/索尔思客户、订单、毛利、现金流和项目审批仍需公告或财报验证 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed_with_block_trade | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-03/04 | T_and_T_plus_1 | 2026-07-03 no_hit | 2026-07-03 2_hits | searched_block_trade_mirror_no_new_operating_signal | updated_large_block_trades | 1.6T/硅光/毛利率和上游物料紧张仍需官方或财报验证 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-03/04 | T_and_T_plus_1 | 2026-07-03 no_hit | 2026-07-03 no_hit | searched_old_order_or_risk_items_no_new_signal | no_change | 200G EML、CW客户扩散、二期扩产资金和收入占比仍需硬证据 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-03/04 | T_and_T_plus_1 | 2026-07-03 no_hit | 2026-07-03 no_hit | searched_old_cb_mirror_no_new_customer_signal | no_change | 可转债募资落地不等于高速通讯连接器/液冷订单、产能消化或毛利兑现 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-03/04 | T_and_T_plus_1 | 2026-07-03 no_hit | 2026-07-03 no_hit | searched_quote_old_block_no_new_signal | no_change | 合资公司注册不等于CPO/FAU/ELS/1.6T订单、收入占比、客户和毛利率兑现 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed_no_new_material_change_already_recorded | controller_open_web_only | CNINFO 2026-07-03 2 hits already_recorded | T_and_T_plus_1 | 2026-07-03 no_hit | 2026-07-03 no_hit | searched_official_mirror_already_recorded | no_change_already_recorded | H股/AIDC电源仍需监管进度、具名客户、订单、收入占比和毛利率验证 | not_used_by_policy |
| 000636.SZ | 风华高科 | 11 | completed_with_official_announcement | controller_open_web_only | CNINFO 1 issuer hit 2026-07-03 | T_and_T_plus_1 | 2026-07-03 no_hit | 2026-07-03 no_hit | searched_dividend_and_prior_block_mirrors | updated_dividend_calendar | AI算力/高端MLCC仍缺客户、订单、收入占比、ASP、毛利率；官方已否认英伟达直接供货和认证 | not_used_by_policy |

## reconciliation

- enabled_watchlist_count: 11
- completion_table_count: 11
- completed_enabled_tickers: 002428.SZ, 603256.SH, 601869.SH, 301511.SZ, 002384.SZ, 300308.SZ, 688498.SH, 688668.SH, 300394.SZ, 002851.SZ, 000636.SZ
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
- watchlist_last_update_date: 2026-07-03 for all enabled rows
- events_appended_count: 6
