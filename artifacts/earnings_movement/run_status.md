# A 股业绩异动自动化运行状态

- 执行状态：completed/with_new
- 北京时间：2026-07-30T09:15:32+08:00
- lookback_hours：24
- 窗口开始：2026-07-29T09:00:41+08:00
- 窗口结束：2026-07-30T09:00:41+08:00
- 数据源：D:\vcp_hunter\紫金研选\data\vcp_hunter.db
- 读取模式：SQLite mode=ro、PRAGMA query_only=ON、WAL-aware
- kv_store.updated_at：2026-07-29 16:00:55
- last_sync_date：2026-07-30
- 数据库主文件 SHA256：401da95b4c0026c393aee2959b4ce0995831bbf1d460d77fc9b55733734ca78a
- 原始记录数：59
- ST 剔除后数量：59
- 去重后数量：59
- 24 小时窗口命中数量：1
- 最终新增股票数量：1
- 新增股票：宏发股份（600885.SH），20260630，财报
- 发现时间：2026-07-29T19:00:36+08:00
- 事件首次可得时间：2026-07-29T17:29:42+08:00
- time_filter_fallback：false
- 去重结果：历史日报无 600885；同一股票、报告期、披露事件未重复处理
- 官方核验覆盖率：1/1
- announcement_window_checked：pending_evening_rescan
- 日报：D:\vcp_hunter\产业链投研\artifacts\earnings_movement\2026-07-30.md
- 结束原因：new_earnings_movement_analyzed

## 公司准出状态

| ticker | calculation_audit_status | audit_release_status | audit_artifact | audit_blockers | unresolved_numeric_conflicts |
|---|---|---|---|---|---|
| 600885.SH | PASS | publishable | D:\vcp_hunter\产业链投研\artifacts\earnings_movement\audits\2026-07-30-600885-audit-result.json | [] | [] |

## 运行版本元数据

```json
{
  "captured_at_beijing": "2026-07-30T09:15:32+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "1f07968108801924b2345acc1ac3daf59feea40ae4497561e5f4efa342d96a35",
  "skill_revision": "git:66a329d92b5e2300c28e0579cf720cfd9d86a61f",
  "skill_tree_status": "clean",
  "skills": [
    "a-share-disclosure-trading-data",
    "earnings-call-investment-analyst",
    "financial-evidence-audit"
  ],
  "status": "ok"
}
```

- metadata_status：ok
