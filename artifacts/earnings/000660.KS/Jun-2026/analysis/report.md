# SK hynix（000660.KS）2026Q2 财报电话会深挖

> 报告时点：2026-07-29 11:49 北京时间。当前数字为公司初步 K-IFRS 合并结果，外部审阅尚未完成，后续可能调整。

## 一、结论

**当季经营性判断：`低于`。** SK hynix 创下收入和经营利润纪录，但事前 14 家券商同口径共识更高：收入和经营利润分别低于共识 5.685% 和 5.550%，均经确定性审计判定为 `miss`。这解释了业绩发布后的盘中股价走弱：市场首先交易的是经营性 miss，而不是投资资产收益推高的净利润。

**电话会增量偏正面。** 相比 2026Q1，公司把 LTA 从“正在评估、无法满足所有客户要求”推进到约 10 家客户完成谈判；HBM4 从“按客户约定计划爬坡”推进到 Q2 已开始量产出货，管理层称良率和质量接近成熟期 HBM3E。AI 数据中心、server DRAM、HBM 和 eSSD 的需求措辞更强，客户仍要求更多供给。

**不能把 118% 净利率外推。** 当季非经营利润为 62.166 万亿韩元，其中投资资产相关收益为 63.270 万亿韩元。净利润和 EPS 的跃升不是全部来自持续经营改善；不应以当季净利润年化估值。

**投资含义：经营趋势强、执行证据增强，但短期预期差弱。** 中期关键不是“AI 有没有需求”，而是 H2 延后产品、HBM4 爬坡和新产能能否把 latent demand 转为收入，同时避免 CapEx 和应收占用恶化。由于 ADR 发行后的股本与收盘价估值链未完成审计，本报告不发布估值或买卖建议。

## 二、运行与证据状态

| 字段 | 状态 |
|---|---|
| `skill_revision` | `git:bc9242494edc9582877b7fb850ca87cc6162d311` |
| `prompt_contract_version` | `2026-07-27.1` |
| `skill_content_sha256` | `1d8e93b9831ac4353aa9c196bb3cd2f9c82c03462bcc9100ebf927fe88d6b357` |
| `skill_tree_status` | `clean` |
| `skills` | `earnings-call-investment-analyst`; `financial-evidence-audit` |
| `company_original_status` | `found` |
| `call_content_status` | `official_complete` |
| `final_source_type` | `company_original + official_event_platform + exchange_announcement + local_derivative` |
| `provisional` | `false` |
| `confidence level` | 中高：财务数字高；电话会解读中高 |
| `calculation_audit_status` | 核心审计 `PASS`（22/22）；EPS 比较冲突审计 `FAIL` |
| `audit_release_status` | 核心数字 `publishable`；EPS QoQ/预期差 `blocked` |
| `audit_artifact` | `audit/core_evidence_audit_result.json`; `audit/eps_conflict_audit_result.json` |
| `audit_blockers` | `MATERIAL_CONFLICT`：仅影响 Q1 basic EPS 比较及其下游结论 |
| `unresolved_numeric_conflicts` | Q2 演示稿的 Q1 basic EPS 比较列为 KRW 21,852；Q1 演示稿为 KRW 57,175 |

`missing_materials`：官方书面逐字稿/完整字幕；完成外部审阅的半年度报告及附注；订单总额、backlog、LTA 收入覆盖、客户名单和个别价格；Q3 收入/经营利润/EPS 数值指引；当季分业务利润率与具体外部上游供应商瓶颈。

## 三、公司基本面基线

SK hynix 的盈利核心是 DRAM 与 NAND 的规模制造、先进制程迁移和高附加值产品组合；Solidigm 并表增强 enterprise SSD 能力。AI 暴露不是单一 HBM：HBM 提供 accelerator bandwidth，server DRAM/SOCAMM2 支撑 agentic AI 的内存容量，eSSD/QLC/TLC 承接训练、推理、KV-cache offloading 和 near-GPU storage。季度解释桥为：bit shipment × ASP × 产品 mix − 制造成本/折旧/研发，再叠加汇兑、投资资产损益和税项。由此，经营利润更适合观察主营景气，净利润必须剔除一次性非经营项目后再讨论持续性；本报告不自行计算未披露的调整后净利润。

完整基线见 `analysis/company_fundamental_baseline.md`。

## 四、财务结果与预期差

