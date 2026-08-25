# UI Surface Contract

UI Surface Contract 是面向产品表面的、技术栈无关的结构化契约。它描述用户能看到、触发和验证的 surface，不把 React、Vue、DOM、组件树或框架 AST 当作权威。

## 1. 适用范围和文件

- `greenfield` 可以使用 Surface Contract 描述新页面、区域和状态。
- `existing-product-extension` 必须在 `prototype-brief.md` 和 `prototype-context/repository-ui-contract.md` 中记录 Surface Contract，并在 manifest 中引用契约路径与 revision。
- 机器可校验的契约使用 YAML 或等价的结构化对象，传给 `scripts/validate_surface_contract.py`；视觉 token 继续由 `visual-assertions.json` 和 `validate_prototype_artifact.py` 负责。

## 2. 顶层字段

```yaml
schema_version: 1
contract_id: <stable-contract-id>
classification: greenfield|existing-product-extension
required_surface_ids: [<surface-id>]
surfaces: []
```

自然语言文档中的尖括号仅表示字段说明；实际 fixture 不得保留占位值。

## 3. Surface 字段

The contract explicitly records surface, region hierarchy, required states, interaction transitions, observable fields, layout invariants, visual anchors, required viewports, evidence methods, and implementation mappings. It must not require a React/Vue component tree.

每个 `surfaces[]` 项必须包含：

- `surface_id`: 以 `SURFACE-` 开头且在契约中唯一的稳定 ID。
- `name`: 用户可识别的页面、视图、抽屉、弹窗或内嵌区域名称。
- `purpose`: 用户目标和该 surface 的可观察结果。
- `hierarchy`: surface 与 region 的层级关系；每个 region 需要唯一 `region_id`、`name`、`purpose` 和 `parent_region_id`。
- `required_states`: 默认、加载、成功、空、失败、禁用或阻塞等适用状态；每个状态需要 `state_id`、`name` 和 `observable_result`。
- `interactions`: 触发、前置条件、状态转换、成功结果和失败结果；每个交互需要 `interaction_id`。
- `observables`: 可观察字段、显示关系、空值/错误语义；每项需要 `observable_id`、`field` 和 `meaning`。
- `layout_invariants`: 结构、相对位置、尺寸、溢出或响应式不变量；每项需要 `invariant_id`、`rule` 和 `verification`。
- `visual_anchors`: 有证据的视觉锚点；精确颜色、尺寸、品牌文案和 forbidden token 不在此重复实现。
- `viewports`: 至少一个需要验证的 viewport，包含名称和尺寸。
- `evidence`: 当前契约、实现和运行时证据方法；material visible outcome 需要 `current` 或明确的 `freshness`。
- `implementation_mappings`: 可选但在 Completion 前必须补齐的实现入口；每项需要 `mapping_id`、`locator_type` 和 `locator`。

## 4. 技术无关 locator

允许的 `locator_type`：`file`、`route`、`template`、`view`、`source-entry`。locator 是实现入口证据，不是设计 authority；它可以指向框架组件、服务端模板、路由处理器或其他实现单元，但契约不解析其框架。

不得使用 `framework`、`component_tree`、`dom_tree` 或 `ast` 作为必填字段，也不得以这些字段替代 surface 语义。

## 5. Finding 和 Gate 边界

- 缺失或重复 ID、缺少必需字段、占位值、空 evidence 或不完整 mapping 由独立 Surface validator 报告。
- Surface Contract 完整性是 Design readiness 条件；缺失时必须指出具体 surface、region 或 field。
- 实现入口、当前 runtime evidence、layout evidence 和 evidence revision 是 Completion review-matrix 的每个 Surface ID 行；缺少或 stale 时 Completion 不能返回 `pass`。
- `chrome-smoke` 仍需要真实交互后的可见状态和截图；`chrome-layout` 仍需要 viewport、截图、几何/overflow 和交互前后证据。Surface Contract、DOM 文本、原型截图和 provider score 不能替代当前 Chrome。
