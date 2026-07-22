---
run: "20260710-105828-bruce-workflow-flexibility"
task: "将 Bruce v4 简化为 Codex 原生执行的风险驱动工作流插件"
plan: plan.md
created: "2026-07-10T10:58:28+08:00"
updated: "2026-07-18"
---

# 测试计划：将 Bruce v4 简化为 Codex 原生执行的风险驱动工作流插件

## 测试原则

- 测试 Bruce 的 workflow contract 和 plugin package，不测试 Codex 自己的 sandbox、权限系统或 subagent runtime。
- 单元测试可以使用 fixture 表示 Codex tool/subagent 返回结果，但不得据此声称验证了宿主安全能力。
- 通过 repo marketplace 运行插件安装命令、修改全局 Codex 配置或重启 App 属于用户确认后的手工 smoke，不放入默认自动测试；创建和静态校验仓库内 marketplace 文件属于实现范围。
- 每个计划 task 恰好对应一个同名 anchor 和一组可执行验证入口。

## bruce-v4-1
- **feature_bearing**: true
- **regression_source**: 当前仓库缺少标准 `.codex-plugin/plugin.json`，同时把根 SKILL 和镜像目录当成源码，没有明确 Codex/plugin 责任边界。
- **state_intent_matrix**:
  - valid manifest + `skills: ./skills/` + Bruce skill exists -> pass
  - manifest 声明 MCP/app/hooks/公共 CLI -> contract failure
  - marketplace source 指向插件根 -> pass
  - marketplace path 越界、递归镜像或目标不存在 -> fail
- **scenarios**:
  - happy: 最小 manifest 和 repo marketplace 被解析，`skills/bruce/SKILL.md` 可定位
  - edge: supporting skills 可被同一 manifest 包含，但 Bruce 仍是文档中的唯一主工作流入口
  - error: 缺 manifest、绝对 component path、错误 `skills` 目录、HostAdapter/SandboxBackend 被列为 plugin capability 均失败
  - integration: manifest、marketplace、README 的 plugin name/version/skills path 一致
- **verification**: `python3 -m unittest discover -s tests -p 'test_plugin_manifest.py'`

## bruce-v4-2
- **feature_bearing**: true
- **regression_source**: 旧 Bruce 用 express/standard/full 控制固定 artifact 深度和 human gates，把宿主 approval 与业务治理混为一体。
- **state_intent_matrix**:
  - single component + local reversible -> standard + low -> direct execute
  - multi component + local reversible -> full + low -> no business gate
  - single component + guarded + current task already authorizes exact change -> no duplicate question
  - guarded + authority absent -> one blocking business question
  - single component + critical -> standard + critical -> explicit impact/recovery confirmation
  - topology correction without scope expansion -> update route without approval
  - risk rationale disproved by repository evidence -> record evidence and lower risk without approval
- **scenarios**:
  - happy: 四种 topology/risk profile 选择最小能力集合并进入实现
  - edge: 单组件架构/schema 仍是 standard；full 不强制 parallel 或 architecture.md；无法消除的歧义只问一个问题
  - error: express 残留、full 自动触发用户 gate、guarded 重复确认、无证据降级风险以绕过确认、修改 sandbox mode、创建 permission hash 均违反 contract
  - integration: 用户请求和仓库事实形成 task contract，supporting capability 只有触发时才选中
- **verification**: `python3 -m unittest discover -s tests -p 'test_workflow_routing.py'`

## bruce-v4-3
- **feature_bearing**: true
- **regression_source**: 旧方案任一失败全局停止；上一版又为恢复引入 run/evidence/decision store、lease 和 fencing，超出插件职责。
- **state_intent_matrix**:
  - L0 + 幂等 + `retry_count<2` -> retry；计数不含首次失败
  - L0 + `retry_count>=2` -> L2
  - L1 + actual code/input change + `repair_round<2` -> reverify
  - L1 unchanged rerun or `repair_round>=2` still failing -> reject/L2
  - L2 -> replan affected task/descendants；independent task continues
  - L3 -> related task waits for one business decision；independent task continues
  - L4/unknown external state -> freeze tasks inside incident boundary；read-only diagnostics remain allowed
  - host permission denied + alternative/no alternative -> L2/blocked
