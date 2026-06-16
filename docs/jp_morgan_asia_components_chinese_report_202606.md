# J.P. Morgan Asia Components 中文整理版研读记录

来源文件：`D:/Downloads/JP_Morgan_Asia_Components_Chinese_Report.pdf`
源头口径：J.P. Morgan Asia Pacific Equity Research, June 2026，中文整理版，共 46 页。
本地记录日期：2026-06-16
证据等级：B。核心 TAM、UTR、盈利预测、评级和估值来自卖方估算；可用于产业链方向、节点优先级和后续验证问题，不可直接作为 A 股公司订单、客户、涨价或量产证明。

## 结论先行

这篇报告的主线不是“又一份 AI 硬件看多”，而是把 AI 基础设施需求从芯片扩散到四类可跟踪组件：被动元件、PCB/CCL、IC 载板、测试设备。对本项目已有记录的最大价值有四点：

1. MLCC 从普通周期复苏上调为 AI server 高端规格的持续跟踪线索。报告给出 AI server MLCC TAM 150%+ CAGR 的卖方估算，并说明高端 MLCC 产能消耗会挤压低阶/中阶供给。A 股上仍需用三环集团、风华高科自己的客户、规格、ASP 和收入拆分验证。
2. CCL/PCB 继续强化 M8/M9、HPC CCL、AI switch 高层板、HDI 良率这条主线。报告提示 HPC CCL TAM 可用 2.5-3 倍近似外推 PCB TAM，并把 M9 升级、产能爬坡和良率下降列为供给可能落后需求的原因。它支持 `soft_bottleneck+`，但不足以单独升为 `hard_bottleneck`。
3. IC 载板是本报告里被显著强化的独立节点。报告估计行业 UTR 在 2027e 超过 100%，AI server & switch 需求面积从 2024 年 2,448 bn mm2 升至 2028e 21,522 bn mm2，占比从 26% 升至 75%。这强化 Unimicron、Ibiden、南电等海外载板链的景气判断，但 A 股兴森科技、深南电路仍只能按订单突破期权或平台能力跟踪。
4. 测试设备是新增值得建账的相邻线索。报告把 GPU FT/SLT 测试时间延长、TDP 提升、CPO/光引擎测试、数据中心电源测试串成 Chroma 的三条 100%+ CAGR 方向。A 股映射不能直接类比 Chroma，应拆成半导体测试机/SLT、光通信测试、电源测试三类分别验证。

## 分板块研读

| 板块 | 报告关键信号 | 对本地记录的处理 |
|---|---|---|
| 被动元件 / MLCC | AI server MLCC TAM 150%+ CAGR；Blackwell 到 Rubin 抬升单计算托盘 MLCC 用量；高端 MLCC 产能消耗挤压低阶供给；YAGEO 低阶 MLCC UTR、价格、钽电容和电阻也受益。 | MLCC 次主线优先级提高。三环集团仍是基本面主受益候选，风华高科是高交易弹性观察。不得把 YAGEO 的价格弹性直接迁移为 A 股 ASP 已兑现。 |
| CCL / PCB | HPC CCL TAM 由 AI server、常规 server、LEO 共同推动；CCL TAM 乘 2.5-3 可近似 PCB TAM；switch 层数提升、HDI 良率下降、M9 爬坡滞后可能让供给落后需求。 | 维持 M7/M8/M9/M10 CCL / prepreg `soft_bottleneck+`。对生益科技、南亚新材、沪电、胜宏、生益电子等只增强需求侧和复杂度侧证据，不替代客户订单验证。 |
| 载板 / ABF / BT | 2027e UTR 超过 100%；AI server & switch 需求面积成为主导；芯片尺寸、层数和总面积从 Hopper 到 Rubin Ultra、Feynman 持续迁移；stepper 与 T-glass 是供给约束；LTA 和容量预留费可能改善商业条款。 | 将 ABF/IC 载板从“相邻观察”强化为独立 `watch_to_soft`，但仍与板级 PCB 严格分开。A 股兴森、深南需要大客户订单、良率、收入和毛利验证后才能上调。 |
| 测试设备 | GPU FT/SLT 测试时间变长，TDP 提高带动 SLT ASP；Chroma 的 SLT、光通信、数据中心电源测试均被报告标注为 100%+ CAGR；电源测试覆盖 DC converter、rack level power、BBU、HVDC。 | 新增 AI 系统级测试设备观察线。A 股测试设备链要拆成半导体测试、光通信测试、电源测试，不把通用仪器或普通分选机直接写成 Chroma 同级受益。 |

## 页码索引

