# 周度跟踪：AI PCB 及上游材料设备 - 滚动状态

更新时间：2026-08-09  
最近报告：[2026-08-09.md](2026-08-09.md)  
前次报告：[2026-08-02.md](2026-08-02.md)  
基线模板：[BASELINE_TEMPLATE.md](BASELINE_TEMPLATE.md)  
结构化输入：[2026-08-09_research_inputs.json](2026-08-09_research_inputs.json)  
证据包：[2026-08-09_bottleneck_evidence.csv](2026-08-09_bottleneck_evidence.csv)

## 本期运行元数据

- captured_at_beijing：2026-08-09T18:17:35+08:00
- prompt_contract_version：2026-07-27.1
- skill_revision：git:d02fac57d10911d2937cadd349fd096b46596ec8
- skill_content_sha256：656fd6486cebe6403278246e6d7424d8f25c1ae6894787f172b244eeec2bb5e0
- skill_tree_status：clean
- skills：ai-chain-research-orchestrator，research-industry-chain
- status：ok
- 固定 as_of：2026-08-09（北京时间）。

## 当前阶段

- 当前仍没有 hard_bottleneck。HVLP3/4/5 或 M8/M9/M10 分等级的 allocation、硬交期、订单延期、锁产/LTA 及同一等级多源闭环均为 N/A。
- 高频高速 PCB 铜箔（含 HVLP）、板级 Low Dk/Df/超薄电子布、M8/M9/M10 CCL/prepreg 材料组合保持 soft_bottleneck / unchanged。三个当前证据包均为 A 级、fresh，并由 normalizer 重新计算为 eligible_for_bottleneck_review；该状态是人工判断资格，非自动确认。
- 电子布新增日东纺 2026-08-05/06 A 级需求证据：NER 低介电玻璃的 AI 服务器需求强劲、销量计划增加；其扩产和本财年暂无调价计划是全面硬短缺的反证，状态不升级。
- 超低损耗树脂、板级成品板良率/测试、湿制程/电镀设备、钻针、测试设备和相关湿化学维持 watch。东威科技 2026-08-08 只证明设备需求和 VCP 订单增长，行业 backlog、交期、利用率、客户延期和认证排队仍为 N/A。
- 高端 PCB 干膜光刻胶为公司 validation、链级 watch：容大部分头部客户样测通过并推进小/批量测试；AI 客户、订单、行业交期与收入均为 N/A。
- ABF/BT 载板和 Low CTE/T-glass 继续 watch_separate。日东纺的 T-glass 信息只适用于封装载板，不能与板级 PCB/CCL 统计混用。

## 本期证据、预检与变化

| 节点 | 检查 ID | 当前严重程度 | 本期变化 | 验证结果 | 关键边界 |
|---|---|---|---|---|---|
| 高频高速 PCB 铜箔（含 HVLP） | ai-pcb-20260809-copper-01 | soft_bottleneck | unchanged | eligible_for_bottleneck_review；证据年龄 18-20 天 | 广义 HVLP 不能写成 HVLP4/5 硬短缺 |
| 板级 Low Dk/Df/超薄电子布 | ai-pcb-20260809-cloth-01 | soft_bottleneck | unchanged | eligible_for_bottleneck_review；证据年龄 3-25 天 | 日东纺补强需求但扩产/暂不调价是反证；T-glass 不属于板级证据 |
| M8/M9/M10 CCL/prepreg 材料组合 | ai-pcb-20260809-ccl-01 | soft_bottleneck | unchanged | eligible_for_bottleneck_review；证据年龄 18-31 天 | 南亚聚合口径混列 ABF；无分等级商业条款 |

- validate_bottleneck_evidence.py --as-of 2026-08-09：reviewable；3 条 eligible、0 条 incomplete、0 条 ineligible。
- normalize_research_inputs.py --as-of 2026-08-09 --strict：0 个 issues；ledger、check、顶层 as_of 和 time_horizon 一致。
- 2026-08-03 至 2026-08-09：除日东纺和东威外，未找到带材料等级、供给/缺口、交期或订单延期的新 A/B 级原始披露。定向官方扫描的零公告是证据缺口，不解释为供需放松。

## 当前堵点账本

