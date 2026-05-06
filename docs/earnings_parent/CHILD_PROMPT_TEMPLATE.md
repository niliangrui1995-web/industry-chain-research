# Earnings Call Deep-Dive Child Prompt Template

Use this template whenever the parent automation creates or updates a single-company child automation. Fill every bracketed value at runtime. If a credible value is unavailable, write `N/A` or `not_found`; do not delete header fields.

The child prompt body must be written in English. The only Chinese text should be the final-answer requirement and the exact final judgment labels that the child must use in its Chinese output.

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

CHILD TASK SKILL HARD GATE: At the start of this single-company child task, before collecting or analyzing anything, invoke and follow the skill earnings-call-investment-analyst. The project-local skill directory hint is D:\vcp_hunter\产业链投研\skills\earnings-call-investment-analyst, so use that project skill location when resolving the skill. This skill is invoked only by the child task at runtime, not by the parent scheduler. If the child task cannot invoke earnings-call-investment-analyst from that project-local skill location, stop immediately and report missing_skill: earnings-call-investment-analyst. Do not silently substitute industry-research-router, finance-news, stock-evaluator, generic web search, or your own framework for this child task. Do not claim skill invocation by merely reading SKILL.md as a plain file; normal skill resolution may read that SKILL.md.

## Scope

- Analyze only the company and ticker specified in the header. Do not turn this task into a sector overview or multi-company comparison.
- Invoke `earnings-call-investment-analyst` first. Only after that skill is successfully invoked may you collect materials, verify financials, analyze the call, and form an investment judgment.
- Collect and verify the company's IR materials, earnings release, financial statements, presentation, SEC or exchange filings, conference call webcast, audio/video replay, transcript, captions, and Q&A when available.

## Fundamental Baseline Hard Constraint

Before reading or analyzing the earnings release, conference call, transcript, or Q&A, first complete the earnings-call-investment-analyst Company Fundamental Baseline:

- one-paragraph business model
- business and product-line map
- competitive position by business
- AI exposure path by business
- quarter-sensitive KPIs
- earnings interpretation bridge

Base beat/miss assessment, guidance interpretation, Q&A reading, bottleneck analysis, and supply-chain impact on this baseline.

## Upstream Bottleneck Evidence Hard Constraint

In the earnings release, prepared remarks, and Q&A, actively search for upstream bottleneck evidence and label each relevant item with one mention status:

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
- If official transcript, audio replay, video replay, complete captions, or Q&A are not yet published or fully accessible, keep looking for complete call content that can support the investment judgment.
- Choose the retrieval path pragmatically: official pages, SEC or exchange pages, web search, reliable third-party transcript or audio providers, browser inspection, HTTP, page source, network requests, direct downloads, or project scripts are all allowed after the hard-gate skill invocation succeeds.
- StockAnalysis, Quartr, Motley Fool, Seeking Alpha, Benzinga, Alpha Spread, and EarningsCall.biz are optional search seeds, not a mandatory checklist.
- Reliable third-party full transcripts or third-party-hosted original call audio may be used as fallback evidence, but label them as `third_party_transcript` or `original_call_audio + third_party_hosted`; do not classify them as official sources.
- If both a reliable full transcript and original call audio are available, use the full transcript as the main working material. Use audio only to verify key wording, disputed passages, or transcript quality; do not run full-call ASR by default.
- The hard gate's ban on generic web search means generic search cannot substitute for skill invocation. Once the skill is invoked successfully, use any efficient and reliable retrieval route allowed by the skill's agent-first and source-quality-first principles.
- Scripts are optional helpers. Do not run a script merely because it exists. If a script is actually used, record `script_used`, `script_result`, `script_limitation`, `manual_fallback_path`, and `final_source_type`.
- Script failure, no result, 401/403, JavaScript-rendered pages, stale provider data, or parser misses are not valid stop reasons.

## Required Analysis

Verify and analyze:

- revenue, EPS, margins, orders, backlog, inventory, capital expenditure, guidance, and consensus expectations
- call and Q&A evidence on outlook, customer ordering intent, AI/data-center demand, pricing, inventory, lead times, capacity, upstream bottlenecks, and supply-chain impact
- whether the quarter was above expectations, in line, below expectations, or not sufficiently evidenced
- confidence level and the evidence tier supporting that confidence

## Final Output Requirement

Write the final answer in Chinese. Use one of these exact Chinese judgment labels where applicable: `超预期` / `符合` / `低于` / `证据不足`.

The final Chinese output must include:

- `company_original_status`
- `call_content_status`
- `final_source_type`
- `missing_materials`
- `provisional true/false`
- `confidence level`
