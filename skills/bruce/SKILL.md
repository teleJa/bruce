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

Before creating any native Subagent, select exactly one Functional Agent Profile from
[model-profiles.yaml](references/model-profiles.yaml) and construct the v1 Task Packet defined in
[functional-agent-contracts.md](references/functional-agent-contracts.md). Resolve task override >
project override > user override > built-in Profile > current-model fallback through the shared
resolver; do not let an individual Skill create a model selector or Runtime. Pass `model` to the
Codex host only when the host has confirmed the configured model. Otherwise omit `model` to inherit
the current model and record `resolution_result=fallback`, `fallback_used=true`,
`capability_status=degraded`, and the effective model. A fallback is not model heterogeneity.
Every delegated result must include `model_resolution` and the role-specific Packet; the main Agent
and the existing Design/Completion Gates retain all terminal authority.

## Entry routing

`bruce` is the total workflow orchestrator. It owns task-contract formation, capability selection,
subagent lifecycle, implementation sequencing, verification, Design Gate, Completion Gate, and
authorized delivery boundaries. It is not the default entry for every request that mentions Bruce.

When the user's intent is explicitly analysis-only — for example, “先调研”“分析方案”“分析可行性”
or “暂不改代码并等待我确认” — route the request to `solution-analysis` as the entry Skill. Do not
start the implementation-oriented Bruce workflow and then silently continue past the analysis stop.
`solution-analysis` performs read-only inspection and feasibility analysis, then returns
`Analysis: complete` and `Awaiting user direction: yes`.

When the user asks to implement, fix, refactor, deliver, or otherwise authorizes execution, remain in
this `bruce` workflow. If the user first completed `solution-analysis` and later explicitly asks to
persist the confirmed design, re-enter Bruce with a `design-only` scope when implementation is not yet
authorized; if implementation is authorized, use the normal implementation workflow.

## 1. Inspect

Read the user request, applicable `AGENTS.md`, relevant code, and repository facts. Preserve
unrelated working-tree changes. Ask at most one blocking question only when evidence cannot resolve
an ambiguity that changes scope, acceptance, or business consequences.

Start with `profile: unresolved` when component or contract-boundary facts are incomplete. Continue
bounded read-only inspection until the profile is resolved. Inspection alone does not create a
Goal, design review, test design, or change directory. Do not begin behavior implementation while
the profile is `unresolved`.

Use direct inspection when the entry point, component boundary, and relevant conventions are already
clear. Use `inspect-parallel` when unresolved facts can be divided into at least two independent
read-only scopes and the task spans multiple components/directories, a cross-cutting concern, or
repository-wide patterns whose separate evidence must be synthesized. Repository size, expected
`full` profile, or a desire to use subagents is not sufficient by itself.

For parallel inspection, give each native subagent a bounded scope, concrete questions, and a common
evidence format. Keep every shard read-only, preserve the working tree, and require repository paths,
symbols, commands, and observed cross-boundary relationships rather than broad summaries. The main
agent owns synthesis, resolves conflicting findings against the current workspace, and makes the
profile and task-contract decisions. If native subagents are unavailable or one shard fails, inspect
only the missing scope directly; unavailable parallelism alone does not block contract formation.

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
- `tasks`: for a persisted implementation plan, handoff, or multi-step requirement, create one
  change-level `tasks/` package containing frozen task contracts. A trivial documentation-only change
  may omit it only with a recorded reason. Read [task-contract.md](references/task-contract.md).
- `batches`: required before implementation for a `full` or `critical` task that spans two or more
  independently delivered components or a propagated cross-component contract. Each batch is a closed,
  verifiable delivery boundary, not a remaining-work bucket. Record its stable `batch_id`, included
  task/acceptance ids, owned components and allowed paths, excluded work, direct call sites, dependency
  preconditions, evidence boundary, checkpoint trigger, repair budget, and stop condition. The stop
  condition states when the batch must stop opening new inspection and return its checkpoint; it must
  exclude every path and concern not mapped to a current acceptance id, known failing matrix row, or
  declared direct call site.

