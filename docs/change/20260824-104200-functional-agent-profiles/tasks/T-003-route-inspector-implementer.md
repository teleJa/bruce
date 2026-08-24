# Task T-003: 接入 Inspector 与 Implementer 路由

- Contract revision: 1
- Contract state: frozen before execution
- Status source: `../checkpoint.yaml`
- Parent plan: `../plan.md`

## Objective

让 Inspector、Implementer 和 prototype generation worker 明确声明 Profile/Task Packet，并保持只读/限定路径边界。

## Included scope

- `skills/bruce/SKILL.md`、`skills/inspect-parallel/**`、`skills/spawn-execute/**`、`skills/explore-prototype/**`。

## Excluded scope

- 不改变 Goal/Design/Completion 数量；不自建模型 selector/runtime。

## Dependencies

- Depends on: T-002
- Consumes: `inspector`/`implementer` Profile 与 Task Packet validator
- Produces: 路由静态合同

## Acceptance

- Parent scenario ids: FA-02, FA-05, FA-06
- Given: Inspector 或 Implementer 被委派
- When: Skill 构造委派输入
- Then: Profile ID、Packet、允许/禁止工具、写入范围和 stop condition 明确；主 Agent 保留综合权
- Evidence: Skill 文本与路由契约测试

## Verification

- Required layer: unit/contract + native-subagent smoke
- Commands/checks: `python3 -m unittest tests.test_functional_agent_profiles`
- Environment: 真实 smoke 需当前 Codex 宿主，未执行不伪装通过

## Authorization and risks

- Authorization: normal
- Risk trigger: guarded；实施 Agent 获得有限写权限
- Stop condition: 发现越权或未映射调用点时停止迁移

## Contract change rule

Do not silently widen this task. If scope, acceptance, dependency, authorization, or required verification changes, create a new contract revision or a superseding task and record the reason in the next checkpoint.
