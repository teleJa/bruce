# 测试计划：可配置浏览器验证提供者

## 验收映射

| 验收 ID | 场景 ID | 验证层级 | Evidence |
|---|---|---|---|
| AC-001 | CFG-001 | unit/contract | `python3 -m unittest tests.test_bruce_config_contract tests.test_browser_provider` |
| AC-002 | BROWSER-001 | contract | `python3 -m unittest tests.test_validation_loop_contract tests.test_completion_contract` |
| AC-003 | BROWSER-002 | contract | `python3 -m unittest tests.test_validation_loop_contract tests.test_supporting_skill_contracts tests.test_explore_prototype_contract` |
| AC-004 | BROWSER-003 | contract | `python3 -m unittest tests.test_validation_loop_contract tests.test_completion_contract tests.test_failure_policy` |
| AC-005 | MIGRATION-001 | contract | `python3 -m unittest tests.test_validation_loop_contract tests.test_prototype_contract` |

## 前置条件与真实依赖

- Python 3、PyYAML 和仓库现有 unittest 依赖。
- 不需要真实浏览器，因为本次测试锁定配置与流程契约；真实 Provider runtime preflight 属于后续宿主执行证据。

## 按比例确定视觉验证范围

- 范围：browser-smoke|browser-layout（规则契约变更；不执行业务页面视觉验收）。
- 判断依据：本变更改变用户可见 Web 的验证 Provider 和布局证据规则，但不修改具体产品页面。
- 对于 browser-layout：Provider 必须提供目标、viewport、截图/hash、几何/溢出和交互前后检查。

## 一致性分类

```yaml
behavior_kinds:
  - availability_derivation
consistency_check: not_applicable
reason: 本变更不修改业务资源、权限投影、持久化关系或跨对象数据不变量；只改变验证能力选择和证据契约。
```

## 一致性与权威状态矩阵

> not_applicable：本变更不涉及业务持久化或跨对象一致性。

## 冲突与权限视角场景矩阵

> not_applicable：本变更不涉及业务资源冲突、角色权限或持久化数据。

## 状态与意图矩阵

| 起始状态 | 用户/系统意图 | 预期行为 | 数据后果 |
|---|---|---|---|
| 未配置 Provider | 使用默认浏览器验证 | 解析为 `ego-lite` | 无业务数据变化 |
| 配置 `chrome` | 使用当前 Chrome 验证 | 证据记录 `chrome` | 无业务数据变化 |
| 配置非法 Provider | 防止不确定的验证环境 | 配置错误并阻塞依赖验收 | 无业务数据变化 |
| Provider 不可用 | 保持证据真实 | incomplete/blocked，不 fallback | 无业务数据变化 |

## 测试场景

### CFG-001：默认与显式 Provider 配置

- 映射到：AC-001、AC-002
- 类型：happy/edge
- Given：工作区和模板配置都由 PyYAML 读取，工作区未配置或显式配置 `ego-lite`/`chrome`。
- When：运行配置契约测试并检查 Provider 枚举规则。
- Then：默认是 `ego-lite`，显式 `chrome` 可表达，非法值不被接受。
- 预期 UI 状态：not_applicable；本任务不运行业务页面。
- 预期 API/结果：not_applicable；本任务不调用业务 API。
- 持久化不变量：not_applicable；不修改业务数据。
- Evidence：`tests/test_bruce_config_contract.py`、`tests/test_browser_provider.py` 和相关契约测试。
- 必需验证层级：unit/contract。

### BROWSER-001：按 Provider 记录浏览器证据

- 映射到：AC-002
- 类型：integration/contract
- Given：任务声明 `browser-smoke` 或 `browser-layout`，Provider 为 `ego-lite` 或 `chrome`。
- When：验证规则准备并检查 browser evidence。
- Then：证据必须记录实际 Provider；不允许用未配置 Provider 的结果充当当前证据。
- 预期 UI 状态：Provider 执行时必须产生真实可见结果；本测试只检查契约。
- 预期 API/结果：not_applicable。
- 持久化不变量：not_applicable。
- Evidence：`verification-loop.md`、`completion-gate/SKILL.md` 和证据字段契约。
- 必需验证层级：contract。

### BROWSER-002：布局范围要求完整视觉证据

- 映射到：AC-003
- 类型：edge/contract
- Given：可见结果包含布局、viewport、overflow、响应式或原型匹配风险。
- When：声明 `browser-layout` 并执行 Completion Gate 规则。
- Then：必须有截图、viewport、几何/overflow、交互前后状态；DOM 文本不能替代。
- 预期 UI 状态：not_applicable；不运行具体页面。
- 预期 API/结果：not_applicable。
- 持久化不变量：not_applicable。
- Evidence：规则文本和 `tests/test_validation_loop_contract.py`。
- 必需验证层级：contract。

### BROWSER-003：Provider 不可用时 fail-closed

- 映射到：AC-004
- 类型：error/recovery
- Given：Provider 标识非法、能力 preflight 不可用或证据不完整。
- When：进入浏览器依赖批次或 Completion Gate。
- Then：相关验收为 incomplete/blocked/issues，不降低 scope，不静默 fallback，不报告通过。
- 预期 UI 状态：无法收集有效浏览器证据时保持未验收；不伪造页面结果。
- 预期 API/结果：配置或能力错误被报告。
- 持久化不变量：not_applicable。
- Evidence：`tests/test_validation_loop_contract.py`、`tests/test_completion_contract.py`、`tests/test_failure_policy.py`。
- 必需验证层级：unit/contract。

### MIGRATION-001：历史 visual scope 兼容

- 映射到：AC-005
- 类型：regression/contract
- Given：历史文档或任务使用 `chrome-smoke`/`chrome-layout`。
- When：更新规则和模板。
- Then：旧名称有明确兼容映射，新文档使用 `browser-smoke`/`browser-layout`，不改变证据强度。
- 预期 UI 状态：not_applicable。
- 预期 API/结果：not_applicable。
- 持久化不变量：not_applicable。
- Evidence：契约测试和仓库定向搜索。
- 必需验证层级：unit/contract。

## 回归来源

- 当前 `chrome-smoke`/`chrome-layout` 硬绑定规则 -> MIGRATION-001、BROWSER-002。
- 当前 Chrome unavailable 必须 blocked -> BROWSER-003，迁移后改为 selected Provider unavailable 必须 blocked/incomplete。

## 限制与未验证边界

- 本次不连接真实 ego-lite 或 Chrome；不能证明宿主 runtime 的具体 API、登录态继承、扩展加载或截图落盘实现。
- 本次不运行业务页面；产品页面仍需在所选 Provider 上按任务合同执行真实交互和视觉证据。
- Provider 的真实能力由每次浏览器批次的 capability preflight 证明。

## 自检

- 每个 acceptance item 都映射到了证据。
- 每个 behavior scenario 都有 Given/When/Then 和可执行契约检查。
- consistency_check 为 not_applicable，已说明不涉及业务持久化关系。
- 本变更未修改业务 UI/API/数据库。
- Provider 不可用时保持 fail-closed。
- 新 scope Provider 中立，旧 scope 有兼容映射。
- 中文自然语言字段使用简体中文，稳定标识和路径保持原样。
