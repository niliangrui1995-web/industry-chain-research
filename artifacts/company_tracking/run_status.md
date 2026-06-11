# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-06-11
- run_started_at_beijing: 2026-06-11 20:32:28 +08:00
- run_finished_at_beijing: 2026-06-11 20:41:48 +08:00
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
| 002428.SZ | 云南锗业 | done | done | done | done | done | yes | yes |
| 603256.SH | 宏和科技 | done | done | done | done | done | yes | yes |
| 601869.SH | 长飞光纤 | done | done | done | done | done | no_change | no |
| 301511.SZ | 德福科技 | done | done | done | done | done | yes | yes |
| 002384.SZ | 东山精密 | done | done | done | done | done | no_change | no |
| 300308.SZ | 中际旭创 | done | done | done | done | done | yes | yes |
| 688498.SH | 源杰科技 | done | done | done | done | done | no_change | no |
| 688668.SH | 鼎通科技 | done | done | done | done | done | no_new_event_duplicate | no |
| 300394.SZ | 天孚通信 | done | done | done | done | done | no_change | no |
| 002851.SZ | 麦格米特 | done | done | done | done | done | no_change | no |

## source_notes

- New official events appended: 002428.SZ subsidiary guarantee progress and subsidiary/sun-subsidiary business-scope registration changes; 603256.SH finance lease and credit facility progress.
- New trading events appended: 002428.SZ 2026-06-11 dragon-tiger list; 301511.SZ 2026-06-11 block trade; 300308.SZ 2026-06-11 block trades.
- Prior T+1 official event not duplicated: 688668.SH 2026-06-11 board resolution on convertible-bond proceeds accounts.
- CNINFO company-name query remained necessary for several companies; code-only query missed 002428.SZ and 603256.SH T+1 announcements.
- SZSE block-trade ShowReport confirmed 301511.SZ and 300308.SZ block trades; SZSE dragon-tiger endpoint failed for 002428.SZ, so Eastmoney trading data was used as secondary trading evidence.
- No sub-agents, company workers, external browsers, browser plugins, Grok, Gemini, X, or social search tools were used.

## completion_table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_with_official_and_dragon_tiger | controller_open_web_only | CNINFO name hit 2 T+1 announcements | T_and_T_plus_1 | 2026-06-11 hit_gain_deviation | 2026-06-11 no_hit | searched_lhb_media_confirmed | official_and_dragon_tiger_appended | 深交所龙虎榜直连接口失败，龙虎榜以东方财富二级交易数据确认；经营兑现仍缺客户/订单/良率证据 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed_with_official_financing_events | controller_open_web_only | CNINFO name hit 3 T+1 announcements | T_and_T_plus_1 | 2026-06-11 no_hit | 2026-06-11 no_hit | searched_official_mirrors_no_operating_signal | official_financing_events_appended | 融资租赁/授信不等于Low CTE/T-glass订单或涨价；需看融资成本和负债率 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed_no_material_change | controller_open_web_only | CNINFO name/code no_hit | T_and_T_plus_1 | 2026-06-11 no_hit | 2026-06-11 no_hit | searched_no_new_hard_signal | no_change | 无数据中心光纤订单、运营商集采、价格或毛利率新增硬证据 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed_with_block_trade | controller_open_web_only | CNINFO name/code no_hit | T_and_T_plus_1 | 2026-06-11 no_hit | 2026-06-11 hit_1_block_trade_6578.50w | searched_block_trade_and_project_observation | block_trade_appended | 连续第六个交易日同规格大宗交易归属仍待官方减持进展确认；未证明HVLP/RTF订单或毛利率 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed_no_material_change | controller_open_web_only | CNINFO name/code no_hit | T_and_T_plus_1 | 2026-06-11 no_hit | 2026-06-11 no_hit | searched_no_new_material_signal | no_change | 无AI服务器PCB/FPC、索尔思订单、客户、H股进展或盈利修复新增硬证据 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed_with_block_trade | controller_open_web_only | CNINFO name/code no_hit | T_and_T_plus_1 | 2026-06-11 no_hit | 2026-06-11 hit_2_block_trades_12553.06w | searched_block_trade_signal_only | block_trade_appended | 平价机构换手不构成800G/1.6T、硅光、客户、物料或毛利率新增披露 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed_no_material_change | controller_open_web_only | CNINFO name/code no_hit | T_and_T_plus_1 | 2026-06-11 no_hit | 2026-06-11 no_hit | searched_no_material_signal | no_change | 无200G EML客户定点、批量订单、收入占比或H股新进展新增证据 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed_duplicate_official_checked | controller_open_web_only | CNINFO name hit 2026-06-11 board resolution already_in_ledger | T_and_T_plus_1 | 2026-06-11 no_hit | 2026-06-11 no_hit | searched_no_relevant_result | no_new_event_duplicate | 可转债专户事项已在上一轮T+1入账；无液冷/高速连接器大额订单或短期业绩贡献新增证据 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed_no_material_change | controller_open_web_only | CNINFO name/code no_hit | T_and_T_plus_1 | 2026-06-11 no_hit | 2026-06-11 no_hit | searched_corporate_action_mirror_no_new_hard_signal | no_change | 除权转增为既有权益分派执行；无1.6T/CPO/FAU/ELS客户、订单、H股审批新增硬证据 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed_no_material_change | controller_open_web_only | CNINFO name/code no_hit | T_and_T_plus_1 | 2026-06-11 no_hit | 2026-06-11 no_hit | searched_h_share_mirrors_no_new_hard_signal | no_change | H股事项为既有公告延续；无AI数据中心电源客户、订单、收入占比、毛利率或交付节奏新增硬证据 | not_used_by_policy |

## reconciliation

- enabled_watchlist_count: 10
- completion_table_count: 10
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
- watchlist_last_update_date: 2026-06-11 for all enabled rows
- disabled_or_not_enabled_in_workbook: 002222.SZ, 300476.SZ, 603738.SH
