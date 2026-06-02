# A股公司持续跟踪 run_status

## latest_run

- run_date: 2026-06-02
- run_started_at_beijing: 2026-06-02 20:33:56 +08:00
- run_finished_at_beijing: 2026-06-02 20:57:55 +08:00
- automation_id: a-grok
- enabled_company_count: 12
- completed_company_count: 12
- baseline_created_or_refreshed_count: 0
- multi_agent_status: completed_with_one_worker_timeout_controller_fallback
- worker_model_policy: model=gpt-5.5; reasoning_effort=xhigh; explicitly passed for each company worker
- logical_company_worker_limit: 6
- actual_company_workers_spawned: 12
- actual_company_workers_completed: 11
- actual_company_workers_timed_out: 1
- controller_fallback_companies: 688668.SH
- grok_chrome_status: unavailable_no_callable_chrome_tool
- browser_substitution_policy: Browser/Playwright not used as Grok/X substitute
- open_web_fallback_status: searched_per_company_observation_only
- announcement_window_policy: T_and_T_plus_1 because run is after 20:00 Beijing time

## worker_batches

- batch_1: 002428.SZ, 002222.SZ, 300476.SZ, 603256.SH, 601869.SH, 301511.SZ
- batch_2: 002384.SZ, 300308.SZ, 688498.SH, 688668.SH, 300394.SZ, 603738.SH

## source_notes

- New official announcements appended: 301511.SZ 2026-06-02 buyback progress; 603256.SH 2026-06-03 dividend implementation; 002384.SZ 2026-06-03 controlling-shareholder pledge/release.
- New trading events appended: 603256.SH 2026-06-02 LHB amplitude event; 002384.SZ 2026-06-02 LHB gain-deviation event.
- No new block trades were found for any enabled company on 2026-06-02.
- 688668.SH company worker timed out and was closed; the controller completed the isolated company task block with CNINFO/SSE/Eastmoney trading feeds and open-web fallback, finding no material event.
- Open-web fallback did not add standalone new observation-only items beyond official/trading-data events.

## completion_table

