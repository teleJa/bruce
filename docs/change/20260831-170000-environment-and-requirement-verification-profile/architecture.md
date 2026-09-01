# 架构：Environment Profile 与需求级 Verification Profile

## 1. Design summary

Bruce 的验证循环分为三个层次，但仍属于同一个 Bruce workflow：

```text
Environment Profile
  -> Requirement Verification Profile
      -> Verification Run / Checkpoint
          -> Completion Gate
```

- Environment Profile 记录用户提供并确认的、支撑开发和测试的可复用运行拓扑与操作声明，不是仓库扫描或代码索引。
- Requirement Verification Profile 读取用户指定的 `requirements.md`，将需求 Acceptance 映射到已确认的环境、账号、Skill、证据和修复路径。
- Verification Run/Checkpoint 记录一次执行的真实 revision、状态、证据、阻塞和恢复信息。
- Completion Gate 仍是唯一最终完成判断。

Profile confirmation 是输入授权和事实确认，不是第三个 Gate。

## 2. Component boundaries

### 2.1 Environment Profile skill

新增 `$environment-profile` supporting skill，负责：

- 接收用户提供的环境身份、用途、应用部署、构建/生命周期、依赖/中间件、网络、身份、数据、Credential 引用、权限和能力选择；不从仓库扫描来填充 Profile；
- 收集用户脑中的环境事实、账号池、Credential 来源和操作授权；
- 记录用户声明、运行拓扑、操作边界、未知项、preflight、secret policy 和 freshness；
- 生成或更新项目环境 Profile；
- 生成确认摘要并等待用户确认；
- 对本地环境检查项目根目录 `.env`，在用户明确授权后创建或补全被 Git 忽略的 `.env`，只输出元数据。

它不执行构建、部署、数据库写入、客户端测试或外部环境操作，也不实现通用 Secret Manager。

### 2.2 Requirement Verification Profile skill

改造 `$verification-profile` supporting skill，必须接收用户提供的 `requirements.md` 路径，并消费一个或多个已确认的 Environment Profile。

它负责：

- 提取需求 Objective、Scope、Actors、Decisions、Acceptance IDs 和约束；
- 为每个 Acceptance 设计需求级验证阶段；
- 绑定所需 Environment Profile、账号 alias/pool、Credential reference 和 Skill/capability；
- 定义证据、失败诊断、修复路径、阻塞条件、用户 handoff 和恢复动作；
- 生成确认摘要，默认保持 pending。

它不改变 requirements.md，不执行测试或部署，不把需求 Acceptance 写入 Environment Profile。

### 2.3 Verification Run / Checkpoint

运行时状态不写入静态 Profile。未来实现应在 Verification Run 或现有 change-level `checkpoint.yaml` 中记录：

- 实际 source revision、requirements revision 和 environment revision；
- 实际账号绑定和 preflight 结果；
- build/deployment/client identity；
- stage 状态、evidence refs、failure classification、repair round；
- `waiting_external`、`waiting_user`、`blocked`、resume event 和 stale evidence。

本变更不实现项目环境或验证运行；`validate_profile.py` 只负责静态 Profile contract 校验，`check_local_env.py` 只返回本地 `.env` 元数据，`create_local_env.py` 只在用户明确授权后执行受限的本地文件初始化，不执行外部环境操作。

## 3. Environment Profile data model

Environment Profile 是 project/environment scoped 的共享资产，推荐放在目标项目：

```text
<project-root>/.bruce/environments/<environment-id>.profile.yaml
```

它包含：

- profile identity and revision；
- project/environment/scope；
- user-provided and user-confirmed facts；
- application deployment, build/lifecycle, dependencies (including databases/middleware), network, identity, data, configuration, and operation declarations；
- build and deployment strategies；
- service/database/client targets；
- account pools and safe Credential references；
- local `.env` path, required variable names and security conditions (never values)；
- available Skills and evidence boundaries；
- preflight and freshness rules；
- confirmation metadata。

它不包含某个需求的 AC、Task、Scenario、当前结果或完成判断。

## 4. Derived Environment Operation Manifest

`$environment-operations` is an opt-in static capability that generates a project-local operation Manifest only from an exact confirmed Environment Profile. It packages declared build, deployment, dependency preparation, lifecycle, status, logs, and preflight operations; it does not dynamically register a project Skill, execute operations, infer commands from source, or expand authorization. High-risk operations such as migration, reset/drop, remote deployment, production access, and credential retrieval remain excluded or separately authorized. A stale source Profile makes the Manifest stale.

## 5. Requirement Verification Profile data model

Requirement Verification Profile 推荐放在需求变更目录：

