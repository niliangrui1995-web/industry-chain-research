# AI 产业链逐级拆解 - Level 4 P0 梳理表

日期：2026-05-31

任务类型：梳理

上游依据：`docs/ai_chain_disassembly/level_03_audit_2026-05-31.md`

父级来源：`docs/ai_chain_disassembly/level_03_from_level_02_audit_approved_2026-05-31.md`

当前状态：pending_audit

下一任务：审计本 Level 4 P0 梳理表；审计通过后再决定继续 Level 4 P1/P2 梳理或进入 Level 5。

## 本轮口径

| 字段 | 口径 |
|---|---|
| Level 0 | AI 数据中心 / 智算中心。 |
| Level 1-3 | 使用已经审计通过的上游表；Level 3 审计允许进入 Level 4。 |
| 本轮范围 | 只梳理 Level 3 表中 priority = P0 的 67 个父节点。 |
| 本轮结果 | 67 个 P0 父节点拆出 283 个 Level 4 节点。 |
| 未覆盖范围 | Level 3 的 P1/P2 节点尚未在本轮展开，后续仍需继续梳理。 |
| 本轮不做 | 不审计、不进入 Level 5、不判定瓶颈、不做价值量排序、不映射股票、不使用行情数据。 |
| 证据口径 | 本轮为结构梳理；份额、价格、产能、交期、公司证据均标记为后续证据任务。 |

## P0 覆盖摘要

| Level 1 主链 | Level 3 P0 父节点数 | Level 4 子节点数 | 备注 |
|---|---:|---:|---|
| DC-L1R-001 GPU/ASIC 加速计算链 | 26 | 113 | 覆盖计算 die、HBM、先进封装、中介层、ABF/PCB、先进制程和测试。 |
| DC-L1R-002 高速网络与光/铜互连链 | 14 | 59 | 覆盖交换机装配、SerDes/交换芯片、NIC、光模块和网络板 PCB。 |
| DC-L1R-004 高密度供配电设备链 | 16 | 64 | 覆盖变压器、开关柜、UPS、母线槽、PDU、PSU 和功率器件。 |
| DC-L1R-005 热管理与液冷链 | 11 | 47 | 覆盖冷板、CDU、快速接头、密封材料和泄漏可靠性测试。 |
| DC-L1R-003 / 006 / 007 | 0 | 0 | 本轮 P0 批次无父节点；这些主链的 P1/P2 后续仍需继续梳理。 |

## Level 4 主表

### DC-L1R-001 GPU/ASIC 加速计算链

