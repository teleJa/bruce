---
status: implemented
run: "20260710-105828-bruce-workflow-flexibility"
task: "将 Bruce v4 简化为 Codex 原生执行的风险驱动工作流插件"
created: "2026-07-10T10:58:28+08:00"
updated: "2026-07-23"
---

# 计划：将 Bruce v4 简化为 Codex 原生执行的风险驱动工作流插件

## 实施结果（更新至 2026-07-23）

- 已建立标准 Codex plugin manifest、repo-local marketplace 和单一 `skills/bruce/SKILL.md` 真源。
- 已将主流程、topology、业务风险、L0-L4、恢复与完成判断拆为可达 references。
- 已将规划、架构、数据库、测试、评审、委派和完成复核改为无固定级联的条件式能力。
- 已删除根 skill 镜像、旧 checklist/config/state-machine、固定 progress/completion 模板和 active REDESIGN 入口。
- 已增加 contract/package tests 和只读 validator；真实插件安装仍是需用户另行授权的手工 smoke。
- 已增加行为验收与验证闭环：Given/When/Then/Evidence、开发期失败反馈、C0 代码自检、
  分层真实验证、原场景重跑与关联回归；Web 真实使用验收复用 Codex App Chrome 当前会话。
- 已将 full test-design 路由改为确定性条件判断：命中复杂验收条件时强制生成
  `test-plan.md`，全部不命中时必须在同级 `artifact-review.md` 记录 repository-backed skip reason。
- 已恢复设计产物完整性门禁：full 或持久化下游设计真源的任务在实现前必须生成同级
  `artifact-review.md`，缺少必需产物或跳过证据时阻断。

本节是实施快照，不是运行状态真相；当前代码、工具结果和工作区事实仍优先。

## 背景与纠偏

Bruce 的产品形态是一套通过 Codex plugin 分发的个人/团队研发工作流。Codex 是执行载体，负责命令、文件修改、工具调用、sandbox、权限审批、会话和 subagent 生命周期；Bruce 只负责告诉 Codex“如何组织一次研发任务”。

旧草案把 Bruce 误建模为独立 runtime engine，自建了 SandboxBackend、HostAdapter、权限 hash、DecisionPackage、可信 evidence、lease/fencing、ChangeSet 合并器和 JSONL 恢复协议。这些能力重复了宿主职责，也让插件比实际工作流更复杂。

v4 改为 plugin-first：以 `skills/bruce/SKILL.md` 为主入口，复用 Codex 原生执行与任务上下文，只保留工作流路由、业务风险、失败策略、条件式 artifact 和完成判断。插件可以提供确定性校验脚本，但不得包装或替代 Codex 的通用执行、安全和调度能力。

## 已确认决策

1. **产品边界**：Bruce 是 Codex workflow plugin，不是 CLI、MCP server、执行引擎或 sandbox provider。
2. **一条默认流程**：`inspect -> task contract -> implement -> verify -> summary`，不再保留 express lane。
3. **standard/full 只描述任务拓扑**：standard 是单组件；full 是多组件或跨组件契约。拓扑不决定用户确认或 artifact 数量。
4. **low/guarded/critical 描述业务与变更风险**：不映射 Codex sandbox mode，也不复制宿主 approval。
5. **失败采用 L0-L4**：有限重试、局部修复、受影响范围重规划、等待业务决策、未知状态停止；独立任务可以继续。
6. **Codex task/thread 是运行状态**：优先使用当前任务上下文和 Codex 原生 plan/subagent 能力，不维护自定义 runtime state store。
7. **artifact 条件生成**：普通任务不强制 clarification、architecture、plan、test-plan、review、progress 或 completion Markdown。
8. **一个主入口**：用户只需调用 Bruce；现有 supporting skills 作为插件内能力按需使用，不再组成固定阶段链。
9. **v4 硬切换**：移除旧 checklist/state-machine 运行入口，不迁移旧 flow；历史文档保留为只读设计记录。
10. **验证闭环按行为触发**：行为验收使用稳定的 Given/When/Then/Evidence 场景；代码变化强制 C0，
    但纯文档、生成代码和机械修改不套用仪式化 TDD。用户可见 Web 行为必须通过 Codex App Chrome
    复用当前会话验证真实服务，不得静默退回 Playwright。

## 责任边界

