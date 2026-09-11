---
name: bruce
description: "Guide an Agent through Bruce's three stages: analysis, design, and development."
---

# Bruce workflow

Bruce is the top-level workflow guide for software work. It explains which stage the Agent is in,
what that stage must produce, and when it must stop. Detailed work belongs to specialized Skills.

```text
分析 → 设计 → 开发
```

## 1. 分析

Use `solution-analysis` when the requirement, scope, feasibility, or business decision is unclear.
Inspect relevant evidence and project knowledge; distinguish user decisions, existing rules, assumptions,
and unknowns; then return a recommendation and unresolved decisions.

Analysis is read-only. It does not create design artifacts, tasks, checkpoints, or implementation.
Wait for the user to confirm the direction before entering design.

## 2. 设计

Enter design only after the user confirms the analysis. Invoke only the necessary specialist Skills:

- `write-architecture` for architecture or public and cross-component contracts;
- `write-db-design` for schema and persistence decisions;
- `write-plan` for the overall implementation plan;
- `write-task` after plan review and user confirmation to freeze concrete execution task contracts;
- `write-tests` for behavior-change test design;
- `design-gate` when persisted design governs downstream implementation.

The design result must define scope, exclusions, acceptance, verification, dependencies, and file ownership.
After `write-plan`, wait for the independent reviewer and the user to confirm the plan. Only then invoke
`write-task` to create the concrete frozen execution task package before Design Gate. `write-plan` is
the overall plan; `write-task` owns the per-task contracts.

After the necessary artifacts pass their checks and `design-gate` returns `Design: pass`, stop in
design-only mode. This means the design is ready; it does not authorize implementation.

## 3. 开发

Enter development only when the user authorizes implementation and the confirmed design is ready.
Consume the existing scope and task boundaries. Do not restart broad analysis or silently redesign them.
Implement and verify the smallest ready slice first. Use `spawn-execute` only for boundary-clear,
low-coupling work; keep shared-file or unresolved-contract work with the main Agent.

Use the configured verification Skills for acceptance evidence. The main Agent owns scope, ordering,
integration, and re-verification. A delegated Agent's completion message is not completion evidence.
After implementation and targeted verification, use `completion-gate`; only `Completion: pass` is a
completion decision.

## Stage boundaries

- Analysis does not imply design.
- Design does not imply implementation.
- A plan does not prove implementation or verification.
- A delegated task does not decide design or completion.
- Do not use Goal, a scheduler, or a second lifecycle to move between stages.

Specialized Skills and Bruce references own detailed contracts, templates, evidence rules, recovery,
browser verification, delegation, and Gate procedures. This entry Skill routes the stage; it does not
duplicate those procedures.

## Does not own

Do not implement product behavior, create a scheduler or runtime, select models, manage permissions,
maintain a second evidence store, or decide Design or Completion on behalf of the owning Gate.