For user-visible Web acceptance, resolve `visual_scope` before implementation. A missing scope is
an unresolved contract field, not permission to assume `none`; record the material visible outcome
and the reason for the selected level. For a `full` or `critical` cross-component task, missing,
open-ended, or overlapping batches also leave the task contract unresolved; do not implement until
those batch boundaries are closed and assigned.

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

### Task package and checkpoint

When a change package persists an implementation plan, derive one change-level `tasks/` directory
before implementation. `tasks/index.yaml` records stable ids, dependency order, acceptance ids, and
path ownership; each `T-<id>-<slug>.md` freezes one task contract. Do not create one plan or task
package per repository, and do not silently widen a frozen task. A contract change creates a new
revision or superseding task.

The current task state belongs in the change-level `checkpoint.yaml` or the current checkpoint
message, not in the frozen task file. The checkpoint aggregates every task's status, the active task,
contract revisions, basis revision, environment, evidence references, blockers, findings, and next
action. It is progress feedback only: it is not a third decision, a Goal ledger, or a second evidence
store. Native Goal state remains authoritative for Goal lifecycle; the checkpoint is authoritative only
for change/task progress, and `.goal/<goal-id>/execute_record.md` is an audit record that may reference
it. Recovery never infers Goal state from a checkpoint, and checkpoint state never overrides either
Gate. Tasks execute sequentially by default; `depends_on` prepares future scheduling but does not
activate parallel execution.

A long-running task may span multiple checkpoints without being split or restarted. Use a progress
checkpoint at a meaningful milestone, task transition, environment/risk change, or work-interval
boundary. Resume the same `task_id` and contract revision when the task remains in scope.

## 3. Select only necessary capabilities

Continue directly when Codex can implement and verify the task without another artifact. Invoke a
supporting skill only for a present need:

- pre-design read-only inspection and feasibility analysis that must stop for user direction:
  `solution-analysis`;
- parallel read-only discovery of unresolved component, contract, or repository-pattern facts:
  `inspect-parallel`;
- connected domain decisions or durable domain documentation: `grill-with-docs`;
- architecture or public/cross-component contract design: `write-architecture`;
- schema or persistence design: `write-db-design`;
- persistent implementation planning: `write-plan`;
- a question-driven throwaway logic or UI-variant exploration: `explore-prototype`;
- an explicitly requested or implementation-governing grounded UI prototype: `write-prototype`;
- complex acceptance and regression design: `write-tests`;
- an explicitly requested standalone plan review: `plan-review`;
- readiness of persisted downstream design: `design-gate`;
- explicit Goal intent or a task-contract need for continuous/cross-turn persistence or an audit
  record: `goal-execution`;
- final completion decision for every implementation task: `completion-gate`.

A resolved profile does not itself invoke Goal, Design Gate, test design, or prototype generation.
A required persisted implementation plan does invoke `write-tests`; plan verification bullets do not
replace the resulting `test-plan.md`. Run `design-gate` only when a requirement, architecture, API
contract, table design, implementation
plan, test design, or confirmed UI prototype will govern downstream implementation. It owns artifact
completeness and document readiness and returns one implementation-entry result:
`Design: pass|blocked`.

Every public or cross-component API, event, or file-contract change uses `write-architecture` and
must generate or update `api-contracts.md` before behavior implementation.

Do not chain supporting skills merely because one was selected. In particular, Bruce does not
automatically invoke `solution-analysis`; explicit analysis-only intent is routed to that standalone
entry Skill before this workflow begins.

## 4. Implement with Codex

A `design-only` scope is a valid Bruce handoff after the user has confirmed the analysis result but
has not authorized behavior implementation. In this mode, Bruce may form the task contract, invoke
only the necessary `write-architecture`, `write-db-design`, `write-plan`, and `write-tests` skills,
and run `design-gate` when the resulting artifacts will govern downstream implementation. It must
stop after the design artifacts and Design Gate result; it must not implement behavior, invoke
`completion-gate`, or perform delivery actions. `Design: pass` in this mode means the artifacts are
ready to govern a later implementation; it is not permission to implement without a separate user
instruction.