| 能力 | Codex 宿主 | Bruce 插件 |
|---|---|---|
| 文件、命令和工具执行 | 负责 | 使用返回结果，不包装执行器 |
| sandbox 与网络边界 | 负责 | 不配置、不证明、不绕过 |
| shell/app/MCP 权限审批 | 负责 | 不复制 approval，不持久化权限 |
| 会话、任务恢复、subagent 生命周期 | 负责 | 使用原生能力，不自建 scheduler/lease |
| 任务目标、scope、acceptance | 提供上下文载体 | 形成最小 task contract |
| standard/full 路由 | 不负责业务判断 | 负责 |
| low/guarded/critical 变更风险 | 提供工具事实 | 负责业务判断 |
| L0-L4 失败处理 | 返回执行结果 | 选择 retry/repair/replan/ask/stop |
| artifact 与完成标准 | 保存对话和文件 | 决定何时生成、如何验收 |

### 两类“需要用户”的严格区分

- **宿主 approval**：Codex 因 filesystem、network、app/MCP side effect 等权限边界向用户请求批准。Bruce 不创建第二套 approval，也不把它写入业务风险状态。
- **业务决策**：需求存在无法从仓库消除的歧义、要扩大 scope、改变公共契约、接受不可逆业务后果等。Bruce 只在当前任务尚未明确授权时询问一个真正阻塞的问题。

如果 Codex 的宿主 approval 被拒绝，Bruce 读取拒绝结果：当前 contract 内存在替代路径则按 L2 重规划；没有合法路径则报告 blocked。不得尝试绕过 sandbox，也不得把宿主拒绝伪装成业务批准。

## 目标与非目标

### 目标

- 让清晰、低风险任务直接由 Codex 实现和验证，不经过固定文档链或人工 gate。
- 让 full+low 仍可自治，standard+critical 仍能在真正的业务风险点停下。
- 让局部失败不再无条件停止整条工作流，并限制重试/修复次数。
- 让复杂任务按需调用现有规划、架构、测试和 review 能力，但不把这些能力变成每次必经阶段。
- 让插件通过标准 `.codex-plugin/plugin.json + skills/` 结构安装、发现和使用。
- 让完成结论绑定当前任务中的真实 diff、命令结果和验收事实，而不是固定 artifact 是否存在。
- 让代码生成速度与验证能力形成闭环：实现前可验证、实现后自检、失败后修复并重跑原场景和回归。

### 非目标

- 不实现 sandbox、HostAdapter、typed action adapter 或权限系统。
- 不实现通用 DAG scheduler、lease、heartbeat、fencing、worktree manager 或事务合并器。
- 不实现 `run.json/evidence.jsonl/decisions.jsonl` runtime protocol。
- 不把 Codex transcript 复制为另一套审计日志。
- 不通过 CLI 或 MCP 暴露 Bruce 自己的公共执行面。
- 不要求所有 supporting skills 在每次 Bruce 运行中出现。
- 不在本轮自动迁移或删除历史 `docs/flow`/旧 run。

## 目标工作流

```text
inspect repository and user intent
  -> normalize minimal task contract
  -> classify topology: standard | full
  -> classify change risk: low | guarded | critical
  -> choose only necessary supporting capabilities
  -> implement from a failing test/repro when applicable
  -> C0 code self-review
  -> verify Given/When/Then scenarios at required layers
  -> on L1: repair -> C0 -> original scenario -> regression
  -> on L0/L2/L3/L4: bounded retry / replan / decision / incident freeze
  -> report concise evidence summary
```

### 最小 task contract

task contract 是当前 Codex 任务中的结构化工作上下文，不要求落盘，至少包含：

- `objective`：要达成的结果。
- `scope`：允许和不允许改变的范围。
- `acceptance`：可验证的完成条件；行为工作使用稳定 scenario id，并为每项写明 Given、When、
  Then 和能证明各重要结果的精确 Evidence 入口。
- `constraints`：仓库规则、用户约束和已知风险。
- `topology`：standard/full 及一句理由。
- `risk`：low/guarded/critical 及触发原因。
- `tasks`：仅在多步骤工作需要时建立的最小任务列表和依赖。

优先使用 Codex 当前 task/thread 和原生 plan 能力承载这些信息。只有用户明确要求交接、跨任务迁移或长期保存时，才生成 `handoff.md`；它是人类可读快照，不是运行真相，也不能反向覆盖当前任务。

## standard 与 full

| 路由 | 判定 | 默认行为 |
|---|---|---|
| standard | 单组件，没有跨组件契约传播 | 主 Agent 直接执行；需要多步时使用轻量 plan |
| full | 多组件，或改变跨组件 API/event/data/file contract | 记录组件和契约依赖；按需要使用 Codex subagent 或顺序执行 |

补充规则：

