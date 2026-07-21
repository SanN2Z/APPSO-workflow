# 视觉说明

本轮采用「2 张自制笨拙涂鸦 + 3 张 Anthropic 官方素材」的混合方案，共 5 张发布视觉。

## 视觉角色

1. `assets/cover.png`：微信封面，以「AI 撞上现实」和反馈回路呈现全文核心判断。
2. `assets/model-timeline-scribble.png`：正文时间线，压缩 2022—2026 的能力范式变化；节点不是完整模型谱系。
3. `assets/anthropic-claude-code-official.png`：为「模型进入终端」提供官方产品界面证据。
4. `assets/anthropic-fable-mythos-official.png`：标记 2026 年 Fable 5、Mythos 5 的发布节点。
5. `assets/anthropic-mythos-protein-design-official.png`：配合厂商科研能力口径，并在相邻正文与图注中保留内部评估限制。

## 风格与版权边界

- 两张生成图统一调用受控 Prompt `appsso-004`，详细调用记录见 `image-prompts.md`。
- Anthropic 官方图保持原样，不裁切、不标注、不伪装成项目自有素材。
- 官方图用于有出处的科技评论，用户已在本轮明确要求采用；此确认不等于获得商业授权。
- 正文不再追加「相变示意图」或「反馈闭环图」，避免图片过密；封面已经承担反馈闭环的概念表达。

## 2026 年 7 月 22 日风格路由修正

- 本轮用户反馈说明：仅在文字记录中写明 `appsso-004`，不能防止首次调用被通用科技媒体模板覆盖。
- 后续候选图统一以 `research/image-generation-plan.json` 为执行真源。当前生产计划只锁定 `cover` 与 `capability-timeline`；此前已经否决的「相变示意图」和「反馈闭环图」不重新进入制作范围。
- 每个任务先生成不对外展示的结构参考图，再以该输入执行 `appsso-004` 重绘；两个阶段分别预检。风格冲突、Prompt 哈希变化、参考图缺失、改编权未确认或最终模式为 `text_to_image` 时直接停止。
- 该计划与 preflight receipt 只证明调用配置通过，不证明图片已经生成、质检或入稿。只有成品进入 `assets/`、完成原尺寸检查并登记 manifest 后，任务才算完成；回归测试用例不自动升级为真实生产任务。
