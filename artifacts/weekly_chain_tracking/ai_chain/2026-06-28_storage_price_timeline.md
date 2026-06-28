# 2026-06-28 存储涨价时间线最小沉淀

核验日期：2026-06-28（北京时间）

本文只沉淀 2026 年存储涨价的产品线时间线、供需驱动和证据分层。沿用 `state.md` 现有主链节点 `HBM / server DRAM / LPDRAM / NAND / enterprise SSD / AI server parts supply`，不新增 A 股订单、客户、收入或利润兑现判断。

## 方法边界

- 研究写法采用事实、可信二手、推演分离的做法；官方财报、prepared remarks、公司业绩会和官方 transcript 标为 `confirmed_official`。
- TrendForce / DRAMeXchange 等行业数据只标为 `credible_secondary`，用于补足行业价格幅度、产品线拆分和横向验证。
- 产品线之间的传导只写到产业链机制，不外推为 A 股公司订单、ASP、毛利率或利润兑现。
- HBM test / probe / Cube Prober 仍按原状态留在 `watch_to_soft / soft_bottleneck_candidate`，不因 Micron 主链紧张自动升为 `hard_bottleneck`。

## 结论先行

1. 这轮不是单一“存储涨价”，而是四条曲线叠加：HBM 的 2026 年价量锁定最早，server DRAM 与 NAND 在 2026Q1-Q3 连续重定价，enterprise SSD 从 AI inference / Agent 存储层爆发中强化，nearline HDD 从 2025H2 已经开始短缺并向 QLC/eSSD 传导。
2. Micron 官方口径已经把 DRAM/NAND tight 从 2026 年内问题升级为 `beyond calendar 2027` 的结构性供需紧张；但这只能作为 memory/storage 主链证据，不能直接写成任何 A 股材料、设备、测试或封装公司的订单兑现。
3. LPDDR/LPDRAM 的涨价证据最需要克制：Micron 官方确认 LP DRAM/SOCAMM 在数据中心扩展，TrendForce 指向 NVIDIA Vera Rubin 平台 LPDRAM allocation 不足，但“LPDDR 合约价涨幅”仍主要来自二手行业数据和推演，不是 Micron 单独披露的产品线价格表。
4. HDD 与 enterprise SSD 有明确传导：nearline HDD 冷数据供给紧张 -> CSP 把部分 warm/capacity tier 转向 QLC/eSSD -> 拉动 NAND 与 enterprise SSD 合约价；但 HDD 并不是 Micron 官方口径覆盖的产品线，需要用 Seagate/WD 等硬盘厂官方资料与 TrendForce 分层处理。

## 产品线时间线

