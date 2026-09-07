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

## Procedure

1. Confirm the parent authorized implementation and froze the task slice, acceptance, allowed paths,
   dependencies, and stop condition. If an execution handoff exists, consume it as the bounded
   implementation contract: accept frozen decisions, verify only `executor_must_verify` items, and
   honor its investigation budget and stop conditions. Do not ask the executor to reread the full design
   package to rediscover scope. If those inputs are incomplete, return control to Bruce without
   creating a Goal or audit record. If delegation is unavailable or unsafe, use sequential execution
   within the same scope.
2. Delegate only boundary-clear, low-coupling work without hidden context. Keep shared-file and
   unresolved-contract work sequential.
3. Give the executor objective, allowed/excluded files, dependencies, exact interfaces, acceptance,
   verification, investigation budget, stop conditions, and prohibited side effects. If a frozen decision
   conflicts with current evidence, require a bounded conflict report instead of silent redesign.
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

This Skill is the `implementer` Profile consumer. Each bounded task must carry a v1 Task Packet with `task_kind=implement`, `output=task_evidence_packet`, exact `allowed_paths`, excluded paths, verification commands, and a stop condition. The implementer may write only within `allowed_paths`; it returns changed files, commands, evidence gaps, and `model_resolution`, never a Gate verdict. `explore-prototype` generation workers reuse this Profile with `task_kind=throwaway_prototype`.

## Does not own

Do not create or close native Goals, decide design readiness or completion, implement a scheduler,
worker registry, process monitor, model selector, permission wrapper, second ledger, or global
stop-on-first-failure policy. Do not create a Goal-specific ledger or require Goal tools for delegation.
