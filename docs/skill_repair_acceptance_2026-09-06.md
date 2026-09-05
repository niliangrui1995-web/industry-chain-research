# 项目 Skill 七项修复与生产联调验收

验收日期：2026-09-06（北京时间）。七项缺陷均已修复，先保留失败复现，再运行修复后的回归与真实接口联调。当前累计 **158 项相关测试通过，11 个项目 Skill 结构校验通过**；仓库健康检查通过，按 `--skip-slow` 跳过依赖当前自动化环境的 earnings guardrail。

本轮只修改技能脚本、相应合同和测试，保留此前未提交的优化。生产请求和真实数据检查均为只读，结果写入 `artifacts/skill_repair_20260906/`；正式研究包、两融数据目录、HT 行情源未被联调覆盖。尚未提交或推送。

## 七项修复

| 问题 | 修复后的行为 | 验证 |
|---|---|---|
| 1. 财务 ratio 混用母公司与合并数据仍准出 | 检查报表范围、会计框架、计量口径；margin 的调整口径还需一致调整定义；同口径的不同指标标签可配对 | 冲突、未知范围阻断；真实 SEC 同季度合并毛利率通过 |
| 2. HHI 丢失 `%` 后错误放大 | 裸数字必须声明 `percent/fraction`，显式 `%` 保留；拒绝非有限数和非法份额 | `0.9% + 0.1%` 得到 HHI `0.82`、覆盖率 `1%` 并提示覆盖不足；真实 `N/A` 输入不产生精确 HHI |
| 3. 瓶颈主表与关联证据漂移仍 strict 通过 | 主表与权威 check 的 12 个重复证据字段逐项一致 | 等级、二供状态、证据文本等漂移全部拒绝；三个真实历史包完成隔离迁移验证 |
| 4. 两融缺日被算成单日变化 | 沪深日期并集保留缺口后求差；复用现有本地 TDX 日历识别双方同时缺日 | 缺失市场与合计变动为 `N/A`；完整单边保留有效变化；真实返回及三类删日注入通过 |
| 5. 字幕缺段仍报告成功 | 结束标记、列表格式、非空分段、全部下载和 WebVTT 时间轴共同决定完整性 | 缺段、错误页、非法时长、滑动窗口均非零退出；完整远端样例 100/100 分段通过 |
| 6. 真实零股息率被误阻断 | 有来源的零股息允许计算 `0%`；缺失、负股息与无效分母仍按原约束处理 | 零值、缺失与负值分开回归；Tesla 官方历史零股息与真实股价经 CLI 验证得到 `0%` |
| 7. HT 递归黑名单可能进入账户/日志目录 | 固定行情目录和文件名白名单；查询元数据前过滤名称；拒绝链接和 reparse point | 真实 HT 检查的 stat/lstat 边界违规为 0；合成账户/日志路径与路径穿越回归通过 |

## 真实接口与数据验收

| 接口或输入 | 本次实际结果 | 证据 |
|---|---|---|
| SEC companyfacts → submissions → 官方 10-Q | 三个接口均 HTTP 200；AAPL 同期毛利、收入与 iXBRL 原文一致，正式 audit 为 `PASS/publishable`；仅改范围的注入为 `FAIL/blocked` | `financial/production/` |
| Tesla 官方 2025 年 10-K → Yahoo chart | companyfacts 无股息 tag，按来源缺口保留；官方 10-K 明确从未支付普通股现金股息，以 FY2025 历史每股股息 0 配 2026-09-04 实际股价，CLI 为 `PASS/publishable`、`0%`。这不是未来股息预测 | `financial/production_zero_dividend/production_zero_dividend_summary.json` |
| DFCF 沪深两融 | 沪市 10 行截至 09-04，深市 9 行截至 09-03；共同数据截至 09-03，没有生成 09-04 两市合计 | `market/dfcf_live/dfcf_margin_audit.json` |
| HT 本地生产数据 | 12,237 个有效日线文件，9,443 个最新为 09-04；147 个财务 ZIP 检查通过；19 次白名单目录枚举，150,325 次 stat/lstat 监控，0 越界 | `market/ht_live_validation.json` |
| Lumentum 官方 IR → Q4 事件 API → HLS 字幕 CDN | 真实下载 14/14 段，总计 28 秒；源无 ENDLIST，因此退出 1、`playlist_complete=false`，正确保留来源缺口 | `captions/lite_live_final/captions_manifest.json` |
| NVIDIA 官方事件平台单份字幕 | API 与字幕真实 HTTP 200，70,601 字节 WebVTT 通过格式检查；这是单份字幕接口，不算 HLS 完整下载测试 | `captions/nvda_discovery/` |
| Apple 官方 HLS 协议样例 | 分段样例 100/100，600 秒，退出 0、完整；另一个 byte-range 样例按暂不支持的格式拒绝 | `captions/apple-bipbop-integration.json` |
| 三个 08-30 产业链生产结构化包 | 原包因重复证据字段漂移退出 2；仅在隔离副本迁移后 3/3 strict 通过；9 次单字段注入全部拒绝，原件 SHA 不变 | `industry/production-replay-manifest.json` |

