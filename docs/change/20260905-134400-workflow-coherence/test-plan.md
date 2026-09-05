# 测试计划：工作流一致性与评估

## 验收映射与前置条件

Python 与当前仓库依赖可用，所有 fixture 使用 TemporaryDirectory；不依赖数据库、浏览器或远程模型。
visual_scope: none；consistency_check: required，因为冻结输入、可变文件和评估结果必须保持一致。

| 验收 ID | 场景 | 层级 | Evidence |
|---|---|---|---|
| AC-01 | S-01 路由一致性 | contract | 参数化检查入口、描述、权威表及模板选择 |
| AC-02 | S-02 最小模板 | contract | 字段完整且无空矩阵；复杂模板兼容 |
| AC-03 | S-03 分层预算 | contract | 同一失败、新失败、批次、Completion、恢复、未知计数的决策表 |
| AC-04 | S-04 冻结与边界 | executable fixture | 原测试、未知结果、用户草稿、越界文件、测试计划白名单 |
| AC-05 | S-05 度量汇总 | unit/CLI | 合法、缺失、伪造类型、不同来源、未复核、重复 ID |
| AC-06 | S-06 回归与交付 | full suite/package | pytest、插件校验、缓存刷新输出 |

## 状态与权威矩阵

| 对象 | 权威状态 | 冲突/失败语义 | 保留保证 |
|---|---|---|---|
| fixture 文件 | evaluator baseline 和明确 mutable/created 白名单 | 冻结变化或越界即拒绝，验证前不执行命令 | 原测试和用户草稿完整 |
| 自动检查 | 当前 evaluator 实际命令结果 | 非零/超时不通过 | 不等同 actor 原生工具历史 |
| 测量 | 调用者显式提供的记录及引用 | 缺失未知，非法拒绝，来源分组 | 不认证引用或推测语义 |
| 修复预算 | 稳定 failure_id 与现有 checkpoint/证据 | 本地或全局先耗尽即停止 | 继续与恢复不重置 |

## 场景

### S-01 / S-02：按需深度而非省略测试设计
- Given: 局部行为修复、复杂状态交互、无行为纯文案以及显式要求测试设计的文档任务。
- When: 读取统一策略及入口描述，选择对应模板。
- Then: 行为变更有独立测试计划；复杂度只切换模板，简单任务不制造空矩阵。
- Evidence: tests/test_workflow_policy_contract.py；既有 workflow profiles 与 supporting skills 回归。

### S-03：预算相互约束
- Given: 同一错误修复 0/1/2 次、全局 0/4/5 轮、批次与 Completion、恢复时计数未知。
- When: 应用权威决策表及 checkpoint 示例。
- Then: 两轮同错转 L2；Completion 五轮耗尽停止；批次不消费全局；恢复保持计数、未知先恢复。
- Evidence: tests/test_workflow_policy_contract.py 与 tests/test_failure_policy.py。

### S-04：真实命令与文件故障注入
- Given: 八个隔离场景、冻结测试和用户草稿、未知外部动作记录。
- When: 正确修复或注入测试删改、越界文件、空/缺失计划、符号链接、草稿修改、未知动作执行。
- Then: 正确状态仅通过自动检查并要求人工复核；错误状态拒绝；未知动作不由检查器重放。
- Evidence: tests/test_workflow_behavior.py，保留既有 CLI、超时及重复 prepare 回归。

### S-05：只读汇总与证据边界
- Given: 不同版本/来源、pending/失败/已复核记录，以及未知值、重复 ID、布尔冒充整数、NaN、未知字段、小数舍入和真实超限边界。
- When: 通过函数与 CLI 汇总显式输入。
- Then: 正确分组；缺失不补零；fixture 测试无 actor 通过率；非法输入退出 2；文件不变。
- Evidence: tests/test_workflow_measurements.py。

## 命令与限制

- python3 -m pytest tests/test_workflow_policy_contract.py tests/test_workflow_behavior.py tests/test_workflow_measurements.py -q
- python3 -m pytest -q
- python3 scripts/validate_plugin.py
- python3 scripts/validate_functional_agents.py
- git diff --check
- python3 scripts/refresh_local_plugin.py /Users/tele/ai-workspace/bruce（通过前述检查后执行）

这些检查不能证明真实 actor 没有瞬时越界或已经提高效率；原生工具历史与回复语义仍需明确授权的独立 trial。
本次不读取用户历史会话，也不把 fixture_test 测量冒充真实模型效果。测试计划是待执行合同，不是通过记录。
