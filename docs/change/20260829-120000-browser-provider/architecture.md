# 架构：可配置浏览器验证提供者

## 目标与范围

- Objective：让 Bruce 的用户可见 Web 验收根据配置选择 `ego-lite` 或 `chrome`，同时保持统一的验收层级、证据要求和 Completion Gate 裁决。
- Included：配置 schema/template、Provider 选择规则、Provider capability preflight、Provider 中立 visual scope、浏览器证据元数据、相关技能与契约测试。
- Excluded：底层浏览器 runtime、业务 UI、API、数据库、自动 fallback 和浏览器 Provider 的安装管理。

## 仓库证据

- `.bruce/config.yaml` — 当前工作区配置为 YAML，包含 `version`、`artifacts.root` 和 `workflow`。
- `skills/bruce/templates/config.yaml` — 新工作区配置模板，当前只定义 artifact root 和 workflow limits。
- `skills/bruce/references/verification-loop.md:20-42` — 当前用 `chrome-smoke`/`chrome-layout` 表示 Web 视觉范围，并定义截图、viewport、几何和 overflow 证据。
- `skills/bruce/references/browser-provider.md` — 本变更新增的 Provider 标识、能力 preflight、统一证据和 fail-closed 契约。
- `scripts/browser_provider.py` — 确定性解析默认/显式 Provider、归一化历史 scope、声明能力并拒绝证据 Provider mismatch。
- `tests/test_browser_provider.py` — 覆盖默认值、显式选择、非法值、scope 兼容、证据 mismatch 和 CLI 结果。
- `skills/bruce/references/verification-loop.md:87-94` — 当前要求 Codex App Chrome 当前会话，并在 Chrome 不可用时 fail-closed。
- `skills/completion-gate/SKILL.md:146-173` — Completion Gate 当前硬编码 current Codex App Chrome evidence。
- `tests/test_bruce_config_contract.py` — 当前配置契约使用 PyYAML 读取工作区和模板配置。

## 组件与责任

| 组件 | 现有交付物 | 负责 | 不负责 |
|---|---|---|---|
| Workspace verification config | `.bruce/config.yaml`、`skills/bruce/templates/config.yaml` | 声明受控 Provider 默认值/选择 | 启动浏览器、定义业务验收 |
| Provider contract | `skills/bruce/references/browser-provider.md`、`scripts/browser_provider.py` | 定义 Provider 标识、能力前置检查、scope 归一化、证据元数据和 fail-closed | 取代 Acceptance Scenario 或 Completion Gate |
| Browser execution provider | host-owned `ego-lite` / `chrome` capability | 执行真实导航、交互、状态观察、截图和必要几何检查 | 修改 Bruce 终态、静默 fallback |
| Verification loop | `skills/bruce/SKILL.md`、`verification-loop.md` | 按 `visual_scope` 和 Provider 组织验证 | 放宽证据要求 |
| Completion Gate | `skills/completion-gate/SKILL.md` | 检查 Provider evidence 的新鲜度、完整性并作唯一 Completion 裁决 | 重新选择 Provider |
| Contract tests | `tests/*contract.py` | 锁定配置、命名、能力和 fail-closed 语义 | 证明真实浏览器已运行 |

## 数据与控制流

1. Bruce 解析 `.bruce/config.yaml` 的 `verification.browser_provider`；缺省为 `ego-lite`。
2. 任务合同声明 Provider 中立的 `visual_scope=browser-smoke|browser-layout`。
3. 浏览器批次开始前，对所选 Provider 做一次最小 read-only capability preflight。
4. Provider 执行 `When` 中的真实交互并采集可见结果；`browser-layout` 额外采集 viewport、几何和 overflow；`scripts/browser_provider.py` 校验 scope 与 Provider 选择。
5. 形成统一 `browser_evidence`，记录 Provider、目标、会话、动作、可见结果、时间、revision 和 artifact path/hash。
6. Completion Gate 校验 Provider 与证据一致性；缺失、过期或能力不足时返回 `issues`/`blocked`，不使用其他 Provider 代替。

## 决策

### 决策一：配置文件继续使用 YAML

- Chosen：在 `.bruce/config.yaml` 增加 `verification.browser_provider`。
- Rationale：当前模板、文档和测试全部以 YAML 为配置契约；引入 TOML 会产生无必要的格式迁移。
- Rejected：新增 `.bruce/config.toml`，因为会造成双配置来源和加载优先级歧义。
- Reversibility：高；未来可增加版本化 schema，但不改变当前路径。

### 决策二：Provider 与 visual scope 分离

- Chosen：Provider 选择“谁执行”，`browser-smoke`/`browser-layout` 选择“需要什么证据强度”。
- Rationale：避免 `chrome-layout` 这类名称在支持 ego-lite 后继续错误表达 Chrome 绑定。
- Rejected：保留 `chrome-smoke` 作为正式名称，因为它把实现者和验收级别耦合在一起。
- Reversibility：中；历史名称保留兼容别名，新任务只生成中立名称。

### 决策三：默认 ego-lite、无静默 fallback

- Chosen：缺省 Provider 为 `ego-lite`；配置非法、Provider 不可用或能力不足时 fail-closed。
- Rationale：ego-lite 适合隔离和重复交互；无 fallback 才能保证证据来源可追溯和结果可复现。
- Rejected：ego-lite 失败自动切换 Chrome，因为会使实际验证环境与配置不一致。
- Reversibility：高；用户可在任务或工作区配置中显式选择 `chrome`。

### 决策四：保留统一 Gate

- Chosen：Provider 只负责执行和证据，Design Gate/Completion Gate 保持唯一决策权。
- Rationale：符合 Bruce 的现有 ownership boundary，防止 Provider 成功状态变成第二个 verdict。
- Rejected：为每个 Provider 增加独立 UI Gate，因为会制造多裁决源。
- Reversibility：高。

## 契约

- `requirements.md#AC-001` 至 `AC-005` 定义行为契约。
- `api-contracts.md#browser-provider-configuration` 定义配置、能力和证据字段。

## 横切行为

- Compatibility：接受历史 `chrome-smoke`/`chrome-layout` 作为兼容别名；新模板使用 `browser-smoke`/`browser-layout`。
- Authentication/authorization：Provider 复用其宿主既有会话能力；Bruce 不保存凭证、不扩大登录权限、不把 Provider 配置当作登录授权。
- Failure/recovery：配置错误/能力缺失为配置或 preflight blocker；不可静默 fallback；遵循现有 L0-L4 规则。
- Observability：证据必须记录 Provider、Provider 版本/能力摘要（若可得）、target、session/task space 或 current Chrome tab、actions、visible result、capture time、basis revision、artifact path/hash。
- Rollout/rollback：先更新模板与契约规则，再更新工作区默认值；用户可将 Provider 改回 `chrome`。不涉及数据库迁移或远程部署。

## 验证影响

- AC-001 -> PyYAML 配置契约测试。
- AC-002 -> verification-loop、Completion Gate 和证据格式契约测试。
- AC-003 -> visual scope 和模板契约测试。
- AC-004 -> provider 枚举、preflight、无 fallback 和 blocked/incomplete 规则测试。
- AC-005 -> 旧名称兼容和新命名检查。

## 开放决策

- 无。Provider runtime 的具体 host API 不在本仓库实现范围内；本变更只定义 Bruce 的选择与证据契约。
