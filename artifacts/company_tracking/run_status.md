# Company Tracking Run Status

metadata:
- run_date: 2026-05-11
- run_time_beijing: 2026-05-11 20:12:48 +08:00
- run_type: multi_agent_daily_update
- status: completed_with_grok_unavailable_open_web_fallback
- company_count: 9
- baseline_created_count: 0
- daily_updated_count: 9
- watchlist_updated: true
- multi_agent_status: completed
- multi_agent_workers_successful: 9
- multi_agent_worker_errors: 0
- logical_batches: 2
- chrome_grok_status: unavailable_chrome_extension_backend_not_available
- chrome_probe_detail: "node_repl bootstrap retry returned Browser is not available: extension; local Chrome running; Codex Chrome Extension installed/enabled; native host manifest correct"
- open_web_fallback_status: completed_observation_only

## Summary

9 家 enabled 公司均已完成公司级 worker 跟踪研究。逻辑并行上限为 6；第一批 6 家完成后按槽位补入第二批 3 家。没有 enabled 公司遗漏，没有 company worker 失败。

Chrome/Grok 登录态浏览器后端不可用，错误为 `Browser is not available: extension`。只读检查显示本机 Chrome 正在运行、Codex Chrome Extension 已安装启用、native host manifest 正确，但当前会话仍无法取得 Chrome extension browser。全部公司已按规则改用普通 open-web fallback，且未把该结果标记为 Grok/X 或 Chrome 登录态结果。

本轮新增 2 条公司级硬事件：福晶科技 2026-05-11 股票交易异常波动公告，胜宏科技 2026-05-11 小额大宗交易。其余 7 家未发现新增公告、龙虎榜或大宗交易硬事件。日报、run_status 和 watchlist `last_update_date` 已更新。

## Files Updated

- `artifacts/company_tracking/2026-05-11.md`
- `artifacts/company_tracking/run_status.md`
- `watchlists/a_share_company_watchlist.xlsx`
- `artifacts/company_tracking/002222.SZ/events.jsonl`
- `artifacts/company_tracking/002222.SZ/state.md`
- `artifacts/company_tracking/300476.SZ/events.jsonl`
- `artifacts/company_tracking/300476.SZ/state.md`
- `C:\Users\Administrator\.codex\automations\a-grok\memory.md`

No Git backup was run, per user instruction.

## Per-company completion table

| ticker | name | batch_no | queue_status | browser_scope | announcements_checked | lhb_checked | block_trade_checked | grok_status | open_web_fallback_status | state_change | miss_risk_notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed | fallback_no_browser | checked_no_new | checked_no_new | checked_no_new | unavailable_chrome_extension_backend_not_available | searched_no_new_hard_signal | none | SZSE annList 仍有服务端错误风险；晚间公告可能滞后 |
| 002222.SZ | 福晶科技 | 1 | completed | fallback_no_browser | new_official_announcement_found | checked_no_new | checked_no_new | unavailable_chrome_extension_backend_not_available | searched_material_official_announcement_found | updated | CNINFO 未返回该公告，但 SZSE 官方公告已确认；open-web 只作观察层 |
| 300476.SZ | 胜宏科技 | 1 | completed | fallback_no_browser | checked_no_new | checked_empty | new_record_found | unavailable_chrome_extension_backend_not_available | searched_observation_only | updated | 小额大宗交易不能外推为基本面变化 |
| 603256.SH | 宏和科技 | 1 | completed_no_new_hard_event | fallback_no_browser | checked_no_new | checked_existing_2026_05_08_only | checked_no_new | unavailable_chrome_extension_backend_not_available | searched | none | 若 2026-05-11 盘后继续公告，下一轮需复扫 |
| 601869.SH | 长飞光纤 | 1 | done_no_new_material_event | fallback_no_browser | checked_no_new | checked_empty | checked_empty | unavailable_chrome_extension_backend_not_available | searched_no_new_hard_event | none | 公司官网/IR 与交易所披露可能有发布时间差 |
| 301511.SZ | 德福科技 | 1 | completed | fallback_no_browser | checked_no_new | checked_no_new | checked_no_new | unavailable_chrome_extension_backend_not_available | searched_with_observation_item | none | HVLP5 互动回复缺量化订单和收入证据；自媒体供应链说法未入账 |
| 002384.SZ | 东山精密 | 2 | completed_no_new_material_event | fallback_no_browser | checked_no_new | checked_no_new | checked_no_new | unavailable_chrome_extension_backend_not_available | searched_observation_pool_only | none | 5 月 15 日年度股东大会仍需后续关注 |
| 300308.SZ | 中际旭创 | 2 | completed_no_material_change | fallback_no_browser | checked_no_new | checked_empty | checked_empty | unavailable_chrome_extension_backend_not_available | searched_no_new_confirmed_signal | none | 深交所接口维护/50x，已用 CNINFO 与东方财富补位 |
| 688498.SH | 源杰科技 | 2 | done_no_material_change | fallback_no_browser | checked_no_new | checked_no_record | checked_no_record | unavailable_chrome_extension_backend_not_available | searched_no_new_hard_signal | none | 板块背景不等于源杰订单或客户验证 |

## Material Changes

- 福晶科技：新增 2026-05-11 官方异常波动公告。该公告确认 2026-05-06 至 2026-05-08 三个交易日收盘价格涨幅偏离值累计超过 20%，同时否认存在应披露未披露重大事项。性质是官方风险提示和交易热度确认，不是新增基本面利好。
- 胜宏科技：新增 2026-05-11 小额大宗交易，成交额 404.57 万元，折价约 24.14%。性质是硬交易数据，但规模很小，只作交易观察项。

## Trading-event highlights

- 福晶科技：本轮无新增龙虎榜或大宗交易；新增异常波动公告与 2026-05-08 高拥挤交易状态相互印证。
- 胜宏科技：新增 1 笔小额大宗交易；未发现新龙虎榜。
- 宏和科技：未发现 2026-05-11 新龙虎榜或大宗交易；2026-05-08 既有龙虎榜仍为近窗交易热度核心。
- 其余公司：本轮窗口无新增龙虎榜或大宗交易硬记录。

## Validation

- Enabled watchlist count: 9.
- Completion table count: 9.
- Missing enabled companies: none.
- JSONL validation: all company `events.jsonl` files parse successfully.
- Batch validation: batch 1 had 6 companies; batch 2 had 3 companies; all completed.
- Watchlist validation: enabled rows `last_update_date` set to 2026-05-11; `baseline_status` and `last_baseline_date` unchanged.
- Git backup: not run, per user instruction.

## Notes

Next high-value checks are 福晶科技异常波动后的监管/减持/资金退潮信号，胜宏科技 Q2 毛利率和 AI PCB 收入证据，云南锗业 2026-05-13 业绩说明会，德福科技 HVLP5 客户导入量化证据，以及宏和科技 Low CTE/高端电子布是否继续落到收入和现金流。
