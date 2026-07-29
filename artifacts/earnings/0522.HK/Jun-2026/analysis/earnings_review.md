# ASMPT（0522.HK）2026 Q2 财报电话会深挖

信息截止：2026-07-29 11:50:15（北京时间）  
TASK_KEY：`0522.HK|2026-07-29|Jun/2026`

## 结论先行

**判断：证据不足。** 财报本身呈现强劲且广泛的 AI 驱动订单/收入动能，Q2 收入达到上一季度公司指引区间之上，Q3 公司仍给出 `US$630m-690m` 收入指引；但截至截止时点，本次电话会的官方录音、完整 Q&A 和可靠第三方全文记录尚未发布，事件前市场一致预期也没有获得可审计数值。因此：

- 对“公司自身指引兑现”的判断为 `超预期`（公司原始材料明确称 Q2 收入超过其指引）；
- 对“Q2 实际值相对市场一致预期”及“Q3 指引相对市场一致预期”的正式判断均为 `证据不足`；
- 当前只能给出财报材料层面的临时投资判断，不能把准备材料当作完整电话会，也不能评价本季 Q&A 的锋利度或回避程度。

基本面方向偏正面：TCB、Photonics、SMT AI server 和 mainstream power-management 四条 AI 暴露线同时转强，利润率亦改善；最大制约是部分材料交期仍长、HBM4 客户采购时点仍随产品 rollout 变化，以及 Hybrid Bonding 仍在 sampling/潜在 qualification 阶段。

## 运行状态

- `skill_revision`: `git:bc9242494edc9582877b7fb850ca87cc6162d311`
- `prompt_contract_version`: `2026-07-27.1`
- `skill_content_sha256`: `1d8e93b9831ac4353aa9c196bb3cd2f9c82c03462bcc9100ebf927fe88d6b357`
- `skill_tree_status`: `clean`
- `skills`: `earnings-call-investment-analyst`, `financial-evidence-audit`
- `company_original_status`: `found`
- `call_content_status`: `official_partial`
- `final_source_type`: `company_original + third_party_transcript(prior-quarter only) + market_data_vendor`
- `missing_materials`: Q2 官方电话会音频/回放、官方逐字稿、字幕、完整 Q&A、可信第三方当前季度全文记录；事件前数值化市场共识；完整中期报告现金流/资本开支/承诺/关联方附注
- `provisional`: `true`
- `confidence level`: `中等（财务和准备材料高；当前电话会内容低）`
- `calculation_audit_status`: `core PASS 7/7；expectation FAIL 0/2`
- `audit_release_status`: `核心环比与毛利率可发布；市场 surprise 和时点余额派生百分比 blocked/not_released`
- `audit_artifact`: `financial_audit_input.json`, `financial_audit_result.json`, `expectation_audit_input.json`, `expectation_audit_result.json`
- `audit_blockers`: 事件前 Q2/Q3 收入共识数值缺失；当前电话会全文内容缺失；审计合同不支持以 duration change 校验 instant 余额变化率
- `unresolved_numeric_conflicts`: `none`（Yahoo/网页行情碎片与 iFinD 前收盘存在冲突，未进入证据包；财报后股价反应记为 `N/A`）

## 基本面基线与盈利桥

ASMPT 通过 SEMI Solutions 与 SMT Solutions 两大业务销售半导体封装/组装和电子装联设备。AI 暴露不是单一“Hybrid Bonding 概念”，而是：先进逻辑/HBM 的 TCB、光模块与 CPO 的 Photonics/精密贴装、未来 D2W Hybrid Bonding、AI server board 的 SMT、以及 AI 数据中心电源管理带来的 wire/die bonder 需求。盈利桥为：订单与供应交期 → 收入转化 → SEMI/SMT 及 AP 产品组合 → 毛利率与经营杠杆 → 调整后利润；客户 qualification、HBM4 rollout、材料交期和 NEXX/SWAT 等调整项决定财务质量。完整基线见 `fundamental_baseline.md`。

## 核心经审计财务

紧邻上一季度已明确为 `Mar/2026`（Q1 2026）。以下环比和毛利率均来自确定性审计 `PASS`：

