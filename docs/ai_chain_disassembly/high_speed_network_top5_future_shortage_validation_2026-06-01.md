# 高速网络与光/铜互连链前五个“高概率转紧”节点复核

日期：2026-06-01

## 复核结论

严格按“下游放量证据 + 供给刚性 + 直接转紧证据 + 替代路径”四个门槛复核后，原先 5 个节点不能全部无条件维持“高”。

| 序号 | 原节点 | 原评级 | 复核评级 | 结论 |
|---:|---|---|---|---|
| 1 | Retimer / Linear Driver / SerDes 器件 > Retimer SerDes PHY / CDR / Equalizer / Linear amplifier | 高 | 高，但需收窄到 224G/1.6T retimer、SerDes PHY、AEC/板级 retimer | 需求和技术门槛均强，是真正高概率转紧节点；不应泛化到所有 linear driver。 |
| 2 | DAC / ACC / AOC 线缆 > ACC Linear Driver 和 AEC retimer cable | 高 | 拆分：AEC retimer cable 高；ACC linear driver 中高 | AEC 的证据强于 ACC。ACC 仍有需求，但受 passive DAC、AEC、AOC/LPO 路线竞争影响。 |
| 3 | AI 集群交换机 > 交换机主板 / Line card 装配 > connector / cage 与 DAC / ACC / AOC 线缆 > 高速线缆连接器 / Cage | 高 | 中高 | 224G/1.6T OSFP/OSFP-XD 需求明确，但连接器/cage 供应商更多，缺少直接 allocation 或 lead-time 拉长证据。 |
| 4 | 网络测试与认证设备 > BERT / 光模块测试仪 / 协议分析仪 / 流量发生器 | 高 | 高，但定义为“验证/测试产能瓶颈”而非单纯设备缺货 | 1.6T 铜缆、ACC、AEC、LPO/LRO、CPO 并行验证，测试窗口、夹具、工程资源更可能转紧。 |
| 5 | 光引擎 / CPO > Fiber array / FAU 与 CPO 封装对准与测试 | 高 | 中高；CPO 多客户放量后升为高 | CPO 方向和供给刚性成立，但当前对 FAU/对准测试的直接缺口证据还不够，属于条件型高概率节点。 |

## 判断框架

“转紧概率高”不能只看技术难度。这里使用四个判断门槛：

1. 下游需求是否已经进入明确放量窗口，例如 800G 向 1.6T、224G/lane、scale-up fabric、PCIe Gen6/CXL、CPO。
2. 供给是否刚性，例如高速 SerDes/retimer 设计、认证周期、封装/测试良率、客户导入周期、专用仪器和夹具。
3. 是否有直接或准直接的转紧证据，例如收入超预期、客户/供应商明确提到 demand、qualification 扩容、volume shipment、lead time、allocation。
4. 是否存在替代路径稀释转紧，例如 passive DAC、ACC、AEC、AOC、LPO/LRO、pluggable optics、CPO 之间的路线切换。

## 逐项复核

### 1. Retimer / SerDes PHY / CDR / Equalizer / Linear amplifier

复核评级：高，但需要收窄。

支持证据：

- 下游端口速率迁移明确。Dell'Oro 2026 年 1 月预测 AI 后端网络端口将从 800G 继续迁移，1600G 预计在 2027 年成为主流，3200G 在 2030 年到来；这直接推高 224G/lane SerDes、retimer、equalization 和链路裕量需求。
- Broadcom Tomahawk 6 已把 100G/200G SerDes、long-reach passive copper、CPO option 放进同一个 AI scale-up/scale-out 平台叙事里，说明高速 SerDes 和铜/光互连不是边缘需求。
- MaxLinear 在 2026 年推出 224G scale-up retimer，定位是 AI data center 的 AEC 和板级 retimer；Credo FY2026 Q3 收入同比增长 201.5%，Astera Labs Q1 2026 收入同比增长 93%，都指向 AI 互连硅片需求强劲。

约束和反证：

- 这些证据证明“需求强、门槛高、资格认证紧”，但还不是所有 retimer/linear driver 都已经缺货。
- Linear driver 的供需弹性通常高于 224G DSP/retimer/SerDes IP，不应和高端 retimer 混为一个评级。

结论：224G/1.6T retimer、SerDes PHY、AEC/板级 retimer 维持高；普通 linear amplifier/driver 降为中高或随具体规格判断。

需要跟踪：

- Astera、Credo、MaxLinear、Broadcom 对 224G、AEC、PCIe Gen6、CXL、NVLink/UALink/Ethernet scale-up 的 backlog、供货周期和客户 ramp 口径。
- 800G 到 1.6T 端口迁移是否提前，特别是 2026H2-2027 的 1.6T 交换机和 AI rack 量产节奏。

