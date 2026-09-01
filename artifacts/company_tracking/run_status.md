# A 股公司持续跟踪运行状态

- run_date: 2026-08-31
- run_mode: 晚间 T/T+1，含 2026-08-30 补扫
- enabled_company_count: 13
- baseline_created_count: 0
- baseline_refresh_count: 0
- state_updated_count: 4
- event_append_count: 6
- financial_evidence_audit_count: 1
- financial_evidence_audit_status: 688048.SH PASS/publishable 4/4
- multi_agent_status: not_used_by_policy
- snapshot_status: snapshot_created
- snapshot_path: artifacts/company_tracking/.run_validation_snapshot.tmp

## 运行元数据（完整）

~~~json
{
  "captured_at_beijing": "2026-08-31T20:36:42+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "223840607b9814d4d960aec4d2ab728ebf2e08be8b4d4cb82e8d659db8b9c3fb",
  "skill_revision": "git:70322d0618433338b66ac7fde69473df60ff7f2f",
  "skill_tree_status": "clean",
  "skills": [
    "a-share-company-tracking",
    "a-share-disclosure-trading-data",
    "financial-evidence-audit"
  ],
  "status": "ok"
}
~~~

## 来源可用性与边界

- 晚间公告回扫覆盖 `2026-08-31` 与可访问的 `2026-09-01`，并补扫 `2026-08-30`。CNINFO 是公告主源；8 家深市公司对应的 SZSE annList 返回 HTTP 500，记为 `source_gap`。
- 龙虎榜与大宗交易均按公司逐一查询；二级接口对 2026-08-31 返回 `code=9201` 空结果，不等于交易所官方零记录。
- native open-web 搜索也按公司逐一执行；非官方结果只作为线索，未升级为订单、客户或收入事实。

## Per-company completion table

| ticker | name | batch_no | queue_status | collection_scope | announcements_checked | lhb_checked | block_trade_checked | announcement_window_checked | open_web_search_status | state_change | miss_risk_notes | multi_agent_status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 002428.SZ | 云南锗业 | 1 | completed | official_filings_and_open_web | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 8/31 code=9201 空结果 | 东财二级 8/31 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市交叉源故障；InP合同履约/回款待核验 | not_used_by_policy |
| 603256.SH | 宏和科技 | 2 | completed | official_filings_and_open_web | CNINFO/SSE 2：T+1股东会决议、法律意见 | 东财二级 8/31 code=9201 空结果 | 东财二级 8/31 code=9201 空结果 | T_and_T_plus_1 | searched_official_event_confirmed_no_extra_signal | updated_1_event | 实际提款、债转股与黄石项目待核验 | not_used_by_policy |
| 601869.SH | 长飞光纤 | 3 | completed | official_filings_and_open_web | CNINFO/SSE 0 | 东财二级 8/31 code=9201 空结果 | 东财二级 8/31 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 光纤需求、海外项目和订单兑现待核验 | not_used_by_policy |
| 301511.SZ | 德福科技 | 4 | completed | official_filings_and_open_web | CNINFO 1：投资者开放日安排；SZSE HTTP 500 source_gap | 东财二级 8/31 code=9201 空结果 | 东财二级 8/31 code=9201 空结果 | T_and_T_plus_1 | searched_official_event_confirmed_no_extra_signal | no_change_schedule_only | 深市交叉源故障；高端铜箔客户/回款待核验 | not_used_by_policy |
| 002384.SZ | 东山精密 | 5 | completed | official_filings_and_open_web | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 8/31 code=9201 空结果 | 东财二级 8/31 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市交叉源故障；光电互连/并购整合待核验 | not_used_by_policy |
| 300308.SZ | 中际旭创 | 6 | completed | official_filings_and_open_web | CNINFO 3：董事会、回购方案、H股次日披露；SZSE HTTP 500 source_gap | 东财二级 8/31 code=9201 空结果 | 东财二级 8/31 code=9201 空结果 | T_and_T_plus_1 | searched_official_event_confirmed_no_extra_signal | updated_1_event | 深市交叉源故障；回购执行与客户/收入拆分待核验 | not_used_by_policy |
| 688498.SH | 源杰科技 | 7 | completed | official_filings_and_open_web | CNINFO/SSE 0 | 东财二级 8/31 code=9201 空结果 | 东财二级 8/31 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 客户、单产品收入、200G验证与回款待核验 | not_used_by_policy |
| 688668.SH | 鼎通科技 | 8 | completed | official_filings_and_open_web | CNINFO/SSE 0 | 东财二级 8/31 code=9201 空结果 | 东财二级 8/31 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 连接器订单、毛利率和激励执行待核验 | not_used_by_policy |
| 300394.SZ | 天孚通信 | 9 | completed | official_filings_and_open_web | CNINFO 3：股东会、法律意见、激励自查；SZSE HTTP 500 source_gap | 东财二级 8/31 code=9201 空结果 | 东财二级 8/31 code=9201 空结果 | T_and_T_plus_1 | searched_official_event_confirmed_no_extra_signal | updated_1_event | 深市交叉源故障；实际授予、费用和客户/收入待核验 | not_used_by_policy |
| 002851.SZ | 麦格米特 | 10 | completed | official_filings_and_open_web | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 8/31 code=9201 空结果 | 东财二级 8/31 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市交叉源故障；AIDC拆分/现金流待核验 | not_used_by_policy |
| 000636.SZ | 风华高科 | 11 | completed | official_filings_and_open_web | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 8/31 code=9201 空结果 | 东财二级 8/31 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市交叉源故障；AI MLCC拆分、库存和回款待核验 | not_used_by_policy |
| 688048.SH | 长光华芯 | 12 | completed | official_filings_and_open_web | CNINFO/SSE 6：中报、减值、关联交易等 | 东财二级 8/31 code=9201 空结果 | 东财二级 8/31 code=9201 空结果 | T_and_T_plus_1 | searched_official_event_confirmed_no_extra_signal | updated_3_events | 光通信毛利率、现金流、非关联客户与200G验证待核验 | not_used_by_policy |
| 301217.SZ | 铜冠铜箔 | 13 | completed | official_filings_and_open_web | CNINFO 0；SZSE HTTP 500 source_gap | 东财二级 8/31 code=9201 空结果 | 东财二级 8/31 code=9201 空结果 | T_and_T_plus_1 | searched_no_new_operating_signal | no_change | 深市交叉源故障；HVLP分代、现金流与客户验证待核验 | not_used_by_policy |

## 最终对账

- baseline_created=0；baseline_refresh=0；state_updated=4；event_append=6；财务审计=688048.SH 1 份且 4/4 通过。
- Excel 仅变更 13 家 enabled 行的 `last_update_date=2026-08-31`；所有公司均处于 completion table 终态且保持 watchlist 顺序。
- postwrite_validation: passed；validator_result={"completion_table_count":13,"enabled_company_count":13,"event_append_only":"passed","new_event_count":6,"status":"passed","workbook_round_trip":"passed"}
