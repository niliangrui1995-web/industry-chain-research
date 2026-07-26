# 周度跟踪：光模块及上游细分环节 - 滚动状态

更新时间：2026-07-26 18:50 CST
最新周报：`artifacts/weekly_chain_tracking/optical_module/2026-07-26.md`
本周窗口：2026-07-20 至 2026-07-26
补扫窗口：2026-06-29 至 2026-07-19
下次运行先读：本文件、`BASELINE_TEMPLATE.md`、`2026-07-26.md` 与自动化记忆。

## 任务边界

- 覆盖：光模块/光引擎、800G-3.2T、硅光/CPO/OCS、激光器与材料、DSP/TIA/driver、无源器件、光纤连接、封装测试和模块/光引擎热管理接口。
- 每期 1 个主深挖，最多 3 个次级环节；扫描其余节点未来 6-24 个月迁移。
- “卡点”必须有需求超过合格供给、有效产能、良率、交付或认证供应商的证据；技术难度、集中度、标准或概念热度本身不是卡点。
- 公司映射分开写能力、客户认证、订单、收入和利润；没有硬证据不得越级。
- 公司排名分基本面质量、业绩弹性、交易弹性。投资判断须通过点时预期门槛；无可复核共识时 formal surprise=`N/A`。
- 最新价格、财务、订单、公告、政策与市场状态须实时核验；缺失统一写 `N/A`。

## 当前主结论

1. **当前最明确硬卡点：`200G/lane EML`；上溯到合格 `InP substrate / epiwafer / 器件前道`。**
   - 天孚 2026-07-09 IR：H1 受 200G EML 供应紧张影响，泰国有源线仅小量生产。
   - 天孚 2026-07-18 H1 预告：个别物料紧缺仍影响相关产品提产。
   - 中际 2026-07-12 IR：光芯片、电芯片、PCB 均不同程度紧张，订单与交付仍有缺口。
   - AXT-Coherent 合同：预付款、最低采购和新增产能优先权把 6 英寸 InP 锁产能升级为 A 级商业证据；精确良率、认证、缺口和实际出货仍 `N/A`。
   - 当前存在置信度高；系统性持续时间为 2026H2-2027H1，置信度中高；天孚预计 H2 逐步改善。

2. **模块整机：`soft_bottleneck / easing_but_unresolved`。**
   - 新易盛称 Q1 紧张影响交付、Q2 缓解但 Q3 仍偏紧，部分核心原料突出。
   - 模块装配产能本身不是主要瓶颈；光芯片、电芯片、PCB 和其他核心料齐套决定有效交付。
   - 预计 2026Q3-Q4 边际缓解，置信度中。

3. **未来最重要迁移：`CPO/SiPh 封装测试、主动对准、OWAT/WLBI、known-good optical engine 与综合良率`。**
   - 罗博特科 IR 称 Insertion 2/3 已提供批量设备、Insertion 4 启动、多家客户有采购订单；仍缺 CPO 专项合同金额、交期、验收收入、毛利和良率。
   - 状态从 `watch` 上调 `watch_to_soft`；当前硬缺口 `N/A`，实际卡点更可能在 2027-2028。

4. **平台/标准层没有新增当前硬卡点。**
   - NVIDIA Spectrum-6、IEEE P802.3dj、OIF CPO/ELS 只确认 1.6T、200G/lane、CPO、液冷和高密连接迁移。
   - DSP/TIA/driver、FAU/MMC/MT/PM fiber、热接口、OCS 均缺交期、allocation、良率、有效产能或未满足订单数据，当前写 `N/A/watch`。

## 本期主深挖与次级跟踪

- 主深挖：200G EML -> 合格 InP substrate/epiwafer/6 英寸平台。
- 次级 1：800G/1.6T 模块核心料齐套与交付。
- 次级 2：CPO/SiPh 主动对准、OWAT/WLBI、光电联合测试和设备验收。
- 次级 3：FAU/MMC/MT/PM fiber/ELS 高密连接、现场清洁返工和液冷热接口。

## 上期问题回访状态

