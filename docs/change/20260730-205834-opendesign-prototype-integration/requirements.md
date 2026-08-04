# Open Design prototype integration requirements

## Objective

Add an optional Bruce prototype-design capability that can drive an externally configured Open
Design MCP server, preserve design provenance, and connect a confirmed prototype to the existing
Design Gate and Completion Gate without importing ai-workspace product-delivery stages.

## Scope

Included:

- Add one independently discoverable `write-prototype` supporting skill and its templates.
- Route prototype work from Bruce only when a UI prototype is actually needed.
- Define the Open Design capability, existing-product grounding, input-context, preflight,
  run-lifecycle, effective-output, and artifact contracts.
- Add an optional UI prototype candidate to Design Gate.
- Add implementation-to-prototype alignment to Completion Gate.
- Update repository documentation, validator expectations, and contract tests.

Excluded:

- Bundling or installing an MCP server, CLI, app, scheduler, or host adapter.
- Running a real Open Design generation as part of Bruce package validation.
- Copying ai-workspace lanes, TAPD/COS publishing, product-stage orchestration, or fixed PM gates.
- Treating generated prototype code as production frontend implementation.

## Acceptance scenarios

### OD-01 Optional routing

- Given: a Bruce task has no UI prototype need.
- When: Bruce selects supporting capabilities.
- Then: `write-prototype` is skipped and no Open Design setup or run is required.
- Evidence: workflow-routing contract tests and the Bruce skill text.

### OD-02 Host capability boundary

- Given: a task explicitly requires an Open Design prototype.
- When: `write-prototype` starts.
- Then: it checks the required host-exposed Open Design capabilities and blocks with setup guidance
  if any are unavailable; it does not install, wrap, or silently replace Open Design.
- Evidence: prototype contract tests, plugin-manifest tests, and validator output.

### OD-03 Grounded generation input

- Given: the required Open Design capabilities are available.
- When: a prototype run is prepared.
- Then: the run receives a product brief plus repository-backed design/source evidence, distinguishes
  `confirmed`, `inferred`, and `unresolved`, and does not start while a material product decision is
  unresolved.
- Evidence: prototype skill and brief-template contract tests.

### OD-04 Safe run lifecycle

- Given: a grounded prototype input and a stable project id.
- When: Open Design generation is submitted.
- Then: one run is started, ambiguous submissions are not replayed, running status is polled, and
  cancellation occurs only on explicit user request. A terminal result without an artifact is
  handled as provider clarification/failure evidence rather than a generated prototype.
- Evidence: prototype lifecycle contract tests.

### OD-05 Confirmed artifact provenance

- Given: Open Design returns a generated artifact.
- When: Bruce imports it and the user confirms or refines it in Open Design Studio.
- Then: imported files are checked as untrusted input, generated and confirmed snapshots remain
  distinguishable, hashes and run identity are recorded, and only a user-confirmed artifact can
  govern implementation.
- Evidence: prototype artifact and manifest-template contract tests.

### OD-06 Gate integration

- Given: a prototype governs downstream UI implementation.
- When: Design Gate and Completion Gate run.
- Then: Design Gate requires and reviews the UI prototype candidate; Completion Gate compares the
  real UI with the confirmed prototype using current Codex App Chrome evidence.
- Evidence: gate contract tests and full plugin validation.

### OD-07 Existing-product grounding

- Given: a requested prototype extends an existing product surface.
- When: `write-prototype` prepares generation context.
- Then: it classifies the work as `existing-product-extension`, records the host surface, exact
  entry, destination surface, layout invariants, reuse and visual anchors, and materializes a
  baseline artifact. Missing exact entry, destination, or baseline blocks a high-fidelity claim or
  explicitly downgrades the result to a source-grounded wireframe.
- Evidence: grounding and context-bundle contract tests.

### OD-08 Structure and visual drift

- Given: current product evidence defines an unchanged interaction topology and visual language.
- When: a provider returns a functionally plausible redesign.
- Then: changed behavior follows confirmed requirements, unchanged structure and visual language
  follow current product evidence, and detectable layout or token drift fails its corresponding
  assertion even when provider quality scores pass.
