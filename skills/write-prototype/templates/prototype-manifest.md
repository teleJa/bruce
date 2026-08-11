# Prototype manifest

- provider: `open-design`
- selected_agent: <explicit agent id and version>
- selected_generation_skill: <explicit generation skill id and version>
- generation_skill_readiness: <clear, partial, or blocked plus reusable workflow/seed evidence>
- selected_visual_plugin: <explicit visual plugin id and version, or none>
- selected_design_system: <explicit design-system id and version, or none>
- selection_basis: <repository/runtime evidence or greenfield rationale>
- compatibility_check: <clear, partial, or blocked with evidence>
- effective_plugin: <exact plugin id passed to `start_run`, or none>
- effective_design_system: <exact design-system id passed to `start_run`, or none>
- run_input_summary: <exact Agent/skill/plugin/design-system/project/context identity>
- discovery_mode: <selective, full, or legacy>
- direction_selection: <skip, provider-capability, or legacy-unknown>
- context_hash: <none or sha256 of compact provider-facing context>
- context_files: <compact provider input plus local evidence references>
- sync_mode: <full, incremental, or legacy>
- base_project_id: <stable base project id>
- project_id: <current explicit project id>
- run_id: <provider run id>
- run_status: <pending, running, succeeded, failed, or canceled>
- provider_state: <queued, thinking, working, reconnecting, degraded, stalled_candidate, succeeded, failed, or canceled>
- observation_mode: <summary, event-incremental, or full-run-legacy>
- last_event_id: <none or provider event cursor>
- last_progress_at: <none or timestamp>
- effective_output_state: <pending, blocked-before-generation, failed, canceled, no_artifact, no_effect, or generated>
- artifact_count: <pending or integer>
- parent_project_id: <none or parent project id>
- parent_run_id: <none or parent run id>
- baseline_sha256: <none or refinement target digest>
- source_evidence: <brief, UI contract, baseline, and design/source evidence paths>
- generated_snapshot: <pending, none, removed, or `prototype/versions/<run-id>/generated/`>
- confirmed_snapshot: <pending, none, removed, or `prototype/versions/<run-id>/confirmed/`>
- confirmation_state: <pending, confirmed, or rejected>
- confirmation: <pending or explicit user signal, inspected exact snapshot identity, and timestamp>
- studio_url: <not returned or provider URL>
- preview_url: <not returned or provider URL>
- known_gaps: <none or explicit gaps and fidelity impact>

## Preflight

- preflight_status: <clear, partial, or blocked-before-generation>
- agent_readiness: <clear, partial, or blocked plus host-reported auth/readiness evidence>
- cli_compatibility: <clear, partial, or blocked plus CLI version/config evidence>
- input_readability: <clear or blocked plus every checked path>
- visual_capability: <available or unavailable plus browser/screenshot mechanism>

## Independent checks

- functional_check: <pending, clear, or blocked with assertion findings>
- visual_check: <pending, automated-clear, manual-confirmed, or blocked with findings>
- visual_evidence: <automated, manual-only, or unavailable>
- exact_token_assertions: <pending, clear, or blocked with findings>
- artifact_visual_checker: <path, version, contract path, and result>
- safety_check: <pending, clear, or blocked with findings>
- provenance_check: <pending, clear, or blocked with findings>

## Run history

Retain this history even when the user requests old local snapshot cleanup.

| Project / run | Agent / version | Parent / baseline | Provider status | Output state | Artifact count | Hash summary | Snapshot retention | Result notes |
|---|---|---|---|---|---:|---|---|---|
| <project / run> | <agent / version> | <none or parent / SHA> | <status> | <state> | <count> | <digests or none> | <retained/removed/not-created> | <message/findings> |

## Generated snapshot SHA-256

| File | sha256 |
|---|---|
| <none or relative path> | <none or digest> |

## Confirmed snapshot SHA-256

| File | sha256 |
|---|---|
| <pending or relative path> | <pending or digest> |

## Refinement diff

- Added: <none or paths>
- Changed: <none or paths>
- Deleted: <none or paths>
- Unchanged: <none or paths>

## Functional findings

- Positive assertions: <clear or failed ids and evidence>
- Negative assertions: <clear or failed ids and evidence>
- Host relationships and state transitions: <clear or findings>

## Visual findings

- Viewports: <none or dimensions>
- Exact token assertions: <pending, clear, or findings>
- Exact token assertions must run before manual confirmation; a failed assertion remains blocked and
  cannot be downgraded to `unavailable` or bypassed by `manual-only` evidence.
- Region-specific screenshot comparisons: <clear, unavailable, or findings plus tolerance>
- Manual inspection: <not used or user signal and exact artifact identity>

## Safety findings

- Path containment: <clear or findings>
- Remote resources: <clear or findings>
- Credentials and test accounts: <clear or findings>
- Real backend connections or addresses: <clear or findings>
- Executable or unexpected binary content: <clear or findings>

## Provenance findings

- Provider, Agent, project, run, and lineage: <clear or findings>
- Artifact count and effective output: <clear or findings>
- Context, baseline, and snapshot hashes: <clear or findings>
- Cleanup retention: <clear or findings>
