# 高速网络与光/铜互连链：当前平衡但可能转紧缺的节点前瞻表

研究日期：2026-06-01（北京时间）

本稿是 `high_speed_network_optical_copper_supply_demand_price_2026-06-01.md` 的前瞻补充，专门回答：哪些 L3/L4 节点当前没有明确全行业缺货，但如果 AI 后端网络、1.6T/3.2T、CPO、224G 电互连、AI 数据中心布线继续爆发，较大概率从“平衡/近平衡”转为“供给紧缺”。

2026-06-01 复核更新：根据 `high_speed_network_top5_future_shortage_validation_2026-06-01.md`，原前五个“高概率”节点已重新校准。Retimer/SerDes、AEC retimer cable、网络验证与认证产能仍保留高评级；ACC linear driver、connector/cage、CPO FAU 与封装对准/测试下调为中高或条件型高。2026-06-01 二次细分：优先级 1/2/3 已从宽节点拆到可用于公司产品映射的子节点，尤其区分 224G retimer 主芯片、CDR/重定时核心、retimer 封装测试、AEC cable 模组、AEC retimer IC、BERT、校准治具和认证服务。

## 结论先行

| 优先级 | 当前平衡但未来可能转紧节点 | 转紧概率 | 最关键触发 |
|---:|---|---|---|
| 1.1 | `Retimer / Linear Driver / SerDes 器件 > Retimer SerDes PHY` 中的 224G/lane、200G PAM4 retimer PHY | 高 | 1.6T/3.2T 端口、scale-up fabric、PCIe Gen6/CXL 同时拉高高速 PHY 合格设计与客户导入门槛。 |
| 1.2 | `Retimer / Linear Driver / SerDes 器件 > CDR / 重定时核心` 中的 AEC/板级 retimer DSP-CDR 核心 | 高 | AEC 和板级 retimer 需要在 224G PAM4 下重建时钟、恢复眼图和控制误码，客户互操作验证集中。 |
| 1.3 | `Retimer / Linear Driver / SerDes 器件 > Retimer 封装与测试` 中的低功耗封装、热设计、ATE/系统级验证 | 高 | 224G retimer 不只缺芯片设计，也容易卡在低功耗封装、散热、误码测试和客户 qualification 节拍。 |
| 1.4 | `Retimer / Linear Driver / SerDes 器件 > Equalizer / Linear amplifier` 中的 224G 线性均衡/放大器 | 中高 | 受益于 ACC/LPO/LRO/线性接收路线，但供给弹性和替代路线强于高端 retimer。 |
| 2.1 | `DAC / ACC / AOC 线缆 > AEC retimer cable`，本地 taxonomy 未单列，按 AEC 模组 + retimer 核心组合节点处理 | 高 | 无源 DAC reach 不够，客户在 rack 内转向低功耗有源铜，AEC 模组的 retimer、热设计和客户认证更容易成为约束。 |
| 2.2 | `Retimer / Linear Driver / SerDes 器件 > CDR / 重定时核心` 中的 cable-end retimer IC | 高 | AEC 的核心增量价值在 cable 两端 retimer IC，若客户集中导入，先紧的是合格 IC 与 reference design。 |
| 2.3 | `DAC / ACC / AOC 线缆 > 线缆屏蔽 / 护套 / 测试` 中的 1.6T AEC SI、热、误码和量产测试 | 中高 | 线缆本体不难，难点在 224G/1.6T 下屏蔽、散热、误码率、热插拔和批量一致性。 |
| 2.4 | `DAC / ACC / AOC 线缆 > ACC Linear Driver` | 中高 | ACC 仍受益于短距低功耗铜互连，但与 passive DAC、AEC、AOC/LPO 存在路线竞争，证据弱于 AEC retimer cable。 |
| 3.1 | `网络测试与认证设备 > BERT 误码率测试设备`，聚焦 1.6T/224G electrical/optical BERT | 高 | 1.6T LPO/LRO、passive copper、ACC、AEC、CPO 同时验证，最先消耗高速误码测试端口。 |
| 3.2 | `网络测试与认证设备 > 校准治具 / 认证服务` 中的 HCB/MCB、electrical fixture、第三方认证和 FAE 资源 | 高 | 瓶颈更像测试窗口和治具/服务产能，不是单纯仪器硬件缺货。 |
| 3.3 | `网络测试与认证设备 > 协议分析仪 / 流量发生器` 中的 800G/1.6T Ethernet、RoCE/UEC、scale-up traffic validation | 中高 | 从链路误码扩展到系统流量、拥塞、协议一致性和 AI workload emulation，需求明确但可外包/共享。 |
| 3.4 | `光模块测试 / 校准 > optical tester / thermal calibration / aging` 中的 1.6T LPO/LRO/FRO 光电联合验证 | 中高 | 与 1.6T 光模块路线绑定，热校准、老化和光电联合测试会转紧，但不是所有通用光模块测试仪都紧。 |
| 4 | `AI 集群交换机 > 交换机主板 / Line card 装配 > connector / cage` 与 `DAC / ACC / AOC 线缆 > 高速线缆连接器 / Cage` | 中高 | OSFP/OSFP-XD、224G PAM4、1.6T/3.2T 端口密度提升明确，但供应商群体较宽，缺少直接交期或 allocation 证据。 |
| 5 | `光引擎 / CPO > Fiber array / FAU` 与 `CPO 封装对准与测试` | 中高，CPO 多客户放量后升高 | NVIDIA/Broadcom CPO 方向明确，但 FAU/对准测试的直接缺口证据不足，需等 CPO 从平台验证转向多客户批量部署。 |
| 6 | `光引擎 / CPO > External laser source` | 中高 | CPO 采用外置激光源路线，ELSFP/PLS 从样品走向系统级部署。 |
| 7 | `光模块 / 光收发器 > Silicon photonics / InP PIC` 及 `CPO 硅光 / InP PIC` | 中高 | 1.6T/3.2T 功耗压力促使硅光/CPO 渗透率快速上修。 |
| 8 | `交换机/网络板 PCB > 网络板高速 CCL > resin / copper foil / lamination` | 中高 | 当前主要卡在高端 glass cloth；若玻纤布扩产后下游需求继续爆发，PPE/PPO/PTFE 树脂、HVLP 铜箔和 lamination 良率会轮到承压。 |
| 9 | `交换机/网络板 PCB > 网络背板 / Midplane PCB` 与 `网络 PCB 信号完整性测试` | 中高 | cableless rack、orthogonal backplane、1.6T/3.2T 高层高速板从少数平台扩到更多 AI rack。 |
| 10 | `光纤连接器与被动光组件 > MPO / LC 连接器` 中的 VSFF/MMC/SN-MT 高密度连接器 | 中高 | 数据中心光纤密度快速提升，普通 MPO/LC 不能满足密度、损耗和可维护性。 |
| 11 | `NIC / DPU / SmartNIC > NIC SerDes / PHY` 与 `RDMA / RoCE 卸载引擎` | 中 | 800G/1.6T NIC 从高端集群向更广泛 AI 推理/训练集群扩散。 |
| 12 | `AI 集群交换机 > 交换机散热模块` 和 `CPO 热管理与供电接口` | 中 | 102.4T/204.8T 交换、CPO、1.6T/3.2T 端口功耗推高交换机热流密度。 |
| 13 | `Retimer / Linear Driver / SerDes 器件 > 参考时钟 / 抖动控制器件` | 中 | PCIe Gen6/CXL/224G link 对 jitter budget 更严格，客户验证窗口集中。 |
| 14 | `光纤连接器与被动光组件 > 透镜 / 隔离器 / 滤波器` 中的高可靠微光学件 | 中 | 1.6T/3.2T、CPO、AOC 的光路复杂度提升，普通件不能直接替代。 |

