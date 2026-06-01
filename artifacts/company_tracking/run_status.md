# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-06-01
- run_started_at_beijing: 2026-06-01 20:33:14 +08:00
- run_finished_at_beijing: 2026-06-01 20:53:53 +08:00
- automation_id: a-grok
- enabled_company_count: 12
- completed_company_count: 12
- baseline_created_or_refreshed_count: 0
- multi_agent_status: completed
- worker_model_policy: model=gpt-5.5; reasoning_effort=xhigh; explicitly passed for each company worker
- logical_company_worker_limit: 6
- actual_company_workers_spawned: 12
- actual_company_workers_completed: 12
- grok_chrome_status: unavailable_no_callable_chrome_tool
- browser_substitution_policy: Browser/Playwright not used as Grok/X substitute
- open_web_fallback_status: searched_per_company_observation_only
- announcement_window_policy: T_and_T_plus_1 because run is after 20:00 Beijing time

## worker_batches

- batch_1: 002428.SZ, 002222.SZ, 300476.SZ, 603256.SH, 601869.SH, 301511.SZ
- batch_2: 002384.SZ, 300308.SZ, 688498.SH, 688668.SH, 300394.SZ, 603738.SH

## source_notes

- New official announcements appended: 301511.SZ 2026-06-01 subsidiary guarantee progress; 300308.SZ 2026-06-01 rumor clarification.
- New trading events appended: 002428.SZ 2026-06-01 LHB negative-deviation event; 002384.SZ 2026-06-01 LHB negative-deviation event; 002222.SZ 2026-06-01 block trade; 603738.SH 2026-06-01 block trade.
- New source-gap event appended: 002384.SZ 2026-06-01 interactive answer on AI PCB expansion progress, with no disclosed customer/order/revenue/capacity details.
- CNINFO/SSE/SZSE/Eastmoney/company IR checks found no new T/T+1 formal announcements for the remaining enabled companies.
- Several SZSE direct endpoints returned 500/503 or inconclusive results; workers cross-checked with CNINFO, Eastmoney notice mirror, company IR pages, SSE/HKEX where applicable, and Eastmoney trading APIs.
- Open-web fallback did not add standalone new observation-only items beyond official/trading-data events.

## completion_table

