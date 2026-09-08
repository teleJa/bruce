# 测试设计：统一 Bruce 工作流状态机

## 目标

验证统一任务级状态机的 schema、合法转移、终态保护、Gate ownership 和现有对象映射。不执行项目外部环境或真实部署。

## 场景

### STATE-001：合法主路径

`unresolved -> contracting -> designing -> design_ready -> implementing -> verifying -> completion_review -> completed`，每次转移递增 `state_revision`。

### STATE-002：实现路径跳过设计

`contracting -> implementing` 仅在 `design_gate=not_required` 且事件为 `implementation_authorized` 时允许。

### STATE-003：等待和恢复

`verifying -> waiting_external|waiting_user -> verifying`，以及 `active -> paused -> previous active`；恢复必须满足 `resume_conditions`，且不重置 repair/evidence/profile 版本。

### STATE-004：修复回路

`verifying -> repairing -> re_verifying -> verifying|completion_review`；未知事件和非法跳转拒绝。

### STATE-005：终态保护

只有 `completion_passed` 且 `completion_result=pass` 才能进入 `completed`；完成态不允许继续执行。

### STATE-006：Gate ownership

状态机不产生 `Design` 或 `Completion` verdict；Design/Completion Gate 文档仍保持唯一裁决权。

### STATE-007：兼容映射

checkpoint 和 Verification Run 包含统一状态引用；运行子状态仍可表达等待、修复和复验，不形成第二任务终态。

## 验证命令

```sh
python3 -m pytest -q
python3 scripts/validate_plugin.py .
python3 scripts/validate_workflow_state.py skills/bruce/templates/workflow-state.yaml
python3 -m py_compile scripts/workflow_state.py scripts/validate_workflow_state.py
```

## 限制

本测试计划不证明 ego-lite、Chrome、CNB、部署、项目 Adapter 或生产环境可用性；这些属于项目 Environment/Verification Profile 和真实运行时验收边界。