| 节点 | claim_as_of | 严重程度 | 时间维度 | 约束机制 | 预计缓解 | 关键反转 |
|---|---|---|---|---|---|---|
| 高频高速 PCB 铜箔（含 HVLP） | 2026-08-09 | soft_bottleneck | 2026H2 | 低粗糙度一致性、树脂匹配、良率和客户认证 | 2027 年起看扩产、良率和二供认证 | 加工费/交期回落，多源入同一 AVL |
| 板级 Low Dk/Df/超薄电子布 | 2026-08-09 | soft_bottleneck | 2026H2 | 配方、拉丝/织布、表面处理、良率和 AVL | FY2027 新处理厂、第二代转代和同平台认证 | 分布种价格/交期回落，多源合格供给 |
| M8/M9/M10 CCL/prepreg 材料组合 | 2026-08-09 | soft_bottleneck | 2026H2 | 布、铜箔、树脂共同通过配方、压合和终端认证 | 2027H1 起看上游与 CCL 合格扩产 | 报价/交期常态化，停止锁料，二供入 AVL |

## 未来 6-24 个月候选池

| 节点 | 当前处理 | 可能时间 | 置信度 | 升级触发阈值 | 反转指标 |
|---|---|---|---|---|---|
| HVLP5/下一代超低粗糙度铜箔 | watch | 2027H2-2028 | low | 分等级交期、配额或加工费上行 | 同平台多源批供与交期回落 |
| Q cloth/石英布与更低损耗板级电子布 | watch | 2027H2-2028 | low | 板级 AI 客户、AVL、产能、交期或 allocation 披露 | 配方替代或多家稳定量产 |
| M10 CCL/prepreg 与树脂组合 | watch | 2027-2028 | low | M10 收入、交期、锁料、二供或牌号级证据 | 多家量产、报价回落、停止锁料 |
| 成品高层高速 PCB 良率/测试 | watch | 2026H2-2027 | low | 两家以上板厂披露良率/测试不足、延期或转单 | 扩产达产、良率与交期恢复 |
| 湿制程/电镀设备、钻针及测试设备 | watch | 2026H2-2027 | low | 两家以上供应商/板厂确认 backlog、交付受阻或认证排队 | 设备交期常态、扩产稳定交付 |
| ABF/BT 载板 T-glass/Low CTE 玻璃 | watch_separate | 2026H2-2027 | low | 载板链路单独出现 allocation、锁产、交期或良率证据 | 替代材料认证、专用产能和良率改善 |

所有未来行均为低置信度 watch，future_max_age_days=365；没有 likely_future_bottleneck 或高置信度结论。

## 公司映射与三类排名状态

- 保留 watch_only：铜冠铜箔 301217.SZ（高频高速铜箔，revenue，2026-07-20）、宏和科技 603256.SH（板级电子布，revenue，2026-07-15）、容大感光 300576.SZ（高端 PCB 干膜，validation，2026-06-26）、东威科技 688700.SH（湿制程/电镀设备，shipment，2026-08-08）。均有 A 级、可定位原始证据，但收入重要性、客户/AVL、AI 专用暴露或行业缺口不足，均不得标为 main_candidate。
- 基本面质量仅按节点级披露完整度：铜冠铜箔 > 宏和科技 > 东威科技 > 容大感光。
- 业绩弹性仅按已披露量价/订单传导：铜冠铜箔 > 宏和科技 > 东威科技 > 容大感光；非一致预期差。
- 交易弹性：N/A。本期未获取可核验行情、估值或市值快照，不复用历史数据，也未触发 financial-evidence-audit。

## 下期默认问题

1. 第二家板厂是否披露同一材料的具体交期、配额、延期或转单？
2. HVLP3/4/5 是否出现分等级销量、良率、客户、加工费、毛利或 LTA？
3. 电子布能否按板级 Low Dk/Df、载板 Low CTE/T-glass、Q cloth 分别披露产能、良率、AVL 和交期？
4. CCL 厂能否披露 M8/M9/M10 报价有效期、lead time、锁料、二供和树脂牌号？
5. 容大、东威及板厂是否出现高端干膜、湿制程/电镀设备、钻针或测试设备的 backlog、认证排队或交付受阻？
