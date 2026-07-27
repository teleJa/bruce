# Test plan: defer profile routing

## Acceptance mapping

| Acceptance | Scenario | Verification layer | Evidence |
|---|---|---|---|
| PR-01 unresolved inspection is side-effect free | profile-unresolved | component | `python3 -m unittest tests.test_workflow_profiles -v` |
| PR-02 full requires structural evidence | full-positive-evidence | component | `python3 -m unittest tests.test_workflow_profiles -v` |
| PR-03 capability triggers are independent | independent-capability-routing | component | `python3 -m unittest tests.test_workflow_routing tests.test_execution_contract tests.test_supporting_skill_contracts -v` |
| PR-04 later facts re-evaluate only affected routing | scope-change-recheck | component | `python3 -m unittest tests.test_workflow_profiles -v` |
| PR-05 no unrelated workflow regression | repository-regression | integration | `python3 -m unittest discover -s tests -v` and `python3 scripts/validate_plugin.py` |

## Preconditions and real dependencies

- Repository files under `skills/`, `tests/`, and `README.md`.
- Python 3 standard-library `unittest`; no service, database, credentials, or browser required.

## State and intent matrix

| Pre-state | User/system intent | Expected behavior | Data consequence |
|---|---|---|---|
| Profile evidence incomplete | inspect repository | remain unresolved and read-only | no Goal or design artifact is created solely from uncertainty |
| One component, no propagation | implement local change | resolve standard | capability predicates are evaluated independently |
| Multiple evidenced components/contracts | coordinate topology | resolve full | profile records components, propagation, and evidence only |
| Any resolved profile with Goal intent or persistence need | preserve cross-turn execution | enter Goal execution mode | one native Goal and audit record |
| Any resolved profile with downstream-governing design | enter implementation | run Design Gate | one same-directory design review |
| Any resolved profile with complex acceptance | design verification | invoke write-tests | one persistent test plan |

## Scenarios

### profile-unresolved: uncertainty does not create workflow state

- Maps to: PR-01
- Type: regression
- Given: the user request is understood but repository inspection has not established component and
  contract boundaries.
- When: Bruce forms the provisional task contract.
- Then: profile is `unresolved`; only bounded read-only inspection is allowed; Goal, design review,
  test design, change-directory creation, and behavior implementation do not occur solely because of
  uncertainty.
- Evidence: assertions over `skills/bruce/SKILL.md` in `tests/test_workflow_profiles.py`.
- Required layer: component

### full-positive-evidence: full is an evidenced topology result

- Maps to: PR-02
- Type: happy
- Given: inspection proves multiple delivery components or cross-component contract propagation.
- When: Bruce resolves the profile.
- Then: the task contract names components, propagated contract or independent delivery boundary,
  and repository evidence; size, duration, and uncertainty are insufficient.
- Evidence: assertions over `skills/bruce/SKILL.md` in `tests/test_workflow_profiles.py`.
- Required layer: component

### independent-capability-routing: profile is not a master switch

- Maps to: PR-03
- Type: regression
- Given: a task has any resolved topology.
- When: Bruce selects Goal execution, Design Gate, and test design.
- Then: Goal execution depends on explicit Goal intent or a task-contract persistence/audit need,
  Design Gate depends on persisted downstream-governing design, and test design depends on acceptance
  complexity; no supporting skill treats `full` alone as sufficient.
- Evidence: assertions across workflow, execution, and supporting-skill contract tests.
- Required layer: component

### scope-change-recheck: correction happens before affected implementation

- Maps to: PR-04
- Type: edge
- Given: later repository facts change a profile or capability predicate.
- When: Bruce detects the scope change.
- Then: it corrects the task contract and re-evaluates only affected predicates before continuing
  affected behavior implementation, without requiring approval unless authority or business impact
  changes.
- Evidence: assertions over correction language in `tests/test_workflow_profiles.py`.
- Required layer: component

### repository-regression: plugin remains structurally valid

- Maps to: PR-05
- Type: integration
- Given: routing sources and contract tests are updated.
- When: the full unit suite and plugin validator run.
- Then: all tests pass and bundled skill metadata/resources remain valid.
- Evidence: command exit codes and test output from the current workspace.
- Required layer: integration

## Regression sources

- Eager `standard|full` classification before deep inspection -> `profile-unresolved`.
- `full` automatically triggering Design Gate, Goal, and test-design decision ->
  `independent-capability-routing`.
- Late profile correction after side effects -> `scope-change-recheck`.

## Limits

- These are textual workflow-contract tests; they prove the distributed skill policy is internally
  consistent, not that a language model will make every repository classification correctly.
- No Web or external runtime behavior changes, so Chrome evidence is not applicable.

## Self-check

- Every acceptance item maps to evidence.
- Every behavior scenario has concrete Given/When/Then and a feasible evidence path.
- Unresolved, resolved, and later-scope-change states are covered.
- Commands use the repository's available `python3` runtime.
