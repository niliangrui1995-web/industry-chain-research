# 国内 FAU／PM-FAU／dFAU 企业证据分层报告

研究截止日（`as_of`）：2026-08-29（北京时间）
状态：最终可交付版；仅作产业与证据研究，不构成投资建议。
覆盖口径：本报告复用前期候选池作为检索起点，但只把本轮能够以公司官网、CNINFO、交易所或港交所原始文件复核的主体纳入分层表。未进入表格不等于不存在相关能力，而是截至截止日缺少足以按本报告口径准入的当前一手证据。

## 结论先行

1. **完整 FAU 能力**：天孚通信、光库科技、仕佳光子、长芯博创（EverProX）、HYC、爱德泰、TwinstarTech、杰普特均有直接的 FA／FAU 产品、制造平台或产品组合证据；其中，天孚、光库、仕佳具有更靠近交付/订单/资格的当前披露，HYC 官网则称其大通道高精度 FAU 已规模化生产并稳定交付（`management_claim`）。
2. **明确 PM-FAU / PM-FA 能力**：爱德泰、仕佳光子、光库科技、HYC 有“SM/PM FAU”“保偏型 CPO 用光纤阵列”或 PM 光纤阵列并带偏振性能要求的直接原文。该结论只证明对应产品能力，**不**证明 PM-FAU 已对 CPO 客户批量交付或形成单品收入。
3. **明确严格 dFAU 结构证据**：TwinstarTech 与爱德泰符合本报告的结构门槛；前者明确 `Detachable FAU`、CPO edge coupler、Pin/Pin-hole 被动对准，后者明确“可拆卸 FAU”与可拆卸锁定设计。二者均无产品级商业交付硬证据。
4. **严格 dFAU 的商业交付结论：N/A**。截至本轮检索，未找到任一国内主体同时满足“严格 dFAU 结构 + 该 dFAU 的客户/订单/收入或明确产品级出货”的一手证据。普通 FAU、MPO/MT、`Detachable FA` 或可拆卸连接器都不能替代该闭环。
5. **最容易误判的边界**：MPO 是连接器，MT 是多芯插芯；两者与 FA/FAU 可并列或组合，但并不自动成为 dFAU。V 槽、盖板、透镜、对位/检测设备是 FAU 的上游件或设备，不是完整 FAU。

## 分类规则、阶段和证据标签

