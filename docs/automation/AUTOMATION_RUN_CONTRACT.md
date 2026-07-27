# 自动化运行版本合同

`prompt_contract_version=2026-07-27.1`

本合同适用于调用本项目 `.agents/skills/` 的自动化。稳定研究流程只维护在项目 Skill、引用文件和确定性脚本中；自动化 prompt 只声明本轮范围、输入、写入边界、失败策略与输出合同。

## 启动预检

每轮开始、任何领域采集或业务写入之前，按实际使用的 Skill 重复传入 `--skill`：

```powershell
python scripts/automation_run_metadata.py --repo-root "D:\vcp_hunter\产业链投研" --skill <skill-name> --pretty
```

命令输出中的以下字段必须原样写入该任务的 `run_status.md`、本期报告或等价的持久化运行状态；即使本轮无新增而提前结束也不能省略：

- `skill_revision`
- `prompt_contract_version`
- `skill_content_sha256`
- `skill_tree_status`
- `skills`

`skill_revision` 的稳定格式为 `git:<full_sha>`。若 `.agents/skills` 存在未提交改动，则为 `git:<full_sha>+dirty:<content_digest_prefix>`，同时保留完整 `skill_content_sha256`，避免把浮动工作树误报成固定版本。

若命令返回非零、`status=blocked`、Skill 入口缺失或版本字段无法解析，本轮必须以 `blocked/precheck_failed` 结束；只允许在既定运行状态文件中记录失败，不得继续领域采集或产生部分业务写入。

## Prompt 与产物要求

1. 活跃自动化 prompt 必须显式引用本文件，并声明上述启动预检。
2. 每个新建或恢复的财报子任务必须由当前 `CHILD_PROMPT_TEMPLATE.md` 完整渲染，继承当前 `prompt_contract_version`；不得复用历史 prompt 正文。
3. `prompt_contract_version` 只在 prompt 的输入、写入、失败或输出合同发生实质变化时递增；措辞修正不单独升级。
4. `skill_revision` 记录运行时实际解析值，不在 prompt 中硬编码某个 Git SHA。
5. 任务完成前必须回读持久化产物，确认两个必填版本字段存在且与启动预检结果一致。
6. 若本轮后续又调用了启动时未列入的条件性 Skill，完成前必须带齐实际 Skill 重新运行元数据命令，并用新结果覆盖本轮元数据。
