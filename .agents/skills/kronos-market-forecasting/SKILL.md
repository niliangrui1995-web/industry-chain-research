---
name: kronos-market-forecasting
description: Run, validate, adapt, and evaluate the project-local Kronos-base financial K-line model offline, including A-share TDX snapshots, PIT data gates, LoRA/scorer training, checkpoint recovery, OHLC(V/amount) inference, provenance capture, and walk-forward evaluation. Use for Kronos、Kronos-base、本地 K 线模型、A股微调、LoRA、OHLCV 预测、模型安装检查、GPU/CPU 兼容、预测脚本或 Kronos 回测. Treat every result as model_output, never as a future fact or standalone trading signal.
---

# Kronos Market Forecasting

把本技能作为本项目的 K 线模型伴侣。只处理 Kronos 本地安装、A股数据快照、微调、推理和模型评估；不要替代公司、产业链、财报、估值或交易纪律研究。

## 固定本地合同

- 项目根：`D:\vcp_hunter\产业链投研`。
- Base 推理 Python：`.venv_kronos\Scripts\python.exe`。
- A股九命令 Python：`D:\vcp_hunter\产业链投研\_training\kronos_ashare\runtime\venvs\kronos-ashare\Scripts\python.exe`。
- 上游源码：`_downloads\Kronos\source`。
- Predictor：`_downloads\Kronos\Kronos-base`。
- Tokenizer：`_downloads\Kronos\Kronos-Tokenizer-base`。
- 稳定入口：`scripts/run_kronos_forecast.py`。
- A股入口：`scripts/run_kronos_a_share.py`。
- 训练根：`_training\kronos_ashare`，所有大文件、缓存、临时文件、数据集和 checkpoint 必须位于此目录。
- 固定 `max_context=512`；默认只读取尾部 `lookback` 根 K 线。

模型、Tokenizer 或源码缺失时，停止推理并报告 `missing_local_runtime`。不要在推理途中静默联网下载或切换 checkpoint。

## 执行流程

1. 需要了解字段、参数、能力、版本、许可或故障处理时，读取 [usage-and-capabilities.md](references/usage-and-capabilities.md)。
   A股快照、PIT门、两阶段训练和准出方法读取 [a-share-finetuning.md](references/a-share-finetuning.md)。
2. 首次使用、环境变化或报错后，先运行：

   ```powershell
   .venv_kronos\Scripts\python.exe .agents\skills\kronos-market-forecasting\scripts\run_kronos_forecast.py --check --load-model
   ```

3. 固定证券、市场、bar 频率、数据截止时点、复权口径和时区。若读取 `D:\HT`，附加使用 `ht-local-market-data`，保留其厂商数据边界。
4. 验证 `timestamps, open, high, low, close`；允许可选 `volume, amount`。拒绝重复/倒序时间、非数值、NaN/Inf、非正价格、负成交量及不合法 OHLC。
5. 明确提供未来时间戳文件，或显式提供 `--freq`。交易所日历、节假日、午休或停牌可能影响时间序列时，优先提供时间戳文件；不要把简单频率推算伪装成已核验交易日历。
6. 运行本地 CLI；5GB 显存默认保持 `sample_count=1`。CUDA 不兼容或显存不足时，明确改用 `--device cpu`，不要静默改变设备。
7. 检查输出无 NaN/Inf，并报告预测 K 线结构异常数。不要自动修正模型输出后仍称其为原始预测。
8. 只在命令以退出码 0 完成后消费 CSV 与同名 `.metadata.json`，并核对 metadata 中的 `output_sha256`；报告 checkpoint revision、输入哈希、数据截止时点、lookback、pred_len、采样参数、设备、日历假设和警告。

## A股微调流程

