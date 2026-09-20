# Jev 调研与设计依据

核查日期：2026-09-20。

Jev 是 TypeSafe AI 的结构化决策模型。它以 state 和问题集合为输入，输出类型化判断；主模型仍负责规划、生成及复杂推理。官方声称批量独立问题可并行评估；这不是本项目的延迟实测结论。[官方介绍](https://docs.typesafe.ai/introduction)

当前 HTTP 接口为 `POST https://api.typesafe.ai/v1/systemone`，使用 Bearer key；模型别名为 `jev-latest`。Choice 返回选择、概率分布及 confidence；Score 按有序描述量表返回数值；Noul 返回 0–1 判断。插件使用接口的文本 instructions 子集，而非完整结构化 instructions。[API](https://docs.typesafe.ai/api)

官方已有 Typesafe agent skill，主要帮助编写集成。这里增加可被多个宿主直接调用的 MCP 服务、四类工具、响应校验以及保守上下文筛选，并非复制官方模型或声称官方合作。[Quickstart](https://docs.typesafe.ai/introduction/quickstart)

选择 MCP 而非四份模型 API 包装：插件运行在宿主的工具层，主模型与 Jev 分工。不同宿主的 hooks、插件清单并不一致；统一自动截取工具输出的方案不能仅凭 MCP 就保证，因此首版显式调用。

## 兼容依据

- [Claude Code MCP](https://code.claude.com/docs/en/mcp)：支持本地 stdio 和远程 MCP。
- [Kimi Code MCP](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/mcp.html)：提供 stdio、HTTP 配置；项目与用户配置使用 mcpServers。
- [ZCode MCP](https://zcode.z.ai/en/docs/mcp-services)：设置可导入 mcpServers JSON，支持 stdio/HTTP；需留意原生配置优先级。
- [ChatGPT 接入](https://developers.openai.com/plugins/deploy/connect-chatgpt)：开发者模式连接公网端点或安全隧道，需在实际账号里发现工具并验证调用。
- [官方 Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)：提供服务端、客户端和协议实现；本项目锁定依赖解析结果到 uv.lock。

## 目前不能据此声称的结论

没有真实 API key 测试，因此不报告 P50/P95、准确率、上下文压缩比例或节省费用。社交媒体热度不作为这些指标的证据。客户端联调进度见 validation.md；协议适配与生产验收是不同的验证层级。

建议验收：每个客户端发现四个工具；真实 Jev 分类及混合批量请求成功；输入含歧义时恢复主模型复核；缺 key/限流时保留原文；用自有标注样本比较正确率、漏删率、延迟和总成本后再设自动化阈值。

## v0.2.0 implementation update

The earlier prototype's machine-specific config was replaced by a pinned Git
launcher and per-installation config generator. Added an OAuth resource server,
explicit env/key-file support, response size limits and installable distributions.
Actual client verification is recorded separately in [validation](validation.md).
