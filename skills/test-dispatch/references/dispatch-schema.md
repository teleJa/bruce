# Test Dispatch request schema v1

Test Dispatch selects tracks for one exact shared Scenario version and produces bounded Task Packets.
It is an orchestration contract, not a model registry, browser runtime, API runtime, Verification Run,
or Completion verdict.

## Canonical shape

The values below are non-executable placeholders. Replace namespaces, paths, and the packet only after
the shared Scenario, repository evidence, and confirmed Profiles are available.

```yaml
version: 1
scenario_id: CONTENT-CREATION-001
scenario_version: 1
feature_area: content-creation
business_flow: select-topic -> generate-artifact -> reload-recovery
actor: regular-user
tracks:
  - track: api
    execution_mode: real-http
    data_namespace: "<unique-api-namespace>"
    allowed_paths: [<project-relative-api-test-path>]
    required_evidence: [request-summary, state-trace]
  - track: ui
    execution_mode: browser-provider
    data_namespace: "<unique-ui-namespace>"
    allowed_paths: []
    required_evidence: [final-url, visible-state, screenshot]
routing:
  required_capabilities: [reproducible-verification]
  functional_agent_profile: verifier
  resolver: bruce-functional-agent-resolver
  model_resolution:
    requested_profile: verifier
    configured_model: "<resolver-configured-model>"
    effective_model: "<resolver-effective-model>"
    fallback_used: false
    fallback_reason: null
    capability_status: resolved
    resolution_result: resolved
    source: built-in
  functional_packet: "<validated-bruce-v1-task-packet>"
  subagent_browser_access: forbidden
  visual_scope: browser-smoke
```

## Invariants

- `scenario_id` and `scenario_version` are copied from the shared Scenario and are immutable for the
  dispatch. The dispatch must select one or both unique tracks.
- API execution modes are `memory-application`, `real-http`, and `live-acceptance`; UI execution mode
  is `browser-provider`. A UI track always keeps real browser actions in the main Agent/host.
- Every selected track has a non-empty, safe lowercase, unique `data_namespace`. API/UI `allowed_paths`
  must not overlap or contain one another. An empty `allowed_paths` means the track is read-only and
  its `modified_paths` must remain empty.
- `required_evidence` is declared before execution. A track cannot be promoted to `passed` when the
  declared evidence or assertions are missing.
- `routing.functional_agent_profile` is one of Bruce's existing `inspector`, `implementer`, `verifier`,
  or `reviewer` Profiles. `resolver` and the full `model_resolution` record come from Bruce's shared
  resolver; this file never creates a private router.
- `functional_packet` must pass Bruce's v1 Task Packet validator and repeat the same
  `model_resolution`. `subagent_browser_access` is always `forbidden`; no packet may give a Subagent
  browser tools, task-space ownership, login state, Captcha handling, or human handoff control.
- Account, credential, environment operation, and evidence paths must reference confirmed
  Environment/Requirement Profiles. No secret value, raw authorization header, cookie, token, password,
  API key, or database URL is stored in a dispatch request.

## Failure handling

- Missing or stale Profile bindings, unavailable operations/capabilities/accounts, version mismatch,
  duplicate tracks, namespace/path conflicts, invalid resolver records, or an invalid Task Packet block
  dispatch.
- A failed or blocked track is preserved as its own result. Dispatch aggregation follows
  `failed > blocked > passed > executed > designed`; it never emits `Completion`, `verdict`, or
  `approval`.
- Repair creates a new bounded run/evidence revision while preserving the original Scenario version
  and failed evidence. A material Scenario change creates a new `scenario_version` instead of mutating
  prior evidence.

## Validation entry point

Use `scripts/validate_contract.py dispatch <path>` for deterministic static validation. The validator
only reads YAML and checks the Bruce resolver/Task Packet contract; it never calls a project command,
service, browser, database, model, or credential store.
