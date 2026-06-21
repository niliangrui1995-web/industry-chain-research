---
name: semiconductor-ai-chain-investment-researcher
description: Top-down semiconductor and AI supply-chain investment research for segment selection, technology bottlenecks, overseas oligarchs, hard-evidence A-share mapping, and within-segment company comparison. Use for AI产业链, semiconductor, HBM, advanced packaging, ABF substrate, PCB/CCL/electronic cloth/copper foil/resin, optical modules, silicon photonics, CPO/OCS, liquid cooling, power, connectors, servers, data-center power, A-share mapping, true beneficiary vs concept stock, or 1-3 hard-strength stock picks per subsegment.
---

# Semiconductor AI Chain Investment Researcher

## Purpose

Use this skill as the main deep-research and stock-selection skill for semiconductor and AI supply-chain workflows.

For evergreen structural questions, it can run directly after `industry-research-router`. For current-news, rumor, or source-gap tasks, use it after `ai-chain-research-orchestrator` has framed the evidence and, when needed, after `browser-grok-gemini-research` has collected Grok/X or Gemini webpage output.

This skill turns evidence into a top-down investment workflow:

`subsegment priority -> technology bottleneck -> overseas oligarchs -> A-share hard-strength mapping -> within-segment horizontal comparison -> 1-3 picks or observation-only`

It is not a news collector, browser operator, cron job, or daily-report pipeline.

## Inputs

Use the strongest available verified inputs:

- Segment taxonomy, aliases, and overseas oligarch anchors.
- Evidence ledgers from `ai-chain-research-orchestrator`.
- Objective collection rows from Grok/X, Gemini, user-provided links, official pages, or filings.
- Official announcements, exchange disclosures, filings, annual/interim/quarterly reports, company IR, reputable media, and direct source pages.
- `TDX Finance Data:tdx-finance-data`, `allstock-data`, and other market-data skills only for quote, K-line, turnover, valuation, technical timing, concept heat, and涨停/跌停 market-reaction checks.

If evidence is missing, state the source gap and keep the conclusion at observation level.

## Fixed Workflow

### 1. Score The Segment Universe

Do not start from A-share names. Start from the relevant AI/semiconductor segment universe.

Create one scored row for every serious track with three independent scores. Do not collapse them into one vague heat score.

| Field | Meaning |
|---|---|
| `track_id`, `track_name` | Segment identity |
| `structural_segment_score` | 0-1 score for whether the segment is structurally important in the AI/semiconductor chain |
| `today_attention_score` | 0-1 score for whether the segment deserves attention in the current evidence window |
| `a_share_execution_score` | 0-1 score for whether the segment can be mapped to hard-evidence A-share opportunities |
| `evidence_strength` | A/B/C/none, with exact source refs |
| `strict_window_signal` | Whether the signal is fresh inside the requested window |
| `overseas_vanguard_signal` | Overseas oligarch or leading customer signal, positive/neutral/negative/unavailable |
| `source_gap_impact` | Whether an unresolved gap can change the conclusion |
| `a_share_mapability` | high/medium/low/none |
| `risk_level` | evidence risk, crowding risk, valuation risk, accounting risk, or policy risk |
| `segment_status` | selected/strategic_watch/event_noise/rejected |
| `a_share_status` | main_pick/observation_only/no_mapping |
| `reason` | Why the track is selected, watched, or rejected |

### Structural Segment Score

This score answers: "Is this segment structurally worth studying from the top down?"

- 25% technology bottleneck and substitution difficulty: yield, certification, process recipe, reliability, power/thermal envelope, or material know-how.
- 20% value share and margin leverage: unit value, ASP leverage, gross-margin sensitivity, or operating leverage.
- 15% AI demand transmission strength: direct linkage to GPU/ASIC/HBM/advanced packaging/server/datacenter buildout.
- 15% overseas oligarch concentration and industrial validation: whether global leaders and customers confirm the chain position.
- 15% supply-demand pressure: shortage, price hike, allocation, capacity expansion, order visibility, or utilization.
- 10% A/B source-proof quality.

### Today Attention Score

This score answers: "Should this segment enter the current research window?"

- 30% strict-window A/B catalyst: fresh official, filing, earnings, order, capex, pricing, shortage, or reputable media evidence.
- 20% overseas oligarch or leading-customer signal.
- 20% freshness and incrementality: whether the evidence changes the prior view instead of recycling old news.
- 15% source-gap result impact: whether supplemental search confirms, rejects, or materially reframes the signal.
- 10% market attention or C-layer signal specificity: only for watch or verification priority unless confirmed.
- 0 to -20% risk penalty: stale news, C-only evidence, source-missing chatter, valuation crowding, accounting noise, or policy uncertainty.

### A-Share Execution Score

This score answers: "Can this segment produce hard-evidence A-share picks?"

- 25% exact business exposure to the selected segment.
- 25% customer/order/certification evidence.
- 15% capacity, yield, product generation, value share, or process fit.
- 15% revenue, gross-margin, and net-profit elasticity.
- 10% market cap, float market cap, valuation, liquidity, trend, and crowding.
- 0 to -20% penalty for financial deterioration, concept-board contamination, weak disclosure, valuation exhaustion, or only technical-price evidence.

