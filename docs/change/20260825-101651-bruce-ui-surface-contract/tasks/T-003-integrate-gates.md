# Task T-003: 接入 Design Gate 与 Completion Gate

- Contract revision: 1
- Contract state: frozen before execution
- Status source: `../checkpoint.yaml`
- Parent plan: `../plan.md`

## Objective

将 Surface Contract 完整性、生产实现入口映射和当前运行时证据接入 Design Gate 与 Completion Gate，同时保持现有唯一 verdict、visual_scope 和证据层级规则。

## Included scope

- `skills/design-gate/SKILL.md`
- `skills/completion-gate/SKILL.md`
- `skills/bruce/references/verification-loop.md`
- `tests/test_design_gate_validator.py`
- `tests/test_completion_contract.py`
- `tests/test_prototype_contract.py`

## Excluded scope

- 不新增第三个 Gate 或独立 Completion verdict。
- 不把 DOM 文本、原型截图、provider score 或静态 validator clearance 当作生产页面完成证据。
- 不修改 Open Design provider、浏览器宿主、Joytime 源码或部署流程。

## Dependencies

- Depends on: T-001, T-002
- Consumes: surface validator 输出、radar findings、`chrome-smoke`/`chrome-layout` 现有规则
- Produces: Design readiness blocker 规则、Completion review-matrix Surface ID 行、缺证据时的 issues/blocked 边界和契约测试

## Acceptance

- Parent scenario ids: UI-SURFACE-04, UI-SURFACE-05
- Given: governing prototype 存在但 surface contract 缺失或有占位字段
- When: Design Gate 评估
- Then: 设计进入实现前被阻塞，并指出具体 surface/region/field，而不是仅报告 prototype 文件存在
- Given: surface contract 已存在但某个 Surface ID 没有实现入口、当前运行时证据或 layout evidence
- When: Completion Gate 评估
- Then: Completion 不能为 `pass`；按现有外部状态规则返回 `issues` 或 `blocked`
- Given: Web 的 `chrome-layout` 场景
- When: 评估 material visible outcome
- Then: 仍要求当前 Chrome 的交互、截图、几何/溢出和区域证据；不允许以 DOM text alone 替代
- Evidence: Gate skill diff、Design/Completion negative fixtures、目标契约测试

## Verification

- Required layer: contract/integration
- Commands/checks: `python3 -m unittest tests.test_design_gate_validator tests.test_completion_contract tests.test_prototype_contract`
- Environment: none for contract tests; real Chrome remains an execution-time requirement for actual UI acceptance

## Authorization and risks

- Authorization: normal
- Risk trigger: guarded；会改变 Design/Completion readiness 判定和既有 artifact 的进入/完成边界
- Stop condition: 任一现有唯一 verdict、visual_scope 或 provenance invariant 被破坏，停止并返回 issues，不继续扩展规则

## Contract change rule

Do not silently widen this task. If scope, acceptance, dependency, authorization, or required verification changes, create a new contract revision or a superseding task and record the reason in the next checkpoint.
