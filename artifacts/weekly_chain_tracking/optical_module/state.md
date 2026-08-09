# 周度跟踪：光模块及上游细分环节 - 滚动状态

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