| 产品线 | 启动时点 | 关键供需/价格证据 | 核心驱动 | 与其他产品线的传导 | 证据等级与结论 |
|---|---|---|---|---|---|
| HBM | 2025-12 已进入 2026 全年价量协议；2026Q1 HBM4 开始随客户平台 ramp；2026Q3 HBM4 收入已实质放量 | Micron Q1 FY26 称 2026 年 HBM supply 的价格和数量协议已完成；Q2 称 HBM4 12-high 已开始量产出货并面向 NVIDIA Vera Rubin；Q3 称 HBM4 12-high ramp 快于 HBM3E，HBM4 收入已超过 10 亿美元，Singapore advanced packaging 预计 2027H1 贡献 HBM packaging capacity | AI GPU/ASIC 对高带宽、低功耗、封装集成的刚性需求；HBM 新世代带来更高 trade ratio 和更复杂的 base die / stack / packaging / test | HBM 挤占 DRAM 晶圆、先进制程和 cleanroom，Micron 官方明确 HBM 对 non-HBM supply 继续施压；传导到 server DRAM/LPDRAM allocation，但不直接证明 test/probe 或 A 股订单 | `confirmed_official`：HBM 是主链 hard 证据；`inference`：测试/探针/材料受益仍需单独订单、交期和收入证据 |
| server DRAM | 2025-12 起明显重定价；2026Q1-Q3 连续上行 | Micron Q1 DRAM 价格环比约 +20%；Q2 DRAM 价格环比 mid-60s；Q3 DRAM 价格环比 low-60s。Q3 还称客户为了在极紧 allocation 下最大化 server units，降低平均 server DRAM content 增速 | AI server 与传统 server 同时扩张；HBM trade ratio 挤压非 HBM DRAM；客户提前锁量和 SCA 提高需求可见度 | server DRAM 与 HBM 同属 DRAM wafer / node / cleanroom 竞争；也会挤压 PC/mobile DRAM 和部分 LPDDR 供给 | `confirmed_official`：server DRAM 是 2026 年主涨价曲线之一；仍不能直接映射为国内 DRAM 周边公司业绩兑现 |
| LPDDR / LPDRAM | 2025-12 已进入数据中心 LP DRAM/SOCAMM 验证；2026Q2 后 LPDRAM allocation 线索显著增强 | Micron Q1 披露 192GB LP SOCAMM2 sample；Q2 披露 256GB LP SOCAMM2 sample、LPDDR5X 进入 personal AI workstation 并高量出货；DRAMeXchange/TrendForce 2026-06-10 称 NVIDIA Vera Rubin Superchip 因 LPDRAM allocation 不足调整 SOCAMM 配置，初步计划只能满足约 60% 需求 | AI inference 对低功耗、高密度 memory pool 的需求；数据中心 LPDRAM 与手机/PC LPDDR 共享先进节点和封装/模组资源 | 与 server DRAM 共享先进 DRAM 产能；与手机高端 LPDDR 形成 allocation 竞争。传导方向是“AI server LPDRAM 紧张强化 LPDDR 供给约束”，不是所有移动 LPDDR 自动涨价 | `confirmed_official + credible_secondary`：数据中心 LPDRAM 紧张可以沉淀；具体 LPDDR 合约价涨幅仍是二手/推演 |
| NAND | 2025-12 开始价格修复；2026Q1-Q3 加速重定价 | Micron Q1 NAND 价格环比 mid-teens；Q2 NAND 价格环比 high-70s；Q3 NAND 价格环比 mid-80s。TrendForce 2026-01-05 预计 1Q26 NAND Flash 价格环比 +33%-38% | enterprise SSD、capacity SSD 与 AI context memory storage 拉动；NAND 厂商纪律性控产；部分 cleanroom 从 NAND 转向 DRAM 进一步约束 NAND bit supply | 由 eSSD 需求直接拉动，也受 DRAM/HBM 优先级影响。HDD 紧张会把部分存储层级需求推向 QLC/eSSD，间接拉动 NAND | `confirmed_official` 支撑 NAND 上行；`credible_secondary` 补充行业价格幅度；不等于消费级 NAND 全面同幅度兑现 |
| enterprise SSD | 2025H2 因 nearline HDD 紧张和 AI storage tier 启动；2026Q1 合约价大幅上行；2026Q3 Micron 官方收入放量确认 | TrendForce 2026-06-11 称 1Q26 enterprise SSD revenue 环比 +86.1% 至 184.6 亿美元，合约价约 +80%；Micron Q3 FY26 称 data center SSD revenue 超过 50 亿美元且环比翻倍以上 | AI Agent / inference 形成 vector database、KV cache offload、warm/capacity tier 需求；CSP 采购强，供应商库存处历史低位；QLC SSD 承接部分 HDD 缺口 | eSSD 是 NAND 价格的最直接需求牵引；同时被 HDD 短缺推高；也与服务器整机交付的 memory/storage BOM 约束互相强化 | `confirmed_official + credible_secondary`：eSSD 已可列入 hard 主链；但具体客户 LTA、订单价格仍需各厂商财报和客户侧验证 |
| HDD / nearline HDD | 2025H2 已启动短缺；2026Q2 官方确认产能长期锁定 | TrendForce 2025-09-15 称 inference AI 数据量导致 nearline HDD 严重短缺，QLC SSD 2026 年有爆发机会；Seagate Q3 FY26 官方 transcript 称 nearline 接近 90% exabyte shipments，capacity almost fully allocated through CY2027，并与 hyperscale 客户推进 through FY2027 的 build-to-order contracts，包含 configuration and pricing；同时 data center revenue per TB 同比 mid-single-digit 增长 | AI inference 冷数据、历史数据、备份和长期保存需求上升；nearline HDD 单位成本最低但扩产节奏慢，客户更重视可靠供给 | HDD 短缺把一部分 warm/capacity tier 推向 QLC/eSSD，从而向 NAND/eSSD 传导；但 eSSD 不是 HDD 的即时完全替代，成本和用途不同 | `confirmed_official + credible_secondary`：HDD 供给锁定和价格纪律成立；“全行业涨价幅度”仍需 Seagate/WD/Toshiba 多方官方交叉 |

## 相互传导关系

| 传导链条 | 可以沉淀的结论 | 不能越界写成什么 |
|---|---|---|
| HBM -> non-HBM DRAM / server DRAM | HBM 新世代 trade ratio、先进节点与 cleanroom 需求抬高，压缩 server DRAM 与普通 DRAM 可用供给 | 不能写成 HBM 测试设备、探针卡、材料或 A 股公司已获得订单 |
| server DRAM / LPDRAM allocation -> PC/mobile DRAM / LPDDR | 数据中心优先级提高，会压缩消费电子和低优先级 DRAM/LPDDR allocation，并支撑更高价格纪律 | 不能把数据中心 LPDRAM 紧张直接写成手机 LPDDR 全面涨价幅度，除非有产品线合约价证据 |
| HDD shortage -> enterprise SSD -> NAND | nearline HDD 供给不足推高 QLC/eSSD 采购，eSSD 又反向强化 NAND 合约价和供应商 capacity allocation | 不能把 HDD 短缺等同于所有 SSD 企业订单，也不能把 NAND 涨价直接写成国内 NAND 侧翼公司业绩兑现 |
| SCA / LTA / build-to-order contracts -> 价格周期钝化 | Micron SCA 和 Seagate build-to-order 把部分市场从现货价格波动转向中长期价量锁定，提高 2026-2027 可见度 | 不能把价量锁定自动解释为客户永续补库；若库存恢复或需求放缓，价格斜率仍会回落 |

