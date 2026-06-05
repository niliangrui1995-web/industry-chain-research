# VR-NVL72 vs GB300/GB200 BOM 增量节点账本

日期：2026-06-05  
用途：把 Vera Rubin NVL72 相对 GB300/GB200 的物料增量，拆成可验证的产业链节点、A 股映射、剔除项和跟踪指标。  
结论属性：产业链研究备忘录，不构成买卖建议。

## 0. 结论先行

从上一代 GB300/GB200 到 VR-NVL72，最核心的变化不是 GPU/CPU 数量增加，而是在同样 72 GPU / 36 CPU 的 rack-scale 形态下，把 scale-up / scale-out 互联、板级复杂度、电源密度和液冷结构继续推高。

真正值得放进主线的增量：

| 层级 | 节点 | 增量判断 | A 股可映射性 | 当前结论 |
|---|---|---|---|---|
| 第一主线 | 高速 PCB / midplane / ConnectX PCB / switch PCB / UBB / 高阶 HDI | VR 拆解显示 PCB 价值量从约 3.51 万美元/柜升至约 11.67 万美元/柜，+233% | 高 | 主线最高 |
| 第一主线上游 | M8/M9 CCL / prepreg / Low Dk-Df 材料 | 由更高速信号、更高层数、更低损耗需求驱动 | 高 | soft bottleneck |
| 第一主线上游 | 高端电子布 / Low CTE / 低介电布 / 超低损耗布 | AI server 与高速 PCB 拉动，普通玻纤不能替代 | 中高 | soft bottleneck+ |
| 第一主线延伸 | PCB 级 HVLP/VLP/RTF 铜箔 | 224G/1.6T 与 M8/M9 对低粗糙度铜箔要求上升 | 中 | watch+，不得混同锂电铜箔 |
| 第二主线 | NVSwitch / CX9 / BF4 拉动的板级、ABF、MLCC、连接器 | 芯片数量和速率提升明确，但芯片本身由 NVIDIA 控制 | A 股间接映射 | 看 PCB/连接结构，不看泛芯片概念 |
| 第二主线 | 800VDC / HVDC / power shelf / busbar | 机架功耗密度提升，NVIDIA 800VDC 生态明确 | 中 | 需订单和收入验证 |
| 第二主线 | 液冷 / manifold / QD / 冷板 / CDU | GB300 已液冷，VR 是密度与架构升级，不是从 0 到 1 | 中 | 长期强，单柜增量不是最高 |
| 旁线强机会 | 800G/1.6T 光模块、EML/CW/InP、CPO/ELS | AI cluster scale-out 真实高景气，但不属于 VR 柜内 BOM 主增量 | 高 | 单独光通信主线，不混进 VR 单柜 BOM |
| 剔除/观察 | Retimer/AEC、BMC/MCU/ERoT、SSD、泛设备耗材 | 技术重要，但 A 股硬证据不足或价值量不清 | 低 | 不作为主线 |

一句话：A 股“高速互联弹性最高”，严格说不是买 NVIDIA 互联芯片，而是买高速互联把 PCB/CCL/电子布/高端铜箔/连接结构件的层数、材料等级、良率和客户认证难度推上去。

## 1. 关键来源与证据等级

