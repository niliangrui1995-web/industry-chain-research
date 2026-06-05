---
name: earnings-call-investment-analyst
description: Use this skill to analyze public-company earnings releases, financial results, management guidance, and earnings-call transcripts or replays. It is optimized for investment research, beat-or-miss analysis, expectation-gap judgment, guidance quality, conference-call extraction, upstream supply-chain bottleneck extraction, original-source collection, audio replay transcription, and post-earnings stock-reaction assessment.
---

# Earnings Call Investment Analyst

## Purpose

Use this skill to turn earnings releases, financial statements, guidance, and conference-call content into an investment-grade analysis.

Terminology: in this skill, "call content" includes a U.S.-style earnings call, earnings webcast, results briefing, investor meeting, corporate briefing, management Q&A, official captions, replay audio, or replay video. For Japan, Taiwan, Korea, Hong Kong, and Europe, do not assume the company holds a U.S.-style quarterly conference call; use the closest official IR event and label the source type precisely.

Answer four questions first:

1. Did the company beat, meet, or miss expectations?
2. What changed versus prior guidance, consensus, and our previous forecast?
3. What did management say that changes the next one to four quarters?
4. What should be tracked after the print for stock reaction, thesis validation, and risk control?

Before answering those questions, build a concise company baseline so the earnings analysis is anchored in what the company actually does.

## Source Priority

Base the analysis on company-hosted original materials whenever possible. Treat the company investor-relations site, company-hosted earnings release, company-hosted webcast replay, company-hosted presentation, and official regulatory filings as the primary evidence layer. Third-party transcripts, media summaries, and analyst notes are useful only after the original company evidence has been checked.

Prefer primary and time-stamped sources:

1. Official earnings release, shareholder letter, investor presentation, Form 8-K, Form 6-K, Form 10-Q, Form 10-K, Form 20-F, or exchange filing.
2. Official conference-call transcript, audio replay, video replay, webcast event page, or company-hosted replay file.
3. Reliable transcript providers when no official transcript is available.
4. Consensus estimates and market data from reliable financial-data sources.
5. Reputable financial media and analyst commentary as supporting context only.

For current facts, verify live. Do not rely on memory for earnings dates, guidance, consensus, stock price, market cap, or post-earnings price action.

If sources conflict, use this hierarchy:

1. Official company original material or regulatory filing for reported results, guidance, and management wording.
2. Official company webcast/audio/video replay for call content when no official transcript exists.
3. Third-party transcript only as a convenience layer, with key quotes or numbers checked against official materials when possible.
4. Analyst consensus and market data only for expectation comparison, not for reported company facts.

State the source gap clearly if the company has not posted the original earnings material, replay, or transcript.

When a company-linked event platform exposes only live/DVR caption playlists, check whether the playlist has `EXT-X-ENDLIST`. If it does not, treat the captions as a partial sliding-window capture, not a complete official transcript.

If official IR, the company-hosted event page, or the official event platform does not expose a complete transcript, audio replay, or video replay, keep looking for complete call content through any efficient and defensible route. Reputable transcript or audio providers, search results, browser inspection, page source, network requests, HTTP probes, direct downloads, and event-platform payloads are all valid routes when they fit the source problem. Provider names such as StockAnalysis, Quartr, Motley Fool, Seeking Alpha, Benzinga, Alpha Spread, and EarningsCall.biz are examples and search seeds, not a mandatory checklist. The hard requirement is to label final source quality, call-content completeness, source gaps, and confidence. If a script cannot fetch, parse, or download the relevant material, continue through another route and record the script limitation only if the script was actually used. If a reputable third-party full transcript and original call audio are both available, use the full transcript as the primary working source and use the audio only for targeted verification of decision-useful wording, disputed passages, and transcript quality issues. Do not run full-audio ASR by default in that case. If a complete recording is found on a transcript/audio aggregator, treat the content as original call audio but label the hosting as third-party hosted. Cross-check decision-useful claims against the official release, SEC or exchange filing, and company-linked event page.

