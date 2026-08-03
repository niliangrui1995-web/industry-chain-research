# Kronos-base A股微调与准出参考

## 固定边界

- 项目根固定为 `D:\vcp_hunter\产业链投研`。
- 大文件根固定为 `_training\kronos_ashare`；源码、默认配置与测试仍由 Git 管理。
- `_downloads\Kronos\source`、Base 和 Tokenizer 只读，运行前继续核验固定 revision 与 SHA256。
- `D:\HT` 是活动中的厂商行情源。数据构建只读它，训练只读项目内不可变快照。
- Hugging Face 凭据不迁入项目；训练缓存与凭据路径分离。

## 目录

```text
_training\kronos_ashare\
  runtime\
    uv-cache\ uv-python\ pip-cache\ venvs\
    huggingface\ torch\ tmp\
  data\
    raw\ normalized\ datasets\ tokens\ qlib\
  runs\<run_id>\
    checkpoints\ logs\ metrics\ predictions\
  registry\
```

每个入口都先 `resolve()` 路径，再验证写入目标属于训练根。`D:\HT`、C盘、`~\.qlib`、模型权重目录和项目外目录均不是合法写入目标。

## 存储迁移与环境重建

```powershell
# 只读审计；可重复运行
powershell -NoProfile -ExecutionPolicy Bypass -File .agents\skills\kronos-market-forecasting\scripts\migrate_kronos_storage.ps1

# 仅首次迁移时执行：复制、全量 SHA256、C盘备份、Junction、功能验证、删除备份
powershell -NoProfile -ExecutionPolicy Bypass -File .agents\skills\kronos-market-forecasting\scripts\migrate_kronos_storage.ps1 -Apply

# 用锁定依赖重建项目推理环境和隔离训练环境
powershell -NoProfile -ExecutionPolicy Bypass -File .agents\skills\kronos-market-forecasting\scripts\rebuild_kronos_envs.ps1
```

重建脚本固定使用两个互不重叠的锁：`requirements-training.lock` 从官方 PyPI 提供全部运行依赖，`requirements-torch-cu118.lock` 只含 `torch==2.7.1+cu118`。两者均以 `--require-hashes` 安装，Torch 轮子从官方 PyTorch CU118 索引以 `--no-deps` 安装，避免第二个索引重新解析或降级公共依赖。`requirements-lock-contract.json` 同时绑定两个 input、两个 lock、包数和官方索引；任一文件单独变化都会在移动环境前失败。安装后执行 `uv pip check`，以 `-I -B` 核对锁定包集合与版本完全一致，并实际观测 `sys.prefix`、`sys.base_prefix`、临时目录及 UV/PIP/HF/Torch 缓存路径。每个环境最后生成 `kronos-package-manifest.json` 和对应 SHA256 sidecar；manifest 验证是提交点，此前失败回滚，提交后的旧备份清理失败返回 `cleanup_pending` 和退出码2，不得删除已验证的新环境或恢复残缺备份。

Base 零样本推理固定使用 `.venv_kronos\Scripts\python.exe`；下面九个 A股工程命令固定使用 `D:\vcp_hunter\产业链投研\_training\kronos_ashare\runtime\venvs\kronos-ashare\Scripts\python.exe`。验收时同时核对两者的 `sys.base_prefix`、Torch 版本、包清单和缓存路径。Hugging Face 凭据、`uv\tools`、`C:\Python314`、普通系统临时文件及 `D:\AI_Cache\huggingface` 不在迁移范围。

## 数据证据和点时门

数据优先级为交易所/中证指数/CNINFO原始材料、公开逐日状态数据、TDX厂商数据。每个外部文件保存 URL、抓取时点、有效时点、原始 SHA256 和字段映射。公开源冲突时不投票，相关证券日期退出可交易样本。

PIT normalization v2 把“模型样本期”与“证据回看期”固定分开：

```text
model_coverage_start = 2018-01-02
model_coverage_end = 2026-07-31
evidence_lookback_start = 2017-12-29
```

`evidence_lookback_start` 是官方交易日历中 `model_coverage_start` 的前一开放日，只用于首日涨跌停和前收证据，不得生成覆盖期外样本。确定性处理链是：

```text
官方原始响应
→ 版本化 allowlist 解析器
→ canonical CSV
→ Schema/键空间/来源冲突审计
→ normalized PIT
```

