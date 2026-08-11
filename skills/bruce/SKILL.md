---
name: bruce
description: Use when the user asks Bruce to implement, fix, refactor, or deliver a software change with proportional planning, one design-readiness decision before implementation when needed, one evidence-backed completion decision, optional native Goal persistence, and bounded L0-L4 failure handling.
---

# Bruce workflow

Run one proportional workflow through the current Codex task:

```text
inspect -> task contract -> design when needed -> Design Gate when needed -> implement -> [batch checkpoint when triggered] -> Completion Gate -> summary
                                      \-> optional Goal execution mode -/
```

Bruce has two decisions and one optional execution mode:

- `design-gate` is the only implementation-entry decision for persisted downstream design.
- `completion-gate` is the only completion decision.
- A batch checkpoint is progress feedback, not a third decision or an overall completion result.
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
- `visual_scope`: `none`, `chrome-smoke`, or `chrome-layout`, selected from the material visible
  outcome and layout/interaction risk. Any user-visible Web acceptance must use the Codex App
  Chrome capability; Playwright is prohibited as an acceptance runner or fallback. A frontend
  path alone does not force Chrome, but a visible Web outcome always requires one real Chrome
  interaction and visual-evidence pass before completion.
- `tasks`: only when dependent work benefits from an explicit plan.
- `batches`: only for multi-batch work; each batch has a stable id, included task/acceptance ids,
  an evidence boundary, and its checkpoint trigger.

For user-visible Web acceptance, resolve `visual_scope` before implementation. A missing scope is
an unresolved contract field, not permission to assume `none`; record the material visible outcome
and the reason for the selected level.

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

Never infer `guarded` or `critical` from `full`, multiple components, duration, uncertainty, or
subagent use. Record the concrete risk-policy trigger; when no trigger remains, use `low` even when
the delivery profile is `full`.

Read [verification-loop.md](references/verification-loop.md) before changing behavior. Do not begin
an implementation while a material `Then` has no feasible evidence path unless the user explicitly
accepts an exploratory or unverified boundary.

For any persisted design, plan, test, handoff, or review document, read
[document-language.md](references/document-language.md) and apply its language rule. The user's
language controls natural-language prose; stable machine-facing contract tokens remain unchanged.

## 3. Select only necessary capabilities

Continue directly when Codex can implement and verify the task without another artifact. Invoke a
supporting skill only for a present need:

- connected domain decisions or durable domain documentation: `grill-with-docs`;
- architecture or public/cross-component contract design: `write-architecture`;
- schema or persistence design: `write-db-design`;
- persistent implementation planning: `write-plan`;
- an explicitly requested or implementation-governing grounded UI prototype: `write-prototype`;
- complex acceptance and regression design: `write-tests`;
- an explicitly requested standalone plan review: `plan-review`;
- readiness of persisted downstream design: `design-gate`;
- explicit Goal intent or a task-contract need for continuous/cross-turn persistence or an audit
  record: `goal-execution`;
- final completion decision for every implementation task: `completion-gate`.

A resolved profile does not itself invoke Goal, Design Gate, test design, or prototype generation.
Run `design-gate` only when a requirement, architecture, API contract, table design, implementation
plan, test design, or confirmed UI prototype will govern downstream implementation. It owns artifact
completeness and document readiness and returns one implementation-entry result:
`Design: pass|blocked`.

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

When a confirmed prototype governs UI implementation, use it for visible scope, state, and
interaction intent while implementing with the target repository's real components and theme tokens.
Do not copy prototype source into production merely because the generated artifact renders.

## 5. Classify failures and recover

Read [failure-recovery.md](references/failure-recovery.md) whenever a command, tool, validation, or
subagent fails. Apply L0-L4 to the smallest affected boundary. Retry only within the documented
budget, repair only after a real change, and never replay an unknown external side effect.

Resume non-Goal work from the conversation, current plan, tool results, and actual workspace. Resume
Goal-backed work from native Goal plus those current facts; never derive Goal status from its audit
record. Use [handoff.md](templates/handoff.md) only when the user explicitly requests durable transfer.

## 6. Decide completion and report

After implementation and targeted verification, invoke `completion-gate`. It performs all required
author checks, evidence checks, scope checks, design-to-diff checks, and any risk-triggered independent
review internally. No caller repeats those checks or combines their internal labels.

When the contract declares multiple delivery batches, when Goal execution spans a long-running or
cross-component task, or before crossing an external verification or side-effect boundary, run a
batch checkpoint after the current batch. The checkpoint reviews only that batch's bounded matrix and
returns `Checkpoint: clear|issues|blocked`; it never returns `Completion`, starts a per-finding review
chain, or makes the overall delivery decision. Repair batch findings before starting dependent work.
Use the final `completion-gate` once all batches are complete.

When a batch has `visual_scope=chrome-smoke|chrome-layout`, include its bounded Chrome evidence in
that batch checkpoint. The evidence must include a real action against the target, the resulting
visible state, and a screenshot or equivalent Chrome visual artifact; `chrome-layout` additionally
requires geometry/overflow checks. Do not trigger a visual checkpoint for `visual_scope=none`;
re-evaluate the scope only when the acceptance or changed surface reveals a material visible
outcome. Playwright output is never valid evidence for these rows.

The gate must return one complete findings packet for the current final state. When findings are
repairable, batch compatible repairs before rerunning verification. A later change invalidates only
the affected checks; rerun stale rows, the unchanged original failure, and related regressions. Reuse
a checkpoint row only when its evidence revision matches the current review basis and its affected
scope is unchanged.
Do not start a fresh review for each finding or repeat unaffected checks unless the review basis or
risk trigger materially changes.

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
