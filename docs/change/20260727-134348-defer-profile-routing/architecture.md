# Architecture: defer profile routing

## Objective and scope

- Objective: make `standard`/`full` a repository-evidenced result of bounded inspection and prevent
  an unresolved or full profile from automatically cascading into Goal, design review, or test
  design.
- Included: Bruce task-contract formation, capability routing, Goal entry, Design Gate entry,
  test-design invocation, README and skill metadata guidance, and contract tests.
- Excluded: risk classification, L0-L4 recovery, native Goal implementation, host permissions,
  deployment, persistence, root plugin metadata, and compatibility shims for the previous routing
  contract.

## Repository evidence

- `skills/bruce/SKILL.md` uses `unresolved` during bounded read-only inspection and requires a
  resolved profile before behavior implementation.
- `skills/bruce/SKILL.md` requires named components, propagated contract or independent delivery
  boundary, and repository evidence for `full`.
- `skills/design-gate/SKILL.md` enters only for persisted downstream-governing design; profile alone
  is not an entry predicate.
- `skills/goal-execution/SKILL.md` enters only for explicit Goal intent or a task-contract
  persistence/audit requirement.
- `skills/write-tests/SKILL.md` applies acceptance-complexity triggers for any resolved profile.
- `tests/test_workflow_profiles.py` and related routing tests make those conditions executable.

## Components and ownership

| Component | Existing stack/deliverable | Owns | Does not own |
|---|---|---|---|
| Bruce router | `skills/bruce/SKILL.md` | bounded inspection, profile resolution, capability selection | Goal lifecycle or artifact contents |
| Goal execution | `skills/goal-execution/SKILL.md` | explicit persistence/audit entry and native Goal lifecycle | topology classification or gate verdicts |
| Design Gate | `skills/design-gate/SKILL.md` | completeness and readiness of persisted downstream design | deciding whether work is multi-component |
| Test design | `skills/write-tests/SKILL.md` | persistent scenarios for complex acceptance | execution profile selection |
| Contract tests | `tests/test_workflow_*.py`, supporting contract tests | executable routing invariants | runtime orchestration |

## Data and control flow

1. User request -> Bruce bounded read-only inspection -> component and contract boundary map.
2. Unresolved evidence -> `profile: unresolved`; continue inspection without Goal, design-review,
   test-plan, change-directory, or behavior-implementation side effects.
3. Sufficient evidence -> resolve `standard` or `full` and record components, propagated contract,
   and repository evidence for `full`.
4. Independently evaluate persistence/audit need -> Goal, persisted downstream design source ->
   Design Gate, and complex acceptance -> test design.
5. Freeze the task contract before behavior implementation and re-evaluate only the affected
   capability when later repository facts change a trigger.

## Decisions

### Add a side-effect-free unresolved inspection state

- Chosen: allow `profile: unresolved` only during bounded inspection; prohibit behavior changes and
  heavyweight workflow side effects until the profile is resolved.
- Rationale: missing evidence is not positive evidence for either topology, while read-only
  inspection is sufficient to resolve the normal case.
- Rejected: default to `full`, because false positives create immediate durable artifacts and Goal
  state; default to `standard`, because false negatives may begin implementation before contract
  propagation is understood.
- Reversibility: remove the unresolved state and restore eager classification in the skill contract.

### Make full evidence structural and explicit

- Chosen: `full` requires named components, a propagated API/event/data/file contract or multiple
  independently delivered components, and concrete repository evidence. Size and duration alone do
  not determine topology.
- Rationale: the evidence can be checked before behavior implementation and avoids subjective
  phrases such as "large" or "benefits from complete delivery".
- Rejected: confidence scores, because they preserve ambiguity without defining a safe action.
- Reversibility: broaden the profile definition without changing capability triggers.

### Route capabilities by their own predicates

- Chosen: Goal execution is triggered by explicit Goal intent or a task-contract persistence/audit
  need; Design Gate by persisted downstream-governing design; test design by acceptance complexity.
  `full` is neither necessary nor sufficient for any of them.
- Rationale: each cost is justified by the fact it manages, and an error in topology classification
  no longer multiplies into three unrelated costs.
- Rejected: keep `full` as a master switch and merely delay it, because a later false positive still
  produces the same cascade.
- Reversibility: reintroduce individual profile triggers, although that would restore coupling.

## Contracts

- [`api-contracts.md`](api-contracts.md#profile-resolution-v2)

## Cross-cutting behavior

- Compatibility/versioning: intentional hard cutover of the Bruce workflow contract; no runtime
  data format or public API is migrated.
- Authentication/authorization: not applicable.
- Failure and recovery: unresolved inspection never mutates behavior or workflow state; scope
  changes return to the affected predicate before implementation continues.
- Observability: task contract records the resolved profile evidence and each independent capability
  decision; contract tests assert absence of the previous couplings.
- Rollout/rollback: update bundled skill sources and tests atomically; rollback is a targeted source
  revert with no persistent-data recovery.

## Verification impact

- Deferred profile resolution -> `tests.test_workflow_profiles` asserts `unresolved`, bounded
  inspection, and prohibited side effects.
- Evidence-backed full topology -> profile tests assert components, propagated contract, and
  repository evidence.
- Independent capability routing -> workflow, execution, and supporting-skill tests reject
  `full -> Goal/Design Gate/test-design` coupling.
- Regression safety -> full repository unit suite and plugin validator.

## Open decisions

- None.