| 上期问题 | 本期结果 | 状态 |
|---|---|---|
| InP 供给墙能否获 A 级验证？ | 天孚确认 200G EML 缺料限制提产；中际确认光芯片等紧张造成订单—交付缺口；AXT-Coherent 锁 6 英寸产能。 | 已升级为 A 级卡点闭环；6 英寸精确缺口仍 N/A |
| Coherent/JX/IQE/Tower 扩产兑现？ | Coherent 既有量产口径、AXT 合同、IQE 需求加速、Tower 2027Q4 产能计划增强路径；精确良率/认证/可售产量未披。 | 路径增强，兑现仍待跟踪 |
| Lumentum Mizuho 官方 transcript/PDF 或 SEC 业务披露？ | 仍无；下一硬节点 2026-08-11 财报。 | unchanged |
| AXT 与出口许可进展？ | 本周 AXT 8-K 仅董事任命；未见公开官方许可恢复。云南部分出口订单获许可不等于全面正常化。 | 许可 N/A |
| 光库/安捷讯 FAU/MT/MPO/Lens 经营兑现？ | 6/29 后无新客户、订单、毛利、产能或交期披露。 | unchanged |
| 罗博特科/ficonTEC CPO 订单/交付？ | IR 管理层称批量设备和采购订单；1.23 亿元重大合同实际为车载摄像头整线。 | watch -> watch_to_soft；尚未合同/收入闭环 |
| 中际/新易盛/天孚等是否拆出缺料与交付？ | 已披核心料紧张、缓解动作和 H1 预告；正式半年报与点时共识仍缺。 | 经营证据增强 |
| 光连接/FAU/MT/PM fiber 当前短缺？ | 中际称 FAU 正常；Corning 披露高密连接清洁风险与多源 ferrule。 | 未来 watch；当前短缺 N/A |

## 当前堵点账本

| 节点 | 状态 | 严重程度 | 造成堵点的机制 | 本期变化 | 关键证据 | 预计持续时间 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|---|---|---|
| 200G EML + 合格 InP substrate/epiwafer | 当前主堵点 | hard_bottleneck | 合格衬底/外延、器件良率、老化可靠性、客户认证、许可和二供周期限制可交付供给 | `evidence_upgraded_to_A` | 天孚缺料限制产量；中际光芯片紧且订单—交付有缺口；AXT-Coherent 合同锁 6 英寸产能 | 公司级影响 2026H2 改善；系统性 2026H2-2027H1；置信度高/中高 | EML 交期/allocation 回落、天孚转量产、中际交付缺口关闭、6 英寸良率/认证/出货披露 | 跟天孚、中际、Coherent、Lumentum、AXT/JX/云南 |
| 6 英寸合格 InP 平台 | 主堵点组成 | hard_component / exact_gap_NA | 从名义晶圆产能到可重复良率、客户认证、跨厂一致性和出口许可仍有鸿沟 | lock-in evidence strengthened | AXT-Coherent 预付/最低采购/优先权；Coherent 既有 6 英寸量产及相对良率口径 | 2026H2-2027H1；长期缓解 2028-2030；置信度中高 | 精确良率、合格可售产量、客户验收、许可和库存改善 | 跟 10-Q、IR、发货和合同收入 |
| 模块核心料齐套 | 当前传导堵点 | soft_bottleneck | 光芯片、电芯片、PCB 等须同步，最短板限制有效交付；名义装配产能不是主瓶颈 | eased_but_unresolved | 中际、新易盛 IR | 2026Q3-Q4 边际改善；置信度中 | 交付/毛利/现金流改善、库存预付款转化、不再点名缺料 | 跟正式半年报和 Q3 IR |
| CPO/SiPh 对准、封装测试、OWAT/WLBI | 未来迁移核心 | watch_to_soft | known-good PIC/EIC、纳米对准、测试节拍、设备交付验收和综合良率 | upgraded_watch | 罗博 IR；Aehr/FormFactor/ASMPT 既有量产设备路径 | 当前硬缺口 N/A；2027-2028 潜在；置信度中低 | CPO 专项合同、设备排队/交期、利用率、验收收入、良率瓶颈 | 跟罗博/ficonTEC、Aehr、FormFactor、ASMPT |
| FAU/MMC/MT/MPO/PM fiber/Lens | 未来迁移观察 | watch | 高密连接的精密加工、清洁返工、插拔力、低损耗耦合和客户认证 | direction_up / no_shortage | Corning 高密连接与多源 ferrule；中际 FAU 正常 | 当前 N/A；2027-2028 潜在；置信度低中 | 交期/涨价、返工率、客户定点/量产订单、二供不足 | 跟 Corning/Fujikura/Sumitomo/天孚/光库/太辰光 |
| DSP/TIA/driver/CDR | 战略节点 | watch/rejected_as_current_itemized_bottleneck | 中际只披露“电芯片紧”，未拆到具体芯片；先进制程/IP/设计导入是未来刚性 | broad evidence up, itemized gap N/A | 中际 IR、IEEE/NVIDIA/Broadcom 路线 | N/A；2026H2-2027H2 watch；置信度低中 | 模块厂点名单品、allocation、交期和认证供应商不足 | 跟供应商 allocation/交期、模块厂二供 |
| 模块/CPO 热管理与液冷兼容 | 未来观察 | watch | TIM/cold plate/ELSFP、热可靠性和光温稳接口 | platform direction up / gap N/A | NVIDIA Spectrum-6、OIF CPO IA | 当前 N/A；2027-2028 潜在；置信度低 | 厂商点名认证/返修/交付受限 | 跟平台部署、接口标准和供应商 |
| OCS | 未来观察 | watch | 光学一致性、控制软件、大规模连接和供应商集中 | unchanged | Google Jupiter 既有路线；本周无短缺披露 | 当前 N/A；2027-2028 潜在；置信度低 | 交期、部署延期、未满足订单、认证供应商数 | 跟 Google/Coherent/Lumentum |