- 单组件中的架构、schema 或高风险修改仍是 standard；由 risk 决定治理强度。
- full 不等于必须并行，也不机械生成 architecture/plan/test-plan；但行为实现前必须执行
  test-design decision。验收跨越至少两个组件/契约边界，包含状态、重试、并发、部分失败、
  恢复、权限或回滚，需要真实集成/部署/运行环境或多个验证层，或多个实现任务共享行为场景/
  回归来源时，必须调用 `write-tests`。均不命中时必须记录
  `write-tests: skipped — <repository-backed reason>`，不得静默跳过。
- 使用 subagent 时，只委派边界清晰、低耦合任务；主 Agent 负责说明依赖和文件范围、汇总结果并处理冲突。Bruce 不维护 worker 状态。
- topology 可以随仓库事实升级或纠正；只要 objective/scope 未扩大，不需要用户批准路由变化。

## 业务风险规则

| 风险 | 典型触发 | 工作流行为 |
|---|---|---|
| low | 本地、可逆、无公共契约/schema/生产/不可逆后果 | 直接执行和验证，不询问、不强制 review |
| guarded | schema、公共 API/contract、安全敏感配置、重要但可恢复的数据变更 | 若当前任务已明确授权则继续；否则在实际变更前询问一个业务决策；完成前必须执行完成复核 |
| critical | 生产、基础设施、不可逆数据操作、权限边界、安全事件、外部不可逆写 | 执行前明确说明对象、影响和恢复方式并取得用户确认；未知状态按 L4 停止 |

风险只能基于仓库或工具的新事实改变：发现更高风险时立即升级；发现原判定依据不成立时可以带证据下调并记录理由，不需要用户批准。不得为了绕过尚未取得的 guarded/critical 确认而自行下调。扩大 scope、改变 acceptance 或接受新的业务后果仍必须得到用户业务决策。用户在当前任务中已经明确要求并授权的 guarded 变更不得重复确认；critical 仍按其不可逆边界确认。

Codex 是否弹出宿主 approval 与本表无关。Bruce 不读取或设置 sandbox mode，也不要求为命令生成 permission/hash/attestation。

## 条件式 supporting capabilities

| 真实需要 | 调用或生成 |
|---|---|
| 单个、孤立且仓库事实无法消除的需求歧义 | Bruce 直接询问一个阻塞性问题 |
| 多个相互依赖的领域决策、需要持久化领域文档或用户明确要求 grilling | `grill-with-docs` |
| 需要冻结架构/公共契约、需要交接 | `write-architecture`，必要时 `write-db-design` |
| 多步骤、多人交接、full 依赖复杂 | `write-plan` |
| full 验收跨至少两个组件/契约边界；涉及状态/重试/并发/部分失败/恢复/权限/回滚；需要真实集成、部署、运行环境或多个验证层；多个任务共享行为场景或回归来源 | 实现行为前调用 `write-tests` 并持久化 `test-plan.md`；全部不命中则记录 repository-backed skip reason |
| full，或 standard 已持久化下游设计真源 | 实现前调用 `artifact-review-gate` 并在同级生成 `artifact-review.md`；缺文件、缺评审或 skipped 无证据时阻断 |
| 代码或运行行为变化 | 读取 `verification-loop.md`；实现前检查 Evidence 可行性，完成后强制 C0 与分层验证 |
| 任意文档发生修改 | 强制 D0 self-review：事实、跨文档一致性、完整性、占位符和链接，输出 pass/issues |
| 需求、架构、公共契约、开发计划、测试设计、多文档联动或下游真源 | 条件式 D1 `doc-review-gate` P0/P1 放行；仅计划深度执行风险可改用 `plan-review`，不机械双跑；Clean=通过，Issues Found=不通过 |
| 存在实际计划且风险值得独立检查 | `plan-review` |
| 普通任务中适合边界清晰的独立工作 | 直接使用 Codex 原生 subagent，不创建 Goal |
| 用户明确要求 Goal、持续/跨轮或可审计执行 | `goal-execution-gate` 创建/接续原生 Goal 和 `execute_record.md`，其下游可调用 `spawn-execute` |
| ordinary guarded | `verify-completion`；主 Agent 做与实现步骤分离的结构化 second pass |
| broad guarded | `verify-completion`；独立性有实质价值时优先 Codex 原生 fresh reviewer |
| critical 或用户明确要求独立复核 | `verify-completion`；要求 Codex 原生 fresh reviewer，不可用时 blocked |

