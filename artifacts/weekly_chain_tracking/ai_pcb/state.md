# 周度跟踪：AI PCB 及上游材料设备 - 滚动状态

更新时间：2026-06-25
最近报告：`artifacts/weekly_chain_tracking/ai_pcb/2026-06-21.md`
前次证据追杀：`artifacts/weekly_chain_tracking/ai_pcb/2026-06-17_hvlp_tglass_nvidia_capacity_evidence_layering.md`、`artifacts/weekly_chain_tracking/ai_pcb/2026-06-17_hvlp_tglass_nvidia_official_lock_capacity_chase.md`
A股供给压力卡：`artifacts/weekly_chain_tracking/ai_pcb/2026-06-17_defu_block_trade_supply_pressure_card.md`
A股 CCL 质量锚最小卡：`artifacts/company_tracking/600183.SH/state.md`

当前阶段：完成 2026-06-15 至 2026-06-21 周度更新。本期不升级任何节点为 `hard_bottleneck`。`高端电子玻纤布 / Low Dk / Low CTE / T-glass / NER-glass / Q cloth` 与 `M7/M8/M9/M10 CCL / prepreg` 继续作为当前最强 `soft_bottleneck+`。本周最重要新增 A 级增量是沪电股份 2026-06-18 投资者关系记录：公司点名超低损耗树脂、HVLP 铜箔、特种高性能玻纤布阶段性供应偏紧。该证据强化材料端卡点，但不能直接证明成品板制程端交期失控，也不能把 HVLP4/5 或 NVIDIA 锁产写成硬事实。

`HVLP4/HVLP5 PCB 铜箔` 维持 `watch_to_soft / 高优先级验证`。Mitsui、Co-Tech 年报与 DIGITIMES 可支持高端 HVLP 需求和供应链介入线索，但 `NVIDIA 直签`、`寄售/consignment`、`LTA`、`capacity reservation`、`prepayment` 仍未形成 A 级闭环；A 股公司仍缺 HVLP4/5 多客户批量收入、客户认证、加工费和毛利贡献。`高频高速树脂体系` 因沪电官方点名超低损耗树脂偏紧，新增为 `watch_to_soft`；仍缺牌号、供应商、交期、价格和客户 AVL 证据。`成品 AI PCB 高层板良率 / 测试 / 交付` 从 `watch` 上调 `watch_to_soft`，但当前没有足够交期/良率/测试瓶颈证据。

2026-06-22 08:53 邮件复核：建滔 CCL 单张毛利 80 元、铜冠 HVLP4 加工费 15-20 万元/吨与 HVLP5 送样、生益科技/南亚新材映射，全部先作为 `mixed-source / lead_only` 增量处理。它们可以和沪电 IR、Mitsui、Co-Tech、台系 CCL 涨价材料一起强化 `M7/M8/M9/M10 CCL / prepreg` 的 `soft_bottleneck+` 以及 `HVLP4/HVLP5 PCB 铜箔` 的 `watch_to_soft`，但不能升级为 hard，也不能写成铜冠或 A 股 CCL 公司已完成 HVLP4/5 或 M8/M9/M10 分产品收入、加工费、毛利闭环。最关键 source gap 排序：`A股公司分产品收入/毛利` > `铜冠 HVLP4/5 官方客户/收入/加工费/毛利` > `建滔单张毛利官方口径`。

2026-06-25 08:49 邮件复核：`12 英寸硅片涨价 -> 台积电先进节点涨价 5-10% -> 联发科涨价函 -> PCB/CCL 材料涨价` 只能作为行业涨价背景线索。官方/一级来源层面，TSMC Q1 2026 仅确认先进制程/HPC 收入占比和毛利率强，不公开确认 5-10% 全节点涨价；MediaTek 官方法说仅确认通过 disciplined pricing strategy 维持毛利，涨价函来自媒体披露；SEMI 确认硅片出货和 AI data center 需求强，环球晶股东会报道可作为上游涨价 primary-adjacent 线索，但信越/SUMCO 涨价幅度没有公司公告闭环。该线索维持 `M7/M8/M9/M10 CCL / prepreg` 的 `soft_bottleneck+`，不升 hard；生益科技只作为 A 股 CCL 质量锚，已兑现口径限于公司 2025 年报/Q1 的分产品收入、毛利率和业绩改善，不能外推到 M8/M9/M10 ASP、客户锁料或高端 CCL 毛利闭环。详见 [生益科技 600183.SH 最小跟踪卡](../../company_tracking/600183.SH/state.md)。

