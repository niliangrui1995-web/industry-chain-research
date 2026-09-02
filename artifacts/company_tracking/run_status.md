# A 股公司持续跟踪运行状态

- run_date: 2026-09-02
- run_mode: 晚间 T/T+1
- announcement_window: T=2026-09-02；T_plus_1=2026-09-03（可访问）
- enabled_company_count: 13
- baseline_created_count: 0
- baseline_refresh_count: 0
- state_updated_count: 3
- event_append_count: 5
- financial_evidence_audit_count: 0
- financial_evidence_audit_status: not_required_no_decision_critical_derived_figures
- multi_agent_status: not_used_by_policy
- snapshot_status: snapshot_created
- snapshot_path: artifacts/company_tracking/.run_validation_snapshot.tmp
- postwrite_validation: passed

## 运行元数据（完整）

~~~json
{
  "captured_at_beijing": "2026-09-02T22:32:50+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_revision": "git:b8ed468ccbb8808ed40e1b337c0161dccfcfb994",
  "skill_tree_status": "clean",
  "skills": [
    "a-share-company-tracking",
    "a-share-disclosure-trading-data"
  ],
  "skill_content_sha256": {
    "a-share-company-tracking": "011e59462fcbca54aecf2f2764f8e47dc8c46cdafcb37a0b2fd32d5c7e349e2f",
    "a-share-disclosure-trading-data": "ba7bb5d35e78dd4b08d771fe5d4d7ceb8a8924967e95ed9a9c21a0dff1b8089a"
  },
  "metadata_by_skill": [
    {
      "captured_at_beijing": "2026-09-02T22:32:50+08:00",
      "prompt_contract_version": "2026-07-27.1",
      "skill_content_sha256": "011e59462fcbca54aecf2f2764f8e47dc8c46cdafcb37a0b2fd32d5c7e349e2f",
      "skill_revision": "git:b8ed468ccbb8808ed40e1b337c0161dccfcfb994",
      "skill_tree_status": "clean",
      "skills": ["a-share-company-tracking"],
      "status": "ok"
    },
    {
      "captured_at_beijing": "2026-09-02T22:32:50+08:00",
      "prompt_contract_version": "2026-07-27.1",
      "skill_content_sha256": "ba7bb5d35e78dd4b08d771fe5d4d7ceb8a8924967e95ed9a9c21a0dff1b8089a",
      "skill_revision": "git:b8ed468ccbb8808ed40e1b337c0161dccfcfb994",
      "skill_tree_status": "clean",
      "skills": ["a-share-disclosure-trading-data"],
      "status": "ok"
    }
  ],
  "status": "ok"
}
~~~

## 来源可用性与边界

- 公告主源为 CNINFO 的精确 `代码,orgId` 查询；出现线索而精确查询返回 0 时，仅对该公司以公司名复核。沪市公司另以 SSE 公司公告接口交叉。8 家深市公司对应 SZSE `annList` 均返回 HTTP 500，逐家保留为 `source_gap`。
- 2026-09-02 深市龙虎榜和大宗交易官方逐公司查询均为 `recordcount=0`。沪市逐证券官方交易数据本轮没有可消费回读；东方财富二级空结果仅作辅助，不写为交易所官方零记录。
- 每家公司均完成单独的最近 24 小时公开网页观察；非官方材料只用于线索发现、反证或管理层口径边界，不升级为客户、订单、收入或量产事实。

