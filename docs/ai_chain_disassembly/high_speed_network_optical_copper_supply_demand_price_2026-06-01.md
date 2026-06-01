# 高速网络与光/铜互连链供需与价格趋势研究表

研究日期：2026-06-01（北京时间）

本稿用于后续投研的节点底稿。节点范围来自本地清洗表 `nodes_mindmap_level_01_to_05_cleaned_2026-05-31.xlsx` 中的 `高速网络与光/铜互连链`：1 个 Level 1、11 个 Level 2、61 个 Level 3、59 个 Level 4 P0。外部证据只用于判断需求、供给约束、价格趋势和反转信号；本地节点表只用于确定研究边界。

## 结论先行

| 结论 | 当前判断 | 投研含义 |
|---|---|---|
| 硬瓶颈集中在少数上游和制造良率环节 | 1.6T 光模块上游 EML/CW laser/InP 外延、主动对准/测试；网络板高端 Low-Dk/Low-Dk2/Low-Dk3 玻纤布与高层 PCB；部分 hyperscaler 锁定的数据中心高密度光纤/连接能力。 | 后续选股不要只看“光模块/交换机”大标签，要拆到高端光芯片、玻纤布、高速 PCB、光纤连接锁单。 |
| 交换 ASIC、NIC/DPU、Retimer/AEC 是高价值软瓶颈 | 技术壁垒高，需求强，但公开证据更多证明“高价值和设计门槛”，尚不足以一概证明行业性缺货。 | 适合做龙头/份额/客户验证研究，不宜直接等同于短缺涨价逻辑。 |
| 光模块是需求最强主线，但价格逻辑是“代际 mix 上行 + 每 bit 成本下降” | 800G 放量、1.6T 进入量产爬坡；老规格 ASP 下行，高端 1.6T、ZR/ZR+、硅光/CPO 相关产品维持高 ASP。 | 研究光模块公司时必须拆：出货代际、客户资格、上游光芯片锁定、良率和单位毛利。 |
| 铜互连不是整体紧缺，机会迁移到有源铜和信号调理 | DAC 本体成熟且价格低；224G/1.6T 场景受 reach、SI、功耗约束，需求向 ACC/AEC、retimer、linear driver、equalizer 迁移。 | 铜链条要看 IC 含量和客户导入，而不是普通线缆吨位。 |
| CPO/OCS 是 6-24 个月后的迁移方向，不是 2026 年的主量产替代 | CPO 光引擎、外置光源、FAU、封装对准、CPO 测试会逐步从软瓶颈走向硬瓶颈；OCS 当前更多是架构验证和特定部署。 | 当前作为前瞻跟踪，不宜把 CPO 预期直接替代 800G/1.6T pluggable 收入。 |

## 判定口径

| 状态 | 定义 |
|---|---|
| 硬瓶颈 | 已看到需求放量，同时存在合格产能、良率、长交期、涨价、LTA 锁单、客户扩产或供给集中约束。 |
| 软瓶颈 | 技术门槛、认证周期、良率或互操作性构成约束，但公开证据不足以证明全行业缺货。 |
| 观察 | 战略价值高或未来可能紧，但当前更像配置/验证/架构选项。 |
| 非独立供需节点 | 属于芯片内部 IP、模块内部功能块或制造子工序，不宜单独做商品价格和供需结论，应并入上一级产品判断。 |

## 主节点研究表

