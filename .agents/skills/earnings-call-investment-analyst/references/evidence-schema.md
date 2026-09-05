# Earnings Evidence Pack Schema

Use this schema for `evidence_pack.json` and `evidence_pack.md`. The pack is a structured evidence layer, not the final investment analysis.

## Source Policy

The pack must prioritize company original materials:

1. `company_original`: company IR page, company-hosted earnings release, company-hosted presentation, company-hosted webcast, company-hosted replay, company-hosted transcript.
2. `regulatory_filing`: SEC, exchange, or other official regulatory filing.
3. `official_event_platform`: company-linked event platform such as Q4 Inc, Notified, Intrado, Chorus Call, or a company-selected webcast provider.
4. `original_call_audio`: complete original conference-call recording hosted outside the company or official event platform, such as Quartr or StockAnalysis.
5. `market_data`: consensus, price, volume, market cap, valuation, or estimate data.
6. `third_party_transcript`: transcript provider, finance portal, or media transcript.
7. `media_or_analyst`: financial media, analyst notes, blogs, or commentary.
8. `unknown`: source type cannot be determined.

Shared hosting domains such as ON24 or Q4 CDN do not prove that an event belongs to the company. The pack builder keeps them `unknown` until the agent verifies a company IR/filing link to the exact event or asset. Then use the existing `--manual-source` fields with `type=official_event_platform` and `notes` containing the official linking source and verification context; the explicit role also applies when the same URL appears in webcast assets. Pass only company-owned domains to `--company-domain`, never a shared hosting provider.

For reported facts, use `company_original` and `regulatory_filing` first. Use lower-tier sources only when official evidence is missing, and label that limitation.

Use `hosting_type` to separate content origin from hosting path:

- `company_hosted`
- `official_platform_hosted`
- `regulatory_hosted`
- `third_party_hosted`
- `local_derivative`
- `unknown`

For example, a Quartr audio file can be `source_type: original_call_audio` and `hosting_type: third_party_hosted`. A local Whisper transcript made from that file should inherit `source_type: original_call_audio`, use `hosting_type: local_derivative`, and point back to the audio source with `origin_source_id`.

## Top-Level JSON Fields

```json
{
  "schema_version": "1.0",
  "created_at": "ISO-8601 timestamp",
  "company": "Company name",
  "ticker": "Ticker",
  "quarter": "Q1",
  "fiscal_year": "2026",
  "company_original_status": "found | partial | missing | unavailable",
  "call_content_status": "official_complete | official_partial | fallback_complete | fallback_partial | missing",
  "missing_materials": [],
  "provisional": false,
  "fallback_completed": false,
  "recheck_after": "ISO-8601 timestamp or empty string",
  "source_policy": {},
  "sources": [],
  "discovery": {},
  "script_runs": [],
  "fallback_source_matrix": [],
  "webcast": {},
  "transcript": {},
  "actuals": {},
  "guidance": {},
  "consensus": {},
  "valuation": {},
  "calculation_audits": [],
  "financial_quality_checks": [],
  "management_commitments": [],
  "qa_assessments": [],
  "call_takeaways": [],
  "risk_flags": [],
  "evidence_ledger": [],
  "gaps": []
}
```

## Source Object

```json
{
  "id": "S001",
  "title": "Q1 2026 earnings release",
  "source_type": "company_original",
  "url": "https://...",
  "file_path": "raw/earnings_release.pdf",
  "retrieved_at": "ISO-8601 timestamp",
  "publisher": "Company IR",
  "hosting_type": "company_hosted",
  "origin_source_id": "",
  "content_origin": "",
  "notes": "Official company-hosted release"
}
```

## Script Run Object

Use this only when a helper script was actually run. Scripts are optional helpers and must not define the task boundary.

```json
{
  "script_used": "webcast_asset_fetcher.py",
  "purpose": "Probe official webcast page for replay assets",
  "script_result": "found | partial | none | failed | blocked",
  "script_limitation": "401/403, JS-only page, no recording, stale provider, parser miss, unsupported argument, or empty string",
  "manual_fallback_path": "Search/provider/browser/HTTP/network/direct-download path used after the script",
  "final_source_type": "company_original | regulatory_filing | official_event_platform | original_call_audio | third_party_transcript | media_or_analyst | unknown",
  "notes": ""
}
```

## Fallback Source Matrix Object

Use this when official call transcript/audio/video/captions are incomplete and third-party transcript or audio fallback materially affects confidence or source selection. Record routes actually used or checked; provider names are examples, not a mandatory checklist.

