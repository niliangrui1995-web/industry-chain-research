---
name: stock-fundamental-moat-triad
description: Use for future-oriented individual-stock or peer-company fundamental research when the user wants to judge whether a company has future business highlights, inflection points, earnings upside, product/customer breakthroughs, downstream demand transmission, value-chain migration, international peer catch-up potential, and customer-certification milestones. Trigger on 个股基本面, 未来亮点, 未来空间, 拐点, 成长性, 业绩弹性, 下游需求, 上下游, 需求传导, 价值链分析, 国际同行, 同行对标, 波特五力, 客户认证壁垒, 客户导入, AVL/BOM, 产业链位置, true beneficiary, moat, competitive structure, supplier status, or company comparison. This skill puts the future thesis first; downstream demand, value-chain, peer, Porter, and certification checks are supporting tools for judging whether the future can be monetized.
---

# Stock Fundamental Moat Triad

## Purpose

Use this skill as a future-oriented company research framework inside `产业链投研`: first answer what could become materially different in the next 6-24 months, then use downstream demand transmission, value-chain position, international peers, competitive structure, and customer certification only as tools to judge whether that future can be monetized.

For individual-stock research, never analyze the company in isolation. Before the integrated verdict, build the path:

`upstream inputs/equipment -> company product/node -> downstream product/system -> end customer -> terminal demand driver -> revenue/margin pass-through`

This skill does not replace source collection, financial data, valuation, or trading analysis. It feeds `stock-evaluator`, `advanced-evaluation`, and market-data skills after the core business exposure is clear.

International peer benchmarking is a mandatory future-check, not an optional note inside Porter rivalry. Its main purpose is to judge whether the target company can catch up, substitute, localize, or lose share in the future; do not let peer benchmarking turn the report into a static history comparison.

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

Use `N/A` rather than inventing data. Label value-share, TAM, or BOM-cost ranges as research estimates unless they come from a public teardown or company filing. Past and current facts are inputs for probability, milestones, and invalidation risk; they are not the center of the answer when the user asks about the future.

## Future-First Principle

Do not reduce the analysis to "what is proven today." The main output is a forward-looking judgment: whether the company has a credible future highlight that can change revenue, margins, valuation narrative, or industry position.

Lead every report with the future answer:

- Does the company have a future highlight: `strong`, `medium`, `weak`, or `not visible`?
- What is the single most important future variable?
- How can that variable become revenue, margin, profit, or valuation re-rating?
- What evidence would confirm, delay, or kill the thesis in the next 1-2 reports?

Separate supporting evidence into two layers:

- `current evidence verdict`: what is already proven by filings, customers, product data, revenue, or public certification evidence.
- `future highlight rating`: what could improve in 6-24 months, why it could matter, and which observable milestones would upgrade or kill the thesis.

A company with weak current proof can still be an `early optionality` case. Do not reject it only because current revenue is small; reject or downgrade it when the future route is vague, the node has little value capture, the peer gap has no catch-up path, or there is no trackable customer/product milestone.

For the future highlight layer, explicitly test:

- demand inflection: new downstream demand, product generation change, AI/server/auto/robot/energy transition, policy localization, or capacity-cycle shift;
- downstream demand pass-through: whether end-customer capex, traffic, deployment, replacement, or policy demand actually converts into volume, ASP, margin, or share gain for the company's exact product node;
- product upgrade: higher ASP, harder specs, route migration, package/material/process change, or move from commodity to qualified node;
- customer-entry trajectory: sample -> validation -> reliability test -> AVL/BOM -> pilot -> mass production;
- margin translation: product mix, yield, capacity utilization, depreciation absorption, price discipline, or operating leverage;
- bottleneck/profit-pool migration: whether the value node may move toward or away from the company product;
- catalyst timeline: what must be seen in the next 1-2 reports, investor records, product pages, orders, or peer disclosures.

When the user asks about the future, spend most of the answer on future variables, downstream demand, probability, milestones, and earnings translation. Keep current and past facts concise and use them only to explain why the future thesis is credible, early, or weak.

## Workflow

### 1. Define The Object

State the exact listed entity, ticker, main products, relevant segment, and downstream application. If the product is only concept-adjacent, say so before continuing.

Minimum identity check:

- listed company and ticker;
- specific product or service under discussion;
- downstream product/system where it may be used;
- whether revenue exposure is direct, indirect, option-like, or unproven;
- source timestamp and evidence grade.

