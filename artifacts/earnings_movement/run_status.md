# 业绩异动新增股票含金量分析运行状态

- 状态：`completed_with_new`
- 北京时间运行起点：2026-08-10T09:04:02+08:00（周一）
- `lookback_hours=72`
- 窗口开始：2026-08-07T09:04:02+08:00
- 窗口结束：2026-08-10T09:04:02+08:00
- 数据源：`D:\vcp_hunter\紫金研选\data\vcp_hunter.db` / `kv_store.key='earnings_state'`（只读 `mode=ro`，`PRAGMA query_only=ON`，WAL 感知）
- `kv_store.updated_at`：2026-08-10 00:30:25
- `earnings_state_sha256`：`49a8d72aea2398c3afee8269e1b8665b9068afceb81cf2eb63ba3e0699f591cc`
- 原始记录数：55
- ST 剔除后数量：55
- 按代码+报告期去重后数量：53
- 72 小时窗口命中数量：5
- 历史同披露事件剔除数量：0
- 最终新增股票数量：5
- `time_filter_fallback=false`
- 事件优先级替换：`605358.SH|20260630` 财报替代 2026-07-13 发现的预告；`600110.SH|20260630` 财报替代预告。前者正式报告在本窗口内且作为新披露版本纳入。
- 结束原因：`with_new_earnings_movement_reports_generated`
- 当日日报：`artifacts/earnings_movement/2026-08-10.md`

## 本次已处理事件主键

- `688082.SH|20260630|财报|2026-08-08|盛美半导体设备（上海）股份有限公司2026年半年度报告`
- `002741.SZ|20260630|财报|2026-08-08|光华科技：2026年半年度报告`
- `688549.SH|20260630|财报|2026-08-08|中巨芯科技股份有限公司2026年半年度报告`
- `688256.SH|20260630|财报|2026-08-08|中科寒武纪科技股份有限公司2026年半年度报告`
- `605358.SH|20260630|财报|2026-08-08|杭州立昂微电子股份有限公司2026年半年度报告`

## 数值审计摘要

| ticker | calculation_audit_status | audit_release_status | audit_artifact | audit_blockers | unresolved_numeric_conflicts |
|---|---|---|---|---|---|
| 688082.SH | PASS | publishable | `audits/2026-08-10-688082-audit-result.json` | `[]` | `[]` |
| 002741.SZ | PARTIAL_PASS | blocked | `audits/2026-08-10-002741-market-cap-audit-result.json` | `[pre_event_consensus_sample_count_lt_3, consensus_age_470_days, official_disclosure_time_precision_day_only, pe_user_defined_requires_approved_expectation_gap_chain]` | `[valuation_date_share_count_468602310_vs_H1_share_count_465022310]` |
| 688549.SH | PARTIAL_PASS | blocked | `audits/2026-08-10-688549-market-cap-audit-result.json` | `[stale_pre_event_consensus_ages_280_to_651_days, consensus_dispersion_extreme, no_current_fy_institution_forecast, pe_user_defined_requires_approved_expectation_gap_chain]` | `[]` |
| 688256.SH | PASS | publishable | `audits/2026-08-10-688256-audit-result.json` | `[]` | `[]` |
| 605358.SH | PASS | publishable | `audits/2026-08-10-605358-audit-result.json` | `[]` | `[]` |

## 运行版本元数据

```json
{
  "captured_at_beijing": "2026-08-10T09:08:23+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "1f07968108801924b2345acc1ac3daf59feea40ae4497561e5f4efa342d96a35",
  "skill_revision": "git:734f55f3898a018cbc6f871df94fba38c7eb81fb",
  "skill_tree_status": "clean",
  "skills": [
    "a-share-disclosure-trading-data",
    "earnings-call-investment-analyst",
    "financial-evidence-audit"
  ],
  "status": "ok"
}
```
