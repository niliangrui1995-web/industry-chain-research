---
name: earnings-call-investment-analyst
description: Use this skill to analyze public-company earnings releases, financial results, management guidance, and earnings-call transcripts or replays. It is optimized for investment research, beat-or-miss analysis, expectation-gap judgment, guidance quality, conference-call extraction, original-source collection, audio replay transcription, and post-earnings stock-reaction assessment.
---

# Earnings Call Investment Analyst

## Purpose

Use this skill to turn earnings releases, financial statements, guidance, and conference-call content into an investment-grade analysis.

Answer four questions first:

1. Did the company beat, meet, or miss expectations?
2. What changed versus prior guidance, consensus, and our previous forecast?
3. What did management say that changes the next one to four quarters?
4. What should be tracked after the print for stock reaction, thesis validation, and risk control?

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

If official IR, the company-hosted event page, or the official event platform does not expose a complete transcript, audio replay, or video replay, the agent must keep searching for complete call audio or transcript through reputable fallback paths before giving up. Try StockAnalysis, Quartr, Motley Fool, Seeking Alpha, Benzinga, Alpha Spread, and EarningsCall.biz. If a reputable third-party full transcript and original call audio are both available, use the full transcript as the primary working source and use the audio only for targeted verification of decision-useful wording, disputed passages, and transcript quality issues. Do not run full-audio ASR by default in that case. If a complete recording is found on StockAnalysis, Quartr, or another transcript/audio aggregator, treat the content as original call audio but label the hosting as third-party hosted. Cross-check decision-useful claims against the official release, SEC or exchange filing, and company-linked event page.

## Bundled Resources

Use bundled resources only when they help the specific task.

- Read `references/source-workflow.md` when the user asks for original-source collection, replay extraction, transcript evidence packs, or audio-first call analysis.
- Use `scripts/source_discovery.py` to build an initial official-source inventory for a ticker, company, quarter, and fiscal year.
- Use `scripts/webcast_asset_fetcher.py` to inspect an earnings webcast or replay page and extract candidate audio, video, transcript, subtitle, JSON, and script assets.
- Use `scripts/caption_playlist_fetcher.py` to download and merge official HLS caption playlists such as Q4 `subtitles.m3u8` when the webcast exposes captions but not a plain transcript.
- When official webcast assets are incomplete, use the targeted search URLs from `source_discovery.py` to inspect third-party transcript/audio fallback pages, then run `scripts/webcast_asset_fetcher.py` on the chosen StockAnalysis, Quartr, Motley Fool, Seeking Alpha, Benzinga, Alpha Spread, or EarningsCall.biz page.
- Use `scripts/audio_transcriber.py --check-deps` before audio-first work, then use `scripts/audio_transcriber.py` only when no reputable full transcript is available, when the user explicitly asks for audio-first analysis, or when transcript/audio spot checks reveal a material transcript-quality problem. Prefer the project ASR venv plus `--provider faster-whisper --device auto --compute-type auto`; use `--no-ffmpeg` only when PyAV can read the source media directly. Use OpenAI transcription only when the API package and `OPENAI_API_KEY` are configured.
- Use `scripts/setup_asr_env.ps1` on Windows to create a local Python ASR environment from `requirements-asr.txt` when faster-whisper or OpenAI transcription packages are missing.
- Use `scripts/earnings_pack_builder.py` to merge source inventory, webcast assets, transcript output, and optional actuals/guidance/consensus JSON into a standard evidence pack.
- Read `references/evidence-schema.md` when building, validating, or extending the evidence pack format.

## Core Workflow

### 1. Define The Earnings Setup

Identify:

- Company name and ticker.
- Reporting quarter and fiscal or calendar period.
- Earnings release date and call date.
- Prior company guidance.
- Street consensus for revenue, EPS, margin, and next-quarter guidance.
- The user's prior forecast if available.
- Key thesis variables going into the print.

For a pre-earnings preview, separate:

- Company guidance.
- Sell-side consensus.
- Buy-side whisper or implied expectation.
- Our own forecast.

For a post-earnings review, separate:

- Actual results.
- New guidance.
- Conference-call incremental information.
- Stock reaction.

### 2. Extract Core Financial Results

Use a compact comparison table:

| Metric | Actual | Prior Guidance | Consensus | Prior Quarter | YoY | QoQ | Beat/Miss |
|---|---:|---:|---:|---:|---:|---:|---:|

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
- Share count and dilution.

Never mix GAAP and non-GAAP numbers without labeling them.

### 3. Quantify The Surprise

Calculate:

- Revenue beat or miss in dollars and percent.
- EPS beat or miss in dollars.
- Gross-margin surprise in basis points.
- Guidance midpoint versus consensus.
- Guidance midpoint versus prior-quarter run rate.
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

1. Actual Results vs Expectations
[table]

2. Guidance vs Expectations
[table]

3. Conference-Call Takeaways
[table]

4. Difference vs Our Prior Forecast
[table]

5. Investment Judgment
- Fundamental change:
- Earnings elasticity change:
- Trading elasticity change:
- Biggest risk:

6. Follow-Up Checklist
[3-7 specific indicators]
```

## AXTI-Style Special Rules

For AXTI, optical modules, compound semiconductors, InP, GaAs, Ge, SiC, substrate makers, device makers, or export-control-sensitive companies, always check:

- Product mix, especially InP, GaAs, Ge, SiC, substrates, devices, and modules.
- AI data-center demand versus telecom, consumer, and industrial demand.
- Backlog size and whether backlog is cancellable.
- Capacity expansion timing, equipment lead time, yield, and customer qualification.
- Export-license status: granted, pending, denied, not required, or management inference.
- Domestic shipments versus export shipments.
- Customer geography and end-user ambiguity.
- Financing, dilution, subsidiary funding, and capex burden.
- Whether guidance is covered by permitted shipments or still depends on future approvals.

Do not assume:

- A U.S.-listed customer means the shipment destination is the United States.
- Backlog equals revenue.
- Added nameplate capacity equals qualified capacity.
- Export-license improvement means regulatory risk is gone.
- Bullish management tone means orders will convert.

## Quality Bar

A good earnings-call analysis must include:

- Company original-source status: found, partially found, missing, or unavailable.
- Numeric beat-or-miss table.
- Guidance midpoint comparison.
- At least five call takeaways ranked by importance.
- Clear distinction between fact, management claim, analyst inference, and our inference.
- Upside catalysts and downside risks.
- Specific post-call tracking indicators.

If source data is incomplete, state what is missing and downgrade the conclusion to provisional.
