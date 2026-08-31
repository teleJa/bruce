# 需求：可确认的环境 Profile 与需求级 Verification Profile

## Objective

将 Bruce 的验证配置拆为两个可协作但职责不同的 Profile：Environment Profile 描述项目中可复用的验证环境事实，Requirement Verification Profile 针对用户指定的 `requirements.md` 定义本次需求如何验收、如何诊断和修复。两个 Profile 默认均为未确认状态；只有用户确认指定 revision 后，Bruce 才能将其作为受控验证输入。

## 已确认原则

| ID | 原则 | 说明 |
|---|---|---|
| R-01 | requirements.md 是 Verification Profile 的强制输入 | 不允许仅根据项目目录、聊天内容或任意 test-plan 自动猜测当前需求。 |
| R-02 | Environment Profile 独立复用 | 账号、Credential 引用、构建、部署、服务、数据库、客户端和可用 Skill 属于环境资产，可被多个需求引用。 |
| R-03 | Verification Profile 需求级 | 它必须围绕指定 requirements.md 的验收标准定义验证、证据、诊断、修复、阻塞和恢复。 |
| R-04 | Profile 默认未确认 | 新生成或发生实质变化的 Profile，其 `confirmation.state` 必须为 `pending`；不得直接进入受控验证。 |
| R-05 | 用户确认精确 revision | 用户必须确认展示的 Profile 身份、revision、需求来源、环境、账号要求、Skill、证据和修复边界。模糊的“继续”不等于 Profile 确认。 |
| R-06 | 环境事实允许来自用户 | 仓库无法证明的环境、账号和运维知识可以由用户提供，但必须记录来源为 `user`，并由用户确认；运行前仍需 preflight。 |
| R-07 | 秘密值永不进入 Profile | API Key、密码、Cookie、JWT、SSO ticket 和其他 Credential 值不得写入 Profile、Checkpoint、Handoff 或聊天摘要。只记录安全引用和使用方式。 |
| R-08 | Profile 不产生完成结论 | Profile、环境确认、Skill、Adapter 和验证运行都不能替代 Design Gate 或 Completion Gate。 |
| R-09 | 阻塞必须停止并通知 | 发生环境未知、权限不足、版本不匹配、账号状态不明或外部状态未知时，停止受影响 Task/Batch，通知用户并等待显式恢复。 |

## Scope

- 新增 `$environment-profile` supporting skill，生成可复用的环境 Profile。
- 将 `$verification-profile` 改为强制消费 `requirements.md` 和已确认的 Environment Profile，生成需求级验证与修复 Profile。
- 定义 Profile revision、来源、用户确认、拒绝、过期和 supersede 语义。
- 定义项目环境、账号池、Credential 引用、构建、部署、服务、数据库、客户端和可用 Skill 的记录边界。
- 定义需求 Acceptance、Scenario、Environment、Account、Skill、Evidence、Repair、Blocking 和 Resume 的映射。
- 定义 Profile 被 Bruce 使用前的确认条件，以及需求或环境变化后的失效规则。
- 更新 Bruce 文档、模板、契约测试和插件 Skill 元数据。

## Non-scope

- 不实现 CNB、Temporal、Kubernetes、Electron、浏览器、数据库或任意项目 Adapter。
- 不自动读取、保存或传播密码、API Key、Cookie、JWT、SSO ticket 或其他秘密值。
- 不把用户确认实现成第三个 Gate；Design Gate 和 Completion Gate 的 ownership 不变。
- 不在 Profile 文件中记录某次执行的实时状态、测试通过结果、当前 build id 或最终完成结论。
- 不自动选择用户未确认的测试账号、部署目标、外部写操作或生产环境。
- 不修改 Multica、Joytime 或其他项目的业务代码、部署配置和数据库 schema。

## Acceptance scenarios

### AC-001：Environment Profile 可独立复用

- Given：项目存在可复用的本地、测试集群、Web、Desktop、数据库、账号或构建环境信息。
- When：使用 `$environment-profile` 扫描仓库并收集用户补充信息。
- Then：生成带有环境身份、事实来源、构建/部署方式、账号池、Credential 引用、可用 Skill、preflight 和 freshness 规则的 Environment Profile；Profile 默认未确认。
- Evidence：Profile schema、模板和 supporting skill contract tests。

