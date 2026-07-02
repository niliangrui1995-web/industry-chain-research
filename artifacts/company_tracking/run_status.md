# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-07-02
- run_started_at_beijing: 2026-07-02 22:44:41 +08:00
- run_finished_at_beijing: 2026-07-02 22:54:28 +08:00
- automation_id: a-grok
- enabled_company_count: 10
- completed_company_count: 10
- baseline_created_or_refreshed_count: 0
- current_run_multi_agent_status: not_used_by_policy
- collection_scope: controller_open_web_only
- announcement_window_policy: T_and_T_plus_1 because run is after 20:00 Beijing time
- announcement_query_window: 2026-07-02 to 2026-07-03
- catch_up_check_window: 2026-07-01 to 2026-07-03 because workbook last_update_date was 2026-06-30
- trading_event_date_checked: 2026-07-01 and 2026-07-02
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
| 002428.SZ | 云南锗业 | done | done | done | done | done | no_change | no |
| 603256.SH | 宏和科技 | done | done | done | done | done | no_change | no |
| 601869.SH | 长飞光纤 | done | done | done | done | done | no_change_already_recorded | no |
| 301511.SZ | 德福科技 | done | done | done | done | done | updated_buyback_progress_and_continued_block_trades | yes |
| 002384.SZ | 东山精密 | done | done | done | done | done | updated_dragon_tiger_drawdown | yes |
| 300308.SZ | 中际旭创 | done | done | done | done | done | updated_two_day_institutional_block_trades | yes |
| 688498.SH | 源杰科技 | done | done | done | done | done | no_change_already_recorded | no |
| 688668.SH | 鼎通科技 | done | done | done | done | done | no_change_already_recorded | no |
| 300394.SZ | 天孚通信 | done | done | done | done | done | no_change | no |
| 002851.SZ | 麦格米特 | done | done | done | done | done | updated_guarantee_and_cash_management | yes |

## source_notes

- New official announcements appended: 德福科技回购股份进展；麦格米特对子公司担保进展和闲置募集资金现金管理。
- New trading events appended: 德福科技 2026-07-01/02 共 3 笔大宗交易；东山精密 2026-07-02 龙虎榜；中际旭创 2026-07-01/02 共 2 笔大宗交易。
- 长飞光纤、源杰科技、鼎通科技的 2026-07-01 公告已在上一轮 T+1 窗口落账，本轮复核不重复追加。
- No independent open-web observation was promoted this run; useful search results were official announcements, trading data pages, old reports, market pages, or official mirrors.
- CNINFO company-name and code queries were both used; issuer filtering by `secCode/secName/title` was applied to avoid code-query noise.
- Dragon-tiger and block-trade checks used exchange pages where available and Eastmoney trading data for cross-check; trading events remain trading-structure evidence, not business-quality proof.
- No sub-agents, company workers, external browsers, browser plugins, Grok, Gemini, X, or social search tools were used.

## per_company_completion_table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-01/2026-07-03 | T_and_T_plus_1 | 2026-07-01/02 no_hit | 2026-07-01/02 no_hit | no_signal | no_change | 锗资源、InP/GaAs客户、订单、良率、6英寸量产、出口许可和利润兑现仍缺 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-01/2026-07-03 | T_and_T_plus_1 | 2026-07-01/02 no_hit | 2026-07-01/02 no_hit | no_signal | no_change | 高估值、减持执行、H股/扩产资金链、Low CTE/T-glass订单和毛利仍需复核 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed_no_new_material_change | controller_open_web_only | CNINFO 2026-07-01 2 hits already_recorded; no new 2026-07-02/03 | T_and_T_plus_1 | 2026-07-01/02 no_hit | 2026-07-01/02 no_hit | searched_old_official_mirror_no_new_ai_signal | no_change_already_recorded | 光纤价格、光互联组件、海外收入、空芯/新型光纤收入拆分和毛利率仍需硬证据 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed_with_official_announcement_and_block_trade | controller_open_web_only | CNINFO 1 issuer hit 2026-07-02 | T_and_T_plus_1 | 2026-07-01/02 no_hit | 2026-07-01 2_hits; 2026-07-02 1_hit | searched_official_trading_mirror_no_customer_revenue_signal | updated_buyback_progress_and_continued_block_trades | 大宗交易归属和剩余额度待后续减持进展公告，HVLP/RTF订单和毛利仍缺 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed_with_dragon_tiger | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-01/2026-07-03 | T_and_T_plus_1 | 2026-07-02 1_hit | 2026-07-01/02 no_hit | searched_lhb_mirror_no_new_operating_signal | updated_dragon_tiger_drawdown | AI PCB/索尔思客户、订单、毛利、现金流和项目审批仍需公告或财报验证 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed_with_block_trade | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-01/2026-07-03 | T_and_T_plus_1 | 2026-07-01/02 no_hit | 2026-07-01 1_hit; 2026-07-02 1_hit | searched_block_trade_mirror_no_new_operating_signal | updated_two_day_institutional_block_trades | 1.6T/硅光/毛利率和上游物料紧张仍需官方或财报验证 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed_no_new_material_change | controller_open_web_only | CNINFO 2026-07-01 1 hit already_recorded; no new 2026-07-02/03 | T_and_T_plus_1 | 2026-07-01/02 no_hit | 2026-07-01/02 no_hit | searched_old_official_risk_warning_no_new_order_signal | no_change_already_recorded | 200G EML、CW客户扩散、二期扩产资金和收入占比仍需硬证据 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed_no_new_material_change | controller_open_web_only | CNINFO 2026-07-01 5 hits already_recorded; no new 2026-07-02/03 | T_and_T_plus_1 | 2026-07-01/02 no_hit | 2026-07-01/02 no_hit | searched_old_fund_arrangement_no_new_customer_signal | no_change_already_recorded | 募资落地不等于高速通讯连接器/液冷订单、产能消化或毛利兑现 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-07-01/2026-07-03 | T_and_T_plus_1 | 2026-07-01/02 no_hit | 2026-07-01/02 no_hit | no_signal | no_change | 合资公司注册不等于CPO/FAU/ELS/1.6T订单、收入占比、客户和毛利率兑现 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed_with_official_announcements | controller_open_web_only | CNINFO 2 issuer hits 2026-07-03 | T_and_T_plus_1 | 2026-07-01/02 no_hit | 2026-07-01/02 no_hit | searched_official_mirror_no_new_order_signal | updated_guarantee_and_cash_management | H股/AIDC电源仍需监管进度、具名客户、订单、收入占比和毛利率验证 | not_used_by_policy |

