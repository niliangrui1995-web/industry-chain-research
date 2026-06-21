# 周度总览：AI产业链上下游雷达 - 滚动状态

更新时间：2026-06-22
最新报告：`artifacts/weekly_chain_tracking/ai_chain/2026-06-21.md`
覆盖窗口：2026-06-15 至 2026-06-21，北京时间
当前阶段：第九期全链雷达。已吸收光模块专项最新状态和 AI PCB 专项 2026-06-21 状态；本期主深挖为 `memory/storage/server parts + HBM test/probe` 与 `数据中心电力/并网/液冷/800VDC`。

## 任务边界

本任务负责 AI 产业链横向雷达、堵点账本、赛道优先级和上市主体映射，不重复展开光模块和 AI PCB 专项细节。每次执行必须读取：

- `artifacts/weekly_chain_tracking/ai_chain/state.md`
- `artifacts/weekly_chain_tracking/ai_chain/BASELINE_TEMPLATE.md`
- `artifacts/weekly_chain_tracking/ai_chain/` 下最近一期日期报告
- `artifacts/weekly_chain_tracking/optical_module/state.md`
- `artifacts/weekly_chain_tracking/ai_pcb/state.md`

堵点定义：必须意味着需求超过合格供给、可用产能、良率、交付能力或客户认证供应商。高壁垒、高毛利、高 HHI、长认证周期或股票热度不能单独作为堵点。

对话窗口摘要只保留两张表：`当前核心卡点｜原因/约束机制｜关键证据｜预计持续时间｜缓解/反转指标`，以及 `未来潜在卡点环节｜可能成为卡点的原因｜当前证据/争议｜预计成为卡点时间｜升级触发阈值｜反转指标`。

## 本期全链结论

1. `HBM / server DRAM / LPDRAM / NAND / enterprise SSD / AI server parts supply` 维持全链最硬 `hard_bottleneck`。HPE 10-Q/transcript、TrendForce enterprise SSD、Oracle RPO 与 Broadcom/Marvell AI 需求共同强化。预计 `2026H2-2027H1`，慢 ramp 可到 `2027H2`，中高置信。
2. `HBM final/package test / memory probe card / Cube Prober` 从未来观察上调为 `watch_to_soft / soft_bottleneck_candidate`。The Elec 披露 Techwing 获 SK hynix Cube Prober 首单，但合同金额、数量、交期和内存厂官方瓶颈表述仍缺，不能独立升 hard。预计 `2026H2-2027H2`，精确交期 `N/A`，中置信。
3. 光模块专项吸收结论：`InP substrate / 6 英寸合格 InP / EML / CW-DFB / UHP pump / ELS` 维持 `hard_bottleneck`。预计 EML/InP `2026H2-2027H1`，CW/ELS/UHP 尾部 `2027H2-2028H1`。
4. AI PCB 专项吸收结论：本期不升级任何 PCB 节点为 hard；`高端电子玻纤布 / Low Dk / Low CTE / T-glass / NER-glass / Q cloth` 与 `M7/M8/M9/M10 CCL / prepreg` 维持 `soft_bottleneck+`。沪电股份 2026-06-18 IR 强化高端材料阶段性偏紧证据。
5. `数据中心电力 / 并网 / transformer / switchgear / UPS / busway / rack power / CDU / 冷板 / 800VDC` 维持 `soft_bottleneck`，区域并网按 `regional hard operational bottleneck`。FERC 2026-06-18 大负载行动和 Google Brazos 提供 A 级方向证据；NVIDIA 800VDC 仍为 2027 起架构迁移观察。
6. `高端 MLCC / X6S / AI power passives` 新增为 `future_watch/watch_to_soft`。TrendForce 线索说明 2H26 起可能出现结构性短缺，但缺供应商官方 allocation、客户料号和公司收入拆分。

## 专项吸收状态

