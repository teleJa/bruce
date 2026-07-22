# Verification and feedback loop

Read this policy for any code change or runtime-behavior change.

## Verifiable acceptance scenarios

Give every behavior-bearing acceptance item a stable id and define:

- `Given`: concrete user/system state, data, permissions, and real dependencies.
- `When`: the user or system action under verification.
- `Then`: observable behavior and relevant data/state consequence.
- `Evidence`: the exact unit, integration, API, database, build, or real-browser check that can prove
  each `Then` now.

Tie scenarios to actual use, not only implementation details. Do not start behavior implementation
while a material `Then` has no feasible evidence path. Investigate the repository first; ask one
blocking question only when scope or acceptance truly cannot be resolved. An exploratory prototype
may leave an item unverified only when the user explicitly accepts that boundary.

## Development feedback

For behavior changes, start with the smallest failing automated test or reproducible scenario when
feasible, then implement to make it pass and refactor under green tests. For a bug, reproduce the
failure before fixing it. For a refactor, establish a passing characterization baseline first.

When test-first work is genuinely impractical, record why and establish the nearest repeatable check
before the risky change. Do not impose TDD on documentation-only, generated, or purely mechanical
changes.

## C0 code self-review

After code changes and before final scenario verification, perform a pass separate from writing:

1. Inspect the actual diff and affected call sites for omissions or unintended scope.
2. Check error paths, edge inputs, state transitions, resource cleanup, and compatibility.
3. Check security, permissions, concurrency, idempotency, and data integrity when relevant.
4. Check that tests exercise changed behavior and important regressions rather than merely passing.
5. Return `Code review: self-review`, `Verdict: pass|issues`, checks performed, and findings.

Repair issues and rerun C0. Any later code change invalidates the previous C0 result.

## Verification layers

Use the smallest sufficient evidence at each layer, but do not let a lower layer stand in for a
required higher layer:

1. Unit/component checks prove local behavior.
2. Integration/API/database checks prove crossed process, service, persistence, or contract edges
   using real dependencies when acceptance requires them.
3. Real-use checks prove user-visible workflows and deployed/runtime wiring.

For user-visible Web behavior, use the Codex App Chrome capability to reuse the user's current
Chrome session, login state, and extensions. Execute the actual `Given/When/Then` against the real
localhost or target service and record the URL/context, actions, visible result, and supporting
network/API/screenshot evidence when useful. If Chrome is unavailable, report the missing E2E
evidence and do not claim that acceptance passed. Do not silently substitute Playwright; use it only
for an established repository SOP or an explicit user request.

## Repair and regression loop

When verification fails:

1. Preserve the original failing scenario and evidence.
2. Classify the failure with L0-L4 and identify its dependency boundary.
3. Follow the class before any rerun:
   - L0: retry only an idempotent operation within its transient retry budget.
   - L1: make an actual correction; do not weaken acceptance or replace the failure with a smaller
     passing check.
   - L2: replan the affected dependency boundary before choosing new verification.
   - L3: pause the affected work and obtain the required business decision.
   - L4: freeze writes and retries inside the incident boundary; never replay the original scenario
     while external side effects or data/security state remain unknown.
4. Only for L1, rerun C0 after code changes, rerun the original failed scenario unchanged, then run
   the related regression set.
5. Update the acceptance-to-evidence mapping with current results.

An L1 repair round counts only after the original scenario and related regressions have been rerun.
After two unsuccessful L1 rounds, move the affected work to L2 instead of looping indefinitely.

## Completion evidence

For each acceptance id report its scenario, verification layer, current evidence, and result. A
natural-language claim, stale run, mocked-only evidence for a real integration requirement, or unit
test for a required user-visible flow does not satisfy completion. Required but unavailable evidence
keeps that acceptance incomplete.
