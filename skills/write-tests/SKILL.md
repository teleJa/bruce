---
name: write-tests
description: Use when acceptance is complex enough to need a persistent test design, including stateful workflows, retries, permissions, integrations, regressions, or multiple task-to-scenario mappings. Produce only the necessary test plan from actual acceptance and repository test capabilities.
---

# Write tests

Turn acceptance into concrete, executable verification scenarios.

## Inputs

- Task contract and acceptance criteria.
- An actual implementation plan when one exists.
- Current repository test frameworks, commands, fixtures, environments, and real dependency rules.
- Risk and known regression sources.

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
7. Separately inspect the document diff and check acceptance/requirement traceability, prerequisites,
   Given/When/Then observability, evidence-layer fit, real dependency semantics, regression coverage,
   omissions, placeholders, and links. Repair issues and return
   `Document self-review: pass|issues`. Flag D1 readiness review when the test design gates downstream
   work; do not invoke another supporting skill automatically.

## Output

Produce a test design with Given/When/Then/Evidence acceptance mapping, scenarios, prerequisites,
commands, known limits, and the document self-review verdict.

## Does not own

Do not create execution state, own the development sequence, approve a plan, invoke plan review, run
the whole workflow, or declare completion.
