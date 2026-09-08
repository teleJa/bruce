# Design Review

- Objective: 为 Bruce 建立统一、版本化、可校验的任务级工作流状态机，并收敛现有 checkpoint、Verification Run、repair loop 和 Gate 的生命周期映射。
- Scope: 状态枚举、事件转移、状态快照、模板、校验器、现有文档/模板接入和契约测试。
- Implementation boundary: 只修改 Bruce 工作流协议、脚本、模板和测试；不实现项目环境、Adapter、部署、数据库、浏览器 runtime 或发布流程。
- Review mode: main-agent
- Behavior implementation: yes
- Public/cross-component contract change: yes
- Database/persistence design change: no
- Governing UI prototype: no

## Candidate Matrix

| Candidate | Applicability | Delivery | Path | Repository-backed evidence |
|---|---|---|---|---|
| Requirement or clarification | required | generated | requirements.md | 用户明确同意先增加统一状态机；现有状态分散在 checkpoint、Verification Run、Gate 和 failure recovery |
| Architecture | required | generated | architecture.md | `skills/bruce/SKILL.md`、`skills/bruce/references/verification-loop.md`、`skills/bruce/templates/checkpoint.yaml` |
| API/file contracts | required | generated | api-contracts.md | 现有 checkpoint/run 模板存在独立状态字段，需要统一引用和转移约束 |
| Database/table design | skipped | skipped | none | 不引入业务数据库或持久化表 |
| Implementation plan | required | generated | plan.md | 变更跨脚本、模板、workflow references 和 tests |
| Test design | required | generated | test-plan.md | 状态机涉及状态、事件、终态、恢复和 Gate ownership |
| UI prototype | skipped | skipped | none | 不改变 Bruce 或项目产品 UI；无原型文件、无视觉契约输入 |

## Readiness

- Facts and consistency: pass — 已核对当前 Bruce workflow、checkpoint、verification run、failure recovery 和 Gate ownership；统一状态机只增加任务级生命周期，不替换子对象状态。
- Acceptance and verification coverage: pass — AC-001 至 AC-005 映射到状态 schema、合法转移、对象映射、Gate ownership 和回归测试。
- Risk and recovery coverage: pass — 非法事件 fail closed；冻结范围带有明确解锁条件；恢复保留 repair/evidence/profile revision，不重置历史计数。
- Existing-product visual authority and compatibility: clear — 本设计不治理具体产品 UI；项目的 Desktop/Web 视觉证据仍由项目 Profile/Adapter 声明并由 Bruce 消费。
- Deterministic artifact visual assertions: clear — 本设计没有 UI prototype 或确定性视觉产物，不新增视觉断言。
- Blocking findings: none
- Evidence boundary: checked Bruce source/docs/templates/tests; not claiming project runtime, external Adapter or production evidence.
- Smallest next action: 实现状态校验器、模板接入和契约测试。

## Validation

- Command: `python3 skills/design-gate/scripts/validate_design_review.py --change-dir docs/change/20260908-120000-unified-workflow-state-machine`
- Result: pass — 当前设计边界、候选矩阵和测试覆盖已完成。

## Verdict

Design: pass
