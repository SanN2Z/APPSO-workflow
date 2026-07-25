# 自媒体运营知识库

这是公司内容工作的私有仓库。它保存内容真源、可复用方法、公司数字资产和必要工具，不要求每次写稿都加载全部资料。

> 仓库含 `internal` 与受限索引，只能保持 Private。公开前必须逐项脱敏和核权。

## 三步开始

1. 读根 [`AGENTS.md`](AGENTS.md)，确定安全规则和任务类型。
2. 使用 [`self-media-ops`](.agents/skills/self-media-ops/SKILL.md) 选择最短流程。
3. 只进入目标平台、目标内容包和被当前任务触发的专项模块。

新任务、跨稿切换或仓库整理时再读 [`上下文/当前重点.md`](上下文/当前重点.md)。普通改字不需要读取全局状态。

## 架构

| 层 | 唯一职责 |
|---|---|
| `AGENTS.md` | 安全硬门与任务路由 |
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

本仓库不包含开源许可；未经权利人明确授权，不得复制、公开或重新许可其中内容。
