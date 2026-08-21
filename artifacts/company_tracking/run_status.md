# A 股公司持续跟踪运行状态

- run_date: 2026-08-20
- run_started_at_beijing: 2026-08-20T20:32:01+08:00
- announcement_window_checked: T_and_T_plus_1
- run_status: completed
- run_finished_at_beijing: 2026-08-20T21:11:27+08:00
- enabled_company_count: 13
- completed_company_count: 13
- baseline_created_or_refreshed_count: 0
- baseline_identifier_mapping_count: 0
- state_updated_count: 2
- events_appended_count: 2
- excel_last_update_date_synced_count: 13
- open_web_search_completed_count: 13
- open_web_new_operating_signal_count: 1_secondary_not_hard_fact
- open_web_new_operating_hard_fact_count: 0
- financial_evidence_audit: calc_only_passed_368033000；无估值、预期差、覆盖率或派生财务结论，未执行 formal audit release。
- multi_agent_status: not_used_by_policy
- source_limitations: 深市8家 annList 本轮分别出现 HTTP 500、ReadTimeout 或 TLS 连接错误，均按 source_gap 保留；CNINFO 为深市公告的一手替代来源。上交所5家 issuer 查询可用且为0。
- trading_data_limitations: 龙虎榜和大宗交易均为东方财富二级数据逐家公司查询。龙虎榜13家无新增返回；大宗交易仅宏和科技8月17日53笔折价记录入账，其余小额记录不外推经营。
- write_snapshot: artifacts/company_tracking/.run_validation_snapshot.tmp

## 运行元数据（完整）

~~~json
{
  "captured_at_beijing": "2026-08-20T21:00:55+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "223840607b9814d4d960aec4d2ab728ebf2e08be8b4d4cb82e8d659db8b9c3fb",
  "skill_revision": "git:558ddced76820e5be99ac7ebc330a0774339d47f",
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
| 002428.SZ | 云南锗业 | 1 | completed | controller_open_web_only | CNINFO恢复窗口 no_hit；SZSE annList HTTP 500 source_gap；IR无新增 | 2026-08-15至20 东财二级 no_hit | 2026-08-15至20 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | InP合同履约、客户和收入待验证；深市公告源缺口 | not_used_by_policy |
| 603256.SH | 宏和科技 | 1 | completed | controller_open_web_only | CNINFO/SSE恢复窗口 no_hit；IR无新增 | 2026-08-15至20 东财二级 no_hit | 8月17日53笔折价记录已入账；8月20日小额记录不改变状态 | T_and_T_plus_1 | searched_no_new_operating_signal | secondary_block_trade_cluster | 交易所原始明细、股东身份、特种电子布客户订单和项目执行待验证 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 1 | completed | controller_open_web_only | CNINFO/SSE恢复窗口 no_hit；IR无新增 | 2026-08-15至20 东财二级 no_hit | 8月17日1笔小额记录，未入账 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 数据中心订单、ASP、毛利率与现金流待验证 | not_used_by_policy |
| 301511.SZ | 德福科技 | 1 | completed | controller_open_web_only | CNINFO恢复窗口 no_hit；SZSE annList HTTP 500 source_gap；IR无新增 | 2026-08-15至20 东财二级 no_hit | 2026-08-15至20 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 解禁后股东变动、HVLP认证和现金流待验证 | not_used_by_policy |
| 002384.SZ | 东山精密 | 1 | completed | controller_open_web_only | CNINFO恢复窗口 no_hit；SZSE annList timeout source_gap；IR无新增 | 2026-08-15至20 东财二级 no_hit | 8月20日1笔约593.01万元小额记录，未入账 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 整合、客户订单和利润待验证；深市公告源缺口 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 1 | completed | controller_open_web_only | CNINFO恢复窗口 no_hit；SZSE annList timeout source_gap；IR无新增 | 2026-08-15至20 东财二级 no_hit | 8月17日1笔约340.35万元小额记录，未入账 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 交易所确认、过户、协同收入利润和现金流待验证 | not_used_by_policy |
| 688498.SH | 源杰科技 | 1 | completed | controller_open_web_only | CNINFO恢复窗口 no_hit；SSE 0；IR无新增 | 2026-08-15至20 东财二级 no_hit | 2026-08-15至20 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 高端激光芯片客户、订单、收入和现金流待验证 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 1 | completed | controller_open_web_only | CNINFO恢复窗口 no_hit；SSE 0；IR无新增 | 2026-08-15至20 东财二级 no_hit | 2026-08-15至20 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 连接器客户、订单、产品收入和盈利待验证 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 1 | completed | controller_open_web_only | CNINFO恢复窗口 no_hit；SZSE annList timeout source_gap；IR无新增 | 2026-08-15至20 东财二级 no_hit | 2026-08-15至20 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 1.6T/CPO订单、收入和现金流待验证；深市公告源缺口 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 1 | completed | controller_open_web_only | CNINFO恢复窗口 no_hit；SZSE annList HTTP 500 source_gap；IR无新增 | 2026-08-15至20 东财二级 no_hit | 2026-08-15至20 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | AIDC电源客户订单收入待验证；深市公告源缺口 | not_used_by_policy |
| 000636.SZ | 风华高科 | 1 | completed | controller_open_web_only | CNINFO恢复窗口 no_hit；SZSE annList HTTP 500 source_gap；IR无新增 | 2026-08-15至20 东财二级 no_hit | 2026-08-15至20 东财二级 no_hit | T_and_T_plus_1 | searched_secondary_product_signal | secondary_parent_group_product_progress | 发行人原文、4款型号/客户/订单/收入待验证；英伟达否认口径仍有效 | not_used_by_policy |
| 688048.SH | 长光华芯 | 1 | completed | controller_open_web_only | CNINFO恢复窗口 no_hit；SSE 0；IR无新增 | 2026-08-15至20 东财二级 no_hit | 2026-08-15至20 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 200G及以上产品客户订单收入待验证 | not_used_by_policy |
| 301217.SZ | 铜冠铜箔 | 1 | completed | controller_open_web_only | CNINFO恢复窗口 no_hit；SZSE annList TLS source_gap；IR无新增 | 2026-08-15至20 东财二级 no_hit | 2026-08-15至20 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 履职恢复、HVLP分代客户订单收入和现金流待验证 | not_used_by_policy |

## 端到端验证门

- snapshot 已在任何业务写入前生成。
- 2026-08-20T21:11:27+08:00 执行 validate：status=passed。
- validation_result: completion_table_count=13；enabled_company_count=13；new_event_count=2；event_append_only=passed；workbook_round_trip=passed。
