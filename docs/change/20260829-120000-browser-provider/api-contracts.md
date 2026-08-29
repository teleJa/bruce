# 文件契约：可配置浏览器验证提供者

## browser-provider-configuration

- Change：added
- Provider：Bruce workspace configuration
- Consumers：verification loop、prototype skills、Completion Gate、contract tests
- Authoritative source：`.bruce/config.yaml` 与 `skills/bruce/templates/config.yaml`
- Compatibility：additive；未配置时默认 `ego-lite`，历史 visual scope 名称保留兼容映射
- Authentication/authorization：配置不授予登录、扩展或敏感数据传输权限

### 输入

```yaml
verification:
  browser_provider: ego-lite | chrome
```

默认规则：

```text
未配置 verification.browser_provider -> ego-lite
非法值 -> configuration issue，不得静默修复或 fallback
```

### Provider 能力契约

所选 Provider 必须在使用前证明与 scope 匹配的能力：

| Scope | 必需能力 |
|---|---|
| `browser-smoke` | navigate、real interaction、visible state、screenshot/artifact |
| `browser-layout` | browser-smoke 全部能力，加 viewport、geometry、overflow、before/after evidence |

### 成功结果

统一浏览器证据至少包含：

```yaml
browser_evidence:
  provider: ego-lite | chrome
  target: URL or runtime target
  session: task-space or current-chrome-session metadata
  actions: real actions corresponding to When
  visible_result: observed result
  capture_time: timestamp
  basis_revision: revision
  screenshot_artifact: path or hash
  geometry: required only for browser-layout
```

### 错误与恢复

| 条件 | 结果 | 重试/回退行为 |
|---|---|---|
| Provider 标识非法 | configuration issue | 不 fallback；修复配置后重跑 |
| Provider 不可连接 | blocked/incomplete | 按 L0/L2 规则处理；不换 Provider |
| Provider 缺少 scope 所需能力 | blocked/incomplete | 不降低 scope；补齐能力或显式改合同 |
| 证据缺少截图/可见结果 | issues/incomplete | 重新执行受影响场景 |
| 证据基于旧 revision | issues/incomplete | 代码变化后重新采集 |

### 验证

- 配置消费者：`tests/test_bruce_config_contract.py`
- 规则消费者：`tests/test_validation_loop_contract.py`、`tests/test_completion_contract.py`
- 模板消费者：`tests/test_supporting_skill_contracts.py`
