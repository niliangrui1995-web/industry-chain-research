# 周度跟踪：光模块及上游细分环节 - 滚动状态

更新时间：2026-08-02 18:32 CST
最新周报：`artifacts/weekly_chain_tracking/optical_module/2026-08-02.md`
本周窗口：2026-07-27 至 2026-08-02
`as_of`：2026-08-02
下次运行先读：本文件、`BASELINE_TEMPLATE.md`、`2026-08-02.md` 与自动化记忆。

## 运行元数据

```json
{
  "captured_at_beijing": "2026-08-02T18:32:37+08:00",
  "prompt_contract_version": "2026-07-27.1",
  "skill_content_sha256": "656fd6486cebe6403278246e6d7424d8f25c1ae6894787f172b244eeec2bb5e0",
  "skill_revision": "git:28e32cd0f4383dcb99ec0e6af8a8be5f12d55d4e",
  "skill_tree_status": "clean",
  "skills": [
    "ai-chain-research-orchestrator",
    "research-industry-chain"
  ],
  "status": "ok"
}
```

结构化产物已以同一 `as_of=2026-08-02` 运行：

- `normalize_research_inputs.py --strict`：0 个 issues。
- `validate_bottleneck_evidence.py`：`reviewable`；2 条 `eligible_for_bottleneck_review`、0 条 incomplete、0 条 ineligible。
- 以上状态只说明证据包完整/等级相容，不自动确认卡点。

## 任务边界

- 覆盖光模块/光引擎、800G–3.2T、硅光/CPO/OCS、激光器与材料、DSP/TIA/driver、无源器件、光纤连接、封装测试和模块/光引擎热管理接口。
- 卡点须有需求超过合格供给、有效产能、良率、交付或认证供应商的直接证据；技术壁垒、标准路线、概念标签和单一传闻均不够。
- 公司映射严格区分能力、认证、订单、收入和利润；没有一手可定位证据不得越级。
- 三类排名分基本面质量、业绩弹性和交易弹性；行情只作交易属性，不证明产业受益。

## 当前主结论

1. **当前主硬卡点：`1.6T 高速光模块有效交付（核心料齐套＋客户认证）`。**
   - 中际旭创 2026-07-28 官方投关称原材料紧缺、1.6T交付紧张、仅少数厂商可大规模交付，且现阶段供给缺口较大。
   - 客户订单几乎覆盖 2026 全年、部分已至 2027；该需求证据与供给/缺口证据组成 A 级三腿闭环。
   - `hard_bottleneck`、`2026H2`、本期相对上期 `upgraded`。预计 H2 物料阶段性改善，但精确交期、缺口比例和认证释放节点未披。

2. **`200G/lane EML + 合格 InP 输入`：`soft_bottleneck`，由主硬卡点降级为公司级、改善中约束。**
   - 天孚 2026-07-09 披露 H1 因 200G EML 供应紧张，泰国有源线仅小量生产；同时称供应矛盾正在逐步缓解。
   - 不再单独声称行业级硬缺口：缺 A/B 级行业交期、配额、缺口比例和二供认证数据。

3. **6 英寸 InP：锁产能机制确认，精确缺口仍 `N/A`。**
   - AXT–Coherent 合同包含 2026–2028 产能承诺、预付款、最低采购和新增产能优先权。
   - 不把合同外推为良率合格、稳定出货或行业实际短缺数量。

4. **未来迁移核心：NPO/2.4T 光引擎的硅光/电芯片/封装/认证。**
   - `likely_future_bottleneck`、2027H2–2028、中等置信度；当前缺客户订单、产能、良率、交期和认证供应商数。
   - CPO/SiPh对准/OWAT/WLBI/测试、ELS/PM fiber/FAU/MT、热接口、OCS、DSP/TIA/driver均保留 `watch`；当前单品短缺 `N/A`。

## 本期主深挖与次级跟踪

- 主深挖：1.6T 有效交付 → 核心料齐套、客户认证与大规模制造。
- 次级 1：200G/lane EML → 合格 InP 输入、良率、可靠性与二供。
- 次级 2：NPO/2.4T → 硅光、电芯片、封装、主动对准/测试与认证。
- 次级 3：FAU 等元器件自动化设备合同 → 订单、交付、验收收入与是否涉及 CPO。

## 上期问题回访状态