| 来源 | 用途 | 证据等级 |
|---|---|---|
| NVIDIA Vera Rubin NVL72 官方规格页：https://www.nvidia.com/en-us/data-center/vera-rubin-nvl72/ | 72 Rubin GPU、36 Vera CPU、ConnectX-9、BlueField-4、NVLink 6、260 TB/s、HBM4/LPDDR5X 参数 | A |
| NVIDIA GB300 NVL72 Enterprise RA：https://docs.nvidia.com/enterprise-reference-architectures/nvl72-ai-factory/latest/components.html | GB300 compute tray、ConnectX-8、BlueField-3、4 E1.S、8 power shelves、142kW | A |
| NVIDIA GB200 NVL72 技术博客：https://developer.nvidia.com/blog/upgrading-multi-gpu-interconnectivity-with-the-third-generation-nvidia-nvswitch/ | GB200 18 compute nodes、9 NVLink switch trays、130 TB/s、copper cable cartridge、liquid cooling | A |
| NVIDIA Vera Rubin POD 技术博客：https://developer.nvidia.com/blog/?p=113993 | VR 18 compute trays、9 switch trays、PCB midplane、cable-free/hose-free/fanless 设计 | A |
| NVIDIA 800VDC 技术博客：https://developer.nvidia.com/blog/building-the-800-vdc-ecosystem-for-efficient-scalable-ai-factories/ | 800VDC 生态、1MW+ rack 方向、Delta/Flex/LiteOn/Megmeet/Vertiv/Eaton 等 | A |
| 本地用户文件 `vr-nvl72.md` | VR compute tray / switch tray / CX9 module / BMC-HMC-BF4 等细分 BOM | 用户给定资料，按待核验 A-/B+ 使用 |
| `docs/rubin_价值量拆解_逐页梳理_20260522.md` | Rubin rack BOM 价值量拆分，尤其 PCB/MLCC/ABF/电源/液冷增幅 | B，卖方测算/本地整理 |
| `artifacts/weekly_chain_tracking/ai_pcb/2026-05-31.md` | PCB/CCL/电子布/HVLP 铜箔当前堵点账本 | A/B 混合，本地已整理 |
| `artifacts/weekly_chain_tracking/optical_module/2026-05-31.md` | 光模块、EML/CW/InP、CPO/FAU 旁线判断 | A/B 混合，本地已整理 |

## 2. GB300/GB200 到 VR-NVL72 的物料变化

| 项目 | GB300/GB200 公开口径 | VR-NVL72 口径 | 增量结论 | 产业链含义 |
|---|---:|---:|---|---|
| GPU | 72 GPU | 72 Rubin GPU | 数量不变，单颗价值/功耗/封装/内存升级 | 不产生 A 股 GPU 数量弹性 |
| CPU | 36 Grace CPU | 36 Vera CPU | 数量不变，CPU 内存与 C2C 能力升级 | CPU memory 方向 A 股弱映射 |
| NVLink bandwidth | GB200/GB300 约 130 TB/s | VR 260 TB/s | 带宽约翻倍 | Switch tray、PCB、NVSwitch、ABF/MLCC、散热供电复杂度上升 |
| NVSwitch ASIC | GB300/GB200 常见口径为 9 trays × 2 = 18 | 用户 VR 文件为 9 trays × 4 = 36 | 芯片数量约 +100% | 芯片本身无 A 股映射；拉动 switch PCB、ABF、MLCC、供电和散热 |
| East/West NIC | GB300 每 tray 4 个 ConnectX-8，18 tray 合计 72 | 用户 VR 文件每 tray 4 个 CX9 module，每 module 2 个 CX9 ASIC，合计 72 module / 144 ASIC | ASIC 数量与速率均上升 | 直接拉动 ConnectX PCB、OSFP/CAGE、MLCC、ABF、测试与高速板材 |
| DPU | GB300 每 tray 1 个 BF3，约 18 | VR 每 tray 1 个 BF4，约 18 | 数量不变，代际升级 | 主要是 BF4 板、供电、互联升级，A 股弱直接映射 |
| Local storage | GB300 每 tray 4 E1.S + 1 M.2 | 用户 VR 文件显示 CX9 module 内 E1.S 及 boot E1.S | 可能增加，但 OEM 配置变量大 | SSD 不是主要投资主线 |
| PCB | 卖方测算约 35,100 美元/柜 | 约 116,730 美元/柜 | +233% | A 股最强直接映射 |
| MLCC | 约 1,530 美元/柜 | 约 4,320 美元/柜 | +182% | 百分比高，绝对值小，需看 AI server 客户与涨价 |
| ABF | 约 11,160 美元/柜 | 约 20,340 美元/柜 | +82% | 全球高壁垒，A 股直接映射弱 |
| Power | 约 57,600 美元/柜 | 约 76,000 美元/柜 | +32% | power shelf / busbar / HVDC 受益，订单证据最关键 |
| Cooling | 约 64,610 美元/柜，不含侧车 CDU | 约 72,080 美元/柜 | +12% | 不是最大单柜增量，但热密度长期拉动 |
| Optical module | GB300/VR 柜外 scale-out 都需要 | VR scale-out 继续增强，CPO/硅光方向更强 | 不是柜内 BOM 主增量 | 单独光通信主线 |

