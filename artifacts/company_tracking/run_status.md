# A 股公司持续跟踪运行状态

- run_date: 2026-08-24
- run_started_at_beijing: 2026-08-24T20:31:24+08:00
- announcement_window_checked: T_and_T_plus_1
- run_status: completed
- run_finished_at_beijing: 2026-08-24T21:02:48+08:00
- enabled_company_count: 13
- completed_company_count: 13
- baseline_created_or_refreshed_count: 0
- baseline_identifier_mapping_count: 0
- state_updated_count: 5
- events_appended_count: 5
- excel_last_update_date_synced_count: 13
- open_web_search_completed_count: 13
- open_web_new_operating_signal_count: 2_secondary_issuer_authored_ir_records
- open_web_new_operating_hard_fact_count: 0
- financial_evidence_audit: not_required；无估值、预期差、覆盖率、单位换算或派生的决策财务数字，未执行 formal audit release。
- multi_agent_status: not_used_by_policy
- source_limitations: 深市8家 annList 均返回 HTTP 500，按 source_gap 保留，CNINFO 为公告主源。上交所公司公告查询对长飞光纤出现一次 ReadTimeout；CNINFO 已确认其 T+1 文件。东方财富交易接口初始日期格式错误已排除，按正确日期格式逐公司复核后均返回 code=9201/返回数据为空；这是二级数据空结果，不等同交易所官方零事件。
- trading_data_limitations: 龙虎榜与大宗交易为东方财富二级数据逐家公司查询；13 家均为 code=9201/返回数据为空，无可入账新增交易事件。深市交易所端存在接口可用性缺口，未将其扩写为官方“无上榜/无大宗交易”。
- write_snapshot: artifacts/company_tracking/.run_validation_snapshot.tmp

## 运行元数据（完整）

~~~json
{
  "captured_at_beijing": "2026-08-24T20:31:24+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "373e89b132cc3857c1cde2ce283bcc183c205904beacc7cac25b69672f861852",
  "skill_revision": "git:65734ce614bf2d2fb00985793ff4d1f52e4785f6",
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
| 002428.SZ | 云南锗业 | 1 | completed | controller_single_company | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | InP 合同交付、验收、客户及收入待验证 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed | controller_single_company | CNINFO 0；SSE 0 | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 特种电子布客户、订单和项目执行待验证 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed | controller_single_company | CNINFO T+1 2 项；SSE ReadTimeout source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | official_capital_governance | 9月11日股东会、实际分红及 H 股奖励计划待验证 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed | controller_single_company | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 客户认证、订单与经营现金流待验证 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed | controller_single_company | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | secondary_ir_management_claim_recorded | management_claim_ir_recorded | 1.6T/AI PCB 客户、订单、收入与产能待验证 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed | controller_single_company | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | secondary_ir_management_claim_recorded | management_claim_ir_recorded | 2027订单、NPO 样品、出货及收入待验证 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed | controller_single_company | CNINFO 0；SSE 0 | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 高端激光芯片客户、订单、收入和现金流待验证 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed | controller_single_company | CNINFO T+1 4 项；SSE 0 | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | official_capital_structure | 股份登记、实际股本变化与连接器经营兑现待验证 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed | controller_single_company | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 物料、CPO/1.6T 订单、泰国产能和现金流待验证 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed | controller_single_company | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | AIDC 电源客户、订单、收入和毛利率待验证 | not_used_by_policy |
| 000636.SZ | 风华高科 | 11 | completed | controller_single_company | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 高端 MLCC 客户、订单、收入和 ASP 待验证 | not_used_by_policy |
| 688048.SH | 长光华芯 | 12 | completed | controller_single_company | CNINFO T+1 1 项；SSE 0 | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | official_receivable_settlement | 分期回款、坏账转回及现金流待验证 | not_used_by_policy |
| 301217.SZ | 铜冠铜箔 | 13 | completed | controller_single_company | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 高管补聘、HVLP 客户、订单和现金流待验证 | not_used_by_policy |

## 端到端验证门

- snapshot 已在任何业务写入前生成。
- 2026-08-24T21:02:48+08:00 执行 validate：status=passed。
- validation_result: completion_table_count=13；enabled_company_count=13；new_event_count=5；event_append_only=passed；workbook_round_trip=passed。
