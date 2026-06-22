# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-06-22
- run_started_at_beijing: 2026-06-22 20:33:32 +08:00
- run_finished_at_beijing: 2026-06-22 20:44:09 +08:00
- automation_id: a-grok
- enabled_company_count: 10
- completed_company_count: 10
- baseline_created_or_refreshed_count: 0
- current_run_multi_agent_status: not_used_by_policy
- collection_scope: controller_open_web_only
- announcement_window_policy: T_and_T_plus_1 because run is after 20:00 Beijing time
- announcement_query_window: 2026-06-22 to 2026-06-23
- trading_event_date_checked: 2026-06-22
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
| 002428.SZ | 云南锗业 | done | done | done | done | done | updated_block_trade | yes |
| 603256.SH | 宏和科技 | done | done | done | done | done | updated_patent | yes |
| 601869.SH | 长飞光纤 | done | done | done | done | done | updated_open_web_observation | yes |
| 301511.SZ | 德福科技 | done | done | done | done | done | updated_block_trade | yes |
| 002384.SZ | 东山精密 | done | done | done | done | done | no_change | no |
| 300308.SZ | 中际旭创 | done | done | done | done | done | updated_block_trade | yes |
| 688498.SH | 源杰科技 | done | done | done | done | done | updated_risk_warning | yes |
| 688668.SH | 鼎通科技 | done | done | done | done | done | updated_convertible_bond | yes |
| 300394.SZ | 天孚通信 | done | done | done | done | done | no_change | no |
| 002851.SZ | 麦格米特 | done | done | done | done | done | updated_stock_option | yes |

## source_notes

- New official announcements appended: 宏和科技发明专利、源杰科技股票交易风险提示、鼎通科技可转债发行文件、麦格米特股票期权自主行权及更正。
- New trading events appended: 云南锗业 2 笔大宗交易、中际旭创 1 笔大宗交易、德福科技 1 笔大宗交易。2026-06-22 未发现 tracked-company 龙虎榜。
- New open-web observations appended: 长飞光纤 A+H 总市值突破 3000 亿元的可信媒体观察；其他 open-web 搜索结果主要是官方镜像、行情页、旧材料或弱观察。
- No baseline was created or refreshed.
- CNINFO company-name query and code query were both used; code-only query noise was filtered by issuer `secCode/secName`, especially for 麦格米特.
- No sub-agents, company workers, external browsers, browser plugins, Grok, Gemini, X, or social search tools were used.

## per_company_completion_table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_with_material_trading_event | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-22/23 | T_and_T_plus_1 | 2026-06-22 no_hit | 2026-06-22 2_hit | searched_market_pages_no_new_hard_signal | updated_block_trade | 折价大宗归属、股东/资金方减持和质押风险需继续核对 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed_with_official_announcement | controller_open_web_only | CNINFO issuer hit patent 2026-06-23 | T_and_T_plus_1 | 2026-06-22 no_hit | 2026-06-22 no_hit | searched_official_patent_mirrors | updated_patent | 专利不等于 Low CTE/T-glass 订单、价格或毛利兑现 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed_with_open_web_observation | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-22/23 | T_and_T_plus_1 | 2026-06-22 no_hit | 2026-06-22 no_hit | searched_useful_media_observation | updated_open_web_observation | 市值/涨停观察不等于新增订单或数据中心收入确认 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed_with_material_trading_event | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-22/23 | T_and_T_plus_1 | 2026-06-22 no_hit | 2026-06-22 1_hit | searched_market_pages_no_new_hard_signal | updated_block_trade | 同卖方席位大宗归属和剩余额度仍待官方减持进展 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-22/23 | T_and_T_plus_1 | 2026-06-22 no_hit | 2026-06-22 no_hit | searched_prior_source_photonics_mirrors_no_new_signal | no_change | 索尔思项目审批、资金安排、客户订单和毛利量化仍缺 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed_with_material_trading_event | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-22/23 | T_and_T_plus_1 | 2026-06-22 no_hit | 2026-06-22 1_hit | searched_market_topic_no_new_hard_signal | updated_block_trade | 高价大宗仅是交易结构观察，不证明 1.6T/硅光经营新增 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed_with_official_announcement | controller_open_web_only | CNINFO issuer hit risk warning 2026-06-23 | T_and_T_plus_1 | 2026-06-22 no_hit | 2026-06-22 no_hit | searched_official_risk_warning_mirrors | updated_risk_warning | 200G EML、CW 客户和二期扩产仍需硬证据 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed_with_official_announcement | controller_open_web_only | CNINFO issuer hit convertible-bond filings 2026-06-22 | T_and_T_plus_1 | 2026-06-22 no_hit | 2026-06-22 no_hit | searched_convertible_bond_media_mirrors | updated_convertible_bond | 募资进展不等于高速连接器/液冷客户订单或毛利兑现 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed_no_new_material_change | controller_open_web_only | CNINFO name/code no issuer hit 2026-06-22/23 | T_and_T_plus_1 | 2026-06-22 no_hit | 2026-06-22 no_hit | searched_old_market_pages_no_new_signal | no_change | 1.6T/CPO/FAU/ELS 客户、订单、收入占比、毛利率或 H 股审批新增证据仍缺 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed_with_official_announcement | controller_open_web_only | CNINFO issuer hit stock-option exercise/correction 2026-06-22; code-query noise filtered | T_and_T_plus_1 | 2026-06-22 no_hit | 2026-06-22 no_hit | searched_stock_option_mirrors_no_new_ai_power_signal | updated_stock_option | AI 电源客户、订单、收入占比、毛利率和交付节奏仍未量化 | not_used_by_policy |

## reconciliation

- enabled_watchlist_count: 10
- completion_table_count: 10
- completed_enabled_tickers: 002428.SZ, 603256.SH, 601869.SH, 301511.SZ, 002384.SZ, 300308.SZ, 688498.SH, 688668.SH, 300394.SZ, 002851.SZ
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
- watchlist_last_update_date: 2026-06-22 for all enabled rows
- disabled_or_not_enabled_in_workbook: 002222.SZ, 300476.SZ, 603738.SH
