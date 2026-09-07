# 飞书连接与本次交付

本次用户已要求尝试直接传到飞书，并把归档位置选择交给助手。默认按「自媒体运营」项目归档，每篇单独新建文档；不覆盖用户正在编辑的旧文档。远端文件夹 ID 尚未通过工具读取，不猜造 ID。

## 已查明的连接状态

2026-09-05，只读诊断结果：

- 当前公司配置已有官方 Remote MCP，URL 为 https://mcp.feishu.cn/mcp。
- 配置通过本地检查，工具限制为 create-doc、fetch-doc。
- 当前 Agent 会话没有加载这两个工具；当前进程没有 FEISHU_MCP_UAT。
- 根 .env 已有相应字段，但该本地凭据的 JWT exp 已过期。这里仅本地读取过期字段，未验证签名，也未把凭据发送到网络。
- 本地未配置本次检查的飞书刷新凭据字段，不能据此自动刷新登录。
- 没有执行 create、begin、upload 或其他飞书外部写入，尚无远端文档链接。

## 恢复连接的最短路径

1. 在本机重新取得飞书用户授权，将有效 UAT 更新到仓库根 .env 的 FEISHU_MCP_UAT 字段。凭据留在本机，不发到聊天。
2. 从仓库根目录启动已存在的公司入口：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\codex-company.ps1 -WithFeishu
```

这个入口读取本机 .env 并启动 clone 内 Codex。这里不用带 ImportUatFromClipboard 的入口，避免把正在复制的正文误当登录材料。

3. 新会话按 company-content-sync 检查实际 MCP 工具、目标账号与目录。本轮归档选择已经委托给助手，不重复问目录偏好；需要的是工具返回的真实目录信息。
4. 当前稿件及轻量素材均已准备。工具实际连入后，按真实 create-doc schema 检查本地 GIF 能否作为图片上传；不能仅凭工具名宣称支持本地文件。创建与读回必须确认正文和图片均在文档里。

官方入口：[飞书 Remote MCP 文档](https://open.feishu.cn/document/mcp_open_tools/developers-call-remote-mcp-server?lang=zh-CN)。网页正文依赖客户端渲染，本轮 web 抽取为空；实际配置与本地状态以仓库诊断为据。

## 当前可直接用的本地材料

- `dist/feishu-upload/正文-先复制这份.txt`：不含图片 Base64 的文字，按配图位置编号。
- `dist/feishu-upload/`：按正文顺序编号的原图与轻量 GIF。
- `dist/feishu-upload.zip`：仅便于一次取走文件，解压后逐张上传，不声称可由飞书自动导入 ZIP。
- `dist/wechat-preview.html`：更新后的本地视觉预览。即使 GIF 压小，整页复制仍会包含静态图片数据；上传文件与整页复制是不同路径。

MCP 连接未完成时遵循 company-content-sync 的明确边界：

> 当前能力显示可信执行器未接入时停止；不得运行 begin，不得用浏览器覆盖、通知 webhook 或自写客户端绕过。

此处的上传未完成首先是实际工具和过期登录凭据所限，不是等待额外的目录偏好确认。
