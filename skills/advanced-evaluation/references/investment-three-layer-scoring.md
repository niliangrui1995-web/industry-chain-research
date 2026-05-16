# Investment Three-Layer Scoring

Use this project-local template when comparing stocks, segments, or A-share candidates in `产业链投研`.

The three scores answer different questions:

1. Fundamental quality: is this a high-quality business or value-chain position?
2. Earnings elasticity: will the relevant catalyst plausibly convert into revenue, margin, or profit?
3. Trading elasticity: can the stock react strongly in the market if the thesis is recognized?

Do not merge these into one score unless the user explicitly asks for a composite.

## Scorecard

| Candidate | Fundamental Quality 0-5 | Earnings Elasticity 0-5 | Trading Elasticity 0-5 | Evidence Strength | Source Gap Impact | Verdict |
|---|---:|---:|---:|---|---|---|

## Fundamental Quality

Score 0-5 using:

- exact industry-chain position;
- product value share;
- moat, process, yield, reliability, certification, or customer switching cost;
- customer quality and concentration;
- margin and cash-flow structure;
- balance-sheet and governance risk;
- official disclosure quality.

High score requires durable business evidence, not only market attention.

## Earnings Elasticity

Score 0-5 using:

- revenue exposure to the selected segment;
- order, backlog, capacity, ASP, utilization, mix, or yield evidence;
- gross-margin and operating leverage;
- latest report or guidance direction;
- whether the catalyst affects this company materially, not only the sector.

High score requires a visible conversion path from industry change to company financials.

## Trading Elasticity

Score 0-5 using:

- market cap and float market cap where available;
- liquidity, turnover, volatility, and trend;
- catalyst density and expectation gap;
- valuation and crowding risk;
- upcoming announcements, earnings, IR, policy, or customer events.

Trading elasticity can only be ranked after real exposure is established.

## Evidence Strength

Use:

- `A`: official announcement, filing, exchange disclosure, annual/interim/quarterly report, company IR, prospectus, official customer/supplier source.
- `B`: reputable financial/industry media, named-source industry database, broker note summary with cited source.
- `C`: social post, Grok/X, forum, model output, unsourced concept-board label.
- `N/A`: no usable evidence.

C-grade evidence can set a watch item; it cannot by itself create a main recommendation.

## Verdict Labels

- `main_candidate`: strong enough for focused follow-up.
- `watch`: plausible but needs more evidence or better timing.
- `event_trade_only`: trading catalyst exists but business evidence is weak.
- `observation_only`: route is interesting, listed exposure is not yet strong.
- `reject`: concept heat, weak exposure, weak evidence, or high risk dominates.

## Conflict Handling

If rankings conflict, state it directly:

- high fundamental quality + low trading elasticity = core long-term candidate, not highest short-term弹性;
- low fundamental quality + high trading elasticity = event-only, not hard-strength company;
- high earnings elasticity + weak evidence = watch until official or customer evidence improves;
- strong sector + weak company exposure = do not reverse-map the stock story.
