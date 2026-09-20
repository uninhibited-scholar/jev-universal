# Jev Universal 中文说明

用同一套 MCP 工具，把 TypeSafe 的 Jev 接入 Claude、ChatGPT、Kimi Code（K3）、ZCode（GLM-5.3）和 Codex。主模型负责推理与执行，Jev 提供分类、评分、断言检查、路由建议及保守上下文筛选。

这是独立开源集成，不是官方插件或免费模型服务。每位使用者配置自己的 TypeSafe key。当前为预览版；实际验证范围见 [验证记录](validation.md)，不会把模拟测试称为真实 Jev 调用。

## 快速安装

先安装 uv；在终端运行：

```sh
git clone https://github.com/uninhibited-scholar/jev-universal.git
cd jev-universal
uv sync --project jev-universal --locked --no-dev --no-editable
uv run --project jev-universal --no-editable jev-universal probe
```

最后一条会验证 MCP 握手、四个工具的发现和固定内容原样返回，不消耗 TypeSafe 额度。

在仓库外建立私有 env 文件，写入 `TYPESAFE_API_KEY=你的密钥`。不要发到模型对话、提交 Git 或写入公开配置。在 macOS/Linux 上可用 `chmod 600` 限制文件读取权限。

```sh
uv run --project jev-universal --no-editable jev-universal --env-file /绝对路径/private.env doctor --live
uv run --project jev-universal --no-editable jev-universal --env-file /绝对路径/private.env config --client kimi
```

第一条会真实调用一次收费 API，测试 Choice、Score、Noul。第二条只生成配置，不覆盖已有设置。把输出的 Jev 条目合并到客户端 MCP 配置，保留其他服务。

| 客户端 | 用法 |
|---|---|
| Claude Code | `--client claude`，合并到项目 `.mcp.json` 并在客户端批准 |
| Claude Desktop | 使用同样的 JSON，合并到 Desktop MCP 配置 |
| Kimi Code | `--client kimi`，合并到 `.kimi-code/mcp.json`，首次交互启动时信任自己的项目 |
| ZCode | `--client zcode`，在设置 → MCP Servers → Full configuration 导入 |
| Codex | `--client codex`，生成 TOML 合并到 MCP 设置 |
| ChatGPT | 启动 HTTP 服务后使用安全隧道或经 OAuth 认证的 HTTPS 服务，见 [接入指南](hosting.md) |

K3、GLM-5.3 由宿主选择，插件不会修改模型设置。GUI 客户端未必继承终端环境变量，因此推荐生成带私有 env 文件路径的配置。不要将生成的本机路径提交到公开仓库。

## 工具与边界

- `jev_evaluate`：多个相互独立的问题一起分类或评分。
- `jev_route`：根据你提供的可用路线及能力描述建议选择，不自动调用模型。
- `jev_check`：逐项判断证据是否支持要求，不代替运行测试。
- `jev_select_context`：返回原文片段，只建议省略高置信度的无关内容。

每个上下文片段必须显式填写 `pinned: true/false`。固定用户约束、关键决定、未解决错误及证据。`pinned` 防止省略，不阻止传输：只要存在待判断片段，所传上下文会送往 TypeSafe；全固定请求不调用 API。调用方必须保存完整原文。

`review_required` 表示需要主模型或人工复核的判断。置信度不是实测准确率；未提供准确率、加速比、压缩率或成本节省保证。缺 key、超时、上游错误会明确失败，不编造结果。

HTTP 默认只监听本机；公网部署需要完整 OAuth 参数，使用者自行负责域名、TLS、身份提供商和额度管理。开源发布并不等同于已在每个人的 ChatGPT 账号里启用。
