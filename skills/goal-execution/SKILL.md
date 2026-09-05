---
name: goal-execution
description: Use only when the user explicitly requests native Goal creation or continuation, including /goal or this Skill. Adapt host Goal state to existing Bruce evidence; ordinary execution and recovery do not need Goal, and audit records are opt-in.
---

# Native Goal adapter

Goal execution is a mode, not a gate, and is not a prerequisite for Bruce delivery. This compatibility
adapter connects an explicitly requested host capability to existing Bruce evidence. Native Goal owns
only its lifecycle; Bruce owns task progress, bounded execution, and acceptance. The adapter accepts
Design and Completion results from their owners and does not re-check their internal criteria.

## Entry

Enter only when the user explicitly requests native Goal creation or continuation, including `/goal`
or an explicit invocation of this Skill. A discussion, evaluation, or removal of Goal is not a request
to run it. Profile, complexity, duration, risk, subagent use, cross-turn recovery, and audit needs
do not enable this adapter. Requests such as `continue nonstop`, `继续开发`, and `持续推进直到完成`
authorize ordinary scoped continuation, not implicit Goal creation.

For an explicit Goal request, use `get_goal` before creating or continuing it. Match the native
objective and scope to the authorized task, its acceptance, constraints, and current workspace.
Do not silently replace a conflicting unfinished Goal.
Pass a token budget only when the user explicitly specified one.
Honor host pause, cancellation, permissions, and budget limits; a continuation instruction does not
bypass host-controlled state. If Goal tools are unavailable, report the explicit capability request
as unavailable; do not claim it ran or silently replace it with a local loop. Independent ordinary
work may continue only within its existing authorization and stop conditions.

Do not start Goal-backed implementation while a required Design result is absent or blocked.
Use the ordinary Bruce resume procedure in [failure-recovery.md](../bruce/references/failure-recovery.md).
The adapter does not add a second resume checkpoint or repeat inspection and verification.

## Reuse progress and evidence

Use the existing task contract, checkpoint, and verification evidence. Reference the Design result when applicable
and the Completion result and evidence summary; do not duplicate their checks. Profile confirmation,
capability preflight, event-driven checkpoints, and material live handles remain part of ordinary Bruce
execution. Continuing native Goal does not reset L0/L1 retry or repair counts.

Do not create or maintain `execute_record.md` by default. Only when the user explicitly requests a durable audit record,
reuse an existing suitable record or the requested path. A legacy `.goal/<goal-id>/execute_record.md`
may be reused as a human-readable reference to current evidence; it is not required for native Goal
or ordinary recovery. Do not mirror transcripts, checkpoints, or every Goal transition. An audit record
never overrides native Goal state or either Gate result. Preserve historical records without silently
rewriting or deleting them.

## Synchronize owned results

Ordinary implementation, recovery, delegation, and verification remain owned by Bruce and its selected
capabilities. Synchronize only a matching, explicitly requested native Goal, using the owning Gate's
current result and the host's lifecycle rules:

- `Completion: pass`: mark the Goal complete only if its entire objective and acceptance are achieved
  and no required work remains. A passing subtask does not complete a broader Goal.
- `Completion: issues`: preserve findings and use the ordinary bounded repair path; do not mark complete
  or extend exhausted repair budgets to keep Goal running.
- `Completion: blocked`: report the exact blocker; mark native status blocked only after the host's
  blocked-status threshold is satisfied, never merely because a tool or one batch failed.

For an explicitly design-only Goal, consume the Design Gate result and the confirmed design-only
acceptance; do not start implementation or invoke Completion Gate to close that Goal.
Do not independently inspect artifacts, author checks, review labels, or acceptance mappings to
override the owning Gate's result. Native status synchronization creates no additional verdict.

## Output

Return the observed native Goal status, existing evidence references, the owning Gate result when
available, remaining work, and any blocker. Include an audit path only when one was explicitly requested.

## Does not own

Do not create a scheduler, custom runtime, mandatory audit ledger, second evidence store, or background
execution promise. Do not infer native Goal state from local Markdown or use Goal to bypass user pauses,
permissions, scope, risk, verification, or host limits. This adapter does not authorize commit, push,
publish, deployment, infrastructure mutation, or any other delivery side effect.
