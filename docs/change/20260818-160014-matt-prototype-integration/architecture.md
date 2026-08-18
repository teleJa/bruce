# Architecture：集成探索型原型能力

## Objective and scope

- Objective：在 Bruce 中新增一个问题驱动的探索型原型能力，并允许在边界冻结后把原型生成委托给 native subagent，以减少主 agent 的上下文占用。
- Included：`logic` 与 `ui-variants` 两种探索模式、主/子 agent 责任边界、探索结果到正式原型的提升规则、Bruce 能力路由、文档和契约测试。
- Excluded：修改 Open Design host/MCP、把探索原型直接作为生产真源、增加第三个 Gate、增加 scheduler/worker registry、安装第三方 Skill、生成具体产品原型。

## Repository evidence

- `skills/bruce/SKILL.md` 已允许 Codex 对边界明确、低耦合任务直接使用 native subagent，同时要求主 agent 负责 scope、ownership、integration 和 conflict resolution。
- `skills/write-prototype/SKILL.md` 已独占 grounded UI prototype 的 Open Design 生成、manifest、generated/confirmed snapshot 和 provenance 契约。
- `skills/design-gate/SKILL.md` 只接受经过 `prototype-manifest.md` 解析的确认原型作为下游实现真源。
- `skills/spawn-execute/SKILL.md` 仅服务 active Goal，不能被复用为普通探索原型的强制入口。
- `/Users/tele/skill_repo/mattpocock-skills/skills/engineering/prototype` 以 MIT 许可提供问题驱动、`logic`/`UI` 分支和 throwaway prototype 方法；本变更只做 Bruce 边界下的概念适配。

## Components and ownership

| Component | Existing stack/deliverable | Owns | Does not own |
|---|---|---|---|
| Bruce router | `skills/bruce/SKILL.md` | 根据问题选择探索或正式原型能力，决定是否可委托 | 生成原型细节、subagent 生命周期实现 |
| Explore Prototype | `skills/explore-prototype/` | 回答一个逻辑或 UI 方案问题，生成可丢弃原型与探索结论 | Open Design、生产实现、Design/Completion verdict |
| Write Prototype | `skills/write-prototype/` | 正式 grounded UI artifact、确认快照、provenance | 探索型多方案发散 |
| Codex main agent | host runtime | 冻结问题和边界、准备委托包、检查实际 diff、组织用户反馈与提升 | 把产品决策或门禁责任交给 subagent |
| Native subagent | host runtime | 在允许路径内生成并验证一个已冻结的原型切片 | 改 scope、选择产品方案、声明 readiness/completion |

## Data and control flow

1. User request -> Bruce task contract -> 判断是待探索问题还是正式 implementation-governing prototype。
2. 待探索问题 -> `explore-prototype` -> 选择 `logic` 或 `ui-variants`。
3. 若 question、mode、allowed paths、scenarios/variants 和 verification 均已冻结，main agent 可把 generation packet 委托给一个 native subagent；否则顺序执行。
4. Subagent -> prototype evidence packet -> main agent 检查实际文件、命令输出和运行结果。
5. User feedback -> 记录 `answered|needs-iteration|inconclusive`；探索代码仍为 throwaway。
6. 若探索结果要约束生产 UI -> 通过 `write-prototype` 导入或重建为有 manifest、确认快照和 provenance 的正式原型 -> Design Gate。
7. 生产实现完成后仍由 Completion Gate 作唯一完成决定。

## Decisions

### 新增独立 `explore-prototype` supporting skill

- Chosen：新增独立 Skill，保留 `write-prototype` 的正式原型职责。
- Rationale：探索型原型追求快速回答问题，正式原型追求 grounded artifact 和证据闭环；合并会让轻量探索承担不必要成本，也可能让 throwaway code 被误当作生产真源。
- Rejected：直接扩写 `write-prototype`，因为会混合两种不同触发条件、产物生命周期和完成标准。
- Reversibility：删除新增 Skill 和 Bruce 路由即可，Open Design 契约不受影响。

### 允许生成委托，但不委托决策和门禁

- Chosen：仅在 generation packet 完整且文件所有权不冲突时委托单个 bounded worker。
- Rationale：原型代码和变体生成消耗大量局部上下文，适合下放；问题选择、用户反馈和跨产物证据需要主 agent 的连续上下文。
- Rejected：把整个原型工作交给 subagent，因为会丢失需求权威、用户确认和 Design Gate 责任链。
- Reversibility：工具不可用或边界不满足时顺序执行，不改变产物契约。

### 探索原型不能直接治理生产实现

- Chosen：探索结果只有经过 `write-prototype` 的导入/确认契约后，才能作为 Design Gate 的 UI prototype candidate。
- Rationale：Matt 方法明确把 prototype 视为 throwaway；Bruce 需要额外的 safety、visual、provenance 和 confirmation 证据。
- Rejected：给探索原型新增简化 Gate，因为 Bruce 只保留 Design Gate 和 Completion Gate 两个决定。
- Reversibility：未来可扩展 `write-prototype` 的 import adapter，但不改变 Gate 数量。

## Contracts

- [`api-contracts.md`](api-contracts.md#explore-prototype-v1)
- [`api-contracts.md`](api-contracts.md#prototype-generation-delegation-v1)

## Cross-cutting behavior

- Compatibility/versioning：新增可选 Skill 和路由；已有 `write-prototype`、Goal 和 Gate 调用保持兼容。
- Authentication/authorization：不新增权限机制；继续由 Codex host 管理工具和 subagent。
- Failure and recovery：subagent 不可用或失败时，仅对缺失 generation slice 顺序降级；未知 side effect 按 Bruce L0-L4 处理。
- Observability：subagent 回传 changed files、commands/results、assumptions、gaps 和 status；main agent 重新检查实际 workspace。
- Rollout/rollback：Skill、路由、文档和测试原子更新；回滚不涉及数据迁移。

## Verification impact

- 模式路由 -> 新契约测试检查 `logic` 与 `ui-variants` 的互斥条件和对应 reference。
- 委托边界 -> 测试检查 generation packet、evidence packet、顺序降级和 main-agent ownership。
- 正式原型隔离 -> 测试检查探索结果必须通过 `write-prototype` 才能进入 Design Gate。
- 包完整性 -> Skill validator、插件 validator、完整 unittest 和 `git diff --check`。

## Open decisions

- None。
