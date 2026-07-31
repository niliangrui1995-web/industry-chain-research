# Earnings Call Deep-Dive Child Prompt Template

Use this template whenever the parent automation creates or updates a single-company child automation. Fill every bracketed value at runtime. If a credible value is unavailable, write `N/A` or `not_found`; do not delete header fields.

Resuming a historical `PAUSED` child counts as an update: read this current repository template and fully re-render the prompt in the same update that restores `ACTIVE`. Never reuse the paused child's stored prompt body. If this template is missing, unreadable, or lacks `CHILD TASK SKILL HARD GATE`, do not resume the child.

The child automation configuration lives outside the prompt body. Every child created or updated from this template must use `model="gpt-5.6-terra"` and `reasoning_effort="xhigh"` (Codex UI: `5.6 terra` / `XHIGH`). Do not copy these configuration fields into the generated child prompt header.

The child prompt body must be written in English. The only Chinese text should be the final-answer requirement and the exact final judgment labels that the child must use in its Chinese output. Exception: the generated Chinese final output must render the downstream demand outlook section and upstream bottleneck evidence section in Chinese, while preserving the allowed `Mention Status` enum values exactly as written.

## Header

```text
TASK_KEY: [ticker]|[report_date]|[fiscal_period]
Automation parent: 22-30-2
Company: [company]
Ticker: [ticker]
Market: [market]
Sector: [sector]
Report date: [YYYY-MM-DD]
Fiscal period: [fiscal_period or N/A]
Planned child start Beijing: [YYYY-MM-DD HH:MM]
Schedule basis: [official_call_plus_3h / default_proxy_not_call_time]
Official call Beijing time: [YYYY-MM-DD HH:MM or not_found]
Original call time text: [original text or N/A]
Original timezone: [IANA/source timezone or N/A]
Call time source URL: [official URL or N/A]
Call time source type: [official_ir_event / official_ir_webcast / official_ir_press_release / sec_filing / exchange_announcement / third_party_unconfirmed / not_found]
Calendar source: [Company IR / JPX / TDnet / DART / KIND / MOPS / SEC EDGAR 6-K / confirmed / Yahoo Finance / Nasdaq / Alpha Vantage / not_found_in_current_calendar]
Event status: [confirmed / estimated / estimated_unverified / estimated_conflict / unknown]
Source confidence: [official_confirmed / official_disclosure / third_party_calendar_estimate / non_official_estimate / conflict_requires_official_verification / official_date_mismatch / unknown_current_event_missing]
Official source URL: [official URL or N/A]
Calendar caveat: [one-line caveat explaining official, estimate, conflict, skipped DART, or mismatch status]
```

## Prompt Body

OUTPUT LANGUAGE HARD GATE: Every user-visible final result, run summary, warning, failure reason, and conclusion must be written in Chinese. Keep only tickers, code, filenames, URLs, field names, exact labels, and required enums in their original form.

AUTOMATION RUN VERSION HARD GATE (`prompt_contract_version=2026-07-27.1`): Before any domain collection or business write, read `D:\vcp_hunter\产业链投研\docs\automation\AUTOMATION_RUN_CONTRACT.md` and run `python scripts/automation_run_metadata.py --repo-root "D:\vcp_hunter\产业链投研" --skill earnings-call-investment-analyst --skill financial-evidence-audit --pretty`. Persist `skill_revision`, `prompt_contract_version`, `skill_content_sha256`, `skill_tree_status`, and `skills` in this run's report or equivalent durable run status. If the precheck fails, write only the minimal failure status and stop as `blocked/precheck_failed`; do not continue collection or create partial business output.

CHILD TASK SKILL HARD GATE: At the start of this single-company child task, before collecting or analyzing anything, invoke and follow the skill earnings-call-investment-analyst. The standard project-local skill directory is D:\vcp_hunter\产业链投研\.agents\skills\earnings-call-investment-analyst. Project-local skill resolution is successful if that SKILL.md exists and you follow it as the task skill; absence from the global skill inventory alone is not missing_skill. This skill is invoked only by the child task at runtime, not by the parent scheduler. If the child task cannot invoke it from that project location, stop immediately and report missing_skill: earnings-call-investment-analyst. Do not silently substitute another skill or generic search for the skill invocation. Reading SKILL.md is valid only when its workflow is actually followed.

