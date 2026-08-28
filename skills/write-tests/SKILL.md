---
name: write-tests
description: Use when acceptance crosses multiple component or contract boundaries; needs state, repeat use, retry, concurrency, partial failure, recovery, permission, rollback, or cross-object consistency coverage; requires real integration, deployment, runtime evidence, or multiple verification layers; shares behavior scenarios or regression sources across tasks; or changes a stateful UI with repeat entry, mutable data, or lifecycle-sensitive interaction. 中文请求默认产出 Simplified Chinese（简体中文）test-plan.md。
---

# Write tests

将验收条件转换为具体、可执行、可追溯的验证场景。

## Artifact placement

持久化 `test-plan.md` 时，使用 [artifact-placement.md](../bruce/references/artifact-placement.md)。
跨仓库（cross-repository）测试计划仍只保留一份共享工件，并在计划中记录各仓库的命令和证据边界。

## Invocation decision

在行为实现前应用 frontmatter trigger contract。对任何 resolved Bruce profile 都执行判断；profile 本身既不是必要条件，也不是充分条件。只要存在持久化实现计划，就必须触发本 Skill。触发后必须持久化
`test-plan.md`；写在 `plan.md` 里的验收条目、验证 bullet 或 Goal 审计文字都不能替代它。没有任何触发条件时
不要调用本 Skill。如果 Design Gate 独立必需，由 Design Gate 在 candidate matrix 中记录 repository-backed 的
测试设计 skip；否则不要创建持久化 skip 记录。

## Invocation triggers

### 通用触发条件

以下任一条件成立时触发测试设计：

- 验收跨越多个组件、API、服务、数据库或其他合同边界；
- 需要验证 state、repeat use、retry、concurrency、partial failure、recovery、permission、rollback；
- 需要真实 integration、deployment、runtime、database、browser 证据或多个验证层级；
- 共享行为场景或回归来源跨越多个任务；
- 修改有重复进入、可变数据或生命周期语义的 stateful UI。

### UI 触发条件

对于 UI 变更，以下任一条件成立时触发：

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
- 已存在的 implementation plan。
- 当前仓库的测试框架、命令、fixture、环境和真实依赖规则。
- 风险、已知回归来源、对象关系和权限边界。
- [document-language.md](../bruce/references/document-language.md)。

## Procedure

1. 将每个有行为含义的 acceptance 条件映射为稳定的 scenario id，写出具体的 `Given`、`When`、`Then` 和
   `Evidence`。每个重要 `Then` 都必须有可执行的证据路径。对于 `chrome-smoke` 或 `chrome-layout`，明确可见
   状态；对于 `chrome-layout`，除 DOM 文本外还要记录 layout invariant and interaction evidence（布局不变量和交互证据）。
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
9. 使用 [test-plan.md](templates/test-plan.md) 持久化 `test-plan.md`。
10. 中文请求时，`test-plan.md` 的标题、说明、矩阵字段、场景名称、Given/When/Then/Evidence 内容、Limits、Self-check
    和其他自然语言字段默认全部使用简体中文；保留 `Given`、`When`、`Then`、`Evidence`、scenario id、命令、路径、API
    名称和其他稳定 machine-facing tokens，不要为了中文化而翻译它们。
11. 检查文档 diff 以及 requirement/acceptance traceability、prerequisites、Given/When/Then 可观察性、evidence layer
    是否匹配、真实依赖语义、回归覆盖、矩阵不变量、权威状态、冲突场景、占位符和链接。修复问题后返回
    `Document check: clear|issues`。测试设计将约束实现时，告知 Bruce 必须运行 `design-gate`；不要自动调用它。

## Output

产出包含以下内容的中文测试设计：验收映射、前置条件、按比例确定视觉验证范围、生命周期矩阵、
（一致性适用时）一致性与权威状态矩阵、冲突/权限视角场景、命令、已知限制和文档检查结果。

## Does not own

不要创建 execution state，不负责开发顺序，不批准计划，不调用 plan review，不运行完整 workflow，不委托或声明
completion。不要自动调用其他 supporting skill。
