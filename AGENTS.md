# 项目 Agent 指引

## 本地 Bruce 插件刷新

修改本项目的 Codex Bruce 插件后，使用以下命令刷新本地插件缓存：

```sh
python3 scripts/refresh_local_plugin.py /Users/tele/ai-workspace/bruce
```

不要直接执行 `codex plugin add` 代替该脚本。刷新完成后必须新建 Codex 任务/会话；运行中的会话会保留旧插件缓存的绝对 `PLUGIN_ROOT`，旧缓存被替换后可能导致 `PostToolUse` hook 找不到 `post_tool_review_reminder.py`。
