# T-005：生成 Executable Environment Operation Skill

- Contract revision: 1

## Objective

定义从精确确认的 Environment Profile 派生项目级可执行操作 Skill 的边界、模板和安全约束。

## Included scope

- `skills/environment-operations/SKILL.md`；
- `skills/environment-operations/agents/openai.yaml`、Skill generator and bounded runner；
- Environment Profile 的开发/测试拓扑、构建/部署/生命周期操作声明；
- 生成 Skill 的 Profile revision/hash 绑定和高风险操作排除；
- Bruce capability routing、profile lifecycle/security references、README 和对应契约测试。

## Dependencies

- T-002 Environment Profile user declaration, topology, operation and confirmation contract；
- Environment Profile schema、模板和静态 validator。

## Excluded scope

- 生成阶段不执行 build、deploy、start、stop、migration、reset、drop 或 credential retrieval；
- 不在运行阶段从仓库源码、Makefile、历史命令或测试文件推导操作；Profile 已确认的 argv 可调用项目脚本或 Makefile；
- 不授予远程部署、生产、数据库写入或凭证读取权限；
- 不覆盖已有非 Bruce 生成的 Skill；生成目标为项目本地可执行 `SKILL.md` 和 runner。

## Acceptance

- 只有 confirmed Environment Profile 才能生成可执行 Skill；
- Skill 和 runner 绑定源 Profile revision/content hash；
- 只生成已确认 argv 的执行入口，critical 操作需要额外授权；
- Profile stale 或 hash 不匹配时 runner 必须 fail closed 并要求重新生成；
- Skill 生成或操作成功不等于运行时验收或 Completion。

## Verification

执行 Skill metadata、generated runner generation/execution、source Profile binding、existing Skill check、high-risk authorization 和 contract tests。

## Authorization and risks

- Authorization：Skill 生成是用户显式请求的代码/能力生成动作，不在生成阶段授权或运行环境操作。
- Risk：若把未确认命令或隐含权限写入 Skill，可能形成授权升级；因此只允许用户确认的 argv，并由 runner 执行风险门控。

## Contract change rule

Environment topology、operation fields、source Profile binding 或 authorization semantics 变化时增加 contract revision。
