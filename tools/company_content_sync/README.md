# 公司内容同步

这是公司稿「本地 `draft.md` → 锁定 AppSo 排版校验 → 飞书在线文档预览与协作 → 微信草稿准备」的轻量总入口。人和 Agent 共用一个 CLI；不启动常驻服务、不后台轮询，也不维护第二套公司 CSS。

当前版本是 `0.3.0`。公司稿默认把可见预览交付为飞书在线文档链接；本地锁定 HTML 先完成确定性版式校验，并继续作为微信样式保真凭据和离线回退。真实 create／fetch 只有在 MCP 配置、UAT、host 工具证明与本次精确授权同时成立时才会放行。微信公众号写入仍保持关闭。

## 唯一入口

- Agent：使用 `$company-content-sync`。
- 人：首次 clone 先运行 `tools/bootstrap.ps1`，之后从仓库根目录运行 `powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 company status <内容包> --json`。

`status` 是只读操作，并且只返回一个 `next_action`：

- 有完整命令时读取 `command`。
- 缺精确 tenant／目录时读取 `command_template` 与 `required_inputs`。
- `tool_blockers` 表示工具故障；`workflow_blockers` 表示稿件流程不能继续。
- `operational_ok` 只表示 CLI 可运行，不等于 `workflow_ready`。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 company doctor --json
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 company connector-doctor --json
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 company status "微信公众号/内容/2026/07/<slug>" --json
```

## 最短流程

```text
status
  → configure-company（旧稿缺路由时，只补安全的本地手工路线）
  → build（先用锁定 Profile 完成本地版式与保真校验）
  → feishu-prepare-push（本地密封 intent，不联网）
  → 接入可信的一次性飞书执行器（官方 connector + 当前授权证明 + claim 原子消费）
  → 对精确 authorization_scope_sha256 取得本次授权
  → feishu-begin-push（落一次性持久 dispatch claim）
  → 可信执行器只放行 1 次 create-doc，再调用 fetch-doc
  → feishu-commit-push（白名单回执 + readback，建立同步基线）
  → 返回经过校验的飞书文档 URL，作为默认在线排版预览
  → 团队在飞书编辑；不轮询
  → feishu-prepare-pull
  → Agent 调用 fetch-doc
  → feishu-stage-pull（三方比较，只暂存）
  → feishu-accept-pull（显式接受，只替换正文）
  → 重新通过事实、权利与终校门禁
  → build（团队修改后重新锁定 Profile，生成本机 HTML）
  → 精确公众号账号 × 格式合同资格门
  → 单独授权后才可创建微信草稿
  → 人工后台与手机预览
```

团队修改不会直接覆盖 `draft.md`。`stage` 只写候选；只有下一动作明确成为 `accept_feishu_pull` 后，显式接受才替换正文，并把稿件降回 `editorial_review`。事实与终校失效；图片变化时权利检查也失效。

## 命令

| 命令 | 外部写入 | 用途 |
|---|---:|---|
| `doctor` | 否 | 校验唯一版式角色、文件哈希、品牌资产、Node 和精确解析器版本 |
| `connector-doctor` | 否 | 检查当前 `CODEX_HOME` 的飞书 Remote MCP 非敏感配置状态 |
| `status` | 否 | 汇总状态并给出唯一下一步 |
| `configure-company` | 否 | 只补缺失的 `appsso + manual_editor + default` 路由；冲突时拒绝覆盖 |
| `feishu-prepare-push` | 否 | 绑定 tenant、目标目录、正文、发布配置和图片哈希，生成 create intent |
| `feishu-begin-push` | 否 | 在可信执行器可用且已取得精确授权后，消费一次性 dispatch claim |
| `feishu-commit-push` | 否 | 校验 create／fetch 白名单回执与读回，成功后建立基线 |
| `feishu-prepare-pull` | 否 | 为精确文档生成只读 fetch intent |
| `feishu-stage-pull` | 否 | 校验拉回回执，执行本地／基线／远端三方比较 |
| `feishu-accept-pull` | 否 | 在本地未变化时接受暂存正文并重开编辑门禁 |
| `build` | 否 | 调用锁定扩展，生成 `article.html` 与密封回执 |

飞书在线文档承载协作与读者可见预览；它不会像素级复刻公众号 CSS。`article.html` 是精确微信样式的锁定依据，但默认不再用浏览器本地页代替飞书交付。连接器未就绪时必须明确报错；只有用户另行同意，才可把本地 HTML 作为临时预览回退。

旧公司稿可先运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 company configure-company <内容包> --json
```

它不会把稿件切到公众号 API 路线，也不会覆盖已有冲突值。

