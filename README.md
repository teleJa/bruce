# Bruce

Bruce is a Codex workflow plugin for software delivery. It organizes a task around a minimal
contract, proportional planning, scenario-based acceptance, bounded verification/repair loops, and
evidence-backed completion. Ordinary execution continues within the authorized scope through verification
and bounded repair without requiring Goal. Standard/full describes evidenced delivery topology;
design readiness and test design are selected independently. A low-noise plugin hook reminds Codex
when changed planning or design documents may require Design Gate before implementation and
deterministically validates any written `design-review.md`.

## Functional Agent contracts

Bruce routes native Subagents through five internal Profiles: `inspector`, `implementer`, `prototype-generator`, `verifier`, and `reviewer`. The shared v1 Task/Verification/Review Packet contract lives in `skills/bruce/references/functional-agent-contracts.md`, and the built-in registry lives in `skills/bruce/references/model-profiles.yaml`.

Profile resolution is `task override > project override > user override > built-in Profile > current model fallback`. The resolver passes `model` to the Codex host only when the target model is confirmed available; Profiles with `fallback=current` may otherwise inherit the current model and record `fallback_used`, `effective_model`, `capability_status=degraded`, and `resolution_result=fallback`. `prototype-generator` instead defaults to `gemini-3.8-flash` + `high` with `fallback=blocked`: formal `write-prototype` work must spawn with its resolved Profile model and pass the same model to Open Design, never inherit a default/current model. Inspector remains read-only (the built-in inspection route is `gpt-5.6-luna` + `max`), Implementer is path-bounded, Verifier emits only `verification_packet`, and Reviewer emits only `review_packet`; Design/Completion remain the only terminal decisions.

Validate the contract with `python3 scripts/validate_functional_agents.py`.

## Pre-design solution analysis

`$solution-analysis` is the read-only pre-design analysis layer. It inspects the current implementation and existing project solutions, analyzes feasibility and alternatives, reports evidence gaps and unresolved decisions, and then waits for explicit user direction. The main Agent decides whether to inspect directly or delegate bounded shards through `inspect-parallel`; delegated code research uses the `inspector` Profile (`gpt-5.6-luna` + `max`), while a delegated read-only feasibility challenge may use the `reviewer` Profile (`gpt-5.6-terra` + `high`). It does not create `docs/change`, write design artifacts, invoke downstream Skills automatically, or authorize implementation.

`$bruce` is the user-directed design and implementation capability. Analysis-only work starts with
`$solution-analysis`, not with a hidden pre-step inside `$bruce`. After the user discusses and confirms
the analysis, `$bruce` can be entered with an explicit `design-only` scope to persist the necessary design
artifacts and run Design Gate without implementing behavior or invoking Completion Gate. A separate user
instruction is required before implementation begins. Bruce does not infer implementation from a
prior analysis or design document without an explicit user instruction.

## Workflow

```text
inspect -> task contract -> design when needed -> Design Gate when needed -> implement -> Completion Gate -> summary
```

- `unresolved` is a temporary, read-only inspection state. It creates no Goal, design artifact,
  change directory, or behavior implementation solely because boundary evidence is incomplete.
- `standard` is resolved after inspection proves one delivery component with no cross-component
  contract propagation.
- `full` is resolved from named multi-component delivery or cross-component contract evidence. Size,
  duration, risk, or uncertainty alone is insufficient, and `full` does not trigger other capabilities.
- `low`, `guarded`, and `critical` describe business/change risk only.
- L0-L4 classify transient, repairable, replan, business-authority, and unknown/incident failures.
- Planning, architecture, test design, review, and delegation run only from their own predicates.
  Ordinary continuation, cross-turn recovery, and checkpoint recording do not require Goal.
  Only an explicit request to use native Goal (`/goal` or `$goal-execution`) enters its compatibility
  adapter; profile, duration, `continue nonstop`, `继续开发`, and audit needs do not activate it.
- Continue authorized implementation until acceptance is met or a user pause, host limit, scope/authority
  change, exhausted repair budget, or real blocker requires stopping. A progress checkpoint alone does
  not end execution or require another user message. This is not a background-execution guarantee.
- UI prototype generation is an optional `write-prototype` capability. It can drive a host-configured
  Open Design MCP run, preserve generated and user-confirmed snapshots, and feed the existing Design
  and Completion Gates without adding a third gate or copying product-delivery lanes.