```json
{
  "provider": "StockAnalysis | Quartr | Motley Fool | Seeking Alpha | Benzinga | Alpha Spread | EarningsCall.biz | search | browser | HTTP | event platform | other",
  "status": "found | stale | missing | blocked | partial",
  "url": "https://...",
  "source_type": "third_party_transcript | original_call_audio | media_or_analyst | unknown",
  "complete": "yes | no | partial | unknown",
  "access_or_failure_note": "403, login wall, older quarter only, no target transcript, complete transcript found, etc.",
  "used": true,
  "source_refs": ["S010"]
}
```

## Actuals Object

Use this object for reported financial results:

```json
{
  "period": "Q1 FY2026",
  "currency": "USD",
  "metrics": [
    {
      "name": "revenue",
      "actual": 28200000,
      "unit": "USD",
      "gaap_type": "reported",
      "prior_guidance": "26M-28M",
      "consensus": 27000000,
      "yoy": null,
      "qoq": null,
      "source_refs": ["S001", "S002"],
      "notes": ""
    }
  ]
}
```

## Guidance Object

```json
{
  "period": "Q2 FY2026",
  "metrics": [
    {
      "name": "revenue",
      "range_low": 33000000,
      "range_high": 35000000,
      "midpoint": 34000000,
      "unit": "USD",
      "consensus": null,
      "source_refs": ["S001", "S003"],
      "notes": "Covered by permitted or permit-free shipments"
    }
  ]
}
```

## Consensus Object

```json
{
  "provider": "Source name",
  "expectation_as_of": "ISO-8601 date or timestamp",
  "value_type": "historical_point_in_time | public_pre_event_reconstruction | current_rolling",
  "contributor_count": 5,
  "member_prediction_dates": ["ISO-8601 date"],
  "expectation_age_days": 30,
  "metrics": [
    {
      "name": "revenue",
      "consensus_metric": "revenue",
      "metric_basis": "reported | deducted_nonrecurring | adjusted_non_gaap",
      "period": "Q1 FY2026",
      "value": 27000000,
      "unit": "USD",
      "source_refs": ["S010"]
    }
  ],
  "comparisons": [
    {
      "source_period": "Q2 FY2026",
      "company_metric": "deducted_attributable_net_profit",
      "derived_metric": "annualized_single_quarter_deducted_attributable_net_profit",
      "company_value_type": "actual_quarter | preannouncement_quarter_range | derived_quarter",
      "quarterly_value_low": 0,
      "quarterly_value_mid": 0,
      "quarterly_value_high": 0,
      "annualization_factor": 4,
      "annualized_value_low": 0,
      "annualized_value_mid": 0,
      "annualized_value_high": 0,
      "derivation_formula": "H1-Q1 for Q2, nine-month-H1 for Q3, FY-nine-month for Q4, or empty string",
      "consensus_metric": "fy_attributable_net_profit",
      "consensus_period": "FY2026",
      "consensus_value": 0,
      "comparison_basis": "annualized_quarterly_deducted_vs_fy_attributable_consensus",
      "gap_low": null,
      "gap_mid": null,
      "gap_high": null,
      "annualized_core_gap_status": "above | straddles | below | insufficient",
      "formal_surprise_status": "N/A",
      "attributable_minus_deducted": null,
      "source_refs": ["S001", "S010"],
      "notes": "User-defined cross-period and cross-metric run-rate comparison."
    }
  ]
}
```

For non-A-share reported actual or company guidance surprise, retain the
`financial-evidence-audit` `expectation_surprise` artifact with
`subject_kind=reported_actual|company_guidance`, same-period/same-metric/same-basis
consensus lineage, explicit meet band, and PIT source dates. Do not reuse the A-share
annualized-quarter comparison object for global GAAP/non-GAAP results or guidance.

For A-share comparisons, annualize the latest single-quarter deducted attributable profit by multiplying it by four, compare it with the pre-event full-year attributable-profit consensus, use `comparison_basis: annualized_quarterly_deducted_vs_fy_attributable_consensus`, and keep `formal_surprise_status: N/A`. A derived quarter must use same-company official cumulative disclosures on the same accounting basis and include `derivation_formula`. Preserve the raw quarterly values and `annualization_factor: 4`; do not store only the annualized result.

## Valuation Object

Use this object only when `market=A-share` and the task or user explicitly requests the single-quarter annualized convention. It is not a standard trailing-four-quarter multiple. For non-A-share companies, use a same-basis standard TTM or explicitly labeled forward denominator and the generic valuation audit contract.