| node_id | level | parent_node_id | node_name | 精确定义 | Level 5 候选，不在本轮展开 | 唯一归属与边界 | priority | status |
|---|---:|---|---|---|---|---|---|---|
| DC-L4-001-001-001-001 | 4 | DC-L3-001-001-001 | MAC 阵列 | MAC 阵列 是「张量/矩阵计算核心」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：只属于计算 die 设计，不计入制造制程或封装；本行只统计「张量/矩阵计算核心」内的「MAC 阵列」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-001-001-002 | 4 | DC-L3-001-001-001 | Tensor Core 类单元 | Tensor Core 类单元 是「张量/矩阵计算核心」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：只属于计算 die 设计，不计入制造制程或封装；本行只统计「张量/矩阵计算核心」内的「Tensor Core 类单元」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-001-001-003 | 4 | DC-L3-001-001-001 | 低精度计算单元 | 低精度计算单元 是「张量/矩阵计算核心」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只属于计算 die 设计，不计入制造制程或封装；本行只统计「张量/矩阵计算核心」内的「低精度计算单元」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-001-001-004 | 4 | DC-L3-001-001-001 | 调度微架构 | 调度微架构 是「张量/矩阵计算核心」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：只属于计算 die 设计，不计入制造制程或封装；本行只统计「张量/矩阵计算核心」内的「调度微架构」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-001-002-001 | 4 | DC-L3-001-001-002 | SRAM bitcell | SRAM bitcell 是「片上 SRAM / Cache」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：不等于 HBM 或外部 DRAM；本行只统计「片上 SRAM / Cache」内的「SRAM bitcell」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-001-002-002 | 4 | DC-L3-001-001-002 | cache controller | cache controller 是「片上 SRAM / Cache」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：不等于 HBM 或外部 DRAM；本行只统计「片上 SRAM / Cache」内的「cache controller」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-001-002-003 | 4 | DC-L3-001-001-002 | bank 结构 | bank 结构 是「片上 SRAM / Cache」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于 HBM 或外部 DRAM；本行只统计「片上 SRAM / Cache」内的「bank 结构」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-001-002-004 | 4 | DC-L3-001-001-002 | ECC | ECC 是「片上 SRAM / Cache」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于 HBM 或外部 DRAM；本行只统计「片上 SRAM / Cache」内的「ECC」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-001-003-001 | 4 | DC-L3-001-001-003 | NoC router | NoC router 是「NoC / 片上互连」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：只指 die 内互连，不含板级或机柜级互连；本行只统计「NoC / 片上互连」内的「NoC router」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-001-003-002 | 4 | DC-L3-001-001-003 | crossbar | crossbar 是「NoC / 片上互连」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：只指 die 内互连，不含板级或机柜级互连；本行只统计「NoC / 片上互连」内的「crossbar」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-001-003-003 | 4 | DC-L3-001-001-003 | 片上链路 | 片上链路 是「NoC / 片上互连」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只指 die 内互连，不含板级或机柜级互连；本行只统计「NoC / 片上互连」内的「片上链路」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-001-003-004 | 4 | DC-L3-001-001-003 | QoS 控制 | QoS 控制 是「NoC / 片上互连」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：只指 die 内互连，不含板级或机柜级互连；本行只统计「NoC / 片上互连」内的「QoS 控制」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-001-004-001 | 4 | DC-L3-001-001-004 | HBM PHY | HBM PHY 是「HBM PHY / 内存控制器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：HBM 存储堆本体归 DC-L2-001-002；本行只统计「HBM PHY / 内存控制器」内的「HBM PHY」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-001-004-002 | 4 | DC-L3-001-001-004 | memory controller | memory controller 是「HBM PHY / 内存控制器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：HBM 存储堆本体归 DC-L2-001-002；本行只统计「HBM PHY / 内存控制器」内的「memory controller」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-001-004-003 | 4 | DC-L3-001-001-004 | training logic | training logic 是「HBM PHY / 内存控制器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：HBM 存储堆本体归 DC-L2-001-002；本行只统计「HBM PHY / 内存控制器」内的「training logic」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-001-004-004 | 4 | DC-L3-001-001-004 | 接口验证 | 接口验证 是「HBM PHY / 内存控制器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：HBM 存储堆本体归 DC-L2-001-002；本行只统计「HBM PHY / 内存控制器」内的「接口验证」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-001-001 | 4 | DC-L3-001-002-001 | DRAM cell | DRAM cell 是「HBM DRAM core die」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：只指 HBM 存储 die，不含 base die；本行只统计「HBM DRAM core die」内的「DRAM cell」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-001-002 | 4 | DC-L3-001-002-001 | sense amplifier | sense amplifier 是「HBM DRAM core die」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：只指 HBM 存储 die，不含 base die；本行只统计「HBM DRAM core die」内的「sense amplifier」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-001-003 | 4 | DC-L3-001-002-001 | wordline | wordline 是「HBM DRAM core die」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：只指 HBM 存储 die，不含 base die；本行只统计「HBM DRAM core die」内的「wordline」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-001-004 | 4 | DC-L3-001-002-001 | bitline | bitline 是「HBM DRAM core die」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：只指 HBM 存储 die，不含 base die；本行只统计「HBM DRAM core die」内的「bitline」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-001-005 | 4 | DC-L3-001-002-001 | ECC | ECC 是「HBM DRAM core die」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只指 HBM 存储 die，不含 base die；本行只统计「HBM DRAM core die」内的「ECC」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-002-001 | 4 | DC-L3-001-002-002 | I/O logic | I/O logic 是「HBM base logic die」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：与 GPU die 的内存控制器分开；本行只统计「HBM base logic die」内的「I/O logic」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-002-002 | 4 | DC-L3-001-002-002 | test logic | test logic 是「HBM base logic die」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：与 GPU die 的内存控制器分开；本行只统计「HBM base logic die」内的「test logic」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-002-003 | 4 | DC-L3-001-002-002 | PHY interface | PHY interface 是「HBM base logic die」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：与 GPU die 的内存控制器分开；本行只统计「HBM base logic die」内的「PHY interface」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-002-004 | 4 | DC-L3-001-002-002 | power management | power management 是「HBM base logic die」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与 GPU die 的内存控制器分开；本行只统计「HBM base logic die」内的「power management」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-003-001 | 4 | DC-L3-001-002-003 | TSV etch | TSV etch 是「TSV 垂直互连」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：HBM TSV 归 HBM 链，interposer TSV 归 DC-L2-001-004；本行只统计「TSV 垂直互连」内的「TSV etch」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-003-002 | 4 | DC-L3-001-002-003 | TSV fill | TSV fill 是「TSV 垂直互连」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：HBM TSV 归 HBM 链，interposer TSV 归 DC-L2-001-004；本行只统计「TSV 垂直互连」内的「TSV fill」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-003-003 | 4 | DC-L3-001-002-003 | 绝缘层 | 绝缘层 是「TSV 垂直互连」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：HBM TSV 归 HBM 链，interposer TSV 归 DC-L2-001-004；本行只统计「TSV 垂直互连」内的「绝缘层」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-003-004 | 4 | DC-L3-001-002-003 | 露铜工艺 | 露铜工艺 是「TSV 垂直互连」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：HBM TSV 归 HBM 链，interposer TSV 归 DC-L2-001-004；本行只统计「TSV 垂直互连」内的「露铜工艺」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-004-001 | 4 | DC-L3-001-002-004 | copper pillar | copper pillar 是「Microbump / Hybrid bonding」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：只覆盖 HBM stack 内部连接；本行只统计「Microbump / Hybrid bonding」内的「copper pillar」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-004-002 | 4 | DC-L3-001-002-004 | microbump | microbump 是「Microbump / Hybrid bonding」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只覆盖 HBM stack 内部连接；本行只统计「Microbump / Hybrid bonding」内的「microbump」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-004-003 | 4 | DC-L3-001-002-004 | hybrid bonding | hybrid bonding 是「Microbump / Hybrid bonding」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：只覆盖 HBM stack 内部连接；本行只统计「Microbump / Hybrid bonding」内的「hybrid bonding」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-004-004 | 4 | DC-L3-001-002-004 | underfill | underfill 是「Microbump / Hybrid bonding」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只覆盖 HBM stack 内部连接；本行只统计「Microbump / Hybrid bonding」内的「underfill」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-005-001 | 4 | DC-L3-001-002-005 | die thinning | die thinning 是「HBM stack assembly」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于 GPU/HBM 整体先进封装；本行只统计「HBM stack assembly」内的「die thinning」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-005-002 | 4 | DC-L3-001-002-005 | stacking | stacking 是「HBM stack assembly」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：不等于 GPU/HBM 整体先进封装；本行只统计「HBM stack assembly」内的「stacking」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-005-003 | 4 | DC-L3-001-002-005 | bonding | bonding 是「HBM stack assembly」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：不等于 GPU/HBM 整体先进封装；本行只统计「HBM stack assembly」内的「bonding」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-005-004 | 4 | DC-L3-001-002-005 | molding | molding 是「HBM stack assembly」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：不等于 GPU/HBM 整体先进封装；本行只统计「HBM stack assembly」内的「molding」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-002-005-005 | 4 | DC-L3-001-002-005 | warpage control | warpage control 是「HBM stack assembly」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于 GPU/HBM 整体先进封装；本行只统计「HBM stack assembly」内的「warpage control」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-003-001-001 | 4 | DC-L3-001-003-001 | interposer attach | interposer attach 是「2.5D CoWoS 类封装」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：硅中介层本体另见 DC-L2-001-004；本行只统计「2.5D CoWoS 类封装」内的「interposer attach」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-003-001-002 | 4 | DC-L3-001-003-001 | die attach | die attach 是「2.5D CoWoS 类封装」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：硅中介层本体另见 DC-L2-001-004；本行只统计「2.5D CoWoS 类封装」内的「die attach」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-003-001-003 | 4 | DC-L3-001-003-001 | bump | bump 是「2.5D CoWoS 类封装」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：硅中介层本体另见 DC-L2-001-004；本行只统计「2.5D CoWoS 类封装」内的「bump」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-003-001-004 | 4 | DC-L3-001-003-001 | underfill | underfill 是「2.5D CoWoS 类封装」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：硅中介层本体另见 DC-L2-001-004；本行只统计「2.5D CoWoS 类封装」内的「underfill」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-003-001-005 | 4 | DC-L3-001-003-001 | warpage control | warpage control 是「2.5D CoWoS 类封装」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：硅中介层本体另见 DC-L2-001-004；本行只统计「2.5D CoWoS 类封装」内的「warpage control」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-004-001-001 | 4 | DC-L3-001-004-001 | silicon wafer | silicon wafer 是「硅中介层晶圆」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于普通晶圆制造服务；本行只统计「硅中介层晶圆」内的「silicon wafer」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-004-001-002 | 4 | DC-L3-001-004-001 | 薄化 | 薄化 是「硅中介层晶圆」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：不等于普通晶圆制造服务；本行只统计「硅中介层晶圆」内的「薄化」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-004-001-003 | 4 | DC-L3-001-004-001 | 绝缘层 | 绝缘层 是「硅中介层晶圆」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：不等于普通晶圆制造服务；本行只统计「硅中介层晶圆」内的「绝缘层」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-004-001-004 | 4 | DC-L3-001-004-001 | 刻蚀 | 刻蚀 是「硅中介层晶圆」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：不等于普通晶圆制造服务；本行只统计「硅中介层晶圆」内的「刻蚀」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-004-002-001 | 4 | DC-L3-001-004-002 | 铜电镀 | 铜电镀 是「RDL 铜再布线」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：只统计封装互连，不统计板级 PCB 铜线路；本行只统计「RDL 铜再布线」内的「铜电镀」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-004-002-002 | 4 | DC-L3-001-004-002 | seed layer | seed layer 是「RDL 铜再布线」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只统计封装互连，不统计板级 PCB 铜线路；本行只统计「RDL 铜再布线」内的「seed layer」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-004-002-003 | 4 | DC-L3-001-004-002 | 线路图形 | 线路图形 是「RDL 铜再布线」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：只统计封装互连，不统计板级 PCB 铜线路；本行只统计「RDL 铜再布线」内的「线路图形」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-004-002-004 | 4 | DC-L3-001-004-002 | 介电层 | 介电层 是「RDL 铜再布线」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只统计封装互连，不统计板级 PCB 铜线路；本行只统计「RDL 铜再布线」内的「介电层」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-005-001-001 | 4 | DC-L3-001-005-001 | ABF resin | ABF resin 是「ABF build-up film」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：不等于板级 CCL；本行只统计「ABF build-up film」内的「ABF resin」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-005-001-002 | 4 | DC-L3-001-005-001 | filler | filler 是「ABF build-up film」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：不等于板级 CCL；本行只统计「ABF build-up film」内的「filler」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-005-001-003 | 4 | DC-L3-001-005-001 | film casting | film casting 是「ABF build-up film」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：不等于板级 CCL；本行只统计「ABF build-up film」内的「film casting」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-005-001-004 | 4 | DC-L3-001-005-001 | surface treatment | surface treatment 是「ABF build-up film」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于板级 CCL；本行只统计「ABF build-up film」内的「surface treatment」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-005-003-001 | 4 | DC-L3-001-005-003 | laser drilling | laser drilling 是「载板激光钻孔 / 微孔」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：不等同于普通 PCB 钻孔；本行只统计「载板激光钻孔 / 微孔」内的「laser drilling」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-005-003-002 | 4 | DC-L3-001-005-003 | desmear | desmear 是「载板激光钻孔 / 微孔」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等同于普通 PCB 钻孔；本行只统计「载板激光钻孔 / 微孔」内的「desmear」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-005-003-003 | 4 | DC-L3-001-005-003 | via formation | via formation 是「载板激光钻孔 / 微孔」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等同于普通 PCB 钻孔；本行只统计「载板激光钻孔 / 微孔」内的「via formation」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-005-003-004 | 4 | DC-L3-001-005-003 | microvia inspection | microvia inspection 是「载板激光钻孔 / 微孔」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：不等同于普通 PCB 钻孔；本行只统计「载板激光钻孔 / 微孔」内的「microvia inspection」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-005-004-001 | 4 | DC-L3-001-005-004 | copper plating | copper plating 是「载板电镀与线路形成」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：与板级 PCB 线路加工分开；本行只统计「载板电镀与线路形成」内的「copper plating」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-005-004-002 | 4 | DC-L3-001-005-004 | patterning | patterning 是「载板电镀与线路形成」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与板级 PCB 线路加工分开；本行只统计「载板电镀与线路形成」内的「patterning」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-005-004-003 | 4 | DC-L3-001-005-004 | etching | etching 是「载板电镀与线路形成」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：与板级 PCB 线路加工分开；本行只统计「载板电镀与线路形成」内的「etching」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-005-004-004 | 4 | DC-L3-001-005-004 | SAP/MSAP | SAP/MSAP 是「载板电镀与线路形成」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：与板级 PCB 线路加工分开；本行只统计「载板电镀与线路形成」内的「SAP/MSAP」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-001-001 | 4 | DC-L3-001-006-001 | 树脂体系 | 树脂体系 是「高速低损耗 CCL」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：网络板 CCL 另归 DC-L2-002-009；本行只统计「高速低损耗 CCL」内的「树脂体系」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-001-002 | 4 | DC-L3-001-006-001 | 电子布 | 电子布 是「高速低损耗 CCL」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：网络板 CCL 另归 DC-L2-002-009；本行只统计「高速低损耗 CCL」内的「电子布」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-001-003 | 4 | DC-L3-001-006-001 | 铜箔 | 铜箔 是「高速低损耗 CCL」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：网络板 CCL 另归 DC-L2-002-009；本行只统计「高速低损耗 CCL」内的「铜箔」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-001-004 | 4 | DC-L3-001-006-001 | 填料 | 填料 是「高速低损耗 CCL」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：网络板 CCL 另归 DC-L2-002-009；本行只统计「高速低损耗 CCL」内的「填料」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-001-005 | 4 | DC-L3-001-006-001 | 压合 | 压合 是「高速低损耗 CCL」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：网络板 CCL 另归 DC-L2-002-009；本行只统计「高速低损耗 CCL」内的「压合」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-002-001 | 4 | DC-L3-001-006-002 | PPO/PPE | PPO/PPE 是「低损耗树脂体系」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：不泛化到普通化工树脂；本行只统计「低损耗树脂体系」内的「PPO/PPE」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-002-002 | 4 | DC-L3-001-006-002 | PTFE | PTFE 是「低损耗树脂体系」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：不泛化到普通化工树脂；本行只统计「低损耗树脂体系」内的「PTFE」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-002-003 | 4 | DC-L3-001-006-002 | 碳氢树脂 | 碳氢树脂 是「低损耗树脂体系」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：不泛化到普通化工树脂；本行只统计「低损耗树脂体系」内的「碳氢树脂」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-002-004 | 4 | DC-L3-001-006-002 | 环氧改性 | 环氧改性 是「低损耗树脂体系」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不泛化到普通化工树脂；本行只统计「低损耗树脂体系」内的「环氧改性」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-002-005 | 4 | DC-L3-001-006-002 | 填料 | 填料 是「低损耗树脂体系」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不泛化到普通化工树脂；本行只统计「低损耗树脂体系」内的「填料」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-003-001 | 4 | DC-L3-001-006-003 | glass yarn | glass yarn 是「电子玻纤布 / 玻纤纱」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：不等于建筑玻纤或普通纺织玻纤；本行只统计「电子玻纤布 / 玻纤纱」内的「glass yarn」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-003-002 | 4 | DC-L3-001-006-003 | spread glass | spread glass 是「电子玻纤布 / 玻纤纱」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：不等于建筑玻纤或普通纺织玻纤；本行只统计「电子玻纤布 / 玻纤纱」内的「spread glass」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-003-003 | 4 | DC-L3-001-006-003 | weaving | weaving 是「电子玻纤布 / 玻纤纱」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于建筑玻纤或普通纺织玻纤；本行只统计「电子玻纤布 / 玻纤纱」内的「weaving」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-003-004 | 4 | DC-L3-001-006-003 | surface treatment | surface treatment 是「电子玻纤布 / 玻纤纱」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于建筑玻纤或普通纺织玻纤；本行只统计「电子玻纤布 / 玻纤纱」内的「surface treatment」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-004-001 | 4 | DC-L3-001-006-004 | ED copper foil | ED copper foil 是「PCB 铜箔」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：不等同于锂电铜箔；本行只统计「PCB 铜箔」内的「ED copper foil」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-004-002 | 4 | DC-L3-001-006-004 | rolled copper foil | rolled copper foil 是「PCB 铜箔」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：不等同于锂电铜箔；本行只统计「PCB 铜箔」内的「rolled copper foil」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-004-003 | 4 | DC-L3-001-006-004 | roughness control | roughness control 是「PCB 铜箔」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等同于锂电铜箔；本行只统计「PCB 铜箔」内的「roughness control」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-004-004 | 4 | DC-L3-001-006-004 | surface treatment | surface treatment 是「PCB 铜箔」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等同于锂电铜箔；本行只统计「PCB 铜箔」内的「surface treatment」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-005-001 | 4 | DC-L3-001-006-005 | lamination | lamination 是「高层板压合 / 背钻 / 电镀」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：属 PCB 制造工艺，不是 CCL 材料本体；本行只统计「高层板压合 / 背钻 / 电镀」内的「lamination」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-005-002 | 4 | DC-L3-001-006-005 | drilling | drilling 是「高层板压合 / 背钻 / 电镀」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：属 PCB 制造工艺，不是 CCL 材料本体；本行只统计「高层板压合 / 背钻 / 电镀」内的「drilling」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-005-003 | 4 | DC-L3-001-006-005 | back drilling | back drilling 是「高层板压合 / 背钻 / 电镀」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：属 PCB 制造工艺，不是 CCL 材料本体；本行只统计「高层板压合 / 背钻 / 电镀」内的「back drilling」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-005-004 | 4 | DC-L3-001-006-005 | PTH | PTH 是「高层板压合 / 背钻 / 电镀」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：属 PCB 制造工艺，不是 CCL 材料本体；本行只统计「高层板压合 / 背钻 / 电镀」内的「PTH」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-006-005-005 | 4 | DC-L3-001-006-005 | plating | plating 是「高层板压合 / 背钻 / 电镀」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：属 PCB 制造工艺，不是 CCL 材料本体；本行只统计「高层板压合 / 背钻 / 电镀」内的「plating」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-007-001-001 | 4 | DC-L3-001-007-001 | MOSFET | MOSFET 是「DrMOS / Power stage」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于服务器 PSU 功率级；本行只统计「DrMOS / Power stage」内的「MOSFET」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-007-001-002 | 4 | DC-L3-001-007-001 | driver | driver 是「DrMOS / Power stage」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：不等于服务器 PSU 功率级；本行只统计「DrMOS / Power stage」内的「driver」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-007-001-003 | 4 | DC-L3-001-007-001 | package | package 是「DrMOS / Power stage」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于服务器 PSU 功率级；本行只统计「DrMOS / Power stage」内的「package」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-007-001-004 | 4 | DC-L3-001-007-001 | current sense | current sense 是「DrMOS / Power stage」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于服务器 PSU 功率级；本行只统计「DrMOS / Power stage」内的「current sense」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-007-001-005 | 4 | DC-L3-001-007-001 | thermal pad | thermal pad 是「DrMOS / Power stage」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：不等于服务器 PSU 功率级；本行只统计「DrMOS / Power stage」内的「thermal pad」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-008-001-001 | 4 | DC-L3-001-008-001 | lithography scanner | lithography scanner 是「EUV / DUV 光刻」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：只按 GPU/ASIC die 制程归属；本行只统计「EUV / DUV 光刻」内的「lithography scanner」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-008-001-002 | 4 | DC-L3-001-008-001 | photoresist | photoresist 是「EUV / DUV 光刻」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：只按 GPU/ASIC die 制程归属；本行只统计「EUV / DUV 光刻」内的「photoresist」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-008-001-003 | 4 | DC-L3-001-008-001 | mask | mask 是「EUV / DUV 光刻」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：只按 GPU/ASIC die 制程归属；本行只统计「EUV / DUV 光刻」内的「mask」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-008-001-004 | 4 | DC-L3-001-008-001 | overlay metrology | overlay metrology 是「EUV / DUV 光刻」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：只按 GPU/ASIC die 制程归属；本行只统计「EUV / DUV 光刻」内的「overlay metrology」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-008-002-001 | 4 | DC-L3-001-008-002 | plasma etch | plasma etch 是「刻蚀工艺与设备」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于 PCB 蚀刻；本行只统计「刻蚀工艺与设备」内的「plasma etch」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-008-002-002 | 4 | DC-L3-001-008-002 | wet etch | wet etch 是「刻蚀工艺与设备」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于 PCB 蚀刻；本行只统计「刻蚀工艺与设备」内的「wet etch」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-008-002-003 | 4 | DC-L3-001-008-002 | etch gas | etch gas 是「刻蚀工艺与设备」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：不等于 PCB 蚀刻；本行只统计「刻蚀工艺与设备」内的「etch gas」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-008-002-004 | 4 | DC-L3-001-008-002 | chamber parts | chamber parts 是「刻蚀工艺与设备」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于 PCB 蚀刻；本行只统计「刻蚀工艺与设备」内的「chamber parts」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-008-003-001 | 4 | DC-L3-001-008-003 | CVD | CVD 是「薄膜沉积」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只统计半导体晶圆制程；本行只统计「薄膜沉积」内的「CVD」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-008-003-002 | 4 | DC-L3-001-008-003 | PVD | PVD 是「薄膜沉积」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只统计半导体晶圆制程；本行只统计「薄膜沉积」内的「PVD」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-008-003-003 | 4 | DC-L3-001-008-003 | ALD | ALD 是「薄膜沉积」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只统计半导体晶圆制程；本行只统计「薄膜沉积」内的「ALD」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-008-003-004 | 4 | DC-L3-001-008-003 | precursor | precursor 是「薄膜沉积」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：只统计半导体晶圆制程；本行只统计「薄膜沉积」内的「precursor」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-008-003-005 | 4 | DC-L3-001-008-003 | target | target 是「薄膜沉积」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：只统计半导体晶圆制程；本行只统计「薄膜沉积」内的「target」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-008-006-001 | 4 | DC-L3-001-008-006 | inspection | inspection 是「量测检测」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：与封装检测分开；本行只统计「量测检测」内的「inspection」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-008-006-002 | 4 | DC-L3-001-008-006 | metrology | metrology 是「量测检测」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：与封装检测分开；本行只统计「量测检测」内的「metrology」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-008-006-003 | 4 | DC-L3-001-008-006 | CD-SEM | CD-SEM 是「量测检测」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：与封装检测分开；本行只统计「量测检测」内的「CD-SEM」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-008-006-004 | 4 | DC-L3-001-008-006 | overlay | overlay 是「量测检测」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：与封装检测分开；本行只统计「量测检测」内的「overlay」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-008-006-005 | 4 | DC-L3-001-008-006 | defect review | defect review 是「量测检测」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：与封装检测分开；本行只统计「量测检测」内的「defect review」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-009-001-001 | 4 | DC-L3-001-009-001 | tester | tester 是「ATE 测试机」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：整机系统测试另属 DC-L2-003-005；本行只统计「ATE 测试机」内的「tester」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-009-001-002 | 4 | DC-L3-001-009-001 | test program | test program 是「ATE 测试机」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：整机系统测试另属 DC-L2-003-005；本行只统计「ATE 测试机」内的「test program」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-009-001-003 | 4 | DC-L3-001-009-001 | handler interface | handler interface 是「ATE 测试机」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：整机系统测试另属 DC-L2-003-005；本行只统计「ATE 测试机」内的「handler interface」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-001-009-001-004 | 4 | DC-L3-001-009-001 | test cell | test cell 是「ATE 测试机」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：整机系统测试另属 DC-L2-003-005；本行只统计「ATE 测试机」内的「test cell」，不跨父节点合并。 | P0 | pending_audit |

