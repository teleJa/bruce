# Design Review

- Objective: 在 Bruce 已确认的 Environment Profile、Requirement Verification Profile、Browser Provider 和 Completion Gate 体系上，引入通用的 API 编排验证、真实页面验收和测试轨道调度能力，同时禁止子代理操作浏览器并排除 `gpt-5.6-sol` 测试路由。
- Scope: 包含共享 Scenario 契约、API/UI 轨道职责、数据命名空间隔离、轨道状态聚合、Functional Agent/模型路由边界、浏览器执行权、Verification Run/Checkpoint 和 Completion Gate 对接；排除 Joytime 业务代码、数据库 schema/migration、浏览器 runtime、Playwright 迁移、子代理浏览器权限、第五类 Functional Agent Profile、`gpt-5.6-sol`、生产和未声明的环境操作。
- Implementation boundary: 后续按 `tasks/` 六个冻结合同顺序，仅修改 Bruce 的三个新 supporting skills、公共 references/scripts、Verification Profile/Loop/Completion 集成、metadata/docs 和契约测试；Joytime 三个 Skill 仅作为证据和适配来源，不能原样复制项目路径、业务模块或私有模型路由。实施不包含插件刷新、commit、push、部署或真实项目 API/UI 执行。
- Review mode: main-agent
- Behavior implementation: yes
- Public/cross-component contract change: yes
- Database/persistence design change: no
- Governing UI prototype: no

## Candidate Matrix

| Candidate | Applicability | Delivery | Path | Repository-backed evidence |
|---|---|---|---|---|
| Requirement or clarification | skipped | skipped | none | 用户已在当前会话明确确认两项关键需求边界：子代理不得操作浏览器，测试场景不得引入 `gpt-5.6-sol`；目标、Included/Excluded、验收 TVO-01 至 TVO-08 和实现边界已冻结在架构与计划中，本阶段没有独立 `requirements.md` 输入。 |
| Architecture | required | generated | architecture.md | 变更横跨 Environment Profile、Verification Profile、测试场景、API/UI 轨道、Functional Agent、Browser Provider、Checkpoint 和 Completion Gate，文档已定义组件所有权、控制流、失败恢复和用户确认边界。 |
| API/file contracts | required | generated | api-contracts.md | Scenario、Dispatch Packet、轨道结果、浏览器执行权、模型路由和 verdict ownership 是多个 Skill/Gate 消费的跨组件文件契约。 |
| Database/table design | skipped | skipped | none | 架构、计划和任务合同均排除数据库 schema、migration 和持久化结构变更；持久化只作为测试证据层和目标项目适配能力。 |
| Implementation plan | required | generated | plan.md | full/guarded 跨组件变更已拆为六个 sequential task，明确依赖、路径所有权、验收、验证层级、当前 dirty-worktree 边界和交付限制。 |
| Test design | required | generated | test-plan.md | TVO-01 至 TVO-08 已映射到 Scenario/API/UI/Dispatch/Routing/Profile/Completion/Regression 场景，覆盖版本、权限、异步、持久化、浏览器 ownership、stale 和回归。 |
| UI prototype | skipped | skipped | none | 本变更不设计或修改产品 UI；Browser UI Verification Track 是测试编排能力，不是用户界面或治理性视觉原型。 |

## Readiness

- Facts and consistency: pass — 已核对当前 Environment Profile 的 test context/operation/authorization 边界、Requirement Verification Profile 的 `skill_selections`、Browser Provider 的统一证据、Functional Agent 四 Profile/resolver 以及 Completion Gate 的唯一裁决权；架构、文件契约、计划、六个 task contract 和测试计划使用一致的 Scenario、轨道、浏览器 ownership、模型路由和状态词汇。
- Acceptance and verification coverage: pass — TVO-01 至 TVO-08 全部映射到计划任务和测试场景；每个行为场景具有 Given/When/Then、所需验证层级和具体仓库命令或后续项目运行边界。Scenario version、API/UI namespace、bounded polling、权限/控制权、Provider fail-closed、无 Sol、Profile/Run 静态动态分离和唯一 Completion 均有正反场景。
- Risk and recovery coverage: pass — 已覆盖 Profile stale/未确认、operation/账号/Provider 不可用、场景版本或写入冲突、API 替代页面动作、子代理 browser 越权、模型或 Packet 越权、证据不完整、无静默 mode/Provider/model 降级、修复后重跑原始场景和相关回归；数据库破坏性操作、生产和远程操作仍保持显式授权。T-005 明确要求先核对并兼容当前 Verification Profile 未提交修改，冲突时停止而非覆盖。
- Existing-product visual authority and compatibility: clear — 本变更不治理产品视觉；页面执行继续使用已有 `ego-lite|chrome` Provider 和 Provider 中立的 `browser-smoke|browser-layout`，Joytime 现有场景只允许通过项目适配层增量消费，不要求修改现有 UI 或 Playwright 资产。
- Deterministic artifact visual assertions: clear — 无 UI prototype、设计系统、颜色、尺寸、品牌或视觉 artifact 变更；浏览器 screenshot/geometry 是后续目标项目运行时验证证据，不是本 Design Gate 的视觉设计产物。
- Blocking findings: none
- Evidence boundary: checked 当前 Bruce 的 Environment/Verification Profile、Environment Operations、Browser Provider、Functional Agent resolver/Packet、Verification Loop、Completion Gate、三个新 Skill 的契约实现和相关测试，Joytime 三个参考 Skill，以及本变更的架构、API/file contracts、plan、tasks/index、六个冻结任务和 test-plan；unchecked 真实目标项目场景适配、真实 API/数据库/Worker/浏览器运行和插件刷新/交付，这些留在后续项目验证阶段并不得由 Design Gate 伪造。
- Smallest next action: none

## Validation

- Command: `python3 skills/design-gate/scripts/validate_design_review.py --change-dir docs/change/20260902-184244-test-verification-orchestration`
- Result: pass with current command evidence

## Verdict

Design: pass

## Contract repair alignment (2026-09-03)

独立复核发现了 Track Result 新鲜度、typed browser evidence、权威 readback、有限 polling、凭证
query、namespace、Scenario/Dispatch 一致性和 resolver Packet 绑定的 fail-closed 缺口。已在原有范围内
补强共享 validator/aggregator、Scenario/Dispatch/Track Result references、Verification Loop/Gate
消费规则和契约测试；未改变组件 ownership、唯一 Completion authority、六个 task 的路径边界或
排除项。新增的 `profile_id/profile_revision/profile_content_hash`、`basis_revision`、
`evidence_revision`、typed `evidence_records`、UI `browser_evidence` 和
`validate_track_results_for_context` 只强化运行证据边界，不把动态结果写入静态 Profile。

修复后的最小下一步是完成当前工作区的 Completion review；真实项目 API、数据库、Worker、浏览器
和远程交付仍不属于本仓库契约验证范围。
