# Jev 启发的高效开发 Skill

**用更窄的检索、更少的重复操作完成开发任务；无需 TypeSafe 账号、API key、服务器或插件服务。**

[English overview](../../README.md) · [Skill 正文](../skills/jev-universal/SKILL.md) · [效率调研](efficiency-research.md) · [可选 TypeSafe MCP 适配器](../README.md)

Jev 是 TypeSafe AI 的决策模型。本仓库默认提供的是面向编码任务的提示词 Skill：结合常见的上下文节省做法，以及 Jev 公开介绍中的“拆成窄判断、再按明确规则决策”的思路。可用于 Claude、ChatGPT、Kimi Code、ZCode 等助手。**它不是 Jev 模型，也不保证固定的 token 或时间节省。**

## 使用

把 `jev-universal/skills/jev-universal/` 放入客户端支持的 skills 目录，或将 `SKILL.md` 指令添加到项目/用户规则。Skill 适用于编码、调试、测试、代码审查和仓库调研。

它要求先找出会改变实现的少数问题，再沿最相关的代码路径调查；限制噪声命令输出，复用未变化的证据，避免重复操作，并保留必要验证。它不会要求每个任务都输出长篇结构化分析，也不允许靠跳过测试来“省 token”。

实际节省需用相同任务做对照，记录端到端 input/output token、缓存、工具动作、耗时和任务结果。较长版 Skill 没有稳定收益，之后通过开发场景对照迭代了 runner 和 Skill。最新 1,123 字符版本在输出召回 CLI 功能任务的两组同提示、顺序平衡配对中合计少用 35.1% token，少 28 次工具动作，耗时少 33.9%；四组完整测试均通过（每组 52 个）。但在不同的 OAuth URL 校验 bugfix 中，同一 Skill 合计多用 26.0% token，尽管工具动作更少、耗时略短。后续触发条件试验没有稳定触发 Skill。P085 的证据交接候选合计少用 15.7% token，但只在跳过 Skill 的候选臂出现节省；加载 Skill 的配对反而多用 13.9%。P087 用干净 Git worktree 重跑功能任务后合计少用 11.6%，但未加载 Skill 的 A 臂少用 22%，加载 Skill 的 B 臂反而多用 1.6%；耗时只改善 0.7%。P084 CLI key 优先级任务则多用 7.7% token、耗时增加 14.4%；两臂 Ruff 导入排序失败。P086 因快照污染作废。P088 两个已加载 Skill 的候选臂合计少用 28.1% token，但都错误拒绝了合法整数写法“01”，因此质量门槛失败。P089 明确整数解析约定后，四臂测试与 lint 全通过、13 个旧测试均未改，但 Skill 组反而多用 6.5% token（工具动作少 18.5%，耗时少 3.7%）。P090 的输出检索任务中，配对结果因顺序反转：一个多用 13.6%，另一个少用 5.7% token；两组工具动作都更多。所有补丁虽通过聚焦测试和 lint，但 CLI 行为不一致，不能计作有效质量样本。P090 还发现干净 clone 缺少预装虚拟环境，导致 uv 尝试联网并重复验证，runner 需先修复离线环境注入。P091 的 key-file `~/` 配置任务合并少用 12.6% token；但两个 treatment 中只有 B 臂实际加载 Skill，唯一有效配对少用 17.0% token、工具动作少 25.8%，耗时反而多 1.6%。四臂完整测试均通过，旧测试均保持，但这是一个尚待重复的单配对信号。P092 在明确固定测试环境、并确保 treatment 读取 Skill 后复跑同类任务，结果反转：token 多用 20.2%，工具动作多 16.7%。两臂完整测试都仅因沙箱不能绑定 localhost 各失败 1 项，其余 62/63 项通过；7 个旧 CLI 测试函数均未修改。配置任务节省未能复现。runner 需显式指定共同锁定的 Python/Ruff 路径，避免环境探索污染成本。P093 的 all-pinned 元数据契约修复中，已加载 Skill 的单配对少用 18.9% token、23.5% 工具动作，耗时少 5.5%；两臂实现一致，旧测试均未改，完整测试除同一个沙箱 localhost 绑定错误外全过。这是一个质量保持的正向样本，但尚无重复。P091/P092 的 key-file 复测则从少 17.0% 反转为多 20.2%，说明收益不稳定。现有正向结果尚不能归因于 Skill，也未达到稳定节省目标。早期 P077/P078 候选组多收到了一条“先读 Skill”的额外指令，不是严格的同提示对照。2x 目标尚未达到。完整数据、限制和后续研究见[调研依据和限制](efficiency-research.md)。

另有一个可选的 Codex 专用大输出 hook：它把较长 Bash 输出暂存到本机，用预览替代完整结果，并提供按行/关键词取回的方法。四组顺序平衡配对合计节省 9.5% token；大输出任务为 14.8%，但反序样本从 20.6% 降到 6.3%，目前不能称为稳定收益。它不需要 TypeSafe/API，且不适用于 Claude、Kimi 或 ZCode；详情见[研究记录](efficiency-research.md)。

从 GitHub 安装 Codex 插件：

```sh
codex plugin marketplace add uninhibited-scholar/jev-universal --ref main --sparse .agents/plugins --sparse jev-universal
codex plugin add jev-universal@jev-universal
```

安装后在 Codex 中打开 `/hooks`，先检查并信任该 hook。只复制 Skill 的其它客户端不会启用这个 Codex 专用自动钩子。

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
