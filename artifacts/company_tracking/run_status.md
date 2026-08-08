# A 股公司持续跟踪运行状态

- run_date_beijing: 2026-08-08
- run_started_at_beijing: 2026-08-08 23:39:57 +08:00
- run_finished_at_beijing: 2026-08-08 23:52:32 +08:00
- run_duration: 00:12:35
- automation_id: a-grok-evening-rescan
- run_status: completed
- enabled_company_count: 13
- completed_company_count: 13
- failed_company_count: 0
- baseline_created_or_refreshed_count: 0
- state_updated_company_count: 0
- events_appended_count: 0
- announcement_window_checked: T_and_T_plus_1
- announcement_query_window: 2026-08-08 to 2026-08-09
- trading_event_dates_checked: not_run_user_scoped_official_rescan
- collection_scope: official_evening_rescan_only
- multi_agent_status: not_used_by_policy
- company_worker_queue: completed；总控按 watchlist 顺序独立完成 13 家 enabled 公司
- open_web_search_summary: 未运行；本轮按用户范围仅做交易所/CNINFO/公司 IR 官方晚间补扫。
- source_limitations: 8 家深交所 `annList` 直连返回 50x 非 JSON 页面；云南锗业官网直连超时，长飞光纤官网直连断开，铜冠铜箔未定位可验证的独立 IR 入口。CNINFO 对 13 家均无 T/T+1 新增发行人披露；上交所对 5 家均无 T/T+1 原始公告。
- financial_evidence_audit: not_applicable_no_decision_critical_numbers
- prompt_contract_version: 2026-07-27.1
- precheck_metadata_captured_at_beijing: 2026-08-08T23:39:57+08:00
- skill_revision: git:b3b8800a7f5feff69ef52e3a528e01713977f87b
- skill_content_sha256: 373e89b132cc3857c1cde2ce283bcc183c205904beacc7cac25b69672f861852
- skill_tree_status: clean
- skills: ["a-share-company-tracking", "a-share-disclosure-trading-data"]
- metadata_status: ok
- prewrite_snapshot_status: snapshot_created；enabled_company_count=13
- postwrite_validation_status: passed
- postwrite_validation_result: enabled_company_count=13；completion_table_count=13；new_event_count=0；workbook_round_trip=passed；event_append_only=passed
- daytime_run_reference: 2026-08-08 13:40:01 至 14:40:26 的日间运行已完成；本文件现记录其后 T/T+1 晚间补扫结果。

## 运行元数据（完整）

```json
{
  "captured_at_beijing": "2026-08-08T23:39:57+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "373e89b132cc3857c1cde2ce283bcc183c205904beacc7cac25b69672f861852",
  "skill_revision": "git:b3b8800a7f5feff69ef52e3a528e01713977f87b",
  "skill_tree_status": "clean",
  "skills": [
    "a-share-company-tracking",
    "a-share-disclosure-trading-data"
  ],
  "status": "ok"
}
```

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