## Bundled Resources

Use bundled resources only when they clearly help the specific task. Do not run a script merely because it exists.

- Read `references/source-workflow.md` when the task needs original-source collection, replay extraction, transcript evidence packs, or audio-first call analysis.
- Prefer agent-led source discovery: choose the fastest reliable path for the source problem, then preserve enough evidence for another analyst to understand source quality and gaps.
- Optionally use `scripts/source_discovery.py` to create a repeatable official-source inventory after or during manual discovery. If automation input includes exact report date, call date, call URL, or fiscal period not accepted by the script, carry those fields manually into notes or the evidence pack.
- Optionally use `scripts/webcast_asset_fetcher.py` as a first-pass webcast asset probe. If it finds only shell pages, adapter JSON, static scripts, 401/403 errors, or no recording, continue with manual web/browser/network inspection.
- Optionally use `scripts/caption_playlist_fetcher.py` to download and merge official HLS caption playlists such as Q4 `subtitles.m3u8` when the webcast exposes captions but not a plain transcript.
- Use fallback transcript/audio providers directly when needed. Treat provider lists as examples and search seeds; do not require every named provider to be checked when the agent already has complete, reliable call content.
- Use `scripts/audio_transcriber.py --check-deps` before audio-first work, then use `scripts/audio_transcriber.py` only when no reputable full transcript is available, when the user explicitly asks for audio-first analysis, or when transcript/audio spot checks reveal a material transcript-quality problem. Prefer the project ASR venv plus `--provider faster-whisper --device auto --compute-type auto`; use `--no-ffmpeg` only when PyAV can read the source media directly. Use OpenAI transcription only when the API package and `OPENAI_API_KEY` are configured.
- Use `scripts/setup_asr_env.ps1` on Windows to create a local Python ASR environment from `requirements-asr.txt` when faster-whisper or OpenAI transcription packages are missing.
- Use `scripts/earnings_pack_builder.py` to merge source inventory, webcast assets, transcript output, and optional actuals/guidance/consensus JSON into a standard evidence pack when enough structured inputs exist. If the final source is a third-party transcript found manually, still record the provider, URL, source type, retrieval time, and official-source gap in final notes or `evidence_pack.json`.
- Read `references/evidence-schema.md` when building, validating, or extending the evidence pack format.

## Agent-First Collection Rule

Start from the live source problem, not from the scripts. The agent should actively search, inspect, open, compare, and download sources. Scripts are accelerators for repeatable inventory, caption merging, transcription, and evidence packaging. They are never a reason to stop.

When a script is used, record:

| Field | Meaning |
|---|---|
| `script_used` | Script name and command purpose |
| `script_result` | `found`, `partial`, `none`, `failed`, or `blocked` |
| `script_limitation` | Missing parameter, 401/403, JS-only page, no recording, stale provider, parser miss, or other issue |
| `manual_fallback_path` | Search/browser/HTTP/network/direct-download path used after the script |
| `final_source_type` | `company_original`, `regulatory_filing`, `official_event_platform`, `third_party_transcript`, `original_call_audio`, or other schema value |

If only third-party transcript/audio is available after reasonable original-source collection, mark the analysis as provisional, explain the missing official materials, and include a concrete official replay/transcript recheck time when timing matters.

## Core Workflow

### 0. Build The Company Fundamental Baseline

Before collecting or analyzing the earnings release, call, and Q&A, build a concise company baseline in three layers. Do not skip this step; it defines what matters in the quarter.

First, write a one-paragraph business model answer:

- What the company sells.
- Who buys it.
- Why customers need it.
- How the company makes money: unit volume, ASP, mix, utilization, yield, service/software attach, financing, or one-time items.

Second, build a business map table:

| Business / Product Line | Segment Role | What It Sells | Value-Chain Position | Customers / End Market | Competitive Position | AI Exposure Path | Quarter-Sensitive KPIs |
|---|---|---|---|---|---|---|---|

