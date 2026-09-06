# 方案落盘后自动执行 Design Gate

## 目标

当 Bruce 在设计或实现任务中将会约束后续实现的方案工件成功落盘并完成本地文档检查后，必须在同一轮工作流内自动衔接 `design-gate`，不得停下来要求用户再次输入“执行 Design Gate”。

## 验收条件

- AC-01：`skills/bruce/SKILL.md` 明确规定，下游治理型设计工件落盘后，Bruce 必须在同一轮自动运行 `design-gate`，不需要新的用户指令。
- AC-02：`write-architecture`、`write-db-design`、`write-plan`、`write-prototype`、`write-tests` 在适用时返回强制 Gate handoff；文档作者不自行裁决 Design verdict，但也不得把 Gate 留给下一轮用户触发。
- AC-03：自动衔接仅适用于 artifact policy 判定为治理型设计或下游合同的工件；单纯执行清单、进度说明、普通文档编辑或尚未确认且不可治理的原型不误触发 Design Gate。
- AC-04：Design Gate 不扩大实施授权。`design-only` 在 Gate 结果后停止；已经明确授权的 implementation scope 可在 `Design: pass` 后继续，`Design: blocked` 时停止受影响实现。
- AC-05：契约测试覆盖自动衔接、职责边界、无需追加用户指令和非适用场景，并通过全量插件验证。

## 范围

允许修改 Bruce 核心工作流、方案写入类 Skill、artifact policy、README/CONTEXT、对应契约测试和本变更工件。不得新增第三个 Gate、后台执行器、Hook 自动裁决、数据库/CI/依赖变更，也不得把普通计划持久化等同于治理型设计。

## 交付边界

本次仅修改 Bruce 插件源码并刷新本地插件缓存；不提交、不推送、不启动服务。插件刷新后的新行为需在新建 Codex 会话中生效。
