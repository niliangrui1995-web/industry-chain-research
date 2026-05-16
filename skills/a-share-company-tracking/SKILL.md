---
name: a-share-company-tracking
description: Project-local A-share company tracking workflow for watchlist-driven daily updates, per-company baselines, official disclosures, CNINFO evening/T+1 announcement rescans, dragon-tiger list and block-trade checks, Grok/X observation fallback discipline, multi-agent batching, and durable company state files in the 产业链投研 project.
---

# A-Share Company Tracking

Use this skill for the `产业链投研` A 股公司持续跟踪 workflow. It turns the project watchlist into durable per-company research records and daily update reports.

This is a project-owned tracking workflow, not a generic market-news brief and not a replacement for the investment-research route. Always enter through `industry-research-router`, then use this skill when the task is watchlist maintenance, company daily tracking, baseline refresh, or run-status reconciliation.

## Inputs

- Watchlist: `watchlists/a_share_company_watchlist.xlsx`
- Company artifacts: `artifacts/company_tracking/<ticker>/`
- Daily report: `artifacts/company_tracking/YYYY-MM-DD.md`
- Run status: `artifacts/company_tracking/run_status.md`
- Automation prompt reference: `docs/company_tracking/A_SHARE_COMPANY_TRACKING_PROMPT.md`

Required watchlist columns:

`enabled`, `ticker`, `exchange`, `name`, `aliases`, `industry_tags`, `priority`, `baseline_status`, `grok_query_terms`, `tracking_focus`, `official_sources_hint`, `last_baseline_date`, `last_update_date`, `notes`

Only process rows where `enabled=Y`.

## Hard Gates

1. Read `AGENTS.md` and route through `skills/industry-research-router`.
2. Treat each enabled company as an isolated work unit. Do not merge many companies into one broad query before per-company checks are complete.
3. Use one dedicated worker/sub-agent per company whenever sub-agent tools are available. Maximum parallelism is 6 company workers.
4. If sub-agent tools are unavailable or workers time out, the controller may complete a documented fallback, but must write `multi_agent_status` and per-company fallback notes in `run_status.md`.
5. Grok/X is discovery only. If Chrome/Grok is unavailable, use open-web search as `open_web_fallback`; do not call that Grok or X-native evidence.
6. A/C evidence separation is mandatory: official disclosure and exchange data can update the formal state; Grok/X, social, forum, and model summaries stay in an observation pool unless independently verified.
7. Before finishing, reconcile the enabled watchlist against the completion table. No enabled company may be missing.

## 20:00 Announcement Hard Gate

For runs at or after 20:00 Beijing time, check both announcement dates:

- `T`: the Beijing calendar date of the run.
- `T+1`: the next announcement date, because evening CNINFO and exchange disclosures can be published after market close but carry the next calendar announcement date.

This is a hard gate for A-share company tracking. If the run starts before 20:00, check `T` and explicitly state whether a later evening/T+1 rescan is still needed.

For every enabled company, the controller or company worker must record the announcement-window result in the completion table:

`announcement_window_checked = T_only | T_and_T_plus_1 | pending_evening_rescan | failed_with_reason`

If a user flags a missed announcement, immediately perform a company-by-company CNINFO/name/ticker rescan for the affected window and update `events.jsonl`, `state.md`, the daily report, and `run_status.md`.

## Baseline Workflow

For every enabled company with `baseline_status` in `pending`, `refresh_needed`, or blank:

1. Build a company baseline:
   - listing entity and history;
   - business segments and revenue/profit structure;
   - products, technology route, customers, suppliers, and certification cycle where disclosed;
   - capacity, projects, financing, M&A, and major investments;
   - recent annual report, quarterly report, announcements, and IR records;
   - real beneficiary evidence versus market narrative;
   - major risks and false-positive concept-stock risks.
2. Separate three lenses:
   - fundamental quality;
   - earnings elasticity;
   - trading elasticity.
3. Create or update:
   - `baseline.md`
   - `state.md`
   - `events.jsonl`
4. Update the watchlist row:
   - `baseline_status=done`
   - `last_baseline_date=YYYY-MM-DD`
   - `last_update_date=YYYY-MM-DD`

## Daily Update Workflow

For every enabled company:

1. Read `baseline.md`, `state.md`, and recent `events.jsonl`.
2. Check official announcements, exchange disclosures, CNINFO, company IR, and the configured `official_sources_hint`.
3. Apply the 20:00 announcement hard gate.
4. Check dragon-tiger list and block-trade records for the most recent trading day when relevant.
5. Run Grok/X 24-hour discovery through logged-in Chrome when available, using the company's name, ticker, aliases, `grok_query_terms`, and `tracking_focus`.
6. If Grok/X is unavailable, run open-web fallback and label it as observation-only.
7. Append material events to `events.jsonl` with compact JSON lines:
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
8. Update `state.md` only for real changes, unresolved gaps, or next tracking questions.
9. Write the daily report and `run_status.md`.

## Output Requirements

The daily report must include:

- run metadata;
- companies with material changes, with what happened, why it matters, and evidence type;
- announcement / dragon-tiger / block-trade highlights;
- Grok/X or open-web observation pool only when it contains useful items;
- baseline changes and unresolved source gaps;
- next 3-5 tracking questions;
- per-company completion table.

The final chat summary should be short. Do not list every file path or every queue-status row unless it changes the user's next decision.

## Related Skills

- `industry-research-router`: required entrypoint.
- `a-share-disclosure-trading-data`: official announcements, CNINFO, dragon-tiger, and block-trade data discipline.
- `search-specialist`: source discovery and contradiction tracking.
- `research-summarizer`: long announcements, annual reports, quarterly reports, and IR records.
- `stock-evaluator`: project-style company evaluation after material events.
- `allstock-data` / `finance`: quote, K-line, liquidity, valuation, and timing context.
- `browser-grok-gemini-research`: Grok/X and Gemini webpage collection boundary.