### 2. ACC Linear Driver 和 AEC Retimer Cable

复核评级：AEC retimer cable 高；ACC linear driver 中高。

支持证据：

- Molex 的 AEC 产品说明明确把 AEC 定位为使用 retimer technology 延长高速信号距离，并覆盖 1.6T/224G PAM4 方向。
- Keysight 的 1.6T interconnect validation 资料把 AEC、ACC、passive DAC、LPO/LRO 都列入 AI/HPC 网络关键互连类型，说明有源铜方案已经进入正式测试和导入窗口。
- MaxLinear 明确称 224G retimer 面向 AEC 和板级 retimer 应用，说明 AEC 的核心瓶颈会落到 retimer/DSP、低功耗封装、热设计和链路调参。

约束和反证：

- ACC 依赖 linear driver，可覆盖更短距离和更低功耗场景，但与 passive DAC、AEC、AOC/LPO 存在路线竞争。
- AEC 的技术壁垒、BOM 价值量和客户认证难度高于普通 ACC，因此“高”应主要给 AEC retimer cable。

结论：AEC retimer cable 维持高；ACC linear driver 单独列为中高。

需要跟踪：

- AI rack 内 3m、5m、7-9m 连接距离组合变化。
- 云厂商是否从 passive DAC/ACC 转向 AEC，或在 1.6T 端口上提高 AEC 采用率。
- Retimer cable 的功耗、散热、误码率、热插拔可靠性认证节奏。

### 3. 高速线缆连接器 / Cage

复核评级：中高。

支持证据：

- TE OSFP 资料显示 OSFP 连接器和线缆组件支持 200Gbps 到 1.6T，并覆盖 224G PAM4 signaling，需求触发明确。
- OSFP、OSFP-XD、1.6T/3.2T 端口密度提升，会提高 cage、连接器、屏蔽、散热、SI 设计难度。
- 高速连接器不是普通机械件，224G PAM4 下插损、串扰、散热和公差都会直接影响系统良率。

约束和反证：

- 连接器/cage 的全球供应商群体相对更宽，TE、Molex、Amphenol、Samtec、FIT 等都可参与，不像高端 retimer 或 1.6T 测试仪那样集中。
- 目前公开证据更多是“规格升级”和“产品路线”，不是直接的缺货、排产满载或交期拉长。

结论：从高下调到中高。它更可能在高端 OSFP/OSFP-XD、液冷适配、EMI/SI 认证和特定客户料号上转紧，而不是整个连接器/cage 大类全面短缺。

需要跟踪：

- OSFP-XD、1.6T copper/optics port 的高端料号 lead time。
- 主流交换机 ODM/OEM 是否出现 cage、连接器、散热结构件二供不足。
- 供应商毛利、订单交期和扩产口径是否出现明显变化。

### 4. 网络测试与认证设备

复核评级：高，但瓶颈形态是“验证/认证产能”，不是简单设备现货缺口。

支持证据：

- Keysight 2026 年 3 月发布 1.6T Ethernet interconnect validation 扩展，明确覆盖 passive copper DAC、ACC、LPO、LRO、AEC，并指出这些互连是 AI/HPC scale-out 和 scale-up 部署的关键。
- 同一时间 1.6T optical、passive copper、ACC、AEC、LPO/LRO、CPO 多路线并行爬坡，会让 BERT、协议分析仪、流量发生器、夹具、reference platform、FAE 资源同时承压。
- 测试认证是 ramp 的前置瓶颈，一旦客户验证周期被拉长，会直接影响供货确认和量产爬坡。

约束和反证：

- 公开资料未直接证明 Keysight、Anritsu、Spirent 等设备已经全面缺货。
- 更高概率的转紧是客户实验室、第三方认证、供应商应用工程和测试夹具窗口紧张。

结论：维持高，但名称建议改为“1.6T/224G 网络验证与认证产能”。这比“测试仪器硬件短缺”更准确。

需要跟踪：

- 1.6T BERT、protocol analyzer、traffic generator、optical/electrical fixture 的交期。
- 光模块、铜缆、交换机、CPO 供应商的客户验证周期是否拉长。
- 测试服务商、仪器厂商的订单和 backlog 口径。

### 5. CPO FAU 与封装对准/测试

复核评级：中高；条件型高。

支持证据：

- Dell'Oro 预计 CPO adoption 在预测期内加速，且由 NVIDIA 推动。
- NVIDIA 已把 CPO 放进 AI factory power efficiency 和产业协作路线；Broadcom 宣布第三代 200G/lane CPO，并提到 TH5-Bailly CPO volume-production、fiber routing、automated testing、scalable manufacturing process 等成熟度提升。
- CPO 的光纤阵列、FAU、edge coupling、fiber routing、自动化对准和封装测试具有明显供给刚性，良率爬坡可能慢于需求。