Segment and A-share decisions use the three scores separately:

| Score Pattern | Decision |
|---|---|
| High structural + high today + high A-share execution | selected segment with 1-3 main A-share picks |
| High structural + high today + low A-share execution | selected segment, `observation_only` for A-share |
| High structural + low today | strategic watch, not a current main segment |
| Low structural + high today | event noise or short-term watch |
| High A-share execution + low structural | reject reverse-mapped stock story; do not promote the segment |

Select 3-5 priority segments when evidence supports them. Select fewer if evidence is weak. Never force filler tracks.

### 2. Deep-Research Each Selected Segment

For each selected segment, answer:

- What exactly is the segment and where does it sit in the AI compute stack?
- What changed now, and is it inside the requested window?
- What is the real technical bottleneck: yield, capacity, material formula, equipment, reliability, power/thermal envelope, certification, or customer qualification?
- Where is the value share and margin leverage?
- Who are the overseas oligarchs and what indicator sequence should be watched?
- What would invalidate the thesis?
- Which evidence gaps still matter before mapping a main A-share pick?

Keep C-layer, X-only, or source-missing items in watch mode unless direct sources confirm them.

### 3. Map Overseas Oligarchs To A-Share Candidates

Only map through the exact supply-chain relation:

- Product exposure to the selected segment.
- Customer/order/certification evidence.
- Capacity, yield, product generation, or material/process fit.
- Revenue contribution or plausible earnings leverage.
- Replacement difficulty and customer switching cost.
- Whether the company is a true beneficiary or only theme-adjacent.

Reject candidates that only share a theme keyword, appear in concept boards, or rely only on technical strength.

### 4. Compare Candidates Inside Each Segment

Compare within the same selected segment before cross-segment ranking.

Required dimensions:

- Product position and value share.
- Hard evidence: official filing, customer proof, certification, order/capacity disclosure, IR answer, or reputable source.
- Customer quality and verification cycle.
- Capacity/yield/process barrier.
- Revenue, gross margin, net profit trend, and latest financial-report direction.
- Market cap, float market cap when available, valuation, turnover, trend, and crowding.
- Fundamental quality, earnings elasticity, and trading elasticity as separate rankings.

Each selected segment should output:

- 1-3 hard-strength A-share companies when evidence is sufficient.
- `observation_only` when evidence is not sufficient.
- A short reason for rejected names that are popular but weak.

### 5. Optional Structured Outputs

If the user asks for files, tables, or a reusable watchlist, write only the artifacts needed for that request:

- `segment_priority_heatmap.md` or `.json`: readable heatmap and selected/watch/rejected explanation.
- `segment_deep_research.md`: one section per selected segment.
- `segment_a_share_compare.md`: within-segment A-share candidate comparison.
- `a_share_fundamental_compare.md`: cross-segment summary of serious A-share candidates.
- `mapped_candidates.json`: grouped by segment, not event-first headlines.

Do not require daily-report guardrail scripts, email sending, or pipeline-specific validation in this project unless those files actually exist and the user requested that workflow.

## Recommended Skill Stack

Use the smallest useful combination:

- Entry and routing: `industry-research-router`.
- Current evidence coordination: `ai-chain-research-orchestrator`.
- Browser Grok/Gemini collection: `browser-grok-gemini-research` when needed.
- Segment investment deep research: `semiconductor-ai-chain-investment-researcher`.
- Long-form source collection or cross-language gap fill: `deep-research`.
- Competitive landscape and true leaders: `competitive-landscape`, `competitive-intel`.
- A-share company fundamentals: `stock-evaluator`, `business-analyst`.
- Ranking rubric and bias control: `advanced-evaluation`.
- Market data and timing: `TDX Finance Data:tdx-finance-data`, iFinD MCPs, `allstock-data`, `banana-farmer`, `finance`, `alpha-vantage`.

Non-semiconductor niche analysis should stay in `user-investment-framework` + `industry-chain-deep-disassembly` + `deep-research` unless the user explicitly requests another installed framework.

## Output Pattern

```text
结论先行：
- 当前最值得深研的细分环节：...
- 可进入主结论的 A 股硬实力公司：...
- 只能观察的环节或公司：...

细分环节热力图：
| rank | track | structural_segment_score | today_attention_score | a_share_execution_score | why now | evidence | status |

环节深研：
## Segment X
- 技术瓶颈：
- 海外寡头：
- A股候选池：
- 入选/剔除理由：

环节内横向对比：
| rank | company | code | product position | hard evidence | earnings elasticity | trading elasticity | verdict |
```

## Anti-Patterns

- Do not start from hot A-share names and reverse-map a story.
- Do not let market reaction, K-line strength, Grok chatter, or Gemini prose prove beneficiary status.
- Do not promote C-layer or source-missing rumors to main picks.
- Do not compare companies across different segments before finishing within-segment comparison.
- Do not force three picks when only one company has hard evidence.
- Do not mix fundamental quality, earnings elasticity, and trading elasticity into one vague score.