Fill the table with evidence-based labels:

- `Segment Role`: core growth engine, margin engine, cash-cow, cyclical drag, turnaround, early option, or discontinued/immaterial.
- `Value-Chain Position`: upstream material, component, device, module, system, equipment, software/service, distributor/channel, or end customer.
- `Competitive Position`: global leader, regional leader, niche leader, qualified challenger, price taker, commodity supplier, or unclear. Support this with share, customer wins, technology generation, capacity, margin, or management claims; do not use vague praise.
- `AI Exposure Path`: direct AI infrastructure, indirect AI infrastructure, AI-adjacent, non-AI cyclical, or no meaningful AI exposure. Explain the path from product to AI capex; do not label a business "AI" only because the company uses AI language.
- `Quarter-Sensitive KPIs`: the specific metrics that should move this business in the earnings release or call, such as units, ASP, backlog, bookings, utilization, yield, gross margin, lead time, inventory, capex, customer qualification, design wins, or regulatory approvals.

Third, create an earnings interpretation bridge before reading the quarter:

- Which businesses should drive current-quarter revenue, gross margin, operating leverage, cash flow, and guidance?
- Which businesses are legacy drags, cyclical noise, or non-core and should not dominate the thesis?
- Which customer, order, capacity, pricing, inventory, and upstream-input terms must be searched in the call and Q&A?
- What would make the print high quality versus low quality for this specific company?
- Which claims require caution because they depend on one customer, unqualified capacity, future ramps, regulatory approvals, or undisclosed end users?

Use official filings, company IR, investor presentations, and recent earnings materials first. If the baseline cannot be built from reliable sources, label the source gap and keep later conclusions provisional.

Do not analyze beat/miss, guidance, Q&A, or upstream bottlenecks before this baseline is clear enough to interpret which business lines and bottleneck terms matter.

### 1. Define The Earnings Setup

Identify:

- Company name and ticker.
- Reporting quarter and fiscal or calendar period.
- Earnings release date and call date.
- Prior company guidance.
- Street consensus for revenue, EPS, margin, and next-quarter guidance.
- The user's prior forecast if available.
- Key thesis variables going into the print.
- The immediately preceding quarter's official earnings release, financial supplement, investor presentation, and regulatory filing URL. Find these through live web/IR/SEC or exchange search; do not rely on memory or the current-quarter release alone for prior-quarter actuals.
- The immediately preceding quarter's conference-call, earnings-webcast, results-briefing, or investor-meeting source: official transcript, audio/video replay, webcast page, captions, or reliable third-party full transcript when official event content is unavailable. Find it through live web/IR/event-platform/transcript-provider search and record URL, source type, completeness, and retrieval time.

For a pre-earnings preview, separate:

- Company guidance.
- Sell-side consensus.
- Buy-side whisper or implied expectation.
- Our own forecast.

For a post-earnings review, separate:

- Actual results.
- Prior-quarter actuals from the immediately preceding quarter's official materials.
- New guidance.
- Conference-call incremental information.
- Conference-call changes versus the immediately preceding quarter's prepared remarks and Q&A.
- Stock reaction.

### 1A. Resolve The Prior-Quarter Identity

Before retrieving prior-quarter financials or call content, explicitly determine and write the prior-quarter period you are searching for. Do not leave "prior quarter" as an implicit phrase.

Use these rules:

