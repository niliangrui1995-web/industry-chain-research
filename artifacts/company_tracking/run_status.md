# A 股公司持续跟踪运行状态

- run_date_beijing: 2026-08-11
- run_started_at_beijing: 2026-08-11 20:31:56 +08:00
- run_finished_at_beijing: 2026-08-11 20:47:35 +08:00
- run_duration: 00:15:39
- automation_id: a-grok
- run_status: completed
- enabled_company_count: 13
- completed_company_count: 13
- failed_company_count: 0
- baseline_created_or_refreshed_count: 0
- state_updated_company_count: 0
- events_appended_count: 0
- announcement_window_checked: T_and_T_plus_1
- announcement_query_window: 2026-08-11 to 2026-08-12
- trading_event_dates_checked: 2026-08-11
- collection_scope: controller_open_web_only
- multi_agent_status: not_used_by_policy
- company_worker_queue: completed；总控按 watchlist 顺序独立完成 13 家 enabled 公司，未使用子代理或 worker。每家公司均已完成 baseline、thesis contract、management ledger、state、recent events 读取，以及公告、龙虎榜、大宗交易、Codex open-web、分类、五维归因与 thesis gate 检查。
- open_web_search_summary: 13/13 家逐家公司独立检索最近 24 小时；无可升级为公司级经营硬事实的有效结果，历史材料、泛行业讨论与社交内容均未进入确认事实。
- source_limitations: CNINFO 对 13 家均为 T/T+1 零命中；上交所 `queryCompanyBulletin.do` 对 5 家均为零命中；深交所 annList 对 7 家返回 HTTP 500 HTML，对云南锗业出现 SSL EOF，属于交易所交叉核验 source_gap，不等同于无公告。龙虎榜和大宗交易的单公司、单日期结构化二级查询均无命中，未把二级无结果升级为官方无事件结论。
- financial_evidence_audit: not_applicable_no_decision_critical_numbers
- prompt_contract_version: 2026-07-27.1
- precheck_metadata_captured_at_beijing: 2026-08-11T20:31:56+08:00
- skill_revision: git:9007ee32cb753d5a2f5d0a12edae05b3490195e5
- skill_content_sha256: 373e89b132cc3857c1cde2ce283bcc183c205904beacc7cac25b69672f861852
- skill_tree_status: clean
- skills: ["a-share-company-tracking", "a-share-disclosure-trading-data"]
- metadata_status: ok
- prewrite_snapshot_status: snapshot_created；enabled_company_count=13
- postwrite_validation_status: passed
- postwrite_validation_result: enabled_company_count=13；completion_table_count=13；new_event_count=0；workbook_round_trip=passed；event_append_only=passed

## 运行元数据（完整）

- captured_at_beijing: 2026-08-11T20:31:56+08:00
- prompt_contract_version: 2026-07-27.1
- skill_content_sha256: 373e89b132cc3857c1cde2ce283bcc183c205904beacc7cac25b69672f861852
- skill_revision: git:9007ee32cb753d5a2f5d0a12edae05b3490195e5
- skill_tree_status: clean
- skills: ["a-share-company-tracking", "a-share-disclosure-trading-data"]
- metadata_status: ok

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

## Per-company completion table（最终）

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | lhb_checked | block_trade_checked | announcement_window_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | ---: | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed | controller_open_web_only | CNINFO 8/11-8/12 no_hit；SZSE annList SSL source_gap；IR/open-web 无新增 | 8/11 no_hit_secondary | 8/11 no_hit_secondary | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市直连缺口；InP 合同交付验收回款待核 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed | controller_open_web_only | CNINFO/SSE 8/11-8/12 no_hit；IR/open-web 无新增 | 8/11 no_hit_secondary | 8/11 no_hit_secondary | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 特种电子布拆分、扩产及客户验证待核 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed | controller_open_web_only | CNINFO/SSE 8/11-8/12 no_hit；IR/open-web 无新增 | 8/11 no_hit_secondary | 8/11 no_hit_secondary | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 基金备案、实际出资及订单待核 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed | controller_open_web_only | CNINFO 8/11-8/12 no_hit；SZSE annList 500 source_gap；IR/open-web 无新增 | 8/11 no_hit_secondary | 8/11 no_hit_secondary | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市直连缺口；担保余额与 HVLP 分代数据待核 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed | controller_open_web_only | CNINFO 8/11-8/12 no_hit；SZSE annList 500 source_gap；IR/open-web 无新增 | 8/11 no_hit_secondary | 8/11 no_hit_secondary | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市直连缺口；并购整合和客户交付待核 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed | controller_open_web_only | CNINFO 8/11-8/12 no_hit；SZSE annList 500 source_gap；IR/open-web 无新增 | 8/11 no_hit_secondary | 8/11 no_hit_secondary | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市直连缺口；产品拆分和交易所原文待核 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed | controller_open_web_only | CNINFO/SSE 8/11-8/12 no_hit；IR/open-web 无新增 | 8/11 no_hit_secondary | 8/11 no_hit_secondary | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 200G EML 量产、订单及现金流待核 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed | controller_open_web_only | CNINFO/SSE 8/11-8/12 no_hit；IR/open-web 无新增 | 8/11 no_hit_secondary | 8/11 no_hit_secondary | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 说明会原始问答、液冷分产品证据及实际转股待核 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed | controller_open_web_only | CNINFO 8/11-8/12 no_hit；SZSE annList 500 source_gap；IR/open-web 无新增 | 8/11 no_hit_secondary | 8/11 no_hit_secondary | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市直连缺口；1.6T/CPO 收入与物料约束待核 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed | controller_open_web_only | CNINFO 8/11-8/12 no_hit；SZSE annList 500 source_gap；IR/open-web 无新增 | 8/11 no_hit_secondary | 8/11 no_hit_secondary | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市直连缺口；担保余额和 AIDC 收入拆分待核 | not_used_by_policy |
| 000636.SZ | 风华高科 | 11 | completed | controller_open_web_only | CNINFO 8/11-8/12 no_hit；SZSE annList 500 source_gap；IR/open-web 无新增 | 8/11 no_hit_secondary | 8/11 no_hit_secondary | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市原始榜单待复核；高端 MLCC 客户和现金流待核 | not_used_by_policy |
| 688048.SH | 长光华芯 | 12 | completed | controller_open_web_only | CNINFO/SSE 8/11-8/12 no_hit；IR/open-web 无新增 | 8/11 no_hit_secondary | 8/11 no_hit_secondary | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 200G EML 验证、量产和现金流待核 | not_used_by_policy |
| 301217.SZ | 铜冠铜箔 | 13 | completed | controller_open_web_only | CNINFO 8/11-8/12 no_hit；SZSE annList 500 source_gap；IR/open-web 无新增 | 8/11 no_hit_secondary | 8/11 no_hit_secondary | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市直连缺口；HVLP 分代销量和客户待核 | not_used_by_policy |

## 最终对账（写入后、校验前）

- enabled_watchlist_count: 13
- completion_table_count: 13
- missing_enabled_tickers: none
- duplicate_completion_tickers: none
- watchlist_order_match: true
- pending_or_refresh_needed_baselines: 0
- baseline_files_changed: 0
- state_updated_company_count: 0
- events_appended_count: 0
- watchlist_excel_logical_changes: 13（仅 enabled 行的 last_update_date）
- project_files_only: true
- git_commit_or_push: false
- final_validation: passed；enabled_company_count=13；completion_table_count=13；new_event_count=0；workbook_round_trip=passed；event_append_only=passed