| 专项任务 | 最新状态 | 本期吸收结论 | 对全链排序影响 |
|---|---|---|---|
| 光模块及上游 | `artifacts/weekly_chain_tracking/optical_module/state.md` | InP/6 英寸合格 InP/EML/CW-DFB/UHP/ELS 为 hard；整机装配 soft/eased；FAU/主动对准/WLBI/ELSFP thermal 为 future watch。 | 光源链排当前核心卡点第 2；1.6T/3.2T driver/TIA/DSP/GaN/FAU/热管理列未来迁移。 |
| AI PCB 及上游 | `artifacts/weekly_chain_tracking/ai_pcb/state.md` | 高端电子玻纤布与 M7-M10 CCL/prepreg 并列 soft+；HVLP4/5、高频高速树脂、板厂良率/测试为 watch_to_soft。 | PCB 材料链排当前核心卡点第 3；M9/M10/Q cloth/HVLP/板厂测试列未来迁移。 |

## 当前全链堵点账本

| 节点 | 状态 | 造成堵点的机制 | 本期变化 | 预计持续时间 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|---|
| HBM / server DRAM / LPDRAM / NAND / enterprise SSD / AI server parts | `hard_bottleneck` | AI server、agentic inference、custom ASIC 和 AI cloud buildout 需求超过 qualified memory/storage/parts 供给；DRAM allocation、HBM stack/test、LPDRAM allocation、eSSD qualified output 与 LTA 锁量共同约束。 | strengthened | `2026H2-2027H1`；慢 ramp 可至 `2027H2`；中高置信 | 价格涨幅回落、库存恢复、多供方认证、客户不再提前锁量、ODM 不再提 parts constraint | 跟 HPE/Dell/SMCI、Micron/Samsung/SK hynix/Kioxia/SanDisk、eSSD 合约价与 LTA。 |
| HBM final/package test / memory probe card / Cube Prober | `watch_to_soft / soft_bottleneck_candidate` | HBM4E/HBM4/custom HBM 提高 KGD、stack/final test、探针卡和 Cube Prober 负荷。 | upgraded | `2026H2-2027H2`；精确交期 `N/A`；中置信 | 内存厂未点名测试瓶颈、Techwing/MJC/ATE backlog 或交期回落、二供扩产兑现 | 跟 Techwing DART/公告、MJC、Advantest、Teradyne、FormFactor、Technoprobe、MPI、精测电子订单/收入。 |
| NOR Flash / SLC NAND / 高可靠小容量存储 | `formal_observation/watch+` | HBM 和高层 3D NAND 抢占产能后，成熟节点 NOR/SLC 供给被挤压；边缘 AI、汽车、工业和高端网络需求拉动可靠存储。 | unchanged | `2026H2`，若 LTA 强化可延到 `2027`；中置信 | NOR/SLC 报价回落、补库结束、三家公司毛利/净利回落 | 跟 TrendForce 报价、兆易创新/东芯股份/普冉半导体 H1/H2 财报。 |
| InP substrate / 6 英寸合格 InP / EML / CW-DFB / UHP / ELS | `hard_bottleneck` | 出口许可、InP 衬底集中、6 英寸良率、老化测试、capacity rights、客户认证和 ELS 热稳定共同约束。 | unchanged | EML/InP `2026H2-2027H1`；CW/ELS/UHP 尾部 `2027H2-2028H1`；中高/中置信 | 许可正常化、6 英寸良率兑现、二供认证、交期/allocation/价格回落 | 交给光模块专项追 AXT/Coherent/Lumentum/Ciena/Corning。 |
| 高端电子玻纤布 / Low Dk / Low CTE / T-glass / NER / Q cloth | `soft_bottleneck+` | 窑炉、拉丝、电子级纱、织布、后处理、良率、专利和客户 AVL 限制 qualified output。 | strengthened | `2026H2-2027年底`；Q cloth/NER `2027H2-2028 watch`；中高置信 | 高端布报价回落、交期缩短、库存恢复，多供应商进入核心 AVL | 交给 PCB 专项跟台玻/Nittobo/高端布分产品。 |
| M7/M8/M9/M10 CCL / prepreg | `soft_bottleneck+` | 超低损耗树脂、高端玻纤布、HVLP 铜箔、新线 qualified output 和客户认证共同约束。 | strengthened | `2026H2-2027H1`；中高置信 | 报价停涨或回落，lead time 常态化，客户不再提前锁料，二供进入 AVL | 跟沪电、生益、台系 CCL、M8/M9/M10 lead time。 |
| HVLP4/5 铜箔与高频高速树脂 | `watch_to_soft` | 低粗糙度一致性、表面处理、树脂配方和客户认证约束；批量证据不足。 | unchanged | `2026H2-2027 watch`；精确持续 `N/A` | 多客户批量供货、加工费回落、国产良率确认 | 跟德福、诺德、嘉元、铜冠与树脂供应商。 |
| 数据中心并网 / firm power / grid operations | `soft_bottleneck`；区域 `hard operational` | 大负载接入、成本分摊、电源与输配电建设、备用容量、动态负载稳定性约束。 | strengthened | 区域 `2026H2-2030`；中高置信 | reserve margin 改善，容量/电价压力回落，真实项目延期减少 | 跟 FERC/PJM/ERCOT/utility；项目级核对 site control、interconnection、permit、construction、equipment order/prepayment。 |
| Transformer / switchgear / UPS / busway / rack PDU / CDU / 冷板 | `soft_bottleneck/watch` | 高功率 rack、新建 AI factory 与存量风冷机房逐机架改造共同拉动长交期设备、系统认证和现场集成。 | strengthened | `6-24 个月`；单品精确交期 `N/A`；中置信 | 设备交期正常化，项目不再因设备延期；已锁队列订单取消且 slot 无法再分配 | 跟单品 lead time、预付款/排产锁定、Chinese OEM/prefab、Brazos/OCP 规格、A 股收入拆分。 |
| 800VDC / SST / SiC / GaN power conversion | `watch_to_soft` | 高功率 rack 推动 medium-voltage-to-rack、GaN/SiC、hot-swap/protection 和系统认证。 | attention_up | `2027-2028`；精确持续 `N/A` | 800VDC 推迟，传统架构继续满足；design win 无法转收入 | 跟 NVIDIA ecosystem、Delta/Lite-On/Megmeet、麦格米特等 design win 转量产。 |
| CoWoS / EFB / SoIC / advanced packaging / substrate | `soft_bottleneck/watch+` | GPU/ASIC multi-die 和 HBM 需求推高 2.5D/3D 封装、基板、键合、测试和设备负荷。 | unchanged | `2026H2-2027H1` 偏紧，2027 后边际缓解 | TSMC/OSAT 交期恢复，客户不再锁封装产能 | 跟 TSMC/ASE/Amkor/基板/设备。 |
| AI networking switch ASIC / NIC / DPU / retimer / custom XPU | `strategic_watch/watch_to_soft` | Broadcom/Marvell/NVIDIA/Oracle 需求强，但缺 silicon allocation、lead time 或出货受限证据。 | attention_up | `N/A`；出现 allocation 后升级 | 出货顺畅，客户部署不推迟 | 跟 Broadcom/Marvell/NVIDIA/Arista。 |
| High-end MLCC / X6S / AI power passives | `future_watch/watch_to_soft` | AI ASIC/accelerator 板卡功率上升，带动小尺寸高容高温 MLCC 用量和可靠性要求。 | new | `2026H2-2027` 可能升级；中置信 | 扩产兑现、价格不涨、lead time 正常、客户多源认证顺利 | 跟村田/TDK/三星电机/国巨/风华高科/三环集团订单、料号、ASP、毛利。 |

