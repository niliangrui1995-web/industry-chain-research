# 技能与插件维护策略

Last verified: 2026-07-10

## 单一真相源

- 项目专属、可自动发现的技能只放在 `.agents/skills/`。
- 通用 Word/PDF/PPT/Excel 能力不在根级项目技能中复制；项目需要维护的插件源码位于 `plugins/document-skills/`。
- 账户级或已安装插件提供的通用技能按安装来源升级，不复制到本仓库后再局部修改。

## 何时允许新增项目技能

仅在至少满足一项时新增：

- 存在本项目独有的文件、状态或证据合同；
- 操作脆弱、重复且需要确定性脚本；
- 领域边界无法由全局技能或短 reference 表达；
- 用户明确希望把重复工作沉淀为仓库技能。

通用分析方法、人格、普通检查清单、第三方 API 说明和上游技能的轻微改写不构成新增理由。

## 插件源码

`plugins/document-skills/` 是当前文档插件的项目源码副本。没有专项升级计划时不批量重写；需要修改时先记录来源版本、受影响入口和验证命令。安全测试只覆盖这份插件源码，不再维护第二套根级镜像。

## 验证

- 项目技能运行 `skill-creator` 的 `quick_validate.py`。
- 运行 `python scripts\repo_health_check.py --skip-slow`。
- 文档插件改动运行 `tests/test_security_hardening.py` 及相关格式验证。
