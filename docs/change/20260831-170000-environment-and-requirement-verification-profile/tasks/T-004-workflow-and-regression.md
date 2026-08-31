# T-004：接入 Bruce workflow 文档与回归

- Contract revision: 1

## Objective

将两个 Profile 纳入 Bruce 工作流的验证循环边界，并保持用户阻塞、Checkpoint、Goal 和 Completion ownership 一致。

## Included scope

- Bruce 主工作流和 verification-loop/failure-recovery 文档；
- Goal resume、Checkpoint、Completion Gate 的 Profile 使用条件；
- 两个新/改造 Skill 的 discoverability 和 supporting contract regression。

## Excluded scope

- 项目环境执行器、运行时状态机、CNB/部署、业务代码和远程交付。

## Dependencies

- T-001、T-002、T-003 的 schema 和 Skill contract；
- `requirements.md` AC-007、AC-009。

## Acceptance

- 未确认 Profile 不得作为受控验证输入；
- 阻塞时停止受影响工作并通知用户，用户显式恢复后才能继续；
- Profile、Adapter、Checkpoint 和 Skill 不产生 Completion verdict；
- 旧 verification-profile 项目级语义被需求级语义替代，不保留矛盾规则。

## Verification

执行 Bruce 全量契约测试、插件校验、Design Review validator 和 `git diff --check`。

## Authorization and risks

- Authorization：只更新 Bruce 文档、Skill、模板和测试，不授权项目环境操作。
- Risk：workflow 文档和 Profile lifecycle 不一致会产生未确认执行或第二个完成判断源。

## Contract change rule

任何 Profile 使用条件、阻塞传播或 Completion ownership 变化必须同步更新主工作流、references、模板、测试和本 Task revision。