- If the task header provides a month-ended fiscal period such as `Mar/2026`, `Jun/2026`, `Sep/2026`, or `Dec/2026`, treat it as the current quarter-end month and subtract three calendar months. Example: `Mar/2026 -> Dec/2025`; `Jun/2026 -> Mar/2026`; `Sep/2026 -> Jun/2026`; `Dec/2026 -> Sep/2026`.
- If the task header provides `FY2026 Q3`, `Fiscal 2026 third quarter`, or another quarter label without a month-end date, use the company's official filing or IR material to identify the quarter-end date and then resolve the immediately preceding fiscal quarter. Example: `FY2026 Q3 -> FY2026 Q2` only after checking the company's fiscal calendar.
- If the current period is `Q1`, the prior quarter is the previous fiscal year's `Q4`; verify the fiscal year rollover from official filings or IR materials.
- If `Fiscal period` is `N/A`, infer the current reporting period from the official earnings release, Form 10-Q/10-K, Form 8-K/6-K, exchange filing, or company IR event title before searching prior-quarter sources.
- If the current period cannot be resolved from official material, write `prior-quarter period unresolved`, search using ticker/company plus report date and "previous quarter earnings call" as a fallback, and downgrade confidence for prior-quarter comparisons.

Record this compactly before the results table:

| Current Period Evidence | Resolved Current Period | Resolved Prior Quarter | Resolution Source | Confidence |
|---|---|---|---|---|

### 2. Extract Core Financial Results

Before filling the results table, independently retrieve the immediately preceding quarter's official earnings materials through live web/IR/SEC or exchange search. Use the prior-quarter official release, financial supplement, investor presentation, Form 10-Q/10-K, Form 8-K/6-K, or exchange filing as the source for prior-quarter actuals. If the current-quarter release repeats prior-quarter numbers, still verify them against the prior-quarter source when feasible. Record the prior-quarter period, source URL, source type, and retrieval time in the notes.

Use a compact comparison table that explicitly includes quarter-over-quarter growth rate (`QoQ Growth`, 季度环比增速):

| Metric | Actual | Prior Guidance | Consensus | Prior Quarter Actual | QoQ Growth | YoY | Beat/Miss | Source Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---|

For QoQ Growth:

- Calculate it from current actual versus prior-quarter actual: `(current quarter actual - prior quarter actual) / abs(prior quarter actual)`.
- Use percentage growth for revenue, segment revenue, backlog, bookings, inventory, capex, cash flow, and other level metrics.
- Use basis-point change for margins and margin-like rates.
- For EPS or net income when either period is negative, near zero, or affected by one-time items, show the dollar change and explain why a percentage growth rate may be misleading.
- If a prior-quarter value cannot be verified from a reliable source, write `prior-quarter source gap`, leave the QoQ field blank or `n/a`, and downgrade confidence for that metric rather than estimating from memory.

Check at least:

- Revenue.
- Gross margin.
- Operating income or loss.
- Net income or loss.
- EPS, clearly labeled as GAAP or non-GAAP.
- Cash, debt, and liquidity.
- Free cash flow when disclosed.
- Backlog, bookings, deferred revenue, prepayments, or order indicators when relevant.
- Segment, product, geography, and customer mix.
- Quarter-over-quarter growth for total revenue, EPS, gross margin, major segment revenue, backlog/orders, inventory, capex, and free cash flow when the relevant prior-quarter actual is available.
- Share count and dilution.

Never mix GAAP and non-GAAP numbers without labeling them.

### 3. Quantify The Surprise

Calculate:

- Revenue beat or miss in dollars and percent.
- EPS beat or miss in dollars.
- Gross-margin surprise in basis points.
- Guidance midpoint versus consensus.
- Guidance midpoint versus prior-quarter run rate.
- QoQ acceleration or deceleration versus the prior quarter for total company and thesis-critical segments.
- Whether the surprise came from demand, pricing, mix, pull-forward, cost control, tax, share count, one-time items, or accounting.

Classify the print:

| Classification | Meaning |
|---|---|
| Clean beat | Revenue, margin, EPS, and guidance all exceed expectations with quality drivers |
| Low-quality beat | EPS beat mainly comes from cost cuts, tax, share count, or one-time items |
| Mixed print | Current quarter beats but guidance is weak, or revenue beats while margins disappoint |
| Beat-and-raise | Current quarter beats and next-quarter or full-year guidance rises materially |
| Thesis break | Results or commentary directly contradict the core investment thesis |

