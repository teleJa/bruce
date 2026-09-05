# 可选工作流效果度量

## 边界

复用 fixture 的主 Agent 持有运行证据；本命令只汇总**调用者明确提供的测量**，不运行模型、
不读取 Codex/Claude 历史会话、不认证 evidence_refs，也不判断回复语义或发出 Completion verdict。
没有真实 actor 运行时，不得把 helper 测试数据填成 native_actor。自动检查通过不等于真实 Agent 验收通过。

```sh
./scripts/workflow_behavior_fixture.py summarize /explicit/path/measurements.json
```

命令只读取指定输入与内置场景表，输出到 stdout；需要保存时由调用者显式重定向。
合法输入退出 0（仅表示汇总成功，不表示任何样本通过），输入错误退出 2。没有自动采集、后台运行或强制记录。

## 输入示例与来源

以下仅为结构示例，不代表一次已执行试验；所有未测量值保持 null 或省略。

```json
{
  "version": 1,
  "trials": [{
    "trial_id": "example-only",
    "workflow_revision": "explicit-workflow-snapshot",
    "fixture_revision": "explicit-helper-and-scenario-snapshot",
    "scenario": "local_fix",
    "source": "fixture_test",
    "automated_checks_passed": false,
    "manual_status": "pending",
    "evidence_refs": [],
    "metrics": {"elapsed_seconds": null, "tool_calls": null}
  }]
}
```

- trial_id 在一个输入中唯一；各 revision 必须指向实际用于试验的快照，含脏工作区时不能只写旧 HEAD。
- scenario 来自固定八场景；source 为 native_actor 或 fixture_test，二者永不合并。
- automated_checks_passed 来自当前 check 结果；manual_status 是主 Agent 检查原生工具历史和回复后的
  passed/failed/pending。passed 和 failed 都必须引用证据；pending 不能充当通过。
- 原生试验复核必须检查全部 manual_review 问题，包括瞬时/撤回的越界、原失败测试是否真的由 actor 重跑。
- 不仅要查看最终文件；环境不可用场景的预期退出码 3，证明的是 fixture 符合预期，不是环境可用。
- 不能用 evaluator 在结束后的测试结果伪装成 actor 本人的首次验证或工具调用记录。

## 指标及未知值

| 指标 | 类型 | 口径 |
|---|---|---|
| elapsed_seconds | 非负有限数 | actor 起止之间的实际耗时 |
| first_verification_seconds | 非负有限数 | 从 actor 开始到首个有效验证的耗时；未发生为未知 |
| planning_seconds / inspection_seconds / implementation_seconds / verification_seconds | 非负有限数 | 来自原生记录的互不重叠阶段区间；不能凭感觉分配 |
| tool_calls | 非负整数 | actor 实际调用数，不含 evaluator 后续检查 |
| repair_rounds | 非负整数 | 实际完整修复与复验次数 |
| redundant_checks | 非负整数 | 主 Agent 根据依据未变的重复检查逐项确认 |
| user_interventions | 非负整数 | 所需人工介入次数，原因保留在已有证据引用中 |
| false_completion_claims | 非负整数 | 语义复核确认的错误完成声明；不能只数关键词 |
| tokens | 非负整数 | 仅使用宿主实际返回值，未提供则未知 |

每个指标允许省略或 null，汇总返回 observed_samples 和 mean，不以零填补未知。
已知 first_verification_seconds 不得超过 elapsed_seconds；已知阶段区间之和也不得超过总耗时。
为避免 0.1+0.2 被误拒绝，比较采用相对 1e-12、绝对 0 的舍入容差；零总耗时不接受任何正耗时。
负数、NaN、Infinity、布尔冒充数值、小数计数、重复 ID、未知字段和不支持的场景均拒绝。

## 输出与版本比较

按 workflow_revision、fixture_revision、scenario、source 分组，保留 samples、人工复核覆盖数、
manual_pending_samples 及各指标的观测覆盖。仅 native_actor 的已复核记录计算 reviewed_pass_rate：
分子要求人工 passed 且自动检查通过，分母仅含已复核记录。必须同时报告 pending 数，避免幸存者偏差。
fixture_test 或没有人工复核的分组，该值为 null。引用是调用者提供的，不是工具认证的真实成效。

比较版本时固定相同 fixture 快照、场景组合、宿主模型/参数、权限和环境；不要把不同条件的均值直接归因于规则。
先看错误完成和验收覆盖，再看耗时、无效检查与人工介入。单次样本不证明提效；空 trials 只产生空 groups。

## 可执行回归

```sh
python3 -m pytest tests/test_workflow_measurements.py tests/test_workflow_behavior.py -q
```

这些是汇总器/夹具测试，不是当前 Bruce 的真实 actor 效果报告。
