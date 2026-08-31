# Artifact placement

Use one resolver for every persisted Bruce design artifact (`requirements.md`, `architecture.md`,
`api-contracts.md`, `table-design.md`, `plan.md`, `test-plan.md`, `design-review.md`, the `tasks/`
task-contract package, `checkpoint.yaml`, and prototype artifacts).

## Resolution order

1. Use a document path explicitly supplied by the user for this task.
2. For a cross-repository task, identify the participating repositories and compare their direct parent
   directories. Do not walk farther up the filesystem looking for another ancestor.
3. If all participating repositories have the same direct parent, look for `.bruce/config.yaml` in that
   parent. If it exists, resolve its relative `artifacts.root` from the directory containing the config.
   If `artifacts.root` is absent, use `docs/change` under that parent.
4. If the direct parent differs, ask the user where the shared design documents should be stored. Do not
   choose one repository, the current working directory, a higher ancestor, or a home directory.
5. For a single-repository task, use the repository's documented convention, then its `.bruce/config.yaml`,
   then `docs/change` under the repository root.

An existing task change directory may be reused only after the task context or the user identifies it;
its presence alone must not make an unrelated directory the source of truth.

Environment Profiles are project/environment-scoped reusable artifacts. Unless the user supplies a
path, place them under `<project-root>/.bruce/environments/<environment-id>.profile.yaml`; do not place
them inside an unrelated change directory. A Requirement Verification Profile is requirement-scoped
and belongs beside its `requirements.md` under `<change-dir>/verification-profile.yaml`. Both artifacts
carry revision and explicit user confirmation; their current execution results belong in a
Verification Run/Checkpoint.

## Configuration

The optional workspace configuration is:

```yaml
version: 1
artifacts:
  root: docs/change
verification:
  browser_provider: ego-lite
workflow:
  repair_loop:
    max_rounds: 5
  review:
    max_wait_seconds: 60
    max_no_progress_polls: 2
```

The config file is always located at:

```text
<shared-direct-parent>/.bruce/config.yaml
```

`verification.browser_provider` accepts `ego-lite` or `chrome` and defaults to `ego-lite`; Invalid values must be reported and must not trigger a silent fallback. `artifacts.root` may be relative or absolute. A relative value is resolved relative to the config file's
containing directory, never relative to the current working directory. The resolved directory is the
shared source of truth; participating repositories do not receive copied portions of the same design.

Invalid or unreadable configuration must be reported and the user asked to provide a path; do not silently
fall back to a different repository or ancestor.

## Cross-repository record

A cross-repository change package must identify its participating repositories, paths, ownership, and
verification boundaries in `architecture.md` and `plan.md`. A separate manifest is optional and should
only be added when the repository or user requests machine-readable discovery.

## Task package placement

A persisted implementation plan may add exactly one change-level `tasks/` directory beside `plan.md`
and one current `checkpoint.yaml` beside it. The task package is derived from the shared change
package; it is not copied into each participating repository. Task files hold frozen contracts, while
checkpoint state holds current progress and references evidence without copying evidence content.

### Workflow limits

`workflow.repair_loop.max_rounds` controls the Completion Gate repair loop only. The initial review
scan is round 0; a repair loop may run at most this many subsequent repair rounds. It must be an integer from 1 through 5. Generic L0/L1 failure-recovery retry budgets remain governed by
`references/failure-recovery.md` and are not silently widened by this setting.

`workflow.review.max_wait_seconds` and `workflow.review.max_no_progress_polls` bound asynchronous
reviewer polling. They must be bounded integers: `max_wait_seconds` is 1 through 60 and `max_no_progress_polls` is 1 through 2. After the configured number of no-progress polls,
stop polling the handle; if independent review is required and unavailable, the Completion Gate returns
`Completion: blocked`.

If `verification` is absent, use `browser_provider=ego-lite`. If `workflow` is absent, use the documented
defaults (`5`, `60`, and `2`). Invalid Provider or workflow values must be reported rather than silently
changed, widened, or ignored.
