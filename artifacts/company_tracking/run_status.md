# Company Tracking Run Status

metadata:
- run_date: 2026-05-15
- run_time_beijing: 2026-05-15 20:18:34 +08:00
- run_type: multi_agent_daily_update_with_controller_fallback
- status: completed_with_grok_unavailable_open_web_fallback
- company_count: 11
- baseline_created_count: 0
- daily_updated_count: 11
- watchlist_updated: true
- multi_agent_status: completed_with_controller_fallback_for_4_worker_timeouts
- multi_agent_workers_successful: 7
- multi_agent_worker_timeouts: 4
- logical_batches: 2
- chrome_grok_status: unavailable_chrome_plugin_not_exposed
- chrome_probe_detail: "Chrome/@chrome plugin tool surface was not exposed in this automation turn; no Browser Use or Playwright fallback was used as a substitute for logged-in Chrome/Grok"
- open_web_fallback_status: completed_observation_only

## Summary

11 家 enabled 公司已全部完成本轮日更。逻辑并行上限仍按 6 个公司 worker 执行：batch 1 的 6 家均已启动并完成，batch 2 的 5 家也全部启动；其中 4 家 worker 在合理时间内未回传，主控已按官方公告、CNINFO 与东方财富交易接口补全，不留 completion 缺口。

本轮有 3 家公司出现实质增量：云南锗业新增确认 `2026-05-13` 业绩说明会官方 IR 记录已落地，且晚间补扫确认公告日期为 `2026-05-16` 的 `2025年年度股东会决议公告` 和股东会法律意见书；福晶科技 `2026-05-15` 新增 1 笔平价大宗交易；中际旭创 `2026-05-15` 新增 1 笔机构对机构小额大宗交易。其余 8 家未发现高于既有基线和上一轮状态的新硬经营事件。

correction_note:
- 2026-05-15 20:30 后按用户提示补扫 CNINFO 公司名检索，发现云南锗业两份公告落在 `2026-05-16` 公告日期下。原日更按 `2026-05-15` 自然日查询会漏掉晚间跨日公告，已补入日报、state 和 events。

## Files Updated

- `artifacts/company_tracking/2026-05-15.md`
- `artifacts/company_tracking/run_status.md`
- `watchlists/a_share_company_watchlist.xlsx`
- `artifacts/company_tracking/002428.SZ/events.jsonl`
- `artifacts/company_tracking/002428.SZ/state.md`
- `artifacts/company_tracking/002222.SZ/events.jsonl`
- `artifacts/company_tracking/002222.SZ/state.md`
- `artifacts/company_tracking/300308.SZ/events.jsonl`
- `artifacts/company_tracking/300308.SZ/state.md`

## Per-company completion table

