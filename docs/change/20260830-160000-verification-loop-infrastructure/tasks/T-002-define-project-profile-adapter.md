# T-002：定义项目 Verification Profile 与 Adapter 边界

- Contract revision: 1

## Objective

定义项目如何声明环境相关验证阶段，以及 Adapter 如何返回事实和证据，而不把项目环境耦合到 Bruce 核心。

## Included scope

- Profile schema；
- `skills/verification-profile` supporting skill、schema reference 和输出模板；
- Adapter input/output；
- 异步外部事件、产物 identity、部署 identity 和用户 handoff 的字段；
- Multica CNB/客户端与 Joytime Web/runtime 的示例映射。

## Excluded scope

- 实现任何 Multica、Joytime、CNB、集群、Electron 或浏览器 Adapter。

## Dependencies

- T-001 的状态、事件和证据协议；
- `requirements.md` AC-002、AC-003、AC-006。
- 现有 supporting skill、artifact placement 和 document language 约定。

## Acceptance

- 两个不同 Profile 可以表达不同阶段和外部等待；
- `verification-profile` skill 可被插件发现，并生成项目自适应 Profile，而不执行项目环境；
- Adapter success 不生成 Completion pass；
- 缺能力或结果未知时能进入 `waiting_external`/`blocked`；
- 事件必须携带 task、acceptance、basis revision 和 evidence refs。

## Authorization and risks

- Authorization：仅定义通用接口和示例，不授权访问项目凭证、CNB、集群或生产环境。
- Risk：Profile 过度假设项目环境会导致错误验证或伪造证据。

## Contract change rule

Adapter 输入输出、Profile 状态或证据要求发生变化时，必须增加 contract revision；不得为兼容项目而改变 Bruce 核心语义。

## Verification

使用 Profile/Adapter fixture 和边界测试验证；不运行具体项目命令。

## Stop conditions

若 Profile 需要 Bruce 猜测项目环境、凭证或部署事实，停止并返回项目侧设计问题。
