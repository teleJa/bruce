---
name: write-tests
description: Use for every behavior change to create an independent test-plan.md; use the minimal template for simple acceptance and the expanded template only for applicable state, concurrency, permission, cross-component or real-runtime evidence needs. Also use when the user explicitly requests test design. 中文请求默认产出 Simplified Chinese（简体中文）test-plan.md。
---

# Write tests

将验收条件转换为具体、可执行、可追溯的验证场景。

## Artifact placement

持久化 `test-plan.md` 时，使用 [artifact-placement.md](../bruce/references/artifact-placement.md)。
跨仓库（cross-repository）测试计划仍只保留一份共享工件，并在计划中记录各仓库的命令和证据边界。

## Invocation decision

在行为实现前应用 [artifact-policy.md](../bruce/references/artifact-policy.md) 的测试设计决策表。
对任何 resolved Bruce profile 都执行判断；profile 本身既不是必要条件，也不是充分条件。
Frontmatter 仅摘要该表，不维护另一套调用条件；下列复杂度条件只决定模板深度，不能跳过行为变更的测试设计。
工件适用性遵循 [artifact-policy.md](../bruce/references/artifact-policy.md)：任何行为变更都必须调用本 Skill，
并独立持久化 `test-plan.md`。简单任务使用最小场景、命令和证据；复杂验收再扩展矩阵、多层验证和回归覆盖。
`plan.md` 或任务合同可以引用场景，但不能替代独立测试计划。仅当 Design Gate 独立必需时，在其候选矩阵中记录
skip 证据；行为变更不得将 Test design 标记为 skipped。

## Invocation triggers

### 通用触发条件

所有行为变更均触发测试设计。以下任一条件成立时使用扩展模板，仅填写适用模块：

- 验收跨越多个组件、API、服务、数据库或其他合同边界；
- 需要验证 state、repeat use、retry、concurrency、partial failure、recovery、permission、rollback；
- 需要真实 integration、deployment、runtime、database、browser 证据或多个验证层级；
- 共享行为场景或回归来源跨越多个任务；
- 修改有重复进入、可变数据或生命周期语义的 stateful UI。

### UI 触发条件

对于 UI 变更，以下任一条件成立时扩展生命周期/视觉证据模块：

- modal、drawer、picker、tab、editor 或 paginated/list surface 可以关闭后再次进入；
- 展示或可选择的数据可能在 surface 关闭期间或两次进入之间变化；
- 存在 cache、refresh、reset、re-fetch、prefill 或 selection-retention 语义；
- cancel、confirm、save、retry、异步加载、分页、过滤或 dependent controls 产生重要状态转换；
- 缺陷涉及 stale state、duplicate interaction、reopening 或 recovery；
- 验收需要真实浏览器，或跨越组件、API、服务边界。

### 跨对象一致性触发条件

当行为涉及绑定、分配、占用、认领、共享、唯一归属、权限授予、候选选择、重绑或状态转移时，
必须判断是否存在跨对象一致性风险。以下任一条件成立时，`consistency_check` 必须为 `required`，并生成
“一致性与权威状态矩阵”：

- 当前操作会创建、替换、删除或转移对象之间的关系；
- 一个资源可能被多个实体竞争，或关系存在一对一/一对多约束；
- 页面展示状态与提交时的服务端状态之间存在时间窗口；
- 关联对象受到独立的权限过滤，当前用户可能看不到该对象；
- 页面状态依赖关联对象的健康度、可用性、存在性或执行权限；
- 需要区分 online、offline、hidden、denied、missing、unknown 等状态。

如果判断不适用，也必须在 `test-plan.md` 中显式记录 `consistency_check: not_applicable` 和原因，
不能静默省略。不要把“对象对当前用户不可见”推导为“对象离线”，也不要把“页面未找到关联对象”推导为
“对象不存在”，除非权威状态已经证明该结论。

不要为纯 copy、icon、color 或没有状态、数据、交互和验证边界的 layout-only 变更调用本 Skill，除非用户或
现有测试计划明确要求。多个 UI 触发条件同时成立时，只创建一份紧凑的测试计划。

## Inputs

- Task contract 和 acceptance criteria。
- 任务合同中的 proportional `visual_scope`（如果涉及用户可见 Web 行为）。
- 适用 Bruce 配置路径及 `verification.browser_provider` 的解析结果；按
  [browser-provider.md](../bruce/references/browser-provider.md) 使用共享解析器，未配置默认 `ego-lite`。
- 已存在的 implementation plan。
- 当前仓库的测试框架、命令、fixture、环境和真实依赖规则。
- 风险、已知回归来源、对象关系和权限边界。
- [document-language.md](../bruce/references/document-language.md)。

## 浏览器选择与视觉检查

生成和更新 Web 测试计划时，先按 [artifact-placement.md](../bruce/references/artifact-placement.md)
定位适用的 `.bruce/config.yaml`；配置存在时通过 `scripts/browser_provider.py --config <实际配置路径> --scope <visual_scope>`
解析 `verification.browser_provider`（脚本从实际 Bruce 插件根目录定位）。没有适用配置文件时，使用同一模块的
`resolve_browser_provider(None)` 缺省分支，不向文件解析器传入不存在的路径，也不为取默认值创建配置文件。
记录配置路径或无配置、配置显式值或未配置、解析后的 Provider；未配置默认 `ego-lite`，
仅显式配置 `chrome` 时使用 Chrome。配置非法/不可读时报告问题，不当作缺省值；运行时 Provider 不可用时保持
`blocked`/`incomplete`，不得静默切换。计划阶段的解析结果不构成浏览器能力可用证据。

