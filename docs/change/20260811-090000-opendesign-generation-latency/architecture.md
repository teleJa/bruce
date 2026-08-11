# Architecture：Open Design 原型生成编排提速

## 目标与范围

- 目标：降低 Bruce `write-prototype` 启动前编排和运行态观测的上下文与等待开销，同时保持现有证据、溯源和失败边界。
- 包含：选择性 Open Design preflight、单份精简生成输入、repository visual authority 的方向跳过、上下文哈希与修订增量、低频增量运行观测。
- 不包含：Open Design 桌面端/CLI 实现或升级、MCP 安装配置、provider 模型路由、产品前端实现、生成 artifact 的完成判定。

## 仓库证据

- `skills/write-prototype/SKILL.md`：当前要求全量 `list_skills`/`list_plugins`/`list_agents`，同步多份上下文并重复读取，且只定义完整 `get_run` 轮询。
- `skills/write-prototype/templates/prototype-manifest.md`：已有选择、上下文身份、运行状态和溯源字段，可扩展记录 discovery/context/observation 策略。
- `tests/test_prototype_contract.py`：现有 Open Design 能力、preflight、运行和 lineage 契约测试。
- `docs/change/20260730-205834-opendesign-prototype-integration/architecture.md`：Bruce 保持 skills-only，Open Design 执行由宿主拥有；本次不改变该边界。

## 组件与所有权

| 组件 | 现有交付物 | 负责 | 不负责 |
|---|---|---|---|
| `skills/write-prototype/` | Bruce supporting skill | 选择性 preflight、上下文包策略、方向跳过策略、轮询/观测规则 | Open Design CLI/MCP 实现、模型路由 |
| `prototype-manifest.md` | 变更目录内 manifest | 记录 capability 选择、context hash、observation mode、run lineage | 第二套状态源、provider 调度 |
| Codex/Open Design host | 当前宿主能力 | 执行逻辑 MCP、创建项目、启动和查询 run | Bruce 完成或设计判定 |
| `tests/test_prototype_contract.py` | 静态契约回归 | 防止全量 discovery、重复上下文和模糊运行状态规则回退 | 真实 provider E2E |

## 数据与控制流

1. 任务合同确定 `agent/model/skill/plugin/design-system` 后，preflight 只验证已选对象；未选择时才发现候选，并如实记录 generation skill 是可复用模板还是仅包装说明。
2. existing-product extension 提取一份 `generation-input.md`（或等价的单一输入身份），由 brief、UI contract、视觉断言和 baseline 的必要事实组成；详细证据仍保留在 change 目录，但不全部重复注入 provider。
3. `repository/runtime` 视觉权威明确时写入 `direction_selection=skip`；只有无权威且宿主声明支持时才允许方向库调用。
4. 计算稳定 `context_hash`。首轮同步精简输入；修订只同步变化的输入和 baseline diff，并复用 provider 支持的 conversation/project lineage，不重新复制未变化上下文。
5. run 观测采用低频（约 45–60 秒）查询；优先消费增量事件或摘要，状态变化时才读取完整 run。`reconnecting`、`tool_error`、`stalled_candidate` 不再伪装成普通 `running`。

## 决策

### 选择性 discovery，而不是默认全量枚举

- 选择：明确传入的 Agent、skill、plugin、design-system 只做定点能力确认；仅对缺失选择的字段执行 discovery。`plugin=none` 或 `design-system=none` 不调用对应列表。
- 理由：本轮任务已明确 `codex/gpt-5.6-terra/artifacts-builder/none/none`；全量列表只产生无关上下文。
- 否决：继续全量枚举，理由是“记录选择依据”不等于“把全部候选注入模型上下文”。
- 可逆性：manifest 增加策略字段即可恢复 discovery，不改变 provider API。

### 单份精简生成输入与稳定上下文哈希

- 选择：provider 侧以单份精简输入为主，详细文档作为本地证据；manifest 记录 `context_hash` 与 `context_files`。
- 理由：避免外层已提炼内容被内层再次逐份理解，同时保留可追溯源文件。
- 否决：删除详细证据或把所有源码直接拼入 prompt；前者损害审计，后者扩大上下文。
- 可逆性：hash 不匹配时可退回完整同步，并在 manifest 记录原因。

### 视觉方向按权威条件跳过

- 选择：repository/runtime visual authority 存在、plugin/design-system 均为 none 时，明确写入 `direction_selection=skip`，禁止调用 `tools directions`。
- 理由：现有产品扩展不能让 provider 默认方向覆盖仓库 UI 约束；也避免依赖待升级的 Open Design CLI 子命令。
- 否决：在每次 run 中试探 `tools directions`；这会制造确定性 CLI 错误。
- 可逆性：升级后宿主声明 capability 且确实无视觉权威时可恢复调用。

### 增量运行观测

- 选择：以 `get_run` 为兼容基线，优先使用宿主提供的事件增量/摘要；记录 `observation_mode`、`last_event_id`、`last_progress_at` 和细分状态。
- 理由：当前宿主可能没有 `wait_run`，Bruce 不能自行增加 MCP；但可避免嵌套长等待和重复完整对象。
- 否决：把轮询封装成新的 Bruce CLI/MCP；违反 skills-only 边界。
- 可逆性：新宿主提供增量接口后只替换观测步骤，manifest 状态兼容。

## 契约

- [api-contracts.md](api-contracts.md#prototype-orchestration-contract)

## 横切行为

- 兼容性：新增字段和策略均为 additive；旧 manifest 缺失字段按 `legacy/unknown` 解释，不阻断历史审计。
- 认证/授权：不新增凭证或权限；Open Design 认证仍由宿主负责。
- 失败恢复：明确选择但无法验证时 `blocked-before-generation`；方向 capability 不支持时记录 `skip` 或 `partial`，不执行未知命令；连续无增量只标记 `stalled_candidate`，不自动取消 run。
- 可观测性：manifest 记录 discovery mode、context hash、direction policy、observation mode、last event/progress、provider细分状态和错误摘要。
- 发布/回滚：仅发布 Bruce skill/docs/tests；Open Design 升级独立发布。回滚删除新增策略文本和字段，不改 provider 项目或运行。

## 验证影响

- 明确选择不全量 discovery -> `tests/test_prototype_contract.py` 静态契约测试。
- repository authority 跳过 directions -> skill/brief/manifest 文本契约测试。
- 精简输入与 context hash -> 模板字段和 refinement 规则测试。
- 低频增量观测、reconnecting/tool error/stalled 状态 -> skill/manifest 状态契约测试。
- Open Design CLI 升级兼容性 -> 宿主侧另行执行真实 preflight；本仓库不虚构 E2E 通过。

## 开放决策

- 无。Open Design 桌面端/CLI 的升级版本与发布时间由用户另行安排，不属于本次 Bruce 代码变更。
