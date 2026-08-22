---
name: company-content-sync
description: Start and coordinate the lightweight company-content path from a local content package through locked AppSo validation, Feishu online-document preview and collaboration, and WeChat draft preparation. Use for APPSO/company articles, Feishu preview delivery, local formatted HTML fallback, Feishu push or pull planning, format-lock checks, sync conflicts, or WeChat draft handoff.
---

# 公司内容同步

这是公司内容协作的唯一 Agent 入口。详细命令、回执合同和人类说明只看 [工具 README](../../../tools/company_content_sync/README.md)；不要在聊天里另造状态机。

## 快速开始

1. 运行 `git status --short`，保留所有无关修改。
2. 优先使用用户指定的内容包；否则从当前目录向上发现唯一 `draft.md`。找不到或有歧义时再让用户选择，不要猜。
3. 从仓库根目录调用 CLI；若当前不在根目录，先用 `git rev-parse --show-toplevel` 得到根目录。
4. 运行 `status --json`，只执行返回的一个 `next_action`；完成后重新 status。
5. 优先执行 `next_action.command`。若只有 `command_template`，只补 `required_inputs`，不要猜 tenant、目录或账号。
6. `handler` 指向其他 Skill 时转入对应 Skill。任何 `conflict`、`result_unknown`、过期哈希、未知路径或 journal 异常都停止自动推进。

首次 clone 必须先运行 `tools/bootstrap.ps1 -FullTest`。公司 Agent host 只通过 `tools/workflow.ps1 codex-company` 或 `codex-company-feishu` 启动，以使用 clone 内锁定的 Codex 和独立 `CODEX_HOME`；不要回退到全局 CLI 或个人配置目录。

```powershell
$repoRoot = git rev-parse --show-toplevel
powershell -NoProfile -ExecutionPolicy Bypass -File "$repoRoot/tools/workflow.ps1" company status <内容包> --json
```

Windows PowerShell 读取中文 Markdown 时显式使用 `-Encoding UTF8`。

当 `next_action.id` 是 `integrate_trusted_feishu_executor` 时，先运行只读诊断，不要尝试 begin：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$repoRoot/tools/workflow.ps1" company connector-doctor --json
```

`connector-doctor` 只报告当前 `CODEX_HOME` 的非敏感配置状态以及环境变量名是否存在；不得读取、输出或代填 Token 值。

## 旧稿轻量迁移

当下一动作是 `configure_company_route`，执行返回的 `configure-company` 命令。它只能补缺失字段：

- `project_adapter: appsso`
- `delivery_mode: manual_editor`
- `layout_profile: default`

它不覆盖已有冲突值，不启用公众号 API，也不修改 `draft.md`。

## 默认排版预览

公司稿的默认可见预览是飞书在线文档。状态机仍会先运行本地 `build`，因为飞书 intent 必须绑定一份通过锁定 Profile 校验的 HTML；该 HTML 是微信样式凭据，不是默认交付面。

当下一动作是 `run_local_build` 时执行返回命令。仅当用户明确要求本机诊断预览或同意连接器失败后的临时回退时，才直接运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$repoRoot/tools/workflow.ps1" company build <内容包> --json
```

`build` 只写内容包下已忽略的 `dist/content-sync/`。源 Markdown 始终是 `draft.md`。不得静默改用 `wechat_publish.py preview --open` 冒充飞书上传成功；连接器未就绪时应停在明确 gate，并报告缺失条件。

排版硬门：

- 先由 `doctor` 验证唯一 Profile role、锁定文件哈希和精确依赖版本。
- 只调用 `locked_format_adapter.py` 与扩展 v1.10.0 的 renderer，不复制或近似改写公司 CSS。
- Markdown 映射不明确时硬失败。
- 区分 `local_format_qualified` 与 `company_format_qualified`；本地通过不代表公众号生产资格。

## 飞书 prepare／begin／commit

这些 CLI 命令只写本地文件；真实 MCP create／fetch 由 Agent host 执行。

`prepare_feishu_create`：

- 取得经只读确认的公司 tenant 指纹与目标文件夹 ID；不确定时向用户索取。
- 运行 command template，得到确定性的 operation、intent 与 `authorization_scope_sha256`。
- prepare 不是授权，也不代表飞书已创建。

`integrate_trusted_feishu_executor`：

- 先发现并验证官方飞书文档 connector，至少确认 `create-doc` 与 `fetch-doc` 可调用；仅安装 connector 不足以解锁 begin。
- 使用 `connector-doctor --json` 检查最小 allowlist 配置；若配置缺失，向用户报告需要在本机设置 `FEISHU_MCP_UAT` 并重启 Agent host，不要让用户把 Token 粘贴进聊天。
- 重启后的 host 必须实际发现精确 `create-doc`、`fetch-doc` 两项工具。确认无额外写工具后，只为本次 CLI 进程设置非敏感 `FEISHU_MCP_HOST_TOOLS_ATTESTED=create-doc,fetch-doc`；未发现工具时不得设置。
- Agent host 必须把当前会话的授权证明与 claim 原子绑定，只放行 1 次 `create-doc`，随后读回，并保存可核验的调用证据。
- `authorization_scope_sha256` 只是范围标识，不是授权凭据；不得把它当成用户授权。
- 当前能力显示可信执行器未接入时停止；不得运行 begin，不得用浏览器覆盖、通知 webhook 或自写客户端绕过。

