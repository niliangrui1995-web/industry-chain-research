---
name: ht-local-market-data
description: >-
  Read and validate the user's manually updated local HT/TongdaXin market-data
  folder at C:\zd_huatai. Use after user-investment-framework when an investment task
  needs local A-share daily K-line data, HT/TongdaXin vipdoc files, T0002 block
  lists, hq_cache vendor tables, gpcw financial packages, or freshness checks
  for data updated after the market close. This is a market_data_vendor and
  secondary_trading_context skill only: it must not replace CNINFO, exchange
  filings, company IR, annual/quarterly reports, customer/supplier proof,
  TDX/iFinD current APIs, or official evidence. Do not read trading-account,
  password, order, or log details unless the user explicitly asks for that
  diagnostic.
---

# HT Local Market Data

Use this skill as the project-local bridge to `C:\zd_huatai`, the user's local 华泰/通达信 data folder. It is useful for fast, offline market context after the user has manually refreshed the client data, especially for A-share daily K-lines, local block pools, vendor classification tables, and quick freshness checks.

This skill is a data-source boundary, not an investment framework. Always start investment research from `user-investment-framework`, then load this skill only when local HT data adds specific market, candidate-pool, or freshness value.

## Tested Data Surface

The folder was inspected read-only on 2026-07-10 after the post-close update.

| Path | Data found | Tested status | Evidence label |
|---|---|---|---|
| `C:\zd_huatai\vipdoc\sh\lday`, `sz\lday`, `bj\lday` | TDX `.day` daily OHLCV files for Shanghai, Shenzhen, Beijing stocks and indexes | 9,389 files parsed, all record sizes valid; 9,358 latest records were `20260710` | `market_data_vendor` |
| `C:\zd_huatai\vipdoc\sh\minline`, `sz\minline`, `bj\minline` | TDX `.lc1` 1-minute K-line files | Directories exist but contain 0 `.lc1` files; do not use this root for minute data | unavailable |
| `C:\zd_huatai\vipdoc\cw` | `gpcw*.zip` financial packages and per-stock `gp*.dat` files | 147 nonzero zip files passed integrity checks; 7,399 per-stock `gp*.dat` files found | `market_data_vendor`, not official filings |
| `C:\zd_huatai\T0002\blocknew` | Local/custom TDX block pools and self-defined candidate lists | 4 `.blk` files found, 3 nonempty; parse as candidate/watchlist pools only | `secondary_trading_context` |
| `C:\zd_huatai\T0002\hq_cache` | Code tables, vendor industry/concept/chain tables, fund and HK metadata | 89 files found; core code, industry, concept, chain, fund, and HK metadata tables are present | `market_data_vendor` or `secondary_trading_context` |
| `C:\zd_huatai\T0002\cache`, `zst_cache`, `tmp` | Session/chart caches and temporary files | Not stable data contracts; inspect freshness only unless a specific format is re-tested | context only |
| `C:\zd_huatai\htlog`, `T0001`, `lct`, `funcs_jy`, `华泰证券网上交易委托系统` | Logs, software runtime, trading UI, templates, and possible account state | Do not read details by default; skip account/password/order/log content | out of scope unless explicitly requested |

## Workflow

1. Confirm the task needs local HT data.
   Use this skill for local daily K-line freshness, historical OHLCV, local block-pool membership, vendor concept/industry context, or a quick check that the user's afternoon manual update completed.

2. Run a narrow freshness check.
   Prefer `scripts/inspect_ht_data.py --root C:\zd_huatai --json` for a read-only inventory. The helper rejects roots missing the required directories, valid Shanghai/Shenzhen benchmark `.day` files, or a nonempty core `hq_cache` file, so an empty directory skeleton cannot silently produce an empty result. Compare latest parsed `.day` record dates with the expected trading date and mention whether the data is post-close, stale, partial, or unavailable.

3. Parse daily K-lines from `.day` only when needed.
   TDX `.day` records are 32 bytes:

   ```text
   <IIIIIfII
   date, open*100, high*100, low*100, close*100, amount(float), volume, reserved
   ```

   Use the market-prefixed filename as the ticker, for example `sh600000.day`, `sz300750.day`, `bj899050.day`.

4. Treat local minute K-lines as unavailable unless re-tested.
   `.lc1` records are structurally parseable as:

   ```text
   <HHfffffII
   packed_date, minute_of_day, open, high, low, close, amount, volume, reserved
   ```

   Decode `packed_date` as:

   ```text
   year = packed_date // 2048 + 2004
   month = (packed_date % 2048) // 100
   day = packed_date % 100
   ```

   The tested folder contains no `.lc1` files, so use TDX/iFinD/web APIs for current intraday or minute-level work.

5. Use local block files as candidate pools only.
   `T0002\blocknew\*.blk` lines usually store a market flag plus six-digit code:

   ```text
   0 + 300750 -> sz300750
   1 + 600000 -> sh600000
   2 + 920xxx -> bj920xxx
   ```

   These files can tell what the user or client software has grouped together, but they cannot prove industry exposure, customer orders, revenue materiality, or beneficiary status.

6. Use `vipdoc\cw` financial packages cautiously.
   They are vendor-transformed financial snapshots. Check zip integrity, file size, and reporting period before use. For any hard financial claim, retrieve the official filing, CNINFO/exchange announcement, annual report, quarterly report, or company IR source.

7. Preserve privacy and write safety.
   Do not open or summarize account directories, `.pass` files, trading委托 files, logs, order history, password caches, or broker UI runtime details unless the user explicitly asks for that diagnostic. Never write to `C:\zd_huatai` from this skill.

## Routing Boundary

Use this skill as an optional local market-data layer inside the project route:

```text
user-investment-framework -> task-specific research/source skills -> ht-local-market-data when local HT data is useful -> final evidence-tiered synthesis
```

Prefer this skill over web/API calls only when the local file is the requested source or when a post-close local daily snapshot is sufficient. Prefer TDX/iFinD/current web data when the task needs live intraday quotes, current valuation, limit-board details, fund flows, or fields not stored in the local files.

Never upgrade this skill's output above `market_data_vendor` or `secondary_trading_context`. It cannot replace official source collection, demand-chain proof, company filings, or the project's final fundamental-quality / earnings-elasticity / trading-elasticity ranking.

## Read-Only Helper

Run:

```bash
python skills/ht-local-market-data/scripts/inspect_ht_data.py --root C:\zd_huatai --json
```

Useful options:

```bash
python skills/ht-local-market-data/scripts/inspect_ht_data.py --root C:\zd_huatai --codes sh000001 sz000001 sh600000 sz300750 --json
python skills/ht-local-market-data/scripts/inspect_ht_data.py --root C:\zd_huatai --skip-block-samples --json
```

The helper avoids account/trading/log directories and returns compact JSON covering top-level inventory, `.day` freshness, `.lc1` availability, `gpcw` zip integrity, block-pool counts, and selected `hq_cache` files.