```text
<change-dir>/verification-profile.yaml
```

它包含：

- requirements path and immutable content hash；
- extracted acceptance inventory；
- confirmed environment profile references and revisions；
- requirement-specific account bindings and initial-state predicates；
- selected Skills/capabilities and their evidence boundaries；
- per-acceptance verification graph；
- failure diagnosis and bounded repair rules；
- blocking notification and explicit resume requirements；
- confirmation metadata。

它不包含实际测试结果。实际结果由 Verification Run/Checkpoint 引用。

## 5. Confirmation lifecycle

两类 Profile 共享以下生命周期：

```text
draft
  -> needs_input
  -> ready_for_confirmation
  -> confirmed
  -> stale
  -> ready_for_confirmation
  -> confirmed
```

也允许：

```text
ready_for_confirmation -> rejected -> draft
confirmed -> superseded
```

规则：

1. 新建 Profile 的 `confirmation.state` 必须为 `pending`。
2. 用户声明、输入 hash、环境引用、账号要求、Credential 来源、能力选择、证据层、修复边界或外部授权发生实质变化时，revision 增加，confirmation 重置为 `pending`；普通仓库代码变化不触发 Environment Profile stale。
3. 用户必须确认精确 `profile_id + profile_revision + content_hash`，确认消息不能只引用“继续”。
4. 确认不证明环境当前可用；受控验证前仍执行 capability preflight。
5. Profile 处于 `confirmed` 且所有引用 revision 匹配时，才允许作为 Bruce 验证循环输入。
6. requirements.md 内容 hash 变化时，需求级 Profile 立即 stale；Environment Profile 变化时，引用它的需求级 Profile stale。

## 6. User-supplied environment facts

环境事实来源必须显式区分：

```text
repository
project-document
user
runtime-preflight
external-system
```

用户提供的事实可以进入 Profile，但必须保留：

- fact id；
- source kind/user statement reference；
- provided time；
- confirmation status；
- runtime preflight requirement。

如果关键事实只来自用户且未确认，Profile 不能进入 confirmed。

## 7. Account and Credential boundary

账号记录使用 alias、pool 和状态谓词，不保存秘密值：

```yaml
account_id: new-sso-user
account_pool: auth-center-new-users
required_initial_state:
  local_identity_exists: false
credential_source: user-managed-browser-session
```

Credential 只记录安全引用：

```yaml
credential_id: auth-center-test
source_ref: AUTH_CENTER_TEST_API_KEY
secret_value_persisted: false
expose_to_model: false
redact_logs: true
```

具体账号绑定和运行时可用性属于 Verification Run，不属于共享 Environment Profile 的静态事实。

## 8. Requirement mapping example: Multica SSO

对于 `20260825-154000-sso-xiangjia-default-workspace/requirements.md`，需求级 Profile 应表达：

```text
AC-01 -> multica-local + migration/database capability
AC-02 -> multica-local + cnb/test-cluster + new-sso-user + real browser
AC-03 -> test-cluster + new-sso-user + Chrome smoke
AC-04 -> multica-local + existing-sso-user + identity idempotence
AC-05 -> test-cluster + bootstrap-admin + operational SQL + explicit authorization
AC-06 -> test-cluster + new-sso-user + workspace creation API/browser
AC-07 -> multica-local + PostgreSQL fault injection + safe callback error
AC-08 -> multica-local + non-SSO/auth invitation regression
```

这些 AC 只属于本次需求级 Profile；Multica Environment Profile 只提供可复用的环境、账号池、Credential 引用和 Skill/capability。

## 9. Blocking and recovery

验证循环发现以下情况时，停止受影响 Task/Batch 的写入、修复、重试和依赖工作：

- requirements 或 profile revision 不匹配；
- Environment Profile 未确认或已 stale；
- 必需账号的初始状态无法证明；
- build/deployment/client identity 不匹配；
- Credential、权限或外部系统状态未知；
- 用户需要提供环境事实或做范围/授权决策。

Bruce 必须通知用户并记录：

- blocker id and classification；
- known facts and unknown facts；
- frozen scope；
- user action；
- exact unlock condition；
- required resume event。

用户处理并显式恢复后，重新执行受影响 preflight，使旧证据 stale，并从原 Task/Batch/Stage 继续；不得重置 retry/repair budget。

## 10. Ownership and non-goals

- Environment Profile owns reusable environment facts.
- Verification Profile owns requirement-specific verification and repair design.
- Verification Run/Checkpoint owns dynamic execution state.
- Design Gate owns implementation-entry decision.
- Completion Gate owns final completion decision.
- Project adapters and Skills own project/environment actions and return facts, not Bruce verdicts。