### 4. Analyze Guidance

Extract:

- Revenue range and midpoint.
- EPS or net income/loss range.
- Gross-margin assumptions.
- Segment drivers.
- Capacity assumptions.
- Customer and order assumptions.
- Regulatory, export-license, supply-chain, or qualification assumptions.
- Revenue already covered by backlog, orders, permits, or contracted shipments versus revenue still dependent on new orders or approvals.

Compare guidance against:

- Street consensus.
- Prior implied trajectory.
- Management's historical conservatism or optimism.
- The growth rate required by the investment thesis.

### 5. Mine The Conference Call

Extract only decision-useful content.

Before analyzing the current call in isolation, retrieve the immediately preceding quarter's call, earnings-webcast, results-briefing, or investor-meeting content through the same source-quality hierarchy used for the current event. Prefer official company transcript, company-hosted replay, official event-platform replay/captions, or regulatory filing exhibits. If those are unavailable, use a reliable third-party full transcript as a fallback and label it as `prior_quarter_third_party_transcript`. If no complete prior-quarter event content can be found after reasonable source discovery, write `prior-quarter call source gap`, list the missing material, and avoid making unsupported tone-change claims.

Use this table:

| Topic | Management Said | Evidence Type | Investment Meaning | Follow-Up |
|---|---|---|---|---|

Required topics:

- Demand: AI data center, telecom, consumer, industrial, auto, or other end markets.
- Orders: backlog, visibility, cancellation risk, long-term agreements.
- Capacity: utilization, expansion timing, bottlenecks, capex.
- Customers: wins, qualification progress, concentration, geography, hyperscaler/OEM/channel signals.
- Pricing and margin: ASP, mix, yield, raw materials, freight, labor.
- Supply chain: shortages, export controls, inventory, supplier qualification.
- Balance sheet: cash burn, financing, dilution, debt maturity.
- Management tone: more confident, more cautious, or materially changed versus prior calls.
- Analyst Q&A: questions management avoided, clarified, or answered with unusual detail.

### 5A. Compare With The Prior-Quarter Call

Every post-earnings call, webcast, results-briefing, or investor-meeting analysis must include a prior-quarter event comparison when the prior-quarter event content is available. Compare current-quarter prepared remarks, management discussion, and Q&A against the immediately preceding quarter, not against vague historical memory.

Use this table:

| Topic | Prior-Quarter Call | Current-Quarter Call | Change | Evidence Type | Investment Meaning | Follow-Up |
|---|---|---|---|---|---|---|

Required comparison topics:

- Demand and end-market tone: AI data center, telecom, industrial, consumer, auto, or company-specific end markets.
- Orders and backlog: visibility, cancellation risk, order duration, LTAs, bookings, backlog conversion, or customer ordering intent.
- Guidance drivers: whether management raised, narrowed, softened, or changed the assumptions behind next-quarter or full-year guidance.
- Capacity and bottlenecks: utilization, expansion timing, internal constraints, upstream constraints, lead times, yield, and supplier qualification.
- Pricing and margins: ASP, mix, cost pass-through, raw materials, yield, utilization, freight, labor, and gross-margin bridge.
- Customer signals: named customers, design wins, qualification status, concentration risk, geographic or end-user ambiguity.
- Inventory and channel: customer inventory, company inventory, channel digestion, pull-forward, or allocation.
- Q&A behavior: newly detailed answers, avoided questions, changed wording, or analyst concerns that repeated across quarters.

Classify each change as one of:

- `improved`
- `deteriorated`
- `unchanged`
- `new_disclosure`
- `walked_back`
- `prior-quarter source gap`

When the prior-quarter call and current-quarter call use different source types, state the source-quality mismatch. Do not overstate wording changes if one side is an official transcript and the other side is a third-party transcript.

### Downstream Demand Outlook Rule

