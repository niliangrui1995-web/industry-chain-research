# AI 产业链逐级拆解 - Level 3 梳理表

日期：2026-05-31

任务类型：梳理

上游依据：`docs/ai_chain_disassembly/level_02_audit_2026-05-31.md`

当前状态：pending_audit

下一任务：审计本 Level 3 表，不进入 Level 4。

## 本轮口径

| 字段 | 口径 |
|---|---|
| Level 0 | AI 数据中心 / 智算中心。 |
| Level 1 | 已通过审计的 7 条主链。 |
| Level 2 | 已通过 Level 2 审计、且 `Level 3 权限 = allow` 的 60 个父节点。 |
| Level 3 | 每个 Level 2 父节点继续往上游拆出的产品、器件、材料、工艺、设备、测试或制造服务节点。 |
| 本轮不做 | 不审计、不进入 Level 4、不判定瓶颈、不做价值量排序、不映射股票、不使用行情数据。 |
| 证据口径 | 本轮为结构梳理；涉及份额、价格、产能、交期、短缺、毛利率和公司证据时标 `N/A`，留给后续证据任务。 |

## 不进入 Level 3 主表的 Level 2 节点

| source_node_id | item | 本轮处理 |
|---|---|---|
| DC-L2-003-006 | 供应链管理与组件 allocation | Level 2 审计已转附表，不作为 Level 3 父节点。 |
| DC-L2-003-007 | 现场部署与售后维护 | Level 2 审计已转附表，不作为 Level 3 父节点。 |

## Level 3 主表

### DC-L1R-001 GPU/ASIC 加速计算链

| node_id | level | parent_node_id | node_name | 精确定义 | Level 4 候选，不在本轮展开 | 唯一归属与边界 | priority | status |
|---|---:|---|---|---|---|---|---|---|
| DC-L3-001-001-001 | 3 | DC-L2-001-001 | 张量/矩阵计算核心 | GPU、ASIC、TPU die 内负责矩阵乘、张量运算和 AI 加速的核心计算单元。 | MAC 阵列、Tensor Core 类单元、低精度计算单元、调度微架构。 | 只属于计算 die 设计，不计入制造制程或封装。 | P0 | pending_audit |
| DC-L3-001-001-002 | 3 | DC-L2-001-001 | 片上 SRAM / Cache | 加速芯片内部用于缓存权重、激活、调度数据的片上存储结构。 | SRAM bitcell、cache controller、bank 结构、ECC。 | 不等于 HBM 或外部 DRAM。 | P0 | pending_audit |
| DC-L3-001-001-003 | 3 | DC-L2-001-001 | NoC / 片上互连 | die 内连接计算阵列、缓存、I/O 和控制模块的片上网络。 | NoC router、crossbar、片上链路、QoS 控制。 | 只指 die 内互连，不含板级或机柜级互连。 | P0 | pending_audit |
| DC-L3-001-001-004 | 3 | DC-L2-001-001 | HBM PHY / 内存控制器 | GPU/ASIC die 与 HBM 通信的物理接口和内存访问控制模块。 | HBM PHY、memory controller、training logic、接口验证。 | HBM 存储堆本体归 DC-L2-001-002。 | P0 | pending_audit |
| DC-L3-001-001-005 | 3 | DC-L2-001-001 | Die-to-die / Chiplet 接口 IP | 多 die 或 chiplet 间高速互连所需的接口协议、PHY 和封装协同 IP。 | UCIe 类接口、SerDes、bump map、互连协议。 | 不等于封装工艺本身。 | P1 | pending_audit |
| DC-L3-001-001-006 | 3 | DC-L2-001-001 | 加速芯片设计验证 IP / EDA 流程 | 支撑 GPU/ASIC 架构设计、仿真、验证和时序收敛的软件与 IP 流程。 | RTL 验证、formal、仿真器、时序分析、功耗分析。 | 作为芯片设计上游工具链保留，不进入软件生态附表。 | P2 | pending_audit |
| DC-L3-001-002-001 | 3 | DC-L2-001-002 | HBM DRAM core die | HBM 堆栈中的存储核心晶粒。 | DRAM cell、sense amplifier、wordline、bitline、ECC。 | 只指 HBM 存储 die，不含 base die。 | P0 | pending_audit |
| DC-L3-001-002-002 | 3 | DC-L2-001-002 | HBM base logic die | HBM 堆栈底部负责接口、控制和测试支持的逻辑晶粒。 | I/O logic、test logic、PHY interface、power management。 | 与 GPU die 的内存控制器分开。 | P0 | pending_audit |
| DC-L3-001-002-003 | 3 | DC-L2-001-002 | TSV 垂直互连 | HBM 堆栈中贯穿 DRAM die 的垂直导通结构。 | TSV etch、TSV fill、绝缘层、露铜工艺。 | HBM TSV 归 HBM 链，interposer TSV 归 DC-L2-001-004。 | P0 | pending_audit |
| DC-L3-001-002-004 | 3 | DC-L2-001-002 | Microbump / Hybrid bonding | HBM die 间或 HBM 与 base die 间的微凸点、混合键合和互连结构。 | copper pillar、microbump、hybrid bonding、underfill。 | 只覆盖 HBM stack 内部连接。 | P0 | pending_audit |
| DC-L3-001-002-005 | 3 | DC-L2-001-002 | HBM stack assembly | 将多层 DRAM die、base die 和互连结构堆叠封装为 HBM stack 的组装工艺。 | die thinning、stacking、bonding、molding、warpage control。 | 不等于 GPU/HBM 整体先进封装。 | P0 | pending_audit |
| DC-L3-001-002-006 | 3 | DC-L2-001-002 | HBM 测试与老化 | HBM 堆栈级电性、带宽、温度和可靠性测试。 | wafer probe、stack test、burn-in、thermal test、repair。 | 只覆盖 HBM，不覆盖整包 GPU 模块。 | P1 | pending_audit |
| DC-L3-001-003-001 | 3 | DC-L2-001-003 | 2.5D CoWoS 类封装 | 通过中介层或高密度互连把 GPU/ASIC 与 HBM 集成的 2.5D 封装服务。 | interposer attach、die attach、bump、underfill、warpage control。 | 硅中介层本体另见 DC-L2-001-004。 | P0 | pending_audit |
| DC-L3-001-003-002 | 3 | DC-L2-001-003 | 3D stacking / Hybrid bonding | 通过垂直堆叠或混合键合提升 die 间互连密度的先进封装工艺。 | wafer-to-wafer bonding、die-to-wafer bonding、alignment、bonding metrology。 | 不与 HBM stack 内部键合重复。 | P1 | pending_audit |
| DC-L3-001-003-003 | 3 | DC-L2-001-003 | Fan-out / RDL 封装 | 使用再布线和扇出结构实现多 die 互连与 I/O 扩展的封装路线。 | RDL、molding、temporary carrier、debond、panel process。 | 与硅中介层路线分开标记。 | P1 | pending_audit |
| DC-L3-001-003-004 | 3 | DC-L2-001-003 | Underfill / Molding 材料与工艺 | 先进封装中用于填充、保护和应力控制的胶材与成型工艺。 | underfill、molding compound、stress buffer、固化工艺。 | 材料在本节点只按封装用途统计。 | P1 | pending_audit |
| DC-L3-001-003-005 | 3 | DC-L2-001-003 | 封装翘曲与热机械控制 | 面向大尺寸先进封装的应力、翘曲、热膨胀和可靠性控制环节。 | warpage metrology、CTE 匹配、仿真、夹具、热循环测试。 | 不等于系统级液冷。 | P1 | pending_audit |
| DC-L3-001-003-006 | 3 | DC-L2-001-003 | 先进封装设备与自动化 | 支撑先进封装贴装、键合、清洗、检测和自动化搬运的设备环节。 | die bonder、hybrid bonder、plasma clean、AOI、X-ray。 | 设备只按封装用途归属。 | P1 | pending_audit |
| DC-L3-001-004-001 | 3 | DC-L2-001-004 | 硅中介层晶圆 | 用于承载 GPU/ASIC 与 HBM 高密度互连的硅基中介层基底。 | silicon wafer、薄化、绝缘层、刻蚀。 | 不等于普通晶圆制造服务。 | P0 | pending_audit |
| DC-L3-001-004-002 | 3 | DC-L2-001-004 | RDL 铜再布线 | 中介层或封装层中的高密度铜互连线路。 | 铜电镀、seed layer、线路图形、介电层。 | 只统计封装互连，不统计板级 PCB 铜线路。 | P0 | pending_audit |
| DC-L3-001-004-003 | 3 | DC-L2-001-004 | TSV 刻蚀与填充 | 中介层中的通孔刻蚀、绝缘、金属填充和连接工艺。 | deep etch、liner、copper fill、CMP。 | 与 HBM die 内 TSV 分开。 | P1 | pending_audit |
| DC-L3-001-004-004 | 3 | DC-L2-001-004 | 介电层 / Passivation 材料 | RDL 和中介层中用于绝缘、钝化和可靠性保护的材料体系。 | polyimide、PBO、low-k dielectric、passivation。 | 只按封装互连材料归属。 | P1 | pending_audit |
| DC-L3-001-004-005 | 3 | DC-L2-001-004 | Interposer 检测与修复 | 对中介层开短路、线宽线距、TSV 缺陷和可靠性进行检测修复。 | e-test、AOI、metrology、repair、yield map。 | 不等于整包测试。 | P1 | pending_audit |
| DC-L3-001-005-001 | 3 | DC-L2-001-005 | ABF build-up film | 高端 IC 载板增层用绝缘膜材料。 | ABF resin、filler、film casting、surface treatment。 | 不等于板级 CCL。 | P0 | pending_audit |
| DC-L3-001-005-002 | 3 | DC-L2-001-005 | 载板 core / BT 材料 | IC 载板内部芯板或 BT 类材料体系。 | core substrate、BT resin、glass fabric、copper foil。 | 只按封装载板用途归属。 | P1 | pending_audit |
| DC-L3-001-005-003 | 3 | DC-L2-001-005 | 载板激光钻孔 / 微孔 | ABF/IC 载板中形成微孔和高密度垂直互连的加工环节。 | laser drilling、desmear、via formation、microvia inspection。 | 不等同于普通 PCB 钻孔。 | P0 | pending_audit |
| DC-L3-001-005-004 | 3 | DC-L2-001-005 | 载板电镀与线路形成 | IC 载板中精细线路、铜柱和互连层形成工艺。 | copper plating、patterning、etching、SAP/MSAP。 | 与板级 PCB 线路加工分开。 | P0 | pending_audit |
| DC-L3-001-005-005 | 3 | DC-L2-001-005 | 载板阻焊 / 表面处理 | IC 载板外层保护、焊盘处理和封装连接界面。 | solder mask、surface finish、ENEPIG、OSP。 | 只统计 IC 载板表面处理。 | P1 | pending_audit |
| DC-L3-001-005-006 | 3 | DC-L2-001-005 | 载板检测与电测 | ABF/IC 载板开短路、尺寸、翘曲和可靠性检测。 | e-test、AOI、X-ray、warpage test、reliability test。 | 不等于整包芯片测试。 | P1 | pending_audit |
| DC-L3-001-006-001 | 3 | DC-L2-001-006 | 高速低损耗 CCL | 算力板 PCB 使用的低损耗覆铜板材料。 | 树脂体系、电子布、铜箔、填料、压合。 | 网络板 CCL 另归 DC-L2-002-009。 | P0 | pending_audit |
| DC-L3-001-006-002 | 3 | DC-L2-001-006 | 低损耗树脂体系 | 用于高频高速 CCL 的树脂、固化剂和配方体系。 | PPO/PPE、PTFE、碳氢树脂、环氧改性、填料。 | 不泛化到普通化工树脂。 | P0 | pending_audit |
| DC-L3-001-006-003 | 3 | DC-L2-001-006 | 电子玻纤布 / 玻纤纱 | CCL 增强材料中的电子级玻纤纱和玻纤布。 | glass yarn、spread glass、weaving、surface treatment。 | 不等于建筑玻纤或普通纺织玻纤。 | P0 | pending_audit |
| DC-L3-001-006-004 | 3 | DC-L2-001-006 | PCB 铜箔 | 用于算力板 CCL 和 PCB 线路的电子级铜箔。 | ED copper foil、rolled copper foil、roughness control、surface treatment。 | 不等同于锂电铜箔。 | P0 | pending_audit |
| DC-L3-001-006-005 | 3 | DC-L2-001-006 | 高层板压合 / 背钻 / 电镀 | 算力板 PCB 的层压、钻孔、背钻、孔金属化和电镀加工。 | lamination、drilling、back drilling、PTH、plating。 | 属 PCB 制造工艺，不是 CCL 材料本体。 | P0 | pending_audit |
| DC-L3-001-006-006 | 3 | DC-L2-001-006 | PCB 电测 / 信号完整性测试 | 算力板的开短路、阻抗、插损、串扰和可靠性测试。 | flying probe、e-test、TDR、VNA、thermal cycling。 | 网络板测试另按网络板归属。 | P1 | pending_audit |
| DC-L3-001-007-001 | 3 | DC-L2-001-007 | DrMOS / Power stage | 加速卡 VRM 中集成功率开关、驱动和保护的功率级器件。 | MOSFET、driver、package、current sense、thermal pad。 | 不等于服务器 PSU 功率级。 | P0 | pending_audit |
| DC-L3-001-007-002 | 3 | DC-L2-001-007 | PWM 控制器 | 多相 VRM 的控制、调制、保护和遥测芯片。 | PWM IC、digital controller、telemetry、loop compensation。 | 只服务板级 VRM。 | P1 | pending_audit |
| DC-L3-001-007-003 | 3 | DC-L2-001-007 | VRM 电感 / 磁性件 | 板级供电中用于储能、滤波和电流纹波控制的电感。 | metal inductor、ferrite、core material、winding。 | 不等于 PSU 变压器。 | P1 | pending_audit |
| DC-L3-001-007-004 | 3 | DC-L2-001-007 | MLCC / 聚合物电容 | 加速卡板级电源去耦、滤波和瞬态响应所需电容。 | MLCC、polymer capacitor、decoupling network、ESR/ESL。 | 与供配电链大功率电容分开。 | P1 | pending_audit |
| DC-L3-001-007-005 | 3 | DC-L2-001-007 | 电流/温度监测器件 | 板级 VRM 的电流、电压、温度检测和保护器件。 | current sensor、temperature sensor、PMBus monitor、protection IC。 | 不等于整机电力监控。 | P2 | pending_audit |
| DC-L3-001-008-001 | 3 | DC-L2-001-008 | EUV / DUV 光刻 | 先进制程晶圆制造中的图形转移设备和工艺。 | lithography scanner、photoresist、mask、overlay metrology。 | 只按 GPU/ASIC die 制程归属。 | P0 | pending_audit |
| DC-L3-001-008-002 | 3 | DC-L2-001-008 | 刻蚀工艺与设备 | 晶圆制造中形成沟槽、通孔和结构的干法或湿法刻蚀环节。 | plasma etch、wet etch、etch gas、chamber parts。 | 不等于 PCB 蚀刻。 | P0 | pending_audit |
| DC-L3-001-008-003 | 3 | DC-L2-001-008 | 薄膜沉积 | 晶圆制程中的介质、金属和阻挡层沉积环节。 | CVD、PVD、ALD、precursor、target。 | 只统计半导体晶圆制程。 | P0 | pending_audit |
| DC-L3-001-008-004 | 3 | DC-L2-001-008 | CMP / 平坦化 | 先进制程中实现表面平坦化的设备、耗材和工艺。 | CMP tool、slurry、pad、conditioner、cleaning。 | 不等于封装后段研磨。 | P1 | pending_audit |
| DC-L3-001-008-005 | 3 | DC-L2-001-008 | 离子注入 / 热处理 | 晶圆制造中掺杂、退火和晶体质量控制环节。 | ion implanter、anneal、furnace、dopant gas。 | 只属于前道制程。 | P1 | pending_audit |
| DC-L3-001-008-006 | 3 | DC-L2-001-008 | 量测检测 | 晶圆制程中缺陷、尺寸、膜厚、套刻和良率监控设备。 | inspection、metrology、CD-SEM、overlay、defect review。 | 与封装检测分开。 | P0 | pending_audit |
| DC-L3-001-008-007 | 3 | DC-L2-001-008 | 工艺化学品 / 特气 | 前道制程用光刻、刻蚀、清洗、沉积相关化学品和气体。 | photoresist、wet chemicals、etch gas、precursor、clean gas。 | 不泛化到普通化工品。 | P1 | pending_audit |
| DC-L3-001-009-001 | 3 | DC-L2-001-009 | ATE 测试机 | 对 GPU/ASIC 封装和加速卡进行自动化电性测试的设备。 | tester、test program、handler interface、test cell。 | 整机系统测试另属 DC-L2-003-005。 | P0 | pending_audit |
| DC-L3-001-009-002 | 3 | DC-L2-001-009 | 探针卡 / Probe card | 晶圆级或封装前测试中连接测试机和芯片焊盘的耗材设备。 | probe needle、MEMS probe、substrate、probe head。 | 只按计算芯片测试归属。 | P1 | pending_audit |
| DC-L3-001-009-003 | 3 | DC-L2-001-009 | Burn-in 老化设备 | 通过高温、负载、电压压力筛选早期失效的设备和治具。 | burn-in board、oven、socket、stress program。 | 与整机 burn-in 分开。 | P1 | pending_audit |
| DC-L3-001-009-004 | 3 | DC-L2-001-009 | 热测试 / 功耗测试 | 对高功耗封装和加速卡进行散热、功耗和热稳定性验证。 | thermal head、liquid thermal fixture、power emulator、sensor。 | 不等于液冷系统本体。 | P1 | pending_audit |
| DC-L3-001-009-005 | 3 | DC-L2-001-009 | X-ray / SAM / 失效分析 | 对封装空洞、分层、裂纹和失效机理进行无损检测和分析。 | X-ray、SAM、cross-section、FA lab、microscope。 | 只服务芯片封装可靠性。 | P1 | pending_audit |
| DC-L3-001-009-006 | 3 | DC-L2-001-009 | Load board / Socket | 测试机和被测封装或加速卡之间的接口板、插座和治具。 | load board、socket、contactor、test fixture。 | 与系统测试治具分开。 | P1 | pending_audit |

