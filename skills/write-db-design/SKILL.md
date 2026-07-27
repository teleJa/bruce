---
name: write-db-design
description: Use when a task actually needs schema or persistence design. Derive tables, columns, constraints, indexes, lifecycle behavior, migration impact, and verification from real usage scenarios and the target repository's existing database conventions; do not impose project-specific schema rules on other repositories.
---

# Write database design

Derive persistence design from behavior and current repository facts.

## Inputs

- Task objective, scope, acceptance, lifecycle rules, and data-risk constraints.
- Existing schema, migrations, models, repositories, queries, and project database conventions.
- Key read/write scenarios, including retries, concurrency, history, and deletion/retention.
- A requested output location when the design must be persisted.

## Procedure

1. Confirm that the task needs schema or persistence design. If it does not, return `not needed`
   with repository-backed evidence to Bruce for the same-directory `artifact-review.md`; do not
   create a separate exemption file or write the decision to `execute_record.md`.
2. Inspect repository conventions before choosing identifiers, foreign keys, types, timestamps,
   migration style, naming, or index patterns. Never import conventions from another project.
3. For each important scenario, record pre-state, action, post-state, data consequences, read path,
   transaction boundary, idempotency, and failure recovery.
4. Derive tables, columns, constraints, indexes, and lifecycle invariants from those scenarios. Map
   every non-obvious field or index back to a scenario or decision.
5. Describe forward migration, compatibility, backfill, rollback or compensating recovery, and
   validation. Do not execute migrations in this skill.
6. Persist `table-design.md` from [table-design.md](templates/table-design.md) only when requested or
   needed as a durable contract.
7. When a design file was persisted, separately inspect its diff, verify it against actual
   schema/repository rules, and check scenario coverage, lifecycle/migration consistency, omissions,
   placeholders, and links. Repair issues and return `Document self-review: pass|issues`. Flag D1
   readiness review when the design governs downstream work; do not invoke another supporting skill
   automatically.

## Output

Return the proposed data model, scenario mapping, migration/recovery impact, open decisions, and
verification requirements. List the generated file and document self-review verdict when persisted.

## Does not own

Do not choose Bruce execution profile/risk, create workflow state, force plan or test updates, approve schema
changes, execute migrations, or invoke another supporting skill automatically.
