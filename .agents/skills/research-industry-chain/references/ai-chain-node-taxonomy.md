# AI Chain Node Taxonomy

Use this reference when `research-industry-chain` handles AI data-center, AI hardware, semiconductor-chain, bottleneck, node comparison, or listed-company mapping tasks.

This is a local node map, not an evidence source. It helps choose the exact industry-chain node before collecting demand, supply, pricing, customer, filing, or market evidence.

## Source Files

| File | Role |
|---|---|
| `docs/ai_chain_disassembly/nodes_mindmap_level_01_to_05_cleaned_2026-05-31.md` | Human-readable cleaned Level 1-5 mind map. Use it to scan the full tree and explain the chain path. |
| `docs/ai_chain_disassembly/nodes_mindmap_level_01_to_05_cleaned_2026-05-31.xlsx` | Structured workbook for filtering and node lookup. Use this for precise counts, paths, priorities, and P5 summaries. |

The original full tree remains in `docs/ai_chain_disassembly/nodes_mindmap_level_01_to_05_2026-05-31.md`. Prefer the cleaned version for normal investment research unless the user asks for full-detail expansion.

## Workbook Sheets

| Sheet | Use |
|---|---|
| `统计说明` | Check provenance, counts, and usage notes. |
| `思维导图树` | Read the full tree in display order with indentation and complete path. |
| `节点清单` | Filter by `主链名称`, `层级`, `优先级状态`, `节点类型`, and `完整路径`. This is the primary structured lookup sheet. |
| `P5摘要` | Search material, equipment, component, and process hints under Level 4 nodes. Use as search-keyword support only. |

Known cleaned workbook shape as of 2026-05-31:

| Item | Count |
|---|---:|
| Level 1 nodes | 7 |
| Level 2 nodes | 62 |
| Level 3 nodes | 320 |
| Level 4 P0 nodes | 283 |
| P5 summary rows | 205 |

## Granularity Rules

| Level | How to use it |
|---|---|
| Level 1 | Chain-family orientation, such as GPU/ASIC, high-speed network, power, liquid cooling, storage, or rack structure. |
| Level 2 | Major segment framing and companion-skill routing. |
| Level 3 | Normal segment research unit for demand transmission and same-chain comparison. |
| Level 4 P0 | Preferred unit for bottleneck diagnosis, value-share checks, technical moat checks, and listed-company exposure mapping. |
| P5 summary | Material, equipment, component, process, and search-keyword hints. Do not promote P5 items into final conclusions without independent A/B evidence. |

Do not treat `P0`, `P1`, or `P2` as an investment ranking by itself. These labels help scope the node tree. The investment conclusion still depends on downstream demand, qualified-supply gaps, value share, global leader validation, listed-company hard evidence, valuation, and trading context.

## Workflow Hook

1. If the user starts from a stock or company and the product/node is unknown, first identify the listed entity, official business lines, disclosed products, customer applications, and evidence grade. Do not choose a taxonomy node from the stock name alone.
2. Search candidate product, material, equipment, component, process, or application terms in `节点清单`.
3. Keep multiple candidate paths when the exposure is ambiguous. Mark each as `confirmed`, `partial_clue`, `rumor_only`, or `not_found`.
4. Record the path at the narrowest useful level, usually Level 3 or Level 4 P0.
5. Translate the path into `terminal demand -> downstream application/customer -> selected node -> company product/service -> revenue/ASP/margin path`.
6. Use `P5摘要` only to expand source-search keywords.
7. Collect A/B evidence for demand, qualified supply, pricing, customer validation, and company exposure.
8. Map listed companies only after the exact node and pass-through path are explicit.
9. Keep final rankings separated into fundamental quality, earnings elasticity, and trading elasticity.

## Evidence Boundary

The taxonomy can locate adjacent nodes and search terms. It cannot prove current demand acceleration, qualified-supply shortage, price or margin improvement, company customer/order/capacity/yield exposure, or investment quality. C-grade sources and model output can guide search but cannot prove a main bottleneck or main stock pick.

When this reference materially shapes the answer, include:

```text
taxonomy path: AI 数据中心 / 智算中心 > [Level 1] > [Level 2] > [Level 3] > [Level 4 P0 if available]
```

If the path is unavailable, state the gap and continue with the normal industry-chain workflow.
