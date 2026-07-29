# KLA（KLAC）FY2026 Q4 财报电话会深挖

核验截止：`2026-07-29T08:43:15+08:00`  
报告期：`Jun/2026`（KLA FY2026 Q4）  
前一季度：`Mar/2026`（KLA FY2026 Q3；按 `Jun/2026 - 3 months` 解析）

## 结论

KLA 的经营读数和管理层语气较上季明显增强：先进逻辑、HBM/DRAM、先进封装与 PCB/基板相关需求共同向上，客户排期总体保持，管理层所述 backlog/RPO 约 12.5B，H2 供应释放支持收入加速。这一正面变化同时揭示了约束：H1 确实受长交期物料短缺影响，关键光学件新增产能仍需 12-24 个月；DRAM 芯片价格与 tariffs 继续压制毛利。故基本面方向为**偏正面、需求强但短期仍受供应上限约束**。

正式预期差标签必须收敛：non-GAAP diluted EPS 对三组可核验盘前快照均为 `beat`，判断为 **超预期**；收入对三个盘前快照分别为 `beat`、`beat`、`meet`，因此收入及本季整体市场预期差为 **证据不足**。FY2027 Q1 指引缺少合格盘前共识，指引预期差同样为 **证据不足**。这不是把负面证据藏入 provisional，而是由确定性审计对受影响结论实行阻断。

## 运行与准出状态

| 字段 | 结果 |
|---|---|
| `skill_revision` | `git:bc9242494edc9582877b7fb850ca87cc6162d311` |
| `prompt_contract_version` | `2026-07-27.1` |
| `skill_content_sha256` | `1d8e93b9831ac4353aa9c196bb3cd2f9c82c03462bcc9100ebf927fe88d6b357` |
| `skill_tree_status` | `clean` |
| `skills` | `earnings-call-investment-analyst`, `financial-evidence-audit` |
| `company_original_status` | `available_complete_official_audio` |
| `call_content_status` | `complete_prepared_remarks_and_q_and_a` |
| `final_source_type` | `company_original + regulatory_filing + official_event_platform + third_party_transcript` |
| `missing_materials` | 官方逐字稿/captions；FY2026 Form 10-K；季度 orders/bookings 数值；FY2027 Q1 合格盘前共识；指引 backlog/合同覆盖率 |
| `provisional` | `false` |
| `confidence level` | `中高`：公司披露和完整电话会为高；市场预期差因共识冲突/缺失降为中低并被阻断 |
| `calculation_audit_status` | `core PASS; expectations FAIL/blocked` |
| `audit_release_status` | `partial_release` |
| `audit_artifact` | `analysis/audit-manifest.json`；核心与预期差审计输入/结果均已保存 |
| `audit_blockers` | 收入盘前共识冲突；FY2027 Q1 盘前共识缺失 |
| `unresolved_numeric_conflicts` | Q4 revenue consensus 3.6016B / 3.61B / 3.67B；adjusted EPS consensus 1.00 / 1.00 / 1.02（方向均为 beat） |

## 公司基本面基线

KLA 销售晶圆、光罩、材料、芯片、先进封装与 PCB 制造所需的检测、量测、良率管理软件及部分沉积/刻蚀设备，并依托装机量获得持续服务收入。客户购买工具的主要价值是更快发现缺陷、缩短工艺开发和量产爬坡、提高良率并降低报废；系统收入受节点复杂度、fab readiness、发货/安装/验收和产品组合驱动，服务收入则随装机基数和续约增长。AI 暴露是经先进逻辑、EUV/2nm、HBM/DRAM、先进封装和 IC substrate 复杂度间接传导，不是直接 hyperscaler 收入。

| 业务 | 产品和客户 | 竞争位置证据边界 | AI 暴露路径 | 季度敏感 KPI |
|---|---|---|---|---|
| Semiconductor Process Control | 检测、量测、数据/软件、化学品控制及服务；foundry/logic、memory、晶圆/光罩/材料客户 | 公司自称领先供应商；优势来自组合、算法、应用工程和流程嵌入；不把公司份额主张升级为外部事实 | 先进逻辑、HBM/DRAM 与先进封装增加 process-control intensity | F/L 与 memory 系统组合、先进节点进度、递延系统收入、毛利率 |
| Specialty Semiconductor Process | MEMS、RF、功率与先进封装沉积/刻蚀 | 专业细分工具；缺少本季可核验份额 | 先进封装扩产间接受益，另受汽车/工业周期影响 | 先进封装项目、产品组合、毛利率 |
| PCB and Component Inspection | PCB、IC substrate、封装器件检测/测试/量测/直接成像 | 基板与封装质量控制参与者；缺少可核验份额 | AI 加速器提高高密度基板、互连和封装质量要求 | 基板/封装投资、PCB 周期、业务重组 |
| Services | 维护、升级、延寿与支持 | 装机基数与全球支持形成粘性 | 高端新增装机扩大后续服务池 | 服务收入、续约、合同负债、服务毛利率 |

