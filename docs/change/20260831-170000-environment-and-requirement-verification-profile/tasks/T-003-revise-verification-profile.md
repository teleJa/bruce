# T-003：改造 verification-profile 为需求级生成

- Contract revision: 1

## Objective

让 `$verification-profile` 强制读取用户指定的 `requirements.md`，并生成当前需求的验收、环境、账号、Skill、证据、修复和阻塞映射。

## Included scope

- `skills/verification-profile/SKILL.md`；
- profile schema/reference 和 verification-profile template；
- requirements path/hash/Acceptance coverage；
- Environment Profile references and revision matching；
- account requirements、Skill selections、diagnosis/repair、blocking/resume 和 confirmation。

## Excluded scope

- 生成项目 Environment Profile；
- 执行项目测试、CNB、部署、浏览器或用户手测；
- 修改 requirements.md 或生成 Completion verdict。

## Dependencies

- T-001 lifecycle/security contract；
- T-002 Environment Profile schema and confirmation；
- `requirements.md` AC-003、AC-004、AC-005、AC-006、AC-007、AC-008。

## Acceptance

- 缺少 requirements path 时返回 Missing requirements input；
- 每个重要 Acceptance 有环境、账号、Skill、证据和修复映射；
- 未确认或 stale 的环境引用不能进入 confirmed；
- Profile 默认 pending；
- 阻塞规则要求停止、通知、显式恢复和重新 preflight。

## Verification

执行 requirements binding、Acceptance coverage、environment reference、confirmation、security 和 blocking contract tests。

## Authorization and risks

- Authorization：只生成需求级验证设计，不授权运行外部动作或修改业务代码。
- Risk：错误的 Acceptance 映射可能让局部构建或错误账号被当成需求通过证据。

## Contract change rule

requirements input、Acceptance mapping、environment reference、account binding、Skill selection、evidence layer 或 repair boundary 变化时，必须增加 contract revision。

## Stop conditions

若无法读取 requirements.md、关键 Acceptance 无验证路径或 Profile 可以绕过确认，停止并返回 Missing verification evidence 或 issues。
