---
name: bruce
description: Use when the user asks Bruce to implement, fix, refactor, or deliver a software change with proportional planning and evidence-backed verification. Route standard work through the current Codex task and full delivery through the bundled native Goal gate, with independent low/guarded/critical business risk and bounded L0-L4 failure handling.
---

# Bruce workflow

Run one risk-driven workflow through the current Codex task, adding native Goal persistence only for
the routes defined below:

```text
inspect -> task contract -> design when needed -> artifact gate when required -> implement -> verify -> summary
```

Keep Bruce as workflow guidance. Let Codex own commands, files, tools, permissions, task context,
and subagent lifecycle. Read [plugin-boundary.md](references/plugin-boundary.md) before handling a
permission denial, external side effect, or request to add execution infrastructure.

## 1. Inspect

Read the user request, applicable `AGENTS.md`, relevant code and repository facts. Preserve unrelated
working-tree changes. Ask at most one blocking question only when repository evidence cannot resolve
an ambiguity that changes scope, acceptance, or business consequences.

## 2. Form the task contract

Keep the contract in the current task unless the user requests a persistent plan or handoff. Include:

- `objective`: the result to achieve.
- `scope`: allowed and excluded changes.
- `acceptance`: observable completion conditions. For behavior-bearing work, give each scenario a
  stable id with `Given`, `When`, `Then`, and an exact `Evidence` path for every material outcome.
- `constraints`: repository rules, user constraints, and known risks.
- `profile`: `standard` or `full`, with one-sentence evidence.
- `risk`: `low`, `guarded`, or `critical`, with its trigger.
- `tasks`: only when multiple dependent steps benefit from an explicit plan.

Treat execution profile and risk as independent dimensions:

- `standard`: one component with no cross-component API, event, data, or file-contract propagation;
  deliver inside the current Codex task and add a lightweight plan only when useful. A standard task
  does not create a Goal by default.
- `full`: a large, multi-deliverable change, multiple components, or a cross-component contract
  change that benefits from complete, persistent, auditable execution. Record component and contract
  dependencies, complete design selection and artifact review, then enter `goal-execution-gate`
  before implementation.

A single-component schema change can be `standard + guarded`; a multi-component local documentation
change can be `full + low`. Correct the profile when repository facts disprove the initial route.
Do not ask for approval unless that correction also expands scope, changes acceptance, or adds
business consequences. Read [risk-policy.md](references/risk-policy.md) before any guarded or
critical business action.

Read [verification-loop.md](references/verification-loop.md) before changing code or runtime
behavior. Do not begin a behavior implementation while a material `Then` has no feasible evidence
path, unless the user explicitly accepts an exploratory/unverified boundary.

## 3. Select only necessary capabilities

Continue directly when Codex can implement and verify the task without another artifact. Invoke a
supporting skill only for a present need:

- multiple dependent domain decisions, durable domain documentation, or an explicit grilling
  request: `grill-with-docs`; ask one blocking question directly for an isolated ambiguity;
- architecture design: `write-architecture`, and `write-db-design` when schema design is actually
  needed; every public or cross-component API, event, or file-contract change must invoke
  `write-architecture` and generate or update `api-contracts.md` before behavior implementation
  begins;
- persistent multi-step or handoff plan: `write-plan`;
- complex acceptance matrix: `write-tests`; apply the full test-design decision below before
  behavior implementation;
- important requirement, architecture, public-contract, implementation-plan, or test-design
  readiness; multi-document consistency; or an explicit document review: `doc-review-gate`;
- meaningful plan risk: `plan-review`;
- design-artifact completeness before implementation: `artifact-review-gate`;
- a `full` profile by default, or a `standard` task with an explicit request for Goal, continuous/cross-turn
  execution, or an audit record: `goal-execution-gate`; once its native Goal and
  `execute_record.md` exist, use `spawn-execute` only for boundary-clear delegation;
- guarded/critical or user-requested completion review: `verify-completion`.

### Full test-design decision

For a `full` task, invoke `write-tests` before behavior implementation when any of these conditions
is present:

- acceptance crosses two or more component or contract boundaries;
- scenarios require state, repeat use, retry, concurrency, partial failure, recovery, permission, or rollback;
- acceptance requires real integration, deployment, or runtime-environment evidence, or more than one verification layer;
- multiple implementation tasks map to shared behavior scenarios or a known regression source.

