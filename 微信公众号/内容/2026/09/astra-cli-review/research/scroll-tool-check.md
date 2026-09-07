# 长图滑动框工具核查

日期：2026-09-05；对应 FB016。

已找到现有实现 `微信公众号/tools/wechat_publish.py` 的 `vertical_scroll_fragment`、`build_scroll_handoff`，统一入口为 `tools/workflow.ps1 wechat scroll-handoff`。组件支持 1—9 张已登记静态图，固定 300 px 视窗，上下滚动，离线复制 HTML；不访问网络，不写公众号后台。

原有公司 SOP 已链接到 wechat-publishing.md，未另建同名工具。此次只扩大原合同的日常评估触发，未修改实现或新增测试。

现有 5 个 scroll_handoff 回归测试通过：三图自包含与顺序、数量及重复、assets 路径和用途、权利／平台限制、产物篡改。首次沙箱运行因 Windows 临时目录权限失败，获准后原测试通过；没有关闭工具门禁。

```powershell
& '.venv/Scripts/python.exe' -m unittest discover -s '微信公众号/tools/tests' -p 'test_wechat_publish.py' -k scroll_handoff
```

正例：完整网页长截图应在 visual-notes 出现候选与处理原因。反例：唱片店首屏需要对比，保留普通静态图；小妖需要观察动作，保留 GIF。它们不因新偏好被强制转换。

本篇仍 draft，正文以首屏／操作 GIF 为主，完整月屿长截图列为后续滑动候选。当前未创建可复制的滑动交接页，未做公众号后台保存重开测试。此项限制不妨碍本地文章和压缩素材交付。滑动框不减少图片字节，不视为飞书大体积复制的修复。