| 本地节点路径 | 研究粒度 | 下游需求传导 | 当前供需关系 | 产品价格 / ASP 趋势 | 关键公司或供应节点 | 反转指标 |
|---|---|---|---|---|---|---|
| AI 数据中心 / 智算中心 > 高速网络与光/铜互连链 > AI 集群交换机 | 800G/1.6T AI 后端交换机系统、line card、switch board、cage/connector | GPU/ASIC 集群从 scale-out 扩到 scale-up/scale-across，端口速率从 400G/800G 走向 1.6T；Dell'Oro 预计 AI 后端交换机支出到 2030 年超过 1000 亿美元，且多数端口已转向 800G，2027 年预计转向 1.6T。 | 软瓶颈。系统需求强，但真正卡点分散在 ASIC、光模块、PCB、连接器、散热和整机认证；机箱/SMT 本身不是硬瓶颈。 | 整机 ASP 随 51.2T/102.4T、800G/1.6T 端口密度上行；同等带宽每 bit 成本长期下降。 | Broadcom Tomahawk/Jericho、Cisco/Acacia、Marvell Teralynx、NVIDIA Spectrum、Arista、Accton/智邦、Celestica、Delta 等。 | 云厂商 capex 延后、800G 库存堆积、1.6T 认证延期、光模块或 PCB 供给释放后整机交期缩短。 |
| AI 集群交换机 > 交换机主板 / Line card 装配 > SMT / line card / switch board / connector / cage | 交换机板卡装配与高速 I/O 结构件 | 端口密度上升带来板卡层数、背钻、阻抗控制、连接器密度和热设计升级。 | 板卡制造靠近软瓶颈；普通 SMT 非瓶颈，224G/1.6T 高速连接器和 cage 是局部约束。 | 普通装配价格稳定；高端 line card、OSFP/QSFP-DD cage、低损耗连接器单端口价值量提升。 | TE、Molex、Amphenol、Samtec、Luxshare Precision、富士康/工业富联、Accton 体系等。 | 连接器交期恢复、交换机 ODM 毛利回落、同端口规格报价下行。 |
| 高速网络与光/铜互连链 > 交换芯片 / Switch ASIC | Switch ASIC、SerDes、packet processor / traffic manager | AI 后端网络要求高 radix、低时延、拥塞控制、RoCE/UEC 适配、遥测和 AI-aware routing；102.4T ASIC 已出现，200G/224G SerDes 进入新周期。 | 高价值软瓶颈。ASIC 设计和验证是硬技术门槛，但公开证据更多证明迭代门槛与集中度，不等于行业性缺货。 | 新代际 ASIC 单颗价值高，系统 ASP 上行；长期每 bit 成本下降。NRE、先进制程、IP 和封测成本抬高门槛。 | Broadcom Tomahawk 6 支持 102.4Tbps、200G/100G PAM4 SerDes、长距被动铜和 CPO 选项；Marvell Teralynx 10 51.2T 已量产；Cisco Silicon One、NVIDIA Spectrum。 | 新 ASIC 多供应商放量、客户从单一路线转多源、同规格交换机价格快速下行。 |
| 交换芯片 / Switch ASIC > SerDes IP / PHY > PAM4 SerDes / CDR / equalization / PLL | 交换芯片内高速 PHY/IP | 800G 到 1.6T 端口需要 100G/200G/224G lane；铜背板/线缆 reach 和误码率压力上升。 | 软瓶颈，偏设计能力瓶颈。SerDes 是核心壁垒，但多数以 ASIC、retimer 或 PHY 芯片形式体现，不宜单独看现货供需。 | 授权/IP 价值和芯片面积成本上升；单独 IP 没有透明市场价格。 | Broadcom、Marvell、Synopsys、Cadence、Rambus、Credo、MaxLinear 等。 | 224G SerDes 设计失败率下降、IP 授权竞争加剧、同类芯片毛利率下降。 |
| 交换芯片 / Switch ASIC > Packet processor / Traffic manager > parser / scheduler / buffer manager / congestion control | 交换 ASIC 内转发和拥塞控制逻辑 | AI 训练/推理网络需要低 tail latency、lossless/near-lossless fabric、拥塞感知和遥测。 | 非独立供需节点。它决定芯片和系统竞争力，但不是单独采购商品。 | 价值反映在 ASIC 份额、软件生态和系统溢价；无独立 ASP。 | Broadcom、Cisco、Marvell、NVIDIA、Arista EOS/SONiC 生态。 | UEC/UALink/SONiC 标准化降低差异，客户不再为特定转发特性付溢价。 |
| 高速网络与光/铜互连链 > NIC / DPU / SmartNIC | 400G/800G NIC、SuperNIC、DPU、SmartNIC | GPU 节点到交换机的端点带宽提升；RDMA/RoCE、拥塞控制、安全隔离、存储/网络卸载增加 NIC/DPU 价值量。 | 软瓶颈。需求强，重点在客户认证、驱动/固件、协议栈互操作性和端到端平台绑定；不是普通网卡缺货。 | 800G NIC/DPU ASP 高于 400G；DPU/SmartNIC 因 SoC、内存、固件和安全功能有更高价值。 | NVIDIA ConnectX/BlueField、Broadcom Thor、Marvell、Intel、AMD Pensando。 | 云厂自研端点替代、RDMA 互操作问题、NIC 降配或由 switch 侧承担更多能力。 |
| NIC / DPU / SmartNIC > Ethernet 控制器 / MAC > MAC / PCS / FEC / flow control / time sync | NIC 内以太网控制逻辑 | 与 800G 端点、RoCE、PTP/同步、FEC 和链路诊断绑定。 | 非独立供需节点，随 NIC/DPU 芯片整体判断。 | 无独立商品 ASP；价值体现在 NIC/DPU 代际和毛利。 | NVIDIA、Broadcom、Marvell、Intel、AMD。 | 标准化后差异缩小，客户从高端 DPU 回到低价 NIC。 |
| NIC / DPU / SmartNIC > RDMA / RoCE 卸载引擎 > RDMA engine / RoCE logic / queue pair / transport offload | NIC/DPU 协议卸载 | 大模型训练和分布式推理需要低时延、高带宽、低 CPU 开销；网络效率直接影响 GPU 利用率。 | 软瓶颈。关键在端到端调优、固件稳定性和生态绑定，不是单颗部件短缺。 | 高端 NIC/DPU 的价格和毛利支撑项；无独立 ASP。 | NVIDIA、Broadcom、Marvell、Cisco/AMD 生态。 | 云厂软件栈绕开专用卸载、UEC/标准以太网降低专有溢价。 |
| NIC / DPU / SmartNIC > NIC SerDes / PHY > SerDes / retimer interface / PLL / equalizer | NIC 端高速 PHY | 800G/1.6T 端点、PCIe Gen6/CXL 和长通道板级互连推升 PHY 难度。 | 软瓶颈，和 retimer/AEC 节点共振。 | 高速 PHY 价值随 lane speed 上行；每 bit 成本随规模下降。 | NVIDIA、Broadcom、Marvell、Credo、Astera、MaxLinear。 | PCIe/CXL 平台延期、端点速率升级放缓。 |
| 高速网络与光/铜互连链 > 光模块 / 光收发器 | 800G/1.6T pluggable、LPO/LRO、ZR/ZR+ 光模块 | AI 集群互连带来 800G+ 光模块高速增长。TrendForce 预计 AI 光收发器市场从 2025 年 165 亿美元增长至 2026 年 260 亿美元，增速超过 57%。 | 强需求 + 局部硬瓶颈。模块总装不是最硬卡点，卡点在 EML/CW laser、主动对准、热管理、测试和 1.6T 客户资格。 | 400G/800G 老规格每 bit ASP 下行；1.6T、200G/lane、ZR/ZR+、LPO/硅光新品维持高 ASP 和高 BOM。整体收入 mix 上行。 | Coherent、Lumentum、Applied Optoelectronics、Innolight、新易盛、中际旭创、光迅科技、博创科技、Marvell/Broadcom/Cisco Acacia 等。 | 上游光芯片扩产兑现、1.6T 良率快速提升、云厂采购节奏放缓、模块库存天数上升。 |
| 光模块 / 光收发器 > EML / Laser chip > EML / DFB laser / InP epitaxy / reliability test | 200G/lane EML、DFB/CW laser、InP 外延和可靠性筛选 | 1.6T 光模块、LPO/CPO 外置光源、硅光方案都要消耗高可靠激光器；TrendForce 明确指出 EML、CW laser 是光模块扩产主要瓶颈之一。 | 硬瓶颈，尤其 200G/lane EML、CW laser、InP 外延和可靠性筛选。800G 已扩产但仍紧，1.6T 更紧。 | 高端 EML/CW laser ASP 和毛利受益；老规格 DFB/EML 价格随产能释放下行。无公开稳定单颗报价，需用供应商 mix、光芯片收入和毛利验证。 | Lumentum、Coherent、Broadcom、AOI、三菱电机、住友、ELASER、LuxNet 等。 | Coherent/Lumentum/AOI 扩产后交期缩短，客户双供通过，1.6T 模块良率提升导致激光器报价松动。 |
| 光模块 / 光收发器 > Silicon photonics / InP PIC > SiPh modulator / InP PIC / grating coupler / waveguide | 硅光和 InP PIC | DSP 功耗、光电集成、CPO/LPO 和 1.6T 以上代际推动 SiPh/PIC 渗透。 | 软瓶颈到未来硬瓶颈。当前不是全行业缺片，核心约束是 foundry PDK、耦合、封装、良率、客户 qualification。 | 硅光长期目标是降功耗和每 bit 成本；短期 1.6T/CPO 高端方案 ASP 高，成本也高。 | Intel、Coherent、Lumentum、Broadcom、Marvell、NVIDIA、TSMC COUPE/Tower+Innolight 等。 | Pluggable 传统 EML 路线继续占优、硅光良率/可靠性不达标、CPO 导入延后。 |
| 光模块 / 光收发器 > DSP > DSP ASIC / FEC / equalization / ADC/DAC | 光模块 DSP | 800G/1.6T PAM4、相干 ZR/ZR+、FEC 和 equalization 推升 DSP 算力、制程和功耗要求。 | 软瓶颈。1.6T 3nm/2nm DSP、coherent DSP 是局部紧张和高壁垒环节，但模块路线正尝试 LPO/LRO 降低 DSP 功耗。 | 800G DSP 随规模降本；1.6T、coherent、3nm/2nm DSP 单颗价值高。LPO 渗透会压缩部分传统 DSP BOM。 | Marvell、Broadcom、Cisco Acacia、Credo 等。 | LPO/LRO 大规模替代、DSP 多源供给、先进制程价格下降。 |
| 光模块 / 光收发器 > Driver / TIA > laser driver / TIA / limiting amplifier / analog front-end | 224G driver/TIA/AFE | 200G/lane 光模块、LPO、AOC 和硅光都需要低功耗、高线性模拟前端。 | 软瓶颈。技术门槛高，供给集中，但公开缺货证据弱于 EML/CW laser。 | 224G TIA/driver 比 100G/112G 代际 ASP 高；长期随集成和规模下降。 | Semtech、Marvell、Broadcom、MACOM、MaxLinear、Credo。 | 设计标准统一、LPO 良率提升、多家供应商量产后毛利回落。 |
| 光模块 / 光收发器 > TOSA / ROSA > TOSA / ROSA / active alignment / hermetic package | 光发射/接收组件与主动对准 | 1.6T 对光路耦合、热漂移、封装气密性和批量校准提出更高要求。 | 软到硬瓶颈。TOSA/ROSA 本体供应可扩，但 active alignment、热校准、良率是量产爬坡卡点。 | 高端组件 ASP 上升；普通 TOSA/ROSA 价格受竞争下行。良率改善会明显释放毛利。 | Coherent、Lumentum、Fabrinet、光迅科技、博创科技、天孚通信等。 | 主动对准节拍缩短、设备瓶颈释放、良率提升后单位加工费下滑。 |
| 光模块 / 光收发器 > 光模块 PCB / FPC / 被动光组件 | 光模块小板、FPC、透镜/滤波器/隔离器 | 模块代际升级提高板材、散热和光路精度要求。 | 观察到软瓶颈。单个环节多数不是独立硬短缺，但高端客户认证和良率会限制放量。 | 高端小板和被动光组件价值上行；普通件价格竞争。 | TTM、台光电/联茂/台燿体系、天孚通信、Coherent、Senko、US Conec。 | 普通化、国产替代扩大、客户多供压价。 |
| 光模块 / 光收发器 > 光模块测试 / 校准 > BERT / optical tester / thermal calibration / aging | 光模块测试、校准、老化 | 800G/1.6T 量产需要更高带宽 BERT、眼图、误码、温循和自动化校准；测试时间会影响产能。 | 软瓶颈。设备和测试节拍约束爬坡，但不是所有厂商同时缺设备。 | 1.6T/224G 测试平台 ASP 上行；低速成熟设备价格承压。 | Keysight、Anritsu、VIAVI、Teradyne、EXFO。 | 测试平台交付改善、模块厂自研夹具自动化、单位测试时间下降。 |
| 高速网络与光/铜互连链 > 光引擎 / CPO | CPO 光引擎模块、External laser source、CPO SiPh/InP PIC、FAU、封装对准与测试 | 交换芯片功耗和前面板 I/O 密度逼近限制，CPO 用于降低每 bit 功耗并提升带宽密度。 | 当前观察到软瓶颈，6-24 个月可能转硬。2026 年 CPO 仍以平台验证和早期导入为主，不能替代 pluggable 主量产。 | 样品和早期量产 ASP 高；成熟后目标是降低每 bit 能耗和系统成本。外置光源、FAU、封装对准价值提升。 | Broadcom CPO、NVIDIA CPO、TSMC COUPE、Marvell、Coherent、Lumentum、Intel、OIF 标准生态。 | CPO 商用延期、ELS 可靠性问题、可插拔 1.6T/3.2T 继续满足需求。 |
| 光引擎 / CPO > Fiber array / FAU / CPO 封装对准与测试 | FAU、光纤到芯片耦合、封装校准 | CPO 和硅光需要多通道、高精度、低损耗耦合；通道数上升推高 FAU 和对准难度。 | 软瓶颈，未来潜在硬瓶颈。当前需求小于 pluggable，但客户验证严格，良率影响大。 | 高通道数、窄间距、PM fiber、定制化 FAU ASP 高于普通光纤阵列。 | Corning、Orbray、天孚通信、US Conec、Coherent 生态。 | CPO 推迟、硅光封装标准化降低定制费、FAU 二供成熟。 |
| 高速网络与光/铜互连链 > OCS 光交换 | MEMS/LCoS 光交换引擎、cross-connect、控制电子、光纤管理、校准监测 | 用于降低网络重构成本、减少电交换层级、提升大集群资源利用率。 | 观察。架构价值明确，但当前 AI 数据中心大规模商用证据有限，更多是特定客户和前瞻部署。 | 早期系统 ASP 高，随部署规模和标准化下降。 | Google/内部 OCS 方案、Coherent/Calient/Polatis 等光交换生态。 | 以太网交换机持续降本、OCS 运维复杂度高、云厂部署案例不足。 |
| 高速网络与光/铜互连链 > DAC / ACC / AOC 线缆 > Twinax 铜导体 / 线材 | DAC/Twinax 铜缆 | rack 内短距互连优先用低成本铜缆；224G/1.6T 下 reach 变短、SI 难度上升。 | 非硬瓶颈。铜导体和普通 DAC 供给成熟，限制主要是高速 reach 和认证。 | DAC 仍是最低成本方案；1.6T 线缆单价上升，但同距离/同带宽竞争激烈。 | Amphenol、Molex、TE、Luxshare Precision、BizLink、Credo ecosystem。 | 铜缆 reach 不达标、客户转 AEC/AOC、铜价波动吞噬毛利。 |
| DAC / ACC / AOC 线缆 > ACC Linear Driver / Equalizer / Linear amplifier | ACC/有源线性驱动 | 224G 高速铜互连需要补偿损耗，兼顾低功耗和低成本。 | 软瓶颈。客户导入和信号完整性是关键，IC 供给相对可扩。 | ASP 高于 DAC，低于完整 retimed AEC/AOC；速度和距离越高，IC 价值越高。 | Credo、MaxLinear、Marvell、Astera、Semtech、Molex/TE cable module。 | DAC 能覆盖更多场景、retimed AEC 降价挤压 ACC、线性方案互操作问题。 |
| DAC / ACC / AOC 线缆 > AOC 光电组件 | AOC、短距光电线缆 | 铜 reach 不足、功耗/布线密度要求提升时转向 AOC。 | 局部硬瓶颈。AOC 受 EML/CW laser、driver/TIA、主动对准和测试能力影响，比普通铜缆更可能卡供应。 | ASP 高于 DAC/ACC；若上游光芯片紧张，AOC 报价和毛利更有支撑。 | Coherent、Lumentum、Credo、Molex、TE、Luxshare、AOI、Fabrinet。 | AEC 低功耗版本替代、光芯片供给释放、客户降配至 DAC/ACC。 |
| DAC / ACC / AOC 线缆 > EEPROM / 管理 IC / 屏蔽护套测试 | 线缆辅料和管理 IC | 随线缆数量增长同步增长。 | 观察或非瓶颈。普通 EEPROM、护套、屏蔽件不是核心短缺。 | 价格随原材料和规格小幅波动，高端认证测试收费提升。 | Microchip、ST、线缆 ODM。 | 规格标准化、供给过剩。 |
| 高速网络与光/铜互连链 > Retimer / Linear Driver / SerDes 器件 | PCIe/CXL/Ethernet retimer、CDR、linear driver、equalizer、参考时钟 | AI 服务器、交换机、AEC、PCIe Gen6/CXL 3.x 长通道都需要高速信号调理。Astera 2026Q1 收入同比增长 93%，Credo 2026Q3 收入同比增长 201.5%，反映 AI 连接需求强。 | 软到局部硬瓶颈。需求强，客户认证和高速 SerDes 能力是门槛；但供给可通过多家 fabless 扩张。 | 高速 retimer/AEC IC ASP 上行；成熟 PCIe 4/5 retimer 价格竞争，PCIe 6/224G 仍高价值。 | Astera、Credo、Marvell、MaxLinear、Broadcom、Renesas、TI。 | PCIe Gen6/CXL 平台延期、GPU 主板通道缩短、客户转无源铜或光互连。 |
| Retimer / Linear Driver / SerDes 器件 > 参考时钟 / 抖动控制器件 | clock buffer、jitter attenuator、timing IC | 高速链路需要更低 jitter，但多数是伴随增长。 | 观察。设计重要，但供给成熟度高于 retimer/SerDes。 | 高端 Gen6/224G timing IC 有溢价；普通时钟件竞争充分。 | Renesas、TI、Microchip、Skyworks、Silicon Labs。 | 平台延期、参考设计稳定后价格回落。 |
| 高速网络与光/铜互连链 > 交换机/网络板 PCB > 网络板高速 CCL | 高速 CCL、resin、glass cloth、copper foil、lamination | 800G/1.6T、224G lane、AI server cableless/midplane 设计推动 CCL 从 M7 走向 M8/M9/M10，低损耗介质要求大幅提高。 | 玻纤布硬瓶颈，树脂/CCL 软瓶颈，铜箔观察。TrendForce 指出 NER/NEZ/Q-glass 供应紧，高端玻纤布价格显著上行；SABIC PPE 扩产要到 2026H2。 | NE-glass ASP 约为 E-glass 6 倍，NER-glass 约为 NE-glass 2.5 倍；高端 CCL mix 推升报价。铜箔受 HVLP mix 和铜价共同影响。 | Nittobo、Asahi Kasei、SABIC、Panasonic MEGTRON、Elite Material、台光电、联茂、台燿、斗山、Mitsui、JX Advanced Metals。 | Nittobo/二供扩产、NEZ/Q-glass 加速商业化、M8/M9 供给增多、AI server PCB 需求放缓。 |
| 交换机/网络板 PCB > 网络板高速 CCL > resin / glass cloth / copper foil / lamination | CCL L4 P0 上游 | resin 决定低 Dk/Df 与热可靠性；glass cloth 决定 GWS/FWE 和高速损耗；copper foil 决定 skin effect；lamination 决定多层可靠性。 | glass cloth 为硬瓶颈；resin 为软瓶颈；copper foil 暂无硬缺证据；lamination 受 CCL 厂良率约束。 | 玻纤布涨价最直接；PPE/PPO/PTFE 高性能树脂受 mix 拉动；HVLP 铜箔高端溢价但更受金属价格影响。 | Nittobo、Asahi Kasei、SABIC、台光电、联茂、台燿、Mitsui、JX。 | 高端玻纤布交期恢复、CCL 厂库存上升、下游 PCB 报价回落。 |
| 高速网络与光/铜互连链 > 交换机/网络板 PCB > 网络高层 PCB 制造 | 高层高速 PCB、lamination、back drilling、plating、HDI、impedance control | 交换机主板、AI server UBB/OAM/midplane/backplane 层数和信号完整性要求提升。纬创 2025 年报披露 AI server/HPC 需求导致高层 PCB、HDI、高速材料板产能紧张、部分产品交期延长，高端 PCB 价格维持高位。 | 硬到软瓶颈。真正难点在高层数、高速材料、背钻/电镀/阻抗控制/测试良率，而不是普通 PCB。 | 高端高层 PCB ASP 维持高位；消费电子普通 PCB 恢复弱、价格稳定或承压。 | TTM、健鼎、欣兴、臻鼎、瀚宇博德、深南电路、沪电股份、景旺电子、生益电子等。 | 高端线体扩产、泰国/越南产能爬坡、AI 交换机/服务器订单波动。 |
| 交换机/网络板 PCB > 光模块 PCB / 高频小板 / 网络背板 / Midplane PCB / 网络 PCB 信号完整性测试 | 小型高频板、backplane/midplane、SI 测试 | 1.6T、cableless rack、orthogonal backplane 推升高速板材和测试需求。 | 软瓶颈。midplane/backplane 更紧，小板视客户认证。 | 高层 backplane/midplane ASP 高；小板价格随材料和良率分化。 | TTM、健鼎、欣兴、深南电路、沪电股份、生益电子、Keysight/Anritsu SI 测试生态。 | cableless 架构放缓、材料供应释放、良率改善。 |
| 高速网络与光/铜互连链 > 光纤连接器与被动光组件 > 数据中心光纤 | 数据中心光纤、ribbon fiber、光缆和连接产品 | AI 数据中心内部光纤密度显著提高，Meta 与 Corning 签订最高 60 亿美元多年协议，Corning 为其供应光纤、光缆和连接产品并扩产。 | 局部硬瓶颈。不是普通通信光纤全面短缺，而是 hyperscaler 锁定的高密度数据中心光纤/连接产品趋紧。 | 长协和定制产品支撑价格；普通长途/接入光纤价格不能直接套用。 | Corning、Prysmian、CommScope、AFL、YOFC、亨通、烽火通信等。 | 大客户 LTA 放松、Corning/其他厂商新产能释放、数据中心建设延期。 |
| 光纤连接器与被动光组件 > 陶瓷插芯 / Ferrule | LC/SC/MPO/MT ferrule | 高密度连接器数量随光纤密度增长，但 LC/SC 陶瓷插芯成熟。 | 普通 LC/SC 非瓶颈；MPO/MTP/MT 高密度 ferrule 是软瓶颈。 | 高精度 MPO/MT 单价高于普通 LC/SC；低端 ferrule 竞争充分。 | Kyocera、US Conec、Senko、T&S、Adamant Namiki、国内陶瓷插芯厂。 | MPO/MTP 二供增多、VSFF 标准固化后价格下降。 |
| 光纤连接器与被动光组件 > FAU / 光纤阵列 | FAU、V-groove、fiber-to-chip array | 硅光、CPO、相干模块和高通道数耦合推动 FAU 需求。 | 软瓶颈。和 CPO/SiPh 放量高度相关。 | 高通道数、窄 pitch、PM fiber、定制 FAU ASP 上行；普通 FAU 竞争。 | Corning、Orbray、天孚通信、Coherent、US Conec。 | CPO/硅光延期、封装标准化、客户二供导入。 |
| 光纤连接器与被动光组件 > 透镜 / 隔离器 / 滤波器 / 光胶 / 封装辅助材料 | 微光学被动件和光胶 | 光模块、AOC、CPO 的光路复杂度提升。 | 软瓶颈或观察。高端微光学件有认证门槛，普通光胶不是硬瓶颈。 | 高可靠、低损耗、耐热件有溢价；普通光学胶和标准件价格承压。 | Coherent、天孚通信、II-VI/Coherent 体系、Dymax、DELO、Senko。 | 标准化、良率改善、客户多供压价。 |
| 光纤连接器与被动光组件 > MPO / LC 连接器 | MPO/MTP、LC、VSFF 高密度连接器 | AI 数据中心光纤密度、布线复杂度和维护需求上升。 | MPO/MTP/VSFF 软瓶颈，LC 成熟。 | 高密度低损耗连接器 ASP 上升；普通 LC 价格稳定或下行。 | US Conec、Senko、Corning、Amphenol、TE、Molex。 | 数据中心布线方案简化、二供导入、良率提高。 |
| 高速网络与光/铜互连链 > 网络测试与认证设备 | BERT、光模块测试仪、协议分析仪/流量发生器、热箱/可靠性、校准服务 | 800G/1.6T、PCIe Gen6、224G lane、AI workload emulation 要求更高端测试平台。 | 软瓶颈。高端设备交期和测试能力会限制客户验证/量产节拍，但不是普通测试设备缺货。 | 1.6T BERT、光测试、协议分析平台 ASP 上行；成熟 100G/400G 工具价格承压。 | Keysight、Anritsu、VIAVI、Spirent、Ixia/Keysight、Teradyne、EXFO。 | 设备交付改善、测试外包扩容、标准稳定后测试时间下降。 |
| 网络测试与认证设备 > 热箱 / 环境可靠性测试 / 校准治具 / 认证服务 | 环境老化、夹具、认证服务 | 高速模块和线缆需温度/老化/互操作认证。 | 观察。测试时间是流程约束，但普通热箱和夹具不是核心短缺。 | 高速定制夹具和认证服务收费提升；通用设备竞争充分。 | Keysight、Anritsu、VIAVI、第三方实验室、模块厂自建测试。 | 测试流程自动化、认证标准固化。 |

