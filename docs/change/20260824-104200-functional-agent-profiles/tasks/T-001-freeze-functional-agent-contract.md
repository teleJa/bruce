# Task T-001: 冻结 Functional Agent 与 Model Profile 公共合同

- Contract revision: 1
- Contract state: frozen before execution
- Status source: `../checkpoint.yaml`
- Parent plan: `../plan.md`

## Objective

冻结 Profile/Packet v1 的字段、四类角色、覆盖层级、宿主映射和 Gate 权威边界。

## Included scope

- `architecture.md`、`api-contracts.md`、`functional-agent-contracts.md`、`model-profiles.yaml`。
- `tasks/` 中本变更的执行合同。

## Excluded scope

- 不修改既有 Skill 行为；不写用户级配置；不引入 Runtime、数据库或外部交付。

## Dependencies

- Depends on: none
- Consumes: `plan.md` 与现有 Skill/测试事实
- Produces: v1 合同和 registry 输入

## Acceptance

- Parent scenario ids: FA-01, FA-02, FA-03, FA-04, FA-06
- Given: Bruce 需要跨 Skill 委派
- When: 读取公共合同
- Then: Profile、Packet、fallback、权限和 Gate 边界可被 validator 直接执行
- Evidence: `architecture.md`、`api-contracts.md`、`functional-agent-contracts.md`

## Verification

- Required layer: document + Design Gate
- Commands/checks: `python3 skills/design-gate/scripts/validate_design_review.py --change-dir docs/change/20260824-104200-functional-agent-profiles`
- Environment: none

## Authorization and risks

- Authorization: normal
- Risk trigger: guarded；公共合同影响多个 Skill
- Stop condition: 合同未通过 Design Gate 时不得实施行为路由

## Contract change rule

Do not silently widen this task. If scope, acceptance, dependency, authorization, or required verification changes, create a new contract revision or a superseding task and record the reason in the next checkpoint.