- `write-prototype` may also carry a technology-neutral UI Surface Contract: stable Surface IDs,
  region/state/interaction/observable/layout semantics, generic implementation locators, and current
  evidence. Surface completeness is validated separately from exact visual-token assertions; Design and
  Completion remain the only verdict owners, and a Surface Contract never replaces configured-provider runtime evidence.
- Question-driven prototype exploration is an optional `explore-prototype` capability. It builds a
  throwaway logic demo or structurally different UI variants to answer one uncertainty. A bounded
  native subagent may generate the code after the main agent freezes the question, paths, scenarios,
  and checks; the main agent keeps product decisions, user feedback, integration, and Gate ownership.
  Exploration becomes implementation-governing only after promotion through `write-prototype`.
- Behavior acceptance uses stable `Given/When/Then/Evidence` scenarios. Development starts from a
  failing test or reproducible scenario when feasible.
- User-visible Web work declares proportional `visual_scope=none|browser-smoke|browser-layout` and
  reads `verification.browser_provider` from `.bruce/config.yaml` (default: `ego-lite`; supported:
  `ego-lite`, `chrome`). Visible acceptance requires a real interaction through the selected Provider
  plus visual evidence. Layout-sensitive outcomes additionally require the selected Provider's
  screenshots and relevant geometry/overflow evidence. Provider failure is incomplete/blocked; no
  silent fallback is allowed.
- Verification is layered across unit/component, real integration/API/database, and real use. Web
  acceptance records the selected Provider, target/session, actions, visible result, capture time,
  basis revision, and artifact path or hash. See `skills/bruce/references/browser-provider.md`.
- Shared user-facing verification can use [`test-dispatch`](skills/test-dispatch/SKILL.md) to lock one
  Scenario ID/version and isolate `api`/`ui` tracks. [`api-test-orchestration`](skills/api-test-orchestration/SKILL.md)
  covers project-grounded API state transitions, bounded polling, permissions, idempotency, and
  authoritative readback. [`browser-ui-verification`](skills/browser-ui-verification/SKILL.md) keeps real
  page actions with the configured host Browser Provider; subagents and API shortcuts cannot replace
  them. Track `overall_status` is evidence for Verification Run/Checkpoint and never a second
  `Completion` verdict.
- An L1 failed scenario enters a bounded repair loop: fix, inspect the change, rerun the unchanged scenario,
  then run related regressions. Two unsuccessful complete rounds escalate to L2 replanning; L0,
  L2, L3, and L4 retain their retry, replan, decision, and incident-freeze semantics.
- Every task that persists downstream-governing design runs `design-gate`. It decides artifact
  completeness and document readiness together, persists one `design-review.md`, and returns only
  `Design: pass|blocked`.
- When independent per-task boundaries or handoff require it, use one change-level
  `tasks/` package: `tasks/index.yaml` plus frozen `T-<id>-<slug>.md` contracts. Task state is tracked
  in `checkpoint.yaml` or the current checkpoint message; sequential execution is the default and
  the package is not a scheduler or second evidence store.
- Persisted design artifacts use one shared placement resolver. For cross-repository work, only the
  repositories' direct parent directories are compared; a shared parent may use `.bruce/config.yaml`,
  while different parents require asking the user for the document path. Bruce never searches higher
  ancestors or splits one design package across repositories.
- Every implementation task ends with `completion-gate`. It performs final author-quality, scope,
  evidence, design-alignment, and risk-triggered independent checks internally and returns only
  `Completion: pass|issues|blocked`.
- Completion review first completes one acceptance/branch/evidence matrix and batches all current
  findings. Repairs rerun only affected checks, the unchanged original failure, and related
  regressions; they do not create a per-finding review chain.
- Structured checkpoints record material execution boundaries; routine progress and unchanged-context
  continuation use brief updates. Trigger and recovery rules live in
  [`failure-recovery.md`](skills/bruce/references/failure-recovery.md), not in this overview.
- Runtime-dependent work still requires read-only capability preflight and current evidence; retry,
  async-wait, permission, and unknown-side-effect boundaries remain mandatory.
- Independent review is a mode inside one of those gates, not another verdict that callers combine.

The canonical entry is [`skills/bruce/SKILL.md`](skills/bruce/SKILL.md). Other directories under
`skills/` are independently discoverable supporting capabilities. `environment-operations` is a
project-operation capability that generates an executable project-local Skill and bounded runner from
an exact confirmed Environment Profile; it does not generate `operations.yaml` or silently execute
project operations. Every skill
includes generated `agents/openai.yaml` UI metadata. Bruce has no CLI, MCP server, app, sandbox
implementation, or custom scheduler.

