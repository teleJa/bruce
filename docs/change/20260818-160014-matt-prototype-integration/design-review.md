# Design Review

- Objective：新增 Matt Pocock 风格的问题驱动探索原型能力，并允许在责任边界清晰时委托 native subagent 生成原型。
- Scope：`skills/explore-prototype`、Bruce prototype 路由、subagent 委托边界、README/CONTEXT、相关测试和本 change 目录；排除 Open Design host、生产 UI、第三个 Gate 和用户现有未提交改动。
- Implementation boundary：Bruce plugin 的 Skill、文档和静态契约测试。
- Review mode：main-agent

## Candidate Matrix

| Candidate | Applicability | Delivery | Path | Repository-backed evidence |
|---|---|---|---|---|
| Requirement or clarification | skipped | skipped | none | 用户已明确同意先集成 Matt Pocock Prototype，并明确提出 subagent 上下文优化问题 |
| Architecture | required | generated | `architecture.md` | 新 Skill、正式原型隔离和主/子 agent ownership 是跨 Skill 结构决策 |
| API/file contracts | required | generated | `api-contracts.md` | generation/evidence packet 和 promotion 状态由 main agent、subagent、Bruce 路由及测试共同消费 |
| Database/table design | skipped | skipped | none | 不涉及数据库、持久化 schema、migration 或数据生命周期 |
| Implementation plan | skipped | skipped | none | 当前会话已有最小执行计划，未要求持久 handoff |
| Test design | skipped | skipped | none | 通过局部契约测试、完整 unittest、validator 和 diff check 覆盖；不涉及真实运行依赖或多层产品验收 |
| UI prototype | skipped | skipped | none | 本次实现 prototype workflow capability，不生成产品 UI 原型 |

## Readiness

- Facts and consistency：pass；当前 Bruce、`write-prototype`、`design-gate`、`spawn-execute` 和 Matt 本地 Skill/许可均已核对。
- Acceptance and verification coverage：pass；两种模式、正式原型隔离、generation/evidence packet、顺序降级和主 agent ownership 均有对应契约测试路径。
- Risk and recovery coverage：pass；subagent unavailable/failure、path overlap、scope drift 和生产副作用均 fail closed 或顺序降级。
- Existing-product visual authority and compatibility：not-applicable；本次不生成产品原型，已有 `write-prototype` authority 顺序保持不变。
- Deterministic artifact visual assertions：not-applicable；本次无生成 artifact。
- Blocking findings：none。
- Evidence boundary：已检查当前工作区 Skill、测试和第三方本地来源；未运行具体 prototype、Open Design 或 Chrome 产品验收。
- Smallest next action：实现新增 Skill、Bruce 路由、文档和契约测试，然后运行完整验证与 Completion Gate。

## Verdict

Design: pass
