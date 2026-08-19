# Artifact placement

Use one resolver for every persisted Bruce design artifact (`requirements.md`, `architecture.md`,
`api-contracts.md`, `table-design.md`, `plan.md`, `test-plan.md`, `design-review.md`, and prototype
artifacts).

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

## Configuration

The optional workspace configuration is:

```yaml
version: 1
artifacts:
  root: docs/change
```

The config file is always located at:

```text
<shared-direct-parent>/.bruce/config.yaml
```

`artifacts.root` may be relative or absolute. A relative value is resolved relative to the config file's
containing directory, never relative to the current working directory. The resolved directory is the
shared source of truth; participating repositories do not receive copied portions of the same design.

Invalid or unreadable configuration must be reported and the user asked to provide a path; do not silently
fall back to a different repository or ancestor.

## Cross-repository record

A cross-repository change package must identify its participating repositories, paths, ownership, and
verification boundaries in `architecture.md` and `plan.md`. A separate manifest is optional and should
only be added when the repository or user requests machine-readable discovery.
