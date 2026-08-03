# A 股业绩异动自动化运行状态

- 执行状态：completed/with_new
- 北京时间：2026-08-03T09:04:26+08:00（星期一）
- lookback_hours：72
- 窗口开始：2026-07-31T09:04:26+08:00
- 窗口结束：2026-08-03T09:04:26+08:00
- 数据源：D:\vcp_hunter\紫金研选\data\vcp_hunter.db 的 `kv_store.key='earnings_state'`
- 读取模式：SQLite `mode=ro`、`PRAGMA query_only=ON`、WAL-aware
- kv_store.updated_at：2026-08-02 16:00:14
- last_sync_date：2026-08-03
- earnings_state.value SHA256：54394ac9363ff3c71b5dca1333a8ac7015d11f35d138bc197e3bdf7a2a928344
- 原始记录数：59
- ST 剔除：0；ST 剔除后数量：59
- 代码+报告期去重后数量：58
- 72 小时窗口命中数量：1
- 历史同披露事件剔除数量：0
- 最终新增股票数量：1
- 新增股票：仕佳光子（688313.SH），20260630，财报
- 发现时间：2026-07-31T19:00:35+08:00
- 事件首次可得时间：2026-07-31T18:55:17+08:00；上交所法定公告日期：2026-08-01
- processed_event_key：`688313.SH|20260630|财报|2026-08-01|https://static.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-08-01/688313_20260801_DVHP.pdf`
- time_filter_fallback：false
- 去重结果：扫描既有日报后未发现相同 `processed_event_key`；同一股票、报告期、披露事件未重复处理
- 官方核验覆盖率：1/1
- announcement_window_checked：pending_evening_rescan
- 日报：D:\vcp_hunter\产业链投研\artifacts\earnings_movement\2026-08-03.md
- 结束原因：new_earnings_movement_analyzed
- 外部操作边界：未打开或修改紫金研选 UI/代码；未操作其他自动化；未提交或推送 Git。

## 公司准出状态

| ticker | calculation_audit_status | audit_release_status | audit_artifact | audit_blockers | unresolved_numeric_conflicts |
|---|---|---|---|---|---|
| 688313.SH | PASS | publishable | D:\vcp_hunter\产业链投研\artifacts\earnings_movement\audits\2026-08-03-688313-audit-result.json | [] | [] |

## 运行版本元数据

```json
{
  "captured_at_beijing": "2026-08-03T09:05:06+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "1f07968108801924b2345acc1ac3daf59feea40ae4497561e5f4efa342d96a35",
  "skill_revision": "git:432318b21e29b9d3c97515ce042a8b92a0bff3ff+dirty:1f0796810880",
  "skill_tree_status": "dirty",
  "skills": [
    "a-share-disclosure-trading-data",
    "earnings-call-investment-analyst",
    "financial-evidence-audit"
  ],
  "status": "ok"
}
```

- metadata_status：ok
