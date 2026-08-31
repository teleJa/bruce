# 测试设计：Environment Profile 与需求级 Verification Profile

## 验证策略

本设计验证 Profile 的结构、来源、确认和需求映射契约，不执行 CNB、部署、数据库、浏览器或客户端操作。真实环境可用性必须由未来 Verification Run 的 preflight 和项目 Adapter/用户证据证明。

## 场景

### PROFILE-001：Environment Profile 默认未确认

- 映射：AC-001、AC-005
- Given：仓库发现本地测试、CNB、服务、账号池和浏览器 Skill 信息。
- When：运行 `$environment-profile` 生成 Profile。
- Then：生成环境身份、事实来源、能力、账号池、Credential 引用、Skill evidence boundary 和 preflight；`profile_state=ready_for_confirmation`，`confirmation.state=pending`。
- Evidence：Skill resource/metadata tests、schema fixture 和 template assertions。
- 必需验证层级：unit/contract。

### PROFILE-002：环境信息不足时要求用户补充

- 映射：AC-002、AC-006
- Given：仓库没有部署目标、账号初始状态或 Credential 来源的可验证事实。
- When：生成 Environment Profile。
- Then：记录 `unresolved_facts` 和最小用户问题；不写入猜测值或秘密值，状态保持 `draft` 或 `needs_input`。
- Evidence：missing-fact and secret-boundary tests。
- 必需验证层级：unit/contract。

### PROFILE-003：Verification Profile 必须读取 requirements.md

- 映射：AC-003
- Given：用户提供指定的 SSO requirements.md 路径。
- When：运行 `$verification-profile`。
- Then：Profile 记录 requirements path、content hash 和 AC-01 至 AC-08；没有路径时返回 `Missing requirements input`，不生成需求 Profile。
- Evidence：requirements input contract tests。
- 必需验证层级：unit/contract。

### PROFILE-004：需求 Acceptance 映射到环境和账号

- 映射：AC-004
- Given：SSO 需求的 AC-01 至 AC-08 和已确认 Multica Environment Profiles。
- When：生成需求级 Profile。
- Then：引用的 SSO fixture requirements.md 中的 AC-02/03/06 使用测试集群、新 SSO 账号和浏览器能力；AC-05 使用人工管理员账号和独立 SQL 授权；每个 fixture Acceptance 有证据和修复边界；Environment Profile 不出现这些需求 ID。
- Evidence：fixture mapping and coverage tests。
- 必需验证层级：unit/contract。

### PROFILE-005：Profile 精确确认

- 映射：AC-005
- Given：Profile revision 1 已生成但未确认。
- When：用户只说“继续”或确认 `profile_id + revision + content_hash`。
- Then：前者不能改变 confirmation；后者才能将对应 Profile 标记 confirmed；确认不产生 Completion verdict。
- Evidence：confirmation lifecycle tests。
- 必需验证层级：unit/contract。

### PROFILE-006：需求或环境变化使 Profile stale

- 映射：AC-008
- Given：requirements.md hash、环境 Profile revision、账号要求或证据层发生变化。
- When：检查 Profile freshness。
- Then：需求级 Profile 标记 `stale`，确认状态失效；重新生成/更新并再次确认后才可使用。
- Evidence：freshness matrix tests。
- 必需验证层级：unit/contract。

### PROFILE-007：阻塞必须停止和显式恢复

- 映射：AC-007
- Given：部署 revision 不匹配、账号状态不明、Credential 不可用或外部状态未知。
- When：验证循环分类为阻塞。
- Then：冻结受影响 Task/Batch 的写入、修复、重试和依赖工作；通知用户 known/unknown facts、影响范围和解锁条件；没有 resume event 时不能继续。
- Evidence：blocking/resume contract and checkpoint tests。
- 必需验证层级：unit/contract。

### PROFILE-008：动态结果不污染静态 Profile

- 映射：AC-009
- Given：一次 Verification Run 获得 build id、账号绑定、截图或失败结果。
- When：更新运行状态。
- Then：结果进入 Verification Run/Checkpoint，静态 Profile 只保留计划和确认 revision；Adapter/Skill/环境确认不能生成 Completion verdict。
- Evidence：dynamic boundary and Completion ownership tests。
- 必需验证层级：unit/contract。

## 状态与意图矩阵

| 状态 | 触发 | 预期行为 | 允许动作 |
|---|---|---|---|
| `draft` | 已生成但存在用户信息缺口 | 收集最小补充信息 | 不进入受控验证 |
| `needs_input` | 关键环境/账号事实缺失 | 向用户提问并等待 | 不执行依赖该事实的动作 |
| `ready_for_confirmation` | 结构完整且事实缺口已处理 | 展示确认摘要 | 等待精确确认 |
| `confirmed` | 用户确认精确 revision/hash | 允许作为 Bruce 验证输入 | 运行前仍需 preflight |
| `stale` | 输入或引用 revision 变化 | 清除确认并要求更新 | 不使用旧 Profile |
| `waiting_user` | 当前阶段需要用户操作 | 生成 handoff 并等待反馈 | 不修改当前受控范围 |
| `blocked` | 无法安全继续 | 停止、通知、等待 resume | 只读诊断 |

## 限制与未验证边界

- 不验证真实 CNB、部署、账号、API Key、Auth Center、Chrome、Desktop 或数据库可用性。
- 用户确认只证明其接受 Profile 内容，不证明运行时能力或需求已通过。
- Profile fixture 中只使用 Credential reference 和账号 alias，不使用真实秘密值。
- 只有未来真实 Verification Run 具备当前 revision、preflight 和证据后，才能关闭对应 Acceptance。

## 自检

- `$environment-profile` 不读取具体需求 AC，也不生成需求修复计划。
- `$verification-profile` 强制读取 requirements.md，并保持需求级 AC 映射。
- 两类 Profile 默认 pending，精确确认后才能被 Bruce 消费。
- 环境信息允许来自 user，但来源和 preflight requirement 已记录。
- Credential 只记录引用，不记录秘密值。
- 阻塞会停止受影响工作、通知用户并要求显式恢复。
- 动态结果与静态 Profile 分离，Completion Gate 仍是唯一完成判断。
