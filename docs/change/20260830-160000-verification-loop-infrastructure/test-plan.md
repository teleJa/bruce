# 测试设计：Bruce 验证—反馈—修复循环基础设施

## 验证策略

本设计自身只验证契约和文档，不执行 CNB、部署、Electron、Joytime 服务或用户客户端。未来实现必须区分本地、Adapter、外部运行时和用户证据；mock 或自然语言结论不能替代被声明的真实层级。

## 场景

### LOOP-001：验证循环属于 Bruce 工作流

- 映射：AC-001
- Given：Task 已有 acceptance、verification layer 和 project profile。
- When：进入 implementation 的验证阶段。
- Then：Loop 复用 Task Contract、Checkpoint、Failure Policy、Goal 和 Completion Gate，不创建第二个 workflow 或 verdict。
- Evidence：契约测试、文档引用和 Completion ownership 断言。

### LOOP-002：Multica 与 Joytime 使用不同 Profile

- 映射：AC-002
- Given：Multica 需要 CNB/部署后客户端验证，Joytime 需要 Web/runtime 验证。
- When：生成两个验证图。
- Then：阶段、Adapter、等待节点和证据要求可以不同；Bruce 核心不出现项目命令。
- Evidence：Profile schema fixtures 和路径边界检查。

### LOOP-003：等待 CNB 或部署事件

- 映射：AC-003
- Given：本地检查通过，CNB 或部署结果尚未返回。
- When：提交异步外部动作。
- Then：状态为 `waiting_external`，记录 external identity 前置状态和 next action；不重复触发，不报告通过。
- Evidence：状态机/事件契约测试。

### LOOP-004：等待用户客户端测试

- 映射：AC-003、AC-006
- Given：构建产物和目标 revision 已确认，客户端真实行为仍需用户验证。
- When：生成 handoff。
- Then：状态为 `waiting_user`，handoff 包含版本、步骤、预期、证据要求；用户未反馈前不修复、不完成。
- Evidence：handoff schema 和状态转换测试。

### LOOP-005：发生阻塞时冻结并通知

- 映射：AC-004
- Given：外部状态未知、权限缺失、能力不可用或需要用户决策。
- When：分类为 L2/L3/L4 或 blocker。
- Then：冻结受影响 batch 的写入、修复、重试和依赖任务；输出已知/未知事实和精确解锁条件。
- Evidence：failure policy、blocking notification、checkpoint contract tests。

### LOOP-006：用户处理后恢复原 batch

- 映射：AC-005
- Given：用户明确提供 `resume_event` 并处理了 blocker。
- When：恢复执行。
- Then：保留 task/batch/contract revision，重新 preflight，使受影响旧证据 stale，继续原验证路径，不重置失败预算。
- Evidence：resume and stale-evidence tests。

### LOOP-007：用户反馈失败进入 bounded repair

- 映射：AC-006
- Given：用户回传确定版本上的可复现失败，并且失败属于当前允许范围。
- When：Loop 接收 `Verification Event(status=fail)`。
- Then：分类 L1，生成 bounded repair set，修复后重跑原始场景和相关回归；超过预算转 L2/报告用户。
- Evidence：failure classification and repair loop tests。

### LOOP-008：用户反馈不明确或范围变化

- 映射：AC-004、AC-006
- Given：用户只说“还是有问题”，或要求扩大范围/改变验收。
- When：Loop 接收 `unclear` 或 contract-changing feedback。
- Then：不猜测修复；分别要求最小事实或进入 L3，冻结受影响工作并等待用户决定。
- Evidence：unclear/L3 contract tests。

### LOOP-009：Completion ownership

- 映射：AC-007
- Given：Adapter、CNB、客户端或用户反馈均为成功。
- When：进入完成审查。
- Then：只有 Completion Gate 能返回 `Completion: pass|issues|blocked`；等待状态和 Adapter success 不能产生完成结论。
- Evidence：Completion contract regression tests。

## 状态与意图矩阵

| 状态 | 触发 | 预期行为 | 允许动作 |
|---|---|---|---|
| `waiting_external` | CNB/部署/运行时事件未返回 | 等待指定事件 | 只读独立工作 |
| `waiting_user` | 已生成用户 handoff | 等待结构化反馈 | 不修改当前验证范围 |
| `blocked` | L2/L3/L4 或未知外部状态 | 通知并冻结 | 只读诊断，待 resume |
| `repairing` | 确认是当前范围内可修复失败 | bounded repair | 仅允许路径 |
| `re_verifying` | repair 完成 | 重跑受影响证据 | 当前任务验证 |

## 限制与退出条件

- 本设计不证明任何项目 Adapter 已实现或任何 CNB/Desktop/Web 运行时已通过。
- 只有在项目 Profile、Adapter、外部事件回传和用户 handoff 均有真实证据后，才能把对应验收行标记为通过。
- 阻塞恢复必须由用户显式确认；新会话不能仅凭历史聊天自动恢复。

## 自检

- 覆盖了本地、外部、用户三类反馈。
- 明确区分 waiting、blocked、repairing 和 completion verdict。
- 阻塞时冻结写入并通知用户，恢复后重新 preflight。
- 没有把项目环境写入 Bruce 核心。
