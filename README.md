# 自媒体运营知识库

这是一个面向公司内容工作的私有仓库，用于沉淀选题、调研、写作、视觉素材、发布准备、反馈复盘、SOP 和跨平台知识。

> 仓库包含 `internal` 资料与受限资产索引，只能创建为 **Private repository**。未经逐项脱敏和授权审查，不得改为公开仓库。

## 从这里开始

1. 阅读根目录 [`AGENTS.md`](AGENTS.md)，确认项目边界和通用规则。
2. 阅读 [`上下文/当前重点.md`](上下文/当前重点.md)，了解正在推进的稿件与下一步。
3. 处理 APPSO、Hunt Good 或实习反馈时，从 [`APPSO-数字资产/README.md`](APPSO-数字资产/README.md) 进入，并先核对保密分级。
4. 写稿前进入目标平台，继续阅读对应的 `AGENTS.md` 与 `CONTEXT.md`。
5. 使用项目 skill：[`self-media-ops`](.agents/skills/self-media-ops/SKILL.md)。
6. 稿件交付、发布或收到修改反馈后，使用 [`content-retrospective`](.agents/skills/content-retrospective/SKILL.md) 完成复盘和 SOP 升级判断。

## 仓库结构

| 目录 | 真源职责 | Git 边界 |
|---|---|---|
| `.agents/skills/self-media-ops/` | Codex 内容工作流、质量门和验证脚本 | 提交 |
| `.agents/skills/content-retrospective/` | 发布反馈复盘、SOP 进化和工作流迁移 | 提交 |
| `上下文/` | 长期定位、作者声音、事实规范、版权规则与当前重点 | 提交 |
| `APPSO-数字资产/` | 公司方法、栏目规则、SOP、模板和资产台账 | 脱敏内容提交；原件和受限资料忽略 |
| `共享/` | 跨平台模板、公共事实包、权利明确素材与运营台账 | 按权利状态提交 |
| `微信公众号/` | 公众号知识库、选题和独立内容包 | 内容真源提交；凭据、依赖和预览忽略 |
| `X/` | X 平台内容、SOP、脚本和发布记录 | 内容真源提交；凭据忽略 |
| `tools/` | 本地辅助工具 | 通用、无凭据的工具提交 |
| `output/` | 可重建预览、截图和检查输出 | 本地保留，Git 忽略 |
| `临时素材/` | 尚未归档或确认权利的临时文件 | 本地保留，Git 忽略 |

## 真源关系

- 单篇稿件的 brief、事实、正文、素材和发布记录，以对应平台的内容包为唯一真源。
- 跨平台只共享已核事实和通用方法，公众号与 X 必须分别成稿。
- APPSO 数字资产库只保存跨稿有效的方法；单稿成稿、逐条反馈和版本链保留在原内容包或反馈库。
- `draft.md` 是公众号正文真源；`dist/`、手机预览和草稿箱内容都是派生产物。
- 内容状态写入稿件 frontmatter 和 `publish-record.md`，不靠移动目录表达。

## 内容包

正式选题使用稳定目录：

```text
平台/内容/YYYY/MM/slug/
├─ brief.md
├─ draft.md
├─ sources.md
├─ review.md
├─ copyedit.md
├─ asset-manifest.yml
├─ assets/
└─ publish-record.md
```

统一状态为：

```text
idea → research → draft → fact_checked → editorial_review → ready → published → archived
```

Codex 最多自动推进到 `ready`。只有用户明确确认已经发布，才能记录 `published`、真实链接和发布日期。

## SOP 与知识沉淀

- 新事实先进入内容包的 `sources.md`，不要直接写进长期知识库。
- 单稿反馈先保留在案例、反馈库或内容包；确认跨稿有效后再升级为 SOP。
- 公开样本分析标记为 `public-derived`，不得写成 APPSO 官方规则。
- 公司终稿、完整反馈、后台数据和原始品牌文件只建索引或留在 Git 忽略区。
- 修改 SOP 时同步更新版本、日期、资产台账或变更记录。

详细规则见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。

SOP 总入口见 [`共享/运营/SOP/README.md`](共享/运营/SOP/README.md)。Git 提交节奏和命名规范见 [`Git 提交与仓库整理 SOP`](共享/运营/SOP/Git%20提交与仓库整理%20SOP.md)。提交前运行：

```powershell
powershell -ExecutionPolicy Bypass -File tools/repository_preflight.ps1
```

## 首次建仓建议

1. 在 GitHub 或公司 Git 服务创建空的 **Private repository**，不要初始化 README、License 或 `.gitignore`。
2. 首次提交前运行 `git status --short --ignored`，确认 `.env`、`output/`、`临时素材/`、原始品牌文件和 `90-受限资料/` 未进入候选文件。
3. 检查 `.env.example` 只有变量名和占位符。
4. 提交后在远端再次检查仓库可见性为 Private，再邀请公司成员。

本仓库不包含开源许可；未经权利人明确授权，不得复制、公开或重新许可其中内容。
