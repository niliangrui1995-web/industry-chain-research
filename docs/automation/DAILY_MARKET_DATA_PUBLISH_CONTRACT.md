# 工作日 09:00 两融、交易拥挤度与 AI 产业链拥挤度运行合同

`daily_market_data_publish_protocol_version=2026-08-30.1`

本合同是自动化 `09-00-2` 的唯一业务合同。它包含三条独立的数据链：DFCF 两融网页、C5 交易拥挤度、AI 产业链成交额占比。任务在北京时间每个工作日 09:00 运行；周末和休市日允许任一或全部链路返回 `no_changes`，不补造数据。

## 启动预检与数据边界

1. 先读取 `AGENTS.md`、`docs/automation/AUTOMATION_RUN_CONTRACT.md`、`docs/automation/LEVERAGE_INCREMENTAL_REFRESH_CONTRACT.md` 与本文件，再运行：

   ```powershell
   python scripts/automation_run_metadata.py --repo-root "D:\vcp_hunter\产业链投研" --skill a-share-leverage-capitulation-analyst --skill ht-local-market-data --pretty
   ```

   将运行元数据写入 `C:\Users\Administrator\.codex\automations\09-00-2\run_status.md` 和 `memory.md`；`run_status.md` 还必须记录 `leverage_status`、`concentration_status`、`ai_chain_membership`、`ai_chain_action`、`changed_components`、`release_status` 及失败原因。预检失败只能写最小失败状态并以 `blocked/precheck_failed` 结束。
2. 每轮建立三张数据卡：
   - 两融余额与市值尾部：DFCF `RPTA_WEB_RZRQ_LSSH` / 合同限定的 `RPT_VALUEMARKET`，`vendor_snapshot`，无回退；
   - C5：本地 `D:\HT\vipdoc\sh\lday\sh880008.day` 分母及项目既有 C5 口径，`market_data_vendor`；
   - AI 产业链：`watchlists/AI产业链.xlsx` 的代码列与相同 TDX 日线，分母仍为 `sh880008.day.amount`，`derived_metric`。
3. `D:\HT` 只读，不复制原始 `.day` 文件；不得读取账户、订单、密码或日志。DFCF 不得改用交易所、iFinD、同花顺或 TDX；两融历史不得全量重建。
4. 两仓开始时用 `scripts/automation_worktree_guard.py snapshot` 将完整 Git 状态写到任务目录外的快照文件。开始前已存在的非发布路径改动与未跟踪文件一律保留、不纳入暂存，也不阻止本轮；但若任一将要发布的白名单产物已在开始前脏，则阻断对应链路，防止把旧改动混入本轮提交。唯一受控输入例外是 `watchlists/AI产业链.xlsx`：仅当本轮确认其成分集合变化时，才可作为本轮白名单的一部分。

## 链路 A：DFCF 两融网页尾部

唯一入口：

```powershell
python scripts/refresh_leverage_dashboard_incremental.py --project-root "D:\vcp_hunter\产业链投研" --fund-root "D:\vcp_hunter\基金持仓" --execute
```

按 `LEVERAGE_INCREMENTAL_REFRESH_CONTRACT.md` 处理其 JSON：

- `updated`：只确认返回的新增尾部窗口和 `append_leverage_dashboard_tail.py` 已追加日期；不得调用 `build_leverage_dashboard_bundle.py`；
- `no_changes`：本链路无新增；
- `pending_dfcf_source` 或 `pending_market_cap_source`：本链路等待来源，不得换源、回看、补抓或使用 `--bootstrap-full`；
- `blocked` 或非零退出：记录硬失败，不得把本链路产物纳入发布。

## 链路 B：C5 与 AI 产业链交易拥挤度

唯一入口：

```powershell
& .\.venv_earnings_asr\Scripts\python.exe .\trading_concentration\refresh_tdx_trading_concentration_daily.py --project-root "D:\vcp_hunter\产业链投研" --publish-dir "D:\vcp_hunter\基金持仓\public\data"
```

该入口必须输出单行 JSON，并先比较当前工作簿与上一个成功发布日包内记录的 **成分集合**（不比较行顺序）：