When triggered, persist `test-plan.md` through `write-tests`; an inline acceptance table in the task
contract or Goal audit record is not a substitute. When a `full` task meets none of these conditions,
do not invoke `write-tests` solely because of the profile, but record
`write-tests: skipped — <repository-backed reason>` in the task contract and record the decision in
the same-directory `artifact-review.md`. Do not leave the durable decision implicit or place it in
`execute_record.md`.

### Design artifact gate

For every `full` task, invoke `artifact-review-gate` before entering Goal execution. Also invoke it
for a `standard` task when a requirement, architecture, API contract, table design, implementation
plan, or test design is persisted as a downstream source of truth.

The gate must write `artifact-review.md` in the same change directory as the design documents and
enumerate requirement/clarification, architecture, API contracts, table design, implementation
plan, and test design as `required/generated/skipped` decisions with repository-backed evidence.
Do not begin behavior implementation until the current file exists and reports
`Artifact gate: pass`. A task contract, chat response, D1 summary, or Goal audit record is not a
substitute. If scope changes a decision, rerun the gate and update the same file.

Do not turn a supporting skill's Markdown output into global workflow state. Do not call the rest of
the skill chain merely because one capability was selected.

## 4. Implement with Codex

Use the tools available in the current Codex surface. For `standard`, prefer the main agent and a
lightweight plan when useful. By default, every `full` task enters `goal-execution-gate` only after
the design artifact gate passes; the Goal gate creates or resumes native Goal state and the audit
record, after which Bruce executes the recorded dependencies sequentially or delegates only
boundary-clear, low-coupling tasks.
Honor an explicit user instruction to skip Goal for a `full` task, but report that persistent
recovery and the audit record are unavailable; do not silently downgrade the profile.

For behavior changes, use the development feedback in `verification-loop.md`: begin with a failing
test or reproducible scenario when feasible, reproduce bugs before fixing them, and establish a
characterization baseline before refactoring. Record why when test-first work is genuinely
impractical; do not turn documentation or mechanical changes into ceremonial TDD.

Do not begin implementing a public or cross-component API, event, or file-contract change until the
required `api-contracts.md` exists at the location resolved by `write-architecture` and covers the
provider, consumers, changed shape or semantics, compatibility, authentication, errors, and
verification. An existing OpenAPI, Proto, schema, or README can remain an authoritative source, but
it does not replace this change-scoped contract artifact.

Use native subagents directly for incidental delegation in `standard`. A `standard` task enters Goal
only when the user explicitly requests Goal mode, continuous/cross-turn execution, or an auditable
record. For every Goal-backed route, invoke the bundled `goal-execution-gate` first. It owns native
Goal lifecycle and `.goal/<goal-id>/execute_record.md`; `spawn-execute` runs only as its downstream
execution capability.

Keep the main agent responsible for scope, file ownership, dependency ordering, result integration,
and conflict resolution. If native subagents or plan tools are unavailable, continue sequentially;
do not build a scheduler, worker registry, or alternate runtime.

## 5. Classify failures and recover

Read [failure-recovery.md](references/failure-recovery.md) whenever a command, tool, validation, or
subagent fails. Apply L0-L4 to the affected dependency boundary. Retry only within the documented
budget, repair only after a real change, and never replay an unknown external side effect.

Resume `standard` from the conversation, current plan, tool results, and actual workspace. Resume
Goal-backed work from native Goal plus those current facts; never derive Goal status from its audit
record. Use
[handoff.md](templates/handoff.md) only when the user explicitly requests cross-task handoff or
durable transfer. A handoff is a snapshot, not runtime truth.

## 6. Verify and report

Verify each acceptance condition with current evidence. Inspect the actual diff and run the relevant
tests, lint, build, page checks, or other risk-proportional validation. Do not infer completion from a
file named `done`, an agent claim, or an old review.

If code changed, perform the separated C0 code self-review from `verification-loop.md` and report
`Code review: self-review`, `Verdict: pass|issues`, checks, and findings. Repair issues and rerun C0;
any later code change invalidates the previous verdict.

Verify each behavior acceptance through its `Given/When/Then/Evidence` scenario and use the required
unit/component, integration/API/database, and real-use layer. For user-visible Web behavior, use the
Codex App Chrome capability with the user's current session and real service. If Chrome is
unavailable, report the E2E gap and do not claim the scenario passed. Never silently substitute
Playwright; use it only for an established repository SOP or an explicit user request.