### DC-L1R-002 高速网络与光/铜互连链

| node_id | level | parent_node_id | node_name | 精确定义 | Level 4 候选，不在本轮展开 | 唯一归属与边界 | priority | status |
|---|---:|---|---|---|---|---|---|---|
| DC-L3-002-001-001 | 3 | DC-L2-002-001 | 交换机机箱 / 结构 | AI 集群交换机的物理机箱、风道、端口面板和安装结构。 | sheet metal、front panel、fan tray、air duct、mounting kit。 | 网络设备结构，不计入机柜结构链。 | P1 | pending_audit |
| DC-L3-002-001-002 | 3 | DC-L2-002-001 | 交换机主板 / Line card 装配 | 承载交换芯片、光/电接口、电源和管理模块的板卡装配。 | SMT、line card、switch board、connector、cage。 | PCB 制造本体归 DC-L2-002-009。 | P0 | pending_audit |
| DC-L3-002-001-003 | 3 | DC-L2-002-001 | 交换机散热模块 | 交换机内部风冷、液冷或混合散热组件。 | fan module、heatsink、cold plate interface、thermal sensor。 | 数据中心液冷系统另归热管理链。 | P1 | pending_audit |
| DC-L3-002-001-004 | 3 | DC-L2-002-001 | 交换机管理控制模块 | 交换机内部 BMC、管理控制板、时钟和监控硬件。 | BMC、CPLD、clock module、sensor、management port。 | NOS 软件不进入本硬件主表。 | P2 | pending_audit |
| DC-L3-002-001-005 | 3 | DC-L2-002-001 | 交换机系统测试 / 认证 | 对整机交换设备进行吞吐、延迟、协议、热和可靠性验证。 | traffic test、thermal test、protocol test、interoperability。 | 光模块单体测试另属 DC-L2-002-011。 | P1 | pending_audit |
| DC-L3-002-002-001 | 3 | DC-L2-002-002 | SerDes IP / PHY | 交换芯片中负责高速串并转换和链路物理层的 IP。 | PAM4 SerDes、CDR、equalization、PLL。 | Retimer 独立器件另归 DC-L2-002-008。 | P0 | pending_audit |
| DC-L3-002-002-002 | 3 | DC-L2-002-002 | Packet processor / Traffic manager | 交换芯片中负责包处理、调度、拥塞控制和队列管理的逻辑模块。 | parser、scheduler、buffer manager、congestion control。 | 只属于交换 ASIC 设计。 | P0 | pending_audit |
| DC-L3-002-002-003 | 3 | DC-L2-002-002 | 片上缓存 / Buffer memory | 交换芯片内部用于队列、转发和拥塞管理的缓存资源。 | SRAM、TCAM、buffer controller、ECC。 | 不等于外部 HBM 或存储 DRAM。 | P1 | pending_audit |
| DC-L3-002-002-004 | 3 | DC-L2-002-002 | 交换芯片先进制程制造 | 交换 ASIC 的晶圆制造、良率和先进制程服务。 | lithography、etch、deposition、CMP、metrology。 | 与 GPU 制造同属前道工艺但父节点不同。 | P1 | pending_audit |
| DC-L3-002-002-005 | 3 | DC-L2-002-002 | 交换芯片封装与测试 | 交换 ASIC 的封装基板、散热封装和电性测试。 | package substrate、thermal lid、ATE、socket、burn-in。 | 不等于光模块封装。 | P1 | pending_audit |
| DC-L3-002-003-001 | 3 | DC-L2-002-003 | Ethernet 控制器 / MAC | NIC 或 DPU 中负责以太网协议和端口控制的核心模块。 | MAC、PCS、FEC、flow control、time sync。 | 不等于交换芯片。 | P0 | pending_audit |
| DC-L3-002-003-002 | 3 | DC-L2-002-003 | DPU SoC 计算与加速核 | DPU/SmartNIC 中用于网络、安全、存储或虚拟化卸载的计算与加速模块。 | ARM cores、crypto engine、compression、storage offload。 | 只作为网络卸载节点，不提升到 GPU 计算链。 | P1 | pending_audit |
| DC-L3-002-003-003 | 3 | DC-L2-002-003 | RDMA / RoCE 卸载引擎 | 支撑低延迟集群网络和存储网络访问的协议卸载硬件。 | RDMA engine、RoCE logic、queue pair、transport offload。 | 存储路径应用另在 DC-L2-006-007 标边界。 | P0 | pending_audit |
| DC-L3-002-003-004 | 3 | DC-L2-002-003 | NIC SerDes / PHY | 网卡和 DPU 端口的高速物理层接口。 | SerDes、retimer interface、PLL、equalizer。 | 与独立 Retimer 分开。 | P0 | pending_audit |
| DC-L3-002-003-005 | 3 | DC-L2-002-003 | NIC 板卡 / Cage / 连接器 | 网卡板、光模块笼子、电连接器和固定结构。 | NIC PCB、QSFP cage、edge connector、bracket。 | PCB 制造若深拆应回到网络板 PCB。 | P1 | pending_audit |
| DC-L3-002-004-001 | 3 | DC-L2-002-004 | EML / Laser chip | 光模块发射端的高速激光芯片，常用于数据中心高速模块。 | EML、DFB laser、InP epitaxy、reliability test。 | 不是完整光模块。 | P0 | pending_audit |
| DC-L3-002-004-002 | 3 | DC-L2-002-004 | Silicon photonics / InP PIC | 光模块中的集成光芯片或光子集成平台。 | SiPh modulator、InP PIC、grating coupler、waveguide。 | 与分立被动光器件区分。 | P0 | pending_audit |
| DC-L3-002-004-003 | 3 | DC-L2-002-004 | DSP | 光模块中负责高速信号处理、均衡、FEC 和重定时的数字信号处理芯片。 | DSP ASIC、FEC、equalization、ADC/DAC。 | 不等于交换 ASIC。 | P0 | pending_audit |
| DC-L3-002-004-004 | 3 | DC-L2-002-004 | Driver / TIA | 光模块中驱动激光器和接收光电信号的模拟电芯片。 | laser driver、TIA、limiting amplifier、analog front-end。 | 只属于光模块电芯片。 | P0 | pending_audit |
| DC-L3-002-004-005 | 3 | DC-L2-002-004 | TOSA / ROSA | 光发射和接收子组件，集成光芯片、电芯片、透镜和封装结构。 | TOSA、ROSA、active alignment、hermetic package。 | 光引擎可更高集成，不完全等同。 | P0 | pending_audit |
| DC-L3-002-004-006 | 3 | DC-L2-002-004 | 光模块 PCB / FPC | 光模块内部承载 DSP、driver、TIA 和接口的高频小板。 | module PCB、FPC、high-speed routing、soldering。 | 与交换机主板 PCB 分开。 | P1 | pending_audit |
| DC-L3-002-004-007 | 3 | DC-L2-002-004 | 光模块被动光组件 | 光模块内部的 FAU、透镜、隔离器、滤波器、光胶和连接件。 | FAU、lens、isolator、filter、optical adhesive。 | 与外部光纤连接器可交叉，需按装配位置区分。 | P1 | pending_audit |
| DC-L3-002-004-008 | 3 | DC-L2-002-004 | 光模块测试 / 校准 | 对光模块进行误码率、眼图、温漂、功耗和一致性测试。 | BERT、optical tester、thermal calibration、aging。 | 网络系统测试另归 DC-L2-002-011。 | P0 | pending_audit |
| DC-L3-002-005-001 | 3 | DC-L2-002-005 | CPO 光引擎模块 | 与交换芯片近封装或共封装的光电转换引擎。 | optical engine、modulator、receiver、package integration。 | 不等于传统可插拔光模块。 | P1 | pending_audit |
| DC-L3-002-005-002 | 3 | DC-L2-002-005 | External laser source | CPO 或近封装光学中为光引擎提供光源的外置激光源。 | laser array、fiber coupling、power control、redundancy。 | 只作为 CPO 路线光源。 | P1 | pending_audit |
| DC-L3-002-005-003 | 3 | DC-L2-002-005 | CPO 硅光 / InP PIC | CPO 光引擎中的集成光子芯片。 | SiPh PIC、InP PIC、modulator、waveguide。 | 光模块 PIC 按 DC-L2-002-004 另列。 | P1 | pending_audit |
| DC-L3-002-005-004 | 3 | DC-L2-002-005 | Fiber array / FAU | CPO 光引擎与外部光纤阵列耦合的精密被动组件。 | FAU、fiber attach、lens array、alignment fixture。 | 外部连接器另归被动光组件。 | P1 | pending_audit |
| DC-L3-002-005-005 | 3 | DC-L2-002-005 | CPO 热管理与供电接口 | 光引擎近芯片部署时的散热、供电和可靠性接口。 | micro cold plate、thermal interface、power delivery、sensor。 | 不替代数据中心液冷主链。 | P2 | pending_audit |
| DC-L3-002-005-006 | 3 | DC-L2-002-005 | CPO 封装对准与测试 | 光引擎封装、主动对准、耦合效率和可靠性测试环节。 | active alignment、coupling test、BER test、thermal cycle。 | 不等于普通模块测试。 | P1 | pending_audit |
| DC-L3-002-006-001 | 3 | DC-L2-002-006 | MEMS / LCoS 光交换引擎 | OCS 系统中实现光路切换的核心光学执行器或调制器。 | MEMS mirror、LCoS、beam steering、switch fabric。 | 不等于光模块。 | P2 | pending_audit |
| DC-L3-002-006-002 | 3 | DC-L2-002-006 | 光交叉矩阵 / Cross-connect | OCS 中进行端口到端口光路连接的矩阵结构。 | optical matrix、port array、fiber routing、loss control。 | 只属于光层交换。 | P2 | pending_audit |
| DC-L3-002-006-003 | 3 | DC-L2-002-006 | OCS 控制电子 | 控制光路切换、校准和状态监控的电子硬件。 | control board、driver IC、monitoring sensor、MCU/FPGA。 | 控制软件不进入主表。 | P2 | pending_audit |
| DC-L3-002-006-004 | 3 | DC-L2-002-006 | OCS 光纤管理 | OCS 内部高密度光纤、连接器、端口和布线结构。 | fiber tray、connector array、splicing、labeling。 | 外部机柜线缆管理另归结构链。 | P2 | pending_audit |
| DC-L3-002-006-005 | 3 | DC-L2-002-006 | OCS 校准与监测 | 对 OCS 光路插损、串扰、端口状态和可靠性进行校准监控。 | optical power monitor、calibration fixture、diagnostics。 | 仅服务 OCS。 | P2 | pending_audit |
| DC-L3-002-007-001 | 3 | DC-L2-002-007 | Twinax 铜导体 / 线材 | DAC/ACC 中用于高速短距传输的双轴铜线和导体材料。 | copper conductor、dielectric、twisted pair、foil shield。 | 不等于电源线缆。 | P1 | pending_audit |
| DC-L3-002-007-002 | 3 | DC-L2-002-007 | 高速线缆连接器 / Cage | DAC/ACC/AOC 两端的高速连接器、笼子和结构件。 | QSFP/OSFP connector、cage、latch、EMI gasket。 | 光模块 cage 如属于网卡/交换机也需边界说明。 | P1 | pending_audit |
| DC-L3-002-007-003 | 3 | DC-L2-002-007 | EEPROM / 管理 IC | 线缆或模块中用于身份、配置和管理通信的小型芯片。 | EEPROM、I2C management、temperature sensor。 | 不等于 DSP。 | P2 | pending_audit |
| DC-L3-002-007-004 | 3 | DC-L2-002-007 | ACC Linear Driver | 有源铜缆中用于补偿高速信号损耗的线性驱动器件。 | linear driver、equalizer、package、power control。 | 独立 Retimer 另归 DC-L2-002-008。 | P1 | pending_audit |
| DC-L3-002-007-005 | 3 | DC-L2-002-007 | AOC 光电组件 | 有源光缆中的小型光发射、接收和驱动组件。 | VCSEL/EML、driver、TIA、fiber attach、module PCB。 | 不等于标准可插拔光模块。 | P1 | pending_audit |
| DC-L3-002-007-006 | 3 | DC-L2-002-007 | 线缆屏蔽 / 护套 / 测试 | 线缆电磁屏蔽、机械保护、弯折可靠性和高速测试。 | shield、jacket、strain relief、bend test、BER test。 | 结构管理件不在此列。 | P2 | pending_audit |
| DC-L3-002-008-001 | 3 | DC-L2-002-008 | CDR / 重定时核心 | Retimer 中用于时钟数据恢复和链路重定时的核心模块。 | CDR、PLL、clock recovery、jitter cleanup。 | 与光模块 DSP 分开。 | P1 | pending_audit |
| DC-L3-002-008-002 | 3 | DC-L2-002-008 | Equalizer / Linear amplifier | 高速链路信号均衡、补偿和线性放大的模拟前端。 | CTLE、DFE、linear amplifier、gain control。 | 只用于链路信号完整性。 | P1 | pending_audit |
| DC-L3-002-008-003 | 3 | DC-L2-002-008 | Retimer SerDes PHY | Retimer 或线性驱动器内的高速串行物理层。 | SerDes lane、PAM4、PLL、ESD。 | 不等于 switch ASIC 内部 SerDes。 | P1 | pending_audit |
| DC-L3-002-008-004 | 3 | DC-L2-002-008 | Retimer 封装与测试 | 高速模拟/混合信号器件的封装、电性和误码测试。 | package、ATE、load board、BER test、thermal test。 | 只按独立高速链路器件归属。 | P1 | pending_audit |
| DC-L3-002-008-005 | 3 | DC-L2-002-008 | 参考时钟 / 抖动控制器件 | 高速链路中提供时钟源和抖动清理的器件。 | oscillator、clock buffer、jitter cleaner、PLL。 | 时钟器件只在网络链使用场景下归属。 | P2 | pending_audit |
| DC-L3-002-009-001 | 3 | DC-L2-002-009 | 网络板高速 CCL | 交换机、网卡和光模块板使用的低损耗 CCL。 | resin、glass cloth、copper foil、lamination。 | 与计算板 CCL 按用途分开。 | P0 | pending_audit |
| DC-L3-002-009-002 | 3 | DC-L2-002-009 | 网络高层 PCB 制造 | 交换机主板、line card、NIC PCB 的钻孔、压合、电镀和线路加工。 | lamination、back drilling、plating、HDI、impedance control。 | 光模块小板可单独标注。 | P0 | pending_audit |
| DC-L3-002-009-003 | 3 | DC-L2-002-009 | 光模块 PCB / 高频小板 | 光模块内部承载 DSP 和模拟芯片的高频小板。 | module PCB、FPC、surface finish、SMT。 | 与交换机主板 PCB 分开。 | P1 | pending_audit |
| DC-L3-002-009-004 | 3 | DC-L2-002-009 | 网络背板 / Midplane PCB | 交换系统或机架网络中的高速背板、中板和连接 PCB。 | backplane PCB、midplane、connector footprint、SI test。 | 若仅为机械支撑则归机柜结构链。 | P1 | pending_audit |
| DC-L3-002-009-005 | 3 | DC-L2-002-009 | 网络 PCB 信号完整性测试 | 网络板的阻抗、插损、串扰、回损和可靠性测试。 | TDR、VNA、coupon test、thermal cycling、e-test。 | 只服务网络板。 | P1 | pending_audit |
| DC-L3-002-010-001 | 3 | DC-L2-002-010 | 数据中心光纤 | AI 集群内高速光互连使用的多模或单模光纤。 | fiber preform、drawing、coating、ribbon fiber。 | 不泛化到接入网光纤。 | P1 | pending_audit |
| DC-L3-002-010-002 | 3 | DC-L2-002-010 | 陶瓷插芯 / Ferrule | 光连接器中保证端面定位和低插损的精密陶瓷件。 | zirconia ferrule、grinding、polishing、inspection。 | 只按数据中心光连接用途归属。 | P1 | pending_audit |
| DC-L3-002-010-003 | 3 | DC-L2-002-010 | FAU / 光纤阵列 | 多芯光纤与光芯片或光引擎耦合的阵列组件。 | fiber array、V-groove、alignment、adhesive。 | CPO 内部 FAU 需按装配位置区分。 | P1 | pending_audit |
| DC-L3-002-010-004 | 3 | DC-L2-002-010 | 透镜 / 隔离器 / 滤波器 | 光路耦合、隔离、滤波和准直相关被动光器件。 | lens、isolator、WDM filter、collimator。 | 不等于光芯片。 | P1 | pending_audit |
| DC-L3-002-010-005 | 3 | DC-L2-002-010 | MPO / LC 连接器 | 数据中心光链路端口连接和维护使用的连接器。 | MPO、LC、connector housing、polishing、cleaning。 | 机柜理线结构不在此列。 | P1 | pending_audit |
| DC-L3-002-010-006 | 3 | DC-L2-002-010 | 光胶 / 封装辅助材料 | 光组件中用于固定、耦合和可靠性保护的胶材和辅助材料。 | optical adhesive、epoxy、UV cure、outgassing test。 | 只按光组件用途归属。 | P2 | pending_audit |
| DC-L3-002-011-001 | 3 | DC-L2-002-011 | BERT 误码率测试设备 | 对高速电/光链路进行误码率、眼图和链路压力测试的设备。 | BERT、pattern generator、error detector、jitter test。 | 不等于系统流量测试。 | P1 | pending_audit |
| DC-L3-002-011-002 | 3 | DC-L2-002-011 | 光模块测试仪 | 对光模块发射、接收、功耗、温漂和协议进行测试的设备。 | optical tester、OSA、power meter、thermal fixture。 | 光模块生产测试专用。 | P1 | pending_audit |
| DC-L3-002-011-003 | 3 | DC-L2-002-011 | 协议分析仪 / 流量发生器 | 对交换机、NIC、DPU 网络协议和吞吐性能进行验证的设备。 | protocol analyzer、traffic generator、packet capture。 | 与光电物理层测试分开。 | P1 | pending_audit |
| DC-L3-002-011-004 | 3 | DC-L2-002-011 | 热箱 / 环境可靠性测试 | 网络设备和模块在温度、湿度、振动等条件下的验证设备。 | thermal chamber、humidity chamber、vibration table。 | 不等于整机服务器可靠性测试。 | P2 | pending_audit |
| DC-L3-002-011-005 | 3 | DC-L2-002-011 | 校准治具 / 认证服务 | 高速网络测试中的校准件、夹具和第三方认证服务。 | calibration fixture、golden module、compliance test。 | 只服务网络链认证。 | P2 | pending_audit |

