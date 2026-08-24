# Task T-002: 增加 Profile、Packet schema 与静态校验

- Contract revision: 1
- Contract state: frozen before execution
- Status source: `../checkpoint.yaml`
- Parent plan: `../plan.md`

## Objective

提供可导入的 Profile/Packet 校验与模型解析函数，并提供命令行 validator。

## Included scope

- `scripts/functional_agent_profiles.py`、`scripts/validate_functional_agents.py`。
- `skills/bruce/references/model-profiles.yaml`、`functional-agent-contracts.md`。
- `tests/test_functional_agent_profiles.py`。

## Excluded scope

- 不调用真实 Subagent，不安装插件，不写用户/项目覆盖文件。

## Dependencies

- Depends on: T-001
- Consumes: v1 registry/packet contract
- Produces: resolver API、validator、契约 fixtures

## Acceptance

- Parent scenario ids: FA-01, FA-02, FA-04, FA-06
- Given: registry、覆盖层或 Packet 可能非法
- When: 运行 resolver/validator
- Then: 合法输入通过，未知字段、版本、路径、权限和 Gate 字段 fail closed；fallback 状态可审计
- Evidence: `tests/test_functional_agent_profiles.py`、validator output

## Verification

- Required layer: unit/contract
- Commands/checks: `python3 -m unittest tests.test_functional_agent_profiles`、`python3 scripts/validate_functional_agents.py`
- Environment: Python 3 + PyYAML

## Authorization and risks

- Authorization: normal
- Risk trigger: guarded；解析结果影响宿主调用参数
- Stop condition: resolver contract 失败时不迁移 Skill 路由

## Contract change rule

Do not silently widen this task. If scope, acceptance, dependency, authorization, or required verification changes, create a new contract revision or a superseding task and record the reason in the next checkpoint.