### DC-L1R-002 高速网络与光/铜互连链

| node_id | level | parent_node_id | node_name | 精确定义 | Level 5 候选，不在本轮展开 | 唯一归属与边界 | priority | status |
|---|---:|---|---|---|---|---|---|---|
| DC-L4-002-001-002-001 | 4 | DC-L3-002-001-002 | SMT | SMT 是「交换机主板 / Line card 装配」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：PCB 制造本体归 DC-L2-002-009；本行只统计「交换机主板 / Line card 装配」内的「SMT」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-001-002-002 | 4 | DC-L3-002-001-002 | line card | line card 是「交换机主板 / Line card 装配」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：PCB 制造本体归 DC-L2-002-009；本行只统计「交换机主板 / Line card 装配」内的「line card」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-001-002-003 | 4 | DC-L3-002-001-002 | switch board | switch board 是「交换机主板 / Line card 装配」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：PCB 制造本体归 DC-L2-002-009；本行只统计「交换机主板 / Line card 装配」内的「switch board」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-001-002-004 | 4 | DC-L3-002-001-002 | connector | connector 是「交换机主板 / Line card 装配」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：PCB 制造本体归 DC-L2-002-009；本行只统计「交换机主板 / Line card 装配」内的「connector」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-001-002-005 | 4 | DC-L3-002-001-002 | cage | cage 是「交换机主板 / Line card 装配」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：PCB 制造本体归 DC-L2-002-009；本行只统计「交换机主板 / Line card 装配」内的「cage」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-002-001-001 | 4 | DC-L3-002-002-001 | PAM4 SerDes | PAM4 SerDes 是「SerDes IP / PHY」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：Retimer 独立器件另归 DC-L2-002-008；本行只统计「SerDes IP / PHY」内的「PAM4 SerDes」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-002-001-002 | 4 | DC-L3-002-002-001 | CDR | CDR 是「SerDes IP / PHY」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：Retimer 独立器件另归 DC-L2-002-008；本行只统计「SerDes IP / PHY」内的「CDR」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-002-001-003 | 4 | DC-L3-002-002-001 | equalization | equalization 是「SerDes IP / PHY」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：Retimer 独立器件另归 DC-L2-002-008；本行只统计「SerDes IP / PHY」内的「equalization」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-002-001-004 | 4 | DC-L3-002-002-001 | PLL | PLL 是「SerDes IP / PHY」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：Retimer 独立器件另归 DC-L2-002-008；本行只统计「SerDes IP / PHY」内的「PLL」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-002-002-001 | 4 | DC-L3-002-002-002 | parser | parser 是「Packet processor / Traffic manager」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只属于交换 ASIC 设计；本行只统计「Packet processor / Traffic manager」内的「parser」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-002-002-002 | 4 | DC-L3-002-002-002 | scheduler | scheduler 是「Packet processor / Traffic manager」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只属于交换 ASIC 设计；本行只统计「Packet processor / Traffic manager」内的「scheduler」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-002-002-003 | 4 | DC-L3-002-002-002 | buffer manager | buffer manager 是「Packet processor / Traffic manager」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：只属于交换 ASIC 设计；本行只统计「Packet processor / Traffic manager」内的「buffer manager」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-002-002-004 | 4 | DC-L3-002-002-002 | congestion control | congestion control 是「Packet processor / Traffic manager」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只属于交换 ASIC 设计；本行只统计「Packet processor / Traffic manager」内的「congestion control」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-003-001-001 | 4 | DC-L3-002-003-001 | MAC | MAC 是「Ethernet 控制器 / MAC」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：不等于交换芯片；本行只统计「Ethernet 控制器 / MAC」内的「MAC」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-003-001-002 | 4 | DC-L3-002-003-001 | PCS | PCS 是「Ethernet 控制器 / MAC」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于交换芯片；本行只统计「Ethernet 控制器 / MAC」内的「PCS」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-003-001-003 | 4 | DC-L3-002-003-001 | FEC | FEC 是「Ethernet 控制器 / MAC」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：不等于交换芯片；本行只统计「Ethernet 控制器 / MAC」内的「FEC」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-003-001-004 | 4 | DC-L3-002-003-001 | flow control | flow control 是「Ethernet 控制器 / MAC」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于交换芯片；本行只统计「Ethernet 控制器 / MAC」内的「flow control」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-003-001-005 | 4 | DC-L3-002-003-001 | time sync | time sync 是「Ethernet 控制器 / MAC」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于交换芯片；本行只统计「Ethernet 控制器 / MAC」内的「time sync」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-003-003-001 | 4 | DC-L3-002-003-003 | RDMA engine | RDMA engine 是「RDMA / RoCE 卸载引擎」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：存储路径应用另在 DC-L2-006-007 标边界；本行只统计「RDMA / RoCE 卸载引擎」内的「RDMA engine」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-003-003-002 | 4 | DC-L3-002-003-003 | RoCE logic | RoCE logic 是「RDMA / RoCE 卸载引擎」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：存储路径应用另在 DC-L2-006-007 标边界；本行只统计「RDMA / RoCE 卸载引擎」内的「RoCE logic」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-003-003-003 | 4 | DC-L3-002-003-003 | queue pair | queue pair 是「RDMA / RoCE 卸载引擎」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：存储路径应用另在 DC-L2-006-007 标边界；本行只统计「RDMA / RoCE 卸载引擎」内的「queue pair」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-003-003-004 | 4 | DC-L3-002-003-003 | transport offload | transport offload 是「RDMA / RoCE 卸载引擎」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：存储路径应用另在 DC-L2-006-007 标边界；本行只统计「RDMA / RoCE 卸载引擎」内的「transport offload」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-003-004-001 | 4 | DC-L3-002-003-004 | SerDes | SerDes 是「NIC SerDes / PHY」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：与独立 Retimer 分开；本行只统计「NIC SerDes / PHY」内的「SerDes」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-003-004-002 | 4 | DC-L3-002-003-004 | retimer interface | retimer interface 是「NIC SerDes / PHY」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：与独立 Retimer 分开；本行只统计「NIC SerDes / PHY」内的「retimer interface」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-003-004-003 | 4 | DC-L3-002-003-004 | PLL | PLL 是「NIC SerDes / PHY」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：与独立 Retimer 分开；本行只统计「NIC SerDes / PHY」内的「PLL」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-003-004-004 | 4 | DC-L3-002-003-004 | equalizer | equalizer 是「NIC SerDes / PHY」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与独立 Retimer 分开；本行只统计「NIC SerDes / PHY」内的「equalizer」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-001-001 | 4 | DC-L3-002-004-001 | EML | EML 是「EML / Laser chip」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不是完整光模块；本行只统计「EML / Laser chip」内的「EML」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-001-002 | 4 | DC-L3-002-004-001 | DFB laser | DFB laser 是「EML / Laser chip」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不是完整光模块；本行只统计「EML / Laser chip」内的「DFB laser」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-001-003 | 4 | DC-L3-002-004-001 | InP epitaxy | InP epitaxy 是「EML / Laser chip」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不是完整光模块；本行只统计「EML / Laser chip」内的「InP epitaxy」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-001-004 | 4 | DC-L3-002-004-001 | reliability test | reliability test 是「EML / Laser chip」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：不是完整光模块；本行只统计「EML / Laser chip」内的「reliability test」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-002-001 | 4 | DC-L3-002-004-002 | SiPh modulator | SiPh modulator 是「Silicon photonics / InP PIC」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：与分立被动光器件区分；本行只统计「Silicon photonics / InP PIC」内的「SiPh modulator」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-002-002 | 4 | DC-L3-002-004-002 | InP PIC | InP PIC 是「Silicon photonics / InP PIC」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与分立被动光器件区分；本行只统计「Silicon photonics / InP PIC」内的「InP PIC」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-002-003 | 4 | DC-L3-002-004-002 | grating coupler | grating coupler 是「Silicon photonics / InP PIC」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与分立被动光器件区分；本行只统计「Silicon photonics / InP PIC」内的「grating coupler」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-002-004 | 4 | DC-L3-002-004-002 | waveguide | waveguide 是「Silicon photonics / InP PIC」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与分立被动光器件区分；本行只统计「Silicon photonics / InP PIC」内的「waveguide」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-003-001 | 4 | DC-L3-002-004-003 | DSP ASIC | DSP ASIC 是「DSP」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：不等于交换 ASIC；本行只统计「DSP」内的「DSP ASIC」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-003-002 | 4 | DC-L3-002-004-003 | FEC | FEC 是「DSP」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：不等于交换 ASIC；本行只统计「DSP」内的「FEC」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-003-003 | 4 | DC-L3-002-004-003 | equalization | equalization 是「DSP」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于交换 ASIC；本行只统计「DSP」内的「equalization」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-003-004 | 4 | DC-L3-002-004-003 | ADC/DAC | ADC/DAC 是「DSP」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：不等于交换 ASIC；本行只统计「DSP」内的「ADC/DAC」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-004-001 | 4 | DC-L3-002-004-004 | laser driver | laser driver 是「Driver / TIA」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：只属于光模块电芯片；本行只统计「Driver / TIA」内的「laser driver」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-004-002 | 4 | DC-L3-002-004-004 | TIA | TIA 是「Driver / TIA」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：只属于光模块电芯片；本行只统计「Driver / TIA」内的「TIA」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-004-003 | 4 | DC-L3-002-004-004 | limiting amplifier | limiting amplifier 是「Driver / TIA」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：只属于光模块电芯片；本行只统计「Driver / TIA」内的「limiting amplifier」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-004-004 | 4 | DC-L3-002-004-004 | analog front-end | analog front-end 是「Driver / TIA」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只属于光模块电芯片；本行只统计「Driver / TIA」内的「analog front-end」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-005-001 | 4 | DC-L3-002-004-005 | TOSA | TOSA 是「TOSA / ROSA」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：光引擎可更高集成，不完全等同；本行只统计「TOSA / ROSA」内的「TOSA」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-005-002 | 4 | DC-L3-002-004-005 | ROSA | ROSA 是「TOSA / ROSA」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：光引擎可更高集成，不完全等同；本行只统计「TOSA / ROSA」内的「ROSA」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-005-003 | 4 | DC-L3-002-004-005 | active alignment | active alignment 是「TOSA / ROSA」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：光引擎可更高集成，不完全等同；本行只统计「TOSA / ROSA」内的「active alignment」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-005-004 | 4 | DC-L3-002-004-005 | hermetic package | hermetic package 是「TOSA / ROSA」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：光引擎可更高集成，不完全等同；本行只统计「TOSA / ROSA」内的「hermetic package」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-008-001 | 4 | DC-L3-002-004-008 | BERT | BERT 是「光模块测试 / 校准」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：网络系统测试另归 DC-L2-002-011；本行只统计「光模块测试 / 校准」内的「BERT」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-008-002 | 4 | DC-L3-002-004-008 | optical tester | optical tester 是「光模块测试 / 校准」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：网络系统测试另归 DC-L2-002-011；本行只统计「光模块测试 / 校准」内的「optical tester」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-008-003 | 4 | DC-L3-002-004-008 | thermal calibration | thermal calibration 是「光模块测试 / 校准」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：网络系统测试另归 DC-L2-002-011；本行只统计「光模块测试 / 校准」内的「thermal calibration」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-004-008-004 | 4 | DC-L3-002-004-008 | aging | aging 是「光模块测试 / 校准」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：网络系统测试另归 DC-L2-002-011；本行只统计「光模块测试 / 校准」内的「aging」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-009-001-001 | 4 | DC-L3-002-009-001 | resin | resin 是「网络板高速 CCL」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：与计算板 CCL 按用途分开；本行只统计「网络板高速 CCL」内的「resin」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-009-001-002 | 4 | DC-L3-002-009-001 | glass cloth | glass cloth 是「网络板高速 CCL」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：与计算板 CCL 按用途分开；本行只统计「网络板高速 CCL」内的「glass cloth」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-009-001-003 | 4 | DC-L3-002-009-001 | copper foil | copper foil 是「网络板高速 CCL」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：与计算板 CCL 按用途分开；本行只统计「网络板高速 CCL」内的「copper foil」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-009-001-004 | 4 | DC-L3-002-009-001 | lamination | lamination 是「网络板高速 CCL」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：与计算板 CCL 按用途分开；本行只统计「网络板高速 CCL」内的「lamination」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-009-002-001 | 4 | DC-L3-002-009-002 | lamination | lamination 是「网络高层 PCB 制造」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：光模块小板可单独标注；本行只统计「网络高层 PCB 制造」内的「lamination」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-009-002-002 | 4 | DC-L3-002-009-002 | back drilling | back drilling 是「网络高层 PCB 制造」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：光模块小板可单独标注；本行只统计「网络高层 PCB 制造」内的「back drilling」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-009-002-003 | 4 | DC-L3-002-009-002 | plating | plating 是「网络高层 PCB 制造」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：光模块小板可单独标注；本行只统计「网络高层 PCB 制造」内的「plating」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-009-002-004 | 4 | DC-L3-002-009-002 | HDI | HDI 是「网络高层 PCB 制造」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：光模块小板可单独标注；本行只统计「网络高层 PCB 制造」内的「HDI」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-002-009-002-005 | 4 | DC-L3-002-009-002 | impedance control | impedance control 是「网络高层 PCB 制造」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：光模块小板可单独标注；本行只统计「网络高层 PCB 制造」内的「impedance control」，不跨父节点合并。 | P0 | pending_audit |