| 上期问题 | 本期结果 | 状态 |
|---|---|---|
| 中际/新易盛是否拆出缺料与交付？ | 中际 7/28 明确 1.6T 交付紧张、供给缺口大；新易盛此前仍称Q3核心料偏紧。 | `upgraded` |
| 天孚200G EML缺料是否改善？ | 原材料仍显示有源线小量生产，但公司称供应矛盾逐步缓解；无新产量/交期。 | `downgraded` 为公司级soft |
| Lumentum是否披露上游光源数据？ | 截至as_of未披，8/11为下一官方验证点。 | `unchanged` |
| InP扩产是否兑现实际合格供给？ | 无新良率、认证、出货或收入证据。 | `unchanged` |
| 罗博/ficonTEC是否有订单/交付？ | 新增FAU等自动化制造设备正式合同；非CPO专项、未确认收入。 | `upgraded` 映射 |

## 当前堵点账本

| 节点 | 严重程度 | `claim_as_of` | 证据检查ID | 证据评审状态 | 本期变化 | 预计持续时间 | 反转指标 |
|---|---|---|---|---|---|---|---|
| 1.6T 高速光模块有效交付（核心料齐套与客户认证） | `hard_bottleneck` | 2026-08-02 | `optical-20260802-1p6t-delivery-01` | `eligible_for_bottleneck_review` | `upgraded` | 2026H2，中等置信度 | 交期常态化、多家经认证供应商稳定批量交付、锁料下降。 |
| 200G/lane EML及其合格InP输入 | `soft_bottleneck` | 2026-08-02 | `optical-20260802-200g-eml-01` | `eligible_for_bottleneck_review` | `downgraded` | 2026H2，改善中 | 天孚有源线稳定量产、EML交期/配额恢复、二供认证完成。 |
| CPO/SiPh对准、封装测试、OWAT/WLBI | `watch` | 2026-08-02 | 不适用 | `watch_only` | `unchanged` | 2027–2028潜在 | CPO专项设备交期/利用率、合同、验收收入与综合良率。 |
| FAU/MT/PM fiber/ELS高密连接 | `watch` | 2026-08-02 | 不适用 | `watch_only` | `unchanged` | 2027–2028潜在 | 单品交期/涨价、返工率、客户定点、二供不足。 |
| DSP/TIA/driver/CDR、热接口、OCS | `watch` | 2026-08-02 | 不适用 | `watch_only` | `unchanged` | 2027–2028或更晚 | 模块/系统厂点名单品、allocation、交期、认证或部署受限。 |

## 公司映射与三类排名基线

- 基本面质量：`中际旭创 > 新易盛 > 天孚通信 > 罗博特科`。
- 业绩弹性：`新易盛 ≈ 中际旭创 > 天孚通信 > 罗博特科`；`formal_surprise=N/A`，未取得可复核点时共识。
- 交易弹性（腾讯行情 2026-07-31 收盘，仅交易属性）：`罗博特科 > 云南锗业 > 长光华芯 > 源杰科技 > 天孚通信`。
- 关键边界：罗博的合同不等于 CPO 订单或已确认收入；天孚 FAU 交付不等于 FAU 短缺；云南/源杰/长光华芯的行情不等于已验证的主卡点受益。

## 下周默认跟踪问题

1. 中际、新易盛中报是否拆出 1.6T 交付、核心料、预付款、库存、应收和经营现金流？
2. 天孚 200G EML 是否使泰国有源线从小量生产转为稳定量产；二供和交期能否披露？
3. Lumentum 8 月 11 日财报是否披 EML/CW/UHP pump/ELS、allocation、InP良率和产能爬坡？
4. AXT/Coherent 是否披露 6 英寸 InP 良率、客户认证、发货、收入或预付款消耗？
5. 罗博/ficonTEC 是否披露新合同的交付、验收、收入、毛利和CPO关联？

## 关键来源

- [中际旭创 2026-07-28 投资者关系活动记录表](https://static.cninfo.com.cn/finalpage/2026-07-28/1225445792.PDF)
- [天孚通信 2026-07-09 投资者关系活动记录表](https://static.cninfo.com.cn/finalpage/2026-07-09/1225417924.PDF)
- [新易盛 2026-07-19 投资者关系活动记录表](https://static.cninfo.com.cn/finalpage/2026-07-20/1225434243.PDF)
- [罗博特科 2026-07-27 日常经营重大合同公告](https://static.cninfo.com.cn/finalpage/2026-07-27/1225443709.PDF)
- [AXT 2026-06-26 Form 8-K](https://www.sec.gov/Archives/edgar/data/1051627/000143774926022557/axti20260630_8k.htm)
- [IEEE P802.3dj](https://www.ieee802.org/3/dj/public/index.html)
