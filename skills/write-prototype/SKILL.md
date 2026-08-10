---
name: write-prototype
description: Use when a user explicitly requests a UI prototype or repository-backed task evidence shows that a confirmed prototype must govern downstream UI implementation. Prepare grounded design context, drive an externally configured Open Design MCP run, preserve generated and confirmed artifact provenance, and defer readiness and completion to Bruce's existing gates.
---

# Write prototype

Create a change-scoped UI prototype only when the user explicitly requests a prototype or current
task evidence shows that a confirmed prototype must govern downstream UI implementation. A UI code
change, `full` profile, guarded risk, or Open Design availability does not trigger this skill.

Keep provider execution optional. Before an external generation run, require the user's explicit
Open Design selection because it can consume model capacity and change provider state. Do not select
a provider only because it is installed.

## Inputs

- Objective, scope, acceptance scenarios, constraints, profile, and risk from the task contract.
- The repository's current change directory and artifact convention.
- Confirmed page, role/permission, state, interaction, navigation, failure, and non-goal facts.
- Existing source evidence, design system, theme token, component, typography, icon, layout,
  screenshot, DOM, accessibility, HTML, and confirmed-prototype evidence as applicable.
- Current user feedback and the last valid artifact/run for refinement.
- The user's explicit Open Design selection before `start_run`.
- The document language rule in [document-language.md](../bruce/references/document-language.md).
- For a Chinese request, write natural-language artifact content in Simplified Chinese while
  preserving provider fields, paths, statuses, hashes, and other stable tokens.

## Artifact placement

Resolve the current change directory using the repository convention, then an existing task change
directory, then `docs/change/<YYYYMMDD-HHmmss>-<short-slug>/`.

Create or update:

- `prototype-brief.md` from [prototype-brief.md](templates/prototype-brief.md);
- `prototype-context/repository-ui-contract.md` from
  [repository-ui-contract.md](templates/repository-ui-contract.md) for existing-product work;
- `prototype-context/baseline/` for bounded screenshots, DOM/accessibility evidence, current HTML, or
  the last confirmed prototype that is actually supplied to the provider;
- `prototype-manifest.md` from [prototype-manifest.md](templates/prototype-manifest.md);
- `prototype/versions/<run-id>/generated/` for the first valid changed run result;
- `prototype/versions/<run-id>/confirmed/` for the exact artifact repulled after user confirmation.

A user-supplied prototype enters the same snapshot, hashing, checks, and manifest contract. An
external path or URL alone cannot govern implementation.

## Open Design host contract

Codex owns MCP, app, browser, file, hashing, and command execution. Resolve Open Design functions by
logical capability from the current host tool surface; do not require a fixed MCP server prefix.

Required capabilities:

- `list_projects`;
- `create_project`;
- `write_file`;
- `list_skills`;
- `list_plugins`;
- `list_agents`;
- `start_run`;
- `get_run`;
- `cancel_run`;
- `get_artifact`.

Optional capabilities are `search_files` and `get_file`. Their absence disables only the associated
inspection convenience.

Block before creating or changing an Open Design project when any required capability is not
callable. Report missing logical names and the smallest host action. Do not install or configure an
MCP server, launch a replacement daemon, or wrap Open Design behind Bruce. Do not silently substitute
hand-written HTML or another design tool.

## Surface grounding

Classify the target as `greenfield` or `existing-product-extension` before generation.

For `existing-product-extension`, materialize the repository UI contract and at least one baseline
artifact. Record the host surface, exact entry and source/selector anchor, destination surface and
lifecycle, layout invariants, reuse anchors, visual anchors, responsive behavior, evidence gaps, and
fidelity limit. Missing exact entry, destination surface, or baseline blocks a high-fidelity claim;
continue only after evidence is added or the user explicitly accepts a `source-grounded wireframe`.
Before generation, inspect the filled UI contract: placeholders, empty evidence/verification cells,
or visual anchors that omit applicable shell/layout, palette, typography, brand, and geometry block a
high-fidelity claim. A template heading alone is not grounded evidence.

Use these evidence rules in the brief, UI contract, and provider prompt:

- Confirmed requirements govern changed behavior.
- Current runtime screenshot or DOM evidence governs unchanged visible state; record the source
  revision and drift instead of silently choosing stale source styling.
- Repository source governs structural ownership and reusable implementation anchors.
- Repository theme/source governs reusable visual authority for unchanged shell, palette, typography,
  brand, spacing, dimensions, and geometry when it is evidenced.
- The confirmed prototype governs the refinement baseline.
- Provider and framework defaults may fill only uncovered gaps.

Stop on a conflict that changes scope or behavior authority. Do not redesign an unchanged surface to
make a new requirement easier to display.

