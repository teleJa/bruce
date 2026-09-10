---
name: spawn-execute
description: Use when an authorized implementation task has boundary-clear work that benefits from Codex-native delegation or sequential fallback. Return task evidence to Bruce without requiring Goal, creating workflow state, or deciding completion.
---

# Spawn and execute

Execute a bounded slice of an authorized implementation task without creating another runtime or
verdict protocol. Neither a native Goal nor `execute_record.md` is a prerequisite.

## Inputs

- The current authorized task contract and existing checkpoint when applicable.
- Objective, scope, acceptance, constraints, profile, and risk.
- The task slice, dependencies, file ownership, interfaces, and required verification.
- The execution handoff when a design model/profile differs from the executor or durable handoff is required.
- Current workspace facts and unrelated changes that must be preserved.
- A compact evidence handoff for every implementation slice, including same-model and sequential work,
  following [implementation-preparation.md](../bruce/references/implementation-preparation.md).

## Procedure

1. Confirm the parent authorized implementation and froze the task slice, acceptance, allowed paths,
   dependencies, and stop condition. If an execution handoff exists, consume it as the bounded
   implementation contract: accept frozen decisions, verify only `executor_must_verify` items, and
   honor its investigation budget and stop conditions. When additional investigation is needed, reconcile
   consumed/remaining focused evidence rounds before dispatch, including parent consumption and whether
   the single extension was used; absent values are unknown, not a fresh allowance. If no investigation
   gaps remain and safety prerequisites are confirmed, keep missing consumption unknown and proceed
   directly to editing or verification with no additional investigation or extension allowance.
   Budget bookkeeping must not block a ready safe slice or skip current-source safety checks.
   Calls/reads are additional ceilings, never convertible to extra rounds. Do not ask the executor to reread the full design
   package to rediscover scope. If those inputs are incomplete, return control to Bruce without
   creating a Goal or audit record. If delegation is unavailable or unsafe, use sequential execution
   within the same scope.
2. Delegate only boundary-clear, low-coupling work without hidden context. Keep shared-file and
   unresolved-contract work sequential. Dispatch the first ready slice without waiting for unrelated
   scopes to finish inspection. Do not duplicate an active worker's investigation on the main thread;
   do integration, the next independent slice, or a bounded check that does not overlap its assignment.
3. Give the executor objective, allowed/excluded files, dependencies, exact interfaces, acceptance,
   verification, investigation budget, stop conditions, and prohibited side effects. If a frozen decision
   conflicts with current evidence, require a bounded conflict report instead of silent redesign.
   A path list or `fork_context=true` alone is not an evidence handoff. Include the verified facts,
   their source basis, executor-only gaps, and the first edit/test target in the existing Packet
   fields. The worker must consume those facts rather than restart Bruce, memory discovery, or a full
   design read. Recheck current instructions, workspace identity, dirty worktree, and exact source before editing;
   for stale or inaccessible evidence, reopen only affected facts and their direct dependencies.
   Changed task constraints or current-source mismatches take precedence over the handoff.
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

Return task evidence to Bruce for integration and its existing checkpoint when applicable. Do not
return a Design or Completion verdict; the owning gates make those decisions against the integrated
state.

## Functional Agent routing

This Skill consumes the `implementer` Profile and the shared [delegation contract](../bruce/references/delegation-contract.md).
Each bounded task must carry a v1 Task Packet with `task_kind=implement`, `output=task_evidence_packet`,
exact `allowed_paths`, excluded paths, verification commands, and a stop condition. Resolve the
`implementer` Profile and complete the shared pre-dispatch routing gate before calling `spawn_agent`;
do not dispatch when resolution, host arguments, packet, or write scope disagree. The implementer may
write only within `allowed_paths`; it returns changed files, commands, evidence gaps, and
`model_resolution`, never a Gate verdict. `explore-prototype` generation workers reuse this Profile
with `task_kind=throwaway_prototype` and must use their declared role-specific scope.

## Does not own

Do not create or close native Goals, decide design readiness or completion, implement a scheduler,
worker registry, process monitor, model selector, permission wrapper, second ledger, or global
stop-on-first-failure policy. Do not create a Goal-specific ledger or require Goal tools for delegation.
