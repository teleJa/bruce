# 实施计划：Bruce 验证—反馈—修复循环基础设施

## Task contract

- Objective：在 Bruce 工作流内部建立项目自适应的验证循环基础设施，使本地验证、CNB/部署、客户端/Web 验证和用户手测都能通过统一状态、证据、反馈、修复、阻塞通知和恢复协议接入；不把任何项目环境硬编码到 Bruce 核心。
- Scope：验证循环状态与事件契约、Project Verification Profile/Adapter 边界、用户手测 handoff、阻塞通知与显式恢复、Checkpoint/Goal/Completion 映射、契约测试和文档。
- Excluded：Multica/Joytime 具体 Adapter、CNB/Temporal/Kubernetes/Electron runtime、业务代码、数据库和远程部署。
- Acceptance：AC-001 至 AC-007；详细验证见 `test-plan.md`。
- Topology：full；涉及 Bruce workflow、verification loop、failure recovery、checkpoint、Goal、Completion Gate 和多个 supporting contract。
- Risk：guarded；错误的状态转换可能让外部验证被误报为通过，或在阻塞状态下继续写入。
- Execution：sequential；先冻结协议和状态，再实现验证器/适配器边界，最后接入项目。

## Task package

- Path: `tasks/`
- Index: `tasks/index.yaml`
- Status source: future implementation uses the same change-level `checkpoint.yaml`
- Contract state: each Task file is frozen before its task starts; status is not written into the Task file

## Task summary

| Task ID | Title | Depends on | Acceptance IDs | Verification |
|---|---|---|---|---|
| T-001 | 冻结验证循环状态与事件协议 | none | AC-001, AC-003, AC-004, AC-005, AC-007 | contract/schema tests |
| T-002 | 定义 Project Verification Profile 与 Adapter 边界 | T-001 | AC-002, AC-003, AC-006 | profile/adapter contract tests |
| T-003 | 接入阻塞通知、用户交接与恢复语义 | T-001, T-002 | AC-003, AC-004, AC-005, AC-006 | handoff/resume/failure tests |
| T-004 | 更新 Bruce 文档、checkpoint 与 Gate 回归 | T-001, T-002, T-003 | AC-001, AC-004, AC-007 | full contract validation |

## 关键决策

1. `waiting_external` 与 `waiting_user` 表示计划内等待，不等于 `blocked`，但都不能产生 `pass`。
2. `blocked` 发生后必须通知用户并冻结受影响 batch；用户显式恢复后才可继续。
3. 恢复不重置 retry/repair 预算，不删除失败证据，不改变 contract revision。
4. Profile/Adapter 提供项目环境事实；Bruce 统一解释反馈、执行恢复策略并交给 Gate 作终局判断。
5. 不在 Bruce 核心中内置 CNB、Temporal、Electron 或任何具体项目命令。

## 交付边界

本设计阶段只产出文档和契约测试设计，未实现 Loop Runtime、Adapter 或项目接入；不提交、不推送、不刷新插件缓存、不触发外部构建或部署。
