# API and event contracts: defer profile routing

## profile-resolution-v2

- Change: `changed`
- Provider: `skills/bruce/SKILL.md`
- Consumers: `skills/goal-execution`, `skills/design-gate`, `skills/write-tests`, Bruce
  task authors, and workflow contract tests
- Authoritative source: `skills/bruce/SKILL.md`
- Compatibility: intentional breaking workflow-policy cutover; remove profile-driven capability
  entry rather than supporting both policies
- Authentication/authorization: none

### Request, event, or input

```text
user request + applicable AGENTS.md + repository evidence
```

During bounded inspection, the task contract may contain:

```text
profile: unresolved
profile evidence: missing component or contract-boundary facts
```

A resolved full profile must contain:

```text
profile: full
components: <named component A>, <named component B or independently delivered component set>
propagated contract: <API/event/data/file contract and direction, or independently delivered boundary>
evidence: <repository paths, symbols, manifests, or ownership facts>
```

Capability inputs are evaluated separately:

```text
goal_required := explicit Goal request OR task contract requires continuous/cross-turn persistence
                 or an audit record
design_gate_required := a requirement, architecture, API contract, table design, implementation
                        plan, or test design will govern downstream implementation
test_design_required := acceptance matches write-tests complexity triggers
```

### Success result

```text
Before behavior implementation:
- profile is resolved to standard or full from repository evidence;
- unresolved caused no Goal, design-review, test-plan, or change-directory side effect;
- each capability is invoked or skipped from its own predicate;
- later scope changes re-evaluate affected predicates before implementation continues.
```

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| Component/contract evidence is incomplete | remain `unresolved`; continue bounded read-only inspection | inspection is repeatable and side-effect free |
| One isolated ambiguity remains after repository inspection | ask at most one blocking question | resume from collected evidence |
| Facts disprove a resolved profile | correct profile before affected behavior implementation continues | re-evaluate independent capability predicates |
| `full` lacks named components or evidence | invalid task contract; do not use profile to trigger capabilities | return to bounded inspection |

### Verification

- Provider: `python3 -m unittest tests.test_workflow_profiles tests.test_workflow_routing -v`
- Consumer: `python3 -m unittest tests.test_execution_contract tests.test_supporting_skill_contracts -v`
- Repository: `python3 -m unittest discover -s tests -v` and `python3 scripts/validate_plugin.py`
