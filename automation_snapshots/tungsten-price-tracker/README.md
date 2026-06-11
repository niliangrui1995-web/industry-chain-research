# Tungsten Price Tracker

This folder is the durable data store for the tungsten-price tracking automation.

## Files

- `price_history.csv`: append-only historical price table.
- `daily_reports/`: generated daily summaries.

## Tracking Scope

Core daily indicators:

- 65% black tungsten concentrate
- 55% black tungsten concentrate
- 65% white tungsten concentrate
- 55% white tungsten concentrate
- domestic APT
- domestic tungsten powder
- domestic tungsten carbide powder
- tungsten scrap indicators when available
- Europe APT / ferro-tungsten when available

Preferred source order:

1. SMM public tungsten price pages.
2. CTIA / Chinatungsten market daily notes.
3. Zhangyuan Tungsten, Xianglu Tungsten, Ganzhou Tungsten Association long-order or forecast prices.
4. Reputable secondary reposts only when the original source is not publicly readable.

## Automation Rule

Each run should collect only the current day's publicly available prices, append verified rows to
`price_history.csv`, then compare them with the previous observations in this file and write a
reader-facing summary under `daily_reports/`.