原始工件可为 `csv|json|html|pdf`。解析产物不得冒充官方原文；任何人工修正只能通过 `kronos-a-share-reviewed-overlay-v1` 进入，并绑定原文 SHA256、解析产物 SHA256、`extractor_id/version/config_sha256`、原始行号、修正原因、审核人与时点。

TDX 快照中的 `bars_raw` 保存原始成交 OHLCVA，不做今天口径的前复权。PIT 版本根严格使用七张业务表和一张 coverage 表；CSV、Parquet 和 PQ 三种后缀可选其一，同表不得同时出现多个后缀：

- `security_master`：`ticker/exchange/board/security_type/list_date/delist_date`，保存上市、退市、重新上市及证券类型有效区间。
- `st_status`：`ticker/effective_from/effective_to/is_st`，区间必须无重叠且覆盖正式样本。
- `suspensions`：`ticker/trade_date/is_suspended`，正式样本必须逐证券逐日有明确状态。
- `price_limits`：`ticker/trade_date/up_limit/down_limit/rule_version/no_limit_reason/previous_trade_date/previous_close_raw`。正式准出按上一交易日原始收盘、交易所、板块、ST和上市状态，用 `Decimal(ROUND_HALF_UP)` 到0.01元现场复算并逐字段比对。
- `index_membership`：`index_code/ticker/effective_from/effective_to`，保存点时 CSI300/CSI500 成分。
- `corporate_actions`：`ticker/announcement_date/ex_date/cash_div/bonus_ratio/rights_ratio/rights_price`；`gbbq` 缺公告时点时不得作为实施日前特征。
- `trading_calendar`：`trade_date/is_open`，可选 `benchmark_ticker`；必须由 `official_primary` 原始响应产生，并在 provenance 中固定 `artifact_role=trading_calendar`、`artifact_schema_version=kronos-a-share-trading-calendar-v1`。用于未来时间戳的同一原始响应必须精确为单列 `timestamps`。
- `coverage`：逐表绑定实际覆盖期、派生文件和原始来源；它是正式准出的证据表，不是自行声明完整性的开关。

v2 不接受 manifest 自定义键空间表达式。`coverage_key_contract` 由固定代码决定：`security_master`、`st_status`、`suspensions`、`price_limits` 为 `derived`，分别按历史成分并集、成员有效期内连续状态和 `active_membership × open_calendar` 派生；`index_membership`、`corporate_actions`、`trading_calendar` 为 `source_bound`，必须由官方锚点/全部变更事件、CNINFO完整分页回执和官方开放日集合证明。CSI300/CSI500 成员区间不得越过上市区间；ST区间不得缺口或重叠；停牌、涨跌停的成员交易日缺失数必须为0。

配置使用严格、不可扩展的 `public_pit` Schema：

```yaml
public_pit:
  version_root: null
  security_master: null
  st_status: null
  suspensions: null
  price_limits: null
  index_membership: null
  corporate_actions: null
  trading_calendar: null
  coverage: null
```

全部为 `null` 时使用训练根下的 `data\normalized\pit`，缺表只会得到 `local_provisional`。显式配置任一单表路径时必须同时配置绝对 `version_root`；所有单表必须使用上述规范文件名、直接位于同一版本根且处于 `_training\kronos_ashare\data` 内。`securities`、`trade_status` 等旧字段或任何未知字段都会在读取配置时 fail closed。未显式填写的表仍按规范文件名在版本根发现，缺失时不得升级为 `production_ready`。

`coverage` 基础字段为 `dataset/coverage_start/coverage_end/is_complete`。若要证明正式完整性，每个 complete 行还必须包含：

```text
binding_schema,file_sha256,schema_sha256,row_count,file_bytes,
source_manifest,source_manifest_sha256
```

其中 `binding_schema` 固定为 `kronos-a-share-pit-coverage-v1`；派生表的实际 SHA256、逻辑 Schema、行数和字节数必须逐项相等。旧四字段 coverage 只能是 `local_provisional`；部分填写绑定字段或绑定漂移属于合同错误。

`source_manifest` 必须是相对 PIT 版本根的 JSON 路径，Schema 固定为 `kronos-a-share-pit-provenance-v1`，并与 coverage 中的 manifest SHA256 一致。manifest 顶层绑定 `dataset/coverage_start/coverage_end/sources`；每个 source 至少保存：

