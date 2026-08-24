# Functional Agent 与 Packet 合同 v1

## 1. 公共字段

每一次原生 Subagent 委派必须先选择一个 `profile_id`，并提交 `schema_version: 1` 的 `task_packet`。Profile 是内部合同，不是可直接调用的顶层 Skill；主 Agent 仍负责综合、依赖顺序、冲突、业务决定、集成和最终 Gate。

```yaml
schema_version: 1
profile_id: inspector|implementer|verifier|reviewer
task_packet:
  task_id: string
  task_kind: inspect|implement|verify|review|throwaway_prototype
  objective: non-empty string
  context:
    inherit: none|task|author
    sources: repository-relative paths or evidence ids
  tools:
    allow: declared tool ids
    deny: declared forbidden tool ids
  allowed_paths: repository-relative paths; empty for read-only roles
  model_capabilities:
    required: capability ids
    preferred: capability ids
    independence: required|preferred|none
  evidence:
    acceptance_ids: stable acceptance ids
    required: concrete commands, files, or runtime evidence
  output: task_evidence_packet|verification_packet|review_packet
  stop_conditions: non-empty list
  model_override: optional concrete model name
```

未知字段、绝对路径、空目标、未知 Profile、错误 `schema_version` 或不匹配的 output 类型必须 fail closed。`allowed_paths` 必须是仓库相对路径；路径校验使用规范化后的 path containment，不接受 `..` 越权。

## 2. Profile roles

| Profile ID | 允许职责 | 禁止职责 | 输出 |
|---|---|---|---|
| `inspector` | 只读收集仓库事实、边界、调用关系、风险证据 | 写入、删除、部署、业务决策、Gate | `task_evidence_packet` |
| `implementer` | 在 Packet 允许路径内实现并运行声明的检查 | 越权路径、权限代理、部署、push、最终 Gate | `task_evidence_packet` |
| `verifier` | 重现验收、确认证据是否真实、标记证据缺口 | 修改工作区、独立最终审查、Gate verdict | `verification_packet` |
| `reviewer` | clean context 下检查实现/计划问题并返回 findings | 修改工作区、替代 Verifier、Gate verdict | `review_packet` |

`explore-prototype` 的 generation worker 复用 `implementer`，`task_kind=throwaway_prototype`，不能新增第五类 P0 Agent；Explore Skill 可以在 worker Packet 之外维护自己的 `prototype_evidence_packet` 包装，不属于 Functional Agent 输出类型。

## 3. 输出 Packet

### task_evidence_packet

```yaml
schema_version: 1
status: completed|blocked|failed
output_type: task_evidence_packet
changed_files: [repository-relative paths]
commands: [{command: string, result: pass|fail|blocked, evidence: string}]
evidence: [string]
assumptions: [string]
evidence_gaps: [string]
model_resolution: model_resolution
gate_verdict: absent
```

### verification_packet

```yaml
schema_version: 1
status: completed|blocked|failed
output_type: verification_packet
acceptance_ids: [string]
scenario_results: [{acceptance_id: string, result: pass|fail|blocked, evidence: [string], gaps: [string]}]
repro_commands: [string]
evidence_revision: string
model_resolution: model_resolution
gate_verdict: absent
```

Verifier 只回答“证据是否真实重现验收”，不得返回 `Design`、`Completion`、`verdict` 或 `approval` 字段。

### review_packet

```yaml
schema_version: 1
status: completed|blocked|failed
output_type: review_packet
review_subject: implementation|plan|design
review_mode: main-agent|independent
review_mode_reason: none|explicit-independent-request|critical-risk|guarded-multi-component-contract|guarded-migration-rollout|guarded-semantic-ambiguity|guarded-weak-evidence|guarded-repeated-repair|guarded-broad-security-data-impact
findings: [{severity: critical|high|medium|low, path: string, evidence: string, issue: string}]
review_matrix: [{acceptance_id: string, path: string, required_layer: string, evidence: string, result: pass|finding|incomplete}]
model_resolution: model_resolution
gate_verdict: absent
```

Reviewer 只回答“实现或计划还存在什么问题”，不得返回 `Design`、`Completion`、`verdict` 或 `approval` 字段。最终仍只有 `Design: pass|blocked` 与 `Completion: pass|issues|blocked`。

## 4. Model resolution

覆盖层顺序固定为：task explicit override > project `project/.bruce/model-profiles.yaml` > user `~/.codex/bruce/model-profiles.yaml` > built-in registry > current model fallback。

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
```

- 目标模型经宿主能力证据确认可用：传入 `model`，`resolution_result=resolved`。
- 目标模型不可用且 `fallback=current`：省略 `model` 以继承当前模型，`fallback_used=true`、`capability_status=degraded`、`resolution_result=fallback`。
- 当前模型不可用、clean context 为 `required` 但不可用、工具不满足 required，或任务显式禁止 fallback：`resolution_result=blocked`。
- 配置文件内容不能证明真实模型已经生效；宿主返回的实际模型和 smoke packet 才是运行证据。

## 5. Host mapping boundary

Resolver 只生成宿主调用所需的可选参数：`model`（仅 resolved 时存在）和 `reasoning_effort`，以及不透明的 `model_resolution` 记录。它不创建 scheduler、worker registry、provider runtime 或权限代理。调用方必须把 Packet 和解析记录一起传给原生 Subagent；不能在 Skill 内自行选择模型或静默切换。
