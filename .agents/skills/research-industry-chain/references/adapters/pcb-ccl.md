# PCB / CCL Adapter

## Trigger

Use when `target_industry` includes AI PCB, PCB, CCL, copper clad laminate, electronic cloth, glass fiber, copper foil, resin, ABF, HDI, high-speed board, high-layer board, or substrate-like PCB.

Chinese keywords: AI PCB, 覆铜板, CCL, 电子布, 玻纤布, 玻璃纤维布, 铜箔, PCB 铜箔, 树脂, 高频高速板, HDI, ABF, IC 载板, 类载板.

## Node Map

| layer | node | exact definition | do not confuse with |
|---|---|---|---|
| upstream | resin system | Epoxy, PPO/PPE, PTFE/hydrocarbon, BT, cyanate ester and related formula systems used in CCL | generic chemical resin without verified CCL formula or customer qualification |
| upstream | electronic glass fiber/cloth | Glass yarn and woven electronic cloth used as CCL reinforcement | building glass fiber or generic textile glass cloth |
| upstream | copper foil | Electrodeposited or rolled copper foil used in CCL and PCB | lithium battery copper foil without PCB-grade evidence |
| midstream | CCL | Copper clad laminate, including high-speed/high-frequency and low-CTE materials | finished PCB board |
| midstream | PCB fabrication | Board-level drilling, plating, lamination, imaging, etching, testing, and HDI/high-layer processing | ABF substrate or IC substrate unless exact product evidence exists |
| midstream | ABF / IC substrate | Package substrate with semiconductor packaging function and different customer/process system | board-level AI server PCB |
| downstream | AI server / switch board | GPU baseboard, accelerator board, switch/router board, backplane, high-speed interconnect board | consumer electronics PCB demand |

## BOM / Value Nodes

| product | key node | value share logic | evidence priority |
|---|---|---|---|
| AI server board | high-layer PCB, high-speed CCL, copper foil, electronic cloth, resin | Value rises with layer count, signal integrity, low-loss material, yield, and testing difficulty | customer board specs, material certification, company filings, teardown with method |
| high-speed switch/router board | low-loss CCL, high-layer PCB, copper foil roughness control | Higher speed and lower loss raise material and process requirements | switch platform specs, CCL grade disclosure, vendor qualification evidence |
| advanced package / substrate | ABF substrate, BT substrate, substrate equipment/materials | Different chain from board-level PCB; value is tied to package substrate capacity and yield | substrate revenue disclosure, package customer evidence, prospectus/filing |

## Bottleneck Signals

| node | shortage signal | lead-time signal | capacity rigidity | invalidation |
|---|---|---|---|---|
| high-speed CCL | price increase, allocation, customer qualification bottleneck | longer material procurement cycle or tight qualified supply | formula know-how, qualification cycle, upstream material constraints | multiple vendors pass qualification and ASP spreads normalize |
| electronic cloth/glass yarn | price rise, low-inventory channel checks, tight high-end cloth supply | delayed cloth or yarn delivery | furnace/yarn ramp, weave capacity, high-end certification | new capacity releases faster than demand or low-end cloth is misread as high-end supply |
| PCB fabrication | order backlog, high utilization, high-end board allocation | longer fabrication and testing cycle | drilling/plating/yield/high-layer process, customer audit | capacity expansion reaches yield and customers qualify new vendors |
| ABF / IC substrate | substrate allocation or package bottleneck evidence | substrate lead time longer than board-level PCB | yield, equipment, customer qualification, packaging ecosystem | demand shifts away from package substrate bottleneck or leading customers second-source rapidly |

## Company Mapping Rules

| node | true beneficiary evidence | weak/concept evidence |
|---|---|---|
| CCL / resin / cloth / copper foil | exact product grade, customer qualification, segment revenue, margin change, capacity plan, named AI/server/networking use | "AI PCB material" wording without grade, customer, or revenue materiality |
| PCB fabrication | high-layer/high-speed board product, AI server or switch customer proof, utilization or backlog, yield/process disclosure | generic PCB capacity or consumer electronics exposure |
| ABF / IC substrate | substrate product generation, customer certification, capacity/yield disclosure, package-chain revenue | confusing board-level PCB with package substrate |

## Watch Indicators

- price: CCL, electronic cloth, copper foil, resin, high-end PCB ASP or surcharge.
- lead time: high-speed CCL procurement, high-layer board fabrication, substrate qualification.
- capex: new CCL lines, electronic cloth/yarn capacity, PCB high-layer expansion, substrate capacity.
- customer certification: AI server, switch/router, accelerator, package customer qualification.
- inventory: downstream server/networking inventory and upstream material inventory.

## Common Confusions

- Board-level PCB is not ABF substrate.
- Battery copper foil demand does not prove PCB copper foil tightness.
- Low-end electronic cloth capacity does not solve high-end low-loss CCL bottlenecks.
- A concept-board stock is not a beneficiary without exact product exposure and revenue materiality.