这些能力没有固定调用顺序。不存在真实触发条件时，Bruce 直接使用 Codex 完成任务。任何 supporting skill 都不得把自己的 Markdown 变成全局状态门禁。

## 失败等级与恢复

| 等级 | 类型 | 示例 | 默认处理 | 用户交互 |
|---|---|---|---|---|
| L0 | transient | 429、连接重置、临时锁、偶发工具超时 | 在幂等且预算充足时退避重试；首次失败后默认最多再重试 2 次 | 不打断，摘要记录 |
| L1 | repairable | 编译、测试、lint、场景或局部实现错误 | 实际修复，代码变化后重跑 C0，再不改验收地重跑原失败场景和关联回归；最多 2 轮完整修复闭环 | 通常不打断 |
| L2 | replan | 依赖缺失、接口不匹配、原方案不可行、宿主权限被拒但有替代路径 | 只重规划受影响 task/descendants | 无合法路径时报告 |
| L3 | business_authority | 需求歧义、扩大 scope、改变 acceptance、未授权的 guarded/critical 业务动作 | 暂停相关任务，询问一个精确业务问题 | 立即报告 |
| L4 | unknown_or_incident | 外部动作可能半成功、数据/安全状态未知、工具明确报告完整性风险 | 停止 incident boundary 内所有写入、重试和依赖未知结果的动作，报告已知/未知事实 | 立即报告 |

### 传播与继续规则

- 当前 task 的 L0/L1 只影响自己和依赖它的任务。
- L2 只暂停受影响 task、它的 descendants，以及共享同一契约/文件且不能安全并行的任务。
- L3 只暂停需要该业务决定的任务；真正独立的工作可以继续。
- L4 才停止整个 incident boundary：包括接触同一外部系统、数据集、安全边界或依赖未知结果的任务。只读诊断可以继续；只有能证明不会读写该边界、不会掩盖现场的独立任务才可继续。
- 主 Agent 根据当前 plan 和仓库事实判断依赖；不创建持久化 scheduler、lease 或 fencing token。
- Codex subagent 失败后由主 Agent读取其结果并分类；插件不监控 PID、heartbeat 或后台进程。
- Goal-backed 执行中，`spawn-execute` 将任务范围、修改文件、scenario id、Given/When/Then、
  验证层和当前证据、C0 verdict、repair round、原场景重跑、关联回归、失败等级与依赖影响作为
  evidence packet 返回；`goal-execution-gate` 负责更新唯一的 `execute_record.md`。该文件不保存运行状态。
- 文档任务的 evidence packet 同时包含 D0/D1 review mode、verdict 和问题结论，Goal Gate 将其写入既有审计记录，不创建独立 review ledger。

### 确定性升级规则

- L0 的 `retry_count` 只统计首次失败后的重试，`retry_count < 2` 才可再次执行；没有代码、输入、环境或时间窗口变化时，不允许把同一失败命令无限归为 L0。
- 编译、断言、类型、lint 和行为场景错误属于 L1，必须有实际修复后才能进入完整重验。
- L1 的 `repair_round` 仅在实际修复、代码变化后的 C0、未改变的原失败场景和关联回归均已执行后
  计数；两轮完整闭环仍失败则进入 L2。不得削弱验收或用更小的通过检查替换原失败。
- 需要新 scope、改变 acceptance 或未授权高风险业务动作至少是 L3。
- 外部 side effect 状态为 unknown、数据完整性或安全事件必须是 L4，模型不得降级。
- 工具明确返回 permission denied 时，遵守 Codex 宿主结果；有替代路径转 L2，否则 blocked，不自行提升权限。

### 恢复来源

- 同一 Codex task 恢复：读取当前对话、原生 plan、tool results 和工作区实际状态，继续未完成项。
- Codex task 已结束或上下文不可用：不扫描旧 checklist 推断状态；用户提供目标或 handoff 后重新 inspect。
- 用户要求跨任务交接：生成可选 `handoff.md`，包含 objective、scope、acceptance、已完成、未完成、关键决定和验证结果；接手任务仍需重新核对工作区。
- 历史 Markdown 只能提供背景，不能证明当前代码已验证或已完成。

## 完成判断

Bruce 只在以下条件同时成立时报告完成：

- 当前工作区变化与 objective/scope 一致，没有未解释的越界修改。
- 每个行为 acceptance 都有 scenario id、Given/When/Then、所需验证层、当前 Evidence 和结果；
  重要 Then 在实现前已有可行验证入口，除非用户明确接受探索性未验证边界。
