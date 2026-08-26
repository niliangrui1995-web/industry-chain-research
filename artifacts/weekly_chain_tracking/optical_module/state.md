# 周度跟踪：光模块及上游细分环节 - 滚动状态

## 2026-08-23 当前状态

更新时间：2026-08-23 18:36:57 CST
最新周报：artifacts/weekly_chain_tracking/optical_module/2026-08-23.md
本周窗口：2026-08-10 至 2026-08-23
as_of：2026-08-23
下次运行先读：本文件、BASELINE_TEMPLATE.md、2026-08-23.md、2026-08-23.evidence.json、2026-08-23.normalized.json、2026-08-23.bottleneck_evidence_checks.csv 与自动化记忆。

### 运行元数据

    {
      "captured_at_beijing": "2026-08-23T18:36:57+08:00",
      "prompt_contract_version": "2026-07-27.1",
      "skill_content_sha256": "8d0f9c8c73892ddab5208744456451de4f87d514520815a0686ea6f644fe9540",
      "skill_revision": "git:0027e7bf17f1bcd418d20412868df311919decf4",
      "skill_tree_status": "clean",
      "skills": [
        "ai-chain-research-orchestrator",
        "financial-evidence-audit",
        "research-industry-chain"
      ],
      "status": "ok"
    }

### 本期准出与边界

- 2026-08-23.evidence.json、2026-08-23.normalized.json、2026-08-23.bottleneck_evidence_checks.csv 均使用 as_of=2026-08-23。
- normalizer 严格模式 issues=[]；validator 状态为 reviewable，eligible_for_bottleneck_review=3、incomplete=0、ineligible=0。
- 中际旭创 H1 的九项官方财务字段审计为 PASS / publishable；只用于 H1 已披露字段核验，未用于价格、估值、预期差或交易结论。
- eligible_for_bottleneck_review 不是自动确认卡点；本状态的 hard/soft 结论均已由人工按三腿证据和反证复核。

### 当前主结论

1. 1.6T 高速光模块有效交付（核心料齐套与客户认证）仍是 hard_bottleneck，时间维度为 2026H2，变化为 unchanged。
   - 证据检查 ID：optical-20260823-1p6t-delivery-01；claim_as_of=2026-08-23；evidence_review_status=eligible_for_bottleneck_review。
   - 中际旭创 2026-07-28 官方材料同时支持需求、少数厂商可大规模交付、原材料紧缺和供给缺口较大三腿；8 月 22 日 H1 的规模放量是供给响应，未证明行业交期常态化。
   - 缓解/反转：核心料扩产、稳定二供、新供应商完成同客户认证；多家认证供应商稳定批量交付且交期常态化。
2. 高速有源光器件有效产出（公司级，200G/lane EML 为已披露约束样本）维持 soft_bottleneck，时间维度为 2026H2，变化为 unchanged。
   - 证据检查 ID：optical-20260823-active-material-02；claim_as_of=2026-08-23；evidence_review_status=eligible_for_bottleneck_review。
   - 天孚 2026-08-19 说明 H1 个别物料短缺影响有源线利用率和提产，Q3 起导入新供应商、预计逐步缓解；短缺物料名称、比例、交期和行业总缺口仍 evidence_absent。
   - 缓解/反转：有源线稳定量产、核心料交期恢复、经认证二供持续贡献产出。
3. InP 衬底出口许可可得性（AXT/Tongmei 通道）升级为 soft_bottleneck，时间维度为 2026H2，变化为 upgraded。
   - 证据检查 ID：optical-20260823-inp-export-03；claim_as_of=2026-08-23；evidence_review_status=eligible_for_bottleneck_review。
   - AXT 2026-08-13 10-Q 表明许可审批时间不可预测、仍有订单积压；范围仅为该出口许可通道，不能写作全球 InP 物理产能或全行业 EML 短缺。
   - 缓解/反转：积压订单获批、审批周期可预测且不再影响出货和收入确认。