## 任务边界

本任务只跟踪板级 AI PCB 及其上游材料、设备和耗材：
- AI 服务器 / 交换机板级 PCB。
- 高速多层板、HDI/mSAP、类载板工艺；不等同于 ABF/BT 封装载板。
- 高端 CCL / prepreg：M7/M8/M9/M10 低损耗材料。
- 低 Dk / 低 Df / 低 CTE 电子布、T-glass、NER-glass、Q cloth、石英布、超薄布。
- HVLP / VLP / RTF PCB 铜箔。
- PPO / PPE / 碳氢 / 活性酯 / BMI 等高频高速树脂体系。
- 钻针、铣刀、压合、曝光、钻孔、电镀、测试设备。
- 湿化学、油墨、PCB 光刻胶等工艺材料。

强制边界：
- 板级 PCB 与 ABF/BT 封装载板必须分开。
- 载板 T-glass/Q glass 与板级 CCL Low Dk/Low CTE 电子布必须标注 `end_use`，不得跨用途自动升级。
- 行情、涨停、换手、媒体标题、X/Grok/Gemini 结论只能作为交易或核验线索，不能证明产业受益或卡点成立。

## 执行补充要求

- 每次更新报告时，必须对当前 `hard_bottleneck` 和 `soft_bottleneck` 预估可能持续时间，写明时间窗口、判断依据、置信度、缓解路径和反转指标；证据不足时写 `N/A`，并说明缺哪类证据。
- 每次不能只分析主深挖节点，还要扫描其他材料、设备、耗材、化学品和成品板环节，判断未来 6-24 个月可能出现的新卡点或卡点迁移。
- 对话窗口最终摘要只保留两张表：`当前核心卡点｜原因/约束机制｜关键证据｜预计持续时间｜缓解/反转指标`，以及 `未来潜在卡点环节｜可能成为卡点的原因｜当前证据/争议｜预计成为卡点时间｜升级触发阈值｜反转指标`。
- 行情快照必须按项目 `skills/allstock-data` 的多源 fallback 规则执行：A/H/美股优先腾讯 `qt.gtimg.cn`，台股优先 TWSE MIS；行情只用于交易弹性上下文，不证明产业受益或堵点成立。

## 上期问题回访状态

| 待验证问题 | 当前状态 | 结论 |
|---|---|---|
| 台玻是否发布更正式的股东会资料或法说，披露 Low DK/Low CTE 分产品交期、价格、客户认证、产能和良率 | 部分证实，仍待跟踪 | 台玻高端玻纤布供不应求至 2027 年底仍主要来自媒体转述；沪电官方从板厂侧确认特种高性能玻纤布偏紧，强化 `soft_bottleneck+`，但缺分产品 A 级交期/配额/良率。 |
| Nittobo、台玻、宏和、中材、国际复材、菲利华是否出现分布种 allocation、客户 AVL 排队或订单延期证据 | 证据增强但未 hard | 沪电 IR 强化方向，但不是供应商分布种 allocation；继续要求官方交期、配额、客户 AVL 和订单延期。 |
| 台光电、台燿、联茂、建滔、生益、南亚是否披露 M8/M9/M10 CCL/prepreg 分产品 lead time、报价有效期、客户提前锁料或二供认证 | 部分证实，仍待跟踪 | 台系涨价、强营收、板厂材料偏紧、2026-06-22 邮件中的建滔单张毛利线索、以及 2026-06-25 邮件中的晶圆代工/IC 设计涨价背景共同支持 CCL/prepreg `soft_bottleneck+`，但建滔 80 元单张毛利、台积电 5-10% 涨价和联发科涨价函均不能直接写成 A 股 CCL 分产品 ASP/毛利证据。 |
| 德福、诺德、嘉元、铜冠是否出现 PCB 级 HVLP4/HVLP5 多客户批量供货、客户认证、收入、良率或毛利贡献 | 未证实，维持观察 | 海外高端 HVLP 偏紧有 A/B 级支撑；2026-06-22 邮件新增铜冠 HVLP4 涨价、加工费和 HVLP5 送样线索，但仍属 mixed-source。A 股端仍缺 HVLP4/5 批量收入、客户、加工费和毛利；不能因股价强、邮件或互动线索升主结论。 |
| 沪电、生益电子、深南、胜宏、TTM、Sanmina、金像电、臻鼎、尖点、大族数控、鼎泰高科是否披露交期拉长、良率/测试瓶颈、设备 backlog 或耗材认证排队 | 需求证实，瓶颈 `watch_to_soft` | 沪电/TTM 等强化需求和材料偏紧，但成品板制程端仍缺两家以上交期/良率/测试瓶颈证据；设备耗材仍缺 backlog/认证排队。 |
| NVIDIA、AWS、Google、Meta、Nittobo、Mitsui、Co-Tech 是否出现 LTA、consignment、prepayment、allocation 或 capacity reservation 官方表述 | 仍未闭环 | DIGITIMES 只能支持 NVIDIA 接洽 Co-Tech 的 B 级线索；NVIDIA 10-Q 通用预付/长期供应披露不能外推到 HVLP/T-glass。 |

