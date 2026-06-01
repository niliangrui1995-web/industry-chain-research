# 高速网络高概率转紧子节点核心供应商深研

日期：2026-06-01

本文件只覆盖用户指定的 6 个高概率转紧子节点：

1. `Retimer / Linear Driver / SerDes 器件 > Retimer SerDes PHY` 中的 224G/lane、200G PAM4 retimer PHY。
2. `Retimer / Linear Driver / SerDes 器件 > CDR / 重定时核心` 中的 AEC/板级 retimer DSP-CDR 核心。
3. `Retimer / Linear Driver / SerDes 器件 > Retimer 封装与测试` 中的低功耗封装、热设计、ATE/系统级验证。
4. `Retimer / Linear Driver / SerDes 器件 > CDR / 重定时核心` 中的 cable-end retimer IC。
5. `网络测试与认证设备 > BERT 误码率测试设备`，聚焦 1.6T/224G electrical/optical BERT。
6. `网络测试与认证设备 > 校准治具 / 认证服务` 中的 HCB/MCB、electrical fixture、第三方认证和 FAE 资源。

## 结论先行

这 6 个节点不是 6 条独立产业链，而是一条连续的验证链：

`224G/200G SerDes PHY -> DSP-CDR / retimer core -> cable-end retimer IC 或板级 retimer -> 低功耗封装和系统级误码测试 -> 1.6T/224G BERT -> HCB/MCB/fixture/认证/FAE`

最值得优先跟踪的核心供应商分三层：

| 层级 | 供应商 | 结论 |
| --- | --- | --- |
| 第一层：直接暴露于 AEC/retimer 主芯片 | Credo、Marvell、MaxLinear、Broadcom | 这几家公司直接提供 224G/200G PAM4 retimer、AEC DSP、SerDes 或完整 AI 网络连接平台。Credo 和 Marvell 是最直接的 cable-end retimer IC/AEC DSP 映射；MaxLinear 是 224G scale-up retimer 新进入者；Broadcom 是平台级 SerDes、Agera retimer、Tomahawk 生态的强供应商。 |
| 第二层：PCIe/CXL 和智能线缆/板级 retimer | Astera Labs、Marvell Alaska P、Broadcom PCIe/CXL retimer | 更偏 AI 服务器、GPU baseboard、PCIe/CXL fabric 和 smart cable。Astera 是最强的公开纯标的之一，但当前公开 Taurus Ethernet SCM 仍以 100G/lane、800G 级别为主，不应直接等同于 224G Ethernet AEC retimer。 |
| 第三层：测试和认证瓶颈 | Keysight、VIAVI、MultiLane、Anritsu | Keysight 和 VIAVI 的 1.6T/224G 证据最强；MultiLane 同时覆盖 224G/lane BERT 与 1.6T OSFP MCB；Anritsu 在 800G、112G、PCIe Gen6 BERT 有强基础，但当前公开证据不足以把它放到 224G/lane BERT 第一梯队。 |

A 股/中资映射要降温处理：截至本次复核，没有看到 A 股公司已经公开证明自己是 224G Ethernet AEC retimer PHY、cable-end retimer IC 或 1.6T/224G BERT 的核心供应商。澜起科技更接近 PCIe/CXL retimer 映射；立讯精密、鸿腾精密、BizLink、UDE 等更接近线缆/连接器/模组和测试客户映射，不是 retimer 主芯片供应商。

## 节点到供应商总表