| ticker | name | batch_no | queue_status | browser_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | grok_status | open_web_fallback_status | state_change | miss_risk_notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_with_trading_event | no_callable_chrome_grok_tool | CNINFO/SZSE/公司公告/IR/Eastmoney mirror 2026-06-01~2026-06-02 zero | T_and_T_plus_1 | 2026-06-01 hit_negative_deviation | 2026-06-01 no_hit | unavailable_no_callable_chrome_tool | searched_no_new_operating_signal | lhb_appended | SZSE LHB endpoint 503; 以东方财富交易数据确认，需后续复核官方接口。 |
| 002222.SZ | 福晶科技 | 1 | completed_with_block_trade | no_callable_chrome_grok_tool | CNINFO/SZSE/公司IR/Eastmoney mirror 2026-06-01~2026-06-02 zero | T_and_T_plus_1 | 2026-06-01 no_hit | 2026-06-01 1_trade_appended | unavailable_no_callable_chrome_tool | searched_no_new_hard_signal | block_trade_appended | 小额平价大宗交易不等于 WSS/法拉第旋光片收入兑现。 |
| 300476.SZ | 胜宏科技 | 1 | completed_no_material_change | fallback_no_browser | CNINFO/Eastmoney/公司IR zero; SZSE annList 500 source_gap | T_and_T_plus_1 | 2026-06-01 no_hit | 2026-06-01 no_hit | unavailable_no_callable_chrome_tool | searched_observation_only_no_verified_new_operating_signal | no_change | open-web AI服务器PCB份额/客户说法未获官方确认。 |
| 603256.SH | 宏和科技 | 1 | completed_no_hard_event | fallback_no_browser | CNINFO/SSE/公司IR/Eastmoney mirror zero | T_and_T_plus_1 | 2026-06-01 no_hit | 2026-06-01 no_hit | unavailable_chrome_plugin_not_exposed | searched_market_observation_only | no_change | 二级网页显示板块下跌，不构成 Low-CTE/T-glass 订单或价格证据。 |
| 601869.SH | 长飞光纤 | 1 | completed_no_hard_event | no_callable_chrome_grok_tool | CNINFO/SSE/YOFC IR/HKEX/Eastmoney mirror zero | T_and_T_plus_1 | 2026-06-01 no_hit | 2026-06-01 no_hit | unavailable_no_callable_chrome_tool | searched_observation_only | no_change | 雪球/二级特种光纤讨论仅观察池，非官方披露。 |
| 301511.SZ | 德福科技 | 1 | completed_with_official_announcement | no_callable_chrome_grok_tool | CNINFO/SZSE/Eastmoney found 1 guarantee announcement | T_and_T_plus_1 | 2026-06-01 no_hit | 2026-06-01 no_hit | unavailable_no_callable_chrome_tool | searched_no_new_hvlp_rtf_hard_signal | guarantee_event_appended | CNINFO 代码查询漏检，以公司名、SZSE、东方财富交叉补足。 |
| 002384.SZ | 东山精密 | 2 | completed_with_trading_event_and_ir_gap | no_callable_chrome_grok_tool | CNINFO/Eastmoney zero; SZSE endpoint inconclusive | T_and_T_plus_1 | 2026-06-01 hit_negative_deviation | 2026-06-01 no_hit | unavailable_no_callable_chrome_tool | searched_no_new_operating_signal | lhb_and_ir_gap_appended | 互动易未答/保密类问题不能构成客户、订单或产能证据。 |
| 300308.SZ | 中际旭创 | 2 | completed_with_official_clarification | no_callable_chrome_grok_tool | CNINFO/Eastmoney found 1 rumor-clarification announcement; SZSE 500 | T_and_T_plus_1 | 2026-06-01 no_hit | 2026-06-01 no_hit | unavailable_no_callable_chrome_tool | searched_secondary_repeats_only | clarification_appended | 网传董事长演讲全文已被官方否认，应剔出证据池。 |
| 688498.SH | 源杰科技 | 2 | completed_no_material_change | no_callable_chrome_grok_tool | CNINFO/SSE STAR/company IR/Eastmoney mirror zero | T_and_T_plus_1 | 2026-06-01 no_hit | 2026-06-01 no_hit | unavailable_chrome_grok_not_callable | searched_no_new_hard_signal | no_change | 200G EML 仍待客户/订单/量产/收入披露。 |
| 688668.SH | 鼎通科技 | 2 | completed_no_material_change | no_callable_chrome_grok_tool | CNINFO/SSE/company IR/Eastmoney mirror zero | T_and_T_plus_1 | 2026-06-01 no_hit | 2026-06-01 no_hit | unavailable_no_callable_chrome_tool | searched_no_company_specific_hard_event | no_change | 2026-06-02 业绩说明会 Q&A 是下一关键来源。 |
| 300394.SZ | 天孚通信 | 2 | completed_no_material_change | no_callable_chrome_grok_tool | CNINFO/SZSE/HKEX/Eastmoney mirror zero | T_and_T_plus_1 | 2026-06-01 no_hit | 2026-06-01 no_hit | unavailable_no_callable_chrome_tool | searched_no_new_confirmed_event | no_change | H股申请仍无新进展；1.6T/CPO 订单和物料瓶颈未新增官方确认。 |
| 603738.SH | 泰晶科技 | 2 | completed_with_block_trade | no_callable_chrome_grok_tool | CNINFO/SSE/company website/Eastmoney mirror zero | T_and_T_plus_1 | 2026-06-01 no_hit | 2026-06-01 1_trade_appended | unavailable_no_callable_chrome_tool | searched_no_new_hard_signal | block_trade_appended | 官网科普文章不是 IR/公告；大宗交易金额偏小。 |

## reconciliation

- enabled_watchlist_count: 12
- completion_table_count: 12
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