Use the current Codex task and available tools. Use native subagents directly for incidental
delegation and only for boundary-clear, low-coupling tasks. Keep the main agent responsible for
scope, file ownership, dependency order, integration, and conflict resolution.

When a task package exists, execute one frozen task contract at a time by default. Before changing a
file, confirm it is allowed by the active task's `include`/`exclude` scope and acceptance ids. At a
task boundary, update the requirement-level checkpoint with the task status and current evidence;
do not rewrite the task contract merely to record progress. If scope, acceptance, dependency,
authorization, or verification changes, stop and create a contract revision or a superseding task
before continuing.

For `explore-prototype`, a native subagent may generate the bounded prototype only after the main
agent freezes the question, mode, exclusive allowed paths, repository facts, scenarios or variants,
run instructions, observable checks, and prohibited side effects. The main agent retains product
decisions, user feedback, actual-diff inspection, production promotion, and every Gate decision. If
native subagents are unavailable or ownership overlaps, generate sequentially; unavailable
delegation alone does not block exploration.

When Design Gate is required, do not implement affected behavior until the current same-directory
`design-review.md` reports `Design: pass` and the Design Gate validator passes against that current
change directory. A prose verdict, plan status, or file presence without validator evidence is not
implementation entry. If scope changes a design decision, rerun Design Gate before continuing
affected implementation.

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
record. An unfinished `full` task that resumes after a user-turn boundary requires continuous/cross-turn
persistence: enter or resume `goal-execution` before implementation or verification continues. Use
[handoff.md](templates/handoff.md) only when the user explicitly requests durable transfer.

For that cross-turn `full` resume, do not treat “继续” or an equivalent continuation request as permission
to reopen code discovery. First establish the native Goal and current workspace basis, then return a
`Resume checkpoint` before any new code inspection, behavior edit, or verification. It records the
current `batch_id`, basis revision or working-tree basis, latest checkpoint or its absence, known
findings and repair set, allowed paths/direct call sites, deferred concerns, next evidence action, and
stop condition. New inspection is allowed only when it maps to a current acceptance id, known failing
matrix row, or declared direct call site; otherwise record it as deferred and proceed to the checkpoint,
declared repair set, or completion path.

## 6. Decide completion and report

For a `design-only` handoff, report the generated design artifacts, Design Gate result, unresolved
risks, and the explicit implementation boundary, then stop. Do not invoke `completion-gate`, because
no behavior implementation or completion evidence is being claimed.

After implementation and targeted verification, invoke `completion-gate`. It performs all required
author checks, evidence checks, scope checks, design-to-diff checks, and any risk-triggered independent
review internally. No caller repeats those checks or combines their internal labels.

When the contract declares multiple delivery batches, when Goal execution spans a long-running or
cross-component task, or before crossing an external verification or side-effect boundary, run a
batch checkpoint after the current batch. The checkpoint reviews only that batch's bounded matrix and
returns `Checkpoint: clear|issues|blocked`; it never returns `Completion`, starts a per-finding review
chain, or makes the overall delivery decision. Once a batch has changed behavior and starts its planned
verification, map every new inspection to a current acceptance id, known failing matrix row, or declared
direct call site. Do not open an adjacent concern merely because it might be risky; classify an unmapped
concern as deferred. Complete the batch matrix and return one batch findings packet before repairing
non-blocking failures or starting further inspection after the second non-blocking finding; classify
findings as blocking, compatible, or deferred, and repair compatible findings together in one bounded
repair set. An `update_plan` progress update never substitutes for this checkpoint. Repair the resulting
batch repair set before starting dependent work. Use the final `completion-gate` once all batches are
complete.

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
