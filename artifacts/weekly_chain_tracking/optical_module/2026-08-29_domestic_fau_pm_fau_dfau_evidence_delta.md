# 光模块周度跟踪：国内 FAU / PM-FAU / dFAU 证据增量账本

研究截止日（`as_of`）：2026-08-29（北京时间）
记录类型：非周报重跑；仅同步 FAU / PM-FAU / 严格 dFAU 的窄口径公司映射。
承接状态：[滚动状态](state.md)；唯一结论来源：[国内 FAU／PM-FAU／dFAU 企业证据分层报告](../../../docs/国内FAU_PM-FAU_dFAU企业证据分层报告_20260829.md)。

## 写入边界

- 本增量不重跑或改写 2026-08-23 的 `hard_bottleneck`、`soft_bottleneck`、`evidence_check_id`、三类排名及结构化证据包；FAU 子节点仍为 `watch`，因为本轮没有单品交期、配额、返工率、未满足订单或合格二供不足的供需缺口闭环。
- 这里的 `shipment` 只表示对应公司材料所述的产品阶段；不等于客户侧验收、命名客户、订单金额或单品收入。`qualification` 也不等于 `shipment` 或 `revenue`。
- 严格 dFAU 需同时见到 FAU 本体、可拆卸/可重复连接，以及面向 PIC、光引擎或 CPO 的导向/锁定/Pin-Pin-hole/微光学接口等结构。MPO/MT、普通 FAU、`Detachable FA`、可拆卸连接器不得替代严格 dFAU 的结构或商业化闭环；产品页或泛 CPO 进展不得单独替代商业化闭环，但内容满足三项结构要件的产品页可支持结构证据。

## 运行元数据

```json
{
  "captured_at_beijing": "2026-08-29T21:06:19+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "c73403ffce0c14eef29a7199c9487a512ab7cb950e1d7b45dc9be8c50c6a7a78",
  "skill_revision": "git:46472618dbd882d43c8a243ff0feb11a79086ca9",
  "skill_tree_status": "clean",
  "skills": [
    "research-industry-chain"
  ],
  "status": "ok"
}
```

## 节点结论

| 子节点 | 本期可确认状态 | 证据标签 | 不可升级的内容 |
|---|---|---|---|
| 完整 FAU | 产品/制造能力以及个别公司的资格、订单或出货阶段可分别确认；仍是高密连接 `watch` 的细化，不构成供需卡点。 | `official_fact`、`management_claim`、`inference` | 不由 FAU 产品能力或公司整体收入推导单品收入、客户订单或行业短缺。 |
| PM-FAU / PM-FA | 仅确认爱德泰、仕佳、光库、HYC 的阵列级 PM 产品能力；没有一项被本轮材料明确为 CPO PM-FAU 的出货或收入。 | `official_fact`、`management_claim`、`evidence_absent` | 不把仕佳一般 CPO 高通道 FAU 的小批量出货，或光库高精度 FAU 的 AVL，外推为 PM-FAU 出货。 |
| 严格 dFAU | 爱德泰与 TwinstarTech 仅达到结构证据门槛。国内严格 dFAU 产品级商业交付为 `N/A`。 | 结构：`official_fact`/`management_claim` + `inference`；商业：`evidence_absent` | 不把普通 FAU、MPO/MT、`Detachable FA`、产品页或泛 CPO 进展写成 dFAU 商业交付、客户订单或收入。 |

## 原始来源索引

