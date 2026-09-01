# Profile lifecycle and confirmation

Bruce supports two static profile types that feed its verification loop:

- **Environment Profile**: reusable user-confirmed development/test runtime topology, controlled operations, and capability references;
- **Requirement Verification Profile**: one requirement-scoped verification and repair strategy derived
  from an explicit `requirements.md` and confirmed Environment Profiles.

Neither Profile is a test result, execution ledger, Gate, or completion verdict. A confirmed Environment Profile may explicitly derive a project-local Environment Operation Manifest, but the Manifest is not a third Profile type or a new authorization source.

## Lifecycle

```text
draft -> needs_input -> ready_for_confirmation -> confirmed -> stale
                                      |                 |
                                  rejected          superseded
```

Both Profile types must carry:

```yaml
profile_revision: 1
content_hash: sha256:...
profile_state: draft|needs_input|ready_for_confirmation|confirmed|stale|rejected|superseded
confirmation:
  state: pending|confirmed|rejected
  confirmed_by: null
  confirmed_at: null
  confirmed_revision: null
  confirmed_content_hash: null
```

A newly generated Profile starts with `confirmation.state=pending`. It becomes consumable only when
`profile_state=confirmed`, `confirmation.state=confirmed`, `confirmed_revision` matches the current
revision, and `confirmed_content_hash` matches the current content.

Confirmation is an explicit user authorization of the exact Profile input. It is not `Design: pass`,
`Completion: pass`, a runtime preflight, or proof that a requirement has passed.

## Freshness

A Profile becomes `stale` and its confirmation resets to `pending` when an input that can change its
verification meaning changes. Examples include:

- requirements content or Acceptance criteria;
- referenced Environment Profile revision or content hash;
- account pool, initial-state predicate, Credential source, or authorization;
- selected Skill/capability, environment topology, operation set, evidence layer, deployment topology, or repair boundary.

A stale Profile cannot be used until updated and explicitly confirmed again.

## Source classes

Environment Profile facts are user-provided declarations and use `source.kind: user`. Repository,
project-document, runtime-preflight, and external-system observations belong to architecture/codebase
documentation, Requirement Verification Profiles, or Verification Run/Checkpoint instead.

A Requirement Verification Profile may use the broader evidence classes needed for requirement
mapping. Runtime preflight still checks whether a user-declared environment fact is currently true.

## Environment Operation Manifest lifecycle

`$environment-operations` may create a project-local `<environment-id>.operations.yaml` only from an
exact confirmed Environment Profile and a user-explicit request. The Manifest binds the source
`profile_id`, `profile_revision`, and `content_hash`; it selects only operation IDs and resolves full
operation definitions from that exact Profile. It becomes stale when the source Profile becomes stale
or those values no longer match.

Manifest generation and Manifest presence do not authorize build, start, stop, database mutation,
remote deployment, production access, or credential retrieval. Each operation retains its own risk
class, ownership boundary, and per-invocation authorization requirement. Runtime outcomes remain in
Verification Run/Checkpoint.

## Secret boundary

Profiles may store safe references such as environment-variable names, secret-manager paths, account
aliases, and credential owners. They must not store passwords, API keys, cookies, JWTs, SSO tickets,
or complete provider responses.
