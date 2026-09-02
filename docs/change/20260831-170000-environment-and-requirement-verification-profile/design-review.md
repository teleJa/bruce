# Design Review

- Objective: 建立只记录用户提供并确认、用于支撑开发和测试的运行拓扑与操作声明、默认未确认的 Environment Profile，并将 Verification Profile 改造为强制绑定 requirements.md 的需求级验收与修复策略；支持从 confirmed Profile 派生受边界约束的 Executable Environment Operation Skill。
- Scope: 两类 Profile 的用户声明拓扑 schema、部署/构建/生命周期/依赖/网络/身份/数据/配置边界、账号与 Credential 安全、能力选择、用户确认、stale、阻塞恢复、本地 `.env`、生成可执行 Operation Skill、模板、文档和契约测试。
- Implementation boundary: 只实现 Bruce supporting skills、Profile lifecycle/security references、workflow/README 文档、本地 `.env` helpers、可执行操作 Skill generator/runner 和契约测试；Environment Profile 不扫描仓库填充事实，不执行项目 Adapter、CNB/部署/客户端操作、业务代码或远程环境操作。
- Review mode: main-agent
- Behavior implementation: yes
- Public/cross-component contract change: yes
- Database/persistence design change: no
- Governing UI prototype: no

## Candidate Matrix

| Candidate | Applicability | Delivery | Path | Repository-backed evidence |
|---|---|---|---|---|
| Requirement or clarification | required | generated | requirements.md | 用户确认 requirements.md 强制输入、环境 Profile 独立复用和 Profile 默认未确认 |
| Architecture | required | generated | architecture.md | 当前 Bruce workflow、verification-loop、Checkpoint、Goal 和 Completion ownership 规则 |
| API/file contracts | required | generated | api-contracts.md | 两类 Profile、确认、账号/Credential、动态 Run 边界需要稳定文件契约 |
| Database/table design | skipped | skipped | none | 不修改业务数据库 schema 或表结构 |
| Implementation plan | required | generated | plan.md | 变更跨 Environment Profile、Environment Operations supporting skill、workflow references、templates、local `.env` helpers 和 tests |
| Test design | required | generated | test-plan.md | 涉及 Profile 生命周期、用户确认、外部环境、账号安全、阻塞恢复和 evidence ownership |
| UI prototype | skipped | skipped | none | 不改变产品 UI，不需要 prototype |

## Readiness

- Facts and consistency: pass — 已核对当前 verification-profile、artifact placement、Task/Checkpoint、Failure Policy、Goal 和 Completion 规则；设计将需求级 Profile 与用户声明的开发/测试运行拓扑分离，并将数据库/中间件纳入 dependencies + data policy。
- Acceptance and verification coverage: pass — AC-001 至 AC-011 均映射到用户声明 Profile 拓扑 schema、需求输入、环境/账号/能力映射、确认、stale、拓扑操作声明、生成可执行 Operation Skill、来源 Profile exact binding、暂停恢复或 Completion ownership 场景；对抗性 validator 测试覆盖 repository metadata、原始值和风险降级绕过。
- Risk and recovery coverage: pass — 明确 Profile 默认 pending、只记录用户声明、普通仓库代码不触发 stale、Credential 不进入 Profile，用户明确授权后才允许本地 `.env` 初始化，文件必须被 Git 忽略且 owner-only，秘密不进入模型可见输出；暂停停止通知和用户显式恢复边界不变。
- Existing-product visual authority and compatibility: clear — 本变更不治理产品 UI；浏览器/客户端能力只作为环境或需求 Profile 的验证输入。
- Deterministic artifact visual assertions: clear — 无 UI prototype 和视觉产物。
- Blocking findings: none
- Evidence boundary: checked 当前 Bruce Skill、`.env` metadata/creation helpers、用户声明 schema、Profile contract validator、对抗性测试契约、Git ignore 规则和既有 Multica SSO change package 的需求/测试结构；unchecked 具体项目 Environment Profile 实例、Adapter、CNB webhook、客户端自动化和外部运行时实现。
- Smallest next action: 按 T-002 revision 4 和 T-005 revision 1 校验开发/测试拓扑与生成 Skill contract；仅在 Profile exact confirmed 后生成项目级 Skill 和 runner。

## Validation

- Command: `python3 skills/design-gate/scripts/validate_design_review.py --change-dir docs/change/20260831-170000-environment-and-requirement-verification-profile`
- Result: pass — `python3 skills/design-gate/scripts/validate_design_review.py --change-dir docs/change/20260831-170000-environment-and-requirement-verification-profile`

## Verdict

Design: pass