### AC-002：环境未知时向用户收集信息

- Given：仓库无法证明某个验证所需的部署目标、账号状态、Credential 来源或操作授权。
- When：生成 Environment Profile。
- Then：记录 `unresolved_facts` 和最小用户问题，状态为 `draft` 或 `needs_input`；不得用猜测、历史默认值或项目常识替代事实。
- Evidence：信息缺口场景和 fail-closed contract tests。

### AC-003：Verification Profile 强制绑定 requirements.md

- Given：用户提供一个明确的 `requirements.md` 路径。
- When：使用 `$verification-profile` 生成需求级 Profile。
- Then：Profile 记录需求路径、hash/revision、验收 ID，并以该文件的 Acceptance 为权威输入；未提供 requirements path 时不生成需求级 Profile。
- Evidence：input contract tests and requirements binding schema。

### AC-004：需求级验收与环境能力映射

- Given：requirements.md 定义了多个 Acceptance，Environment Profile 定义了不同环境能力。
- When：生成 Verification Profile。
- Then：每个重要 Acceptance 映射到具体验证阶段、环境 Profile、账号要求、Skill/capability、证据、失败诊断和修复边界；不把 Acceptance 写回可复用 Environment Profile。
- Evidence：需求映射 schema、Multica SSO fixture 和 coverage tests。

### AC-005：默认未确认与精确确认

- Given：Environment Profile 或 Verification Profile 刚生成，或其输入发生实质变化。
- When：查看 Profile 或尝试启动受控验证。
- Then：`confirmation.state=pending`，Profile 不可用于受控验证；用户确认精确 Profile revision 后才可被 Bruce 消费。
- Evidence：lifecycle schema and confirmation contract tests。

### AC-006：用户提供的账号和 Credential 信息安全落盘

- Given：用户补充账号、API Key 来源、登录态、部署权限或数据库访问方式。
- When：Bruce 更新 Environment Profile 或 Verification Profile。
- Then：只记录账号 alias/pool、用途、初始状态、Credential 引用、权限和来源；不记录秘密值；用户确认仍不等于运行时可用。
- Evidence：secret redaction and profile boundary tests。

### AC-007：阻塞停止、通知和显式恢复

- Given：环境能力不可用、账号状态不明、部署 revision 不匹配、外部状态未知或需要用户处理。
- When：验证循环发现无法安全继续。
- Then：停止受影响 Task/Batch 的写入、修复、重试和依赖工作，生成阻塞通知和精确解锁条件；用户处理并显式恢复后，才可重新 preflight 并继续原验证路径。
- Evidence：blocking/resume contract and checkpoint mapping tests。

### AC-008：Profile 失效与重新确认

- Given：requirements.md、Environment Profile、账号要求、证据层、选定 Skill 或部署拓扑发生影响验证语义的变化。
- When：Bruce 检查 Profile freshness。
- Then：标记受影响 Profile 为 `stale`，清除其可用确认状态；重新生成或更新后必须由用户确认新 revision。
- Evidence：freshness matrix and stale invalidation tests。

### AC-009：Completion ownership 不变

- Given：Profile 已确认，部分验证步骤成功，仍有未完成或用户等待的 Acceptance。
- When：Bruce 执行需求验证或完成审查。
- Then：Profile 只提供验证计划和证据要求；`waiting_user`、环境确认和 Adapter 结果不能生成 `Completion: pass`；最终仍由 Completion Gate 判断。
- Evidence：Completion ownership regression tests。

## 约束与风险

- 环境 Profile 是可复用的事实契约，不是当前运行结果；所有动态结果必须进入 Verification Run/Checkpoint。
- 用户确认的是 Profile 内容和 revision，不是测试通过，也不是外部系统可用。
- Profile 中的 Skill 仅表示选择和用途；Skill 存在、Provider 配置存在或 Credential 引用存在，都不能替代运行时 preflight。
- 需求级 Profile 可以引用多个环境 Profile，但每个被引用的环境 Profile 必须处于 `confirmed` 且 revision 匹配。
- 任何会改变环境目标、账号状态、证据层、修复范围或外部授权的修改，都要使确认失效。
