# T-004：更新文档与 Gate 回归

- Contract revision: 1

## Objective

将验证循环、Profile/Adapter、阻塞通知、用户恢复和 Completion ownership 纳入 Bruce 文档与契约测试。

## Included scope

- Bruce 主工作流说明；
- verification-loop、failure-recovery、Goal、Completion 文档；
- checkpoint/handoff 模板；
- 契约测试与文档检查。

## Excluded scope

- 项目实现和外部环境接入；
- 插件刷新、提交、推送和部署。

## Dependencies

- T-001、T-002、T-003 的协议设计；
- `requirements.md` AC-001、AC-004、AC-007。

## Acceptance

- Bruce 文档明确 Loop 是工作流内组成部分；
- 阻塞时冻结受影响范围并通知用户，恢复必须显式；
- 不把 Adapter、CNB、客户端或用户反馈升级为 Completion pass；
- 现有 Gate ownership 和 evidence freshness 规则保持一致。

## Authorization and risks

- Authorization：仅文档和契约回归，不授权业务代码或外部环境变更。
- Risk：文档与模板不一致会使后续实现产生第二套状态或完成判断。

## Contract change rule

任何新增状态、事件或 Gate ownership 变化必须同步更新 requirements、architecture、api-contracts、test-plan 和本 Task 的 revision。

## Verification

执行 Bruce 全量契约测试、Design Review validator 和 `git diff --check`。

## Stop conditions

若文档出现第二个完成裁决源，或阻塞路径可继续写入，任务必须返回 issues，不得进入实现。
