# Implementation plan: Bruce 设计产物完整性门禁

## Task contract

- Objective: 恢复设计阶段的通用产物完整性门禁，使产物生成/跳过及其证据在设计目录同级可审计。
- Scope: 新增 artifact gate skill/模板，修改 Bruce、Goal、数据库设计和完成复核契约，更新插件版本、README、测试与本 change 文档；不修改业务数据库、本机插件安装或历史任务目录。
- Acceptance:
  - AR-01: Given full 或存在下游设计真源的任务；When 准备进入实现；Then 同级 `artifact-review.md` 列出完整候选集合并通过；Evidence: contract tests 和本目录门禁文件。
  - AR-02: Given 必需产物缺失或 skipped 无仓库证据；When 执行 artifact gate；Then 阻止进入实现；Evidence: `tests/test_supporting_skill_contracts.py`。
  - AR-03: Given Goal-backed full 任务；When 进入执行阶段；Then Goal 只消费门禁路径/结论，`execute_record.md` 不承载设计取舍；Evidence: `tests/test_execution_contract.py`。
  - AR-04: Given 实现后最终 diff 扩大设计影响；When 完成复核；Then 过期门禁返回 issues；Evidence: `tests/test_completion_contract.py`。
- Constraints: 保留按需生成设计内容的原则；不恢复固定 clarification/architecture/plan/test-plan 链；不把门禁文件当运行状态。
- Topology: full，涉及 Bruce 主路由、支持 skill、Goal 和 completion 四个契约边界。
- Risk: guarded，改变插件的公共工作流和文件契约。

## Repository evidence

- [`skills/bruce/SKILL.md`](../../../skills/bruce/SKILL.md) — 当前设计选择后直接进入 Goal/实现。
- [`skills/goal-execution-gate/SKILL.md`](../../../skills/goal-execution-gate/SKILL.md) — 此前未提交修改错误地把 test-design 决策写进执行记录。
- [`skills/write-db-design/SKILL.md`](../../../skills/write-db-design/SKILL.md) — `not needed` 只返回会话。
- [`tests/test_supporting_skill_contracts.py`](../../../tests/test_supporting_skill_contracts.py) — 可承载新 skill 与门禁静态契约。

## Tasks

### artifact-gate-1

- Title: 新增 artifact review gate 与模板
- Component: design governance
- Depends on: `artifact-review-file-v1`
- Parallel safe: false
- Files/scope: `skills/artifact-review-gate/**`
- Consumes: task contract、change directory、设计能力输出、D0/D1
- Produces: 同级 `artifact-review.md` 和 `pass|blocked`
- Detail: 固定候选集合、状态语义、证据要求、落盘位置、重跑规则和阻塞条件。
- Acceptance: AR-01、AR-02
- Verification: contract tests、plugin validator

### artifact-gate-2

- Title: 将 Bruce 设计到实现路由接入门禁
- Component: workflow routing
- Depends on: artifact-gate-1
- Parallel safe: false
- Files/scope: `skills/bruce/SKILL.md`、`skills/write-db-design/SKILL.md`
- Consumes: `artifact-review-file-v1`
- Produces: 设计能力 -> artifact gate -> Goal/实现的明确顺序
- Detail: full 和持久化下游设计真源的 standard 任务必须先通过门禁；test-design skip evidence 进入同级门禁。
- Acceptance: AR-01、AR-02
- Verification: workflow/supporting skill contract tests

### artifact-gate-3

- Title: 收紧 Goal 与完成复核边界
- Component: execution and completion
- Depends on: artifact-gate-2
- Parallel safe: false
- Files/scope: `skills/goal-execution-gate/SKILL.md`、`skills/verify-completion/SKILL.md`
- Consumes: artifact gate path/verdict
- Produces: 执行记录职责收敛、最终 diff 时效性复核
- Detail: Goal 不保存候选决策；completion 检查门禁文件存在、当前且覆盖实际 diff。
- Acceptance: AR-03、AR-04
- Verification: execution/completion contract tests

### artifact-gate-4

- Title: 更新历史设计说明和回归测试
- Component: docs and tests
- Depends on: artifact-gate-1、artifact-gate-2、artifact-gate-3
- Parallel safe: false
- Files/scope: `.codex-plugin/plugin.json`、`README.md`、`docs/change/**`、`tests/**`
- Consumes: 新工作流契约
- Produces: 防止门禁再次退化的回归覆盖
- Detail: 修正“无固定 artifact gate”的过宽表述，保留内容按需生成并增加完整性门禁。
- Acceptance: AR-01、AR-02、AR-03、AR-04
- Verification: 定向测试、完整 unittest、validator、`git diff --check`

## Dependency and risk notes

- artifact gate 必须先于 Goal 和行为实现，completion 再按最终 diff 二次校验。
- `artifact-review.md` 是设计审计文件，不是运行状态或第二份执行 ledger。
- 本次没有数据库、迁移、生产或外部写入。

## Whole-change verification

- AR-01 -> full 任务完整列举候选设计产物 -> component -> `tests/test_workflow_profiles.py`
- AR-02 -> 缺失或无证据时阻塞 -> component -> `tests/test_supporting_skill_contracts.py`
- AR-03 -> Goal 只消费路径/结论 -> component -> `tests/test_execution_contract.py`
- AR-04 -> completion 拒绝过期门禁 -> component -> `tests/test_completion_contract.py`

## Delivery boundary

- 仅修改当前工作区并验证；不提交、不推送、不刷新本机已安装插件。