## 2026-06-21 芯碁微装先进封装设备最小跟踪卡

新增：[芯碁微装 688630.SH 最小跟踪卡](../../company_tracking/688630.SH/state.md)。定位为 `advanced_packaging_equipment_watch / evidence_gap_card`。可确认的是 WLP/PLP/IC 载板直写光刻设备、WLP 2000 重复订单/出货与多个头部客户验收量产、WLP 在手订单突破 1 亿元的 B 级公司官微转述；不能把 SK 海力士清州 HBM4 封装备产、Amkor-TSMC 美国先进封装协议或类 CoWoS-L 量产线索直接写成芯碁微装 HBM4/CoWoS 客户、订单、收入占比或交付节奏。

## 2026-06-22 三环集团高端 MLCC 最小跟踪卡

新增：[三环集团 300408.SZ 最小跟踪卡](../../company_tracking/300408.SZ/state.md)。定位为 `secondary_track_up / fundamental_main_beneficiary_candidate / evidence_gap_card`。可确认的是 AI server 高端 MLCC/X6S 与 AI power passives 需求上行已进入 `future_watch/watch_to_soft`，且既有 MLCC 次主线材料把三环集团列为更偏基本面主受益候选；不能把行业侧高端 MLCC 交期、TAM、涨价或 Rubin 价值量线索直接写成三环集团 AI server 客户、料号、订单、收入拆分或毛利兑现。

