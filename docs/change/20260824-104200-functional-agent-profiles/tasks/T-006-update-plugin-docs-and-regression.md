# Task T-006: 更新插件文档、元数据与全量回归

- Contract revision: 1
- Contract state: frozen before execution
- Status source: `../checkpoint.yaml`
- Parent plan: `../plan.md`

## Objective

更新 README/CONTEXT/plugin metadata 的合同说明并执行全量回归，区分代码验证与真实宿主/外部交付证据。

## Included scope

- `README.md`、`CONTEXT.md`、`.codex-plugin/plugin.json`、测试文件。

## Excluded scope

- 不安装/刷新插件，不修改 marketplace，不 commit/push/deploy/Chrome。

## Dependencies

- Depends on: T-003, T-004, T-005
- Consumes: 已验证的 Profile/Packet 路由与 resolver
- Produces: 文档、元数据与全量验证结果

## Acceptance

- Parent scenario ids: FA-07
- Given: 功能型 Agent 改造已完成
- When: 执行静态、契约、插件与 diff 检查
- Then: 所有仓库内检查有独立结果，真实 smoke/插件安装/Chrome/部署/交付明确标记执行状态
- Evidence: unittest、plugin validator、functional validator、git diff check

## Verification

- Required layer: repository/full
- Commands/checks: `python3 -m unittest discover -s tests -p 'test_*.py'`; `python3 scripts/validate_plugin.py`; `python3 scripts/validate_functional_agents.py`; `git diff --check`
- Environment: none for static checks

## Authorization and risks

- Authorization: normal
- Risk trigger: guarded；跨文档/插件合同回归
- Stop condition: 任一全量检查失败则返回 issues，不进行外部交付

## Contract change rule

Do not silently widen this task. If scope, acceptance, dependency, authorization, or required verification changes, create a new contract revision or a superseding task and record the reason in the next checkpoint.
