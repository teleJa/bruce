# T-005：派生 Environment Operation Manifest

- Contract revision: 1

## Objective

定义从精确确认的 Environment Profile 派生项目级操作 Manifest 的边界、模板和安全约束。

## Included scope

- `skills/environment-operations/SKILL.md`；
- `skills/environment-operations/agents/openai.yaml`、Manifest 模板和静态 validator；
- Environment Profile 的开发/测试拓扑、构建/部署/生命周期操作和 operation_manifest 字段；
- 派生 Manifest 的 Profile revision/hash 绑定和高风险操作排除；
- Bruce capability routing、profile lifecycle/security references、README 和对应契约测试。

## Dependencies

- T-002 Environment Profile user declaration, topology, operation and confirmation contract；
- Environment Profile schema、模板和静态 validator。

## Excluded scope

- 不执行 build、deploy、start、stop、migration、reset、drop 或 credential retrieval；
- 不从仓库源码、Makefile、历史命令或测试文件推导操作；
- 不授予远程部署、生产、数据库写入或凭证读取权限；
- 不动态注册或安装项目级/全局 `SKILL.md`。

## Acceptance

- 只有 confirmed Environment Profile 才能生成可用 Manifest；
- Manifest 绑定源 Profile revision/content hash；
- 只封装已确认的操作，默认排除高风险操作；
- Profile stale 时 Manifest 必须 stale 或要求重新生成；
- 操作成功不等于运行时验收或 Completion。

## Verification

执行 Skill metadata、Manifest template/validator、source Profile binding、high-risk exclusion 和 contract tests。

## Authorization and risks

- Authorization：Manifest 生成是用户显式请求的文档/能力生成动作，不授权运行环境操作。
- Risk：若把未确认命令或隐含权限写入 Manifest，可能形成授权升级；因此只允许用户确认的 operation entries。

## Contract change rule

Environment topology、operation fields、source Profile binding 或 authorization semantics 变化时增加 contract revision。
