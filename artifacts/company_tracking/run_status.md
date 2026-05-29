# Company Tracking Run Status

metadata:

- run_date: 2026-05-29
- run_start_time_beijing: 2026-05-29 20:33:29 +08:00
- run_closeout_time_beijing: 2026-05-29 21:09 +08:00
- run_type: multi_agent_daily_update_evening_T_T_plus_1_closeout
- status: completed_T_and_T_plus_1_no_missing_enabled_company
- watchlist_updated: true
- company_count: 12
- baseline_created_count: 0
- daily_updated_count: 12
- logical_batches: 2
- multi_agent_status: completed
- multi_agent_workers_spawned: 12
- multi_agent_workers_successful: 12
- worker_model_policy: gpt-5.5 / reasoning_effort=xhigh, explicitly passed at spawn
- chrome_grok_status: unavailable_no_callable_chrome_or_grok_tool_namespace
- open_web_fallback_status: completed_or_recorded_observation_only_by_company
- announcement_window_policy: post_20_00_all_companies_T_and_T_plus_1_checked

## Material changes

- `301511.SZ` 德福科技：新增 2026 年限制性股票激励计划草案，授予 176.8 万股、授予价 56.56 元/股、激励对象 56 人，并披露 2026-2028 年铜箔销量 16/18/20 万吨、净利润 6/10/15 亿元的公司层面考核目标。该事件新增销量/利润考核锚，不构成 HVLP/RTF 客户认证、订单、收入占比或毛利率兑现。
- `002384.SZ` 东山精密：新增控股股东部分股份质押、解除质押及质押展期公告；公司称系置换前期质押、不涉及新增融资、不存在平仓风险、不导致控制权变更。新增互动易对苏州易缆微合作的商业保密回复，强化 source gap。
- `603256.SH` 宏和科技：新增 SSE/CSI 官方指数调整事件，宏和科技调入上证380，2026-06-12 收市后生效。属于交易结构/被动资金观察，不是经营基本面披露。
- `603738.SH` 泰晶科技：新增 2026-05-29 龙虎榜，因日价格振幅达到15%上榜，前五净卖出约 1,604.45 万元。属于交易拥挤度和资金分歧事件，不改变 AI 光模块晶振商业化证据边界。
- `002222.SZ` 福晶科技：新增 1 笔小额平价大宗交易，成交额 201.12 万元。open-web 发现法拉第旋光片收入占比/产能爬坡的二级媒体线索，但未找到官方原文，暂为 observation-only。
- `300308.SZ` 中际旭创：新增 3 笔小额平价大宗交易，合计 1,288.89 万元。2026-05-29 股权激励归属结果公告已由上一轮 T+1 入账，本轮确认不重复追加。

## Announcement And Trading Highlights

- Announcement window: all 12 enabled companies were checked after 20:00 Beijing time for announcement dates `2026-05-29` and `2026-05-30`; every completion row records `announcement_window_checked=T_and_T_plus_1`.
- Dragon-tiger list: `603738.SH` 泰晶科技 had a new 2026-05-29 LHB record. No other enabled company had a new 2026-05-29 record in completed checks.
- Block trades: `002222.SZ` had one 2026-05-29 flat block trade; `300308.SZ` had three 2026-05-29 flat block trades. No other enabled company had a 2026-05-29 block-trade addition in completed checks.
- Baseline: no baseline was created or refreshed.

## Grok/X And Fallback Status

- Multi-agent tools were available and used. Twelve company workers were spawned with explicit `model="gpt-5.5"` and `reasoning_effort="xhigh"`, with maximum logical concurrency of 6.
- Chrome/Grok callable tools were not exposed in this run, so no logged-in Chrome/Grok or X-native result was collected.
- No Browser Use or Playwright substitute was used as a Grok/X replacement.
- Open-web fallback was used or recorded per company as observation-only. No social/open-web item was promoted to confirmed fact without official disclosure, exchange data, company IR, or reputable source confirmation.

## Baseline Changes And Source Gaps

- Baseline updates: none.
- Primary timing gate closed for this run: all enabled companies were scanned for `2026-05-29` plus T+1 `2026-05-30` announcement dates. Later overnight disclosures after closeout remain next-run scope.
- SZSE source gaps: several SZSE announcement or trading endpoints returned 50x/maintenance responses. Company workers used CNINFO, company pages, SSE, Eastmoney trading APIs, P5W/互动易, HKEX, official index pages, and open-web observation as cross-checks.
- `301511.SZ`: CNINFO ticker query missed the new incentive announcements, while company-name query and SZSE stock query found them. Future scans should retain company-name + ticker/SZSE dual path.
- `002222.SZ`: e公司法拉第旋光片线索 is observation-only until an official IR, CNINFO, SZSE, or company source is found.

## Per-company completion table