| 项目 | 本报告采用的严格口径 |
|---|---|
| 完整 FAU | 需要产品原文直接指向 `FAU` / `Fiber Array Unit`，或能确认企业将精密多纤阵列作为其自身制造/销售产品；不以单纯 MPO、MT、光引擎、CPO 系统或上游 V 槽替代。 |
| PM-FAU | 需要“PM / 保偏”与实际光纤阵列/FAU 在同一产品证据中出现，或出现 PMF 方向控制、PER/消光比等阵列级证据；仅有保偏跳线、保偏尾纤不准入。 |
| 严格 dFAU | 同时需要：① FAU/光纤阵列本体；② 明确可拆卸、可重复连接；③ 面向 PIC、光引擎或 CPO 的导向/锁定/Pin-Pin-hole/微光学接口等结构证据。Lightmatter 的 [vClick](https://lightmatter.co/products/vclick-optics/) 显示的可重复连接、被动对准、连接器接口等是校准参照，不是国内企业的自动背书，也不是行业统一标准。 |
| 商业化阶段 | 仅使用 `rd_plan`、`sampling`、`validation`、`design_win`、`qualification`、`mass_production`、`shipment`、`revenue`、`profit_cashflow`；没有单品阶段披露时写 `N/A`，不从公司整体营收反推。 |
| `official_fact` | 原始法定披露或正式申请文件可直接核对的产品列名、订单、出货、收入或阶段事实。 |
| `management_claim` | 公司官网或投资者关系记录中的产品性能、稳定交付、客户资格等表述；即使载于正式 IR，也不等同于客户侧独立确认。 |
| `inference` | 本报告据上述原文作出的产品归类与边界判断。 |
| `evidence_absent` | 本轮一手材料未披露该产品的命名客户、订单金额、单品收入、利润或可复核的商业交付。它不是“没有业务”的证明。 |

## 一、完整 FAU：已获产品/制造能力直接证据

此表的“完整”指完成型 FAU 器件能力，不代表每一家都已量产或贡献单品收入；同一主体可以同时出现在 PM-FAU、dFAU 或相邻观察表。

| 公司 / 主体 | 产品原文与证据标签 | 来源日期 / URL | 商业化阶段（仅该产品） | 客户、订单、收入证据 | 本报告归类 |
|---|---|---|---|---|---|
| 天孚通信（300394.SZ） | `official_fact`：半年报列示“**FAU 光纤阵列设计与制造技术平台**”。`management_claim`：公司 IR 称“面向 CPO 领域配套的 **FAU、ELS 外置光源**等相关产品处于**稳定交付**状态”。 | [2026H1](https://static.cninfo.com.cn/finalpage/2026-08-19/1225480328.PDF)，2026-08-19；[投资者关系活动记录](https://static.cninfo.com.cn/finalpage/2026-06-28/1225393900.PDF)，2026-06-28。 | `shipment`（公司 IR 的稳定交付表述；`management_claim`）。 | `evidence_absent`：未披露 CPO FAU 的客户名、订单金额、单品收入/毛利率；公司无源器件收入不能拆分给 FAU。 | `inference`：完整 FAU；CPO 配套交付已到公司陈述的 `shipment`，但未到可验证的单品 `revenue`。 |
| 光库科技（300620.SZ） | `official_fact`：光通讯产品含“**光纤阵列单元（涵盖 DR4/DR8 系列/MT-FAU…保偏型 CPO 用光纤阵列…）**”。`management_claim`：高精度多通道 FAU “已经通过大客户合格供应商清单”。 | [2026H1](https://static.cninfo.com.cn/finalpage/2026-08-18/1225477531.PDF)，2026-08-18。 | `qualification`（高精度多通道 FAU 通过 AVL；非出货/收入证明）。 | “大客户”未具名；FAU 订单、交付量、单品收入均为 `evidence_absent`。 | `inference`：完整 FAU，且有 PM-FAU 能力；当前可严谨确认的高精度 FAU 阶段是 `qualification`。 |
| 仕佳光子（688313.SH） | `official_fact`：2026H1 明确“面向 CPO 先进封装场景的**高通道 FAU 产品已达成小批量出货**”；“高精度光纤阵列（FAU）项目”写明“客户端送样验证，**已取得小批量订单**”。 | [2026H1](https://static.cninfo.com.cn/finalpage/2026-08-01/1225451928.PDF)，2026-08-01。 | `shipment`（CPO 高通道 FAU 小批量出货）；另有 `sampling`/小批量订单的项目证据。 | `official_fact`：有“小批量订单”表述；客户名、订单金额、FAU 独立收入/利润均为 `evidence_absent`。 | `inference`：完整 FAU；是表内少数有当前“CPO FAU 小批量出货”直接披露的主体。 |
| 长芯博创（300548.SZ，EverProX） | `official_fact`：2026H1 将光纤阵列定义为“一根或多根光纤按精确间距排列的元件”，并称高精度 FA 向 72 通道以上、2D 面阵升级。`management_claim`：官网称推出 “**full-line Fiber Array Unit (FAU) product portfolio**”。 | [2026H1](https://static.cninfo.com.cn/finalpage/2026-08-22/1225492397.PDF)，2026-08-22；[OFC 2026 产品稿](https://en.everprox.com/view_251.html)，2026-03-19。 | `N/A`：最新定期报告未给 FAU 单品出货/收入阶段。 | FAU 客户、订单、收入均为 `evidence_absent`；数通收入与光纤阵列不可互相归因。 | `inference`：完整 FAU/FA 能力；其 `Detachable FA` 另列相邻观察，不能升为 dFAU。 |
| HYC（广东亿源通） | `management_claim`：官网称“**大通道高精度光纤阵列（FAU）**”采用“**保偏光纤（PMF）+ 常规单模光纤（SMF）**”混合封装，并称“实现规模化生产与稳定交付”。 | [大通道高精度 FAU 产品页](https://cn.hyc-system.com/Product/index_306/8466)，规格书/图纸更新 2026-02-24，本轮复核 2026-08-29。 | `shipment`（官网自述“稳定交付”；`management_claim`，非客户侧确认）。 | 命名客户、订单、收入、出货量均为 `evidence_absent`。 | `inference`：完整 FAU 产品能力；公司官网的阶段陈述不等同于可核验的单品收入。 |
| 深圳市爱德泰科技股份有限公司（ADTEK） | `official_fact`：港交所申请文件及官网列出“**多形态高通道 SM&PM FAU**”“**可拆卸式 FAU**”；官网还写有 FAU 与微透镜阵列集成能力。 | [港交所申请版本](https://www1.hkexnews.hk/app/sehk/2026/108541/a132948/sehk26051500244_c.pdf)，2026-05-15；[官网产品系列](https://adtek.com.cn/%E4%BA%A7%E5%93%81%E7%B3%BB%E5%88%97/)，未标注发布日期，本轮复核 2026-08-29。 | `N/A`：文件展示产品系列，未给 FAU 单品阶段。 | 公司总体客户/收入描述不能替代 FAU；FAU/PM-FAU/dFAU 的命名客户、订单、收入、出货均为 `evidence_absent`。 | `inference`：完整 FAU，且 PM-FAU、严格 dFAU 结构均有直接产品证据。 |
| TwinstarTech（上海） | `management_claim`：产品页为“**Detachable FAU for CPO edge coupler**”，且称其为带透镜阵列的光纤阵列。 | [产品页](https://www.twinstartech.com/products/pdetail/id/32)，未标注发布日期，本轮复核 2026-08-29。 | `N/A`（产品页无可复核阶段信息）。 | 命名客户、订单、收入、出货均为 `evidence_absent`。 | `inference`：完整 FAU；其结构符合严格 dFAU，详见第三表。 |
| 杰普特（688025.SH） | `official_fact`：2026H1 称公司开发“**MPO/MMC 光纤连接器、光纤阵列单元（FAU）及各类光纤组件产品**”；并披露 FAU 产线直通率提升、4/8 通道产品工艺优化及大通道定制研发。 | [2026H1](https://static.cninfo.com.cn/finalpage/2026-08-26/1225506196.PDF)，2026-08-26。 | `N/A`：有产线/工艺证据，但未披露 FAU 单品的出货阶段。 | MPO/MMC 的交付、订单与“光纤器件”合并收入不能转移给 FAU；FAU 单品客户、订单、收入为 `evidence_absent`。 | `inference`：完整 FAU 能力；不准入 PM-FAU 或 dFAU。 |

## 二、明确 PM-FAU / PM-FA：仅确认保偏阵列产品能力

| 公司 / 主体 | 产品原文与来源 | 商业化阶段（仅 PM-FAU / PM-FA） | 客户、订单、收入证据 | 本报告归类 |
|---|---|---|---|---|
| 爱德泰（ADTEK） | `official_fact`：“**多形态高通道 SM&PM FAU**”，支持单模及保偏光纤高密度排列。来源：[港交所申请版本](https://www1.hkexnews.hk/app/sehk/2026/108541/a132948/sehk26051500244_c.pdf)，2026-05-15；[官网](https://adtek.com.cn/%E4%BA%A7%E5%93%81%E7%B3%BB%E5%88%97/)，2026-08-29 复核。 | `N/A`。 | PM-FAU 单品客户、订单、收入、出货均为 `evidence_absent`。 | `inference`：明确 PM-FAU 产品能力。 |
| 仕佳光子（688313.SH） | `official_fact`：“**36、40、48 等 SM、PM 大通道 FAU**”。来源：[2025 年报](https://static.cninfo.com.cn/finalpage/2026-04-18/1225122538.PDF)，2026-04-18；2026H1 另称 CPO 大通道保偏器件小批量出货，但未把该出货明示为 PM-FAU。 | `N/A`：PM-FAU 的专门阶段未披露。 | PM-FAU 命名客户、订单、收入为 `evidence_absent`；不得将一般 CPO FAU 小批量出货外推为 PM-FAU 出货。 | `inference`：明确 PM-FAU 能力，商业化强度未单品披露。 |
| 光库科技（300620.SZ） | `official_fact`：光纤阵列单元产品列含“**保偏型 CPO 用光纤阵列**”。来源：[2026H1](https://static.cninfo.com.cn/finalpage/2026-08-18/1225477531.PDF)，2026-08-18。 | `N/A`：高精度 FAU 的 AVL 不等于 PM 阵列的出货阶段。 | PM 阵列客户、订单、收入为 `evidence_absent`。 | `inference`：明确 PM 光纤阵列/PM-FAU 能力。 |
| HYC（广东亿源通） | `management_claim`：最新大通道 FAU 产品页写“**PMF+SMF 混合封装**”、保偏光纤旋转角度精度与偏振消光比，并称实现规模化生产与稳定交付；其 [PM FA 产品页](https://www.hyc-system.com/Product/index_304/8419)另给出 PMF 的 V 槽阵列与 “Extinction ratio ≥18dB”。来源：[大通道高精度 FAU](https://cn.hyc-system.com/Product/index_306/8466)，2026-02-24 更新，本轮复核 2026-08-29。 | `shipment`（仅公司官网自述）。 | PM-FAU / PM-FA 命名客户、订单、收入、出货量均为 `evidence_absent`。 | `inference`：明确 PM-FAU / PM 阵列能力；不据此声称已获 CPO 客户侧确认。 |

## 三、明确严格 dFAU：结构已见，商业交付未见

| 公司 / 主体 | 达到严格 dFAU 的直接原文 | 来源日期 / URL | 商业化阶段 | 客户、订单、收入证据 | 结论 |
|---|---|---|---|---|---|
| TwinstarTech（上海） | `management_claim`： “**Detachable FAU for CPO edge coupler**”；“high precision Pin and Pin hole… fiber array is **pluggable** and achieve passive alignment”，应用列 CPO/Optical IO。 | [产品页](https://www.twinstartech.com/products/pdetail/id/32)，未标注发布日期，本轮复核 2026-08-29。 | `N/A`。 | dFAU 的命名客户、订单、收入、出货为 `evidence_absent`。 | `inference`：通过结构型 dFAU 门槛（FAU + CPO + 可插拔 + Pin/Pin-hole 被动对准）；**不**通过商业交付门槛。 |
| 爱德泰（ADTEK） | `official_fact`：申请文件列“**可拆卸 FAU**”，并说明“高精度阵列对准及**可拆卸锁定设计**”，满足 CPO 的可维护光连接需求。 | [港交所申请版本](https://www1.hkexnews.hk/app/sehk/2026/108541/a132948/sehk26051500244_c.pdf)，2026-05-15；[官网产品系列](https://adtek.com.cn/%E4%BA%A7%E5%93%81%E7%B3%BB%E5%88%97/)，2026-08-29 复核。 | `N/A`。 | dFAU 的命名客户、订单、收入、出货为 `evidence_absent`。公司总体大规模交付描述不可替代 dFAU 单品证据。 | `inference`：通过结构型 dFAU 门槛（FAU + CPO + 可拆锁定）；**不**通过商业交付门槛。 |
| 国内严格 dFAU 商业交付 | 不适用。 | 截至 2026-08-29 的上述原始材料。 | `N/A`。 | `evidence_absent`：未见“严格 dFAU + 产品级客户/订单/收入或明确单品出货”的国内一手闭环。 | 不把产品页、展会、普通 FAU、MPO/MT 或 `Detachable FA` 写成 dFAU 商业交付。 |

## 四、相邻观察：有相关结构、研发或术语，但不应升格

| 公司 / 主体 | 直接原文与来源 | 当前可确认阶段 | 为什么只作相邻观察 | 客户/订单/收入边界 |
|---|---|---|---|---|
| 长芯博创（300548.SZ，EverProX） | `management_claim`：官网称“**Detachable FA: Supports repeated on-site plugging and unplugging**”。来源：[OFC 2026 产品稿](https://en.everprox.com/view_251.html)，2026-03-19。 | `N/A`。 | 未使用 `dFAU` / `Detachable FAU` 命名，也未给 Pin/锁定/微光接口、重复插拔损耗或循环次数等结构证据；故不能由“Detachable FA”升格为严格 dFAU。 | dFAU 产品级客户、订单、收入、出货均为 `evidence_absent`。 |
| 腾景科技（688195.SH） | `management_claim`：官网历史展会稿称“**展示 CPO 用 FAU 组件**”。[来源](https://www.optowide.com/article-20959-74280.html)，2025-03-24（`historical`）。当前 2026H1 披露的是二维准直器阵列小批量生产/OCS 订单导入，而非 FAU。 | `historical` / `watch_only`（不能作为当前 FAU 阶段）。 | “FA+MT”中的 MT 是多芯插芯，且展会展示没有独立出货、客户认证或结构化 dFAU 证据。 | FAU/PM-FAU/dFAU 的客户、订单、收入为 `evidence_absent`。 |
| 太辰光（300570.SZ） | `official_fact`：2025 年报的研发表列“**FAU 产品开发**”；较早官方 IR 表述光柔性板、FAU 正配合客户开展技术开发和样品试制，保偏 MPO 的小批量出货是另一产品。来源：[2025 年报](https://static.cninfo.com.cn/finalpage/2026-03-31/1225061015.PDF)，2026-03-31；[IR 记录](https://static.cninfo.com.cn/finalpage/2024-11-07/1221649956.PDF)，2024-11-07（`historical`）。 | `sampling`（历史线索；没有当前单品升级证据）。 | PM-MPO、光柔性板的出货不能转移给 FAU，更不能成为 PM-FAU/dFAU。 | FAU 命名客户、订单、收入、出货为 `evidence_absent`。 |

## 五、排除项：不能作为完整 FAU / PM-FAU / dFAU 制造商计入

| 主体或产品类别 | 原文与来源 | 排除理由 | 证据标签 |
|---|---|---|---|
| 炬光科技（688167.SH） | 官网称为光通信客户提供“**构成光纤阵列单元（FAU）的关键光学元器件，如精密设计 V 型槽阵列、盖板等**”。[来源](https://www.focuslight.com/application/optical-communication/fiber-array-units/?action=&goods_id=&lang=cn)，未标注发布日期，本轮复核 2026-08-29。 | V 槽、盖板、微透镜与检测系统是 FAU 的上游材料/元件或装备，原文也界定为“构成”FAU；未见其作为完整 FAU 制造商的证据。 | 构件身份为 `official_fact`/官网 `management_claim`；“非完整 FAU”为 `inference`；FAU 单品客户/订单/收入为 `evidence_absent`。 |
| 太辰光的 MTP/MPO、PM-MPO、光柔性板 | 最新 H1 直接列“**MTP/MPO 高密度光纤连接器、光纤路由柔性板**”等产品。[来源](https://static.cninfo.com.cn/finalpage/2026-08-15/1225475478.PDF)，2026-08-15。 | MPO 是连接器、MT 是插芯、柔性板是布纤组件；它们可与 FAU 共处同一系统，但不是 FAU 本体，更不是 dFAU。太辰的 FAU 仅保留为上一表的研发/样品观察。 | 产品列名为 `official_fact`；将其排除出完整 FAU/dFAU 为 `inference`。 |
| 一般 MPO/MT、光引擎、CPO 系统、FAU 对位/点胶/检测设备 | 本报告采用的物理链路为 `ELS/CW laser → PMF/FAU → PIC/光引擎 → FAU/MT → MPO → 外部光纤`。 | 这些节点与 FAU 可能互补，但不是可替代的同一器件；不得因“CPO/MPO/MT/FAU 关键词共现”而把供应商升格为 dFAU 制造商。 | 分类结论为 `inference`；若无完整 FAU 本体证据则为 `evidence_absent`。 |

## 商业化台账与下一验证点

| 重点主体 | 已确认的最高阶段 | 尚缺的决定性证据 | 下一次可升级条件 |
|---|---|---|---|
| 天孚通信 | `shipment`（CPO FAU 稳定交付，`management_claim`） | CPO FAU 客户名、订单金额、单品收入/毛利率、出货量。 | 正式财报或客户侧材料披露对应 FAU 的订单、收入或认证。 |
| 光库科技 | `qualification`（高精度多通道 FAU 进入 AVL，`management_claim`） | AVL 后的实际出货、产品级订单/收入。 | 后续定期报告/IR 明确 FAU 获订单、量产或收入。 |
| 仕佳光子 | `shipment`（CPO 高通道 FAU 小批量出货，`official_fact`） | 客户名称、订单金额、CPO/PM-FAU 的单独收入及持续性。 | 披露命名客户、批量订单、FAU 产品收入或可靠性/认证节点。 |
| HYC | `shipment`（大通道高精度 FAU 稳定交付，`management_claim`） | 客户名称、订单金额、单品收入、出货量与客户侧验收。 | 监管披露、客户侧材料或可核验的产品级订单/收入证据。 |
| 爱德泰、TwinstarTech | `N/A`（dFAU 结构产品证据） | dFAU 的产品级客户、订单、收入、出货、循环可靠性/交付证据。 | 原始订单、客户侧认证、正式出货/收入或可复核产品规格书。 |
| 长芯博创 | `N/A`（FAU 产品组合；`Detachable FA` 术语） | 严格 dFAU 命名和结构、FAU/dFAU 单品商业化证据。 | 明确 dFAU 产品页/专利/规格与客户或出货披露同时出现。 |

## 资料与核验说明

- 本轮优先采用公司官网、CNINFO、港交所申请文件等一手材料；搜索结果、媒体和概念标签仅用于定位原文，未作为客户、订单或收入结论的依据。
- 对 A 股公司，本轮用 CNINFO `hisAnnouncement/query` 回读了 2026 年截至 8 月 29 日的定期报告目录，并以最新可得 2026H1 为主；旧展会/产品文仅可保留为 `historical` 或 `watch_only`，不负责当前商业化阶段。
- 写入后对文中 19 个去重外部 URL 逐一做了 HTTP 可达性复核，均返回可达状态；网页无发布日期时，表内明确标注“未标注发布日期”和本轮复核日；这不能被误写为产品发布日期。
- 本报告没有使用市值、估值、预测或单品财务拆分，故不对未披露的 FAU 收入做推算。
