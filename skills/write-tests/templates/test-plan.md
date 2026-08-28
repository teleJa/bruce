# 测试计划：<变更名称>

## 验收映射

| 验收 ID | 场景 ID | 验证层级 | Evidence |
|---|---|---|---|
| <验收 ID> | <场景 ID> | <unit/component/integration/API/database/Chrome> | <命令或当前观察> |

## 前置条件与真实依赖

- <服务、数据库、凭证、fixture、浏览器会话，或无>

## 按比例确定视觉验证范围

- 范围：<none|chrome-smoke|chrome-layout>
- 判断依据： <为什么该可见结果以及当前渲染风险需要此层级>
- 对于 `chrome-layout`： <目标 URL/tab、viewport、截图/hash、几何/溢出和交互检查>

## 一致性分类

```yaml
behavior_kinds:
  - <resource_binding|exclusive_ownership|permission_projection|availability_derivation|shared_resource|state_transfer>
consistency_check: <required|not_applicable>
reason: <若为 not_applicable，说明不涉及跨对象状态、权限投影或持久化关系>
```

## 一致性与权威状态矩阵

> 当 `consistency_check: required` 时必须填写。若为 `not_applicable`，保留本节并说明原因。

| ID | 主体 | 关联资源 | 业务不变量 | 当前权威状态源 | 竞争者/权限视角 | 状态时间窗口 | 冲突/错误规则 | 数据后果 | UI/API 重新同步 |
|---|---|---|---|---|---|---|---|---|---|---|
| <CONS-001> | <主体> | <关联资源> | <必须始终成立的业务不变量> | <权威 API/服务/数据库> | <竞争实体或权限视角> | <读取到提交的时间窗口> | <冲突、无权、缺失或未知时的规则> | <成功/失败后的数据结果> | <页面/API 如何重新同步> |

## 冲突与权限视角场景矩阵

> 当 `consistency_check: required` 时，填写所有适用场景。每行必须能映射到一个可执行 scenario。

| 场景 ID | 适用性 | 不适用原因 | 起始状态 | 角色/操作者 | 动作 | 预期 UI 状态 | 预期 API/结果 | 持久化不变量 | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| <CONS-S-001> | <applicable|not_applicable> | <不适用原因> | <资源已被其他实体占用或关联对象不可见> | <角色/用户> | <打开、选择、提交或使用> | <页面状态和原因> | <接口结果和错误语义> | <冲突后数据不变或满足共享规则> | <API/database/Chrome 等证据> |

## 状态与意图矩阵

| 起始状态 | 用户/系统意图 | 预期行为 | 数据后果 |
|---|---|---|---|
| <起始状态> | <用户/系统意图> | <预期结果> | <写入、历史或 current-pointer 影响> |

## 测试场景

### <scenario-id>：<场景名称>

- 映射到： <验收 ID 和可选 task id>
- 类型： <happy/edge/error/integration/permission/regression>
- Given: <具体用户/系统状态、数据、权限和真实依赖>
- When: <用户或系统动作>
- Then: <可观察行为以及数据/状态后果>
- 预期 UI 状态： <适用时填写页面、控件、文案、可用性或 loading/error 状态；不适用写 not_applicable 及原因>
- 预期 API/结果： <适用时填写响应、错误码或服务端裁决；不适用写 not_applicable 及原因>
- 持久化不变量： <适用时填写关系、数据完整性或不变性；无持久化时写 not_applicable 及原因>
- Evidence: <每个重要 Then 对应的确切命令、API/database 检查或 Chrome 可见观察>
- 必需验证层级： <unit/component/integration/API/database/Chrome>

## 回归来源

- <Bug 或既有覆盖缺口> -> <scenario id>

## 限制与未验证边界

- <fixture、mock 或当前环境不能证明什么，以及仍需执行的真实检查>

## 自检

- 每个 acceptance item 都映射到了证据。
- 每个 behavior scenario 都有具体的 Given/When/Then，每个重要 Then 都有可执行的证据路径。
- 若 `consistency_check: required`，已定义业务不变量、权威状态、竞争 actor/viewer、冲突规则和重新同步方式。
- 若 `consistency_check: required`，已按 `behavior_kinds` 标记场景适用性和不适用原因，仅对适用场景验证 UI、API/result 或持久化后果。
- Stateful behavior 已按适用性覆盖 repeat use、failure 和 recovery。
- 命令和环境在目标仓库中真实存在。
- 用户可见 Web 验收必须使用 Codex App Chrome capability 和当前用户会话；Acceptance row 必须记录真实交互、结果可见状态以及截图或等价 Chrome visual artifact。禁止使用 Playwright 替代该证据。
- 中文请求的自然语言字段全部使用简体中文；稳定的 `Given`、`When`、`Then`、`Evidence`、scenario id、命令、路径和 API 名称保持原样。
