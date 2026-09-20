# Jev 启发的高效开发 Skill

**用更窄的检索、更少的重复操作完成开发任务；无需 TypeSafe 账号、API key、服务器或插件服务。**

[English overview](../../README.md) · [Skill 正文](../skills/jev-universal/SKILL.md) · [效率调研](efficiency-research.md) · [可选 TypeSafe MCP 适配器](../README.md)

Jev 是 TypeSafe AI 的决策模型。本仓库默认提供的是面向编码任务的提示词 Skill：结合常见的上下文节省做法，以及 Jev 公开介绍中的“拆成窄判断、再按明确规则决策”的思路。可用于 Claude、ChatGPT、Kimi Code、ZCode 等助手。**它不是 Jev 模型，也不保证固定的 token 或时间节省。**

## 使用

把 `jev-universal/skills/jev-universal/` 放入客户端支持的 skills 目录，或将 `SKILL.md` 指令添加到项目/用户规则。Skill 适用于编码、调试、测试、代码审查和仓库调研。

它要求先找出会改变实现的少数问题，再沿最相关的代码路径调查；限制噪声命令输出，复用未变化的证据，避免重复操作，并保留必要验证。它不会要求每个任务都输出长篇结构化分析，也不允许靠跳过测试来“省 token”。

实际节省需用相同任务做对照，记录端到端输入/输出 token、工具调用、耗时和任务成功率。最近三轮合成跨层评测结果仍然混合：一轮少用 26.7% token，一轮多用 9.7%，同类任务的反向顺序复测又少用 14.6%；两次同类测试合并后仅少用 2.5%。目前不能证明稳定节省，更未达到 2 倍目标。完整数据、限制和后续目标见[调研依据和限制](efficiency-research.md)。

## 可选：TypeSafe API 适配器

仓库另保留 MCP 适配器，供已有 TypeSafe API 权限的人使用。使用本 Skill 不依赖该适配器。见[适配器配置](../README.md)。

MIT 许可。此仓库许可不包含 TypeSafe 模型或服务的访问权。