### Visual authority and compatibility

For an `existing-product-extension`, use this strict order for every unchanged visible decision:

```text
confirmed requirements
  > current runtime screenshot/DOM for unchanged visible state
  > repository theme/source
  > confirmed prototype for refinement
  > provider/framework defaults only for uncovered gaps
```

This is a visual authority contract, not a prompt suggestion. Do not allow a provider default to
replace an evidenced shell, brand, palette, typography, spacing, dimensions, radius, or layout
relationship. Record exact token assertions in `prototype-context/visual-assertions.json` when the
contract has normalized values. Product-specific values belong in that change-scoped contract, not in
this generic skill.

Treat generation capability and visual policy as separate selections. A generation skill (for
example `artifacts-builder`) provides generation behavior; a visual plugin/design system (for
example `design-system-ant`) may inject theme, layout, or brand defaults. For existing-product work:

1. Record `selected_generation_skill`, `selected_visual_plugin`, `selected_design_system`, and the
   `selection_basis` from repository/runtime evidence.
2. Check whether the visual selection can override the repository UI contract and record
   `compatibility_check` with evidence. Missing or incompatible evidence is
   `blocked-before-generation`.
3. Record the exact `effective_plugin` and `effective_design_system` actually passed to `start_run`;
   do not silently default to `design-system-ant`.

Greenfield work may select a visual plugin/design system when its constraints are explicitly part of
the brief. A generation skill alone does not authorize a visual redesign of an existing surface.

Use `confirmed`, `inferred`, and `unresolved` for every fact that can change visible scope or
behavior. Material unresolved facts about scope, permission, state, navigation, interaction, or
acceptance block generation unless the user explicitly narrows the artifact to exploratory fidelity.
Never put credentials, tokens, cookies, test accounts, private keys, or real authenticated access in
context.

## Preflight

After explicit provider selection and before project mutation:

1. Resolve every required logical capability.
2. Use `list_skills`, `list_plugins`, and `list_agents` to select explicit ids; never rely on the
   provider's default Agent route.
3. Record `selected_agent`, host-reported `agent_readiness`, `cli_compatibility` with version and
   required config evidence, the selected generation/visual plugin/design-system ids and
   `compatibility_check`, local `input_readability` for every source file, `visual_capability`,
   and aggregate `preflight_status` in the manifest. Include a `run_input_summary` with the exact
   selections and synchronized context identities.
4. A missing Agent selection, reported authentication/readiness failure, incompatible required
   CLI/config, or unreadable input is `blocked-before-generation`.
   For existing-product work, an incompatible or unproven visual plugin/design system is also
   `blocked-before-generation`; do not treat it as a prompt-only warning.
5. When the host cannot expose Agent or CLI readiness proof, record `partial` and the missing proof.
   Do not claim preflight passed. Proceed only within an explicit fidelity and evidence boundary;
   any host-reported failure still blocks.

Screenshot capability may be unavailable without blocking greenfield generation. It limits Visual
evidence and may block an existing-product fidelity claim when no other sufficient baseline exists.

## Generation and effective output

1. Derive the base project id as `<repository>-<change>-<surface>`. Normalize to lowercase ASCII
   letters, digits, and hyphens; collapse and trim hyphens; cap the complete id at 100 characters.
   Pass the project id explicitly to every project-scoped call.
2. Call `list_projects`. Reuse the id only when its context matches this repository, change, and
   surface. A collision blocks; do not create a random replacement.
3. Create the project when absent. Synchronize the brief, UI contract, baseline, and minimum design
   context under `workflow-context/`, then verify the provider-side inputs are readable before
   `start_run` when the host exposes that check. For a refinement, validate the complete local
   brief/assertion patch before project mutation; then create/reuse the lineage project, synchronize
   provider context, and verify provider-side readability. Any step failure stops before `start_run`.
4. Call `start_run` once with the explicit project and Agent ids, generation skill, compatible
   effective visual plugin/design-system selection, and grounded prompt. Persist these exact inputs
   in `run_input_summary`. If submit
   success is ambiguous, halt without resubmitting and resolve the original run from provider facts.
5. Continue to poll `get_run` at a reasonable interval and report useful progress. Unchanged files
   do not prove a hang. Call `cancel_run` only after an explicit user request.
6. Map provider outcome to effective output rather than trusting terminal status alone:
   - preflight failure -> `blocked-before-generation`;
   - failed run -> `failed`, with no snapshot;
   - canceled run -> `canceled`, with no snapshot;
   - terminal success with `artifactCount == 0` -> `no_artifact`;
   - terminal success with artifacts -> retrieve the bounded candidate, then map an unchanged
     refinement target SHA-256 to `no_effect` or validated changed artifacts to `generated`.