FINANCIAL EVIDENCE AUDIT HARD GATE: Before publishing any decision-critical number, comparison, beat/miss judgment, valuation, or derived financial conclusion, invoke and follow the project-local skill financial-evidence-audit at D:\vcp_hunter\产业链投研\.agents\skills\financial-evidence-audit. Build the required evidence package and run its deterministic audit rather than relying on mental arithmetic. A `FAIL`, `blocked`, unresolved conflict, missing required provenance, or missing skill blocks only the affected numerical conclusion and every downstream conclusion that depends on it; it cannot be bypassed by a provisional label. Report `missing_skill: financial-evidence-audit` when the skill is unavailable.

## Scope

- Analyze only the company and ticker specified in the header. Do not turn this task into a sector overview or multi-company comparison.
- Invoke `earnings-call-investment-analyst` first. Only after that skill is successfully invoked may you collect materials, verify financials, analyze the call, and form an investment judgment.
- Invoke `financial-evidence-audit` for every decision-critical calculation or source conflict before numerical release. Preserve the audit input and result paths in the final output.
- Collect and verify the company's IR materials, earnings release, financial statements, presentation, SEC or exchange filings, conference call, earnings webcast, results briefing, investor meeting, audio/video replay, transcript, captions, and Q&A when available.

## Fundamental Baseline Hard Constraint

Before reading or analyzing the earnings release, conference call, transcript, or Q&A, first complete the earnings-call-investment-analyst Company Fundamental Baseline:

- one-paragraph business model
- business and product-line map
- competitive position by business
- AI exposure path by business
- quarter-sensitive KPIs
- earnings interpretation bridge

Base beat/miss assessment, guidance interpretation, Q&A reading, bottleneck analysis, and supply-chain impact on this baseline.

## Downstream Demand Outlook Hard Constraint

In the earnings release, guidance, prepared remarks, and Q&A, actively extract downstream demand and customer-outlook evidence. Do not stop at financial metrics, supply-chain wording, or upstream bottleneck checks.

In the Chinese final output, write the full downstream demand outlook section in Chinese, including table headers, demand items, evidence notes, timeframe, demand quality, investment meaning, confidence narrative, and absence statements. Keep only the allowed `Mention Status` enum values in English.

Separate:

- End-market demand: AI data center, hyperscaler, enterprise, telecom, consumer, industrial, auto, or company-specific end markets.
- Customer ordering intent: bookings, backlog conversion, cancellations, long-term agreements, take-or-pay, design wins, qualification status, pull-forward, push-outs, or channel inventory.
- Guidance coverage: revenue already covered by backlog, contracts, qualified demand, permits, or contracted shipments versus revenue still dependent on future orders, approvals, qualifications, ramps, or macro recovery.
- Demand quality: durable ramp, pull-forward, inventory rebuild, price/mix effect, one-time shipment, cyclical recovery, or weak/uncertain demand.
- Management tone: stronger, weaker, unchanged, or ambiguous versus the resolved prior-quarter event.

Use this table when downstream demand outlook matters:

| Downstream Demand Item | Mention Status | Evidence Location | Management Wording | Timeframe | Demand Quality | Investment Meaning | Confidence |
|---|---|---|---|---|---|---|---|

Allowed `Mention Status` values:

- `demand_accelerating`
- `demand_stable`
- `demand_decelerating`
- `demand_uncertain`
- `customer_pull_forward`
- `inventory_digesting`
- `not_mentioned`
- `third_party_only`

If downstream demand or customer ordering intent is not discussed in the available materials, write `not_mentioned` or `evidence_absent`. Do not infer demand strength from industry headlines, stock moves, or supplier commentary unless clearly labeled as outside-call context.

## Upstream Bottleneck Evidence Hard Constraint

In the earnings release, prepared remarks, and Q&A, actively search for upstream bottleneck evidence and label each relevant item with one mention status:

In the Chinese final output, write the full upstream bottleneck evidence section in Chinese, including table headers, upstream items, evidence notes, bottleneck type, timeframe, investment meaning, confidence narrative, and absence statements. Keep only the allowed `Mention Status` enum values in English.

- `mentioned_current_bottleneck`
- `mentioned_future_risk`
- `mentioned_mitigated`
- `mentioned_not_bottleneck`
- `not_mentioned`
- `third_party_only`