### 2. Future Highlight And Inflection Thesis

Before any static analysis, write the future thesis in one tight paragraph:

`future demand/change -> company product/node -> expected business effect -> required proof -> risk that invalidates it`

Then classify the future highlight:

- `clear future highlight`: credible future route, meaningful value capture, visible customer/product milestones, and at least partial source support.
- `early optionality`: plausible route and meaningful upside, but current proof is mostly product/application/certification clue.
- `watch only`: interesting direction, but value capture, peer gap, customer path, or financial translation is too unclear.
- `low future relevance`: no credible path from future demand to company earnings.

Minimum table:

```text
| future driver | company product/node | business effect | probability | time window | required proof | invalidation risk |
```

### 3. Value-Chain Analysis

Map from end demand back to the company product:

`terminal demand -> downstream product -> subsystem/BOM node -> component/process/material -> company product -> customer/channel`

For every company report, include a downstream demand table before judging whether the company is good:

```text
| downstream application | end customer/buyer | demand driver | current evidence | pass-through to company | timing | risk |
```

For each node, answer:

- What exact role does the company product play?
- Is it a core value node, bottleneck node, qualified-supply node, or low-value commodity node?
- Which downstream product creates revenue pull?
- Which downstream buyer or capex cycle creates that pull?
- How does the pull convert into company volume, ASP, mix, margin, or share gain?
- What is the likely value capture: high, medium, low, or N/A?
- Which evidence proves the mapping?

Do not stop at an industry label or a company profile. A company can be in the right theme but the wrong node, or in the right node with too little downstream demand pass-through to move earnings.

### 3A. Core Product/Service Demand And Price Trend Mainline

When the target company's earnings depend on a core product, core service, business line, SKU, product mix, price, ASP, ARPU, take rate, fee rate, spread, unit economics, or capacity utilization, add a two-line verification before the integrated verdict:

1. Downstream demand mainline:
   `terminal demand -> downstream product/system/customer -> core product/service demand -> company offering -> volume/ASP/ARPU/mix/margin`
2. Core product price and unit-economics mainline:
   `market price/rate -> company realized ASP/ARPU/take rate/fee/spread -> input/delivery/funding cost -> unit spread/gross margin -> sustainability`

This is mandatory whenever price, ASP, ARPU, fee rate, take rate, spread, utilization, product mix, or service mix is central to the thesis. For non-product businesses, translate "price" into the relevant monetization metric: ARPU, subscription price, take rate, fee rate, commission rate, interest spread, occupancy rate, utilization rate, yield, renewal price, or unit revenue.

Minimum output:

```text
| core product/service | downstream application/customer | end buyer/demand driver | same-chain validation | company proof | pass-through | timing | reversal risk |
| reported price/unit metric and volume | external price/rate signal | input/delivery/funding cost | mix effect | unit spread/margin | supply-demand or competition reason | sustainability verdict | reversal indicator |
```

Use these verdict labels for the price, mix, or unit-economics thesis:

- `structural_mix_upgrade`: high-end or special products are becoming a larger revenue/profit share.
- `qualified_supply_shortage`: demand exceeds qualified supply, yield, certification, or usable capacity.
- `demand_led_pricing`: real demand allows higher price, ARPU, take rate, fee rate, spread, or utilization.
- `commodity_cycle`: broad product prices are recovering, but durability depends on capacity and inventory.
- `cost_push`: realized price mainly follows input-cost inflation; margin durability is weaker.
- `utilization_or_operating_leverage`: earnings improve mainly because fixed costs are spread over higher volume or usage.
- `inventory_pull_forward`: downstream stocking or allocation behavior may reverse.
- `competitive_price_pressure`: competition, customer bargaining power, or regulation is compressing price or unit economics.
- `unclear`: evidence is insufficient; keep the stock as watch or event-only.

Do not treat company-reported ASP, ARPU, take rate, fee rate, spread, or utilization alone as proof. Separate common versus premium offerings, external market price/rate versus realized company metric, input-cost inflation versus true spread expansion, and end demand versus pull-forward.

### 4. International Peer Benchmarking

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

### 5. Porter Five Forces

Apply the five forces at the exact value-chain node, not at the broad industry level.

