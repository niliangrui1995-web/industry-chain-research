# AI产业链周度堵点跟踪模板说明

本目录服务三个长期自动化任务：

- `optical_module/`：光模块及上游细分环节。
- `ai_pcb/`：AI PCB 及上游材料设备。
- `ai_chain/`：AI 产业链上下游总览。

## 光模块边界补充

`optical_module/` 的研究宇宙纳入光模块/光引擎热管理与液冷兼容，以及明确传导到 AI 数据中心、CPO/ELS、光引擎或高密度光连接的光纤/跳线/光纤阵列/PM fiber。机柜级液冷、CDU、冷板总成、通信用普通光纤大周期、光纤预制棒和普通光缆需求只作为外部变量，除非出现 A/B 级证据证明它们直接限制光模块或光引擎交付、良率、客户认证或可靠性。

## 核心目标

每次周度任务不是重写行业教材，而是识别和跟踪产业链的堵点/卡点：

1. 当前哪些细分环节存在堵点/卡点。
2. 堵点/卡点由什么机制造成。
3. 与上次相比，堵点/卡点是缓解、加剧、不变、证伪、降级观察，还是出现了新卡点。
4. 当前堵点/卡点可能持续多久，缓解路径和反转指标是什么。
5. 其他产业链环节未来 6-24 个月是否可能出现新卡点或卡点迁移。
6. 这些变化如何影响产业链利润池、订单兑现、上市公司映射和后续跟踪优先级。

## 堵点/卡点定义

只有满足“需求超过合格供给、可用产能、良率、交付能力或客户认证供应商”的节点，才可归为堵点/卡点。

以下情况不能单独作为堵点结论：

- 细分环节技术壁垒高。
- 毛利率高或价值量高。
- 市占率集中或 HHI 高。
- 客户认证周期长。
- 国产替代难。
- 股票市场关注度高。
- 只有 C 级传闻或概念板块标签。

这些可以进入 `watch`，但不能升为 `hard_bottleneck` 或 `soft_bottleneck`，除非有 A/B 级证据证明供需缺口。

## 状态口径

每个任务每次运行后都要更新对应的 `state.md`。

| 状态 | 含义 |
|---|---|
| `new` | 本期新增堵点或新进入观察的潜在卡点 |
| `upgraded` | 证据闭环或严重程度较上期升级，包括供需缺口扩大、交期拉长、良率/认证收紧 |
| `unchanged` | 堵点仍存在，但没有明显边际变化 |
| `downgraded` | 供给改善、交期缩短、替代/二供推进，或原有证据不足而降级 |
| `resolved` | 供需缺口已被证实消除 |
| `rejected` | 被证据证伪，不再作为堵点跟踪 |

## 证据分级

| 等级 | 允许用途 |
|---|---|
| A | 官方公告、交易所披露、财报、业绩会、IR、监管文件、客户/供应商一手材料。可支持主结论。 |
| B | 可信财经或产业媒体、可核验研报摘要、行业数据库、具名来源。可支持主结论，但要说明限制。 |
| C | 社交平台、传闻、模型摘要、无原始链接信息。只能作为搜索线索或观察池。 |

## 每次运行的固定顺序

执行中可以按研究复杂度自主拆分任务并调用子代理；子代理适合承担独立的信息收集、证据核验、细分环节拆解、海外龙头梳理和上市主体初筛。子代理默认使用超高智能。若子代理达到上限，应排队等待前面的子代理完成，再继续新建后续子代理；主代理负责最终证据分级、交叉验证、堵点判断、排名和报告合成。

0. 读取 `docs/automation/AUTOMATION_RUN_CONTRACT.md`，在业务采集或写入前运行 `python scripts/automation_run_metadata.py --repo-root "D:\vcp_hunter\产业链投研" --skill research-industry-chain --pretty`；将 `skill_revision`、`prompt_contract_version` 及完整元数据写入本期报告和 `state.md`。如后续调用 `ai-chain-research-orchestrator` 或 `financial-evidence-audit`，完成前带齐实际 Skill 重跑并覆盖元数据。预检失败时只写最小失败状态并以 `blocked/precheck_failed` 结束。
1. 读取本任务 `state.md` 和最近一期报告。
2. 回访上次留下的 3-5 个跟踪问题。
3. 建立本周新增证据表，标明 A/B/C 等级。
4. 更新当前堵点账本；`status_change` 只使用 `new | upgraded | unchanged | downgraded | resolved | rejected`。
5. 为每个 `hard_bottleneck` 和 `soft_bottleneck` 建立唯一 `evidence_check_id` 的三腿证据包：需求、供给、缺口分别记录证据日期、来源类型和可复核定位，并做节点深挖。
6. 预估当前 `hard_bottleneck` 和 `soft_bottleneck` 的可能持续时间，写明时间窗口、判断依据、置信度、缓解路径和反转指标；证据不足时写 `N/A` 并说明缺什么证据。
7. 扫描未进入本期主深挖的其他产业链环节，预测未来 6-24 个月可能出现的新卡点或卡点迁移，写明需求触发、供给滞后机制、可能时间、升级触发阈值、证据日期/类型/定位、最大证据年龄、证据缺口和反转指标。`likely_future_bottleneck` 或 high confidence 只接受不晚于本期 `as_of` 且默认 365 天内的 A/B 级可信来源；陈旧或弱来源只能 low-confidence `watch`。
8. 只有在堵点节点明确后，才映射上市公司，并完整记录商业化阶段证据链、`revenue_materiality` 和 `verdict`。
9. 生成本期结构化证据包，依次运行 strict normalizer 与 bottleneck validator；只有两者均通过，hard/soft 才可准出。
10. 更新本期报告和 `state.md`。

