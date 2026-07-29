# A 股公司持续跟踪运行状态

- run_date_beijing: 2026-07-29
- run_started_at_beijing: 2026-07-29 20:31:29 +08:00
- run_finished_at_beijing: 2026-07-29 21:02:53 +08:00
- run_duration: 00:31:24
- automation_id: a-grok
- run_status: completed
- enabled_company_count: 13
- completed_company_count: 13
- failed_company_count: 0
- baseline_created_or_refreshed_count: 0
- state_updated_company_count: 5
- events_appended_count: 7
- announcement_window_checked: T_and_T_plus_1
- announcement_query_window: 2026-07-29 to 2026-07-30
- trading_event_dates_checked: 2026-07-29
- collection_scope: controller_open_web_only
- multi_agent_status: not_used_by_policy
- company_worker_queue: completed；总控按 watchlist 顺序独立完成 13 家 enabled 公司
- open_web_policy: Codex 逐公司联网观察；只用于发现和反证，非官方结果不得直接进入确认事实层
- source_priority: 官方披露 -> 公司署名 IR -> 交易所交易数据 -> 行情厂商交叉 -> 可信媒体 -> open-web 观察
- source_limitations: T+1 查询为收口时点快照；2026-07-30 后续公告、IR 异步更新、中际旭创 H 股最终配售/挂牌结果、东山精密原始互动与保险确认仍待核
- prompt_contract_version: 2026-07-27.1
- precheck_metadata_captured_at_beijing: 2026-07-29T20:31:29+08:00
- metadata_captured_at_beijing: 2026-07-29T20:59:33+08:00
- skill_revision: git:46088c9e9c3c8a407ded04aa6cad45e029728c80
- skill_content_sha256: 373e89b132cc3857c1cde2ce283bcc183c205904beacc7cac25b69672f861852
- skill_tree_status: clean
- skills: a-share-company-tracking；a-share-disclosure-trading-data
- metadata_status: ok
- prewrite_snapshot_status: snapshot_created
- postwrite_validation_status: passed
- postwrite_validation_result: enabled_company_count=13；completion_table_count=13；new_event_count=7；workbook_round_trip=passed；event_append_only=passed

## 公司顺序

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
11. 000636.SZ 风华高科
12. 688048.SH 长光华芯
13. 301217.SZ 铜冠铜箔

## 本轮实质结果

- 交易事件：宏和科技、风华高科新增龙虎榜；东山精密、中际旭创新增大宗交易。
- 延迟补录：东山精密 Source Photonics 光模块运输丢失事实与保险影响管理层主张分开入账；源杰科技 7 月 21 日公司调研纪要入账，但合作意向不升级为订单。
- 无新增公司级硬事件：云南锗业、长飞光纤、德福科技、鼎通科技、天孚通信、麦格米特、长光华芯、铜冠铜箔。
- 基线：13 家 baseline_status 均为 done；无新建/刷新。
- Excel：13 家 last_update_date 已在当日早间同步为 2026-07-29，本轮无逻辑单元格变更，工作簿结构保持不变。

## Per-company completion table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | lhb_checked | block_trade_checked | announcement_window_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed | controller_open_web_only | CNINFO/SZSE/IR 7/29-7/30 no_hit | 7/29 no_hit | 7/29 no_hit | T_and_T_plus_1 | searched_no_new_beyond_prior_contract | no_change | 7/30后续异步披露及合同交付/回款待核 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed | controller_open_web_only | CNINFO/SSE/IR 7/29-7/30 no_hit | 7/29 hit_amplitude_15.69 | 7/29 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | higher_trading_divergence_fundamental_unchanged | 7/30后续披露及特种电子布拆分待核 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed | controller_open_web_only | CNINFO/SSE/IR/HKEX 7/29-7/30 no_hit | 7/29 no_hit | 7/29 no_hit | T_and_T_plus_1 | searched_media_restate_no_new_hard_signal | no_change | IR/HKEX异步更新与商业化拆分风险 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed | controller_open_web_only | CNINFO/SZSE/IR 7/29-7/30 no_hit | 7/29 no_hit | 7/29 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 7/30后续披露及HVLP分代数据待核 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed | controller_open_web_only | CNINFO/SZSE/IR 7/29-7/30 no_hit | 7/29 no_hit | 7/29 hit_1_small_flat_trade | T_and_T_plus_1 | searched_hit_transport_loss_ir_mirrors | transport_insurance_risk_added_stage_unchanged | 原始互动页、保险确认和客户影响待核 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed | controller_open_web_only | CNINFO/SZSE 7/29-7/30 no_new_after_buyback_proposal | 7/29 no_hit | 7/29 hit_2_flat_trades | T_and_T_plus_1 | searched_h_share_final_result_pending | institutional_turnover_fundamental_unchanged | H股配售/挂牌结果可能在收口后披露 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed | controller_open_web_only | CNINFO/SSE/IR 7/29-7/30 no_hit | 7/29 no_hit | 7/29 no_hit | T_and_T_plus_1 | searched_hit_company_ir_docx_mirror | management_claim_enriched_stage_not_upgraded | 原始交易所链接及合作意向转订单待核 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed | controller_open_web_only | CNINFO/SSE/IR 7/29-7/30 no_hit | 7/29 no_hit | 7/29 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 7/30后续披露及转股价股东会待核 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed | controller_open_web_only | CNINFO/SZSE/IR 7/29-7/30 no_hit | 7/29 no_hit | 7/29 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | H股/IR异步更新及1.6T/CPO拆分待核 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed | controller_open_web_only | CNINFO/SZSE/IR 7/29-7/30 no_hit | 7/29 no_hit | 7/29 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | AIDC客户、订单金额和利润拆分N/A | not_used_by_policy |
| 000636.SZ | 风华高科 | 11 | completed | controller_open_web_only | CNINFO/SZSE/IR 7/29-7/30 no_hit | 7/29 hit_upside_9.08 | 7/29 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | higher_trading_heat_and_net_selling | 异动公告及H1高端产品拆分待核 | not_used_by_policy |
| 688048.SH | 长光华芯 | 12 | completed | controller_open_web_only | CNINFO/SSE/IR 7/29-7/30 no_hit | 7/29 no_hit | 7/29 no_hit | T_and_T_plus_1 | searched_no_new_beyond_prior_interview | no_change | 媒体管理层口径仍待官方验证 | not_used_by_policy |
| 301217.SZ | 铜冠铜箔 | 13 | completed | controller_open_web_only | CNINFO/SZSE/IR 7/29-7/30 no_hit | 7/29 no_hit | 7/29 no_hit | T_and_T_plus_1 | searched_no_new_hard_signal | no_change | HVLP具名客户与分代财务拆分N/A | not_used_by_policy |

## 最终对账

- enabled_watchlist_count: 13
- completion_table_count: 13
- missing_enabled_tickers: none
- duplicate_completion_tickers: none
- watchlist_order_match: true
- pending_or_refresh_needed_baselines: 0
- baseline_files_changed: 0
- watchlist_excel_logical_changes: 0
- state_updated_company_count: 5
- events_appended_count: 7
- project_files_only: true
- git_commit_or_push: false
- final_validation: passed
