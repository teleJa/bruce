# API and file contracts: Bruce 功能型 Agent 与 Model Profile 路由

## functional-agent-profile-v1

- Change: `added`
- Provider: `scripts/functional_agent_profiles.py` 与 `skills/bruce/references/model-profiles.yaml`
- Consumers: `skills/inspect-parallel`、`skills/spawn-execute`、`skills/explore-prototype`、`skills/completion-gate`、`skills/plan-review`、`skills/design-gate`、主 Agent
- Authoritative source: 本变更目录 `architecture.md` 与仓库内 validator/registry
- Compatibility: additive；`schema_version: 1`，未知字段和错误版本 fail closed
- Authentication/authorization: 不新增认证；路径和工具权限由 Packet 与 Profile 校验

### Request, event, or input

```yaml
schema_version: 1
profile_id: inspector|implementer|verifier|reviewer
task_packet:
  task_id: string
  objective: string
  context: {inherit: none|task|author, sources: [string]}
  tools: {allow: [string], deny: [string]}
  allowed_paths: [repository-relative path]
  model_capabilities: {required: [string], preferred: [string], independence: required|preferred|none}
  evidence: {acceptance_ids: [string], required: [string]}
  output: task_evidence_packet|verification_packet|review_packet
  stop_conditions: [string]
  model_override: string|null
```

### Success result

Every output packet carries its own `model_resolution`; the packet type determines the allowed role and evidence fields.

```yaml
model_resolution:
  requested_profile: string
  configured_model: string|null
  effective_model: string|null
  fallback_used: boolean
  fallback_reason: string|null
  capability_status: resolved|degraded|blocked
  resolution_result: resolved|fallback|blocked
  source: task|project|user|built-in|current

# Exactly one of the following packet shapes is returned.
task_evidence_packet:
  status: completed|blocked|failed
  output_type: task_evidence_packet
  changed_files: [string]
  commands: [{command: string, result: pass|fail|blocked, evidence: string}]
  evidence: [string]
  assumptions: [string]
  evidence_gaps: [string]
  model_resolution: model_resolution  # requested_profile: inspector|implementer
  gate_verdict: absent
verification_packet:
  status: completed|blocked|failed
  output_type: verification_packet
  acceptance_ids: [string]
  scenario_results: [object]
  repro_commands: [string]
  evidence_revision: string
  model_resolution: model_resolution  # requested_profile: verifier
  gate_verdict: absent
review_packet:
  status: completed|blocked|failed
  output_type: review_packet
  review_subject: implementation|plan|design
  review_mode: main-agent|independent
  review_mode_reason: string
  findings: [object]
  review_matrix: [object]
  model_resolution: model_resolution  # requested_profile: reviewer
  gate_verdict: absent
```

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| Profile/Packet schema invalid | `blocked` with `profile_invalid` or `packet_invalid` | 修复合同后重试；不调用宿主 |
| 目标模型不可用且 `fallback=current` | `fallback` + `capability_status=degraded`，省略 `model` 参数 | 继承 current model；不得宣称异构 |
| 目标模型不可用且 fallback 禁止 | `blocked` | 需提供可用模型或放宽任务策略 |
| current model 不可用 | `blocked` | 不重放未知 Subagent 运行 |
| clean context/tool unavailable | `degraded` 或 `blocked`，取决于 `independence`/能力要求 | 必须记录原因，不能静默降级 |
| changed path 超出 `allowed_paths` | `blocked`，`path_forbidden` | 不接受越权变更 |
| Verifier/Reviewer 返回 Gate terminal field | `blocked`，`authority_violation` | 丢弃该 Packet，Gate 重新综合 |

### Verification

- Provider: `python3 scripts/validate_functional_agents.py`、`tests/test_functional_agent_profiles.py`。
- Consumer: Skill 静态路由测试覆盖四类 Profile、Packet 类型、禁止字段和 Profile ID 完整映射。

## profile-override-files-v1

- Change: `added`
- Provider: Resolver 的文件读取边界
- Consumers: Bruce 主 Agent 与相关 Skill
- Authoritative source: built-in registry；user/project 文件是可选覆盖
- Compatibility: additive；覆盖只允许已存在 Profile 的非结构性字段，拒绝新增 Profile、结构字段、凭证和绝对路径
- Authentication/authorization: 用户文件由当前用户控制；项目文件不得包含个人凭证、token 或本机路径

### Request, event, or input

```yaml
version: 1
profiles:
  reviewer:
    default_model: model-name
    reasoning_effort: medium
    fallback: current
```

### Success result

Resolver 返回已合并 Profile 与 `model_resolution`，并标明来源层级；不写回用户/项目文件。

### Errors and recovery

非法 YAML、未知 Profile、结构字段覆盖、绝对路径或凭证 token -> `blocked` / `profile_invalid`；修复配置后重试。

### Verification

- Provider: resolver fixture tests for built-in/user/project/task precedence and invalid override.
- Consumer: `spawn_agent` 参数静态合同只允许由解析结果提供 `model`/`reasoning_effort`，不允许 Skill 自建 selector/runtime。
