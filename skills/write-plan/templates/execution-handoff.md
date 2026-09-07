# Execution handoff

> This is the bounded implementation contract produced from a confirmed design. It is not a second
> design source of truth. Reinspect only the items marked `executor_must_verify`; do not reopen frozen
> design decisions unless current repository evidence directly conflicts.

## Handoff identity

- Parent plan: `<path>`
- Design review: `<path and verdict>`
- Design model/profile: `<profile/model if known>`
- Execution profile/model: `<profile/model if known>`
- Handoff revision: `1`

## Frozen scope

### Allowed paths

- `<path or symbol>`

### Excluded paths and decisions

- `<path, component, contract, or behavior that must not be changed>`

## Confirmed decisions

| ID | Decision | Evidence | Executor action |
|---|---|---|---|
| D-001 | `<frozen decision>` | `<source path/section>` | `accept` |

Use `accept` for a frozen decision, `verify_signature_only` for a narrow compatibility check,
`executor_must_verify` for an unresolved repository fact, and `escalate_if_conflict` when a conflict
returns control to Bruce/design review.

## Implementation map

| Step | File/symbol | Action | Depends on | Acceptance/evidence |
|---|---|---|---|---|
| I-001 | `<path#symbol>` | `create|modify|delete|verify` | `<ids>` | `<ids/command>` |

## Required verification

- `<exact command or check>`

## Investigation budget

- Maximum discovery calls before the first edit: `12`
- Maximum full-file or multi-range reads before the first edit: `3`
- Maximum source output before the first edit: `120000` characters
- Preferred search mode: `compact` with a narrow limit
- After the budget is reached: stop broad discovery, record unknowns, and use the smallest safe implementation

## Stop conditions

Begin implementation once all `executor_must_verify` items and implementation-map joins are confirmed.
Stop and return a bounded conflict when a frozen decision, allowed path, acceptance condition, or required
verification command is contradicted. Do not widen scope to resolve an unrelated uncertainty.

## Open risks

- `<risk, impact, and smallest safe response>`