- **scenarios**:
  - happy: task-a transient 后成功，依赖 task-b 继续，独立 task-c 始终不被暂停
  - edge: Codex task resume 重新读取 plan/tool results/worktree；显式 handoff 包含已知事实但接手后重新 inspect；只有能证明与 incident boundary 隔离的任务可在 L4 后继续
  - error: 无限 attempt、原样重跑编译错误、把 permission denied 当业务批准、unknown side effect 自动重放、从旧 checklist 推断完成均被阻止
  - integration: L0-L4 分别收敛到 retry、repair、replan、ask、stop，不产生 runtime JSON/JSONL/lease 文件
- **verification**: `python3 -m unittest discover -s tests -p 'test_failure_policy.py' && python3 -m unittest discover -s tests -p 'test_resume_contract.py'`

## bruce-v4-4
- **feature_bearing**: true
- **regression_source**: 现有 supporting skills 被绑定到固定 lane、stage、checklist 和 artifact gate，即使主入口简化也会把用户带回旧流水线。
- **state_intent_matrix**:
  - no real ambiguity/design/plan/test/review need -> no supporting artifact
  - one unresolved requirement ambiguity -> only clarification capability
  - public contract freeze/handoff -> architecture capability；DB schema only when needed
  - complex dependency/handoff -> plan capability
  - complex acceptance matrix -> test-plan capability
  - actual plan + meaningful risk -> plan review capability
  - any document mutation -> separated D0 self-review -> explicit pass/issues
  - requirement/architecture/public-contract/plan/test-design/multi-doc/downstream-source -> conditional D1 P0/P1 gate
  - plan-only meaningful execution risk -> plan-review instead of mechanically running both reviewers；Clean=通过，Issues Found=不通过
- **scenarios**:
  - happy: 每个 capability 接收明确输入，只生成自己的产物并返回主 Bruce；写文档时同时返回 D0 pass
  - edge: 普通 README 小改只做 D0；重要文档做 D0+D1；计划需要深度执行风险检查时只用 plan-review 作为 D1；supporting skill 可独立使用
  - error: 文档改完无 verdict、D0 issues 未修复、必需 D1 缺失/不通过、reviewer 擅自改文档、机械双跑 doc-review-gate 和 plan-review、supporting skill 创建状态文件或强制级联均失败
  - integration: contract fixture 遍历六个 supporting skills 及其可达 references/templates，验证输入、输出和不负责事项完整且无隐藏旧 gate
- **verification**: `python3 -m unittest discover -s tests -p 'test_supporting_skill_contracts.py' && python3 -m unittest discover -s tests -p 'test_document_review_contract.py'`

## bruce-v4-5
- **feature_bearing**: true
- **regression_source**: spawn-execute 当前承担自定义进度/隔离语义，verify-completion 依赖 Agent Markdown；快速产出代码后缺少可执行验收、最终代码自检、真实使用验证以及失败后的修复回归闭环。
- **state_intent_matrix**:
  - behavior acceptance -> stable scenario id + Given/When/Then + exact Evidence for every material outcome
  - material Then without feasible Evidence -> investigate/clarify before implementation；explicit exploratory boundary -> record gap
  - behavior change -> smallest failing test/repro when feasible；bug -> reproduce first；refactor -> characterization baseline
  - documentation/generated/mechanical change -> no ceremonial TDD
  - code changed -> C0 self-review against final diff -> pass/issues；later code change invalidates old C0
  - unit/component evidence -> proves local behavior only；integration/API/database and real-use remain independently required
  - user-visible Web -> Codex App Chrome current session + real localhost/target service；Chrome unavailable -> incomplete, no silent Playwright fallback
  - L1 failed scenario -> actual repair -> C0 after code changes -> unchanged original scenario -> related regressions -> evidence update
  - L0/L2/L3/L4 -> bounded idempotent retry / replan / wait for decision / freeze without replay
  - two unsuccessful complete L1 rounds -> L2 replan
  - standard+low -> main Agent implement/verify -> pass without reviewer
  - full+low -> sequential or native subagents -> no human business gate
  - ordinary incidental delegation -> native subagent directly -> no Goal or audit file
  - explicit Goal/continuous/auditable execution -> goal-execution-gate -> active Goal + one execute_record.md -> optional spawn-execute
  - spawn-execute result -> scenario/evidence/C0/repair-loop audit packet -> Goal Gate updates execute_record.md and native Goal
  - document-changing Goal task -> D0/D1 verdict enters the existing audit evidence packet
  - ordinary guarded -> current evidence + mandatory main Agent structured second pass
  - broad guarded -> fresh subagent only when independence adds material value
  - critical or explicit independent review -> fresh reviewer required；unavailable -> blocked
  - subagent local failure -> classify and affect only dependency closure
  - tool permission denied -> wait for Codex result；denied 后 alternative/blocked
  - acceptance lacks current evidence or diff out of scope -> incomplete/blocked
