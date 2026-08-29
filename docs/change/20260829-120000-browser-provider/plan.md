# 实施计划：可配置浏览器验证提供者

## Task contract

- Objective：Bruce 默认使用 `ego-lite` 执行用户可见 Web 的 UI/交互验证，并支持显式选择 `chrome`，由统一验收契约记录和裁决 Provider 证据。
- Scope：`.bruce/config.yaml`、配置模板、Bruce verification/completion/prototype 文档、测试契约和 Provider 中立命名；不实现浏览器 runtime，不修改业务 UI/API/数据库。
- Acceptance：AC-001 至 AC-005；每项证据见 `test-plan.md`。
- Constraints：保持 YAML 配置路径；不自动 fallback；Chrome/ego-lite 的底层连接由宿主提供；保护工作区已有未提交改动。
- Topology：full；跨配置、核心 verification loop、Completion Gate、prototype 规则和测试契约多个边界，存在共享验收语义传播。
- Risk：guarded；改变正式 Web 验收环境和 evidence contract，错误迁移可能导致误报通过或错误阻塞。

## Task package

- Path: `tasks/`
- Index: `tasks/index.yaml`
- Contract state: task files are frozen before their task starts
- Status source: `checkpoint.yaml` or the current checkpoint message
- Execution mode: sequential
- Omission reason: none

## Task summary

| Task ID | Title | Depends on | Acceptance IDs | Allowed paths | Verification layer |
|---|---|---|---|---|---|
| T-001 | 增加 Provider 配置与统一契约 | none | AC-001, AC-002, AC-003, AC-004, AC-005 | `.bruce/config.yaml`, `skills/bruce/templates/config.yaml`, `skills/bruce/SKILL.md`, `skills/bruce/references/verification-loop.md`, `skills/bruce/references/browser-provider.md`, `scripts/browser_provider.py`, `skills/bruce/references/artifact-placement.md`, `skills/completion-gate/SKILL.md`, `skills/explore-prototype/SKILL.md`, `skills/explore-prototype/references/ui-variants.md`, `skills/write-prototype/references/ui-surface-contract.md`, `skills/write-tests/SKILL.md`, `skills/write-tests/templates/test-plan.md`, `README.md` | contract tests and validator |
| T-002 | 更新测试契约与迁移检查 | T-001 | AC-001, AC-002, AC-003, AC-004, AC-005 | `tests/test_bruce_config_contract.py`, `tests/test_browser_provider.py`, `tests/test_validation_loop_contract.py`, `tests/test_completion_contract.py`, `tests/test_supporting_skill_contracts.py`, `tests/test_explore_prototype_contract.py`, `tests/test_prototype_contract.py` | unit/contract |

## Repository evidence

- `.bruce/config.yaml` 与 `skills/bruce/templates/config.yaml` 当前为 YAML，测试使用 PyYAML。
- `skills/bruce/references/verification-loop.md` 与 `skills/completion-gate/SKILL.md` 当前将 current Codex App Chrome 作为 Web evidence 硬要求；新增 `skills/bruce/references/browser-provider.md` 承载 Provider 选择与证据契约。
- 当前仓库未发现 browser provider runtime resolver；本次实现以规则/契约配置为主，不虚构底层 runtime 已存在。

## 依赖与风险

- 先更新 provider-neutral scope 和 config contract，再更新 Gate 文案，避免配置默认值与验收规则冲突。
- 历史 `chrome-*` 术语必须明确为兼容别名，不能让旧任务失去可解释性。
- Provider 不可用时必须保持 blocked/incomplete，不能用另一个 Provider 伪造同一条证据。
- 只修改本任务列出的路径；保留工作区已有 `.codex-plugin/plugin.json`、`README.md` 等无关改动，若路径重叠只做本任务映射的最小修改。

## 全变更验证

- AC-001 -> 配置与模板解析测试 -> `python3 -m unittest tests.test_bruce_config_contract tests.test_browser_provider`。
- AC-002/AC-003 -> verification、completion、prototype 和 test-plan 契约测试。
- AC-004 -> resolver fail-closed 测试、规则断言和全量测试。
- AC-005 -> resolver 旧/新 visual scope 归一化测试和术语检查。

## 交付边界

- 工作区代码和文档变更；不提交、不推送、不刷新插件缓存、不启动浏览器或修改外部服务。
