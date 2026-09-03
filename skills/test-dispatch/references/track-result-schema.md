# Track result and aggregation schema v1

Track Results record current execution evidence for one exact shared Scenario version. They are runtime
evidence inputs, not static Environment/Requirement Profile facts and not a Completion verdict.

## Canonical input

The values below are non-executable placeholders. The aggregator adds `overall_status` only after the
input passes validation.

```yaml
version: 1
scenario_id: CONTENT-CREATION-001
scenario_version: 1
profile_id: verification-profile
profile_revision: 1
profile_content_hash: "sha256:<64-hex-profile-hash>"
basis_revision: "<current-source-or-working-tree-revision>"
evidence_revision: "<unique-evidence-revision>"
required_tracks: [api, ui]
tracks:
  api:
    scenario_id: CONTENT-CREATION-001
    scenario_version: 1
    status: passed
    execution_mode: real-http
    data_namespace: "<unique-api-namespace>"
    allowed_paths: [<project-relative-api-test-path>]
    evidence_paths: [<project-relative-api-evidence-file>]
    modified_paths: []
    commands: [<declared-project-api-test-command>]
    browser_actions: []
    assertions: [job-succeeded, artifact-readback]
    blockers: []
    unverified_gates: []
    evidence_records:
      - {kind: command, ref: <api-evidence-ref>, status: verified}
      - {kind: readback, ref: <api-readback-ref>, status: verified}
    persistence_required: true
    authoritative_readback: [artifact-readback]
  ui:
    scenario_id: CONTENT-CREATION-001
    scenario_version: 1
    status: passed
    execution_mode: browser-provider
    data_namespace: "<unique-ui-namespace>"
    allowed_paths: []
    evidence_paths: [<project-relative-ui-summary>, <project-relative-ui-screenshot>]
    modified_paths: []
    commands: []
    browser_actions: [open-page, click-submit, observe-result]
    assertions: [visible-result, authoritative-readback]
    blockers: []
    unverified_gates: []
    evidence_records:
      - {kind: browser, ref: <ui-evidence-ref>, status: verified}
      - {kind: screenshot, ref: <ui-screenshot-ref>, status: verified}
      - {kind: readback, ref: <ui-readback-ref>, status: verified}
    persistence_required: true
    authoritative_readback: [authoritative-readback]
    browser_evidence:
      provider: ego-lite
      target: "<evidence-backed-page-target>"
      session: "<host-session-reference>"
      visual_scope: browser-smoke
      actions: [open-page, click-submit, observe-result]
      visible_result: "<visible-result-after-real-action>"
      capture_time: "<iso-8601-timestamp-with-timezone>"
      screenshot_path: "<project-relative-ui-screenshot>"
```

## Validation

- `required_tracks` contains unique `api` and/or `ui` values and every required track has one result.
- Each result repeats the exact top-level Scenario ID/version and uses the mode allowed for its track.
- API/UI namespaces must be distinct, safe lowercase namespaces and non-empty.
- Non-empty `allowed_paths` between tracks must not overlap or contain one another. An empty list means
  read-only; a non-empty `modified_paths` then fails validation.
- A `passed` result requires current `profile_id`, `profile_revision`, `profile_content_hash`,
  `basis_revision`, and `evidence_revision`, plus non-placeholder evidence paths, typed evidence
  records, assertions, no blockers or unverified gates, and the declared command/action.
- API `passed` requires authoritative readback when `persistence_required=true`. UI `passed` requires
  typed Provider/session/target/visible-result/screenshot evidence and real browser actions; layout
  scope additionally requires viewport, geometry, and overflow evidence.
- `blocked` requires at least one blocker. `failed` requires evidence or an assertion describing the
  reached failure.
- Credential-like fields, raw secret values, credential-bearing query parameters, and browser/API
  shortcuts are forbidden.
- Use `validate_evidence.py` to compare Scenario/Profile/basis/evidence revisions and the selected
  Provider/scope with the current run context. Static validation does not claim that a referenced
  artifact file or runtime target is available.

## Aggregation

Priority is fixed:

1. any required `failed` -> `failed`;
2. otherwise any required `blocked` -> `blocked`;
3. otherwise all required `passed` -> `passed`;
4. otherwise any required `executed` -> `executed`;
5. otherwise -> `designed`.

Aggregation preserves every track result and only adds derived `overall_status`. It rejects a supplied
mismatching `overall_status`, never returns `Completion`, `verdict`, or `approval`, and does not rewrite
historical evidence.
