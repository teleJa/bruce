# T-001：冻结 Profile schema、来源与确认生命周期

- Contract revision: 1

## Objective

定义 Environment Profile 与 Requirement Verification Profile 的身份、revision、来源、确认、stale、动态结果和 Completion ownership。

## Included scope

- Profile lifecycle and confirmation schema；
- repository/user/runtime source classification；
- Credential and account security boundary；
- static Profile 与 Verification Run/Checkpoint 的边界；
- blocking and explicit resume semantics。

## Excluded scope

- 具体项目 Adapter、CNB、部署、客户端、浏览器和数据库执行。

## Dependencies

- `requirements.md` AC-001、AC-005、AC-006、AC-008、AC-009；
- 现有 `verification-loop.md`、`failure-recovery.md`、`checkpoint.yaml` 和 Completion ownership 规则。

## Acceptance

- 新 Profile 默认 `confirmation.state=pending`；
- requirements/environment revision 变化会使引用 Profile stale；
- 静态 Profile 不记录动态执行结果；
- Credential 值、密码、Cookie、JWT 和 ticket 不进入 Profile；
- Profile 不产生 Completion verdict。

## Verification

使用 schema、lifecycle、security 和 ownership contract tests 验证；不访问项目环境。

## Authorization and risks

- Authorization：仅设计和契约变更，不授权外部系统、数据库或生产操作。
- Risk：确认或 stale 语义错误可能导致错误环境和旧证据被复用。

## Contract change rule

Profile 状态、确认字段、revision、secret policy 或动态结果边界变化时，必须增加 contract revision 或创建 superseding task。

## Stop conditions

若确认能够绕过用户精确 revision，或静态 Profile 可以伪造动态结果，停止并返回设计问题。
