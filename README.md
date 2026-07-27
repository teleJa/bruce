# Bruce

Bruce is a Codex workflow plugin for software delivery. It organizes a task around a minimal
contract, proportional planning, scenario-based acceptance, bounded verification/repair loops, and
evidence-backed completion. Standard work stays in the current Codex task; full delivery uses the
bundled native Goal gate for persistent, auditable execution. A low-noise plugin hook reminds Codex
to run D0 self-review after changing planning or design documents.

## Workflow

```text
inspect -> task contract -> design when needed -> artifact gate when required -> implement -> verify -> summary
```

- `standard` is the current-task delivery profile and does not create a Goal by default.
- `full` is the complete delivery profile for large, multi-deliverable, multi-component, or
  cross-component contract work. It passes a same-directory design artifact gate before entering
  `goal-execution-gate` and implementation.
- `low`, `guarded`, and `critical` describe business/change risk only.
- L0-L4 classify transient, repairable, replan, business-authority, and unknown/incident failures.
- Planning, architecture, test design, review, and delegation skills run only when the task needs
  them. Full tasks are Goal-backed by default. A standard task enters Goal only when the user explicitly
  requests Goal, continuous/cross-turn execution, or an audit record. Goal-backed execution
  maintains `.goal/<goal-id>/execute_record.md` for human audit while native Goal remains the only
  execution-state source.
  An explicit request to skip Goal is honored but leaves persistent recovery and the audit record
  unavailable; it does not silently reclassify the task as standard.
- Behavior acceptance uses stable `Given/When/Then/Evidence` scenarios. Development starts from a
  failing test or reproducible scenario when feasible; every code change receives a C0 self-review.
- Verification is layered across unit/component, real integration/API/database, and real use. Web
  acceptance uses the Codex App Chrome capability with the user's current session and real service;
  Bruce never silently replaces it with Playwright.
- An L1 failed scenario enters a bounded repair loop: fix, rerun C0, rerun the unchanged scenario,
  then run related regressions. Two unsuccessful complete rounds escalate to L2 replanning; L0,
  L2, L3, and L4 retain their retry, replan, decision, and incident-freeze semantics.
- Every documentation change receives a separate D0 self-review with an explicit verdict. Important
  or downstream-governing documents receive a conditional D1 P0/P1 readiness gate.
- Every full task, and every standard task that persists a downstream design source of truth,
  receives an `artifact-review.md` beside its design documents. The gate enumerates requirement,
  architecture, API contract, table design, plan, and test-design candidates; missing required
  artifacts or skipped candidates without repository evidence block implementation.

The canonical entry is [`skills/bruce/SKILL.md`](skills/bruce/SKILL.md). Other directories under
`skills/` are independently discoverable supporting capabilities. Every skill includes generated
`agents/openai.yaml` UI metadata. Bruce has no CLI, MCP server, app, sandbox implementation, or
custom scheduler.

The bundled `artifact-review-gate` owns design-artifact completeness and its same-directory audit
file. The bundled `goal-execution-gate` begins afterward and owns native Goal creation, continuation,
terminal status, and the single execution audit record. It may link to `artifact-review.md`, but it
does not copy design skip decisions into `execute_record.md`. It uses `spawn-execute` only for
bounded work under the active Goal. Ordinary standard-task subagent delegation uses Codex directly
and creates no Goal.

The D1 document gate currently uses the separately discoverable `doc-review-gate`. Plan-only work
with meaningful execution risk may use the deeper `plan-review` instead; Bruce does not run both
mechanically. `plan-review: Clean` maps to D1 pass; `Issues Found` maps to D1 failure. Design-phase
D0/D1 results are summarized in `artifact-review.md`; implementation/completion review evidence stays
in the current task or enters the Goal execution audit record. Until the D1 gate is bundled with
Bruce, an unavailable gate falls back to a disclosed main-agent P0/P1 pass unless the user explicitly
requires an independent reviewer.

## Planning document review hook

The bundled `PostToolUse` hook recognizes planning and design documents under `docs/` plus Trellis
task documents. It injects a D0 self-review reminder after a successful edit-like tool call. Code,
ordinary documentation, failed tools, and absolute paths outside the active task `cwd` stay quiet.

The hook is advisory: it neither runs the review nor proves that review passed. Bruce's C0/D0/D1
completion contract remains authoritative. Plugin hooks run whenever the Bruce plugin is enabled,
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
codex plugin marketplace add /absolute/path/to/bruce
codex plugin add bruce@bruce
```

Start a new Codex task after installation, then ask: `Use Bruce to implement and verify this task.`
Review and trust the Bruce hook in `/hooks` before testing planning-document reminders.
The marketplace source is `.` because `.agents/plugins/marketplace.json` lives in the plugin root;
it must not be rewritten to `./plugins/bruce`.

## Development boundary

- Edit the Bruce workflow only in `skills/bruce/SKILL.md` and its reachable references/templates.
- Keep supporting skills independent; invoking one must not cascade into a fixed pipeline.
- Keep installation smoke separate from static package validation.
- Preserve historical change documents under `docs/`; they are design records, not resumable state.