4. Lumentum 的 EML/1.6T 初始出货及 Coherent 的 6 英寸 InP 扩产均强化供给缓解路径，未推翻第 1 项硬卡点。
5. 唯一维持的 likely_future_bottleneck 为 NPO/2.4T 光引擎的系统认证、互操作与先进封装测试，窗口为 2027H2–2028、medium、future_max_age_days=180。CPO/SiPh 测试、ELS/FAU/MT/PM fiber、OCS、DSP/TIA/driver、热接口和数据中心光连接均为 low 或 medium 的 watch，未新增升级。

### 公司映射、排名与遗留问题

- main_candidate：中际旭创（300308.SZ，revenue/current）和新易盛（300502.SZ，revenue/current）。中际的 H1 经九项官方字段审计通过，但两者均不得拆写未披露的 1.6T 单独收入、客户或订单金额。
- watch_only：天孚通信（shipment/current）、光库科技（qualification/current）、光迅科技（mass_production/current）、罗博特科（design_win/current）、云南锗业（mass_production/current）。资格、送样、合同、能力或计划交付均不得升级为 shipment/revenue。
- 基本面质量：中际旭创 > 新易盛 > 天孚通信 > 光迅科技 > 光库科技 > 罗博特科 > 云南锗业。
- 业绩弹性：中际旭创 ≈ 新易盛 > 天孚通信 > 光迅科技 > 光库科技 ≈ 罗博特科 ≈ 云南锗业。
- 交易弹性：N/A；本期未运行价格、估值或量能审计。
- 下期优先补齐：1.6T 交期和认证供应商数；有源器件短缺物料、交期和二供；AXT 许可积压的获批与出货；CPO/NPO 的认证/良率/交期；FAU、耦合设备、InP 的实际 shipment 或收入。

### 结构化产物与关键来源

