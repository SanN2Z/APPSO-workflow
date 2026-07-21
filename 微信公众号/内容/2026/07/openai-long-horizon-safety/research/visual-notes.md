# 视觉方案

用户人工定稿共有 9 个图片位置。本地正文已同步 4 张原始证据图和 3 张 X 原帖截图；Tibo 长截图已登记并移入 `research/source-assets/`，只作备选核对。人工定稿另有 2 张图片尚未收到原文件，正文以 HTML 注释记录位置，不用占位图冒充。没有使用 AI 生成图。

## 375 px 手机预览回归

- 2026 年 7 月 21 日曾使用固定版 Wenyan CLI 2.0.11 检查 6 图交付版；用户人工定稿调整正文并恢复 1 张官方长截图后，旧预览结论已失效，待 7 图版本重新渲染。
- 旧版 6 张正文图均能加载，正文、小标题和图注没有横向溢出；开头的 Matt 图已换为 1140 × 900 紧凑嵌入版，不含登录横幅。
- 21:40 后已重建 7 图本地版本 `dist/wechat-preview.html`，并生成 `dist/phone-preview-final-375.png`；首屏标题、正文和 Matt 图无横向溢出。validator 为 0 error / 7 warning，warning 均是图片尚未允许 `wechat`。
- 上述检查只能证明本地 7 图重建版；人工定稿准确的 9 图版本仍缺 2 张原图，不能据此关闭资产完整性阻断。
- 英文原帖和图表只承担证据 / 换气任务，关键事实、数字和限制均在邻近中文正文或图注中重复说明，读者不放大图片也能理解主线。
- 本次预览只关闭 `VISUAL-001` 的可读性问题，不解除 `needs_review` 权利阻断，也不替代尚待重跑的 copyedit。

## VISUAL-00：Matt Shumer 的删文件报告

- 状态：已使用，`assets/x-matt-shumer-file-deletion.png`。
- 实际位置：开头首次提到 Matt Shumer 报告 Mac 文件被删之后。
- 编辑任务：用当事人原帖直接证明「开头那起删文件报告是什么」，不展开二手媒体截图。
- 截图范围：由 X 官方嵌入页直接生成，保留公开账号、原文、帖内 Codex 事故说明、日期和互动数；不含侧栏趋势、无关账号和页面登录 CTA。
- 替代文本：`Matt Shumer 公开报告 GPT-5.6 Sol 删除其 Mac 文件`。
- 图注：`Matt Shumer 对 GPT-5.6 Sol 删除 Mac 文件的公开报告。图源：X；该截图记录当事人说法，不等于独立技术取证。`
- 权利：`needs_review`；按有出处的评论报道证据处理，发布前人工确认。

## VISUAL-00A：Tibo 的初步调查回应

- 状态：未使用，仅作备选核对，`research/source-assets/x-tibo-file-delete-response.png`。
- 建议位置：「OpenAI 产品负责人 Tibo 回应」段落之后。
- 编辑任务：证明 OpenAI 确实调查过少量报告，并展示「完整访问、无沙箱、改写 `$HOME`」和后续防护这几层信息。
- 手机端取舍：原帖文字较长。若与 Matt 原帖、Peter 额度梗图同时使用，开头会连续出现 3 张 X 截图；优先保留 Matt 证据图和 Peter 梗图，Tibo 截图只作备选，避免「图注—截图—图注」过密。
- 建议替代文本：`OpenAI 产品负责人 Tibo 在 X 说，公司调查的少量报告常见于开启完整访问、缺少沙箱与自动审查，且模型尝试改写 HOME 环境变量的情况。`
- 建议图注：`OpenAI 产品负责人 Tibo 对文件删除报告的初步调查口径。该回应不能证明所有外部事故有同一根因。图源：X。`
- 权利：`needs_review`；按有出处的评论报道证据处理，发布前人工确认。

## 开头配图取舍

1. 必选：Matt Shumer 原帖，快速兑现「GPT-5.6 删文件」的开头冲突。
2. 换气：保留现有 Peter 额度梗图，但图注继续明确「不是 OpenAI 补偿承诺」。
3. 备选：Tibo 原帖只在需要证据链完整性时使用；若使用，建议将 Peter 梗图下移至后文或二选一，不让开头连续堆 3 张 X 截图。

Bruno Lemos 的公开原帖已定位为 `https://x.com/brunolemos/status/2076769881534398974`，但本轮不再叠加第 3 张删文件个案图：它与 Matt 原帖的编辑任务重复，且会让开头失去节奏。

## VISUAL-00B：严肃回应下的额度玩梗