Neither state creates or promotes a snapshot: `no_artifact` and `no_effect` retain only evidence.
Preserve the Agent message and run history. After the first explicit refinement no-op, a
user-requested next attempt must use deterministic `<base-project-id>-r<sequence>` lineage,
truncating the base before the suffix when necessary and using the smallest unused positive sequence
from manifest history. Supply the last valid artifact and complete change assertions, and record
`parent_project_id`, `parent_run_id`, and `baseline_sha256`. Do not resume the same completed session
again for that correction.

## Artifact checks and confirmation

For terminal success with `artifactCount > 0`, call `get_artifact` with the explicit project id and
bounded import size. Treat all returned content as untrusted. Reject path escapes, executable or
unexpected binary content, credentials, real backend connections or addresses, remote resources,
and references outside the imported boundary. Compute the refinement target SHA-256 before assigning
`no_effect` or `generated`.

Record these dimensions independently; one must not substitute for another:

- Functional: required topology, pages, states, transitions, positive assertions, and negative
  assertions are present in the correct host relationship.
- Visual: layout, hierarchy, density, responsive behavior, and evidenced selector/token assertions
  match the baseline. Exact normalized tokens are exact checks. Screenshot checks record each
  viewport, critical region, and region-specific tolerance; one global provider score is insufficient.
- Safety: path, resource, credential, backend, executable, and binary checks are clear.
- Provenance: provider/Agent/version, project/run/parent ids, artifact count, hashes, snapshots, and
  context evidence agree.

When `visual-assertions.json` is present, run
`scripts/validate_prototype_artifact.py` from the Bruce plugin root against the
bounded artifact before assigning a Visual state or accepting manual confirmation. It must check
exact normalized colors, dimensions, required brand text, and forbidden tokens/strings. A failed
exact assertion sets `exact_token_assertions = blocked` and `visual_check = blocked`; provider
success, a provider score, or manual-only confirmation cannot override it. `manual-only` fills only
the screenshot-comparison gap after deterministic assertions are clear.

A terminal `succeeded` result has no artifact when its count is zero; preserve the provider's agent
message and record no generated snapshot. A Jury or other provider score, must-fix count, terminal
success, or static Functional pass cannot override another failed dimension. Store only valid changed
output under the immutable generated path and record every file SHA-256.

Show the Studio/preview URL when returned and wait for explicit user confirmation or correction. If
browser or screenshot comparison is unavailable, explicit user inspection of the rendered exact
artifact may set `visual_check = manual-confirmed` with `visual_evidence = manual-only`; this does not
mean automated Visual pass. Record the inspected exact snapshot in confirmation evidence. Automated
Visual readiness uses `visual_check = automated-clear` with `visual_evidence = automated`.

Only `automated-clear + automated` or `manual-confirmed + manual-only` may govern implementation,
and the latter is valid only after deterministic exact-token assertions are clear.
Pending or blocked Visual checks, unavailable Visual evidence, and every mismatched pair cannot
govern. Do not convert `unavailable` to `manual-only` without explicit exact-snapshot inspection.

Before any refinement, convert each confirmed user correction into at least one positive and one
negative regression assertion in the brief. Do not start refinement until the assertions and
unchanged invariants are synchronized with the baseline.

After confirmation, repull the same explicit project, rerun Safety and Provenance checks, store the
exact result under the confirmed path, and record added/changed/deleted files and SHA-256. Only a
confirmed snapshot with `effective_output_state = generated`, `confirmation_state = confirmed`,
clear Functional, Safety, and Provenance checks, and one valid Visual pair can govern implementation.
Confirmation must never overwrite the effective-output fact.

Keep every run in manifest history. Deleting an old local snapshot at the user's request must not
delete its project/run identity, lineage, output state, artifact count, hash summary, result notes,
or snapshot-retention record.

Inspect final brief, UI contract when applicable, manifest, files, hashes, links, four checks,
confirmation, and evidence gaps. Return `Document check: clear|issues`. When the prototype will
govern implementation, tell Bruce that `design-gate` is required; do not invoke it automatically.

## Output

Return provider and Agent, preflight status, explicit base/current/parent project and run ids,
provider status, effective-output state, artifact count, Studio/preview URLs, brief/UI-contract/
manifest paths, generated/confirmed snapshot paths, four check results, Visual evidence strength,
confirmation state/evidence, known gaps, cleanup history, and `Document check: clear|issues`.

## Does not own

Do not make product decisions, install or configure host tools, create a Bruce MCP/CLI/app, publish
artifacts, implement production frontend code, approve the prototype, decide design readiness, or
declare delivery complete. Do not invoke another supporting skill automatically.
