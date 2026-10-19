# 自媒体运营知识库

这是兼顾日常写作与 ARIS 研究的私有工作区。它保存内容真源、可复用方法、公司数字资产、研究文档和必要工具，不要求每次写稿都加载全部资料。

日常选题、改稿、配图和排版走原内容工作流。科研任务按需进入 ARIS；当前研究方向已记录，尚未启动。文档分工与跨会话交接见 [RESEARCH_HANDOFF.md](RESEARCH_HANDOFF.md)。

> 仓库含 `internal` 与受限索引，只能保持 Private。公开前必须逐项脱敏和核权。

## 全新 clone 的唯一初始化入口

先安装 Git、Windows PowerShell 5.1、Python 3.11 或更高版本、Node.js 22 或更高版本；仓库当前验证版本分别记录在 `.python-version` 与 `.nvmrc`。随后从私有远端 clone，并在仓库根目录运行：

```powershell
git clone PRIVATE_REPOSITORY_URL self-media-ops
Set-Location self-media-ops
powershell -NoProfile -ExecutionPolicy Bypass -File tools/bootstrap.ps1 -FullTest
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 verify
```

`bootstrap.ps1` 会创建被 Git 忽略的 `.venv`，按统一清单安装精确 Python 依赖，以 `npm ci` 恢复锁定的 Wenyan、Codex 和 Claude Code，从模板创建缺失的本地配置槽，并恢复项目内固定版 ARIS 技能链接。它随后验证公司扩展文件树、脚本语法、9 个能力包和核心 doctor；已有配置永不覆盖，模板也不含真实凭据。

可分发的适配器、依赖、Skill、SOP、公司扩展源码和配置模板全部随 clone 到达。账号值、浏览器登录态、远端 `image_gen` 能力通过固定入口在本机接线，不进 Git。2026-09-07 获授权的 APPSO Prompt、设计规范和 Logo 已随私有仓库保存，并校验原文哈希。完整清单与迁移方法见 [`tools/README-capabilities.md`](tools/README-capabilities.md)。

初始化后不必激活虚拟环境，统一用 clone 内入口：

```powershell
# 仅读自检
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 verify

# 分别查看打包完整性与当前机器的运行时输入
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 capabilities doctor --bundle-only
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 capabilities doctor

# 校验一个内容包
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 validate <内容包路径>

# 查看公众号或公司同步能力，不联网、不写外部系统
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 wechat capability --json
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 company doctor --json
```

依赖、入口、能力包与本机运行输入的机器可读真源是 [`tools/workflow-toolchain.json`](tools/workflow-toolchain.json)；详细可移植合同只在核心工作流的 `CORE-PORTABILITY-001` 维护。

日常写作、生图和排版可直接查[工作流使用入口](共享/运营/SOP/工作流使用入口.md)。桌面材料的归位与原文入口也在其中。

## 三步开始

1. 读根 [`AGENTS.md`](AGENTS.md)，确定安全规则和任务类型。
2. 内容任务使用 [`self-media-ops`](.agents/skills/self-media-ops/SKILL.md) 选择最短流程；科研任务按根指令进入 ARIS。
3. 只进入目标平台、目标内容包和被当前任务触发的专项模块。

新任务、跨稿切换或仓库整理时再读 [`上下文/当前重点.md`](上下文/当前重点.md)。普通改字不需要读取全局状态。

## 架构

| 层 | 唯一职责 |
|---|---|
| `AGENTS.md` | 安全硬门与任务路由 |
| `RESEARCH_BRIEF.md`、`RESEARCH_WORKFLOW.md`、`RESEARCH_HANDOFF.md` | 当前研究方向、共享科研流程、交接；分别维护 |
| `research-wiki/` | 研究记忆，按实际阅读和实验逐步增加 |
| `共享/运营/SOP/内容工作流.md` | 跨平台核心流程唯一真源 |
| `.agents/skills/` | 按任务调用流程，不复制完整 SOP |
| `微信公众号/`、`X/` | 平台写法、工具和独立内容包 |
| `APPSO-数字资产/` | 公司专属方法、资产、保密规则和专项 adapter |
| `共享/` | 跨平台模板、研究、素材和运营索引 |
| `tools/` | 校验、排版和已授权的私有公司工具 |
| `output/`、`临时素材/` | 可重建或待归档文件，Git 忽略 |

## 内容真源

- 单篇稿件的正文和状态以目标内容包的 `draft.md` 为准。
- 来源、图片、审校、交付与反馈文件按任务阶段逐步增加，不在一个想法出现时就创建整套工程。
- `dist/`、预览、草稿箱和导出 HTML 都是派生产物。
- APPSO 方法只在数字资产库维护；公众号知识库中的兼容入口只链接，不复制正文。
- 原始反馈留在内容包；跨稿模式进入复盘台账；SOP 只保存通过晋升门的规则。

内容包的渐进结构见 [`content-package.md`](.agents/skills/self-media-ops/references/content-package.md)，核心流程见 [`内容工作流.md`](共享/运营/SOP/内容工作流.md)。

## 专项入口

- APPSO：[`APPSO-数字资产/README.md`](APPSO-数字资产/README.md)
- 公众号：[`微信公众号/README.md`](微信公众号/README.md)
- X：[`X/README.md`](X/README.md)
- SOP 地图：[`共享/运营/SOP/README.md`](共享/运营/SOP/README.md)
- 复盘：[`content-retrospective`](.agents/skills/content-retrospective/SKILL.md)
- 洞察实验：[`共享/研究/洞察实验室/README.md`](共享/研究/洞察实验室/README.md)
- Git：[`Git 提交与仓库整理 SOP`](共享/运营/SOP/Git%20提交与仓库整理%20SOP.md)

本项目内容与公司资产未经权利人明确授权，不得复制、公开或重新许可。`tools/aris/upstream/` 保留其上游 MIT 许可；第三方许可不改变其他目录的保密与权利要求。