| PDF 页 | 原文页 | 内容 | 本地投研含义 |
|---:|---:|---|---|
| 6 | 4 | MLCC：AI server demand 150%+ CAGR | 支持 MLCC 高端规格需求不是单纯消费电子周期。 |
| 7-10 | 5-8 | YAGEO：低阶 MLCC、UTR、价格、钽电容、电阻 | 证明被动元件受益外溢，但 A 股需另找公司级证明。 |
| 12-14 | 10-12 | HPC CCL/PCB TAM、内容价值、供需缺口 | 强化 M8/M9、switch PCB、HDI 良率和 CCL 供需紧张。 |
| 17-18 | 15-16 | EMC：高端 CCL 与载板 CCL | 提示载板用 CCL、Q glass 是新 TAM；不要与板级 PCB CCL 混同。 |
| 21-26 | 19-24 | 载板 UTR、AI server/switch 需求面积、T-glass、stepper、LTA | 把 ABF/IC 载板提升为独立重点跟踪线索。 |
| 30-37 | 28-35 | IC 测试、SLT、CPO、光通信、数据中心电源测试 | 新增测试设备观察线，重点看测试时间、TDP、光引擎和 HVDC/rack power 测试。 |
| 39-46 | 37-44 | 财务预测、评级、披露和免责声明 | 卖方预测与目标价只作背景，不进入本项目硬证据。 |

## 本地节点映射

| 节点 | 当前判断 | 受影响公司/主体 | 后续验证指标 |
|---|---|---|---|
| AI server 高端 MLCC | `secondary_track_up` | YAGEO、Murata、Samsung Electro；A 股三环集团、风华高科 | 高容、大尺寸、高压、高可靠 MLCC 的客户认证、ASP、收入占比、毛利率；48V power shelf / GPU board / switch board 料号证据。 |
| M8/M9 HPC CCL / prepreg | `soft_bottleneck+` | EMC、台光电、台燿、联茂；A 股生益科技、南亚新材 | M8/M9/M10 分产品 lead time、报价有效期、客户提前锁料、AVL/二供认证、涨价传导到毛利。 |
| 成品 AI PCB / HDI / switch board | `watch_to_soft` | 沪电、胜宏、深南、生益电子、台系 PCB | 高层板良率、测试产能、backlog、交期、客户转单、midplane / switch / ConnectX / BlueField 板收入。 |
| ABF / IC package substrate | `watch_to_soft_separate` | Unimicron、Ibiden、Nan Ya PCB、Samsung Electro；A 股兴森科技、深南电路 | 载板 UTR、advance payment / capacity reservation、stepper 排队、T-glass allocation、FC-BGA 大客户订单、收入和毛利。 |
| AI 系统级测试设备 | `new_watch` | Chroma；A 股长川科技、华峰测控、华兴源创、伟测科技、精智达等按子环节拆分 | GPU FT/SLT 测试时间、TDP 和 SLT ASP；CPO/光引擎测试设备订单；数据中心 HVDC/rack power/BBU 测试设备订单。 |

## 边界和反证

- 这份报告不能证明任何 A 股公司已经拿到 NVIDIA、Google、AWS 或 AMD 的直接订单。
- 载板与板级 PCB 必须分开：ABF/FC-BGA 是封装载板链，AI server/switch PCB 是板级互连链。
- 载板用 Q glass / T-glass 与板级 CCL 的 Low Dk/Low CTE 电子布相关但不等同，后续记录要分清用途。
- 测试设备不能一概写成“半导体测试设备受益”。SLT、光通信测试、CPO optical engine 测试、数据中心电源测试是不同产品线。
- JPM 的评级、目标价、PE/PB 和 EPS 预测不纳入本地硬证据；只保留为卖方估算背景。

## 下次跟踪问题

1. YAGEO、Murata、Samsung Electro、三环集团、风华高科是否披露 AI server 高端 MLCC 的交期、涨价、客户认证、收入和毛利。
2. EMC、台光电、台燿、联茂、生益科技、南亚新材是否披露 M8/M9/M10 CCL 的分产品 lead time、价格、客户锁料和二供认证。
3. Unimicron、Ibiden、Nan Ya PCB、兴森科技、深南电路是否披露 AI server/switch substrate 的 UTR、advance payment、capacity reservation、FC-BGA 量产和毛利。
4. Nittobo、台玻、宏和科技、中材科技是否披露 T-glass / Q glass / Low CTE 电子布的 allocation、交期、价格和客户 AVL。
5. Chroma 与 A 股测试设备公司是否披露 SLT、CPO/光通信、rack power/HVDC 测试设备订单或收入拆分。
