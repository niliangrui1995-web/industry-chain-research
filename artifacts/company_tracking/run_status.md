# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-06-15
- run_started_at_beijing: 2026-06-15 20:34:40 +08:00
- run_finished_at_beijing: 2026-06-15 20:47:28 +08:00
- automation_id: a-grok
- enabled_company_count: 10
- completed_company_count: 10
- baseline_created_or_refreshed_count: 0
- current_run_multi_agent_status: not_used_by_policy
- collection_scope: controller_open_web_only
- announcement_window_policy: T_and_T_plus_1 because run is after 20:00 Beijing time
- announcement_query_window: 2026-06-13 to 2026-06-16, includes weekend gap since last run
- trading_event_date_checked: 2026-06-15
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
| 300308.SZ | 中际旭创 | done | done | done | done | done | no_change | no |
| 688498.SH | 源杰科技 | done | done | done | done | done | no_change | no |
| 688668.SH | 鼎通科技 | done | done | done | done | done | no_change | no |
| 300394.SZ | 天孚通信 | done | done | done | done | done | yes | yes |
| 002851.SZ | 麦格米特 | done | done | done | done | done | yes | yes |

## source_notes

- New official events appended: 002428.SZ 控股股东质押和异常波动风险提示；301511.SZ 子公司担保进展；002851.SZ 期权注销完成。
- New trading events appended: 002428.SZ 2026-06-15 龙虎榜；301511.SZ、002384.SZ、300394.SZ 2026-06-15 大宗交易。
- No baseline was created or refreshed.
- CNINFO company-name query remained necessary; code-only query can miss announcements.
- SZSE confirmed the 002428.SZ dragon-tiger record and the 301511.SZ / 002384.SZ / 300394.SZ block trades; Eastmoney was used as secondary trading-data cross-check.
- No sub-agents, company workers, external browsers, browser plugins, Grok, Gemini, X, or social search tools were used.

## completion_table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_with_official_risk_and_dragon_tiger | controller_open_web_only | CNINFO name/code hit 2 new 2026-06-16 announcements; weekend gap checked | T_and_T_plus_1 | 2026-06-15 hit_szse_dragon_tiger | 2026-06-15 no_hit | searched_official_and_market_mirrors_no_new_operating_signal | official_risk_and_dragon_tiger_appended | 估值/业绩/出口管制风险强化；仍无InP/GaAs客户、订单、良率、6英寸量产、出口许可或利润兑现新增硬证据 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed_no_new_material_change | controller_open_web_only | CNINFO name hit prior 2026-06-13 land certificate already_in_ledger; no 2026-06-15/16 new | T_and_T_plus_1 | 2026-06-15 no_hit | 2026-06-15 no_hit | searched_sector_electronic_cloth_price_observation | no_change | 电子布涨价为行业媒体观察，未看到公司Low CTE/T-glass订单、价格、毛利率或客户认证新增公告 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed_no_material_change | controller_open_web_only | CNINFO name/code no_hit | T_and_T_plus_1 | 2026-06-15 no_hit | 2026-06-15 no_hit | searched_no_new_hard_signal | no_change | 无数据中心光纤订单、运营商集采、价格或毛利率新增硬证据 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed_with_official_guarantee_and_block_trade | controller_open_web_only | CNINFO name hit 1 new 2026-06-15 guarantee progress | T_and_T_plus_1 | 2026-06-15 no_hit | 2026-06-15 hit_1_block_trade_7973.00w | searched_official_trading_mirrors_no_new_customer_signal | official_guarantee_and_block_trade_appended | 担保是融资支持不是HVLP/RTF订单；连续50万股大宗交易归属和剩余额度待官方减持进展公告 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed_with_block_trade | controller_open_web_only | CNINFO name/code no_hit | T_and_T_plus_1 | 2026-06-15 no_hit | 2026-06-15 hit_1_block_trade_615.69w | searched_irmirror_no_new_official_signal | block_trade_appended | 小额折价机构交易；无AI服务器PCB/索尔思客户、订单、收入拆分、毛利率或产能新增硬证据 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed_no_material_change | controller_open_web_only | CNINFO name/code no_hit | T_and_T_plus_1 | 2026-06-15 no_hit | 2026-06-15 no_hit | searched_no_new_hard_signal | no_change | 无800G/1.6T、硅光、客户需求、上游物料或毛利率新增官方硬披露 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed_no_material_change | controller_open_web_only | CNINFO name/code no_hit | T_and_T_plus_1 | 2026-06-15 no_hit | 2026-06-15 no_hit | searched_old_h_share_and_product_context_no_new_order | no_change | 无200G EML客户定点、批量订单、CW光源收入拆分、H股进展或毛利率新增证据 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed_no_material_change | controller_open_web_only | CNINFO name/code no_hit | T_and_T_plus_1 | 2026-06-15 no_hit | 2026-06-15 no_hit | searched_repeated_liquid_cooling_clarification_no_new_order | no_change | 无高速连接器、铜缆连接、液冷长期订单或客户新增硬证据；6月4日液冷小批量供货澄清仍是最新边界 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed_with_block_trade | controller_open_web_only | CNINFO name/code no_hit | T_and_T_plus_1 | 2026-06-15 no_hit | 2026-06-15 hit_1_block_trade_610.08w | searched_block_trade_mirror_no_new_operating_signal | block_trade_appended | 小额平价机构换手；无1.6T/CPO/FAU/ELS客户、订单、收入占比、毛利率或H股审批新增证据 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed_with_official_option_cancel | controller_open_web_only | CNINFO name hit 1 new 2026-06-16 option cancel completion | T_and_T_plus_1 | 2026-06-15 no_hit | 2026-06-15 no_hit | searched_h_share_and_ai_power_mirrors_no_new_hard_signal | official_event_appended | 期权注销不影响股本；无AI数据中心电源客户、订单、收入占比、毛利率或交付节奏新增硬证据 | not_used_by_policy |

## reconciliation

- enabled_watchlist_count: 10
- completion_table_count: 10
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
- watchlist_last_update_date: 2026-06-15 for all enabled rows
- disabled_or_not_enabled_in_workbook: 002222.SZ, 300476.SZ, 603738.SH
