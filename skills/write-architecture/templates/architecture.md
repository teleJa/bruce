# Architecture: <change name>

## Objective and scope

- Objective: <observable outcome>
- Included: <components and responsibilities>
- Excluded: <explicit boundaries>

## Repository evidence

- <path or current interface> — <fact used by this design>

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