### DC-L1R-003 AI 服务器与机架级整机集成链

| node_id | level | parent_node_id | node_name | 精确定义 | Level 4 候选，不在本轮展开 | 唯一归属与边界 | priority | status |
|---|---:|---|---|---|---|---|---|---|
| DC-L3-003-001-001 | 3 | DC-L2-003-001 | SMT / 板卡装配产线 | ODM/OEM 对服务器主板、加速板、管理板等进行贴装和板级装配的产线能力。 | SMT line、reflow、AOI、X-ray、rework station。 | PCB 制造本体不在此列。 | P1 | pending_audit |
| DC-L3-003-001-002 | 3 | DC-L2-003-001 | 整机装配产线 | 将板卡、电源、散热、结构件和线缆装配为服务器或托盘的制造服务。 | final assembly、screw fastening、cable routing、labeling。 | 只统计制造服务，不重复统计部件。 | P1 | pending_audit |
| DC-L3-003-001-003 | 3 | DC-L2-003-001 | DFM / NPI 工程 | 服务器导入量产前的可制造性设计、工艺验证和新产品导入服务。 | DFM、NPI、pilot run、process validation、yield ramp。 | 属制造服务能力。 | P1 | pending_audit |
| DC-L3-003-001-004 | 3 | DC-L2-003-001 | 工厂测试治具 | ODM/OEM 出厂测试、功能测试和压力测试所需治具。 | fixture、load emulator、cable harness、test rack。 | 测试设备只按整机制造用途归属。 | P1 | pending_audit |
| DC-L3-003-001-005 | 3 | DC-L2-003-001 | 质量体系 / 追溯系统 | 整机制造中的质量控制、批次追溯、失效反馈和过程管控体系。 | MES、traceability、QA process、failure loop。 | 不等于供应链 allocation 服务。 | P2 | pending_audit |
| DC-L3-003-002-001 | 3 | DC-L2-003-002 | 主板 SMT 装配 | CPU/DPU/BMC/电源管理等器件在服务器主板上的贴装和焊接。 | placement、reflow、AOI、X-ray、cleaning。 | 主板 PCB 制造另按 PCB 节点归属。 | P1 | pending_audit |
| DC-L3-003-002-002 | 3 | DC-L2-003-002 | Socket / Connector 安装 | 大电流、高速和可维护连接器、CPU socket、内存插槽等装配环节。 | CPU socket、DIMM slot、high-speed connector、press-fit。 | 连接器本体若深拆需按器件归属。 | P1 | pending_audit |
| DC-L3-003-002-003 | 3 | DC-L2-003-002 | 管理板 / BMC 板装配 | BMC、传感器、管理接口和辅助电路板的板级装配。 | management board、sensor board、CPLD board、SMT。 | BMC 芯片与固件另在 DC-L2-003-004。 | P2 | pending_audit |
| DC-L3-003-002-004 | 3 | DC-L2-003-002 | 板级电源模块装配 | 主板或基板上的 VRM、power module 和供电子组件装配。 | VRM assembly、inductor mounting、capacitor bank、thermal pad。 | 供电器件本体按 VRM 或供配电链处理。 | P1 | pending_audit |
| DC-L3-003-002-005 | 3 | DC-L2-003-002 | 板级 AOI / X-ray / 电测 | 主板和基板组件装配后的焊点、开短路和功能检测。 | AOI、X-ray、ICT、functional test、rework。 | 芯片封装测试不在此列。 | P1 | pending_audit |
| DC-L3-003-003-001 | 3 | DC-L2-003-003 | Rack 装配服务 | 将服务器、交换机、PDU、液冷和结构件集成为整机柜的装配服务。 | rack assembly、mounting、torque control、labeling。 | 机柜结构件本体归 DC-L1R-007。 | P1 | pending_audit |
| DC-L3-003-003-002 | 3 | DC-L2-003-003 | 机柜线缆集成 | 机柜内网络线缆、电源线缆和管理线缆的布线与联调服务。 | cable harness、routing、labeling、continuity test。 | 线缆本体归网络或供配电链。 | P1 | pending_audit |
| DC-L3-003-003-003 | 3 | DC-L2-003-003 | 液冷回路联调 | 机柜液冷管路、CDU、manifold、冷板和泄漏检测的集成调试服务。 | leak test、pressure test、flow balance、commissioning。 | 液冷部件本体归热管理链。 | P1 | pending_audit |
| DC-L3-003-003-004 | 3 | DC-L2-003-003 | Rack power 联调 | 机柜级电源、PDU、power shelf、PSU 输入和监控的联调服务。 | power-up test、load balancing、metering、protection test。 | 供配电设备本体归 DC-L1R-004。 | P1 | pending_audit |
| DC-L3-003-003-005 | 3 | DC-L2-003-003 | 网络 fabric 联调 | 机架级交换机、NIC、线缆和端口拓扑的连通性、带宽和协议联调。 | topology validation、traffic test、link training、port map。 | 网络硬件本体归 DC-L1R-002。 | P1 | pending_audit |
| DC-L3-003-003-006 | 3 | DC-L2-003-003 | 现场验收前预集成 | 出厂前对整机柜进行预配置、测试、包装和交付准备。 | pre-integration、configuration、burn-in、shipping fixture。 | 现场部署服务已转附表，不在本主链。 | P2 | pending_audit |
| DC-L3-003-004-001 | 3 | DC-L2-003-004 | BMC 芯片 | 服务器板级管理控制器芯片。 | BMC SoC、MCU、CPLD、secure element。 | 与交换机管理控制模块分开。 | P2 | pending_audit |
| DC-L3-003-004-002 | 3 | DC-L2-003-004 | 传感器接口与监测硬件 | BMC 连接温度、电压、风扇、液冷和机箱状态的接口硬件。 | sensor hub、ADC、I2C/SPI interface、fan controller。 | 不等于数据中心级监控系统。 | P2 | pending_audit |
| DC-L3-003-004-003 | 3 | DC-L2-003-004 | 固件栈 / BIOS / Boot 管理 | 启动、硬件初始化、管理协议和板级状态控制固件。 | BIOS、UEFI、BMC firmware、Redfish、bootloader。 | 集群调度软件不进入主链。 | P2 | pending_audit |
| DC-L3-003-004-004 | 3 | DC-L2-003-004 | 固件安全 / Secure boot | 服务器板级启动、固件更新和安全验证硬件/固件机制。 | root of trust、TPM、signature verification、secure update。 | 网络安全服务不在此列。 | P2 | pending_audit |
| DC-L3-003-004-005 | 3 | DC-L2-003-004 | BMC 测试与兼容性验证 | BMC、传感器、固件和管理接口的功能与兼容性测试。 | test script、emulator、sensor simulation、management test。 | 整机 burn-in 另列。 | P2 | pending_audit |
| DC-L3-003-005-001 | 3 | DC-L2-003-005 | 系统负载测试治具 | 对 AI 服务器或整机柜施加计算、网络、电源和热负载的测试治具。 | load generator、GPU stress、network traffic、power emulator。 | 芯片 ATE 测试不在此列。 | P1 | pending_audit |
| DC-L3-003-005-002 | 3 | DC-L2-003-005 | Burn-in 房 / 老化环境 | 整机或机柜在高负载和温控环境下长期运行筛选早期失效的设施。 | burn-in room、thermal control、rack fixture、monitoring。 | 与芯片 burn-in 分开。 | P1 | pending_audit |
| DC-L3-003-005-003 | 3 | DC-L2-003-005 | 热循环 / 环境可靠性测试 | 服务器整机在温度、湿度、振动和运输条件下的可靠性验证。 | thermal cycling、humidity、vibration、shock、shipping test。 | 不等于液冷部件单体测试。 | P1 | pending_audit |
| DC-L3-003-005-004 | 3 | DC-L2-003-005 | 电源压力与保护测试 | 整机供电、冗余、保护、掉电和异常状态测试。 | power stress、brownout、redundancy test、fault injection。 | 供电设备制造本体归供配电链。 | P1 | pending_audit |
| DC-L3-003-005-005 | 3 | DC-L2-003-005 | 整机失效分析 / 返修闭环 | 对系统级故障定位、返修、批次问题和良率闭环的服务流程。 | FA process、debug fixture、RMA analysis、quality feedback。 | 售后维护已转附表，本节点仅限制造质量闭环。 | P2 | pending_audit |