## 当前堵点账本

| 节点 | 定位 | 严重程度 | 造成堵点的机制 | 本期变化 | 关键证据 | 预计持续时间 | 缓解路径 | 反转指标 | 下次动作 |
|---|---|---|---|---|---|---|---|---|---|
| 高端电子玻纤布 / Low Dk / Low CTE / T-glass / NER-glass / Q cloth | 本期主深挖卡点 | `soft_bottleneck+` | 窑炉、拉丝、电子级纱、织布、后处理、良率、专利和客户 AVL 限制 qualified output；普通布/工业纱不可替代 | `worsened/confirmed` | 沪电官方点名特种高性能玻纤布阶段性供应偏紧；台玻媒体口径称供不应求至 2027 年底；Nittobo/TrendForce 支持供给集中和扩产慢 | 2026H2-2027年底中高置信；Q cloth/NER 2027H2-2028 watch | 台玻/富乔/宏和/中材/国际复材扩产或二供验证，Nittobo 2027-2028 扩产，CCL 配方优化 | 报价回落、交期缩短、库存恢复，多供应商进入核心客户 AVL | 查正式法说、分布种交期、客户认证、良率和 allocation |
| M7/M8/M9/M10 CCL / prepreg | 当前最明确板级材料卡点 | `soft_bottleneck+` | AI server/networking 拉动低损耗材料；玻纤布、超低损耗树脂、HVLP 铜箔、新线 qualified output 和客户认证共同约束 | `industry_price_background_added_no_upgrade` | 沪电官方点名超低损耗树脂/HVLP/特种玻纤布偏紧；台系涨价和采购端 lead-time 线索继续支持；2026-06-25 邮件的台积电/联发科/硅片涨价链只作为行业背景，不作为 A 股公司 ASP 证据 | 2026H2 中高置信偏紧；2027H1 中等偏高；2027H2 取决于高端布、树脂、铜箔和 CCL 新线释放 | CCL 高端线投产，二供通过终端认证，上游材料同步放松 | 报价停涨或回落，lead time 常态化，客户不再提前锁料，二供进入核心 AVL | 查台系/大陆 CCL 的 M8/M9/M10 lead time、报价有效期、分产品收入、ASP 和毛利；生益科技只记录已披露产品收入/毛利，不补写未披露 ASP |
| HVLP4/HVLP5 PCB 铜箔 | 次级跟踪 | `watch_to_soft` | 表面处理、低粗糙度一致性、添加剂配方、客户认证和进口供应集中限制高端供给；锂电铜箔不能替代 PCB 级铜箔 | `unchanged_high_priority / mixed_source_increment / lock_capacity_unclosed` | Mitsui 官方确认高端 HVLP 需求增长和扩产；Co-Tech 年报确认 HVLP4 结构性缺口、认证时间长和良率慢；DIGITIMES 称 NVIDIA 接洽 Co-Tech；2026-06-22 邮件新增铜冠 HVLP4 涨价和 HVLP5 送样 mixed-source 线索；A 股批量证据不足 | 2026H2-2027 watch_to_soft；持续时间 N/A，缺 HVLP4/5 多客户批量收入、客户、加工费、毛利和锁产合同证据 | 国内外多供应商稳定量产，并被 CCL/板厂客户认证 | PCB 级 HVLP4/5 多客户批量供货、加工费回落、国产良率确认；或官方确认/否认客户锁产 | 查 Mitsui/Co-Tech/德福/诺德/嘉元/铜冠/逸豪 PCB 级 HVLP4/5 交付、收入、加工费、客户和毛利证据 |
| 高频高速树脂体系 | 新增次级观察 | `watch_to_soft` | M8/M9/M10 CCL 对 PPO/PPE、碳氢、活性酯、BMI 等牌号和配方认证提出更高要求 | `new` | 沪电官方点名超低损耗树脂阶段性供应偏紧 | 2026H2-2027 watch；持续时间 N/A，缺牌号级交期、涨价、供应商和客户证据 | 替代配方通过认证，树脂供应恢复 | 树脂牌号供给恢复、交期正常、CCL 厂不再提示材料压力 | 查 CCL 厂和树脂供应商是否披露牌号、价格、交期和认证 |
| 成品 AI PCB 高层板良率 / 测试 / 交付 | 次级跟踪 | `watch_to_soft` | 高层压合、背钻、钻孔、电镀、阻抗测试和客户审厂可能成为材料之后的制程瓶颈 | `upgraded_from_watch` | 沪电/TTM/胜宏/深南证明需求和高端产品放量；仍缺交期/良率/测试硬证据 | 2026H2-2027 watch_to_soft | 板厂扩产达产、客户二供补足 | 交期恢复、订单延期减少、未出现良率/测试瓶颈 | 查沪电、生益电子、深南、胜宏、TTM、Sanmina、金像电、臻鼎 backlog、交期、良率、测试产能 |
| 钻针/测试设备/湿化学/油墨/PCB 光刻胶 | 观察 | `watch` | 板厂 capex 和高端工艺升级带动设备、耗材和工艺材料需求 | `unchanged` | 大族数控/尖点等证明需求方向；缺 A/B 级 backlog、短缺或客户认证排队 | 2027-2028 watch；中低置信 | 国产设备/耗材供应与客户验证顺利 | 设备交付恢复，价格稳定，客户认证不排队 | 跟踪 backlog、交期、认证排队 |
| ABF/BT 封装载板 | 单独观察 | `watch_separate` | 封装载板链路，和板级 AI PCB 不同 | `separate_only` | JP Morgan 中文整理和海外载板证据支持相邻链路景气，但不能并入板级 PCB | 6-24 个月单独跟踪 | 单独载板扩产和良率改善 | 与板级 PCB 混同即无效 | 如有载板证据单独开表 |

