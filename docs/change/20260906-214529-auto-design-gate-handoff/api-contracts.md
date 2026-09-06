# 工作流与 Skill handoff 合同

## Mandatory Design Gate handoff

当方案 writer 已成功持久化会约束后续实现的设计工件，并完成 `Document check` 后，输出必须包含可被 Bruce 消费的强制 handoff 语义：

- Applicability：由 `artifact-policy.md` 判断为需要 Design Gate。
- Continuation：调用方必须在当前轮次立即调用 `design-gate`。
- User interaction：不得要求用户再次输入 Design Gate 指令；已有设计/实现请求已经授权这一步门禁检查。
- Authority：writer 不产生 `Design: pass|blocked`，Design Gate 仍是唯一裁决者。

## 非适用合同

以下情况不自动触发：

- 仅有执行清单且没有治理型设计决定或下游合同；
- 普通进度说明、现有命令列表或文档编辑；
- 工件尚未成功写入或局部检查仍有问题；
- 需要用户确认的原型仍处于 pending。

## Gate 后续合同

- `design-only`：报告工件与 Gate 结果后停止，不执行实现或 Completion Gate。
- `implementation`：用户已授权实现时，只有当前 Gate 和 validator 均通过才进入受影响实现。
- `Design: blocked`：报告阻塞项和最小修复动作，不等待用户重复发出 Gate 指令来完成当前门禁本身。

## 兼容边界

不新增命令、CLI、Hook verdict、Skill id、持久化 schema 或配置字段。现有 `design-gate` 输入、输出与 validator 命令保持不变。