`begin_feishu_create`：

- 这是外部写入的最后本地边界。必须在当前任务获得对精确 tenant、文件夹、正文、图片、`create 1 doc` 和 scope 哈希的明确授权；普通「继续」不构成该授权。
- 执行 status 返回的精确 begin 命令。begin 再次检查稿件门禁、发布配置、正文、图片、intent、payload、资产清单和回执模板。
- begin 成功即写入不可重复的持久 dispatch claim。此后只允许调用 `create-doc` 1 次，再立即 `fetch-doc` 读回。
- 超时、取消、schema 变化、`result.isError`、缺 revision、读回不一致或无法落盘，都按结果未知处理；禁止第二次 create。

`feishu-commit-push`：

- 不保存完整 MCP 响应，只写白名单 `receipt.json` 与规范化 `readback.md`。
- server／tool／call ID／响应 SHA、授权 scope、时间边界、访问检查、受信飞书文档 URL、正文与图片映射必须全部通过。
- 任一未知字段或校验失败都会进入 `result_unknown`。
- commit 成功后，把返回的 `document_url` 作为默认在线排版预览交给用户。说明飞书文档用于在线协作与结构预览，锁定 HTML 才是精确公众号 CSS 凭据。

## 飞书拉回

`execute_feishu_pull` 只读精确公司文档，不覆盖本地稿：

- 可信读取执行器不可用时同样停在执行器 gate。
- 归一化结果不得含 frontmatter；标题必须一致；图片必须映射回 intent 中已有相对路径和 SHA-256。
- 写白名单 receipt／readback 后运行 `feishu-stage-pull`。
- 只有下一动作明确成为 `accept_feishu_pull` 时才接受。
- 接受后降回 `editorial_review`，转入 `$self-media-ops` 重做事实与终校；图片变化时重做权利门禁。

已有文档覆盖更新保持关闭。没有服务端 revision／CAS 时，不得用「先 fetch 再 update」冒充条件写入，也不得采用最后写入者获胜。

## 安全日志

两类忽略文件用途不同：

- `.company-content-sync/journal/`：持久防重复写日志与一次性 claims，是安全真源。
- `<内容包>/dist/content-sync/`：工作快照、operation 文件、HTML 和 build receipt。

不要在 pending／in-flight operation 存在时删除 journal。`dist/` 丢失时 journal 会恢复安全相位；协议状态缺 journal 时 CLI 必须硬失败，跨机器只能先只读核对远端，不得继续 begin／create。

状态含义：

- `push_prepared`：尚未消费 claim；正文、配置或图片变化会使授权失效。
- `push_in_flight`：create 已派发或可能已派发；只读核对，禁止重试。
- `feishu_synced`：等待团队完成信号，不轮询。
- `remote_dirty`：远端候选已暂存，尚未覆盖本地。
- `local_dirty`：当前连接层不能安全回写已有文档。
- `conflict`：保留两边，人工选择或合并。
- `result_unknown`：只读核对精确 operation，禁止新建第二份文档。

`tool_blockers` 表示工具故障；`workflow_blockers` 表示稿件不能继续。`operational_ok` 不能代替 `workflow_ready`。

## 微信外部动作

`manual_editor + default` 不能进入公众号 API。只有用户显式选择 `sealed_draft + appsso-article-v1`、精确账号 × 格式合同资格回执通过，并且微信草稿执行器 capability 为 true，才允许出现 `wechat_create_draft`。

资格测试、正式微信草稿、浏览器覆盖草稿、发布和群发都是独立授权点。继续复用并约束 `微信公众号/tools/wechat_publish.py`，不得维护第二套发布客户端。当前 `wechat_create_draft` capability 为 false 时停止，不伪造成功。

进入微信阶段时先运行纯本地探针：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$repoRoot/tools/workflow.ps1" wechat capability --json
powershell -NoProfile -ExecutionPolicy Bypass -File "$repoRoot/tools/workflow.ps1" wechat sealed-draft-dry-run `
  <内容包> `
  --build <内容包>/dist/content-sync/build.json `
  --json
```

`capability` 与 `sealed-draft-dry-run` 都不得读凭据、联网或写入外部系统。后者必须校验密封 HTML、Profile、精确账号本地往返、封面与图片权利；往返未完成时失败关闭是正确结果。本地资格回执不是 host 签名的生产授权；`trusted_production_qualification`、`authorization_ready`、`sealed_html_execute` 或 `wechat_create_draft` 任一为 false 时，都不得进入真实草稿创建。

密钥、Cookie、登录态、完整请求头、正文 Base64 和完整 MCP 响应不得进入日志、状态、回执或提交。