- `Buyer power`: customer concentration, qualification difficulty, price pressure, dual-source requirements, switching cost, and whether customers control specs.
- `Supplier power`: critical upstream inputs, equipment/process constraints, substitution options, cost pass-through, and foreign dependency.
- `Rivalry`: use the peer benchmark above to judge global and domestic peers, product spec parity, price competition, capacity expansion, yield/reliability gaps, and margin trend.
- `Substitutes`: technology route changes, integration by customers, alternative architectures, or adjacent components that may replace the node.
- `New entrants`: capex, process know-how, patents, reliability data, certification cycle, yield learning curve, and channel access.

Conclude with pricing power and margin durability: `strong`, `moderate`, `weak`, or `not proven`.

### 6. Customer Certification Barrier Model

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

### 7. Integrated Verdict

Combine the models into a future-first judgment, then attach the evidence state:

`future conclusion`:

- `strong future highlight`: material driver, meaningful earnings path, credible customer/product/catch-up milestones, and observable confirmation path.
- `medium future highlight`: real future driver, but value capture, peer gap, customer entry, or financial translation still needs proof.
- `weak future highlight`: plausible story, but earnings path is small, delayed, low-value, or mostly dependent on external narrative.
- `not visible`: no credible path from future demand to company earnings.

`current evidence verdict`:

- `core beneficiary`: exact high-value or bottleneck node, near-parity or leading peer benchmark, favorable forces, and A/B customer proof.
- `qualified supplier with upside`: real node and improving certification evidence, but international peer gap, value share, or customer proof is still incomplete.
- `option-like candidate`: product direction is plausible, but certification/revenue proof is C-level or weaker.
- `concept-adjacent`: theme exposure exists, but the value-chain node or customer proof is weak.
- `reject`: no credible evidence for the claimed exposure.

`future highlight rating`:

- `clear future highlight`: material future driver, meaningful node, credible catch-up/customer path, and observable next signals.
- `early optionality`: future route is plausible and potentially meaningful, but proof is still early.
- `watch only`: worth monitoring, but the path from product to earnings is not yet strong enough.
- `low future relevance`: future story is too vague, low-value, or structurally disadvantaged.

Do not assign `core beneficiary` if same-node international peers are materially ahead on key specs, customer design-in, or manufacturing scale and the target company's catch-up path is not evidenced. If the company has a future path but lacks proof, say `current evidence: option-like` and `future highlight: early optionality` rather than forcing one blended label.

Do not turn this verdict into a buy/sell call unless valuation, current market data, and trading context have also been checked.

## Output Pattern

For a single company:

```text
结论先行：
- 未来结论：strong / medium / weak / not visible
- 核心未来变量：
- 对收入/利润/估值的传导路径：
- 未来 1-2 个报告期需要验证的信号：
- 当前证据定性：core beneficiary / qualified supplier with upside / option-like candidate / concept-adjacent / reject
- 未来亮点等级：clear future highlight / early optionality / watch only / low future relevance
- 关键依据：
- 最大证据缺口：
- 下一步跟踪指标：

一、未来亮点与拐点假设
| future driver | company product/node | business effect | probability | time window | required proof | invalidation risk |

二、价值链位置
| downstream product | BOM/node | company product | role | value capture | evidence grade | source |

三、国际同行基准对标
| peer | country/listing | same node? | product/spec benchmark | customer/BOM proof | manufacturing moat | commercial scale | gap vs target | evidence grade |

四、波特五力
| force | verdict | evidence | implication |

五、客户认证壁垒
| stage | evidence grade | current proof | missing proof | next signal |

六、综合判断
| dimension | verdict | reason | risk |
```

For peer comparison, use the scorecard in `references/scorecard-template.md` when the user asks for ranking or a structured table.

## Common Mistakes

- Skipping downstream demand and price/unit-economics bridges when the thesis depends on a core product, service, ASP, ARPU, take rate, fee rate, spread, utilization, or mix.
- Treating a company-reported ASP, ARPU, take-rate, fee-rate, spread, or utilization increase as durable pricing power without checking external price/rate signals, unit costs, mix effect, and unit spread.
- Mixing common/low-end offerings with premium/high-value offerings when judging demand, price, or margin durability.
- Do not infer BOM entry from a product launch alone.
- Do not let current proof alone answer the whole question; always separate current evidence from future highlight potential.
- Do not make the report mainly about past and present when the user asks about the future; past and current evidence should support the future thesis, not replace it.
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
- `allstock-data` / `finance` / `alpha-vantage` / iFinD MCPs: current market and valuation data.
