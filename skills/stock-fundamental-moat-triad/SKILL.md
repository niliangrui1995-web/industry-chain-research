---
name: stock-fundamental-moat-triad
description: Use for individual-stock or peer-company fundamental research when the user wants to combine value-chain analysis, international peer benchmarking, Porter Five Forces, and customer-certification barrier analysis. Trigger on 个股基本面, 价值链分析, 国际同行, 同行对标, 波特五力, 客户认证壁垒, 客户导入, AVL/BOM, 产业链位置, true beneficiary, moat, competitive structure, supplier status, or company comparison. This skill judges whether a listed company has real value-chain exposure, same-node global competitiveness, durable competitive position, and verifiable customer-entry evidence before valuation or trading-elasticity analysis.
---

# Stock Fundamental Moat Triad

## Purpose

Use this skill as a company-level fundamental filter inside `产业链投研`: first prove where the company sits in the value chain, then judge the competitive structure, then test whether customer certification creates a real entry barrier.

This skill does not replace source collection, financial data, valuation, or trading analysis. It feeds `stock-evaluator`, `advanced-evaluation`, and market-data skills after the core business exposure is clear.

International peer benchmarking is a mandatory gate, not an optional note inside Porter rivalry. Do not enter the integrated verdict until the target company has been benchmarked against same-node global leaders or until the peer evidence is explicitly marked `N/A`.

## Default Route

Use this route unless the user specifies otherwise:

`industry-research-router -> search/source or industry skill -> stock-fundamental-moat-triad -> stock-evaluator -> advanced-evaluation when ranking/scoring is needed`

For current price, market cap, PE/PB, latest filings, orders, policy, or news, verify with source and market-data skills before making current claims.

## Evidence Discipline

Separate evidence into these buckets:

- `confirmed`: named customer, official announcement, contract, filing, audited segment data, or explicit revenue/order disclosure.
- `partial clue`: official product/application statement, unnamed top customer, certification language, batch supply language, or credible primary-adjacent evidence.
- `undisclosed`: no public proof for exact BOM position, customer, share, ASP, quantity, or revenue.
- `rumor only`: social/media/model claims without hard source; use only as a lead.

Use `N/A` rather than inventing data. Label value-share, TAM, or BOM-cost ranges as research estimates unless they come from a public teardown or company filing.

## Workflow

### 1. Define The Object

State the exact listed entity, ticker, main products, relevant segment, and downstream application. If the product is only concept-adjacent, say so before continuing.

Minimum identity check:

- listed company and ticker;
- specific product or service under discussion;
- downstream product/system where it may be used;
- whether revenue exposure is direct, indirect, option-like, or unproven;
- source timestamp and evidence grade.

### 2. Value-Chain Analysis

Map from end demand back to the company product:

`terminal demand -> downstream product -> subsystem/BOM node -> component/process/material -> company product -> customer/channel`

For each node, answer:

- What exact role does the company product play?
- Is it a core value node, bottleneck node, qualified-supply node, or low-value commodity node?
- Which downstream product creates revenue pull?
- What is the likely value capture: high, medium, low, or N/A?
- Which evidence proves the mapping?

Do not stop at an industry label. A company can be in the right theme but the wrong node, or in the right node with too little value share to move earnings.

### 3. International Peer Benchmarking

Complete this step before Porter Five Forces and before any integrated verdict.

First classify peers by node:

- `same-node international peer`: global company selling the same component, material, equipment, process service, subsystem, or BOM node.
- `adjacent international company`: platform owner, downstream customer, upstream supplier, or adjacent-route company; useful for context but not a direct peer.
- `domestic peer`: local listed or unlisted company at the same or adjacent node.
- `not comparable`: company from another value-chain layer; exclude from technical and customer-status comparison.

For same-node international peers, benchmark:

- product family and exact use case;
- public technical parameters: performance, reliability, yield, power, size/package, operating range, materials, process route, or other node-specific specs;
- customer and BOM status: named customer, AVL/BOM proof, platform design-in, shipment, or mass-production evidence;
- manufacturing moat: equipment, process know-how, patents, quality system, scale, yield learning, and supply-chain control;
- commercial strength: market share, capacity, ASP/margin direction, delivery ability, and ability to survive dual-source price pressure;
- route risk: whether the peer uses a technology route that could replace, integrate, or commoditize the target company's product;
- gap versus the target company: `ahead`, `near parity`, `catching up`, `unclear`, or `not comparable`;
- evidence grade and source boundary.

Use public specs and hard customer evidence first. Do not claim parity with international leaders from one headline parameter. If current peer specs, customer status, or market share may have changed, verify them through official product pages, filings, reputable data sources, or source-collection skills before making a current claim.

Minimum table:

```text
| peer | country/listing | same node? | product/spec benchmark | customer/BOM proof | manufacturing moat | commercial scale | gap vs target | evidence grade |
```