### DC-L1R-004 高密度供配电设备链

| node_id | level | parent_node_id | node_name | 精确定义 | Level 4 候选，不在本轮展开 | 唯一归属与边界 | priority | status |
|---|---:|---|---|---|---|---|---|---|
| DC-L3-004-001-001 | 3 | DC-L2-004-001 | 电工钢 / 铁芯材料 | 变压器铁芯使用的硅钢、电工钢和磁性材料。 | grain-oriented steel、core cutting、stacking、annealing。 | 只按变压器用途归属。 | P0 | pending_audit |
| DC-L3-004-001-002 | 3 | DC-L2-004-001 | 铜绕组 / 铜线 / 铜箔 | 变压器中用于能量转换的绕组导体。 | copper wire、copper foil、winding process、insulation coating。 | 与 PCB 铜箔分开。 | P0 | pending_audit |
| DC-L3-004-001-003 | 3 | DC-L2-004-001 | 绝缘纸 / 绝缘油 / 树脂 | 变压器内部绝缘、冷却和安全运行材料。 | kraft paper、pressboard、transformer oil、cast resin。 | 不泛化到普通绝缘材料。 | P0 | pending_audit |
| DC-L3-004-001-004 | 3 | DC-L2-004-001 | 分接开关 / 保护附件 | 变压器调压、保护和运行状态控制组件。 | tap changer、bushing、relay、temperature monitor。 | 只属于变压器附件。 | P1 | pending_audit |
| DC-L3-004-001-005 | 3 | DC-L2-004-001 | 变压器冷却 / 箱体 | 变压器散热器、油箱、风机和结构件。 | radiator、tank、fan、oil pump、surface treatment。 | 不等于数据中心 IT 冷却。 | P1 | pending_audit |
| DC-L3-004-001-006 | 3 | DC-L2-004-001 | 变压器出厂测试 | 对变压器绝缘、损耗、温升和安全进行测试认证。 | routine test、type test、partial discharge、temperature rise。 | 只服务变压器。 | P1 | pending_audit |
| DC-L3-004-002-001 | 3 | DC-L2-004-002 | 断路器 | 中低压开关柜中执行开断、保护和故障隔离的核心设备。 | vacuum breaker、air breaker、mechanism、arc chamber。 | 不等于 IT 网络交换机。 | P0 | pending_audit |
| DC-L3-004-002-002 | 3 | DC-L2-004-002 | 接触器 / 隔离开关 | 配电回路中的接通、隔离和切换器件。 | contactor、disconnector、switch mechanism、contacts。 | 只按电气保护用途归属。 | P1 | pending_audit |
| DC-L3-004-002-003 | 3 | DC-L2-004-002 | 保护继电器 / 控制单元 | 开关柜中用于故障检测、保护逻辑和联锁控制的电子单元。 | protection relay、trip unit、control board、communication module。 | 不是数据中心软件监控。 | P1 | pending_audit |
| DC-L3-004-002-004 | 3 | DC-L2-004-002 | 柜内铜排 / 母排 | 开关柜内部导电连接和电流分配结构。 | copper busbar、plating、insulation、joint。 | Busway 主通道另归 DC-L2-004-004。 | P1 | pending_audit |
| DC-L3-004-002-005 | 3 | DC-L2-004-002 | 开关柜绝缘件 / 柜体 | 开关柜安全距离、绝缘、防护和结构支撑组件。 | insulating support、enclosure、arc shield、gasket。 | 只按开关柜用途归属。 | P1 | pending_audit |
| DC-L3-004-002-006 | 3 | DC-L2-004-002 | 开关柜测试认证 | 对开关柜短路、温升、绝缘、联锁和安全性能的测试。 | short-circuit test、temperature rise、dielectric test、interlock test。 | 只服务配电保护设备。 | P1 | pending_audit |
| DC-L3-004-003-001 | 3 | DC-L2-004-003 | UPS 整流器 | UPS 中把交流输入转换为直流母线的功率变换模块。 | rectifier bridge、PFC、control board、power device。 | 与服务器 PSU 输入级分开。 | P0 | pending_audit |
| DC-L3-004-003-002 | 3 | DC-L2-004-003 | UPS 逆变器 | UPS 中把直流电转换为稳定交流输出的功率变换模块。 | inverter bridge、filter、gate driver、control loop。 | 只属于设施级 UPS。 | P0 | pending_audit |
| DC-L3-004-003-003 | 3 | DC-L2-004-003 | 静态开关 / 旁路模块 | UPS 中用于快速切换、旁路和故障保护的电力电子模块。 | static switch、SCR/thyristor、bypass contactor、control logic。 | 不等于开关柜断路器。 | P1 | pending_audit |
| DC-L3-004-003-004 | 3 | DC-L2-004-003 | DC-link 电容 / 滤波 | UPS 功率变换中用于能量缓冲和滤波的电容与滤波网络。 | film capacitor、electrolytic capacitor、LC filter、bus capacitor。 | 与服务器 PSU 电容按系统边界分开。 | P1 | pending_audit |
| DC-L3-004-003-005 | 3 | DC-L2-004-003 | UPS 控制板 / 监控板 | UPS 内部控制、保护、通信和状态监测硬件。 | control PCB、DSP/MCU、communication module、sensor interface。 | 纯 DCIM 软件不在此列。 | P1 | pending_audit |
| DC-L3-004-003-006 | 3 | DC-L2-004-003 | UPS 电池接口 / 充放电模块 | UPS 与电池系统之间的充电、放电、保护和接口模块。 | charger、DC breaker、battery interface、BMS link。 | 电池本体归 DC-L2-004-009。 | P1 | pending_audit |
| DC-L3-004-003-007 | 3 | DC-L2-004-003 | UPS 散热与机柜 | UPS 系统的风冷、液冷接口、机柜和结构热设计。 | fan、heatsink、cabinet、air duct、thermal sensor。 | 不等于 IT 液冷系统。 | P2 | pending_audit |
| DC-L3-004-004-001 | 3 | DC-L2-004-004 | 母线铜/铝导体 | Busway 中承载大电流的铜或铝导体。 | copper bar、aluminum bar、surface plating、conductor forming。 | 与 PCB 铜箔分开。 | P0 | pending_audit |
| DC-L3-004-004-002 | 3 | DC-L2-004-004 | 母线绝缘材料 | Busway 导体间绝缘、防护和耐热材料。 | insulation film、epoxy coating、flame-retardant material。 | 只按母线槽用途归属。 | P0 | pending_audit |
| DC-L3-004-004-003 | 3 | DC-L2-004-004 | Busway 外壳 / 散热结构 | 母线槽外壳、支撑、散热和防护结构。 | aluminum housing、steel enclosure、heat dissipation、bracket。 | 机柜结构支撑件不在此列。 | P1 | pending_audit |
| DC-L3-004-004-004 | 3 | DC-L2-004-004 | Tap-off / 插接箱 | 从 Busway 向机柜或设备取电的插接、保护和计量单元。 | tap-off box、breaker、metering module、connector。 | PDU 主设备另列 DC-L2-004-005。 | P0 | pending_audit |
| DC-L3-004-004-005 | 3 | DC-L2-004-004 | Busway 测试认证 | 母线槽温升、短路、绝缘和安装可靠性测试。 | temperature rise、short-circuit test、dielectric test、IP test。 | 只服务 Busway。 | P1 | pending_audit |
| DC-L3-004-005-001 | 3 | DC-L2-004-005 | PDU 配电板 / 铜排 | Rack PDU 或 power shelf 内部的电流分配板、母排和连接结构。 | distribution board、busbar、terminal block、fuse holder。 | 不等于 facility busway。 | P0 | pending_audit |
| DC-L3-004-005-002 | 3 | DC-L2-004-005 | 断路器 / 熔断器 / 保护器件 | PDU 或 power shelf 中的过流、短路和安全保护器件。 | breaker、fuse、SPD、protection relay。 | 开关柜保护设备另列。 | P0 | pending_audit |
| DC-L3-004-005-003 | 3 | DC-L2-004-005 | 计量与遥测模块 | 机柜级电压、电流、功率、能耗和状态监测模块。 | metering IC、current sensor、communication module、PMBus。 | 设施级电力监控另列 DC-L2-004-010。 | P1 | pending_audit |
| DC-L3-004-005-004 | 3 | DC-L2-004-005 | 高电流连接器 / 插座 | Rack power 到服务器或托盘的电源连接接口。 | power connector、busbar connector、socket、blind-mate interface。 | 与高速网络连接器分开。 | P0 | pending_audit |
| DC-L3-004-005-005 | 3 | DC-L2-004-005 | PDU 外壳 / 热设计 | Rack PDU 或 power shelf 的结构、散热和安装设计。 | enclosure、air duct、thermal pad、mounting bracket。 | 机柜结构只统计支撑，不统计电源设备。 | P2 | pending_audit |
| DC-L3-004-006-001 | 3 | DC-L2-004-006 | PFC 输入级 | 服务器 PSU 中负责功率因数校正和前端整流的电路模块。 | PFC controller、bridge、inductor、switching device。 | UPS 整流器另归 DC-L2-004-003。 | P0 | pending_audit |
| DC-L3-004-006-002 | 3 | DC-L2-004-006 | LLC / DC-DC 变换级 | 服务器 PSU 中进行隔离变换和输出稳压的主功率级。 | LLC transformer、synchronous rectifier、PWM control、output filter。 | 板级 VRM 不在此列。 | P0 | pending_audit |
| DC-L3-004-006-003 | 3 | DC-L2-004-006 | PSU 磁性元件 | 服务器 PSU 中的变压器、电感和共模电感。 | high-frequency transformer、inductor、magnetic core、winding。 | 与设施变压器不同。 | P0 | pending_audit |
| DC-L3-004-006-004 | 3 | DC-L2-004-006 | PSU 功率半导体 | PSU 中的 Si、SiC、GaN MOSFET、二极管和同步整流器件。 | MOSFET、GaN FET、SiC diode、driver、package。 | 与通用功率器件节点有交叉，需按用途标记。 | P0 | pending_audit |
| DC-L3-004-006-005 | 3 | DC-L2-004-006 | PSU 电容 / 滤波件 | PSU 中输入、母线、输出和 EMI 滤波电容及滤波件。 | electrolytic capacitor、film capacitor、MLCC、EMI filter。 | 与 UPS 大功率电容分开。 | P1 | pending_audit |
| DC-L3-004-006-006 | 3 | DC-L2-004-006 | PSU 控制 / 散热 / 测试 | PSU 控制芯片、风扇散热、效率和可靠性测试。 | control IC、fan、thermal sensor、efficiency test、burn-in。 | 只属于服务器 PSU。 | P1 | pending_audit |
| DC-L3-004-007-001 | 3 | DC-L2-004-007 | SiC / GaN / Si 功率开关 | 整流、逆变和电源模块中的核心功率半导体开关器件。 | SiC MOSFET、GaN FET、Si MOSFET、IGBT。 | 如按具体系统使用，需回到 UPS/PSU/power shelf。 | P1 | pending_audit |
| DC-L3-004-007-002 | 3 | DC-L2-004-007 | Gate driver / 隔离驱动 | 功率模块中驱动功率器件开关并提供隔离保护的芯片或模块。 | gate driver、isolator、bootstrap、protection circuit。 | 只按功率模块用途归属。 | P1 | pending_audit |
| DC-L3-004-007-003 | 3 | DC-L2-004-007 | DBC / AMB 功率基板 | 功率模块内部承载功率芯片、导热和绝缘的陶瓷金属化基板。 | DBC、AMB、ceramic substrate、copper layer。 | 不等于 PCB 或 IC 载板。 | P1 | pending_audit |
| DC-L3-004-007-004 | 3 | DC-L2-004-007 | 功率模块磁性件 / 电容 | 功率变换模块内部储能、滤波和谐振组件。 | inductor、transformer、film capacitor、snubber。 | 系统级电容按具体设备另可归属。 | P1 | pending_audit |
| DC-L3-004-007-005 | 3 | DC-L2-004-007 | 功率模块封装与散热 | 功率器件模块封装、导热、绝缘和可靠性结构。 | module package、baseplate、TIM、thermal cycling。 | 不等于 IT 液冷系统。 | P1 | pending_audit |
| DC-L3-004-008-001 | 3 | DC-L2-004-008 | Si MOSFET / IGBT | 供配电和电源系统中使用的硅基功率器件。 | MOSFET、IGBT、diode、wafer、package。 | 与具体 PSU/UPS 用途需边界说明。 | P1 | pending_audit |
| DC-L3-004-008-002 | 3 | DC-L2-004-008 | SiC / GaN 器件 | 高效率、高功率密度电源中使用的宽禁带功率器件。 | SiC MOSFET、GaN HEMT、epitaxy、package。 | 本轮不判断替代速度或瓶颈。 | P1 | pending_audit |
| DC-L3-004-008-003 | 3 | DC-L2-004-008 | 功率二极管 / 整流桥 | 整流、保护和续流相关功率器件。 | diode、bridge rectifier、Schottky、package。 | 只按电源系统用途归属。 | P2 | pending_audit |
| DC-L3-004-008-004 | 3 | DC-L2-004-008 | 薄膜电容 | UPS、PSU、功率模块中用于 DC-link、滤波和吸收的薄膜电容。 | film material、metallization、winding、encapsulation。 | 与 MLCC、电解电容区分。 | P1 | pending_audit |
| DC-L3-004-008-005 | 3 | DC-L2-004-008 | 电解电容 | 电源系统中用于能量缓冲和滤波的铝电解或固态电容。 | aluminum foil、electrolyte、winding、seal、aging。 | 不等于板级去耦 MLCC。 | P1 | pending_audit |
| DC-L3-004-008-006 | 3 | DC-L2-004-008 | MLCC / 驱动控制 IC | 电源控制和局部滤波中的小型电容、驱动和保护芯片。 | MLCC、driver IC、controller IC、protection IC。 | 如用于 VRM，需回归板级 VRM。 | P2 | pending_audit |
| DC-L3-004-009-001 | 3 | DC-L2-004-009 | 备电电芯 | UPS 或备用能源系统中的锂电、铅酸或其他电芯。 | Li-ion cell、lead-acid cell、chemistry、formation。 | 本轮不判断技术路线优劣。 | P2 | pending_audit |
| DC-L3-004-009-002 | 3 | DC-L2-004-009 | 电池模组 / Rack | 将电芯组合成数据中心备电模组、柜体或 rack 的硬件。 | module、rack、cabinet、busbar、thermal path。 | 与 IT 机柜结构分开。 | P2 | pending_audit |
| DC-L3-004-009-003 | 3 | DC-L2-004-009 | BMS / 保护板 | 备用电源电池的监控、均衡、保护和通信硬件。 | BMS IC、current sensor、balancing circuit、communication。 | 不等于服务器 BMC。 | P2 | pending_audit |
| DC-L3-004-009-004 | 3 | DC-L2-004-009 | DC 保护 / 接触器 | 电池系统中断路、熔断、接触和隔离保护硬件。 | DC breaker、fuse、contactor、disconnect switch。 | 与开关柜保护设备分开。 | P2 | pending_audit |
| DC-L3-004-009-005 | 3 | DC-L2-004-009 | 电池柜安全 / 消防接口 | 电池柜内热失控检测、防护、排气和消防联动硬件。 | gas sensor、thermal sensor、vent、fire interface。 | 只限电池系统内部安全。 | P2 | pending_audit |
| DC-L3-004-009-006 | 3 | DC-L2-004-009 | 发电机接口硬件 | 备用电源与柴油或燃气发电机系统的切换、接口和保护硬件。 | ATS、generator breaker、synchronizer、control interface。 | 发电机燃料和工程服务不进入本表。 | P2 | pending_audit |
| DC-L3-004-010-001 | 3 | DC-L2-004-010 | 智能电表 / 计量芯片 | 数据中心配电路径中用于电量、电压、电流和功率因数计量的硬件。 | meter IC、smart meter、sampling circuit、calibration。 | 不等于财务计费系统。 | P2 | pending_audit |
| DC-L3-004-010-002 | 3 | DC-L2-004-010 | 电流 / 电压传感器 | 供配电设备中用于状态采集和保护判断的传感器。 | current transformer、Hall sensor、voltage sensor、shunt。 | 与液冷传感器分开。 | P2 | pending_audit |
| DC-L3-004-010-003 | 3 | DC-L2-004-010 | 电能质量监测模块 | 对谐波、波动、暂降、频率和故障波形进行监控的硬件。 | power quality analyzer、harmonic monitor、waveform recorder。 | 纯软件分析不在本节点。 | P2 | pending_audit |
| DC-L3-004-010-004 | 3 | DC-L2-004-010 | 保护继电器 / 边缘控制器 | 供配电系统本地保护、联锁、采集和通信的控制硬件。 | relay、PLC/edge controller、gateway、I/O module。 | 不等于服务器 BMC。 | P2 | pending_audit |
| DC-L3-004-010-005 | 3 | DC-L2-004-010 | 监控通信模块 / 网关 | 将供配电设备状态接入本地监控或 DCIM 的硬件接口。 | Modbus gateway、Ethernet module、fiber converter、I/O gateway。 | DCIM 软件不进入本表。 | P2 | pending_audit |