### DC-L1R-004 高密度供配电设备链

| node_id | level | parent_node_id | node_name | 精确定义 | Level 5 候选，不在本轮展开 | 唯一归属与边界 | priority | status |
|---|---:|---|---|---|---|---|---|---|
| DC-L4-004-001-001-001 | 4 | DC-L3-004-001-001 | grain-oriented steel | grain-oriented steel 是「电工钢 / 铁芯材料」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：只按变压器用途归属；本行只统计「电工钢 / 铁芯材料」内的「grain-oriented steel」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-001-001-002 | 4 | DC-L3-004-001-001 | core cutting | core cutting 是「电工钢 / 铁芯材料」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：只按变压器用途归属；本行只统计「电工钢 / 铁芯材料」内的「core cutting」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-001-001-003 | 4 | DC-L3-004-001-001 | stacking | stacking 是「电工钢 / 铁芯材料」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：只按变压器用途归属；本行只统计「电工钢 / 铁芯材料」内的「stacking」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-001-001-004 | 4 | DC-L3-004-001-001 | annealing | annealing 是「电工钢 / 铁芯材料」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：只按变压器用途归属；本行只统计「电工钢 / 铁芯材料」内的「annealing」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-001-002-001 | 4 | DC-L3-004-001-002 | copper wire | copper wire 是「铜绕组 / 铜线 / 铜箔」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：与 PCB 铜箔分开；本行只统计「铜绕组 / 铜线 / 铜箔」内的「copper wire」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-001-002-002 | 4 | DC-L3-004-001-002 | copper foil | copper foil 是「铜绕组 / 铜线 / 铜箔」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：与 PCB 铜箔分开；本行只统计「铜绕组 / 铜线 / 铜箔」内的「copper foil」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-001-002-003 | 4 | DC-L3-004-001-002 | winding process | winding process 是「铜绕组 / 铜线 / 铜箔」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：与 PCB 铜箔分开；本行只统计「铜绕组 / 铜线 / 铜箔」内的「winding process」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-001-002-004 | 4 | DC-L3-004-001-002 | insulation coating | insulation coating 是「铜绕组 / 铜线 / 铜箔」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与 PCB 铜箔分开；本行只统计「铜绕组 / 铜线 / 铜箔」内的「insulation coating」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-001-003-001 | 4 | DC-L3-004-001-003 | kraft paper | kraft paper 是「绝缘纸 / 绝缘油 / 树脂」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：不泛化到普通绝缘材料；本行只统计「绝缘纸 / 绝缘油 / 树脂」内的「kraft paper」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-001-003-002 | 4 | DC-L3-004-001-003 | pressboard | pressboard 是「绝缘纸 / 绝缘油 / 树脂」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不泛化到普通绝缘材料；本行只统计「绝缘纸 / 绝缘油 / 树脂」内的「pressboard」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-001-003-003 | 4 | DC-L3-004-001-003 | transformer oil | transformer oil 是「绝缘纸 / 绝缘油 / 树脂」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：不泛化到普通绝缘材料；本行只统计「绝缘纸 / 绝缘油 / 树脂」内的「transformer oil」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-001-003-004 | 4 | DC-L3-004-001-003 | cast resin | cast resin 是「绝缘纸 / 绝缘油 / 树脂」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：不泛化到普通绝缘材料；本行只统计「绝缘纸 / 绝缘油 / 树脂」内的「cast resin」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-002-001-001 | 4 | DC-L3-004-002-001 | vacuum breaker | vacuum breaker 是「断路器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于 IT 网络交换机；本行只统计「断路器」内的「vacuum breaker」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-002-001-002 | 4 | DC-L3-004-002-001 | air breaker | air breaker 是「断路器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于 IT 网络交换机；本行只统计「断路器」内的「air breaker」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-002-001-003 | 4 | DC-L3-004-002-001 | mechanism | mechanism 是「断路器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于 IT 网络交换机；本行只统计「断路器」内的「mechanism」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-002-001-004 | 4 | DC-L3-004-002-001 | arc chamber | arc chamber 是「断路器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于 IT 网络交换机；本行只统计「断路器」内的「arc chamber」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-003-001-001 | 4 | DC-L3-004-003-001 | rectifier bridge | rectifier bridge 是「UPS 整流器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与服务器 PSU 输入级分开；本行只统计「UPS 整流器」内的「rectifier bridge」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-003-001-002 | 4 | DC-L3-004-003-001 | PFC | PFC 是「UPS 整流器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与服务器 PSU 输入级分开；本行只统计「UPS 整流器」内的「PFC」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-003-001-003 | 4 | DC-L3-004-003-001 | control board | control board 是「UPS 整流器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与服务器 PSU 输入级分开；本行只统计「UPS 整流器」内的「control board」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-003-001-004 | 4 | DC-L3-004-003-001 | power device | power device 是「UPS 整流器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与服务器 PSU 输入级分开；本行只统计「UPS 整流器」内的「power device」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-003-002-001 | 4 | DC-L3-004-003-002 | inverter bridge | inverter bridge 是「UPS 逆变器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只属于设施级 UPS；本行只统计「UPS 逆变器」内的「inverter bridge」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-003-002-002 | 4 | DC-L3-004-003-002 | filter | filter 是「UPS 逆变器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只属于设施级 UPS；本行只统计「UPS 逆变器」内的「filter」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-003-002-003 | 4 | DC-L3-004-003-002 | gate driver | gate driver 是「UPS 逆变器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：只属于设施级 UPS；本行只统计「UPS 逆变器」内的「gate driver」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-003-002-004 | 4 | DC-L3-004-003-002 | control loop | control loop 是「UPS 逆变器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只属于设施级 UPS；本行只统计「UPS 逆变器」内的「control loop」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-004-001-001 | 4 | DC-L3-004-004-001 | copper bar | copper bar 是「母线铜/铝导体」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：与 PCB 铜箔分开；本行只统计「母线铜/铝导体」内的「copper bar」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-004-001-002 | 4 | DC-L3-004-004-001 | aluminum bar | aluminum bar 是「母线铜/铝导体」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与 PCB 铜箔分开；本行只统计「母线铜/铝导体」内的「aluminum bar」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-004-001-003 | 4 | DC-L3-004-004-001 | surface plating | surface plating 是「母线铜/铝导体」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：与 PCB 铜箔分开；本行只统计「母线铜/铝导体」内的「surface plating」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-004-001-004 | 4 | DC-L3-004-004-001 | conductor forming | conductor forming 是「母线铜/铝导体」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与 PCB 铜箔分开；本行只统计「母线铜/铝导体」内的「conductor forming」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-004-002-001 | 4 | DC-L3-004-004-002 | insulation film | insulation film 是「母线绝缘材料」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：只按母线槽用途归属；本行只统计「母线绝缘材料」内的「insulation film」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-004-002-002 | 4 | DC-L3-004-004-002 | epoxy coating | epoxy coating 是「母线绝缘材料」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只按母线槽用途归属；本行只统计「母线绝缘材料」内的「epoxy coating」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-004-002-003 | 4 | DC-L3-004-004-002 | flame-retardant material | flame-retardant material 是「母线绝缘材料」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只按母线槽用途归属；本行只统计「母线绝缘材料」内的「flame-retardant material」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-004-004-001 | 4 | DC-L3-004-004-004 | tap-off box | tap-off box 是「Tap-off / 插接箱」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：PDU 主设备另列 DC-L2-004-005；本行只统计「Tap-off / 插接箱」内的「tap-off box」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-004-004-002 | 4 | DC-L3-004-004-004 | breaker | breaker 是「Tap-off / 插接箱」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：PDU 主设备另列 DC-L2-004-005；本行只统计「Tap-off / 插接箱」内的「breaker」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-004-004-003 | 4 | DC-L3-004-004-004 | metering module | metering module 是「Tap-off / 插接箱」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：PDU 主设备另列 DC-L2-004-005；本行只统计「Tap-off / 插接箱」内的「metering module」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-004-004-004 | 4 | DC-L3-004-004-004 | connector | connector 是「Tap-off / 插接箱」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：PDU 主设备另列 DC-L2-004-005；本行只统计「Tap-off / 插接箱」内的「connector」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-005-001-001 | 4 | DC-L3-004-005-001 | distribution board | distribution board 是「PDU 配电板 / 铜排」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于 facility busway；本行只统计「PDU 配电板 / 铜排」内的「distribution board」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-005-001-002 | 4 | DC-L3-004-005-001 | busbar | busbar 是「PDU 配电板 / 铜排」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于 facility busway；本行只统计「PDU 配电板 / 铜排」内的「busbar」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-005-001-003 | 4 | DC-L3-004-005-001 | terminal block | terminal block 是「PDU 配电板 / 铜排」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于 facility busway；本行只统计「PDU 配电板 / 铜排」内的「terminal block」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-005-001-004 | 4 | DC-L3-004-005-001 | fuse holder | fuse holder 是「PDU 配电板 / 铜排」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于 facility busway；本行只统计「PDU 配电板 / 铜排」内的「fuse holder」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-005-002-001 | 4 | DC-L3-004-005-002 | breaker | breaker 是「断路器 / 熔断器 / 保护器件」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：开关柜保护设备另列；本行只统计「断路器 / 熔断器 / 保护器件」内的「breaker」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-005-002-002 | 4 | DC-L3-004-005-002 | fuse | fuse 是「断路器 / 熔断器 / 保护器件」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：开关柜保护设备另列；本行只统计「断路器 / 熔断器 / 保护器件」内的「fuse」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-005-002-003 | 4 | DC-L3-004-005-002 | SPD | SPD 是「断路器 / 熔断器 / 保护器件」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：开关柜保护设备另列；本行只统计「断路器 / 熔断器 / 保护器件」内的「SPD」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-005-002-004 | 4 | DC-L3-004-005-002 | protection relay | protection relay 是「断路器 / 熔断器 / 保护器件」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：开关柜保护设备另列；本行只统计「断路器 / 熔断器 / 保护器件」内的「protection relay」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-005-004-001 | 4 | DC-L3-004-005-004 | power connector | power connector 是「高电流连接器 / 插座」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与高速网络连接器分开；本行只统计「高电流连接器 / 插座」内的「power connector」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-005-004-002 | 4 | DC-L3-004-005-004 | busbar connector | busbar connector 是「高电流连接器 / 插座」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与高速网络连接器分开；本行只统计「高电流连接器 / 插座」内的「busbar connector」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-005-004-003 | 4 | DC-L3-004-005-004 | socket | socket 是「高电流连接器 / 插座」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与高速网络连接器分开；本行只统计「高电流连接器 / 插座」内的「socket」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-005-004-004 | 4 | DC-L3-004-005-004 | blind-mate interface | blind-mate interface 是「高电流连接器 / 插座」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：与高速网络连接器分开；本行只统计「高电流连接器 / 插座」内的「blind-mate interface」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-006-001-001 | 4 | DC-L3-004-006-001 | PFC controller | PFC controller 是「PFC 输入级」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：UPS 整流器另归 DC-L2-004-003；本行只统计「PFC 输入级」内的「PFC controller」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-006-001-002 | 4 | DC-L3-004-006-001 | bridge | bridge 是「PFC 输入级」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：UPS 整流器另归 DC-L2-004-003；本行只统计「PFC 输入级」内的「bridge」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-006-001-003 | 4 | DC-L3-004-006-001 | inductor | inductor 是「PFC 输入级」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：UPS 整流器另归 DC-L2-004-003；本行只统计「PFC 输入级」内的「inductor」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-006-001-004 | 4 | DC-L3-004-006-001 | switching device | switching device 是「PFC 输入级」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：UPS 整流器另归 DC-L2-004-003；本行只统计「PFC 输入级」内的「switching device」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-006-002-001 | 4 | DC-L3-004-006-002 | LLC transformer | LLC transformer 是「LLC / DC-DC 变换级」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：板级 VRM 不在此列；本行只统计「LLC / DC-DC 变换级」内的「LLC transformer」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-006-002-002 | 4 | DC-L3-004-006-002 | synchronous rectifier | synchronous rectifier 是「LLC / DC-DC 变换级」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：板级 VRM 不在此列；本行只统计「LLC / DC-DC 变换级」内的「synchronous rectifier」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-006-002-003 | 4 | DC-L3-004-006-002 | PWM control | PWM control 是「LLC / DC-DC 变换级」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：板级 VRM 不在此列；本行只统计「LLC / DC-DC 变换级」内的「PWM control」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-006-002-004 | 4 | DC-L3-004-006-002 | output filter | output filter 是「LLC / DC-DC 变换级」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：板级 VRM 不在此列；本行只统计「LLC / DC-DC 变换级」内的「output filter」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-006-003-001 | 4 | DC-L3-004-006-003 | high-frequency transformer | high-frequency transformer 是「PSU 磁性元件」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与设施变压器不同；本行只统计「PSU 磁性元件」内的「high-frequency transformer」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-006-003-002 | 4 | DC-L3-004-006-003 | inductor | inductor 是「PSU 磁性元件」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与设施变压器不同；本行只统计「PSU 磁性元件」内的「inductor」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-006-003-003 | 4 | DC-L3-004-006-003 | magnetic core | magnetic core 是「PSU 磁性元件」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：与设施变压器不同；本行只统计「PSU 磁性元件」内的「magnetic core」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-006-003-004 | 4 | DC-L3-004-006-003 | winding | winding 是「PSU 磁性元件」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：与设施变压器不同；本行只统计「PSU 磁性元件」内的「winding」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-006-004-001 | 4 | DC-L3-004-006-004 | MOSFET | MOSFET 是「PSU 功率半导体」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与通用功率器件节点有交叉，需按用途标记；本行只统计「PSU 功率半导体」内的「MOSFET」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-006-004-002 | 4 | DC-L3-004-006-004 | GaN FET | GaN FET 是「PSU 功率半导体」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与通用功率器件节点有交叉，需按用途标记；本行只统计「PSU 功率半导体」内的「GaN FET」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-006-004-003 | 4 | DC-L3-004-006-004 | SiC diode | SiC diode 是「PSU 功率半导体」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与通用功率器件节点有交叉，需按用途标记；本行只统计「PSU 功率半导体」内的「SiC diode」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-006-004-004 | 4 | DC-L3-004-006-004 | driver | driver 是「PSU 功率半导体」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：与通用功率器件节点有交叉，需按用途标记；本行只统计「PSU 功率半导体」内的「driver」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-004-006-004-005 | 4 | DC-L3-004-006-004 | package | package 是「PSU 功率半导体」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：与通用功率器件节点有交叉，需按用途标记；本行只统计「PSU 功率半导体」内的「package」，不跨父节点合并。 | P0 | pending_audit |

