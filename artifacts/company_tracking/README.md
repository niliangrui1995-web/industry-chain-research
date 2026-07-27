# A-share company tracking

This directory stores the recurring company-tracking outputs.

## Inputs

- Watchlist: `watchlists/a_share_company_watchlist.xlsx`
- Enabled companies: rows where `enabled` is `Y`
- First-run companies: rows where `baseline_status` is `pending`, `refresh_needed`, or blank

## Output Contract

Each run should keep these files current:

- `YYYY-MM-DD.md`: daily cross-company summary.
- `<ticker>/baseline.md`: first full company baseline.
- `<ticker>/state.md`: rolling company state.
- `<ticker>/events.jsonl`: append-only event ledger.
- `run_status.md`: run status, failures, and source availability.

## Per-Company Isolation

- Each enabled company must be processed as a separate work unit.
- The controller processes companies in watchlist order without spawning company-level sub-agents or browser workers.
- The daily report or `run_status.md` must include a per-company completion table in the exact enabled-watchlist order so missing, duplicate, or extra companies are visible before the run ends.

## End-to-End Run Validation

Before changing the workbook or appending events, create a snapshot:

```powershell
python scripts/validate_company_tracking_run.py snapshot --watchlist watchlists/a_share_company_watchlist.xlsx --events-root artifacts/company_tracking --output artifacts/company_tracking/.run_validation_snapshot.tmp
```

After all writes and before reporting success, validate Excel round-trip/structure, append-only JSONL records and the completion table:

```powershell
python scripts/validate_company_tracking_run.py validate --snapshot artifacts/company_tracking/.run_validation_snapshot.tmp --watchlist watchlists/a_share_company_watchlist.xlsx --events-root artifacts/company_tracking --run-status artifacts/company_tracking/run_status.md
```

Only `status=passed` may complete the run. A failure must be reported as `blocked/postwrite_validation_failed` with the validator error.

## Source Rules

- Official announcements, exchange filings, company IR pages, and CNINFO are formal evidence.
- Dragon-tiger list and block-trade records are trading-event evidence.
- Grok/X is a discovery layer only. If Grok fails, the run continues and records the failure.
- Social or model-surfaced messages enter the observation pool unless independently verified.

## Chat Summary Contract

The chat summary stays short: companies with material changes, announcement/dragon-tiger/block-trade highlights, changes versus baseline, thesis-gate result, main attribution and the next 3-5 questions. File paths, per-company completion status and queue details stay in the report or `run_status.md` unless they affect the user's next decision.
