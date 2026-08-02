# 周度跟踪：AI PCB 及上游材料设备 - 滚动状态

更新时间：2026-08-02
最近报告：[2026-08-02.md](2026-08-02.md)
前次报告：[2026-07-26.md](2026-07-26.md)
基线模板：[BASELINE_TEMPLATE.md](BASELINE_TEMPLATE.md)
结构化输入：[2026-08-02_research_inputs.json](2026-08-02_research_inputs.json)
证据包：[2026-08-02_bottleneck_evidence.csv](2026-08-02_bottleneck_evidence.csv)

## 本期运行元数据

- `captured_at_beijing`：`2026-08-02T18:04:35+08:00`
- `prompt_contract_version`：`2026-07-27.1`
- `skill_revision`：`git:28e32cd0f4383dcb99ec0e6af8a8be5f12d55d4e`
- `skill_content_sha256`：`656fd6486cebe6403278246e6d7424d8f25c1ae6894787f172b244eeec2bb5e0`
- `skill_tree_status`：`clean`
- `skills`：`ai-chain-research-orchestrator`, `research-industry-chain`
- `status`：`ok`
- 固定 `as_of`：2026-08-02（北京时间）。

## 当前阶段

- 本期仍没有 `hard_bottleneck`。截至 2026-08-02，缺 HVLP3/4/5 或 M8/M9/M10 分等级 allocation、硬交期、订单延期、锁产/LTA，及同一具体等级的多源闭环。
- 高频高速 PCB 铜箔（含 HVLP）、高端 Low Dk/Df/超薄电子布、M8/M9/M10 CCL/prepreg 材料组合均为 `soft_bottleneck`，状态 `unchanged`。三条当前证据包均为 A 级、fresh，并由 normalizer 重新计算为 `eligible_for_bottleneck_review`；该状态只是人工判断资格，不是自动确认卡点。
- 超低损耗树脂只有材料组合层面的板厂采购证据。具体牌号、供应商、交期、allocation 和 AVL 均为 `N/A`，单列状态为 `watch`。
- PCB 光刻胶保持公司级 `soft`、链级 `watch`：容大现有产能趋满和扩产时滞有效，但 AI 专用收入、客户、认证和行业交期为 `N/A`。
- 成品 AI PCB 的压合、背钻、电镀、良率、测试与交付维持 `watch`；钻针、设备、湿化学和油墨也维持 `watch`，尚无 backlog/交期/认证排队闭环。
- ABF/BT 载板和 Low CTE/T-glass 继续 `watch_separate`，不与板级 AI PCB/CCL 统计混用。

## 本期证据、预检与变化

| 节点 | `check_id` | 当前严重程度 | 本期变化 | 验证结果 | 关键边界 |
|---|---|---|---|---|---|
| 高频高速 PCB 铜箔（含 HVLP） | `ai-pcb-20260802-copper-01` | `soft_bottleneck` | `unchanged` | `eligible_for_bottleneck_review`，证据年龄 11-13 天 | 广义 HVLP 证据不能写成 HVLP4/5 的硬短缺 |
| 高端 Low Dk/Df/超薄电子布 | `ai-pcb-20260802-cloth-01` | `soft_bottleneck` | `unchanged` | `eligible_for_bottleneck_review`，证据年龄 11-18 天 | 不把板级 Low Dk/Df、载板 T-glass 与 Q cloth 混为一类 |
| M8/M9/M10 CCL/prepreg 材料组合 | `ai-pcb-20260802-ccl-01` | `soft_bottleneck` | `unchanged` | `eligible_for_bottleneck_review`，证据年龄 11-24 天 | 南亚聚合口径混列 ABF；没有 M8/M9/M10 分级条款 |

- `validate_bottleneck_evidence.py --as-of 2026-08-02`：`reviewable`；3 条 eligible、0 条 incomplete、0 条 ineligible。
- `normalize_research_inputs.py --as-of 2026-08-02 --strict`：0 个 issues；ledger、check、顶层 `as_of` 和 `time_horizon` 已一致。
- 2026-07-27 至 2026-08-02 未找到带材料等级、客户、配额、交期或订单延期的新 A/B 级原始披露。TTM 的官方 AI 项目案例只给“关键原材料长交期”的泛化风险，未给材料名称、时长或范围，因此不升级任何节点。

