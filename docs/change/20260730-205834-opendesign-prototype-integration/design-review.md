# Design Review

- Objective: revise Bruce's optional Open Design prototype capability from real Joytime usage so an
  existing-product extension preserves repository visual authority, rejects incompatible visual
  plugins/design systems before generation, detects deterministic artifact drift, and remains
  grounded and auditable through refinement and cleanup.
- Scope: `write-prototype`, its templates and file/state contracts, Design Gate prototype readiness,
  Completion Gate alignment, regression tests, and local plugin refresh. Excludes Open Design host
  implementation, provider installation/configuration, a live generation run, and production UI.
- Implementation boundary: Bruce plugin skills, templates, documentation, and static contract tests
  governed by this change directory.
- Review mode: main-agent

## Candidate Matrix

| Candidate | Applicability | Delivery | Path | Repository-backed evidence |
|---|---|---|---|---|
| Requirement or clarification | required | generated | `requirements.md` | User-confirmed repair scope plus OD-01 through OD-19 map the original contract and the newly observed provider-theme override to observable evidence |
| Architecture | required | generated | `architecture.md` | Visual authority, generation-versus-visual selection, compatibility preflight, artifact checker, output mapping, lineage, and four checks propagate across writer and both gates |
| API/file contracts | required | generated | `api-contracts.md` | Brief/UI-contract fields, `visual-assertions.json`, actual run selections, manifest states/history, and gate candidate are cross-skill file contracts |
| Database/table design | skipped | skipped | none | Scope changes Markdown/HTML workflow artifacts only and introduces no database or application persistence schema |
| Implementation plan | skipped | skipped | none | The current native task plan defines design, contract tests, implementation, validation, plugin refresh, and completion review; no durable handoff was requested |
| Test design | skipped | skipped | none | OD-01 through OD-19 define deterministic evidence; checker fixtures cover clear and drifted artifact states, while no live provider E2E is in package acceptance |
| UI prototype | skipped | skipped | none | This task changes prototype-generation workflow guidance, not a user-facing application surface requiring its own governing prototype |

## Readiness

- Facts and consistency: pass. The prior retrospective remains the source for lifecycle regressions;
  the newly audited Joytime run records `designSystemId = ant`, `pluginId = design-system-ant`, while
  its artifact used `#d32029`, `248px`, `Joytime Studio`, and `JT` instead of the repository-evidenced
  `#df6f57`, `184px`, and `乐享时光`. Requirements, architecture, and file contracts now use the
  same ordered visual authority, selected/effective plugin fields, compatibility result, structured
  visual assertion sidecar, exact-token status, and manual-only limitation.
- Acceptance and verification coverage: pass. OD-07 through OD-15 directly cover missing existing
  host/entry/baseline, structure drift, visual token drift, unauthenticated default Agent, incompatible
  CLI config, succeeded-without-artifact, unchanged refinement/fresh lineage, absent browser evidence,
  feedback assertions, and provenance after cleanup. OD-16 through OD-19 cover visual authority,
  plugin/design-system compatibility, executable token/brand drift detection, and refusal of a
  manual-only override. Each material outcome has a contract or executable unit-test path plus full
  validator evidence; live Open Design generation remains explicitly out of scope.
- Risk and recovery coverage: pass. Bruce stays skills-only and performs no host mutation itself.
  Explicit Agent selection or a host-reported failure blocks before generation; an unavailable host
  diagnostic is truthfully `partial` rather than invented as clear. One explicit no-op moves only a
  requested retry to deterministic fresh lineage. Unsafe or provenance-invalid artifacts cannot be
  promoted, and local snapshot cleanup retains manifest history.
- Blocking findings: none. Self-review rejected making screenshots mandatory for greenfield or every
  provider run, and rejected claiming authentication can always be probed. Existing-product
  high-fidelity work still requires a materialized runtime/HTML/confirmed-prototype baseline;
  unavailable automation is carried as `manual-only` only after explicit user inspection. Runtime
  governs unchanged visible state, confirmed requirements govern changes, and source drift remains
  observable. Screenshot comparisons are viewport/region-specific; exact tokens remain exact.
  Implementation review also separated local pre-mutation readability from provider-side
  pre-run readability and moved `no_effect` SHA comparison after bounded artifact retrieval, avoiding
  two impossible execution-order requirements without changing the accepted scope. Independent
  Completion review then found that Visual readiness could fail open and that effective output mixed
  confirmation with provider results. The repaired design accepts only the two valid Visual
  state/evidence pairs, fails closed on every other pair, preserves `generated` as the immutable
  successful output fact, and records confirmation separately. The repair keeps visual plugins
  available to greenfield runs but makes an existing-product visual selection fail closed when it is
  incompatible or unproven. Product-specific values stay in each change's assertion sidecar rather
  than being hard-coded into Bruce.
- Existing-product visual authority and compatibility: clear. The ordered authority is recorded in
  the Skill, brief, UI contract, and API contract; generation capability is separate from visual
  plugin/design-system selection; the manifest retains selected/effective values, compatibility
  evidence, and `run_input_summary`; incompatible or unproven visual selection blocks before
  generation.
- Deterministic artifact visual assertions: clear. `visual-assertions.json` declares exact colors,
  dimensions, brand text, and forbidden tokens; the checker runs before manual confirmation, and
  `manual-only` cannot override `exact_token_assertions = blocked`.
- Evidence boundary: checked current Bruce workflow/gate/validator/test conventions, the original
  ai-workspace integration template, and Joytime's retrospective plus prototype manifest. Did not
  configure Open Design MCP, inspect secret-bearing Agent configuration, or run a live generation;
  those are host-owned and excluded from this package-contract revision.
- Smallest next action: implement OD-16 through OD-19 in `write-prototype`, its templates, Design
  Gate, the artifact checker, and tests; then run Completion Gate on the final diff.

## Verdict

Design: pass
