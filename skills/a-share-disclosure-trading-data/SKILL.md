---
name: a-share-disclosure-trading-data
description: Project-local A-share official disclosure and trading-event data workflow for CNINFO, exchange announcements, investor-relations records, dragon-tiger lists, block trades, announcement-date T/T+1 evening checks, evidence grading, and handoff into company tracking or stock research.
---

# A-Share Disclosure And Trading Data

Use this skill when a task needs A 股 official announcements, exchange disclosures, CNINFO records, investor-relations activity, dragon-tiger lists, block trades, or announcement-window reconciliation.

This is a data/evidence skill. It does not decide stock recommendations by itself. Hand verified facts to `industry-research-router`, `a-share-company-tracking`, `stock-evaluator`, or the relevant industry skill.

## Source Priority

Use sources in this order:

1. Company announcements on CNINFO, SSE, SZSE, BSE, STAR Market, ChiNext, or company IR pages.
2. Exchange trading-event pages: dragon-tiger list, block trades, abnormal trading notices, supervision letters.
3. Official investor-relations records and meeting minutes.
4. Reputable financial data vendors or media only as secondary confirmation.
5. Grok/X, forums, social posts, and model summaries only as leads.

Never treat social or model output as official disclosure.

## Announcement Window Rule

For Beijing-time A-share checks:

- Before 20:00: check today's announcement date and record `pending_evening_rescan` if the task is a daily closeout.
- At or after 20:00: check both `T` and `T+1` announcement dates.
- When the user flags a missed item: rescan affected companies by company name, ticker, and aliases across the suspected date window.

Reason: evening disclosures can be released after the market close but carry the next calendar announcement date.

Record the window explicitly:

`announcement_window_checked = T_only | T_and_T_plus_1 | pending_evening_rescan | failed_with_reason`

## Data Checks

For each company, normalize:

- ticker with suffix: `600xxx.SH`, `000xxx.SZ`, `688xxx.SH`, `8xxxxx.BJ`;
- company name and aliases;
- announcement date versus event date;
- source URL and source platform;
- source type: `official_announcement`, `exchange_disclosure`, `investor_relations`, `dragon_tiger`, `block_trade`, `reputable_media`, `open_web_fallback`, `grok_x_observation`;
- verification status: `confirmed_official`, `confirmed_secondary`, `observation_only`, `contradicted`, `source_gap`.

## Dragon-Tiger List

Use dragon-tiger data as a trading-event signal, not as proof of business quality.

Extract:

- date;
- reason for list inclusion;
- buy/sell seats and amounts when available;
- institution / quant / northbound / retail-style clues;
- whether the event is consistent with a known official catalyst;
- whether it changes trading elasticity, crowding, or risk.

## Block Trades

Use block-trade data as a trading-structure signal.

Extract:

- date;
- price, volume, amount, discount/premium where available;
- buyer and seller seats when available;
- whether it appears neutral, disposal pressure, institutional transfer, or signal-worthy accumulation;
- whether the amount is material relative to turnover or float.

Do not overinterpret small or flat-price block trades without supporting evidence.

## Output Contract

Return a compact evidence table:

| ticker | name | date | source_type | title/event | source | verification_status | impact_hint | next_check |
|---|---|---|---|---|---|---|---|---|

For company tracking, append material rows into `events.jsonl` and summarize only material changes in `state.md` and the daily report.

## Related Skills

- `a-share-company-tracking`: daily watchlist workflow and durable company files.
- `search-specialist`: query design and source conflict handling.
- `research-summarizer`: long announcement and IR-record digestion.
- `allstock-data`: quote, K-line, and market reaction context.
- `stock-evaluator`: company-level investment interpretation after verified facts are collected.
