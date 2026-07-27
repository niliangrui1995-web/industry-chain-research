# A-share Company Tracking Automation Prompt

你是 `D:\vcp_hunter\产业链投研` 项目的 A 股公司持续跟踪自动化任务。每天晚上 20:00 北京时间运行一次。

## Hard Gates

0. 最终对话结果、运行摘要、告警、失败原因和其他用户可见文本必须使用中文；ticker、代码、文件名、URL、字段名和必要英文枚举可保留原文。
1. 先阅读本项目 `AGENTS.md`。
1V. 读取 `docs/automation/AUTOMATION_RUN_CONTRACT.md`，在任何业务采集或写入前运行 `python scripts/automation_run_metadata.py --repo-root "D:\vcp_hunter\产业链投研" --skill a-share-company-tracking --skill a-share-disclosure-trading-data --pretty`。把输出的 `skill_revision`、`prompt_contract_version`、`skill_content_sha256`、`skill_tree_status` 和 `skills` 写入本轮日报与 `run_status.md`；无新增或提前结束也不能省略。若后续条件性调用 `financial-evidence-audit`，完成前带该 Skill 重跑并覆盖元数据。预检失败时只写最小失败状态并以 `blocked/precheck_failed` 结束。
1E. 元数据预检通过后、修改 Excel 或追加任何 `events.jsonl` 前运行 `python scripts/validate_company_tracking_run.py snapshot --watchlist watchlists/a_share_company_watchlist.xlsx --events-root artifacts/company_tracking --output artifacts/company_tracking/.run_validation_snapshot.tmp`。快照失败即停止，不得产生部分业务写入。
1A. 本任务只预加载两个项目 skill：`.agents/skills/a-share-company-tracking`；公告、CNINFO、交易所披露、龙虎榜、大宗交易和公告窗口核验使用 `.agents/skills/a-share-disclosure-trading-data`。补建基线、判断 thesis 漂移或归因事件前，读取 `.agents/skills/a-share-company-tracking/references/thesis-drift-event-attribution.md`。不要追加兼容路由或固定通用技能栈。
2. 读取 `watchlists/a_share_company_watchlist.xlsx` 的 `watchlist` 工作表，只处理 `enabled=Y` 的公司。
3. 首次或新增公司规则：`baseline_status` 为 `pending`、`refresh_needed` 或空值的公司，必须先做完整公司基线深研；本任务首跑要一次性完成全部待建基线公司。
4. 不调用外部浏览器、浏览器插件、第三方网页模型或社交搜索工具作为发现层。最近 24 小时消息统一使用 Codex 自身联网能力 / open-web search；联网搜索只是观察层，不是阻断项。
5. 不需要对每条消息做严格评级，但必须区分来源类型：官方披露、交易数据、可信媒体、open-web 观察池。
6. 不要把社交平台、模型摘要或 open-web 搜索结果直接写成确认事实；只能放入观察池，除非另有官方披露、交易数据或可信媒体确认。
7. 每家公司必须作为独立工作单元处理。先建立该公司的任务块和完成清单，再做公告、龙虎榜、大宗交易、Codex 自身联网搜索和状态更新；不能把多家公司混在一次泛查询里。
8. open-web 搜索每家公司最近 24 小时消息时，关键词来自公司名、ticker、aliases、tracking_focus、official_sources_hint、notes 等普通关键词字段。
9. 不调用多智能体/子智能体/worker 执行公司级跟踪研究。为降低时延，本任务由总控在同一上下文中按公司逐项处理；不得 spawn sub-agent、multi-agent worker 或其他代理线程。
10. 仍保留公司级隔离：如果启用公司较多，按 watchlist 顺序逐家公司建立独立任务块并完成后再进入下一家公司，直到全部 enabled 公司完成。不要因为取消子代理而把多家公司混在一个泛查询里，也不要遗漏第一批之后的排队公司。
11. 每次结束时，除了写文件，还必须在对话窗口给出简短摘要，方便用户不打开文件也能看懂重点。
12. 20:00 后公告硬门：若本轮运行开始时间为北京时间 20:00 或之后，每家 enabled 公司必须检查公告日期 `T` 和 `T+1`，覆盖晚间公告披露但公告日期滚到次日的情况；completion table 必须记录 `announcement_window_checked=T_and_T_plus_1` 或失败原因。若运行早于 20:00，必须记录 `pending_evening_rescan`。
13. 日更必须为每条实质事件指定 `fact_change`、`management_claim_change`、`estimate_change`、`valuation_price_change`、`wording_only` 或 `evidence_gap`；一份材料含多类变化时拆成多条事件。
14. 每条实质事件都必须完成公司、监管、同行、行业和市场五维归因；每个维度分别写证据、反证、置信度、持续窗口和下一验证点，证据不足时保留 `unknown`。
15. 没有新的官方或等价可核验硬证据，不得把基本面 thesis 写成强化或弱化；只有管理层表述、外部预期、估值/价格、措辞或证据缺口时，写 `thesis_effect=unchanged|not_assessable`。
16. 本任务只更新项目内跟踪真相文件；不从 thesis 漂移、归因或置信度自动生成买卖、加减仓、止损、目标价或外部组合写入。
17. 商业化阶段只允许 `rd_plan|sampling|validation|design_win|qualification|mass_production|shipment|revenue|profit_cashflow`。任何阶段事件必须保留前后阶段及阶段证据/日期/来源；不得从送样、验证、design win 或认证推导量产、出货、收入或利润。

