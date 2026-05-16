# Bias Mitigation Techniques

Use this checklist before trusting an automated or rubric-based ranking.

## Common Biases

| Bias | Failure Mode | Mitigation |
|---|---|---|
| Position bias | First item wins too often | Swap order and compare consistency |
| Length bias | Longer explanation scores higher | Penalize irrelevant detail |
| Recency bias | Latest news overwhelms durable facts | Separate strict-window catalyst from structural quality |
| Price-action bias | Strong K-line treated as proof | Keep trading elasticity separate from beneficiary evidence |
| Concept-label bias | Theme membership treated as exposure | Require product/customer/revenue evidence |
| Authority-tone bias | Confident claim beats sourced claim | Require citations and source grade |
| Availability bias | Easy-to-find sources dominate | Track unresolved official-source gaps |

## Investment-Specific Guardrails

- Do not let market heat raise fundamental quality.
- Do not let a good company automatically rank first on trading elasticity.
- Do not promote C-grade rumor above watch status without A/B confirmation.
- Do not compare companies across different value-chain nodes without stating the node difference.
- Do not turn missing data into zero.

## Stability Checks

Before finalizing a ranking, ask:

1. Would the ranking change if company order were reversed?
2. Would it change if the newest rumor were removed?
3. Would it change if only official and filing evidence were allowed?
4. Which score is most sensitive to missing market cap, float, turnover, or margin data?
5. Which conclusion is observation-only rather than main-candidate quality?

If the answer changes materially, report the instability instead of forcing a clean rank.
