# Jev 启发的高效开发 Skill

**用更窄的检索、更少的重复操作完成开发任务；无需 TypeSafe 账号、API key、服务器或插件服务。**

[English overview](../../README.md) · [Skill 正文](../skills/jev-universal/SKILL.md) · [效率调研](efficiency-research.md) · [可选 TypeSafe MCP 适配器](../README.md)

Jev 是 TypeSafe AI 的决策模型。本仓库默认提供的是面向编码任务的提示词 Skill：结合常见的上下文节省做法，以及 Jev 公开介绍中的“拆成窄判断、再按明确规则决策”的思路。可用于 Claude、ChatGPT、Kimi Code、ZCode 等助手。**它不是 Jev 模型，也不保证固定的 token 或时间节省。**

## 使用

把 `jev-universal/skills/jev-universal/` 放入客户端支持的 skills 目录，或将 `SKILL.md` 指令添加到项目/用户规则。Skill 适用于编码、调试、测试、代码审查和仓库调研。

它要求先找出会改变实现的少数问题，再沿最相关的代码路径调查；限制噪声命令输出，复用未变化的证据，避免重复操作，并保留必要验证。它不会要求每个任务都输出长篇结构化分析，也不允许靠跳过测试来“省 token”。

实际节省需用相同任务做对照，记录端到端输入/输出 token、工具调用、耗时和任务成功率。最后完成评测的版本在全 pinned 快速路径修复反序配对中少用 15.4%、4.0%；key-file 功能任务首轮少用 26.3%，但反序复测因本机 Python 环境被 macOS 标为未下载而中止，不能纳入效果结论。有效配对的全套测试和目标 Ruff 均通过。当前草稿进一步规定：任务或验证命令已给出文件路径时，不要再枚举目录；该规则尚未评测。完整数据、限制和后续目标见[调研依据和限制](efficiency-research.md)。

## 可选：TypeSafe API 适配器

仓库另保留 MCP 适配器，供已有 TypeSafe API 权限的人使用。使用本 Skill 不依赖该适配器。见[适配器配置](../README.md)。

### 本地客户端配置

在 `jev-universal` 包目录中生成客户端配置，例如：

```sh
uv run --no-editable jev-universal --env-file /absolute/path/private.env config --client zed
```

已支持 `claude`、`kimi`、`zcode`、`zcode-native`、`codex` 和 `zed`。命令只打印配置，不会修改你的客户端文件。把生成的 `jev-universal` 条目合并到现有设置中，不要覆盖整个设置文件，也不要删除已有 MCP server、profile 或编辑器设置。

- Claude Code：合并到项目 `.mcp.json`；Claude Desktop 使用自己的 MCP 设置文件，可使用同一份生成 JSON。
- Kimi Code：合并到 `.kimi-code/mcp.json` 或 `~/.kimi-code/mcp.json`。项目配置需要先在客户端中信任目录。
- ZCode：在 Settings → MCP Servers → Full configuration 导入 JSON，或按需合并原生 `.zcode` 配置。
- Codex：把生成的 TOML 合并到相应 MCP 设置，或使用本包的本地插件配置。
- Zed：在 Settings → AI → MCP Servers 添加本地服务器，或运行 `zed: open settings file` 打开 `settings.json`。把生成的 `context_servers.jev-universal` 对象合并进已有 `context_servers`，保留其它 `context_servers` 条目，不要覆盖完整 `settings.json`。

API key 应保存在私有 env 文件或 `TYPESAFE_API_KEY_FILE` 指向的密钥文件中。生成的客户端配置只应包含 env 文件路径，不应包含密钥值；不要把密钥粘贴进助手对话、编辑器设置或仓库。

MIT 许可。此仓库许可不包含 TypeSafe 模型或服务的访问权。