```text
source_id,source_class,url,retrieved_at,valid_from,valid_to,path,sha256
```

可选 `bytes` 也会参与核验。`url` 仅允许 HTTPS，`retrieved_at` 必须带时区，`path` 必须指向版本根内独立原始响应，不能指向派生表或 manifest 自身；多个 source 的有效区间合并后必须无缺口覆盖声明期。日历来源还必须带固定的 `artifact_role/artifact_schema_version`，并来自上交所、深交所、北交所或中证指数官方域名。绝对路径、`..` 越界、原始响应或 manifest 哈希漂移均阻断准出。

模型价格和交易价格严格分栏。`trade_price_raw` 始终用于成交、涨跌停和回测；`model_price_adjusted` 只用于 Tokenizer、未来路径和模型标签。复权必须按每个样本 `origin_date` 重建，只使用当时已公告信息；需要尚未公告公司行动的窗口直接排除，`future_action_use_count` 必须为0。窗口在 cutoff 处缩放回原始收盘量级。

`data_quality_report.json` 只能返回：

- `production_ready`：正式字段对纳入样本完整，抽样官方回核通过。
- `local_provisional`：本地工程样本可生成，但至少一个 PIT 正式字段缺失。
- `blocked`：快照、窗口、日期、公司行动或字段合同无效。

只有 `production_ready` 可以进入正式模型比较；另外两个状态只允许工程冒烟。

最终正式数据不能只看总状态，必须同时满足：

```text
data_status=production_ready
sample_trade_state_checked=true
survivorship_bias_audit.verified=true
model_price_adjusted=true
future_action_use_count=0
future_action_audit_verified=true
```

v2 对 manifest 未知字段、不受支持的解析器及实际工件哈希/行数漂移全部 fail closed。CSI300 每个开放日必须恰为300只，CSI500 必须恰为500只。

公开数据原始层由 `scripts\kronos_a_share_public_data.py` 提供三个受控函数：`snapshot_url_manifest()` 保存显式 HTTPS 官方/公开响应、最终 URL、抓取时点、工件身份和 SHA256；`fetch_baostock_trade_status_shards()` 分证券保存 `tradestatus/isST` shard 及 manifest；`publish_normalized_pit_bundle()` 把已抓原始响应发布为七张业务表、`coverage`、原始副本、独立 extracted CSV、reviewed overlay 和逐表 provenance。归一化优先级固定为 `official_primary > public_secondary > tdx_mechanical`；TDX 只能是 `mechanical_cross_check`，不得供值。同等级异值、官方缺口或 TDX 核验冲突直接排除对应证券日期，不投票、不猜测。

v2 manifest 顶层严格使用 `schema_version/model_coverage_start/model_coverage_end/evidence_lookback_start/source_priority/datasets`。每张表固定 `coverage_key_contract/sources/expected_keys`；`derived` 合同的 `expected_keys` 必须为 `null`，由固定代码派生完整键空间；`source_bound` 合同必须提供受官方原文哈希绑定的 `expected_keys`。两者都不接受可编程表达式。每个 source 另外绑定：

```text
format=csv|json|html|pdf
extractor_id,extractor_version,extractor_config,extractor_config_sha256
extracted_sha256,extracted_row_count,row_audit_status=passed
row_audit={schema_version,path,sha256,bytes,row_count,source_sha256,
           extracted_sha256,audit_status,audited_at,auditor}
```

`row_audit` 不是标量声明：独立 CSV 必须逐行给出连续 `source_row_number`、原始定位、canonical 行哈希和审核状态，publisher 与 consumer 都会从原文重放并核对。`index_membership` 还必须提供 CSI 期初锚点及全部调样事件的链式 `completeness_receipt`；`corporate_actions` 必须提供 CNINFO 完整分页 receipt，并从每页原始 JSON 重放 `totalRecordNum/totalpages/pageNum`、页内行数和键哈希。缺锚点、断链、缺末页或官方分页元数据缺失时一律不能正式准出。

allowlist 只含 `csv-table-v1`、`json-records-v1`、`html-table-v1`、`pdf-table-v1`，当前 `extractor_version` 均为1。原文发布到 `raw/<dataset>/`，解析结果发布到 `extracted/<dataset>/<source_id>.csv`，逐行审计发布到 `row_audits/<dataset>/<source_id>.csv`，完整性回执发布到 `receipts/`，overlay 发布到 `overlays/<dataset>/<source_id>.csv`；provenance 同时绑定 raw/extracted/audit/receipt/overlay/派生表哈希。overlay CSV 除规范列外必须含 `source_row_number,correction_reason`，且 `review_status=approved`。任一原文、解析器配置/版本、解析结果、审计、回执或 overlay 哈希漂移都阻断。

