# 全能力打包与本机接线

本仓库把内容生产所需的可分发部分统一打包：脚本、Skill、SOP、精确依赖、公司扩展源码、配置模板和本地导入器都随私有 Git clone 到达。账号凭据、浏览器登录态和远端服务在本机接线。2026-09-07 主理人授权的工作流原件已随私有仓库保存，清单为 `tools/workflow-source-assets.json`。

## 一次安装

先安装 Git、Windows PowerShell 5.1、Python 3.11 或更高版本、Node.js 22 或更高版本。仓库当前实测版本见 `.python-version` 与 `.nvmrc`。然后在仓库根目录运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/bootstrap.ps1 -FullTest
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 verify
```

`bootstrap.ps1` 会完成五件事：

1. 创建 clone 内 `.venv`，按 `requirements-workflow.txt` 安装精确 Python 依赖。
2. 对两个锁文件执行 `npm ci`：恢复公众号 Wenyan 渲染器，以及 clone 内 Codex／Claude CLI。
3. 从已跟踪模板创建缺失的本地配置槽；已有文件永不覆盖。
4. 从 clone 内固定源恢复 Claude／Codex 的 ARIS 技能链接，保留原内容技能与项目状态。
5. 运行源码合同、运行时 doctor 和可选全量回归。

`.venv`、`node_modules`、`.env`、`.local-capabilities` 和运行缓存均被 Git 忽略；另一台机器通过锁文件重建，不提交生成物。

## 能力清单

机器可读真源是 `tools/workflow-toolchain.json`，当前登记 9 个完整能力包：

| 能力包 | 随 clone 到达的部分 | 本机执行前输入 |
|---|---|---|
| `content_core` | 内容包校验、开头检查、复盘、洞察、语料、PDF／图片／文本工具、固定版 ARIS 与初始化器 | 内容工具无额外输入；科研外部模型连接另查 |
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

### Gemini 主笔试跑

按[主笔交接模板](<../共享/模板/写作/Gemini主笔交接.md>)准备 `external_shareable`、`prompt` 和 `locked_fragments` 字段。原生 agy 是用户自行安装并登录的外部运行输入，未打包进 clone；通过 `AGY_BIN`、`--agy-bin` 或忽略的 `.aris/runtime.local.json` 中的 `agy_bin` 注入，不使用旧 Gemini CLI 自动替代。目前适配并校验 agy 1.4.2，模型和 effort 必须逐次显式指定。

```powershell
# 只查本机二进制，不假称已验证登录或模型连接
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 gemini-writer doctor --model gemini-4-argon-high --effort high

# 只返回试写，不写 canonical；输出目录必须是尚不存在的 .tmp 子目录
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 gemini-writer draft --model gemini-4-argon-high --effort high --handoff <本次已脱敏交接.json> --output-dir .tmp/agy-writer/run-01
```

运行于无仓库祖先的临时目录，使用 plan 模式并请求原生 sandbox；未启用跳过权限。指令要求纯文本写作，检查实际工具调用是否为零；这些设置不冒称关闭了全部原生工具。原始 stdout、stderr 和 CLI 日志仅存忽略目录。可归档正文和白名单 receipt，不能整包提交诊断日志。模型不符、调用工具、缺失锁定段落、空输出或失败均保留诊断并失败退出，不自动重试或换供应商。

局部修复先冻结原稿 SHA256，以及 `allowed-spans.json` 的 `[{"id":"P01","old":"待修改原文","issue":"问题"}]`。主笔返回 `{"patches":[{"id":"P01","old":"待修改原文","new":"修改后原文"}]}`，再运行本地装配：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 gemini-writer apply-patches --source <首次正文.md> --source-sha256 <审稿冻结的SHA256> --allowed-spans <允许范围.json> --patches <主笔补丁.json> --locked-handoff <原交接.json> --output <新的试写正文.md>
```

此命令不调用模型，不要求安装 agy。它逐项匹配允许范围，检查图片顺序和锁定段落，只创建新文件。输入不含 frontmatter，输出不得是 `draft.md`。装配成功仍需原有审稿与发布检查，不自动更新文章状态。

### ARIS 与日常写作

本仓库同时保存研究与内容工作流。研究入口、版本来源和恢复命令见 [ARIS 接入说明](aris/README.md)；日常改稿继续按 `self-media-ops`，不自动加载研究全文。`aris setup` 不启动文献研究或模型调用，`aris doctor` 检查固定源与本地链接。

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