| 子节点 | 核心供应商 | 证据强度 | 投研判断 |
| --- | --- | --- | --- |
| 224G/lane、200G PAM4 retimer PHY | Credo、Marvell、Broadcom、MaxLinear、Synopsys/Cadence/Alphawave Semi 作为 SerDes IP 上游 | 高 | 真正紧的是已通过大客户互操作、低功耗和长 reach 验证的 200G/224G PAM4 SerDes/retimer，不是普通 PHY。 |
| AEC/板级 retimer DSP-CDR 核心 | Credo、Marvell Alaska A/P、MaxLinear Annapurna、Broadcom Agera/PCIe retimer、Astera Aries | 高 | AEC 和板级 retimer 的价值集中在 DSP-CDR、equalization、FEC/telemetry、firmware 调参和客户 qualification。 |
| Retimer 低功耗封装、热设计、ATE/系统级验证 | Retimer 厂商自身、OSAT/ATE 隐性供应链、Keysight/MultiLane/VIAVI/Anritsu 系统级验证 | 中高 | 公开资料很少直接披露 OSAT 或 ATE 供应商；此节点更适合跟踪 retimer 厂商交期、库存、良率和系统级测试排队，而不是直接押注某个封测股。 |
| cable-end retimer IC | Credo、Marvell Alaska A、MaxLinear Annapurna、Broadcom Agera/BCM87851 系列、Astera Taurus 作为 100G/lane 级别观察 | 高 | 如果 AEC 替代 DAC 的比例提升，最先转紧的是两端 retimer/DSP IC 和 reference design，而不是普通 Twinax 铜线。 |
| 1.6T/224G electrical/optical BERT | Keysight、VIAVI、MultiLane；Anritsu 为 800G/112G/PCIe Gen6 强供应商 | 高 | 1.6T、224G、AEC、LPO/LRO、FRO、CPO 同时验证，会集中消耗 BERT、error-performance validation 和长期稳定性测试端口。 |
| HCB/MCB、electrical fixture、第三方认证、FAE | MultiLane、Keysight、VIAVI、各大线缆/模块/芯片厂自建实验室和 FAE；第三方认证机构/标准组织 | 高 | 瓶颈很可能不是仪器单机供给，而是 fixture、校准、测试窗口、FAE 和客户认证流程。 |

## 供应商深研

### Credo Technology Group（CRDO）

对应节点：

- 224G/lane、200G PAM4 retimer PHY。
- AEC/板级 retimer DSP-CDR 核心。
- cable-end retimer IC。
- Retimer 系统级验证和调试软件。

核心证据：

- Credo 2026 年 1 月发布 Blue Heron 224G AI scale-up retimer，支持 UALink、ESUN 和 Ethernet，面向延长 cable/backplane links，并称可 full recovery of a 40+dB 224G link，采用 3nm 和 Credo 224G SerDes，量产供货时间指向 CQ3 2026。
- Credo ZeroFlap AEC 页面显示其 AEC 覆盖 100G、200G、400G、800G、1.6T，且在连接器中集成低功耗 retimer、gearbox 和 FEC 电路来保证 56G/112G per lane 的信号完整性。
- Credo FY2026 Q3 SEC 附件披露季度收入 4.07 亿美元，同比增 201.5%，并在管理层评论中明确提到 AECs 和 ICs 持续增长。

投研判断：

Credo 是这轮高概率转紧链条里最直接的纯标的之一。它不是只卖普通线缆，而是把 AEC 模组、retimer/DSP、SerDes、调试工具和客户验证结合在一起。若 224G scale-up copper 进入批量验证，Credo 可能同时受益于主芯片 ASP、AEC 模组价值量、客户认证粘性和软件/诊断工具。

主要风险：

- 客户集中度和大客户节奏变化会显著影响季度收入。
- 若 hyperscaler 在 2026H2 更快转向光互连，AEC 渗透率上行斜率会受压。
- 估值已经反映较高增长预期，业绩弹性和交易弹性不等于安全边际。

### Marvell Technology（MRVL）

对应节点：

- 200G PAM4 AEC DSP/retimer。
- cable-end retimer IC。
- PCIe Gen6/CXL retimer。
- 光 DSP、linear driver 等相邻 AI interconnect 平台。

核心证据：

- Marvell Alaska A 1.6T PAM4 DSP 被公司定义为 active electrical cable 的 PAM4 DSP retimer，面向 AI accelerators、server to ToR、switch-to-switch 等 rack 内短距铜互连；产品 brief 显示其采用 8 条 host-side 200G SerDes 和 8 条 cable-side 200G SerDes，支持 1.6T full-duplex mission-mode traffic。
- Marvell 2025 年 12 月披露 Alaska P PCIe retimer 被 AI 和数据中心基础设施供应商采用，面向 GPU、XPU、CPU、SSD、CXL 等连接，支持 PCIe 6/CXL 3.x，并且可用于 on-board、copper cable 或 optical PCIe cable。

投研判断：

Marvell 是 cable-end retimer IC 的强供应商，但它不是纯 AEC 标的，而是数据中心半导体平台公司。它的优势在于 PAM4 DSP、SerDes、光电 DSP、PCIe/CXL retimer 和客户生态。相较 Credo，Marvell 的弹性会被更大的收入基数摊薄，但供应链话语权和产品组合更深。