### DC-L1R-005 热管理与液冷链

| node_id | level | parent_node_id | node_name | 精确定义 | Level 4 候选，不在本轮展开 | 唯一归属与边界 | priority | status |
|---|---:|---|---|---|---|---|---|---|
| DC-L3-005-001-001 | 3 | DC-L2-005-001 | 冷板铜/铝基材 | 冷板主体使用的高导热金属材料。 | copper plate、aluminum plate、alloy、surface treatment。 | 只按冷板用途归属。 | P0 | pending_audit |
| DC-L3-005-001-002 | 3 | DC-L2-005-001 | 微通道 / 流道结构 | 冷板内部提升换热效率和控制压降的流道设计与加工。 | microchannel、fin、pin-fin、CNC、etching。 | 不等于 CDU 管路。 | P0 | pending_audit |
| DC-L3-005-001-003 | 3 | DC-L2-005-001 | 钎焊 / 扩散焊 / 焊接工艺 | 冷板上下盖、流道和接口密封连接的加工工艺。 | brazing、diffusion bonding、laser welding、vacuum process。 | 只服务冷板制造。 | P0 | pending_audit |
| DC-L3-005-001-004 | 3 | DC-L2-005-001 | 冷板密封 / 表面处理 | 防腐、密封、接触热阻和长期可靠性相关处理。 | plating、coating、gasket、surface flatness、corrosion test。 | 快接头密封件另列。 | P0 | pending_audit |
| DC-L3-005-001-005 | 3 | DC-L2-005-001 | 冷板压力 / 泄漏测试 | 冷板单体压力保持、泄漏、流阻和换热性能测试。 | pressure test、helium leak、flow resistance、thermal test。 | 系统级漏液检测另列。 | P0 | pending_audit |
| DC-L3-005-001-006 | 3 | DC-L2-005-001 | 冷板平台适配件 | 冷板与 GPU/CPU/ASIC 机械固定、载荷和接口匹配结构。 | mounting frame、spring screw、load frame、interface bracket。 | 机柜结构件不在此列。 | P1 | pending_audit |
| DC-L3-005-002-001 | 3 | DC-L2-005-002 | CDU 换热器 | CDU 内部连接二次侧冷却液与设施水或冷源的换热部件。 | plate heat exchanger、microchannel exchanger、gasket。 | Chiller 设施侧设备另列。 | P0 | pending_audit |
| DC-L3-005-002-002 | 3 | DC-L2-005-002 | CDU 泵组 | CDU 中提供流量和压力的泵、冗余泵组和控制接口。 | pump、motor、VFD、redundancy、seal。 | 单体泵阀器件另可按 DC-L2-005-004 归属。 | P0 | pending_audit |
| DC-L3-005-002-003 | 3 | DC-L2-005-002 | CDU 阀组 / 过滤器 | CDU 内部控制流量、旁路、过滤和维护的流体组件。 | valve、filter、strainer、bypass、air separator。 | 只按 CDU 系统内部归属。 | P1 | pending_audit |
| DC-L3-005-002-004 | 3 | DC-L2-005-002 | CDU 控制器 / 传感器 | CDU 的温度、压力、流量、电导率和状态控制硬件。 | controller、temperature sensor、pressure sensor、flow meter。 | 数据中心 DCIM 软件不在此列。 | P0 | pending_audit |
| DC-L3-005-002-005 | 3 | DC-L2-005-002 | CDU 机柜 / 管路接口 | CDU 设备柜体、管路接口、接头和安装结构。 | cabinet、manifold interface、pipe fitting、service port。 | 机柜结构主链不重复统计 CDU 设备柜。 | P1 | pending_audit |
| DC-L3-005-002-006 | 3 | DC-L2-005-002 | CDU 出厂测试 / 联调 | CDU 的压力、流量、控制、泄漏和可靠性测试。 | flow test、pressure test、leak test、control validation。 | 整机柜联调归整机集成链。 | P1 | pending_audit |
| DC-L3-005-003-001 | 3 | DC-L2-005-003 | Manifold 主体 | 分液歧管的金属或工程塑料主体和流道结构。 | machined block、extrusion、molding、surface treatment。 | 冷板流道不在此列。 | P1 | pending_audit |
| DC-L3-005-003-002 | 3 | DC-L2-005-003 | 分支接头 / 管路接口 | Manifold 到服务器、冷板或机柜管路的接口组件。 | fitting、adapter、hose barb、threaded joint。 | 快接头若具备快速插拔功能另归 DC-L2-005-005。 | P1 | pending_audit |
| DC-L3-005-003-003 | 3 | DC-L2-005-003 | 流量平衡阀 | Manifold 中控制各支路流量、压差和平衡的阀件。 | balancing valve、orifice、control valve、calibration。 | 通用泵阀另归 DC-L2-005-004。 | P1 | pending_audit |
| DC-L3-005-003-004 | 3 | DC-L2-005-003 | Manifold 传感器 | 分液歧管上的温度、压力、流量和泄漏监测硬件。 | temperature sensor、pressure sensor、flow meter、leak sensor。 | 系统级监控另列。 | P2 | pending_audit |
| DC-L3-005-003-005 | 3 | DC-L2-005-003 | Manifold 压力 / 泄漏测试 | Manifold 出厂或集成过程中的压力保持和泄漏验证。 | pressure test、burst test、leak test、flow balance test。 | 只服务分液歧管。 | P1 | pending_audit |
| DC-L3-005-004-001 | 3 | DC-L2-005-004 | 冷却液泵 | 液冷回路中提供流量和压头的泵。 | centrifugal pump、gear pump、motor、bearing、seal。 | CDU 内泵组按系统可另标。 | P1 | pending_audit |
| DC-L3-005-004-002 | 3 | DC-L2-005-004 | 控制阀 / 电磁阀 | 液冷回路中执行流量、旁路、关断和安全联动的阀件。 | control valve、solenoid valve、ball valve、actuator。 | 不等于供配电开关。 | P1 | pending_audit |
| DC-L3-005-004-003 | 3 | DC-L2-005-004 | 流量计 | 对冷却液流量进行监测和控制反馈的传感器。 | turbine flow meter、ultrasonic flow meter、Coriolis sensor。 | 只属于液冷回路。 | P1 | pending_audit |
| DC-L3-005-004-004 | 3 | DC-L2-005-004 | 温度 / 压力传感器 | 液冷系统中监测冷却液温度、压力和异常状态的传感器。 | temperature sensor、pressure transducer、connector、calibration。 | 与电力传感器分开。 | P1 | pending_audit |
| DC-L3-005-004-005 | 3 | DC-L2-005-004 | 泵阀控制板 | 对泵、阀、传感器进行本地控制和状态采集的硬件。 | controller PCB、driver、MCU、communication interface。 | 纯软件不在此列。 | P2 | pending_audit |
| DC-L3-005-005-001 | 3 | DC-L2-005-005 | 快速断开接头 / QD | 液冷系统维护时可快速插拔并降低泄漏风险的接头。 | quick disconnect、valve core、locking mechanism、plating。 | 普通管件不在此列。 | P0 | pending_audit |
| DC-L3-005-005-002 | 3 | DC-L2-005-005 | O-ring / 密封材料 | 快接头、管路、冷板接口中防泄漏的密封材料。 | EPDM、FKM、silicone、compression set、compatibility test。 | 只按液冷密封用途归属。 | P0 | pending_audit |
| DC-L3-005-005-003 | 3 | DC-L2-005-005 | 软管 / 管材 | 液冷系统中连接 CDU、manifold、冷板的软管或管材。 | hose、tube、barrier layer、bend radius、aging test。 | 机柜管路支撑结构不在此列。 | P1 | pending_audit |
| DC-L3-005-005-004 | 3 | DC-L2-005-005 | 接头锁止 / 阀芯结构 | 快接头内部防误插、防脱落、自动封闭和安全联动结构。 | latch、valve core、spring、anti-drip design。 | 作为快接头内部结构归属。 | P1 | pending_audit |
| DC-L3-005-005-005 | 3 | DC-L2-005-005 | 寿命 / 泄漏可靠性测试 | 对快接头、密封件、软管进行插拔寿命、压力和材料兼容性测试。 | cycle test、leak test、pressure pulse、chemical compatibility。 | 只服务连接密封可靠性。 | P0 | pending_audit |
| DC-L3-005-006-001 | 3 | DC-L2-005-006 | 水乙二醇冷却液 | 冷板液冷系统常见的水基冷却液体系。 | water-glycol、inhibitor、biocide、conductivity control。 | 不等于浸没式介电液。 | P1 | pending_audit |
| DC-L3-005-006-002 | 3 | DC-L2-005-006 | 介电冷却液 | 浸没式或特定绝缘冷却场景使用的绝缘流体。 | fluorinated fluid、synthetic oil、dielectric property、aging。 | 与冷板水基液体分开。 | P2 | pending_audit |
| DC-L3-005-006-003 | 3 | DC-L2-005-006 | 防腐剂 / 添加剂 | 提升冷却液防腐、抑菌、稳定性和材料兼容性的添加剂。 | inhibitor、anti-corrosion package、biocide、pH buffer。 | 只按冷却液配方用途归属。 | P1 | pending_audit |
| DC-L3-005-006-004 | 3 | DC-L2-005-006 | 过滤 / 离子控制材料 | 控制颗粒、离子、电导率和污染物的过滤材料。 | filter cartridge、ion exchange resin、particle filter。 | 不是空气过滤。 | P1 | pending_audit |
| DC-L3-005-006-005 | 3 | DC-L2-005-006 | 材料兼容性测试 | 验证冷却液与金属、橡胶、塑料、涂层长期兼容性的测试。 | corrosion test、swelling test、aging test、conductivity drift。 | 测试作为流体材料验证环节保留。 | P1 | pending_audit |
| DC-L3-005-007-001 | 3 | DC-L2-005-007 | 浸没式 tank / 箱体 | 承载服务器和介电液的浸没式冷却容器。 | tank、lid、seal、frame、lifting structure。 | 与 rack 机柜结构分开。 | P2 | pending_audit |
| DC-L3-005-007-002 | 3 | DC-L2-005-007 | 介电液循环泵 / 过滤 | 浸没式系统中介电液循环、过滤和污染控制组件。 | pump、filter、particle control、fluid maintenance。 | 冷板液冷泵按 DC-L2-005-004。 | P2 | pending_audit |
| DC-L3-005-007-003 | 3 | DC-L2-005-007 | 浸没式换热器 | 介电液和设施冷源之间进行换热的组件。 | heat exchanger、coil、plate exchanger、cooling loop。 | 设施侧 chiller 另列。 | P2 | pending_audit |
| DC-L3-005-007-004 | 3 | DC-L2-005-007 | 服务器托盘改造件 | 适配浸没式环境的服务器托盘、接口、防护和材料替换件。 | tray、connector protection、material compatibility、service fixture。 | 与普通机箱托盘分开。 | P2 | pending_audit |
| DC-L3-005-007-005 | 3 | DC-L2-005-007 | 蒸汽 / 冷凝管理 | 两相或高挥发介电液系统中的蒸汽回收和冷凝结构。 | condenser、vapor seal、pressure control、fluid recovery。 | 仅适用于对应浸没式路线。 | P2 | pending_audit |
| DC-L3-005-008-001 | 3 | DC-L2-005-008 | Chiller 压缩机 / 制冷回路 | 设施侧冷源中压缩、冷凝、蒸发和制冷循环部件。 | compressor、condenser、evaporator、refrigerant circuit。 | 不等于 CDU。 | P1 | pending_audit |
| DC-L3-005-008-002 | 3 | DC-L2-005-008 | 设施侧热交换器 | 数据中心冷源与液冷或水系统之间的换热设备。 | plate heat exchanger、shell-and-tube、gasket、cleaning。 | CDU 内换热器另列。 | P1 | pending_audit |
| DC-L3-005-008-003 | 3 | DC-L2-005-008 | 冷却塔填料 / 风机 | 冷却塔中用于散热、气液接触和通风的部件。 | fill media、fan、motor、spray nozzle、drift eliminator。 | 不泛化到普通建筑 HVAC。 | P2 | pending_audit |
| DC-L3-005-008-004 | 3 | DC-L2-005-008 | 冷源泵组 / 水处理 | 设施侧冷冻水、冷却水循环和水质控制设备。 | pump group、water treatment、filter、chemical dosing。 | 液冷二次侧泵另列。 | P2 | pending_audit |
| DC-L3-005-008-005 | 3 | DC-L2-005-008 | 冷源控制阀 / 传感器 | 设施侧冷源流量、温度、压力和能效控制硬件。 | control valve、temperature sensor、pressure sensor、controller。 | 纯楼宇软件不在此列。 | P2 | pending_audit |
| DC-L3-005-008-006 | 3 | DC-L2-005-008 | 节水 / 自然冷却接口 | 支撑 free cooling、节水和高能效冷源架构的接口设备。 | economizer、dry cooler、adiabatic module、control interface。 | 只作为设施侧热管理节点。 | P2 | pending_audit |
| DC-L3-005-009-001 | 3 | DC-L2-005-009 | 漏液检测线缆 / 点传感器 | 液冷系统中定位泄漏的线型或点式传感器。 | leak detection cable、spot sensor、conductivity sensor。 | 与流量压力传感器分开。 | P1 | pending_audit |
| DC-L3-005-009-002 | 3 | DC-L2-005-009 | 漏液控制器 / 报警模块 | 接收漏液信号、触发报警、联动关断的控制硬件。 | controller、alarm module、relay、communication interface。 | 不等于数据中心综合安防。 | P1 | pending_audit |
| DC-L3-005-009-003 | 3 | DC-L2-005-009 | 自动关断阀 / 联动硬件 | 漏液或异常状态下执行隔离、旁路或停机的硬件。 | shutoff valve、solenoid valve、interlock module。 | 控制阀若作为常规流量控制归泵阀节点。 | P1 | pending_audit |
| DC-L3-005-009-004 | 3 | DC-L2-005-009 | 热控制本地硬件 | 液冷系统本地热控制、冗余策略和安全联动硬件。 | thermal controller、edge controller、sensor hub、I/O board。 | 纯算法或运维软件不在此列。 | P2 | pending_audit |
| DC-L3-005-009-005 | 3 | DC-L2-005-009 | 监控集成接口 | 将液冷状态接入 BMC、DCIM 或本地控制系统的接口硬件。 | gateway、communication module、protocol converter。 | DCIM 软件不进入主表。 | P2 | pending_audit |
| DC-L3-005-010-001 | 3 | DC-L2-005-010 | TIM 导热垫 / 导热凝胶 | 芯片、封装、板级器件与冷板或散热件之间的导热界面材料。 | thermal pad、gel、phase-change material、dispensing。 | 封装 underfill 另属封装链。 | P1 | pending_audit |
| DC-L3-005-010-002 | 3 | DC-L2-005-010 | 均热板 / Vapor chamber | 板级或模块级局部热扩散结构。 | vapor chamber、heat pipe、wick structure、working fluid。 | 不等于设施侧热交换器。 | P1 | pending_audit |
| DC-L3-005-010-003 | 3 | DC-L2-005-010 | 铜/石墨/导热片 | 局部热扩散和界面导热使用的金属、石墨或复合片材。 | copper sheet、graphite sheet、thermal spreader、adhesive。 | 只按板级散热用途归属。 | P2 | pending_audit |
| DC-L3-005-010-004 | 3 | DC-L2-005-010 | 弹簧载荷 / 固定结构 | 保证 TIM 厚度、接触压力和可维护性的机械加载件。 | spring screw、load frame、clip、torque control。 | 机柜结构件不在此列。 | P2 | pending_audit |
| DC-L3-005-010-005 | 3 | DC-L2-005-010 | 热界面可靠性测试 | 对 TIM、均热板和局部散热件进行热阻、老化和循环测试。 | thermal resistance、aging、pump-out test、thermal cycling。 | 只服务热界面材料。 | P2 | pending_audit |

