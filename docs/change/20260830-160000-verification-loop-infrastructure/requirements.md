# 需求：项目自适应的验证—反馈—修复循环基础设施

## 目标

Bruce 仍然是一个用户驱动的软件交付工作流；验证循环是 Bruce 工作流中的一个组成部分。Bruce 不包办项目构建、部署、客户端或运行时验证，而是根据项目提供的验证能力，生成并驱动一套有状态、可反馈、可恢复的验证—反馈—修复循环。

当验证依赖 CNB、集群、Electron、浏览器、外部服务或用户本机时，Bruce 必须把外部能力纳入同一循环：记录等待状态、证据版本、下一步动作和恢复条件；不能把外部验证留在流程之外，也不能把局部成功升级为整体完成。

## 范围

- 定义 Bruce 工作流内验证循环的统一状态、事件、证据和下一步动作语义。
- 定义项目 Verification Profile 与 Verification Adapter 的边界，允许 Multica、Joytime 等项目提供不同的构建、部署和运行时验证策略。
- 定义 `waiting_external`、`waiting_user` 与 `blocked` 的区别和转换规则。
- 明确发生阻塞时必须停止受影响范围的写入、修复和依赖工作，通知用户；用户处理并显式恢复后，重新执行必要 preflight 和失效证据检查，再继续原 batch。
- 保留 Design Gate、Completion Gate 的唯一裁决权；Loop 状态和 Adapter 成功不能替代 Gate verdict。
- 为未来实现提供 machine-readable contract、checkpoint、handoff 和事件回传的设计依据。

## 非范围

- 不在 Bruce 核心内置 CNB、Temporal、Kubernetes、Electron、Joytime、Multica 或任一项目的部署命令。
- 不实现具体项目 Adapter、CNB webhook、Desktop 自动化或浏览器 runtime。
- 不改变现有 Design Gate、Completion Gate 的唯一裁决权。
- 不把 `waiting_user` 或 `waiting_external` 当作 `pass`，不允许凭空生成外部验证证据。
- 不在本设计中修改业务 API、数据库 schema、应用部署配置或项目代码。

## 验收场景

### AC-001：验证循环属于 Bruce 工作流

- Given：Bruce 执行一个包含本地、外部服务或用户验收的 Task。
- When：生成执行计划并进入验证阶段。
- Then：验证循环作为 Bruce 工作流的一部分，沿用 Task Contract、Failure Policy、Checkpoint、Goal Execution 和 Completion Gate；不创建第二套独立工作流或第二个终局裁决器。
- Evidence：`architecture.md`、`api-contracts.md`、`plan.md` 与现有 `skills/bruce/SKILL.md` 的边界映射。

### AC-002：项目环境由 Profile/Adapter 提供

- Given：两个项目的构建、部署和真实使用验证方式不同。
- When：Bruce 为 Task 生成验证循环。
- Then：循环只消费项目 Verification Profile 和 Adapter 能力，不假设所有项目使用同一构建、部署或客户端验证方式。
- Evidence：Profile/Adapter 契约、`verification-profile` skill、Multica 与 Joytime 的示例映射和契约测试设计。

### AC-003：外部等待状态可恢复

- Given：验证需要等待 CNB、部署结果或用户手测。
- When：本地可执行验证已经完成，但外部结果尚未返回。
- Then：Task 进入 `waiting_external` 或 `waiting_user`，记录 task、acceptance、basis revision、产物/目标和下一动作；不报告通过，不重复触发同一外部动作。
- Evidence：状态转换矩阵、checkpoint schema、handoff contract。

### AC-004：阻塞时停止并通知用户

- Given：发生 L2/L3/L4、必需能力不可用、外部状态未知或需要用户处理的阻塞。
- When：Bruce 判定当前 batch 无法安全继续。
- Then：立即停止受影响 batch 的写入、修复、重试和依赖任务；向用户报告已知事实、未知事实、阻塞原因、影响范围和精确解锁条件。用户未显式恢复前不得继续。
- Evidence：Failure Policy 扩展、`blocked` checkpoint、用户通知/恢复事件契约和测试场景。

### AC-005：用户处理后从原上下文恢复

- Given：用户已处理阻塞并明确要求继续，或外部能力事实已发生变化。
- When：Bruce 恢复原 batch。
- Then：使用同一 task/batch/contract revision，重新执行受影响 preflight，标记旧证据 stale，并从最近安全 checkpoint 继续；不重置失败预算、不绕过原始失败场景和相关回归。
- Evidence：resume checkpoint、事件契约、failure-recovery 和 Goal Execution 规则。

### AC-006：验证反馈驱动修复而非自然语言猜测

- Given：验证返回失败、通过、阻塞或不明确结果。
- When：Bruce 接收本地、Adapter 或用户反馈。
- Then：反馈被规范化为带有证据、版本、场景和观察结果的 Verification Event；可修复且在范围内的失败进入 bounded repair set，阻塞进入停止通知，不明确结果不得直接修复或通过。
- Evidence：事件 schema、失败映射矩阵和修复/复验场景。

### AC-007：完成仍由 Completion Gate 判断

- Given：验证循环产出若干成功、等待、失败或阻塞状态。
- When：所有必要证据已收集并进入完成审查。
- Then：只有 `Completion: pass|issues|blocked` 产生终局判断；Loop、Profile、Adapter、CNB、客户端或用户反馈不能单独产生完成结论。
- Evidence：Completion Gate 契约与回归测试设计。