## reconciliation

- enabled_watchlist_count: 10
- completion_table_count: 10
- completed_enabled_tickers: 002428.SZ, 603256.SH, 601869.SH, 301511.SZ, 002384.SZ, 300308.SZ, 688498.SH, 688668.SH, 300394.SZ, 002851.SZ
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
- watchlist_last_update_date: 2026-07-02 for all enabled rows
- events_appended_count: 8

## ad_hoc_baseline_supplement_2026-07-02_000636

- supplement_started_at_beijing: 2026-07-02 23:06:11 +08:00
- supplement_finished_at_beijing: 2026-07-02 23:10:00 +08:00
- automation_id: a-grok
- scope: user_requested_single_company_add_and_full_baseline
- ticker: 000636.SZ
- name: 风华高科
- watchlist_writeback: enabled=Y, baseline_status=done, last_baseline_date=2026-07-02, last_update_date=2026-07-02
- baseline_created_or_refreshed_count: 1
- collection_scope: controller_open_web_only
- announcement_window_checked: T_and_T_plus_1
- multi_agent_status: not_used_by_policy
- browser_or_external_model_status: not_used_by_policy
- enabled_watchlist_count_after_addition: 11
- baseline_pending_or_refresh_needed_after_supplement: none

### ad_hoc_company_task_block

| ticker | name | baseline_read | announcements_checked | lhb_checked | block_trade_checked | open_web_checked | state_updated | events_appended |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 000636.SZ | 风华高科 | existing_minimum_state_read | done | done | done | done | baseline_created_and_state_rebuilt | yes |

### ad_hoc_completion_table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 000636.SZ | 风华高科 | ad_hoc_1 | completed_with_baseline_created | controller_open_web_only | company_site/CNINFO/SZSE official window checked; no new 2026-07-02/03 issuer announcement | T_and_T_plus_1 | 2026-07-02 no_hit; recent 2026-06-25/29/30 hits recorded as baseline | 2026-07-02 2_hits | searched_useful_trading_mirror_and_official_risk_notice | baseline_created_and_state_rebuilt | AI算力/高端MLCC仍缺客户、订单、收入占比、ASP、毛利率；官方已否认英伟达直接供货和认证 | not_used_by_policy |

### ad_hoc_source_notes

- Official baseline sources: company website, 2025 annual report, 2026 Q1 report, 2025 annual results briefing, 2026-06-18 abnormal volatility announcement, 2026-06-30 severe abnormal volatility and risk notice.
- Trading data: 2026-07-02 two block trades at 66.96 yuan, total 227,000 shares and 15.20 million yuan, both institution-to-institution; 2026-07-02 no new dragon-tiger list hit found, recent 2026-06-25/29/30 hits recorded as baseline.
- Evidence boundary: official disclosures support high-end MLCC and AI-compute application tracking, but do not confirm NVIDIA direct supply/certification, named AI server orders, revenue share, ASP, or margin realization.
