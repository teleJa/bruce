# API and file contracts: Open Design prototype integration

## Open Design host capability contract

- Change: `added`
- Provider: Codex host plus an externally configured Open Design MCP server
- Consumers: `write-prototype`
- Authoritative source: Open Design 0.11.0 daemon MCP tool surface and `skills/bruce/references/plugin-boundary.md`
- Compatibility: additive; non-prototype tasks and hosts without Open Design remain usable
- Authentication/authorization: host-owned Open Design daemon/BYOK configuration; no credential is
  accepted or persisted by Bruce

### Request, event, or input

```text
Required logical capabilities:
  list_projects
  create_project
  write_file
  list_skills
  list_plugins
  list_agents
  start_run
  get_run
  cancel_run
  get_artifact

Optional logical capabilities:
  search_files
  get_file

Invocation rule:
  Resolve these capabilities from the current Codex host tool surface.
  Do not require a fixed MCP server prefix.
  Derive base_project_id as <repository-slug>-<change-slug>-<surface-slug>.
  Normalize each slug to lowercase ASCII letters, digits, and hyphens; collapse and trim hyphens;
  cap the complete id at 100 characters.
  For a fresh refinement after one explicit no-op, derive project_id as
  <base-project-id>-r<sequence>, truncating the base before the suffix when needed.
  Pass project_id explicitly to every project-scoped call.

Preflight record:
  selected_agent: explicit Agent id and version
  selected_generation_skill: explicit generation capability id
  selected_visual_plugin: explicit visual plugin id or none
  selected_design_system: explicit design-system id or none
  selection_basis: repository evidence or greenfield rationale
  compatibility_check: clear | blocked plus evidence
  effective_plugin: exact plugin id passed to start_run or none
  effective_design_system: exact design-system id passed to start_run or none
  run_input_summary: exact agent, skill, plugin, design-system, project, and prompt/context identities
  agent_readiness: clear | partial | blocked plus host-reported auth/readiness evidence
  cli_compatibility: clear | partial | blocked plus version and required config evidence
  input_readability: clear | blocked for every local context/baseline source before mutation and
    every provider-side synchronized input before start_run when that check is exposed
  visual_capability: available | unavailable plus browser/screenshot mechanism
  overall: clear | partial | blocked-before-generation
```

### Success result

```text
All required capabilities are callable before project mutation.
The selected Agent, generation capability, visual selection and every preflight dimension have
evidence; `partial` never becomes a claimed
preflight pass and limits fidelity/verification claims.
The provider's actual project/run/artifact responses remain authoritative.
```

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| Required capability missing | Prototype work is blocked with setup guidance | Recheck only after host configuration changes |
| Selected Agent is missing or host reports auth/readiness failure | `blocked-before-generation` | Select an available authenticated Agent or repair host auth before mutation |
| Existing-product visual plugin/design system is incompatible or compatibility is unproven | `blocked-before-generation` | Use a repository-compatible selection or no visual plugin; do not default to `design-system-ant` |
| Required CLI version/config is incompatible | `blocked-before-generation` with the reported field/version | Repair the host-owned provider config, then rerun preflight |
| Host cannot expose an Agent/CLI readiness proof | Preflight is `partial`; never claim it passed | Continue only within the recorded fidelity/risk boundary |
| Synchronized brief, UI contract, or baseline is unreadable | `blocked-before-generation` | Repair the exact input path before project mutation |
| Stable project id belongs to different context | Block on project collision | Do not reuse or create a random replacement |
| Open Design unavailable before submit | L0 connectivity failure | Retry within Bruce failure policy |
| `start_run` result is ambiguous | Halt without resubmitting | Resolve the original run from provider evidence |
| Run remains `running` | Continue polling and report progress | Do not infer a hang from unchanged files |
| Terminal result has no artifact | Effective output is `no_artifact`; preserve provider message and create no snapshot | First explicit no-op allows a requested retry through fresh deterministic lineage |
| User requests cancellation | Call `cancel_run` once | Never cancel only because the run is slow |

### Verification

- Provider: static contract test against required logical capability names.
- Consumer: skill-routing and no-fallback contract tests.

## Prototype input contract

- Change: `added`
- Provider: `write-prototype`
- Consumers: Open Design generation run and Design Gate
- Authoritative source: `prototype-brief.md` template plus repository/task evidence referenced by it
- Compatibility: additive, change-scoped Markdown file
- Authentication/authorization: must not contain credentials, cookies, tokens, or test-account secrets

### Request, event, or input

