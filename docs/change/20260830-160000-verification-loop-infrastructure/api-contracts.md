# 文件契约：验证循环基础设施

## 1. Verification Profile

```yaml
version: 1
profile_id: multica-desktop-cnb
project: example-project
capabilities:
  - id: local-check
    kind: local|cnb|deployment|browser|desktop|user|runtime
stages:
  - stage_id: local-check
    depends_on: []
    adapter: example-local-adapter
    acceptance_ids: []
    required_evidence: []
    async: false
    stop_condition: stage completed or terminal failure
    next_on_pass: null
    next_on_fail: classify
    next_on_blocked: notify-user
```

Profile 是项目配置/生成产物；Bruce 只消费其稳定字段并验证结构完整性。

## 2. Verification Run

```yaml
version: 1
run_id: VR-0001
requirement_id: 20260830-160000-verification-loop-infrastructure
task_id: T-001
batch_id: B-001
contract_revision: 1
basis_revision: abc123
status: ready|running|waiting_external|waiting_user|evaluating|repairing|re_verifying|passed|blocked
active_stage: local-check
attempt: 1
repair_round: 0
retry_count: 0
evidence_refs: []
findings: []
blockers: []
next_action: run-stage|await-external|await-user|repair|resume-after-user|return-control|completion-gate
```

## 3. Verification Event

```yaml
version: 1
event_id: VE-0001
run_id: VR-0001
task_id: T-001
batch_id: B-001
acceptance_id: AC-001
stage_id: local-check
source: local|adapter|cnb|deployment|browser|desktop|user
observed_at: 2026-08-30T20:00:00+08:00
basis_revision: abc123
status: pass|fail|blocked|unclear|unexecuted
expected: expected result
observed: observed result
evidence_refs: []
external_identity: dev-abc123
failure_level: none|L0|L1|L2|L3|L4
next_action: open the target and perform the acceptance action
```

事件是事实和反馈，不是 Completion verdict。`unclear` 不得直接进入代码修复；必须补充事实或暂停。

## 4. User Verification Handoff

```yaml
version: 1
handoff_id: HV-0001
run_id: VR-0001
task_id: T-001
acceptance_ids: [AC-001]
basis_revision: abc123
artifact:
  kind: desktop-package|deployed-service|web-target
  identity: example-value
  target: example-value
preconditions: []
steps:
  - step_id: S-001
    action: perform the acceptance steps
    expect: the expected result is visible
evidence_required:
  - screenshot|log|recording|observed-result
response:
  status: pending|pass|fail|blocked|unclear
  failed_step: null
  actual_result: null
  evidence_refs: []
  reported_at: null
```

用户未回传时保持 `waiting_user`；用户回传后事件进入统一分类和修复/恢复流程。

## 5. Blocking Notification / Resume Event

```yaml
blocking_notification:
  run_id: VR-0001
  task_id: T-001
  batch_id: B-001
  status: blocked
  reason: capability
  known_facts: []
  unknown_facts: []
  frozen_scope: []
  unlock_condition: the required external capability is available and preflight passes
  user_action_required: repair the dependency or confirm the environment is ready

resume_event:
  event_id: RE-0001
  run_id: VR-0001
  actor: user
  intent: continue
  handled_blocker: blocker-001
  changed_facts: []
  reported_at: 2026-08-30T20:00:00+08:00
```

没有 `resume_event` 不得从 `blocked` 自动恢复。恢复必须重新 preflight 并重算受影响证据新鲜度。

## 6. Verdict ownership

- Adapter 只能返回外部事实。
- Verification Loop 只能返回当前节点/批次状态和 `next_action`。
- Checkpoint 只能记录进度和证据引用。
- Design Gate 仍拥有设计准入判断。
- Completion Gate 仍是唯一 `Completion: pass|issues|blocked` 来源。
