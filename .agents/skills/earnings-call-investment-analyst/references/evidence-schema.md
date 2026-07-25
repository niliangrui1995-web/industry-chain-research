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
      "company_metric": "annualized_single_quarter_deducted_attributable_net_profit",
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

For A-share comparisons, annualize the latest single-quarter deducted attributable profit by multiplying it by four, compare it with the pre-event full-year attributable-profit consensus, use `comparison_basis: annualized_quarterly_deducted_vs_fy_attributable_consensus`, and keep `formal_surprise_status: N/A`. A derived quarter must use same-company official cumulative disclosures on the same accounting basis and include `derivation_formula`. Preserve the raw quarterly values and `annualization_factor: 4`; do not store only the annualized result.

## Valuation Object

Use this object when PE(TTM) is requested. It records the user's single-quarter annualized convention rather than a standard trailing-four-quarter multiple.

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
- Every user-defined PE(TTM) should record total market cap, `market_cap_as_of`, source quarter, annualized deducted-profit denominator, `valuation_basis`, and source references; return `N/A` when the denominator is non-positive.
- Third-party-hosted original call audio must not be listed as a company-hosted or official-event-hosted source.
- When a reputable full transcript and original call audio are both available from fallback providers, use the full transcript as the primary working source and record audio only as targeted verification evidence unless full-audio ASR was explicitly requested.
- The final analysis should not cite `media_or_analyst` as the sole source for reported results.
- Missing official company materials must create a `gaps` entry.
- A script returning no usable asset, 401/403, stale data, or a parser miss must create a `script_runs` entry if the script was run, and must not be treated as completion of fallback search.
- If official transcript, official replay, official audio/video, and official complete captions are missing while the call analysis uses third-party transcript or third-party-hosted original audio, set `provisional: true`, set `fallback_completed: true` only after obtaining complete reliable fallback call content or documenting a reasonable source-specific search, list `missing_materials` in `gaps`, and set `recheck_after` when a near-term official replay/transcript update is likely.
