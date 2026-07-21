# 来源与证据

- 二轮访问与核查日期：2026-07-12
- 事实卡：`research/fact-sheet.md`
- 原则：发布与价格先以一手页面为准；能力比较再用独立评测校准。X 页面无法直接渲染时，只使用包内截图可见内容，并把页面不可访问写进限制。

| 来源 | URL/路径 | 类型 | 访问日期 | 支持表述 | 口径与备注 |
|---|---|---|---|---|---|
| OpenAI：GPT-5.6 发布页 | <https://openai.com/index/gpt-5-6/> | 官方发布 | 2026-07-12 | 7 月 9 日发布；Sol / Terra / Luna 定位；`max` / `ultra`；上线范围；发布页价格；厂商评测表 | 厂商自报。正式 rollout 是从发布日起在 24 小时内渐进完成，不能把单个发布时刻写成所有用户同时可用。`ultra` 默认四 agent，配置与单 agent 不同。 |
| OpenAI API Pricing | <https://developers.openai.com/api/docs/pricing> | 官方文档 | 2026-07-12 | 当前标准短上下文 API 价：Sol $5/$30、Terra $2.50/$15、Luna $1/$6（每百万输入/输出 token） | 与发布页当日公开价一致；当前页面另列标准长上下文价 Sol $10/$45、Terra $5/$22.50、Luna $2/$9。Batch、Flex、Priority、缓存和区域处理另有口径；token 单价不等于完成任务总成本。 |
| OpenAI：ChatGPT Work | <https://openai.com/index/chatgpt-for-your-most-ambitious-work/> | 官方发布 | 2026-07-12 | Work 是 ChatGPT 内的 agent；Codex app 合并进新版 ChatGPT 桌面端；Codex 可设默认视图；旧 ChatGPT 桌面端改名 Classic；Codex 周活与非开发用途数字 | 产品形态与入口变化可直接引用；“超过 500 万周用户、超过 100 万用于软件开发之外”为 OpenAI 自报，未公开去重与任务分类方法。 |
| OpenAI Forum：Codex 活动 | <https://forum.openai.com/public/events/codex-is-for-everyone-why-codex-matters-beyond-code-fa40puy7wi> | 官方社区 | 2026-07-12 | Thibault “Tibo” Sottiaux 是 OpenAI MTS，Head of Codex / leads Codex | 支持写“Codex 负责人”；不支持扩写成“OpenAI 全部 ChatGPT 与 Codex 的负责人”。 |
| OpenAI 官方直播预告原帖 | <https://x.com/OpenAI/status/2075254288956440848> | 官方社交原帖 | 2026-07-12 | 预告 2026-07-09 10:00 PT 开播 | X 直达页本次未返回正文；时间由原帖直链在 Digg 镜像页展示。只用于近似时间线，不作为“所有用户广泛上线”的精确时刻。 |
| OpenAI 发布直播回放 | <https://www.youtube.com/watch?v=Wq45rvPGNHs> | 官方视频 | 2026-07-12 | 回放标题为 “Introducing ChatGPT Work, powered by Codex and GPT-5.6” | 本次文本抓取未返回视频元数据或逐字稿；不能仅据此精确到分钟。 |
| Digg：OpenAI 直播预告镜像 | <https://digg.com/tech/3omw8o0i> | 第三方聚合 | 2026-07-12 | 展示 OpenAI 原帖直链及 “Today. 10am PT” | 用来校准不可渲染的 X 原帖；不是 OpenAI 发布页，不能替代官方产品事实。 |
| Axios：OpenAI releases GPT-5.6 and ChatGPT Work tool | <https://www.axios.com/2026/07/09/ai-openai-gpt-release> | 独立媒体 | 2026-07-12 | 7 月 9 日广泛发布、三档定位与 ChatGPT Work 同日发布 | 页面正文未给出 17:00 UTC 的精确“广泛上线”时间，因此不支持旧稿的精确时刻断言。 |
| ClaudeDevs reset 与 Tibo 回复截图 | `assets/claude-reset-tibo.png` | 用户提供 / 社交截图 | 2026-07-12 | ClaudeDevs 原文 “We've reset 5-hour and weekly rate limits for all users.”；截图显示本地时间 2026-07-10 03:01；Tibo 回复 “I smell fear” | 截图没有印出时区；只能在明确“按截图本地时区换算”的前提下计算间隔。公告没有解释动机，也没有说永久扩容、unlimited 或 API 限流重置。 |
| Tibo 原帖直链 | <https://x.com/thsottiaux/status/2075287108680601929> | 当事人社交原帖 | 2026-07-12 | `I smell fear` 的原帖定位与账号 | X 直达页本次返回 cache miss；原文与回复关系由包内截图和下列独立报道交叉确认。 |
| OfficeChai：I Smell Fear | <https://officechai.com/ai/i-smell-fear-says-openai-exec-who-led-gpt-5-6-sol-livestream-after-claude-resets-usage-limits-for-users/> | 独立媒体 | 2026-07-12 | 提供 Tibo 原帖直链；把评论描述为针对 reset 的竞争性调侃 | 可校准回复语境，不采用其对 Tibo 职务的扩张性称呼，也不把媒体对动机的解读当事实。 |
| Claude Usage limit best practices | <https://support.claude.com/en/articles/9797557-usage-limit-best-practices> | 官方帮助 | 2026-07-12 | Pro、Max、Team、seat-based Enterprise 的五小时 session 与 weekly usage limits；Usage 页面分别显示两类消耗与下次 reset | 支持把 reset 理解为订阅产品当前计数器重置；不支持解释成 API rate limit、永久加量或新的固定额度。实际消息数受长度、附件、对话长度、工具使用和模型影响。 |
| Anthropic：Claude Fable 5 / Mythos 5 | <https://www.anthropic.com/news/claude-fable-5-mythos-5> | 官方发布 | 2026-07-12 | Fable 5 / Mythos 5 定位、可用范围与 API 价 $10 输入 / $50 输出 | 厂商自报。Mythos 5 与 Fable 5 是同底层模型，但前者在部分领域解除 safeguards、访问受限；跑分必须写清具体版本。 |
| Claude Status | <https://status.claude.com/> | 官方状态页 | 2026-07-12 | 7 月 7–10 日多次已记录故障；7 月 8 日多个模型报错与 Claude Code/Cowork 等性能问题；7 月 12 日页面显示系统正常 | 只能证明故障背景，不能证明 7 月 9 日 reset 的原因。状态页会滚动更新。 |
| Claude Fable 5 promotional access | <https://support.claude.com/en/articles/15424964-claude-fable-5-promotional-access> | 官方帮助 | 2026-07-12 | 原计划用于核对促销体验延期 | **本次访问返回 Internal Error**。不得据此写“reset 是延期补偿”或任何已证实动机；如正文保留，只能明确为未证实猜测，建议删除。 |
| Artificial Analysis：GPT-5.6 评测文章 | <https://artificialanalysis.ai/articles/gpt-5-6-has-landed> | 第三方评测 | 2026-07-12 | Sol max 在 Intelligence Index 为 59，Fable 5 max 为 60；Sol 在 Coding Agent Index 为 80；Terra / Luna 为 55 / 51 | Artificial Analysis 曾参与 OpenAI 的预发布评估，但评测与榜单由其发布；Coding Agent Index 使用各自 agent harness，不能等同裸模型统一环境。 |
| Artificial Analysis：模型总榜 | <https://artificialanalysis.ai/leaderboards/models/> | 第三方榜单 | 2026-07-12 | 当前榜单：Fable 5（with Opus 4.8 fallback）60 分第 1，GPT-5.6 Sol max 59 分第 2；Terra max 55、Luna max 51 | 综合指数会掩盖任务差异；Fable 条目含 Opus 4.8 fallback；榜单会更新，发布前须重开。 |
| Artificial Analysis：GPT-5.6 Sol | <https://artificialanalysis.ai/models/gpt-5-6-sol> | 第三方评测 | 2026-07-12 | Sol max 59 分、API 价格与速度等模型页数据 | 单模型页；结论受评测套件、reasoning effort 与提供商行为影响。 |
| Artificial Analysis：Claude Fable 5 | <https://artificialanalysis.ai/models/claude-fable-5> | 第三方评测 | 2026-07-12 | Fable 5 条目 60 分与 $10/$50 | 页面明确标注 “with fallback / Opus 4.8 fallback”，不能把结果写成纯 Fable 5 无回退测试。 |
| METR：GPT-5.6 Sol 预部署评估 | <https://metr.org/blog/2026-06-26-gpt-5-6-sol/> | 独立研究组织 | 2026-07-12 | 对软件/R&D 能力未显著超出现有前沿的谨慎判断；time-horizon 测量因作弊判定极不稳健 | 不是通用能力总榜。METR 明确说 11.3h、71h、270h+ 等估计均不构成稳健测量，不得摘取单个数字宣传。 |
| OpenAI：SWE-Bench Pro 审计 | <https://openai.com/index/separating-signal-from-noise-coding-evaluations/> | 官方审计 | 2026-07-12 | 731 个公开任务；pipeline 标出 200 个（27.4%），人工标注活动标出 249 个（34.1%）；估计约 30% 任务有破损问题 | OpenAI 是参赛厂商且曾推荐该题集，不是外部独立审计。原文是建议开发者谨慎审视结果，没有明确写“撤回推荐”。 |
| Arena Leaderboard | <https://arena.ai/leaderboard> | 第三方榜单 | 2026-07-12 | 原计划核对 GPT-5.6 的人类偏好票数与名次 | **本次页面只返回导航，不返回模型行、票数或置信区间**。不能继续写“票数不足”或任何名次判断；需要人工浏览器看到榜单行后再补。 |
| 参考公众号文章 | <https://mp.weixin.qq.com/s/YZdoqo4eWbO1oqcCDujxBA> / `research/reference-article.txt` | 用户指定参考 | 2026-07-12 | 信息组织与原始话题背景 | 仅用于结构研究，不证明本文事实，也不复制独特表达。 |

## 本轮不可访问 / 不可用页面

- <https://support.claude.com/en/articles/15424964-claude-fable-5-promotional-access>：返回 `Internal Error`；促销延期与 reset 的关系未核实。
- <https://x.com/OpenAI/status/2075254288956440848>：直达页未返回正文；仅通过保留原帖直链的第三方镜像校准 10:00 PT 直播预告。
- <https://x.com/thsottiaux/status/2075287108680601929>：直达页返回 cache miss；原文由包内截图与独立报道交叉确认。
- <https://arena.ai/leaderboard>：页面未返回实际榜单行；不对 GPT-5.6 票数或排名下结论。