## 结构化准出合同

三份 `BASELINE_TEMPLATE.md` 中的“当前堵点账本”“瓶颈证据检查”“未来 6-24 个月卡点迁移”“上市公司映射”分别对应 `bottleneck_ledger`、`bottleneck_evidence_checks`、`future_bottleneck_scenarios`、`china_candidates`。表头使用 normalizer 支持的中文字段名，不得自行改成未登记同义词。

每期至少保存：

- `YYYY-MM-DD.evidence.json`：上述结构化表的原始证据包。
- `YYYY-MM-DD.bottleneck_evidence_checks.csv`：与 JSON 中同一批 `bottleneck_evidence_checks` 记录一致，供独立 validator 复核。
- `YYYY-MM-DD.normalized.json`：strict normalizer 输出。

以同一个明确的 `as_of` 依次运行：

```powershell
python .agents/skills/research-industry-chain/scripts/normalize_research_inputs.py --input artifacts/weekly_chain_tracking/<task>/YYYY-MM-DD.evidence.json --as-of YYYY-MM-DD --strict --pretty --out artifacts/weekly_chain_tracking/<task>/YYYY-MM-DD.normalized.json
python .agents/skills/research-industry-chain/scripts/validate_bottleneck_evidence.py --csv artifacts/weekly_chain_tracking/<task>/YYYY-MM-DD.bottleneck_evidence_checks.csv --as-of YYYY-MM-DD --pretty
```

normalizer 与 validator 都只做证据完整性和等级一致性门，不自动授予瓶颈结论。ledger 的 `evidence_review_status` 必须与 normalizer 计算值一致；validator 非零退出、证据过期、来源等级不足或交叉表关联失败时，必须降为 `watch/rejected` 或保留为明确的证据缺口，不能继续输出 hard/soft。

## 行情快照规则

涉及最新价格、市值、PE/PB、换手、涨跌幅、成交量或交易弹性时，必须用本地市场数据或联网核对；缺失就写 `N/A`，不要用记忆补数。行情只作为交易弹性和拥挤度上下文，不证明产业受益或堵点成立。

默认 fallback 顺序：

| 市场 | 首选 | 备选 | 失败处理 |
|---|---|---|---|
| A 股 | 腾讯 `http://qt.gtimg.cn/q=sh/sz<code>` | adata SDK（如已安装） | 全部失败写 `N/A` 并说明原因 |
| 港股 | 腾讯 `http://qt.gtimg.cn/q=hk<code>` | Stooq；Yahoo 原生 chart | 全部失败写 `N/A` 并说明原因 |
| 美股 | 腾讯 `http://qt.gtimg.cn/q=us<TICKER>` | Stooq；Yahoo 原生 chart | Yahoo 兼容代理只作最后兜底 |
| 台股上市 | TWSE MIS `tse_<code>.tw` | Yahoo 原生 chart `<code>.TW`；Stooq（如可用） | 全部失败写 `N/A` 并说明原因 |
| 台股上柜 | TWSE MIS `otc_<code>.tw` | Yahoo 原生 chart `<code>.TWO`；Stooq（如可用） | 全部失败写 `N/A` 并说明原因 |

接口失败判定不能只看 HTTP 状态码。HTTP `404`、超时、空响应、陈旧数据、解析失败，以及腾讯返回 `v_pv_none_match="1"`，都视为该源失败并继续 fallback。台股不要把腾讯 `tw<code>` 的 no-match 返回当成有效行情源。

## 输出文件

每个任务目录至少保留：

- `state.md`：滚动状态。
- `BASELINE_TEMPLATE.md`：首期和后续报告模板。
- `YYYY-MM-DD.md`：每期实际报告。
- `YYYY-MM-DD.evidence.json`、`YYYY-MM-DD.bottleneck_evidence_checks.csv`、`YYYY-MM-DD.normalized.json`：结构化证据、独立验证输入和规范化结果。

## 对话窗口摘要要求

每次运行除了更新本期报告和 `state.md`，还必须在对话窗口给出一个极简摘要。摘要不替代报告正文；窗口里不再重复已更新文件、上期问题回访、完整证据表、候选公司排名、最大风险或下期问题。

对话窗口摘要只包含两张表：

| 当前核心卡点 | 原因/约束机制 | 关键证据 | 预计持续时间 | 缓解/反转指标 |
|---|---|---|---|---|
| N/A | N/A | N/A | N/A | N/A |

| 未来潜在卡点环节 | 可能成为卡点的原因 | 当前证据/争议 | 预计成为卡点时间 | 升级触发阈值 | 反转指标 |
|---|---|---|---|---|---|
| N/A | N/A | N/A | N/A | N/A | N/A |

证据不足时写 `N/A` 或 `watch`，并在对应单元格说明证据缺口。