`kronos-a-share-pit-normalization-v1` 仅保留旧数据回放兼容，无论 coverage 自报如何，`formal_release_allowed=false` 且最高只能 `local_provisional`。正式归一化示例为 `configs\pit_normalization_v2.example.json`。先将占位路径、原文哈希、解析器配置和键空间绑定替换为已审核合同，再继续使用原 `prepare` 入口：

```powershell
$AsharePython = 'D:\vcp_hunter\产业链投研\_training\kronos_ashare\runtime\venvs\kronos-ashare\Scripts\python.exe'
& $AsharePython .agents\skills\kronos-market-forecasting\scripts\run_kronos_a_share.py prepare --config .agents\skills\kronos-market-forecasting\configs\a_share_daily_v1.yaml --pit-root 'D:\vcp_hunter\产业链投研\_training\kronos_ashare\data\normalized\pit\pit-v2' --pit-normalization-manifest .agents\skills\kronos-market-forecasting\configs\pit_normalization_v2.reviewed.json
```

三个流程均整批 staging 后原子发布，任何缺失、重定向越域、Schema 或哈希漂移都拒绝复用。它们不会自动补造历史指数成分、公司行动公告时点、证券日状态或交易规则。

项目内基线由 `scripts\kronos_a_share_baseline.py` 的 `build_project_qlib_provider()`、`run_alpha158_lightgbm()` 和 `build_evaluation_companion()` 构建。Provider 只读取项目快照，不下载 Qlib 社区数据包；OHLC/VWAP与动量/反转使用只含当时已知公司行动的因果复权价，标签仍用原始价与总回报。成交 companion 使用次日原始可成交价、停牌/涨跌停、持有期公司行动因子和按有效期版本化的卖方印花税。正式 validation 每次从绑定源重建 companion，任意 `--input` 只能指向 canonical 路径，重哈希旧 CSV 不能改变准出指标。

## 固定切分

| split | 起止 |
|---|---|
| train | 2018-01-02—2022-12-30 |
| validation | 2023-01-03—2024-06-28 |
| development_test | 2024-07-01—2025-06-30 |
| locked_retrospective | 2025-07-01—2026-07-31 |

输入90日，目标未来10日，边界 purge/embargo 11个交易日。目标不得跨 split。锁定回溯已被人工诊断触及，不再称为 blind；真正前瞻从 2026-08-03 起至少60个、推荐120个交易日。

正式训练额外执行反向幸存者审计：每个点时 CSI300/CSI500 成分在每个交易日都必须有 `.day` 记录，缺记录只能由同日 PIT `suspensions.is_suspended=true` 解释；缺整只证券、静态现存股票池替代历史成分或事后补齐都会阻断 `production_ready`。deterministic smoke sampler 不得按 ticker 排序截头；`local_provisional` 只能按市场、板块、日期分层抽取工程样本，不报告质量指标。`production_ready` 才能按历史 CSI300/CSI500 成分生成质量样本。

## 两阶段训练

第一阶段只训练26个 LoRA 目标：12层 self-attention 的 `q_proj/v_proj`，以及 dependency cross-attention 的 `q_proj/v_proj`。固定 `r=8, alpha=16, dropout=0.05`，应有346,112个参数。损失只覆盖 token 序列中未来10根位置。已公告且在目标窗内生效的公司行动只前复权除权日及其后的目标价格；不得用未来除权日前收盘价反向改写90日历史 token。尚未公告的目标窗事件直接排除。

第二阶段冻结 Base、Tokenizer 和 LoRA，取90日历史最后一位 hidden state，训练 `LayerNorm(832) -> Linear(832,1)` 的2,497参数评分头。标签是未来10日相对CSI800的超额对数收益，损失为 SmoothL1 与只在同日计算的 RankNet。

默认 Windows 单进程、FP32、`num_workers=0`。Adapter 为 `batch=16`、累积2。工程 smoke 最多400步，`checkpoint_interval=validation_interval=50`，早停 `patience=3`；full 最多10000步，两个 interval 均为1000，早停同为3。两个 interval 不等直接拒绝配置。数据非 `production_ready` 时，`pipeline --mode smoke` 只验证显存、NaN、因果损失、checkpoint 和恢复，不运行 scorer，不生成可解读 RankIC 或 formal gate。

