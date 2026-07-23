# API and event contracts: mandatory Bruce API contract artifacts

## mandatory-api-contract-artifact

- Change: `added`
- Provider: Bruce main workflow (`skills/bruce/SKILL.md`)
- Consumers: `write-architecture`, `verify-completion`, and Bruce delivery tasks that change public
  or cross-component contracts
- Authoritative source: [`skills/bruce/SKILL.md`](../../../skills/bruce/SKILL.md) and
  [`skills/write-architecture/SKILL.md`](../../../skills/write-architecture/SKILL.md)
- Compatibility: additive governance requirement; private implementation-only work is unchanged,
  while affected contract work gains a mandatory pre-implementation artifact
- Authentication/authorization: not applicable

### Request, event, or input

The task changes at least one observable public or cross-component contract, including an API,
route, method, RPC, event, file contract, request or response field, status or error semantic,
authentication or authorization rule, idempotency rule, compatibility rule, or version.

### Success result

Before behavior implementation begins, Bruce invokes `write-architecture` and generates or updates a
change-scoped `api-contracts.md`. The artifact identifies providers and consumers and covers the
changed shape or semantics, compatibility, authentication, errors, and verification.

An existing OpenAPI, Proto, schema, or README may remain authoritative and should be linked, but it
does not replace this change artifact.

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| Required artifact is absent before implementation | Blocking contract gap; implementation must not begin | Create the artifact, then resume from the contract boundary |
| Artifact exists but omits a material contract change | Completion returns `issues` | Update the same artifact and rerun D0, D1, and completion review |
| Change is purely private with no observable contract effect | Requirement does not trigger | Continue through the normal Bruce route |

### Verification

- Routing: `tests/test_workflow_routing.py::WorkflowRoutingContractTest::test_public_contract_change_requires_persisted_api_contract`
- Artifact rule: `tests/test_supporting_skill_contracts.py::SupportingSkillContractTest::test_api_contract_artifact_is_mandatory_and_has_a_default_location`
- Completion: `tests/test_completion_contract.py::CompletionContractTest::test_public_contract_requires_current_api_contract_artifact`

## contract-artifact-placement

- Change: `added`
- Provider: `write-architecture`
- Consumers: Bruce main workflow and contract authors
- Authoritative source: [`skills/write-architecture/SKILL.md`](../../../skills/write-architecture/SKILL.md)
- Compatibility: existing repository conventions and current change directories retain precedence
- Authentication/authorization: not applicable

### Request, event, or input

Resolve a location for `api-contracts.md` or an optional adjacent `architecture.md`.

### Success result

Resolve the artifact directory in this order:

1. Repository-documented convention for the current change.
2. Existing change directory for the current task.
3. Repository-root fallback `docs/change/<YYYYMMDD-HHmmss>-<short-slug>/`.

The complete fallback contract path is
`docs/change/<YYYYMMDD-HHmmss>-<short-slug>/api-contracts.md`.

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| User path conflicts with a repository convention | Repository convention wins | Resolve once from repository evidence |
| No convention or current change directory exists | Use the fallback path | Reuse the created directory for later artifacts |

### Verification

- Placement precedence and complete fallback path are asserted by
  `test_api_contract_artifact_is_mandatory_and_has_a_default_location`.

## completion-contract-coverage-gate

- Change: `added`
- Provider: `verify-completion`
- Consumers: Bruce main workflow and Goal-backed completion
- Authoritative source: [`skills/verify-completion/SKILL.md`](../../../skills/verify-completion/SKILL.md)
- Compatibility: strengthens guarded and critical completion evidence without changing native Goal
  state ownership
- Authentication/authorization: not applicable

### Request, event, or input

The completion reviewer compares the actual diff with the resolved `api-contracts.md` and its
contract-to-diff mapping.

### Success result

The task is eligible for `pass` only when the current artifact covers every material public or
cross-component contract change and all required D0/D1 reviews pass.

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| Artifact is missing, stale, or incomplete relative to the actual diff | Return `issues` | Repair the artifact and rerun affected reviews |
| Only OpenAPI, Proto, schema, or README evidence exists | Return `issues` until the change artifact exists | Link the authoritative source from `api-contracts.md` |

### Verification

- Completion blocking behavior is asserted by
  `test_public_contract_requires_current_api_contract_artifact`.

## Bootstrap sequencing note

This policy-introduction task began implementation before this artifact existed because the previous
Bruce contract treated `api-contracts.md` as optional. The fresh D1 review applied the new rule to
its own change, returned `不通过`, and required this artifact. This remediation is a one-time
bootstrap sequencing deviation, not an exception available to later tasks.