## 3. 节点级严筛

### 3.1 GPU / CPU / HBM / CPU memory

| 维度 | 判断 |
|---|---|
| 增量 | 数量不变，单颗 GPU、HBM4、CPU memory、NVLink-C2C 升级。 |
| 需求传导 | 下游 AI factory 对更高吞吐和更低 token cost 的需求，传导到 GPU/HBM/先进封装/内存。 |
| A 股映射 | 弱。GPU/HBM/CPU memory 核心供应链主要在 NVIDIA、HBM 厂、先进封装与海外内存体系。 |
| 结论 | 不作为 A 股主线。A 股里不要硬塞“HBM/存储概念”进 VR-NVL72，除非有具体封装、材料、设备、订单证据。 |

### 3.2 NVSwitch / NVLink switch tray

| 维度 | 判断 |
|---|---|
| 硬增量 | NVLink 带宽从 130 TB/s 到 260 TB/s；用户 VR 文件显示 switch tray 每 tray 4 颗 NVL6 NVSwitch，9 tray 共 36 颗。 |
| 直接供应商 | NVIDIA。 |
| A 股可受益处 | switch PCB、高速 CCL、ABF、MLCC、供电、散热和连接结构件。 |
| 剔除项 | A 股“交换机概念”不能等同 NVSwitch；IT 网络交换机、园区交换机和 NVLink switch tray 不是同一节点。 |
| 结论 | 技术增量强，但投资映射应落到 PCB/材料，不落到泛交换机。 |

### 3.3 ConnectX-9 / SuperNIC / CX9 module

| 维度 | 判断 |
|---|---|
| 硬增量 | GB300 每 tray 4 个 CX8；VR 文件显示每 tray 4 个 CX9 module、每 module 2 颗 CX9 ASIC，合计 144 颗 CX9 ASIC。 |
| 需求传导 | 每 GPU 1600G E/W bandwidth 推高 OSFP、CAGE、连接器、PCB、MLCC、ABF 与高速测试要求。 |
| A 股映射 | 胜宏、沪电、深南、生益电子等高速 PCB；鼎通/立讯等连接结构件需客户和订单证明。 |
| 剔除项 | A 股没有公开硬证据成为 CX9 ASIC 供应商；不要把 retimer、网通芯片、普通连接器都硬贴成 CX9。 |
| 结论 | 是高速互联弹性来源之一，但 A 股真正买点仍是板级和材料。 |

### 3.4 BlueField-4 DPU

| 维度 | 判断 |
|---|---|
| 增量 | 数量大概率 18 个/柜不变，代际由 BF3 到 BF4，带宽/安全/存储卸载升级。 |
| A 股映射 | 弱。可间接拉动 DPU module PCB、MLCC、ABF、供电。 |
| 剔除项 | 不要把国内 DPU、边缘计算、网络安全概念直接映射为 BF4 供应链。 |
| 结论 | 观察，不作为 A 股核心主线。 |

### 3.5 PCB / 高层板 / HDI / midplane

| 维度 | 判断 |
|---|---|
| 硬增量 | 本地拆解测算 PCB 价值量 +233%，新增 midplane PCB、BlueField PCB、ConnectX PCB，compute/switch board 价值同步提升。 |
| 需求传导 | NVLink/CX9 带宽提升 -> 更高速信号、更高层数、更低损耗材料、更严格阻抗/可靠性/测试 -> 高端 PCB ASP 与毛利弹性。 |
| 当前瓶颈状态 | 成品板厂需求强，但本地周度账本仍把“成品 AI PCB 高层板良率/测试/交付”列为 watch+，不是 hard bottleneck。 |
| 主线 A 股 | 胜宏科技、沪电股份、深南电路、生益电子。 |
| 公司差异 | 胜宏弹性强、AI PCB 和高阶 HDI 兑现明显；沪电高速交换机/数据通讯 PCB 质量稳；深南质量强但交易弹性可能弱；生益电子更纯 PCB 但需看客户和毛利兑现。 |
| 剔除项 | 普通 PCB、消费电子 PCB、低层板、没有 AI server/switch/UBB 证据的公司。 |

### 3.6 CCL / prepreg / M8-M9 低损耗材料

