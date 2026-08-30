# Design Review

- Objective: 在 Bruce 工作流内部建立项目自适应的验证—反馈—修复循环基础设施，并在阻塞时冻结受影响工作、通知用户，待用户显式恢复后继续。
- Scope: 验证循环状态/事件/证据协议、Project Verification Profile/Adapter 边界、用户 handoff、阻塞通知与恢复、Checkpoint/Goal/Completion 映射、契约测试设计。
- Implementation boundary: 本设计只治理 Bruce 核心协议和未来项目接入边界；不实现 CNB、Temporal、Kubernetes、Electron、Joytime/Multica Adapter、业务代码或远程部署。
- Review mode: main-agent
- Behavior implementation: no
- Public/cross-component contract change: yes
- Database/persistence design change: no
- Governing UI prototype: no

## Candidate Matrix

| Candidate | Applicability | Delivery | Path | Repository-backed evidence |
|---|---|---|---|---|
| Requirement or clarification | required | generated | requirements.md | 用户确认 Bruce 工作流包含验证循环；阻塞时必须停止、通知、显式恢复 |
| Architecture | required | generated | architecture.md | `skills/bruce/SKILL.md:8-23,59-147`；现有验证、Gate 和项目无关边界；`skills/verification-profile/SKILL.md` 作为 Profile 生成入口 |
| API/file contracts | required | generated | api-contracts.md | `skills/bruce/references/verification-loop.md:123-188` 的 checkpoint/next_action；现有无统一外部事件协议 |
| Database/table design | skipped | skipped | none | 只定义运行协议，不设计业务数据库或持久化 schema |
| Implementation plan | required | generated | plan.md | 变更跨 workflow、verification、failure recovery、Goal、Completion 和 tests |
| Test design | required | generated | test-plan.md | `skills/bruce/references/verification-loop.md:7-18,84-121,195-237`；外部和用户证据需要分层验证 |
| UI prototype | skipped | skipped | none | 不改变 UI，不需要 prototype |

## Readiness

- Facts and consistency: pass — 已核对 Bruce 当前 Task Contract、验证分层、preflight、checkpoint、L0-L4 和 Completion ownership；已区分规范层能力与缺少运行时 Adapter/Event 的实现缺口。
- Acceptance and verification coverage: pass — AC-001 至 AC-007 均映射到状态、Profile、Adapter、Profile 生成 skill、暂停、恢复、用户 handoff 或 Gate ownership 场景。
- Risk and recovery coverage: pass — 明确 `waiting_external`/`waiting_user`/`paused`，暂停时冻结写入并要求用户显式 resume；恢复不重置预算且重跑 preflight。
- Existing-product visual authority and compatibility: clear — 本设计不治理具体产品 UI；项目的 Desktop/Web 视觉证据由项目 Profile/Adapter 声明并由 Bruce 消费。
- Deterministic artifact visual assertions: clear — 无 UI prototype 和确定性视觉产物。
- Blocking findings: none
- Evidence boundary: checked Bruce 文档/模板/测试契约与已知 Multica 项目验证边界；unchecked 具体 Adapter、CNB webhook、客户端自动化和运行时部署实现。
- Smallest next action: 按 T-002 验证 `verification-profile` supporting skill 的 Profile 生成边界，仍不接入具体项目环境。

## Validation

- Command: `python3 skills/design-gate/scripts/validate_design_review.py --change-dir docs/change/20260830-160000-verification-loop-infrastructure`
- Result: pass — `python3 skills/design-gate/scripts/validate_design_review.py --change-dir docs/change/20260830-160000-verification-loop-infrastructure`

## Verdict

Design: pass