### DC-L1R-006 高性能存储与数据通路链

| node_id | level | parent_node_id | node_name | 精确定义 | Level 4 候选，不在本轮展开 | 唯一归属与边界 | priority | status |
|---|---:|---|---|---|---|---|---|---|
| DC-L3-006-001-001 | 3 | DC-L2-006-001 | NAND package | 企业级 SSD 内的 NAND 封装颗粒。 | NAND die stack、package substrate、wire bonding、test。 | NAND 晶圆另归 DC-L2-006-002。 | P1 | pending_audit |
| DC-L3-006-001-002 | 3 | DC-L2-006-001 | SSD controller | 企业级 SSD 中负责协议、纠错、映射和数据调度的主控芯片。 | controller SoC、ECC、FTL、NVMe interface。 | 控制器本体也可从 DC-L2-006-004 深拆，需避免重复。 | P1 | pending_audit |
| DC-L3-006-001-003 | 3 | DC-L2-006-001 | SSD DRAM cache | SSD 内部用于映射表、缓存和性能优化的 DRAM。 | DRAM chip、cache interface、ECC、power-loss protection。 | 不等于 HBM。 | P2 | pending_audit |
| DC-L3-006-001-004 | 3 | DC-L2-006-001 | SSD PCB / 电源保护 | 企业级 SSD 的板级承载、电源、掉电保护和连接接口。 | SSD PCB、PLP capacitor、PMIC、connector。 | PCB 若按材料深拆需保留存储用途边界。 | P2 | pending_audit |
| DC-L3-006-001-005 | 3 | DC-L2-006-001 | SSD 固件 | SSD 控制、纠错、寿命管理、QoS 和故障恢复固件。 | FTL firmware、wear leveling、telemetry、error recovery。 | 作为设备固件保留，不进入软件生态附表。 | P2 | pending_audit |
| DC-L3-006-001-006 | 3 | DC-L2-006-001 | SSD 散热 / 测试 | 企业级 SSD 热设计、压力测试、寿命测试和可靠性验证。 | heat spreader、thermal pad、burn-in、endurance test。 | 存储服务器系统测试另列。 | P1 | pending_audit |
| DC-L3-006-002-001 | 3 | DC-L2-006-002 | NAND wafer / die | 3D NAND 存储晶圆和切割后的裸片。 | wafer process、die sort、yield map、dicing。 | 不等于 SSD 封装颗粒。 | P1 | pending_audit |
| DC-L3-006-002-002 | 3 | DC-L2-006-002 | 3D NAND 堆叠结构 | NAND 存储单元的多层堆叠、沟道和字线结构。 | channel hole、wordline、staircase、string stack。 | 结构节点，不做制程瓶颈判断。 | P1 | pending_audit |
| DC-L3-006-002-003 | 3 | DC-L2-006-002 | NAND 刻蚀 / 沉积工艺 | 3D NAND 中高深宽比刻蚀、沉积和清洗工艺。 | etch、deposition、cleaning、metrology。 | 与逻辑芯片先进制程分开。 | P1 | pending_audit |
| DC-L3-006-002-004 | 3 | DC-L2-006-002 | NAND 封装测试 | NAND die 的堆叠封装、测试和分级。 | package、probe、burn-in、binning、reliability。 | SSD 整盘测试另列。 | P1 | pending_audit |
| DC-L3-006-002-005 | 3 | DC-L2-006-002 | NAND 颗粒筛选 / 质量分级 | 按企业级耐久、温度、错误率和可靠性要求筛选 NAND。 | grading、enterprise qualification、error rate、retention test。 | 不等于 SSD 主控算法。 | P1 | pending_audit |
| DC-L3-006-003-001 | 3 | DC-L2-006-003 | 磁盘盘片 / 介质 | 企业级 HDD 用磁记录盘片和介质。 | platter、magnetic media、coating、lubrication。 | 只按冷数据存储用途归属。 | P2 | pending_audit |
| DC-L3-006-003-002 | 3 | DC-L2-006-003 | 磁头 / 读写组件 | HDD 中读写数据的磁头、悬臂和定位组件。 | head、slider、HAMR/MAMR component、suspension。 | 不涉及光模块光头。 | P2 | pending_audit |
| DC-L3-006-003-003 | 3 | DC-L2-006-003 | 主轴马达 / 执行器 | HDD 中驱动盘片旋转和磁头定位的机电组件。 | spindle motor、voice coil motor、bearing、actuator。 | 只属于 HDD。 | P2 | pending_audit |
| DC-L3-006-003-004 | 3 | DC-L2-006-003 | HDD 控制板 / 固件 | HDD 读写、纠错、缓存和接口控制硬件与固件。 | controller PCB、preamp、firmware、SATA/SAS interface。 | 与 SSD 主控分开。 | P2 | pending_audit |
| DC-L3-006-003-005 | 3 | DC-L2-006-003 | HDD 密封 / 测试校准 | 企业级 HDD 密封、氦气、振动、温度和读写校准测试。 | hermetic seal、helium fill、calibration、burn-in。 | 只服务 HDD。 | P2 | pending_audit |
| DC-L3-006-004-001 | 3 | DC-L2-006-004 | SSD controller SoC | 存储控制器芯片主体。 | CPU core、NAND interface、PCIe controller、SRAM。 | 与 SSD 设备节点有从属关系。 | P1 | pending_audit |
| DC-L3-006-004-002 | 3 | DC-L2-006-004 | ECC / LDPC 引擎 | 主控中负责纠错、寿命和可靠性的硬件引擎。 | LDPC、BCH、RAID-like protection、error recovery。 | 只属于存储控制器。 | P1 | pending_audit |
| DC-L3-006-004-003 | 3 | DC-L2-006-004 | PCIe / NVMe PHY | SSD 主控连接主机系统的高速接口物理层。 | PCIe PHY、NVMe controller、SerDes、clocking。 | 网络 SerDes 另归网络链。 | P1 | pending_audit |
| DC-L3-006-004-004 | 3 | DC-L2-006-004 | FTL / 固件算法 | NAND 映射、磨损均衡、垃圾回收和 QoS 管理的固件逻辑。 | FTL、wear leveling、garbage collection、QoS。 | 保留为存储设备固件，不等于数据管理软件。 | P2 | pending_audit |
| DC-L3-006-004-005 | 3 | DC-L2-006-004 | 控制器封装与测试 | SSD 主控芯片的封装、电性、热和可靠性测试。 | package、ATE、burn-in、thermal test。 | 不等于 SSD 整盘测试。 | P1 | pending_audit |
| DC-L3-006-005-001 | 3 | DC-L2-006-005 | DDR / LPDDR 缓存芯片 | 存储设备或存储服务器中的缓存 DRAM。 | DDR4/DDR5、LPDDR、ECC、package。 | HBM 归计算链。 | P2 | pending_audit |
| DC-L3-006-005-002 | 3 | DC-L2-006-005 | RDIMM / 内存模组 | 存储服务器中用于缓存、元数据或系统内存的内存模组。 | DIMM PCB、register、PMIC、SPD。 | 只按存储服务器用途归属。 | P2 | pending_audit |
| DC-L3-006-005-003 | 3 | DC-L2-006-005 | ECC / Register / PMIC | 存储缓存内存模组中的纠错、寄存、供电管理器件。 | ECC logic、register clock driver、PMIC、SPD EEPROM。 | 与 GPU HBM 接口不同。 | P2 | pending_audit |
| DC-L3-006-005-004 | 3 | DC-L2-006-005 | 缓存测试与可靠性 | 存储缓存 DRAM 和模组的温度、错误率和兼容性测试。 | memory test、thermal test、ECC validation、compatibility。 | 只服务存储缓存。 | P2 | pending_audit |
| DC-L3-006-006-001 | 3 | DC-L2-006-006 | 存储机箱 / 托盘 | JBOF/JBOD 或存储服务器承载大量盘位的结构和热插拔托盘。 | chassis、drive tray、backplane bracket、airflow design。 | 机柜结构另列。 | P1 | pending_audit |
| DC-L3-006-006-002 | 3 | DC-L2-006-006 | NVMe backplane | 存储服务器中连接大量 SSD 的背板或中板。 | backplane PCB、connector、retimer interface、power plane。 | 若只作结构支撑需标边界。 | P1 | pending_audit |
| DC-L3-006-006-003 | 3 | DC-L2-006-006 | PCIe switch / Expander | 存储服务器中扩展 PCIe/NVMe 或 SAS/SATA 通路的芯片和板卡。 | PCIe switch、SAS expander、retimer、controller board。 | 主网络交换芯片另归网络链。 | P1 | pending_audit |
| DC-L3-006-006-004 | 3 | DC-L2-006-006 | 存储节点电源 / 散热集成 | 存储服务器内部电源、风扇、散热器和监控集成。 | PSU bay、fan module、air duct、thermal sensor。 | PSU 本体归供配电链。 | P2 | pending_audit |
| DC-L3-006-006-005 | 3 | DC-L2-006-006 | 存储服务器系统测试 | 对存储节点容量、吞吐、热、掉电和可靠性进行测试。 | I/O stress、thermal test、power loss test、burn-in。 | SSD 单盘测试另列。 | P1 | pending_audit |
| DC-L3-006-007-001 | 3 | DC-L2-006-007 | 存储 NIC / HBA | 连接计算节点与存储节点的网卡、HBA 或协议适配卡。 | NIC、HBA、RDMA card、Fibre Channel adapter。 | 与主网络 NIC 有交叉，只按存储路径用途标记。 | P2 | pending_audit |
| DC-L3-006-007-002 | 3 | DC-L2-006-007 | NVMe-oF / RoCE 硬件卸载 | 存储网络协议卸载和低延迟访问相关硬件。 | RDMA offload、NVMe-oF engine、queue processing。 | DPU 主节点在网络链。 | P2 | pending_audit |
| DC-L3-006-007-003 | 3 | DC-L2-006-007 | 存储交换机 / Fabric | 面向存储集群的数据交换设备或 fabric 硬件。 | Ethernet switch、FC switch、storage fabric module。 | 通用 AI 集群交换机另归 DC-L2-002-001。 | P2 | pending_audit |
| DC-L3-006-007-004 | 3 | DC-L2-006-007 | 存储线缆 / 光模块 | 存储路径中使用的 DAC、AOC、光模块和连接器。 | DAC、AOC、optical module、connector、cable test。 | 与网络互连链重叠，需按用途标注。 | P2 | pending_audit |
| DC-L3-006-007-005 | 3 | DC-L2-006-007 | 存储协议一致性测试 | NVMe-oF、RoCE、FC、PCIe 等存储通路协议和性能测试。 | protocol analyzer、traffic generator、latency test、interop。 | 网络通用测试另归 DC-L2-002-011。 | P2 | pending_audit |
| DC-L3-006-008-001 | 3 | DC-L2-006-008 | 磁带库 / LTO 介质 | 长期归档和冷备份用磁带设备与介质。 | tape drive、LTO media、library cartridge、robotics。 | 只属于归档硬件。 | P2 | pending_audit |
| DC-L3-006-008-002 | 3 | DC-L2-006-008 | 冷存储 HDD 阵列 | 低访问频率数据保存的 HDD 阵列和盘柜。 | HDD enclosure、RAID controller、cold storage chassis。 | 企业级 HDD 单盘另列。 | P2 | pending_audit |
| DC-L3-006-008-003 | 3 | DC-L2-006-008 | 备份控制器 / 归档控制板 | 备份归档设备中负责数据路径、介质管理和校验的控制硬件。 | controller board、checksum engine、media management。 | 备份软件策略不在此列。 | P2 | pending_audit |
| DC-L3-006-008-004 | 3 | DC-L2-006-008 | 归档设备电源 / 机箱 | 备份归档硬件的机箱、电源、散热和机械装载结构。 | enclosure、PSU bay、fan、robotic loader。 | PSU 本体按供配电链。 | P2 | pending_audit |

