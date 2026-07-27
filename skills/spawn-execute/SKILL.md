---
name: spawn-execute
description: Use only under an active goal-execution mode when boundary-clear Goal work benefits from Codex-native delegation or sequential fallback. Return task evidence to the parent without creating workflow state or deciding completion.
---

# Spawn and execute

Execute a bounded slice of an active Goal without creating another runtime or verdict protocol.

## Inputs

- The active native Goal and `.goal/<goal-id>/execute_record.md` initialized by `goal-execution`.
- Objective, scope, acceptance, constraints, profile, and risk.
- The task slice, dependencies, file ownership, interfaces, and required verification.
- Current workspace facts and unrelated changes that must be preserved.

## Procedure

1. Confirm matching native Goal state and audit record exist. Otherwise return control to Bruce.
2. Delegate only boundary-clear, low-coupling work without hidden context. Keep shared-file and
   unresolved-contract work sequential.
3. Give the executor objective, allowed/excluded files, dependencies, exact interfaces, acceptance,
   verification, and prohibited side effects.
4. Keep the main agent responsible for dependency order, conflicts, scope, integration, and final
   verification.
5. Inspect actual changes and tool evidence. Classify failures with
   [failure-recovery.md](../bruce/references/failure-recovery.md) and pause only the affected boundary.
6. Return a task evidence packet containing task id, scope, result, changed files, acceptance/scenario
   ids, verification layer, commands/checks and outcomes, L0-L4 classification, repair-round evidence,
   dependent impact, and remaining work.
7. Reverify integrated changes against the parent acceptance. A delegated agent's `done` statement
   is not completion evidence.

## Output

Return task evidence to `goal-execution` for audit recording and to Bruce for integration. Do not
return a Design or Completion verdict; the owning gates make those decisions against the integrated
state.

## Does not own

Do not create or close native Goals, decide design readiness or completion, implement a scheduler,
worker registry, process monitor, model selector, permission wrapper, second ledger, or global
stop-on-first-failure policy. Do not infer Goal status from `execute_record.md`.