| 维度 | 判断 |
|---|---|
| 硬增量 | VR 计算板、交换板、midplane、ConnectX board 对低损耗、高可靠材料需求显著上升。 |
| 当前瓶颈状态 | 本地周度账本为 soft_bottleneck，证据包括涨价、lead time、allocation 线索和高端材料偏紧。 |
| A 股映射 | 生益科技最稳；南亚新材、华正新材可观察，但需要 M7/M8/M9 客户、订单和毛利证据。 |
| 关键约束 | 树脂配方、电子布、铜箔、压合良率、客户 AVL 和二供认证。 |
| 剔除项 | 普通 FR-4、普通覆铜板、只讲“高频高速材料”但没有等级/客户/收入的公司。 |

### 3.7 高端电子布 / Low CTE / Low Dk-Df / T-glass / Q cloth

| 维度 | 判断 |
|---|---|
| 硬增量 | 高速 PCB 和 M8/M9/M10 CCL 需要低介电、低损耗、低热膨胀、尺寸稳定性更好的布种。 |
| 当前瓶颈状态 | soft_bottleneck+。证据已经强化，但尚缺官方分产品 allocation、量化交期、客户排队。 |
| 主线 A 股 | 宏和科技。 |
| 观察 A 股 | 中材科技、国际复材、菲利华。 |
| 严格边界 | 宏和官方口径是 Low CTE / 低介电等特种电子布，不应无条件写成“T-glass 已确定大量供货”。 |
| 剔除项 | 普通玻纤、建筑玻纤、风电玻纤、没有电子级/低介电/Low CTE 客户认证的公司。 |

### 3.8 PCB 级 HVLP / VLP / RTF 铜箔

| 维度 | 判断 |
|---|---|
| 硬增量 | 224G/1.6T、高速背板、M8/M9 低损耗 CCL 对低粗糙度和一致性要求上升。 |
| 当前瓶颈状态 | soft_bottleneck/watch+。有需求和扩产证据，但 HVLP5 多客户批量收入仍未验证。 |
| 主观察 A 股 | 德福科技。 |
| 其他观察 | 嘉元科技、诺德股份、铜冠铜箔，但必须逐家验证 PCB 级高端铜箔，而不是锂电铜箔。 |
| 德福边界 | RTF-3/4、HVLP1-3、HVLP4/5 有进展；但 2025 收入和利润主体仍不是高端电子电路铜箔，不能把锂电铜箔修复当 AI PCB 兑现。 |
| 剔除项 | 只讲锂电铜箔产能、没有 PCB 级 HVLP/RTF 客户认证和收入的公司。 |

### 3.9 ABF / IC substrate

| 维度 | 判断 |
|---|---|
| 硬增量 | 卖方测算 ABF 每柜价值 +82%，来自 GPU/CPU/NVSwitch/ConnectX 等芯片数量与封装价值提升。 |
| 产业链特点 | 与板级 PCB 是不同链路，核心在高端封装载板良率、客户认证和先进封装生态。 |
| 全球核心 | Ibiden、Shinko、Unimicron、Nan Ya PCB 等。 |
| A 股映射 | 兴森科技、深南电路可观察，但高端 AI ABF 订单、良率、收入拆分不足。 |
| 剔除项 | 把板级 PCB 公司直接等同 ABF 龙头，或者把普通 IC 载板收入外推到 AI GPU substrate。 |

### 3.10 MLCC

| 维度 | 判断 |
|---|---|
| 硬增量 | 测算从约 1,530 美元/柜升至 4,320 美元/柜，+182%。 |
| 投研含义 | 百分比高，但绝对美元额低于 PCB；更适合作为供需紧张验证线索。 |
| A 股观察 | 三环集团、风华高科等。 |
| 证据要求 | 必须有 AI server / GPU board / switch board 客户、产品规格、涨价或收入毛利兑现。 |
| 剔除项 | 普通 MLCC 周期复苏不能直接等同 Rubin 受益。 |

### 3.11 电源 / 800VDC / HVDC / power shelf / busbar