## 候选观察池与升级阈值

| 候选节点 | 当前判断 | 升级为卡点所需证据 | 当前不可升级原因 |
|---|---|---|---|
| CW-DFB/UHP pump/ELS | 主卡点尾部和未来迁移 | 单品交期、allocation、锁产金额、客户交付受限或合格供给缺口 | 本周无独立产品级增量 |
| 1.6T 200G/lane DSP/TIA/driver/光引擎 | strategic_watch | 模块厂逐项点名、二供认证不足、交期或配额 | 只有平台/标准和广义“电芯片紧” |
| CPO 测试/主动对准 | watch_to_soft | 专项合同、设备排队、交期、利用率、验收收入、良率 | 管理层主张尚未合同和财务闭环 |
| FAU/MMC/MT/PM fiber/ELS 高密连接 | future_watch | 交期/涨价、返工率、客户量产定点、二供不足 | 中际称 FAU 正常，Corning 已有多源缓解 |
| 热管理/液冷接口 | future_watch | 模块/交换机厂点名热可靠性、返修、认证或交付限制 | 只确认采用方向 |
| 448G/400G-lane/3.2T | design_watch, 2028+ | 标准与客户量产时间显著提前并出现供给约束 | IEEE 时间表和公司口径更偏 2028-2029 |

## 公司映射基线

