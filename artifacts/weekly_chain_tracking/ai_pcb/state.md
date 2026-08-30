# 周度跟踪：AI PCB 及上游材料设备 - 滚动状态

最近成功更新：2026-08-30（北京时间）。
本期完整报告：[2026-08-30.md](2026-08-30.md)。历史 2026-08-23 包保留为上期基线，不回写其 `claim_as_of`。

## 本期运行元数据

- captured_at_beijing：2026-08-30T18:03:14+08:00
- prompt_contract_version：2026-07-27.1
- skill_revision：git:c6eaa5262bd8c836d06cd48813bb0e49d70adefe
- skill_content_sha256：656fd6486cebe6403278246e6d7424d8f25c1ae6894787f172b244eeec2bb5e0
- skill_tree_status：clean
- skills：ai-chain-research-orchestrator，research-industry-chain
- status：ok
- 固定 as_of：2026-08-30（北京时间）。

## 当前阶段

- 当前没有 `hard_bottleneck`。本期 hard/soft 均以同一 `as_of` 的 companion 检查包重建；`eligible_for_bottleneck_review` 只表示证据包完整、新鲜且等级一致，不替代人工瓶颈判断。
- 板级高多层/高阶 HDI 有效交付（不含 ABF/BT）、高频高速 PCB 铜箔（含 HVLP）、板级 Low Dk/Df/超薄电子布和高端高速 CCL/prepreg 材料组合保持 `soft_bottleneck / unchanged`。
- 8 月 26–29 日正式中报补强了四项软卡点：沪士的 AI/HPC PCB 收入与原产能满载、铜冠的高端铜箔供不应求、金安的广义 CCL/电子布偏紧、南亚的 M6-M8 批供及 M9 认证/NPI。分等级交期、配额、LTA、同一 AVL 二供和客户延期仍为 `N/A`。
- 超低损耗树脂、干膜/湿化学、湿制程/电镀设备、钻针和测试设备均为 `watch`。容大、天承、正业只证明产品/项目/需求，未见行业 backlog、硬交期、认证排队或交付受阻。
- ABF/BT 与板级 PCB 继续分开：当前 ABF/BT 为 `watch_separate`；仅高端 IC/FC-BGA 载板的 SAP 有效产能上调为 2026Q4–2028 `likely_future_bottleneck / high`，BT 不借用该证据。

## 本期证据、校验与变化

| 节点 | 检查 ID | 严重程度 | 状态变化 | 校验 / 关键边界 |
|---|---|---|---|---|
| 板级高多层/高阶 HDI 有效交付（不含 ABF/BT） | ai-pcb-20260830-board-01 | soft_bottleneck | unchanged | fresh / eligible；公司级满产不等于行业硬交期 |
| 高频高速 PCB 铜箔（含 HVLP；分等级 N/A） | ai-pcb-20260830-copper-01 | soft_bottleneck | unchanged | fresh / eligible；HVLP1-4 批供是缓解反证 |
| 板级 Low Dk/Df/超薄电子布 | ai-pcb-20260830-cloth-01 | soft_bottleneck | unchanged | fresh / eligible；不混入 Low CTE/T-glass 或 Q cloth |
| 高端高速 CCL/prepreg 材料组合（M8/M9/M10 分级 N/A） | ai-pcb-20260830-ccl-01 | soft_bottleneck | unchanged | fresh / eligible；M6-M8 批供不推导 M9/M10 或行业 AVL |

- `normalize_research_inputs.py --as-of 2026-08-30 --strict`：0 issues；ledger、check、顶层 `as_of` 和 `time_horizon` 一致。
- `validate_bottleneck_evidence.py --as-of 2026-08-30`：`reviewable`；4 条 eligible、0 条 incomplete、0 条 ineligible。

## 当前堵点账本

