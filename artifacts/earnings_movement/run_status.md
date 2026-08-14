# 业绩异动新增股票含金量分析运行状态

- 状态：`completed_with_new`
- 北京时间运行起点：`2026-08-14T09:02:41+08:00`
- 北京时间状态扫描时点：`2026-08-14T09:02:55+08:00`
- 北京时间运行完成时点：`2026-08-14T09:33:38+08:00`
- `lookback_hours=24`
- 窗口开始：`2026-08-13T09:02:55+08:00`
- 窗口结束：`2026-08-14T09:02:55+08:00`
- 执行日：周五；未触发周一 `lookback_hours=72` 的扩展窗口。
- 只读数据源：`D:\vcp_hunter\紫金研选\data\vcp_hunter.db` / `kv_store.key='earnings_state'`（SQLite `mode=ro`、`PRAGMA query_only=ON`、WAL 感知）。
- `kv_store.updated_at=2026-08-14 00:30:34`；`last_sync_date=2026-08-14`；`earnings_state_sha256=93e18fb787a16263be11dca2b12c8459ef7746e62a9453a5ba51f1d432b18786`。
- 状态源原始记录数：33；ST 剔除后：33；按代码+报告期去重后：32；窗口命中：3；历史同披露事件剔除：0；最终新增：3。
- 正式报告优先：`688041.SH` 的正式 H1 报告替代旧 H1 预告；宏和科技、海光信息此前仅处理预告，纳芯微不存在历史相同事件，均未被当作重复事件剔除。
- `time_filter_fallback=false`。
- 法定公告日核验：三项均为 `2026-08-14`；接口 `ADDDATE` 分别为 `2026-08-13T17:28:04+08:00`、`2026-08-13T18:43:23+08:00`、`2026-08-13T21:01:22+08:00`。接口时间作为可追溯时点，不作为交易所保证的首次公众可得时点。
- `announcement_window_checked=pending_evening_rescan`。
- 结束原因：`with_new_earnings_movement_reports_generated`。
- 未打开或修改紫金研选 UI/代码；未操作其他自动化；未执行 Git 提交或推送。
- 当日日报：`artifacts/earnings_movement/2026-08-14.md`。

## 本次已处理事件主键

- `603256.SH|20260630|财报|2026-08-14|宏和科技2026年半年度报告`
- `688041.SH|20260630|财报|2026-08-14|海光信息2026年半年度报告`
- `688052.SH|20260630|预告|2026-08-14|2026年半年度业绩预告的自愿性披露公告`

## 数值审计摘要

| ticker | calculation_audit_status | audit_release_status | audit_artifact | audit_blockers | unresolved_numeric_conflicts |
|---|---|---|---|---|---|
| 603256.SH | PASS | publishable | `audits/2026-08-14-603256-audit-result.json` | `[]` | `[]` |
| 688041.SH | PASS | publishable | `audits/2026-08-14-688041-audit-result.json` | `[]` | `[]` |
| 688052.SH | PASS | publishable | `audits/2026-08-14-688052-audit-result.json` | `[]` | `[]`（H1 预告约数与 H1-Q1 反推差 6.69 元，已解释为舍入） |

## 运行版本元数据

```json
{
  "captured_at_beijing": "2026-08-14T09:29:05+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "1f07968108801924b2345acc1ac3daf59feea40ae4497561e5f4efa342d96a35",
  "skill_revision": "git:cb911e6e89ba7df8a69f3c17c47aa04044943691",
  "skill_tree_status": "clean",
  "skills": [
    "a-share-disclosure-trading-data",
    "earnings-call-investment-analyst",
    "financial-evidence-audit"
  ],
  "status": "ok"
}
```