| ticker | name | batch_no | queue_status | browser_scope | announcements_checked | lhb_checked | block_trade_checked | grok_status | open_web_fallback_status | state_change | miss_risk_notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | corrected_after_evening_cninfo_rescan | fallback_no_browser | added_2026-05-16_agm_resolution_and_legal_opinion; confirmed_2026-05-13_ir_record | checked_no_new | checked_no_new | unavailable_chrome_plugin_not_exposed | searched_no_new_hard_signal | updated_event_and_state | 晚间公告日期跨到2026-05-16；IR全文未抽取；客户/订单/良率仍缺硬证据 |
| 002222.SZ | 福晶科技 | 1 | completed_worker_returned | fallback_no_browser | checked_no_new_official | checked_no_new | added_1_block_trade_2026-05-15 | unavailable_chrome_plugin_not_exposed | searched_no_new_hard_signal | updated_event_and_state | 新增仅为交易层平价大宗交易；IR页仍有轻微延迟风险 |
| 300476.SZ | 胜宏科技 | 1 | completed_worker_returned_partial_gaps | fallback_no_browser | partial_cross_checked_no_new | checked_no_new | checked_no_new | unavailable_chrome_plugin_not_exposed | partial_timeout_not_retried_no_signal | none | CNINFO定向过滤异常；官网IR抓取不稳定 |
| 603256.SH | 宏和科技 | 1 | completed_worker_returned | fallback_no_browser | checked_no_new_after_2026-05-13 | checked_no_new | checked_no_new | unavailable_chrome_plugin_not_exposed | searched_no_new_hard_signal | none | 最新有效硬信息仍是5月13日减持结果公告 |
| 601869.SH | 长飞光纤 | 1 | completed_worker_returned | fallback_no_browser | checked_no_new | checked_no_new | checked_no_new | unavailable_chrome_plugin_not_exposed | searched_no_new_hard_signal | none | 中文IR页直连失败；H股侧未结构化复扫 |
| 301511.SZ | 德福科技 | 1 | completed_worker_returned_partial_gaps | fallback_no_browser | checked_no_new_official | checked_no_new | checked_no_new | unavailable_chrome_plugin_not_exposed | searched_no_new_hard_signal | none | IR iframe未深挖；官网超时 |
| 002384.SZ | 东山精密 | 2 | completed_controller_fallback_after_worker_timeout | fallback_no_browser | controller_checked_no_new_official | checked_no_new | checked_no_new | unavailable_chrome_plugin_not_exposed | searched_no_new_hard_signal | none | worker超时后主控回补；CNINFO过滤噪声与官网IR缺口仍在 |
| 300308.SZ | 中际旭创 | 2 | completed_controller_fallback_after_worker_timeout | fallback_no_browser | controller_checked_no_new_official | checked_no_new | added_1_block_trade_2026-05-15 | unavailable_chrome_plugin_not_exposed | searched_trading_event_only | updated_event_and_state | worker超时后主控回补；新增仅为小额机构大宗交易 |
| 688498.SH | 源杰科技 | 2 | completed_worker_returned_partial_gaps | fallback_no_browser | checked_no_new_with_sse_timeout | checked_no_new | checked_no_new | unavailable_chrome_plugin_not_exposed | searched_no_material_signal | none | 上交所源站超时；5月20日说明会仍是下一验证窗口 |
| 688668.SH | 鼎通科技 | 2 | completed_controller_fallback_after_worker_timeout | fallback_no_browser | controller_checked_no_new_official | checked_no_new | checked_no_new | unavailable_chrome_plugin_not_exposed | searched_no_new_hard_signal | none | worker超时后主控回补；可转债注册与224G/液冷兑现待跟踪 |
| 300394.SZ | 天孚通信 | 2 | completed_controller_fallback_after_worker_timeout | fallback_no_browser | controller_checked_no_new_after_2026-05-14_ir | checked_no_new | checked_no_new | unavailable_chrome_plugin_not_exposed | searched_no_new_hard_signal | none | worker超时后主控回补；5月14日IR后暂无新量化披露 |

## Additional announcement rescan correction

- Rescan scope: after the user flagged missed announcements, all 11 enabled companies were rechecked company-by-company through CNINFO company-name search for `2026-05-15~2026-05-16`, covering evening disclosures whose announcement date rolled to the next day.
- No additional announcements found in the rescan window: 002222.SZ 福晶科技, 300476.SZ 胜宏科技, 601869.SH 长飞光纤, 688668.SH 鼎通科技, 300394.SZ 天孚通信.
- Additional affected files: `artifacts/company_tracking/603256.SH/events.jsonl`, `artifacts/company_tracking/603256.SH/state.md`, `artifacts/company_tracking/301511.SZ/events.jsonl`, `artifacts/company_tracking/301511.SZ/state.md`, `artifacts/company_tracking/002384.SZ/events.jsonl`, `artifacts/company_tracking/002384.SZ/state.md`, `artifacts/company_tracking/688498.SH/events.jsonl`, `artifacts/company_tracking/688498.SH/state.md`.

### Corrected rows from evening announcement rescan

| ticker | name | correction_status | announcements_checked | state_change | miss_risk_notes |
| --- | --- | --- | --- | --- | --- |
| 603256.SH | 宏和科技 | corrected_after_evening_cninfo_rescan | added_2026-05-16_agm_resolution_and_legal_opinion | updated_event_and_state | 股东会/授信担保/独董补选类公告；非经营兑现 |
| 301511.SZ | 德福科技 | corrected_after_evening_cninfo_rescan | added_2026-05-15_agm_resolution_and_legal_opinion | updated_event_and_state | 股东会/分红方案类公告；非 HVLP/RTF 兑现 |
| 002384.SZ | 东山精密 | corrected_after_evening_cninfo_rescan | added_5_governance_and_board_transition_announcements | updated_event_and_state | 换届和 Multek 治理观察点；非订单/收入兑现 |
| 300308.SZ | 中际旭创 | corrected_after_evening_cninfo_rescan | added_2026-05-15_investor_relations_record | updated_event_and_state | IR 有经营口径但无量化指引；较大宗交易更重要 |
| 688498.SH | 源杰科技 | corrected_after_evening_cninfo_rescan | added_vp_unable_to_perform_and_dismissal_announcement | updated_event_and_state | 销售营销条线风险事件；官方称不影响经营 |
