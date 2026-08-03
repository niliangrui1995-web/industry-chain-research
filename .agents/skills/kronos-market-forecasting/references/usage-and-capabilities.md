# Kronos-base 功能与使用参考

## 目录

1. 模型能做什么
2. 本地版本与文件
3. 输入与时间戳
4. 参数与输出
5. 命令和 Python API
6. 评估方法
7. 故障处理
8. 官方来源与许可

## 1. 模型能做什么

Kronos 把连续 OHLCV K 线先量化为分层离散 token，再由自回归 Transformer 生成未来 token，并反归一化为未来 K 线。`KronosPredictor` 自动完成字段补齐、标准化、截断、生成和反标准化。

| 能力 | 当前状态 | 边界 |
|---|---|---|
| 单序列零样本预测 | 本 Skill 已封装 | 输入历史 K 线，输出未来 OHLCV/amount |
| 多样本生成并平均 | 上游支持 | `sample_count` 增大显存和耗时；5GB 显存从 1 开始 |
| 批量序列预测 | 上游 `predict_batch` 支持 | 本 Skill CLI 暂不封装，序列长度需一致 |
| Tokenizer/Predictor 微调 | 项目已封装 A股两阶段训练 | 仅 D盘隔离训练环境；必须通过 PIT、样本外和成本准出门 |
| 回测 | 上游有演示代码 | 演示不是生产交易系统，必须另做样本外评估和成本建模 |

模型不读取财报、新闻、订单、估值、宏观变量或公司身份；它不能单独证明基本面、因果关系或投资价值。输出不是上涨概率，也不是确定目标价。

## 2. 本地版本与文件

本地固定版本：

| 组件 | Revision / commit | 关键文件 |
|---|---|---|
| Kronos source | `67b630e67f6a18c9e9be918d9b4337c960db1e9a` | `source/model/*.py` |
| `NeoQuasar/Kronos-base` | `2b554741eca47781b64468546e77fef3e85130e6` | `config.json`, `model.safetensors` |
| `NeoQuasar/Kronos-Tokenizer-base` | `0e0117387f39004a9016484a186a908917e22426` | `config.json`, `model.safetensors` |

权重 SHA256：

- Base：`abff193acab6db1a0368e9773e75799d11403b6d054ee6d5f0a11aeabc5f4b83`
- Tokenizer：`59d85f6af76a2c3b8240ea06cb21db4213b4eeca053f246b23e29cf832fc6bee`

Base 为 102.3M 参数，最大上下文为 512 根 K 线。两个运行权重合计约 405.4 MiB。环境使用 Python 3.12、PyTorch `2.7.1+cu118`；CUDA 11.8 构建用于兼容本机 GTX 1060 的 `sm_61`。

本项目分开路由两个环境：Base 零样本推理 `run_kronos_forecast.py` 使用 `.venv_kronos\Scripts\python.exe`；A股 `snapshot` 至 `pipeline` 的九个命令使用 `D:\vcp_hunter\产业链投研\_training\kronos_ashare\runtime\venvs\kronos-ashare\Scripts\python.exe`。不要用 Base 环境启动 A股数据、训练或评估命令。

需要重建环境时，使用项目脚本从官方 PyPI 与 PyTorch CU118 索引重建两个环境：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .agents\skills\kronos-market-forecasting\scripts\rebuild_kronos_envs.ps1
```

脚本先用 `requirements-lock-contract.json` 验证 input/lock SHA256、包数和两个哈希锁零重叠；公共依赖由 `requirements-training.lock` 管理，`requirements-torch-cu118.lock` 只含 CUDA 11.8 Torch 轮子并以 `--no-deps` 安装。重建结束前还会运行 `uv pip check`，以隔离 Python 验证安装包集合、版本和实际 D盘 runtime path，并在每个环境写入带 SHA256 sidecar 的 `kronos-package-manifest.json`。manifest 验证前失败才回滚；验证后的备份清理失败返回 `cleanup_pending`，保留新环境供使用和人工清理备份。

恢复源码与权重时使用上表固定 revision；不要只下载 Predictor 而漏掉 Tokenizer。先下载到新目录并通过脚本哈希检查，再替换当前运行目录，避免产生半更新状态。

```powershell
New-Item -ItemType Directory -Path _downloads\Kronos.new -Force
git clone --no-checkout https://github.com/shiyu-coder/Kronos.git _downloads\Kronos.new\source
git -C _downloads\Kronos.new\source checkout --detach 67b630e67f6a18c9e9be918d9b4337c960db1e9a
.venv_kronos\Scripts\huggingface-cli.exe download NeoQuasar/Kronos-base config.json model.safetensors README.md --revision 2b554741eca47781b64468546e77fef3e85130e6 --local-dir _downloads\Kronos.new\Kronos-base
.venv_kronos\Scripts\huggingface-cli.exe download NeoQuasar/Kronos-Tokenizer-base config.json model.safetensors README.md --revision 0e0117387f39004a9016484a186a908917e22426 --local-dir _downloads\Kronos.new\Kronos-Tokenizer-base
.venv_kronos\Scripts\python.exe .agents\skills\kronos-market-forecasting\scripts\run_kronos_forecast.py --runtime-root _downloads\Kronos.new --check --load-model
```

## 3. 输入与时间戳

CSV 至少包含：

```text
timestamps,open,high,low,close
```

可选字段：

```text
volume,amount
```

- 缺少 `volume` 时，上游以 0 填充 `volume` 和 `amount`。
- 有 `volume` 但缺少 `amount` 时，上游以 `volume * OHLC 行均价` 派生 `amount`。
- 统一频率、复权口径、时区和证券；不要在同一序列混合前复权/不复权、带时区/不带时区或不同交易时段。
- `lookback` 不得超过 512。更长历史不会扩大 Base 的有效上下文。
- `y_timestamp` 是模型时间特征的一部分。A 股/期货等市场应提供已核验的未来交易时点 CSV；`--freq B` 不识别中国节假日，`--freq 5min` 不识别午休和夜盘切换。

未来时间戳 CSV 只需一列：

```text
timestamps
2026-08-04 09:35:00+08:00
2026-08-04 09:40:00+08:00
```

## 4. 参数与输出

| 参数 | 默认 | 含义 |
|---|---:|---|
| `--lookback` | 400 | 使用末尾多少根历史 K 线，最大 512 |
| `--pred-len` | 必填 | 生成多少根未来 K 线 |
| `--temperature` | 1.0 | 采样温度；越高越分散 |
| `--top-k` | 0 | 0 表示不做 top-k 截断 |
| `--top-p` | 0.9 | nucleus sampling 阈值 |
| `--sample-count` | 1 | 并行生成并平均的样本数 |
| `--seed` | 42 | 随机种子；不同硬件不保证逐位一致 |
| `--device` | auto | 在本机优先可兼容的 CUDA，否则 CPU |

输出 CSV 固定为 `timestamps,open,high,low,close,volume,amount`。同名 `.metadata.json` 记录输入/输出哈希、checkpoint、参数、设备、时间戳来源、异常 K 线数量和警告。写出器用输出目录内的 `.kronos-locks` 操作系统锁、pending/backup 和提交标记处理并发与进程中断；下次运行会回滚未提交的半组文件，或核验已提交文件的大小和哈希后清理现场。锁文件会保留供复用，但 OS 锁会在进程退出后自动释放。

两个文件对不参与锁的读取者不是单一原子对象，因此只能在命令以退出码 0 结束后读取，并必须核对 metadata 的 `output_sha256` 与 CSV 实际 SHA256。不要删除 metadata 后再把预测当作可审计结果；看到 `recovery_required` 时保留 pending/backup/commit 现场并人工核查，不要强制清理。

## 5. 命令和 Python API

安装与完整加载检查：

```powershell
.venv_kronos\Scripts\python.exe .agents\skills\kronos-market-forecasting\scripts\run_kronos_forecast.py --check --load-model
```

本地 Python API：

```python
import os
import sys
from pathlib import Path

