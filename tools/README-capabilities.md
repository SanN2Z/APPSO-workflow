# 全能力打包与本机接线

本仓库把内容生产所需的可分发部分统一打包：脚本、Skill、SOP、精确依赖、公司扩展源码、配置模板和本地导入器都随私有 Git clone 到达。账号凭据、浏览器登录态和远端服务在本机接线。2026-09-07 主理人授权的工作流原件已随私有仓库保存，清单为 `tools/workflow-source-assets.json`。

## 一次安装

先安装 Git、Windows PowerShell 5.1、Python 3.11 或更高版本、Node.js 22 或更高版本。仓库当前实测版本见 `.python-version` 与 `.nvmrc`。然后在仓库根目录运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/bootstrap.ps1 -FullTest
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 verify
```

`bootstrap.ps1` 会完成四件事：

1. 创建 clone 内 `.venv`，按 `requirements-workflow.txt` 安装精确 Python 依赖。
2. 对两个锁文件执行 `npm ci`：恢复公众号 Wenyan 渲染器，以及 clone 内 Codex／Claude CLI。
3. 从已跟踪模板创建缺失的本地配置槽；已有文件永不覆盖。
4. 运行源码合同、运行时 doctor 和可选全量回归。

`.venv`、`node_modules`、`.env`、`.local-capabilities` 和运行缓存均被 Git 忽略；另一台机器通过锁文件重建，不提交生成物。

## 能力清单

机器可读真源是 `tools/workflow-toolchain.json`，当前登记 9 个完整能力包：

| 能力包 | 随 clone 到达的部分 | 本机执行前输入 |
|---|---|---|
| `content_core` | 内容包校验、开头检查、复盘、洞察、语料、PDF／图片／文本工具 | 无 |
| `wechat` | 预览、交接、纵向滑动页、密封草稿与微信适配器 | 执行草稿时填写微信凭据并联网 |
| `x` | 环境检查、只读检查、可见性、趋势扫描、队列和发布脚本 | X 凭据、网络；发布仍需本次授权 |
| `company_feishu` | 公司同步状态机、锁定排版、飞书配置模板、clone 内 Codex | 飞书 UAT、Codex 登录、网络与精确写入授权 |
| `company_browser` | 已登记的 v1.10.0 基线、v1.10.1—1.10.3 修复候选及本地回归脚本 | Chrome／Edge、公司专用 Profile、明确选择版本与本次覆盖授权 |
| `image_generation` | Image2 SOP、风格档案、生成前检查与回执合同 | Agent host 提供 `image_gen` |
| `appsso_visual_profiles` | 风格档案、完整设计规范、Logo、原始 Prompt 与哈希检查 | 无需额外导入；实际生图需 host 工具 |
| `openrouter_ox` | OpenRouter 客户端、密钥录入器、clone 内 Claude | OpenRouter key、可用模型 ID 与网络 |
| `writing_skill_assets` | 自媒体 Skills 与 `qu-ai-wei` 完整版本化资产 | 无 |

「能力已打包」表示另一台机器不需要回到桌面找脚本、猜依赖或依赖全局 Codex／Claude；「运行时已就绪」还要求对应账号和主机条件存在。二者可分别检查：

```powershell
# 只检查 9 个能力包是否完整，不要求本机已有账号或登录态
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 capabilities doctor --bundle-only

# 检查当前机器的配置、受限资产、浏览器和 host 条件
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 capabilities doctor

# 查看机器可读报告
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 capabilities doctor --json
```

## 本机配置

初始化会在文件不存在时创建以下槽位：

| 本地文件 | 模板 | 用途 |
|---|---|---|
| `.env` | `.env.example` | `OPENROUTER_API_KEY`、`FEISHU_MCP_UAT` |
| `微信公众号/.env` | `微信公众号/.env.example` | 微信开发者凭据 |
| `X/.env` | `X/.env.example` | X API 凭据 |
| `.local-capabilities/codex-company/config.toml` | `tools/capability-templates/codex-company.config.toml` | 公司 Codex 的飞书最小 allowlist |

模板只有占位符。填写真实值后不需要改 manifest，也不要把值粘贴到聊天、命令行或提交中。可重复运行以下命令补齐缺失槽位，它不会覆盖已有配置：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 capabilities prepare
```

## 公司 Codex 与 Ox Alpha

公司 Codex 默认使用仓库内独立 `CODEX_HOME` 和锁定的 `@openai/codex`，不会依赖 `%APPDATA%` 中的全局安装：

```powershell
# 普通公司配置
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 codex-company

# 从当前进程、本地 .env 或剪贴板导入完整 UAT 后启动
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 codex-company-feishu
```

Ox Alpha 启动器同样调用 clone 内锁定的 Claude Code：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 set-openrouter-key
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 claude-ox -Isolated
```

外部模型会收到提示词和附件，只能使用允许送往外部提供方的公开材料。

## 公司浏览器扩展

打印当前 clone 中可加载的绝对目录：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 capabilities extension-path
```

在 `chrome://extensions` 或 `edge://extensions` 打开开发者模式，选择「加载已解压的扩展程序」，指向输出目录。浏览器 Profile 和登录态不复制；扩展写入微信公众号草稿仍是单独授权动作。

## APPSO 受限视觉 Prompt

当前私有 clone 已包含登记的原文、完整设计规范与 Logo，正常安装不需要导入。以下命令只供恢复旧版缺失文件时使用：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 capabilities import-private-assets --source-root <受控原件目录>
```

工具递归定位登记文件，提取登记标题下的 Prompt，逐字核对哈希后才复制到登记目标目录。来源不唯一、内容漂移或目标已有不同版本时硬失败，不覆盖。

## 常用入口

```powershell
# 内容包
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 validate <内容包>

# 公众号／公司能力只读诊断
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 wechat capability --json
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 company doctor --json

# X 工具说明；不执行发布
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 x-post --help
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 x-trend-scan --help

# 全量测试与仓库提交前检查
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 test
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 repo-preflight
```

任何带外部写入的命令仍遵循目标平台 SOP：安装完成不等于授权完成，dry-run 也不自动升级为执行。