## 当前堵点账本

| 节点 | `claim_as_of` | 严重程度 | 时间维度 | 约束机制 | 预计缓解 | 关键反转 |
|---|---|---|---|---|---|---|
| 高频高速 PCB 铜箔（含 HVLP） | 2026-08-02 | `soft_bottleneck` | 2026H2 | 低粗糙度一致性、树脂匹配、良率和客户认证 | 2027 年起看扩产、良率与同平台认证 | 加工费/交期回落，多源入 AVL |
| 高端 Low Dk/Df/超薄电子布 | 2026-08-02 | `soft_bottleneck` | 2026H2 | 配方、拉丝/织布、表面处理、良率和 AVL | 2027 年前后看分布种扩产良率与认证 | 分布种价格/交期回落，多源合格供给 |
| M8/M9/M10 CCL/prepreg 材料组合 | 2026-08-02 | `soft_bottleneck` | 2026H2 | 布、铜箔、树脂共同通过配方、压合和终端认证 | 2027H1 起看上游与 CCL 合格扩产 | 报价/交期常态化，停止锁料，二供入 AVL |

## 未来 6-24 个月候选池

| 节点 | 当前处理 | 可能时间 | 置信度 | 升级触发阈值 | 反转指标 |
|---|---|---|---|---|---|
| HVLP5/下一代超低粗糙度铜箔 | `watch` | 2027H2-2028 | 低 | 多客户批供之外，板厂/CCL 厂披露交期、配额或加工费上行 | 多源同平台批供与交期回落 |
| Q cloth/石英布、更低损耗板级电子布 | `watch` | 2027H2-2028 | 低 | 板级客户、AVL、交期或 allocation 正式披露 | 配方替代或多家稳定量产 |
| M10 CCL/prepreg 与树脂组合 | `watch` | 2027-2028 | 低 | 分级收入、交期、锁料、二供或牌号级供应证据 | 多家量产、报价回落、停止锁料 |
| 成品高层高速 PCB 良率/测试 | `watch` | 2026H2-2027 | 低 | 两家以上板厂披露良率/测试不足、延期或转单 | 扩产达产、良率与交期恢复 |
| 光刻胶、钻针、钻孔/曝光/测试设备 | `watch` | 2027-2028 | 低 | 两家以上供应商/板厂确认 backlog、交付受阻或认证排队 | 新线合格达产、设备交期回落 |
| ABF/BT 载板级 T-glass/Q glass | `watch_separate` | 2026H2-2028 | 低 | 独立出现 allocation、锁产、预付款、交期或良率证据 | 载板专用产能和良率改善 |

所有未来行在本期均为低置信度 `watch`，`future_max_age_days=365`；没有 `likely_future_bottleneck` 或高置信度结论。

## 公司映射与三类排名状态

- 已保留 `watch_only`：铜冠铜箔 `301217.SZ`（高频高速铜箔，`revenue`，2026-07-20）、宏和科技 `603256.SH`（电子级玻纤布，`revenue`，2026-07-15）、容大感光 `300576.SZ`（PCB 光刻胶，`revenue`，2026-07-24）。三者均使用 A 级、可定位公司原始材料，但因分产品收入重要性、客户/AVL 或 AI 专用敞口不足，不得标为 `main_candidate`。
- 基本面质量（仅本期披露完整度）：铜冠铜箔 > 宏和科技 > 容大感光；业绩弹性（非正式预期差）：铜冠铜箔 > 宏和科技 > 容大感光。
- 交易弹性：`N/A`。本期未重新获取截至 2026-08-02 的实时价格、换手、市值或估值快照，不复用 7 月 24 日旧行情，也未触发 `financial-evidence-audit`。

## 下期默认问题

1. 第二家板厂是否披露同一材料的具体交期、配额、订单延期或转单？
2. HVLP3/4/5 是否出现分等级销量、良率、客户、加工费、毛利或 LTA？
3. 电子布能否按板级 Low Dk/Df、载板 Low CTE/T-glass、Q cloth 分别披露产能、良率、AVL 和交期？
4. CCL 厂能否披露 M8/M9/M10 报价有效期、lead time、锁料、二供和树脂牌号？
5. 容大新增产线、设备、钻针、湿化学是否出现可验证 backlog、认证排队或交付受阻？
