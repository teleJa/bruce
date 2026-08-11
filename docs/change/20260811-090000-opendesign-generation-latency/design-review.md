# Design review：Open Design 原型生成编排提速

## Candidate matrix

| Candidate | Applicability | Delivery | Path | Evidence |
|---|---|---|---|---|
| requirement or clarification | skipped | skipped | none | 用户已明确同意按前述问题优先优化，无新增业务规则 |
| architecture.md | required | generated | `docs/change/20260811-090000-opendesign-generation-latency/architecture.md` | Bruce skills-only 边界、现有 `write-prototype` preflight/manifest/polling 契约 |
| api-contracts.md | required | generated | `docs/change/20260811-090000-opendesign-generation-latency/api-contracts.md` | `write-prototype` 与 Open Design host 的跨边界调用和 manifest/file contract |
| table-design.md | skipped | skipped | none | 不涉及数据库或持久化 schema |
| plan.md | skipped | skipped | none | 当前对话已有最小实施计划；未要求持久化 handoff |
| test-plan.md | skipped | skipped | none | 采用现有静态契约/插件验证，不新增跨组件测试设计 |
| UI prototype | skipped | skipped | none | 本次修改生成编排，不生成或确认产品 UI 原型 |

## Readiness checks

- 现有能力边界已核对：Bruce 不实现 MCP、CLI、daemon 或 provider adapter。
- 选择性 discovery、方向跳过、context hash、incremental sync、观测细分状态均有明确字段和失败行为。
- 旧 manifest 兼容规则已写明；新字段只增不删。
- Open Design CLI 升级由宿主侧验证，本仓库不把静态测试写成 live E2E 证据。
- 未发现会改变产品业务范围、数据库、权限或生产 API 的遗漏。

## Evidence boundary

- Designed：skill、manifest、host 编排契约和静态回归规则。
- Executed：待实现后运行静态测试、插件验证和 diff 检查。
- Unexecuted：真实 Open Design 升级、MCP capability preflight、生成 artifact、Chrome 视觉验收。

## Review mode

- `main-agent`

## Decision

Design: pass