## 晚间补扫 Per-company completion table（最终）

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | lhb_checked | block_trade_checked | announcement_window_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed | official_evening_rescan_only | CNINFO 8/8-8/9 no_hit；SZSE annList 50x；公司IR直连超时 | not_run_user_scoped_official_rescan | not_run_user_scoped_official_rescan | T_and_T_plus_1 | not_run_user_scoped_official_rescan | no_new_official_fact_no_write | 官网直连超时；CNINFO无新增 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed | official_evening_rescan_only | CNINFO/SSE 8/8-8/9 no_hit；公司IR无新增标识 | not_run_user_scoped_official_rescan | not_run_user_scoped_official_rescan | T_and_T_plus_1 | not_run_user_scoped_official_rescan | no_new_official_fact_no_write | 无新增经营、订单、客户或收入事实 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed | official_evening_rescan_only | CNINFO/SSE 8/8-8/9 no_hit；公司IR直连断开 | not_run_user_scoped_official_rescan | not_run_user_scoped_official_rescan | T_and_T_plus_1 | not_run_user_scoped_official_rescan | no_new_official_fact_no_write | 官网直连断开；CNINFO/SSE无新增 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed | official_evening_rescan_only | CNINFO 8/8-8/9 no_hit；SZSE annList 50x；公司IR无新增标识 | not_run_user_scoped_official_rescan | not_run_user_scoped_official_rescan | T_and_T_plus_1 | not_run_user_scoped_official_rescan | no_new_official_fact_no_write | 深交所接口50x；CNINFO无新增 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed | official_evening_rescan_only | CNINFO 8/8-8/9 no_hit；SZSE annList 50x；公司IR无新增标识 | not_run_user_scoped_official_rescan | not_run_user_scoped_official_rescan | T_and_T_plus_1 | not_run_user_scoped_official_rescan | no_new_official_fact_no_write | 深交所接口50x；CNINFO无新增 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed | official_evening_rescan_only | CNINFO 8/8-8/9 no_hit；SZSE annList 50x；公司IR无新增标识 | not_run_user_scoped_official_rescan | not_run_user_scoped_official_rescan | T_and_T_plus_1 | not_run_user_scoped_official_rescan | no_new_official_fact_no_write | 深交所接口50x；CNINFO无新增 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed | official_evening_rescan_only | CNINFO/SSE 8/8-8/9 no_hit；公司IR无新增标识 | not_run_user_scoped_official_rescan | not_run_user_scoped_official_rescan | T_and_T_plus_1 | not_run_user_scoped_official_rescan | no_new_official_fact_no_write | 无新增经营、订单、客户或收入事实 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed | official_evening_rescan_only | CNINFO/SSE 8/8-8/9 no_hit；公司IR无新增标识 | not_run_user_scoped_official_rescan | not_run_user_scoped_official_rescan | T_and_T_plus_1 | not_run_user_scoped_official_rescan | no_new_official_fact_no_write | 无新增经营、订单、客户或收入事实 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed | official_evening_rescan_only | CNINFO 8/8-8/9 no_hit；SZSE annList 50x；公司IR无新增标识 | not_run_user_scoped_official_rescan | not_run_user_scoped_official_rescan | T_and_T_plus_1 | not_run_user_scoped_official_rescan | no_new_official_fact_no_write | 深交所接口50x；CNINFO无新增 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed | official_evening_rescan_only | CNINFO 8/8-8/9 no_hit；SZSE annList 50x；公司IR无新增标识 | not_run_user_scoped_official_rescan | not_run_user_scoped_official_rescan | T_and_T_plus_1 | not_run_user_scoped_official_rescan | no_new_official_fact_no_write | 深交所接口50x；CNINFO无新增 | not_used_by_policy |
| 000636.SZ | 风华高科 | 11 | completed | official_evening_rescan_only | CNINFO 8/8-8/9 no_hit；SZSE annList 50x；公司IR无新增标识 | not_run_user_scoped_official_rescan | not_run_user_scoped_official_rescan | T_and_T_plus_1 | not_run_user_scoped_official_rescan | no_new_official_fact_no_write | 深交所接口50x；CNINFO无新增 | not_used_by_policy |
| 688048.SH | 长光华芯 | 12 | completed | official_evening_rescan_only | CNINFO/SSE 8/8-8/9 no_hit；公司IR无新增标识 | not_run_user_scoped_official_rescan | not_run_user_scoped_official_rescan | T_and_T_plus_1 | not_run_user_scoped_official_rescan | no_new_official_fact_no_write | 无新增经营、订单、客户或收入事实 | not_used_by_policy |
| 301217.SZ | 铜冠铜箔 | 13 | completed | official_evening_rescan_only | CNINFO 8/8-8/9 no_hit；SZSE annList 50x；未定位独立IR入口 | not_run_user_scoped_official_rescan | not_run_user_scoped_official_rescan | T_and_T_plus_1 | not_run_user_scoped_official_rescan | no_new_official_fact_no_write | 深交所接口50x；独立IR入口待下轮复核 | not_used_by_policy |