```text
prototype-brief.md:
  identity:
    change, target surface, frontend type, surface_classification, run objective, prior run
  context:
    product/requirement evidence
    design-system/tokens/component evidence when matching an existing UI
    source evidence and known gaps
  scope[]:
    entry state, actor/permission, goal, structure, actions, required states,
    navigation, explicit non-goals
  facts[]:
    status = confirmed | inferred | unresolved
    statement
    evidence
  assertions[]:
    id
    kind = positive | negative
    exact observable condition
    evidence method
  output:
    artifact type, entry file, required pages/states/interactions, static mocks
  visual_authority:
    confirmed requirements > current runtime unchanged state > repository theme/source >
    confirmed prototype refinement > provider/framework defaults for uncovered gaps
  fidelity_mode:
    high-fidelity | source-grounded wireframe | exploratory
  plugin_compatibility:
    selected_generation_skill, selected_visual_plugin, selected_design_system,
    selection_basis, compatibility_check, effective_plugin, effective_design_system,
    run_input_summary

prototype-context/repository-ui-contract.md for existing-product-extension:
  host_surface
  exact_entry including source symbol and selector
  destination_surface and lifecycle
  layout_invariants[]
  reuse_anchors[]
  visual_anchors[] with exact tokens when evidenced
  baseline_artifacts[] with sha256
  source_revision and runtime/source drift
  visual_viewports[] and region-specific tolerance when automated comparison is possible
  evidence_gaps[] and fidelity_limit

prototype-context/visual-assertions.json (for exact-token checks declared by an existing-product
contract):
  schema_version: 1
  exact_colors[]: {selector, value}
  exact_dimensions[]: {selector, property, value, unit}
  required_brand_text[]: {selector, value}
  forbidden_tokens[]: {selector?, value}

Evidence authority:
  Confirmed requirements govern changed behavior.
  Current runtime screenshot/DOM governs unchanged visual state; source anchors and revision remain recorded.
  The confirmed prototype governs refinement baseline.
  Framework/provider defaults fill only uncovered gaps.
```

### Success result

```text
Every material product fact is confirmed or explicitly accepted as exploratory.
No unresolved fact that changes scope, state, permission, or acceptance remains.
Existing-product work includes an exact entry, destination surface, layout/visual invariants, and at
least one materialized baseline, or is explicitly downgraded to a source-grounded wireframe.
Every user correction is represented by at least one positive and one negative assertion before
refinement.
```

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| Material fact is unresolved | Do not start generation | Obtain one user decision, then update the brief |
| Existing UI has no usable design evidence | Block high-fidelity generation | Gather current repository/browser evidence or explicitly narrow fidelity |
| Exact entry, destination, or baseline is missing | Block high-fidelity generation | Complete the UI contract or label the output source-grounded wireframe |
| Runtime and source evidence conflict | Runtime governs unchanged visual state; record source revision and drift | Stop only when the conflict changes scope/behavior authority |
| User feedback has no regression assertion | Do not refine yet | Add positive and negative assertions, then synchronize context |
| Existing-product visual plugin/design-system is incompatible or unproven | `blocked-before-generation` | Select a compatible plugin or explicitly downgrade to source-grounded wireframe |
| Secret or real backend access appears in input | Reject the input | Remove/sanitize it before retry |

### Verification

- Provider: brief-template contract test.
- Consumer: Design Gate readiness contract test.

## Prototype artifact contract

- Change: `added`
- Provider: Open Design through `write-prototype`
- Consumers: Design Gate, frontend implementation, Completion Gate
- Authoritative source: `prototype-manifest.md` and its referenced versioned files
- Compatibility: additive, change-scoped artifact; prototype code is never a production-code contract
- Authentication/authorization: imported output is untrusted and must not contain credentials or
  connect to real authenticated backends

### Request, event, or input

```text
prototype-manifest.md:
  provider: open-design
  selected_agent and preflight evidence
  base_project_id and current project_id
  run_id and provider terminal status
  effective_output_state: pending | blocked-before-generation | failed | canceled | no_artifact |
    no_effect | generated
  confirmation_state: pending | confirmed | rejected
  artifact_count
  parent_project_id, parent_run_id, and baseline_sha256 for fresh refinement
  source_evidence[]
  generated_snapshot: path + per-file sha256
  confirmed_snapshot: path + per-file sha256
  confirmation: explicit user signal and timestamp, or pending
  studio_url and preview_url when returned
  functional_check: clear | blocked with findings
  visual_check: automated-clear | manual-confirmed | pending | blocked with findings
  visual_evidence: automated | manual-only | unavailable
  exact_token_assertions: pending | clear | blocked with findings
  artifact_visual_checker: path, version, contract path, and result
  safety_check: clear | blocked with findings
  provenance_check: clear | blocked with findings
  known_gaps[]
  run_history[]: durable identity, lineage, output state, artifact count, hash summary, result notes,
    and snapshot-retention state

artifact paths:
  prototype/versions/<run-id>/generated/**
  prototype/versions/<run-id>/confirmed/**
```