If no same-node international peer can be identified, say so explicitly and explain whether the node is too niche, too opaque, or the comparison requires further source work.

### 4. Porter Five Forces

Apply the five forces at the exact value-chain node, not at the broad industry level.

- `Buyer power`: customer concentration, qualification difficulty, price pressure, dual-source requirements, switching cost, and whether customers control specs.
- `Supplier power`: critical upstream inputs, equipment/process constraints, substitution options, cost pass-through, and foreign dependency.
- `Rivalry`: use the peer benchmark above to judge global and domestic peers, product spec parity, price competition, capacity expansion, yield/reliability gaps, and margin trend.
- `Substitutes`: technology route changes, integration by customers, alternative architectures, or adjacent components that may replace the node.
- `New entrants`: capex, process know-how, patents, reliability data, certification cycle, yield learning curve, and channel access.

Conclude with pricing power and margin durability: `strong`, `moderate`, `weak`, or `not proven`.

### 5. Customer Certification Barrier Model

Place the company on the customer-entry ladder:

1. product/spec announced;
2. samples delivered;
3. customer board/module/system validation;
4. reliability and lifecycle tests;
5. factory/process audit;
6. approved vendor list or BOM entry;
7. pilot/small-batch supply;
8. mass production and repeat orders;
9. sticky replacement or platform-wide design-in.

Evidence grading:

- `A`: named customer, AVL/BOM, contract/order, revenue contribution, or official mass-production disclosure.
- `B`: official batch-supply or certification language with unnamed customer or exact application.
- `C`: product release and target application only.
- `D`: industry rumor, investor Q&A ambiguity, or broker inference.
- `Reject`: no public evidence that connects the product to the claimed customer/product.

Analyze whether certification is a real moat:

- certification cycle length and failure cost;
- customer reluctance to switch suppliers;
- platform reuse across product generations;
- quality/reliability penalty if the component fails;
- whether dual sourcing caps supplier profit;
- whether the customer or upstream chip/platform owner controls specs.

### 6. Integrated Verdict

Combine the four models into one fundamental judgment:

- `core beneficiary`: exact high-value or bottleneck node, near-parity or leading peer benchmark, favorable forces, and A/B customer proof.
- `qualified supplier with upside`: real node and improving certification evidence, but international peer gap, value share, or customer proof is still incomplete.
- `option-like candidate`: product direction is plausible, but certification/revenue proof is C-level or weaker.
- `concept-adjacent`: theme exposure exists, but the value-chain node or customer proof is weak.
- `reject`: no credible evidence for the claimed exposure.

Do not assign `core beneficiary` if same-node international peers are materially ahead on key specs, customer design-in, or manufacturing scale and the target company's catch-up path is not evidenced.

Do not turn this verdict into a buy/sell call unless valuation, current market data, and trading context have also been checked.

## Output Pattern

For a single company:

```text
结论先行：
- 基本面定性：core beneficiary / qualified supplier with upside / option-like candidate / concept-adjacent / reject
- 关键依据：
- 最大证据缺口：
- 下一步跟踪指标：

一、价值链位置
| downstream product | BOM/node | company product | role | value capture | evidence grade | source |

二、国际同行基准对标
| peer | country/listing | same node? | product/spec benchmark | customer/BOM proof | manufacturing moat | commercial scale | gap vs target | evidence grade |

三、波特五力
| force | verdict | evidence | implication |

四、客户认证壁垒
| stage | evidence grade | current proof | missing proof | next signal |

五、综合判断
| dimension | verdict | reason | risk |
```

For peer comparison, use the scorecard in `references/scorecard-template.md` when the user asks for ranking or a structured table.

## Common Mistakes

- Do not infer BOM entry from a product launch alone.
- Do not flatten `certification`, `sample delivery`, `batch supply`, and `mass production` into one phrase.
- Do not compare companies before explaining whether they sit at the same value-chain node.
- Do not hide international peer benchmarking inside Porter rivalry; complete the same-node peer table before the integrated verdict.
- Do not claim technical parity from a single nominal parameter; benchmark the specs that actually matter for the node and the customer's failure cost.
- Do not use broad theme exposure as proof of revenue exposure.
- Do not hide customer names as "top customer" unless the source itself is unnamed; mark it as unnamed and lower the evidence grade.
- Do not present value-share ranges as audited facts without teardown or filing support.

## Companion Skills

- `industry-research-router`: required entry route and project discipline.
- `search-specialist`: official-source search, filings, announcements, and contradiction tracking.
- `research-summarizer`: annual reports, PDFs, IR records, and long-source digestion.
- `industry-chain-deep-disassembly`: BOM/value-node and bottleneck decomposition.
- `stock-evaluator`: valuation, financial quality, earnings elasticity, and final stock evaluation.
- `advanced-evaluation`: scoring consistency and peer-ranking bias control.
- `allstock-data` / `finance` / `stocks`: current market and valuation data.
