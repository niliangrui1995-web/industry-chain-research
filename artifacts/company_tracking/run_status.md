# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-06-09
- run_started_at_beijing: 2026-06-09 20:33:26 +08:00
- run_finished_at_beijing: 2026-06-09 20:47:28 +08:00
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
| 601869.SH | 长飞光纤 | done | done | done | done | done | yes | yes |
| 301511.SZ | 德福科技 | done | done | done | done | done | yes | yes |
| 002384.SZ | 东山精密 | done | done | done | done | done | no_change | no |
| 300308.SZ | 中际旭创 | done | done | done | done | done | no_new_event_duplicate | no |
| 688498.SH | 源杰科技 | done | done | done | done | done | no_change | no |
| 688668.SH | 鼎通科技 | done | done | done | done | done | no_change | no |
| 300394.SZ | 天孚通信 | done | done | done | done | done | yes | yes |
| 002851.SZ | 麦格米特 | done | done | done | done | done | yes | yes |

## source_notes

- New official events appended: 603256.SH shareholder reduction plan; 002851.SZ H-share listing plan and stock-option vesting.
- New trading events appended: 301511.SZ 2026-06-09 block trade; 300394.SZ 2026-06-09 two block trades.
- New open-web observations appended: 601869.SH Amazon-Corning official fiber agreement as sector observation; 301511.SZ project-launch media item citing company WeChat.
- T/T+1 name-query correction remains important: 603256.SH and 002851.SZ official CNINFO hits were found by company-name query, while code-only query was incomplete.
- 300308.SZ 2026-06-09 cash-management announcement was already appended in the previous run's T+1 window and was not duplicated.
- No sub-agents, company workers, external browsers, browser plugins, Grok, Gemini, X, or social search tools were used.

## completion_table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_no_material_change | controller_open_web_only | CNINFO code/name no_hit | T_and_T_plus_1 | 2026-06-09 no_hit | 2026-06-09 no_hit | searched_no_material_signal | no_change | 无 InP/GaAs 客户、订单、良率、6英寸量产、出口许可或利润兑现新增证据 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed_with_official_announcement | controller_open_web_only | CNINFO name hit shareholder reduction plan; code query no_hit | T_and_T_plus_1 | 2026-06-09 no_hit | 2026-06-09 no_hit | searched_confirmed_official_mirrors | official_event_appended | 减持实施期从 2026-07-02 起，需跟踪实际减持和大宗交易 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed_with_open_web_observation | controller_open_web_only | CNINFO/SSE no_hit | T_and_T_plus_1 | 2026-06-09 no_hit | 2026-06-09 no_hit | searched_sector_signal_amazon_corning | open_web_observation_appended | Amazon-Corning 为外部行业信号，不是长飞光纤订单或收入确认 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed_with_block_trade_and_observation | controller_open_web_only | CNINFO code/name no_hit | T_and_T_plus_1 | 2026-06-09 no_hit | 2026-06-09 hit_1_block_trade_6771.50w | searched_project_launch_observation | media_observation_and_block_trade_appended | 6月9日大宗交易归属待后续官方减持进展确认 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed_no_material_change | controller_open_web_only | CNINFO code/name no_hit | T_and_T_plus_1 | 2026-06-09 no_hit | 2026-06-09 no_hit | searched_no_new_material_signal | no_change | 无 AI服务器 PCB/FPC 订单、客户、H股进展或盈利修复新增硬证据 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed_no_new_material_delta | controller_open_web_only | CNINFO name hit 2026-06-09 cash-management already_in_ledger | T_and_T_plus_1 | 2026-06-09 no_hit | 2026-06-09 no_hit | searched_no_new_operating_signal | no_new_event_duplicate | 现金管理公告已在上一轮入账；无 800G/1.6T、硅光、客户或毛利率新增披露 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed_no_material_change | controller_open_web_only | CNINFO code/name no_hit | T_and_T_plus_1 | 2026-06-09 no_hit | 2026-06-09 no_hit | searched_no_material_signal | no_change | 无 200G EML 客户定点、批量订单、收入占比或 H 股新进展新增证据 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed_no_material_change | controller_open_web_only | CNINFO code/name no_hit | T_and_T_plus_1 | 2026-06-09 no_hit | 2026-06-09 no_hit | searched_research_only_no_hard_signal | no_change | 无高速连接器、铜缆连接、液冷长期订单或客户新增硬证据 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed_with_block_trade | controller_open_web_only | CNINFO/SZSE no_hit | T_and_T_plus_1 | 2026-06-09 no_hit | 2026-06-09 hit_2_block_trades_13559.45w | searched_block_mirror_no_operating_signal | block_trade_appended | 大宗交易为平价机构换手，不是 1.6T/CPO/H股进展经营证据 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed_with_official_announcements | controller_open_web_only | CNINFO name hit 29 announcements including H-share plan and option vesting | T_and_T_plus_1 | 2026-06-09 no_hit | 2026-06-09 no_hit | searched_official_events_no_new_ai_order | official_events_appended | H股和期权事项不证明 AI数据中心电源客户、订单、收入占比或毛利率 | not_used_by_policy |

## reconciliation

- enabled_watchlist_count: 10
- completion_table_count: 10
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
- watchlist_last_update_date: 2026-06-09 for all enabled rows
- disabled_or_not_enabled_in_workbook: 002222.SZ, 300476.SZ