1. 先运行存储审计；训练进程的 `UV_CACHE_DIR`、`HF_HOME`、`TORCH_HOME`、`TEMP/TMP` 和 Qlib provider 不得落到 C 盘。迁移脚本不带 `-Apply` 时只审计，首次迁移先审计再执行；迁移和双环境重建命令见下文。
2. `snapshot` 只读复制 `D:\HT` 的 `.day`、`gbbq`、`base.dbf`，复制前后校验活动源哈希；训练不直接读取活动中的 TDX 目录。
3. `prepare` 要求90日历史、未来10日标签、11日 purge；原始成交价与因果复权模型价分栏。已抓公开原始响应需要归一化时，使用 `prepare --pit-normalization-manifest <reviewed.json>`；它固定官方>公开补充>TDX机械核验的优先级，无受哈希绑定的 `expected_keys` 不得声称 coverage 完整。正式数据还必须具备专用、官方且受哈希绑定的 `trading_calendar`，以及可由上一交易日原始收盘复算的逐日涨跌停上下限；缺历史 CSI300/CSI500 成分、ST、停复牌、日历或涨跌停状态时只能是 `local_provisional` 或 `blocked`。
4. 第一阶段冻结 Tokenizer/Base，只训练26个 `q_proj/v_proj` LoRA；第二阶段冻结 LoRA，只训练 `LayerNorm(832) -> Linear(832,1)` 横截面评分头。
5. 先跑 `pipeline --mode smoke`；通过1000步显存、NaN、checkpoint和因果验证合同后，才允许 `pipeline --mode full` 续训。验证时仅 dependency cross-attention 保持 causal mask，LoRA dropout 仍为 eval；禁止用普通 `model.eval()` 产生可见未来 token 的 CE。
6. `evaluate --split validation` 必须现场重算 checkpoint CE、scorer 预测、LoRA 摘要、zero-shot、head-only、朴素基线、Alpha158+LightGBM 和真实成交 companion；旧 CSV、metadata 或 checkpoint 自报指标不能单独准出。`development_test` 与 `locked_retrospective` 只写分段报告，绝不签发或改写 gate。未同时通过数据门、RankIC、bootstrap和成本压力门时，`score-as-of` 输出 `N/A`。
7. 每日评分先在15:00收盘后用 `snapshot --inference-as-of <交易日零点+08:00> --inference-pit-root <production_ready PIT>` 固化独立输入；`score-as-of` 必须显式传该快照和其中受哈希绑定的官方未来交易日原始响应，禁止读取训练快照或活动 `D:\HT`。
8. 前瞻观察期内允许内部写入不可变账本，但对话与正式文件仍返回 `N/A`。Gate、receipt、active head、lineage 和当前 forward registry 任一断链、回滚或漂移都必须阻断。

训练依赖由互不重叠的 `requirements-training.lock` 与 `requirements-torch-cu118.lock` 固定并要求哈希：前者从官方 PyPI 提供全部运行依赖，后者只含 `torch==2.7.1+cu118`，从官方 PyTorch CU118 索引以 `--no-deps` 安装。`requirements-lock-contract.json` 绑定两个 input/lock 的 SHA256。重建脚本先做一致性预检，再运行 `uv pip check`、`-I -B` 精确包清单、实际 D盘 runtime path 和清单 SHA256 验证；验证前失败回滚当前环境，验证后的备份清理失败只返回 `cleanup_pending` 并保留已验证环境。`kronos_a_share_public_data.py` 负责公开原始响应的原子快照，`kronos_a_share_baseline.py` 负责项目内 Qlib Provider、Alpha158+LightGBM 和评估 companion。它们的工件必须位于训练根并被 SHA256 provenance 绑定，不能用手工 CSV 绕过。

## 准出边界

- 始终标记 `evidence_class=model_output`。
- 把结果解释为“给定历史 K 线与未来时间特征下的一条条件生成路径”；它不是未来事实，不解释为确定价格、上涨概率、目标价、订单、基本面或因果证据。
- 不从单次样本、单张图或训练集内拟合得出可交易结论。需要评估时，使用严格滚动样本外窗口，并与 last-value、drift 等朴素基线比较。
- 不把预测直接写入公司真相文件、财务事实、watchlist、模拟交易或外部账户。相关写入仍需用户明确授权及相应项目 Skill。
- 若数据口径、未来时间戳、复权方式或回测切分不清，返回 `provisional` 或 `N/A`，说明证据缺口。
- `production_ready` 只表示数据合同完整，不表示模型有效；`gate_status=passed` 也只准出模型工件，不构成交易建议。
- 2025-07-01 至 2026-07-31 已用于诊断，只称锁定回溯；真正前瞻观察自 2026-08-03 起累计，期间不得回看调参。
- `run_kronos_forecast.py --adapter-dir` 遇到未准出 gate 时默认不运行 Predictor、不写数值 CSV并返回退出码2；只有显式 `--allow-research-output` 才能生成强制以 `.research-only.csv` 结尾的研究文件，顶层仍为 `unverified / N/A`。