解释桥：终端需求只有在转化为客户排期、订单池、发货、安装、验收后才进入收入；系统组合影响毛利，服务形成周期缓冲。backlog 是潜在交付池，但取消/推迟、fab readiness、出口许可和安装验收仍会改变转化，不能单独视为指引完全覆盖。

## 本季财务与指引

所有每股数字均按 2026-06-11 生效的 10-for-1 split 追溯调整。GAAP 与 non-GAAP 分列；下列同比外的派生数全部来自确定性审计。

| 指标 | FY2026 Q4 | FY2026 Q3 | 环比/状态 | 证据层 |
|---|---:|---:|---:|---|
| Revenue | 3,657.6M | 3,415.1M | +7.1% | 官方事实；审计 `PASS` |
| GAAP net income | 1,363.1M | 1,201.0M | +13.5% | 官方事实；审计 `PASS` |
| non-GAAP diluted EPS | 1.05 | 0.94 | +11.7% | 公司 non-GAAP；审计 `PASS` |
| Service revenue | 820.4M | 774.8M | +5.9% | 官方事实；审计 `PASS` |
| non-GAAP gross margin | 62.4% | 62.2% | 小幅改善 | 公司 non-GAAP；本季来源审计 `PASS` |
| Operating cash flow | 906.4M | N/A | N/A | 官方事实；审计 `PASS` |
| Company-defined free cash flow | 817.1M | N/A | N/A | 公司 non-GAAP；审计 `PASS` |
| Capex | 89.3M | N/A | N/A | 官方现金流表；审计 `PASS` |

库存期末为 3.65B、应收为 2.89B，均较 3 月末上升；递延系统收入也上升。事实层面这与增长准备和待验收系统增加相容；投资解释层面则意味着现金转化需继续观察，不能用库存上升单独证明需求强弱。季度 orders/bookings 数值为 `evidence_absent`；管理层只披露订单漏斗和 backlog/RPO 方向。

FY2027 Q1 公司指引为收入 3.8B-4.2B、GAAP gross margin 61.6% ±1、non-GAAP gross margin 62.5% ±1、GAAP diluted EPS 1.04-1.24、non-GAAP diluted EPS 1.06-1.26。公司原 FY2026 Q4 指引兑现为 **符合**：收入处于原区间且高于中点，non-GAAP EPS 位于原区间上端。FY2027 Q1 相对市场共识为 **证据不足**，因为截止时点没有可核验盘前共识。

## 市场预期差审计

| 项目 | 盘前快照 | 审计状态 | 判断 |
|---|---:|---|---|
| Q4 revenue 3.6576B vs MarketBeat 3.6016B | +1.55% | `PASS: beat` | 超预期 |
| Q4 revenue 3.6576B vs Zacks 3.61B | +1.32% | `PASS: beat` | 超预期 |
| Q4 revenue 3.6576B vs ChartMill 3.67B | -0.34%，落在 1% meet band 内 | `PASS: meet` | 符合 |
| Q4 adjusted diluted EPS 1.05 vs 1.00 / 1.00 / 1.02 | +5.0% / +5.0% / +2.94% | 三项均 `PASS: beat` | **超预期** |
| FY2027 Q1 revenue/EPS guidance vs consensus | 合格盘前共识缺失 | 两项 `FAIL: not_meaningful` | **证据不足** |

收入快照给出不同标签，因此不能挑选有利来源形成整体“beat”。本季整体相对市场预期标签为 **证据不足**；但 adjusted EPS 的超预期方向跨三来源稳健。

## 下游需求展望

