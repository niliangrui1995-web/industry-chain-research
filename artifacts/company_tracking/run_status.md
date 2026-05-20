# Company Tracking Run Status

metadata:
- run_date: 2026-05-19
- run_start_time_beijing: 2026-05-19 20:03:13 +08:00
- run_closeout_time_beijing: 2026-05-19 20:21:26 +08:00
- run_type: multi_agent_daily_update_after_20_00
- status: completed_with_one_worker_timeout_controller_completed_grok_unavailable_open_web_fallback
- company_count: 11
- baseline_created_count: 0
- daily_updated_count: 11
- watchlist_updated: true
- multi_agent_status: completed_with_timeout_fallback
- multi_agent_workers_spawned: 11
- multi_agent_workers_successful: 10
- multi_agent_worker_timeouts: 1
- logical_batches: 2
- worker_model_policy: gpt-5.5 / reasoning_effort=xhigh, explicitly passed at spawn
- chrome_grok_status: unavailable_chrome_plugin_not_exposed
- chrome_probe_detail: "Chrome/@chrome plugin tool surface was not exposed in this automation turn; no Browser Use or Playwright fallback was used as a substitute for logged-in Chrome/Grok"
- open_web_fallback_status: completed_observation_only
- announcement_window_policy: after_20_00_all_companies_T_and_T_plus_1

## Summary

11 家 enabled 公司均已启动独立公司 worker，按最多 6 个公司 worker 并行调度。10 个 worker 正常返回；`002384.SZ` 东山精密 worker 超时并被关闭，已由总控按独立公司任务块补做公告、龙虎榜、大宗交易和 open-web fallback 核对。

本轮完成 2026-05-19 20:00 后 T/T+1 公告硬门。新增或确认 7 个可入账/校正事件：德福科技权益分派实施、云南锗业一笔大宗交易、胜宏科技 2026-05-15 IR 官方源校正、胜宏科技 H 股稳定价格期结束、宏和科技 H 股递表、长飞光纤业绩说明会预告、鼎通科技权益分派实施、天孚通信两笔大宗交易。其他公司未发现高于既有基线和上轮状态的新硬经营事件。

## Files Updated

- `artifacts/company_tracking/2026-05-19.md`
- `artifacts/company_tracking/run_status.md`
- `artifacts/company_tracking/002428.SZ/events.jsonl`
- `artifacts/company_tracking/002428.SZ/state.md`
- `artifacts/company_tracking/301511.SZ/events.jsonl`
- `artifacts/company_tracking/301511.SZ/state.md`
- `artifacts/company_tracking/300476.SZ/events.jsonl`
- `artifacts/company_tracking/300476.SZ/state.md`
- `artifacts/company_tracking/300394.SZ/events.jsonl`
- `artifacts/company_tracking/300394.SZ/state.md`
- `artifacts/company_tracking/688668.SH/events.jsonl`
- `artifacts/company_tracking/688668.SH/state.md`
- `artifacts/company_tracking/601869.SH/state.md`
- `artifacts/company_tracking/603256.SH/state.md`
- `artifacts/company_tracking/002384.SZ/state.md`
- `artifacts/company_tracking/300308.SZ/state.md`
- `artifacts/company_tracking/688498.SH/state.md`

## Material changes

- `603256.SH` 宏和科技：H 股递表及申请资料刊发，资本运作进度更新，不等同于电子布/Low CTE 订单兑现。
- `300476.SZ` 胜宏科技：H 股稳定价格期结束，交易结构事件；2026-05-15 IR source gap 升级为官方源确认，但未新增订单/客户/收入占比量化。
- `300394.SZ` 天孚通信：2026-05-19 两笔大宗交易合计 100,262,400 元，交易结构信号。
- `002428.SZ` 云南锗业：2026-05-19 一笔大宗交易 13,588,500 元，小额平价交易结构信号。
- `301511.SZ` 德福科技：2025 年度权益分派实施公告，股权登记日 2026-05-25，除权除息日 2026-05-26。
- `601869.SH` 长飞光纤：2026-05-22 业绩说明会预告，IR日程事件。
- `688668.SH` 鼎通科技：2025年年度权益分派实施公告，分红日程事件。

## Per-company completion table