| 指标 | Q2 2026 | Q1 2026 | 经审计环比/水平 | 解读 |
|---|---:|---:|---:|---|
| 收入 | HK$4,935.8m | HK$3,966.8m | +24.4% | SEMI 与 SMT 均增长 |
| 订单 | HK$7,080.4m | HK$5,673.4m | +24.8% | book-to-bill 继续高于 1，但公司未披露 backlog 金额/覆盖率 |
| 调整后毛利率 | 42.5% | 39.5% | 42.50% vs 39.48% | 组合和经营杠杆改善 |
| 调整后持续经营净利 | HK$637.528m | HK$335.220m | +90.2% | 经营杠杆明显，但为 Non-HKFRS 口径 |
| 调整后持续经营基本 EPS | HK$1.53 | HK$0.81 | +88.9% | 与调整后利润方向一致 |
| Q3 收入指引 | US$630m-690m | 上季给 Q2 US$540m-600m | 市场比较 `证据不足` | 公司称中点仍有环比增长，但外部 PIT 共识缺值 |

财务质量边界：Q2 持续经营 HKFRS 期内利润为 HK$417.843m，而调整后持续经营净利为 HK$637.528m；调整项目包括股份支付、出售 SWAT 业务亏损、商誉/无形资产减值等。现金流量表和资本开支尚未见于当前结果公告，因此经营现金流、自由现金流及订单转现金质量均为 `N/A`。

资产负债表仅保留官方原始余额，不发布未通过合同审计的派生百分比：存货 `HK$7,249.601m`（2025-12-31：`HK$6,301.732m`）、贸易应收 `HK$4,562.208m`（`HK$3,551.700m`）、客户预付款 `HK$1,953.064m`（`HK$1,092.195m`）。这些余额与强订单并存，但在现金流及 backlog 细节缺失时，不能单独证明收入确定性或回款质量。

## 下游需求展望

| Downstream Demand Item | Mention Status | Evidence Location | Management Wording | Timeframe | Demand Quality | Investment Meaning | Confidence |
|---|---|---|---|---|---|---|---|
| 先进逻辑 C2S/C2W TCB | demand_accelerating | Q2 业绩公告 pp.4-5 | C2S 获 OSAT 重复及 7 月逾 50 台 bulk orders；C2W 获全球 IDM bulk order并交付超细间距设备 | Q2、7月及后续转化 | 多客户/重复订单与交付，质量较高；客户匿名 | TCB 从主题进入订单与交付验证阶段 | 高（公司原始材料） |
| HBM memory TCB | demand_uncertain | Q2 业绩公告 p.5 | 持续获得 HBM 厂商重复订单，但新设备采购时点取决于 HBM4 rollout | H2 2026 及 HBM4 节奏 | 有订单但时点不确定 | 内存 AI 敞口存在，短期收入节奏不能线性外推 | 中高 |
| 800G+ 光模块/Photonics | demand_accelerating | Q2 业绩公告 p.5 | 客户扩充 800G 及更高速光收发器产能；1H 相关收入近三倍 | 2026 余下时间 | 客户产能 ramp；但上一季提示基数较小 | AI 网络链为第二条已兑现增长曲线 | 高 |
| CPO | demand_accelerating | Q2 业绩公告 p.5 | 与多家全球 CPO 玩家深化合作，覆盖 photonics、TCB、HB | 中期 | 合作/参与加深，未披露可核验量产收入 | 有技术卡位，商业兑现仍需订单与 HVM 证据 | 中等 |
| Hybrid Bonding | demand_uncertain | Q2 业绩公告 p.6 | 第二代平台进入关键逻辑和存储客户 sampling，目标是潜在 qualification | 未明确 | sampling/潜在 qualification，不是订单或量产 | 期权价值提高，但当前利润贡献仍不可量化 | 高（阶段表述清晰） |
| AI 数据中心电源管理/SEMI mainstream | demand_accelerating | Q2 业绩公告 p.6 | 领先 IDM 高利用率，AI 数据中心电源管理与工业需求改善；中国 WB/DB 强 | Q2/H2 | 利用率与设备需求共振，兼有周期恢复 | AI 受益扩散到 mainstream，降低单一 AP 依赖 | 中高 |
| SMT AI server 与光模块装联 | demand_accelerating | Q2 业绩公告 pp.8-9 | SMT 录得创纪录订单，AI servers、optical transceivers 和中国 EV 为主要驱动 | Q2/H2 | 实际订单强，来源跨多个应用 | SMT 从上季预期的高基数回落转为超预期强度 | 高 |
| 传统消费/工业应用 | demand_stable | Q2 outlook | 管理层预计部分传统应用复苏延续 | 2026 | 周期恢复，强度不及 AI 结构性需求 | 提供广度但可持续性需订单验证 | 中等 |
| 指引 backlog/合同覆盖率 | not_mentioned | Q2 业绩公告与演示 | 未披露 Q3 指引中已由 backlog、不可取消合同或合格订单覆盖的比例 | Q3 2026 | evidence_absent | 指引可见性无法量化，不能把 book-to-bill 当作全额覆盖 | 高（缺失判断） |