不得从历史计划、示例、旧的 `chrome-smoke`/`chrome-layout` scope 或当前打开的浏览器推断 Provider。
新计划使用 `browser-smoke`/`browser-layout`；更新旧计划时将旧 scope 归一化并重新读取配置，不继承 Chrome-only
前提。若验收确实依赖用户当前 Chrome 登录态或扩展但配置不匹配，记录冲突并请用户确认配置调整，不自行改配置。
执行前复核配置；若与计划不同，更新受影响的前提和证据要求，旧 Provider 的证据不能沿用。

所有 Web 场景均须按 [visual-checks.md](references/visual-checks.md) 写明实际视觉判读，不以 DOM 结构/文本检查
替代视觉检查，也不以“截图已保存”作为通过结论。`browser-smoke` 做受影响区域的基础视觉检查；布局、裁切、
溢出、遮挡或响应式风险必须选择 `browser-layout` 并补齐适用的布局断言和几何证据。两种模板都遵循此要求，
不因最小模板而降低证据强度。`visual_scope: none` 保留无可见变化的依据，不生成空视觉清单。

## Procedure

1. 将每个有行为含义的 acceptance 条件映射为稳定的 scenario id，写出具体的 `Given`、`When`、`Then` 和
   `Evidence`。每个重要 `Then` 都必须有可执行的证据路径。对于 `browser-smoke` 或 `browser-layout`，明确可见
   状态；对于 `browser-layout`，除 DOM 文本外还要记录 layout invariant and interaction evidence（布局不变量和交互证据）。
2. 先判断是否需要 `consistency_check`。若为 `required`，先填写“一致性与权威状态矩阵”，明确业务不变量、
   资源、当前 owner、竞争 actor/viewer、权威状态源、stale window、冲突规则、数据后果和 UI/API 重新同步方式。
3. 对 `consistency_check: required` 的任务，先按 `behavior_kinds` 判断场景类别的适用性；对每个类别记录
   `applicable` 或 `not_applicable` 及判断原因，仅对适用类别生成场景。资源绑定/排他归属通常需要覆盖已占用资源
   首次加载、当前关系回显、读取后状态变化、旧快照提交、并发竞争和冲突后数据不变；权限投影/可用性推导通常
   需要覆盖主体可见性、依赖对象可见性、真实健康状态、当前用户访问权和最终可用性。每个场景按适用性记录
   预期 UI 状态、预期 API/结果和持久化不变量；不适用时写 `not_applicable` 及原因。
4. 对 stateful UI 建立紧凑的 lifecycle matrix，按适用性覆盖 first entry、close and reopen、data changes while
   closed、cancel and reopen、confirm and reopen、failure and retry。说明 fresh observable result 和 state-retention
   语义，不要规定具体实现机制，例如必须发起某个网络请求或绕过某个 cache。
5. 对其他 stateful behavior，按适用性覆盖 first use、repeat use、retries、concurrent actions、partial failure、
   history/current pointers 和 recovery。
6. 只在能增加真实覆盖时定义 happy、edge、error、integration、permission 和 regression scenarios；场景必须来自
   实际用户/系统使用，而不是只复述实现细节。
7. 使用仓库真实存在的命令和环境，区分 unit fixture 与需要真实 database、browser、service 或 external dependency
   的验证。当验收断言涉及权威 API、持久化结果或真实用户视角时，必须在对应层级取证；mock 或 DOM 文本不得替代
   被要求的更高层级证据。未涉及的验证层级不强制要求。
8. 有计划时将场景映射到 task id；不要求每个非功能任务都制造 synthetic scenario。
9. 按权威决策表选择模板并统一持久化为 `test-plan.md`：简单验收使用
   [test-plan-minimal.md](templates/test-plan-minimal.md)，复杂验收使用 [test-plan.md](templates/test-plan.md)。
   最小模板保留验收、前提、Given/When/Then、命令、预期证据、适用性理由和限制；不复制空矩阵。
   扩展模板只保留适用模块；不适用的一致性检查保留分类和一句理由，不生成空的权威状态/冲突矩阵。
10. 中文请求时，`test-plan.md` 的标题、说明、矩阵字段、场景名称、Given/When/Then/Evidence 内容、Limits、Self-check
    和其他自然语言字段默认全部使用简体中文；保留 `Given`、`When`、`Then`、`Evidence`、scenario id、命令、路径、API
    名称和其他稳定 machine-facing tokens，不要为了中文化而翻译它们。
11. 检查文档 diff 以及 requirement/acceptance traceability、prerequisites、Given/When/Then 可观察性、evidence layer
    是否匹配、真实依赖语义、回归覆盖、矩阵不变量、权威状态、冲突场景、占位符和链接；
    同时检查 Provider 是否来自配置（未配置默认 `ego-lite`）、是否残留 Chrome-only 前提、视觉断言及截图判读是否具体。修复问题后返回
    `Document check: clear|issues`。测试设计将约束实现时，返回强制 `design-gate` handoff；Bruce/调用方
    必须在同一轮内立即运行 `design-gate`，无需用户追加指令，不得停在“需要门禁”的提示上。本 Skill 不拥有 Design verdict。

## Output

产出独立 `test-plan.md` 和文档检查结果。默认最小内容为验收映射、前提、Given/When/Then、命令、
预期证据及限制；仅在适用时增加视觉、生命周期、一致性与权威状态、冲突/权限场景矩阵。
实际要求的证据层级不因模板更短而降低。

## Does not own

不要创建 execution state，不负责开发顺序，不批准计划，不调用 plan review，不运行完整 workflow，不委托或声明
completion。除强制 Design Gate handoff 外，不要自动调用其他 supporting skill。