| 节点 | claim_as_of | 严重程度 | 时间维度 | 约束机制 | 预计缓解 / 关键反转 |
|---|---|---|---|---|---|
| 板级高多层/高阶 HDI 有效交付（不含 ABF/BT） | 2026-08-30 | soft_bottleneck | 2026H2 | 良率、认证、材料齐套与新线爬坡 | 新线达客户认可良率、交期常态；多家硬交期/配额才考虑升级 |
| 高频高速 PCB 铜箔（含 HVLP；分等级 N/A） | 2026-08-30 | soft_bottleneck | 2026H2 | 低粗糙度一致性、树脂匹配、良率与客户 AVL | HVLP 同平台多源批供、分等级加工费和交期回落 |
| 板级 Low Dk/Df/超薄电子布 | 2026-08-30 | soft_bottleneck | 2026H2 | 配方、拉丝、织布、表面处理、良率与 AVL | 特种纱/布扩产稳定批供、分布种交期/价格回落 |
| 高端高速 CCL/prepreg 材料组合（M8/M9/M10 分级 N/A） | 2026-08-30 | soft_bottleneck | 2026H2 | 布、铜箔、树脂共同通过配方、压合与终端认证 | N8/M9 认证和合格产出兑现、分等级交期/报价常态化 |

## 未来 6–24 个月候选池

| 节点 | 当前状态 | 未来状态 / 时间 | 置信度 | 关键缺口 / 反转指标 |
|---|---|---|---|---|
| 高端 IC/FC-BGA 载板 SAP 有效产能（ABF 工艺族；BT 不含） | watch_separate | likely_future_bottleneck / 2026Q4-2028 | high | 分客户 allocation、实际交期和二供仍缺；Cell6/Cell8、AT&S Kulim 合格产能释放即反转 |
| 板级高多层/高阶 HDI 有效交付 | soft_bottleneck | likely_future_bottleneck / 2026H2 | medium | 缺行业硬交期/配额；新线稳定良率和常态交期即反转 |
| 板级下一代低损耗 CCL/prepreg + Low Dk/Df 电子布组合 | soft_bottleneck | watch / 2026H2-2027H2 | medium | 缺分级交期、LTA、树脂牌号和同 AVL 二供；新线量产和多源认证即反转 |
| HVLP5/下一代超低粗糙度铜箔 | soft_bottleneck（广义） | watch / 2026H2-2028 | low | 缺 HVLP5 批供量、交期、配额、同 AVL；多源量产和扩产按期释放即反转 |
| Q cloth/石英布与更低损耗板级电子布 | watch | watch / 2027H2-2028 | low | 缺板级 AI 客户、AVL、稳定批供与交期；配方替代和多源量产即反转 |
| 设备、钻针、精密耗材和测试 | watch | watch / 2026H2-2027 | low | 缺两家以上 backlog、硬交期或认证排队；稳定交付即反转 |

所有 future 记录均设 `future_max_age_days`：high/likely 的 SAP 情景为 180 天；其他 watch 为 30–365 天。封装载板 SAP 情景的“需求超过供给”是厂商管理层预测，非当前订单/交期事实。

## 公司映射与三类排名状态

- `main_candidate`：沪士电子 002463.SZ，`revenue`；AI 服务器/HPC PCB 收入约 18.28 亿元和高层板增长已有 A 级报告支持。该标签只代表研究优先级。
- `watch_only`：南亚新材 688519.SH、生益科技 600183.SH、宏和科技 603256.SH、铜冠铜箔 301217.SZ、德福科技 301511.SZ、容大感光 300576.SZ、天承科技 688603.SH。阶段、来源、evidence gap 已写入本期 JSON；不将批供/认证升级为 AI 专用收入。
- 基本面质量初筛第一档：沪士电子、生益科技、南亚新材；业绩弹性第一档：沪士电子、南亚新材、铜冠铜箔、宏和科技。两者均只基于正式报告的披露完整度与经营/量价传导，不是估值或交易排序。
- 交易弹性：N/A。本期没有可复核价格、市值、估值、换手或流动性快照。

## 下期默认问题

1. 多家板厂是否出现高多层/高阶 HDI 的行业硬交期、allocation、转单、客户延期或未满足订单。
2. HVLP3/4/5 是否出现同平台客户、批供量、交期、加工费、配额或 LTA。
3. 南亚 M9 认证/NPI、N8 试生产与 M6-M8 的分等级收入/客户 AVL 是否获得正式更新。
4. Low Dk/Df、Q cloth 与载板 Low CTE/T-glass 能否按分布种、用途、产能、良率、AVL、交期拆开。
5. IBIDEN/AT&S 的 SAP 扩产、良率、交期、第二来源如何验证或否定未来载板约束；BT 保持独立取证。
