# Verification and feedback loop

Use this policy while implementing and gathering evidence. `design-gate` makes the only design
readiness decision; `verify-completion` performs the final author-quality, evidence, and review checks
and returns the only completion decision.

## Verifiable acceptance scenarios

Give every behavior-bearing acceptance item a stable id and define:

- `Given`: concrete user/system state, data, permissions, and real dependencies.
- `When`: the user or system action under verification.
- `Then`: observable behavior and relevant data/state consequence.
- `Evidence`: the exact unit, integration, API, database, build, or real-browser check that proves
  each material outcome now.

Do not start behavior implementation while a material outcome has no feasible evidence path unless
the user explicitly accepts an exploratory or unverified boundary.

## Development feedback

For behavior changes, start with the smallest failing automated test or reproducible scenario when
feasible. Reproduce bugs before fixing them and establish a passing characterization baseline before
refactoring. When test-first work is genuinely impractical, record why and establish the nearest
repeatable check. Do not impose TDD on documentation-only, generated, or mechanical changes.

## Verification layers

Use the smallest sufficient evidence at each layer, but never substitute a lower layer for a required
higher one:

1. Unit/component checks prove local behavior.
2. Integration/API/database checks prove crossed process, service, persistence, or contract edges
   using real dependencies when acceptance requires them.
3. Real-use checks prove user-visible workflows and deployed/runtime wiring.

For user-visible Web behavior, use the Codex App Chrome capability with the user's current Chrome
session, login state, extensions, and real localhost or target service. Record the context, actions,
visible result, and supporting network/API/screenshot evidence when useful. If Chrome is unavailable,
report the missing evidence and do not claim acceptance passed. Do not silently substitute Playwright;
use it only for an established repository SOP or explicit user request.

## Continuous author feedback

During implementation, inspect each meaningful code or document diff before moving on. For code,
check affected call sites, boundaries, errors, security, concurrency, data integrity, and regression
coverage as relevant. For documents, check facts, terminology, contracts, cross-references,
acceptance coverage, placeholders, and links.

These checks are development feedback, not separately named gates and not completion evidence by
themselves. `verify-completion` repeats the necessary checks against the final state once, because
later edits can invalidate earlier observations.

## Independent review

Independence is a review mode inside `design-gate` or `verify-completion`, never a third verdict.
When required, use a fresh native subagent with no inherited author conversation. Supply objective,
acceptance, the final review target diff or immutable snapshot, raw evidence, and only necessary
constraints. Exclude author rationale, confidence, and proposed conclusion.

The reviewer may inspect repository facts and rerun safe checks but must not edit the reviewed work.
If required independence is unavailable, the owning gate returns `blocked`.

## Repair and regression loop

When verification fails, preserve the original scenario and evidence, then follow
[failure-recovery.md](failure-recovery.md). After an actual repair, inspect the changed code, rerun
the original failed scenario unchanged, and run related regressions. Update the acceptance evidence
after each action; do not replace a failure with a smaller passing check.

## Completion evidence

For each acceptance id, retain its scenario, required verification layer, current evidence, and
result. Natural-language claims, stale runs, mocked-only evidence for a real integration requirement,
or unit evidence for a user-visible flow keep that acceptance incomplete. Pass this evidence once to
`verify-completion`; callers do not create parallel verdicts from it.