- **scenarios**:
  - happy: 行为任务按 GWT 场景实现，最终 C0 pass，并在所需 unit/integration/real-use 层产生当前 Evidence；active Goal evidence packet 同时包含 scenario、C0、repair loop 和 completion 结果
  - edge: TDD 不可行时记录原因和最近可重复检查；Chrome 不可用保留 Web 验收缺口；仓库既定 SOP 或用户明确要求时可使用 Playwright；full 选择顺序执行也合法；普通 delegation 不调用 spawn-execute
  - error: 无 Evidence 开始正式行为实现、用 unit 代替真实集成/页面、代码变化后沿用旧 C0、削弱失败场景、两轮 L1 后继续循环、静默切 Playwright、无 active Goal 调用 spawn-execute、创建第二份 ledger、subagent 失败触发全局停止、只凭自然语言宣布完成均失败
  - integration: 浏览器场景按 Given 准备真实登录态/数据，When 执行用户动作，Then 检查页面和必要 API/数据后果；L1 失败后修复并不改场景地重跑，再执行关联回归和更新 acceptance-to-evidence；L4 未知副作用场景冻结且绝不重放
- **verification**: `python3 -m unittest discover -s tests -p 'test_validation_loop_contract.py' && python3 -m unittest discover -s tests -p 'test_execution_contract.py' && python3 -m unittest discover -s tests -p 'test_completion_contract.py' && python3 -m unittest discover -s tests -p 'test_workflow_profiles.py'`

## bruce-v4-6
- **feature_bearing**: true
- **regression_source**: 当前根目录与 `skills/bruce/` 人工双写，旧 checklist/templates 仍可调用，README 仍描述固定四阶段状态机。
- **state_intent_matrix**:
  - canonical plugin source + validator -> pass
  - root/mirror drift or legacy runtime entry -> fail
  - repo marketplace file + static validation -> pass without changing global Codex config
  - legacy wording only in retained `docs/**` or negative fixtures -> ignored by scoped validator
  - user-confirmed local install + new Codex task -> Bruce skill discoverable
  - no user confirmation -> skip install smoke, static suite remains valid
- **scenarios**:
  - happy: manifest、skill frontmatter、relative refs、README 和全量 contract tests 通过
  - edge: 历史 run/docs 保留但不可 resume；历史和负面 fixture 中的禁止词不触发误报；supporting skills 仍可单独发现；安装说明区分仓库 marketplace 文件、静态验证和真实 App smoke
  - error: 根 SKILL 继续充当真源、active skill 可达资源残留 checklist gate/旧 config/REDESIGN 运行语义、公开 CLI/MCP/host runtime、validator 修改全局配置或自动删除历史 run 均失败
  - integration: 按 README 完成静态验证；取得用户确认后再通过 repo marketplace 安装，在新任务中触发 Bruce
- **verification**: `python3 -m unittest discover -s tests -p 'test_package.py' && python3 -m unittest discover -s tests -p 'test_*.py' && python3 scripts/validate_plugin.py`

## 计划质量检查

- [x] 6 个计划 task 均有且只有一个同名测试 anchor。
- [x] 依赖引用存在且依赖图无环。
- [x] 每个任务有独立验证入口和 state intent matrix。
- [x] 覆盖标准 Codex plugin manifest、marketplace 和 skill discovery 路径。
- [x] 明确 Codex 宿主与 Bruce workflow 的责任边界。
- [x] 覆盖 standard/full 与 low/guarded/critical 的正交组合。
- [x] 覆盖 L0-L4、有限预算、局部传播、业务决策和未知状态停止。
- [x] 覆盖宿主 permission denied，但不测试或复制 sandbox 实现。
- [x] 覆盖无 runtime state store、无固定 artifact 链和单一 Bruce 真源。
- [x] 覆盖 GWT/Evidence、TDD 边界、C0、分层真实验证、Chrome E2E 和失败修复回归 loop。
- [x] 覆盖 active skill 可达 references/templates/config，且 legacy 扫描不误伤历史文档与负面 fixture。
