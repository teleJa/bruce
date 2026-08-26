# Verification and feedback loop

Use this policy while implementing and gathering evidence. `design-gate` makes the only design
readiness decision; `completion-gate` performs the final author-quality, evidence, and review checks
and returns the only completion decision.

## Verifiable acceptance scenarios

Give every behavior-bearing acceptance item a stable id and define:

- `Given`: concrete user/system state, data, permissions, and real dependencies.
- `When`: the user or system action under verification.
- `Then`: observable behavior and relevant data/state consequence.
- `Evidence`: the exact unit, integration, API, database, build, or real-browser check that proves
  each material outcome now.

Do not start behavior implementation while a material outcome has no feasible evidence path unless
the user explicitly accepts an exploratory or unverified boundary.

## Proportional visual scope

Classify user-visible Web verification in the task contract as one of:

- `visual_scope=none`: no material rendered output, layout, responsive behavior, or user-visible
  interaction changes; record a repository-backed reason when the task touches UI code.
- `visual_scope=chrome-smoke`: a visible label, route, control, or state changes without a material
  layout invariant; require one real user interaction against the current Chrome target, the
  resulting visible state, and a screenshot or equivalent Chrome visual artifact.
- `visual_scope=chrome-layout`: layout, sizing, overflow, wrapping, grid/flex, responsive behavior,
  long content, modal/table geometry, animation, prototype matching, or a reported visual defect is
  in scope; require current Chrome screenshots plus the relevant geometry and interaction evidence.

Do not infer `chrome-layout` from any frontend diff alone. Infer it from the material acceptance
outcome and changed rendering risk. Completion must upgrade an under-scoped declaration when the
final diff or acceptance exposes a stronger visible outcome; it must not downgrade a declared
layout check merely to reduce verification cost.

For `chrome-layout`, the evidence records the target URL/tab, viewport, capture time, basis revision,
screenshot path or hash, and the applicable checks (for example card boxes, row heights,
`scrollWidth <= clientWidth`, and before/after interaction states). DOM text presence alone is not
visual evidence. For Web acceptance, an absent `visual_scope` remains an unresolved contract gap;
do not silently treat it as `none`.

## Capability preflight

Before the first batch that depends on a browser, database, model, external service, or another
runtime capability, perform one minimal read-only preflight. Record `capability`, exact `target`,
`check`, `status=available|unavailable|unknown`, current evidence, and dependent acceptance ids. A
configured client, installed extension, environment variable, or planned test is not availability
evidence by itself; verify the actual target and required operation without creating production data
or triggering a billable/irreversible action.

When preflight is unavailable or unknown, mark dependent scenarios `blocked` or `unexecuted`, pause
only their batch, and continue proven-independent work. Do not repeat the same preflight until a
relevant configuration, credential, process, target, or host-capability fact changes. Rerun it before
dependent work resumes and carry its evidence revision into the batch matrix.

## Development feedback

For behavior changes, start with the smallest failing automated test or reproducible scenario when
feasible. Reproduce bugs before fixing them and establish a passing characterization baseline before
refactoring. When test-first work is genuinely impractical, record why and establish the nearest
repeatable check. Do not impose TDD on documentation-only, generated, or mechanical changes.

For a cross-component batch, use the first failing scenario only to establish the batch boundary.
Before the next behavior edit, build a batch change map covering the owned entry points, direct call
sites, allowed paths, material state/error paths, and planned evidence. The change map also records a
stop condition. Implement that
declared compatible slice before rerunning the batch matrix; do not follow each downstream failure into
an undeclared component. Once the batch has changed behavior and starts planned verification, every new
inspection must map to a current acceptance id, known failing matrix row, or declared direct call site.
Classify any unmapped adjacent concern as `deferred`; do not inspect it opportunistically. After the
second non-blocking finding in the same batch, stop single-finding repair and further nonessential
inspection, complete the current batch matrix, and return its findings packet. Only a failure that
prevents safe evidence collection or continuation of the current batch may be repaired immediately.

## Verification layers

Use the smallest sufficient evidence at each layer, but never substitute a lower layer for a required
higher one:

1. Unit/component checks prove local behavior.
2. Integration/API/database checks prove crossed process, service, persistence, or contract edges
   using real dependencies when acceptance requires them.
3. Real-use checks prove user-visible workflows and deployed/runtime wiring.

For user-visible Web behavior, use the Codex App Chrome capability with the user's current Chrome
session, login state, extensions, and real localhost or target service. The required acceptance pass
is: connect to Chrome, perform the real interaction described by `When`, observe the resulting
visible state, and capture the visual artifact and supporting evidence. Record the target, tab,
actions, visible result, capture time, and screenshot/artifact path or hash. If Chrome is
unavailable, report the missing evidence and keep the acceptance incomplete or blocked; do not
claim it passed. Playwright is prohibited in Bruce acceptance and cannot be used as a fallback,
repository-SOP exception, or user-request override. Any Playwright-only result is invalid evidence.

## Continuous author feedback

During implementation, inspect each meaningful code or document diff before moving on. For code,
check affected call sites, boundaries, errors, security, concurrency, data integrity, and regression
coverage as relevant. For documents, check facts, terminology, contracts, cross-references,
acceptance coverage, placeholders, and links.

These checks are development feedback, not separately named gates and not completion evidence by
themselves. `completion-gate` repeats the necessary checks against the final state once, because
later edits can invalidate earlier observations.

Before completion, the owning gate builds one matrix across acceptance ids, changed entry points,
material error/empty/null/partial/duplicate/state paths, verification layers, and current evidence.
It completes that matrix before reporting findings and returns all current findings together. A
repair reruns only affected matrix rows plus the unchanged original failure and related regressions;
it does not create a per-finding review chain or a fresh independent reviewer unless the repair changes
an independence-triggering concern or risk trigger.