### DC-L1R-007 机柜结构与物理连接链

| node_id | level | parent_node_id | node_name | 精确定义 | Level 4 候选，不在本轮展开 | 唯一归属与边界 | priority | status |
|---|---:|---|---|---|---|---|---|---|
| DC-L3-007-001-001 | 3 | DC-L2-007-001 | 机柜钣金框架 | Rack 机柜主体承重和安装框架。 | steel frame、aluminum frame、welding、riveting。 | 只统计结构，不统计服务器设备。 | P2 | pending_audit |
| DC-L3-007-001-002 | 3 | DC-L2-007-001 | 安装立柱 / 导轨孔位 | 机柜内设备安装、定位和标准孔位结构。 | mounting post、rail hole、U marking、tolerance control。 | 滑轨部件另可归 DC-L2-007-002。 | P2 | pending_audit |
| DC-L3-007-001-003 | 3 | DC-L2-007-001 | 门板 / 侧板 / 通风结构 | 机柜门板、侧板、孔洞、通风和维护结构。 | perforated door、side panel、airflow opening、hinge。 | 不等于交换机机箱。 | P2 | pending_audit |
| DC-L3-007-001-004 | 3 | DC-L2-007-001 | 接地 / 抗震 / 加固件 | 机柜接地、抗震、搬运和承重安全结构。 | grounding bar、seismic bracket、caster、leveling foot。 | 只按 rack 结构归属。 | P2 | pending_audit |
| DC-L3-007-001-005 | 3 | DC-L2-007-001 | 表面处理 / 涂装 | 机柜结构件防腐、绝缘、外观和可靠性处理。 | powder coating、plating、surface treatment、corrosion test。 | 不泛化到所有钣金。 | P2 | pending_audit |
| DC-L3-007-002-001 | 3 | DC-L2-007-002 | 服务器机箱钣金 | 服务器或托盘设备的局部机箱和承载结构。 | chassis、cover、stiffener、EMI shield。 | 整机装配服务不在此列。 | P2 | pending_audit |
| DC-L3-007-002-002 | 3 | DC-L2-007-002 | GPU 托盘 / Sled | 承载 GPU/ASIC 模块、电源和冷却接口的托盘结构。 | sled、tray、alignment pin、load frame。 | GPU 模块本体归计算链。 | P2 | pending_audit |
| DC-L3-007-002-003 | 3 | DC-L2-007-002 | 滑轨 / 导向件 | 服务器、托盘和电源模块插拔、承重和维护用滑轨。 | slide rail、guide rail、bearing、stopper。 | 不等于电气连接器。 | P2 | pending_audit |
| DC-L3-007-002-004 | 3 | DC-L2-007-002 | 锁扣 / 把手 / 紧固件 | 机箱、托盘、滑轨的维护和固定机械件。 | latch、handle、fastener、thumb screw。 | 与热插拔机构交叉，需按功能归属。 | P2 | pending_audit |
| DC-L3-007-002-005 | 3 | DC-L2-007-002 | 结构件表面处理 / 可靠性测试 | 机箱托盘结构件的涂装、防腐、疲劳、振动和跌落测试。 | coating、salt spray、vibration、drop test、cycle test。 | 只按结构件归属。 | P2 | pending_audit |
| DC-L3-007-003-001 | 3 | DC-L2-007-003 | 结构背板 / 支撑板 | 服务器或机柜中主要承担支撑和定位的背板或中板结构。 | stiffener、support plate、alignment feature、bracket。 | 若承载高速信号 PCB，需回到网络或计算 PCB。 | P2 | pending_audit |
| DC-L3-007-003-002 | 3 | DC-L2-007-003 | 板卡加固 / Stiffener | 防止大尺寸 PCB 或模块翘曲、振动和运输损伤的加固件。 | stiffener、backer plate、reinforcement rib、fastener。 | PCB 本体不在此列。 | P2 | pending_audit |
| DC-L3-007-003-003 | 3 | DC-L2-007-003 | 盲插连接器壳体 / 导向结构 | 支撑电源、液冷或高速连接盲插的机械导向与固定结构。 | guide pin、housing、alignment sleeve、floating mount。 | 连接器电气功能按网络或供电归属。 | P2 | pending_audit |
| DC-L3-007-003-004 | 3 | DC-L2-007-003 | 绝缘 / EMI 屏蔽结构 | 背板、中板和连接结构中的绝缘、防护和电磁屏蔽件。 | insulator、EMI gasket、shield can、flame-retardant sheet。 | 不等于电源绝缘件。 | P2 | pending_audit |
| DC-L3-007-003-005 | 3 | DC-L2-007-003 | 中板装配测试 | 结构背板或中板装配后的尺寸、定位、插拔和可靠性测试。 | dimensional test、fit check、insertion test、vibration。 | 电性测试若存在需按功能归属。 | P2 | pending_audit |
| DC-L3-007-004-001 | 3 | DC-L2-007-004 | 线缆托盘 / 走线槽 | 机柜内光纤、铜缆、电源线和管理线的走线支撑结构。 | cable tray、duct、routing channel、bend radius control。 | 线缆本体不在此列。 | P2 | pending_audit |
| DC-L3-007-004-002 | 3 | DC-L2-007-004 | 线缆固定夹 / 扎带 | 固定、分组、标识和保护机柜线缆的低价值结构件。 | clamp、tie、clip、strain relief、label holder。 | 不等于高速连接器。 | P2 | pending_audit |
| DC-L3-007-004-003 | 3 | DC-L2-007-004 | 光纤保护 / 弯曲半径结构 | 保护光纤弯曲半径、插拔和维护通道的结构。 | fiber guide、bend limiter、protective sleeve。 | 光纤和连接器本体归网络链。 | P2 | pending_audit |
| DC-L3-007-004-004 | 3 | DC-L2-007-004 | 线缆标识 / 运维辅助件 | 机柜内线缆标签、色标、维护辅助和防误插结构。 | label、tag、color coding、service guide。 | 运维服务不在主表。 | P2 | pending_audit |
| DC-L3-007-005-001 | 3 | DC-L2-007-005 | 铜排绝缘支撑件 | 高电流铜排安装中的绝缘支柱、隔离和固定件。 | insulating support、standoff、spacer、bracket。 | 铜排电气功能归供配电链。 | P2 | pending_audit |
| DC-L3-007-005-002 | 3 | DC-L2-007-005 | 铜排防护罩 / 盖板 | 防触电、防短路和维护安全的铜排防护结构。 | protective cover、shield、transparent guard、labeling。 | 只统计结构安全件。 | P2 | pending_audit |
| DC-L3-007-005-003 | 3 | DC-L2-007-005 | 爬电距离 / 安全间距结构 | 支撑高电流配电安全距离、绝缘和防护的结构设计。 | creepage design、clearance spacer、insulation barrier。 | 不等于开关柜电气保护。 | P2 | pending_audit |
| DC-L3-007-005-004 | 3 | DC-L2-007-005 | 阻燃 / 绝缘材料 | 铜排固定和绝缘结构中的阻燃、绝缘和机械材料。 | flame-retardant plastic、FRP、epoxy sheet、ceramic insulator。 | 按结构用途归属。 | P2 | pending_audit |
| DC-L3-007-006-001 | 3 | DC-L2-007-006 | 管夹 / 管路支架 | 机柜或服务器内固定液冷管路的夹具和支撑件。 | pipe clamp、bracket、guide rail、rubber insert。 | 液冷管路本体归热管理链。 | P2 | pending_audit |
| DC-L3-007-006-002 | 3 | DC-L2-007-006 | 防滴漏托盘 / 导流结构 | 液冷维护或异常时收集、导流和隔离液体的结构件。 | drip tray、drain guide、splash guard。 | 漏液传感器另归热管理链。 | P2 | pending_audit |
| DC-L3-007-006-003 | 3 | DC-L2-007-006 | 管路保护套 / 防磨件 | 防止液冷管路磨损、压伤、折弯和误操作的保护结构。 | protective sleeve、bend guard、abrasion pad、grommet。 | 不等于软管本体。 | P2 | pending_audit |
| DC-L3-007-006-004 | 3 | DC-L2-007-006 | 液冷维护空间 / 快拆支撑 | 支撑液冷部件维护、拆装和定位的结构设计。 | service clearance、quick-release support、alignment bracket。 | 快接头功能件归热管理链。 | P2 | pending_audit |
| DC-L3-007-007-001 | 3 | DC-L2-007-007 | 盲插导向结构 | 支持服务器、托盘、电源或液冷模块盲插定位的机械结构。 | guide pin、floating connector mount、alignment rail。 | 电气或流体连接功能另归对应链。 | P2 | pending_audit |
| DC-L3-007-007-002 | 3 | DC-L2-007-007 | 锁扣 / 弹出机构 | 热插拔或快装模块中的锁止、释放和弹出机械件。 | latch、ejector lever、spring mechanism、handle。 | 普通固定件按机箱结构归属。 | P2 | pending_audit |
| DC-L3-007-007-003 | 3 | DC-L2-007-007 | 热插拔笼体 / Cage | 支撑模块插拔、导向、散热和屏蔽的笼体结构。 | module cage、EMI spring、guide rail、retention clip。 | 网络端口 cage 如承担高速接口需标网络边界。 | P2 | pending_audit |
| DC-L3-007-007-004 | 3 | DC-L2-007-007 | 插拔寿命 / 误操作测试 | 快装和热插拔机构的循环寿命、容差、防呆和可靠性测试。 | cycle test、mis-insertion test、vibration、force test。 | 只服务机械机构可靠性。 | P2 | pending_audit |

