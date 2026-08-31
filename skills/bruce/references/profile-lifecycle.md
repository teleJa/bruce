# Profile lifecycle and confirmation

Bruce supports two static profile types that feed its verification loop:

- **Environment Profile**: reusable project/environment facts and capability references;
- **Requirement Verification Profile**: one requirement-scoped verification and repair strategy derived
  from an explicit `requirements.md` and confirmed Environment Profiles.

Neither Profile is a test result, execution ledger, Gate, or completion verdict.

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
- selected Skill/capability, evidence layer, deployment topology, or repair boundary.

A stale Profile cannot be used until updated and explicitly confirmed again.

## Source classes

Every material fact should identify one of:

```text
repository
project-document
user
runtime-preflight
external-system
```

User-provided facts are valid inputs only after the Profile is explicitly confirmed. Runtime preflight
still checks whether the fact is currently true.

## Secret boundary

Profiles may store safe references such as environment-variable names, secret-manager paths, account
aliases, and credential owners. They must not store passwords, API keys, cookies, JWTs, SSO tickets,
or complete provider responses.