## Task package and checkpoint

A persisted implementation plan may define a change-level `tasks/` package. Each task file is a
frozen contract; the current task status belongs in the requirement-level checkpoint. Tasks execute
sequentially by default. A long-running task may span multiple checkpoints; the checkpoint does not split, restart, or shorten the task.

Use a checkpoint when a task changes state, a task boundary is reached, a material finding appears,
the environment or risk boundary changes, work resumes after a user-turn boundary, or a long-running
interval needs a progress snapshot. A checkpoint is progress feedback only, not a third decision, a
Goal ledger, or a second evidence store. It records evidence references rather than copying logs.

For a multi-batch change:

Build the matrix for the current batch only before reviewing its bounded rows:

- one row per batch acceptance id;
- direct changed entry points and direct call sites needed to prove that acceptance;
- material state/error paths identified by the acceptance scenario or the changed code; group
  equivalent paths instead of expanding every transitive caller;
- no adjacent path or concern unless it maps to a current acceptance id, known failing matrix row, or
  declared direct call site; otherwise record it as `deferred`.

Each formal batch row records `batch_id` (for example `batch_id: B1-example`), `acceptance_id`,
`path`, `required_layer`, `basis_revision`, `evidence_revision`, `evidence`, `result`, and
`affected_scope`. When a UI Surface Contract governs the acceptance, the row also records `surface_id`,
`implementation_locator`, `runtime_evidence`, and `layout_evidence` when the visible outcome is material.
The locator is implementation evidence and accepts `file`, `route`, `template`, `view`, or
`source-entry`; it does not impose a framework. Missing or stale surface evidence keeps the row
incomplete, issues, or blocked under the existing rules. The requirement-level checkpoint also
records every task's `task_id`, `status`, `contract_revision`, `evidence_refs`, and `blockers`.
Return `Checkpoint: clear|issues|blocked` as progress feedback only; do not use it as the overall
completion verdict. Every checkpoint uses this machine-readable summary, with `[]` when a collection
is empty:

```yaml
version: 1
Checkpoint: clear|issues|blocked
checkpoint_id: CP-0001
checkpoint_kind: progress|batch|resume
requirement_id: <requirement-or-change-id>
basis_revision: <working-tree-or-commit>
environment: {}
active_task: T-001
execution_mode: sequential
batch_id: <batch-or-null>
matrix: []
tasks:
  - task_id: T-001
    status: pending|in_progress|implemented|verifying|verified|blocked|superseded
    contract_revision: 1
    evidence_refs: []
    blockers: []
acceptance:
  passed: []
  failed: []
  unexecuted: []
findings: []
repair_loop:
  max_rounds: 5
  current_round: 0
  status: not_started|scanning|repairing|verifying|exhausted|complete
completion:
  state: not_started|reviewing|repairing|ready|decided
  result: null|pass|issues|blocked
repair_sets: []
next_action: <continue-task|next-task|blocked-unlock|return-control>
```

A task contract is frozen before execution. If its scope, acceptance, dependency, authorization, or
required verification changes, create a new contract revision or superseding task before continuing.
Do not rewrite a task file merely to record progress.

Before repairing a non-blocking batch failure, complete the current batch matrix and return all
currently observable failures in one batch findings packet. Classify every finding as:

- `blocking`: prevents safe continuation of the current batch; repair it immediately only when the
  repair remains inside the current batch boundary;
- `compatible`: can be repaired together without conflicting file ownership, dependency order, or
  acceptance scope; group these findings into one bounded repair set;
- `deferred`: belongs to another declared task or batch, or needs a scope, authority, or design
  decision; record its owner and do not implement it opportunistically.

Do not repair each newly observed non-blocking finding while the batch matrix remains incomplete, and
do not use an `update_plan` progress update as a substitute for the checkpoint or findings packet.
After the packet, repair compatible findings together, then rerun only affected matrix rows, each
unchanged original failure, and related regressions. A row is `stale` when its evidence revision
differs from the current review basis, a changed path intersects its affected scope, or impact cannot
be determined. Rerun stale rows, the unchanged original failure, and related regressions before
dependent tasks continue. The initial packet is review round 0; subsequent repair rounds read
`workflow.repair_loop.max_rounds` from `.bruce/config.yaml` (default 5). A repair may reveal a new
finding, so each round may scan again, but the configured limit still bounds the loop.

## Independent review

Independence is a review mode inside `design-gate` or `completion-gate`, never a third verdict.
When required, use a fresh native subagent with no inherited author conversation. Use the shared `reviewer` Functional Agent Profile and a clean-context v1 Task Packet; supply objective,
acceptance, the final review target diff or immutable snapshot, raw evidence, and only necessary
constraints. Exclude author rationale, confidence, and proposed conclusion.

The reviewer may inspect repository facts and rerun safe checks but must not edit the reviewed work.
If required independence is unavailable, the owning gate returns `blocked`.

## Repair and regression loop

When verification fails, preserve the original scenario and evidence, then follow
[failure-recovery.md](failure-recovery.md). After an actual repair, inspect the changed code, rerun
the original failed scenario unchanged, and run related regressions. Update the acceptance evidence
after each action; do not replace a failure with a smaller passing check.

## Completion evidence

For each acceptance id, retain its scenario, required verification layer, current evidence, evidence
revision, and result. Natural-language claims, stale runs, mocked-only evidence for a real integration
requirement, or unit evidence for a user-visible flow keep that acceptance incomplete. Pass this evidence once
to `completion-gate`; callers do not create parallel verdicts from it.
