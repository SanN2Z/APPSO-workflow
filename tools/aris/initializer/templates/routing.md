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
