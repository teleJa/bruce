# Data design: <change name>

## Objective and repository conventions

- Persistence outcome: <what behavior needs storage>
- Existing schema/migration evidence: <paths>
- Conventions followed: <ids, logical references (no database foreign keys), types, timestamps, naming, migration tool>

## Scenario derivation

### Scenario <n>: <intent>

- Pre-state: <concrete rows/values>
- Action: <write/read operation>
- Post-state: <rows/columns changed>
- Read path: <filters, joins, ordering>
- Transaction/idempotency: <boundary and retry behavior>
- Failure recovery: <rollback or compensation>

## Tables and changes

### `<table>`

Purpose: <scenario-backed responsibility>

| Column/change | Repository-native type/constraint | Scenario or decision |
|---|---|---|
| `<column>` | `<actual type and constraint>` | <scenario n> |

## Constraints and indexes

Database-level foreign keys are prohibited. Do not use `FOREIGN KEY` constraints or `REFERENCES` clauses;
record relationship validation, orphan handling, and deletion behavior in the lifecycle/invariant sections.

| Constraint/index | Columns/predicate | Scenario/read path protected |
|---|---|---|
| `<name>` | `<definition>` | <scenario n> |

## Lifecycle and concurrency invariants

- <invariant> -> <database and/or service enforcement>

## Migration and compatibility

- Forward migration: <steps>
- Existing-data/backfill behavior: <steps>
- Compatibility window: <old/new readers and writers>
- Rollback or compensating recovery: <steps>

## Verification impact

- <scenario/invariant> -> <migration, repository, integration, or production-safe check>

## Open decisions

- <authority needed, or none>
