---
name: write-tests
description: Use when acceptance crosses multiple component or contract boundaries; needs state, repeat use, retry, concurrency, partial failure, recovery, permission, or rollback coverage; requires real integration, deployment, runtime evidence, or multiple verification layers; or shares behavior scenarios or regression sources across tasks. Produce only the necessary persistent test plan from actual acceptance and repository test capabilities.
---

# Write tests

Turn acceptance into concrete, executable verification scenarios.

## Invocation decision

Apply the frontmatter trigger contract before behavior implementation. Do so for any resolved Bruce
profile; profile alone is neither necessary nor sufficient. When triggered, persist `test-plan.md`; inline
acceptance or Goal audit text is not a substitute. When no trigger applies, do not invoke this skill.
If Design Gate is independently required, it records the repository-backed test-design skip
in its candidate matrix; otherwise do not create a durable skip record.

## Inputs

- Task contract and acceptance criteria.
- An actual implementation plan when one exists.
- Current repository test frameworks, commands, fixtures, environments, and real dependency rules.
- Risk and known regression sources.
- The document language rule in [document-language.md](../bruce/references/document-language.md).

## Procedure

1. Map every behavior-bearing acceptance condition to a stable scenario id with concrete `Given`,
   `When`, `Then`, and `Evidence`. Each material `Then` must have a feasible evidence path.
2. For stateful behavior, build a compact state-by-intent matrix covering first use, repeat use,
   retries, concurrent actions, partial failure, history/current pointers, and recovery as relevant.
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
