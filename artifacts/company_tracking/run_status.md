# Company Tracking Run Status

metadata:

- run_date: 2026-05-28
- run_start_time_beijing: 2026-05-28 13:40:41 +08:00
- run_closeout_time_beijing: 2026-05-28 20:56:24 +08:00
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

- `002428.SZ` 云南锗业：新增 2026-05-27 公司官网 IR、控股子公司为孙公司 8,500 万元固定资产贷款提供担保、放弃云南鑫耀 2.97% 股权转让优先购买权；晚间复扫新增 2026-05-28 龙虎榜，净买入约 9.79 亿元。InP 需求/价格/批量供货与上游资源合作线索增强，交易拥挤度继续升高，但仍无客户名称、订单金额、良率数值、6 英寸稳定量产、出口许可或利润贡献。
- `301511.SZ` 德福科技：新增约 31 亿元年产 5 万吨高端 AI 电子电路铜箔项目公告，并新增对子公司琥珀新材 2 亿元担保进展。强化中长期高端铜箔产能主线，同时提高审批、资本开支和爬坡验证要求。
- `688668.SH` 鼎通科技：新增 2025 年报问询回复及会计师专项说明，披露前五大客户合计收入 14.04 亿元、占比 88.43%，2026-04-30 订单覆盖率 117.06%，并明确 CAGE 电镀/贵金属成本风险。客户/订单证据增强但不证明终端客户或 1.6T/GB200/NVIDIA 订单。
- `300308.SZ` 中际旭创：新增 2026-05-26/27 小额平价大宗交易、2026-05-28 治理公告组，以及 T+1 的 2026-05-29 股权激励归属结果暨股份上市公告（归属 1,309,657 股，占当前总股本 0.12%）。属于交易结构、治理和轻微股本摊薄事项，不构成 800G/1.6T、硅光、客户需求、物料或毛利率经营披露。
- `002222.SZ` 福晶科技：新增 2026-05-26 官方互动回复，补充钒酸钇生产结构，同时确认法拉第旋转片产销、产能和订单仍以正式披露为准；属于产品结构和信息边界事件。

## Announcement And Trading Highlights

- Announcement window: all 12 enabled companies were rescanned after 20:00 Beijing time for announcement dates `2026-05-28` and `2026-05-29`; every completion row now records `announcement_window_checked=T_and_T_plus_1`.
- Dragon-tiger list: `002428.SZ` 云南锗业 had a new 2026-05-28 dragon-tiger record, with about 979 million yuan net buy in the disclosure detail. No other enabled company had a new 2026-05-28 record in completed checks.
- Block trades: `300308.SZ` had one 2026-05-26 small flat block trade and two 2026-05-27 small flat block trades. Evening rescan found no enabled-company 2026-05-28 block-trade addition.
- Baseline: no baseline was created or refreshed.

## Grok/X And Fallback Status

- Multi-agent tools were available and used. Twelve company workers were spawned with explicit `model="gpt-5.5"` and `reasoning_effort="xhigh"`, with maximum logical concurrency of 6.
- Chrome/Grok callable tools were not exposed in this run, so no logged-in Chrome/Grok or X-native result was collected.
- No Browser Use or Playwright substitute was used as a Grok/X replacement.
- Open-web fallback was used or recorded per company as observation-only. No social/open-web item was promoted to confirmed fact without official disclosure or trading-data support.

## Baseline Changes And Source Gaps

- Baseline updates: none.
- Primary timing gap closed for this run: the controller launched an evening worker wave after 20:00 and checked `2026-05-28` plus T+1 `2026-05-29` announcement dates company by company. Later overnight disclosures after 20:56 remain next-run scope.
- Trading-data gap: 2026-05-28 LHB/block-trade data were checked in the evening pass; 2026-05-29 trading data were not treated as final because that trading day had not formed yet at run time.
- SZSE source gaps: several SZSE announcement or trading endpoints returned 50x/maintenance responses. Company workers used CNINFO, company pages, SSE, Eastmoney trading APIs, P5W/互动易, and open-web observation as cross-checks.
- `002428.SZ`: CNINFO stock-param query initially returned 0, but company-name/keyword and official company IR found the relevant 2026-05-27 material.
- `301511.SZ`: CNINFO ticker query and Eastmoney mirror missed some notices; CNINFO company-name query and SZSE listing disclosure found the project and guarantee notices.

## Per-company completion table

