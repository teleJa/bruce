# 文件契约：Environment Profile 与需求级 Verification Profile

## 1. Environment Profile

建议文件：`.bruce/environments/<environment-id>.profile.yaml`。文件名中的环境 ID 应使用实际稳定标识，以下示例值仅表示字段类型。

```yaml
version: 1
profile_kind: environment
profile_id: multica-sharkcloud-test
profile_revision: 1
content_hash: sha256:example
project:
  name: multica
  root: /Users/tele/xjjk/aiworkbench/multica
environment:
  name: sharkcloud-test
  kind: shared-test
  production: false
  shared: true
  purposes: [development, integration-test]
  purpose: user-confirmed shared test environment
  allowed_operations: [readiness-check, test-deploy]
  prohibited_operations: [production-write]
declaration:
  source: user
  statement: user-confirmed shared test environment
  provided_at: 2026-09-01T00:00:00+08:00
profile_state: ready_for_confirmation
confirmation:
  state: pending
  confirmed_by: null
  confirmed_at: null
  confirmed_revision: null
  confirmed_content_hash: null
deployment:
  mode: user-confirmed
  owner: user-confirmed-operator
  application_services:
    - service_id: multica-web
      deployment_unit: user-confirmed
authentication:
  mode: user-confirmed
  references: []
build:
  strategy: user-confirmed
  executor: user-confirmed
  working_directory: user-confirmed-project-root
  operations: []
  artifact_expectations: []
lifecycle:
  prepare: []
  start: []
  stop: []
  status: []
  logs: []
dependencies:
  - dependency_id: multica-test-postgres
    category: database
    deployment_unit: user-confirmed
    locality: user-confirmed
    connection_ref: MULTICA_TEST_DATABASE_URL
    mutation_policy: local-ephemeral-or-explicitly-authorized
network:
  access_scope: user-confirmed
  endpoints:
    - endpoint_id: multica-web
      endpoint_ref: MULTICA_TEST_WEB_URL
data_policy:
  ownership: user-confirmed
  persistence: user-confirmed
  migration_write: explicit-authorization-required
  reset_or_drop: explicit-authorization-required
configuration:
  local_env:
    mode: user-managed
    path: .env
    variable_refs: []
operations: []
# Executable operation Skill is a derived project artifact, not an Environment Profile field.
preflight: []
security:
  persist_secrets: false
  expose_secrets_to_model: false
  credential_values_allowed: false
  credential_refs_only: true
  redact_logs: true
```

约束：

- `profile_state=confirmed` 只能在 `confirmation.state=confirmed`、`confirmed_revision=profile_revision` 且 `confirmed_content_hash=content_hash` 时成立。
- Environment Profile 只记录用户提供并确认的开发/测试运行拓扑；不包含 `source_of_truth`、仓库实现路径、Git revision 或代码事实。
- Executable Environment Operation Skill 只能由 confirmed Profile 显式派生，绑定 Profile revision/hash，且不自动执行或扩大授权。
- `value_ref`、`target_ref`、`connection_ref` 和 `source_ref` 只能引用安全配置或外部资源，不得包含秘密值。
- `build`/`deployment` 描述能力和证据要求，不记录本次实际 build/deployment 结果。

## 2. Requirement Verification Profile

建议文件：`<change-dir>/verification-profile.yaml`。

```yaml
version: 1
profile_kind: requirement-verification
profile_id: sso-xiangjia-default-workspace
profile_revision: 1
content_hash: sha256:example
profile_state: ready_for_confirmation
confirmation:
  state: pending
  confirmed_by: null
  confirmed_at: null
  confirmed_revision: null
requirements:
  path: /Users/tele/xjjk/aiworkbench/multica/docs/change/20260825-154000-sso-xiangjia-default-workspace/requirements.md
  content_hash: sha256:example
  acceptance_ids: [AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08]
environment_refs:
  - profile_id: multica-local
    path: /Users/tele/xjjk/aiworkbench/multica/.bruce/environments/multica-local.profile.yaml
    profile_revision: 2
    used_for: [AC-01, AC-02, AC-04, AC-07, AC-08]
  - profile_id: multica-sharkcloud-test
    path: /Users/tele/xjjk/aiworkbench/multica/.bruce/environments/multica-sharkcloud-test.profile.yaml
    profile_revision: 1
    used_for: [AC-02, AC-03, AC-05, AC-06]
account_requirements:
  - binding_id: new-sso-user
    environment_profile: multica-sharkcloud-test
    account_pool: auth-center-new-users
    required_initial_state: local_identity_absent
    used_for: [AC-02, AC-03, AC-06]
skill_selections:
  - skill_id: chrome:control-chrome
    environment_profile: multica-sharkcloud-test
    purpose: real-sso-login-and-visible-route
    used_for: [AC-02, AC-03, AC-06]
acceptance:
  AC-02:
    source: requirements.md#AC-02
    verification_stages: [transaction-integration, build-deploy, real-sso-login]
    evidence_required: [postgres-assertions, deployed_revision, final_url, screenshot]
    diagnosis_rules:
      - condition: deployed_revision_mismatch
        classification: L2
        action: notify-user-and-stop
      - condition: member_missing_on_matching_revision
        classification: L1
        action: bounded-server-repair-and-reverify
blocking_rules:
  notification_required: true
  explicit_resume_required: true
  stop_scope: affected-task-batch-and-dependents
resume_rules:
  preserve: [task_id, batch_id, contract_revision, profile_revision, repair_round, retry_count]
  rerun: [changed-preflight, stale-evidence, original-failure, related-regressions]
completion:
  owner: completion-gate
  profile_may_return_completion: false
```

## 3. Confirmation contract

用户确认必须绑定：

```yaml
confirmation:
  state: confirmed
  confirmed_by: user
  confirmed_at: 2026-08-31T00:00:00+08:00
  confirmed_revision: 1
  confirmed_content_hash: sha256:example
```

确认消息必须明确指向 `profile_id`、`profile_revision` 和 `content_hash`；消费前必须同时校验 `confirmed_content_hash=content_hash`。任何实质更新或 hash 不匹配都将 `state` 重置为 `pending`。

## 4. Dynamic result boundary

以下字段不写入静态 Profile，而写入 Verification Run/Checkpoint：

```yaml
run_id: VR-20260831-001
source_revision: abc123
requirements_content_hash: sha256:example
environment_profile_revisions: [multica-local:2, multica-sharkcloud-test:1]
account_bindings: [new-sso-user:sso-test-new-017]
preflight_results: []
stage_results: []
evidence_refs: []
blockers: []
next_action: await-user|repair|resume|completion-gate
```

## 5. Security contract

- Profile 可记录 Credential 的 `source_ref`、用途、scope、owner 和 preflight 方法；本地 Profile 可记录 `.env` 路径和必需变量名。
- Profile 不得记录 Credential value、密码、Cookie、JWT、ticket、完整 provider response 或敏感身份 payload；实际本地值只允许经用户明确授权写入被 Git 忽略的 `.env`，不得进入 Profile 或模型可见输出。
- 账号使用 alias/pool 和状态谓词；实际账号绑定必须在运行记录中按最小必要范围记录。
- 日志、截图和用户回传证据必须遵守项目脱敏规则。
