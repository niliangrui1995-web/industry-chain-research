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
- Process company work units with a maximum parallelism of 6. If more than 6 companies are enabled, queued companies must be started as earlier slots finish.
- When Chrome/Grok browser control is available, use a separate Chrome/Grok tab or window per company and run only that company's query terms in that tab.
- If a separate browser tab/window is unavailable, keep the company as a separate checklist item and continue non-browser checks.
- The daily report or `run_status.md` should include a per-company completion table so missing companies are visible before the run ends.

## Source Rules

- Official announcements, exchange filings, company IR pages, and CNINFO are formal evidence.
- Dragon-tiger list and block-trade records are trading-event evidence.
- Grok/X is a discovery layer only. If Grok fails, the run continues and records the failure.
- Social or model-surfaced messages enter the observation pool unless independently verified.

## Chat Summary Contract

At the end of each automation run, include a short chat summary with:

1. Updated file paths.
2. Companies with material changes today.
3. Announcement, dragon-tiger list, and block-trade highlights.
4. Grok/X 24-hour observation-pool items, if available.
5. Changes versus the existing baseline.
6. The next 3-5 tracking questions.
7. Per-company completion status and any miss-risk notes.
8. Batch/queue status when more than 6 companies are enabled.
