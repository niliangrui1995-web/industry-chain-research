# A 股公司持续跟踪运行状态

- run_date: 2026-08-25
- run_started_at_beijing: 2026-08-25T20:32:31+08:00
- announcement_window_checked: T_and_T_plus_1
- run_status: completed
- run_finished_at_beijing: 2026-08-25T20:58:33+08:00
- enabled_company_count: 13
- completed_company_count: 13
- baseline_created_or_refreshed_count: 0
- baseline_identifier_mapping_count: 0
- state_updated_count: 2
- events_appended_count: 2
- excel_last_update_date_synced_count: 13
- open_web_search_completed_count: 13
- open_web_new_operating_signal_count: 1_secondary_management_claim
- open_web_new_operating_hard_fact_count: 0
- financial_evidence_audit: not_required；无估值、预期差、覆盖率、单位换算或派生的决策财务数字，未执行 formal audit release。
- multi_agent_status: not_used_by_policy
- source_limitations: 深市 8 家 annList 均返回 HTTP 500，按 source_gap 保留，CNINFO 为公告主源。上交所 5 家公司公告查询均可用并返回 0。CNINFO 对天孚通信 T+1 命中 1 项程序性激励公告；长飞光纤、鼎通科技和长光华芯的前轮 T+1 项已去重。
- trading_data_limitations: 龙虎榜与大宗交易为逐家公司查询。长飞光纤的龙虎榜由上交所交易公开信息确认，并以东方财富二级明细交叉；东山精密和中际旭创仅有小额二级大宗交易记录，均未据此推导股东或经营结论。其余二级结果为 code=9201/返回数据为空，不等同交易所官方零事件。
- write_snapshot: artifacts/company_tracking/.run_validation_snapshot.tmp

## 运行元数据（完整）

~~~json
{
  "captured_at_beijing": "2026-08-25T20:32:31+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "373e89b132cc3857c1cde2ce283bcc183c205904beacc7cac25b69672f861852",
  "skill_revision": "git:2a5b67b2d8ef087df87b5a893bde6b1f94a0164f",
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
| 601869.SH | 长飞光纤 | 3 | completed | controller_single_company | CNINFO 0；SSE 0；前轮 T+1 已去重 | 上交所公开信息命中；东财二级交叉 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | official_trading_event_recorded | 分产品收入、客户订单、现金流及高波动持续性待验证 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed | controller_single_company | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | secondary_management_claim_recorded | secondary_management_claim_recorded | 原始互动易、设备投用、HVLP 客户订单和现金流待验证 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed | controller_single_company | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 1 笔 3,528,000 元，小额不入账 | T_and_T_plus_1 | searched_no_new_operating_signal | no_ledger_change_secondary_small_block_trade | 1.6T、AI PCB 客户、订单、收入与产能待验证 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed | controller_single_company | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 2 条同笔 2,961,000 元，小额不入账 | T_and_T_plus_1 | searched_no_new_operating_signal | no_ledger_change_secondary_small_block_trade | 800G、1.6T、NPO 客户订单和收入待验证 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed | controller_single_company | CNINFO 0；SSE 0 | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | CW、EML 客户、订单、分产品收入和现金流待验证 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed | controller_single_company | CNINFO 0；SSE 0；前轮 T+1 已去重 | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 股份登记、液冷订单和连接器经营兑现待验证 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed | controller_single_company | CNINFO T+1 1 项程序性公告；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_ledger_change_official_procedure_notice | 物料、CPO/1.6T 订单、泰国产能和现金流待验证 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed | controller_single_company | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | AIDC 电源客户、订单、收入和毛利率待验证 | not_used_by_policy |
| 000636.SZ | 风华高科 | 11 | completed | controller_single_company | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 高端 MLCC 客户、订单、收入和 ASP 待验证 | not_used_by_policy |
| 688048.SH | 长光华芯 | 12 | completed | controller_single_company | CNINFO 0；SSE 0；前轮 T+1 已去重 | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 分期回款、坏账转回、现金流及 EML 订单待验证 | not_used_by_policy |
| 301217.SZ | 铜冠铜箔 | 13 | completed | controller_single_company | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 code=9201 空结果 | 东财二级 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 高管补聘、HVLP 客户、订单和现金流待验证 | not_used_by_policy |

## 端到端验证门

- snapshot 已在任何业务写入前生成。
- 2026-08-25T20:58:33+08:00 执行 validate：status=passed。
- validation_result: completion_table_count=13；enabled_company_count=13；new_event_count=2；event_append_only=passed；workbook_round_trip=passed。