| ticker | name | batch_no | queue_status | browser_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | grok_status | open_web_fallback_status | state_change | miss_risk_notes |
|---|---|---:|---|---|---|---|---|---|---|---|---|---|
| 002428.SZ | 云南锗业 | 1 | completed_no_material_change | fallback_no_browser | checked_2026-05-29_to_2026-05-30_no_new | T_and_T_plus_1 | checked_2026-05-29_no_record | checked_2026-05-29_no_record | unavailable_no_callable_chrome_tool | searched_observation_only_turnover_lead | no_formal_state_change | 高成交观察不构成客户/订单/良率/利润证据 |
| 002222.SZ | 福晶科技 | 1 | completed_with_block_trade | fallback_no_browser | checked_no_new_formal_notice | T_and_T_plus_1 | checked_2026-05-29_no_record | checked_2026-05-29_found_2m_flat_block_trade | unavailable_no_callable_chrome_tool | searched_observation_only_secondary_lead | updated_events_and_state | e公司法拉第线索缺官方原文；SZSE annList 50x |
| 300476.SZ | 胜宏科技 | 1 | completed_no_material_change | fallback_no_browser | checked_no_new_cninfo_company_site | T_and_T_plus_1 | checked_2026-05-29_no_record | checked_2026-05-29_no_record | unavailable_no_callable_chrome_tool | searched_no_new_verified_operating_signal | no_change | SZSE接口50x；高成交不等于订单/毛利率证据 |
| 603256.SH | 宏和科技 | 1 | completed_with_index_event | fallback_no_browser | checked_no_new_company_announcement | T_and_T_plus_1 | checked_2026-05-29_no_record | checked_2026-05-29_no_record | unavailable_no_callable_chrome_tool | searched_found_official_index_event | updated_events_and_state | 上证380调入为交易结构事件，不是经营披露 |
| 601869.SH | 长飞光纤 | 1 | completed_no_formal_change | fallback_no_browser | checked_no_new_a_h_notice | T_and_T_plus_1 | checked_2026-05-29_no_record | checked_2026-05-29_no_record | unavailable_no_callable_chrome_tool | searched_useful_observation_only | no_formal_state_change | MSCI/行情为观察层，不并入公司事实 |
| 301511.SZ | 德福科技 | 1 | completed_with_material_official_event | fallback_no_browser | checked_found_8_official_2026-05-29 | T_and_T_plus_1 | checked_2026-05-29_no_record | checked_2026-05-29_no_record | unavailable_no_callable_chrome_tool | searched_no_new_hard_signal_beyond_official | updated_events_and_state | CNINFO代码查询漏报，需保留公司名+SZSE双路径 |
| 002384.SZ | 东山精密 | 2 | completed_with_governance_event | not_available_no_callable_chrome_tool | checked_found_2026-05-30_pledge_notice | T_and_T_plus_1 | checked_2026-05-29_no_record | checked_2026-05-29_no_record | unavailable_no_callable_chrome_tool | searched_no_unverified_material_signal | updated_events_and_state | 互动易仍是商业保密边界；AI主线待硬证据 |
| 300308.SZ | 中际旭创 | 2 | completed_with_block_trade | fallback_no_browser | checked_prior_2026-05-29_incentive_notice_no_2026-05-30_new | T_and_T_plus_1 | checked_2026-05-29_no_record | checked_2026-05-29_found_3_flat_block_trades | unavailable_no_callable_chrome_tool | searched_no_new_operating_signal | updated_block_trade_only | 股权激励公告已入账，不重复追加 |
| 688498.SH | 源杰科技 | 2 | completed_no_material_change | fallback_no_browser | checked_no_new_records | T_and_T_plus_1 | checked_2026-05-29_no_record | checked_2026-05-29_no_record | unavailable_no_callable_chrome_tool | searched_no_new_hard_signal | no_change | 200G EML客户/定点/收入占比仍未披露 |
| 688668.SH | 鼎通科技 | 2 | completed_no_material_change | fallback_no_browser | checked_no_new_after_5_27_inquiry_reply | T_and_T_plus_1 | checked_2026-05-29_no_record | checked_2026-05-29_no_record | unavailable_no_callable_chrome_tool | searched_no_new_24h_material_signal | no_change | 6月2日业绩说明会为下一观察点 |
| 300394.SZ | 天孚通信 | 2 | completed_no_material_change | fallback_no_browser | checked_no_new_cninfo_szse_ir_hkex | T_and_T_plus_1 | checked_2026-05-29_no_record | checked_2026-05-29_no_record | unavailable_no_callable_chrome_tool | searched_market_observation_only | no_change | 公开媒体仅为行情/资金流观察 |
| 603738.SH | 泰晶科技 | 2 | completed_with_lhb_event | fallback_no_browser | checked_no_new_formal_notice | T_and_T_plus_1 | checked_2026-05-29_found_lhb | checked_2026-05-29_no_record | unavailable_no_callable_chrome_tool | searched_no_new_hard_signal | updated_events_and_state | 龙虎榜为交易结构，不证明客户/订单/收入 |

## Reconciliation

Enabled watchlist tickers: `002428.SZ`, `002222.SZ`, `300476.SZ`, `603256.SH`, `601869.SH`, `301511.SZ`, `002384.SZ`, `300308.SZ`, `688498.SH`, `688668.SH`, `300394.SZ`, `603738.SH`.

Completion table tickers: `002428.SZ`, `002222.SZ`, `300476.SZ`, `603256.SH`, `601869.SH`, `301511.SZ`, `002384.SZ`, `300308.SZ`, `688498.SH`, `688668.SH`, `300394.SZ`, `603738.SH`.

Reconciliation result: matched_12_of_12_no_missing_enabled_company.
