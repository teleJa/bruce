# Bruce Workflow

Bruce Workflow defines the language for a proportional Codex-native software delivery workflow with evidence-backed design and completion decisions.

## Language

**Task Contract**:
The current task's objective, scope, acceptance, constraints, execution profile, business risk, and only the planning detail needed to make delivery verifiable.
_Avoid_: Prompt summary, fixed checklist, workflow state file

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

## Evidence Index

- **Verified**: the workflow has two decisions and one optional execution mode (`skills/bruce/SKILL.md:15-20`).
- **Verified**: task contract, profile resolution, and profile/risk independence are defined in `skills/bruce/SKILL.md:38-63`.
- **Verified**: capabilities are predicate-driven and do not cascade from profile selection (`skills/bruce/SKILL.md:69-93`).
- **Verified**: `write-prototype` keeps provider execution host-owned and returns change-scoped brief, manifest, and snapshot evidence (`skills/write-prototype/SKILL.md`).
- **Verified**: Design Gate owns persisted-design readiness, including governing UI prototypes, and its single verdict (`skills/design-gate/SKILL.md`).
- **Verified**: Goal Execution Mode is profile-independent, native-Goal-backed persistence rather than another gate (`skills/goal-execution/SKILL.md:8-18`).
- **Verified**: Completion Gate owns the single completion verdict and treats independence as an internal mode (`skills/completion-gate/SKILL.md:6-9`, `skills/completion-gate/SKILL.md:57-89`).
- **Verified**: L0-L4 recovery applies to the smallest supported dependency or incident boundary (`skills/bruce/references/failure-recovery.md:3-25`).
- **Verified**: Codex and Bruce ownership boundaries are defined in `skills/bruce/references/plugin-boundary.md:3-38`.