| 维度 | 判断 |
|---|---|
| 硬增量 | GB300 官方参考为 full rack up to 142kW、8 power shelves；VR 功率密度继续提高，NVIDIA 800VDC 生态明确。 |
| 需求传导 | 机架功率密度上升 -> power shelf、busbar、保护器件、SiC/GaN、AC/DC、DC/DC、rack power sidecar、facility power 升级。 |
| 全球生态 | Delta、Flex、LiteOn、Megmeet、Vertiv、Eaton、Schneider、ABB 等。 |
| A 股观察 | 麦格米特、立讯/连接供电结构、部分电力设备公司。 |
| 证据缺口 | A 股公司是否有 NVIDIA 800VDC / Kyber / VR rack power shelf 订单、收入和毛利。 |
| 剔除项 | 泛电源、泛 UPS、泛电网设备。Facility transformer/switchgear 与 rack power shelf 是不同层。 |

### 3.12 液冷 / manifold / QD / 冷板 / CDU

| 维度 | 判断 |
|---|---|
| 增量 | GB300 已液冷，VR 是更高热密度、cable-free/hose-free/fanless 设计；本地拆解测算 cooling +12%。 |
| 投资含义 | 方向确定，但相对 PCB 的单柜增量不高。 |
| A 股观察 | 英维克、飞荣达等。 |
| 证据要求 | AI rack 平台认证、冷板/CDU/QD/manifold 订单、收入和毛利，而不是普通 HVAC。 |
| 剔除项 | 泛制冷、普通机房空调、没有 AI rack 项目证据的液冷概念。 |

### 3.13 连接器 / CAGE / OSFP / 铜缆 / 高电流互连

| 维度 | 判断 |
|---|---|
| 增量 | CX9、OSFP、1.6T/GPU、rack power 和高密互连推高连接密度与可靠性要求。 |
| A 股主观察 | 鼎通科技、立讯精密。 |
| 鼎通边界 | 有 CAGE、112G/224G、液冷散热器、客户认证与批量供货线索；但不是 retimer 芯片、不是整机、也不能直接写成 NVIDIA 订单。 |
| 证据要求 | 224G/CAGE/液冷散热器收入、客户、订单、毛利率和产线兑现。 |
| 剔除项 | 普通连接器、汽车连接器、消费电子连接器不能混入 AI rack 高速互联。 |

### 3.14 光模块 / EML / CW / InP / CPO / FAU

| 维度 | 判断 |
|---|---|
| 与 VR BOM 的关系 | 主要是 cluster scale-out / scale-up 旁线，不是 VR 单柜内部 BOM 最大增量。 |
| 当前瓶颈 | 本地光模块账本把高端 EML/InP/CW/pump/ELS 列为 hard bottleneck；模块整机装配为 soft/easing。 |
| A 股主线 | 中际旭创、新易盛、天孚通信、源杰科技、光迅科技。 |
| 严格边界 | 中际/新易盛是模块强者；天孚是器件/光引擎/FAU/ELS；源杰是 CW/EML 光芯片，200G EML 仍待量产收入证明。 |
| 剔除项 | 把光模块当 VR 柜内 BOM 直接增量，或者把 200G EML 验证写成大规模出货。 |

### 3.15 Retimer / AEC / BERT / 高速测试

| 维度 | 判断 |
|---|---|
| 技术重要性 | 224G/200G PAM4、AEC、测试链路重要，全球看 Credo、Marvell、Broadcom、MaxLinear、Keysight、VIAVI 等。 |
| A 股映射 | 弱。当前没有足够公开证据证明 A 股公司是 224G Ethernet AEC retimer IC、cable-end retimer 或 1.6T/224G BERT 核心供应商。 |
| 剔除项 | 澜起 PCIe/CXL retimer 不能直接等同 224G Ethernet AEC；封测/ATE 公司不能在没有客户和产品证据时硬贴 retimer。 |
| 结论 | 只做全球观察，不纳入 A 股主线。 |

### 3.16 BMC / HMC / MCU / ERoT / CPLD / TPM / SSD

| 维度 | 判断 |
|---|---|
| VR 文件细节 | compute tray 有 AST2600 HMC/BMC、CEC1736、MCXN556、TPM、E1.S；switch tray 也有 AST2600、CEC1736、MCXN556 等。 |
| A 股映射 | 很弱，核心供应商多为 Aspeed、Microchip、NXP、Lattice 等。 |
| 投资结论 | 不是 A 股主线。SSD 数量可能变化，但配置不确定、价值量和受益主体不清。 |

