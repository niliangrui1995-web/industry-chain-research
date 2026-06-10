# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-06-10
- run_started_at_beijing: 2026-06-10 20:33:27 +08:00
- run_finished_at_beijing: 2026-06-10 20:51:44 +08:00
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
| 603256.SH | 宏和科技 | done | done | done | done | done | no_new_event_duplicate | no |
| 601869.SH | 长飞光纤 | done | done | done | done | done | no_change | no |
| 301511.SZ | 德福科技 | done | done | done | done | done | yes | yes |
| 002384.SZ | 东山精密 | done | done | done | done | done | no_change | no |
| 300308.SZ | 中际旭创 | done | done | done | done | done | no_change | no |
| 688498.SH | 源杰科技 | done | done | done | done | done | no_change | no |
| 688668.SH | 鼎通科技 | done | done | done | done | done | yes | yes |
| 300394.SZ | 天孚通信 | done | done | done | done | done | no_change | no |
| 002851.SZ | 麦格米特 | done | done | done | done | done | yes | yes |

## source_notes

- New official events appended: 301511.SZ equity-incentive insider-information self-check; 688668.SH convertible-bond proceeds account board resolution.
- New trading events appended: 301511.SZ 2026-06-10 block trade; 002851.SZ 2026-06-10 dragon-tiger list.
- Prior T+1 official events not duplicated: 603256.SH shareholder reduction plan; 002851.SZ H-share listing and stock-option announcements.
- CNINFO company-name query remained primary; code-keyword search can be noisy for some tickers.
- SZSE official endpoints confirmed 301511.SZ block trade and 002851.SZ dragon-tiger details; Eastmoney was used as cross-check / secondary data.
- No sub-agents, company workers, external browsers, browser plugins, Grok, Gemini, X, or social search tools were used.

## completion_table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_no_material_change | controller_open_web_only | CNINFO name no_hit | T_and_T_plus_1 | 2026-06-10 no_hit | 2026-06-10 no_hit | searched_no_material_signal | no_change | 无 InP/GaAs 客户、订单、良率、6英寸量产、出口许可或利润兑现新增证据 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed_no_new_material_delta | controller_open_web_only | CNINFO name hit 2026-06-10 shareholder reduction already_in_ledger | T_and_T_plus_1 | 2026-06-10 no_hit | 2026-06-10 no_hit | searched_confirmed_media_mirrors | no_new_event_duplicate | 7月2日后才进入减持实施期，需跟踪实际减持和大宗交易 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed_no_material_change | controller_open_web_only | CNINFO name no_hit | T_and_T_plus_1 | 2026-06-10 no_hit | 2026-06-10 no_hit | searched_no_new_hard_signal | no_change | 无数据中心光纤订单、运营商集采、价格或毛利率新增硬证据 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed_with_official_and_block_trade | controller_open_web_only | CNINFO name hit insider self-check | T_and_T_plus_1 | 2026-06-10 no_hit | 2026-06-10 hit_1_block_trade_6786.50w | searched_repeated_project_observation | official_and_block_trade_appended | 大宗交易归属需后续官方减持进展确认；未证明 HVLP/RTF 订单或毛利率 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed_no_material_change | controller_open_web_only | CNINFO name no_hit | T_and_T_plus_1 | 2026-06-10 no_hit | 2026-06-10 no_hit | searched_no_new_material_signal | no_change | 无 AI服务器 PCB/FPC 订单、客户、H股进展或盈利修复新增硬证据 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed_no_material_change | controller_open_web_only | CNINFO name no_hit | T_and_T_plus_1 | 2026-06-10 no_hit | 2026-06-10 no_hit | searched_no_new_operating_signal | no_change | 无 800G/1.6T、硅光、客户或毛利率新增披露 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed_no_material_change | controller_open_web_only | CNINFO name no_hit | T_and_T_plus_1 | 2026-06-10 no_hit | 2026-06-10 no_hit | searched_no_material_signal | no_change | 无 200G EML 客户定点、批量订单、收入占比或 H 股新进展新增证据 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed_with_official_announcement | controller_open_web_only | CNINFO name hit 2026-06-11 board resolution | T_and_T_plus_1 | 2026-06-10 no_hit | 2026-06-10 no_hit | searched_convertible_bond_context_no_new_order | official_event_appended | 可转债执行准备不等于液冷/高速连接器大额订单或短期业绩贡献 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed_no_material_change | controller_open_web_only | CNINFO name no_hit | T_and_T_plus_1 | 2026-06-10 no_hit | 2026-06-10 no_hit | searched_social_spam_ignored_no_hard_signal | no_change | 无 1.6T/CPO/FAU/ELS 客户、订单、收入占比、毛利率或 H 股审批新增硬证据 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed_with_dragon_tiger | controller_open_web_only | CNINFO name hit 29 announcements already_in_ledger | T_and_T_plus_1 | 2026-06-10 hit_price_drop_deviation | 2026-06-10 no_hit | searched_h_share_media_mirrors | dragon_tiger_appended | 龙虎榜是交易拥挤/回撤信号，不证明 AI 数据中心电源经营兑现 | not_used_by_policy |

## reconciliation

- enabled_watchlist_count: 10
- completion_table_count: 10
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
- watchlist_last_update_date: 2026-06-10 for all enabled rows
- disabled_or_not_enabled_in_workbook: 002222.SZ, 300476.SZ, 603738.SH
