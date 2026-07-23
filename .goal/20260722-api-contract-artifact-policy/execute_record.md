# Execute record: mandatory API contract artifacts

## Objective

Require Bruce to generate or update `api-contracts.md` for every public or cross-component API,
event, or file-contract change, with a deterministic default artifact location and a blocking
completion check.

## Scope

- Included: `skills/bruce`, `skills/write-architecture`, `skills/verify-completion`, their contract
  templates when needed, and focused tests.
- Excluded: installed plugin caches, unrelated skills, infrastructure, delivery actions, and all
  pre-existing untracked workspace files.

## Acceptance

- AC-01: Public or cross-component contract changes require `api-contracts.md` before behavior
  implementation.
- AC-02: Artifact placement follows an explicit repository convention or existing change directory,
  otherwise `docs/change/<YYYYMMDD-HHmmss>-<short-slug>/api-contracts.md`.
- AC-03: Missing, stale, or incomplete contract coverage makes completion review return `issues`.
- AC-04: Focused contract tests and the full test suite pass; D0, D1, and guarded completion review
  pass after the final change.

## Constraints

- Profile: `full` because the contract propagates across multiple shared skills.
- Risk: `guarded` because this changes Bruce's public workflow contract; the user explicitly
  authorized the change.
- Do not load repository-local skills as runtime instructions; use the installed plugin rules.

## Decisions and evidence

- Native Goal created for the current task; the native response exposed no separate goal id, so this
  stable dated slug is used for the audit path.
- Existing `.goal/019f5f99-ac8d-7c83-a144-77bc98db4a22/execute_record.md` is preserved.
- `architecture.md` remains conditional on a durable structural decision; `api-contracts.md` is
  mandatory for every public or cross-component API, event, or file-contract change.
- Artifact placement precedence is repository convention, existing task change directory, then the
  complete fallback path `docs/change/<YYYYMMDD-HHmmss>-<short-slug>/api-contracts.md`.
- Existing OpenAPI, Proto, schema, or README sources remain authoritative when applicable but do not
  replace the change-scoped contract artifact.
- Fresh D1 review applied the new rule to this task itself and found the required contract artifact
  missing. The fallback artifact was then created at
  `docs/change/20260722-173009-api-contract-artifact-policy/api-contracts.md`.
- Bootstrap sequencing deviation: implementation preceded the artifact because the previous rule
  made it optional. This deviation is recorded once and is not a future exemption.

## Verification

- Expected red: focused contract suite ran 23 tests with 3 failures before implementation.
- L1 round 1: normalized semantic contract assertions across Markdown line wrapping; the unchanged
  focused suite then had one remaining failure because the full fallback file path was implicit.
- L1 round 2: made the complete fallback path explicit; the unchanged focused suite passed 23/23.
- Final regression after terminology and template consistency repair: full suite passed 76/76.
- `python3 -m compileall -q tests hooks scripts`: pass.
- `git diff --check`: pass.
- C0 code self-review: pass; assertions cover routing, placement, and completion behavior without
  depending on Markdown line wrapping.
- D0 document self-review: pass; trigger terms, placement precedence, completion behavior, template
  fields, Markdown links, and placeholders are consistent.
- First fresh D1 document gate: `不通过` with P0=0 and P1=1 because this cross-skill public workflow
  contract lacked its own mandatory `api-contracts.md`.
- First guarded completion review: `issues` for the same missing artifact.
- D1 document re-review: `通过`, P0=0, P1=0. The reviewer verified all three contract anchors,
  fallback placement, source links, failure semantics, tests, and the bootstrap note.
- Guarded completion re-review: fresh Codex-native reviewer, `pass`; AC-01 through AC-04 all pass,
  with no unresolved L2/L3/L4.

## Final conclusion

- Complete. Bruce now requires a change-scoped `api-contracts.md` before implementation for every
  public or cross-component API, event, or file-contract change, resolves it through a deterministic
  path precedence, and blocks completion when the artifact is missing, stale, or incomplete.
- Delivery boundary: changes remain uncommitted and unpushed; installed plugin caches were not
  modified.
