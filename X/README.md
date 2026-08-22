# X 运营子项目

这里保存 X/Twitter 的内容、运营 SOP、API 工具和发布记录。

- `content/`：历史稿件与队列，保留原有英文目录以兼容脚本。
- `docs/`：运营、热点捕捉、变现与 API 文档。
- `scripts/`：检查、趋势扫描和发布工具；默认 dry-run。
- `选题/`：后续新建的结构化选题。
- `发布记录/`：真实发布与复盘记录。

本地凭据放 `X/.env`，不得提交。示例文件只能包含占位符。

首次 clone 在仓库根目录运行 `tools/bootstrap.ps1 -FullTest`；它会从 `X/.env.example` 创建缺失的本地配置槽。X 脚本只依赖 clone 内 Python 标准库，统一入口如下：

```powershell
# 检查字段是否齐全，不输出凭据
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 x-env

# 查看命令参数；不会发布
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 x-readonly --help
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 x-trend-scan --help
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 x-post --help
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 x-publish-queue --help
```

联网读取、趋势扫描和可见性检查需要有效 X 凭据；发布脚本默认 dry-run，真实发布仍需要本次账号与正文的明确授权。
