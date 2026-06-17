# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-06-17
- run_started_at_beijing: 2026-06-17 20:33:41 +08:00
- run_finished_at_beijing: 2026-06-17 20:42:03 +08:00
- automation_id: a-grok
- enabled_company_count: 10
- completed_company_count: 10
- baseline_created_or_refreshed_count: 0
- current_run_multi_agent_status: not_used_by_policy
- collection_scope: controller_open_web_only
- announcement_window_policy: T_and_T_plus_1 because run is after 20:00 Beijing time
- announcement_query_window: 2026-06-17 to 2026-06-18
- trading_event_date_checked: 2026-06-17
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
| 002384.SZ | 东山精密 | done | done | done | done | done | yes | yes |
| 300308.SZ | 中际旭创 | done | done | done | done | done | no_change | no |
| 688498.SH | 源杰科技 | done | done | done | done | done | no_change | no |
| 688668.SH | 鼎通科技 | done | done | done | done | done | no_change | no |
| 300394.SZ | 天孚通信 | done | done | done | done | done | no_change | no |
| 002851.SZ | 麦格米特 | done | done | done | done | done | yes | yes |

## source_notes

- New official events appended: 603256.SH 异常波动暨风险提示；002384.SZ 2026-06-17 投资者关系活动记录；002851.SZ 异常波动公告。
- New trading events appended: 603256.SH 2026-06-17 龙虎榜；301511.SZ 2026-06-17 大宗交易；002851.SZ 2026-06-17 龙虎榜。
- Prior T+1 announcements reviewed but not duplicated: 002384.SZ 2026-06-17 对外投资公告和董事会决议已在上一轮入账。
- No baseline was created or refreshed.
- CNINFO company-name query and stock+orgId query were both used where needed; code-only query can miss announcements.
- SZSE official ShowReport confirmed 301511.SZ block trade and 002851.SZ dragon-tiger record; Eastmoney was used as secondary trading-data cross-check, and for 603256.SH dragon-tiger details where exchange endpoint was not stable in this run.
- No sub-agents, company workers, external browsers, browser plugins, Grok, Gemini, X, or social search tools were used.

## per_company_completion_table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_no_new_material_change | controller_open_web_only | CNINFO stock/name/code no_hit 2026-06-17/18 | T_and_T_plus_1 | 2026-06-17 no_hit | 2026-06-17 no_hit | searched_secondary_price_and_prior_lhb_no_new_hard_signal | no_change | 锗/InP/GaAs客户、订单、良率、出口许可和利润兑现仍缺新增官方证据 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed_with_official_risk_and_lhb | controller_open_web_only | CNINFO hit 2 T+1 announcements abnormal/risk + controller reply appended | T_and_T_plus_1 | 2026-06-17 hit_lhb | 2026-06-17 no_hit | searched_official_mirrors_and_market_data_no_extra_fact | official_risk_and_lhb_appended | 估值与交易拥挤风险升高；Low CTE/T-glass订单、价格和客户认证仍需硬证据 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed_no_new_material_change | controller_open_web_only | CNINFO stock/name/code no_hit 2026-06-17/18 | T_and_T_plus_1 | 2026-06-17 no_hit | 2026-06-17 no_hit | searched_low_material_patent_and_old_lhb_no_state_change | no_change | 数据中心光纤订单、运营商集采、价格/毛利新增证据仍缺 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed_with_block_trade | controller_open_web_only | CNINFO stock/name/code no_hit 2026-06-17/18 | T_and_T_plus_1 | 2026-06-17 no_hit | 2026-06-17 hit_1_block_trade_8018w | searched_trading_mirror_no_new_customer_signal | block_trade_appended | 连续第10个交易日50万股同规格大宗；归属和剩余额度待官方减持进展 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed_with_ir_update | controller_open_web_only | CNINFO hit 3: 2 prior investment/board already_in_ledger + 1 IR appended | T_and_T_plus_1 | 2026-06-17 no_hit | 2026-06-17 no_hit | searched_official_and_media_mirrors_confirmed_by_cninfo | investor_relations_appended | 12亿美元扩建仍需审批/资金/产能爬坡/客户订单/毛利验证；MOCVD和InP/DSP供应需跟踪 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed_no_new_material_change | controller_open_web_only | CNINFO stock/name/code no_hit 2026-06-17/18 | T_and_T_plus_1 | 2026-06-17 no_hit | 2026-06-17 no_hit | no_signal | no_change | 800G/1.6T订单、硅光、上游物料、毛利率无新增官方披露 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed_no_new_material_change | controller_open_web_only | CNINFO stock/name/code no_hit 2026-06-17/18 | T_and_T_plus_1 | 2026-06-17 no_hit | 2026-06-17 no_hit | searched_old_or_prior_trading_signal_no_new_hard_signal | no_change | 200G EML客户定点/量产订单/CW收入/H股或毛利新增证据仍缺 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed_no_new_material_change | controller_open_web_only | CNINFO stock/name/code no_hit 2026-06-17/18 | T_and_T_plus_1 | 2026-06-17 no_hit | 2026-06-17 no_hit | no_signal | no_change | 高速连接器/液冷大额订单、客户和毛利硬证据仍缺 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed_no_new_material_change | controller_open_web_only | CNINFO stock/name/code no_hit 2026-06-17/18 | T_and_T_plus_1 | 2026-06-17 no_hit | 2026-06-17 no_hit | no_signal | no_change | 1.6T/CPO/FAU/ELS客户、订单、收入占比、毛利率或H股审批新增证据仍缺 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed_with_official_risk_and_lhb | controller_open_web_only | CNINFO hit 1 T+1 abnormal volatility announcement appended | T_and_T_plus_1 | 2026-06-17 hit_szse_lhb | 2026-06-17 no_hit | searched_market_and_official_mirrors_no_extra_fact | official_risk_and_lhb_appended | 龙虎榜强化交易热度；AI电源客户、订单、收入占比和毛利率仍缺新增硬证据 | not_used_by_policy |

## reconciliation

- enabled_watchlist_count: 10
- completion_table_count: 10
- completed_enabled_tickers: 002428.SZ, 603256.SH, 601869.SH, 301511.SZ, 002384.SZ, 300308.SZ, 688498.SH, 688668.SH, 300394.SZ, 002851.SZ
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
- watchlist_last_update_date: 2026-06-17 for all enabled rows
- disabled_or_not_enabled_in_workbook: 002222.SZ, 300476.SZ, 603738.SH