```json
{
  "market_cap_as_of": "ISO-8601 timestamp",
  "total_market_cap": 0,
  "currency": "CNY",
  "profit_source_period": "Q2 FY2026",
  "quarterly_deducted_profit_low": 0,
  "quarterly_deducted_profit_mid": 0,
  "quarterly_deducted_profit_high": 0,
  "annualization_factor": 4,
  "annualized_deducted_profit_low": 0,
  "annualized_deducted_profit_mid": 0,
  "annualized_deducted_profit_high": 0,
  "pe_ttm_user_low": null,
  "pe_ttm_user_mid": null,
  "pe_ttm_user_high": null,
  "valuation_basis": "latest_single_quarter_deducted_attributable_net_profit_x4",
  "source_refs": ["S001", "S020"],
  "notes": "If annualized profit is non-positive, PE is N/A/not meaningful."
}
```

For a positive profit range, calculate the PE range in reverse order: `pe_ttm_user_low = market_cap / annualized_deducted_profit_high` and `pe_ttm_user_high = market_cap / annualized_deducted_profit_low`. Keep market cap and profit in the same currency and label the output `PE(TTM, user-defined)` or `PE(TTM，用户口径)`.

## Calculation Audit Object

Use this for every decision-critical calculation or reconciliation. It records the `financial-evidence-audit` result; it does not duplicate the full audit artifact.

```json
{
  "id": "CA001",
  "calculation_type": "qoq | yoy | expectation_gap | derived_quarter | annualization | market_cap | pe | sbc_dilution | cash_conversion | other",
  "input_periods": ["Q1 FY2026", "Q2 FY2026"],
  "currency": "CNY",
  "unit": "million",
  "metric_basis": "reported | deducted_nonrecurring | adjusted_non_gaap | other",
  "source_refs": ["S001", "S010"],
  "origin_ids": ["issuer-filing-Q2FY2026", "consensus-snapshot-2026-07-20"],
  "calculation_audit_status": "PASS | FAIL | ERROR | not_run",
  "audit_release_status": "publishable | blocked | provisional | invalid_input",
  "audit_artifact": "path to retained JSON audit record or empty string",
  "audit_blockers": ["blocking code or evidence gap"],
  "unresolved_numeric_conflicts": [],
  "notes": "Explain period, unit, definition, lineage, rounding, or conflict resolution."
}
```

An audit `PASS` confirms only that the supplied inputs meet the declared calculation and evidence contract. It does not prove that an unsupported input is true. `FAIL`, a non-publishable `audit_release_status`, non-empty `audit_blockers`, or unresolved numeric conflicts block the related beat/miss, valuation, dilution, financial-quality, or investment conclusion.

## Financial Quality Check Object

Use this for footnotes and cross-statement relationships. An unusual relationship is a research lead until its accounting basis, company explanation, and period comparability are verified.

```json
{
  "check_type": "related_party | sbc_dilution | contingency_or_commitment | accounting_policy_change | segment_reclassification | receivables_vs_revenue | inventory_vs_revenue | operating_cash_flow_vs_net_income | capex_or_capitalization",
  "periods": ["Q2 FY2026", "Q2 FY2025"],
  "observations": "Source-backed facts and any company explanation",
  "status": "lead | explained | warning | material_risk | not_disclosed | not_comparable | evidence_absent",
  "investment_meaning": "Why this may or may not change earnings quality or valuation",
  "source_refs": ["S001", "S002"],
  "calculation_audit_refs": ["CA004"],
  "follow_up": "What evidence or later period should resolve the issue"
}
```

For related parties record the counterparty, relationship, transaction nature, amount, pricing basis, and balance where disclosed. For SBC record both the accounting add-back and actual diluted-share effect. For contingencies record the obligation, possible timing, disclosed range, and why an amount is not estimable. For accounting-policy or segment changes preserve the old and new basis and whether prior periods were restated.

## Management Commitment Object

Track only measurable or otherwise verifiable prior management commitments. Do not treat aspirations or generic confidence statements as commitments.

```json
{
  "id": "MC001",
  "commitment": "Reach gross margin of X-Y% in Q2 FY2026",
  "stated_at": "Q1 FY2026 call",
  "due_period": "Q2 FY2026",
  "metric_or_event": "gross_margin",
  "target": "X-Y%",
  "original_source_refs": ["S004"],
  "current_result": "Reported result or event evidence",
  "result_source_refs": ["S001", "S005"],
  "status": "fulfilled | partially_fulfilled | missed | walked_back | not_yet_due | unverifiable",
  "assessment": "Explain basis changes, external conditions, or why verification is impossible"
}
```

Only commitments whose due period has arrived and whose original target and current result are comparable may be marked fulfilled, partially fulfilled, missed, or walked back. Do not calculate an aggregate fulfillment rate from non-comparable or selectively disclosed commitments.

## Q&A Assessment Object

Use this for decision-relevant analyst questions, especially questions about guidance gaps, margins, cash flow, customer loss, inventory, regulation, financing, accounting, or prior commitments.

