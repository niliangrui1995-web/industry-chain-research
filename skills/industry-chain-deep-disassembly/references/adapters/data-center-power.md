# Data Center Power Adapter

## Trigger

Use when `target_industry` includes data-center power, AI datacenter electricity, grid interconnect, UPS, transformer, switchgear, busway, power distribution, PDU, power module, backup power, or North America datacenter power bottleneck.

Chinese keywords: 数据中心电力, AI 数据中心供电, 电网接入, UPS, 变压器, 开关柜, 断路器, 母线槽, 配电, PDU, 电源模块, 北美电力瓶颈.

## Node Map

| layer | node | exact definition | do not confuse with |
|---|---|---|---|
| upstream | electrical steel, copper, insulation, semiconductors | Key materials/components for transformers, switchgear, UPS, power modules | broad commodity exposure without power-equipment linkage |
| upstream | power semiconductors / capacitors | Components in UPS, power conversion, power supplies, and control systems | generic consumer power components |
| midstream | transformer | Utility, substation, pad-mounted, dry-type, or distribution transformer for grid/datacenter power | server PSU |
| midstream | switchgear / breaker | Medium/low-voltage electrical protection and distribution equipment | IT network switch |
| midstream | UPS / power conversion | Backup and power-conditioning system for datacenter loads | diesel generator or battery cell alone |
| midstream | busway / PDU / rack power | Facility and rack-level distribution path | server motherboard power rail |
| downstream | datacenter project | Utility interconnect, substation, facility power chain, rack deployment | cloud software revenue |

## BOM / Value Nodes

| product | key node | value share logic | evidence priority |
|---|---|---|---|
| AI datacenter facility | transformer, switchgear, UPS, busway, generator, cooling power interface | Value rises with MW scale, redundancy, lead time, grid constraints, and safety certification | project filing, utility interconnect, equipment order, vendor backlog |
| rack power | PDU, busway tap-off, power shelf/module, cable, monitoring | Value rises with rack power density and deployment volume | rack design, server platform spec, customer deployment evidence |
| grid interconnect | substation transformer, breaker, switchgear, engineering service | Bottleneck often comes from utility interconnect and equipment lead time | utility queue, project disclosure, grid equipment backlog |

## Bottleneck Signals

| node | shortage signal | lead-time signal | capacity rigidity | invalidation |
|---|---|---|---|---|
| transformer | backlog, allocation, project delays, utility procurement tightness | transformer lead time exceeds datacenter build schedule | factory capacity, testing, materials, certification, utility qualification | new capacity ramps and utility procurement normalizes |
| switchgear / breaker | electrical equipment backlog | medium-voltage gear delays facility energization | safety certification, manufacturing capacity, project engineering | second sourcing and standardization shorten delivery |
| UPS / power conversion | order growth, power-density redesign | UPS delivery tied to facility deployment | reliability, certification, battery/power component supply | datacenter builds slow or alternate architectures reduce UPS scope |
| busway / rack power | rack-density upgrade demand | site delivery and installation schedule tightens | project customization, installation, safety testing | rack design standardizes and suppliers scale quickly |

## Company Mapping Rules

| node | true beneficiary evidence | weak/concept evidence |
|---|---|---|
| transformer / switchgear | datacenter or utility customer orders, backlog, capacity expansion, margin improvement, geographic fit | generic grid-equipment label without AI datacenter linkage |
| UPS / power conversion | datacenter-grade UPS product, named customers, order visibility, service capability | consumer/industrial UPS exposure only |
| rack power / busway | high-density rack or facility project evidence, customer qualification, delivery capacity | low-voltage electrical products without datacenter proof |
| materials/components | direct qualification into transformer/UPS/switchgear chain, revenue materiality | broad copper/electrical material exposure only |

## Watch Indicators

- price: transformer, switchgear, UPS, busway, copper/electrical steel spreads.
- lead time: utility transformer, medium-voltage switchgear, UPS, grid interconnect.
- capex: transformer factory, switchgear line, UPS/power conversion capacity.
- customer certification: utility, CSP, datacenter EPC, electrical integrator.
- inventory: equipment backlog, project delays, utility queue, CSP capex timing.

## Common Confusions

- IT switch and electrical switchgear are unrelated nodes.
- Server PSU/rack power and facility UPS are different layers.
- Grid bottleneck may benefit equipment vendors but can also delay downstream datacenter revenue.
- Broad power-equipment demand is not enough; datacenter-grade order proof matters.