### DC-L1R-005 热管理与液冷链

| node_id | level | parent_node_id | node_name | 精确定义 | Level 5 候选，不在本轮展开 | 唯一归属与边界 | priority | status |
|---|---:|---|---|---|---|---|---|---|
| DC-L4-005-001-001-001 | 4 | DC-L3-005-001-001 | copper plate | copper plate 是「冷板铜/铝基材」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：只按冷板用途归属；本行只统计「冷板铜/铝基材」内的「copper plate」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-001-002 | 4 | DC-L3-005-001-001 | aluminum plate | aluminum plate 是「冷板铜/铝基材」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只按冷板用途归属；本行只统计「冷板铜/铝基材」内的「aluminum plate」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-001-003 | 4 | DC-L3-005-001-001 | alloy | alloy 是「冷板铜/铝基材」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只按冷板用途归属；本行只统计「冷板铜/铝基材」内的「alloy」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-001-004 | 4 | DC-L3-005-001-001 | surface treatment | surface treatment 是「冷板铜/铝基材」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只按冷板用途归属；本行只统计「冷板铜/铝基材」内的「surface treatment」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-002-001 | 4 | DC-L3-005-001-002 | microchannel | microchannel 是「微通道 / 流道结构」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于 CDU 管路；本行只统计「微通道 / 流道结构」内的「microchannel」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-002-002 | 4 | DC-L3-005-001-002 | fin | fin 是「微通道 / 流道结构」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于 CDU 管路；本行只统计「微通道 / 流道结构」内的「fin」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-002-003 | 4 | DC-L3-005-001-002 | pin-fin | pin-fin 是「微通道 / 流道结构」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：不等于 CDU 管路；本行只统计「微通道 / 流道结构」内的「pin-fin」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-002-004 | 4 | DC-L3-005-001-002 | CNC | CNC 是「微通道 / 流道结构」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：不等于 CDU 管路；本行只统计「微通道 / 流道结构」内的「CNC」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-002-005 | 4 | DC-L3-005-001-002 | etching | etching 是「微通道 / 流道结构」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：不等于 CDU 管路；本行只统计「微通道 / 流道结构」内的「etching」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-003-001 | 4 | DC-L3-005-001-003 | brazing | brazing 是「钎焊 / 扩散焊 / 焊接工艺」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：只服务冷板制造；本行只统计「钎焊 / 扩散焊 / 焊接工艺」内的「brazing」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-003-002 | 4 | DC-L3-005-001-003 | diffusion bonding | diffusion bonding 是「钎焊 / 扩散焊 / 焊接工艺」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：只服务冷板制造；本行只统计「钎焊 / 扩散焊 / 焊接工艺」内的「diffusion bonding」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-003-003 | 4 | DC-L3-005-001-003 | laser welding | laser welding 是「钎焊 / 扩散焊 / 焊接工艺」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：只服务冷板制造；本行只统计「钎焊 / 扩散焊 / 焊接工艺」内的「laser welding」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-003-004 | 4 | DC-L3-005-001-003 | vacuum process | vacuum process 是「钎焊 / 扩散焊 / 焊接工艺」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只服务冷板制造；本行只统计「钎焊 / 扩散焊 / 焊接工艺」内的「vacuum process」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-004-001 | 4 | DC-L3-005-001-004 | plating | plating 是「冷板密封 / 表面处理」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：快接头密封件另列；本行只统计「冷板密封 / 表面处理」内的「plating」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-004-002 | 4 | DC-L3-005-001-004 | coating | coating 是「冷板密封 / 表面处理」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：快接头密封件另列；本行只统计「冷板密封 / 表面处理」内的「coating」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-004-003 | 4 | DC-L3-005-001-004 | gasket | gasket 是「冷板密封 / 表面处理」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：快接头密封件另列；本行只统计「冷板密封 / 表面处理」内的「gasket」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-004-004 | 4 | DC-L3-005-001-004 | surface flatness | surface flatness 是「冷板密封 / 表面处理」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：快接头密封件另列；本行只统计「冷板密封 / 表面处理」内的「surface flatness」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-004-005 | 4 | DC-L3-005-001-004 | corrosion test | corrosion test 是「冷板密封 / 表面处理」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：快接头密封件另列；本行只统计「冷板密封 / 表面处理」内的「corrosion test」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-005-001 | 4 | DC-L3-005-001-005 | pressure test | pressure test 是「冷板压力 / 泄漏测试」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：系统级漏液检测另列；本行只统计「冷板压力 / 泄漏测试」内的「pressure test」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-005-002 | 4 | DC-L3-005-001-005 | helium leak | helium leak 是「冷板压力 / 泄漏测试」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：系统级漏液检测另列；本行只统计「冷板压力 / 泄漏测试」内的「helium leak」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-005-003 | 4 | DC-L3-005-001-005 | flow resistance | flow resistance 是「冷板压力 / 泄漏测试」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：系统级漏液检测另列；本行只统计「冷板压力 / 泄漏测试」内的「flow resistance」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-001-005-004 | 4 | DC-L3-005-001-005 | thermal test | thermal test 是「冷板压力 / 泄漏测试」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：系统级漏液检测另列；本行只统计「冷板压力 / 泄漏测试」内的「thermal test」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-002-001-001 | 4 | DC-L3-005-002-001 | plate heat exchanger | plate heat exchanger 是「CDU 换热器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：Chiller 设施侧设备另列；本行只统计「CDU 换热器」内的「plate heat exchanger」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-002-001-002 | 4 | DC-L3-005-002-001 | microchannel exchanger | microchannel exchanger 是「CDU 换热器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：Chiller 设施侧设备另列；本行只统计「CDU 换热器」内的「microchannel exchanger」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-002-001-003 | 4 | DC-L3-005-002-001 | gasket | gasket 是「CDU 换热器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：Chiller 设施侧设备另列；本行只统计「CDU 换热器」内的「gasket」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-002-002-001 | 4 | DC-L3-005-002-002 | pump | pump 是「CDU 泵组」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：单体泵阀器件另可按 DC-L2-005-004 归属；本行只统计「CDU 泵组」内的「pump」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-002-002-002 | 4 | DC-L3-005-002-002 | motor | motor 是「CDU 泵组」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：单体泵阀器件另可按 DC-L2-005-004 归属；本行只统计「CDU 泵组」内的「motor」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-002-002-003 | 4 | DC-L3-005-002-002 | VFD | VFD 是「CDU 泵组」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：单体泵阀器件另可按 DC-L2-005-004 归属；本行只统计「CDU 泵组」内的「VFD」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-002-002-004 | 4 | DC-L3-005-002-002 | redundancy | redundancy 是「CDU 泵组」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：单体泵阀器件另可按 DC-L2-005-004 归属；本行只统计「CDU 泵组」内的「redundancy」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-002-002-005 | 4 | DC-L3-005-002-002 | seal | seal 是「CDU 泵组」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：单体泵阀器件另可按 DC-L2-005-004 归属；本行只统计「CDU 泵组」内的「seal」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-002-004-001 | 4 | DC-L3-005-002-004 | controller | controller 是「CDU 控制器 / 传感器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：数据中心 DCIM 软件不在此列；本行只统计「CDU 控制器 / 传感器」内的「controller」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-002-004-002 | 4 | DC-L3-005-002-004 | temperature sensor | temperature sensor 是「CDU 控制器 / 传感器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：数据中心 DCIM 软件不在此列；本行只统计「CDU 控制器 / 传感器」内的「temperature sensor」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-002-004-003 | 4 | DC-L3-005-002-004 | pressure sensor | pressure sensor 是「CDU 控制器 / 传感器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：数据中心 DCIM 软件不在此列；本行只统计「CDU 控制器 / 传感器」内的「pressure sensor」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-002-004-004 | 4 | DC-L3-005-002-004 | flow meter | flow meter 是「CDU 控制器 / 传感器」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：数据中心 DCIM 软件不在此列；本行只统计「CDU 控制器 / 传感器」内的「flow meter」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-005-001-001 | 4 | DC-L3-005-005-001 | quick disconnect | quick disconnect 是「快速断开接头 / QD」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：普通管件不在此列；本行只统计「快速断开接头 / QD」内的「quick disconnect」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-005-001-002 | 4 | DC-L3-005-005-001 | valve core | valve core 是「快速断开接头 / QD」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 功能模块、接口协议、验证 IP、时钟/功耗、可靠性测试。 | 继承父节点边界：普通管件不在此列；本行只统计「快速断开接头 / QD」内的「valve core」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-005-001-003 | 4 | DC-L3-005-005-001 | locking mechanism | locking mechanism 是「快速断开接头 / QD」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：普通管件不在此列；本行只统计「快速断开接头 / QD」内的「locking mechanism」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-005-001-004 | 4 | DC-L3-005-005-001 | plating | plating 是「快速断开接头 / QD」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 关键设备、工艺步骤、耗材/材料、尺寸/良率指标、可靠性验证。 | 继承父节点边界：普通管件不在此列；本行只统计「快速断开接头 / QD」内的「plating」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-005-002-001 | 4 | DC-L3-005-005-002 | EPDM | EPDM 是「O-ring / 密封材料」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：只按液冷密封用途归属；本行只统计「O-ring / 密封材料」内的「EPDM」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-005-002-002 | 4 | DC-L3-005-005-002 | FKM | FKM 是「O-ring / 密封材料」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：只按液冷密封用途归属；本行只统计「O-ring / 密封材料」内的「FKM」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-005-002-003 | 4 | DC-L3-005-005-002 | silicone | silicone 是「O-ring / 密封材料」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料牌号、配方体系、纯度/损耗/热膨胀指标、供应稳定性、可靠性验证。 | 继承父节点边界：只按液冷密封用途归属；本行只统计「O-ring / 密封材料」内的「silicone」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-005-002-004 | 4 | DC-L3-005-005-002 | compression set | compression set 是「O-ring / 密封材料」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只按液冷密封用途归属；本行只统计「O-ring / 密封材料」内的「compression set」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-005-002-005 | 4 | DC-L3-005-005-002 | compatibility test | compatibility test 是「O-ring / 密封材料」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：只按液冷密封用途归属；本行只统计「O-ring / 密封材料」内的「compatibility test」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-005-005-001 | 4 | DC-L3-005-005-005 | cycle test | cycle test 是「寿命 / 泄漏可靠性测试」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：只服务连接密封可靠性；本行只统计「寿命 / 泄漏可靠性测试」内的「cycle test」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-005-005-002 | 4 | DC-L3-005-005-005 | leak test | leak test 是「寿命 / 泄漏可靠性测试」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：只服务连接密封可靠性；本行只统计「寿命 / 泄漏可靠性测试」内的「leak test」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-005-005-003 | 4 | DC-L3-005-005-005 | pressure pulse | pressure pulse 是「寿命 / 泄漏可靠性测试」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 核心设备、夹具/耗材、工艺窗口、良率指标、维护与校准。 | 继承父节点边界：只服务连接密封可靠性；本行只统计「寿命 / 泄漏可靠性测试」内的「pressure pulse」，不跨父节点合并。 | P0 | pending_audit |
| DC-L4-005-005-005-004 | 4 | DC-L3-005-005-005 | chemical compatibility | chemical compatibility 是「寿命 / 泄漏可靠性测试」的 Level 4 子环节，直接支撑其产品、材料、工艺、设备或功能实现。 | 材料/器件、工艺设备、测试指标、供应商资格、失效模式。 | 继承父节点边界：只服务连接密封可靠性；本行只统计「寿命 / 泄漏可靠性测试」内的「chemical compatibility」，不跨父节点合并。 | P0 | pending_audit |