```json
{
  "question": "Paraphrased question",
  "why_it_matters": "Decision relevance",
  "management_answer": "Short paraphrase or compliant excerpt",
  "directness": "direct | partial | evasive | not_answered | source_incomplete",
  "numeric_or_timeline_support": "Specific support or none",
  "tone_observation": "Optional observation",
  "tone_lead_only": true,
  "follow_up": "Evidence needed next",
  "source_refs": ["S004"],
  "timestamp": "00:42:10"
}
```

Tone, pauses, wording, or emotion may create a lead but cannot alone support a conclusion about integrity, orders, demand, or financial performance. Do not compare tone when the two periods use materially different source types or completeness.

## Call Takeaway Object

```json
{
  "rank": 1,
  "topic": "InP demand",
  "management_said": "Short paraphrase or timestamped quote",
  "evidence_type": "hard_fact | management_claim | analyst_inference | our_inference",
  "investment_meaning": "Why it matters",
  "follow_up": "What to track next",
  "source_refs": ["S004"],
  "timestamp": "00:31:22"
}
```

## Risk Flag Object

```json
{
  "risk": "export_license_dependency",
  "severity": "high | medium | low",
  "description": "Revenue depends on future export approvals.",
  "source_refs": ["S004"],
  "follow_up": "Track license approvals and shipment geography."
}
```

## Evidence Ledger Object

Use this for every important conclusion or data point:

```json
{
  "claim": "Q2 revenue guide is supported by permitted or permit-free shipments.",
  "claim_type": "guidance_quality",
  "confidence": "high | medium | low",
  "source_refs": ["S001", "S004"],
  "quote_or_excerpt": "Short compliant excerpt or paraphrase",
  "notes": "Explain if source is not company original."
}
```

## Gap Object

```json
{
  "gap": "No official transcript found.",
  "impact": "Call commentary depends on audio transcription or third-party transcript.",
  "severity": "medium",
  "next_step": "Use audio replay transcription and label uncertain segments."
}
```

## Validation Rules

- Every reported financial metric should have at least one `company_original` or `regulatory_filing` source reference when available.
- Every management statement should reference an official call transcript, official audio/video replay, official event platform, or `original_call_audio` when complete official media is unavailable.
- Every third-party number should be labeled with provider and date.
- Every A-share consensus comparison should record `expectation_as_of`, source quarter, raw quarterly deducted profit, `annualization_factor: 4`, annualized profit, full-year attributable consensus, `comparison_basis`, and company `value_type`; a derived quarter must record its formula and official source references.
- Every A-share user-defined PE(TTM) should record total market cap, `market_cap_as_of`, source quarter, annualized deducted-profit denominator, `valuation_basis`, and source references; return `N/A` when the denominator is non-positive. Non-A-share valuation must not use this object.
- Every decision-critical calculation must have a `calculation_audits` entry with independent source lineage, `calculation_audit_status: PASS`, and a publishable release before the derived number enters a formal conclusion. `FAIL`, `ERROR`, `not_run`, `blocked`, non-empty `audit_blockers`, or an unresolved numeric conflict must block the related conclusion and cannot be bypassed by setting `provisional: true`.
- Financial-quality warnings must cite official or regulatory evidence when available. Receivables, inventory, cash-flow, capex, SBC, policy, or segment changes are investigation leads until period, unit, definition, consolidation scope, and company explanation are checked.
- A management commitment may be graded only when the original commitment is measurable or verifiable, its due period has arrived, and both the original statement and current result have source references. Generic confidence language must not enter the commitment denominator.
- A Q&A directness judgment must preserve the decision-relevant question, the management answer, source completeness, and any numerical or timeline support. Tone observations must remain `tone_lead_only: true` and cannot be sole evidence for an investment conclusion.
- Third-party-hosted original call audio must not be listed as a company-hosted or official-event-hosted source.
- When a reputable full transcript and original call audio are both available from fallback providers, use the full transcript as the primary working source and record audio only as targeted verification evidence unless full-audio ASR was explicitly requested.
- The final analysis should not cite `media_or_analyst` as the sole source for reported results.
- Missing official company materials must create a `gaps` entry.
- A script returning no usable asset, 401/403, stale data, or a parser miss must create a `script_runs` entry if the script was run, and must not be treated as completion of fallback search.
- If official transcript, official replay, official audio/video, and official complete captions are missing while the call analysis uses third-party transcript or third-party-hosted original audio, set `provisional: true`, set `fallback_completed: true` only after obtaining complete reliable fallback call content or documenting a reasonable source-specific search, list `missing_materials` in `gaps`, and set `recheck_after` when a near-term official replay/transcript update is likely.
- Missing call material may therefore produce a provisional call interpretation through the documented fallback path, but official reported figures still require official/regulatory evidence when available, and unresolved numerical conflicts remain blocking.