## 常用命令

使用精确未来时间戳：

```powershell
.venv_kronos\Scripts\python.exe .agents\skills\kronos-market-forecasting\scripts\run_kronos_forecast.py --input data\history.csv --future-timestamps data\future_timestamps.csv --pred-len 20 --output artifacts\kronos\forecast.csv
```

对连续市场按固定 5 分钟频率推算时间：

```powershell
.venv_kronos\Scripts\python.exe .agents\skills\kronos-market-forecasting\scripts\run_kronos_forecast.py --input data\history.csv --freq 5min --pred-len 12 --output artifacts\kronos\forecast.csv
```

CPU 诊断：

```powershell
.venv_kronos\Scripts\python.exe .agents\skills\kronos-market-forecasting\scripts\run_kronos_forecast.py --input data\history.csv --freq B --pred-len 5 --device cpu --output artifacts\kronos\forecast_cpu.csv
```

A股预检与工程冒烟：

```powershell
$AsharePython = 'D:\vcp_hunter\产业链投研\_training\kronos_ashare\runtime\venvs\kronos-ashare\Scripts\python.exe'
& $AsharePython .agents\skills\kronos-market-forecasting\scripts\run_kronos_a_share.py check --config .agents\skills\kronos-market-forecasting\configs\a_share_daily_v1.yaml --load-model
& $AsharePython .agents\skills\kronos-market-forecasting\scripts\run_kronos_a_share.py pipeline --config .agents\skills\kronos-market-forecasting\configs\a_share_daily_v1.yaml --mode smoke
```

每日独立快照与评分（`future-timestamps` 必须是该快照 `pit_files` 中的官方 `raw_response`）：

```powershell
& $AsharePython .agents\skills\kronos-market-forecasting\scripts\run_kronos_a_share.py snapshot --config .agents\skills\kronos-market-forecasting\configs\a_share_daily_v1.yaml --inference-as-of '2026-08-03T00:00:00+08:00' --inference-pit-root 'D:\vcp_hunter\产业链投研\_training\kronos_ashare\data\normalized\pit\daily-20260803'
& $AsharePython .agents\skills\kronos-market-forecasting\scripts\run_kronos_a_share.py score-as-of --config .agents\skills\kronos-market-forecasting\configs\a_share_daily_v1.yaml --as-of '2026-08-03T00:00:00+08:00' --inference-snapshot '<inference_manifest.json>' --future-timestamps '<snapshot内官方交易日历.csv>' --symbols 300620.SZ 600330.SH 002415.SZ 603259.SH
```

`snapshot`、`prepare`、`check`、`train-adapter`、`train-scorer`、`evaluate`、`score-as-of`、`inspect-checkpoint`、`pipeline` 全部使用上述 D 盘隔离训练环境；Base 零样本推理 `run_kronos_forecast.py` 继续使用项目 `.venv_kronos`。

存储审计、首次迁移和锁定环境重建：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .agents\skills\kronos-market-forecasting\scripts\migrate_kronos_storage.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .agents\skills\kronos-market-forecasting\scripts\migrate_kronos_storage.ps1 -Apply
powershell -NoProfile -ExecutionPolicy Bypass -File .agents\skills\kronos-market-forecasting\scripts\rebuild_kronos_envs.ps1
```

`-Apply` 会移动共享 `uv/pip/Python` 缓存并建立固定 Junction，只有首次迁移或明确重建时使用；日常只运行第一条审计命令。项目路径若移动，必须先迁回或重建这些 Junction。
