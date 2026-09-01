# Bruce

Bruce is a Codex workflow plugin for software delivery. It organizes a task around a minimal
contract, proportional planning, scenario-based acceptance, bounded verification/repair loops, and
evidence-backed completion. Standard/full describes evidenced delivery topology; Goal persistence,
design readiness, and test design are selected independently. A low-noise plugin hook reminds Codex
when changed planning or design documents may require Design Gate before implementation and
deterministically validates any written `design-review.md`.

## Functional Agent contracts

Bruce routes native Subagents through four internal Profiles: `inspector`, `implementer`, `verifier`, and `reviewer`. The shared v1 Task/Verification/Review Packet contract lives in `skills/bruce/references/functional-agent-contracts.md`, and the built-in registry lives in `skills/bruce/references/model-profiles.yaml`.

Profile resolution is `task override > project override > user override > built-in Profile > current model fallback`. The resolver passes `model` to the Codex host only when the target model is confirmed available; otherwise it omits `model`, inherits the current model, and records `fallback_used`, `effective_model`, `capability_status=degraded`, and `resolution_result=fallback`. A fallback never proves model heterogeneity. Inspector remains read-only (the built-in inspection route is `gpt-5.6-luna` + `max`), Implementer is path-bounded, Verifier emits only `verification_packet`, and Reviewer emits only `review_packet`; Design/Completion remain the only terminal decisions.

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
                                      \-> optional Goal execution mode -/
```

- `unresolved` is a temporary, read-only inspection state. It creates no Goal, design artifact,
  change directory, or behavior implementation solely because boundary evidence is incomplete.
- `standard` is resolved after inspection proves one delivery component with no cross-component
  contract propagation.
- `full` is resolved from named multi-component delivery or cross-component contract evidence. Size,
  duration, risk, or uncertainty alone is insufficient, and `full` does not trigger other capabilities.
- `low`, `guarded`, and `critical` describe business/change risk only.
- L0-L4 classify transient, repairable, replan, business-authority, and unknown/incident failures.
- Planning, architecture, test design, review, delegation, and persistence run only from their own
  predicates. Explicit Goal, continuous/cross-turn persistence, or audit requests enter
  `goal-execution`; profile, complexity, duration, risk, and subagent use do not.
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
- An L1 failed scenario enters a bounded repair loop: fix, inspect the change, rerun the unchanged scenario,
  then run related regressions. Two unsuccessful complete rounds escalate to L2 replanning; L0,
  L2, L3, and L4 retain their retry, replan, decision, and incident-freeze semantics.
- Every task that persists downstream-governing design runs `design-gate`. It decides artifact
  completeness and document readiness together, persists one `design-review.md`, and returns only
  `Design: pass|blocked`.
- A persisted implementation plan, handoff, or multi-step requirement derives one change-level
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
- Multi-batch, long-running, cross-component, or pre-side-effect work uses a bounded batch checkpoint
  with `Checkpoint: clear|issues|blocked` as progress feedback; the final `Completion Gate` remains
  the only overall completion decision.
- Runtime-dependent batches perform one read-only capability preflight. Long-running work records a
  progress checkpoint after at most 40 tool calls or 45 minutes; the interval does not split or stop a
  declared current task, and closed or invalid async handles are never polled again.
- Independent review is a mode inside one of those gates, not another verdict that callers combine.

The canonical entry is [`skills/bruce/SKILL.md`](skills/bruce/SKILL.md). Other directories under
`skills/` are independently discoverable supporting capabilities. `environment-operations` is a
static generic capability that reads/writes a project-local Environment Operation Manifest from an
exact confirmed Environment Profile; it does not dynamically install project Skills. Every skill
includes generated `agents/openai.yaml` UI metadata. Bruce has no CLI, MCP server, app, sandbox
implementation, or custom scheduler.

`design-gate` is the only implementation-entry decision. `completion-gate` is the only completion
decision. `goal-execution` is an optional persistence mode: it records those results and synchronizes
native Goal state without re-evaluating either one. `spawn-execute` is only a bounded delegation
helper under an active Goal.

## Planning document review hook

The bundled `PostToolUse` hook recognizes planning and design documents under `docs/`, change-level
`tasks/` contracts, plus Trellis task documents, including writes performed through Bash. Ordinary
planning edits receive an advisory
Design Gate reminder. A written `design-review.md` is instead checked by the bundled deterministic
validator; an invalid review blocks normal tool-result processing until the current files are repaired.
Code, ordinary documentation, failed tools, read-only Bash calls, and absolute paths outside the active
task `cwd` stay quiet. The validator checks candidate completeness, required artifact delivery, real
paths, placeholders, readiness/verdict consistency, the behavior-plan-to-test-plan invariant, and any
new plan-declared `tasks/` contract package.

The hook does not itself author or approve a review: it only validates the persisted gate artifact.
Plugin hooks run whenever the Bruce plugin is enabled,
not only when the `$bruce` skill is selected. Codex requires hooks to be enabled and the installed
definition to be reviewed in `/hooks`; users can decline or disable it there.

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