## 后续审计重点

| 审计重点 | 要求 |
|---|---|
| P0 批次边界 | 确认本表仅来自 Level 3 P0 父节点，不误拉 P1/P2。 |
| 子节点粒度 | 检查 Level 4 是否已经拆到可继续追踪材料、器件、工艺、设备或测试项的颗粒度。 |
| 跨链重复 | PCB、功率器件、测试、材料、结构件等节点仍需按父节点用途区分。 |
| 是否可继续下钻 | 审计后决定通过节点是否进入 Level 5，或先补完 Level 4 P1/P2。 |

## 机器可读状态

```yaml
artifact_type: ai_chain_level_mapping
task_type: mapping
mapping_date: 2026-05-31
current_level: 4
batch_scope: level_3_p0_only
parent_audit: docs/ai_chain_disassembly/level_03_audit_2026-05-31.md
parent_level_file: docs/ai_chain_disassembly/level_03_from_level_02_audit_approved_2026-05-31.md
root_node_id: DC-000
level_3_parent_nodes_used: 67
level_4_total_nodes: 283
level_3_priority_scope: P0
level_3_p1_p2_not_yet_mapped: true
next_required_task: audit_level_4_p0_batch
status: pending_audit
may_enter_next_level: false
live_data_used: false
stock_mapping_included: false
```
