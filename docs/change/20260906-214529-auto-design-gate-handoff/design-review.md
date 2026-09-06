# 设计评审

- Objective: 让治理型方案工件落盘后在同一轮自动执行 Design Gate
- Scope: Bruce 核心工作流、方案 writer、artifact policy、说明文档、契约测试和本变更工件
- Implementation boundary: requirements.md、architecture.md、api-contracts.md、plan.md 与 test-plan.md 约束本次插件修改
- Review mode: main-agent
- Behavior implementation: yes
- Public/cross-component contract change: yes
- Database/persistence design change: no
- Governing UI prototype: no
- Complex acceptance: no

## 候选工件矩阵

| Candidate | Applicability | Delivery | Path | Repository-backed evidence |
|---|---|---|---|---|
| Requirement or clarification | required | generated | requirements.md | 用户明确要求方案落盘后自动执行 Design Gate 且不再等待追加指令 |
| Architecture | required | generated | architecture.md | 两层责任模型定义 writer handoff 与 Bruce 同轮编排边界 |
| API/file contracts | required | generated | api-contracts.md | 共享 Skill handoff 与核心工作流控制流合同发生变化 |
| Database/table design | skipped | skipped | none | 不涉及数据库、schema 或持久化迁移 |
| Implementation plan | required | generated | plan.md | 多个 Skill、说明和测试需要按依赖顺序同步修改 |
| Test design | required | generated | test-plan.md | S-01 至 S-04 覆盖自动衔接、职责边界和非适用场景 |
| UI prototype | skipped | skipped | none | 无用户可见 Web 界面或视觉交互变化 |

## 就绪检查

- Facts and consistency: pass；当前核心工作流已要求 design-only 运行 Gate，但五个 writer 仍存在只提示或禁止自动调用的冲突语义，本方案统一为 mandatory handoff。
- Acceptance and verification coverage: pass；AC-01 至 AC-05 均映射到现有契约测试和全量插件验证命令。
- Risk and recovery coverage: pass；不改变 verdict、validator 或授权边界，Gate 或 validator 非零结果会停止受影响实现。
- Existing-product visual authority and compatibility: not-applicable；本次无产品 UI 或浏览器表面变化。
- Deterministic artifact visual assertions: not-applicable；无原型、视觉 token 或截图工件。
- Blocking findings: none
- Evidence boundary: 已核对当前 Skill、artifact policy、相关测试与插件刷新规则；实现结果由 test-plan.md 中命令验证。
- Smallest next action: none

## 验证

- Command: `python3 skills/design-gate/scripts/validate_design_review.py --change-dir docs/change/20260906-214529-auto-design-gate-handoff`
- Result: pass；以当前直接校验进程的零退出码为权威。

## 结论

Design: pass
