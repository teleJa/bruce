# 工件与设计门禁的适用规则

本文件是 Bruce 工件触发条件的权威来源。入口 Skill 负责路由，各工件 Skill 负责内容质量；
目录位置由 `artifact-placement.md` 决定。不要因为另一个工件已经存在就继续生成配套文件。

| 工件或决策 | 独立触发条件 | 不足以触发的条件 |
|---|---|---|
| `plan.md` | 用户要求持久化步骤、依赖关系，或实际交接需要书面计划 | 仅要求先说明做法；会话内步骤足够 |
| 测试设计 / `test-plan.md` | 所有行为变更都必须调用 `write-tests`，独立持久化 `test-plan.md`；按复杂度决定文档内容深度和矩阵范围 | 不能将测试设计内嵌在 `plan.md` 或任务合同中，也不能因任务简单而跳过 |
| `test-plan.md` | 所有行为变更都必须生成；复杂验收增加状态、矩阵、多层证据和回归覆盖 | 仅有计划、文件多、步骤多、profile 为 full 不代表需要超出实际验收的额外内容 |
| `tasks/` | 需要分别冻结任务边界、分任务交接，或分别追踪交付与证据；一次计划内表格无法清楚表达 | 有计划、有多个操作步骤、单纯耗时长 |
| Design Gate | 持久化工件包含待确认的设计决策或下游合同，实际约束后续实现 | 只是执行清单、现有命令列表、进度说明或普通文档编辑 |

先判断当前需求是否满足条件，再选择必要工件。必要工件缺失不能用“精简流程”跳过；
公共/跨组件合同、数据库设计、治理型 UI 原型仍由各自 Skill 和 Design Gate 检查。
当 Design Gate 的独立触发条件成立，且治理型工件已成功落盘并完成本地文档检查时，工件 Skill
必须返回强制 `design-gate` handoff，Bruce/调用方必须在同一轮内立即执行 Gate，无需用户追加指令。
该自动衔接不把 Design verdict 转移给工件 Skill，也不扩大原任务的实现授权。
所有行为变更都必须在独立 `test-plan.md` 中记录 Given/When/Then（或等价的可观察断言）、
测试命令和预期证据。`plan.md` 和任务合同可以引用测试场景，但不能替代 `test-plan.md`。
简单验收使用最小测试计划；复杂验收再增加矩阵、状态路径和多层证据。

## 测试设计决策表

按表中顺序匹配；本表是入口、Skill 描述和模板选择的单一权威，不从 profile 或已有计划推导调用。
复杂验收指 `write-tests` 中适用的状态、权限、跨边界、多层真实证据等扩展条件，不指文件数或耗时。
若纯文案/图标/颜色/layout-only 不改变行为且无上述验证边界，按无行为变更处理；真实视觉验收仍独立判断。

| Rule | 行为变更 | 用户/现有计划显式要求 | 复杂验收 | 调用 write-tests | 模板 |
|---|---|---|---|---|---|
| TEST-01 | yes | any | no | required | minimal |
| TEST-02 | yes | any | yes | required | expanded |
| TEST-03 | no | yes | no | required | minimal |
| TEST-04 | no | yes | yes | required | expanded |
| TEST-05 | no | no | any | skipped | none |

minimal 使用 `write-tests/templates/test-plan-minimal.md`，expanded 使用兼容的 `test-plan.md` 模板；
最终文件统一为独立 `test-plan.md`。最小内容不取消真实测试，也不因存在该文件自动创建 plan、tasks/ 或 Gate；
Design Gate 仍按下游设计决策/合同的独立条件判断，只有现有测试命令和断言的执行清单不构成新设计决定。

## 计划与任务包

简单计划可以独立存在，不要求 `Task package` 节、省略理由、`tasks/index.yaml` 或 checkpoint 文件。
需要任务包时，只建立一个 change-level 包，保持冻结合同、路径所有权、依赖关系和验收关联完整。
计划若显式声明 `tasks/`，缺目录、索引或合同仍是错误；不得删除声明来逃避已确认的交付边界。
历史计划中的 `Omission reason` 继续兼容，但不限制为纯文档任务。

## Design Gate 输入

只有 Design Gate 独立必需时，才写候选矩阵和 skip 证据，不为简单计划单独建一份门禁材料。
新设计评审显式记录 `Complex acceptance: yes|no`，由实际验收条件决定，与有无计划无关。
`Behavior implementation: yes` 时独立 `test-plan.md` 必须 required；`Complex acceptance: yes` 只表示
测试计划需要更完整的场景矩阵和证据层级，不改变独立文档要求。历史评审缺少该字段仍可读取，
但不能从计划存在推断复杂度。
校验器检查字段、工件和合同一致性；复杂度判断本身仍需要仓库及验收证据，不能靠布尔值证明正确。

## 规则归属

- 本文件：工件与 Design Gate 的适用条件。
- `failure-recovery.md`：事件驱动 checkpoint、恢复、重试和异步等待边界。
- `verification-loop.md` 与 `templates/checkpoint.yaml`：证据层级和结构化 checkpoint 内容。
- `completion-gate/SKILL.md`：完成判定、评审模式及按需展开的交付表达。
- README/CONTEXT：只解释概念和指向上述来源，不重复维护触发阈值或完整执行协议。