明确不放入高概率名单的节点：普通 SMT、通用机箱、普通 Twinax 铜导体、普通 EEPROM/管理 IC、普通 LC/SC 陶瓷插芯、通用光胶、普通热箱。这些节点会受益于量增，但供给弹性、替代性或标准化程度较高，除非出现原材料或设备事故，否则更像量增受益，不像未来紧缺。

## 判定口径

| 维度 | 本稿定义 |
|---|---|
| 当前平衡 | 公开资料没有显示全行业 allocation、长交期、价格明显上调或客户扩产被该节点拖延；即使有认证/良率压力，也还不是当前主瓶颈。 |
| 当前近平衡 | 已有技术门槛或局部客户验证压力，但主流需求仍能被现有供应链承接。 |
| 未来转紧 | 下游规格或数量阶跃后，该节点的合格产能、测试能力、良率、认证队列、材料等级或供应商数量可能跟不上。 |
| 转紧概率 | 高：需求触发清晰且供给弹性低；中高：触发清晰但供给已有扩产或替代路线；中：需要特定架构路线兑现；低：量增但供给弹性高。 |

## 前瞻节点详表

| 本地 taxonomy path | 当前供需为什么仍平衡 | 下游爆发触发条件 | 未来紧缺机制 | 概率 / 时间窗口 | 价格与利润池迁移 | 需要跟踪的硬指标 | 反证 / 排除条件 |
|---|---|---|---|---|---|---|---|
| AI 数据中心 / 智算中心 > 高速网络与光/铜互连链 > Retimer / Linear Driver / SerDes 器件 > Retimer SerDes PHY | 当前 112G/800G 与 PCIe 5.0/部分 Gen6 需求已有多家供应商承接，尚未看到广泛缺货。 | 224G PAM4、200G PAM4 SerDes、1.6T/3.2T 端口、PCIe Gen6/CXL 3.x、scale-up rack 同时进入批量部署。 | 高速 PHY 需要模拟前端、DSP/FEC 协同、低功耗设计和客户平台互操作验证；真正紧的是 224G/200G PAM4 合格 PHY，不是所有 SerDes。 | 高；6-18 个月。 | 高端 retimer PHY、SerDes IP 授权、custom retimer/NIC/switch ASIC 设计导入价值上行。 | 224G/200G PAM4 PHY tape-out、量产公告、设计导入、PCIe Gen6/CXL 平台出货、Astera/Credo/Broadcom/Marvell 连接产品收入。 | 1.6T 端口迁移推迟、客户转向更短链路或光互连、多个高端 PHY 供应商同时通过大客户认证。 |
| 高速网络与光/铜互连链 > Retimer / Linear Driver / SerDes 器件 > CDR / 重定时核心 | 当前 112G retimer/CDR 已有成熟供给，尚未看到全行业 allocation。 | AEC、板级 retimer、scale-up Ethernet/UALink、PCIe Gen6 同时放量，224G PAM4 下链路裕量明显收窄。 | CDR/重定时核心要在高噪声、高损耗链路中恢复时钟并控制误码；客户 reference design 与互操作窗口集中时，合格核心会比普通模拟器件更紧。 | 高；6-18 个月。 | AEC retimer IC、板级 retimer、CDR IP 和调参服务成为利润池。 | 224G retimer 发布、AEC cable design win、客户认证排队、误码率和功耗指标、供应商 backlog。 | AEC 导入不及预期、客户用 passive DAC/光互连绕开、retimer 多源快速成熟。 |
| 高速网络与光/铜互连链 > Retimer / Linear Driver / SerDes 器件 > Retimer 封装与测试 | 当前封装测试不是独立主瓶颈，更多随 retimer 主芯片节奏走。 | 224G retimer 从样品验证转入 1.6T AEC/板级 retimer 批量出货。 | 低功耗封装、散热、ATE、系统级误码测试、热插拔可靠性和客户 qualification 需要协同；如果主芯片订单集中，封装测试节拍会拖慢交付。 | 高；6-18 个月，但依赖 retimer 主芯片放量。 | 高端 retimer 封装、测试程序、系统级验证和可靠性服务价值上升。 | Retimer 量产良率、封装热阻、ATE 测试时长、系统级误码测试排期、客户 RMA/可靠性口径。 | 主芯片需求不放量、封装测试外包产能充足、客户接受更低规格方案。 |
| 高速网络与光/铜互连链 > Retimer / Linear Driver / SerDes 器件 > Equalizer / Linear amplifier | 线性均衡/放大器供应弹性高于 retimer，当前未见单独紧缺。 | ACC、LPO/LRO、linear receive 路线在 1.6T 短距互连中放量。 | 线性路线对功耗有优势，但需要与光/铜链路和接收端算法共同调参；特定 224G 料号可能局部紧张。 | 中高；6-18 个月。 | 高速低功耗 equalizer/linear amplifier 有 mix 溢价，但普通 driver 不具备强涨价逻辑。 | ACC/LPO/LRO 认证、线性器件 design win、客户路线选择、1.6T 端口实测误码。 | AEC retimer 或 pluggable optics 占比提高，线性路线验证失败，二供迅速导入。 |
| 高速网络与光/铜互连链 > DAC / ACC / AOC 线缆 > AEC retimer cable；Retimer / Linear Driver / SerDes 器件 > CDR / 重定时核心 | 无源 DAC 和成熟 AEC/AOC 已有供应，当前瓶颈更多在光芯片、PCB/玻纤布等环节。 | AI rack 内短距互连从 800G 扩到 1.6T，passive copper reach 不足但客户又希望低于光模块成本和功耗。Molex 把 AEC 定位为用 retimer 延伸铜 reach、最高到 1.6T。 | AEC 是“线缆模组 + 两端 retimer IC + firmware/EEPROM + 热设计 + 误码测试”的组合节点；客户验证集中时，合格模组和 retimer IC 会先紧。 | 高；6-18 个月。 | DAC 价格仍低且竞争充分；AEC 单线价值显著高于 DAC，retimer IC 含量和认证服务成为利润池。 | 224G AEC 认证、客户从 DAC/ACC 转 AEC 的比例、Credo/Molex/TE/MaxLinear 1.6T 产品出货、线缆 ODM 交期。 | AOC/LPO 成本快速下降、rack 设计缩短铜链路、客户坚持无源铜或 ACC 即可满足距离需求。 |
| 高速网络与光/铜互连链 > Retimer / Linear Driver / SerDes 器件 > CDR / 重定时核心 中的 cable-end retimer IC | 当前 retimer 供应还在导入期，尚未看到明确全行业缺货。 | 1.6T AEC 采用率上升，cable 两端都需要 retimer/CDR，单 rack retimer IC 数量被连接距离和端口密度放大。 | AEC retimer IC 需要低功耗、低时延、热约束和 firmware 调参；同一客户一旦锁定 reference design，合格 IC 与替代导入都会变慢。 | 高；6-18 个月。 | cable-end retimer IC 的价值量和供应商议价能力强于普通线缆材料。 | AEC retimer IC 出货、单线 BOM 价值、客户认证、firmware 更新节奏、功耗和散热指标。 | ACC/passive DAC 足够、云厂限制有源铜功耗、不同 retimer IC 快速兼容替换。 |
| 高速网络与光/铜互连链 > DAC / ACC / AOC 线缆 > 线缆屏蔽 / 护套 / 测试 | 线缆材料本体可扩，当前不是独立紧缺。 | 1.6T AEC 进入批量验证，线缆不再只是导体和连接器，而要满足 224G PAM4 SI、散热、热插拔和批量误码一致性。 | 高速线缆屏蔽、装配公差、热管理、批量 BERT 测试、良率爬坡会限制 AEC 模组交付节拍。 | 中高；6-18 个月。 | 线缆 ODM 的认证服务、测试服务和高端模组装配价值提升；普通 Twinax 价值有限。 | AEC 模组良率、批量测试时长、线缆 ODM 交期、热插拔失效率、客户 RMA。 | 模组厂自动化测试扩容、rack 设计减少长铜链路、客户降规格。 |
| 高速网络与光/铜互连链 > DAC / ACC / AOC 线缆 > ACC Linear Driver | ACC 已有供应基础，linear driver 供给弹性通常高于高端 retimer；当前没有看到 ACC driver 单独成为全行业瓶颈。 | 1.6T 短距低功耗铜互连放量，客户希望用比 AEC 更低功耗、更低成本的有源铜覆盖 3m 左右场景。 | ACC 需要低功耗 linear driver、线缆屏蔽、连接器、热设计和客户认证配合；若客户验证集中，特定规格 driver 和模组会局部紧张。 | 中高；6-18 个月。 | ACC 价值量高于 passive DAC，但低于 AEC；利润池更多来自短距高端规格和客户认证。 | 1.6T ACC 认证、客户 3m/5m/7-9m 链路比例、ACC 与 AEC 的采用比例、linear driver 厂商设计导入。 | AEC 取代 ACC、passive DAC reach 足够、AOC/LPO 快速降本，或多个 driver 供应商快速二供导入。 |
| 高速网络与光/铜互连链 > 网络测试与认证设备 > BERT 误码率测试设备 | 当前高端 BERT 平台有供应，更多是模块厂和线缆厂的资本开支节奏问题。 | Keysight 已把 1.6T 验证扩展到 passive copper、ACC、LPO、LRO、AEC；当 1.6T、224G、CPO、AEC 同时进入 qualification，误码测试端口会集中消耗。 | BERT、采样示波器和高速 pattern/test platform 不是简单扩产，且 1.6T/224G 测试时长、校准和操作门槛高。 | 高；6-12 个月。 | 1.6T/224G BERT 平台 ASP、租赁、校准和测试服务价格上行。 | Keysight/Anritsu/VIAVI/Spirent 1.6T 产品订单、模块厂测试 capex、认证排队时间、单位测试时长。 | 标准稳定后测试自动化显著提高，客户共用测试平台或外包扩容。 |
| 高速网络与光/铜互连链 > 网络测试与认证设备 > 校准治具 / 认证服务 | 通用治具和普通认证服务可扩，但 224G/1.6T 专用 HCB/MCB、electrical fixture 和客户认证窗口更窄。 | 1.6T copper、AEC、ACC、LPO/LRO、CPO 同时进入客户验证，所有供应商都需要 reference fixture、校准和第三方/客户认证。 | 真正瓶颈可能不是仪器硬件，而是夹具、校准、测试窗口、认证服务和 FAE 资源；这些资源无法像普通产能一样快速复制。 | 高；6-12 个月。 | 校准治具、认证服务、FAE 支持和实验室排期价值上升。 | HCB/MCB 交期、fixture 复用率、第三方实验室排期、客户认证 cycle time、FAE 人力。 | 客户开放共享测试平台、认证流程标准化、供应商自建实验室快速扩容。 |
| 高速网络与光/铜互连链 > 网络测试与认证设备 > 协议分析仪 / 流量发生器 | 当前协议和流量测试可通过实验室、云厂和设备商资源承接，未见全面短缺。 | 800G/1.6T Ethernet、RoCE/UEC、scale-up fabric 和 AI workload emulation 同时验证，系统级测试复杂度上升。 | 协议一致性、拥塞控制、流量发生、AI workload emulation 需要软硬件和工程经验结合；客户 qualification 集中时会排队。 | 中高；6-18 个月。 | 协议分析、流量发生、测试脚本和系统级验证服务价格/利用率上升。 | 1.6T Ethernet 认证、RoCE/UEC 测试需求、云厂系统级验证排期、测试服务收入。 | 标准和工具链成熟、客户内部测试平台复用率提高、第三方服务扩容。 |
| 光模块 / 光收发器 > 光模块测试 / 校准 > BERT / optical tester / thermal calibration / aging | 光模块测试/校准已有成熟供给，普通 400G/800G 测试不是本轮新增瓶颈。 | 1.6T LPO/LRO/FRO 与 CPO 相关光电链路进入客户验证，热校准、老化和光电联合测试窗口集中。 | 低功耗光模块和 CPO 相关验证需要光电联合调参、热漂移控制、aging 与误码测试组合，量产爬坡时会拖慢认证。 | 中高；6-18 个月。 | 光模块测试服务、热校准、老化和高端 optical tester 利用率上升。 | 1.6T LPO/LRO/FRO 认证、热校准时长、aging 排期、光模块测试 capex。 | 低功耗光模块路线推迟、pluggable 传统方案继续满足需求、测试自动化显著提升。 |
| AI 集群交换机 > 交换机主板 / Line card 装配 > connector / cage；DAC / ACC / AOC 线缆 > 高速线缆连接器 / Cage；NIC / DPU / SmartNIC > NIC 板卡 / Cage / 连接器 | OSFP/QSFP-DD 生态成熟，当前还不是单独主瓶颈。 | Dell'Oro 预计 AI 后端网络端口从 800G 走向 2027 年 1.6T；TE、Molex 均已给出 224G/1.6T OSFP 连接器和线缆产品路线。 | 1.6T/224G 下 SI、EMI、散热、机械公差、host board footprint 和 cage 散热窗口更窄；普通连接器产能不能直接等同于合格 224G cage/connector。 | 中高；6-18 个月。 | 普通 cage/connector 价格稳定；OSFP-XD、224G、带散热结构、低损耗高密度连接器单端口价值量上升。 | TE/Molex/Amphenol/Samtec/FIT 224G 高端料号产能、客户认证、交换机 ODM 端口配置、特定料号交期。 | 1.6T 采用更少前面板端口或 CPO 绕开部分 pluggable cage；多家供应商快速通过客户认证，未出现交期拉长。 |
| 高速网络与光/铜互连链 > 光引擎 / CPO > Fiber array / FAU；CPO 封装对准与测试 | CPO 目前仍处于从平台验证到多客户放量的转换期，实际量产规模尚未充分证明，所以 FAU 和 CPO 对准测试还没有被大规模需求压垮。 | Dell'Oro 预计 CPO adoption 加速，NVIDIA 和 Broadcom 持续推进 CPO；若 CPO 从少数平台转为 hyperscaler 多平台导入，FAU 通道数和封装精度需求阶跃。 | 光纤到芯片耦合需要高通道数、窄 pitch、低损耗、一致性和热漂移控制；良率、主动对准设备、熟练工艺和客户资格会限制扩产。 | 中高；9-24 个月，CPO 多客户量产确认后升高。 | 高通道 FAU、PM fiber FAU、CPO 封装/测试服务 ASP 上行，普通 FAU 仍竞争。 | NVIDIA/Broadcom CPO design win、FAU 通道数规格、CPO 封装良率、Corning/Orbray/天孚通信等扩产与客户认证。 | CPO 推迟、pluggable 1.6T/3.2T 继续满足功耗、CPO 封装标准化降低定制壁垒。 |
| 高速网络与光/铜互连链 > 光引擎 / CPO > External laser source | ELS/PLS 当前更多随 CPO 样机和早期平台走，量不大；当前主紧缺在 pluggable 光模块激光器，不等同于 CPO ELS。 | CPO 采用外置激光源并进入多系统量产；OIF co-packaging 标准中包含 ELSFP external laser source，Broadcom CPO 产品也配置 pluggable laser source。 | ELS 要求多通道、高可靠、可维护、低 RIN、热稳定和系统冗余；合格供应商数量少，且和 CPO 平台强绑定。 | 中高；9-24 个月。 | ELS/PLS ASP 高，早期利润池从传统 pluggable module 部分迁移到系统级光源。 | OIF ELSFP 生态、Broadcom/NVIDIA CPO 供货、Lumentum/Coherent 等外置光源产品、可靠性数据。 | CPO 选择集成光源或 VCSEL 路线、ELS 标准碎片化导致量产推迟。 |
| 光模块 / 光收发器 > Silicon photonics / InP PIC；光引擎 / CPO > CPO 硅光 / InP PIC | 目前硅光/PIC 渗透仍在上升期，传统 EML pluggable 可承接大量 800G/1.6T 需求。 | 1.6T/3.2T 功耗、封装尺寸和前面板 I/O 受限，推动硅光、CPO、LPO/LRO 占比上修。NVIDIA CPO、Broadcom CPO、TSMC COUPE 等说明生态在成形。 | 硅光/PIC 的短板不是普通晶圆产能，而是 PDK、耦合、封装、热调谐、良率、可靠性和客户 qualification。 | 中高；12-24 个月。 | 早期高端 SiPh/CPO 光引擎 ASP 高；长期每 bit 成本下降，但利润池迁移到硅光设计、封装测试和平台认证。 | SiPh 1.6T/3.2T 模块份额、CPO 平台量产、foundry PDK 成熟度、光引擎良率。 | EML pluggable 路线继续满足功耗/成本，硅光可靠性或封装良率不达标。 |
| 交换机/网络板 PCB > 网络板高速 CCL > resin / copper foil / lamination | 当前最硬的是 high-end glass cloth；树脂、铜箔、lamination 仍处于近平衡或局部软约束。 | 玻纤布扩产后，如果 AI server PCB、800G/1.6T switch、midplane/backplane 继续放量，CCL 厂会同时拉动 PPE/PPO/PTFE 树脂、HVLP 铜箔和 lamination 工艺。 | PPE/PPO/PTFE 高端树脂扩产周期、配方认证、低 Dk/Df 一致性、HVLP 铜箔粗糙度和 lamination 良率会成为新的短板。SABIC 已安排 PPE oligomer 扩产到 2026H2，说明供应链在提前补位。 | 中高；6-18 个月。 | 玻纤布涨价先行；若需求继续爆发，PPE/PPO/PTFE 和 HVLP 铜箔高端 mix 溢价上升，CCL 毛利向高端材料迁移。 | SABIC PPE 扩产兑现、Mitsui/JX HVLP 铜箔路线、CCL 厂 M8/M9/M10 认证、树脂/铜箔交期。 | 玻纤布持续卡住导致树脂/铜箔需求被压制，或 CCL 厂多源配方快速导入。 |
| 交换机/网络板 PCB > 网络背板 / Midplane PCB；网络 PCB 信号完整性测试 | 高层 PCB 已紧，但 midplane/backplane 作为单独子节点还没有看到全面短缺；更多是先进平台的项目制能力。 | AI rack 向 cableless、orthogonal backplane、1.6T/3.2T 高密度交换发展，背板/中板从少数旗舰平台扩散。 | 高速背板需要高层数、低损耗材料、背钻、电镀、阻抗控制、SI 仿真和整板测试；普通 PCB 产能不能迁移。 | 中高；9-24 个月。 | 高速 backplane/midplane ASP 和测试服务价格上行；普通板继续分化。 | AI rack 架构、switch board 层数、PCB 厂高端线体扩产、SI 测试设备采购。 | 继续采用线缆连接而非背板化，或 ODM 平台标准化降低项目制难度。 |
| 光纤连接器与被动光组件 > MPO / LC 连接器；陶瓷插芯 / Ferrule 中的 MPO/MTP/MT/MMC/VSFF | 普通 LC/SC 和传统 MPO 供给成熟；当前紧缺主要在数据中心光纤/连接产品整体，不是每个 ferrule 都缺。 | AI 数据中心光纤密度提高，Corning/NVIDIA 和 Corning/Meta 长协显示 advanced optical connectivity 被 hyperscaler 锁定；VSFF/MMC/SN-MT 等高密度形态进入更多部署。 | 高密度连接器需要低插损、高一致性、清洁/维护生态、专用 ferrule 和多源框架；普通陶瓷插芯产能不能直接替代。 | 中高；6-24 个月。 | 普通 LC/SC 价格稳定；VSFF/MMC/SN-MT、MPO/MTP 高性能件 ASP 和认证价值提升。 | Corning/US Conec/SENKO 多源框架、MMC/SN-MT 客户部署、高密度 patch panel 交期。 | 数据中心光纤架构简化，传统 MPO 继续够用，多源快速成熟。 |
| NIC / DPU / SmartNIC > NIC SerDes / PHY；RDMA / RoCE 卸载引擎 | 当前高端 NIC/DPU 供应由少数平台主导，但没有看到广泛缺货；更多是平台绑定和认证问题。 | 800G NIC 从训练集群扩散到推理和通用 AI 集群，1.6T endpoint 进入路线图，scale-up/open Ethernet 生态扩大。 | 高速 SerDes、FEC、RoCE/UEC/拥塞控制和 firmware 互操作集中在少数平台；客户 qualification 队列可能比晶圆产能更紧。 | 中；12-24 个月。 | 高端 800G/1.6T NIC、DPU/SuperNIC ASP 和 attach value 上升；普通 NIC 价格继续下行。 | Broadcom Thor/NVIDIA ConnectX/BlueField、Marvell/Intel/AMD 800G 产品、UEC/UALink 生态、云厂端点采购。 | 云厂自研 NIC/DPU、标准以太网降低专有溢价、1.6T endpoint 推迟。 |
| AI 集群交换机 > 交换机散热模块；光引擎 / CPO > CPO 热管理与供电接口 | 当前交换机散热仍能通过风冷、散热器、机箱设计承接；未见其单独形成主瓶颈。 | 102.4T/204.8T switch、CPO 光引擎、1.6T/3.2T 端口密度提升，交换机热流密度和光引擎温控要求上升。 | 光学器件对温度漂移敏感，CPO 同时有 ASIC 热源和光引擎热源；散热模块从机械件变成系统可靠性约束。 | 中；12-24 个月。 | 高端散热结构、液冷接口、热仿真和验证服务价值上升；普通风扇/散热片竞争。 | CPO switch 商用、交换机整机功耗、液冷交换机路线、CPO 温控失效率。 | CPO 延期、系统级功耗下降、传统风冷继续满足。 |
| Retimer / Linear Driver / SerDes 器件 > 参考时钟 / 抖动控制器件 | 时钟件供应商多，当前不是主瓶颈。 | PCIe Gen6、CXL 3.x、224G SerDes、1.6T 电互连验证窗口集中。Renesas 已推出 PCIe Gen6 时钟缓冲器/复用器，说明规格升级正在发生。 | jitter budget 收紧，客户验证和板级 SI 问题可能让高端 timing IC 临时紧张，但供给弹性高于 retimer。 | 中；6-18 个月。 | 高端 Gen6/224G timing IC 有 mix 溢价；普通时钟件价格稳定。 | Gen6 timing IC 交期、主板/交换机参考设计、客户验证失败率。 | 平台延期、竞争供应商快速导入。 |
| 光纤连接器与被动光组件 > 透镜 / 隔离器 / 滤波器；光模块被动光组件 | 当前普通微光学件和光胶供应相对成熟；局部高端件有认证但未成主短缺。 | 1.6T/3.2T、AOC、CPO、相干短距方案提高通道数、热稳定和低损耗要求。 | 高可靠、低损耗、耐热微光学件需要客户认证和一致性；普通透镜/滤波器不能直接替代高端件。 | 中；9-24 个月。 | 高端微光学件 ASP 上行，普通件价格竞争。 | Coherent/天孚通信/Senko 等高端组件订单、CPO/AOC 光路设计、客户认证周期。 | 光路集成度提升减少离散微光学件，供应商二供导入。 |