## L4 P0 覆盖与合并说明

| L2 | 本地 L4 P0 | 本稿处理方式 |
|---|---|---|
| AI 集群交换机 | SMT、line card、switch board、connector、cage | 并入“交换机板卡装配与高速 I/O 结构件”。普通 SMT 非瓶颈，高速 connector/cage 是局部软瓶颈。 |
| 交换芯片 / Switch ASIC | PAM4 SerDes、CDR、equalization、PLL、parser、scheduler、buffer manager、congestion control | SerDes/PHY 单独判断为软瓶颈；parser/scheduler/buffer/congestion control 是 ASIC 内部功能块，不单独做供需价格。 |
| NIC / DPU / SmartNIC | MAC、PCS、FEC、flow control、time sync、RDMA engine、RoCE logic、queue pair、transport offload、SerDes、retimer interface、PLL、equalizer | 并入 NIC/DPU、RDMA/RoCE 卸载、NIC SerDes/PHY 三个产品市场。 |
| 光模块 / 光收发器 | EML、DFB laser、InP epitaxy、reliability test、SiPh modulator、InP PIC、grating coupler、waveguide、DSP ASIC、FEC、equalization、ADC/DAC、laser driver、TIA、limiting amplifier、analog front-end、TOSA、ROSA、active alignment、hermetic package、BERT、optical tester、thermal calibration、aging | 拆为光芯片、硅光/PIC、DSP、Driver/TIA、TOSA/ROSA、测试校准。EML/CW laser/InP 和 active alignment/testing 是最强硬瓶颈。 |
| 交换机/网络板 PCB | resin、glass cloth、copper foil、lamination、back drilling、plating、HDI、impedance control | 拆为高速 CCL 上游和高层 PCB 制造。glass cloth 是硬瓶颈，resin/lamination 软瓶颈，copper foil 观察。 |
| 光引擎 / CPO、DAC/ACC/AOC、Retimer、光纤连接器、测试设备 | 本地没有 L4 P0 或以 L3 为主 | 按 Level 3 产品市场判断；必要时把 FAU、External laser、AOC、retimer、BERT 单列。 |