- 代码变化后存在针对最终 diff 的 C0 `pass`；后续代码改动会使旧 verdict 失效。
- 相关 unit/component、integration/API/database 和 real-use 验证已按验收需要执行，低层证据不替代
  高层要求。用户可见 Web 行为使用 Codex App Chrome 当前会话操作真实 localhost/目标服务；Chrome
  不可用时保留缺口，只有仓库既定 SOP 或用户明确要求时才可使用 Playwright。
- 若验证进入 L1 修复，已保留并重跑未修改的原场景，随后完成关联回归并更新
  acceptance-to-evidence。L0/L2/L3/L4 分别遵守幂等重试、重规划、等待决策和 incident freeze，
  不因闭环要求重放未知外部副作用。
- 没有未解决的 L2/L3/L4，也没有仍依赖失败 task 的未完成项。
- 文档发生修改时必须有当前 D0 pass；重要或控制下游工作的文档还必须有 D1 通过，或由有权决策者明确豁免并记录的有条件通过。
- guarded/critical 必须执行完成复核。ordinary guarded 由主 Agent 做与实现步骤分离的结构化 second pass；broad guarded 仅在独立性有实质价值时优先 fresh reviewer；critical 或用户明确要求独立 reviewer 时必须使用 Codex 原生 fresh reviewer，不可用则 blocked。low 不强制 reviewer。
- 用户要求的 delivery action（仅 workspace、commit、PR 等）已经由 Codex 按用户授权完成，或明确列为未执行。

证据摘要直接引用本次 Codex task 中实际运行的命令、退出结果、页面检查和文件路径。Bruce 不创建第二份 hash-chain evidence store，也不解析“完成了”之类自然语言作为证据。

## Codex 插件结构

v4 采用官方 plugin 结构，插件根目录为当前仓库：

```text
.codex-plugin/
  plugin.json                 # 必需 manifest
.agents/plugins/
  marketplace.json            # repo-local 安装/测试入口
skills/
  bruce/
    SKILL.md                   # 唯一主工作流入口和 canonical source
    references/               # 路由、风险、失败/恢复细则
    templates/                # 仅条件式 artifact 模板
  <supporting-skill>/          # 可复用能力，按需调用
scripts/
  validate_plugin.py          # 只做 manifest/skill/legacy 静态校验
tests/
README.md
```

`.codex-plugin/plugin.json` 只声明 `skills: "./skills/"` 及必要 metadata；v4 不包含 `.mcp.json`、`.app.json` 或 hooks。`skills/bruce/SKILL.md` 是唯一 Bruce 真源，不再维护根 `SKILL.md` 与 `skills/bruce/SKILL.md` 双写镜像。

repo marketplace 只用于本地安装测试。任何修改用户全局 Codex 配置、安装插件或重启 App 的操作都必须单独获得用户确认；静态 package 验证不依赖这些外部变更。

## 任务清单

### bruce-v4-1
- **title**: 建立 Codex plugin 骨架和单一源码边界
- **depends_on**: []
- **parallel_safe**: false
- **files**:
  - `.codex-plugin/plugin.json`
  - `.agents/plugins/marketplace.json`
  - `skills/bruce/references/plugin-boundary.md`
  - `tests/test_plugin_manifest.py`
- **interfaces**:
  - produces: 标准 plugin manifest、repo marketplace entry、Codex/Bruce 责任边界
- **detail**: 建立以 `skills: "./skills/"` 为唯一组件入口的最小 manifest，明确没有 MCP/app/hooks/公共 CLI；marketplace path 必须指向当前插件根且不递归复制。静态测试验证 manifest schema、相对路径和主 skill 存在。
- **feature_bearing**: true
- **tests**: `test-plan.md#bruce-v4-1`
- **acceptance**: 官方 plugin 目录和 manifest 契约可被静态验证；Bruce 不再被描述成独立执行引擎。

### bruce-v4-2
- **title**: 重写主 skill 的默认流程、拓扑和业务风险路由
- **depends_on**: [bruce-v4-1]
- **parallel_safe**: false
- **files**:
  - `skills/bruce/SKILL.md`
  - `skills/bruce/references/risk-policy.md`
  - `tests/test_workflow_routing.py`
- **interfaces**:
  - consumes: 用户请求、仓库事实、Codex 当前 task context
  - produces: 最小 task contract、standard/full、low/guarded/critical、按需 capability 选择