### 3.17 ODM / rack assembly / system integration

| 维度 | 判断 |
|---|---|
| 增量 | 系统复杂度提升，ODM 绝对附加值上升；但毛利率可能受标准化和大客户压价影响。 |
| A 股映射 | 工业富联。 |
| 投资含义 | 确定性高、体量大，但交易弹性通常不如 PCB/材料小中盘。 |
| 剔除项 | 只因“服务器代工”就列所有 ODM/EMS；必须看 AI rack、客户、产能、毛利和营运资金。 |

## 4. A 股严筛池

### 4.1 主线池

| 公司 | 节点 | 证据强度 | 基本面质量 | 业绩弹性 | 交易弹性 | 核心风险 |
|---|---|---|---|---|---|---|
| 胜宏科技 300476.SZ | AI PCB、高层板、高阶 HDI、UBB、交换机板 | 高 | 高 | 很高 | 高 | AI PCB 收入/客户未拆，扩产与毛利回落风险 |
| 沪电股份 002463.SZ | 高速网络 PCB、AI/HPC PCB、1.6T switch/Riser | 高 | 很高 | 高 | 中高 | 估值已反映，订单和毛利持续性 |
| 生益科技 600183.SH | 高速 CCL、prepreg、封装用基材 | 高 | 很高 | 中高 | 中高 | M8/M9 客户和价格传导需跟踪 |
| 深南电路 002916.SZ | 高速背板、AI 加速卡、封装基板能力 | 高 | 很高 | 中高 | 中 | 业务较均衡，交易弹性弱于纯 AI PCB |
| 生益电子 688183.SH | 高端 PCB | 中高 | 高 | 高 | 中高 | 客户/平台/毛利仍需细拆 |
| 宏和科技 603256.SH | 高端电子布、Low CTE、低介电布 | 中高 | 中高 | 很高 | 很高 | 估值极高，终端 AI 客户未拆，T-glass 口径需谨慎 |

### 4.2 次线 / 条件式观察

| 公司 | 节点 | 放进观察的原因 | 不能升级主线的原因 |
|---|---|---|---|
| 德福科技 301511.SZ | PCB 级 HVLP/RTF 铜箔 | RTF/HVLP 产品、头部 CCL 意向、扩产 | 2025 收入主体仍是锂电铜箔，高端电子电路铜箔收入/毛利未拆 |
| 鼎通科技 688668.SH | CAGE、224G、液冷散热结构 | CAGE 收入、224G 批量供货、液冷认证 | 不是 retimer，不是终端订单，客户和收入拆分不足 |
| 麦格米特 002851.SZ | 800VDC / power ecosystem | NVIDIA 800VDC 生态有 Megmeet | A 股主体 AI data center power 收入和订单需验证 |
| 英维克 002837.SZ | CDU / 液冷系统 | 数据中心液冷主线 | VR 单柜增量低于 PCB，需 AI rack 项目证据 |
| 飞荣达 300602.SZ | 散热/结构 | 热管理与结构件弹性 | 需平台认证和收入拆分 |
| 工业富联 601138.SH | ODM/rack assembly | AI server/rack 体量确定 | 毛利率低，市值大，弹性弱于材料 |
| 中际旭创/新易盛/天孚/源杰/光迅 | 光通信 | AI scale-out 网络强主线 | 不属于 VR 单柜 BOM 第一增量，需单独建仓逻辑 |

### 4.3 明确剔除口径

| 类型 | 剔除原因 |
|---|---|
| 泛 PCB | 没有 AI server/switch/UBB/high-layer/HDI 客户或产品证据 |
| 泛玻纤 | 普通建筑/风电玻纤不能替代 Low Dk-Df / Low CTE 电子布 |
| 泛铜箔 | 锂电铜箔不能替代 PCB 级 HVLP/VLP/RTF 铜箔 |
| 泛液冷 | 普通 HVAC、机房空调不能等同 AI rack 冷板/CDU/manifold/QD |
| 泛电源 | 普通 UPS、电源适配器不能等同 800VDC rack power shelf |
| 泛 retimer | PCIe/CXL retimer、封测、ATE 不能直接映射 224G Ethernet AEC retimer |
| 泛光模块 | 光通信强，但不能塞进 VR 单柜 BOM 直接增量 |
| 泛网安/DPU | 国内 DPU 或网络安全概念不能等同 BF4 供应链 |

