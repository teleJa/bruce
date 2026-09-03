# API discovery boundaries

Discovery is read-only and project-grounded. The Agent traces a business flow through the narrowest
available evidence chain:

```text
route/controller/router
        -> service/use-case
        -> repository/data access
        -> Job/worker (when asynchronous)
        -> persistence authority/readback
```

The chain is an evidence map, not permission to edit any of these components.

## Boundary contract

### Route/controller/router

Use route/controller/router declarations and existing API tests to establish the exact HTTP method,
path, input decoding, response shape, status mapping, authentication middleware, and route-level
validation. A route declaration does not prove the business result is durable or that a Job is
finished.

### Service/use-case

Use service/use-case code and tests to establish business transitions, actor checks, validation,
duplicate/idempotency behavior, synchronous versus asynchronous handoff, and returned identifiers.
Do not derive an external endpoint, deployed version, or database durability from service code alone.

### Repository/data access

Use repository/data-access code and tests to establish fields read or written, ownership and
relationship constraints, transaction boundaries, uniqueness/idempotency constraints, and the
minimum facts required by a readback. Repository inspection is not permission to mutate records or
reset a shared database.

### Job/worker

Use Job models, worker code, status handlers, and existing tests to establish the identifier passed
to a poll, the observable status field, progress/failure mapping, retries, and the finite terminal
allowlist. `Job created` is an intermediate observation. Never invent a terminal status from a
framework default or stop polling because a response is merely successful.

### Persistence authority

Prefer a public API readback that is available to the authorized actor. A read-only database query
may be used only when the confirmed Environment Profile authorizes it and repository evidence
identifies the query boundary. Neither an in-memory object, create response, cache snapshot, nor
inferred table/column is authoritative for a required persistence assertion.

## Evidence table

For every used boundary, record:

| field | requirement |
| --- | --- |
| `boundary` | `route`, `service`, `repository`, `job`, or `persistence` |
| `source_ref` | Repository/document/test source; do not include secrets |
| `claim` | The exact behavior the source supports |
| `used_by` | Scenario step, assertion, or readback |
| `unknowns` | Missing/conflicting facts that block execution |

If two sources disagree about a route, status, permission, or persistence fact, preserve the conflict
and stop the affected scenario. Do not select the most convenient interpretation.

## Forbidden discovery shortcuts

- guessing an endpoint from a framework convention or neighboring route;
- guessing a command from a package manager or test framework;
- adding a new HTTP/database runtime, adapter, fixture, or test DSL to compensate for missing
  project evidence;
- changing business code, shared contracts, schemas, migrations, CI, or environment templates;
- using direct database writes or destructive resets to arrange a test state; or
- claiming persistence, permission, or Job completion from an HTTP status alone.
