---
name: test-dispatch
description: Dispatch one versioned API/UI verification scenario with isolated tracks, Bruce model routing, and fail-closed evidence aggregation.
---

# Test Dispatch

Use this Skill to coordinate one shared user-facing verification Scenario across an API track, a UI
track, or both. It selects a single `scenario_id + scenario_version`, consumes confirmed Environment
and Requirement Verification Profiles, creates bounded host/Subagent packets, and preserves each
Track Result for the Verification Run/Checkpoint and Completion Gate.

This is an orchestration contract, not a generic test runner. It does not invent project endpoints,
commands, fixtures, accounts, credentials, browser sessions, model routes, or Completion decisions.

Read the shared contracts before dispatching:

- [Scenario v1](references/scenario-schema.md)
- [Dispatch v1](references/dispatch-schema.md)
- [Track Result v1](references/track-result-schema.md)
- [Evidence and status](references/evidence-status.md)
- [Bruce Functional Agent packets](../bruce/references/functional-agent-contracts.md)
- [Bruce browser ownership](../bruce/references/browser-provider.md)

## Invocation boundary

Use this Skill only when the caller has an exact shared Scenario and a Requirement Verification
Profile that maps the relevant Acceptance IDs. Every Environment Profile referenced by the
Requirement Profile must be exactly confirmed (`profile_id`, `profile_revision`, and `content_hash`).
A pending or stale Profile, missing operation, missing account state, or unavailable capability blocks
the affected track; it never authorizes a guessed command or silent fallback.

The dispatch request must select `api`, `ui`, or `both` through one unique track list. The selected
tracks inherit exactly one Scenario version. A material Scenario change creates a new
`scenario_version`; it must not mix old and new evidence.

## Procedure

1. Validate the Scenario, including its actor, Environment Profile reference, execution modes,
   preconditions, API/UI step separation, namespaces, cleanup policy, persistence readback, evidence
   requirements, and static `designed` status.
2. Validate the Dispatch request. Check the selected track mode against the Scenario, allocate
   non-empty distinct namespaces, and reserve non-overlapping repository-relative `allowed_paths`.
   API and UI tracks must not write the same path or a parent/child path.
3. Resolve required Environment operations, account bindings, and runtime capabilities from the
   confirmed Profiles. Perform one minimal read-only preflight per required dependency before the
   first dependent batch. Keep an unavailable or unknown capability `blocked`/`unexecuted`.
4. Build one bounded Task Packet per delegated test concern. Use Bruce's existing `inspector`,
   `implementer`, `verifier`, or `reviewer` Profile and shared resolver; attach the resolver's
   `model_resolution` to the packet. Do not add a private router, a fifth Profile, or a model outside the Bruce registry. A fallback must remain visible as degraded and must not be reported as a distinct
   model proof.
5. For an API track, delegate only repository-bounded generation, inspection, or evidence review
   according to the selected Functional Agent Profile. API execution remains constrained by the
   project operation and the API Verification Track contract.
6. For a UI track, keep all real page actions in the main Agent/host using the configured Bruce
   Browser Provider. Never put `browser`, task-space ownership, login state, Captcha handling,
   upload control, or page clicks/inputs into a Subagent packet. A verifier may inspect already
   captured evidence, but cannot operate the page.
7. Store one immutable Track Result per selected track. Record its exact Scenario identity, mode,
   namespace, commands or real browser actions, assertions, evidence paths, modified paths,
   blockers, and unverified gates. Do not write runtime results back into Scenario or Profile facts.
8. Validate and aggregate the results with the deterministic scripts. Aggregation follows
   `failed > blocked > passed > executed > designed`; it preserves every track result and only adds
   `overall_status`. It never emits `Completion`, `verdict`, or `approval`.
9. Hand the aggregate to Verification Run/Checkpoint and Completion Gate with the current basis and
   evidence revisions. A passed Track Result is evidence, not final completion.

## Track selection and failure rules

- `api`: use `memory-application`, `real-http`, or `live-acceptance` only as explicitly declared.
  Memory/application evidence cannot be described as real HTTP, PostgreSQL persistence, or live
  acceptance. `Job created`, an HTTP 2xx, or an in-memory assertion is not a durable outcome.
- `ui`: use `browser-provider` only. The selected Provider must match `.bruce/config.yaml` and its
  capability preflight. Do not switch from `ego-lite` to `chrome`, downgrade `visual_scope`, or
  replace a failed page action with an API call.
- `both`: use distinct API/UI namespaces, evidence directories, and write scopes. The two results
  must repeat the same Scenario ID/version. A version mismatch or write-path conflict is `blocked`,
  even when one track passed.
- `failed` preserves the reached failure and evidence. `blocked` records a concrete blocker and
  unlock condition. Missing assertions/evidence is not passed; it remains `executed` or `blocked`.
  Repair creates a new evidence revision, then reruns the original failed Scenario and related
  regressions without rewriting historical evidence.

## Static validation entry points

From the Bruce repository, use read-only checks such as:

```sh
python3 skills/test-dispatch/scripts/validate_contract.py scenario path/to/scenario.yaml
python3 skills/test-dispatch/scripts/validate_contract.py dispatch path/to/dispatch.yaml
python3 skills/test-dispatch/scripts/validate_contract.py track-result path/to/track-result.yaml
python3 skills/test-dispatch/scripts/aggregate_track_results.py path/to/track-result.yaml
python3 skills/test-dispatch/scripts/validate_evidence.py path/to/track-result.yaml path/to/current-context.yaml
```

These scripts parse YAML and validate contracts only. They do not call a project command, HTTP
service, browser, database, model, or credential store.

## Output

Return a bounded dispatch evidence packet containing:

```yaml
schema_version: 1
status: completed|blocked|failed
output_type: task_evidence_packet|verification_packet|review_packet
scenario_id: FEATURE-AREA-001
scenario_version: 1
selected_tracks: [api, ui]
track_results: []
model_resolution: {}
preflight: []
blockers: []
evidence: []
next_action: none|retry-preflight|run-track|repair|wait-for-user
```

The packet is evidence for the caller. It must not contain secret values or terminal `Design`,
`Completion`, `verdict`, or `approval` fields.

## Does not own

- business-code, schema, migration, CI, or project test implementation;
- a generic HTTP/browser/database runtime, scheduler, or credential manager;
- Browser Provider selection, task-space ownership, login/Captcha/human handoff, or real page actions;
- Functional Agent registry/resolver changes, private model routing, or model availability claims;
- Environment/Requirement Profile confirmation or mutation;
- Verification Run/Checkpoint ownership or the single `Completion` decision.
