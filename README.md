# Bruce

Bruce is a Codex workflow plugin for software delivery. It organizes a task around a minimal
contract, proportional planning, scenario-based acceptance, bounded verification/repair loops, and
evidence-backed completion. Standard/full describes evidenced delivery topology; Goal persistence,
design readiness, and test design are selected independently. A low-noise plugin hook reminds Codex
when changed planning or design documents may require Design Gate before implementation.

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
- Behavior acceptance uses stable `Given/When/Then/Evidence` scenarios. Development starts from a
  failing test or reproducible scenario when feasible.
- Verification is layered across unit/component, real integration/API/database, and real use. Web
  acceptance uses the Codex App Chrome capability with the user's current session and real service;
  Bruce never silently replaces it with Playwright.
- An L1 failed scenario enters a bounded repair loop: fix, inspect the change, rerun the unchanged scenario,
  then run related regressions. Two unsuccessful complete rounds escalate to L2 replanning; L0,
  L2, L3, and L4 retain their retry, replan, decision, and incident-freeze semantics.
- Every task that persists downstream-governing design runs `design-gate`. It decides artifact
  completeness and document readiness together, persists one `design-review.md`, and returns only
  `Design: pass|blocked`.
- Every implementation task ends with `verify-completion`. It performs final author-quality, scope,
  evidence, design-alignment, and risk-triggered independent checks internally and returns only
  `Completion: pass|issues|blocked`.
- Independent review is a mode inside one of those gates, not another verdict that callers combine.

The canonical entry is [`skills/bruce/SKILL.md`](skills/bruce/SKILL.md). Other directories under
`skills/` are independently discoverable supporting capabilities. Every skill includes generated
`agents/openai.yaml` UI metadata. Bruce has no CLI, MCP server, app, sandbox implementation, or
custom scheduler.

`design-gate` is the only implementation-entry decision. `verify-completion` is the only completion
decision. `goal-execution` is an optional persistence mode: it records those results and synchronizes
native Goal state without re-evaluating either one. `spawn-execute` is only a bounded delegation
helper under an active Goal.

## Planning document review hook

The bundled `PostToolUse` hook recognizes planning and design documents under `docs/` plus Trellis
task documents. It injects a Design Gate reminder after a successful edit-like tool call. Code,
ordinary documentation, failed tools, and absolute paths outside the active task `cwd` stay quiet.

The hook is advisory: it runs no check and does not make a readiness or completion decision. Plugin
hooks run whenever the Bruce plugin is enabled,
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