## 排除清单：量增但不优先判断为未来紧缺

| 节点 | 排除理由 | 仍需观察的例外 |
|---|---|---|
| AI 集群交换机 > 交换机主板 / Line card 装配 > SMT | 普通 SMT 产能弹性强，瓶颈在高速 PCB、连接器、测试和整机认证。 | 超大客户锁定高端 ODM 线体导致排产挤压。 |
| AI 集群交换机 > 交换机机箱 / 结构 | 金属结构件和普通机箱供应成熟。 | CPO/液冷交换机出现全新结构和热设计认证。 |
| DAC / ACC / AOC 线缆 > Twinax 铜导体 / 线材 | 铜线材本身可扩，真正约束在 reach、连接器、屏蔽、IC 和测试。 | 全球铜价和高端低损耗线材出现供给事件。 |
| DAC / ACC / AOC 线缆 > EEPROM / 管理 IC | 通用管理 IC 供应商多、替代性强。 | 安全认证、专用固件或客户锁定导致短期特规件缺货。 |
| 光纤连接器与被动光组件 > 陶瓷插芯 / Ferrule 的普通 LC/SC | 普通插芯成熟且多源。 | MPO/MTP/MT/MMC/VSFF 高密度 ferrule 不在普通插芯口径内，应单独看。 |
| 光纤连接器与被动光组件 > 光胶 / 封装辅助材料 | 普通光胶不是核心短板。 | CPO/硅光专用低应力、高耐热、低 outgassing 光胶通过大客户认证后可能出现局部紧张。 |
| 网络测试与认证设备 > 热箱 / 环境可靠性测试 | 通用热箱不是主瓶颈。 | 1.6T/CPO 自动化老化产线、定制夹具和高通道并测能力可能紧。 |

