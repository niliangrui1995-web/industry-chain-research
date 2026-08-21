# A 股公司持续跟踪运行状态

- run_date: 2026-08-21
- run_started_at_beijing: 2026-08-21T20:31:36+08:00
- announcement_window_checked: T_and_T_plus_1
- run_status: completed
- run_finished_at_beijing: 2026-08-21T21:05:41+08:00
- enabled_company_count: 13
- completed_company_count: 13
- baseline_created_or_refreshed_count: 0
- baseline_identifier_mapping_count: 16
- state_updated_count: 13
- events_appended_count: 10
- excel_last_update_date_synced_count: 13
- open_web_search_completed_count: 13
- open_web_new_operating_signal_count: 2_backfilled_official_disclosures
- open_web_new_operating_hard_fact_count: 2
- financial_evidence_audit: calc_only_passed_102922200_and_832300；无估值、预期差、覆盖率或派生财务结论，未执行 formal audit release。
- multi_agent_status: not_used_by_policy
- source_limitations: 深市8家 annList 本轮分别出现 HTTP 500、ReadTimeout 或 TLS 连接错误，均按 source_gap 保留；CNINFO 为深市公告的一手替代来源。上交所5家 issuer 查询可用，长飞光纤命中8月22日半年报，其余为0。
- trading_data_limitations: 龙虎榜和大宗交易均为东方财富二级数据逐家公司查询。龙虎榜13家无新增返回；大宗交易仅宏和科技8月21日4笔同卖方折价记录入账。中际旭创接口疑似重复记录，未入账。
- write_snapshot: artifacts/company_tracking/.run_validation_snapshot.tmp

## 运行元数据（完整）

~~~json
{
  "captured_at_beijing": "2026-08-21T20:36:30+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "223840607b9814d4d960aec4d2ab728ebf2e08be8b4d4cb82e8d659db8b9c3fb",
  "skill_revision": "git:62b74f8474700f902a37a53ce197c766ca38b700",
  "skill_tree_status": "clean",
  "skills": [
    "a-share-company-tracking",
    "a-share-disclosure-trading-data",
    "financial-evidence-audit"
  ],
  "status": "ok"
}
~~~

## 逐家公司完成表

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | lhb_checked | block_trade_checked | announcement_window_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed | controller_single_company | CNINFO 0；SZSE HTTP 500 source_gap；IR无新增 | 东财二级 0 | 东财二级 0 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市公告源缺口；InP合同、客户和收入待验证 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed | controller_single_company | CNINFO 0；SSE 0；IR无新增 | 东财二级 0 | 8月21日4笔折价记录已入账 | T_and_T_plus_1 | searched_no_new_operating_signal | secondary_block_trade_cluster | 交易所明细、卖方身份、客户订单与项目执行待验证 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed | controller_single_company | CNINFO 0；SSE 8月22日半年报；IR无新增 | 东财二级 0 | 东财二级 0 | T_and_T_plus_1 | searched_no_new_operating_signal | official_h1_strengthened | 客户订单、产品收入、毛利率和现金流待验证 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed | controller_single_company | CNINFO 8月22日半年报；SZSE HTTP 500 source_gap | 东财二级 0 | 东财二级 0 | T_and_T_plus_1 | searched_no_new_operating_signal | official_h1_mixed | 认证阶段、客户订单与负经营现金流待验证 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed | controller_single_company | CNINFO 8月22日半年报和资本事项；SZSE HTTP 500 source_gap | 东财二级 0 | 东财二级 0 | T_and_T_plus_1 | searched_no_new_operating_signal | official_h1_and_capex | 股东会、项目进度、订单、现金流与担保待验证 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed | controller_single_company | CNINFO 8月22日半年报；SZSE HTTP 500 source_gap | 东财二级 0 | 疑似重复记录，未入账 | T_and_T_plus_1 | searched_no_new_operating_signal | official_h1_strengthened | 1.6T/硅光客户订单、应收存货和现金流待验证 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed | controller_single_company | CNINFO 0；SSE 0；IR无新增 | 东财二级 0 | 东财二级 0 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 高端激光芯片客户、订单、收入与现金流待验证 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed | controller_single_company | CNINFO 股东大会决议；SSE 0；IR无新增 | 东财二级 0 | 东财二级 0 | T_and_T_plus_1 | searched_no_new_operating_signal | official_governance_capital | 权益分派实施、连接器客户订单与盈利待验证 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed | controller_single_company | CNINFO当窗0；回补8月19日半年报；SZSE HTTP 500 source_gap | 东财二级 0 | 东财二级 0 | T_and_T_plus_1 | searched_backfilled_official_h1 | official_h1_mixed | 物料、CPO/1.6T订单、泰国产能与现金流待验证 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed | controller_single_company | CNINFO 0；SZSE TLS source_gap；IR无新增 | 东财二级 0 | 东财二级 0 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市公告源缺口；AIDC电源客户订单收入待验证 | not_used_by_policy |
| 000636.SZ | 风华高科 | 11 | completed | controller_single_company | CNINFO 回购注销完成；SZSE HTTP 500 source_gap | 东财二级 0 | 东财二级 0 | T_and_T_plus_1 | searched_secondary_repeated_no_upgrade | official_capital_structure | 高端MLCC客户、订单、收入及股本后续变化待验证 | not_used_by_policy |
| 688048.SH | 长光华芯 | 12 | completed | controller_single_company | CNINFO 0；SSE 0；IR无新增 | 东财二级 0 | 东财二级 0 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 200G及以上产品客户订单收入待验证 | not_used_by_policy |
| 301217.SZ | 铜冠铜箔 | 13 | completed | controller_single_company | CNINFO当窗0；回补8月17日治理公告；SZSE TLS source_gap | 东财二级 0 | 东财二级 0 | T_and_T_plus_1 | searched_backfilled_official_governance | official_governance_watch | 高管补聘、内控、HVLP客户订单与现金流待验证 | not_used_by_policy |

## 端到端验证门

- snapshot 已在任何业务写入前生成。
- 2026-08-21T21:05:41+08:00 执行 validate：status=passed。
- validation_result: completion_table_count=13；enabled_company_count=13；new_event_count=10；event_append_only=passed；workbook_round_trip=passed。