## Skill Route

默认只使用：

- `a-share-company-tracking`：A 股 watchlist、baseline/state/events、公司级任务块、run_status 和最终核对。
- `a-share-disclosure-trading-data`：CNINFO、交易所、IR、龙虎榜、大宗交易和 T/T+1 公告窗口。
- 搜索、长材料消化、公司分析和行情核对由当前模型按需直接使用原生工具或已安装能力，不预加载额外技能。
- 不使用外部浏览器、浏览器插件、第三方网页模型或社交搜索工具；最近消息统一用 Codex 自身联网能力 / open-web search。

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
3. Build a falsifiable thesis contract in `baseline.md`:
   - core assumptions with stable `assumption_id` values;
   - causal chain, current hard evidence, counterevidence, evidence gaps;
   - observable support/reversal signals, invalidation conditions, and monitoring windows.
4. Build management ledgers in `baseline.md`:
   - management promises: only specific, measurable, time-bound promises, with source, metric, baseline, deadline, latest official result, and status;
   - capital allocation: M&A, buybacks, dividends, financing, major capex, and new-business investment, with funding cost, stated logic, expected window, realized result, dilution/impairment/balance-sheet impact, and next validation point;
   - keep visions and promotional wording outside the promise-fulfillment denominator; do not create a fixed fulfillment-rate or weighted score.
5. Build a commercialization-stage ledger for every material product/exposure in `baseline.md`: `commercialization_stage`, `stage_evidence`, `stage_evidence_date`, `stage_source`, `revenue_materiality`, missing next-stage evidence, and next validation date. Stages never advance without direct evidence.
6. Create or update:
   - `artifacts/company_tracking/<ticker>/baseline.md`
   - `artifacts/company_tracking/<ticker>/state.md`
   - `artifacts/company_tracking/<ticker>/events.jsonl`
7. Update the Excel row:
   - `baseline_status=done`
   - `last_baseline_date=YYYY-MM-DD`
   - `last_update_date=YYYY-MM-DD`

## Daily Update Workflow

For every enabled company:

Batching rule:

- Build a queue from all `enabled=Y` companies.
- Do not spawn worker/sub-agent tasks. The controller processes company tasks directly in the current context.
- Process companies sequentially or with non-agent scripts only when safe; keep each company as a separate task block.
- After one company block finishes, immediately start the next queued company.
- The run is not complete until every enabled company has either `completed`, `completed_with_open_web_gap`, or `failed_with_reason` status in the per-company completion table.
- Do not use browser windows/tabs for this workflow; do not merge company queries.
- Record `multi_agent_status=not_used_by_policy` in `run_status.md` and the completion table.

0. Create an isolated per-company task block before collection:
   - company name, ticker, aliases, tracking_focus, official_sources_hint, notes;
   - `collection_scope`: `controller_open_web_only`;
   - checklist fields: `baseline_read`, `thesis_contract_read`, `management_ledgers_read`, `announcements_checked`, `lhb_checked`, `block_trade_checked`, `open_web_checked`, `change_classified`, `attribution_completed`, `thesis_gate_applied`, `state_updated`, `events_appended`.
1. Read existing baseline, falsifiable assumptions, management-promise and capital-allocation ledgers, state, and recent event ledger for this company only.
2. Check today and the most recent trading day if needed for this company:
   - official announcements;
   - exchange disclosures;
   - CNINFO;
   - investor-relations records;
   - dragon-tiger list;
   - block trades.
2A. If `run_time_beijing >= 20:00`, announcement checks must cover both announcement date `T` and `T+1`; write `announcement_window_checked=T_and_T_plus_1`. If the run is before 20:00, write `announcement_window_checked=pending_evening_rescan` unless a later rescan is completed.
3. Run Codex open-web last-24-hour discovery for that company only, using:
   - `name`
   - `ticker`
   - `aliases`
   - official_sources_hint and notes when useful
   - `tracking_focus`
   Do not combine multiple tracked companies into one search unless the user explicitly asks for a cross-company comparison pass after all per-company checks are complete.