## 最值得提前跟踪的 6 条信号

| 信号 | 为什么重要 | 对应节点 |
|---|---|---|
| AI 后端 switch port 由 800G 转向 1.6T 的节奏是否提前到 2026H2 | 端口速率阶跃会同时拉动 224G SerDes、AEC、ACC、OSFP-XD 和测试认证产能，其中 retimer/AEC/test 的转紧确定性更高。 | Retimer SerDes PHY、CDR / 重定时核心、Retimer 封装与测试、AEC retimer cable、cable-end retimer IC、BERT、校准治具 / 认证服务。 |
| CPO 是否从单一平台样机转为 hyperscaler 多平台采购 | 只有多平台采购和量产节拍被确认后，FAU、CPO 封装测试、ELS、硅光和热管理才应从中高上调到高。 | External laser、FAU、CPO 封装测试、CPO 热管理、SiPh/PIC。 |
| 1.6T LPO/LRO 和 passive copper 的客户认证排队时间 | 低功耗互连路线越快，测试和模拟前端越容易成为新瓶颈。 | Equalizer / Linear amplifier、ACC Linear Driver、BERT、optical tester、thermal calibration、aging。 |
| 高端 glass cloth 扩产是否缓解 | 如果 glass cloth 继续卡住，其他 CCL 上游需求被压住；如果释放，树脂、铜箔、lamination 可能转紧。 | resin、HVLP copper foil、lamination、高速 CCL。 |
| Corning/US Conec/SENKO 等高密度连接器多源框架推进速度 | 多源慢则 VSFF/MMC/SN-MT 更容易紧；多源快则价格压力更早出现。 | MPO/VSFF/MMC/SN-MT、MT ferrule、高密度光连接。 |
| AI rack 是否从 cable-heavy 转向 backplane/midplane 或 cableless 架构 | 架构变化决定需求落在 AEC/ACC 还是高速背板/midplane。 | AEC/ACC、midplane/backplane PCB、SI 测试。 |

