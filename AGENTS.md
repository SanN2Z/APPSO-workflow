# 自媒体运营项目指令

## 默认走最短路径

- 本仓库同时用于日常自媒体写作与 ARIS 研究。当前研究是可适配不同文风、利用反馈改进流程的自动内容生产系统；不要读取无关科研项目。
- `X/` 与 `微信公众号/` 可以共享已核事实，成稿必须分别写。
- 开始任务先运行 `git status --short`，只读取目标平台、目标内容包和本次任务真正需要的规则。
- `上下文/当前重点.md` 只在新任务、跨内容包切换或仓库整理时读取；同一稿件的小改不重复加载。
- 日常内容使用 `.agents/skills/self-media-ops/SKILL.md` 分流，详细流程以 `共享/运营/SOP/内容工作流.md` 为真源。科研任务按本文件 ARIS 分流段进入 `RESEARCH_WORKFLOW.md`，不把普通改稿启动成论文研究。

## 按触发条件加载

| 触发条件 | 追加读取 |
|---|---|
| APPSO、Hunt Good、公司稿或公司资产 | `APPSO-数字资产/README.md`、保密分级及对应专项 SOP |
| L3 多路线稿、中心结构性重写或用户明确共创 | `wechat-judgment-workshop.md`；只有并行研究或独立定向审稿才加载 `wechat-team.md`，不得并行改 canonical prose |
| 用户明确要求文风实验且已有实质正文 | `wechat-clumsy-writing.yml` |
| 生图或图片编辑 | `共享/运营/SOP/Image2 生图工作流.md` |
| 预览、排版、草稿交接 | `wechat-publishing.md` 或公司浏览器排版 SOP |
| 收到实质修改意见、交付或发布 | `.agents/skills/content-retrospective/SKILL.md` |
| 用户要求今后沿用某项反馈、出现重复返工或流程缺口，或准备把案例固化进规则、Skill、模板或工具 | `.agents/skills/feedback-to-system/SKILL.md` |
| 把长期判断做成实验 | `.agents/skills/insight-to-asset/SKILL.md` |
| 整理或提交 Git | `共享/运营/SOP/Git 提交与仓库整理 SOP.md` |

错字、单句润色、补链接等不改变判断、事实、素材和发布状态的小改，不启动完整复盘或多角色评审。

## 不可省略的硬门

- 数字、日期、价格、人物身份、产品名、政策、榜单和「最新」信息必须核查；优先一手来源。
- 事实、厂商自报、第三方结果、作者判断、推断和玩梗必须分开；引语核对原文与说话人。
- 每张发布图片都要在进入 `ready` 前登记来源、权利人、修改、允许平台和权利状态。AI 图必须标记，不能伪装成新闻现场或官方截图。
- APPSO 的 `internal` / `restricted` 资料不得自动进入个人稿或公开环境。公司稿与个人稿只共享已核事实。
- 密钥只放本地 `.env`；不得在日志、稿件或提交中输出凭据、Cookie、登录态或完整请求头。
- 发布、群发、评论、私信、关注、排期以及浏览器覆盖草稿，需要用户在当前任务中明确授权；授权必须对应本次账号、正文、图片和动作，不复用旧授权。
- 不覆盖或混入用户尚未提交的无关修改；远端必须保持 Private。

## 内容状态

`idea → research → draft → fact_checked → editorial_review → ready → published → archived`

- 状态以 `draft.md` frontmatter 为真源，不靠目录名表达。
- Codex 最多自动推进到 `ready`。
- `ready` 必须通过事实、权利、终校、平台适配和敏感信息检查。
- 只有用户明确确认已发布，才能写成 `published` 并记录真实链接和日期。

## 中文交付规则

- 面向用户或读者的中文使用「」；嵌套引用使用『』。
- 中文与英文、中文与阿拉伯数字之间加 1 个半角空格，例如：`OpenAI 发布 GPT-5.6`、`7 月 20 日`。
- 中文标点与英文或数字之间不额外加空格；代码、命令、URL、路径和必须逐字保留的原文不机械替换。

## Git

- 一个可验证工作单元完成后再提交；不要把无关内容混进同一提交。
- 提交前运行 `powershell -ExecutionPolicy Bypass -File tools/repository_preflight.ps1`。
- 使用 `type(scope): 摘要`，例如 `docs(sop): 精简内容生产入口`。
- 不提交生成物、临时素材、依赖、凭据、浏览器 Profile、登录态或受限原件；禁止使用 `git add -f` 绕过忽略规则。
- 默认只向已确认的私有 `origin` 推送通过检查的提交。

## Pipeline Status

