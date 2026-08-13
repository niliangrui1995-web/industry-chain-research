# 业绩异动新增股票含金量分析运行状态

- 状态：`completed_with_new`
- 北京时间运行起点：`2026-08-13T09:01:15+08:00`
- 北京时间状态扫描时点：`2026-08-13T09:06:14+08:00`
- `lookback_hours=24`
- 窗口开始：`2026-08-12T09:06:14+08:00`
- 窗口结束：`2026-08-13T09:06:14+08:00`
- 数据源：`D:\vcp_hunter\紫金研选\data\vcp_hunter.db` / `kv_store.key='earnings_state'`（只读 URI，`PRAGMA query_only=ON`，WAL 感知）
- `kv_store.updated_at`：`2026-08-13 00:55:36`（源字段无时区，未用于北京时间窗口计算）
- `earnings_state_sha256`：`1f88efaa369b832c9050d566414a9cb4252fe17bb2233a97a2d1cec574abe198`
- `last_sync_date`：`2026-08-13`
- 状态源记录总数：45
- 窗口原始候选数：1
- ST 剔除后：1
- 按代码+报告期去重后：1
- 事件优先级淘汰数：0（财报 > 快报 > 预告）
- 历史同披露事件剔除数：0
- 最终新增股票数：1
- 最新发现时间：`2026-08-12T19:01:23+08:00`
- `time_filter_fallback=false`
- 事件日期核验说明：状态源写入 `公告日期=2026-08-12`、`源公告日期=2026-08-13`；上交所正式半年报法定公告日为 `2026-08-13`，接口 `ADDDATE=2026-08-12T17:04:58+08:00`。日报与事件键采用官方法定公告日并保留接口时间。
- `announcement_window_checked=pending_evening_rescan`
- 结束原因：`with_new_earnings_movement_reports_generated`
- 当日日报：`artifacts/earnings_movement/2026-08-13.md`

## 本次已处理事件主键

- `603236.SH|20260630|财报|2026-08-13|移远通信2026年半年度报告`

## 数值审计摘要

| ticker | calculation_audit_status | audit_release_status | audit_artifact | audit_blockers | unresolved_numeric_conflicts |
|---|---|---|---|---|---|
| 603236.SH | PASS | publishable | `audits/2026-08-13-603236-audit-result.json` | `[]` | `[]` |

## 运行版本元数据

```json
{
  "captured_at_beijing": "2026-08-13T09:29:35+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "1f07968108801924b2345acc1ac3daf59feea40ae4497561e5f4efa342d96a35",
  "skill_revision": "git:dcd602685ddb9b8b0bb74610e7d782262105ddf9",
  "skill_tree_status": "clean",
  "skills": [
    "a-share-disclosure-trading-data",
    "earnings-call-investment-analyst",
    "financial-evidence-audit"
  ],
  "status": "ok"
}
```