- 证据包：2026-08-23.evidence.json；规范化：2026-08-23.normalized.json；检查表：2026-08-23.bottleneck_evidence_checks.csv；中际 H1 审计结果：2026-08-23.300308_h1_financial_audit_result.json。
- [中际旭创 2026-07-28 投资者关系活动记录表](https://static.cninfo.com.cn/finalpage/2026-07-28/1225445792.PDF)
- [中际旭创 2026H1](https://static.cninfo.com.cn/finalpage/2026-08-22/1225491753.PDF)
- [天孚通信 2026H1/投关材料](https://pdf.dfcfw.com/pdf/H2_AN202608191828165334_1.pdf?1787176121000.pdf)
- [Lumentum FY2026 Q4](https://investor.lumentum.com/financial-news-releases/news-details/2026/Lumentum-Announces-Fourth-Quarter-and-Full-Fiscal-Year-2026-Results/default.aspx)
- [Coherent FY2026 Q4 演示材料](https://www.coherent.com/content/dam/coherent/site/en/documents/investors/investor-presentations/2026/august-12/investor-presentation-20260812.pdf)
- [AXT 2026-08-13 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1051627/000143774926027677/axti20260630_10q.htm)

## 2026-08-26 财报增量（SMTC FY2027 Q2；非周报重跑）

- **新增（本季合并收入，`official_fact` / 已审计）**：Semtech FY2027 Q2 合并收入为 $341.9m；相对事件前 Q2 收入一致预期 $328.4m，收入层面为 `beat`，+$13.5m / +4.1108%，`C_Q2_REVENUE_SURPRISE=PASS/publishable`。该结论仅为公司合并收入，不拆写为数据中心、800G 或 1.6T 收入。
- **`management_claim`（数据中心、800G/1.6T 与 backlog）**：第三方自动逐字稿中，管理层称 AI 数据中心相关铜缆、光纤和光子产品组合需求强，数据中心、800G/1.6T 及 Q3 目标继续提高；并称 bookings/backlog 强劲、对 FY2027 余下期间及 FY2028 有定性覆盖。该内容不是官方逐字稿，且未披露 backlog 金额、客户、取消率或 take-or-pay；不得升级为官方订单、客户、产能、认证、出货或独立收入事实。
- **未改变（当前台账与 Q3 相对预期）**：不改变 `as_of=2026-08-23`、既有证据检查 ID 或任何 hard/soft/watch 等级。Q3 FY2027 官方收入指引为 $410m ± $5m；其相对事件前市场预期仍为`证据不足`（`source_gap`，`C_Q3_GUIDANCE_REVENUE_SURPRISE=FAIL/blocked`），不得标为 `beat` / `meet` / `miss`。
- **证据边界与下一验证**：在本审计包的 `as_of=2026-08-26T09:14:41+08:00`，FY2027 Q2 10-Q、Q2 official presentation、可匿名核验的官方电话会 replay/transcript/captions 均未取得；本增量未将其纳入结论，保持 `provisional=true`。对 1.6T/AI 光互连账本，优先等待可核验的官方电话会材料以复核上述 `management_claim`；10-Q 继续用于补足财务可比性、税项、营运资本及分部口径。依据：[SMTC FY2027 Q2 财报复盘](../../earnings/SMTC/Jul_2026/analysis/earnings_review.md)。

## 历史记录（2026-08-12 及此前；已被以上状态替代）

## 2026-08-12 财报增量（LITE FY2026 Q4；非周报重跑）

- **新增（产品与管理层进展）**：Lumentum Q4 官方材料披露创纪录 EML 出货，1.6T 云收发器已开始初始出货，部分使用内部 CW laser。管理层称 OCS ramp 仍在轨道、需求增强；ELS 初始订单、NPO engagements 与 CPO laser 需求仍属早期导入/路线图信号。
- **未改变（当前台账）**：不改变 `2026-08-09` 的 `as_of`、证据检查 ID 或等级：1.6T 高速光模块有效交付仍为 `hard_bottleneck`，200G/lane EML 及合格 InP 输入仍为改善中的公司级 `soft_bottleneck`，OCS/CPO 仍为 `watch`。上述不构成客户订单、收入覆盖、规模收入、客户认证完成或上游瓶颈已解除的证据。
- **仍待验证**：Q4 完整官方 Q&A；Q1 FY2027 指引的合同/订单覆盖、库存、取消与拉货；以及 InP/substrate/wafer/epitaxy/EML/pump 的当前供给、良率与合格产能。OCS 协议的实际收入、可取消性及转化节奏仍为 `evidence_absent`。
- **审计边界**：本增量不写入未经审计的 EML 产品份额、协议金额或收入覆盖率；依据：[LITE FY2026 Q4 财报复盘](../../earnings/LITE/FY2026-Q4/analysis/earnings_review.md)。

更新时间：2026-08-09 18:50 CST
最新周报：`artifacts/weekly_chain_tracking/optical_module/2026-08-09.md`
本周窗口：2026-08-03 至 2026-08-09
`as_of`：2026-08-09
下次运行先读：本文件、`BASELINE_TEMPLATE.md`、`2026-08-09.md`、`2026-08-09.evidence.json` 与自动化记忆。

## 运行元数据

```json
{
  "captured_at_beijing": "2026-08-09T18:50:21+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "8d0f9c8c73892ddab5208744456451de4f87d514520815a0686ea6f644fe9540",
  "skill_revision": "git:d02fac57d10911d2937cadd349fd096b46596ec8",
  "skill_tree_status": "clean",
  "skills": [
    "ai-chain-research-orchestrator",
    "financial-evidence-audit",
    "research-industry-chain"
  ],
  "status": "ok"
}
```

本期结构化产物均固定为同一 `as_of=2026-08-09`：

- `2026-08-09.evidence.json`、`2026-08-09.bottleneck_evidence_checks.csv`、`2026-08-09.normalized.json`。
- `normalize_research_inputs.py --strict`：`issues=[]`。
- `validate_bottleneck_evidence.py`：`reviewable`；2 条 `eligible_for_bottleneck_review`、0 条 incomplete、0 条 ineligible。
- `2026-08-09.market_audit_result.json`：最近交易日2026-08-07的7个行情收盘价 `PASS / publishable`、7/7 checks verified；只用于交易属性。
- 上述结构化状态只说明证据包完整/等级相容，不自动确认卡点。

## 任务边界

- 覆盖光模块/光引擎、800G–3.2T、硅光/CPO/OCS、激光器与材料、DSP/TIA/driver、无源器件、光纤连接、封装测试和模块/光引擎热管理接口。
- 卡点须有需求超过合格供给、有效产能、良率、交付或认证供应商的直接证据；技术路线、扩产、主题和单一传闻均不够。
- 公司映射严格区分能力、认证、订单、收入和利润；无一手可定位证据不得越级。
- 三类排名分基本面质量、业绩弹性和交易弹性；行情只作交易属性，不证明产业受益。

## 当前主结论

1. **当前主硬卡点：`1.6T高速光模块有效交付（核心料齐套＋客户认证）`。**
   - 中际旭创2026-07-28官方投关同时提供需求、少数厂商可大规模交付和现阶段供给缺口较大的A级三腿证据。
   - `hard_bottleneck`、`2026H2`、本期相对上期 `unchanged`；没有新的单品交期或缺口比例，不能把它外推为每一种核心料的同等短缺。

2. **`200G/lane EML + 合格InP输入`：`soft_bottleneck`，公司级、改善中。**
   - 天孚2026-07-09称EML紧张使泰国有源线仅小量生产，同时称供应矛盾逐步缓解；本窗口未见稳定量产、交期或二供实证。
   - 不单独声称行业级硬缺口。

3. **InP衬底锁产能机制增强，但实际合格供给仍`N/A`。**
   - AXT–Lumentum长期协议确认最低年度容量承诺、预付款和额外容量支持；AXT Q2披露InP收入创新高和扩产。
   - 不把协议外推为6-inch良率达标、客户认证、实际出货或行业缺口数量。

4. **未来迁移核心：NPO/2.4T光引擎的硅光/电芯片/封装/认证。**
   - `likely_future_bottleneck`、2027H2–2028、中等置信度；缺客户订单、产能、良率、交期和认证供应商数。
   - CPO/SiPh对准/OWAT/WLBI/测试、ELS/PM fiber/FAU/MT、OCS、DSP/TIA/driver、热接口均维持`watch`；当前硬缺口`N/A`。

## 本期主深挖与次级跟踪

- 主深挖：1.6T有效交付 → 核心料齐套、客户认证与大规模制造。
- 次级1：200G/lane EML → 合格InP输入、良率、可靠性与二供。
- 次级2：InP衬底锁产能 → AXT–Lumentum、AXT–Coherent的容量预约、扩产与实际履约。
- 次级3：高速连接/液冷接口与高密光连接 → 鼎通、Corning、FAU/MT/PM fiber的反证和未来迁移条件。

## 上期问题回访状态

| 上期问题 | 本期结果 | 状态 |
|---|---|---|
| 中际/新易盛是否拆出缺料与交付？ | 本窗口无新增经营/投关公告；正式2026H1拆分尚未取得。 | `unchanged` |
| 天孚200G EML缺料是否改善？ | 无稳定量产、交期或二供新证据；原“逐步缓解”口径未被推翻。 | `unchanged` |
| Lumentum是否披露上游光源数据？ | 财报定于8月11日，晚于as_of，未纳入。 | `unchanged` |
| InP扩产是否兑现实际合格供给？ | 新增AXT–Lumentum锁产能和AXT Q2扩产，仍无良率、认证、实际出货或收入拆分。 | `upgraded` 锁料；实际供给`unchanged` |
| 罗博/ficonTEC是否有验收/收入？ | 仅CPO/LPO/NPO/OCS技术活动；无CPO专项订单、交期、验收或收入。 | `unchanged` |
| 光连接/热接口是否已成约束？ | 鼎通交付爬坡、Corning扩产属于供给响应/反证；单品缺口仍N/A。 | `unchanged` |

## 当前堵点账本

| 节点 | 严重程度 | `claim_as_of` | 证据检查ID | 证据评审状态 | 本期变化 | 预计持续时间 | 反转指标 |
|---|---|---|---|---|---|---|---|
| 1.6T高速光模块有效交付（核心料齐套与客户认证） | `hard_bottleneck` | 2026-08-09 | `optical-20260809-1p6t-delivery-01` | `eligible_for_bottleneck_review` | `unchanged` | 2026H2，中等置信度 | 交期常态化、多家经认证供应商稳定批量交付、锁料下降。 |
| 200G/lane EML及其合格InP输入 | `soft_bottleneck` | 2026-08-09 | `optical-20260809-200g-eml-01` | `eligible_for_bottleneck_review` | `unchanged` | 2026H2，改善中 | 天孚有源线稳定量产、EML交期/配额恢复、二供认证完成。 |
| CPO/SiPh对准、封装测试、OWAT/WLBI | `watch` | 2026-08-09 | 不适用 | `watch_only` | `unchanged` | 2027–2028潜在 | CPO专项设备交期/利用率、合同、验收收入与综合良率。 |
| FAU/MT/PM fiber/ELS高密连接 | `watch` | 2026-08-09 | 不适用 | `watch_only` | `unchanged` | 2027–2028潜在 | 单品交期/涨价、返工率、客户定点、二供不足。 |
| DSP/TIA/driver/CDR、热接口、OCS | `watch` | 2026-08-09 | 不适用 | `watch_only` | `unchanged` | 2027–2028或更晚 | 模块/系统厂点名单品、allocation、交期、认证或部署受限。 |

## 公司映射与三类排名基线

- 基本面质量：`中际旭创 > 新易盛 > 天孚通信 > 罗博特科 > 云南锗业 > 鼎通科技`。
- 业绩弹性：`中际旭创 ≈ 新易盛 > 天孚通信 > 罗博特科 ≈ 云南锗业 > 鼎通科技`；`formal_surprise=N/A`，没有把合同金额、路线图或样品试制作为业绩兑现。
- 交易弹性（腾讯行情2026-08-07收盘，仅交易属性，经7项financial audit核验）：高档为`云南锗业、长光华芯、罗博特科`；中档为`天孚通信、源杰科技`；低档为`新易盛、中际旭创`。
- 关键边界：AXT/Lumentum锁产能不等于InP实际短缺或已扩产出货；罗博合同不等于CPO订单或确认收入；云南合同不等于实际shipment/revenue；鼎通高速连接/液冷交付不等于直接光模块供货或行业短缺。

## 下周默认跟踪问题

1. Lumentum 8月11日财报是否披EML/CW/UHP pump/ELS、InP、allocation、订单、良率和产能爬坡？
2. Coherent 8月12日FY2026 Q4是否披6-inch InP良率、客户认证、发货、收入和CW/ELS实际量产？
3. 中际、新易盛、天孚正式中报是否拆1.6T、核心料、库存、预付款、应收和经营现金流？
4. AXT–Lumentum与云南InP合同是否出现尺寸、认证、实际发货、收入或出口许可进展？
5. 罗博/ficonTEC、鼎通、FAU/MT/PM fiber与热接口是否出现CPO专项订单、设备交期、验收、利用率、返修或合格供应商不足？

## 关键来源

- [中际旭创 2026-07-28 投资者关系活动记录表](https://static.cninfo.com.cn/finalpage/2026-07-28/1225445792.PDF)
- [天孚通信 2026-07-09 投资者关系活动记录表](https://static.cninfo.com.cn/finalpage/2026-07-09/1225417924.PDF)
- [AXT–Lumentum Form 8-K](https://www.sec.gov/Archives/edgar/data/1051627/000143774926024883/axti20260715_8k.htm)
- [AXT 2026Q2 结果](https://www.sec.gov/Archives/edgar/data/1051627/000143774926025061/ex_974537.htm)
- [鼎通科技 2026H1](https://static.cninfo.com.cn/finalpage/2026-08-05/1225457964.PDF)
- [云南锗业 2026-07-24 长期供货合同](https://static.cninfo.com.cn/finalpage/2026-07-24/1225438868.PDF)
