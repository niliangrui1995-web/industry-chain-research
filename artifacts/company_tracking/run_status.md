# A 股公司持续跟踪运行状态

- run_date: 2026-09-03
- run_mode: 晚间 T/T+1
- run_started_at_beijing: 2026-09-03T20:31:34+08:00
- run_closed_at_beijing: 2026-09-03T20:49:13+08:00
- announcement_window: T=2026-09-03；T_plus_1=2026-09-04（前瞻窗口）
- enabled_company_count: 13
- baseline_created_count: 0
- baseline_refresh_count: 0
- state_updated_count: 13
- event_append_count: 0
- financial_evidence_audit_count: 0
- financial_evidence_audit_status: not_required_no_decision_critical_derived_figures
- multi_agent_status: not_used_by_policy
- snapshot_status: snapshot_created
- snapshot_path: artifacts/company_tracking/.run_validation_snapshot.tmp
- postwrite_validation: passed

## 运行元数据（完整）

~~~json
{
  "captured_at_beijing": "2026-09-03T20:31:34+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "373e89b132cc3857c1cde2ce283bcc183c205904beacc7cac25b69672f861852",
  "skill_revision": "git:320934a92043f3bc249c204522eba187a2532daf",
  "skill_tree_status": "clean",
  "skills": [
    "a-share-company-tracking",
    "a-share-disclosure-trading-data"
  ],
  "status": "ok"
}
~~~

## 来源可用性与边界

- CNINFO 公司名查询为公告主源；沪市同时回查 SSE 公司公告接口。8 家深市公司对应 SZSE annList 均返回 HTTP 500，逐家写为 source_gap。
- 深市 2026-09-03 龙虎榜和大宗交易官方逐公司查询均为 recordcount=0。沪市交易公开信息未命中；沪市逐证券大宗交易无可消费官方回读，东方财富二级 code=9201 空结果不写作官方零记录。
- 每家公司均完成独立最近 24 小时公开网页观察。非官方材料仅用于线索、反证或管理层口径，不升级为客户、订单、收入、量产或行业需求事实。

