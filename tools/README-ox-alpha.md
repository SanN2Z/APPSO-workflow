# Ox Alpha 本地试验工具

这 3 个脚本只用于公开材料上的模型试验，不属于公众号发布链路：

- `set_openrouter_key.ps1`：交互式把 `OPENROUTER_API_KEY` 写入仓库根目录的本地 `.env`；输入不回显，`.env` 已被 Git 忽略。
- `claude-ox.ps1`：在仓库外的独立目录启动 Claude Code，并把当前进程临时指向 OpenRouter 的 Anthropic 兼容端点；建议使用 `-Isolated`。
- `openrouter_chat.py`：以 OpenRouter Chat Completions 接口做单轮测试。仓库内文件默认拒绝读取；只有确认材料可公开时才可显式增加 `--allow-repository-file`。

硬边界：

- 提示词和附件会发送给外部模型提供方。APPSO `internal`／`restricted` 原件、未公开选题、客户材料、凭据、Cookie 和登录态不得输入。
- 不在命令行参数、日志、稿件或 Git 中写 key；只使用本地 `.env` 或当前进程环境变量。
- `stealth/ox-alpha` 是试验时的默认模型 ID，不视为长期可用承诺；运行前用脚本自检，失效时显式传入新的模型 ID。
- 这些脚本不会发布、群发或覆盖公众号草稿。网络调用产生的费用和数据处理边界以当前 OpenRouter／模型提供方条款为准。

最短用法：

```powershell
.\tools\set_openrouter_key.ps1
.\tools\claude-ox.ps1 -Isolated
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 openrouter "只包含公开信息的测试问题"
```