## 日间运行原始 Per-company completion table（归档）

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | lhb_checked | block_trade_checked | announcement_window_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed | controller_open_web_only | CNINFO/SZSE/IR 8/4-8/8 hit_abnormal | 8/5-8/7 hit_official_SZSE | 8/4-8/7 no_hit | pending_evening_rescan | searched_no_new_operating_signal | trading_updated | InP 首批交付验收回款待核 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed | controller_open_web_only | CNINFO/SSE/IR 8/4-8/8 hit_abnormal_and_patent | 8/6 hit_secondary | 8/4_and_8/6 small_secondary | pending_evening_rescan | searched_no_new_operating_signal | trading_and_patent_updated | 特种电子布拆分及扩产待核 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed | controller_open_web_only | CNINFO/SSE/IR 8/4-8/8 hit_fund_and_abnormal | 8/5-8/6 hit_official_SSE | 8/4-8/7 no_hit | pending_evening_rescan | searched_no_new_operating_signal | capital_and_trading_updated | 基金备案实际出资及订单待核 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed | controller_open_web_only | CNINFO/SZSE/IR 8/4-8/8 hit_guarantee | 8/4-8/7 no_hit | 8/4-8/7 no_hit | pending_evening_rescan | searched_no_new_operating_signal | guarantee_updated | 担保余额和HVLP分代数据待核 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed | controller_open_web_only | CNINFO/SZSE/IR 8/4-8/8 no_hit | 8/4-8/5 hit_official_SZSE | 8/4-8/7 no_hit | pending_evening_rescan | searched_no_new_operating_signal | trading_updated | 并购整合和客户交付待核 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed | controller_open_web_only | CNINFO/SZSE/IR 8/4-8/8 routine_H_share_return | 8/4-8/7 no_hit | 8/6 hit_secondary | pending_evening_rescan | searched_no_new_operating_signal | block_trade_updated | 官方交易所原文及产品拆分待核 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed | controller_open_web_only | CNINFO/SSE/IR 8/4-8/8 no_hit | 8/4-8/7 no_hit | 8/4-8/7 no_hit | pending_evening_rescan | searched_no_new_operating_signal | no_change | H1订单和现金流待核 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed | controller_open_web_only | CNINFO/SSE/IR 8/4-8/8 hit_H1_and_convertible_bond | 8/4 hit_official_SSE | 8/4-8/7 no_hit | pending_evening_rescan | searched_no_new_operating_signal | financial_capital_and_trading_updated | 液冷分产品证据与实际转股待核 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed | controller_open_web_only | CNINFO/SZSE/IR 8/4-8/8 no_hit | 8/4-8/7 no_hit | 8/7 small_secondary | pending_evening_rescan | searched_no_new_operating_signal | no_change | 1.6T/CPO收入与物料约束待核 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed | controller_open_web_only | CNINFO/SZSE/IR 8/4-8/8 hit_guarantee_and_cash_management | 8/5 hit_official_SZSE | 8/4-8/7 no_hit | pending_evening_rescan | searched_no_new_operating_signal | guarantee_and_trading_updated | 担保余额和AIDC收入拆分待核 | not_used_by_policy |
| 000636.SZ | 风华高科 | 11 | completed | controller_open_web_only | CNINFO/SZSE/IR 8/4-8/8 hit_vp_appointment | 8/4 hit_official_SZSE | 8/4-8/7 no_hit | pending_evening_rescan | searched_no_new_operating_signal | governance_and_trading_updated | 高端MLCC客户与现金流待核 | not_used_by_policy |
| 688048.SH | 长光华芯 | 12 | completed | controller_open_web_only | CNINFO/SSE/IR 8/4-8/8 no_hit | 8/4-8/7 no_hit | 8/4-8/7 no_hit | pending_evening_rescan | searched_no_new_operating_signal | no_change | 200G EML验证和现金流待核 | not_used_by_policy |
| 301217.SZ | 铜冠铜箔 | 13 | completed | controller_open_web_only | CNINFO/SZSE/IR 8/4-8/8 hit_abnormal | 8/7 hit_official_SZSE | 8/4-8/7 no_hit | pending_evening_rescan | searched_no_new_operating_signal | trading_updated | HVLP分代销量和客户待核 | not_used_by_policy |

## 最终对账（写入后、校验前）

- enabled_watchlist_count: 13
- completion_table_count: 13
- missing_enabled_tickers: none
- duplicate_completion_tickers: none
- watchlist_order_match: true
- pending_or_refresh_needed_baselines: 0
- baseline_files_changed: 0
- state_updated_company_count: 10
- events_appended_count: 17
- watchlist_excel_logical_changes: 13（仅 enabled 行的 last_update_date）
- project_files_only: true
- git_commit_or_push: false
- final_validation: passed；enabled_company_count=13；completion_table_count=13；new_event_count=17；workbook_round_trip=passed；event_append_only=passed
