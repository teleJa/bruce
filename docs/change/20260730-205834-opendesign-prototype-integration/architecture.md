# Architecture: Open Design prototype integration

## Objective and scope

- Objective: give Bruce an optional, evidence-grounded prototype workflow backed by Open Design.
- Included: capability routing, external MCP invocation rules, prototype input and artifact
  provenance, Design Gate readiness, and Completion Gate alignment.
- Excluded: MCP installation/runtime ownership, product-management lanes, artifact publishing, and
  production frontend generation.

## Repository evidence

- `skills/bruce/SKILL.md` keeps supporting capabilities predicate-driven and makes Codex own tools.
- `skills/bruce/references/plugin-boundary.md` assigns MCP and app execution to Codex.
- `skills/design-gate/SKILL.md` owns persisted-design readiness through one candidate matrix.
- `skills/completion-gate/SKILL.md` already requires current Chrome evidence for visible Web behavior.
- `scripts/validate_plugin.py` forbids `mcpServers`, `apps`, and `cli` in the Bruce manifest.
- `/Users/tele/xjjk/joytime-studio/docs/change/20260803-161041-agent-creation-pipeline/prototype-generation-retrospective.md`
  records ten real runs: Agent/CLI preflight failures, four terminal no-artifact results, functional
  and visual drift, and convergence only after a fresh project received an immutable HTML baseline,
  brand evidence, and exact sidebar tokens.
- `/Users/tele/xjjk/ai-workspace/system-context/references/templates/OPEN-DESIGN-GENERATION-BRIEF-TEMPLATE.md`
  demonstrates grounded page/state/interaction input and `confirmed`/`inferred`/`unresolved` facts.
- Open Design 0.11.0's packaged daemon exposes the project, file, skill, agent, run, cancellation,
  and artifact operations required by the referenced workflow.

## Components and ownership

| Component | Existing stack/deliverable | Owns | Does not own |
|---|---|---|---|
| Bruce main workflow | `skills/bruce/SKILL.md` | Predicate-based selection of prototype capability | Open Design execution or mandatory UI stages |
| Prototype writer | `skills/write-prototype/` | Grounding bundle, readiness/preflight requirements, run and effective-output policy, independent artifact checks, provenance | Product decisions, MCP installation, host execution, final UI code, gate verdicts |
| Codex host | Existing host tools | MCP/app/file execution and actual tool responses | Bruce business readiness or completion decisions |
| Design Gate | Existing `skills/design-gate/` | Prototype candidate applicability and implementation-entry readiness | Generating or refining prototypes |
| Completion Gate | Existing `skills/completion-gate/` | Final implementation-to-prototype alignment evidence | Re-running design generation or making product decisions |

## Data and control flow

1. Bruce resolves a task contract and selects `write-prototype` only for an explicit or evidenced UI
   prototype need.
2. `write-prototype` classifies `greenfield` versus `existing-product-extension`. Existing-product
   work materializes `prototype-context/repository-ui-contract.md` plus a bounded baseline containing
   the exact host/entry/destination, unchanged layout and visual invariants, and evidence gaps.
3. Evidence is partitioned by authority: confirmed requirements own changed behavior; current
   runtime product evidence owns unchanged visual state; repository structure and revision evidence
   own implementation anchors; the last confirmed prototype owns refinement baseline; provider
   defaults fill only uncovered gaps. An unresolved conflict stops rather than silently redesigns.
4. Codex checks host capabilities and records an explicit Agent, host-reported auth/readiness,
   CLI/config compatibility, synchronized input readability, and visual-capture capability. A hard
   failure ends as `blocked-before-generation`; unavailable proof remains `partial` and limits claims.
5. Codex derives `<repository>-<change>-<surface>` as the base project id, creates or reuses only a
   matching project, synchronizes the context bundle, starts one run, and polls it to terminal.
6. Terminal provider status is mapped to an immutable effective-output fact:
   `blocked-before-generation`, `failed`, `canceled`, `no_artifact`, `no_effect`, or `generated`.
   Confirmation remains a separate lifecycle field. Non-generated results retain history but create
   no snapshot. After the first explicit no-op, another requested attempt uses deterministic
   `<base-project-id>-r<sequence>` lineage with parent ids and baseline SHA.
7. Codex imports changed output as untrusted content, validates Functional, Visual, Safety, and
   Provenance evidence independently, and stores an immutable generated snapshot plus manifest
   history. Exact token checks and viewport/region screenshot checks remain distinct.
8. The user confirms or corrects the result. Corrections are converted into positive and negative
   assertions before refinement. A governing repulled exact snapshot requires either
   `automated-clear + automated`, or `manual-confirmed + manual-only` with confirmation evidence that
   names the inspected snapshot. Pending, blocked, unavailable, and mismatched Visual combinations
   fail closed; manual evidence is never reported as automated Visual pass.
9. Design Gate requires the UI prototype candidate only when it governs implementation and blocks
   on missing grounding, confirmation, effective output, hashes, safety/provenance, or an unstated
   visual limitation.
10. Implementation uses real repository components and tokens rather than copying prototype code.
11. Completion Gate compares required visible states, interactions, invariants, and tokens against
   the confirmed artifact using current Codex App Chrome evidence from the actual implementation.

## Decisions

### Add a generic supporting capability with an Open Design provider contract

- Chosen: create `write-prototype`, with Open Design as the first explicitly defined provider.
- Rationale: prototype creation is a reusable delivery capability, while provider execution remains
  a Codex host concern. The name leaves room for later providers without inventing an adapter runtime.