## 投研使用提醒

1. 这些节点不是“现在已经短缺”的主结论，而是下一轮供需错配 watchlist。后续个股研究要先验证公司是否真的做对应规格，而不是做普通产品。
2. 同一节点要拆规格：普通连接器、普通时钟、普通铜线、普通光胶很难涨价；224G、1.6T、CPO、VSFF/MMC、高通道 FAU、高速 low-loss 材料才有转紧逻辑。
3. 当前已明显紧缺的 EML/CW laser/InP、高端 glass cloth、高层高速 PCB、数据中心高密度光纤/连接产品，不纳入本稿“当前平衡”主候选；它们属于上一份当前瓶颈表的主线。
4. 最强的前瞻组合不是单个节点，而是 `1.6T/224G 端口迁移 -> Retimer SerDes PHY / CDR / Retimer 封装与测试 -> AEC retimer cable / cable-end retimer IC -> BERT / 校准治具 / 认证服务` 这条确定性更高的迁移链；`connector/cage` 与 `CPO 商用 -> ELS/FAU/SiPh/封装测试/热管理` 属于中高或条件型高，需要用交期、客户量产和良率数据继续确认。

## 来源索引

| 编号 | 来源 | 用途 |
|---|---|---|
| L0 | `docs/ai_chain_disassembly/nodes_mindmap_level_01_to_05_cleaned_2026-05-31.xlsx` | 本地 L2/L3/L4 P0 节点范围和 taxonomy path。 |
| P1 | `docs/ai_chain_disassembly/high_speed_network_optical_copper_supply_demand_price_2026-06-01.md` | 当前供需状态底稿，用于剔除已紧缺节点。 |
| P2 | `docs/ai_chain_disassembly/high_speed_network_top5_future_shortage_validation_2026-06-01.md` | 前五个高概率节点的复核依据，用于拆分 AEC/ACC 并下调 connector/cage、CPO FAU 的无条件高评级。 |
| S1 | https://www.prnewswire.com/news-releases/ai-back-end-switch-market-will-push-past-100-billion-by-2030-according-to-delloro-group-302678344.html | AI 后端交换机需求、800G 到 1.6T/3.2T 端口迁移。 |
| S2 | https://investors.broadcom.com/news-releases/news-release-details/broadcom-ships-tomahawk-6-worlds-first-1024-tbps-switch | 102.4T switch、100G/200G SerDes、CPO 选项。 |
| S3 | https://www.maxlinear.com/news/press-releases/2026/maxlinear-unveils-annapurna-224g-scale-up-retimer-to-extend-copper-connectivity-in-ai-data-centers | 224G scale-up retimer、1.6T electrical connectivity、AEC/on-board retimer。 |
| S4 | https://www.molex.com/en-us/products/connectors/high-speed-pluggable-io/active-electrical-cables-aec | AEC、retimer、224G PAM4、1.6T、铜 reach 延伸。 |
| S5 | https://www.te.com/en/products/connectors/pluggable-connectors-cages/osfp.html | OSFP、224G PAM4、1.6T connector/cable assembly。 |
| S6 | https://www.keysight.com/fr/en/about/newsroom/news-releases/2026/0319_pr26-056-keysight-expands-1-6t-interconnect-validation-technology-to-include-passive-copper-and-low-power-optics.html | 1.6T passive copper、ACC、LPO、LRO 测试验证。 |
| S7 | https://developer.nvidia.com/blog/scaling-ai-factories-with-co-packaged-optics-for-better-power-efficiency/ | NVIDIA CPO 商用时间、AI factory power efficiency 方向。 |
| S8 | https://www.broadcom.com/company/news/product-releases/63126 | Broadcom 200G/lane CPO 和后续 400G/lane 方向。 |
| S9 | https://www.oiforum.com/oif-launches-the-industrys-first-co-packaging-standard-the-3-2t-co-packaged-module-implementation-agreement/ | OIF 3.2T CPO、ELSFP external laser source、多厂商生态。 |
| S10 | https://www.sabic.com/en/news/49267-sabic-expands-ppe-oligomers-capacity-for-ai-and-5g-data-center-pcbs | PPE oligomer 扩产、AI server 高速 CCL 材料需求。 |
| S11 | https://insights.trendforce.com/p/glass-fiber-cloth-shortage | 高端玻纤布已紧缺，以及 CCL 规格向 1.6T NEZ/Q-glass 升级。 |
| S12 | https://www.jx-nmm.com/english/products/communication.html | 高速通信用低传输损耗铜箔与材料方向。 |
| S13 | https://www.mitsui-kinzoku.com/LinkClick.aspx?fileticket=Qte%2FiivIehw%3D&mid=1027&tabid=242 | 高速数字应用 HVLP 铜箔路线。 |
| S14 | https://www.corning.com/data-center/emea/en/home/solutions/mmc-connectors.html | MMC 高密度连接器、AI workload 光连接密度。 |
| S15 | https://www.senko.com/sn-mt-series/ | SN-MT VSFF 高密度连接器。 |
| S16 | https://www.sec.gov/Archives/edgar/data/24741/000120677426000273/glw4631061-ex991.htm | NVIDIA-Corning AI optical connectivity 合作和先进光连接制造扩张。 |
| S17 | https://asteralabs.gcs-web.com/news-releases/news-release-details/astera-labs-reports-first-quarter-2026-financial-results | Astera Labs AI connectivity 收入和 PCIe 6/scale-up fabric 需求侧验证。 |
| S18 | https://www.sec.gov/Archives/edgar/data/1807794/000162828026013205/credoq32026ex-9911.htm | Credo FY2026 Q3 收入增长和 AI connectivity 需求侧验证。 |