验证固定为 `causal-dependency-cross-attention-v1`：dependency cross-attention 在验证期继续使用因果 mask，而 LoRA dropout 关闭。Checkpoint 使用临时目录、完整文件哈希、`COMMITTED` 和原子 pointer；配置、基础模型、Tokenizer、数据 manifest、LR 或 seed 漂移时必须新建 run，不得混合恢复。`--learning-rate` 和 `--seed` 只能与 `--engineering-smoke` 同用，并写入 resolved config、run_id、checkpoint binding 和哈希。

`best` 只能指向拥有现场因果验证 CE 的 checkpoint，训练最后一步不会因为正常完成而自动成为 best。若没有验证点相对 zero-shot 改善至少1%，`adapter_summary.json` 必须记录 `zero_shot_fallback=true` 并禁止发布 adapter；摘要同时保存 `validation_history`、`best_step`、`selection_reason`、`train_validation_gap`。

### Adapter 诊断矩阵

按顺序执行，任一步失败就停止后续阶段：

1. step0、step200 各重复加载3次，CE 极差必须 `<=1e-5`；选择器必须稳定选回 step200 附近，不得选退化末端。
2. 固定数据与 seed100，依次运行 LR `{1e-5,3e-5,1e-4}`，各最多400步、每50步验证；入围要求 best CE `<=2.637683`，且相邻两个验证点都不劣于 zero-shot。
3. 对入围最佳 LR 运行 seeds `{100,101,102}`；生产 checkpoint 固定 seed100，不从种子中择优。三次都须优于 zero-shot，平均改善至少1%，任一次不得恶化超过1%。LR 并列且 CE 差 `<=1e-4` 时选更低 LR。
4. 数据达到 `production_ready` 后，至少用512条真实 PIT CSI800 分层样本复核；全北交所旧 smoke 只保留为负面对照。只有 adapter 通过后才训练 scorer。

## 评估和准出

至少比较 last-value、漂移、动量/反转、zero-shot Kronos 路径、Base+head、LoRA+head 与项目内 Qlib Alpha158+LightGBM。不得直接采用 Qlib 示例中的固定 `limit_threshold=0.095`，A股交易规则必须逐日版本化。正式 scorer 的每个日期必须 `eligible_count >= 100` 且覆盖当日有效成分至少95%；RankIC 只能按日计算后取均值。scorer 和 LightGBM 均固定运行 seeds `100..119` 并报告均值/标准差，不得择优种子；生产 scorer checkpoint 固定使用 seed100。

正式 `validation` 在当前 token cache 上现场重算 zero-shot/adapted CE 和 scorer 预测，逐张量核对 scorer 与声明 adapter 的 canonical LoRA digest，并从绑定数据重建所有基线和成交列；checkpoint extra、旧 predictions、companion 及其可改写 metadata 只作审计，不能代替重算。`development_test` 只在配置冻结后运行一次；`locked_retrospective` 只审计、不调参。两者只生成各自受控报告和分段工件，不创建、替换或回滚 gate/head。

全部满足才 `gate_status=passed`：

- 数据为 `production_ready`。
- Adapter 验证 Token CE 相对 zero-shot 改善至少1%。
- 验证日均 RankIC 至少0.03，且相对 zero-shot/head-only 至少提升0.005。
- 正 RankIC 季度超过半数。
- 相对最强基线的月度 block bootstrap 95%下界大于0。
- 35 bp 往返成本后收益为正，70 bp压力成本后不为负。

失败工件保留用于诊断，但输出固定为 `gate_status=blocked`、`output_type=N/A`、`evidence_class=model_output`。通过也只能称 `evidence_class=model_output`。

### 每日前瞻与防回滚

