# Bruce Workflow

Bruce Workflow defines the language for a proportional Codex-native software delivery workflow with evidence-backed design and completion decisions.

## Language

**Task Contract**:
The current task's objective, scope, acceptance, constraints, execution profile, business risk, and only the planning detail needed to make delivery verifiable.
_Avoid_: Prompt summary, fixed checklist, live workflow state

**Task Contract Package**:
For a persisted implementation plan, handoff, or multi-step requirement, one change-level `tasks/`
directory containing frozen `T-<id>-<slug>.md` contracts plus `tasks/index.yaml`. Task files define
objective, include/exclude scope, dependencies, acceptance, verification, authorization, and stop
conditions. Live task status belongs in `checkpoint.yaml` or the current checkpoint message; the package
is not a scheduler, parallel executor, or second evidence store.
_Avoid_: One task package per repository, silent scope widening, status edits inside frozen contracts

**Execution Profile**:
A delivery-topology classification that starts as `unresolved` during bounded inspection and resolves to `standard` or `full` from component and contract evidence.
_Avoid_: Task size, business risk, serial mode, parallel mode

**Business Risk**:
The independently classified consequence of a change: `low`, `guarded`, or `critical`, with authorization and review behavior proportional to the evidence-backed risk.
_Avoid_: Execution profile, host permission, failure level

**Supporting Capability**:
A focused Bruce skill selected only when its own predicate is present; selecting one capability does not create a fixed pipeline or automatically invoke another.
_Avoid_: Mandatory stage, profile-driven cascade, full-delivery bundle

**Prototype Design Capability**:
The optional `write-prototype` skill prepares grounded UI context, drives a user-selected Open Design provider through Codex-owned host tools, and preserves generated and user-confirmed artifacts for the existing gates.
_Avoid_: Mandatory UI stage, bundled MCP server, prototype-as-production-code, third gate

**Prototype Exploration Capability**:
The optional `explore-prototype` skill answers one logic or UI-structure question with throwaway code. A native subagent may generate a frozen, path-bounded slice, while the main agent retains decisions, feedback, integration, and promotion through `write-prototype` when the result must govern implementation.
_Avoid_: Formal prototype evidence, production code, delegated product authority, mandatory subagent

**Design Gate**:
The `design-gate` skill makes the only implementation-entry decision for persisted requirements, architecture, contracts, schema design, plans, test designs, or UI prototypes that will govern downstream implementation. It returns `Design: pass|blocked` and persists one `design-review.md`.
_Avoid_: Plan approval, separate artifact gate, independent-agent verdict

**Goal Execution Mode**:
An optional persistence mode entered only for explicit Goal intent or a task-contract need for continuous, cross-turn, or auditable execution. It is independent of execution profile and does not decide design readiness or completion.
_Avoid_: Full profile, Goal gate, scheduler, completion authority

**Goal Audit Record**:
The single `.goal/<goal-id>/execute_record.md` human audit record maintained while Goal Execution Mode is active; native Goal state remains the execution-state source of truth.
_Avoid_: Runtime state, component ledger, second evidence store

**Acceptance Scenario**:
A stable behavior contract expressed as concrete `Given`, `When`, `Then`, and `Evidence`, with every material outcome mapped to a feasible verification layer.
_Avoid_: Natural-language completion claim, mocked-only proof, reduced passing check

**Shared Verification Scenario**:
A versioned, requirement-scoped business-flow contract keyed by `scenario_id + scenario_version`, with independent API/UI steps, namespaces, evidence requirements, and status semantics.
_Avoid_: Environment inventory, runtime result, model router, parallel Completion verdict

**Track Result**:
Current evidence for one exact Scenario version and one API/UI track, including mode, namespace, commands/actions, assertions, evidence, blockers, and unverified gates. Its derived `overall_status` is not `Completion`.
_Avoid_: Static Profile fact, hidden runtime ledger, final completion decision

**Test Dispatch**:
The supporting capability that locks a shared Scenario version, selects `api`/`ui`/`both`, isolates write paths, routes delegated concerns through Bruce Functional Agent Profiles, and aggregates track states without owning browser actions or Completion.
_Avoid_: Generic test runner, private model router, browser runtime, second gate