## Per-company completion table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | lhb_checked | block_trade_checked | announcement_window_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
|---|---|---:|---|---|---|---|---|---|---|---|---|---|
| 002428.SZ | 云南锗业 | 1 | completed | controller_single_company_official_and_open_web | CNINFO精确代码+org 0；SZSE annList HTTP 500 source_gap | SZSE 9/2 recordcount=0 | SZSE 9/2 recordcount=0 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市交叉源故障；InP合同履约、验收与回款待核验 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed | controller_single_company_official_and_open_web | CNINFO/SSE 0 | SSE逐证券交易数据无可消费回读；东财二级code=9201空结果 | SSE逐证券交易数据无可消费回读；东财二级code=9201空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | SSE交易数据source_gap；授信提款、债转股与黄石项目执行待核验 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed | controller_single_company_official_and_open_web | CNINFO/SSE 0 | SSE逐证券交易数据无可消费回读；东财二级code=9201空结果 | SSE逐证券交易数据无可消费回读；东财二级code=9201空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | SSE交易数据source_gap；光纤需求、海外项目和订单兑现待核验 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed | controller_single_company_official_and_open_web | CNINFO公司名复核2；精确代码+org 0；SZSE annList HTTP 500 source_gap | SZSE 9/2 recordcount=0 | SZSE 9/2 recordcount=0 | T_and_T_plus_1 | searched_official_event_confirmed | updated_2_events | 精确代码查询延迟及深市交叉源故障；HVLP/RTF客户、收入和回款待核验 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed | controller_single_company_official_and_open_web | CNINFO精确代码+org 0；回购进展为既有累计数据重复；SZSE annList HTTP 500 source_gap | SZSE 9/2 recordcount=0 | SZSE 9/2 recordcount=0 | T_and_T_plus_1 | searched_official_duplicate_no_new_event | no_change_duplicate | 深市交叉源故障；光电互连客户、订单和并购整合待核验 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed | controller_single_company_official_and_open_web | CNINFO公司名复核3；精确代码+org 0；SZSE annList HTTP 500 source_gap | SZSE 9/2 recordcount=0 | SZSE 9/2 recordcount=0 | T_and_T_plus_1 | searched_official_event_confirmed | updated_1_event | 精确代码查询延迟及深市交叉源故障；质押变动、累计回购和客户订单/收入拆分待核验 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed | controller_single_company_official_and_open_web | CNINFO精确代码+org 0；SSE T+1业绩说明会通知1 | SSE逐证券交易数据无可消费回读；东财二级code=9201空结果 | SSE逐证券交易数据无可消费回读；东财二级code=9201空结果 | T_and_T_plus_1 | searched_official_procedure_notice_no_new_event | no_change_procedure_only | SSE交易数据source_gap；客户、单产品收入、200G验证与回款待核验 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed | controller_single_company_official_and_open_web | CNINFO/SSE 0 | SSE逐证券交易数据无可消费回读；东财二级code=9201空结果 | SSE逐证券交易数据无可消费回读；东财二级code=9201空结果 | T_and_T_plus_1 | searched_management_reaffirmation_no_new_event | no_change_reaffirmed | 液冷仍小批量、未量产；连接器订单、毛利率和激励执行待核验 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed | controller_single_company_official_and_open_web | CNINFO精确代码+org 0；SZSE annList HTTP 500 source_gap | SZSE 9/2 recordcount=0 | SZSE 9/2 recordcount=0 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市交叉源故障；实际授予、费用和客户、收入待核验 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed | controller_single_company_official_and_open_web | CNINFO公司名复核2；精确代码+org 0；SZSE annList HTTP 500 source_gap | SZSE 9/2 recordcount=0 | SZSE 9/2 recordcount=0 | T_and_T_plus_1 | searched_official_event_confirmed | updated_2_events | 精确代码查询延迟及深市交叉源故障；子公司融资、AIDC客户、订单、收入拆分和现金流待核验 | not_used_by_policy |
| 000636.SZ | 风华高科 | 11 | completed | controller_single_company_official_and_open_web | CNINFO精确代码+org 0；SZSE annList HTTP 500 source_gap | SZSE 9/2 recordcount=0 | SZSE 9/2 recordcount=0 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市交叉源故障；AI MLCC拆分、库存和回款待核验 | not_used_by_policy |
| 688048.SH | 长光华芯 | 12 | completed | controller_single_company_official_and_open_web | CNINFO/SSE 0 | SSE逐证券交易数据无可消费回读；东财二级code=9201空结果 | SSE逐证券交易数据无可消费回读；东财二级code=9201空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | SSE交易数据source_gap；光通信毛利率、现金流、非关联客户和200G EML待核验 | not_used_by_policy |
| 301217.SZ | 铜冠铜箔 | 13 | completed | controller_single_company_official_and_open_web | CNINFO精确代码+org 0；SZSE annList HTTP 500 source_gap | SZSE 9/2 recordcount=0 | SZSE 9/2 recordcount=0 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市交叉源故障；HVLP分代、现金流与客户验证待核验 | not_used_by_policy |

## 最终对账

- baseline_created=0；baseline_refresh=0；state_updated=3；event_append=5；财务审计=0（未产生决策关键的派生财务数字）。
- Excel 已同步 13 家 enabled 行的 `last_update_date=2026-09-02`；所有公司均处于 completion table 终态且保持 watchlist 顺序。
- postwrite_validation: passed；validator_result={"completion_table_count":13,"enabled_company_count":13,"event_append_only":"passed","new_event_count":5,"status":"passed","workbook_round_trip":"passed"}。