| 指标 | 2026Q2 | 2026Q1 | 经审计 QoQ | 事前共识 | 经审计预期差 | 判断 |
|---|---:|---:|---:|---:|---:|---|
| 收入 | KRW 79.3187T | KRW 52.5763T | +50.864% | KRW 84.1T | -5.685% | `低于` |
| 经营利润 | KRW 60.5426T | KRW 37.6103T | +60.973% | KRW 64.1T | -5.550% | `低于` |
| 经营利润率 | 76% | 72%（公司四舍五入） | N/A | N/A | N/A | `证据不足` |
| 净利润 | KRW 93.9226T | KRW 40.3459T | +132.793% | 未取得合格事前快照 | N/A | `证据不足` |
| basic EPS | KRW 132,126 | 冲突 | `blocked` | N/A | `blocked` | `证据不足` |

共识来源为 Yonhap Infomax 2026-07-26 09:55 KST 的 14 家本地券商事前快照；审计容忍带为 1%。收入与经营利润均整体落在容忍带下方。

### 现金流与资产负债表

| 指标 | 2026Q2 | 经审计变化/说明 |
|---|---:|---|
| 经营现金流 | KRW 65.710T | QoQ +148.619% |
| PP&E 取得支出 | KRW 10.671T | QoQ +39.363% |
| 现金及短期投资 | KRW 87.958T | 公司演示稿原始时点值 |
| 有息债务 | KRW 18.587T | 公司演示稿原始时点值 |
| 存货 | KRW 17.986T | 时点余额；不伪装成 duration 变化率 |
| 应收账款 | KRW 47.821T | 时点余额；随收入扩张显著增加，需等附注判断质量 |

现金生成能力强，但营运资金等项目当季流出 KRW 32.243T，应收和存货均上升。当前初步材料未提供回款账龄、存货减值、客户集中度、关联方、或有事项和政策变更附注，因此这些项目分别为 `not_disclosed` 或 `evidence_absent`，不能补造“无风险”结论。

### 净利润质量

当季非经营利润 KRW 62.166T，投资资产相关收益 KRW 63.270T，是净利润达到 KRW 93.9226T 的主要解释之一。这里不反推“扣除后净利润”，因为税项、其他非经营项目与具体资产处置/估值明细尚不完整。净利润同比或环比虽可计算，但不代表持续经营增速。

## 五、指引与执行计划

| 项目 | 公司表述 | 预期比较 | 证据结论 |
|---|---|---|---|
| Q3 DRAM bit shipment | 约 +10% QoQ | 未取得同口径事前共识 | 数值经演示稿与官方回放交叉审计；guidance surprise 为 `证据不足` |
| Q3 NAND bit shipment | low-single% QoQ | 未取得同口径事前共识 | 保留原文区间，不换算点值 |
| 2026 年 DRAM/NAND 市场需求 | 分别 mid-20% / high-teen% YoY | 非公司收入指引 | 属于管理层市场需求判断 |
| 2026 年 CapEx | high KRW 40T range | 无合格共识 | 模糊区间，不换算点值；重点投向 M15X、Yongin、先进制程与封装 |
| HBM4 | Q2 开始量产出货，H2 全面爬坡 | 无客户级数量 | 执行证据增强 |
| HBM4E | H1 已向主要客户送样，目标 2027 量产 | 无客户级认证状态 | 比上一季 H2 送样计划表面上提前，但样品版本/客户口径未完全披露 |

公司没有给出 Q3 收入、经营利润、利润率或 EPS 数值指引，因此 forward guidance 判断必须是 `证据不足`，不能用 bit shipment 或行业价格预测替代。

## 六、下游需求展望

