---
name: spawn-execute
description: Use as the downstream execution capability of goal-execution-gate when an active native Goal needs auditable execution of boundary-clear work through Codex-native subagents or sequential fallback. Require the Goal audit file, return structured evidence for it, and do not use for incidental delegation in an ordinary Bruce task.
---

# Spawn and execute

Execute an active Goal with bounded Codex-native delegation and one human-auditable record, without
creating another runtime.

## Inputs

- The active native Goal and `.goal/<goal-id>/execute_record.md` initialized by
  `goal-execution-gate`.
- Objective, scope, acceptance, constraints, execution profile, and risk.
- The selected task or task slice, its dependencies, file ownership, consumed/produced interfaces,
  and verification.
- Current workspace facts and unrelated changes that must be preserved.

## Procedure

1. Confirm that `goal-execution-gate` has created or resumed the matching native Goal and initialized
   its audit record. If either is absent, return control to Bruce; do not create a private Goal,
   ledger, or status file.
2. Confirm that each delegated task is boundary-clear, low-coupling, and executable without hidden
   context. Keep shared-file or unresolved-contract work sequential.
3. Build a brief containing objective, allowed/excluded files, dependencies, exact interfaces,
   acceptance, verification, and prohibited side effects.
4. Use a native subagent only when the current Codex surface exposes one. Otherwise execute the same
   task sequentially in the main agent.
5. Keep the main agent responsible for dependency order, file conflicts, scope, integration, and
   final verification. Do not let a delegated agent broaden scope or perform an unauthorized
   delivery action.
6. On each result, inspect actual changes and tool evidence. Classify failures using
   [failure-recovery.md](../bruce/references/failure-recovery.md); pause only the affected dependency
   boundary unless an L4 incident boundary applies.
7. Return an audit evidence packet containing `task_id`, scope, result, changed files, verification
   commands/checks and outcomes, L0-L4 classification, dependent impact, and remaining work. For
   behavior work, include acceptance/scenario ids, Given/When/Then, required verification layer,
   current evidence, C0 verdict, repair-round number, original-scenario rerun, and related regression
   result. The packet also includes D0/D1 document-review mode and verdict whenever the task changed
   documents.
   The parent `goal-execution-gate` writes material decisions, verification, blocking evidence, and
   the final conclusion to the existing `execute_record.md`.
8. Reverify integrated changes against the parent Goal's acceptance. A subagent's statement that it
   finished is not completion evidence.

## Output

Return the audit evidence packet to `goal-execution-gate`. Do not report the parent Goal complete;
the gate applies its completion rules, updates `execute_record.md`, and changes native Goal status.

## Does not own

Do not own native Goal creation, completion, or blocked status. Do not implement a scheduler, worker
registry, process monitor, model selector, isolation layer, permission wrapper, second persistent
ledger, or global stop-on-first-failure policy. Do not treat `execute_record.md` as runtime state or
use it to infer Goal status.