For every post-earnings call, webcast, results-briefing, or investor-meeting analysis, actively search the earnings release, guidance, prepared remarks, and Q&A for downstream demand and customer-outlook evidence. Do not stop at financial metrics, supply-chain wording, or upstream bottleneck checks.

Language hard rule: In any Chinese final report, the full downstream demand section must be written in Chinese, including the section title, table headers, item names, evidence notes, timeframe, demand-quality assessment, investment meaning, confidence narrative, and absence statements. Preserve only the canonical `Mention Status` enum values in English for machine readability.

Always separate:

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

### Upstream Bottleneck Evidence Rule

For every post-earnings call analysis, actively search the earnings release, investor presentation, prepared remarks, and Q&A for upstream bottlenecks. Do not rely only on generic "supply chain" wording. Search for the company's actual upstream terms, including supplier, substrate, wafer, fab, material, component, capacity, equipment, lead time, yield, inventory, allocation, qualification, long-term agreement, prepayment, take-or-pay, shortage, constraint, tightness, bottleneck, and the segment-specific product names.

Language hard rule: In any Chinese final report, the full upstream bottleneck section must be written in Chinese, including the section title, table headers, upstream item names, evidence notes, bottleneck type, timeframe, investment meaning, confidence narrative, and absence statements. Preserve only the canonical `Mention Status` enum values in English for machine readability.

Always separate:

- Confirmed current bottleneck: management explicitly says a supply, capacity, material, equipment, yield, supplier, or qualification issue limits shipments or margins now.
- Future bottleneck risk: management says future ramp, 2027 demand, new capacity, customer qualification, or supplier expansion could become constrained.
- Covered or mitigated risk: management says the bottleneck exists in the market but is covered by LTAs, inventory, internal capacity, alternate suppliers, or customer agreements.
- Not mentioned: the filing, prepared remarks, and Q&A do not mention the alleged bottleneck.

Do not infer a bottleneck from a hot theme, stock move, segment shortage headlines, or a third-party summary when management did not say it. If the user asks about a specific upstream item, such as InP, substrate, pump lasers, memory, advanced packaging substrate, CCL, copper foil, liquid-cooling components, transformers, or power equipment, answer explicitly whether it was mentioned, not mentioned, denied, mitigated, or only inferable.

Use this table when upstream bottlenecks matter:

| Upstream Item | Mention Status | Evidence Location | Management Wording | Bottleneck Type | Timeframe | Investment Meaning | Confidence |
|---|---|---|---|---|---|---|---|

Allowed `Mention Status` values:

- `mentioned_current_bottleneck`
- `mentioned_future_risk`
- `mentioned_mitigated`
- `mentioned_not_bottleneck`
- `not_mentioned`
- `third_party_only`

If no upstream bottleneck is found, say so plainly and keep the conclusion at `not_mentioned` or `evidence_absent`. Do not fill the gap with industry knowledge unless clearly labeled as outside-call context.

Separate:

- Hard fact.
- Management claim.
- Analyst inference.
- Our own inference.

### 6. Build The Investment Read-Through

Translate the quarter into market implications:

- What changed for the next one to two quarters?
- What changed for the 12- to 24-month thesis?
- Which KPI will validate or disprove management's claims?
- Is the stock reacting to fundamentals, short squeeze, positioning, expectation reset, or sentiment?
- Does the result help suppliers, customers, competitors, or mapped listed peers?

For supply-chain companies, explicitly classify:

- Direct beneficiary.
- Indirect beneficiary.
- Theme-only beneficiary.
- Potential loser.

### 7. Build Scenarios

For important earnings, create three scenarios:

| Scenario | Probability | Key Assumptions | Revenue/EPS Path | Stock Implication |
|---|---:|---|---|---|
| Bull |  |  |  |  |
| Base |  |  |  |  |
| Bear |  |  |  |  |

Do not assign high confidence when a key variable depends on regulatory approval, one large customer, unverified capacity, or undisclosed customer identity.

## Output Template

