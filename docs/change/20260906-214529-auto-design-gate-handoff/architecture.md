# 架构：方案写入到 Design Gate 的同轮自动衔接

## 当前问题

方案写入类 Skill 当前会返回 `Document check: clear|issues` 并提示 Design Gate 必要性，但部分规则同时写有“do not invoke it automatically / 不要自动调用”。这会让调用链在方案落盘后停住，把本应由 Bruce 完成的门禁衔接转化为用户的下一条指令。

## 决策

采用“writer 产出 handoff，Bruce 立即编排 Gate”的两层责任模型：

1. 方案 writer 负责工件写入、局部一致性检查和是否满足 Design Gate predicate 的判定信息。
2. 当工件会约束后续实现时，writer 返回 mandatory `design-gate` handoff；调用方不得结束当前轮次或等待用户重复授权。
3. Bruce 在同一轮消费 handoff，立即调用唯一的 `design-gate`；只有该 Gate 可以持久化 `design-review.md` 并返回 `Design: pass|blocked`。
4. Gate 结果不改变原任务授权：`design-only` 停止在 Gate，implementation scope 仅在 pass 后继续，blocked 时停止受影响实现。

## 组件责任

| 组件 | 负责 | 不负责 |
|---|---|---|
| 方案 writer Skills | 写入各自工件、执行 `Document check`、声明 mandatory Gate handoff | Design verdict、行为实现、Completion verdict |
| Bruce core workflow | 识别 handoff，在同一轮自动调用 `design-gate`，保持授权边界 | 绕过 Gate、把 pass 当成新的实施授权 |
| `design-gate` | 工件完整性、文档就绪度、validator 和唯一 Design verdict | 行为实现、交付完成判定 |
| artifact policy | 判断哪些持久化工件属于治理型设计 | 因“文件已保存”而一律触发 Gate |

## 控制流

```text
persist governing artifacts
  -> Document check
  -> mandatory design-gate handoff
  -> Bruce invokes design-gate in the same turn
  -> Design: pass | blocked
  -> stop for design-only OR continue already-authorized implementation on pass
```

## 失败与恢复

- writer 文档检查有问题：先修复工件，不进入虚假的 pass。
- Gate 输入不完整或 validator 非零：返回 `Design: blocked`，不得继续受影响实现。
- 原型仍等待用户确认：确认前不伪造“成功落盘且可治理”的状态；确认完成后自动衔接 Gate。
- 普通执行清单：artifact policy 判定不适用，不生成无意义的 review。

## 兼容性

不改变 `Design: pass|blocked`、`design-review.md`、validator、Completion Gate 或 Skill id。仅改变方案 writer 与 Bruce 之间的控制流契约，移除“用户必须再发一条 Gate 指令”的交互要求。