## Per-company completion table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | lhb_checked | block_trade_checked | announcement_window_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
|---|---|---:|---|---|---|---|---|---|---|---|---|---|
| 002428.SZ | 云南锗业 | 1 | completed | controller_single_company_official_and_open_web | CNINFO公司名0；SZSE annList HTTP500 source_gap | SZSE ShowReport 9/3 recordcount=0 | SZSE ShowReport 9/3 recordcount=0 | T_and_T_plus_1 | searched_no_new_operating_signal | updated_no_change | 深市公告交叉源故障；InP合同履约、验收与回款待核验 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed | controller_single_company_official_and_open_web | CNINFO/SSE公司公告0 | SSE交易公开信息9/3未命中 | SSE逐证券官方回读缺口；东财二级code=9201空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | updated_no_change | 沪市大宗交易source_gap；授信提款、债转股与黄石项目执行待核验 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed | controller_single_company_official_and_open_web | CNINFO/SSE公司公告0 | SSE交易公开信息9/3未命中 | SSE逐证券官方回读缺口；东财二级code=9201空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | updated_no_change | 沪市大宗交易source_gap；光纤需求、海外项目和订单兑现待核验 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed | controller_single_company_official_and_open_web | CNINFO公司名0；SZSE annList HTTP500 source_gap | SZSE ShowReport 9/3 recordcount=0 | SZSE ShowReport 9/3 recordcount=0 | T_and_T_plus_1 | searched_no_new_operating_signal | updated_no_change | 深市公告交叉源故障；HVLP/RTF客户、收入和回款待核验 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed | controller_single_company_official_and_open_web | CNINFO公司名0；SZSE annList HTTP500 source_gap | SZSE ShowReport 9/3 recordcount=0 | SZSE ShowReport 9/3 recordcount=0 | T_and_T_plus_1 | searched_no_new_operating_signal | updated_no_change | 深市公告交叉源故障；光电互连客户、订单和并购整合待核验 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed | controller_single_company_official_and_open_web | CNINFO公司名1份H股翌日披露报表；SZSE annList HTTP500 source_gap | SZSE ShowReport 9/3 recordcount=0 | SZSE ShowReport 9/3 recordcount=0 | T_and_T_plus_1 | searched_routine_official_disclosure | updated_routine_disclosure | 深市公告交叉源故障；累计回购、质押变动和客户订单/收入拆分待核验 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed | controller_single_company_official_and_open_web | CNINFO2份程序性公告；SSE公司公告0 source_difference | SSE科创板交易公开信息9/3未命中 | SSE逐证券官方回读缺口；东财二级code=9201空结果 | T_and_T_plus_1 | searched_official_procedure_notice | updated_procedure_only | 沪市大宗交易source_gap；9月10日问答、客户、单产品收入和200G验证待核验 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed | controller_single_company_official_and_open_web | CNINFO/SSE公司公告0 | SSE科创板交易公开信息9/3未命中 | SSE逐证券官方回读缺口；东财二级code=9201空结果 | T_and_T_plus_1 | searched_secondary_management_observation | updated_secondary_observation | 液冷仍缺原始订单/收入核验；沪市大宗交易source_gap | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed | controller_single_company_official_and_open_web | CNINFO公司名0；SZSE annList HTTP500 source_gap | SZSE ShowReport 9/3 recordcount=0 | SZSE ShowReport 9/3 recordcount=0 | T_and_T_plus_1 | searched_existing_management_claim | updated_no_change | 深市公告交叉源故障；实际授予、费用和客户、收入待核验 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed | controller_single_company_official_and_open_web | CNINFO2份已入账T+1公告；SZSE annList HTTP500 source_gap | SZSE ShowReport 9/3 recordcount=0 | SZSE ShowReport 9/3 recordcount=0 | T_and_T_plus_1 | searched_official_duplicate_confirmed | updated_existing_events_revalidated | 深市公告交叉源故障；子公司融资、AIDC客户、订单、收入拆分和现金流待核验 | not_used_by_policy |
| 000636.SZ | 风华高科 | 11 | completed | controller_single_company_official_and_open_web | CNINFO公司名0；SZSE annList HTTP500 source_gap | SZSE ShowReport 9/3 recordcount=0 | SZSE ShowReport 9/3 recordcount=0 | T_and_T_plus_1 | searched_management_claim_pending_primary | updated_observation_pending_primary | 深市公告交叉源故障；IR原文、AI MLCC拆分、库存和回款待核验 | not_used_by_policy |
| 688048.SH | 长光华芯 | 12 | completed | controller_single_company_official_and_open_web | CNINFO/SSE公司公告0 | SSE科创板交易公开信息9/3未命中 | SSE逐证券官方回读缺口；东财二级code=9201空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | updated_no_change | 沪市大宗交易source_gap；光通信毛利率、现金流、非关联客户和200G EML待核验 | not_used_by_policy |
| 301217.SZ | 铜冠铜箔 | 13 | completed | controller_single_company_official_and_open_web | CNINFO公司名0；SZSE annList HTTP500 source_gap | SZSE ShowReport 9/3 recordcount=0 | SZSE ShowReport 9/3 recordcount=0 | T_and_T_plus_1 | searched_no_new_operating_signal | updated_no_change | 深市公告交叉源故障；HVLP分代、现金流与客户验证待核验 | not_used_by_policy |

## 最终对账

- baseline_created=0；baseline_refresh=0；state_updated=13；event_append=0；财务审计=0。
- Excel 已同步 13 家 enabled 行的 last_update_date=2026-09-03；所有公司均处于 completion table 终态且保持 watchlist 顺序。
- postwrite_validation: passed；validator_result={"completion_table_count":13,"enabled_company_count":13,"event_append_only":"passed","new_event_count":0,"status":"passed","workbook_round_trip":"passed"}。