| 公司 | ticker | 当前角色 | 状态/证据边界 |
|---|---|---|---|
| 中际旭创 | 300308.SZ | 800G/1.6T、硅光、供应链管理 | 基本面质量核心；核心料紧证据明确；XPO/NPO/CPO 累计收入仅 200 万元，远期路线不计核心盈利 |
| Coherent | COHR.US | 6 英寸 InP、EML/CW/PD、CPO | 全球核心；AXT 合同和内部扩产增强；精确良率/认证/出货 N/A |
| 新易盛 | 300502.SZ | 800G/1.6T、硅光、模块交付 | 业绩弹性核心；Q3 仍偏紧；订单硬度、现金流和营运资金待正式半年报 |
| 东山精密/索尔思 | 002384.SZ | 100/200G EML、模块、SiPh | EML 已批量，产能爬坡；部分海外客户仍测试/验厂，良率和订单 N/A |
| 天孚通信 | 300394.SZ | 光器件、光引擎、FAU/ELS/CPO | 200G EML 外部缺料限制提产；FAU 已交付，不据此认定 FAU 短缺 |
| AXT | AXTI.US | 6 英寸 InP substrate | 三年合同与扩产；实际出货、良率、许可和毛利 N/A |
| JX Advanced Metals | 5016.T | InP substrate | 长期 7-10 倍扩产缓解方；当前公开产品页只列 2/3/4 英寸，不写成 6 英寸供给 |
| IQE | IQE.L | InP epiwafer | 本周需求加速；利用率、良率、交期和 InP 收入 N/A |
| Lumentum | LITE.US | EML/CW/UHP pump/ELS/OCS | 主卡点全球候选；官方 Mizuho transcript 缺，等 8/11 财报 |
| Tower | TSEM.US | 300mm SiPh/SiGe/先进光封装 | 2027Q4 缓解路径；不是 InP 激光器产能 |
| 云南锗业 | 002428.SZ | InP substrate | 真实长期合同映射；尺寸、客户、数量、毛利、6 英寸稳定量产 N/A |
| 源杰科技 | 688498.SH | EML/DFB/CW 光芯片 | H1 数据中心利润兑现增强；客户、订单、良率和二供 N/A |
| 长光华芯 | 688048.SH | 100G EML/光芯片平台 | 2025 年 100G EML 已获认证并批量交付但毛利率低；不等同 200G/CW 主卡点 |
| 罗博特科/ficonTEC | 300757.SZ | CPO 对准/测试设备 | 管理层称批量设备/订单；缺专项合同和验收收入；车载合同不属于 CPO |
| 光库科技 | 300620.SZ | FAU/MT/MPO/Lens/TFLN | 产品矩阵和并购期权；客户/订单/产能/交期兑现 N/A |
| 太辰光 | 300570.SZ | MT ferrule/精密连接 | 高交易弹性观察；本窗口无经营增量 |
| Corning | GLW.US | fiber/cable/connectivity/FAU | 长协、扩产和多源高密连接；当前单品短缺 N/A |
| 长飞光纤 | 601869.SH | 数据中心光纤/光缆 | H1 需求与利润增强；FAU/PM fiber/单品合同和短缺 N/A |
| 光迅科技 | 002281.SZ | 光模块/器件、硅光/CPO/NPO | H1 AI 数通驱动；未拆速率、订单、客户和缺料 |
| 鼎通科技 | 688668.SH | 112G/224G 连接器、液冷小批 | 产品阶段明确；不证明连接器或热接口短缺 |

## 三类排名快照

- 基本面质量：`中际旭创 > Coherent > 新易盛 > Corning > 东山精密 > 天孚通信`。
- 业绩弹性：`新易盛 > 东山精密 > 源杰科技 ≈ 长飞光纤 > 天孚通信 ≈ 光迅科技 > 光库科技 > 鼎通科技`。全部缺预告前点时 FY 归母共识，formal surprise=`N/A`。
- 交易弹性（东方财富 2026-07-24 收盘快照，仅交易属性）：`云南锗业 > 光库科技 > 太辰光 > 罗博特科 > 长光华芯`。高估值/亏损和证据缺口显著，不是基本面排序或买卖建议。

## 业绩预期门槛

- 所有 H1 预告公司：`expectation_as_of=N/A`、`consensus_metric=N/A`、`annualized_core_gap_status=insufficient`、`formal_surprise_status=N/A`。
- `Q2 扣非 = H1 扣非预告 - Q1 扣非实际`；`Q2扣非×4` 是季度年化，不是 TTM 或全年预测。
- 推算区间和来源详见 `2026-07-26.md`；正式半年报后更新收入、毛利、现金流、库存、预付款和应收。

## 下周默认跟踪问题

