# Implementation plan: Bruce 技术无关 UI Surface Contract 与原型对齐验收

## Task contract

- Objective: 将 Bruce 对用户可见页面的控制从“原型自身视觉断言 + 宿主几何检查 + 用户流程验证”补强为技术栈无关的 UI Surface Contract。契约必须明确页面/区域层级、默认与异常状态、可观察字段、交互转换、布局不变量、视口和证据，并要求 Design Gate 与 Completion Gate 将每个 Surface ID 映射到仓库实现入口和当前运行时证据；不要求 React、Vue 或任何特定组件树。
- Scope:
  - Included:
    - 为 `write-prototype` 增加技术无关的 surface/region/state/interaction/observable/layout/evidence 语义和模板字段。
    - 增加独立于 `visual-assertions.json` 的 surface contract 校验能力；保留现有精确颜色、尺寸、品牌文案和 forbidden token 校验的职责边界。
    - 将 surface contract 的完整性、实现入口映射和证据新鲜度接入 Design Gate/Completion Gate 的文字合同与契约测试。
    - 通过 validator 契约测试覆盖 Surface ID 缺失、重复、占位和证据不完整等负例；不提交 Radar 或跨栈 fixture 文件。
    - 更新相关 Bruce skill/reference/test 文档，保留现有 API、Goal、Checkpoint 和交付边界。
  - Excluded:
    - 不直接修改 `/Users/tele/xjjk/joytime-studio` 的 RadarPage、后端 API、数据库或原型实现。
    - 不实现 React 组件树、DOM 树或任意框架专属 AST diff；不把具体框架作为原型 spec 的权威。
    - 不新增通用截图 AI 评分器，不以单一视觉分数替代关键区域断言。
    - 不修改公共业务 API、数据库 schema、部署、插件安装、commit、push 或 force 操作。
- Acceptance:
  - UI-SURFACE-01: Given an `existing-product-extension` prototype; When its design artifacts are prepared; Then a stack-neutral surface contract identifies the target surface, regions and hierarchy, required states, interactions, observable data, layout invariants, visual anchors, viewports, and evidence methods, without requiring a framework-specific component tree; Evidence: template contract tests and a filled fixture.
  - UI-SURFACE-02: Given a surface contract; When the contract validator runs; Then missing, duplicate, placeholder, or incomplete Surface fields fail validation; Evidence: `validate_surface_contract.py` output and temporary contract tests.
  - UI-SURFACE-03: Given a generic implementation locator; When it is mapped to a Surface ID; Then the mapping is accepted without framework-specific inspection; Evidence: validator contract test.
  - UI-SURFACE-04: Given a governing prototype with a missing or incomplete surface contract; When Design Gate evaluates readiness; Then it returns a design blocker rather than allowing a high-fidelity claim based only on prototype existence or visual-token clearance; Evidence: Design Gate contract tests and negative fixture.
  - UI-SURFACE-05: Given an implementation whose required surface has no current mapping, stale evidence, or no runtime proof for a material visible outcome; When Completion Gate evaluates it; Then Completion cannot be `pass`; it returns `issues` or `blocked` according to the existing external-state rules; Evidence: Completion contract tests and review-matrix fixture.
  - UI-SURFACE-06: Given a contract whose required Surface ID is omitted; When the validator runs; Then the missing Surface ID is visible as a finding; Evidence: negative temporary contract test.
  - UI-SURFACE-07: Given the Bruce repository after implementation; When targeted and full static checks run; Then existing prototype, Design Gate, Completion Gate, plugin and language contracts remain green, and no unrelated repository or working-tree changes are required; Evidence: test commands, validator output and `git diff --check`.
- Constraints:
  - Natural-language artifacts use Simplified Chinese; stable IDs, paths, schema keys, `Given`/`When`/`Then`/`Evidence`, and verdict tokens remain unchanged.
  - The contract is black-box/product-surface first. A repository-specific implementation locator is optional evidence for a surface, not the design authority; accepted locator forms must include file/route/template/view/source entry without naming a framework.
  - `visual_scope=chrome-smoke|chrome-layout` remains proportional. Chrome is required for Web visible outcomes; other runtimes use their real platform evidence. DOM text alone remains insufficient for layout evidence.
  - Changes must preserve current Design Gate, Completion Gate, Goal, Checkpoint and artifact provenance ownership. No parallel verdict or second completion authority is introduced.
- Topology: full; evidence: the change crosses `write-prototype` templates/skill, surface validation, Design Gate, Completion Gate, and their contract tests.
- Risk: guarded; trigger: changing persisted prototype and completion-readiness contracts can alter implementation-entry decisions. Mitigate with explicit surface fields, negative fixtures, and full regression tests.

## Task package

- Path: `tasks/`
- Index: `tasks/index.yaml`
- Contract state: task files are frozen before their task starts
- Status source: `checkpoint.yaml` or the current checkpoint message
- Execution mode: `sequential`
- Omission reason: none; the change has cross-skill contracts and independent verification layers.

