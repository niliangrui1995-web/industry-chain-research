# A 股公司持续跟踪运行状态

- run_date: 2026-08-14
- run_started_at_beijing: 2026-08-14T20:32:19+08:00
- announcement_window_checked: T_and_T_plus_1
- run_status: completed
- run_finished_at_beijing: 2026-08-14T20:54:04+08:00
- enabled_company_count: 13
- completed_company_count: 13
- baseline_created_or_refreshed_count: 0
- baseline_identifier_mapping_count: 0
- state_updated_count: 2
- events_appended_count: 3
- excel_last_update_date_synced_count: 13
- open_web_search_completed_count: 13
- open_web_new_operating_signal_count: 0
- financial_evidence_audit: not_applicable_no_decision_critical_derived_financial_number
- multi_agent_status: not_used_by_policy
- source_limitations: 深市 8 家 annList 均返回 HTTP 500 HTML，按 source_gap 保留；CNINFO 官方原文为深市公司入账依据。上交所公司公告接口可用。
- trading_data_limitations: 龙虎榜与大宗交易均为东方财富二级数据逐家公司查询结果，2026-08-14 均未命中，不能替代交易所一手结论。
- write_snapshot: artifacts/company_tracking/.run_validation_snapshot.tmp

## 运行元数据（完整）

~~~json
{
  "captured_at_beijing": "2026-08-14T20:32:19+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "373e89b132cc3857c1cde2ce283bcc183c205904beacc7cac25b69672f861852",
  "skill_revision": "git:46096e5ba0465b0beaa162fb3a259a1075995b40",
  "skill_tree_status": "clean",
  "skills": [
    "a-share-company-tracking",
    "a-share-disclosure-trading-data"
  ],
  "status": "ok"
}
~~~

## 逐家公司完成表

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | lhb_checked | block_trade_checked | announcement_window_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002428.SZ | 云南锗业 | 1 | completed | controller_open_web_only | CNINFO T/T+1 no_hit；SZSE annList HTTP 500 source_gap；IR无新增 | 2026-08-14 东财二级 no_hit | 2026-08-14 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深交所公告源缺口；InP合同履约、客户和收入待验证 | not_used_by_policy |
| 603256.SH | 宏和科技 | 1 | completed | controller_open_web_only | CNINFO/SSE命中既已入账H1与资本事项11份；IR无新增 | 2026-08-14 东财二级 no_hit | 2026-08-14 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change_already_recorded | 特种电子布分项、客户订单、成本传导和项目执行待验证 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 1 | completed | controller_open_web_only | CNINFO/SSE T+1命中权益分派实施公告 | 2026-08-14 东财二级 no_hit | 2026-08-14 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | annual_dividend_implementation | 数据中心订单、ASP、毛利率与分派完成待验证 | not_used_by_policy |
| 301511.SZ | 德福科技 | 1 | completed | controller_open_web_only | CNINFO T/T+1 no_hit；SZSE annList HTTP 500 source_gap；IR无新增 | 2026-08-14 东财二级 no_hit | 2026-08-14 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 解禁后股东变动、HVLP认证和现金流待验证 | not_used_by_policy |
| 002384.SZ | 东山精密 | 1 | completed | controller_open_web_only | CNINFO T/T+1 no_hit；SZSE annList HTTP 500 source_gap；IR无新增 | 2026-08-14 东财二级 no_hit | 2026-08-14 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深交所公告源缺口；整合、订单和利润待验证 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 1 | completed | controller_open_web_only | CNINFO命中既入账股份转让及例行现金管理；SZSE annList HTTP 500 source_gap | 2026-08-14 东财二级 no_hit | 2026-08-14 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change_routine_cash_management | 交易所确认、过户、协同收入利润和现金流待验证 | not_used_by_policy |
| 688498.SH | 源杰科技 | 1 | completed | controller_open_web_only | CNINFO T/T+1 no_hit；SSE 0；IR无新增 | 2026-08-14 东财二级 no_hit | 2026-08-14 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 高端激光芯片客户、订单、收入和现金流待验证 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 1 | completed | controller_open_web_only | CNINFO T/T+1 no_hit；SSE 0；IR无新增 | 2026-08-14 东财二级 no_hit | 2026-08-14 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 连接器客户、订单、产品收入和盈利待验证 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 1 | completed | controller_open_web_only | CNINFO T/T+1 no_hit；SZSE annList HTTP 500 source_gap；IR无新增 | 2026-08-14 东财二级 no_hit | 2026-08-14 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深交所公告源缺口；1.6T/CPO订单收入待验证 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 1 | completed | controller_open_web_only | CNINFO命中已处理募集资金专户注销；SZSE annList HTTP 500 source_gap | 2026-08-14 东财二级 no_hit | 2026-08-14 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change_already_recorded | 深交所公告源缺口；AIDC电源客户订单收入待验证 | not_used_by_policy |
| 000636.SZ | 风华高科 | 1 | completed | controller_open_web_only | CNINFO T/T+1 no_hit；SZSE annList HTTP 500 source_gap；IR无新增 | 2026-08-14 东财二级 no_hit | 2026-08-14 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深交所公告源缺口；注销执行与高端MLCC经营量化待验证 | not_used_by_policy |
| 688048.SH | 长光华芯 | 1 | completed | controller_open_web_only | CNINFO T/T+1 no_hit；SSE 0；IR无新增 | 2026-08-14 东财二级 no_hit | 2026-08-14 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 200G及以上产品客户订单收入待验证 | not_used_by_policy |
| 301217.SZ | 铜冠铜箔 | 1 | completed | controller_open_web_only | CNINFO命中两项治理公告；SZSE annList HTTP 500 source_gap | 2026-08-14 东财二级 no_hit | 2026-08-14 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | governance_temp_duties_and_employee_director | 履职恢复、HVLP分代客户订单收入和现金流待验证 | not_used_by_policy |

## 端到端验证门

- snapshot 已在任何业务写入前生成。
- 2026-08-14T20:54:04+08:00 执行 validate：status=passed。
- validation_result: completion_table_count=13；enabled_company_count=13；new_event_count=3；event_append_only=passed；workbook_round_trip=passed。
