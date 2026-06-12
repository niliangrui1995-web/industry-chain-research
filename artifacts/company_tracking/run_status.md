# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-06-12
- run_started_at_beijing: 2026-06-12 20:33:47 +08:00
- run_finished_at_beijing: 2026-06-12 20:41:21 +08:00
- automation_id: a-grok
- enabled_company_count: 10
- completed_company_count: 10
- baseline_created_or_refreshed_count: 0
- current_run_multi_agent_status: not_used_by_policy
- collection_scope: controller_open_web_only
- announcement_window_policy: T_and_T_plus_1 because run is after 20:00 Beijing time
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
| 603256.SH | 宏和科技 | done | done | done | done | done | yes | yes |
| 601869.SH | 长飞光纤 | done | done | done | done | done | no_change | no |
| 301511.SZ | 德福科技 | done | done | done | done | done | yes | yes |
| 002384.SZ | 东山精密 | done | done | done | done | done | no_change | no |
| 300308.SZ | 中际旭创 | done | done | done | done | done | yes | yes |
| 688498.SH | 源杰科技 | done | done | done | done | done | yes | yes |
| 688668.SH | 鼎通科技 | done | done | done | done | done | no_change | no |
| 300394.SZ | 天孚通信 | done | done | done | done | done | no_change | no |
| 002851.SZ | 麦格米特 | done | done | done | done | done | no_change | no |

## source_notes

- New official events appended: 603256.SH 黄石宏和取得不动产权证暨对外投资进展；301511.SZ 第一次临时股东会通过项目合同和股权激励相关议案并完成限制性股票授予；300308.SZ 董事会换届和高管聘任。
- New trading events appended: 301511.SZ 2026-06-12 1 笔大宗交易；300308.SZ 2026-06-12 1 笔大宗交易；688498.SH 2026-06-12 4 笔大宗交易。
- No dragon-tiger list hit for enabled companies on 2026-06-12.
- CNINFO company-name query remained necessary; code-only query can miss several announcements.
- SZSE ShowReport confirmed 301511.SZ and 300308.SZ block trades; 688498.SH block trades were recorded from Eastmoney secondary trading data, with SSE official block-trade page not checked this run.
- No sub-agents, company workers, external browsers, browser plugins, Grok, Gemini, X, or social search tools were used.

## completion_table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_no_new_material_change | controller_open_web_only | CNINFO name hit 2 prior 2026-06-12 announcements already_in_ledger | T_and_T_plus_1 | 2026-06-12 no_hit | 2026-06-12 no_hit | searched_no_new_material_signal | no_change | 前轮T+1公告已入账；无InP/GaAs客户、订单、良率、6英寸量产、出口许可或利润兑现新增证据 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed_with_official_project_progress | controller_open_web_only | CNINFO name hit 4 announcements incl 1 new 2026-06-13 project land certificate | T_and_T_plus_1 | 2026-06-12 no_hit | 2026-06-12 no_hit | searched_project_progress_confirmed | official_project_progress_appended | 土地权属落地不等于Low CTE/T-glass订单或涨价；仍需环评、建设资金、产能消化和负债率跟踪 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed_no_material_change | controller_open_web_only | CNINFO name no_hit | T_and_T_plus_1 | 2026-06-12 no_hit | 2026-06-12 no_hit | searched_no_new_hard_signal | no_change | 无数据中心光纤订单、运营商集采、价格或毛利率新增硬证据 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed_with_official_and_block_trade | controller_open_web_only | CNINFO name hit 7 announcements: shareholder meeting and equity incentive grant | T_and_T_plus_1 | 2026-06-12 no_hit | 2026-06-12 hit_1_block_trade_6844.00w | searched_official_mirrors_no_new_customer_signal | official_and_block_trade_appended | 股东会/授予落地强化项目和考核锚，但未证明HVLP/RTF订单或毛利率；连续大宗交易归属仍待官方减持进展确认 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed_no_material_change | controller_open_web_only | CNINFO name no_hit | T_and_T_plus_1 | 2026-06-12 no_hit | 2026-06-12 no_hit | searched_no_new_material_signal | no_change | 无AI服务器PCB/FPC、索尔思订单、客户、H股进展或盈利修复新增硬证据 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed_with_official_governance_and_block_trade | controller_open_web_only | CNINFO name hit 5 governance/board transition announcements | T_and_T_plus_1 | 2026-06-12 no_hit | 2026-06-12 hit_1_block_trade_6043.74w | searched_governance_and_block_trade_signal_only | official_governance_and_block_trade_appended | 换届和机构平价换手不构成800G/1.6T、硅光、客户、物料或毛利率新增经营披露 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed_with_block_trade | controller_open_web_only | CNINFO name/code no_hit | T_and_T_plus_1 | 2026-06-12 no_hit | 2026-06-12 hit_4_block_trades_22444.12w | searched_index_and_block_trade_observation_no_operating_signal | block_trade_appended | 科创板大宗交易以上东财二级交易数据记录；无200G EML客户定点、批量订单、收入占比或H股新进展新增证据 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed_no_material_change | controller_open_web_only | CNINFO name no_hit | T_and_T_plus_1 | 2026-06-12 no_hit | 2026-06-12 no_hit | searched_repeated_liquid_cooling_clarification_no_new_order | no_change | 无高速连接器、铜缆连接、液冷长期订单或客户新增硬证据；6月4日液冷小批量供货澄清仍是最新边界 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed_no_material_change | controller_open_web_only | CNINFO name no_hit | T_and_T_plus_1 | 2026-06-12 no_hit | 2026-06-12 no_hit | searched_no_new_hard_signal | no_change | 无1.6T/CPO/FAU/ELS客户、订单、收入占比、毛利率或H股审批新增硬证据 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed_no_material_change | controller_open_web_only | CNINFO name no_hit | T_and_T_plus_1 | 2026-06-12 no_hit | 2026-06-12 no_hit | searched_h_share_and_ai_power_no_new_hard_signal | no_change | H股事项为既有公告延续；无AI数据中心电源客户、订单、收入占比、毛利率或交付节奏新增硬证据 | not_used_by_policy |

## reconciliation

- enabled_watchlist_count: 10
- completion_table_count: 10
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
- watchlist_last_update_date: 2026-06-12 for all enabled rows
- disabled_or_not_enabled_in_workbook: 002222.SZ, 300476.SZ, 603738.SH