On a failed check, apply L0-L4 before acting. Only L1 enters the repair loop: make an actual
correction, rerun C0 after code changes, rerun the original failed scenario unchanged, and then run
its related regression set. L0 allows only bounded idempotent retries; L2 replans; L3 waits for the
required decision; L4 freezes its incident boundary and never replays unknown external side effects.
Update current evidence after each action; do not replace a failure with a smaller passing check.

If any documentation changed, perform a separated D0 document self-review before reporting:

1. Inspect the actual document diff and verify important factual claims against code, configuration,
   schema, or authoritative upstream documents.
2. Check terminology, fields, states, interfaces, and cross-document references for consistency.
3. Check acceptance coverage, material omissions, unresolved placeholders, and broken links.
4. Return `Document review: self-review`, `Verdict: pass|issues`, the checks performed, and concrete
   findings. Repair in-scope issues, then rerun D0; do not report completion while issues remain.

After D0, run D1 with `doc-review-gate` when the changed document is a requirement, architecture,
public contract, implementation plan, or test design; when multiple related documents changed; when
the document becomes a downstream source of truth; or when the user requests review. Use
`plan-review` instead when the only D1 target is an implementation plan whose meaningful execution
risk needs the deeper plan-specific check. Do not run both mechanically. D1 returns
`通过|有条件通过|不通过`; only `通过`, or an explicitly authorized and recorded `有条件通过`, satisfies
completion. When `plan-review` is the D1 substitute, `Clean` is equivalent to `通过` and
`Issues Found` is equivalent to `不通过`. A reviewer does not edit the document; Bruce may repair
issues already inside the authorized scope and must rerun the affected review. Until
`doc-review-gate` is bundled with Bruce, if it is unavailable, perform and disclose a separated
main-agent P0/P1 readiness pass; lack of an independent reviewer remains blocking when the user
explicitly requires independence.

For guarded work, invoke `verify-completion` as a separate structured second pass. Prefer a fresh
native subagent only when the guarded change spans multiple components or contracts, combines a
migration with rollout work, or otherwise has a broad security/data blast radius.
For critical work or an explicitly requested independent review, use a fresh native subagent; when
none is available, report blocked and never present a main-agent pass as independent.

Report completion only when all conditions hold:

1. The actual workspace changes match objective and scope, with unrelated changes preserved.
2. Every acceptance item has current, reproducible evidence from risk-proportional verification.
3. Required C0 code self-review is `pass`, and every behavior scenario has a current
   acceptance-to-evidence result at the required verification layer.
4. No unresolved L2/L3/L4 or dependent unfinished task remains.
5. Required D0/D1 document review and completion review have passing current results.
6. Authorized delivery actions are complete, or omitted delivery actions are explicitly reported.
7. Every public or cross-component API, event, or file-contract change has a current
   `api-contracts.md` whose contents cover the actual diff and whose path follows the
   `write-architecture` placement rule.
8. Every required design-bearing task has a current same-directory `artifact-review.md` with
   `Artifact gate: pass`; its candidate decisions still match the actual diff.
9. Every `full` task has a test-design decision in `artifact-review.md`; when a trigger is present,
   the current `test-plan.md` covers the actual acceptance, otherwise the repository-backed skip
   reason is recorded there.

Summarize changed files, C0 and document-review verdicts, acceptance-to-evidence results, repair
loops, the artifact gate path and decision, residual risks, and any delivery action intentionally
not performed.
Keep implementation/completion D0/D1 results in the current task by default; keep C0 and
completion-review results there as well. Design-phase candidate decisions and their D0/D1 readiness
belong in `artifact-review.md`, never `execute_record.md`. During Goal-backed execution, include only
execution-stage review evidence in the audit packet so `goal-execution-gate` records it in the
existing `execute_record.md`.
For a Goal-backed route, return the evidence to the gate; only the gate applies native Goal complete
or blocked status after its terminal checks.

## Does not own

Do not implement or configure a sandbox, permission layer, host adapter, scheduler, lease, heartbeat,
worktree manager, second evidence store, or transcript mirror. The Goal audit record is not runtime
state. Do not wrap Codex execution behind a Bruce CLI, MCP server, or app.
