# 测试计划：Environment Profile 契约加固

## 范围与限制

本次只修改 Environment Profile 的静态校验、文档契约和契约测试；不执行项目构建、部署、登录、数据库操作或远程操作。
验证使用 Python `unittest` 临时目录 fixture，不依赖真实服务。

## 验收映射

| 场景 ID | Given | When | Then | Evidence |
|---|---|---|---|---|
| EP-CP-01 | 新格式本地 Profile 仅在 `test_context.configuration.env_file` 声明 `.env` | 执行 Validator | Profile 可被接受；同时声明旧 `local_env` 时拒绝 | `tests.test_environment_profile_contract` |
| EP-CP-02 | Workflow 引用不存在的 operation，或 operations 有重复 ID | 执行 Validator | Profile 被拒绝并指出引用/唯一性问题 | `tests.test_environment_profile_contract` |
| EP-CP-03 | Profile 状态为 `ready_for_confirmation` 且 hash 为短标签 | 执行 Validator | Profile 被拒绝，要求真实 SHA-256 hash | `tests.test_environment_profile_contract` |
| EP-CP-04 | 已确认 Profile 使用新 `.env` 位置 | 生成并执行 bounded runner fixture | 既有授权、脱敏和 dotenv 行为保持通过 | `tests.test_environment_operations_contract` |

## 命令

```sh
python3 -m unittest tests.test_environment_profile_contract tests.test_environment_operations_contract tests.test_verification_profile_contract
python3 -m py_compile skills/environment-profile/scripts/validate_profile.py
python3 -m pytest -q tests/test_environment_profile_contract.py tests/test_environment_operations_contract.py tests/test_verification_profile_contract.py
```

## 限制

当前 shell 的 `python3` 没有安装 `pytest`；若该环境仍未提供 pytest，pytest 命令只能记录为未执行，不能替代 unittest 证据。