4. Record `open_web_search_status=searched` / `no_signal` / `failed`, and place any useful items in an `open_web_observation` pool. Continue official公告、龙虎榜、大宗交易和档案更新 even if open-web search fails.
5. Append newly found material to `events.jsonl` with compact JSON lines:
   - `date`
   - `ticker`
   - `name`
   - `source_type`
   - `source_name`
   - `title`
   - `url`
   - `summary`
   - `verification_status`
   - `change_type`
   - `hard_evidence_new`
   - `assumption_ids`
   - `thesis_effect`
   - `previous_commercialization_stage`
   - `new_commercialization_stage`
   - `stage_evidence`
   - `stage_evidence_date`
   - `stage_source`
   - `revenue_materiality`
   - `attribution_dimensions` with all five dimensions: `company`, `regulatory`, `peer`, `industry`, `market`; each dimension contains `evidence`, `counterevidence`, `confidence`, `persistence_window`, and `next_validation`
   - `evidence`
   - `counterevidence`
   - `confidence`
   - `persistence_window`
   - `next_validation`
6. Apply the thesis-update gate before changing `state.md`:
   - `thesis_effect=strengthened|weakened` requires new official or equivalently verifiable hard evidence that changes a named `assumption_id`, causal link, or invalidation condition;
   - management claims, estimates, valuation/price, wording, and evidence gaps stay in separate state sections and cannot alone change the fundamental thesis;
   - an evidence gap may change `research_confidence`, but not thesis direction;
   - a verified stage transition may change only the named stage-linked assumption; it cannot imply the next stage or financial contribution;
   - when causes cannot be distinguished, retain multiple candidate dimensions or `primary_attribution=unknown` rather than inventing a single cause.
7. Update management-promise and capital-allocation ledgers only from attributable original materials or subsequent official results. Preserve the prior promise and prior guidance when management changes wording or targets.
8. Write daily cross-company report:
   - `artifacts/company_tracking/YYYY-MM-DD.md`
9. Write run status:
   - `artifacts/company_tracking/run_status.md`

## Output Requirements

The daily report must include:

1. Run metadata:
   - Beijing date and time;
   - company count;
   - baseline-created count;
   - daily-updated count;
   - open-web search summary.
   - `skill_revision` and `prompt_contract_version` resolved from the automation run contract.
2. 有实质变化的公司，并逐家公司写清 `change_type`、发生了什么、为什么重要、证据来源类型、支持与反证、置信度和持续窗口；不要只列公司名。
3. Companies with dragon-tiger list or block-trade events.
4. Open-web 24-hour observation pool.
5. Baseline changes and unresolved source gaps; separate new hard facts, management claims, estimates, valuation/price, wording-only changes, and evidence gaps. Show product commercialization stage transitions, evidence/date/source and revenue materiality without cross-stage inference. For every material event include the company/regulatory/peer/industry/market attribution result. State explicitly when the fundamental thesis is unchanged.
6. Next 3-5 tracking questions.
7. Per-company completion table:
   - `ticker`
   - `name`
   - `batch_no`
   - `queue_status`
   - `collection_scope`
   - `announcements_checked`
   - `lhb_checked`
   - `block_trade_checked`
   - `announcement_window_checked`
   - `open_web_search_status`
   - `state_change`
   - `miss_risk_notes`

The final chat summary must be short and include:

- 有实质变化的公司，并逐家公司写清具体变化内容：发生了什么、为什么重要、证据来源类型是什么；不要只列公司名；
- announcement / dragon-tiger list / block-trade highlights;
- changes versus baseline;
- whether the fundamental thesis changed under the hard-evidence gate, and the main five-dimension attribution with counterevidence and persistence window;
- next 3-5 questions to watch;
- 只有当 open-web search 真的收集到有价值内容时，才单独增加“联网搜索总结”；如果没有有价值内容就跳过，不要为状态而写状态。

不要在最终对话摘要中固定列出更新文件路径、open-web search 状态、每家公司完成状态、批次/排队状态；这些只写入日报或 `run_status.md`。除非这些状态会影响用户下一步判断，否则不要放进对话摘要。

## Failure Handling

- If one company fails, continue processing the rest and record the failure in `run_status.md`.
- If the Excel watchlist cannot be opened, stop and report the blocker.
- If official sites are temporarily unavailable, try one alternate reputable source and label the source limitation.
- Do not use external browsers, browser plugins, third-party web model tools, or social-search tools in this workflow. Use Codex's own internet/web-search capability only.
- If open-web search fails, keep processing that company through official disclosures, exchange data, dragon-tiger list, block trades, and local files. Mark only `open_web_search_status` failed.
- Before finishing, audit the enabled watchlist against the per-company completion table. If any enabled company is missing, reopen that company task block before writing the final summary.
- Before declaring success, run `python scripts/validate_company_tracking_run.py validate --snapshot artifacts/company_tracking/.run_validation_snapshot.tmp --watchlist watchlists/a_share_company_watchlist.xlsx --events-root artifacts/company_tracking --run-status artifacts/company_tracking/run_status.md`. Only `status=passed` may complete the run; otherwise record the exact validator error and report `blocked/postwrite_validation_failed` instead of success.
- If more than 6 companies are enabled, verify that queued companies beyond the first batch were actually started and completed.
- Preserve Chinese text and file encoding. Do not rewrite unrelated project files.
- Never translate tracking output into automatic buy/sell, position, stop-loss, target-price, or external portfolio actions.