- **detail**: 删除 express、固定 clarify/plan/review gates 和 checklist 状态机。将 topology、capability selection 和 completion contract 保留在主 skill 单一真源，不再维护重复的 workflow-contract reference。普通任务直接 inspect/implement/verify；supporting skills 只在真实触发条件下调用。明确业务确认与 Codex 宿主 approval 不重复，当前请求已授权的 guarded 变更不再询问。
- **feature_bearing**: true
- **tests**: `test-plan.md#bruce-v4-2`
- **acceptance**: standard+low、full+low、standard+guarded、full+critical 的路由与用户交互符合本计划；topology 不决定 approval/artifact。

### bruce-v4-3
- **title**: 实现轻量 L0-L4 失败与恢复 contract
- **depends_on**: [bruce-v4-2]
- **parallel_safe**: true
- **files**:
  - `skills/bruce/references/failure-recovery.md`
  - `skills/bruce/templates/handoff.md`
  - `tests/test_failure_policy.py`
  - `tests/test_resume_contract.py`
- **interfaces**:
  - consumes: Codex tool/subagent result、当前 task plan、工作区事实
  - produces: retry/repair/replan/ask/stop 决定、可选 handoff snapshot
- **detail**: 定义 L0-L4、预算、局部传播、宿主 permission denied 和 unknown side effect 的处理。恢复只依赖 Codex task 与重新 inspect；handoff 仅按需生成，不建立 runtime store。该任务不实现执行器、scheduler 或 JSONL。
- **feature_bearing**: true
- **tests**: `test-plan.md#bruce-v4-3`
- **acceptance**: 局部失败不会全局停止，L3 只暂停相关任务，L4 只冻结定义明确的 incident boundary；重试有界，恢复不读取旧 checklist 判定完成。

### bruce-v4-4
- **title**: 将 supporting skills 改为条件式能力
- **depends_on**: [bruce-v4-2]
- **parallel_safe**: true
- **files**:
  - `skills/grill-with-docs/SKILL.md`
  - `skills/write-architecture/SKILL.md`
  - `skills/write-architecture/templates/architecture.md`
  - `skills/write-architecture/templates/api-contracts.md`
  - `skills/write-db-design/SKILL.md`
  - `skills/write-db-design/DESIGN.md`（删除或改为不参与运行的历史说明）
  - `skills/write-db-design/templates/table-design.md`
  - `skills/write-plan/SKILL.md`
  - `skills/write-plan/templates/plan.md`
  - `skills/write-tests/SKILL.md`
  - `skills/write-tests/templates/test-plan.md`
  - `skills/plan-review/SKILL.md`
  - `skills/plan-review/references/plan-reviewer-prompt.md`
  - `tests/test_supporting_skill_contracts.py`
  - `tests/test_document_review_contract.py`
- **interfaces**:
  - consumes: Bruce task contract 和明确的 capability request
  - produces: 仅在需要时生成的 clarification/design/plan/test/review artifact
- **detail**: 移除 supporting skills 及其被引用 references/templates 对旧 lane、checklist 和固定 stage transition 的依赖。每个 skill 明确输入、输出与不负责事项；它们可以独立使用，也可以由 Bruce 按需调用，但不得成为运行状态真相。普通单点阻塞歧义由 Bruce 直接询问，`grill-with-docs` 只处理多个依赖决策、持久领域文档或显式 grilling。full 的 test-design decision 使用可机械核对的复杂度条件：跨至少两个组件/契约边界，状态/重试/并发/部分失败/恢复/权限/回滚，真实集成/部署/运行环境或多验证层，以及多任务共享行为场景/回归来源；命中任一条件必须调用 `write-tests`，全部不命中必须在同级 `artifact-review.md` 留下 repository-backed skip reason。full 或持久化下游设计真源的 standard 任务必须通过 artifact review gate，但该门禁只检查按需产物集合的完整性，不强制生成全部内容。contract test 必须遍历 skill frontmatter/body 以及从中可达的本地 reference/template，不能只检查 `SKILL.md`。
- **document-review**: 所有持久文档修改必须由写入 Agent 做独立于写作步骤的 D0 自评并返回 pass/issues；需求、架构、公共契约、开发计划、测试设计、多文档联动或下游真源按条件进入 D1 P0/P1 放行。D1 reviewer 默认只读，Bruce 只在原修改授权和 scope 内修复，修复后重新评审。
- **feature_bearing**: true
- **tests**: `test-plan.md#bruce-v4-4`
- **acceptance**: 不存在真实内容触发条件时不生成对应设计文档，但 full 必须在同级 `artifact-review.md` 记录完整候选集合和 test-design skip reason；命中 test-design 任一条件时实现前存在 `test-plan.md`，且内联验收表不能替代；触发单项能力时只生成对应内容，不级联完整旧流水线；任何文档修改都有显式 D0 verdict，重要文档在进入下游前具有合格 D1 verdict，artifact gate 不通过时禁止实现。