| ticker | name | batch_no | queue_status | browser_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | grok_status | open_web_fallback_status | state_change | miss_risk_notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_no_material_change | no_callable_chrome_grok_tool | CNINFO/SZSE/company IR/Eastmoney zero 2026-06-02~2026-06-03 | T_and_T_plus_1 | 2026-06-02 no_hit | 2026-06-02 no_hit | unavailable_no_callable_chrome_tool | searched_observation_only | no_change | 无新增 InP/锗资源/产能/订单硬证据；2026-06-01 龙虎榜仍按前一日事件跟踪。 |
| 002222.SZ | 福晶科技 | 1 | completed_no_material_change | no_callable_chrome_grok_tool | CNINFO/SZSE/company IR/Eastmoney zero 2026-06-02~2026-06-03 | T_and_T_plus_1 | 2026-06-02 no_hit | 2026-06-02 no_hit | unavailable_no_callable_chrome_tool | searched_observation_only | no_change | 未发现 WSS/法拉第旋光片/晶体订单或扩产新增硬披露；前日小额大宗不重复。 |
| 300476.SZ | 胜宏科技 | 1 | completed_no_material_change | no_callable_chrome_grok_tool | CNINFO/Eastmoney/company IR zero; SZSE annList 500 source_gap | T_and_T_plus_1 | 2026-06-02 no_hit | 2026-06-02 no_hit | unavailable_no_callable_chrome_tool | searched_observation_only | no_change | open-web 仅有二级研究/行情复述，未确认海外客户、订单、产能或毛利率新信息。 |
| 603256.SH | 宏和科技 | 1 | completed_with_official_announcement_and_lhb | no_callable_chrome_grok_tool | CNINFO/SSE/Eastmoney found dividend implementation announcement | T_and_T_plus_1 | 2026-06-02 hit_amplitude_lhb | 2026-06-02 no_hit | unavailable_no_callable_chrome_tool | searched_observation_only | dividend_and_lhb_appended | 权益分派不是 Low CTE/T-glass 订单或涨价；龙虎榜属于交易拥挤度信号。 |
| 601869.SH | 长飞光纤 | 1 | completed_no_material_change | no_callable_chrome_grok_tool | CNINFO/SSE/YOFC IR/HKEX/Eastmoney zero | T_and_T_plus_1 | 2026-06-02 no_hit | 2026-06-02 no_hit | unavailable_no_callable_chrome_tool | searched_observation_only | no_change | 未发现数据中心光纤、海外扩张、特种光纤新公告或交易事件。 |
| 301511.SZ | 德福科技 | 1 | completed_with_official_announcement | no_callable_chrome_grok_tool | CNINFO found buyback progress; SZSE annList 500; Eastmoney mirror lagged | T_and_T_plus_1 | 2026-06-02 no_hit | 2026-06-02 no_hit | unavailable_no_callable_chrome_tool | searched_observation_only | repurchase_progress_appended | 回购进展不构成 HVLP/RTF 客户认证、批量订单、收入占比或毛利率兑现。 |
| 002384.SZ | 东山精密 | 2 | completed_with_official_announcement_and_lhb | no_callable_chrome_grok_tool | CNINFO found controlling-shareholder pledge/release announcement; SZSE annList 50x | T_and_T_plus_1 | 2026-06-02 hit_gain_deviation_lhb | 2026-06-02 no_hit | unavailable_no_callable_chrome_tool | searched_observation_only | pledge_and_lhb_appended | 质押置换不涉及新增融资；龙虎榜说明交易波动，非 AI PCB/索尔思经营兑现。 |
| 300308.SZ | 中际旭创 | 2 | completed_no_material_change | no_callable_chrome_grok_tool | CNINFO/SZSE/company IR/Eastmoney zero; latest remains 2026-06-01 clarification | T_and_T_plus_1 | 2026-06-02 no_hit | 2026-06-02 no_hit | unavailable_no_callable_chrome_tool | searched_observation_only | no_change | 未发现 1.6T、硅光、客户需求、物料或毛利率新硬披露。 |
| 688498.SH | 源杰科技 | 2 | completed_no_material_change | no_callable_chrome_grok_tool | CNINFO/SSE STAR/company IR/Eastmoney zero | T_and_T_plus_1 | 2026-06-02 no_hit | 2026-06-02 no_hit | unavailable_no_callable_chrome_tool | searched_observation_only | no_change | 200G EML、AI客户验证、订单、量产和收入占比仍无新增官方确认。 |
| 688668.SH | 鼎通科技 | 2 | completed_by_controller_fallback_after_worker_timeout | no_callable_chrome_grok_tool | CNINFO/SSE/Eastmoney zero; open-web found only prior 2025/2026Q1 performance-briefing announcement and older refinancing materials | T_and_T_plus_1 | 2026-06-02 no_hit | 2026-06-02 no_hit | unavailable_no_callable_chrome_tool | searched_controller_fallback_observation_only | no_change | 公司 worker 超时后由总控补做独立任务块；无新增高速连接器/铜缆/客户/订单硬证据。 |
| 300394.SZ | 天孚通信 | 2 | completed_no_material_change | no_callable_chrome_grok_tool | CNINFO/SZSE/company IR/HKEX zero | T_and_T_plus_1 | 2026-06-02 no_hit | 2026-06-02 no_hit | unavailable_no_callable_chrome_tool | searched_observation_only | no_change | 未发现 1.6T/CPO/FAU/ELS、泰国产能、H股进展或物料供应新硬披露。 |
| 603738.SH | 泰晶科技 | 2 | completed_no_material_change | no_callable_chrome_grok_tool | CNINFO/SSE/company website/Eastmoney zero | T_and_T_plus_1 | 2026-06-02 no_hit | 2026-06-02 no_hit | unavailable_no_callable_chrome_tool | searched_observation_only | no_change | 未发现晶振/TCXO/OCXO 客户验证、价格、产能或交易新事件。 |

## reconciliation

- enabled_watchlist_count: 12
- completion_table_count: 12
- missing_enabled_tickers: none
- baseline_pending_or_refresh_needed: none
