# Architecture: <change name>

## Objective and scope

- Objective: <observable outcome>
- Included: <components and responsibilities>
- Excluded: <explicit boundaries>

## Repository evidence

- <path or current interface> — <fact used by this design>

## Reuse contracts

对每一项“复用已有能力/沿用现有流程/与现有页面一致”的声明，必须填写一条可执行的复用契约，不能只写概念描述。

| reuse_id | 复用对象 | 权威实现锚点 | 输入契约与禁止新增参数 | 输出/用户可观察契约 | 允许变化 | 禁止变化 | 验证方式 |
|---|---|---|---|---|---|---|---|
| <id> | <能力/API/组件/流程> | <path + symbol/route> | <caller, params, defaults> | <response and visible behavior> | <allowed delta> | <forbidden divergence> | <static/test/API/UI evidence> |

每条复用契约必须同时产生至少一个正向验收项和一个负向验收项，并被 `test-plan.md` 与实施计划引用。无法确认权威实现锚点时不得自行创建替代实现，应将其列为 Open decision 或阻塞项。

## Current-to-target delta

- Existing capabilities: <repository-backed capabilities reused by this design>
- Changed behavior: <observable behavior that changes>
- Preserved behavior: <existing behavior that must remain compatible>
- New responsibilities: <new component or ownership responsibilities>
- Unverified assumptions: <facts still requiring bounded evidence; none if none>

## Components and ownership

| Component | Existing stack/deliverable | Owns | Does not own |
|---|---|---|---|
| <name> | <real repository evidence> | <responsibility> | <boundary> |

## Data and control flow

1. <caller/action> -> <provider> -> <result or event>

## Decisions

### <decision>

- Chosen: <option>
- Rationale: <trade-off and repository fit>
- Rejected: <alternatives and why>
- Reversibility: <cost and recovery>

## Domain semantics and authority

- Domain objects and relationships: <objects and relationships; not_applicable with reason if irrelevant>
- State ownership and transitions: <who may change which state and allowed transitions>
- Authority and invariants: <authoritative state source and invariants; not_applicable with reason if irrelevant>
- Concurrency/retry/idempotency: <semantics; not_applicable with reason if irrelevant>
- Conflict/error semantics: <winner, rejection, preservation, and recovery rules>

## Contracts

- <api-contracts.md#anchor, or none with reason>

## Cross-cutting behavior

- Compatibility/versioning: <behavior>
- Authentication/authorization: <behavior>
- Failure and recovery: <behavior>
- Observability: <signals>
- Rollout/rollback: <steps>

## Verification impact

- <acceptance condition> -> <test or visible check>

## Open decisions

- <only decisions that genuinely require authority; otherwise none>
