# 周度跟踪：AI PCB 及上游材料设备 - 滚动状态

更新时间：2026-08-23
最近报告：[2026-08-23.md](2026-08-23.md)
前次报告：[2026-08-09.md](2026-08-09.md)
基线模板：[BASELINE_TEMPLATE.md](BASELINE_TEMPLATE.md)  
结构化输入：[2026-08-23_research_inputs.json](2026-08-23_research_inputs.json)
证据包：[2026-08-23_bottleneck_evidence.csv](2026-08-23_bottleneck_evidence.csv)

## 本期运行元数据

- captured_at_beijing：2026-08-23T18:23:03+08:00
- prompt_contract_version：2026-07-27.1
- skill_revision：git:0027e7bf17f1bcd418d20412868df311919decf4
- skill_content_sha256：656fd6486cebe6403278246e6d7424d8f25c1ae6894787f172b244eeec2bb5e0
- skill_tree_status：clean
- skills：ai-chain-research-orchestrator，research-industry-chain
- status：ok
- 固定 as_of：2026-08-23（北京时间）。

## 当前阶段

- 当前没有 hard_bottleneck。所有 hard/soft 证据包均由 normalizer 重算状态；eligible_for_bottleneck_review 只表示包完整且新鲜，不替代人工瓶颈判断。
- 新增板级高多层/高阶 HDI 有效交付（不含 ABF/BT）为 soft_bottleneck：景旺电子披露批供、订单快速增长、AI 工厂满产及未来数月有效产能不足，生益电子提供高多层/高阶 HDI 结构性紧张交叉证据。仍无行业级硬交期、allocation、转单或客户延期。
- 高频高速 PCB 铜箔（含 HVLP；分等级 N/A）、板级 Low Dk/Df/超薄电子布（不含 Low CTE/T-glass）和高端高速 CCL/prepreg 材料组合（M8/M9/M10 分级 N/A）均保持 soft_bottleneck / unchanged。
- 德福科技的 HVLP1-4 批供、HVLP4 小批量和 HVLP5 客户导入是铜箔二供/扩产反证；宏昌电子高频高速树脂项目正式生产是树脂供给缓解反证。二者均未证明同一 AVL 已稳定放量。
- 树脂、干膜/湿化学、湿制程/电镀设备、钻针和测试设备均为 watch。东威/大族的订单与供给保障只证明需求或缓解路径；未见行业 backlog、硬交期、认证排队或交付受阻。
- ABF/BT 载板与 Low CTE/T-glass 继续 watch_separate。南亚混列的 ABF/CCL/铜箔/玻纤材料口径不能用于 ABF 单独短缺，也不能并入板级 PCB。

## 本期证据、校验与变化

| 节点 | 检查 ID | 当前严重程度 | 本期变化 | 验证结果 | 关键边界 |
|---|---|---|---|---|---|
| 板级高多层/高阶 HDI 有效交付（不含 ABF/BT） | ai-pcb-20260823-board-01 | soft_bottleneck | upgraded | eligible_for_bottleneck_review；最旧腿 1 天 | 现有满产和有效产能不足不是行业 hard lead time |
| 高频高速 PCB 铜箔（含 HVLP；分等级 N/A） | ai-pcb-20260823-copper-01 | soft_bottleneck | unchanged | eligible_for_bottleneck_review；最旧腿 2 天 | HVLP1-4/HVLP5 的二供进展不等于同一 AVL 放松 |
| 板级 Low Dk/Df/超薄电子布 | ai-pcb-20260823-cloth-01 | soft_bottleneck | unchanged | eligible_for_bottleneck_review；最旧腿 9 天 | 不把 Low CTE/T-glass 或 Q cloth 混入板级行 |
| 高端高速 CCL/prepreg 材料组合（M8/M9/M10 分级 N/A） | ai-pcb-20260823-ccl-01 | soft_bottleneck | unchanged | eligible_for_bottleneck_review；最旧腿 8 天 | 南亚 ABF 混列不支持分等级或 ABF 结论 |

- validate_bottleneck_evidence.py 使用 as_of=2026-08-23：reviewable；4 条 eligible、0 条 incomplete、0 条 ineligible。
- normalize_research_inputs.py 使用 as_of=2026-08-23 且 strict：0 个 issues；ledger、check、顶层 as_of 和 time_horizon 一致。
- 2026-08-10 至 2026-08-23 官方扫描的明确证据缺口：HVLP3/4/5 的分等级交期/配额/LTA，M8/M9/M10 的报价和 AVL，树脂的牌号级交期，设备/耗材的行业 backlog。铜冠铜箔和容大感光在窗口内没有相应经营型新披露；零披露不解释为供需放松。

## 当前堵点账本

