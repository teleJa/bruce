# 设计评审

- Objective: 修复已确认的工作流一致性、轻量模板、预算及评估问题
- Scope: 单一 Bruce 插件的相关 Skill、fixture、模板和测试；不涉及远程或数据库
- Implementation boundary: api-contracts.md 和 test-plan.md 约束本次本地修改
- Review mode: main-agent
- Behavior implementation: yes
- Public/cross-component contract change: yes
- Database/persistence design change: no
- Governing UI prototype: no
- Complex acceptance: yes

## 候选工件矩阵

| Candidate | Applicability | Delivery | Path | Repository-backed evidence |
|---|---|---|---|---|
| Requirement or clarification | required | generated | requirements.md | 用户确认五项建议，AC-01 至 AC-06 明确边界 |
| Architecture | skipped | skipped | none | 复用 scripts/workflow_behavior_fixture.py，不改变单一插件结构 |
| API/file contracts | required | generated | api-contracts.md | 明确 manifest 增量、summarize CLI 和现有 checkpoint 行字段 |
| Database/table design | skipped | skipped | none | 无数据库或持久化迁移 |
| Implementation plan | skipped | skipped | none | requirements.md 已记录有界顺序，无独立计划或任务包交接需要 |
| Test design | required | generated | test-plan.md | S-01 至 S-06 覆盖策略、预算、文件完整性和评估边界 |
| UI prototype | skipped | skipped | none | visual_scope 为 none，无 Web 产品界面 |

## 就绪检查

- Facts and consistency: pass；已读取当前源码，复用现有六场景工具，非重复建设。
- Acceptance and verification coverage: pass；AC-01 至 AC-06 均有对应测试/命令，真实 actor 效果不冒充验收。
- Risk and recovery coverage: pass；本地可回退合同增量，旧 manifest 缺省兼容；无远程或数据库操作。
- Existing-product visual authority and compatibility: not-applicable；无产品 UI，visual_scope 为 none。
- Deterministic artifact visual assertions: not-applicable；无原型、视觉 token 或浏览器工件。
- Blocking findings: none
- Evidence boundary: 当前源码与设计已核对；实现与测试尚未执行；本评审仅判定设计就绪。
- Smallest next action: 实施范围内修复并执行 test-plan.md。

## 验证

- Command: `python3 skills/design-gate/scripts/validate_design_review.py --change-dir docs/change/20260905-134400-workflow-coherence`
- Result: pass；以当前 hook/直接校验进程的实际零退出码为权威，本文字段不构成独立执行证据。

## 结论

Design: pass