| 编号 | 主体 / 材料 | 日期 | 一手来源与标签 |
|---|---|---|---|
| S1 | 仕佳光子 2026H1 | 2026-08-01 | [半年度报告](https://static.cninfo.com.cn/finalpage/2026-08-01/1225451928.PDF)，`official_fact`。 |
| S2 | 光库科技 2026H1 | 2026-08-18 | [半年度报告](https://static.cninfo.com.cn/finalpage/2026-08-18/1225477531.PDF)，产品列为 `official_fact`；AVL 表述按 `management_claim`。 |
| S3 | 天孚通信 2026H1 / 投资者关系活动记录 | 2026-08-19 / 2026-06-28 | [半年度报告](https://static.cninfo.com.cn/finalpage/2026-08-19/1225480328.PDF)为 `official_fact`；[投资者关系活动记录](https://static.cninfo.com.cn/finalpage/2026-06-28/1225393900.PDF)中的稳定交付为 `management_claim`。 |
| S4 | HYC 大通道高精度 FAU 产品页 | 页面更新 2026-02-24；2026-08-29 复核 | [产品页](https://cn.hyc-system.com/Product/index_306/8466)，`management_claim`。 |
| S5 | 爱德泰港交所申请文件 | 2026-05-15 | [申请版本](https://www1.hkexnews.hk/app/sehk/2026/108541/a132948/sehk26051500244_c.pdf)，`official_fact`。 |
| S6 | TwinstarTech CPO edge coupler 产品页 | 未标注发布日期；2026-08-29 复核 | [产品页](https://www.twinstartech.com/products/pdetail/id/32)，`management_claim`。 |

## 公司映射

| 主体 | FAU | PM-FAU / PM-FA | 严格 dFAU | 仍缺的决定性证据 |
|---|---|---|---|---|
| 仕佳光子（688313.SH） | `shipment` / `official_fact`：面向 CPO 先进封装的高通道 FAU 已小批量出货；高精度 FAU 项目另有客户端送样验证和小批量订单（S1）。 | `official_fact`：36/40/48 通道 SM、PM 大通道 FAU 证明产品能力；专门阶段为 `N/A`。 | `evidence_absent`。 | 客户名、订单金额、FAU 独立收入/利润；一般 CPO FAU 出货不能外推为 PM-FAU 或 dFAU 出货。 |
| 光库科技（300620.SZ） | `qualification` / `management_claim`：高精度多通道 FAU 已通过大客户合格供应商清单（AVL，S2）。 | `official_fact`：产品列含保偏型 CPO 用光纤阵列；专门阶段为 `N/A`。 | `evidence_absent`。 | AVL 后的实际 FAU 出货、产品级订单/收入；AVL 不等于 `shipment`/`revenue`，也不能外推为 PM-FAU 出货。 |
| 天孚通信（300394.SZ） | `shipment` / `management_claim`：IR 称面向 CPO 配套的 FAU、ELS 外置光源处于稳定交付；半年报仅确认 FAU 设计与制造技术平台（S3）。 | 本轮未见 PM-FAU 专门产品阶段证据，记为 `evidence_absent`。 | `evidence_absent`。 | CPO FAU 的客户名、订单金额、出货量、单品收入/毛利；稳定交付不是客户侧确认或收入。 |
| HYC（广东亿源通） | `shipment` / `management_claim`：官网称大通道高精度 FAU 已规模化生产与稳定交付（S4）。 | `shipment` / `management_claim`：同页的 PMF+SMF 混合封装、偏振要求支持 PM-FAU/PM 阵列能力；无客户侧确认。 | `evidence_absent`。 | 命名客户、订单、收入、出货量及客户侧验收；官网自述不得升级为 CPO 客户确认、收入或 dFAU。 |
| 爱德泰（ADTEK） | `official_fact`：多形态高通道 SM&PM FAU 产品能力（S5）；单品阶段 `N/A`。 | `official_fact`：SM&PM FAU 产品能力；单品阶段 `N/A`。 | 结构：`official_fact` + `inference`，可拆卸 FAU、高精度阵列对准及可拆卸锁定设计满足严格结构门槛；商业阶段 `N/A`。 | dFAU 的产品级客户、订单、收入、明确单品出货及循环可靠性/交付证据均为 `evidence_absent`；公司总体交付或收入不可替代。 |
| TwinstarTech（上海） | `management_claim`：产品页称为带透镜阵列的 FAU（S6）；单品阶段 `N/A`。 | 本轮未见 PM-FAU 直接产品证据，记为 `evidence_absent`。 | 结构：`management_claim` + `inference`，`Detachable FAU for CPO edge coupler`、可插拔及 Pin/Pin-hole 被动对准满足严格结构门槛；商业阶段 `N/A`。 | dFAU 的命名客户、订单、收入、出货均为 `evidence_absent`；产品页和 CPO 应用列名不证明商业交付。 |

## 严格 dFAU 的商业化边界与升级触发

截至 2026-08-29，国内严格 dFAU 商业交付为 `N/A` / `evidence_absent`：未见任何主体同时具备严格 dFAU 结构与该产品的客户、订单、收入或明确单品出货一手闭环。

| 对象 | 后续可验证的升级触发 |
|---|---|
| 仕佳光子 | 命名客户、持续/批量订单、FAU 单品收入，或可定位的可靠性/认证资料；其中一般 CPO FAU 的阶段不得自动归属 PM-FAU 或 dFAU。 |
| 光库科技 | 后续定期报告或 IR 明确对应 FAU 的订单、量产、实际出货或收入；PM 阵列需要单独命名的阶段材料。 |
| 天孚通信 | 正式财报或客户侧材料披露对应 FAU 的订单、收入或认证；仅“稳定交付”仍维持 `management_claim`。 |
| HYC | 监管披露、客户侧材料，或可核验的产品级订单、收入、出货量/验收。 |
| 爱德泰、TwinstarTech | 先以产品级客户认证、原始订单、明确 dFAU 出货或收入证明商业阶段；可复核规格和循环可靠性只能强化结构/可靠性证据，不能单独证明商业交付。 |

## 复核说明

- 标签、日期、阶段及负边界均逐项回对源报告第 11–12、19–26、34–40、47–58、80–85 行；网页未标注发布日期的来源保留本轮复核日，不把复核日写成产品发布日期。
- 本轮不对未披露的 FAU / PM-FAU / dFAU 单品收入、利润、客户或订单金额作推算。