| ticker | name | batch_no | queue_status | browser_scope | announcements_checked | announcement_window_checked | lhb_checked | block_trade_checked | grok_status | open_web_fallback_status | state_change | miss_risk_notes |
|---|---|---:|---|---|---|---|---|---|---|---|---|---|
| 002428.SZ | 云南锗业 | 1 | completed_with_material_events | not_available_no_callable_chrome_tool | checked_2026-05-28_to_2026-05-29_no_new_announcements_after_prior_IR | T_and_T_plus_1 | checked_2026-05-28_found_lhb_net_buy_979m | checked_2026-05-28_no_record | unavailable_no_callable_chrome_tool | searched_observation_only_no_new_operating_signal | updated_events_and_state | 龙虎榜提高交易拥挤度；客户/订单/良率/利润仍待披露 |
| 002222.SZ | 福晶科技 | 1 | completed_with_ir_source_gap_event | not_available_no_callable_chrome_tool | checked_2026-05-28_to_2026-05-29_no_new_formal_notice | T_and_T_plus_1 | checked_2026-05-28_no_record | checked_2026-05-28_no_record | unavailable_no_callable_chrome_tool | searched_observation_only_no_new_hard_signal | updated_state_only_evening_rescan_closed | 法拉第旋转片产销/产能/订单仍未披露；SZSE annList 500 |
| 300476.SZ | 胜宏科技 | 1 | completed_no_material_change | not_available_no_callable_chrome_tool | checked_2026-05-28_to_2026-05-29_no_new | T_and_T_plus_1 | checked_2026-05-28_no_record | checked_2026-05-28_no_record | unavailable_no_callable_chrome_tool | searched_observation_only_no_new_hard_signal | none_no_file_update | SZSE annList 50x；AI PCB订单/客户/毛利率仍待官方量化 |
| 603256.SH | 宏和科技 | 1 | completed_no_material_change | fallback_no_browser | checked_2026-05-28_to_2026-05-29_no_new | T_and_T_plus_1 | checked_2026-05-28_no_record | checked_2026-05-28_no_record | unavailable_no_callable_chrome_tool | searched_observation_only_no_new_hard_signal | none_no_file_update | open-web 仅见涨停/PCB叙事，未见官方 Low CTE/T-glass 新披露 |
| 601869.SH | 长飞光纤 | 1 | completed_no_material_change | not_available_no_callable_chrome_tool | checked_2026-05-28_to_2026-05-29_no_new_a_h_notice | T_and_T_plus_1 | checked_2026-05-28_no_record | checked_2026-05-28_no_record | unavailable_no_callable_chrome_tool | searched_observation_only_no_new_hard_signal | none_no_file_update | 海外/X discovery 缺口仍在；公开检索无新增官方披露 |
| 301511.SZ | 德福科技 | 1 | completed_with_prior_material_no_evening_new | not_available_no_callable_chrome_tool | checked_2026-05-28_to_2026-05-29_no_new_beyond_project_board_shareholder_notices | T_and_T_plus_1 | checked_2026-05-28_no_record | checked_2026-05-28_no_record | unavailable_no_callable_chrome_tool | searched_observation_only_no_new_hard_signal | none_no_evening_update | 项目仍需审批、资金、客户认证、订单和毛利验证 |
| 002384.SZ | 东山精密 | 2 | completed_no_material_event | not_available_no_callable_chrome_tool | checked_2026-05-28_to_2026-05-29_no_new_formal_notice; one_nonmaterial_ir_reply | T_and_T_plus_1 | checked_2026-05-28_no_record | checked_2026-05-28_no_record | unavailable_no_callable_chrome_tool | searched_observation_only_no_new_hard_signal | updated_state_only_evening_rescan_closed | 互动易回复仍为不披露边界；SZSE annList 50x |
| 300308.SZ | 中际旭创 | 2 | completed_with_T_plus_1_official_event | not_available_no_callable_chrome_tool | checked_2026-05-28_to_2026-05-29_found_stock_incentive_listing_notice | T_and_T_plus_1 | checked_2026-05-28_no_record | checked_2026-05-28_no_new_after_2026-05-26_27_records | unavailable_no_callable_chrome_tool | searched_observation_only_no_new_operating_signal | updated_events_and_state | 股权激励归属偏治理/轻微摊薄，不代表经营兑现 |
| 688498.SH | 源杰科技 | 2 | completed_no_material_change | not_available_no_callable_chrome_tool | checked_2026-05-28_to_2026-05-29_no_new | T_and_T_plus_1 | checked_2026-05-28_no_record | checked_2026-05-28_no_record | unavailable_no_callable_chrome_tool | searched_observation_only_no_new_hard_signal | none_no_file_update | 200G EML客户/定点/收入占比仍未披露 |
| 688668.SH | 鼎通科技 | 2 | completed_with_prior_material_no_evening_new | not_available_no_callable_chrome_tool | checked_2026-05-28_to_2026-05-29_no_new_after_inquiry_reply | T_and_T_plus_1 | checked_2026-05-28_no_record | checked_2026-05-28_no_record | unavailable_no_callable_chrome_tool | searched_observation_only_no_new_hard_signal | none_no_evening_update | 问询回复增强客户/订单证据但不证明终端客户或1.6T/GB200订单 |
| 300394.SZ | 天孚通信 | 2 | completed_no_material_change | not_available_no_callable_chrome_tool | checked_2026-05-28_to_2026-05-29_no_new_cninfo_szse_ir_hkex | T_and_T_plus_1 | checked_2026-05-28_no_record | checked_2026-05-28_no_record | unavailable_no_callable_chrome_tool | searched_observation_only_market_move_no_material_event | updated_state_only_evening_rescan_closed | H股/CPO/1.6T叙事未升级为公司硬披露 |
| 603738.SH | 泰晶科技 | 2 | completed_no_material_change | not_available_no_callable_chrome_tool | checked_2026-05-28_to_2026-05-29_no_new | T_and_T_plus_1 | checked_2026-05-28_no_record | checked_2026-05-28_no_record | unavailable_no_callable_chrome_tool | searched_observation_only_no_new_hard_signal | none_no_file_update | 312.5MHz/625MHz客户、订单、收入占比、产能和毛利率仍待披露 |

## Reconciliation

Enabled watchlist tickers: `002428.SZ`, `002222.SZ`, `300476.SZ`, `603256.SH`, `601869.SH`, `301511.SZ`, `002384.SZ`, `300308.SZ`, `688498.SH`, `688668.SH`, `300394.SZ`, `603738.SH`.

Completion table tickers: `002428.SZ`, `002222.SZ`, `300476.SZ`, `603256.SH`, `601869.SH`, `301511.SZ`, `002384.SZ`, `300308.SZ`, `688498.SH`, `688668.SH`, `300394.SZ`, `603738.SH`.

Reconciliation result: matched_12_of_12_no_missing_enabled_company.
