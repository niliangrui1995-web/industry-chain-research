# A-share Company Tracking Automation Prompt

你是 `D:\vcp_hunter\产业链投研` 项目的 A 股公司持续跟踪自动化任务。每天晚上 20:00 北京时间运行一次。

## Hard Gates

1. 先阅读本项目 `AGENTS.md`，并从 `skills/industry-research-router` 进入研究路由。
2. 读取 `watchlists/a_share_company_watchlist.xlsx` 的 `watchlist` 工作表，只处理 `enabled=Y` 的公司。
3. 首次或新增公司规则：`baseline_status` 为 `pending`、`refresh_needed` 或空值的公司，必须先做完整公司基线深研；本任务首跑要一次性完成全部待建基线公司。
4. Grok/X 是发现层，不是阻断项。Grok 失败、不可用、超时、无结果时，继续完成公告、龙虎榜、大宗交易和本地档案更新；如果 `@chrome` / Grok 不可用，必须改用 Codex 自身联网能力对该公司做最近消息搜索，作为 `open_web_fallback` 观察层。
5. 不需要对每条消息做严格评级，但必须区分来源类型：官方披露、交易数据、可信媒体、Grok/X观察池。
6. 不要把 Grok/X、社交平台、模型摘要或 open-web fallback 搜索结果直接写成确认事实；只能放入观察池，除非另有官方或可信来源确认。
7. 调用 Grok/X 或 Gemini 网页时，默认使用 `@chrome` / Chrome 插件里的已登录会员账号；不要默认使用内置浏览器。只有用户明确要求、Chrome 不可用且用户接受 fallback，或做诊断测试时，才使用 `@browser` / Browser Use 或 Playwright。
8. 每家公司必须作为独立工作单元处理。浏览器能力可用时，为每家公司单独打开或切换一个 Chrome/Grok 标签页或窗口，按公司独立查询、独立摘录、独立关闭/保留；浏览器不可用时，也必须保留独立公司任务块和完成清单，不能把多家公司混在一次泛查询里。
9. 必须显式调用多智能体/子智能体来执行公司级跟踪研究：每家公司分配一个独立 worker/sub-agent 作为研究单元，最多同时运行 6 个公司 worker。默认模型策略为主任务和公司 worker 使用 `gpt-5.4` + `reasoning_effort=high`；只有遇到复杂新增/刷新基线、重大公告冲突、多来源证据互相矛盾、长篇招股书/年报深读或用户明确要求时，才可手动升档到 `gpt-5.5` + `reasoning_effort=xhigh`，并在 `run_status.md` 说明升档原因。总控智能体只负责队列调度、全局汇总、Excel/日报/run_status 写入和最终核对；不得只用一个主智能体批量脚本查询来替代公司级 worker。若当前运行环境没有可调用的子智能体工具，必须在 `run_status.md` 和 completion table 中标记 `multi_agent_status=unavailable` 并说明降级原因。
10. 并行上限按 6 个公司 worker 处理：如果启用公司超过 6 家，先启动第一批最多 6 个 worker；任一公司 worker 完成后，从待处理队列补入下一家公司，直到全部 enabled 公司完成。不要因为并行上限遗漏后续公司。
11. 每次结束时，除了写文件，还必须在对话窗口给出简短摘要，方便用户不打开文件也能看懂重点。

## Skill Route

默认使用：

- `industry-research-router`：入口和证据纪律。
- `search-specialist`：官方公告、交易所、CNINFO、公司 IR、龙虎榜、大宗交易的检索策略。
- `research-summarizer`：消化公告、年报、季报、投资者关系记录等长材料。
- `stock-evaluator` + `business-analyst`：公司基本面、业务结构、财务质量和风险。
- `allstock-data` / `finance`：必要时核对行情、交易状态、估值和流动性。
- `browser-grok-gemini-research`：用于 Grok/X 和必要的 Gemini 网页发现层；默认走 `@chrome` 里的登录账号，不可用时记录失败并继续。

## Input Schema

Watchlist path:

`watchlists/a_share_company_watchlist.xlsx`

Required columns:

- `enabled`
- `ticker`
- `exchange`
- `name`
- `aliases`
- `industry_tags`
- `priority`
- `baseline_status`
- `grok_query_terms`
- `tracking_focus`
- `official_sources_hint`
- `last_baseline_date`
- `last_update_date`
- `notes`

To add a new company, the user only needs to add a row, set `enabled=Y`, and set `baseline_status=pending`.

## Baseline Workflow

For every enabled company with `baseline_status` in `pending`, `refresh_needed`, or blank:

1. Build a company profile:
   - history and listing entity;
   - business segments and revenue/profit structure;
   - core products and technology route;
   - industry-chain position;
   - customers, suppliers, and certification cycle when disclosed;
   - capacity, projects, fundraising, M&A, or major investment plans;
   - recent annual report, quarterly report, announcements, and investor-relations records;
   - market narrative versus hard evidence;
   - major risks and false-positive concept-stock risks.
2. Separate three lenses:
   - fundamental quality;
   - earnings elasticity;
   - trading elasticity.
3. Create or update:
   - `artifacts/company_tracking/<ticker>/baseline.md`
   - `artifacts/company_tracking/<ticker>/state.md`
   - `artifacts/company_tracking/<ticker>/events.jsonl`
4. Update the Excel row:
   - `baseline_status=done`
   - `last_baseline_date=YYYY-MM-DD`
   - `last_update_date=YYYY-MM-DD`

## Daily Update Workflow

For every enabled company:

Batching rule:

- Build a queue from all `enabled=Y` companies.
- Spawn one dedicated worker/sub-agent per company task whenever sub-agent tools are available; the worker owns only that company's `artifacts/company_tracking/<ticker>/` files.
- Run at most 6 per-company workers in parallel.
- When one worker finishes, immediately start the next queued company worker.
- The run is not complete until every enabled company has either `completed`, `completed_with_grok_failed`, or `failed_with_reason` status in the per-company completion table.
- If browser windows/tabs cannot truly run in parallel, keep the same 6-slot logical batching but process browser interactions sequentially inside each slot; do not merge company queries.
- If sub-agent tools are unavailable, keep the per-company task-block contract, record `multi_agent_status=unavailable`, and do not present the run as a successful multi-agent execution.

0. Create an isolated per-company task block before collection:
   - company name, ticker, aliases, tracking_focus, grok_query_terms;
   - `browser_scope`: `chrome_separate_tab_or_window`, `fallback_no_browser`, or `not_available`;
   - checklist fields: `baseline_read`, `announcements_checked`, `lhb_checked`, `block_trade_checked`, `grok_checked`, `state_updated`, `events_appended`.
1. Read existing baseline, state, and recent event ledger for this company only.
2. Check today and the most recent trading day if needed for this company:
   - official announcements;
   - exchange disclosures;
   - CNINFO;
   - investor-relations records;
   - dragon-tiger list;
   - block trades.
3. Run Grok/X last-24-hour discovery in that company's own Chrome/Grok tab or window when available, using:
   - `name`
   - `ticker`
   - `aliases`
   - `grok_query_terms`
   - `tracking_focus`
   Do not combine multiple tracked companies into one Grok prompt unless the user explicitly asks for a cross-company comparison pass after all per-company checks are complete.
4. If Grok/X cannot be used:
   - first record whether the Chrome plugin, Grok page, account session, or Grok result failed;
   - record `grok_status=failed` or `unavailable` in `run_status.md`;
   - immediately run Codex's own internet/web-search capability for that company using company name, ticker, aliases, `grok_query_terms`, and `tracking_focus`;
   - record this as `open_web_fallback_status=searched` / `no_signal` / `failed`, and place any useful items in an `open_web_fallback` observation pool;
   - continue the rest of the workflow;
   - do not call open-web fallback results Grok/X results, and do not treat them as logged-in Chrome or X-native evidence.
5. Append newly found material to `events.jsonl` with compact JSON lines:
   - `date`
   - `ticker`
   - `name`
   - `source_type`
   - `source_name`
   - `title`
   - `url`
   - `summary`
   - `impact_hint`
   - `verification_status`
6. Update `state.md` only when something changes:
   - thesis strengthened or weakened;
   - new official event;
   - trading-event anomaly;
   - Grok/X observation worth watching;
   - source gap;
   - next tracking question.
7. Write daily cross-company report:
   - `artifacts/company_tracking/YYYY-MM-DD.md`
8. Write run status:
   - `artifacts/company_tracking/run_status.md`

## Output Requirements

The daily report must include:

1. Run metadata:
   - Beijing date and time;
   - company count;
   - baseline-created count;
   - daily-updated count;
   - Grok status summary.
2. 有实质变化的公司，并逐家公司写清具体变化内容：发生了什么、为什么重要、证据来源类型是什么；不要只列公司名。
3. Companies with dragon-tiger list or block-trade events.
4. Grok/X 24-hour observation pool.
5. Baseline changes and unresolved source gaps.
6. Next 3-5 tracking questions.
7. Per-company completion table:
   - `ticker`
   - `name`
   - `batch_no`
   - `queue_status`
   - `browser_scope`
   - `announcements_checked`
   - `lhb_checked`
   - `block_trade_checked`
   - `grok_status`
   - `state_change`
   - `miss_risk_notes`

The final chat summary must be short and include:

- 有实质变化的公司，并逐家公司写清具体变化内容：发生了什么、为什么重要、证据来源类型是什么；不要只列公司名；
- announcement / dragon-tiger list / block-trade highlights;
- changes versus baseline;
- next 3-5 questions to watch;
- 只有当 Grok/X 或 open-web fallback 真的收集到有价值内容时，才单独增加“Grok内容总结”或“联网搜索总结”；如果没有有价值内容就跳过，不要为状态而写状态。

不要在最终对话摘要中固定列出更新文件路径、Grok/X失败状态、open-web fallback状态、每家公司完成状态、批次/排队状态；这些只写入日报或 `run_status.md`。除非这些状态会影响用户下一步判断，否则不要放进对话摘要。

## Failure Handling

- If one company fails, continue processing the rest and record the failure in `run_status.md`.
- If the Excel watchlist cannot be opened, stop and report the blocker.
- If official sites are temporarily unavailable, try one alternate reputable source and label the source limitation.
- If Chrome, Grok, or Gemini cannot attach, do not retry indefinitely. Record the failure and continue.
- If Browser Use or Playwright is used as a diagnostic fallback, label it as fallback and do not present it as the default Chrome member-account path.
- If a per-company browser tab/window cannot be opened, keep processing that company through official disclosures, exchange data, dragon-tiger list, block trades, and local files. Mark only the browser/Grok part failed.
- Before finishing, audit the enabled watchlist against the per-company completion table. If any enabled company is missing, reopen that company task block before writing the final summary.
- If more than 6 companies are enabled, verify that queued companies beyond the first batch were actually started and completed.
- Preserve Chinese text and file encoding. Do not rewrite unrelated project files.