## 候选观察池

| 候选节点 | 需要验证的堵点问题 | 当前处理 |
|---|---|---|
| 高端电子玻纤布分产品 | Low Dk/Df、Low CTE、T-glass、NER-glass、Q cloth 是否出现交期/配额硬证据 | 当前最重要主线，2026H2-2027年底维持偏紧 |
| M9/M10 低损耗 CCL/prepreg | 是否从当前软卡点升级为官方 allocation/lead time 硬卡点 | `soft_bottleneck+ / likely_future_bottleneck` |
| HVLP4/HVLP5 PCB 铜箔 | 是否有 PCB 级批量交付、客户认证、收入贡献和加工费上调 | `watch_to_soft`，NVIDIA/Co-Tech 线索提高验证优先级但锁产未闭环 |
| 高频高速树脂体系 | 超低损耗树脂是否出现牌号级短缺、涨价和客户 AVL 排队 | `watch_to_soft` 新增观察 |
| 成品板良率/测试 | 是否从订单兑现升级为制程瓶颈 | `watch_to_soft` |
| 钻孔/压合/电镀/测试设备 | 是否出现设备交期拉长和板厂 capex 排队 | 未来迁移观察 |
| 湿化学/油墨/PCB 光刻胶 | 是否出现客户认证排队和高端产品短缺 | 未来迁移观察 |

## 下期默认跟踪问题