### bruce-v4-5
- **title**: 对齐 Codex 原生执行、subagent 和完成验证
- **depends_on**: [bruce-v4-3, bruce-v4-4]
- **parallel_safe**: false
- **files**:
  - `skills/spawn-execute/SKILL.md`
  - `skills/spawn-execute/agents/openai.yaml`
  - `skills/spawn-execute/REDESIGN.md`（删除或改为不参与运行的历史说明）
  - `skills/spawn-execute/templates/progress.md`（删除固定 ledger 模板，或改为仅在用户要求持久交接时使用）
  - `skills/verify-completion/SKILL.md`
  - `skills/bruce/references/verification-loop.md`
  - `skills/write-plan/SKILL.md`
  - `skills/write-plan/templates/plan.md`
  - `skills/write-tests/SKILL.md`
  - `skills/write-tests/templates/test-plan.md`
  - `tests/test_execution_contract.py`
  - `tests/test_completion_contract.py`
  - `tests/test_validation_loop_contract.py`
  - `tests/test_workflow_profiles.py`
- **interfaces**:
  - consumes: active native Goal、`execute_record.md`、task contract、Codex 原生 tools/subagents、实际 diff 和验证结果
  - produces: 有界委派、L0-L4 分类、scenario-level audit evidence packet、C0 与完成复核结论
- **detail**: 普通临时 delegation 直接使用 Codex 原生 subagent。行为工作先把 acceptance 写成稳定的 Given/When/Then/Evidence 场景；重要 Then 没有可行 Evidence 时不得开始正式实现。开发期在可行时从最小失败测试或复现场景开始，Bug 先复现，重构先建立 characterization baseline；纯文档、生成代码和机械修改不强制 TDD。代码变化后强制 C0 自检最终 diff、调用点、错误/边界、安全/权限/并发/幂等/数据完整性和测试遗漏。验证按 unit/component、真实 integration/API/database、real-use 分层；用户可见 Web 行为使用 Codex App Chrome 当前登录态和扩展操作真实服务，不可用时保留验收缺口且不静默切换 Playwright。失败先按 L0-L4 分类；只有 L1 执行“实际修复—代码变化后 C0—不变的原失败场景—关联回归”，两轮完整 L1 失败升级 L2。L0 只做有界幂等重试，L2 重规划，L3 等待业务决策，L4 冻结 incident boundary 且禁止重放未知外部副作用。`spawn-execute` 只作为 `goal-execution-gate` 的下游执行能力，返回上述场景、证据和修复闭环信息，由 Goal Gate 更新唯一 `execute_record.md` 与原生 Goal 终态。`goal-execution-gate` 当前是插件外依赖，后续迁入 Bruce。ordinary guarded 使用主 Agent 结构化 second pass；broad guarded 仅在独立性有实质价值时优先 fresh subagent；critical 或显式独立复核要求 fresh reviewer，不可用时 blocked。
- **feature_bearing**: true
- **tests**: `test-plan.md#bruce-v4-5`
- **acceptance**: 普通 delegation 不产生 Goal；行为验收可追溯到 Given/When/Then/Evidence 和所需验证层；最终代码有当前 C0 pass；Web 用户场景有真实 Chrome 证据或显式缺口；失败后原场景与关联回归形成有界 loop；每次 `spawn-execute` 都处于 active Goal 下并产生可写入唯一审计文件的 evidence packet；任一 subagent 失败只传播到依赖范围；无当前验证事实、存在 L2+ 或越界 diff 时不能报告完成。

### bruce-v4-6
- **title**: 完成 plugin-first 打包、文档和旧运行入口清理
- **depends_on**: [bruce-v4-5]
- **parallel_safe**: false
- **files**:
  - `README.md`
  - `scripts/validate_plugin.py`
  - `tests/test_package.py`
  - `SKILL.md`（删除旧真源）
  - `PIPELINE-REDESIGN.md`（删除根镜像或移入明确的历史文档区）
  - `skills/bruce/PIPELINE-REDESIGN.md`（删除旧运行设计）
  - `config.default.yaml`（删除根镜像）
  - `skills/bruce/config.default.yaml`（删除旧 lane/run/worktree 配置）
  - `scripts/checklist_gate.py`（删除）
  - `skills/bruce/scripts/checklist_gate.py`（删除）
  - `templates/checklist.json`（删除）
  - `skills/bruce/templates/checklist.json`（删除）
  - `templates/clarification.md`（删除根镜像）
  - `templates/plan-review.md`（删除根镜像）
  - `templates/completion-review.md`（删除根镜像）
  - `skills/bruce/templates/clarification.md`（删除；澄清默认留在当前 task）
  - `skills/bruce/templates/plan-review.md`（删除；review 默认返回当前 task）
  - `skills/bruce/templates/completion-review.md`（删除；完成复核默认返回当前 task）
