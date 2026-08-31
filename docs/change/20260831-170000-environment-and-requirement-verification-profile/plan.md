# 实施计划：Environment Profile 与需求级 Verification Profile

## Task contract

- Objective：新增可复用且默认未确认的 Environment Profile，改造 `$verification-profile` 为强制绑定 `requirements.md` 的需求级验证与修复 Profile。
- Scope：两个 Profile 的 schema、确认/失效状态、用户补充信息、账号与 Credential 安全边界、Skill/capability 选择、需求 Acceptance 映射、阻塞恢复、静态 Profile validator、模板、文档和契约测试。
- Excluded：项目 Adapter、CNB/部署/客户端执行器、Verification Run runtime、业务代码、数据库 schema 和远程环境操作。
- Acceptance：AC-001 至 AC-009；详细验证见 `test-plan.md`。
- Topology：full；跨 supporting skills、workflow references、templates、profile lifecycle 和 Completion ownership。
- Risk：guarded；Profile 错误确认或 stale 处理可能导致错误环境、账号或证据被用于需求验收。
- Execution：sequential；先冻结 schema/lifecycle，再实现两个 Skill，最后补文档和契约回归。

## Task package

- Path: `tasks/`
- Index: `tasks/index.yaml`
- Status source: future implementation uses the same change-level `checkpoint.yaml`
- Contract state: each Task file is frozen before its task starts; status is not written into the Task file

## Task summary

| Task ID | Title | Depends on | Acceptance IDs | Verification |
|---|---|---|---|---|
| T-001 | 冻结 Profile schema、来源与确认生命周期 | none | AC-001, AC-005, AC-006, AC-008, AC-009 | schema and lifecycle contract tests |
| T-002 | 新增 environment-profile skill | T-001 | AC-001, AC-002, AC-006, AC-008 | skill metadata, template and security tests |
| T-003 | 改造 verification-profile 为需求级生成 | T-001, T-002 | AC-003, AC-004, AC-005, AC-006, AC-007, AC-008 | requirements binding and mapping tests |
| T-004 | 接入 Bruce workflow 文档与回归 | T-001, T-002, T-003 | AC-007, AC-009 | full contract validation |

## 关键决策

1. `requirements.md` 是 `$verification-profile` 的强制输入；没有路径时返回 `Missing requirements input`，不生成需求级 Profile。
2. Environment Profile 和 Requirement Verification Profile 默认 `confirmation.state=pending`；确认是用户输入授权，不新增第三个 Gate。
3. Environment Profile 保存可复用环境事实和安全 Credential 引用；Requirement Verification Profile 保存当前需求的 AC 到环境/账号/Skill/证据/修复映射。
4. Profile 的动态执行结果进入 Verification Run/Checkpoint，不回写静态 Profile。
5. Profile stale、账号状态不明、部署 revision 不匹配或外部状态未知时，停止受影响范围、通知用户并要求显式恢复。
6. Adapter/Skill 只返回能力事实和证据，Completion Gate 仍是唯一最终判断。

## 交付边界

实现阶段只修改 Bruce Skill、references、templates、契约测试和文档；不接入 Multica/Joytime 环境，不触发 CNB/部署，不读取或落盘秘密值。
