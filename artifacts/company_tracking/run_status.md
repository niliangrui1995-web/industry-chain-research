# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-06-08
- run_started_at_beijing: 2026-06-08 20:32:15 +08:00
- run_finished_at_beijing: 2026-06-08 21:09:00 +08:00
- automation_id: a-grok
- enabled_company_count: 10
- completed_company_count: 10
- baseline_created_or_refreshed_count: 1
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

## source_notes

- New baseline created: 002851.SZ 麦格米特.
- New events appended: 301511.SZ 2026-06-08 incentive committee notice; 301511.SZ 2026-06-08 block trade; 300308.SZ 2026-06-09 cash-management progress; 002851.SZ baseline event ledger.
- T/T+1 name-query correction: 301511.SZ and 300308.SZ had official CNINFO hits by company-name query that the code-only query missed.
- Trading event: 301511.SZ had one 2026-06-08 block trade, 50.00万股, 121.85元, 6,092.50万元, buyer 机构专用, seller 中信证券股份有限公司北京分公司.
- Routine official announcement: 300308.SZ 2026-06-09 cash-management progress, 1,000万元银河证券收益凭证, 2026-06-09 to 2026-06-29, expected annualized yield 1.40%.
- No sub-agents, company workers, external browsers, browser plugins, Grok, Gemini, X, or social search tools were used.

## completion_table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_no_material_change | controller_open_web_only | CNINFO code/name no_hit | T_and_T_plus_1 | 2026-06-08 no_hit | 2026-06-08 no_hit | searched_no_material_signal | no_change | 无 InP/GaAs 客户、订单、良率、6英寸量产、出口许可或利润兑现新增证据 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed_no_material_change | controller_open_web_only | CNINFO code/name no_hit | T_and_T_plus_1 | 2026-06-08 no_hit | 2026-06-08 no_hit | searched_no_material_signal | no_change | 无 Low CTE/T-glass 客户认证、订单、涨价或参数新增证据 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed_no_material_change | controller_open_web_only | CNINFO code/name no_hit | T_and_T_plus_1 | 2026-06-08 no_hit | 2026-06-08 no_hit | searched_no_material_signal | no_change | 无光纤价格、数据中心需求、海外扩张或特种光纤新增硬证据 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed_with_official_and_block_trade | controller_open_web_only | CNINFO name hit incentive committee notice; code query no_hit | T_and_T_plus_1 | 2026-06-08 no_hit | 2026-06-08 hit_1_block_trade_6092.50w | searched_hit_block_trade_mirror_no_new_operating_signal | official_event_and_block_trade_appended | 6月8日大宗交易归属待后续官方减持进展确认 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed_no_new_material_delta | controller_open_web_only | CNINFO code/name no_hit | T_and_T_plus_1 | 2026-06-08 no_hit | 2026-06-08 no_hit | searched_old_lhb_block_only_no_new_material | no_change | open-web 命中 6月4日旧龙虎榜/大宗交易，已在本地事件账本存在，不重复入账 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed_with_routine_announcement | controller_open_web_only | CNINFO name hit 2026-06-09 cash-management notice; code query no_hit | T_and_T_plus_1 | 2026-06-08 no_hit | 2026-06-08 no_hit | searched_no_new_operating_signal | routine_official_event_appended | 现金管理为资金效率事项，不改变 800G/1.6T、硅光、客户或毛利率主线 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed_no_material_change | controller_open_web_only | CNINFO code/name no_hit | T_and_T_plus_1 | 2026-06-08 no_hit | 2026-06-08 no_hit | searched_no_material_signal | no_change | 无 200G EML 客户定点、批量订单或收入占比新增证据 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed_no_material_change | controller_open_web_only | CNINFO code/name no_hit | T_and_T_plus_1 | 2026-06-08 no_hit | 2026-06-08 no_hit | searched_no_material_signal | no_change | 无高速连接器、铜缆连接、液冷长期订单或客户新增硬证据 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed_no_material_change | controller_open_web_only | CNINFO code/name no_hit | T_and_T_plus_1 | 2026-06-08 no_hit | 2026-06-08 no_hit | searched_no_material_signal | no_change | 无 1.6T/CPO/H股发行进展、客户或泰国产能新增硬证据 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed_with_baseline_created | controller_open_web_only | T/T+1 no_hit; baseline historical CNINFO name query hit annual/Q1/6月公告 | T_and_T_plus_1 | 2026-06-08 no_hit; baseline_backfill_2026-06-02_and_06-03_lhb | 2026-06-08 no_hit | searched_baseline_context_no_new_t_event | baseline_created | 新增公司基线已建立；AI数据中心电源客户、订单、收入占比和毛利率仍为 N/A | not_used_by_policy |

## reconciliation

- enabled_watchlist_count: 10
- completion_table_count: 10
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
- watchlist_last_update_date: 2026-06-08 for all enabled rows
- disabled_or_not_enabled_in_workbook: 002222.SZ, 300476.SZ