## 本期深挖方向

1. `HBM/DRAM/LPDRAM/NAND/eSSD + AI server parts supply + HBM test/probe`：重点跟踪 HPE/Dell/SMCI、Micron/Samsung/SK hynix/Kioxia/SanDisk、TrendForce eSSD/LPDRAM、HBM4/HBM4E 认证与 LTA、Techwing/MJC/ATE/probe card 交期和合同规模。
2. `AI cloud capex -> 数据中心电力/并网 + 液冷 + 800VDC`：重点把区域 hard operational 约束和全球设备/液冷单品 soft/watch 分开；跟踪 FERC/PJM/ERCOT、Oracle/Meta/Google/Microsoft/Amazon CapEx、Google Brazos/OCP、NVIDIA 800VDC、transformer/switchgear/UPS/CDU/PDU lead time、A 股订单纯度。

## 未来 6-24 个月卡点迁移

| 节点/赛道 | 当前状态 | 未来状态 | 需求触发 | 供给滞后机制 | 可能时间 | 升级触发阈值 | 证据缺口 | 反转指标 |
|---|---|---|---|---|---|---|---|---|
| HBM test / memory probe card / Cube Prober | watch_to_soft | soft_bottleneck_candidate | HBM4E/HBM4/custom HBM、Rubin Ultra 和更高 stack/带宽要求 | KGD/stack/final test 时间增加、探针卡设计切换、Cube Prober 全检导入、客户 qualification | `2026H2-2027H2` | 内存厂或两家以上测试/探针卡/handler 供应商披露 lead time/allocation、客户预付、交期推迟或追加订单 | 官方交期/allocation、合同规模、A 股订单/收入 | MJC/Techwing/ATE 产能兑现、二供认证、HBM qualification 顺畅。 |
| Enterprise SSD / LPDRAM | hard side expansion | likely_future_bottleneck | AI Agent、long-context inference、CSP storage hierarchy | 低库存、订单超过产出、企业级 qualification 慢，DRAM wafer allocation 竞争 | `2026H2-2027H1` | eSSD 合约价继续上行、CSP LTA、内存厂点名供应紧张 | 内存厂财报和客户 allocation | 库存恢复，合约价回落。 |
| 高端 MLCC / X6S / AI power passives | future_watch | watch_to_soft | CSP 自研 ASIC、高功率 AI 板卡、电源完整性要求 | 高容高温小尺寸 MLCC 扩产和认证慢 | `2026H2-2027` | 两家以上 MLCC 龙头披露 AI server/ASIC 订单、lead time 拉长或涨价；A 股披露料号、收入占比 | 客户料号、ASP、毛利、库存、订单 | 扩产兑现、价格不涨、lead time 正常。 |
| 1.6T/3.2T optical driver/TIA/DSP/GaN/FAU/test/thermal | watch_to_soft | likely_future_bottleneck | 1.6T/3.2T、CPO/NPO/ELS | 高速 analog、精密耦合、测试节拍、热稳定 | `2026H2-2028` | 多供应商 lead time/allocation、客户预付、良率拖累 | 单品交期/良率 | 扩产兑现、二供认证。 |
| M9/M10/Q cloth/NER/HVLP4/5 | soft+/watch | likely_future_bottleneck | Rubin、AI switch、224G+ high-speed board | 新材料认证、AVL、良率和二供慢 | `2026H2-2028` | 官方 allocation、报价上涨、订单延期、客户提前锁料 | 分产品、客户、交期 | 多家供应商稳定量产，报价回落。 |
| 800VDC/SST/GaN/SiC + 存量风冷液冷改造 | soft/watch | likely_future_bottleneck | 高功率 rack、AI factory 投产、Brazos 类逐机架改造 | system certification、设备 lead time、现场集成、OCP/客户规格统一 | `2027-2028` | design win 转量产、Brazos/OCP 多供应商量产、云厂商存量改造项目 | 单品 allocation、项目清单、订单/收入拆分 | 800VDC 推迟、传统架构满足、存量改造难规模化。 |
| CoPoS/FOPLP/glass core/TGV | watch | long_horizon_watch | Package 面积和成本压力 | TGV、对位、翘曲、良率和设备生态 | `2027-2028+` | 试产通过、客户 tape-out、设备订单 | 量产良率、成本、客户产品、设备产能 | CoWoS 扩产满足需求，面板化延后。 |
| AI networking silicon / retimer / substrate | strategic_watch | watch_to_soft | 102.4T switch、NVLink Fusion、custom XPU | SerDes/IP、advanced process、substrate/package | `2026H2-2027` | silicon/substrate/package 被点名限制出货 | 直接交期证据 | 交付顺畅，客户不延期。 |

