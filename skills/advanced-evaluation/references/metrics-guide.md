# Metric Selection Guide

Choose metrics based on the evaluation shape.

## General Evaluation

| Task | Preferred Metric | Notes |
|---|---|---|
| Pass/fail gate | precision, recall, F1 | Use when false positives and false negatives matter |
| 1-5 ordinal rating | weighted agreement, Spearman correlation | Needs level descriptions |
| Pairwise preference | agreement rate, swapped-order consistency | Best for subjective comparison |
| Multi-criterion scorecard | per-criterion score + confidence | Avoid hiding weak dimensions in a total score |
| Source-quality audit | source grade distribution | Track A/B/C evidence separately |

## Investment Research Metrics

Use scores only after evidence is collected. A score without source grade is not actionable.

| Dimension | Typical Measures |
|---|---|
| fundamental quality | moat, customer quality, margin structure, cash conversion, balance sheet, disclosure quality |
| earnings elasticity | revenue exposure, order conversion, ASP/mix, utilization, gross-margin leverage, operating leverage |
| trading elasticity | float/market cap, turnover, volatility, 20/60-day trend, catalyst density, expectation gap, crowding |
| evidence strength | official disclosure, filing, IR, customer/supplier proof, reputable media, C-grade lead |
| source-gap impact | whether missing data could reverse the conclusion |

## Scale Guidance

Use 0-5 when each level is described:

| Score | Meaning |
|---:|---|
| 0 | no evidence or negative evidence |
| 1 | weak / indirect evidence |
| 2 | plausible but incomplete |
| 3 | adequate evidence |
| 4 | strong evidence |
| 5 | very strong, source-backed, hard to replace |

Use `N/A` when a value cannot be verified. Do not convert `N/A` to zero unless zero is a confirmed real value.