1. 天孚 200G EML 缺料是否在 H2 落实为泰国有源线量产、交付和毛利改善；能否披短缺比例、供应商与二供认证？
2. Lumentum 2026-08-11 财报是否披 EML/CW/UHP pump/ELS 订单、allocation、交期、InP 良率和 6 英寸 ramp？
3. AXT、Coherent、云南锗业/JX 能否披 6 英寸合格率、许可、客户验收、出货、收入和毛利；合同是否转成可售供给？
4. 中际、新易盛、东山、天孚正式半年报能否拆核心料、订单—交付缺口、预付款/存货转化、1.6T 收入和经营现金流？
5. 罗博/ficonTEC、Aehr、FormFactor/ASMPT 是否出现 CPO 专项合同、设备交期/利用率、验收收入、PIC/EIC/组装良率；FAU/MMC/MT/PM fiber 和热接口是否首次出现交付约束？

## 关键来源

- [天孚通信 2026-07-09 IR](https://static.cninfo.com.cn/finalpage/2026-07-09/1225417924.PDF)
- [中际旭创 2026-07-12 IR](https://static.cninfo.com.cn/finalpage/2026-07-12/1225420582.PDF)
- [新易盛 2026-07-19 IR](https://static.cninfo.com.cn/finalpage/2026-07-20/1225434243.PDF)
- [AXT-Coherent 6 英寸 InP 合同 8-K](https://www.sec.gov/Archives/edgar/data/1051627/000143774926022557/axti20260630_8k.htm)
- [IQE 2026-07-21 Trading Update](https://www.iqep.com/media/press-releases/2026/trading-update-1/)
- [NVIDIA Spectrum-6](https://blogs.nvidia.com/blog/nvidia-spectrum-six-arrives-in-gigascale-ai-factories/)
- [IEEE P802.3dj July 2026](https://www.ieee802.org/3/dj/public/26_07/index.html)
- [云南锗业 2026-07-24 磷化铟衬底合同](https://static.cninfo.com.cn/finalpage/2026-07-24/1225438868.PDF)
- [罗博特科 2026-07-20 IR](https://static.cninfo.com.cn/finalpage/2026-07-21/1225434440.PDF)

## 对话窗口摘要源表

| 当前核心卡点 | 原因/约束机制 | 关键证据 | 预计持续时间 | 缓解/反转指标 |
|---|---|---|---|---|
| 200G EML；上溯合格 InP substrate/epiwafer/器件前道 | 合格良率、老化可靠性、客户认证、许可和二供周期限制可交付供给 | 天孚缺料使有源线仅小量；中际称光芯片等紧且订单—交付有缺口；AXT-Coherent 锁 6 英寸产能 | 公司级影响 2026H2 改善；系统性 2026H2-2027H1，置信度中高 | EML 交期/allocation 回落、天孚量产、中际交付缺口关闭、6 英寸良率/认证/出货披露 |
| 模块核心料齐套 | 模块名义产能不是主瓶颈，光芯片、电芯片、PCB 等须同步 | 中际、新易盛确认 Q2 缓解但缺口未关 | 2026Q3-Q4 边际缓解，置信度中 | 交付/毛利/现金流改善、库存预付款转化、不再点名核心料紧张 |

| 未来潜在卡点 | 可能机制 | 当前证据/争议 | 预计时间 | 升级触发阈值 | 反转指标 |
|---|---|---|---|---|---|
| CPO/SiPh 主动对准、OWAT/WLBI、光电联合测试和综合良率 | known-good PIC/EIC、纳米对准与测试节拍 | 罗博称批量设备/订单；无专项合同、排队、验收收入或良率 | 2026H2-2028 | 设备交期/利用率、CPO 合同、客户延期、综合良率 | CPO 延后、设备供给和良率充足 |
| 1.6T 200G/lane DSP/TIA/driver/光引擎认证 | 先进制程/IP、设计导入和认证供应商集中 | 标准/平台需求强；除 EML 外逐项缺口 N/A | 2026H2-2027H2 | 模块厂点名单品、allocation、交期或二供不足 | 多供应商稳定、架构改变 BOM |
| ELS+PM fiber+FAU/MMC/MT 高密连接及热接口 | 功率稳定、耦合、污染返工、液冷兼容和认证 | 高密度与多源缓解路径均有；当前短缺 N/A | 2027-2028 | 交期/涨价、返工率、量产订单、认证/热可靠性限制 | 多源、自动化、标准化、CPO 延后 |