## 自审计

| 审计项 | 结果 |
|---|---|
| 是否聚焦“当前平衡但未来可能紧缺” | 通过：明确剔除当前已紧缺节点，并把候选限定为当前平衡/近平衡但触发条件清晰的节点。 |
| 是否覆盖高速网络与光/铜互连链的 L3/L4 | 通过：从本地 taxonomy 中筛选 CPO、DAC/ACC/AOC、Retimer、PCB/CCL、光连接、测试、NIC/DPU、交换机板卡/散热等相关 L3/L4。 |
| 是否把优先级 1/2/3 拆到可映射粒度 | 通过：已拆成 Retimer SerDes PHY、CDR / 重定时核心、Retimer 封装与测试、AEC retimer cable、cable-end retimer IC、线缆屏蔽 / 护套 / 测试、BERT、校准治具 / 认证服务、协议分析仪 / 流量发生器等子节点。 |
| 是否给出触发条件 | 通过：每个候选节点均列出下游爆发触发条件。 |
| 是否解释供给为什么跟不上 | 通过：逐项说明合格产能、良率、认证、测试、材料等级、封装和多源成熟度。 |
| 是否给出跟踪与反证 | 通过：每行均有硬指标和反证条件，并已把直接缺口证据不足的 connector/cage、CPO FAU 调为中高或条件型高，避免把前瞻 watchlist 写成确定短缺。 |
| 是否使用 A/B 级证据 | 通过：以公司官方、SEC 附件、行业研究、标准组织和本地节点表为主；C 级材料未作为核心结论。 |