## 5. 2026-06-05 行情快照：只用于交易弹性，不用于受益证明

数据源：东方财富行情接口，抓取时间为 2026-06-05 盘中。盘中数据会变化，收盘后需复核。

| 代码 | 名称 | 价格 | 涨跌幅 | 成交额亿元 | 换手率 | PE | 总市值亿元 | 交易解读 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 300476 | 胜宏科技 | 349.45 | -4.71% | 109.32 | 3.58% | 66.64 | 3434 | 高流动性、高预期，仍是 PCB 交易核心 |
| 002463 | 沪电股份 | 138.75 | -1.47% | 79.41 | 3.00% | 53.74 | 2670 | 中军属性强，弹性不如胜宏/材料小盘 |
| 600183 | 生益科技 | 142.59 | -0.40% | 59.74 | 1.78% | 74.77 | 3464 | 材料中军，估值已高 |
| 002916 | 深南电路 | 386.17 | -1.83% | 28.40 | 1.11% | 77.35 | 2630 | 高质量但交易弹性相对低 |
| 688183 | 生益电子 | 123.80 | -3.29% | 17.40 | 1.70% | 57.89 | 1030 | 纯 PCB 弹性，但需订单/毛利拆分 |
| 603256 | 宏和科技 | 205.53 | +5.39% | 23.83 | 1.33% | 331.45 | 1859 | 电子布弹性强，估值和拥挤度高 |
| 301511 | 德福科技 | 124.48 | +1.77% | 27.81 | 6.20% | 133.23 | 785 | HVLP 期权强，锂电铜箔混同风险大 |
| 688668 | 鼎通科技 | 408.00 | +12.58% | 27.45 | 4.83% | 176.85 | 568 | 连接结构高弹性，需防概念过热 |
| 688519 | 南亚新材 | 251.00 | +1.62% | 8.49 | 1.48% | 98.30 | 590 | CCL 弹性观察 |
| 301526 | 国际复材 | 22.80 | +0.48% | 26.80 | 8.30% | 79.55 | 860 | 玻纤/电子布交易弹性强，需高端产品证据 |
| 002851 | 麦格米特 | 151.37 | -1.78% | 42.58 | 6.03% | 191.91 | 880 | 800VDC 观察，订单证据不足前不升主线 |
| 002837 | 英维克 | 67.33 | -2.73% | 17.70 | 2.33% | 2477.65 | 858 | 液冷方向强，估值极高 |
| 300602 | 飞荣达 | 42.11 | -0.35% | 7.82 | 4.80% | 79.19 | 245 | 热管理/结构观察 |
| 601138 | 工业富联 | 76.04 | -3.20% | 105.38 | 0.69% | 37.12 | 15089 | 确定性高但市值大、弹性被摊薄 |
| 300308 | 中际旭创 | 1240.79 | -3.06% | 265.87 | 1.89% | 60.31 | 13834 | 光模块中军，不属于 VR 单柜主增量 |
| 300502 | 新易盛 | 780.47 | +0.58% | 181.45 | 2.55% | 69.89 | 7773 | 光模块高弹性，需 Q2/Q3 验证 |
| 300394 | 天孚通信 | 477.18 | -0.68% | 135.92 | 3.59% | 188.84 | 3718 | 光器件/CPO 配套，估值高 |
| 688498 | 源杰科技 | 1388.97 | +1.10% | 56.74 | 3.27% | 240.92 | 1729 | CW/EML 期权强，客户集中和估值风险高 |
| 002281 | 光迅科技 | 235.42 | +6.74% | 113.29 | 6.28% | 197.88 | 1899 | 光模块交易弹性高，需订单/收入拆分 |
| 002475 | 立讯精密 | 72.30 | -3.07% | 96.60 | 1.86% | 35.99 | 5268 | 连接/整机能力强，但 AI rack 细分订单需验证 |

## 6. 三层排名

### 基本面质量

