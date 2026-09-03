# 文件契约：Bruce 通用测试验证编排与轨道调度

## shared-scenario-contract

- Change：added
- Provider：项目测试场景适配层 / Bruce Test Dispatch
- Consumers：Requirement Verification Profile、API Verification Track、Browser UI Verification Track、Verification Run/Checkpoint、Completion Gate
- Authoritative source：本变更的场景规范；项目可使用 YAML、Markdown 或已有测试格式，但必须能表达以下字段
- Compatibility：versioned；已有项目场景可通过适配层消费，历史运行证据不回写
- Authentication/authorization：账号、凭证、服务和 operation 只能引用已确认 Environment Profile，不保存秘密值

### Request, event, or input

```yaml
version: 1
scenario_id: FEATURE-AREA-001
scenario_version: 1
feature_area: user-facing-feature
business_flow: user-action-1 -> async-result -> reload-recovery
actor: regular-user
visual_scope: browser-smoke
execution:
  environment_profile: project-local
  api_mode: real-http|memory-application|live-acceptance|null
  ui_mode: browser-provider|null
data:
  api_namespace: api-run-example-contract-value|null
  ui_namespace: ui-run-example-contract-value|null
  ownership: test-run|dedicated-test-database|read-only-existing-data
  cleanup: declared-safe-strategy
preconditions:
  - backend-health
  - frontend-ready
  - worker-ready
api:
  steps: []
  assertions: []
  persistence:
    required: false
    readback: []
ui:
  steps: []
  assertions: []
  forbidden_shortcuts: []
failure_cases: []
evidence:
  required: []
  directory: repository-relative-or-approved-path
status: designed|executed|passed|failed|blocked
```

### Success result

场景必须能被两个轨道引用同一个 `scenario_id` 和 `scenario_version`，并能将每个 Acceptance 映射到至少一个明确的证据层级。API 与 UI 步骤必须保持语义分离：API 步骤描述请求/状态/持久化，UI 步骤描述真实页面动作和可见结果。

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| 场景缺少稳定 ID/version | designed/blocked | 补齐场景契约；不得创建竞争场景 |
| 场景需要的 Environment operation 未声明 | blocked | 更新已确认 Profile 或显式授权新 operation；不得现场发明命令 |
| API/UI 场景版本不一致 | blocked | 父 Agent 协调并创建新版本；不得合并无关证据 |
| UI 动作由 API 预先完成 | invalid evidence | 丢弃该页面证据，重新执行真实页面动作 |

### Verification

- Provider：项目场景适配器和 `verification-profile`。
- Consumer：场景契约测试、Test Dispatch、API/UI 轨道和 Completion Gate。
- Required evidence：场景文件、Acceptance 映射、execution mode、namespace、前置条件、证据目录和状态。

## track-dispatch-contract

- Change：added
- Provider：Bruce Test Dispatch
- Consumers：API Verification Track、Browser UI Verification Track、Verification Run/Checkpoint
- Authoritative source：Bruce Functional Agent v1 Packet、本变更场景契约
- Compatibility：versioned；`scenario_id/version` 是跨轨道协调键
- Authentication/authorization：Dispatch 只能选择已确认 Profile 声明的 Skill、operation、账号和证据范围

### Request, event, or input

```yaml
version: 1
scenario_id: FEATURE-AREA-001
scenario_version: 1
feature_area: user-facing-feature
business_flow: declared-business-flow
actor: admin|regular-user|unauthenticated
tracks:
  - track: api
    execution_mode: memory-application|real-http|live-acceptance
    data_namespace: api-run-example-contract-value
    allowed_paths: []
    required_evidence: []
  - track: ui
    execution_mode: browser-provider
    data_namespace: ui-run-example-contract-value
    allowed_paths: []
    required_evidence: [final-url, visible-state, screenshot]
routing:
  required_capabilities: []
  functional_agent_profile: verifier|implementer|inspector|reviewer
  model_resolution: resolved|fallback|blocked
```

`routing` 只声明能力和 Bruce Profile，不声明或覆盖 `gpt-5.6-sol`，不创建测试专用模型选择器。实际模型和 effort 必须来自 Bruce resolver 产生的 `model_resolution`。

### Success result