主要风险：

- AEC retimer/DSP 在公司总收入中的贡献可能不够透明。
- 与 Credo、Broadcom、MaxLinear 的竞争会压缩单一产品的超额利润。
- 光 DSP、custom silicon 和存储/网络周期会影响公司整体估值。

### MaxLinear（MXL）

对应节点：

- 224G/lane scale-up retimer PHY。
- AEC/on-board retimer DSP-CDR。
- cable-end retimer IC 潜在供应商。

核心证据：

- MaxLinear 2026 年 3 月发布 Annapurna 224G scale-up retimer，称其提供最高 1.6Tbps electrical connectivity，可让铜 backplane 和 AEC 在 224Gbps per lane PAM4 下可靠运行。
- 公司披露 Annapurna 有 8-lane 和 16-lane 配置，支持 1.6Tbps 和 3.2Tbps 应用，面向 AEC 和 on-board retimer deployment，并支持 ESUN、UALink、Ultra Ethernet 等 scale-up 协议。

投研判断：

MaxLinear 是这轮链条中的“新进入高弹性观察标的”。Annapurna 的定位非常贴合用户指定的前两个节点，但当前还需要继续跟踪样品、客户 design win、量产窗口和 cable partner 采用情况。它的投资属性更像“产品周期反转 + 新品切入”，确定性低于 Credo/Marvell/Broadcom。

主要风险：

- 新产品从发布到大客户量产仍有验证风险。
- 224G scale-up copper 需求若延后，Annapurna 收入兑现会滞后。
- 公司历史业务波动可能使 retimer 产品信号被整体业绩噪声覆盖。

### Broadcom（AVGO）

对应节点：

- 200G/224G SerDes 平台。
- Agera retimer、PCIe/CXL retimer、AEC/optical DSP 生态。
- AI switch ASIC 与 retimer/SerDes 系统级 reference design。

核心证据：

- Broadcom Tomahawk 6 公开资料显示其支持 100G/200G SerDes 和 CPO，Tomahawk 6 family 关键收益包括 200G 或 100G PAM4 SerDes，以及 scale-up/scale-out AI 网络能力。
- Broadcom 把 Tomahawk、Jericho、Thor NIC、Agera retimers、Sian optical DSP、CPO 和 SDK 描述为端到端 Ethernet AI 平台。
- Broadcom OFC 2026 资料披露其展示 200G/lane Ethernet retimers & AECs，包括 Agera 3，覆盖 long-reach Ethernet backplane、front-port 和 extended AEC。

投研判断：

Broadcom 是“平台控制型”核心供应商，而不是单一 retimer 纯标的。其强处在于 switch ASIC、SerDes、retimer、NIC、optical DSP、CPO 的组合。若 AI 后端网络从 800G 向 1.6T/3.2T 演进，Broadcom 对生态的影响会很强，但 AEC/cable-end retimer 的收入弹性可能被平台大盘稀释。

主要风险：

- 标的太大，retimer 节点本身很难成为交易的唯一驱动。
- 自研 ASIC、NVIDIA/自有互连路线和客户自研网络芯片会影响市场份额。
- 平台优势强，但估值更多由 AI ASIC、VMware、switch ASIC 大周期共同决定。

### Astera Labs（ALAB）

对应节点：

- 板级 PCIe/CXL Smart DSP retimer。
- PCIe/CXL smart cable module。
- Ethernet smart cable module 的 100G/lane 级别观察。

核心证据：

- Astera Aries PCIe/CXL Smart DSP Retimers 页面显示 Aries 6 正在量产爬坡，面向 PCIe 6.x/CXL 3.x，支持 AI 和 cloud infrastructure，强调低功耗、热设计、系统互操作和 50+ endpoints testing。
- Aries Smart Cable Modules 支持 PCIe 6/5/4 和 CXL over Active Electrical Cables，应用于 multi-rack GPU clustering，reach up to 7m。
- Taurus Ethernet Smart Cable Modules 面向 200G/400G/800G Ethernet AEC，公开页面显示其为 100G/lane Ethernet connectivity，支持 switch-to-switch 和 switch-to-server。
- Astera 2026 Q1 财报显示收入 3.084 亿美元，同比增 93%，并提到 PCIe 6 AI fabric 和 signal conditioning portfolio 增长。

投研判断：

