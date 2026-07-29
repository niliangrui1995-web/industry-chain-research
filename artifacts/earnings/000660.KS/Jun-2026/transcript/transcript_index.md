# 电话会转写索引

- 当前季度官方英文回放：`current_call_audio_complete.m4a`，时长约 67 分 23 秒，SHA-256 `443680EEAB4AF8B5AE71A2DEF0C45DD68DF23148DCD53F1D94C96F00D7785E08`。
- 上一季度官方英文回放：`prior_call_audio.m4a`，时长约 74 分 32 秒，SHA-256 `2A34411C01057294B0347C3E61E42E8D353AEB001C40F5A787876CC94A0D5540`。
- 当前季度 `chunk_00`、`chunk_01` 使用 `small.en / CPU int8`；`chunk_02` 至 `chunk_06` 使用 `large-v3-turbo / CUDA int8`。
- 上一季度 `chunk_00` 至 `chunk_07` 使用 `small.en / CUDA int8`。
- 每个分段时间戳从零开始；全局时间戳等于分段时间戳加上对应偏移。

| 期间 | 分段 | 全局偏移 | 转写文件 |
|---|---:|---:|---|
| 2026Q2 | 00 | 00:00:00 | `current_asr/chunk_00/transcript_raw.txt` |
| 2026Q2 | 01 | 00:10:00 | `current_asr/chunk_01/transcript_raw.txt` |
| 2026Q2 | 02 | 00:20:00 | `current_asr/chunk_02/transcript_raw.txt` |
| 2026Q2 | 03 | 00:30:00 | `current_asr/chunk_03/transcript_raw.txt` |
| 2026Q2 | 04 | 00:40:00 | `current_asr/chunk_04/transcript_raw.txt` |
| 2026Q2 | 05 | 00:50:00 | `current_asr/chunk_05/transcript_raw.txt` |
| 2026Q2 | 06 | 01:00:00 | `current_asr/chunk_06/transcript_raw.txt` |
| 2026Q1 | 00 | 00:00:00 | `prior_asr/chunk_00/transcript_raw.txt` |
| 2026Q1 | 01 | 00:10:00 | `prior_asr/chunk_01/transcript_raw.txt` |
| 2026Q1 | 02 | 00:20:00 | `prior_asr/chunk_02/transcript_raw.txt` |
| 2026Q1 | 03 | 00:30:00 | `prior_asr/chunk_03/transcript_raw.txt` |
| 2026Q1 | 04 | 00:40:00 | `prior_asr/chunk_04/transcript_raw.txt` |
| 2026Q1 | 05 | 00:50:00 | `prior_asr/chunk_05/transcript_raw.txt` |
| 2026Q1 | 06 | 01:00:00 | `prior_asr/chunk_06/transcript_raw.txt` |
| 2026Q1 | 07 | 01:10:00 | `prior_asr/chunk_07/transcript_raw.txt` |

## 质量边界

转写覆盖两场完整官方回放，包括管理层陈述和 Q&A。英语段落整体可读，韩英交替处、姓名和少量产品缩写存在识别误差；所有关键财务数字以公司新闻稿和演示稿为准，关键管理层表述用官方回放时间戳和演示稿交叉核验。转写是本地派生材料，不升级为官方逐字稿。