- Evidence: evidence-priority, invariant, and independent-check contract tests.

### OD-09 Explicit Agent preflight

- Given: the provider default Agent may be unauthenticated or unavailable.
- When: a run is prepared.
- Then: the manifest records an explicitly selected Agent and the host-reported authentication or
  readiness evidence; a missing selection or reported failure is `blocked-before-generation`, not
  a design failure. A host that cannot expose readiness proof records `partial` and cannot claim
  preflight passed.
- Evidence: preflight contract tests.

### OD-10 CLI and input preflight

- Given: an Agent depends on a CLI/config contract and synchronized context files.
- When: preflight runs.
- Then: compatible version/config evidence and input readability are checked before project
  mutation when the host exposes them; a missing required field or unreadable baseline produces a
  locatable pre-generation blocker.
- Evidence: preflight and host-boundary contract tests.

### OD-11 Effective artifact state

- Given: a prototype attempt reaches a preflight or provider terminal result.
- When: its result is evaluated.
- Then: preflight, failed/canceled provider runs, zero artifacts, unchanged refinement, and valid
  changed output map respectively to `blocked-before-generation`, `failed`/`canceled`,
  `no_artifact`, `no_effect`, and `generated`. Confirmation is a separate lifecycle and never
  overwrites this output fact; non-generated states create or promote no snapshot.
- Evidence: effective-output state-machine contract tests.

### OD-12 Fresh refinement lineage

- Given: the first explicit refinement returns `no_artifact` or `no_effect`.
- When: the user requests another attempt for the same correction.
- Then: `write-prototype` uses a deterministic fresh `-r<sequence>` project, supplies the last valid
  artifact and complete change assertions, and records `parent_project_id`, `parent_run_id`, and
  `baseline_sha256`.
- Evidence: project-lineage contract tests.

### OD-13 Independent acceptance dimensions

- Given: an imported prototype has provider output and static checks.
- When: it is evaluated for confirmation.
- Then: Functional, Visual, Safety, and Provenance results are recorded independently and no result
  substitutes for another. Visual automation records target viewports and region/token assertions
  rather than relying on one global provider score. A governing prototype accepts only
  `automated-clear + automated` or an exact-snapshot `manual-confirmed + manual-only` pair;
  `pending`, `blocked`, `unavailable`, or mismatched pairs fail closed.
- Evidence: manifest and gate contract tests.

### OD-14 Manual-only visual evidence

- Given: browser or screenshot comparison is unavailable.
- When: static checks pass and the user explicitly confirms the rendered artifact they inspected.
- Then: the exact snapshot may become `confirmed` with `visual_evidence = manual-only`, while the
  workflow never claims automated Visual pass and preserves the fidelity limitation. This requires
  `visual_check = manual-confirmed` plus explicit confirmation evidence naming the inspected exact
  snapshot; `unavailable` alone cannot govern implementation.
- Evidence: visual-evidence and confirmation contract tests.

### OD-15 Feedback and durable provenance

- Given: the user corrects a generated prototype or requests old local snapshots be removed.
- When: another refinement or cleanup is prepared.
- Then: every correction becomes at least one positive and one negative regression assertion, and
  snapshot deletion does not remove project/run identity, output state, lineage, artifact count,
  hash summary, or result notes from manifest history.
- Evidence: feedback and manifest-history contract tests.

## Constraints

- Bruce remains a skills-only workflow plugin; Codex owns MCP and app execution.
- Open Design use must be explicit because a generation run can consume external model capacity and
  modify Open Design project state.
- Existing unrelated working-tree changes must remain untouched.
- The integration must remain additive and must not force prototype ceremony on non-UI work.
- Runtime screenshot/DOM evidence governs the current unchanged visual state when it conflicts with
  stale source evidence; confirmed requirements continue to govern changed behavior, and the drift
  plus source revision remains recorded.
- Exact tokens and dimensions use exact normalized assertions. Screenshot comparison records each
  viewport, region, and tolerance; no universal score can replace critical-region assertions.