## 下一轮审计建议表

| audit_item | 目标 | 通过标准 |
|---|---|---|
| 父节点合法性 | 检查所有 Level 3 节点是否只挂在 60 个 allow Level 2 父节点下。 | 不出现 `DC-L2-003-006`、`DC-L2-003-007` 作为父节点。 |
| 层级纯度 | 检查 Level 3 是否仍为产品、器件、材料、工艺、设备、测试或制造服务。 | 不出现公司、股票、涨价、短缺、国产替代、交易弹性等非节点项。 |
| 重叠归属 | 检查 PCB、连接器、测试、电源、散热、线缆和结构件是否按用途唯一归属。 | 同一功能不在计算、网络、供配电、热管理、机柜结构之间重复计数。 |
| 上游可延展性 | 检查每个 Level 3 节点是否能继续拆到 Level 4。 | 每行均有 Level 4 候选或清晰边界。 |
| 优先级合理性 | 检查 P0/P1/P2 是否只表示下钻优先级，不代表瓶颈或投资结论。 | 不把 P0 解释为短缺、卡点或股票弹性。 |

## 机器可读状态

```yaml
artifact_type: ai_chain_level_mapping
task_type: mapping
current_level: 3
parent_audit: docs/ai_chain_disassembly/level_02_audit_2026-05-31.md
parent_level: 2
root_node_id: DC-000
next_required_task: audit_level_3
status: pending_audit
may_enter_next_level: false
level_2_parent_nodes_approved_for_mapping: 60
level_2_parent_nodes_used_in_main_table: 60
level_3_total_nodes: 320
level_2_side_only_nodes_excluded:
  - DC-L2-003-006
  - DC-L2-003-007
live_data_used: false
stock_mapping_included: false
```
