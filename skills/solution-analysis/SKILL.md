---
name: solution-analysis
description: Use when the user asks to investigate the current implementation, existing project solutions, and the feasibility of one or more implementation approaches. Perform read-only inspection and feasibility analysis, then stop and wait for explicit user direction before clarification or persisting design artifacts.
---

# Solution Analysis

建立正式方案设计之前的只读分析层：先基于当前仓库和项目文档收集事实，再分析候选方案的可行性，输出推荐方向和未决问题，最后停住等待用户指令。

```text
inspect current implementation and existing solutions
  -> synthesize evidence
  -> analyze feasibility and alternatives
  -> report recommendation and unresolved decisions
  -> wait for explicit user direction
```

本 Skill 不等同于 `write-plan`，也不替代 `inspect-parallel`。它负责把调研证据组织成方案分析结论，但不把分析结论直接固化为正式设计或执行计划。

## Inputs

- 用户要解决的问题、目标和已知约束。
- 当前仓库、适用的 `AGENTS.md`、工作区状态和相关项目路径。
- 需要回答的现状、已有方案、可行性、影响和风险问题。
- 用户指定的范围、禁止事项和期望输出语言。

如果任务边界或业务后果存在一个无法从仓库事实解决的关键歧义，可以提出一个阻塞问题；不要为了普通细节提前进行访谈。

## Procedure

### 1. Inspect current state (read-only)

先进行只读检查，建立事实基础。重点覆盖：

- 当前实现的入口、核心调用链、数据流、状态流转、权限、错误处理、配置和外部依赖；
- 项目中已有的需求、架构、接口、数据库、测试、ADR、`CONTEXT.md`、`docs/change/` 和历史方案；
- 可复用的现有组件、约定、迁移方式、测试命令、运行入口和回滚能力；
- 当前 Git 工作区状态以及必须保留的无关改动；
- 跨组件或跨仓库边界、消费者、公共契约和验证缺口。

区分并标记：

```text
事实：代码、文档、测试或命令直接证明的内容
推断：由事实推导出的约束或关系
未知：当前证据无法确认的内容
```

不得修改源代码、测试、配置、文档或工作流状态；不得创建 `docs/change`、Goal 或其他持久化产物。

### 2. Decide direct inspection or delegated inspection

由主 Agent 决定是否委托 Subagent，不得因使用本 Skill 就自动委托。

- 单一边界、调用关系已清楚或范围较小：主 Agent 直接 inspect，并返回 `Inspection mode: direct` 及原因；
- 至少两个相互独立的只读范围可以并行调查，且并行结果会显著减少上下文或延迟：主 Agent 可以委托 `inspect-parallel`，由其负责 bounded read-only shard 和证据汇总；
- `inspect-parallel` 仍然只收集证据，最终方案分析、冲突消解和推荐结论必须由主 Agent 负责。

委托必须遵守 Bruce 的 Functional Agent 与 v1 Task Packet 合同：先选择 `inspector` Profile，`task_kind=inspect`，`output=task_evidence_packet`，`allowed_paths=[]`，并保留 `model_resolution`。禁止写入、删除、部署、浏览器操作和业务决策。

模型路由遵循共享 Model Profile resolver，不在本 Skill 内创建 Runtime、scheduler 或私有模型选择器：

- 一般代码、调用链和项目文档调研：使用 `inspector` Profile 的 `gpt-5.6-luna` + `reasoning_effort=max`（即 `5.6-luna-max`）；
- 需要独立推理、挑战候选方案并返回只读 findings 的委托任务：使用 `reviewer` Profile 的 `gpt-5.6-terra` + `reasoning_effort=high`（即 `5.6-terra-high`）；它只能审查主 Agent 提供的分析快照或设计假设并返回 findings，最终可行性结论仍由主 Agent 负责；
- 模型只有在宿主确认可用时才作为 `model` 传入；否则按共享 resolver 的 current-model fallback 记录 `resolution_result=fallback`、`capability_status=degraded`。不得静默切换模型，也不得把配置文件本身当成模型已生效的证据；
- 若目标模型、clean context 或必要工具不可用，记录 `resolution_result=blocked` 并由主 Agent决定是直接完成缺失分析还是停止报告阻塞。

主 Agent 不得把 Subagent 的 `task_evidence_packet` 或 `review_packet` 当作最终方案结论；必须核对路径、符号、接口、命令、测试和当前工作区。

### 3. Analyze feasibility

基于已核对的事实分析方案，不执行实现。至少覆盖：

1. **当前现状**：当前实现和项目既有约定分别是什么；
2. **已有方案**：哪些方案已经存在、可以复用、不能复用或彼此冲突；
3. **候选方案**：实现方式、优点、缺点、影响范围、风险、验证难度和回滚方式；
4. **可行性判断**：技术、架构兼容性、数据/迁移、权限/安全、测试验证、发布/回滚分别标记为 `可行`、`有条件可行`、`当前不可行` 或 `证据不足`；
5. **推荐方案**：推荐理由、关键前提和不推荐其他方案的具体原因；
6. **影响与风险**：受影响的组件、契约、数据、用户场景、运维和验证层；
7. **待确认决策**：仅列出会改变方案、范围、验收或业务后果的未决问题。

必须区分观察、推理和建议，不得把方案分析中的推断写成当前实现事实。若证据不足以作结论，明确写出证据缺口，不得补造 API、路径、表或测试结果。

### 4. Stop and wait

分析完成后必须停止，等待用户的明确指令。不得自动调用后续 Skill 或执行任何落盘、实现和交付动作。

禁止自动执行：

- `grill-with-docs`；
- `write-architecture`、`write-db-design`、`write-plan`、`write-tests`；
- `design-gate`、`completion-gate` 或 `goal-execution`；
- 源代码、测试、配置或项目文档修改；
- 创建或更新 `docs/change`、Goal、checkpoint 或 review 状态；
- commit、push、部署或其他外部副作用。

## Output

默认以聊天结果返回，不创建持久化分析文档。使用用户要求的语言；中文请求用简体中文，自然语言字段保持中文，稳定的机器字段保持英文。

输出至少包含：

```markdown
## 现状与证据

### 事实
- ...

### 推断
- ...

### 未知与证据缺口
- ...

## 项目已有方案
...

## 候选方案对比
| 方案 | 实现方式 | 优点 | 缺点 | 影响范围 | 风险 | 验证难度 |
|---|---|---|---|---|---|---|

## 可行性判断
- 技术可行性：...
- 架构兼容性：...
- 数据/迁移可行性：...
- 权限与安全可行性：...
- 测试与验证可行性：...
- 发布与回滚可行性：...

## 推荐方案
...

## 待用户确认的决策
1. ...

Analysis: complete
Awaiting user direction: yes
```

同时报告 `Inspection mode: direct|parallel`、实际调查范围、委托与模型解析记录（如有）以及没有执行的写入/验证动作。

用户后续明确要求继续澄清时，才可转交 `grill-with-docs`；用户明确确认方案并要求落盘时，才可回到 Bruce 主流程，按需要调用架构、数据库、计划、测试设计和 `design-gate`。

## Does not own

Do not modify files, create or update design artifacts, create a Goal, form an implementation plan, approve a design, decide implementation entry, invoke another supporting Skill automatically, implement behavior, run deployment or delivery actions, commit, or push. Do not treat `Analysis: complete` as `Design: pass` or as permission to start implementation.
