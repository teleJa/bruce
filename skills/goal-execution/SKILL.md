---
name: goal-execution
description: Use only for explicit Goal intent or when the resolved task contract requires continuous or cross-turn persistence or an auditable execution record. Maintain native Goal state and one execute_record.md without deciding design readiness or completion.
---

# Goal execution mode

Add persistence to an otherwise unchanged Bruce workflow. Native Goal is the execution-state source;
`.goal/<goal-id>/execute_record.md` is a human audit record.

Goal execution is a mode, not a gate. It accepts Design and Completion results from their owners and
does not re-check their internal criteria.

## Entry

Enter only for explicit Goal intent or when the resolved task contract requires continuous/cross-turn
persistence or an auditable execution record. An unfinished `full` task that resumes after a user-turn
boundary is such a continuous/cross-turn persistence need. Profile, complexity, duration, risk, or
subagent use alone does not enable this mode.

Before creating or resuming a Goal, use `get_goal` and prepare:

- objective, allowed/excluded scope, and constraints;
- verifiable acceptance criteria and evidence paths;
- profile and business risk;
- `Design: pass` when Design Gate is required.

For an unfinished `full` task that resumes after a user-turn boundary, establish the Goal and current
workspace basis, then return a `Resume checkpoint` before new code inspection, behavior edits, or
verification. Record the current batch, basis revision or working-tree basis, latest checkpoint or its
absence, known findings/repair set, allowed paths/direct call sites, deferred concerns, next evidence,
and stop condition. A continuation request does not reset interval counters and does not authorize
unmapped inspection.

Do not start Goal-backed implementation while a required Design result is absent or blocked. Do not
silently replace a conflicting unfinished Goal. Pass a token budget only when the user explicitly
specified one.

## Audit record

After Goal creation or resumption, create or reuse `.goal/<goal-id>/execute_record.md`. If no usable
Goal id is returned, use a stable timestamp slug and record the native objective. Keep one record with:

- objective, acceptance, scope, and constraints;
- current plan and material decisions;
- Design result when applicable;
- capability preflight results and dependent acceptance ids;
- latest batch checkpoint, work-interval counters, and any material live tool handle;
- executed verification and current outcomes;
- Completion result and evidence summary when available;
- blocking facts and exact unlock condition;
- final conclusion.

Update it at creation, material decisions, verification, confirmed blocking, and closure. Do not
mirror every Goal transition or infer native status from the Markdown file.

## Execute and synchronize

Maintain the nearest executable plan with native planning tools. Use `spawn-execute` only for
boundary-clear delegated work under the active Goal. Ordinary implementation and verification remain
owned by Bruce and the selected capabilities.

At each work-interval boundary, update the existing audit record and run the batch checkpoint before
starting another interval. This rollover is execution persistence, not a Completion result, and it
does not reset L0/L1 retry or repair counts.

Continue until `completion-gate` returns one of its terminal results:

- `Completion: pass`: record the result, then mark the native Goal complete.
- `Completion: issues`: keep the Goal active and return the findings for repair.
- `Completion: blocked`: record the blocker and keep the Goal active until the native blocked-status
  threshold is satisfied; only then mark it blocked.

Do not independently inspect artifacts, author checks, review labels, or acceptance mappings to
override the Completion result. If implementation changes invalidate Design readiness,
`completion-gate` returns an issue and Bruce reruns `design-gate` before affected work continues.

## Output

Return native Goal status, the audit-record path, the latest Design and Completion results, material
evidence references, remaining work, and any blocking condition.

## Does not own

Do not decide design readiness or completion, widen user authority, commit, push, publish, deploy,
mutate infrastructure, implement a scheduler or alternate state machine, or create a second ledger.
