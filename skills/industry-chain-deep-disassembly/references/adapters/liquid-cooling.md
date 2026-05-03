# Liquid Cooling Adapter

## Trigger

Use when `target_industry` includes AI server liquid cooling, cold plate, immersion cooling, CDU, coolant distribution, pump, valve, pipe, quick connector, leak reliability, thermal management, or datacenter cooling.

Chinese keywords: 液冷, AI 服务器液冷, 冷板, 浸没式液冷, CDU, 管路, 泵阀, 快接头, 漏液可靠性, 热管理, 数据中心冷却.

## Node Map

| layer | node | exact definition | do not confuse with |
|---|---|---|---|
| upstream | pumps, valves, sensors | Flow, pressure, temperature, and control components inside liquid-cooling loops | generic HVAC components without server reliability evidence |
| upstream | quick connectors and seals | Leak-resistant connectors, seals, manifolds, hoses, and fluid fittings | ordinary plumbing connectors |
| upstream | coolant and materials | Coolant, corrosion inhibitors, cold-plate metals, sealing materials | generic industrial fluids |
| midstream | cold plate | Plate attached to CPU/GPU/ASIC or memory module to remove heat | air-cooled heatsink |
| midstream | CDU | Coolant distribution unit connecting rack/row loop with facility water loop | chiller or building HVAC unit |
| midstream | rack/loop integration | Manifold, piping, monitoring, leak detection, control software, commissioning | one standalone component without system responsibility |
| downstream | AI server / datacenter | Server OEM, cloud customer, datacenter operator, facility integrator | generic industrial cooling market |

## BOM / Value Nodes

| product | key node | value share logic | evidence priority |
|---|---|---|---|
| direct-to-chip liquid cooling | cold plate, CDU, manifold, pump/valve, quick connector, monitoring | Value depends on heat load, reliability, leak prevention, serviceability, and customer certification | server platform specs, customer project disclosure, supplier certification |
| rack-scale cooling | CDU, rack manifold, piping, sensors, controls | Value rises with rack power density and deployment scale | datacenter deployment spec, tender/project evidence, integrator disclosure |
| immersion cooling | tank, dielectric fluid, heat exchanger, facility integration | Different adoption path; do not merge with cold-plate demand | customer pilot/commercial deployment evidence |

## Bottleneck Signals

| node | shortage signal | lead-time signal | capacity rigidity | invalidation |
|---|---|---|---|---|
| cold plate | qualification queue, GPU/ASIC platform tie-in, yield/reliability issue | longer sample-to-mass-production cycle | design fit, machining/brazing, leak reliability, customer platform validation | standardized designs reduce vendor lock-in |
| CDU | project backlog, datacenter deployment acceleration | delivery tied to rack/facility project cycle | control system, reliability, commissioning, service capability | facility-side delays or multiple mature suppliers remove tightness |
| quick connector/seal | leak incidents, strict reliability requirements | supplier qualification bottleneck | materials, tolerance, lifecycle testing, failure liability | connector becomes standardized commodity |
| pump/valve/sensor | high-reliability component constraints | component delivery extends system lead time | reliability testing and control integration | generic suppliers pass certification quickly |

## Company Mapping Rules

| node | true beneficiary evidence | weak/concept evidence |
|---|---|---|
| cold plate / CDU / system | named AI server/datacenter customer, certified platform, project/order disclosure, product revenue, margin improvement | thermal-management label without liquid-cooling revenue or customer evidence |
| connectors / pumps / valves | server-grade reliability evidence, qualification with liquid-cooling integrator, component value share | generic industrial component sales |
| integrator | rack/facility deployment capability, commissioning and service evidence, recurring customer projects | one-time pilot or non-AI datacenter reference only |

## Watch Indicators

- price: cold plate, CDU, connector, pump/valve ASP and gross margin.
- lead time: platform certification, CDU delivery, connector qualification, facility commissioning.
- capex: machining, brazing, assembly, testing, service network.
- customer certification: GPU/ASIC server platform, CSP datacenter, rack integrator.
- inventory: downstream server shipment, CSP capex timing, component inventory.

## Common Confusions

- A refrigeration/HVAC company is not automatically an AI liquid-cooling beneficiary.
- Cold-plate component capability is different from rack-level system integration.
- Pilot adoption is not the same as commercial-scale deployment.
- Leak reliability and service liability can matter more than nominal heat-transfer specs.
