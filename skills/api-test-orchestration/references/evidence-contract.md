# API orchestration evidence contract

An API Track Result is evidence for one exact Scenario v1 identity and version. It is not a
Completion verdict, an Environment Profile fact, or a substitute for a browser acceptance track.

## Variable lineage

Record each cross-step value as a lineage entry in the test design or evidence summary:

| field | meaning |
| --- | --- |
| `variable` | Stable non-secret name used by later steps |
| `producer` | Earlier response field, fixture, precondition, or declared operation |
| `consumer` | Later request path/body, poll, assertion, cleanup, or readback |
| `validation` | Type, presence, ownership, namespace, and format checks |
| `sensitivity` | `non-secret` or `sensitive-reference`; never the secret value |

The lineage table does not create a new shared schema. Scenario v1 remains the source of truth for
step shape. A missing or ambiguous producer is a blocker; do not manufacture a variable or copy a
value from a UI action.

## Bounded polling

An asynchronous API Scenario uses an API `poll` step with:

- a discovered status request;
- unique non-empty `terminal_statuses`;
- `success_statuses` as a subset of that terminal allowlist;
- positive `timeout_seconds`; and
- positive `interval_seconds`.

The deadline bounds the number of attempts. Polling stops at a listed terminal state or the deadline;
there is no unbounded retry or open-ended sleep. `Job created`, an accepted response, or an HTTP 2xx
is not a terminal success. An unknown or malformed status is fail-closed and must be recorded as
`failed` or `blocked`, never silently treated as success.

## Assertion families

Apply only the families supported by the requirement and project evidence, but make applicability
explicit:

- **negative:** documented validation status/shape and no unintended durable side effect;
- **permission:** actor-specific denial, visibility/ownership boundary, and no unauthorized
  mutation; do not use an admin to prove a regular actor's access;
- **idempotency/duplicate:** documented replay, single-result, or conflict behavior plus an
  authoritative identity/count invariant;
- **retry/concurrency:** documented deduplication, conflict, winner, or post-conflict invariant;
- **recovery:** documented failure/retry behavior, only with authorized safe setup.

Never assert only “2xx”, “non-2xx”, “created”, or “response looked reasonable”.

## Authoritative readback

If `api.persistence.required` is true, the Scenario declares a non-empty `readback`. Prefer the
public API readback after successful terminal state. A read-only database query is allowed only by
an explicitly confirmed Environment Profile operation and repository evidence. It must prove the
required durable facts (for example identity, owner, relation, status, or content invariants), not
repeat an in-memory object or create response.

When the readback is stale, forbidden, unavailable, or ambiguous, keep the result incomplete or
blocked. Do not report `passed` merely because the create or Job request succeeded.

## Redacted evidence

Evidence may include mode, scenario identity/version, namespace, method, route template, status,
safe field names, variable names, state transitions, bounded-poll observations, account alias,
credential reference, and authoritative readback summary.

Evidence must not include raw authorization headers, cookies, passwords, tokens, API keys, database
URLs, credential-bearing query parameters, or secret response fields. Redact before persistence,
printing, checkpoint/Handoff generation, or final reporting. Use a stable alias/reference instead of
a secret value. Keep API `browser_actions` empty and list `modified_paths`; business-code changes
are outside this Skill's ownership.

## Status boundary

Use only Scenario/Track Result statuses `designed`, `executed`, `passed`, `failed`, and `blocked`.
`passed` requires all declared assertions, required evidence, actual declared test invocation,
no blockers or unverified gates, and required authoritative readback. If the mode, environment,
account, command, route, worker, or evidence authority is unavailable, use the appropriate blocked
or waiting path rather than silently changing the claim.