### Success result

```text
Generated output is stored separately from the repulled user-confirmed output.
Only `generated` effective output with a changed target SHA creates a generated snapshot.
Confirmation is recorded separately and never overwrites the effective-output fact.
Functional, Visual, Safety, and Provenance checks remain independent.
Visual readiness accepts only `automated-clear + automated`, or `manual-confirmed + manual-only`
with explicit confirmation evidence naming the inspected exact snapshot. `pending`, `blocked`,
`unavailable`, and mismatched state/evidence pairs cannot govern implementation. Manual inspection
does not produce an automated Visual pass.
The manifest records sufficient identity, lineage, hashes, evidence strength, and retained history
to reproduce the selection after optional local snapshot cleanup.
```

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| Remote resource, real API, secret, or path escape found | Safety check is blocked | Sanitize/regenerate; do not promote the artifact |
| User has not confirmed the artifact | Status remains pending | Show Studio result and wait; do not enter implementation |
| Visual state/evidence pair is pending, blocked, unavailable, or mismatched | Artifact cannot govern implementation | Gather automated evidence or explicit exact-snapshot manual confirmation |
| Repull differs from generated version | Record per-file added/changed/deleted result | Treat repulled confirmed version as the next-run baseline |
| `artifactCount = 0` | Effective output is `no_artifact`; no snapshot | Preserve history; use fresh lineage after the first explicit no-op when another attempt is requested |
| Refinement target SHA-256 is unchanged | Effective output is `no_effect`; no snapshot | Preserve history; use fresh lineage after the first explicit no-op when another attempt is requested |
| Screenshot/browser evidence is unavailable | Visual automation remains pending and evidence is `unavailable` or `manual-only` | Require explicit user inspection for confirmation and retain the limitation; exact token assertions still run |
| Exact token assertion fails | `visual_check = blocked`; manual-only cannot override | Repair artifact or update a confirmed contract before retry |
| Provider score passes but a layout/token assertion fails | Corresponding Functional or Visual check is blocked | Refine against the failed assertion; provider score cannot override it |
| Old local snapshot is deleted by user request | Mark snapshot retention as removed; keep run history and hash summary | Never erase audit identity or lineage from the manifest |
| Artifact exceeds bounded import size | Block import and report limit | Narrow artifact include scope before a new explicit run |

### Verification

- Provider: manifest-template and artifact-policy contract tests plus
  `scripts/validate_prototype_artifact.py` for deterministic visual drift.
- Consumer: Design Gate candidate and Completion Gate alignment tests.

## Gate candidate contract

- Change: `changed`
- Provider: `design-gate` and `completion-gate`
- Consumers: Bruce main workflow and UI implementation tasks
- Authoritative source: `skills/design-gate/SKILL.md`, its template, and `skills/completion-gate/SKILL.md`
- Compatibility: additive candidate; non-UI and non-governing prototypes remain explicitly skipped
- Authentication/authorization: not applicable

### Request, event, or input

```text
Design Gate candidate:
  UI prototype
  applicability: required | skipped
  delivery: generated | skipped
  path: prototype-manifest.md or none
  evidence: task and repository facts

Delivery rule:
  generated means the candidate is materialized in the current change directory.
  A user-supplied prototype must be imported, hashed, and recorded by the same manifest contract;
  it is not represented by an ephemeral external path or URL.

Completion alignment:
  confirmed prototype identity
  mapped pages/states/interactions, positive/negative assertions, layout invariants, and visual anchors
  current Codex App Chrome evidence against the real UI
```

### Success result

```text
Design: pass only when a governing prototype is separately confirmed, grounded for its surface
classification, retains `effective_output_state = generated`, is safe and provenance-clear, and has
either `automated-clear + automated` or exact-snapshot `manual-confirmed + manual-only` Visual
evidence. All pending, blocked, unavailable, and mismatched Visual combinations fail closed.
Completion: pass only when the implemented visible behavior has sufficient current alignment evidence.
```

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| Governing prototype candidate omitted | Design: blocked | Add the complete candidate row and re-review |
| Prototype changed after Design Gate | Design verdict is stale | Rerun Design Gate before affected implementation |
| Real UI lacks required Chrome evidence | Completion: issues | Gather current evidence; do not substitute a unit test |

### Verification

- Provider: Design Gate matrix and completion-alignment contract tests.
- Consumer: full Bruce unit suite and static plugin validator.