- Rejected: add vendor-specific stages directly to Bruce; this would couple the main workflow to one
  tool and impose UI ceremony on unrelated work.
- Reversibility: remove the supporting skill and its optional gate candidate without changing other
  task profiles or Goal behavior.

### Keep MCP configuration outside the plugin

- Chosen: discover required logical capabilities from the current host tool surface at invocation.
- Rationale: the repository explicitly forbids a bundled MCP server and assigns execution to Codex.
- Rejected: declare `mcpServers`, ship a wrapper CLI, or start the desktop executable from Bruce.
- Reversibility: host MCP configuration can change independently of the plugin package.

### Persist a minimal provenance contract

- Chosen: store `prototype-brief.md`, `prototype-manifest.md`, and versioned generated/confirmed
  artifacts below the current change directory.
- Rationale: Design Gate needs stable facts and hashes, while generated and user-refined output must
  not be conflated. One manifest avoids a second readiness verdict.
- Rejected: store only an ephemeral preview URL or copy a full PM artifact/publishing model.
- Reversibility: the artifact tree is change-scoped and can be archived with existing design records.

### Ground existing-product extensions before generation

- Chosen: require a compact repository UI contract and at least one materialized baseline for
  `existing-product-extension`; keep it optional for greenfield work.
- Rationale: semantic phrases such as "use the current canvas" did not preserve Joytime's tree
  topology, connection entry, Drawer placement, or sidebar palette across real runs.
- Rejected: paste broad source/CSS context or treat the existing UI as optional inspiration. Both
  leave the provider free to redesign unchanged product surfaces.
- Reversibility: the context bundle is change-scoped and can downgrade to a source-grounded
  wireframe when runtime evidence is unavailable.

### Separate provider success from effective output

- Chosen: map provider status to `blocked-before-generation`, `failed`, `canceled`, `no_artifact`,
  `no_effect`, or `generated`, keep that effective-output fact immutable, and record confirmation in
  a separate lifecycle field.
- Rationale: four real `succeeded` runs returned no artifacts; provider terminal status therefore
  cannot be the workflow's artifact success signal.
- Rejected: resume the same completed session repeatedly. After one explicit no-op, a fresh
  deterministic refinement project carries the prior baseline and assertions.
- Reversibility: the lineage is manifest metadata and requires no provider-side scheduler.

### Keep acceptance dimensions and evidence strength independent

- Chosen: record Functional, Visual, Safety, and Provenance separately; accept only
  `automated-clear + automated` or exact-snapshot `manual-confirmed + manual-only` for a governing
  prototype, without claiming manual evidence is automated comparison.
- Rationale: provider Jury and static functional checks passed a prototype whose sidebar visibly
  diverged from the current product.
- Rejected: one provider score or user confirmation as a substitute for all four checks.
- Reversibility: additional automated screenshot evidence can later upgrade the evidence field
  without changing the confirmed artifact identity.

### Extend the existing gates instead of adding a prototype gate

- Chosen: add an optional UI prototype row and readiness view to Design Gate, then add prototype
  alignment to Completion Gate.
- Rationale: Bruce intentionally has one implementation-entry decision and one completion decision.
- Rejected: create a third prototype approval gate or parallel review record.
- Reversibility: the new candidate is additive and skipped with evidence when not applicable.

## Contracts

- [api-contracts.md](api-contracts.md#open-design-host-capability-contract)
- [api-contracts.md](api-contracts.md#prototype-input-contract)
- [api-contracts.md](api-contracts.md#prototype-artifact-contract)
- [api-contracts.md](api-contracts.md#gate-candidate-contract)

## Cross-cutting behavior

- Compatibility/versioning: additive supporting skill and additive Design Gate candidate; existing
  non-UI tasks keep the same route and can mark the candidate skipped. A user-supplied prototype is
  copied into the same change-scoped snapshot contract before it can satisfy the candidate.
- Authentication/authorization: Open Design BYOK, daemon access, and MCP configuration remain host
  and user responsibilities; Bruce stores no credentials.
- Failure and recovery: missing capabilities or hard preflight failures block before mutation;
  ambiguous `start_run` results are not replayed; running jobs are polled; no-artifact/no-effect
  results retain history without snapshot promotion; one no-op moves a requested retry to fresh
  deterministic lineage; cancellation needs explicit user intent; unsafe artifacts and invalid
  Visual state/evidence pairs are quarantined from governing confirmation.
- Observability: manifest records provider and Agent readiness, base/current/parent project ids, run
  and effective-output states, baseline and snapshot hashes, artifact count, four check results,
  visual evidence strength, user confirmation, cleanup history, and known gaps.
- Rollout/rollback: validate statically without a live Open Design run; rollback removes the additive
  skill, gate row, documentation, and tests. Host configuration is not changed by package rollout.

## Verification impact

- OD-01/OD-02 -> workflow, manifest, and capability-boundary contract tests.
- OD-03 through OD-08 -> brief, grounding-bundle, evidence-priority, and invariant contract tests.
- OD-09/OD-10 -> Agent, CLI/config, input, and visual-capability preflight contract tests.
- OD-11/OD-12 -> effective-output and fresh-lineage contract tests.
- OD-13/OD-14 -> four-check, visual evidence, confirmation, and gate contract tests.
- OD-15 -> feedback assertion and durable manifest-history contract tests.
- Full plugin validation covers packaging and cross-skill references; no live provider run is required.

## Open decisions

- None. The user confirmed that Bruce should borrow the integration mechanism without copying the
  surrounding ai-workspace business workflow.