Astera 是 AI 服务器 retimer 和智能连接的高质量标的，但要精确映射：它在用户这次指定的“224G/lane、200G PAM4 Ethernet AEC retimer”上，公开证据弱于 Credo、Marvell、MaxLinear、Broadcom。Astera 更强的是 PCIe/CXL retimer、GPU baseboard、smart cable 和 fabric switch，适合放在“板级 retimer 和 PCIe/CXL scale-up fabric”子节点，而不是直接当 224G Ethernet AEC 主芯片标的。

主要风险：

- 如果投研问题是 224G Ethernet AEC/cable-end retimer，Astera 的公开产品证据需要继续验证。
- 估值高度依赖 AI connectivity 叙事，客户节奏和产品路线变化会放大波动。
- 与 Broadcom/Marvell/Credo 的边界需要按协议和端口速率逐项拆开。

### Synopsys、Cadence、Alphawave Semi：SerDes PHY IP 上游

对应节点：

- 224G Ethernet PHY IP。
- custom ASIC、retimer、switch/NIC/AI accelerator 的上游设计 IP。

核心证据：

- Synopsys 224G Ethernet PHY IP 支持 200G/400G/800G/1.6T Ethernet 和 UALink 200G，面向 high-performance data center applications，并强调 DSP-based receiver、CDR 和内建 BER tester/eye monitor。
- Cadence 224G-LR SerDes PHY IP 基于 TSMC N3E，已披露 first-pass silicon success。
- Alphawave Semi AthenaCORE 支持 10Gbps 到 224Gbps 的 Ethernet、PCIe 和 CXL 相关 SerDes 应用。

投研判断：

这些公司不是 cable-end retimer IC 的直接供应商，但它们决定很多 ASIC 或 retimer 厂商能否快速拿到成熟 224G SerDes hard IP。若 224G 设计窗口集中，SerDes IP 授权、验证服务和 ecosystem support 也会受益。对股票弹性而言，Synopsys/Cadence 更大更分散，节点弹性弱于 Credo/Marvell/MaxLinear。

## 测试、BERT、fixture 和认证供应商

### Keysight（KEYS）

对应节点：

- 1.6T/224G interconnect validation。
- BERT、BER/FEC error-performance validation。
- 认证、FAE、长期测试和系统级验证。

核心证据：

- Keysight 2026 年 3 月发布第二代 1.6T Ethernet interconnect error-performance validation portfolio，明确覆盖 passive copper DAC、ACC、LPO、LRO，并提到 AEC 用于 rack 内和 intra-rack 7-9m。
- Keysight 指出 224G interconnects 的 DSP、retimer、linear amplifier 需要复杂 tuning，完整 assembly 需要多轮性能评估；INPT-1600GE 和 AresONE 1600GE 可在真实场景中测量 error performance。
- Keysight FITS-8CH 用于 high-speed optical and copper interconnect 的 BER 和 FEC validation，覆盖 53G、106G、212G PAM4 electrical lanes，并有 UDE 对 1.6T AEC BER-per-lane 验证的客户背书。

投研判断：

Keysight 是这 6 个节点中测试端确定性最高的供应商。真正紧的可能不是一台仪器，而是“硬件平台 + 软件 + 校准 + 应用工程师 + 长时间测试窗口”的组合。它更适合看作 1.6T/224G 验证周期的卖铲人。

### VIAVI（VIAV）

对应节点：

- 1.6T high-speed Ethernet testing。
- 224G SerDes 生态验证。
- pluggable、switch/router、network equipment 测试。

核心证据：

- VIAVI 2024 年发布 ONE-1600，称其面向 emerging 1.6Tb/s ecosystem based on 224G SERDES，适配 OSFP1600 和 QSFP-DD1600。
- ONE LabPro 平台支持最多 64 个 1.6Tb/s test ports 或 128 个 800Gb/s test ports，服务 chips、pluggables、switching/routing devices 和 networks。
- 早期客户包括 InnoLight 和 Lumentum，说明其测试平台已进入 1.6T 光模块和高速网络设备开发链条。

投研判断：

VIAVI 在 1.6T optical/electrical Ethernet testing 上证据强。与 Keysight 相比，它更偏网络测试、lab/production platform 和 Ethernet test port 密度，适合跟踪 1.6T 光模块、pluggable 和网络设备量产验证。

### MultiLane

