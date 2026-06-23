# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-06-23
- run_started_at_beijing: 2026-06-23 20:32:19 +08:00
- run_finished_at_beijing: 2026-06-23 20:42:58 +08:00
- automation_id: a-grok
- enabled_company_count: 10
- completed_company_count: 10
- baseline_created_or_refreshed_count: 0
- current_run_multi_agent_status: not_used_by_policy
- collection_scope: controller_open_web_only
- announcement_window_policy: T_and_T_plus_1 because run is after 20:00 Beijing time
- announcement_query_window: 2026-06-23 to 2026-06-24
- trading_event_date_checked: 2026-06-23
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
| 603256.SH | 宏和科技 | done | done | done | done | done | no_change_duplicate_already_logged | no |
| 601869.SH | 长飞光纤 | done | done | done | done | done | updated_abnormal_volatility_and_lhb | yes |
| 301511.SZ | 德福科技 | done | done | done | done | done | updated_block_trade | yes |
| 002384.SZ | 东山精密 | done | done | done | done | done | no_change | no |
| 300308.SZ | 中际旭创 | done | done | done | done | done | updated_block_trade | yes |
| 688498.SH | 源杰科技 | done | done | done | done | done | no_change_duplicate_already_logged | no |
| 688668.SH | 鼎通科技 | done | done | done | done | done | updated_convertible_bond_issue_reminder | yes |
| 300394.SZ | 天孚通信 | done | done | done | done | done | updated_block_trade_small | yes |
| 002851.SZ | 麦格米特 | done | done | done | done | done | no_change | no |

## source_notes

- New official announcements appended: 长飞光纤股票交易异常波动公告、鼎通科技可转债发行提示性公告。
- Duplicate official announcements not re-appended: 宏和科技 2026-06-23 发明专利公告、源杰科技 2026-06-23 股票交易风险提示公告 were already captured in the previous T+1 run.
- New trading events appended: 长飞光纤 1 条龙虎榜；德福科技 1 笔大宗交易；中际旭创 4 笔大宗交易；天孚通信 1 笔大宗交易。
- No independent high-value open-web observation was promoted. Open-web results were mostly official mirrors, market pages, prior-run material, or weak observations.
- No baseline was created or refreshed.
- CNINFO company-name query and code query were both used; code-query noise was filtered by issuer `secCode/secName`, especially for 麦格米特.
- No sub-agents, company workers, external browsers, browser plugins, Grok, Gemini, X, or social search tools were used.

## per_company_completion_table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-23/24 | T_and_T_plus_1 | 2026-06-23 no_hit | 2026-06-23 no_hit | searched_old_market_pages_no_new_signal | no_change | 光纤级四氯化锗价格传导、InP订单、出口许可和质押/减持仍需后续披露验证 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed_no_new_material_change | controller_open_web_only | CNINFO issuer hit patent 2026-06-23 already_logged | T_and_T_plus_1 | 2026-06-23 no_hit | 2026-06-23 no_hit | searched_duplicate_patent_mirrors | no_change_duplicate_already_logged | 发明专利不等于Low CTE/T-glass订单、价格或毛利兑现 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed_with_official_announcement_and_lhb | controller_open_web_only | CNINFO issuer hit abnormal volatility 2026-06-24 | T_and_T_plus_1 | 2026-06-23 1_hit | 2026-06-23 no_hit | searched_useful_lhb_and_market_mirrors | updated_abnormal_volatility_and_lhb | AI数据中心光纤价格波动仍需业务结构、订单、收入拆分和毛利率确认 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed_with_material_trading_event | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-23/24 | T_and_T_plus_1 | 2026-06-23 no_hit | 2026-06-23 1_hit | searched_market_pages_no_new_hard_signal | updated_block_trade | 同卖方席位大宗归属、减持进展和HVLP/RTF商业化仍待官方验证 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-23/24 | T_and_T_plus_1 | 2026-06-23 no_hit | 2026-06-23 no_hit | searched_old_source_photonics_mirrors_no_new_signal | no_change | 索尔思项目审批、资金安排、客户订单、毛利和良率量化仍缺 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed_with_material_trading_event | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-23/24 | T_and_T_plus_1 | 2026-06-23 no_hit | 2026-06-23 4_hit | searched_market_page_confirms_block_trade | updated_block_trade | 高价平价大宗仅为交易结构，不证明1.6T/硅光/毛利率新增兑现 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed_no_new_material_change | controller_open_web_only | CNINFO issuer hit risk warning 2026-06-23 already_logged | T_and_T_plus_1 | 2026-06-23 no_hit | 2026-06-23 no_hit | searched_duplicate_risk_warning_mirrors | no_change_duplicate_already_logged | 估值风险已入账；200G EML、CW客户和二期扩产仍需硬证据 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed_with_official_announcement | controller_open_web_only | CNINFO issuer hit convertible-bond issue reminder 2026-06-24 | T_and_T_plus_1 | 2026-06-23 no_hit | 2026-06-23 no_hit | searched_convertible_bond_secondary_mirrors | updated_convertible_bond_issue_reminder | 募资执行不等于高速连接器/液冷客户订单、产能消化或毛利兑现 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed_with_material_trading_event | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-23/24 | T_and_T_plus_1 | 2026-06-23 no_hit | 2026-06-23 1_hit | searched_old_market_pages_no_new_signal | updated_block_trade_small | 小额平价大宗不证明1.6T/CPO/FAU/ELS订单、收入占比、H股进展 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed_no_new_material_change | controller_open_web_only | CNINFO name no hit; code-query noise filtered 2026-06-23/24 | T_and_T_plus_1 | 2026-06-23 no_hit | 2026-06-23 no_hit | searched_old_ir_mirrors_no_new_signal | no_change | AI电源客户、订单、收入占比、毛利率、平台归属和交付节奏仍未量化 | not_used_by_policy |

## reconciliation

- enabled_watchlist_count: 10
- completion_table_count: 10
- completed_enabled_tickers: 002428.SZ, 603256.SH, 601869.SH, 301511.SZ, 002384.SZ, 300308.SZ, 688498.SH, 688668.SH, 300394.SZ, 002851.SZ
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
- watchlist_last_update_date: 2026-06-23 for all enabled rows
- disabled_or_not_enabled_in_workbook: 002222.SZ, 300476.SZ, 603738.SH