- 日频 inference snapshot 与训练 snapshot 分离；只能在对应交易日15:00收盘后生成，`as_of` 固定为带 `Asia/Shanghai` 时区的交易日零点。盘中时间、事后补建、同日择时替换、活动 `D:\HT` 直读都 fail closed。
- 每只成分复制91根 `.day`：90根模型历史加1根公司行动复权前驱；七张 PIT 表、provenance 和原始响应逐文件进入 `input_sha256`。
- `future-timestamps` 可以含全年日历，但评分只取 `as_of` 后前10个严格递增、非周末、零时分秒的日期；该 CSV 必须是 inference manifest 中哈希匹配的 `raw_response`，不能传项目外手工文件。
- 研究 gate 可在显式评分时把完整 CSI800 横截面写入前瞻账本，但用户可见结果仍为 `N/A`。每个批次绑定 inference input、adapter/scorer、gate sequence、真实 receipt、10个未来交易日、全量横截面和双重内容哈希；同一交易日只允许一个批次。
- 第10个目标交易日结束后的下一本地日期才记为一个成熟观察日。至少60日、推荐120日；新增批次改变 `registry_root_sha256`，删改、重排、假 receipt 或分钟时间戳都会阻断。
- 每次 `evaluate` 写入单调 `gate_sequence`、不可变 receipt、哈希链 `gate-lineage` 和唯一 `gate-head.json`。正式评分重新检查 active head 与当前 forward registry；历史 passed gate 单文件回滚、账本删除或 receipt 断链不能恢复授权。
- Base `--adapter-dir` 默认仅接受完整 passed 链。blocked/unverified 时不调用 Predictor、不写正式 CSV并返回码2；显式 `--allow-research-output` 只允许 `.research-only.csv`，metadata 固定 `status=unverified/output_type=N/A/publishable=false`。

## 公开接口

```powershell
$AsharePython = 'D:\vcp_hunter\产业链投研\_training\kronos_ashare\runtime\venvs\kronos-ashare\Scripts\python.exe'
$AshareCli = 'D:\vcp_hunter\产业链投研\.agents\skills\kronos-market-forecasting\scripts\run_kronos_a_share.py'
& $AsharePython $AshareCli snapshot --config .agents\skills\kronos-market-forecasting\configs\a_share_daily_v1.yaml
& $AsharePython $AshareCli prepare --config .agents\skills\kronos-market-forecasting\configs\a_share_daily_v1.yaml
& $AsharePython $AshareCli check --config .agents\skills\kronos-market-forecasting\configs\a_share_daily_v1.yaml --load-model
& $AsharePython $AshareCli train-adapter --config .agents\skills\kronos-market-forecasting\configs\a_share_daily_v1.yaml --resume auto --engineering-smoke --learning-rate 0.00003 --seed 100 --stop-after 400
& $AsharePython $AshareCli train-scorer --config .agents\skills\kronos-market-forecasting\configs\a_share_daily_v1.yaml --adapter best
& $AsharePython $AshareCli evaluate --config .agents\skills\kronos-market-forecasting\configs\a_share_daily_v1.yaml --checkpoint best --split validation
& $AsharePython $AshareCli score-as-of --config .agents\skills\kronos-market-forecasting\configs\a_share_daily_v1.yaml --as-of '2026-08-03T00:00:00+08:00' --inference-snapshot '<inference_manifest.json>' --future-timestamps '<snapshot内官方交易日历.csv>' --symbols 300620.SZ 600330.SH 002415.SZ 603259.SH
& $AsharePython $AshareCli inspect-checkpoint --config .agents\skills\kronos-market-forecasting\configs\a_share_daily_v1.yaml --checkpoint best
& $AsharePython $AshareCli pipeline --config .agents\skills\kronos-market-forecasting\configs\a_share_daily_v1.yaml --mode smoke
```

## 官方方法依据

- Kronos 源码与微调示例：<https://github.com/shiyu-coder/Kronos>
- Qlib PIT：<https://qlib.readthedocs.io/en/stable/advanced/PIT.html>
- Qlib RollingGen：<https://qlib.readthedocs.io/en/latest/reference/api.html#qlib.workflow.task.gen.RollingGen>
- Qlib Alpha158/LightGBM：<https://github.com/microsoft/qlib/tree/main/examples/benchmarks/LightGBM>
- PyTorch checkpoint：<https://docs.pytorch.org/docs/stable/checkpoint.html>
- 上交所交易规则：<https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/c/c_20260424_10816492.shtml>
- 深交所交易规则：<https://www.szse.cn/lawrules/rule/trade/current/t20260424_620190.html>
- 北交所交易规则：<https://www.bse.cn/jygl_list/200028217.html>
- 证券交易印花税公告：<https://fgk.chinatax.gov.cn/zcfgk/c102416/c5211343/content.html>
