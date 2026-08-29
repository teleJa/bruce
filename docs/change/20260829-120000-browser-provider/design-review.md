# Design Review

- Objective: Bruce 默认使用 `ego-lite` 执行用户可见 Web 的 UI/交互验证，并支持通过 `.bruce/config.yaml` 显式选择 `chrome`；统一保存 Provider 中立的浏览器证据。
- Scope: 增加 YAML 配置、Provider 中立 visual scope、Provider capability preflight/evidence/fail-closed 规则及相关契约测试；不实现浏览器 runtime，不修改业务 UI/API/数据库。
- Implementation boundary: `.bruce/config.yaml`、配置模板、Bruce verification loop、Completion Gate、prototype/test-plan 规则和对应契约测试。
- Review mode: main-agent
- Behavior implementation: yes
- Public/cross-component contract change: yes
- Database/persistence design change: no
- Governing UI prototype: no

## Candidate Matrix

| Candidate | Applicability | Delivery | Path | Repository-backed evidence |
|---|---|---|---|---|
| Requirement or clarification | required | generated | `requirements.md` | 用户已确认 Provider 配置方向；当前 Web 验收规则在 `skills/bruce/references/verification-loop.md:20-42,87-94` 固定 Chrome，需记录默认值、选择、迁移和 fail-closed 场景。 |
| Architecture | required | generated | `architecture.md` | `.bruce/config.yaml` 与 `skills/bruce/templates/config.yaml` 是现有 YAML 配置入口；`skills/completion-gate/SKILL.md:146-173` 绑定 current Chrome evidence，需定义 Provider 分派边界。 |
| API/file contracts | required | generated | `api-contracts.md` | 配置和 browser evidence 是跨 verification loop、prototype 规则、Completion Gate 与测试的共享文件/文档契约。 |
| Database/table design | skipped | skipped | none | 本变更不修改业务数据库、持久化 schema 或数据生命周期。 |
| Implementation plan | required | generated | `plan.md` | 变更跨配置、核心验证循环、Completion Gate、prototype 规则和测试契约，存在传播依赖，计划采用顺序任务包。 |
| Test design | required | generated | `test-plan.md` | `tests/test_bruce_config_contract.py`、`test_validation_loop_contract.py` 和 `test_completion_contract.py` 已为配置和验收规则提供契约回归入口。 |
| UI prototype | skipped | skipped | none | 本变更修改 UI 验收机制，不设计或实现产品 UI；现有 UI Surface Contract 只需更新证据 Provider 语义。 |

## Readiness

- Facts and consistency: pass；已核对当前 `.bruce/config.yaml`、配置模板、artifact placement、verification loop、Completion Gate 和相关测试；当前文件均为 YAML/Markdown/Python 契约，未引入未确认的 runtime API。
- Acceptance and verification coverage: pass；`requirements.md` 的 AC-001 至 AC-005 映射到 `test-plan.md`、任务包和现有契约测试；覆盖默认值、显式选择、scope、fail-closed 和历史兼容。
- Risk and recovery coverage: pass；配置非法、Provider 不可用、能力不足、证据缺失和 stale revision 均定义为可报告的配置或能力问题；不做静默 fallback，遵循现有 L0-L4 规则。
- Existing-product visual authority and compatibility: not-applicable；本变更不生成或治理产品 UI 原型，只把运行时视觉证据的 Provider 从硬编码 Chrome 改为配置选择。
- Deterministic artifact visual assertions: not-applicable；本变更不修改产品颜色、尺寸、品牌或原型 artifact。
- Blocking findings: none。
- Evidence boundary: checked：配置路径/格式、现有 Chrome 专属规则、Completion Gate 依赖、测试入口和工作区未提交改动；unchecked：宿主实际 ego-lite/Chrome runtime、登录态继承、扩展加载和真实页面执行，这些不在本次仓库实现边界内。
- Smallest next action: 通过当前 Design Gate validator 后，按 `plan.md` 顺序实现配置和契约。

## Validation

- Command: `python3 skills/design-gate/scripts/validate_design_review.py --change-dir docs/change/20260829-120000-browser-provider`
- Result: pass with current command evidence

## Verdict

Design: pass