## 三类排名快照

### 细分赛道结构重要性

1. HBM / DRAM / LPDRAM / NAND / eSSD / HBM test
2. Advanced packaging / CoWoS / SoIC / substrate
3. Data-center power / grid / rack power / liquid cooling / 800VDC
4. Optical source / InP / EML / CW + 1.6T migration
5. AI PCB / high-end glass cloth / CCL / HVLP
6. AI networking / custom ASIC / retimer / NIC/DPU
7. High-end MLCC / passives

### 业绩弹性

1. eSSD/NAND/DRAM/HBM 供应商
2. AI PCB 高端材料/板厂
3. 光源/InP/CW-DFB/1.6T 光互连
4. Power/liquid/rack power/800VDC
5. 高端 MLCC/passives
6. HBM test/probe/tooling

### 交易弹性

1. A 股 PCB/CCL/HVLP/高端材料组
2. A 股光模块/光器件/设备组
3. A 股 power/liquid/800VDC 组
4. NOR/SLC 国内存储侧翼
5. US/KR/TW memory/HBM 龙头
6. US networking/custom ASIC 龙头

## 下期默认跟踪问题

1. HPE/Dell/SMCI/ODM 是否继续披露 DRAM/NAND/eSSD/parts supply constraints、purchase commitments、inventory 或 backlog 转收入受限？
2. Micron、Samsung、SK hynix、Kioxia/SanDisk 是否在最新财报或业绩会确认 eSSD/NAND/LPDRAM/HBM 价格、LTA、库存和 capacity allocation？
3. Techwing、MJC、Advantest、Teradyne、FormFactor、Technoprobe、MPI 或内存厂是否披露 HBM test/probe/Cube Prober lead time、合同规模、追加订单或 allocation？
4. FERC/PJM/ERCOT/utility 是否给出大负载接入规则变化；Oracle/Meta/Google/Microsoft/Amazon 是否继续上修 AI CapEx 或披露电力/设备/液冷对投产节奏的影响？
5. Google Brazos 是否进入 OCP 规格、多供应商量产或云厂商存量机房改造项目；A 股液冷/电源公司是否披露真实客户、订单、收入和毛利？
6. 沪电、台玻、Nittobo、台系 CCL、德福/诺德/嘉元是否继续披露高端玻纤布、M8/M9/M10、HVLP4/5 交期、报价、客户认证和良率？
7. TrendForce MLCC 线索能否被村田、TDK、三星电机、国巨、风华高科、三环集团等官方订单、料号、ASP 或收入拆分验证？

