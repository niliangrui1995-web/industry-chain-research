# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-06-18
- run_started_at_beijing: 2026-06-18 20:32:18 +08:00
- run_finished_at_beijing: 2026-06-18 20:41:49 +08:00
- automation_id: a-grok
- enabled_company_count: 10
- completed_company_count: 10
- baseline_created_or_refreshed_count: 0
- current_run_multi_agent_status: not_used_by_policy
- collection_scope: controller_open_web_only
- announcement_window_policy: T_and_T_plus_1 because run is after 20:00 Beijing time
- announcement_query_window: 2026-06-18 to 2026-06-19
- trading_event_date_checked: 2026-06-18
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
| 002428.SZ | 云南锗业 | done | done | done | done | done | yes | yes |
| 603256.SH | 宏和科技 | done | done | done | done | done | no_change | no |
| 601869.SH | 长飞光纤 | done | done | done | done | done | no_change | no |
| 301511.SZ | 德福科技 | done | done | done | done | done | yes | yes |
| 002384.SZ | 东山精密 | done | done | done | done | done | yes | yes |
| 300308.SZ | 中际旭创 | done | done | done | done | done | yes | yes |
| 688498.SH | 源杰科技 | done | done | done | done | done | no_change | no |
| 688668.SH | 鼎通科技 | done | done | done | done | done | no_change | no |
| 300394.SZ | 天孚通信 | done | done | done | done | done | no_change | no |
| 002851.SZ | 麦格米特 | done | done | done | done | done | no_change | no |

## source_notes

- New official announcements appended: none. CNINFO 2026-06-18 hits for 603256.SH and 002851.SZ were already entered in the prior T+1 run; no 2026-06-19 new announcements found.
- New trading events appended: 300308.SZ 2026-06-18 block trade; 301511.SZ 2026-06-18 block trade.
- New open-web observations appended: 002428.SZ investor-interaction price/supply answer mirror; 002384.SZ Source Photonics transaction/ODI/funding Q&A mirror.
- No baseline was created or refreshed.
- CNINFO company-name query and code query were both used; code-only query can miss announcements.
- SZSE official ShowReport confirmed 300308.SZ and 301511.SZ block trades; Eastmoney was used as secondary trading-data cross-check.
- No sub-agents, company workers, external browsers, browser plugins, Grok, Gemini, X, or social search tools were used.

## per_company_completion_table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_with_ir_observation | controller_open_web_only | CNINFO stock/name/code no_hit 2026-06-18/19 | T_and_T_plus_1 | 2026-06-18 no_hit | 2026-06-18 no_hit | searched_ir_price_answer_observation | ir_observation_appended | 光纤级四氯化锗价格传导仍需定期报告和毛利率验证 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed_no_new_material_change | controller_open_web_only | CNINFO hit prior 2026-06-18 abnormal/risk already_in_ledger; no 2026-06-19 new | T_and_T_plus_1 | 2026-06-18 no_hit | 2026-06-18 no_hit | searched_official_mirrors_no_extra_fact | no_change | Low CTE/T-glass 订单、价格、客户认证和 H 股/扩产实质进展仍缺新增硬证据 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed_no_new_material_change | controller_open_web_only | CNINFO stock/name/code no_hit 2026-06-18/19 | T_and_T_plus_1 | 2026-06-18 no_hit | 2026-06-18 no_hit | searched_company_site_old_items_no_new_signal | no_change | 数据中心光纤订单、运营商集采、价格/毛利新增证据仍缺 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed_with_block_trade | controller_open_web_only | CNINFO stock/name/code no_hit 2026-06-18/19 | T_and_T_plus_1 | 2026-06-18 no_hit | 2026-06-18 hit_1_block_trade_7924w | searched_trading_and_old_project_mirrors | block_trade_appended | 连续第11个交易日50万股同规格大宗；归属和剩余额度待官方减持进展 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed_with_ir_observation | controller_open_web_only | CNINFO stock/name/code no_hit 2026-06-18/19 | T_and_T_plus_1 | 2026-06-18 no_hit | 2026-06-18 no_hit | searched_ir_questions_observation | ir_observation_appended | 索尔思交割/合规答复仍待一手 IR 或正式公告；订单和毛利量化仍缺 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed_with_block_trade | controller_open_web_only | CNINFO stock/name/code no_hit 2026-06-18/19 | T_and_T_plus_1 | 2026-06-18 no_hit | 2026-06-18 hit_1_block_trade_30093w | searched_market_topic_no_new_hard_signal | block_trade_appended | 大额机构换手不等于1.6T/硅光经营兑现；仍待 IR/财报量化 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed_no_new_material_change | controller_open_web_only | CNINFO stock/name/code no_hit 2026-06-18/19 | T_and_T_plus_1 | 2026-06-18 no_hit | 2026-06-18 no_hit | searched_old_roadshow_and_market_pages_no_new_signal | no_change | 200G EML客户验证、CW收入、H股审批和毛利新增证据仍缺 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed_no_new_material_change | controller_open_web_only | CNINFO stock/name/code no_hit 2026-06-18/19 | T_and_T_plus_1 | 2026-06-18 no_hit | 2026-06-18 no_hit | searched_old_liquid_cooling_risk_mirrors_no_new_signal | no_change | 高速连接器/液冷大额订单、客户和毛利硬证据仍缺 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed_no_new_material_change | controller_open_web_only | CNINFO stock/name/code no_hit 2026-06-18/19 | T_and_T_plus_1 | 2026-06-18 no_hit | 2026-06-18 no_hit | no_signal | no_change | 1.6T/CPO/FAU/ELS客户、订单、收入占比、毛利率或H股审批新增证据仍缺 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed_no_new_material_change | controller_open_web_only | CNINFO hit prior 2026-06-18 abnormal volatility already_in_ledger; no 2026-06-19 new | T_and_T_plus_1 | 2026-06-18 no_hit | 2026-06-18 no_hit | searched_old_h_share_and_ai_power_mirrors_no_extra_fact | no_change | AI电源客户、订单、收入占比、毛利率和交付节奏仍缺新增硬证据 | not_used_by_policy |

## reconciliation

- enabled_watchlist_count: 10
- completion_table_count: 10
- completed_enabled_tickers: 002428.SZ, 603256.SH, 601869.SH, 301511.SZ, 002384.SZ, 300308.SZ, 688498.SH, 688668.SH, 300394.SZ, 002851.SZ
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
- watchlist_last_update_date: 2026-06-18 for all enabled rows
- disabled_or_not_enabled_in_workbook: 002222.SZ, 300476.SZ, 603738.SH
