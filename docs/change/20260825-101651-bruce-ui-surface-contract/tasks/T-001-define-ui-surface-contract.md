# Task T-001: 定义技术无关 UI Surface Contract

- Contract revision: 1
- Contract state: frozen before execution
- Status source: `../checkpoint.yaml`
- Parent plan: `../plan.md`

## Objective

为原型和 existing-product extension 建立不依赖 React/Vue/其他框架的页面表面契约，明确页面区域、信息层级、状态、交互、可观察字段、布局不变量、视觉锚点、视口和证据方法。

## Included scope

- `skills/write-prototype/SKILL.md`
- `skills/write-prototype/templates/prototype-brief.md`
- `skills/write-prototype/templates/repository-ui-contract.md`
- `skills/write-prototype/templates/prototype-manifest.md`
- `skills/write-prototype/references/ui-surface-contract.md`（新增）

## Excluded scope

- 不要求或生成 React component tree、DOM tree 或框架 AST。
- 不修改 validator、Design Gate、Completion Gate 实现；这些由后续任务负责。
- 不修改 Joytime 仓库或当前 RadarPage。

## Dependencies

- Depends on: none
- Consumes: 当前 `write-prototype` 模板、`repository-ui-contract` 的 layout/reuse/visual anchor 结构、线程中的雷达差距事实
- Produces: Surface Contract 字段定义、Surface ID 规则、实现入口和运行时证据的技术无关表达

## Acceptance

- Parent scenario ids: UI-SURFACE-01
- Given: 一个 existing-product extension 原型
- When: 使用新的 brief/UI contract 模板描述页面
- Then: 文档能够独立记录 surface、region/hierarchy、required states、interactions、observables、layout invariants、visual anchors、viewports 和 evidence；实现入口只能作为可选定位信息，不能要求某个框架
- Evidence: 模板 diff、`ui-surface-contract.md`、契约测试预期字段清单

## Verification

- Required layer: contract
- Commands/checks: `python3 -m unittest tests.test_prototype_contract`
- Environment: none

## Authorization and risks

- Authorization: normal
- Risk trigger: guarded；修改原型文档合同和模板字段
- Stop condition: 如果字段与现有 manifest/Design Gate 语义冲突，停止并返回 contract revision，不进入 validator 或 Gate 接入

## Contract change rule

Do not silently widen this task. If scope, acceptance, dependency, authorization, or required verification changes, create a new contract revision or a superseding task and record the reason in the next checkpoint.
