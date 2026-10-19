---
name: aris-init
description: 一键建库：启用 ARIS skill、自动路由、research-wiki 和 Claude/Codex/Gemini 共享科研流程。Claude Code 用 /aris-init "研究方向"，Codex 用 $aris-init 研究方向；已有项目可幂等刷新。
---

# ARIS research setup

Use for this repository’s research setup or refresh. This folder also hosts daily self-media work, so follow AGENTS.md routing and preserve existing content rules.

Run the clone-local entrypoint: `powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 aris setup --dry-run`, then run without `--dry-run`. It installs the pinned research skills for Claude and Codex, preserves existing files, initializes the wiki if absent, and refreshes only managed workflow blocks. Use `aris doctor` to check links and sources.

Research roles and the agy routing preference live in RESEARCH_WORKFLOW.md. The active question lives in RESEARCH_BRIEF.md. Do not initialize an unrelated folder, alter global settings or infer publishing authority. Model access and experiment budgets remain explicit local inputs.
