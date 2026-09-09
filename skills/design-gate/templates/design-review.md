# 设计评审

- Objective: <objective>
- Scope: <allowed and excluded scope>
- Implementation boundary: <what this design governs>
- Review mode: <main-agent|independent>
- Behavior implementation: <yes|no>
- Public/cross-component contract change: <yes|no>
- Database/persistence design change: <yes|no>
- Governing UI prototype: <yes|no>
- Complex acceptance: <yes|no>

## 候选工件矩阵

| Candidate | Applicability | Delivery | Path | Repository-backed evidence |
|---|---|---|---|---|
| Requirement or clarification | required\|skipped | generated\|missing\|skipped | <path or none> | <evidence> |
| Architecture | required\|skipped | generated\|missing\|skipped | <path or none> | <evidence> |
| API/file contracts | required\|skipped | generated\|missing\|skipped | <path or none> | <evidence> |
| Database/table design | required\|skipped | generated\|missing\|skipped | <path or none> | <evidence> |
| Implementation plan | required\|skipped | generated\|missing\|skipped | <path or none> | <evidence> |
| Test design | required\|skipped | generated\|missing\|skipped | <path or none> | <evidence> |
| UI prototype | required\|skipped | generated\|missing\|skipped | <prototype-manifest.md path or none> | <evidence> |

## 上下游职责与来源

| 设计维度 | 权威来源 | 下游消费方 | 允许的下游具体化 | 冲突处理 |
|---|---|---|---|---|
| 结构、组件和领域语义 | <architecture.md / confirmed decision> | <API/DB/plan/test> | <implementation detail only> | <return to architecture/user> |
| API、事件或文件契约 | <api-contracts.md / authoritative source> | <test/plan> | <assertions and integration steps> | <return to contract design> |
| 持久化、约束和迁移 | <table-design.md / repository convention> | <test/plan> | <verification and implementation order> | <return to DB design/architecture> |
| 验收、场景和证据 | <requirements/test-plan.md> | <plan/gate> | <task mapping and checks> | <return to acceptance/design> |
| 实施顺序和任务边界 | <plan.md/task contract> | <handoff/executor> | <local coding choices> | <return to plan/design> |

下游工件只能引用或具体化上游决策，不得静默改变业务规则、状态权威、契约、数据语义或验收。

## 跨文档一致性矩阵

| Join ID | 上游来源 | 下游来源 | 核对内容 | 结果 | 证据/问题 |
|---|---|---|---|---|---|
| JOIN-001 | <path#section> | <path#section> | <决策、字段、状态、验收或范围是否一致> | <checked|pass|finding|not_applicable> | <path/observation> |

仅记录实际核对的 material joins，不复制完整工件。`finding` 必须关联具体路径和最小修复方向。

## 就绪检查

- Facts and consistency: <pass|blocked with evidence>
- Acceptance and verification coverage: <pass|blocked with evidence>
- Risk and recovery coverage: <pass|blocked|not-applicable with evidence>
- Existing-product visual authority and compatibility: <clear or findings for ordered authority,
  selected/effective generation skill and visual plugin/design-system, compatibility evidence, and
  run input summary>
- Deterministic artifact visual assertions: <clear or findings for exact colors/dimensions/brand/
  forbidden tokens and whether manual-only evidence is correctly fail-closed>
- Blocking findings: <none or findings>
- Evidence boundary: <checked and unchecked facts>
- Cross-document consistency: <clear or findings with JOIN IDs>
- Upstream decision authority: <all material decisions have sources, or findings>
- Execution claims: <planned evidence is not presented as executed result>
- Smallest next action: <none or action>

## 验证

- Command: `python3 <plugin-root>/skills/design-gate/scripts/validate_design_review.py --change-dir <change-directory>`
- Result: <pass with current command evidence>

## 结论

Design: <pass|blocked>