## 最近证据源

- HPE 10-Q: https://www.sec.gov/Archives/edgar/data/1645590/000164559026000055/hpe-20260430.htm
- HPE Q2 FY26 transcript: https://investors.hpe.com/~/media/Files/H/HP-Enterprise-IR/documents/q2-2026/q2-2026-transcript.pdf
- TrendForce enterprise SSD: https://www.trendforce.com/presscenter/news/20260611-13092.html
- TrendForce NOR Flash / SLC NAND: https://www.trendforce.com/presscenter/news/20260616-13102.html
- The Elec / Techwing Cube Prober: https://www.thelec.net/news/articleView.html?idxno=11441
- FERC large-load action: https://www.ferc.gov/news-events/news/ferc-launches-aggressive-targeted-action-speed-large-load-integration
- Google Brazos: https://cloud.google.com/blog/topics/systems/brazos-liquid-cooling-system-for-air-cooled-data-centers
- Oracle FY26 results: https://investor.oracle.com/investor-news/news-details/2026/Oracle-Announces-Record-Q4-and-FY-2026-Results-Driven-by-Cloud-Infrastructure--Cloud-Applications/default.aspx
- Broadcom Q2 FY26 results: https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-second-quarter-fiscal-year-2026-financial
- Marvell Q1 FY27 results: https://investor.marvell.com/news-events/press-releases/detail/1023/marvell-technology-inc-reports-first-quarter-of-fiscal-year-2027-financial-results
- NVIDIA 800VDC: https://www.nvidia.com/en-us/data-center/technologies/800vdc/
- 沪电股份投资者关系记录: https://data.eastmoney.com/notices/detail/002463/AN202606181823669664.html
- TrendForce high-end MLCC: https://www.trendforce.com/presscenter/news/20260617-13105.html
- TrendForce CoPoS/FOPLP/glass substrate: https://www.trendforce.com/presscenter/news/20260617-13107.html

## 对话窗口摘要

### 当前核心卡点表

| 核心卡点 | 原因/约束机制 | 关键证据 | 预计持续时间 | 缓解/反转指标 |
|---|---|---|---|---|
| HBM/DRAM/LPDRAM/NAND/eSSD + AI server parts | Qualified memory/storage/parts 供给、HBM stack/test、DRAM allocation、eSSD validation 与 ODM 采购同时约束 backlog 转收入。 | HPE 10-Q/transcript、TrendForce eSSD、Oracle RPO。 | `2026H2-2027H1`，慢 ramp 可至 `2027H2`；中高置信。 | 合约价回落、库存恢复、客户不再提前锁量、ODM 不再提 supply constraints。 |
| HBM test/probe/Cube Prober | HBM4E/HBM4 提高 KGD、stack/final test、探针卡和 Cube Prober 负荷。 | The Elec/Techwing 首单，叠加 MJC/probe 线索。 | `2026H2-2027H2`；精确交期 `N/A`，缺合同规模和内存厂官方瓶颈。 | 内存厂不点名测试限制，Techwing/MJC/ATE backlog 或交期回落。 |
| InP/EML/CW-DFB/UHP/ELS | InP 出口许可、6 英寸合格产能、老化测试、客户认证和锁产能限制光源交付。 | 光模块专项、AXT/TrendForce/Ciena 证据链。 | EML/InP `2026H2-2027H1`；CW/ELS/UHP 尾部 `2027H2-2028H1`。 | 许可正常化、二供认证、光源价格/交期/allocation 回落。 |
| 高端电子玻纤布 + M7-M10 CCL/prepreg | 高端布、超低损耗树脂、HVLP 铜箔、配方良率和客户 AVL 同时约束 qualified output。 | AI PCB 专项、沪电 2026-06-18 IR。 | 玻纤布 `2026H2-2027年底`；CCL `2026H2-2027H1`；中高置信。 | 报价回落、lead time 常态化、多供应商进入核心 AVL。 |
| 数据中心并网/电力设备/液冷/800VDC | Firm power、interconnection、transformer/switchgear/UPS、rack power、CDU/冷板和现场集成约束可投产算力。 | FERC 大负载行动、Google Brazos、Oracle RPO、NVIDIA 800VDC。 | 并网区域性 `2026H2-2030`；设备/液冷 `6-24 个月`；800VDC `2027-2028 watch`。 | Tariff 改革、设备交期正常、真实项目延期减少、800VDC 推迟或传统架构继续满足。 |

