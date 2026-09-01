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
profile_state: ready_for_confirmation
confirmation:
  state: pending
  confirmed_by: null
  confirmed_at: null
  confirmed_revision: null
declaration:
  source: user
  statement: 用户声明的验证环境
facts:
  - fact_id: deployment-target
    value: configured-test-cluster
    source:
      kind: user
      provided_at: 2026-09-01T00:00:00+08:00
      statement: user-confirmed non-production target
    confirmation_required: true
    runtime_preflight_required: true
build:
  strategy: cnb
  executor: external-system
  trigger:
    method: project-cnb-trigger
    authorization_required: true
  terminal_states: [success, failed, canceled, unknown]
  required_evidence: [build_id, source_commit, terminal_status, artifact_identity]
  invariants: [trigger-accepted-is-not-build-success]
deployment:
  strategy: cnb-to-test-cluster
  executor: project-adapter
  targets:
    - target_id: test-backend
      identity_ref: configured-test-cluster
  terminal_states: [deployed, failed, rolled_back, unknown]
  required_evidence: [deployed_commit, deployed_artifact, rollout_status, readiness_result]
  invariants: [build-success-is-not-deployment-success, deployment-success-is-not-user-verification]
services:
  - service_id: multica-web
    target_ref: MULTICA_TEST_WEB_URL
databases:
  - database_id: multica-test-postgres
    connection_ref: MULTICA_TEST_DATABASE_URL
    mutation_policy: local-ephemeral-or-explicitly-authorized
local_env:
  path: .env
  required: true
  ignored_by_vcs: required
  file_mode: "0600"
  required_variables: [AUTH_CENTER_TEST_API_KEY]
credentials:
  - credential_id: auth-center-test
    source_ref: env:AUTH_CENTER_TEST_API_KEY
    secret_value_persisted: false
    expose_to_model: false
    redact_logs: true
account_pools:
  - account_pool_id: auth-center-new-users
    purpose: first-sso-login
    allocation: user-confirmed-unused-subject
skills:
  - skill_id: cnb-pipeline
    purpose: inspect-and-diagnose-build-pipeline
    evidence_boundary: pipeline-config-or-diagnosis-only
  - skill_id: chrome:control-chrome
    purpose: real-sso-browser-interaction
    evidence_boundary: current-provider-browser-evidence
preflight:
  - check_id: test-target-reachable
  - check_id: deployed-revision
  - check_id: required-config
  - check_id: account-state
  - check_id: browser-session
freshness:
  invalidate_on: [deployment-topology-change, endpoint-change, account-policy-change, credential-source-change, skill-removal]
security:
  persist_secrets: false
  expose_secrets_to_model: false
  credential_values_allowed: false
  credential_refs_only: true
  redact_logs: true
```

约束：

- `profile_state=confirmed` 只能在 `confirmation.state=confirmed`、`confirmed_revision=profile_revision` 且 `confirmed_content_hash=content_hash` 时成立。
- Environment Profile 只记录用户提供并确认的信息；不包含 `source_of_truth`、仓库实现路径、Git revision 或代码事实。
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
