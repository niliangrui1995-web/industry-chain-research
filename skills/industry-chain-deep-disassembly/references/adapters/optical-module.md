# Optical Module Adapter

## Trigger

Use when `target_industry` includes optical module, datacenter optics, EML, DSP, silicon photonics, InP, CPO, OCS, fiber connector, optical engine, TOSA/ROSA, coherent optics, or AI cluster networking.

Chinese keywords: 光模块, 光通信, EML, DSP, 硅光, InP, CPO, OCS, 光纤连接器, 光引擎, TOSA, ROSA, AI 集群网络.

## Node Map

| layer | node | exact definition | do not confuse with |
|---|---|---|---|
| upstream | EML / laser chip | High-speed optical transmitter chip, often InP-based for datacenter modules | finished optical module |
| upstream | DSP / driver / TIA | Electrical signal-processing and analog chips used in high-speed modules | Ethernet switch ASIC |
| upstream | silicon photonics / InP PIC | Integrated optical chip or photonic platform | generic optical component without integration |
| upstream | FAU, lens, isolator, connector | Passive optical components and packaging materials | telecom-only low-speed components unless datacenter evidence exists |
| midstream | optical engine / TOSA / ROSA | Subassembly integrating optical and electrical components | pluggable module vendor |
| midstream | optical module | 400G/800G/1.6T and related pluggable or co-packaged module | fiber cable or switch system |
| downstream | AI cluster network | Switches, NICs, optical interconnect, CSP datacenter deployment | consumer broadband optical access |

## BOM / Value Nodes

| product | key node | value share logic | evidence priority |
|---|---|---|---|
| 800G / 1.6T module | EML or silicon photonics, DSP, driver/TIA, optical engine, packaging, module assembly | Value shifts with speed generation, yield, power, component shortage, and customer qualification | module BOM teardown, vendor product disclosure, customer qualification |
| CPO / optical engine | optical engine, silicon photonics/InP, advanced packaging, thermal/power management | Value may migrate from pluggable module to optical engine and package integration | switch platform roadmap, official product/customer evidence |
| OCS / optical switching | optical switching engine, MEMS/LCoS or other switching tech, control system | Different chain from transceiver module; verify exact product and customer | deployment case, CSP/network vendor disclosure |

## Bottleneck Signals

| node | shortage signal | lead-time signal | capacity rigidity | invalidation |
|---|---|---|---|---|
| EML / laser chip | allocation, price rise, high-speed chip bottleneck | chip delivery delays constrain module ramp | epitaxy, wafer fab, yield, reliability qualification | merchant supply expands or silicon photonics substitutes faster than expected |
| DSP | limited supplier base, node migration, power constraint | chip availability delays module delivery | advanced process, SerDes/IP, customer qualification | alternate DSP suppliers qualify or integration changes BOM |
| optical engine / packaging | yield or active alignment bottleneck | module ramp takes longer than demand | precision packaging, thermal, testing, automation | packaging automation and second sourcing improve yield |
| module assembly | backlog and capacity utilization | order-to-delivery cycle extends | customer certification, yield, scale manufacturing | downstream order cuts or customer mix shifts |

## Company Mapping Rules

| node | true beneficiary evidence | weak/concept evidence |
|---|---|---|
| laser / optical chip | high-speed product generation, internal or merchant chip evidence, module adoption, capacity/yield proof | claiming "optical chip" without speed, customer, or revenue proof |
| DSP / electronic chips | product in datacenter module generation, customer design-in, financial exposure | generic communication chip exposure |
| module vendor | 800G/1.6T shipments, CSP qualification, order backlog, margin trend, capacity ramp | only telecom module history or concept-board label |
| passive components | datacenter high-speed component evidence, customer qualification, value share | low-speed telecom/broadband component exposure only |

## Watch Indicators

- price: high-speed module ASP, EML/laser chip price, DSP cost, optical engine margin.
- lead time: laser chip, DSP, module delivery, customer qualification.
- capex: optical chip, packaging automation, module assembly, testing capacity.
- customer certification: CSP, switch vendor, module generation, speed roadmap.
- inventory: module inventory, customer order visibility, switch/NIC deployment.

## Common Confusions

- 200G-per-wavelength EML is not the same as a full 800G/1.6T module.
- Optical module company strength does not prove merchant bare-chip competitiveness.
- Telecom optical demand and AI datacenter optical demand have different cycles.
- CPO/OCS are not interchangeable with pluggable transceiver modules.