对应节点：

- 224G/lane BERT。
- 1.6T OSFP Module Compliance Board。
- Loopback、CMIS、TDR、thermal test、compliance/interop service。

核心证据：

- MultiLane 官网列出 ML7008F-LFT，描述为 224Gbps/lane BERT，具备 40dB 以上 Rx equalization、real-hardware FEC、BLER 和 link training。
- 同一页面列出 ML4064-MCB-224，标注为 1.6T Module Compliance Board、OSFP、Best-in-Class SI。
- MultiLane 自称高速度 I/O 和 AI networking 测试设备供应商，并提供 compliance/interop test services、SI design/consultancy services。

投研判断：

MultiLane 是 HCB/MCB、loopback、224G BERT 和实验室级工具的关键供应商。它未必是大型上市交易标的，但对判断 fixture/认证服务是否转紧非常有用。若模块厂和线缆厂都同时做 1.6T/224G qualification，MultiLane 这类供应商的交期和服务排队时间会直接反映瓶颈。

### Anritsu

对应节点：

- 800G/112G PAM4 BERT。
- PCIe Gen6、USB、Thunderbolt 等高速 PHY 层测试。
- 224G/1.6T 的二线或过渡观察。

核心证据：

- Anritsu MP1900A 是 8-slot modular high-performance BERT，支持 NRZ/PAM4 高速网络接口和 PCIe/USB 等总线接口的 PHY 层测量。
- 公开页面列出 target applications 包括 100G/200G/400G/800G Ethernet、CEI-112G、PCIe Gen1-6、Optical module、SERDES、AOC 等。

投研判断：

Anritsu 是高速 BERT 老牌供应商，但这次用户指定的是 1.6T/224G electrical/optical BERT。当前公开资料对 224G/lane 的直接证据弱于 Keysight、VIAVI、MultiLane。因此它可以放入测试设备观察池，但不应在 224G/lane BERT 排名里压过 Keysight/VIAVI/MultiLane。

## 封装、热设计、ATE 和系统级验证怎么映射

这个子节点最容易被误解。224G retimer 转紧时，确实会拉动封装、散热、ATE 和系统级验证，但公开资料通常不会披露某个 retimer 采用哪家 OSAT 或哪台 ATE。因此这里不能简单把 ASE、Amkor、长电科技、通富微电、日月光、Advantest、Teradyne 都列为“核心受益供应商”。

更合理的映射方式：

| 层级 | 应该跟踪什么 | 可跟踪对象 |
| --- | --- | --- |
| 芯片厂内部 | retimer 量产良率、封装热阻、功耗、RMA、firmware 更新、客户 qualification cycle | Credo、Marvell、MaxLinear、Broadcom、Astera 的交期、库存、收入指引和技术发布 |
| 系统级验证 | BERT 长时间测试、FEC/BER、眼图、链路稳定性、热插拔、真实设备连接测试 | Keysight、VIAVI、MultiLane、Anritsu、线缆/模块厂自建实验室 |
| OSAT/ATE 隐性层 | 高速 mixed-signal 芯片封装、热设计、ATE 测试时间、probe/socket、system-level test | 需要后续通过公司公告、供应链访谈或拆机确认，不宜当前直接下核心结论 |
| 客户认证 | 大客户平台认证、FAE 调参、HCB/MCB/fixture 复用、第三方实验室排队 | 芯片厂 FAE、线缆/模块厂 FAE、第三方测试实验室、标准组织活动 |

投研动作上，封装测试节点更适合作为 retimer 主芯片公司的交付约束跟踪项，而不是单独作为 A 股封测股推荐逻辑。

## A 股和中资映射