import pandas as pd

root = Path(r"D:\vcp_hunter\产业链投研")
os.environ["HF_HUB_OFFLINE"] = "1"
sys.path.insert(0, str(root / "_downloads" / "Kronos" / "source"))

from model import Kronos, KronosPredictor, KronosTokenizer

tokenizer = KronosTokenizer.from_pretrained(
    root / "_downloads" / "Kronos" / "Kronos-Tokenizer-base"
)
model = Kronos.from_pretrained(
    root / "_downloads" / "Kronos" / "Kronos-base"
)
tokenizer.eval()
model.eval()

predictor = KronosPredictor(model, tokenizer, device="cuda:0", max_context=512)
pred_df = predictor.predict(
    df=x_df,
    x_timestamp=x_timestamp,
    y_timestamp=y_timestamp,
    pred_len=len(y_timestamp),
    T=1.0,
    top_k=0,
    top_p=0.9,
    sample_count=1,
    verbose=True,
)
```

## 6. 评估方法

1. 按时间滚动切分训练前可见历史与未来持有区间，禁止随机打乱造成未来泄漏。
2. 每个 cutoff 只向模型提供 cutoff 之前的 K 线；未来真实值只用于事后评分。
3. 至少比较 last-value、历史漂移或简单移动平均基线。
4. 分别报告价格误差、方向命中、不同波动环境稳定性；若转为策略，再计点差、手续费、滑点、停牌和涨跌停。
5. 分开记录模型选择期与最终测试期；不要以同一测试集反复调参后仍称其为样本外。

## 7. 故障处理

- `missing_local_runtime`：检查 `_downloads\Kronos` 三个目录和 `.venv_kronos`；不要让 `from_pretrained` 自动联网补文件。
- `sm_61` 不在 `torch.cuda.get_arch_list()`：当前 wheel 不支持 GTX 1060；使用项目固定的 `torch==2.7.1+cu118` 或显式 `--device cpu`。
- CUDA OOM：先设 `--sample-count 1`、缩短 `--pred-len`，关闭占显存程序；仍失败则用 CPU。
- 时间戳报错：确保严格递增、无重复、`pred_len` 与未来时间戳行数完全一致，且第一条未来时点晚于历史末端。
- OHLC 校验失败：核对列名、数字格式、复权处理，以及 `high >= max(open, close)`、`low <= min(open, close)`。
- revision/hash 不一致：把它视为运行时漂移，先核对官方版本并同步更新 Skill、脚本和验证证据，不要跳过校验。

## 8. 官方来源与许可

- 代码与完整用法：[shiyu-coder/Kronos](https://github.com/shiyu-coder/Kronos)
- Base：[NeoQuasar/Kronos-base](https://huggingface.co/NeoQuasar/Kronos-base)
- Tokenizer：[NeoQuasar/Kronos-Tokenizer-base](https://huggingface.co/NeoQuasar/Kronos-Tokenizer-base)
- 论文：[arXiv:2508.02739](https://arxiv.org/abs/2508.02739)
- 下载接口：[Hugging Face Hub 0.33.1](https://huggingface.co/docs/huggingface_hub/v0.33.1/en/guides/download)

代码与两套权重均标注 MIT License。本地保留上游源码中的 `LICENSE`；若重新分发代码或模型的重要部分，保留版权与许可声明。模型及演示不构成投资建议。