每个轨道返回一个独立结果 Packet，至少包括：场景 ID/version、轨道、执行模式、状态、证据路径/引用、修改路径、实际命令或浏览器动作、断言、阻塞项和未验证门禁。API/UI 写入路径必须互斥；UI 轨道的真实浏览器动作不委派给子代理。

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| Profile 未确认或 revision/hash 不匹配 | blocked | 重新确认 Profile；不得执行轨道 |
| 所需 operation、能力或账号不可用 | blocked | 记录解除条件；相关依赖恢复后重新 preflight |
| 子代理 Packet 越权 | blocked | 修正 Packet；不得放宽 allow/deny |
| 轨道失败 | failed | 保留原始证据，按 Bruce repair loop 修复后重跑原始场景和相关回归 |
| 轨道只设计未执行 | designed | 不得提升为 passed |

### Verification

- Provider：`verification-profile`、Environment Profile、Functional Agent Packet validator。
- Consumer：Test Dispatch、轨道 Skill、Checkpoint 和 Completion Gate。
- Required evidence：Packet、`model_resolution`、namespace 隔离、实际命令/动作和 evidence refs。

## track-result-and-status-aggregation

- Change：added
- Provider：API/UI 轨道与 Bruce Test Dispatch
- Consumers：Verification Run/Checkpoint、Completion Gate
- Authoritative source：`skills/test-dispatch/references/track-result-schema.md` 和 Bruce Verification Loop
- Compatibility：additive；轨道状态不等同于 Bruce Completion
- Authentication/authorization：结果只能引用脱敏证据；不得携带凭证值

### Request, event, or input

```yaml
version: 1
scenario_id: FEATURE-AREA-001
scenario_version: 1
profile_id: verification-profile
profile_revision: 1
profile_content_hash: sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
basis_revision: example-source-revision
evidence_revision: example-evidence-revision
required_tracks: [api, ui]
tracks:
  api:
    status: designed|executed|passed|failed|blocked
    execution_mode: memory-application|real-http|live-acceptance
    data_namespace: example-api-namespace
    evidence_paths: []
    modified_paths: []
    commands: []
    browser_actions: []
    assertions: []
    blockers: []
    unverified_gates: []
    evidence_records: []
    persistence_required: false
    authoritative_readback: []
  ui:
    status: designed|executed|passed|failed|blocked
    execution_mode: browser-provider
    data_namespace: example-ui-namespace
    evidence_paths: []
    modified_paths: []
    commands: []
    browser_actions: []
    assertions: []
    blockers: []
    unverified_gates: []
    evidence_records: []
    persistence_required: false
    authoritative_readback: []
    browser_evidence: {}
```

`overall_status` is derived output, not a caller-supplied input. It is added only after all required
track results pass validation and must never be treated as `Completion`.

### Success result

聚合优先级固定为：

1. 任一必需轨道 `failed` -> `overall_status=failed`；
2. 否则任一必需轨道 `blocked` -> `overall_status=blocked`；
3. 否则所有必需轨道 `passed` -> `overall_status=passed`；
4. 否则存在任一轨道 `executed` -> `overall_status=executed`；
5. 否则 -> `overall_status=designed`。

该结果只表示场景和轨道状态。最终是否完成必须由 Completion Gate 独立判定。

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| 必需证据或 Profile/basis/evidence revision 缺失 | executed/blocked，视是否已开始执行 | 补采受影响证据；不得以单个 200、Job created、Toast 或截图代替完整证据 |
| API 与 UI 证据属于不同版本、namespace 或写入路径冲突 | blocked | 统一 Scenario 版本和隔离边界后重新执行受影响轨道 |
| 只完成 API 准备，未执行 UI When | designed 或 blocked | 不计入 UI 轨道通过；必须重新执行页面动作 |
| Completion Gate 发现 Acceptance 缺口 | Gate row remains issues/blocked | 按 Gate 和 repair loop 处理，不修改聚合规则凑成 passed |

### Verification

- Provider：各轨道 evidence format、`validate_evidence.py` 和 Bruce Verification Loop。
- Consumer：Checkpoint、Completion Gate review matrix。
- Required evidence：Scenario ID/version、Profile/basis/evidence revision、轨道状态、模式、命令/动作、证据引用、namespace、未验证门禁。

## browser-execution-ownership

