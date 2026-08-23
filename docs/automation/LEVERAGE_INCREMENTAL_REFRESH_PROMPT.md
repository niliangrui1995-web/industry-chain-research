# 09-00-2 自动化提示词

运行版本：`prompt_contract_version=2026-07-27.1`；`two_rong_refresh_protocol_version=2026-08-23.2`。

先读取 `AGENTS.md`、`docs/automation/AUTOMATION_RUN_CONTRACT.md` 与 `docs/automation/LEVERAGE_INCREMENTAL_REFRESH_CONTRACT.md`，并按运行合同写入本轮简短元数据。已有历史数据一律直接复用：不扫描中间历史日期，不校验或重抓历史数据，不重建历史链。

数据源和水位线完全以 `LEVERAGE_INCREMENTAL_REFRESH_CONTRACT.md` 为准。唯一数据命令是：

```powershell
python scripts/refresh_leverage_dashboard_incremental.py --project-root "D:\vcp_hunter\产业链投研" --fund-root "D:\vcp_hunter\基金持仓" --execute
```

读取 JSON 结果：

- `no_changes`：记录“没有新增尾部缺口”后结束；不得构建、备份、推送或发布。
- `pending_dfcf_source`、`pending_market_cap_source` 或 `blocked`：记录新增尾部区间或原因后结束；不得回看历史、换源、`--bootstrap-full`、手工修复旧文件或全量重建。
- `updated`：只确认 JSON 返回的 `updated_dfcf_tail_gap_windows` 和 `updated_post2017_market_cap_tail_gap_windows` 已由本轮命令处理，以及 `append_leverage_dashboard_tail.py` 已追加这些新日期；不检查历史数据，也不调用 `build_leverage_dashboard_bundle.py`。然后自动备份并发布。

备份和发布只在 `updated` 时执行：

1. 只暂存本轮实际变化的两融文件，绝不使用 `git add .`，也不触碰开始前已有的其他改动。研究仓仅允许 `artifacts/leverage_capitulation/dfcf_daily/` 下四个已跟踪 CSV/审计文件；基金仓仅允许 `public/data/leverage-dashboard.json`、`public/data/leverage-dashboard.manifest.json`，以及站点构建自然更新的 `public/seo/quarter-release-check.json`、`public/sitemap.xml`。
2. 分别在两个仓库提交并推送当前分支；确认各自与 `origin/master` 没有待推送或待拉取提交。
3. 在基金仓运行既有站点构建并部署 `fund-stock-picker`；只确认线上两融 JSON 和 manifest 的 SHA-256 与本轮本地发布文件一致，不回查历史数据。
4. 仅在推送和线上 SHA-256 一致后，写入本轮发布成功状态；中文简报只列出新增日期区间、备份提交、部署地址与失败原因（如有）。