| 下游需求项目 | Mention Status | 证据位置 | 管理层表述摘要 | 时间范围 | 需求质量 | 投资含义 | 置信度 |
|---|---|---|---|---|---|---|---|
| AI data center / hyperscaler | `demand_accelerating` | Shareholder letter；prepared remarks | 3 月以来需求信号显著增强，hyperscaler 数据中心投入和 AI 算力需求推动晶圆制造复杂度 | H2 2026-2027 | 结构性扩产；但属于管理层判断，不是 KLA 直接客户订单披露 | 支撑先进逻辑、memory 和封装 process-control intensity；不能升级为直接 hyperscaler 收入 | 高（措辞）；中（兑现） |
| Leading-edge foundry/logic | `demand_accelerating` | Prepared remarks；Q&A | 客户排期保持，greenfield 项目更广，多个领先客户讨论 2027 交付 | H2 2026-2027 | 持续 ramp；fab readiness 仍影响转化 | 核心系统需求能见度增强，收入仍受供应和验收节奏限制 | 中高 |
| HBM/DRAM 与 memory | `demand_accelerating` | Shareholder letter；Q1 指引；Q&A | 下一季系统组合中 memory 由本季 21% 升至 27%，其中 DRAM 约占 90%；HBM 复杂度提高检测强度 | Sep/2026 及 2027 | 产能与技术迁移并行；可能带周期波动 | 有利于高强度检测/量测组合；不能从组合指引推导客户名单 | 中高 |
| Advanced packaging | `demand_accelerating` | Shareholder letter；Q&A；官方音频 00:28:00-00:30:35 | CY2026 systems revenue 预计约 1.1B、增长超过 70%；客户要求加速交付、该类工具 lead time 较短 | CY2026-2027 | 由架构复杂度驱动的 ramp，但预测仍为公司主张 | 是最清晰的 AI 间接增量；1.1B 已通过核心审计 | 高（公司披露）；中高（实现） |
| PCB / IC substrate / component | `demand_accelerating` | Shareholder letter；prepared remarks | 高性能计算封装和基板需求改善，相关业务本季走强 | H2 2026 | 周期恢复叠加 AI 封装结构增量 | 提供核心 process-control 外的弹性，但波动性更高 | 中 |
| 客户排期、订单漏斗与 backlog | `demand_accelerating` | Q&A；官方音频 00:42:20-00:46:15 | 排期保持，订单漏斗预计继续增长；backlog/RPO 约 12.5B 且近季持续增加 | H2 2026-2027 | 可见度增强；12.5B 尚待 10-K 验证 | 支撑增长持续性，但 backlog 不是不可取消合同，也不等于指引全覆盖 | 中高 |
| 取消、push-out、channel inventory | `not_mentioned` | Release、prepared remarks、Q&A 全文检索 | 未披露取消率、push-out 或渠道库存 | N/A | `evidence_absent` | 不能据“排期保持”推导零取消或零双订 | 高（缺失判断） |
| 指引的合同/backlog 覆盖率 | `demand_uncertain` | Q&A | 有 backlog 与客户排期支持，但未量化 3.8B-4.2B 中已被合同、backlog、许可或确定发货覆盖的比例 | Sep/2026 | 覆盖质量未披露；无 take-or-pay/定金证据 | 指引可信度来自客户沟通与供应计划，而非可核验覆盖比例 | 高（缺失判断） |

需求质量结论：管理层语气较 FY2026 Q3 **更强**。变化不是只来自价格/组合：WFE 预期、先进封装预测、H2 收入框架、backlog/RPO 和客户交付讨论均提高。但没有披露定金、take-or-pay、取消率或指引覆盖比例，所以“高可见度”仍是管理层主张而非完全锁定收入。

## 上游瓶颈证据

| 上游项目 | Mention Status | 证据位置与说明 | 瓶颈类型 | 时间范围 | 投资含义 | 置信度 |
|---|---|---|---|---|---|---|
| 长交期光学部件 | `mentioned_current_bottleneck` | Q&A；官方音频 00:28:00-00:30:35、00:42:20-00:46:15。H1 长交期物料短缺影响交付，光学新增容量需 12-24 个月 | 关键零件产能/lead time | H2 2026-2029+ | 需求不是近期唯一变量；供应释放决定收入斜率，2027 以后需靠长期容量协议 | 高 |
| H2 整体物料供应 | `mentioned_mitigated` | Prepared remarks 与 Q&A。公司称供应正在上线，支持 H2 较 H1 约增 20%；已与关键供应商签长期容量协议 | 供应爬坡 | H2 2026 | 约束边际缓解但未消失；需以出货和 backlog 转化验证 | 中高 |
| DRAM 芯片可得性与价格 | `mentioned_mitigated` | 上季称所需 DRAM supply 已锁定；本季主要问题转为价格，对毛利的拖累超过 100bp，可能延续至 2027 | 可得性已缓解；成本/毛利仍是当前压力 | 2026-2027 | 不构成当前出货量瓶颈的直接证据，但压制毛利改善 | 中高 |
| Tariffs | `mentioned_future_risk` | Shareholder letter 与 Q&A 毛利桥 | 进口成本/毛利 | FY2027 | 即使产品组合改善，tariffs 仍可能抵消部分毛利上行 | 中 |
| 客户 fab space / readiness | `mentioned_current_bottleneck` | Q&A 谈及客户扩产、greenfield 与工具交付节奏；这是客户部署约束，不是 KLA 上游供应商约束 | 下游安装/验收条件 | 2027 及以后 | backlog 转收入仍取决于 fab 建成和验收，不能只看订单池 | 中 |
| 自有工厂、设施与工程人员 | `mentioned_not_bottleneck` | Q&A 称可按需求扩充内部能力 | 内部产能 | 2026-2027 | 当前更关键的约束在外部长交期零件，不在公司内部设施 | 中 |
| Rare earth 当前运营短缺 | `not_mentioned` | Prepared remarks 与 Q&A 未给出当前运营证据；release 风险因素只作一般性提示 | `evidence_absent` | N/A | 不应从行业新闻推导 KLA 当期 rare-earth 瓶颈 | 高（缺失判断） |