## 官方口径、二手资料、推演分层

### confirmed_official

- Micron Q1/Q2/Q3 FY26 prepared remarks：DRAM 和 NAND 价格连续上行；HBM 2026 年供应已完成价量协议；Q3 披露 DRAM/NAND demand 继续显著超过 supply，并预计 tight beyond calendar 2027。
- Micron Q3 FY26 prepared remarks：data center SSD revenue 超过 50 亿美元且环比翻倍以上；16 个 strategic customer agreements 增强价量可见度；FQ4 gross margin outlook 反映涨价斜率开始有意义放缓。
- Seagate Q3 FY26 earnings transcript：nearline capacity 接近全部分配至 CY2027，through FY2027 的 build-to-order contracts 包含具体配置和定价，data center revenue per TB 同比提升。

### credible_secondary

- TrendForce 2026-01-05：预计 1Q26 conventional DRAM contract price +55%-60%，server DRAM >60%，NAND Flash +33%-38%，client SSD >40%。
- TrendForce 2026-06-11：1Q26 enterprise SSD 合约价约 +80%，行业 revenue 环比 +86.1%，AI Agent / CSP 采购驱动供需失衡。
- DRAMeXchange / TrendForce 2026-06-10：NVIDIA Vera Rubin SOCAMM 配置调整反映 LPDRAM allocation 不足，初步供应计划只能覆盖约 60% 需求。
- TrendForce 2025-09-15：nearline HDD 严重短缺，推动 QLC SSD 2026 年进入更高增速窗口。

### inference_only

- HBM test/probe/Cube Prober、A 股材料/测试/设备、国内 NOR/SLC/NAND 侧翼公司，只能作为后续验证方向，升级阈值必须是内存厂或公司侧订单、交期、客户、收入、毛利率、产能或 RPO/预付款证据。
- LPDDR 的“价格曲线”当前只能从 LPDRAM allocation、server LP module、行业报价和产品 mix 推导，不能当成 Micron 官方单列价格披露。
- HDD 价格幅度仍需要 WD/Toshiba/Seagate 多方官方口径交叉；目前可确认的是供给锁定、build-to-order pricing discipline 和 revenue/TB 改善。

## 后续跟踪指标

1. Micron FQ4 FY26：DRAM/NAND 价格斜率是否继续放缓；SCA customer deposits、fixed/floor/ceiling price exposure、RPO 是否继续增加。
2. Samsung / SK hynix / Kioxia / SanDisk：是否确认 eSSD/NAND/LPDRAM/HBM 的 LTA、库存、capacity allocation 与 contract price。
3. Server OEM/ODM：Dell/HPE/SMCI/ODM 是否继续披露 DRAM/NAND/eSSD/parts supply constraints、purchase commitments、backlog 转收入受限。
4. LPDRAM：NVIDIA Vera Rubin / SOCAMM2 后续配置、供应覆盖率、内存厂 allocation 和实际交付节奏。
5. HDD：Seagate/WD/Toshiba nearline exabyte allocation、build-to-order pricing、revenue/TB、HAMR ramp 和 2028 供应计划。
6. A 股映射：只有公司公告、IR、客户/订单、分产品收入、毛利率或交期证据闭环后，才能从“主链涨价背景”升级到公司卡片。

## 主要来源

- Micron Q1 FY26 prepared remarks: https://investors.micron.com/static-files/088991c5-a249-4f66-a0a6-258d9b66f3f9
- Micron Q2 FY26 prepared remarks: https://investors.micron.com/static-files/e089f8c0-065d-47b8-9d02-bfa863cdb357
- Micron Q3 FY26 prepared remarks: https://investors.micron.com/static-files/631b1a32-5537-46ae-8f40-82e42fc79dfe
- Micron Q3 FY26 results press release: https://investors.micron.com/news-releases/news-release-details/micron-technology-inc-reports-record-results-third-quarter
- TrendForce 2026-01-05 memory price: https://www.trendforce.com/presscenter/news/20260105-12860.html
- TrendForce 2026-06-11 enterprise SSD: https://www.trendforce.com/presscenter/news/20260611-13092.html
- DRAMeXchange / TrendForce 2026-06-10 LPDRAM: https://www.dramexchange.com/WeeklyResearch/Post/2/12731.html?type=News
- TrendForce 2025-09-15 nearline HDD / QLC SSD: https://www.trendforce.com/presscenter/news/20250915-12714.html
- Seagate Q3 FY26 transcript: https://s24.q4cdn.com/101481333/files/doc_financials/2026/q3/CORRECTED-TRANSCRIPT_-Seagate-Technology-Holdings-Plc-STX-US-Q3-2026-Earnings-Call-28-April-2026-5_00-PM-ET.pdf