## 当前硬瓶颈清单

| 排名 | 节点 | 瓶颈机制 | 价格趋势 | 置信度 |
|---:|---|---|---|---|
| 1 | 光模块上游 EML/CW laser/InP 外延与可靠性筛选 | 1.6T/200G-lane 和 CPO/LPO 消耗高端激光器，合格产能、外延、可靠性和客户认证限制扩产。 | 高端产品 ASP/mix 上行；老规格随扩产下行。 | 高 |
| 2 | 高端 glass cloth（NER/NEZ/Q-glass） | 224G/1.6T、M8/M9/M10、cableless/midplane 需求叠加，Nittobo 等高端供给集中且扩产滞后。 | NE、NER、NEZ/Q 代际大幅溢价，涨价向 CCL/PCB 传导。 | 高 |
| 3 | 高层高速 PCB 制造 | AI server/HPC 和交换机推升高层数、高速材料、背钻、电镀、阻抗控制和测试要求；部分产品交期延长。 | 高端 PCB 报价维持高位，普通 PCB 不跟涨。 | 高 |
| 4 | 数据中心高密度光纤/连接产品 | Hyperscaler 长协锁定先进数据中心光纤、光缆和连接能力。 | 长协和定制高密度产品支撑价格。 | 中高 |
| 5 | 光模块主动对准、热校准与 1.6T 测试节拍 | 1.6T 光路、热、误码和 aging 要求提升，测试和良率限制模块放量。 | 高端测试设备、校准服务和良率溢价上行。 | 中高 |