约束和反证：

- CPO 仍处在从平台验证到多客户放量的转换期，公开证据对 FAU/对准测试“已经转紧”的证明不足。
- 如果 2026-2027 主流 AI 集群仍以 pluggable optics 和铜互连为主，FAU/CPO 对准测试的短期转紧会被推迟。

结论：不建议无条件列为高。更准确的评级是中高；当 NVIDIA/Broadcom CPO 进入多客户批量部署、CPO switch/光引擎订单和高密度 CPO fiber cable 量产同时确认后，再升为高。

需要跟踪：

- NVIDIA/Broadcom CPO 方案是否从 demo/partner milestone 进入客户 volume deployment。
- Corning、FIT、Twinstar、光引擎厂商对 fiber array、detachable fiber connector、CPO cable、PLS cage/connector 的出货和扩产。
- CPO 封装良率、自动化对准设备、测试节拍是否成为系统交付瓶颈。

## 对原前瞻表的修正建议

建议把原来的“5 个高概率转紧”改成以下读法：

| 分层 | 节点 | 建议评级 |
|---|---|---|
| 第一梯队 | 224G/1.6T retimer、SerDes PHY、AEC/板级 retimer | 高 |
| 第一梯队 | AEC retimer cable | 高 |
| 第一梯队 | 1.6T/224G 网络验证与认证产能 | 高 |
| 第二梯队 | ACC linear driver | 中高 |
| 第二梯队 | OSFP/OSFP-XD 高速连接器 / cage | 中高 |
| 第二梯队 | CPO FAU 与封装对准/测试 | 中高，CPO 多客户放量后升高 |

## 来源台账

- Dell'Oro / PRNewswire, `AI Back-End Switch Market Will Push Past $100 Billion by 2030`, 2026-01-21. https://www.prnewswire.com/news-releases/ai-back-end-switch-market-will-push-past-100-billion-by-2030-according-to-delloro-group-302678344.html
- Broadcom, `Broadcom Ships Tomahawk 6: World's First 102.4 Tbps Switch`, 2025-06-03. https://investors.broadcom.com/news-releases/news-release-details/broadcom-ships-tomahawk-6-worlds-first-1024-tbps-switch
- MaxLinear, `MaxLinear Unveils Annapurna 224G Scale-Up Retimer to Extend Copper Connectivity in AI Data Centers`, 2026-03-16. https://www.maxlinear.com/news/press-releases/2026/maxlinear-unveils-annapurna-224g-scale-up-retimer-to-extend-copper-connectivity-in-ai-data-centers
- Molex, `Active Electrical Cables`. https://www.molex.com/en-us/products/connectors/high-speed-pluggable-io/active-electrical-cables-aec
- TE Connectivity, `OSFP Connectors & Cable Assemblies`. https://www.te.com/en/products/connectors/high-speed-pluggable-io-connectors-and-cages/osfp.html
- Keysight, `Keysight Expands 1.6T Interconnect Validation Technology to Include Passive Copper and Low Power Optics`, 2026-03-19. https://www.keysight.com/fr/en/about/newsroom/news-releases/2026/0319_pr26-056-keysight-expands-1-6t-interconnect-validation-technology-to-include-passive-copper-and-low-power-optics.html
- Astera Labs, `Astera Labs Reports First Quarter 2026 Financial Results`, 2026-05-05. https://asteralabs.gcs-web.com/news-releases/news-release-details/astera-labs-reports-first-quarter-2026-financial-results
- Credo, SEC exhibit 99.1, Q3 FY2026 financial highlights. https://www.sec.gov/Archives/edgar/data/1807794/000162828026013205/credoq32026ex-9911.htm
- NVIDIA Technical Blog, `How Industry Collaboration Fosters NVIDIA Co-Packaged Optics`, 2026. https://developer.nvidia.com/blog/how-industry-collaboration-fosters-nvidia-co-packaged-optics/
- Broadcom, `Broadcom Announces Third-Generation Co-Packaged Optics (CPO) Technology with 200G/lane Capability`, 2025-05-15. https://investors.broadcom.com/news-releases/news-release-details/broadcom-announces-third-generation-co-packaged-optics-cpo

## 自审

- 本复核没有把“技术难”直接等同于“供给短缺”。
- 对直接缺货证据不足的节点做了降级或条件化处理。
- 对同一原节点内证据强弱不同的子项做了拆分，尤其是 AEC retimer cable 与 ACC linear driver、retimer/SerDes 与普通 linear driver。
- 原高评级中，真正可无条件保留的更接近三个：224G/1.6T retimer/SerDes、AEC retimer cable、1.6T/224G 验证认证产能。
