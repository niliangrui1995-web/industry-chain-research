# A-share Company Tracking Automation

## Goal

Track a maintained list of A-share companies every trading day and keep a durable research record for each company. The automation should combine formal disclosures, trading-event data, and Grok/X 24-hour discovery without turning weak social signals into confirmed facts.

## Schedule

- Run daily at 20:00 Beijing time.
- Workspace: `D:\vcp_hunter\产业链投研`
- Watchlist: `watchlists/a_share_company_watchlist.xlsx`

## First Run

On the first run, process every enabled company in the watchlist whose `baseline_status` is `pending`, `refresh_needed`, or blank.

For each company, create or refresh:

- `artifacts/company_tracking/<ticker>/baseline.md`
- `artifacts/company_tracking/<ticker>/state.md`
- `artifacts/company_tracking/<ticker>/events.jsonl`

The baseline must cover:

- Company history and current business structure.
- Main products, customers, and industry-chain position.
- Recent annual report, quarterly report, announcements, investor-relations records, and major disclosed projects.
- Current market narrative, real beneficiary evidence, unresolved questions, and major risks.
- A concise tracking thesis that separates fundamental quality, earnings elasticity, and trading elasticity.

## Daily Update

For every enabled company:

1. Create an isolated per-company task block and completion checklist.
2. Read the company baseline, state file, and recent events.
3. Check same-day official announcements and exchange disclosures.
4. Check dragon-tiger list records.
5. Check block-trade records.
6. Use Grok/X through the logged-in Chrome plugin path to search the last 24 hours with company name, ticker, aliases, and configured query terms.
7. If `@chrome` / Grok is unavailable, use Codex's own internet/web-search capability to search recent company-related messages and store the result as an `open_web_fallback` observation layer.
8. Compare new material against the baseline and state.
9. Append new events to `events.jsonl`.
10. Update `state.md` only for real changes, unresolved questions, source gaps, and next tracking points.

Multi-agent requirement:

- This automation must explicitly call multi-agent/sub-agent workers for company-level tracking whenever sub-agent tools are available.
- Assign exactly one company to each worker. A worker may read shared project instructions and source data, but it may write only that company's `artifacts/company_tracking/<ticker>/state.md` and `events.jsonl`.
- The main/controller agent owns queue scheduling, worker prompts, Excel updates, daily report writing, `run_status.md`, and the final enabled-watchlist reconciliation.
- Do not replace the company-worker requirement with a single broad script pass. A broad data pull may support the controller, but each enabled company still needs its own worker task and completion row.
- If sub-agent tools are not exposed in a run, record `multi_agent_status: unavailable` with the exact blocker and continue only as a documented fallback.

Per-company isolation:

- Treat each enabled company as a separate work unit.
- Use a maximum parallelism of 6 company workers. If more than 6 companies are enabled, start the first batch of up to 6, then fill freed slots from the remaining queue until all enabled companies are complete.
- When Chrome/Grok browser control is available, open or switch to a separate Chrome/Grok tab or window for each company and run only that company's query terms there.
- Do not mix all companies into one broad Grok query before the per-company checks are complete.
- If a separate browser tab/window cannot be opened, continue the official disclosure, dragon-tiger list, block-trade, and local-file checks for that company; mark only the browser/Grok lane as failed.
- Before finishing, compare the enabled watchlist against the per-company completion table and reopen any missing company task block, including queued companies beyond the first batch.

## Grok Rule

Grok/X is non-blocking. If Grok is unavailable, times out, or returns no useful result:

- Continue the announcement, dragon-tiger list, and block-trade work.
- Record the failure in `run_status.md`.
- Mark the related company section as `grok_status: failed`, `unavailable`, or `no_signal`.
- Run Codex open-web fallback search for that company and record `open_web_fallback_status`.
- Do not label ordinary/open-web search as Grok/X, X-native search, or logged-in Chrome results.
- Treat open-web fallback items as observation-pool leads unless they are independently verified by official disclosure, exchange data, company IR, or reputable media.

Default browser path:

- Use `@chrome` / the Chrome plugin for Grok and Gemini because the user's paid/login sessions live there.
- Do not default to the in-app browser for Grok/Gemini.
- Use Browser Use or standalone Playwright only when explicitly requested, when Chrome is unavailable and the user accepts that fallback, or for a diagnostic check. Label any fallback clearly.

## Evidence Tiers

- A: official announcement, exchange filing, CNINFO, company IR, regulator or exchange source.
- B: reputable financial or industry media, named-source research note excerpt, market-data vendor page.
- C: Grok/X, social posts, unsourced model summary, forum chatter, or weak market rumor.

C-tier items can enter the observation pool but cannot override the company baseline or become a formal conclusion without stronger evidence.

## Required Outputs

At the end of every run, write:

- `artifacts/company_tracking/YYYY-MM-DD.md`
- `artifacts/company_tracking/run_status.md`
- Per-company `state.md` updates.
- Per-company `events.jsonl` entries when new events exist.
- A multi-agent execution note in `run_status.md` showing worker count, batch count, and any fallback reason.

Also provide a concise chat summary with:

- 有实质变化的公司，并逐家公司写清具体变化内容：发生了什么、为什么重要、证据来源类型是什么；不要只列公司名。
- Announcement, dragon-tiger list, and block-trade highlights.
- Changes versus baseline.
- Next 3-5 tracking questions.
- 只有当 Grok/X 或 open-web fallback 真的收集到有价值内容时，才单独增加“Grok内容总结”或“联网搜索总结”；如果没有有价值内容就跳过，不要为状态而写状态。

不要在最终对话摘要中固定列出更新文件路径、Grok/X失败状态、open-web fallback状态、每家公司完成状态、批次/排队状态；这些只写入日报或 `run_status.md`。除非这些状态会影响用户下一步判断，否则不要放进对话摘要。

## Maintenance

To add a company, append a row to `watchlists/a_share_company_watchlist.xlsx`, set `enabled=Y`, and set `baseline_status=pending`. The next run will build its baseline before normal daily updates.
