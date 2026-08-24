# Task T-005: 接入 Profile 覆盖、显式 override 与当前模型 fallback

- Contract revision: 1
- Contract state: frozen before execution
- Status source: `../checkpoint.yaml`
- Parent plan: `../plan.md`

## Objective

实现 task/project/user/built-in 覆盖合并与宿主参数解析，目标模型不可用时显式 fallback 到 current model。

## Included scope

- `scripts/functional_agent_profiles.py`、相关 Skill 的 resolver 说明与 references、契约测试。

## Excluded scope

- 不写入 `~/.codex/bruce/model-profiles.yaml`；不修改 `.bruce/config.yaml`；不推断真实模型已生效。

## Dependencies

- Depends on: T-002, T-003, T-004
- Consumes: Profile/Packet 合同与所有路由声明
- Produces: `model_resolution`、host spawn args、fallback matrix

## Acceptance

- Parent scenario ids: FA-03, FA-06, FA-07
- Given: Profile 目标模型、覆盖层或宿主能力不同
- When: 解析委派
- Then: precedence、resolved/fallback/degraded/blocked、effective_model 和原因完整且无静默丢失
- Evidence: resolver tests、model-resolution fixture、静态 Skill contract

## Verification

- Required layer: unit/contract + model-resolution smoke
- Commands/checks: `python3 -m unittest tests.test_functional_agent_profiles`
- Environment: 真实宿主 override/fallback 需单独记录

## Authorization and risks

- Authorization: normal
- Risk trigger: guarded；影响成本、延迟和独立性语义
- Stop condition: 实际宿主能力无法被证据确认时只保留 degraded/blocked，不声称 resolved

## Contract change rule

Do not silently widen this task. If scope, acceptance, dependency, authorization, or required verification changes, create a new contract revision or a superseding task and record the reason in the next checkpoint.