`design-gate` is the only implementation-entry decision. `completion-gate` is the only completion
decision. `goal-execution` is an explicit opt-in adapter for native Goal lifecycle; it consumes existing
Gate results without re-evaluating them. It does not create `execute_record.md` by default. Durable
audit records require an explicit user request and should reference existing progress and evidence.
`spawn-execute` supports bounded ordinary implementation delegation without a Goal or audit-record
prerequisite. Historical `.goal/` records are preserved but never required for ordinary recovery.

## Planning document review hook

The bundled `PostToolUse` hook recognizes planning and design documents under `docs/`, change-level
`tasks/` contracts, plus Trellis task documents, including writes performed through Bash. Ordinary
planning edits receive an advisory
Design Gate reminder. A written `design-review.md` is instead checked by the bundled deterministic
validator; an invalid review blocks normal tool-result processing until the current files are repaired.
Code, ordinary documentation, failed tools, read-only Bash calls, and absolute paths outside the active
task `cwd` stay quiet. The validator checks candidate completeness, required artifact delivery, real
paths, placeholders, readiness/verdict consistency, independently declared acceptance complexity, and any
new plan-declared `tasks/` contract package.

The hook does not itself author or approve a review: it only validates the persisted gate artifact.
Plugin hooks run whenever the Bruce plugin is enabled,
not only when the `$bruce` skill is selected. Codex requires hooks to be enabled and the installed
definition to be reviewed in `/hooks`; users can decline or disable it there.

## Workflow policy ownership

[`artifact-policy.md`](skills/bruce/references/artifact-policy.md) owns independent artifact and Design
Gate predicates. A plan can stand alone; it does not automatically create task files. Every behavior change must create
an independent `test-plan.md` with scenarios, commands, and evidence; its depth is proportional to acceptance complexity.
The authority includes a test-design decision table: every behavior change invokes `write-tests`,
using the minimal template for simple acceptance and applicable modules from the expanded template otherwise.
The recovery reference owns checkpoint triggers and local/global repair-budget precedence;
the verification reference owns evidence content. Batch L1 repairs do not consume the Completion-only
budget, and entering Completion or resuming never resets a repeated failure's local count.
Completion reports are concise by default and expand when coverage, revisions, repairs, or the user
needs detail. This changes presentation, not required verification or permission boundaries.

Optional isolated behavior trials live in [`tests/fixtures/workflow_behavior/README.md`](tests/fixtures/workflow_behavior/README.md).
They supplement deterministic tests and are not a new daily Gate or Agent runtime. Eight scenarios cover
local fixes, design/pause boundaries, original/stale evidence, unavailable prerequisites, unknown external
outcomes and unrelated user work. The optional `summarize` command aggregates explicitly supplied measurements;
see [measurement boundaries](tests/fixtures/workflow_behavior/measurements.md). It never reads user sessions,
launches actors, certifies evidence references, or treats fixture checks as real Agent success.

## Static validation

Static checks do not install the plugin or modify Codex configuration:

```bash
python3 scripts/validate_plugin.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Install for a local smoke test

The repository is both the plugin root and a repo-local marketplace root. Installing it changes the
user's Codex plugin state, so do this only with explicit authorization:

```bash
python3 scripts/refresh_local_plugin.py
```

Use this wrapper for updates instead of calling the cachebuster helper directly. Internally it
performs the equivalent of `codex plugin marketplace add <plugin-root>` and
`codex plugin add bruce@bruce --json`, then repairs compatibility aliases. Codex keeps
an installed hook's absolute `PLUGIN_ROOT` for the lifetime of the current session; the wrapper
keeps old Bruce cache roots usable while installing the new version, so an in-flight session does
not emit a missing `post_tool_review_reminder.py` error. Start a new Codex task after installation,
then ask: `Use Bruce to implement and verify this task.`
Review and trust the Bruce hook in `/hooks` before testing planning-document reminders.
The marketplace source is `.` because `.agents/plugins/marketplace.json` lives in the plugin root;
it must not be rewritten to `./plugins/bruce`.

## Development boundary

- Edit the Bruce workflow only in `skills/bruce/SKILL.md` and its reachable references/templates.
- Keep supporting skills independent; invoking one must not cascade into a fixed pipeline.
- Keep installation smoke separate from static package validation.
- Preserve historical change documents under `docs/`; they are design records, not resumable state.
