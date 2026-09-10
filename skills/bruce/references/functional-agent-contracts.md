# Functional Agent 与 Packet 合同 v1

## 1. 公共字段

每一次原生 Subagent 委派必须先选择一个 `profile_id`，并提交 `schema_version: 1` 的 `task_packet`。Profile 是内部合同，不是可直接调用的顶层 Skill；主 Agent 仍负责综合、依赖顺序、冲突、业务决定、集成和最终 Gate。

```yaml
schema_version: 1
profile_id: inspector|implementer|prototype-generator|verifier|reviewer
task_packet:
  task_id: string
  task_kind: inspect|implement|prototype_generate|verify|review|throwaway_prototype
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

### 委派消息语言

所有 Profile 的初次派发、补充指令和恢复消息都遵循
[共享委派语言规则](delegation-contract.md)：用户明确指定的语言优先，
否则自然语言说明沿用用户当前请求语言；中文请求默认简体中文。`objective`、约束、验收说明、
`stop_conditions` 和结果解释使用该语言，键名、枚举、路径、命令及原始引文保持不变。
该规则通过现有文本字段或消息正文表达，不增加 `language` 字段，也不翻译机器协议。

## 2. Profile roles

| Profile ID | 允许职责 | 禁止职责 | 输出 |
|---|---|---|---|
| `inspector` | 只读收集仓库事实、边界、调用关系、风险证据 | 写入、删除、部署、业务决策、Gate | `task_evidence_packet` |
| `implementer` | 在 Packet 允许路径内实现并运行声明的检查 | 越权路径、权限代理、部署、push、最终 Gate | `task_evidence_packet` |
| `prototype-generator` | 使用已冻结的原型上下文驱动一个 Open Design 生成运行 | 本地实现、模型回退、产品决策、Gate | `task_evidence_packet` |
| `verifier` | 重现验收、确认证据是否真实、标记证据缺口 | 修改工作区、独立最终审查、Gate verdict | `verification_packet` |
| `reviewer` | clean context 下检查实现/计划问题并返回 findings | 修改工作区、替代 Verifier、Gate verdict | `review_packet` |

`explore-prototype` 的一次性 generation worker 复用 `implementer`，`task_kind=throwaway_prototype`。正式 `write-prototype` 的 Open Design generation worker 使用 `prototype-generator`，`task_kind=prototype_generate`；该 Profile 的 `fallback=blocked`，所以必须以已解析的配置模型运行，不能继承当前模型。两条路径都使用现有 `task_evidence_packet`，不新增第五种输出类型。

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
review_mode: independent
review_mode_reason: mandatory-independent-review|explicit-independent-request|critical-risk|guarded-multi-component-contract|guarded-migration-rollout|guarded-semantic-ambiguity|guarded-weak-evidence|guarded-repeated-repair|guarded-broad-security-data-impact
review_basis:
  task_id: current task id
  dispatch_id: native reviewer agent/run id from host receipt
  basis_revision: sha256:<immutable reviewed artifact, acceptance, and evidence snapshot hash>
findings: [{severity: critical|high|medium|low, path: string, evidence: string, issue: string}]
review_matrix: [{acceptance_id: string, path: string, required_layer: string, evidence: string, result: pass|finding|incomplete}]
model_resolution: model_resolution
gate_verdict: absent
```

Reviewer 必须是独立子代理，使用 `context.inherit=none` 的 clean context；主 Agent 自检不能替代该审查。已完成的 `review_packet` 必须有与当前审查依据对应的非空 `review_matrix`，`model_resolution` 必须为 `resolved`，不得以 blocked/fallback 模型解析声明审查已执行。

Reviewer 只回答“实现或计划还存在什么问题”，不得返回 `Design`、`Completion`、`verdict` 或 `approval` 字段。最终仍只有 `Design: pass|blocked` 与 `Completion: pass|issues|blocked`。

### 审查结果与当前依据绑定

`review_basis` 必须来自调用方：`task_id` 来自当前任务，`dispatch_id` 来自原生 reviewer 派发回执，
`basis_revision` 为本次审查的工件/diff、适用验收与证据快照的 `sha256:` 哈希；仅 Git HEAD 不足以覆盖未提交改动。
修复、验收或相关证据改变时更新快照，不把旧审查包当成新结果。相同 reviewer 复核后可以沿用 dispatch_id，
但必须返回新的 basis_revision。记录保存在现有任务/审查证据中，不新建调度器或独立 ledger。

Gate/plan-review 调用方必须使用 `scripts/functional_agent_profiles.py` 的 `validate_review_for_basis`，
将当前 task_id、实际 dispatch_id、当前 basis_revision、保留的预派发 model_resolution 和期望 review_subject
作为独立输入进行消费校验；不能从返回包自己提取这些值作为“期望值”。形状校验 `validate_output_packet` 不能替代它。
错误任务、错误派发、旧快照、模型记录不匹配或非 completed 结果均不能通过消费校验；旧版无绑定的审查包
可以作为历史资料阅读，但不能供新 Gate 决策复用。该函数只校验调用方持有证据的一致性，不认证宿主回执真伪。

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

- 目标模型经宿主能力证据确认可用：传入 `model`，`resolution_result=resolved`。`prototype-generator` 的模型只能来自其 built-in/project/user Profile 配置，不能由 Task Packet 覆盖。
- 允许回退的非 reviewer Profile，目标模型不可用且 `fallback=current`：省略 `model` 以继承当前模型，`fallback_used=true`、`capability_status=degraded`、`resolution_result=fallback`。
- 当前模型不可用、clean context 为 `required` 但不可用、工具不满足 required、任务显式禁止 fallback，或 Profile 声明 `fallback=blocked` 且配置模型不能被宿主确认：`resolution_result=blocked`。
- `reviewer` 的 `fallback=blocked` 是不可被 task/project/user override 放宽的审查边界。模型不可用或未确认时暂停受影响审查，请用户明确指定一个可用替代模型；收到明确选择后以现有 override 机制重新解析和核对宿主能力。不得自动换模型、继承当前模型、让主 Agent 自审或把 `verifier` 当作替代 reviewer。其他 Profile 的回退策略不受此条改变。无需增加 `model_diversity` 字段；实际模型仍记录于 `model_resolution.effective_model`。
- 配置文件内容不能证明真实模型已经生效；宿主返回的实际模型和 smoke packet 才是运行证据。

## 5. Host mapping boundary

Resolver 只生成宿主调用所需的可选参数：`model`（仅 resolved 时存在）和 `reasoning_effort`，以及不透明的 `model_resolution` 记录。它不创建 scheduler、worker registry、provider runtime 或权限代理。调用方必须把 Packet 和解析记录一起传给原生 Subagent；不能在 Skill 内自行选择模型或静默切换。
