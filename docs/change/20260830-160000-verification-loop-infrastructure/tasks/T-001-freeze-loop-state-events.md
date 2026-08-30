# T-001：冻结验证循环状态与事件协议

- Contract revision: 1

## Objective

定义 Bruce 工作流内部验证循环的状态、事件、证据新鲜度、下一步动作和 Completion ownership。

## Included scope

- `verification-loop`、`failure-recovery`、checkpoint、Goal、Completion Gate 的契约；
- `waiting_external`、`waiting_user`、`blocked`、`resume` 的状态转换；
- 阻塞通知的已知/未知事实和解锁条件。

## Excluded scope

- 任何项目 Adapter、CNB、Electron、Temporal、Kubernetes、业务 API 或数据库。

## Dependencies

- `requirements.md` AC-001、AC-003、AC-004、AC-005、AC-007；
- 现有 `skills/bruce/references/verification-loop.md` 和 `failure-recovery.md`。

## Acceptance

- 状态转换覆盖计划内等待、阻塞、用户恢复、证据失效和修复后复验；
- `blocked` 没有 `resume_event` 时禁止继续写入；
- Loop 状态和 checkpoint 不产生 Completion verdict；
- 恢复不重置失败预算。

## Authorization and risks

- Authorization：仅设计和契约变更，不授权项目环境接入、外部写入或部署。
- Risk：错误的状态转换可能在阻塞时继续修改代码，或把等待状态误报为完成。

## Contract change rule

状态、事件、冻结范围、恢复条件或 Completion ownership 发生变化时，必须增加 contract revision 或创建 superseding task；不得静默修改本 Task。

## Verification

使用状态机、事件 schema、checkpoint 和 Gate ownership 契约测试验证；不执行项目 Adapter。

## Stop conditions

协议字段、状态含义或 Gate ownership 不清晰时停止，不进入项目 Adapter 实现，返回设计问题。