| 节点 | claim_as_of | 严重程度 | 时间维度 | 约束机制 | 预计缓解 | 关键反转 |
|---|---|---|---|---|---|---|
| 板级高多层/高阶 HDI 有效交付（不含 ABF/BT） | 2026-08-23 | soft_bottleneck | 2026H2 | 良率、认证、材料齐套与新线爬坡 | 2026H2 起跟踪新线实际交期、稳定良率与客户认可 | 新增合格产能释放且高端订单不再造成满产 |
| 高频高速 PCB 铜箔（含 HVLP；分等级 N/A） | 2026-08-23 | soft_bottleneck | 2026H2 | 低粗糙度一致性、树脂匹配、良率与客户 AVL | HVLP1-4/HVLP5 的批供、认证和同平台二供 | 分等级加工费/交期回落，多源进入同一 AVL |
| 板级 Low Dk/Df/超薄电子布 | 2026-08-23 | soft_bottleneck | 2026H2 | 配方、拉丝、织布、表面处理、良率与 AVL | 2027-06 起跟踪特种纱/布项目与电子薄布稳定批供 | 分布种价格/交期回落，多源稳定进入同一 AVL |
| 高端高速 CCL/prepreg 材料组合（M8/M9/M10 分级 N/A） | 2026-08-23 | soft_bottleneck | 2026H2 | 布、铜箔、树脂共同满足配方、压合与终端认证 | 2026H2-2027H1 跟踪合格扩产和二供进入 AVL | 报价/交期常态化、停止锁料、二供进入核心 AVL |

## 未来 6-24 个月候选池

| 节点 | 当前处理 | 可能时间 | 置信度 | 升级触发阈值 | 反转指标 |
|---|---|---|---|---|---|
| 板级高多层/高阶 HDI 有效交付 | likely_future_bottleneck | 2026H2 | medium | 多家板厂出现硬交期、allocation、转单或延期 | 新线稳定良率和常态交期 |
| HVLP5/下一代超低粗糙度铜箔 | watch | 2027H1-2028 | low | 分等级批供、交期、配额或锁料 | 多源同平台批供、交期回落 |
| M9+/PTFE/M10 CCL-prepreg 与树脂组合 | watch | 2027-2028 | low | 分等级收入、牌号、交期、二供和 AVL | 多家量产、报价和交期常态化 |
| Q cloth/石英布与更低损耗板级电子布 | watch | 2027H2-2028 | low | 板级客户、AVL、稳定批供、交期或 allocation | 配方替代、多家稳定量产 |
| 湿制程/电镀设备、钻针、精密耗材和测试设备 | watch | 2026H2-2027 | low | 两家以上确认 backlog、交付受阻或认证排队 | 设备交期常态、扩产稳定交付 |
| ABF/BT 载板 T-glass/Low CTE 玻璃 | watch_separate | 2026H2-2027 | low | 载板链路独立出现 allocation、锁产、交期或良率缺口 | 替代材料认证、专用产能释放 |

所有 future 记录均设 future_max_age_days，板级高多层/高阶 HDI 的 likely 情景使用 180 天 A 级来源；其他低置信度 watch 使用 365 天上限。

## 公司映射与三类排名状态

- main_candidate：景旺电子 603228.SH，已具备板级 AI PCB 的批供、认证、订单、满产和扩产 A 级链路；AI 收入金额、客户名称和订单期限仍未披露。
- watch_only：生益科技 600183.SH、宏和科技 603256.SH、铜冠铜箔 301217.SZ、德福科技 301511.SZ、东威科技 688700.SH、容大感光 300576.SZ。阶段及来源均写入本期 JSON，不将细分收入、客户或下一阶段外推。
- 基本面质量分档：生益科技、景旺电子为第一档；宏和科技、铜冠铜箔、德福科技、东威科技为第二档；容大感光为 N/A。仅为披露完整度和经营韧性初筛，非估值评级。
- 业绩弹性分档：景旺电子、宏和科技、铜冠铜箔为第一档；生益科技、德福科技、东威科技、容大感光为第二档。仅反映已披露的订单/量价/产品结构传导，不是预期差。
- 交易弹性：N/A。本期没有可复核的行情、估值或市值快照。

## 下期默认问题

1. 两家以上板厂是否披露高多层/高阶 HDI 的硬交期、allocation、转单或客户延期？
2. HVLP3/4/5 是否出现同平台客户、分等级批供、交期、加工费或 LTA？
3. 电子布能否按板级 Low Dk/Df、Q cloth、载板 Low CTE/T-glass 分别披露产能、良率、AVL 和交期？
4. CCL 厂能否披露 M8/M9/M10 报价有效期、lead time、锁料、二供和树脂牌号，并证明宏昌高频高速树脂已通过下游量产导入？
5. 容大、东威及板厂是否出现干膜、湿化学、钻针、设备或测试的 backlog、认证排队或交付受阻？