- Change：clarified
- Provider：Codex Host + Bruce Browser Provider
- Consumers：Browser UI Verification Track、Verification Loop、Completion Gate
- Authoritative source：`skills/bruce/references/browser-provider.md`、`skills/bruce/references/plugin-boundary.md`
- Compatibility：compatible with `ego-lite|chrome` Provider；不引入新的浏览器执行者
- Authentication/authorization：浏览器登录态、task space、Captcha 和人工 handoff 由宿主 Provider 管理；子代理无 browser 工具

### Request, event, or input

```yaml
browser_execution:
  owner: main-agent-host
  provider: ego-lite|chrome
  visual_scope: none|browser-smoke|browser-layout
  scenario_id: FEATURE-AREA-001
  actions: real-user-actions-from-scenario
  evidence: browser_evidence
  verifier_role: evidence-only-review
  subagent_browser_access: forbidden
```

### Success result

`browser_evidence.provider` 必须等于配置的 Provider，并至少包含 target、session、真实 actions、visible result、capture time、basis revision 和 screenshot artifact；`browser-layout` 额外需要 viewport、geometry、overflow 和前后状态。

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| Provider 不可用或能力不足 | blocked/incomplete | 不切换 Provider，不降低 visual scope；修复能力后重新 preflight |
| 需要用户登录/Captcha/接管 | waiting_user 或 blocked | 按宿主 handoff/resume 流程；不绕过敏感操作 |
| 子代理尝试浏览器动作 | invalid dispatch | 拒绝 Packet 或停止该子任务；修正为主 Agent 执行 |
| API 代替页面动作 | invalid evidence | 页面证据无效，重新执行真实页面动作 |

### Verification

- Provider：`scripts/browser_provider.py`、宿主 browser capability、页面运行证据。
- Consumer：Browser UI Verification Track、Verifier、Completion Gate。
- Required evidence：Provider、target、session、actions、visible result、截图和 basis revision。

## model-routing-ownership

- Change：clarified
- Provider：Bruce Functional Agent resolver
- Consumers：Test Dispatch、API/UI 轨道、Verifier/Reviewer、Checkpoint
- Authoritative source：`skills/bruce/references/model-profiles.yaml`、`skills/bruce/references/functional-agent-contracts.md`、`scripts/functional_agent_profiles.py`
- Compatibility：不引入 `gpt-5.6-sol`；保留现有 Profile 和 fallback 规则
- Authentication/authorization：模型名称不得包含凭证样式值；模型可用性必须由宿主确认

### Request, event, or input

```yaml
routing_intent:
  track: api|ui|both|dispatch
  scenario_complexity: routine|cross-module|stateful|diagnostic
  required_capabilities:
    - repository-inspection
    - reproducible-verification
    - clean-context-review
  requested_profile: inspector|implementer|verifier|reviewer
```

Test Skill 不能使用私有的 `model-routing.md` 替换 Bruce resolver，也不能在 Packet 中指定 `gpt-5.6-sol`。当目标模型不可用时，只按 Bruce 已声明的 current-model fallback 或 blocked 规则处理，并记录 `model_resolution`。

### Success result

Subagent Packet 必须含 `model_resolution`，并满足对应 Functional Agent Profile 的 task kind、tools、context、output 和 write scope。Verifier 和 Reviewer 不得输出 Design/Completion/verdict/approval。

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| 请求 `gpt-5.6-sol` 或新增私有模型路由 | blocked/invalid contract | 删除该路由并重新通过 Bruce resolver；不得静默改用其他模型 |
| `gpt-5.6-luna` 使用非 `max` | invalid dispatch | 拒绝调度；修正 effort 后再派发 |
| 模型未确认可用 | fallback 或 blocked | 记录 effective model 和 degraded 状态；不得把 fallback 当作异构模型证明 |
| clean context 或 required tools 不可用 | blocked | 使用 Bruce resolver 的既定阻塞规则 |

### Verification

- Provider：`scripts/functional_agent_profiles.py` 和 Functional Agent contract tests。
- Consumer：Test Dispatch、所有需要 Subagent 的测试轨道和 Gate。
- Required evidence：requested profile、effective model、effort、resolution result、fallback reason（如有）。

## verdict-ownership

- Adapter/轨道只返回事实、轨道状态和证据。
- Test Dispatch 只返回场景级轨道聚合状态。
- Verification Run/Checkpoint 只记录进度、证据引用、阻塞和恢复。
- Design Gate 仍拥有设计准入判断。
- Completion Gate 仍是唯一 `Completion: pass|issues|blocked` 来源。
