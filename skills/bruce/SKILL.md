---
name: bruce
description: Use when the user asks Bruce to implement, fix, refactor, or deliver a software change with proportional planning, one design-readiness decision before implementation when needed, one evidence-backed completion decision, optional native Goal persistence, and bounded L0-L4 failure handling.
---

# Bruce workflow

Run one proportional workflow through the current Codex task:

```text
inspect -> task contract -> design when needed -> Design Gate when needed -> implement -> Completion Gate -> summary
                                      \-> optional Goal execution mode -/
```

Bruce has two decisions and one optional execution mode:

- `design-gate` is the only implementation-entry decision for persisted downstream design.
- `verify-completion` is the only completion decision.
- `goal-execution` adds persistence and an audit record; it never decides design readiness or
  completion.

Keep Bruce as workflow guidance. Let Codex own commands, files, tools, permissions, task context,
native Goal state, and subagent lifecycle. Read
[plugin-boundary.md](references/plugin-boundary.md) before handling a permission denial, external
side effect, or request to add execution infrastructure.

## 1. Inspect

Read the user request, applicable `AGENTS.md`, relevant code, and repository facts. Preserve
unrelated working-tree changes. Ask at most one blocking question only when evidence cannot resolve
an ambiguity that changes scope, acceptance, or business consequences.

Start with `profile: unresolved` when component or contract-boundary facts are incomplete. Continue
bounded read-only inspection until the profile is resolved. Inspection alone does not create a
Goal, design review, test design, or change directory. Do not begin behavior implementation while
the profile is `unresolved`.

## 2. Form the task contract

Keep the contract in the current task unless the user requests a persistent plan or handoff. Include:

- `objective`: the result to achieve.
- `scope`: allowed and excluded changes.
- `acceptance`: observable completion conditions. For behavior changes, give each scenario a stable
  id with concrete `Given`, `When`, `Then`, and `Evidence`.
- `constraints`: repository rules, user constraints, and known risks.
- `profile`: `unresolved` during inspection, then `standard` or `full` before implementation.
- `risk`: `low`, `guarded`, or `critical`, with its trigger.
- `tasks`: only when dependent work benefits from an explicit plan.

Resolve `standard` after inspection proves one delivery component without cross-component API,
event, data, or file-contract propagation. Resolve `full` only when inspection proves multiple
independently delivered components or cross-component contract propagation. For `full`, record
`named components`, the `propagated contract` or independent delivery boundary, and concrete
repository `evidence` in the task contract. Size, duration, risk, and uncertainty are insufficient
to make a task `full`.

Treat execution profile and risk as independent dimensions: a local schema change can be
`standard + guarded`, while multi-component documentation can be `full + low`. Read
[risk-policy.md](references/risk-policy.md) before guarded or critical actions. When later facts
disprove a route, re-evaluate only the affected capability predicates before continuing affected
behavior implementation. Do not ask for approval unless scope, acceptance, authority, or business
consequences also change.

Read [verification-loop.md](references/verification-loop.md) before changing behavior. Do not begin
an implementation while a material `Then` has no feasible evidence path unless the user explicitly
accepts an exploratory or unverified boundary.

## 3. Select only necessary capabilities

Continue directly when Codex can implement and verify the task without another artifact. Invoke a
supporting skill only for a present need:

- connected domain decisions or durable domain documentation: `grill-with-docs`;
- architecture or public/cross-component contract design: `write-architecture`;
- schema or persistence design: `write-db-design`;
- persistent implementation planning: `write-plan`;
- complex acceptance and regression design: `write-tests`;
- an explicitly requested standalone plan review: `plan-review`;
- readiness of persisted downstream design: `design-gate`;
- explicit Goal intent or a task-contract need for continuous/cross-turn persistence or an audit
  record: `goal-execution`;
- final completion decision for every implementation task: `verify-completion`.

A resolved profile does not itself invoke Goal, Design Gate, or test design. Run `design-gate` only
when a requirement, architecture, API contract, table design, implementation plan, or test design
will govern downstream implementation. It owns artifact completeness and document readiness and
returns one implementation-entry result: `Design: pass|blocked`.

Every public or cross-component API, event, or file-contract change uses `write-architecture` and
must generate or update `api-contracts.md` before behavior implementation.

Do not chain supporting skills merely because one was selected.

## 4. Implement with Codex

Use the current Codex task and available tools. Use native subagents directly for incidental
delegation and only for boundary-clear, low-coupling tasks. Keep the main agent responsible for
scope, file ownership, dependency order, integration, and conflict resolution.

When Design Gate is required, do not implement affected behavior until the current same-directory
`design-review.md` reports `Design: pass`. If scope changes a design decision, rerun Design Gate
before continuing affected implementation.

Enter `goal-execution` only for explicit Goal intent or a resolved task-contract need for
continuous/cross-turn persistence or an audit record. `spawn-execute` is an optional delegation
helper under an active Goal, not a scheduler or completion authority.

For behavior changes, start with the smallest failing test or reproducible scenario when feasible.
Reproduce bugs before fixing them and establish a characterization baseline before refactoring.
Documentation-only, generated, and mechanical changes do not require ceremonial TDD.

## 5. Classify failures and recover

Read [failure-recovery.md](references/failure-recovery.md) whenever a command, tool, validation, or
subagent fails. Apply L0-L4 to the smallest affected boundary. Retry only within the documented
budget, repair only after a real change, and never replay an unknown external side effect.

Resume non-Goal work from the conversation, current plan, tool results, and actual workspace. Resume
Goal-backed work from native Goal plus those current facts; never derive Goal status from its audit
record. Use [handoff.md](templates/handoff.md) only when the user explicitly requests durable transfer.

## 6. Decide completion and report

After implementation and targeted verification, invoke `verify-completion`. It performs all required
author checks, evidence checks, scope checks, design-to-diff checks, and any risk-triggered independent
review internally. No caller repeats those checks or combines their internal labels.

Completion is allowed only when it returns `Completion: pass`. Repairable findings return `issues`;
missing authority, unsafe external state, or unresolved L2-L4 conditions return `blocked`.

For Goal-backed work, pass the single completion result and evidence summary to `goal-execution`.
Goal execution records the result and synchronizes native Goal status without re-evaluating it.

Report changed files, acceptance evidence, the Design Gate result when applicable, the Completion
Gate result, residual risks, and authorized delivery actions that were intentionally not performed.

## Does not own

Do not implement a sandbox, permission layer, host adapter, scheduler, lease, heartbeat, worktree
manager, second evidence store, or transcript mirror. Do not wrap Codex execution behind a Bruce
CLI, MCP server, or app.