1. 沪电之外，是否有第二家以上板厂正式确认超低损耗树脂、HVLP 铜箔、特种高性能玻纤布交期拉长或订单延期。
2. 台玻、富乔、Nittobo、宏和科技、中材科技、国际复材是否披露 Low Dk/Low CTE/T-glass/Q cloth 分产品交期、allocation、客户 AVL、良率和价格。
3. 台光电、台燿、联茂、建滔、生益、南亚是否披露 M8/M9/M10 CCL/prepreg 报价有效期、客户锁料、二供认证、lead time、分产品收入、ASP 或毛利；建滔单张毛利 80 元、台积电 5-10% 涨价和联发科涨价函都只能在公司/客户/法说/财报证实后升级为公司侧证据。
4. Co-Tech、Mitsui、德福、诺德、嘉元、铜冠、逸豪是否出现 HVLP4/HVLP5 多客户批量收入、加工费、毛利、客户认证或锁产合同证据；铜冠 HVLP4 涨价落地和 HVLP5 送样需公司公告、IR 或客户/CCL 厂交叉验证。
5. 成品板和设备耗材是否出现交期、良率、测试产能、设备 backlog、钻针/药水/油墨认证排队证据。
6. NVIDIA、AWS、Google、Meta、Nittobo、Mitsui、Co-Tech 是否出现 LTA、consignment、prepayment、allocation 或 capacity reservation 官方表述。
7. 后续所有 T-glass/Low CTE/Q glass 记录必须标注 `end_use`，严格区分 ABF/IC 载板与板级 PCB/CCL；同一供应商同一材料词不自动跨用途升级。

## 对话窗口摘要

| 当前核心卡点 | 原因/约束机制 | 关键证据 | 预计持续时间 | 缓解/反转指标 |
|---|---|---|---|---|
| 高端电子玻纤布 / Low Dk / Low CTE / T-glass / Q cloth | 窑炉、拉丝、织布、后处理、良率、专利和客户 AVL 限制 qualified output；普通布/工业纱不可替代 | 沪电 2026-06-18 IR 点名特种高性能玻纤布阶段性供应偏紧；台玻媒体口径称高端布供不应求至 2027 年底；TrendForce/Nittobo 支持供给集中和扩产慢 | 2026H2-2027年底中高置信；Q cloth/NER 2027H2-2028 watch | 台玻/Nittobo/二供产能转为 qualified output；报价回落、交期缩短、库存恢复，多供应商进入核心 AVL |
| M7/M8/M9/M10 CCL / prepreg | AI server/networking 推动低损耗材料升级；玻纤布、超低损耗树脂、HVLP 铜箔、新线 qualified output 和客户认证共同约束 | 沪电 IR 同时点名超低损耗树脂、HVLP 铜箔、特种高性能玻纤布偏紧；台系涨价、采购端 lead-time、台积电/联发科/硅片涨价背景共同支持，但公司侧 ASP/毛利仍缺分产品闭环 | 2026H2 中高置信偏紧；2027H1 中等偏高；2027H2 取决于上游材料和 CCL 新线释放 | 报价停涨或回落，lead time 常态化，客户不再提前锁料，二供进入核心 AVL |

| 未来潜在卡点环节 | 可能成为卡点的原因 | 当前证据/争议 | 预计成为卡点时间 | 升级触发阈值 | 反转指标 |
|---|---|---|---|---|---|
| HVLP4/HVLP5 PCB 铜箔 | 224G/1.6T/M9/M10 对低粗糙度和表面处理一致性要求提升，海外高端供应集中 | Mitsui/Co-Tech 官方支持高端 HVLP 需求和供给刚性，DIGITIMES 有 NVIDIA 接洽 Co-Tech 线索；但直签、寄售、LTA、capacity reservation、A 股批量收入均未闭环 | 2026H2-2027 watch_to_soft | HVLP4/5 多客户批量收入、客户认证、加工费上调、毛利贡献；或客户/供应商正式锁产证据 | 多供应商稳定供货，加工费回落，国产良率确认；或官方否认/淡化锁产叙事 |
| 高频高速树脂体系 | M8/M9/M10 CCL 配方升级对 PPO/PPE、碳氢、活性酯、BMI 等牌号和认证提出更高要求 | 沪电官方点名超低损耗树脂阶段性偏紧，但缺牌号、供应商、价格和交期证据 | 2026H2-2027 watch_to_soft | CCL 厂或树脂厂点名牌号短缺、交期拉长、涨价、客户 AVL 排队 | 替代配方通过认证，树脂交期恢复，CCL 厂不再提示材料压力 |
| 成品 AI PCB 高层板良率/测试 | 材料缓解后瓶颈可能迁移到高层压合、背钻、电镀、阻抗/可靠性测试和客户审厂 | 沪电/TTM 等证明需求强，但交期/良率/测试硬证据不足 | 2026H2-2027 watch_to_soft | 两家以上板厂披露交期拉长、良率瓶颈、测试产能不足、订单延期或客户转单 | 扩产达产，订单延期减少，交期正常 |