### 未来潜在卡点表

| 潜在卡点环节 | 可能成为卡点的原因 | 当前证据/争议 | 预计成为卡点时间 | 升级触发阈值 | 反转指标 |
|---|---|---|---|---|---|
| 高端 MLCC/X6S 与 AI power passives | AI ASIC/accelerator 板卡功率上升，带动小尺寸高容高温 MLCC 用量和可靠性要求。 | TrendForce B 级线索强；缺供应商官方 allocation 和 A 股客户料号。 | `2026H2-2027` | 两家以上 MLCC 龙头披露涨价/lead time/AI server 客户订单；A 股披露料号、收入占比和毛利。 | 扩产兑现、价格不涨、lead time 正常、客户多源认证顺利。 |
| CoPoS/FOPLP/玻璃基板/TGV | Package 面积和成本压力推动面板化与玻璃基板，但 TGV、对位、翘曲和良率难。 | TrendForce 指向 2026 验证、2027 试产、2H28 量产；当前不是量产瓶颈。 | `2027-2028+` | TSMC/OSAT/设备/基板厂披露试产通过、客户导入或产能上修。 | CoWoS 扩产满足需求，玻璃基板继续延后。 |
| 1.6T/3.2T 光电芯片/FAU/主动对准/热管理 | 高速 analog、精密耦合、老化测试和散热良率随 1.6T/3.2T 升级而收窄。 | Marvell 需求强，光模块专项列 future watch；缺单品交期。 | `2026H2-2028` | 多供应商披露 driver/TIA/DSP/FAU/thermal lead time、allocation 或良率拖累。 | 二供认证快，1.6T/3.2T 放量顺畅，交期回落。 |
| M9/M10/Q cloth/NER/HVLP4/5 与成品板良率/测试 | Rubin、AI switch、224G+ 高速板推动材料、加工和测试窗口同步收窄。 | PCB 专项为 soft+/watch_to_soft；沪电 IR 支持材料偏紧但成品板 hard 证据不足。 | `2026H2-2028` | 官方 allocation、报价上涨、交期延长、客户提前锁料或成品板良率被点名。 | 多家供应商稳定量产，报价回落，板厂良率改善。 |
| AI networking ASIC/NIC/DPU/retimer/substrate | 51.2T/102.4T switch、custom XPU、CPO/NPO 拉动先进制程、SerDes、package/substrate。 | Broadcom/Marvell A 级需求强；缺 silicon/substrate allocation。 | `2026H2-2027` | 官方披露交期、allocation、客户排产延期或 substrate/package 限制。 | 交付顺畅，客户不延期，封装/基板扩产跟上。 |
| 800VDC-SST-GaN-SiC 与存量风冷液冷改造 | 1MW rack、电源转换效率、铜用量和逐机架改造推动架构迁移。 | NVIDIA/Google 为 A 级方向证据；量产订单和 A 股收入证据缺。 | `2027-2028` | 800VDC design win 转量产；Brazos/OCP 出现多供应商量产和云厂商改造项目。 | 传统架构继续满足，存量改造难规模化，design win 不转收入。 |
