# API and file contracts：探索型原型集成

## explore-prototype-v1

- Change：`added`
- Provider：`skills/explore-prototype/SKILL.md`
- Consumers：Bruce router、Codex main agent、native subagent、contract tests
- Authoritative source：`skills/explore-prototype/SKILL.md`
- Compatibility：additive optional capability；不改变 `write-prototype` 输入输出
- Authentication/authorization：none；遵循 Codex host 权限

### Request, event, or input

```text
prototype_question: <one concrete uncertainty>
mode: logic | ui-variants
allowed_paths: <bounded repository paths>
excluded_paths: <production or unrelated paths>
repository_context: <entry point, components, theme/data anchors>
acceptance:
  logic: <happy, edge, illegal scenarios>
  ui-variants: <2-5 structurally different variants>
verification: <double-click/run command and visible checks>
```

### Success result

```text
status: answered | needs-iteration | inconclusive
question: <exact question>
mode: logic | ui-variants
artifact_paths: <throwaway prototype paths>
run_instructions: <one direct action or command>
observations: <what the prototype demonstrated>
decision: <validated answer, or none>
production_promotion: not-promoted | requires-write-prototype
known_gaps: <remaining uncertainty>
```

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| 问题无法归入 logic 或 ui-variants | 返回一个 blocking ambiguity | 主 agent 最多询问一个关键问题 |
| 缺少现有页面/组件上下文 | 不声明高保真 UI 探索 | 补充 bounded repository/runtime evidence 后重试 |
| 原型要执行真实 mutation 或 persistence | 停止并缩小为 stub/in-memory | 需要真实副作用时回到 Bruce task contract |
| 探索结果要治理生产实现 | `requires-write-prototype` | 通过正式 import/confirmation 契约提升 |

### Verification

- Provider：`python3 -m unittest tests.test_explore_prototype_contract -v`
- Consumer：`python3 -m unittest tests.test_prototype_contract tests.test_workflow_routing -v`

## prototype-generation-delegation-v1

- Change：`added`
- Provider：Codex main agent under `skills/explore-prototype/SKILL.md`
- Consumers：one native subagent and Bruce integration flow
- Authoritative source：`skills/explore-prototype/SKILL.md`
- Compatibility：optional optimization；subagent unavailable 时保持顺序语义
- Authentication/authorization：由 Codex host 管理；Bruce 不增加 scheduler、registry 或 model selector

### Request, event, or input

```text
generation_packet:
  question: <frozen question>
  mode: logic | ui-variants
  allowed_paths: <exclusive bounded paths>
  excluded_paths: <explicit exclusions>
  repository_facts: <only facts required to generate>
  scenario_or_variant_contract: <complete expected cases>
  run_and_verification: <commands/actions and expected observable result>
  prohibited_side_effects: <network, persistence, production mutations, unrelated files>
```

### Success result

```text
prototype_evidence_packet:
  status: generated | needs-input | failed
  changed_files: <paths>
  commands_and_results: <actual checks and outcomes>
  assumptions: <explicit assumptions>
  gaps: <unverified facts>
  user_feedback_needed: <specific feedback target>
```

主 agent 必须对实际 workspace 和命令证据重新检查；subagent 的 `generated` 不是 Design 或 Completion 证据。

### Errors and recovery

| Condition | Result | Retry/idempotency behavior |
|---|---|---|
| native subagent unavailable | main agent sequential fallback | 不改变 artifact shape |
| allowed paths 与其他任务重叠 | 不委托 | 主 agent 顺序处理共享 ownership |
| subagent 改变 scope 或产品决策 | 拒绝该部分结果 | 收窄 packet 后重新生成或主 agent 接管 |
| subagent 验证失败 | 返回实际失败和 gaps | 按 Bruce L0-L2 在最小 slice 修复或重规划 |

### Verification

- Provider：契约测试检查 packet 字段与 responsibility boundary。
- Consumer：主 agent 检查实际 diff、运行命令和用户可操作结果。