- **interfaces**:
  - consumes: 已通过 profile tests 的 plugin source
  - produces: 可静态校验、可通过 repo marketplace 安装测试的 Bruce plugin
- **detail**: README 以“一个 Bruce 入口、Codex 原生执行”为首页；validator 检查 manifest、skill frontmatter、相对路径和单一真源。legacy 扫描只覆盖会被 Codex 发现或被 active skill 引用的运行表面，不扫描保留的历史 `docs/**`、本 change 计划以及用于证明禁止行为的负面测试 fixture。先让新主入口和 contract tests 就位，再在本任务中删除旧 checklist/state-machine 入口，删除后运行最终全量测试。创建仓库内 `.agents/plugins/marketplace.json` 是本计划实现的一部分；只有运行安装命令、修改用户全局 Codex 配置或重启 App 才需另行确认。
- **feature_bearing**: true
- **tests**: `test-plan.md#bruce-v4-6`
- **acceptance**: package 的 active/discoverable surface 无双写镜像、旧 lane/checklist 配置和公开 CLI/MCP/host runtime；静态验证和全量测试通过，历史资料与负面测试不会被误报；README 能指导用户在 Codex 中安装并调用 Bruce。

## 本组件验收

- 6 个 task id 与 `test-plan.md` 6 个 anchor 一一对应、唯一且依赖无环。
- `.codex-plugin/plugin.json` 存在并只指向真实 plugin components；主入口是 `skills/bruce/SKILL.md`。
- 默认流程只有 inspect/task contract/按需设计/条件式 artifact gate/implement/verify/summary，没有 express 和固定内容产物链。
- standard/full 只影响拓扑；low/guarded/critical 只影响业务治理。
- full+low 不产生人工业务 gate；已明确授权的 standard+guarded 不重复询问。
- L0-L4 有界且按依赖传播；宿主 permission denied 只触发替代路径或 blocked，插件不提升权限。
- 不存在 SandboxBackend、HostAdapter、PermissionGrant、DecisionPackage、lease/fencing、ChangeSet merge 或 JSONL runtime store。
- 不存在 mandatory clarification/architecture/plan/test-plan/review/progress/completion 内容产物链；full
  必须有同级 `artifact-review.md`，其中包含可审计的 test-design decision；命中复杂验收条件时
  `test-plan.md` 是条件式必需产物。
- 完成判断引用当前 Codex task 的真实 diff、命令/页面结果和 acceptance。
- 行为 acceptance 以 Given/When/Then/Evidence 逐场景验收；代码有最终 C0 pass，失败修复后重跑原场景和关联回归。
- 用户可见 Web 行为优先且默认使用 Codex App Chrome 当前会话验证真实服务；Chrome 不可用不声称通过，也不静默退回 Playwright。
- plugin 安装或全局配置变更不属于静态测试，执行前必须单独确认。

## 风险与恢复

- 最大产品风险是 supporting skills 继续携带旧 lane/checklist 语义，导致主 skill 虽已简化但运行时仍回到旧流水线；必须通过 contract tests 搜索并阻止。
- 旧语义分散在 `SKILL.md`、引用的 reference/template、`config.default.yaml` 和 REDESIGN 文档中；清理与测试必须覆盖 active skill 的可达资源，不能只改主文件。
- Codex 不同 surface 暴露的 plan/subagent/tool 能力可能不同；Bruce 应按当前可用能力降级为主 Agent 顺序执行，而不是引入自建 runtime。
- 删除旧根 `SKILL.md` 和 checklist 入口会中断旧的直接 skill 安装方式，因此 README 必须先提供 plugin 安装路径；历史 run 不自动删除。
- 仓库内 marketplace 文件和静态测试只能证明 packaging 路径；真实 App 安装 smoke 会改变用户 Codex 安装状态，需要用户确认后执行并在新任务中验证 skill discovery。
- handoff 是可选快照；恢复时仍以当前仓库与 Codex task 事实为准，避免把过期文档当完成状态。

## 不涉及表结构变更

本计划只调整 Bruce plugin、skills、校验脚本和文档，不修改业务数据库 schema，因此不生成 `table-design.md`。
