# 架构：Bruce 验证—反馈—修复循环基础设施

## 目标与范围

本设计把验证循环定义为 Bruce 工作流内部的一个可插拔执行层：Bruce 负责统一语义、状态、证据、失败恢复、用户阻塞交互和最终门禁；项目负责提供环境特定的验证 Profile 与 Adapter。

本设计只冻结通用边界和协议，不实现任何项目环境接入。

## 分层

### 1. Bruce Workflow Core

继续拥有：

- Task Contract、Acceptance、Given/When/Then/Evidence；
- profile/risk/visual scope；
- Design Gate 与 Completion Gate；
- L0-L4 failure/recovery policy；
- Goal、Checkpoint、Resume 和用户驱动的阶段边界。

验证循环不是新的工作流，也不是新的 Gate，而是 Bruce 在 implementation workflow 中执行验证、接收反馈和安排修复的统一机制。

### 2. Verification Loop Kernel

新增的通用职责：

- 从 Task Contract 和项目 Profile 生成当前 batch 的 verification graph；
- 管理 `ready → running → waiting_external|waiting_user → evaluating → repairing → re_verifying → passed|blocked` 状态；
- 维护 run、attempt、basis revision、evidence revision 和 next action；
- 将 Adapter/User 反馈归一化为 Verification Event；
- 按 Failure Policy 选择 retry、repair、replan、notify-and-stop 或 resume；
- 在恢复前重新检查外部能力并使受影响旧证据失效；
- 将当前结果交给 Completion Gate，而不是自行宣布完成。

### 3. Project Verification Profile

Bruce 提供 `skills/verification-profile` supporting skill 生成 Profile 初稿；该 skill 只负责基于项目证据产出描述，不执行验证动作、不维护运行状态。

Profile 是项目对验证策略的声明，不是 Bruce 核心代码。它描述：

- 验证阶段和依赖关系；
- 每阶段所需 capability；
- Adapter 名称和输入输出；
- 证据类型与 acceptance 映射；
- 异步等待、用户手测和回滚/止损要求；
- 允许的 retry/repair budget 与 stop condition。

Profile 可以由 Bruce 根据仓库结构和项目文档生成初稿，但在进入受控实现前必须由项目确认；Bruce 不根据猜测补齐部署或运行时事实。

### 4. Verification Adapter / External Actor

Adapter 负责调用项目环境或外部能力，并返回事实，不返回 Bruce 的终局 verdict。典型 Adapter 包括：

- Multica CNB/build/deployment adapter；
- Multica Desktop/user handoff adapter；
- Joytime web-service/runtime/browser adapter；
- 浏览器、数据库或其他外部依赖 adapter。

用户手测属于一种 External Actor：Bruce 生成精确 handoff，用户执行并回传结构化结果；用户反馈进入同一 Verification Event 管道。

## 核心状态边界

| 状态 | 含义 | Bruce 行为 | 是否可继续写入 |
|---|---|---|---|
| `running` | 当前验证动作正在执行 | 等待有限时间并记录 handle | 仅限当前安全动作 |
| `waiting_external` | 等待 CNB、部署、服务或其他外部事件 | 停止依赖该结果的动作，等待事件 | 否 |
| `waiting_user` | 已准备好用户手测，等待用户按 handoff 执行 | 生成步骤和证据要求，等待用户结果 | 否 |
| `blocked` | L2/L3/L4 或能力/权限/外部状态阻止安全继续 | 停止受影响 batch，通知用户并记录解锁条件 | 否 |
| `repairing` | 已确认 bounded、在范围内且可安全修复 | 执行 repair set，保留原始失败场景 | 仅限 repair set |
| `re_verifying` | 修复后重新验证 | 重跑受影响行、原始失败和相关回归 | 仅限当前任务 |
| `passed` | 当前验证节点证据满足要求 | 推进验证图或交给 Completion Gate | 由后续边界决定 |

`waiting_user`/`waiting_external` 是计划内等待，不等于失败；`blocked` 是安全停止状态，也不是完成失败的替代 verdict。所有等待和阻塞都不能被提升为 `pass`。

## 阻塞与恢复规则

1. 识别为阻塞后，立即冻结受影响 batch 的行为编辑、修复、重试和依赖任务。
2. 输出一条面向用户的阻塞通知，至少包含：`run_id`、`task_id`、`batch_id`、当前 revision、已完成证据、未知事实、影响范围、停止原因和精确解锁条件。
3. 用户处理后必须显式发送 resume/continue 意图；不得因为下一轮对话自动恢复。
4. 恢复时保留原 task、batch 和 contract revision；重新执行必要 preflight，失效受影响旧证据，继续原始验证路径。
5. 恢复不能重置 L0/L1 retry/repair budget，也不能删除原始失败证据。
6. 若恢复后范围、验收、权限或风险发生变化，先转 L3/新 contract revision，不直接继续旧任务。

## 项目映射示例

### Multica

```text
local-check
→ CNB build
→ deployment identity
→ Desktop artifact/client verification
→ waiting_user
→ user feedback
→ repair/re-verify or Completion Gate
```

CNB 是否成功、部署到哪个 revision、Desktop 是否使用该版本，必须由对应 Adapter/用户证据分别证明。

### Joytime

```text
local/service checks
→ runtime dependency preflight
→ API/integration checks
→ configured browser smoke/layout
→ user or runtime feedback
→ repair/re-verify or Completion Gate
```

Bruce 不假设 Joytime 使用 Multica 的 CNB 或 Desktop 策略。

## 当前仓库证据与缺口

- `skills/bruce/references/verification-loop.md:7-18,45-63,84-121,123-213` 已定义验收证据、能力 preflight、分层验证、批次矩阵、checkpoint 与 bounded repair。
- `skills/bruce/references/failure-recovery.md:6-39` 已定义 L0-L4、失败预算、工作间隔 checkpoint 和未知外部状态冻结规则。
- `skills/completion-gate/SKILL.md:67-101,229-249` 已定义最终矩阵、修复轮次和唯一 Completion verdict。
- 当前缺口是没有通用 Verification Profile/Adapter/Event 运行时，也没有统一的用户阻塞通知和恢复协议；本设计将其作为后续实现边界，而不把项目环境硬编码进 Bruce。
- `skills/verification-profile` 是 Profile 生成入口，不是 Verification Run 执行器或 Completion Gate。
- Multica 的项目级 managed-delivery 设计可在其自身仓库内实现 CNB/Temporal/人等待，但不应直接成为 Bruce 核心依赖。