| 下游需求项 | Mention Status | 证据位置 | 管理层表述 | 时间范围 | 需求质量 | 投资含义 | 置信度 |
|---|---|---|---|---|---|---|---|
| AI 数据中心 / hyperscaler | `demand_accelerating` | Q2 演示稿 p9；回放 00:04:24-00:06:22、00:14:16-00:19:56 | 大型科技客户扩大基础设施与 memory procurement，主要客户继续要求更多供给；电力和数据中心建设会改变项目节奏 | H2 2026 及明年以后 | durable ramp，带物理约束 | AI 需求强，但 latent demand 不等于当期收入 | 高 |
| HBM / 2027 客户采购 | `demand_accelerating` | 演示稿 p11；回放 00:36:54-00:47:23 | HBM4 已量产，2027 HBM 量价谈判顺利、需求坚实 | H2 2026-2027 | qualified ramp | 支撑 HBM 领导力；客户级量价未披露 | 中高 |
| server DRAM / SOCAMM2 | `demand_accelerating` | 演示稿 p9/p11；回放 00:04:43-00:05:03 | agentic AI 扩大 server DRAM；1cnm SOCAMM2 已开始正式供应 | 2026 | durable AI infrastructure ramp | AI 暴露不只 HBM | 中高 |
| enterprise SSD / NAND | `demand_accelerating` | 演示稿 p9/p11；回放 00:53:43-00:59:36 | AI inference、KV-cache offloading、data lake 和 near-GPU storage 扩大 eSSD 需求 | 2026 及中长期 | durable ramp + price/mix | NAND 盈利弹性上升，但客户和订单未量化 | 中高 |
| PC / mobile | `demand_uncertain` | 演示稿 p9；回放 00:05:51-00:06:06 | 当前因难以取得 memory 出现暂时销售调整；预计供给缓解与 AI 渗透后恢复 | 近期 | supply-constrained / uncertain | 消费端没有与 AI/server 同等级的订单证据 | 中 |
| LTA / 客户订购意向 | `demand_stable` | 演示稿 p10；回放 00:06:44-00:07:31、00:25:04-00:29:45 | 约 10 家客户完成谈判，含长期量承诺与 deposits 等履约机制 | 通常多年期 | visibility improved | 比上一季更扎实，但不是已披露的 non-cancellable backlog | 中高 |
| 指引覆盖 | `demand_uncertain` | 回放 00:28:06-00:28:42 | 管理层拒绝披露 LTA 覆盖总销售比例；未给财务指引 | Q3 2026 | evidence_absent | 无法量化多少收入已被合同覆盖 | 高 |
| telecom / auto / industrial | `not_mentioned` | 完整回放与材料 | 未形成可用客户需求证据 | N/A | evidence_absent | 不做外推 | 高 |

**置信说明：** AI/server/eSSD 的方向由公司演示稿和完整官方回放共同支持；LTA 的合同机制来自管理层表述，但收入覆盖、取消条款与客户集中度缺失，故不能把需求可见度升级为已锁定收入。PC/mobile 的变化是供给约束与恢复预期，不等于已验证的终端订单加速。

## 七、上游瓶颈证据

| 上游项目 | Mention Status | 证据位置 | 证据说明 | 瓶颈类型 | 时间范围 | 投资含义 | 置信度 |
|---|---|---|---|---|---|---|---|
| Fab 产能与新设施建设周期 | `mentioned_current_bottleneck` | 演示稿 p9/p12；回放 00:06:22-00:06:44 | 先进工艺复杂度与新设施建设周期使供需难以短期改善 | 内部制造能力 / cleanroom lead time | 近期至中期 | 支撑价格，也限制销量兑现 | 高 |
| HBM wafer、先进工艺、TSV / packaging 资源 | `mentioned_current_bottleneck` | 回放 00:44:03-00:45:34 | HBM 使用更多 wafer、先进工艺、TSV 与 packaging capacity，形成资源和机会成本 | 内部产能与先进封装资源 | HBM4/HBM4E 爬坡期 | 是产能/定价约束，不代表某一外部材料短缺 | 中高 |
| HBM4 良率与质量 | `mentioned_mitigated` | 回放 00:36:54-00:38:30 | 管理层称已接近成熟 HBM3E，当前重点转向扩产 | 工艺良率 / 质量 | Q2-H2 2026 | 技术风险下降，规模与客户级认证仍未量化 | 中 |
| M15X / Yongin 投产 | `mentioned_future_risk` | 演示稿 p12；回放 00:48:47-00:52:48 | 需要按需求可见度和投资效率分阶段建设 | 扩产执行 / 投资效率 | H2 2026-2027 | 进度决定 latent demand 能否转收入 | 中高 |
| helium、bromine、tungsten、LNG | `not_mentioned` | 本季完整回放；上一季回放 01:05:56-01:09:21 | 本季未更新；上一季称供应多元化、库存或长期协议使影响有限 | 外部材料 / 能源 | 本季 N/A | 上一季缓解状态不能自动外推为当前确认 | 高 |
| 基板、化学品、外部封装供应商或设备缺件 | `not_mentioned` | 本季完整材料 | 未识别具体外部供应商短缺 | evidence_absent | N/A | 不做供应商或 A 股受益映射 | 高 |

**置信说明：** 本季最明确的“瓶颈”是公司自身先进制程、HBM/封装资源和新产能建设周期，而不是某个被点名的上游材料。电力和数据中心建设出现在客户项目节奏讨论中，属于下游部署约束，不应误写为 SK hynix 上游采购瓶颈。

## 八、关键 Q&A 及直接性

