# 本仓库的 ARIS 接入

2026-10-19，主理人要求迁移 DGM 当天采用的科研工作流，并让本目录兼作日常写作目录。`project-profile.json` 固定来源版本与本地适配范围；`source-lock.json` 固定实际文件哈希。上游 MIT 许可保留在 `upstream/LICENSE`。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 aris setup --dry-run
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 aris setup
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 aris doctor
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 aris wiki stats research-wiki
```

`tools/bootstrap.ps1` 自动恢复项目内技能链接；所有链接指向当前 clone 的固定源。旧内容技能、原有文档和研究状态继续保留。安装器不改全局 ARIS 指针、全局客户端设置，不调用外部模型。技能发现列表通常在客户端新会话中刷新，当前会话仍可按文件路径读取和执行。

研究先看根 `RESEARCH_BRIEF.md`、`RESEARCH_WORKFLOW.md`、`RESEARCH_HANDOFF.md`；日常内容走原 `self-media-ops`。更新固定源是独立迁移操作，不会因 setup 自动追远端最新版本。

原生模型客户端、登录、额度和网络是本机输入，不复制进 Git。Gemini 通过 `AGY_BIN`、`.aris/runtime.local.json` 的 `agy_bin` 或 PATH 查找 agy；不自动退到旧 Gemini CLI。实际账号写入、发布与大规模实验继续按当前任务授权执行。
