# LLM-As-Judge Implementation Patterns

Use these patterns when an evaluation needs repeatability rather than a one-off opinion.

## Direct Scoring

Use direct scoring when each item can be judged independently.

Good fit:

- factual completeness;
- instruction following;
- source coverage;
- rubric compliance;
- evidence strength.

Required fields:

| Field | Purpose |
|---|---|
| `criterion` | What is being judged |
| `score_scale` | Numeric or categorical scale |
| `level_descriptions` | Concrete meaning for each level |
| `evidence_required` | What proof must be cited |
| `confidence` | Judge confidence and why |

Do not use a 1-10 scale without level descriptions. It creates false precision.

## Pairwise Comparison

Use pairwise comparison when the question is preference-like or relative.

Good fit:

- which summary is more useful;
- which company has stronger evidence;
- which candidate is more investable after the same evidence standard;
- which source is more authoritative.

Always run swapped-position checks when the comparison matters. If A beats B only in one order, mark the result as unstable.

## Rubric Design

For each criterion, define:

- what counts as strong evidence;
- what counts as weak evidence;
- what must be marked `N/A`;
- what evidence would reverse the score.

For investment work, never let a score hide evidence gaps. Carry `evidence_strength` and `source_gap_impact` next to the score.

## Output Shape

Use structured output:

| item | criterion | score | justification | evidence | confidence | source_gap |
|---|---|---:|---|---|---|---|

Keep justification concise and evidence-linked. Do not ask the judge for hidden chain-of-thought.
