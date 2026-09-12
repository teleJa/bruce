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

## Workflow roles and review gates

- Design thread/profile: `Astra / design`
- Plan review: required independent `reviewer` subagent, clean context, no author history
- Execution thread/profile: `Luna Max / implementer` (actual model is resolver-owned)
- Completion review: required fresh independent `reviewer` subagent, clean context, no executor history
- Final decision: `Bruce Completion Gate`

Plan review and completion review are separate review events. Executor self-checks, author review,
and verifier evidence cannot replace either reviewer. A repair or acceptance change requires a new
snapshot and `basis_revision` before re-review.

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

Use the shared `implementation-preparation.md` rule. Carry forward the existing budget for the same
slice/gaps; it must not reset on delegation, executor changes, or another durable handoff.

- Focused evidence rounds: at most `2` (a narrower existing budget wins)
- Consumed rounds (parent + executors): `<observed total>`
- Remaining rounds: `<limit minus consumed; zero when exhausted>`
- Extension already used: `<yes/no; named blocker, concrete queries, stop condition if used>`

| Gap ID | Blocking fact / acceptance | Rounds already used / evidence | Remaining check / round ceiling |
|---|---|---|---|
| G-001 | `<fact / acceptance id>` | `<round ids and findings>` | `<smallest check within remaining budget>` |

All gap rows draw from the same shared round budget, not separate per-gap allowances. Record a round
covering multiple gaps once in the consumed total. No gaps means no additional discovery allowance.
Missing consumption data is unknown, not zero. When additional investigation is needed, recover it
from existing parent evidence before dispatch; if unavailable, report the affected boundary rather
than grant a fresh budget. If no investigation gaps remain and safety prerequisites are confirmed,
keep missing consumption unknown and proceed directly to editing or verification with no additional
investigation or extension allowance. Budget bookkeeping must not block a ready safe slice or skip
current-source safety checks.

Calls, reads, and output caps are additional ceilings, not new allowances; there is no conversion from
calls to rounds. Record their consumed/remaining amounts across parent and executors as well. Stop at
whichever ceiling is reached first; unused calls cannot buy another evidence round.

- Maximum discovery calls before the first edit: `12` total; consumed `<n>`, remaining `<n>`
- Maximum full-file or multi-range reads before the first edit: `3` total; consumed `<n>`, remaining `<n>`
- Maximum source output before the first edit: `120000` characters total; consumed `<n>`, remaining `<n>`
- Preferred search mode: `compact` with a narrow limit
- After a ceiling is reached: stop discovery. Start only a ready safe slice; otherwise report the affected
  boundary and continue independent ready work. The shared rule permits at most one named extra round;
  carry forward its used state, and it does not replenish any exhausted call/read/output ceiling.

## Stop conditions

Begin implementation once all `executor_must_verify` items and implementation-map joins are confirmed.
Stop and return a bounded conflict when a frozen decision, allowed path, acceptance condition, or required
verification command is contradicted. Do not widen scope to resolve an unrelated uncertainty.

## Open risks

- `<risk, impact, and smallest safe response>`
