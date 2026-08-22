# Project notice

- Upstream: <https://github.com/LifelongLazyLearner/qu-ai-wei>
- Packaged version: `0.8.2`
- License: MIT（见同目录 `LICENSE`）
- Packaged into this private repository on: `2026-08-22`
- Upstream commit: 未从当前本地副本中保留，不能据此声明精确 commit provenance。
- Local compatibility patch: Git Bash 中通过管道调用随 Codex 分发的 Windows `rg.exe` 会错误返回未命中；仅把 3 个测试脚本的标准输入断言改为等价的 `grep -E／-F`，不改 Skill 规则或产出。

该目录为 Claude Code 项目级写作参考，不是本仓库内容流程的规则真源。冲突时依次服从仓库根 `AGENTS.md`、`共享/运营/SOP/内容工作流.md` 和 `.agents/skills/self-media-ops/`；不得用第三方「去 AI 味」规则覆盖事实、权利、保密或发布授权门禁，也不得把作者身份判断或 AI 检测分数当作交付结论。