管理层语气较上一季度**更强但不无条件**：更强之处在于 TCB bulk/repeat orders、Photonics 客户 ramp、SMT record bookings 和 mainstream 高利用率同时出现；保留项是 HBM4 采购时点、客户动态产品 rollout 和材料交期。

## 上游瓶颈证据

| Upstream Item | Mention Status | Evidence Location | Evidence Note | Bottleneck Type | Timeframe | Investment Meaning | Confidence |
|---|---|---|---|---|---|---|---|
| 部分材料交期 | mentioned_current_bottleneck | Q2 outlook | 公司在 Q3 指引旁明确写有 `longer lead times for certain materials` | 材料供应/交付周期；未披露具体材料 | Q3 2026 / 2026 | 限制订单向收入转化，尤其不能把高订单等同即时收入 | 高 |
| 上一季 SMT 供应商交期 | mentioned_future_risk | Q1 第三方全文记录，官方音频可核 | 上季管理层称 SMT 收入转化受供应商交期影响，期待 H2 改善；当前材料显示约束仍在 | 供应商交付 | H2 2026 | H2 改善承诺尚未到完整验证期 | 中等（第三方文字，官方音频存在） |
| SEMI 供应紧张 | mentioned_mitigated | Q1 第三方全文记录 | 上季称 SEMI 同样偏紧但当时仍可管理；本季未按业务披露是否进一步缓解 | 供应/交付 | Q1 基线，Q2 未细分 | 不能推断 SEMI 无约束，也不能推断全面恶化 | 中等 |
| 具体短缺材料/单一瓶颈 | not_mentioned | 当前官方材料 | 未披露基板、先进封装材料、运动控制件、光学件或其他具体元件为唯一瓶颈 | evidence_absent | N/A | 不把行业传闻升级为 ASMPT 的公司级瓶颈 | 高 |

## 上一季度承诺复盘

- Q2 收入指引 `US$540m-600m`：已完成，当前公司披露 Q2 收入 `US$630m`，并明确称超过指引。
- “两大分部订单维持高位”：已完成，集团订单上升；SMT 更录得 record bookings。
- “SMT 订单因高基数环比下降”：未兑现，当前 SMT 订单反而环比上升 14.3%；这说明订单强度高于上一季管理层准备材料的方向性判断。
- “供应交期期待 H2 改善”：尚未到期且当前仍存在材料长交期，状态为 `not_yet_due / unresolved`。
- HB/TCB 客户评估：有进展但阶段不同；TCB 已出现更明确订单/交付，HB 仍为 sampling/潜在 qualification。

## 电话会、Q&A 与股价反应边界

本次电话会 08:30 HKT 开始，公司公告称会后最迟六小时提供音频。截至 11:50，官方财务资料页仍未出现 Q2 音频，搜索亦未发现可靠的本季度全文记录。因此：

- 当前电话会内容状态为 `official_partial`，仅有财报、新闻稿及演示材料；
- 当前 Q&A 为 `evidence_absent`，不评价管理层是否回避问题；
- 上一季度 Q&A 仅用于基线，来源标为 `third_party_transcript`；
- iFinD 最新交易日仍为 2026-07-28，故 7 月 29 日财报后价格/成交量反应为 `N/A`，不使用网页碎片推断市场结论。

## 关键跟踪项

1. Q2 官方电话会录音与完整 Q&A：重点核实 TCB 逾 50 台订单交付节奏、HBM4 采购时点、HB qualification 标准及材料交期具体影响。
2. Q3 收入对 `US$630m-690m` 指引的覆盖：需要 backlog、不可取消条款、客户验收和交付期证据。
3. Hybrid Bonding：从 sampling 到 qualification、HVM、repeat order 的离散里程碑，不能用合作数量替代。
4. Photonics：800G+ ramp 的客户集中度、产能周期和收入基数；CPO 合作要与量产收入分开。
5. 完整中期报告：现金流、资本开支、存货/应收变化、客户预付款和 NEXX/SWAT 调整项的现金影响。

建议在 `2026-07-29 16:30`（北京时间）后重新检查官方音频并补做电话会/Q&A 审计；在此之前不把本稿升级为最终电话会判断。