If the company did not mention an alleged upstream bottleneck, write `not_mentioned` or `evidence_absent`. Do not infer bottlenecks from industry headlines, stock moves, or theme logic.

## Evidence and Source Rules

- Prefer company IR, official company files, SEC filings, exchange filings, and official IR-linked webcast/replay/transcript/captions for financial facts and management wording.
- Third-party financial calendars may only confirm event leads. Do not use them as final evidence for reported facts.
- If official transcript, audio replay, video replay, complete captions, Q&A, results-briefing material, or investor-meeting material is not yet published or fully accessible, keep looking for complete event content that can support the investment judgment.
- Choose the retrieval path pragmatically: official pages, SEC or exchange pages, web search, reliable third-party transcript or audio providers, browser inspection, HTTP, page source, network requests, direct downloads, or project scripts are all allowed after the hard-gate skill invocation succeeds.
- StockAnalysis, Quartr, Motley Fool, Seeking Alpha, Benzinga, Alpha Spread, and EarningsCall.biz are optional search seeds, not a mandatory checklist.
- Reliable third-party full transcripts or third-party-hosted original call/briefing audio may be used as fallback evidence, but label them as `third_party_transcript` or `original_call_audio + third_party_hosted`; do not classify them as official sources.
- If both a reliable full transcript and original call audio are available, use the full transcript as the main working material. Use audio only to verify key wording, disputed passages, or transcript quality; do not run full-call ASR by default.
- The hard gate's ban on generic web search means generic search cannot substitute for skill invocation. Once the skill is invoked successfully, use any efficient and reliable retrieval route allowed by the skill's agent-first and source-quality-first principles.
- Scripts are optional helpers. Do not run a script merely because it exists. If a script is actually used, record `script_used`, `script_result`, `script_limitation`, `manual_fallback_path`, and `final_source_type`.
- Script failure, no result, 401/403, JavaScript-rendered pages, stale provider data, or parser misses are not valid stop reasons.

## Required Analysis

Before retrieving prior-quarter financials or prior-quarter conference-call content, explicitly resolve which period "the immediately preceding quarter" means. If the header has a month-ended fiscal period such as `Mar/2026`, subtract three calendar months, e.g. `Mar/2026 -> Dec/2025`. If the header uses a fiscal-quarter label such as `FY2026 Q3`, verify the company's fiscal calendar from official filings or IR materials and resolve the prior fiscal quarter, e.g. `FY2026 Q3 -> FY2026 Q2`; if the current period is Q1, the prior quarter is the previous fiscal year's Q4. If `Fiscal period` is `N/A`, infer the current reporting period from the official earnings release, Form 10-Q/10-K, Form 8-K/6-K, exchange filing, or company IR event title. If the period still cannot be resolved, write `prior-quarter period unresolved`, avoid unsupported quarter-over-quarter or prior-call comparisons, and downgrade confidence.

Verify and analyze:

- revenue, EPS, margins, orders, backlog, inventory, capital expenditure, guidance, and consensus expectations
- quarter-over-quarter growth using prior-quarter actuals from the resolved prior-quarter official materials
- call, webcast, results-briefing, investor-meeting, and Q&A evidence on outlook, customer ordering intent, AI/data-center demand, pricing, inventory, lead times, capacity, upstream bottlenecks, and supply-chain impact
- changes versus the resolved prior-quarter conference call, earnings webcast, results briefing, or investor meeting, using prior-quarter transcript/replay/captions or reliable third-party full transcript when official event content is unavailable
- whether the quarter was above expectations, in line, below expectations, or not sufficiently evidenced
- whether forward guidance was above expectations, in line, below expectations, straddling, or not sufficiently evidenced; audit non-A-share reported actual and guidance comparisons with `expectation_surprise` using `subject_kind=reported_actual|company_guidance`
- confidence level and the evidence tier supporting that confidence

## Final Output Requirement

Write the final answer in Chinese. Use one of these exact Chinese judgment labels where applicable: `超预期` / `符合` / `低于` / `证据不足`.

The final Chinese output must include:

- `skill_revision`
- `prompt_contract_version`
- `company_original_status`
- `call_content_status`
- `final_source_type`
- `missing_materials`
- `provisional true/false`
- `confidence level`
- `calculation_audit_status`
- `audit_release_status`
- `audit_artifact`
- `audit_blockers`
- `unresolved_numeric_conflicts`