1. 沪电股份 / 生益科技 / 深南电路：证据质量、客户验证和财务韧性更强。
2. 胜宏科技：成长与兑现最强，但高资本开支和客户不透明度高。
3. 中际旭创 / 新易盛：光模块旁线基本面强，但不归入 VR 单柜主线。
4. 生益电子：PCB 纯度高，体量和披露仍需验证。
5. 宏和科技 / 鼎通科技 / 德福科技：节点弹性高，但估值、证据边界和业务混同风险更大。

### 业绩弹性

1. 胜宏科技：PCB 价值量 +233% 的直接映射，且已有高端 HDI/高层板业绩兑现。
2. 宏和科技：高端电子布收入与毛利弹性高，但估值和周期反转风险极高。
3. 德福科技：若 HVLP4/5 和头部 CCL 合作转正式订单，弹性大；当前仍是条件式。
4. 鼎通科技：224G/CAGE/液冷结构件兑现会有弹性，但不能当芯片主线。
5. 沪电股份 / 生益电子 / 深南电路 / 生益科技：更稳，但市场预期也更充分。

### 交易弹性

1. 鼎通科技、德福科技、国际复材：小市值/高换手/高主题弹性，但证据边界更脆弱。
2. 宏和科技：电子布最强题材之一，但 PE 与涨幅已经很危险。
3. 胜宏科技：高成交、高关注、高兑现，仍是主线交易核心。
4. 光迅科技、源杰科技、天孚通信：光通信旁线弹性强，但不是 VR 单柜 BOM 主线。
5. 沪电、生益、深南、中际、工业富联：中军属性更强，弹性被市值摊薄。

## 7. 后续跟踪指标

| 节点 | 关键指标 | 反转信号 |
|---|---|---|
| PCB | midplane、ConnectX PCB、switch PCB、UBB、AI 加速卡订单；高层数、HDI 阶数、良率、海外产能 | 订单递延、毛利率下行、应收/存货失控、客户二供充分 |
| CCL/prepreg | M8/M9/M10 认证、涨价、lead time、客户提前锁料、安全库存 | 报价停涨、交期回落到常态、二供 AVL 扩容 |
| 电子布 | Low CTE / Low Dk-Df / 超低损耗布收入、毛利、客户认证、产能 | 普通布价格回落、高端布不再涨价、客户认证转单不及预期 |
| PCB 铜箔 | HVLP4/5 多客户批量、加工费、电子电路铜箔收入和毛利 | 高端铜箔收入不增、锂电铜箔占比继续主导、现金流恶化 |
| 连接结构 | 224G/CAGE/OSFP/液冷散热器收入、客户、产线 | 客户认证不转订单、年降压缩毛利 |
| Power | 800VDC、power shelf、busbar、SiC/GaN、Megmeet/Delta 等订单 | 2027 Kyber/VR 节奏推迟、项目只停留展示 |
| Liquid cooling | CDU、冷板、manifold、QD 平台认证和收入 | 估值先行但订单/毛利不兑现 |
| Optical | 1.6T/3.2T、EML/CW/InP、CPO/ELS、FAU、模块 ASP 和预付款 | 关键料供给缓解、价格年降扩大、CPO 延后 |

## 8. 当前最严谨的投资结论

第一主线：PCB/CCL/电子布。  
这条线同时满足三点：VR-NVL72 BOM 硬增量最大、A 股公司有真实产品映射、财报/公告/IR 能找到相对硬的公司证据。

第二主线：连接结构件、电源、液冷。  
这些环节有增量，但必须用订单、平台认证和收入拆分筛选，不能泛化。

旁线强机会：光通信。  
AI scale-out 网络确实强，但这是集群网络主线，不是 VR-NVL72 柜内 BOM 主增量。中际、新易盛、天孚、源杰、光迅可以单独做光通信账本，不要混在 PCB 账本里。

当前严筛后的 A 股主池：

1. 胜宏科技：业绩弹性主线。
2. 沪电股份：质量中军。
3. 生益科技：材料中军。
4. 深南电路 / 生益电子：高端 PCB 验证池。
5. 宏和科技：高端电子布高弹性但高风险。
6. 德福科技：PCB 级铜箔条件式观察。
7. 鼎通科技：高速连接结构条件式观察。

一句最重要的纪律：任何公司只要不能回答“它供应的具体物料是什么、用在 VR/GB 的哪个节点、下游需求如何传到它的收入/毛利、官方证据在哪里”，就不进入主线池。
