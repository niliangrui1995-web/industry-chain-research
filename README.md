# 产业链投研

这是一个专门用于产业链和公司研究的 Codex 技能包项目。

## 目录

- `skills/`：精选研究技能副本，共 36 个。
- `skills/industry-research-router/`：产业链与公司研究的入口路由技能。
- `skills/industry-research-router/references/skill-map.md`：研究技能组合清单。
- `AGENTS.md`：本项目的默认研究规则。

## 建议用法

新开对话时可以直接说：

```text
在 D:\vcp_hunter\产业链投研 这个项目里，用产业链与公司研究路由，研究 XXX 赛道/公司。
```

也可以直接问：

```text
这个产业链怎么拆？
谁是真龙头，谁是蹭概念？
这几家公司谁的股票弹性最大？
国产替代里谁最有机会？
```

系统应优先使用 `industry-research-router`，再根据任务选择行情、财务、竞争格局、深度研究和表格技能。