| 问题 | 管理层回答 | 直接性 | 仍缺什么 |
|---|---|---|---|
| 高效模型与数据中心租赁是否意味着 AI CapEx 放缓 | 认为是利用率/商业化提升，不是收缩；AI 竞争仍推动投资 | direct | 客户级 CapEx、power 和项目开工 |
| 扩产会否导致过剩，是否由 LTA 支撑 | 基于客户长期需求和确认需求分阶段扩产 | partial | LTA 收入覆盖、取消条款、客户集中度 |
| LTA 期限、定价和购买承诺 | 多年期、长期量承诺、deposits 等履约机制；定价因客户/产品而异 | partial | 总销售覆盖与 take-or-pay 细节 |
| DRAM ASP 低于预期原因 | 高附加值产品部分延后至 H2、产品 mix 压低 blended ASP；预期 H2 改善 | direct | H2 延后出货的实际兑现 |
| HBM4 差异化 | 性能、良率、质量、规模供应；称良率/质量接近 HBM3E | direct | 客户认证、出货量、盈利率 |
| 2027 HBM 量价 | 谈判顺利、需求坚实，但拒绝披露个别条款 | partial | 数量、价格与客户结构 |

## 九、相对上一季度的变化

1. **需求语气更强。** Q1 是“server demand 抵消 PC/mobile 因价格压力走弱”；Q2 是“主要客户要求更多供给、AI 投资明年以后仍稳健”，同时 PC/mobile 的约束从成本压力转为 memory 难以取得。
2. **LTA 从框架讨论变为已有落地。** Q1 说正在全面评估新结构、受供给限制无法满足全部客户请求；Q2 披露约 10 家客户完成谈判，量承诺与履约机制更具体，但覆盖率仍不披露。
3. **HBM4 从计划转为量产。** Q1 仅称按约定进度爬坡；Q2 已开始量产出货，并提供良率/质量接近 HBM3E 的管理层主张。
4. **HBM4E 进度表面提前。** Q1 内部计划 H2 开始送样；Q2 称 H1 已向主要客户送样。样品版本与客户口径未完全展开，作为执行进展，不计“兑现率”。
5. **CapEx 更具体。** Q1 仅称较去年显著增加；Q2 给出 high KRW 40T range，并明确 M15X、Yongin、P&T7、M17 等分阶段路径。
6. **外部材料风险本季未更新。** Q1 对 helium、bromine、tungsten 和 LNG 给出缓解措施；Q2 没有重复确认，因此本季状态是 `not_mentioned`。

## 十、供应链传导边界

- 可以确认：SK hynix 自身 advanced process、HBM wafer 使用、TSV/packaging capacity、cleanroom 和新 Fab 建设是供给约束；M15X、Yongin、先进封装与关键设备投入方向明确。
- 可以作为产业链线索：EUV、先进封装、测试、cleanroom 和高层 NAND 迁移的资本强度可能上升。
- 不能确认：任何具体上游上市公司是 SK hynix 供应商、获得订单、提高 ASP、增加收入或利润。公司没有在本季材料中点名对应供应商或合同。
- 不能把约 10 家 LTA 直接写成 backlog。公司仅披露量承诺、定价机制与 deposits；没有披露不可取消条款、收入覆盖、客户名单或会计确认节奏。

## 十一、股价反应

留存的 2026-07-29 午间 vendor 快照显示 000660.KS 低于前收盘，方向与收入/经营利润 `miss` 一致。由于该快照是盘中而非收盘，且当日市场还受整体科技股波动影响，本报告不发布盘中变化率，也不把单日反应升级为基本面结论。

## 十二、最重要的跟踪指标

1. H2 延后的高附加值 DRAM 出货是否兑现，blended ASP 是否恢复。
2. HBM4 量产规模、主要客户认证、良率/质量和 HBM 盈利率。
3. 2027 HBM 量价合同是否落定，LTA 收入覆盖、deposits 与取消条款是否披露。
4. Q3 DRAM 约 +10% 与 NAND low-single% bit shipment 是否实现。
5. M15X、Yongin Phase 1、advanced packaging 的工程和设备进度。
6. 应收、存货、营运资金流出与经营现金流的匹配度。
7. 半年度报告对投资资产收益、税项、关联方、或有事项及会计政策的详细解释。
8. 公司是否更正 Q1 basic EPS 比较列冲突。

## 十三、文件与审计链

- 结构化证据包：`evidence_pack.json`
- 公司基本面基线：`analysis/company_fundamental_baseline.md`
- 转写索引：`transcript/transcript_index.md`
- 核心审计输入：`audit/core_evidence_audit_input.json`
- 核心审计结果：`audit/core_evidence_audit_result.json`
- EPS 冲突审计输入：`audit/eps_conflict_audit_input.json`
- EPS 冲突审计结果：`audit/eps_conflict_audit_result.json`
- 运行元数据：`analysis/run_metadata.json`