| 公司/区域 | 映射强度 | 对应节点 | 判断 |
| --- | --- | --- | --- |
| 澜起科技 | 中 | PCIe/CXL retimer、服务器互连 | 更接近 Astera/Marvell Alaska P 的 PCIe/CXL retimer逻辑，不是已验证的 224G Ethernet AEC cable-end retimer IC。需要用年报和产品公告继续核验。 |
| 立讯精密、鸿腾精密、BizLink 等连接/线缆厂 | 中低到中 | AEC/高速线缆模组、连接器、装配、测试 | 可能参与 AEC/高速互连模组和连接器装配，但核心瓶颈在 retimer/DSP IC、认证和测试，不在普通线材。不能直接映射为 224G retimer 主芯片。 |
| UDE 等台系高速互连厂 | 中 | 1.6T AEC 测试客户、模组/线缆 | Keysight FITS-8CH 资料中出现 UDE 对 1.6T AEC BER-per-lane 验证需求的背书，说明其是高速互连验证生态的一部分，但不是 retimer IC 供应商。 |
| 中际旭创、新易盛、光迅科技等光模块公司 | 低到中 | 1.6T 光模块测试/校准相邻节点 | 与 BERT/optical testing 有交集，但这次指定节点聚焦 retimer、AEC retimer IC、BERT、fixture，不应混入光模块主线。 |
| 普源精电、鼎阳科技等通用测试仪器 | 低 | 国产测试仪器观察 | 当前没有足够公开证据证明其具备 1.6T/224G BERT 核心地位。可观察国产替代，但不能列入核心供应商。 |

结论：若用户提问某个 A 股公司，模型不能先套节点表。正确流程是先用公司官方产品、年报、客户、收入结构判断它到底卖什么，再映射到节点：

1. 如果公司卖的是 PCIe/CXL retimer，再映射到板级 retimer，不映射到 Ethernet AEC 224G retimer。
2. 如果公司卖的是线缆、连接器或模组装配，只映射到 AEC 模组/认证/测试，不映射到 cable-end retimer IC。
3. 如果公司卖的是光模块，只映射到 optical tester / thermal calibration / aging 等相邻节点，不映射到 retimer 芯片。
4. 如果公司没有 224G/200G PAM4、1.6T、AEC、BERT、HCB/MCB、PCIe Gen6/CXL 3.x 的官方证据，先标为“无法映射/待证据”，不要硬套高概率转紧节点。

## 投资优先级排序

| 排名 | 供应商 | 基本面质量 | 业绩弹性 | 交易弹性 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 1 | Credo | 高 | 高 | 高 | 最直接映射 AEC、retimer/DSP、SerDes 和 AI cluster copper interconnect，但估值和客户集中风险高。 |
| 2 | Marvell | 高 | 中高 | 中 | AEC DSP、PCIe retimer、光 DSP、custom silicon 多线受益；单一节点弹性被公司体量摊薄。 |
| 3 | Keysight | 高 | 中 | 中 | 1.6T/224G 验证端最确定，偏卖铲人，但测试收入在公司整体中仍需拆分。 |
| 4 | Broadcom | 极高 | 中 | 中 | 平台级强者，AI networking 大逻辑很强，但 retimer 节点不是唯一交易主线。 |
| 5 | MaxLinear | 中 | 高 | 高 | Annapurna 若拿到大客户 design win，弹性很高；当前确定性低于前四名。 |
| 6 | Astera Labs | 高 | 中高 | 高 | AI connectivity 纯度高，但本次 224G Ethernet AEC retimer 证据弱于 Credo/Marvell/MaxLinear/Broadcom。 |
| 7 | VIAVI | 中高 | 中 | 中 | 1.6T testing 证据强，但业务更分散。 |
| 8 | MultiLane | 产业链重要度高 | 不适用或低可交易性 | 不适用 | 非典型上市投资标的，但对判断 fixture/MCB/BERT 转紧非常重要。 |

## 后续跟踪指标

| 指标 | 为什么重要 | 观察对象 |
| --- | --- | --- |
| 224G/200G retimer 量产时间 | 判断 retimer PHY 是否从发布进入供给约束 | Credo Blue Heron、MaxLinear Annapurna、Broadcom Agera 3、Marvell Alaska A/P |
| AEC design win 与 cable partner 采用 | 判断 cable-end retimer IC 是否进入订单放大 | Credo、Marvell、MaxLinear、Molex、Amphenol、TE、UDE、BizLink、Luxshare/FIT 等 |
| BERT/fixture 交期与实验室排队 | 判断测试端是否先于主芯片转紧 | Keysight、VIAVI、MultiLane、Anritsu、第三方实验室 |
| 1.6T/224G standards 和客户认证节奏 | 标准冻结和客户认证会触发集中采购与测试 | IEEE 802.3dj、OIF、UEC、UALink、OCP、PCI-SIG |
| Retimer 功耗、热阻、RMA、link flap | 判断低功耗封装和系统级验证是否成为瓶颈 | Retimer 厂商、线缆/模块厂、云厂互操作报告 |
| A 股公司公告是否出现 1.6T、224G、AEC retimer、PCIe Gen6、BERT、HCB/MCB | 防止“概念映射”误判 | 澜起科技、立讯精密、国内测试仪器公司、光模块公司 |