**UI Surface Contract**:
A technology-neutral product-surface contract keyed by stable `surface_id`, recording region hierarchy, required states, interaction transitions, observable fields, layout invariants, viewports, evidence methods, and generic implementation mappings. It is a design/evidence contract, not a React/Vue/DOM tree or a second verdict authority.
_Avoid_: Framework AST contract, visual-token validator replacement, prototype screenshot or DOM text as runtime proof

**Completion Gate**:
The `completion-gate` skill makes the only completion decision for an implementation task, based on final scope, author quality, current acceptance evidence, design alignment, failures, and delivery boundaries. It returns `Completion: pass|issues|blocked`.
_Avoid_: Self-report, separate review verdict, completion-review artifact

**Review Mode**:
The `main-agent` or `independent` way a Design Gate or Completion Gate performs its internal review. Independence is risk- or user-triggered and never adds another externally combined verdict.
_Avoid_: Mandatory independent reviewer, third gate, reviewer approval

**Failure Level**:
An L0-L4 classification applied to the smallest affected boundary: transient retry, repair, replan, business authority, or unknown/incident handling.
_Avoid_: Task priority, execution lane, global failure hold

**Codex Host Authority**:
Codex ownership of tools, files, commands, permissions, native plans and Goals, and subagent lifecycle; Bruce consumes host results without creating a second permission or execution runtime.
_Avoid_: Bruce permission layer, host adapter, workflow-owned scheduler

## Functional Agent routing

Native Subagent delegation is contract-driven rather than personality-driven. Select one of the five internal Profiles, construct the v1 Task Packet, resolve model override/fallback through the shared resolver, and attach `model_resolution` to the role-specific evidence Packet. `inspector` is read-only, `implementer` is limited to Task Packet paths, `prototype-generator` runs formal Open Design prototype generation with its resolved `gemini-3.8-flash` + `high` configuration and no current-model fallback, `verifier` returns reproducible `verification_packet`, and `reviewer` returns clean-context `review_packet` findings only. Neither worker emits a Design or Completion verdict.

## Evidence Index

- **Verified**: the workflow has two decisions and one optional execution mode (`skills/bruce/SKILL.md:18-24`).
- **Verified**: task contract, profile resolution, and profile/risk independence are defined in `skills/bruce/SKILL.md:38-63`.
- **Verified**: persisted plans derive one sequential `tasks/` contract package while live status remains in the change-level checkpoint (`skills/bruce/references/task-contract.md`, `skills/write-plan/SKILL.md`).
- **Verified**: capabilities are predicate-driven and do not cascade from profile selection (`skills/bruce/SKILL.md:69-93`).
- **Verified**: `write-prototype` keeps provider execution host-owned and returns change-scoped brief, manifest, and snapshot evidence (`skills/write-prototype/SKILL.md`).
- **Verified**: `explore-prototype` separates logic/UI exploration from formal prototype readiness and bounds optional generation delegation (`skills/explore-prototype/SKILL.md`).
- **Verified**: Design Gate owns persisted-design readiness, including governing UI prototypes, and its single verdict (`skills/design-gate/SKILL.md`).
- **Verified**: Goal Execution Mode is profile-independent, native-Goal-backed persistence rather than another gate (`skills/goal-execution/SKILL.md:8-18`).
- **Verified**: Completion Gate owns the single completion verdict and treats independence as an internal mode (`skills/completion-gate/SKILL.md:6-9`, `skills/completion-gate/SKILL.md:57-89`).
- **Verified**: shared Scenario/Track Result contracts lock exact versions, isolate API/UI namespaces and write paths, and aggregate track state without emitting Completion (`skills/test-dispatch/references/scenario-schema.md`, `skills/test-dispatch/references/track-result-schema.md`).
- **Verified**: API orchestration keeps project routes and commands repository-grounded, bounds asynchronous polling, and requires authoritative readback and redacted evidence (`skills/api-test-orchestration/SKILL.md`).
- **Verified**: browser UI verification keeps real page actions with the configured host Provider and rejects subagent/API shortcuts and silent Provider fallback (`skills/browser-ui-verification/SKILL.md`, `skills/browser-ui-verification/references/host-boundary.md`).
- **Verified**: L0-L4 recovery applies to the smallest supported dependency or incident boundary (`skills/bruce/references/failure-recovery.md:3-25`).
- **Verified**: Codex and Bruce ownership boundaries are defined in `skills/bruce/references/plugin-boundary.md:3-38`.
