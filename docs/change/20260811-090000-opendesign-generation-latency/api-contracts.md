# API 与事件契约：Open Design 原型生成编排提速

## prototype-orchestration-contract

- 变更：`changed`；Bruce `write-prototype` 与 Open Design host 之间的调用编排和 manifest/file contract 变更。
- Provider：Codex host 通过逻辑 Open Design MCP 能力。
- Consumers：`skills/write-prototype/`、`prototype-manifest.md`、Design Gate/Completion Gate 审计。
- 权威来源：`skills/write-prototype/SKILL.md`、`skills/write-prototype/templates/prototype-manifest.md`。
- 兼容性：additive；缺失新字段的旧 manifest 按 `legacy/unknown` 处理。
- 认证/授权：沿用宿主 Open Design MCP；Bruce 不存储或传递凭证。

### Request / input

```text
preflight:
  selections: agent, model, generation_skill, visual_plugin, design_system
  discovery_mode: selective | full | legacy
  generation_skill_readiness: clear | partial | blocked
  direction_selection: skip | provider-capability | legacy-unknown
context:
  context_hash: sha256 digest after input materialization
  context_files: one compact provider input plus local evidence references
  sync_mode: full | incremental | legacy
observation:
  mode: summary | event-incremental | full-run-legacy
  poll_interval_seconds: 45..60 when polling is required
```

### Success result

```text
manifest:
  discovery_mode
  direction_selection
  context_hash
  context_files
  sync_mode
  observation_mode
  last_event_id
  last_progress_at
  provider_state: queued | thinking | working | reconnecting | degraded |
                 stalled_candidate | succeeded | failed | canceled
```

`running` may remain as a legacy provider value, but Bruce must preserve a more specific observed
state when `error`, event type, or progress timestamp proves it.

### Errors and recovery

| 条件 | 结果 | 重试/幂等规则 |
|---|---|---|
| Explicit selection cannot be verified | `blocked-before-generation` | Do not start or resubmit a run |
| `plugin=none` / `design-system=none` with repository visual authority | `direction_selection=skip` | Do not call `tools directions` |
| Host does not expose direction capability | `partial` or `skip` based on visual authority | Do not probe unknown CLI commands |
| Context hash unchanged on refinement | `sync_mode=incremental` | Reuse stable context; send only changed input |
| Provider reconnecting/high demand | `provider_state=reconnecting` | Continue bounded observation; no duplicate `start_run` |
| Tool output reports unsupported command | `provider_state=degraded` | Record error; repair host contract before another run |
| No event/progress across bounded polls | `stalled_candidate` | Inspect state; do not cancel without user request |

### Verification

- Provider/host：升级 Open Design 后执行真实 capability preflight；验证 `tools directions` 仅在 capability 声明且无视觉权威时调用。
- Consumer：静态契约测试必须证明选择性 discovery、skip policy、context hash、incremental sync 和细分 observation 状态存在。
- Runtime boundary：本仓库测试不声称真实 Open Design MCP 生成、artifact E2E 或浏览器视觉通过。