```text
Conclusion First:
- Print classification:
- Biggest upside surprise:
- Biggest disappointment:
- Guidance quality:
- Most important call takeaway:
- Stock-reaction view:
- Key follow-up indicators:
- Source status: company_original_status / call_content_status / final_source_type / missing_materials / provisional true/false / confidence level

1. Company Fundamental Baseline
[one-paragraph business model, business map table, and earnings interpretation bridge]

2. Actual Results vs Expectations and QoQ
[table with actual, prior guidance, consensus, prior-quarter actual, QoQ Growth, YoY, beat/miss, and source notes]

3. Guidance vs Expectations
[table]

4. Conference-Call Takeaways and Prior-Quarter Call Comparison
[current-call takeaway table plus prior-quarter call comparison table with prior-quarter source status, current-quarter source status, change classification, evidence type, investment meaning, and follow-up]

5. Upstream Bottleneck Check
[table with mention status; say "not mentioned" when absent]

6. Difference vs Our Prior Forecast
[table]

7. Investment Judgment
- Fundamental change:
- Earnings elasticity change:
- Trading elasticity change:
- Biggest risk:

8. Follow-Up Checklist
[3-7 specific indicators]
```

## AXTI-Style Special Rules

For AXTI, optical modules, compound semiconductors, InP, GaAs, Ge, SiC, substrate makers, device makers, or export-control-sensitive companies, always check:

- Product mix, especially InP, GaAs, Ge, SiC, substrates, devices, and modules.
- AI data-center demand versus telecom, consumer, and industrial demand.
- Backlog size and whether backlog is cancellable.
- Capacity expansion timing, equipment lead time, yield, and customer qualification.
- Upstream bottlenecks named in the earnings release, prepared remarks, and Q&A, especially substrates, wafers, fab capacity, epitaxy, pumps, lasers, MEMS, rare earths, tools, qualified suppliers, and contract manufacturing.
- Export-license status: granted, pending, denied, not required, or management inference.
- Domestic shipments versus export shipments.
- Customer geography and end-user ambiguity.
- Financing, dilution, subsidiary funding, and capex burden.
- Whether guidance is covered by permitted shipments or still depends on future approvals.

Do not assume:

- A U.S.-listed customer means the shipment destination is the United States.
- Backlog equals revenue.
- Added nameplate capacity equals qualified capacity.
- A market-wide shortage headline means this company confirmed the same bottleneck.
- A future capacity project means current upstream supply is already short.
- A supplier or substrate risk is material if management says it is covered, mitigated, or mostly under control.
- Export-license improvement means regulatory risk is gone.
- Bullish management tone means orders will convert.

## Quality Bar

A good earnings-call analysis must include:

- A concise company baseline before earnings interpretation: what the company does, main businesses, competitive strength, AI relevance, and baseline risks.
- Company original-source status: found, partially found, missing, or unavailable.
- Numeric beat-or-miss table.
- Prior-quarter official-source status and QoQ growth calculations for total results and thesis-critical segments.
- Guidance midpoint comparison.
- Current-quarter call source status and prior-quarter call source status.
- At least five call takeaways ranked by importance.
- A prior-quarter call comparison covering demand, orders/backlog, guidance drivers, capacity/bottlenecks, pricing/margins, customer signals, inventory/channel, and Q&A behavior when prior-quarter call content is available.
- A downstream demand outlook check covering end-market demand, customer ordering intent, guidance coverage, demand quality, and management tone.
- Clear distinction between fact, management claim, analyst inference, and our inference.
- An upstream bottleneck check that explicitly marks each relevant item as mentioned, mitigated, future risk, not mentioned, or third-party only.
- Final source-status fields: `company_original_status`, `call_content_status`, `final_source_type`, `missing_materials`, `provisional true/false`, and `confidence level`.
- Upside catalysts and downside risks.
- Specific post-call tracking indicators.

If source data is incomplete, state what is missing and downgrade the conclusion to provisional.
