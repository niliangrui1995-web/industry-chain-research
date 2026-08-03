---
name: kronos-market-forecasting
description: Run and validate the project-local Kronos-base financial K-line model offline, including installation checks, OHLC(V/amount) input validation, future-timestamp handling, CPU/GPU inference, provenance capture, and out-of-sample evaluation. Use for Kronos、Kronos-base、本地 K 线模型、OHLCV 预测、模型推理、模型安装检查、GPU/CPU 兼容、预测脚本或 Kronos 回测. Treat every result as model_output, never as a future fact or standalone trading signal.
---

# Kronos Market Forecasting

把本技能作为本项目的 K 线模型伴侣。只处理 Kronos 本地安装、数据准备、推理和模型评估；不要替代公司、产业链、财报、估值或交易纪律研究。

## 固定本地合同

- 项目根：`D:\vcp_hunter\产业链投研`。
- Python：`.venv_kronos\Scripts\python.exe`。
- 上游源码：`_downloads\Kronos\source`。
- Predictor：`_downloads\Kronos\Kronos-base`。
- Tokenizer：`_downloads\Kronos\Kronos-Tokenizer-base`。
- 稳定入口：`scripts/run_kronos_forecast.py`。
- 固定 `max_context=512`；默认只读取尾部 `lookback` 根 K 线。

模型、Tokenizer 或源码缺失时，停止推理并报告 `missing_local_runtime`。不要在推理途中静默联网下载或切换 checkpoint。

## 执行流程

1. 需要了解字段、参数、能力、版本、许可或故障处理时，读取 [usage-and-capabilities.md](references/usage-and-capabilities.md)。
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

## 准出边界

- 始终标记 `evidence_class=model_output`。
- 把结果解释为“给定历史 K 线与未来时间特征下的一条条件生成路径”；它不是未来事实，不解释为确定价格、上涨概率、目标价、订单、基本面或因果证据。
- 不从单次样本、单张图或训练集内拟合得出可交易结论。需要评估时，使用严格滚动样本外窗口，并与 last-value、drift 等朴素基线比较。
- 不把预测直接写入公司真相文件、财务事实、watchlist、模拟交易或外部账户。相关写入仍需用户明确授权及相应项目 Skill。
- 若数据口径、未来时间戳、复权方式或回测切分不清，返回 `provisional` 或 `N/A`，说明证据缺口。

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