| ticker | name | batch_no | queue_status | browser_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | grok_status | open_web_fallback_status | state_change | miss_risk_notes |
|---|---|---:|---|---|---|---|---|---|---|---|---|---|
| 002428.SZ | 云南锗业 | 1 | completed_with_block_trade | fallback_no_browser | checked_2026-05-19_to_2026-05-20_no_new | T_and_T_plus_1 | checked_2026-05-19_no_record | checked_2026-05-19_one_record_amount_13.5885m | unavailable_chrome_plugin_not_exposed | searched_observation_only_no_new_hard_signal | updated_events_and_state | 小额平价大宗交易为交易结构信号，不证明InP/GaAs经营兑现 |
| 002222.SZ | 福晶科技 | 1 | completed_no_material_change | fallback_no_browser | checked_2026-05-19_to_2026-05-20_no_new | T_and_T_plus_1 | checked_2026-05-19_no_record | checked_2026-05-19_no_record | unavailable_chrome_plugin_not_exposed | searched_no_new_hard_signal | none | 2026-05-20股东会后若晚间/次日披露决议，需下一轮补扫 |
| 300476.SZ | 胜宏科技 | 1 | completed_with_source_gap_closed | fallback_no_browser | checked_2026-05-19_to_2026-05-20_no_new_after_2026-05-18_stabilization_notice | T_and_T_plus_1 | checked_2026-05-19_no_record | checked_2026-05-19_no_record | unavailable_chrome_plugin_not_exposed | searched_observation_only_official_ir_source_found | updated_events_and_state | 5月15日IR源头已升级为官方确认；仍无订单/客户/收入占比量化 |
| 603256.SH | 宏和科技 | 1 | completed_with_official_event | fallback_no_browser | checked_2026-05-19_to_2026-05-20_no_new_after_H_share_application | T_and_T_plus_1 | checked_2026-05-19_no_record | checked_2026-05-19_no_record | unavailable_chrome_plugin_not_exposed | searched_no_new_hard_fact_beyond_H_share_application | updated_state_only | H股递表为资本运作进展，不证明电子布/Low CTE订单或认证兑现 |
| 601869.SH | 长飞光纤 | 1 | completed_with_official_event | fallback_no_browser | checked_2026-05-19_to_2026-05-20_found_results_briefing_notice_no_T_plus_1_new | T_and_T_plus_1 | checked_2026-05-19_no_record | checked_2026-05-19_no_record | unavailable_chrome_plugin_not_exposed | searched_observation_only_fiber_price_discussion | updated_state_only | 光棒/光纤涨价讨论为二级媒体观察，需会后问答和财报验证 |
| 301511.SZ | 德福科技 | 1 | completed_with_official_event | fallback_no_browser | checked_2026-05-19_to_2026-05-20_found_2026-05-20_dividend_implementation | T_and_T_plus_1 | checked_2026-05-19_no_record | checked_2026-05-19_no_record | unavailable_chrome_plugin_not_exposed | searched_observation_only_no_new_HVLP_RTF_signal | updated_events_and_state | 权益分派为分红日程，不改变HVLP/RTF主线；6月4日起减持期需跟踪 |
| 002384.SZ | 东山精密 | 2 | worker_timeout_controller_completed | fallback_no_browser | controller_checked_2026-05-19_to_2026-05-20_no_new | T_and_T_plus_1 | controller_checked_2026-05-19_no_record | controller_checked_2026-05-19_no_record | unavailable_chrome_plugin_not_exposed | searched_no_new_hard_signal | updated_state_only | 公司worker超时后总控补做；未发现索尔思/AI PCB新硬披露 |
| 300308.SZ | 中际旭创 | 2 | completed_no_material_change | fallback_no_browser | checked_2026-05-19_to_2026-05-20_no_new | T_and_T_plus_1 | checked_2026-05-19_no_record | checked_2026-05-19_no_record | unavailable_chrome_plugin_not_exposed | searched_observation_only_high_price_volatility | updated_state_only | open-web仅见行情波动，不构成1.6T/800G经营硬证据 |
| 688498.SH | 源杰科技 | 2 | completed_no_material_change | fallback_no_browser | checked_2026-05-19_to_2026-05-20_no_new | T_and_T_plus_1 | checked_2026-05-19_no_record | checked_2026-05-19_no_record | unavailable_chrome_plugin_not_exposed | searched_no_new_confirmed_signal | updated_state_only | 2026-05-20业绩说明会仍待会后纪要或问答 |
| 688668.SH | 鼎通科技 | 2 | completed_with_official_event | fallback_no_browser | checked_2026-05-19_to_2026-05-20_found_dividend_implementation_no_T_plus_1_new | T_and_T_plus_1 | checked_2026-05-19_no_record | checked_2026-05-19_no_record | unavailable_chrome_plugin_not_exposed | completed_observation_only_no_new_business_evidence | updated_events_and_state | 权益分派为分红日程，不构成高速连接器/液冷/客户订单新证据 |
| 300394.SZ | 天孚通信 | 2 | completed_with_block_trade | fallback_no_browser | checked_2026-05-19_to_2026-05-20_no_new_official_ir | T_and_T_plus_1 | checked_2026-05-19_no_record | checked_2026-05-19_two_records_amount_100.2624m | unavailable_chrome_plugin_not_exposed | searched_market_chatter_only_no_hard_company_event | updated_events_and_state | 两笔大宗交易为交易结构信号；CPO小作文/论坛传言不入确认事实 |

## Final validation

- enabled watchlist count: 11
- completion table count: 11
- missing enabled companies: none
- batch validation: batch 1 covered 6 companies; batch 2 covered 5 companies; no enabled company was left unstarted
- worker timeout fallback: `002384.SZ` 东山精密 worker timed out; controller completed isolated task block
- announcement windows: all rows `T_and_T_plus_1`
- JSONL validation: all company `events.jsonl` files parse successfully
- Git backup: not run