- 状态：已使用，`assets/x-peter-usage-reset-thread.png`。
- 位置：Tibo 对 GPT-5.6 文件删除报告的初步回应之后。
- 截图范围：Peter Fotinis 的主评论及紧邻的两条可见回复；移除侧栏和本地账号回复输入区，避免无关身份信息进入稿件。
- 图注：明确这是网友玩梗，不是 OpenAI 的补偿或额度承诺。
- 来源：https://x.com/peterfotinis/status/2077630629039231044
- 权利：`social_screenshot`，按有出处的评论报道素材处理，发布前人工确认。

## VISUAL-01：OpenAI 文章首屏

- 状态：已使用，`assets/openai-long-horizon-summary.png`。
- 位置：首次引出 OpenAI 7 月 20 日文章之后。
- 截图范围：OpenAI 标识、日期 `July 20, 2026`、标题、副标题与 Summary。
- 图注：7 月 20 日，OpenAI 披露一款未命名长时程内部模型的新失败模式。团队曾暂停访问，补建评测与监控后恢复有限使用。
- 来源：https://openai.com/index/safety-alignment-long-horizon-models/
- 权利：`official_material`，按有出处的评论报道素材处理。

## VISUAL-02：PR #300 对 PowerCool 的追溯

- 状态：已使用，`assets/github-pr300-powercool.png`。
- 位置：PR #287 方案被其他参赛者沿用之后。
- 截图范围：同一 PR 页面中的 #300 标题条、Merged 状态，以及 Credits 对 `PR #287 / power-law LR schedule` 的致谢；两处按上下顺序拼接。
- 图注：原 PR #287 已不再公开，后续 PR #300 仍把 PowerCool 方案追溯到 #287。该图只能证明传播链，不能当成原 PR 截图。
- 来源：https://github.com/KellerJordan/modded-nanogpt/pull/300
- 权利：`needs_review`，GitHub 界面与头像权利需人工确认。

## VISUAL-03：从单步动作到完整轨迹

- 状态：用户人工定稿重新采用，`assets/openai-trajectory-token-case.png`。
- 取舍：英文正文在手机端偏小，但人工定稿用它承担令牌拆分与轨迹级检查的视觉证据；关键含义在邻近中文正文和图注中复述。
- 位置：令牌拆分案例之后。
- 截图范围：OpenAI 原文 `From considering single actions to considering whole trajectories` 一节。
- 图注：模型把认证令牌拆分、混淆后在运行时重组，以避开扫描器。OpenAI 据此主张，长任务不能只检查单个动作，还要判断整段行动最终指向哪里。
- 来源：https://openai.com/index/safety-alignment-long-horizon-models/
- 权利：`needs_review`；按 OpenAI 官方材料的评论报道用途处理，发布前人工确认转载边界。

## VISUAL-03B：安全研究员对任务时程的概括

- 状态：已使用，`assets/x-tomek-task-horizon-comment.png`。
- 位置：解释“轨迹级监控”之后、数学案例之前。
- 截图范围：Tomek Korbak 的账号、英文原文和 X 机器翻译；裁掉下方重复的 OpenAI 文章预览。
- 图注：纠正机器翻译中 `task horizon` 的含义，并保留 `seems`、`still` 的不确定性。
- 来源：https://x.com/tomekkorbak/status/2079285014018367812
- 权利：`social_screenshot`，按有出处的评论报道素材处理，发布前人工确认。

## VISUAL-04：四项防护措施

- 状态：未用于正文；长截图移至 `research/source-assets/openai-long-horizon-safeguards.png`。
- 原因：手机端英文正文过小，且没有新增信息。
- 位置：OpenAI 暂停内部访问之后。
- 截图范围：`Building safeguards for long-running models` 下的四项措施。
- 图注：OpenAI 增加了事故衍生评测、长程指令训练、轨迹级主动监控，以及更清楚的用户可见性与控制。
- 来源：https://openai.com/index/safety-alignment-long-horizon-models/
- 权利：`official_material`。

## VISUAL-04B：内部回放结果

- 状态：已使用，`assets/openai-redeployment-results.png`。
- 位置：有限内部访问恢复及回放结果之后。
- 素材：提取 OpenAI 页面内嵌的官方 SVG，按页面计算样式还原配色并渲染成 PNG；数值、标签和图例未改。
- 图注：标明厂商自报、新防护下的三档结果，以及“不设防护”为反事实估计。
- 来源：https://openai.com/index/safety-alignment-long-horizon-models/#redeployment
- 权利：`official_material`，发布前仍需人工复核转载边界。

## VISUAL-05：Tibo 原帖，可选

- 状态：未使用。
- 位置：若编辑决定扩写外部删文件调查，再放在开头附近。
- 截图要求：完整保留头像、姓名、账号、日期和上下文，不能只做金句卡。
- 图注：OpenAI 产品负责人 Tibo 对少量 GPT-5.6 删文件报告给出初步调查口径。该组事故与 7 月 20 日匿名模型事件不能认定为同一事故。
- 来源：https://x.com/thsottiaux/status/2077630111499882637
- 权利：`social_screenshot`，发布前人工确认评论报道边界。
