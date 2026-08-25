# Task T-002: 实现 Surface Contract 校验与跨栈 fixtures

- Contract revision: 1
- Contract state: frozen before execution
- Status source: `../checkpoint.yaml`
- Parent plan: `../plan.md`

## Objective

实现独立的 surface contract validator，校验页面表面契约的结构、唯一性、证据字段和实现映射；使用临时契约样例覆盖缺失 Surface ID、重复 ID、占位字段和不完整证据，不提交产品场景 fixture。

## Included scope

- `scripts/validate_surface_contract.py`（新增）
- `tests/test_surface_contract.py`（新增）
- `tests/test_prototype_contract.py`（必要的合同断言补充）
- 不新增或提交 Radar、stack-neutral、negative fixture 文件；测试运行时生成最小临时契约

## Excluded scope

- 不修改 `scripts/validate_prototype_artifact.py` 的视觉 token 职责。
- 不解析 React/Vue/Angular AST，不比较 DOM 树，不运行真实 Joytime 页面。
- 不修改 Design Gate 或 Completion Gate 文本合同；由 T-003 负责。

## Dependencies

- Depends on: T-001
- Consumes: Surface Contract schema、Surface ID 和 evidence field definitions
- Produces: validator CLI/API、临时契约测试、清晰的 finding 格式

## Acceptance

- Parent scenario ids: UI-SURFACE-02, UI-SURFACE-03, UI-SURFACE-06（按用户范围调整，不提交场景 fixture）
- Given: 一个最小 surface contract
- When: 运行 validator
- Then: 完整契约通过，缺失、重复、占位字段或不完整 evidence mapping 返回 findings
- Given: 一个通用实现 locator
- When: 映射到 Surface ID
- Then: validator 不要求 React 或其他框架结构
- Evidence: `python3 scripts/validate_surface_contract.py ...` 输出和临时契约测试结果

## Verification

- Required layer: unit/validator
- Commands/checks: `python3 -m unittest tests.test_surface_contract tests.test_prototype_contract`
- Environment: none

## Authorization and risks

- Authorization: normal
- Risk trigger: guarded；新增结构化 validator 可能改变 artifact readiness 结果
- Stop condition: 如果 validator 需要框架解析或无法区分缺失契约与缺失运行时证据，停止并回到 T-001 修订语义边界

## Contract change rule

Do not silently widen this task. If scope, acceptance, dependency, authorization, or required verification changes, create a new contract revision or a superseding task and record the reason in the next checkpoint.
