# Company Tracking Run Status

metadata:
- run_date: 2026-05-09
- run_time_beijing: 2026-05-09 05:32:00 +08:00
- run_type: multi_agent_daily_update
- status: completed_with_grok_unavailable_open_web_fallback
- company_count: 9
- baseline_created_count: 0
- daily_updated_count: 9
- watchlist_updated: true
- multi_agent_status: completed_with_worker_restart
- multi_agent_workers_successful: 9
- multi_agent_worker_errors_restarted: 1
- logical_batches: 2
- chrome_grok_status: unavailable_chrome_tool_not_exposed
- open_web_fallback_status: completed

## Summary

9 家 enabled 公司均已完成日更。已使用多智能体公司 worker 执行公司级研究，逻辑并行上限为 6；第一批 6 家完成后补入第二批 3 家。东山精密首个 worker 被平台误判拦截，已关闭并重启完成。

`@chrome` / Grok 当前未暴露可调用工具，因此全部公司 Grok/X 标记为不可用。按用户新增规则，已对公司补做或由 worker 完成 Codex open-web fallback；该层已明确标为普通公开网页观察，不作为 Grok/X 或 Chrome 登录态结果。

## Files Updated

- `watchlists/a_share_company_watchlist.xlsx`
- `artifacts/company_tracking/2026-05-09.md`
- `artifacts/company_tracking/run_status.md`
- Per-company `state.md` / `events.jsonl` as applicable under `artifacts/company_tracking/<ticker>/`
- Automation prompts updated for multi-agent and open-web fallback requirements:
  - `docs/company_tracking/A_SHARE_COMPANY_TRACKING_PROMPT.md`
  - `docs/company_tracking/A_SHARE_COMPANY_TRACKING_AUTOMATION.md`
  - `C:\Users\Administrator\.codex\automations\a-grok\automation.toml`

## Per-company completion table

| ticker | name | batch_no | queue_status | browser_scope | announcements_checked | lhb_checked | block_trade_checked | grok_status | open_web_fallback_status | state_change | miss_risk_notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed_with_grok_unavailable | not_available | yes | yes | yes | unavailable_chrome_tool_not_exposed | searched/no_new_hard_signal | event_appended_state_updated | 深交所 annList 500；CNINFO+东方财富交叉验证 |
| 002222.SZ | 福晶科技 | 1 | completed_with_grok_unavailable | not_available | yes_no_new_announcement | yes_new_lhb | yes_no_block_trade | unavailable_chrome_tool_not_exposed | searched/no_new_hard_signal | event_appended_state_updated | 新增龙虎榜；不同口径不简单加总 |
| 300476.SZ | 胜宏科技 | 1 | completed_with_grok_unavailable | not_available | yes_ir_event | yes_no_record | yes_no_record | unavailable_chrome_tool_not_exposed | searched/confirmed_same_ir_event | event_appended_state_updated | IR 事件入账，未披露量化订单 |
| 603256.SH | 宏和科技 | 1 | completed_with_grok_unavailable | not_available | yes_abnormal_announcement | yes_new_lhb | yes_no_block_trade | unavailable_chrome_tool_not_exposed | searched/secondary_media_observation | events_appended_state_updated | 二级媒体观察不作为官方硬事实 |
| 601869.SH | 长飞光纤 | 1 | completed_with_grok_unavailable | not_available | yes_no_new | yes_no_record | yes_no_record | unavailable_chrome_tool_not_exposed | searched/secondary_research_only | state_updated_no_event | 公司官网 IR 直连被拒，需后续补查 |
| 301511.SZ | 德福科技 | 1 | completed_with_grok_unavailable | not_available | checked_no_new | checked_no_record | checked_no_record | unavailable_chrome_tool_not_exposed | searched/no_new_hard_signal | state_updated_no_event | 5/6 回购和龙虎榜在窗口外，未入账 |
| 002384.SZ | 东山精密 | 2 | completed_with_grok_unavailable | fallback_no_browser | checked_1_cninfo_new | checked_no_window_record | checked_no_window_record | unavailable_chrome_tool_not_exposed | searched | event_appended_state_updated | 首个 worker 误判拦截后重启 |
| 300308.SZ | 中际旭创 | 2 | completed_with_grok_unavailable_open_web_fallback | not_available | checked_11_cninfo_announcements | checked_no_record | checked_no_record | unavailable_chrome_tool_not_exposed | searched/no_signal | event_appended_state_updated | 官方股权激励事项入账 |
| 688498.SH | 源杰科技 | 2 | completed_with_grok_unavailable_open_web_fallback | not_available | yes_no_new | yes_no_record | yes_no_record | unavailable_chrome_tool_not_exposed | searched/no_signal | state_updated_no_event | 无新增硬事件 |

## Validation

- Enabled watchlist count: 9.
- Completion table count: 9.
- Missing enabled companies: none.
- JSONL validation: all company `events.jsonl` files parse successfully.
- Batch validation: batch 1 had 6 companies; batch 2 had 3 companies; all completed.
- Git backup: not run, per user instruction.

## Notes

Companies completed before the open-web fallback rule was added were supplemented by the controller with `open_web_fallback` notes in their `state.md`. Future runs should have each worker perform that fallback directly when Chrome/Grok is unavailable.