- `membership=unchanged`：只运行严格晚于 C5 水位的尾部追加；C5 与 AI 子序列同步追加，历史记录不回扫；
- `membership=changed` 或旧包缺少集合指纹：先按当前工作簿从 `2025-01-01` 起完整重算 **仅** `ai_chain_series`，再追加 C5 水位之后的尾部；`records` 和 `trading-concentration-daily.csv` 必须字节不变；
- `membership=unchanged` 且本地分母没有更晚日期：返回 `no_changes`；
- 成分重建已完成但没有新的 C5 尾部日期时：返回 `ai_chain_rebuilt`，这仍是需要验证、备份和发布的有效变更；
- `blocked`、非零退出、C5 records/CSV 改写、研究仓与基金仓 JSON/manifest 字节不一致、工作簿或 TDX 快照在计算期间变化：记录 `blocked/concentration_refresh_failed`，不得纳入发布。

AI 全量重算只因成分集合变化触发；工作簿行重排、格式调整或同一成分的排列变化不得触发。分母始终为 `sh880008.day.amount`，C5 的分子、历史 records、CSV 和 C5 水位均不得因 AI 重算而改变。

读取尾部水位时，`append_checkpoint` 缺失或值为 `null` 都必须回退到 `data_range.end`；不得把 `null` 当作可处理的日期。

## 合并、验证、备份与发布

1. 三条链相互独立：`no_changes` 或 `pending_*` 只表示该链路未更新，不能阻止另一条通过验证的链路更新。若至少一条链路为 `updated` 或 AI 链路为 `ai_chain_rebuilt`，且其他硬失败链路没有留下待发布的已跟踪产物，则允许发布成功链路，最终状态标为 `published_success` 或 `partial_success`。硬失败绝不可被静默忽略。
2. 任何要发布的两融产物先运行基金仓 `npm run verify:leverage`；任何要发布的 C5/AI 产物先运行 `npm run verify:concentration`。两个仓库的同名交易拥挤度 JSON/manifest 必须逐字节一致。
3. 在基金仓执行 `npm run build`；确认 `dist/data` 与 `public/data` 中本轮要发布的 JSON/manifest 字节一致。构建失败不得提交、推送或部署。
4. 只暂存本轮实际变更的白名单路径，绝不使用 `git add .`：
   - 研究仓：`artifacts/leverage_capitulation/dfcf_daily/` 下四个已跟踪产物、`trading_concentration/data/trading-concentration-daily.csv`、`trading-concentration-dashboard.json`、`trading-concentration-dashboard.manifest.json`；仅在 `membership=changed` 时，允许暂存与运行快照 SHA-256 一致的 `watchlists/AI产业链.xlsx`；
   - 基金仓：`public/data/leverage-dashboard.json`、`public/data/leverage-dashboard.manifest.json`、`public/data/trading-concentration-dashboard.json`、`public/data/trading-concentration-dashboard.manifest.json`、以及构建自然更新的 `public/seo/quarter-release-check.json`、`public/sitemap.xml`。
5. 暂存前以同一快照运行 `automation_worktree_guard.py verify`，只允许本轮白名单路径变化；暂存后运行 `git diff --cached --check`，分别提交并推送当前分支；两仓都必须证明 `HEAD...origin/master = 0 0`。不触碰开始前已有的非白名单改动。
6. 以基金仓最终提交的完整 SHA 部署：

   ```powershell
   npx --no-install wrangler pages deploy dist --project-name fund-stock-picker --branch master --commit-hash <fund_commit_sha> --commit-dirty=false
   ```

   对预览地址和 `https://fund.niliangrui.cloud` 中本轮发布的两融、交易拥挤度 JSON 与 manifest 都执行 HTTP 200 + `Accept-Encoding: identity` 原始字节 SHA-256 对比；部署命令成功或 `npm run verify-live-release` 成功本身不足以准出。
7. 最终中文简报和持久化状态必须列出三链路状态、新增日期范围、AI `membership` / `ai_chain_action`、是否 AI-only 全量重算、备份提交、部署地址、线上 SHA 验证和失败原因。不得给出投资建议。
