# 业绩异动新增股票含金量分析运行状态

- 状态：`completed_with_new`
- 北京时间运行起点：`2026-08-12T09:14:33+08:00`
- 北京时间状态扫描时点：`2026-08-12T09:17:23+08:00`
- `lookback_hours=24`
- 窗口开始：`2026-08-11T09:17:23+08:00`
- 窗口结束：`2026-08-12T09:17:23+08:00`
- 数据源：`D:\vcp_hunter\紫金研选\data\vcp_hunter.db` / `kv_store.key='earnings_state'`（只读 URI，`PRAGMA query_only=ON`，WAL 感知）
- `kv_store.updated_at`：`2026-08-12 00:30:50`（源字段无时区，未用于北京时间窗口计算）
- `earnings_state_sha256`：`fb4bde3774549c71de5079084da823129fbc8ce390ecd3c0d9f1eb8d8696f38f`
- `last_sync_date`：`2026-08-12`
- 状态源记录总数：58
- 窗口原始候选数：1
- ST 剔除后：1
- 按代码+报告期去重后：1
- 事件优先级淘汰数：0（财报 > 快报 > 预告）
- 历史同披露事件剔除数：0
- 最终新增股票数：1
- 最新发现时间：`2026-08-11T21:00:50`（源字段无时区，按任务上下文解释为北京时间）
- `time_filter_fallback=false`
- 事件日期核验说明：状态源写入 `announcement_date=2026-08-11`，官方巨潮正式半年报日期为 `2026-08-12`；日报和事件键均采用官方日期，具体披露时分秒 `N/A`。
- 结束原因：`with_new_earnings_movement_reports_generated`
- 当日日报：`artifacts/earnings_movement/2026-08-12.md`

## 本次已处理事件主键

- `301128.SZ|20260630|财报|2026-08-12|强瑞技术2026年半年度报告`

## 数值审计摘要

| ticker | calculation_audit_status | audit_release_status | audit_artifact | audit_blockers | unresolved_numeric_conflicts |
|---|---|---|---|---|---|
| 301128.SZ | PASS | publishable | `audits/2026-08-12-301128-audit-result.json` | `[]` | `[]` |

## 运行版本元数据

```json
{
  "captured_at_beijing": "2026-08-12T09:42:41+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "596e23f52108c4ac98a2e90c14b1bf38a9b3e021e0132aed0fce96eb9f9f1f5f",
  "skill_revision": "git:902fa8786034f705368f5dbc80b387dea98be53d",
  "skill_tree_status": "clean",
  "skills": [
    "a-share-disclosure-trading-data",
    "earnings-call-investment-analyst",
    "financial-evidence-audit",
    "ht-local-market-data"
  ],
  "status": "ok"
}
```
