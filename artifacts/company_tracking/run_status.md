# A 股公司持续跟踪运行状态

- run_date: 2026-08-13
- run_started_at_beijing: 2026-08-13T20:32:47+08:00
- announcement_window_checked: T_and_T_plus_1
- run_status: completed
- enabled_company_count: 13
- completed_company_count: 13
- baseline_created_or_refreshed_count: 0
- baseline_identifier_mapping_count: 1
- state_updated_count: 3
- events_appended_count: 6
- excel_last_update_date_synced_count: 13
- open_web_search_completed_count: 13
- open_web_new_operating_signal_count: 0
- financial_evidence_audit: not_applicable_no_decision_critical_derived_financial_number
- multi_agent_status: not_used_by_policy
- source_limitations: 宏和科技 SSE 公司公告接口超时；深市 annList 对德福科技返回 SSL EOF，对其余 7 家深市公司返回 HTTP 500。上述均按 source_gap 保留，CNINFO 官方原文为入账依据。
- trading_data_limitations: 龙虎榜与大宗交易均为东方财富二级数据逐家公司查询结果，2026-08-13 均未命中，不能替代交易所一手结论。
- write_snapshot: artifacts/company_tracking/.run_validation_snapshot.tmp

## 运行元数据（完整）

~~~json
{
  "captured_at_beijing": "2026-08-13T20:32:47+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "373e89b132cc3857c1cde2ce283bcc183c205904beacc7cac25b69672f861852",
  "skill_revision": "git:2c096233d26348d6090f04823d6b01d93830ca3c",
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
| 002428.SZ | 云南锗业 | 1 | completed | CNINFO、SZSE、公司IR、交易数据、独立联网观察 | CNINFO T/T+1 no_hit；SZSE annList HTTP 500 source_gap；IR无新增 | 2026-08-13 东财二级 no_hit | 2026-08-13 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深交所公告源缺口；锗价、InP及红外产品客户订单待验证 | not_used_by_policy |
| 603256.SH | 宏和科技 | 1 | completed | CNINFO、SSE、公司IR、交易数据、独立联网观察 | CNINFO命中H1和资本事项11份；SSE timeout source_gap；IR无新增 | 2026-08-13 东财二级 no_hit | 2026-08-13 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | h1_results_and_capital_allocation | 特种电子布分项、客户订单、成本传导和项目执行待验证 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 1 | completed | CNINFO、SSE、公司IR、交易数据、独立联网观察 | CNINFO T/T+1 no_hit；SSE 0；IR无新增 | 2026-08-13 东财二级 no_hit | 2026-08-13 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 空芯光纤、数据中心客户、订单和收入待验证 | not_used_by_policy |
| 301511.SZ | 德福科技 | 1 | completed | CNINFO、SZSE、公司IR、交易数据、独立联网观察 | CNINFO命中解禁公告；SZSE annList SSL EOF source_gap；IR无新增 | 2026-08-13 东财二级 no_hit | 2026-08-13 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | ipo_pre_shares_unlock | 解禁后股东变动、HVLP认证和现金流待验证 | not_used_by_policy |
| 002384.SZ | 东山精密 | 1 | completed | CNINFO、SZSE、公司IR、交易数据、独立联网观察 | CNINFO T/T+1 no_hit；SZSE annList HTTP 500 source_gap；IR无新增 | 2026-08-13 东财二级 no_hit | 2026-08-13 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深交所公告源缺口；整合、订单和利润待验证 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 1 | completed | CNINFO、SZSE、公司IR、交易数据、独立联网观察 | CNINFO命中中石科技股份转让；SZSE annList HTTP 500 source_gap；IR无增量 | 2026-08-13 东财二级 no_hit | 2026-08-13 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | zhongshi_share_transfer_agreement | 交易所确认、过户、协同收入利润和现金流待验证 | not_used_by_policy |
| 688498.SH | 源杰科技 | 1 | completed | CNINFO、SSE、公司IR、交易数据、独立联网观察 | CNINFO T/T+1 no_hit；SSE 0；IR无新增 | 2026-08-13 东财二级 no_hit | 2026-08-13 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 高端激光芯片客户、订单、收入和现金流待验证 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 1 | completed | CNINFO、SSE、公司IR、交易数据、独立联网观察 | CNINFO仅命中既有分红方案复述；SSE 0；IR无新增 | 2026-08-13 东财二级 no_hit | 2026-08-13 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change_repeated_material_only | 连接器客户、订单、产品收入和盈利待验证 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 1 | completed | CNINFO、SZSE、公司IR、交易数据、独立联网观察 | CNINFO命中既有T+1材料10份；SZSE annList HTTP 500 source_gap | 2026-08-13 东财二级 no_hit | 2026-08-13 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change_already_recorded | 深交所公告源缺口；1.6T/CPO订单收入待验证 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 1 | completed | CNINFO、SZSE、公司IR、交易数据、独立联网观察 | CNINFO命中例行资金账户结项；SZSE annList HTTP 500 source_gap | 2026-08-13 东财二级 no_hit | 2026-08-13 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change_routine_account_closure | 深交所公告源缺口；AIDC电源客户订单收入待验证 | not_used_by_policy |
| 000636.SZ | 风华高科 | 1 | completed | CNINFO、SZSE、公司IR、交易数据、独立联网观察 | CNINFO命中已于上一轮入账材料3份；SZSE annList HTTP 500 source_gap | 2026-08-13 东财二级 no_hit | 2026-08-13 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change_already_recorded | 深交所公告源缺口；注销执行与高端MLCC经营量化待验证 | not_used_by_policy |
| 688048.SH | 长光华芯 | 1 | completed | CNINFO、SSE、公司IR、交易数据、独立联网观察 | CNINFO T/T+1 no_hit；SSE 0；IR无新增 | 2026-08-13 东财二级 no_hit | 2026-08-13 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 200G及以上产品客户订单收入待验证 | not_used_by_policy |
| 301217.SZ | 铜冠铜箔 | 1 | completed | CNINFO、SZSE、公司IR、交易数据、独立联网观察 | CNINFO T/T+1 no_hit；SZSE annList HTTP 500 source_gap；IR无新增 | 2026-08-13 东财二级 no_hit | 2026-08-13 东财二级 no_hit | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深交所公告源缺口；HVLP认证客户订单收入待验证 | not_used_by_policy |

## 端到端验证门

- snapshot 已在任何业务写入前生成。
- 2026-08-13T21:04:27+08:00 执行 validate：status=passed。
- validation_result: completion_table_count=13；enabled_company_count=13；new_event_count=6；event_append_only=passed；workbook_round_trip=passed。