```yaml
stage: idle # idle | idea-discovery | implementation | training | review | paper
idea: "面向不同文风的自适应内容生产工作流，研究反馈驱动的流程改进"
contract: ""         # research_contract.md 路径
current_branch: ""   # 这个 idea 的 git 分支
baseline: ""         # 对比用的 baseline 数字
training_status: idle  # idle | running | complete | failed
language: zh         # en | zh — ARIS skill 的输出语言
active_tasks: []
next: "研究方向已记录；按主理人要求暂不推进，等明确启动后再从 RESEARCH_BRIEF.md 与 RESEARCH_HANDOFF.md 接续"
last_updated: "2026-10-19"
```

<!-- ARIS-INIT:BEGIN -->
## ARIS 工作方式（本项目专用，由 aris-init 维护，重跑会刷新本段）

本仓库同时用于 ARIS 研究和日常自媒体写作。本段只管理科研任务：普通选题、改稿、配图、排版和交接继续走 `self-media-ops`，不因出现「AI」「实验」「写作」就启动论文流水线。研究与内容包分别保存状态。

- 我用自然语言说需求。你结合下表和上面的 Pipeline Status 判断当前阶段，自动选用对应的 ARIS skill，不需要我点名。开工前用一句话说明「用 X，因为 Y」。
- 能串起来的步骤按工作流自动衔接；每完成一个阶段，更新 Pipeline Status。
- 拿不准选哪个时，先读 `tools/aris/upstream/AGENT_GUIDE.md`（本 clone 固定的官方路由索引）或对应 skill 的 SKILL.md，再决定。
- **共享分工**：科研任务先读 `RESEARCH_WORKFLOW.md`。Fable 可主导全流程，Astra 参与关键决策和独立质疑，Gemini 经 agy 参与发散和写作（不默认走旧 Gemini CLI），Sol 默认执行；具体接入、额度和项目约束优先。

| 我的需求 / 项目状态 | 入口 skill |
|---|---|
| 新课题，只有方向或 RESEARCH_BRIEF.md | `idea-discovery`（W1：文献 → idea → 新颖性 → 评审） |
| 想从方向一路做到论文 | `research-pipeline`（W1 → W1.5 → W2 → W3） |
| 想法已定，缺可执行的实验计划 | `research-refine-pipeline` / `experiment-plan` |
| 有 EXPERIMENT_PLAN.md，要实现、部署、跑实验 | `experiment-bridge`（W1.5）；细分用 `run-experiment`、`experiment-queue`、`monitor-experiment`、`training-check` |
| 实验结果出来了 | `analyze-results` → `result-to-claim` → `experiment-audit` |
| 要审稿式迭代改进 | `auto-review-loop`（W2） |
| 准备写论文（已有 NARRATIVE_REPORT.md） | `paper-writing`（W3） |
| 论文打磨、投稿前核查 | `auto-paper-improvement-loop`、`paper-claim-audit`、`citation-audit` |
| 收到审稿意见 / 转投 / 做报告 | `rebuttal`（W4）/ `resubmit-pipeline`（W5）/ `paper-talk`（W6） |
| 查文献、加论文、问领域现状 | `research-lit`、`research-wiki`（ingest / query） |
| 推公式、证明、画图等子任务 | 对应的专用 skill，如 `formula-derivation`、`proof-checker`、`figure-spec`、`paper-figure` |

- **知识库**：`research-wiki/` 是本项目的记忆入口。读过的论文、idea（包括失败的）、实验和 claim，都按 ARIS 的 wiki hook 写进去。
- **授权**：沿用当前任务已有授权，不为同一已授权动作重复询问。新增付费规模、远端部署、公司材料外发和实际发布继续遵守原有边界。没有继承 DGM 的 GPU、Baton、数据集或科研结果。
- **跨会话**：研究状态和下一步同时写入 `RESEARCH_HANDOFF.md`；已确认结论必须有证据，不把普通文章 ready 状态算成科研结果。
- **环境**：Windows；辅助脚本使用 clone 内 `.venv`，入口是 `tools/workflow.ps1 aris`，固定源在 `tools/aris/`。不修改 junction 指向的技能来做单稿改字。
<!-- ARIS-INIT:END -->

<!-- ARIS-WORKFLOW-ENTRY:BEGIN -->
## Shared research workflow

Before research work, read [RESEARCH_WORKFLOW.md](RESEARCH_WORKFLOW.md). It defines the user-adopted Fable/Astra/Gemini/Sol division of labor, evidence checks and cross-client handoff. Preserve project-specific scientific, coding, resource and state-ownership rules.
<!-- ARIS-WORKFLOW-ENTRY:END -->