## 参考资料

- Credo: Blue Heron 224G AI scale-up retimer, Business Wire, 2026-01-29. https://www.businesswire.com/news/home/20260129771160/en/Credo-Introduces-Industrys-First-224G-Multiprotocol-AI-Scale-Up-Retimer-Supporting-UALink-ESUN-and-Ethernet
- Credo: ZeroFlap AEC product page. https://credosemi.com/products/zeroflapaec/
- Credo: FY2026 Q3 results, SEC exhibit. https://www.sec.gov/Archives/edgar/data/1807794/000162828026013205/credoq32026ex-9911.htm
- MaxLinear: Annapurna 224G scale-up retimer, 2026-03-16. https://www.maxlinear.com/news/press-releases/2026/maxlinear-unveils-annapurna-224g-scale-up-retimer-to-extend-copper-connectivity-in-ai-data-centers
- Marvell: Alaska A 1.6T PAM4 DSP for AEC press release, 2024-06-27. https://www.marvell.com/company/newsroom/marvell-extends-connectivity-leadership-industry-first-1-6t-pam4-dsp-active-electrical-cables.html
- Marvell: Alaska A 1.6T PAM4 DSP product brief. https://www.marvell.com/content/dam/marvell/en/public-collateral/phys-transceivers/marvell-alaska-a-1-6t-pam4-dsp-product-brief.pdf
- Marvell: Alaska P PCIe retimer adoption, 2025-12-09. https://investor.marvell.com/news-events/press-releases/detail/1001/marvell-announces-adoption-of-its-pcie-retimers-by-leading-ai-and-data-center-infrastructure-providers
- Broadcom: Tomahawk 6 official release, 2025-06-03. https://investors.broadcom.com/news-releases/news-release-details/broadcom-ships-tomahawk-6-worlds-first-1024-tbps-switch
- Broadcom: BCM83628-DIE 1.6T PAM4 PHY product brief. https://docs.broadcom.com/doc/83628-DIE-PB
- Astera Labs: Aries PCIe/CXL Smart DSP Retimers. https://www.asteralabs.com/products/pcie-cxl-smart-dsp-retimers/
- Astera Labs: Aries Smart Cable Modules. https://www.asteralabs.com/products/aries-smart-cable-modules/
- Astera Labs: Taurus Ethernet Smart Cable Modules. https://www.asteralabs.com/products/taurus-ethernet-smart-cable-modules/
- Astera Labs: Q1 2026 results. https://www.asteralabs.com/news/astera-labs-reports-first-quarter-2026-financial-results/
- Synopsys: 224G Ethernet PHY IP. https://www.synopsys.com/designware-ip/interface-ip/ethernet/224g-ethernet-phy-ip.html
- Cadence: 224G-LR SerDes PHY IP on TSMC N3E. https://www.cadence.com/en_US/home/company/newsroom/press-releases/pr/2023/cadence-advances-hyperscale-soc-design-with-expanded-ip.html
- Alphawave Semi: 1G to 224G SerDes. https://awavesemi.com/silicon-ip/phy-ip/1g-224g-serdes/
- Keysight: 1.6T interconnect validation technology, 2026-03-19. https://www.keysight.com/be/en/about/newsroom/news-releases/2026/0319_pr26-056-keysight-expands-1-6t-interconnect-validation-technology-to-include-passive-copper-and-low-power-optics.html
- Keysight: FITS-8CH digital-layer error-performance validation, 2026-03-11. https://www.nasdaq.com/press-release/keysight-expands-digital-layer-error-performance-validation-high-speed-16t
- VIAVI: ONE-1600 1.6Tb/s high-speed Ethernet testing, 2024-09-10. https://investor.viavisolutions.com/news-events/news-releases/news-details/2024/VIAVI-Introduces-1.6Tbs-High-Speed-Ethernet-Testing-For-AI-Workloads/default.aspx
- Anritsu: MP1900A Signal Quality Analyzer-R. https://www.anritsu.com/en-us/test-measurement/products/mp1900a
- MultiLane: 224G/lane BERT and 1.6T MCB product listings. https://www.multilaneinc.com/