## Task summary

| Task ID | Title | Depends on | Acceptance IDs | Allowed paths | Verification layer |
|---|---|---|---|---|---|
| T-001 | 定义技术无关 UI Surface Contract | none | UI-SURFACE-01 | `skills/write-prototype/**` | contract/document |
| T-002 | 实现 Surface Contract 校验与跨栈 fixtures | T-001 | UI-SURFACE-02, UI-SURFACE-03, UI-SURFACE-06 | `scripts/validate_surface_contract.py`, `tests/**` | validator/unit |
| T-003 | 接入 Design Gate 与 Completion Gate | T-001, T-002 | UI-SURFACE-04, UI-SURFACE-05 | `skills/design-gate/**`, `skills/completion-gate/**`, `tests/**` | contract/integration |
| T-004 | 完成回归与范围收口 | T-003 | UI-SURFACE-07 | `README.md`, `CONTEXT.md`, `tests/**` | repository/full |

Detailed frozen contracts live in the four task files under `tasks/`. Do not duplicate their full scope
or acceptance here; update a task contract only through an explicit revision or superseding task.

## Repository evidence

- `skills/write-prototype/templates/prototype-brief.md` — 当前已描述 Required pages/states/interactions，但缺少技术无关 surface/region/observable contract 的结构化字段。
- `skills/write-prototype/templates/repository-ui-contract.md` — 已有 Host surface、Destination surface、Layout invariants、Reuse anchors 和 Visual anchors，适合扩展为实现栈无关的页面表面契约。
- `scripts/validate_prototype_artifact.py` — 当前校验 exact colors、dimensions、brand text 和 forbidden tokens；不应承担生产页面语义完整性校验。
- `skills/design-gate/SKILL.md` — 已要求 UI prototype 的页面、状态、交互、视觉锚点和实现验收证据，但需要增加 Surface Contract 完整性边界。
- `skills/completion-gate/SKILL.md` — 已要求 prototype 与真实目标的页面/状态/交互/布局证据对齐，但当前没有固定 Surface ID 映射格式。
- `tests/test_prototype_contract.py`, `tests/test_prototype_artifact.py`, `tests/test_design_gate_validator.py`, `tests/test_completion_contract.py` — 现有契约测试和视觉 artifact 测试可作为回归入口。
- 线程 `01a027ec-db04-7762-a429-eccad0c41b28` 的雷达差距 — 原型有平台榜单双视图，生产实现主要验证事件聚合和收入流程；作为不绑定 React 的回归场景。

## Dependency and risk notes

- T-001 先冻结语义字段和 Surface ID 规则；否则 validator 与两个 Gate 会各自发明不同的页面模型。
- T-002 只校验结构化 surface contract 和映射 fixture，不把截图相似度、DOM 结构或框架 AST 作为必需条件。
- T-003 必须保持 Design Gate 是唯一 Design 决策者、Completion Gate 是唯一 Completion 决策者；新增内容只能形成 blocker/finding/evidence row，不能新增第三种 verdict。
- 如果现有宿主无法提供指定运行时或当前证据，按现有规则返回 incomplete/blocked，不以静态模板或 prototype screenshot 替代。

## Whole-change verification

- UI-SURFACE-01 -> Given existing-product prototype -> When loading the new brief/UI-contract schema -> Then required stack-neutral surface fields and evidence columns are present -> T-001 -> template/contract tests.
- UI-SURFACE-02 -> Given radar fixture -> When running surface validator -> Then all radar views/regions/observables are uniquely identified -> T-002 -> validator output and negative cases.
- UI-SURFACE-03 -> Given framework and server-template mappings -> When validating implementation locators -> Then both pass without React-specific checks -> T-002 -> cross-stack fixture tests.
- UI-SURFACE-04 -> Given missing surface contract -> When Design Gate evaluates -> Then readiness is blocked -> T-003 -> Design Gate contract test.
- UI-SURFACE-05 -> Given stale/missing runtime evidence -> When Completion Gate evaluates -> Then Completion is not pass -> T-003 -> Completion contract test.
- UI-SURFACE-06 -> Given radar implementation omits platform board -> When review matrix is built -> Then missing board row is reported despite passing event-flow checks -> T-002/T-003 -> regression fixture.
- UI-SURFACE-07 -> Given all implementation changes -> When running repository checks -> Then targeted contracts, full tests, plugin validation and diff check are clear -> T-004 -> command output.

## Delivery boundary

- Workspace only: persist the plan and, during authorized implementation, change only the Bruce paths listed by the frozen task contracts. No Joytime source modification, commit, push, deployment, plugin installation, or external delivery is included.
- Before implementation, run `design-gate` because this plan changes persisted UI prototype and completion-readiness contracts.

## Scope adjustment

- 2026-08-25: 按用户要求移除 Radar 与跨栈 fixture 文件；validator 测试改为运行时生成最小临时契约，不在仓库提交产品场景 fixture。