准备新建飞书文档需要两个非凭据输入：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 company feishu-prepare-push `
  <内容包> `
  --tenant-fingerprint "<64 位小写 SHA-256>" `
  --parent-id "<公司飞书文件夹不透明 ID>" `
  --json
```

`prepare` 不等于授权，也不等于已经创建文档。

## 飞书连接器配置诊断

`connector-doctor --json` 只读取当前 `CODEX_HOME/config.toml` 和环境变量名是否存在；不读取或输出 Token 值，不联网，也不执行飞书工具。安全的最小配置是：

```toml
[mcp_servers.feishu_docs]
url = "https://mcp.feishu.cn/mcp"
enabled = true
required = false
enabled_tools = ["create-doc", "fetch-doc"]
default_tools_approval_mode = "prompt"
startup_timeout_sec = 20
tool_timeout_sec = 120
http_headers = { "X-Lark-MCP-Allowed-Tools" = "create-doc,fetch-doc" }
env_http_headers = { "X-Lark-MCP-UAT" = "FEISHU_MCP_UAT" }
```

UAT 只放在本机进程环境变量 `FEISHU_MCP_UAT`，不要写入仓库、配置文件、聊天或日志。应在启动公司 Codex 的同一个 PowerShell 窗口中设置它；配置完成后重启 Agent host，再运行：

```powershell
$env:FEISHU_MCP_UAT = "<从飞书开放平台取得的 UAT>"
.\tools\codex-company.cmd
```

新会话中再运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 company connector-doctor --json
```

配置有效只代表 connector 可开始握手，不代表已取得本次写入授权，也不代表可信执行器可用。只有 host 对实际 `create-doc`／`fetch-doc` 工具完成证明，并能把当前会话的一次性授权与 claim 原子绑定时，`trusted_executor_available` 才能变为 true。

host 在当前会话确实发现了精确的 `create-doc`、`fetch-doc` 两项工具后，可为本次 CLI 调用设置非敏感证明变量：

```powershell
$env:FEISHU_MCP_HOST_TOOLS_ATTESTED = "create-doc,fetch-doc"
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 company connector-doctor --json
```

该变量不是 Token，也不是用户授权；工具未实际加载时不得伪造。会话结束后移除它。实际 begin 仍需当前任务对精确 tenant、文件夹、正文、图片和「新建 1 份文档」的明确授权。