## 软瓶颈和未来迁移清单

| 时间窗口 | 可能迁移节点 | 触发条件 | 跟踪指标 |
|---|---|---|---|
| 0-6 个月 | 800G/1.6T 光模块 DSP、Driver/TIA、TOSA/ROSA | 1.6T 订单持续上修，LPO/LRO 良率爬坡慢。 | Marvell/Broadcom/Credo/Semtech 高速光电 IC 收入，模块厂 1.6T 良率和客户认证。 |
| 0-12 个月 | Retimer/AEC/ACC | PCIe Gen6、CXL、AI server 长通道和 1.6T 铜互连放量。 | Astera、Credo、MaxLinear、Marvell 订单、毛利率和客户集中度。 |
| 6-18 个月 | CPO External laser、FAU、CPO 封装对准测试 | NVIDIA/Broadcom 等 CPO 平台进入更多客户部署。 | CPO 公开 design win、ELS 可靠性、FAU 通道数、CPO 测试平台交期。 |
| 6-24 个月 | OCS 光交换 | 大集群资源利用率和电交换功耗压力使光交换进入商用网络。 | 云厂 OCS 部署、OCS 供应商订单、网络拓扑公开案例。 |
| 12-24 个月 | NEZ/Q-glass 与下一代 Low-Dk3 CCL | 1.6T/3.2T、cableless rack 和更高层 midplane/backplane 放量。 | Nittobo/Asahi Kasei/Q-glass 新产能、CCL 厂 M9/M10 认证、PCB 报价。 |