Apple 样例属于远端协议测试；产业链属于真实历史数据回放；删日、改范围等属于异常注入。它们均与实时生产接口结果分别标记，不能互相替代。所有详细证据路径均相对于 `artifacts/skill_repair_20260906/`。

## 兼容性与保留的缺口

- 历史产业链原包共有 121 处摘要差异。新合同要求重复机器字段复制权威 check，摘要放报告正文；隔离迁移清单保留原摘要和对应权威值，未修改历史原件。
- 只有 `reported_affo`、带未知后缀等不能确定完整会计口径的旧财务输入，需要补充有来源支持的 `accounting_context`。调整口径 margin 需附 `measurement_definition`，不得仅靠相同标签假定定义一致。
- DFCF 余额仍为厂商数据，交易所请求为 0；本地 TDX 日历也属于厂商证据。日历缺失时回退日期并集并记录限制，日历覆盖外的双方同时缺日无法保证识别。
- HT 中原有 2 个空日线文件和 0 个分钟线文件按数据缺口保留；本轮没有补造或修改源文件。
- 字幕完整性只针对当前播放列表。滑动窗口不能变成完整电话会；byte range、加密、初始化片段等需要相容下载器，当前脚本明确拒绝。完整下载后仍需核对事件身份与全场时长。

## 回归与复核证据

- 财务全回归：70 项，`financial/full_financial_regression.log`。
- 两融、HT 与增量刷新兼容：20 项，`market/green_tests.log`。
- 产业链、字幕、技能库、安全边界与周更/看板消费者：68 项，`consumer-regression.json`、`consumer-regression.log`。
- Skill 结构校验：11/11，`quick_validate.json`；健康检查：`repo_health.log`。
- 独立复核：`industry/cross-review-final.json`。复核发现的字幕格式误成功和财务合法标签误阻断已再次经历红测、修复、绿测；15 份真实财报字幕未误拒。

遵循的主要规范：[RFC 8216](https://www.rfc-editor.org/rfc/rfc8216.html) 区分播放列表结束与客户端完整下载；[pandas 官方文档](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pct_change.html) 明确变化率比较前一行；[DOJ HHI 定义](https://www.justice.gov/atr/herfindahl-hirschman-index) 使用百分比份额的平方和。这些要求已落实到输入合同与回归测试。

## 备份前任务文件清理

按用户后续清理指令，删除 124 个本任务产生的缓存、空诊断流、重复字幕和已被最终结果替代的日志，共 414,753 字节，并移除 92 个空目录。删除项均未被 Git 跟踪，路径、链接边界及 SHA-256 已逐项核对；19 个重复件有同哈希保留件。最终字幕 manifest 引用的空正文保留。

原验收索引中的 263 份保留证据全部复核通过；47 个被清理的中间证据在索引中转入 `removed_evidence_files`，记录原因和重复件映射。历史运行清单仍保留当时的输出路径，已清理的空流和重复件可按清理清单解释，不代表来源丢失。详细记录见 `artifacts/skill_repair_20260906/cleanup_plan.json` 和 `cleanup_result.json`。