参考：[飞书官方 Remote MCP](https://open.feishu.cn/document/mcp_open_tools/developers-call-remote-mcp-server?lang=zh-CN) 与 [Codex MCP 配置](https://developers.openai.com/codex/mcp/)。

## 一次性飞书派发

`push_prepared` 之后，`status` 会检查可信执行器。若 `capabilities.feishu_trusted_dispatch_executor` 为 `false`，就返回 `integrate_trusted_feishu_executor`；此时直接运行 `feishu-begin-push` 会失败，而且不会落 claim。

仅安装 connector 不足以解锁 begin。Agent host 还必须把本次会话的授权证明与 claim 原子绑定，只放行 1 次 `create-doc`，并保存可核验的 connector 调用证据。该执行器接入后，Agent 才能在取得本次精确授权后执行 `status.command` 中的 begin 命令。begin 会再次验证：

- `draft.md` 仍为 `ready`，正文哈希未变化。
- `publish.yml`、项目路由和授权 scope 未变化。
- `payload.md`、`assets.json`、`intent.json`、回执模板均存在且哈希一致。
- 每张本地图片的路径、大小、顺序和 SHA-256 一致。
- 可信执行器与 connector 当前确实可调用。

claim 一旦落盘，状态即按 `push_in_flight`／结果未知处理。进程崩溃、超时、取消或状态文件丢失都不得第二次 create；只能只读核对精确 operation。

当前只支持安全的「新建 1 份文档」。没有服务端 revision／CAS 时，已有文档覆盖更新保持关闭；不能用「先读后写」冒充条件更新。

`authorization_scope_sha256` 只是精确范围标识，不是授权凭据。正式执行必须另外绑定当前会话产生的不可复用授权证明。

## 白名单回执

CLI 不持有 Token、Cookie、完整请求头或 MCP 登录态。Agent 只能在对应 operation 目录写规范化字段，不能保存完整 MCP 响应。

确认 push 至少要求：

- 协议、operation、intent、idempotency 与授权 scope 全部匹配。
- 固定官方 server ID，精确 `create-doc`／`fetch-doc` 工具名。
- write／read 使用不同 call ID，各自明确 `isError: false` 并记录响应 SHA-256。
- `completed_at` 不早于一次性 dispatch claim。
- tenant、目标目录与访问策略检查通过。
- 文档 ID、无查询参数的受信 `*.feishu.cn/docx/...` 或 `*.feishu.cn/wiki/...` URL、revision、标题与正文 readback 完整一致。
- 图片数量、顺序、源 SHA-256 与远端 token 全部对应。
- 顶层、MCP、访问、读回和图片映射出现任何未知字段都会拒绝。

回执被拒绝后进入 `result_unknown`，不会重新出现 begin／create。Pull 标题漂移、frontmatter、表格、mention、附件、未知图片或无法无损映射的块进入 `conflict`，不会让远端修改本地路由和发布状态。

## 安全日志与本地文件

两类文件都被 Git 忽略：

```text
.company-content-sync/journal/<package-hash>/
  state.json
  claims/<operation_id>.json

<内容包>/dist/content-sync/
  state.json
  article.html
  build.json
  ops/<operation_id>/...
```

`.company-content-sync/journal/` 是防重复写的持久安全日志；内容包下的 `dist/content-sync/` 是工作快照和生成物。写状态时先写 journal，再写内容包快照，并使用单调序号拒绝过期 writer。

不要在存在 pending／in-flight operation 时删除 journal。即使 `dist/` 被删，journal 仍会恢复已同步或结果未知状态。只要 `dist/state.json` 已进入协议状态却缺少对应 journal，CLI 就会硬失败；换电脑后必须先只读核对远端，不能继续 begin／create。

源 Markdown 始终是内容包内的 `draft.md`。本机可长期保存源 Markdown；精确微信样式凭据保存在 `dist/content-sync/article.html`，默认在线预览地址记录在同步状态与成功回执的 `document_url`。

## 版式如何锁定

`profile.json` 是唯一合同声明，真正决定输出的数据平面只有：

`tools/company_content_sync/locked_format_adapter.py`

它包含 Markdown／frontmatter 解析、块映射、图片内嵌、AppSo 题图、renderer payload、Node bridge 调用、HTML 大小门和 fidelity 判定。飞书状态机、授权和回执代码不在该文件中，因此修改协作协议不会旋转版式合同。

Profile 要求以下 role／asset 全局唯一，缺失或重复都会硬失败：

- `markdown_adapter`
- `renderer_bridge`
- `renderer_and_semantics`
- `appso_title`

并精确锁定：

- `markdown-it-py == 4.0.0`
- `mdurl == 0.1.2`
- bridge、扩展 renderer、品牌资产及策略文件 SHA-256
- style version 与关键 CSS 断言

`build` 按 Profile role 实际执行 bridge 和 renderer，完成后再次比较执行文件哈希。密封回执绑定 `format_profile_sha256`、adapter、bridge、renderer、题图、格式合同与 HTML；只补公众号资格回执不会让同一 HTML 失效。

`local_format_qualified: true` 只表示本机确定性渲染与内容保真通过。生产资格还必须绑定 `sealed_draft + appsso-article-v1`、精确公众号账号指纹与可验证的后台往返回执。当前仍是 `production_qualified: false`。

即使资格通过，`wechat_create_draft` capability 仍必须为 true；否则唯一下一步是接入并约束现有 `微信公众号/tools/wechat_publish.py`，不会直接声称可以创建草稿。

Markdown 入口故意严格：正文只允许 H2／H3；H3 必须已有 H2；相同的开头 H1 会作为文章标题移除；其他 H1、H4+、嵌套列表和图文混排段落直接失败，不做猜测。

## 微信草稿离线预检

现有发布器已经提供两个无外部写入的探针：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 wechat capability --json
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 wechat sealed-draft-dry-run `
  <内容包> `
  --build <内容包>/dist/content-sync/build.json `
  --json
```

`capability` 不读凭据、不调用 Wenyan、不联网。`sealed-draft-dry-run` 校验密封 HTML、Profile、本地往返回执、账号路线、封面和图片权利，并生成确定性的 `operation_id` 与完整性范围；它同样不读凭据、不联网、不创建草稿。未完成精确账号 × 格式合同本地往返时必须失败关闭。本地回执不是 host 签名的生产授权，因此 `trusted_production_qualification`、`authorization_ready`、`sealed_html_execute` 与 `wechat_create_draft` 都保持 false。

## 性能预算

- `status`：正常内容包目标 `< 1 s`。
- `build`：正常长文目标 `< 3 s`。
- prepare／begin／commit／stage／accept：只做本地确定性计算与原子写入。
- 协议预检只验证图片，不生成 Base64；只有正式 build 才内嵌图片。
- 不在每篇稿上跑截图回归；只有 Profile／扩展版本变化时跑视觉回归。
- 不引入实时协同引擎、事件总线或后台轮询。
- 网络和人工协作耗时单独记录，不冒充排版耗时。