## 后续研究使用方式

1. 做单家公司研究时，先把公司产品映射到本表的最窄节点，再查公司披露的收入、客户、认证、产能、毛利或订单，不能从“AI 互连概念”直接推导。
2. 判断涨价时，区分 `代际 mix 上行`、`合格供给短缺`、`原材料涨价传导`、`单位良率改善`、`每 bit 成本下降`。光模块、PCB、玻纤布的价格逻辑完全不同。
3. 对 A 股映射，优先查官方公告、年报、互动易/调研纪要、客户认证和产能建设；海外龙头证据只用于校准节点景气，不自动证明本土公司受益。
4. 对硬瓶颈节点，重点看交期、价格、长协、扩产节奏和良率；对软瓶颈节点，重点看设计 win、客户导入、份额和毛利持续性。

## 来源索引

| 编号 | 来源 | 用途 |
|---|---|---|
| L0 | `docs/ai_chain_disassembly/nodes_mindmap_level_01_to_05_cleaned_2026-05-31.xlsx` | 本地节点边界、Level 2/3/4 P0 覆盖。 |
| S1 | https://www.trendforce.com/presscenter/news/20260420-13017.html | AI 光模块市场规模、800G+ 需求、EML/CW laser 与主动对准瓶颈。 |
| S2 | https://www.prnewswire.com/news-releases/ai-back-end-switch-market-will-push-past-100-billion-by-2030-according-to-delloro-group-302678344.html | AI 后端交换机需求、800G/1.6T 端口迁移、CPO 方向。 |
| S3 | https://investors.broadcom.com/news-releases/news-release-details/broadcom-ships-tomahawk-6-worlds-first-1024-tbps-switch | Tomahawk 6、102.4T、200G PAM4 SerDes、CPO 选项。 |
| S4 | https://www.marvell.com/company/newsroom/marvell-teralynx-512t-ethernet-switch-enters-volume-production-for-global-ai-cloud-deployments.html | Teralynx 10 51.2T 交换芯片量产、AI cloud 部署。 |
| S5 | https://asteralabs.gcs-web.com/news-releases/news-release-details/astera-labs-reports-first-quarter-2026-financial-results | Retimer/PCIe 6/AI fabric 需求和 Astera 2026Q1 业务增长。 |
| S6 | https://www.sec.gov/Archives/edgar/data/1807794/000162828026013205/credoq32026ex-9911.htm | Credo AEC/IC/AI infrastructure 收入增长和需求验证。 |
| S7 | https://insights.trendforce.com/p/glass-fiber-cloth-shortage | 高端玻纤布分类、AI 需求、ASP 倍数、Nittobo 份额和涨价。 |
| S8 | https://www.sabic.com/en/news/49267-sabic-expands-ppe-oligomers-capacity-for-ai-and-5g-data-center-pcbs | PPE oligomer 扩产和高速 AI server PCB CCL 材料需求。 |
| S9 | https://www.wistron.com/file/9ecdf53a-9c8a-4df8-aeed-7568724eb956/2025_WistronAnnualReport_EN.pdf | 高层 PCB、HDI、高速材料板产能紧张、交期延长、高端 PCB 价格高位。 |
| S10 | https://investor.corning.com/news-and-events/news/news-details/2026/Corning-and-Meta-Announce-Multiyear-up-to-6-Billion-Agreement-to-Accelerate-US-Data-Center-Buildout/default.aspx | Meta-Corning 数据中心光纤/光缆/连接产品多年长协和扩产。 |
| S11 | https://investor.marvell.com/news-events/press-releases/detail/1013/marvell-ushers-in-the-1-6t-era-with-expanded-optical-dsp-platform-portfolio-redefining-ai-data-center-end-to-end-connectivity | 1.6T 光模块 DSP 平台。 |
| S12 | https://www.semtech.com/company/press/semtech-launches-224-gbps-ic-family-for-linear-optics-era | 224G linear optics driver/TIA/AFE 代际升级。 |
| S13 | https://www.keysight.com.cn/cn/zh/about/newsroom/news-releases/2026/0319_pr26-056-keysight-expands-1-6t-interconnect-validation-technology-to-include-passive-copper-and-low-power-optics.html | 1.6T passive copper/LPO 测试验证需求。 |
| S14 | https://investors.broadcom.com/news-releases/news-release-details/broadcom-announces-third-generation-co-packaged-optics-cpo | Broadcom CPO 代际进展。 |
| S15 | https://developer.nvidia.com/blog/scaling-ai-factories-with-co-packaged-optics-for-better-power-efficiency/ | NVIDIA CPO 和 AI factory 光互连方向。 |
| S16 | https://www.oiforum.com/oif-launches-the-industrys-first-co-packaging-standard-the-3-2t-co-packaged-module-implementation-agreement/ | OIF CPO 标准化。 |

