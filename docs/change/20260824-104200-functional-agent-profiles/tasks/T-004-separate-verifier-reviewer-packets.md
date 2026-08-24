# Task T-004: 分离 Verifier 与 Reviewer 证据边界

- Contract revision: 1
- Contract state: frozen before execution
- Status source: `../checkpoint.yaml`
- Parent plan: `../plan.md`

## Objective

为验证和审查建立互斥的 `verification_packet`/`review_packet` 输出合同，继续由 Gate 输出唯一 terminal verdict。

## Included scope

- `skills/completion-gate/**`、`skills/plan-review/**`、`skills/design-gate/**`、references 与契约测试。

## Excluded scope

- 不改变 Gate 的 verdict token、独立审查触发条件或最终权限。

## Dependencies

- Depends on: T-002
- Consumes: `verifier`/`reviewer` Profile 与 Packet schema
- Produces: Gate 输入边界与静态禁止项

## Acceptance

- Parent scenario ids: FA-02, FA-03, FA-04, FA-06
- Given: 实现已返回候选结果
- When: Verifier/Reviewer 运行
- Then: 各自只返回对应 Packet，不返回 Design/Completion verdict；Reviewer 使用 clean context 并记录 model_resolution
- Evidence: completion/design/plan-review Skill 与契约测试

## Verification

- Required layer: unit/contract + completion smoke
- Commands/checks: `python3 -m unittest tests.test_functional_agent_profiles tests.test_completion_contract`
- Environment: 真实独立审查 smoke 需当前 Codex 宿主，未执行不伪装通过

## Authorization and risks

- Authorization: normal
- Risk trigger: guarded；影响独立审查可信度
- Stop condition: Gate 权威边界被破坏时停止并回退

## Contract change rule

Do not silently widen this task. If scope, acceptance, dependency, authorization, or required verification changes, create a new contract revision or a superseding task and record the reason in the next checkpoint.