瓶颈结论：本季不是“供应问题已解决”。更准确的说法是：H1 的长交期短缺已被管理层明确承认，H2 随容量上线而缓解；关键光学件仍需较长扩产周期，因而供应是 2026 下半年收入加速的关键验证点。DRAM 当前更偏成本压力，不能与零件可得性混为一谈。

## 与上季电话会的变化

| 主题 | FY2026 Q3 | FY2026 Q4 | 变化判断 |
|---|---|---|---|
| CY2026 WFE | 140B+ | low-150B | 更强；公司主张 |
| CY2026 advanced packaging | 约 1.0B / high-50% growth | 约 1.1B / >70% growth | 上调；1.1B 来源审计 `PASS` |
| FY2026 H2 vs H1 revenue | +15%-20% | 约 +20%，且拐点开始兑现 | 区间向上端收敛 |
| 可见度 | 客户抢交付位、讨论 2027 | 排期保持、backlog/RPO 约 12.5B、讨论至 2027 H2 | 更强但仍非不可取消合同 |
| 供应约束 | DRAM 所需量已锁定，长交期风险存在 | 明确承认 H1 短缺；H2 缓解；光学容量需 12-24 个月 | 信息更具体，风险没有消失 |
| 管理层语气 | 2027 增长快于 2026 | 2027 信心提高、greenfield 更广，较少客户表达担忧 | 更强 |

## 投资判断、风险与跟踪

综合判断：**经营趋势偏正面；formal market surprise 为证据不足。** KLA 正处在多条 AI 间接需求链同时增强的阶段，先进封装是最清晰的增量，foundry/logic 与 DRAM/HBM 提供更大基数。服务收入继续形成缓冲。另一方面，长交期光学部件决定交付天花板，DRAM 价格和 tariffs 压制毛利；共识数据冲突意味着不能把“业务强”直接写成“本季全面超预期”。

最大风险：

1. 客户排期或订单池存在 pull-forward、双订或后续 push-out；公司未披露定金、take-or-pay 和取消率。
2. 光学件及其他长交期组件扩产慢于计划，H2 供应释放和 backlog 转化不达预期。
3. DRAM input cost、tariffs 与不利组合使 gross margin 改善滞后。
4. 中国收入占本季约 26%，export controls 与本地竞争会影响机会池和交付许可；不据此推导具体客户。
5. 应收和库存增加导致营运资本继续占用，即使利润增长也可能压低现金转化。

后续验证指标：FY2026 10-K 对 backlog/RPO 约 12.5B 的正式披露；Sep/2026 收入和指引兑现；光学件 lead time 与 supplier capacity；memory/DRAM 系统组合；non-GAAP gross margin 与 DRAM/tariff bridge；应收、库存、递延系统收入与 OCF；取消/push-out；2027 fab readiness 和先进封装交付。

## 主要来源与证据产物

- KLA [FY2026 Q4 earnings release](https://ir.kla.com/news-events/press-releases/detail/518/kla-corporation-reports-fiscal-2026-fourth-quarter-and-full)、[shareholder letter](https://d1io3yog0oux5.cloudfront.net/_b9ee755a5f60dd0fb3f9e27967aed6af/klatencor/db/1117/10668/letter_to_shareholders/KLA+Earnings+Shareholder+Letter+-+Q4+FY26.pdf)、[官方回放](https://event.on24.com/wcc/r/5395899/6008DA167612920BB3D60F6AAA4113A5)、[SEC Form 8-K](https://www.sec.gov/Archives/edgar/data/319201/000031920126000024/klac-20260728.htm)。
- 完整工作转录：[MarketBeat Q4 transcript](https://www.marketbeat.com/earnings/reports/2026-7-28-kla-co-stock/)；上季对照：[Motley Fool Q3 transcript](https://www.fool.com/earnings/call-transcripts/2026/04/29/kla-klac-q3-2026-earnings-call-transcript/)。关键措辞均用官方音频定点复核。
- 本地证据包：`analysis/evidence_pack.json`；来源清单：`analysis/source_inventory.md`；审计清单：`analysis/audit-manifest.json`；基本面基线：`analysis/fundamental_baseline.md`。
