---
name: write-tests
description: Use when acceptance crosses multiple component or contract boundaries; needs state, repeat use, retry, concurrency, partial failure, recovery, permission, or rollback coverage; requires real integration, deployment, runtime evidence, or multiple verification layers; shares behavior scenarios or regression sources across tasks; or changes a stateful UI with repeat entry, mutable data, or lifecycle-sensitive interaction. Produce only the necessary persistent test plan from actual acceptance and repository test capabilities.
---

# Write tests

Turn acceptance into concrete, executable verification scenarios.

## Artifact placement

When persisting `test-plan.md`, use [artifact-placement.md](../bruce/references/artifact-placement.md).
A cross-repository test plan remains one shared artifact and records per-repository commands and evidence
boundaries inside the plan.

## Invocation decision

Apply the frontmatter trigger contract before behavior implementation. Do so for any resolved Bruce
profile; profile alone is neither necessary nor sufficient. A required persisted implementation plan
always triggers this skill. When triggered, persist `test-plan.md`; inline acceptance, plan verification
bullets, or Goal audit text are not substitutes. When no trigger applies, do not invoke this skill.
If Design Gate is independently required, it records the repository-backed test-design skip
in its candidate matrix; otherwise do not create a durable skip record.

For UI changes, invoke this skill when any of the following applies:

- a modal, drawer, picker, tab, editor, or paginated/list surface can be closed and entered again;
- displayed or selectable data can change while the surface is closed or between entries;
- the interaction has cache, refresh, reset, re-fetch, prefill, draft, or selection-retention semantics;
- cancel, confirm, save, retry, asynchronous loading, pagination, filtering, or dependent controls
  create meaningful state transitions;
- the reported defect involves stale state, duplicate interaction, reopening, or recovery; or
- acceptance requires a real browser or crosses a component, API, or service boundary.

Do not invoke this skill for a copy, icon, color, or layout-only change with no changed state,
data, interaction, or verification boundary, unless the user or an existing test plan explicitly
requires it. When multiple UI triggers apply, create one compact plan rather than one plan per trigger.

## Inputs

- Task contract and acceptance criteria.
- The task contract's proportional `visual_scope` when user-visible Web behavior is in scope.
- An actual implementation plan when one exists.
- Current repository test frameworks, commands, fixtures, environments, and real dependency rules.
- Risk and known regression sources.
- The document language rule in [document-language.md](../bruce/references/document-language.md).

## Procedure

1. Map every behavior-bearing acceptance condition to a stable scenario id with concrete `Given`,
   `When`, `Then`, and `Evidence`. Each material `Then` must have a feasible evidence path.
   For `chrome-smoke` or `chrome-layout`, make the visible state explicit; for `chrome-layout`,
   include the relevant layout invariant and interaction evidence rather than only DOM text.
2. For stateful UI behavior, build a compact lifecycle matrix covering first entry, close and reopen,
   data changes while closed, cancel and reopen, confirm and reopen, and failure and retry as
   relevant. State the expected fresh observable result and state-retention semantics; do not encode
   a required implementation mechanism such as a network request or cache bypass.
   For other stateful behavior, cover first use, repeat use, retries, concurrent actions, partial
   failure, history/current pointers, and recovery as relevant.
3. Define happy, edge, error, integration, permission, and regression scenarios only where they add
   real coverage. Tie them to actual user/system use rather than only implementation detail.
4. Use real repository commands and environments. Distinguish unit fixtures from verification that
   requires a real database, browser, service, or external dependency.
5. When a plan exists, map scenarios to its task ids without requiring every non-feature task to
   have a synthetic scenario.
6. Persist `test-plan.md` using [test-plan.md](templates/test-plan.md).
7. Write natural-language fields in the user's language, using Simplified Chinese for a Chinese
   request; keep `Given`/`When`/`Then`/`Evidence` and other stable tokens unchanged.
8. Inspect the document diff and check acceptance/requirement traceability, prerequisites,
   Given/When/Then observability, evidence-layer fit, real dependency semantics, regression coverage,
   omissions, placeholders, and links. Repair issues and return `Document check: clear|issues`.
   When the test design will govern implementation, tell Bruce that `design-gate` is required; do
   not invoke it automatically.

## Output

Produce a test design with Given/When/Then/Evidence acceptance mapping, scenarios, prerequisites,
commands, known limits, and the document-check result.

## Does not own

Do not create execution state, own the development sequence, approve a plan, invoke plan review, run
the whole workflow, or declare completion.