## 自审计

| 审计项 | 结果 |
|---|---|
| 是否覆盖 11 个 Level 2 | 通过：AI 集群交换机、交换芯片 / Switch ASIC、NIC / DPU / SmartNIC、光模块 / 光收发器、光引擎 / CPO、OCS 光交换、DAC / ACC / AOC 线缆、Retimer / Linear Driver / SerDes 器件、交换机/网络板 PCB、光纤连接器与被动光组件、网络测试与认证设备均已覆盖。 |
| 是否覆盖 Level 3 和 Level 4 P0 | 通过：61 个 Level 3 以产品市场粒度覆盖；59 个 Level 4 P0 在“L4 P0 覆盖与合并说明”中说明合并口径，避免把内部 IP 当成独立供需市场。 |
| 是否区分当前供需和未来迁移 | 通过：硬瓶颈、软瓶颈、观察和未来 6-24 个月迁移分开。 |
| 是否给出价格趋势 | 通过：每个主节点均列出 ASP/价格逻辑，并区分代际 mix、每 bit 成本、短缺涨价和普通件竞争。 |
| 是否给出反转指标 | 通过：主节点表和未来迁移表均包含反转或跟踪指标。 |
| 主要证据级别 | 通过：优先使用行业研究、公司官方新闻稿、SEC/年报、客户长协和标准组织；本地 taxonomy 不作为供需证据。 |
