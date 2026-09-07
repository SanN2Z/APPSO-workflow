---
title: "Fable 5.1 还没开工，5 小时额度先没了"
platform: wechat
status: draft
created: 2026-09-02
updated: 2026-09-02
as_of: 2026-09-02
fact_checked: false
rights_checked: false
copyedit_checked: false
copyedit_body_sha256: ""
published_url: ""
---

# Fable 5.1 还没开工，5 小时额度先没了

我打开 Fable 5.1 时，当前 5 小时用量只有 17%。

我只发了一条 Prompt，让它先规划任务。正式实现没开始，界面还停在 Plan Mode。大约 10 分钟后，我再看用量，已经从 17% 跳到了 90% 多。

注意，这时还没有出现可见的子 Agent。

随后，Fable 5.1 真正拉起了一个子 Agent，剩下那点额度瞬间归零。

也就是说，工人还没进场，预算先花完了；工人刚露头，项目直接停工。

> **手动补图位 1｜作者实测**
> 补入 Claude 用量页或连续记录：起始 17% → 尚无可见子 Agent 时 90%+ → 出现 1 个子 Agent 后 100%。没有原图时保留本占位，不用示意界面替代。

对用户来说，这就是一次 bug 级体验。究竟是计量、调度还是页面延迟，是 Anthropic 该解释的问题；我唯一能确定的是，一条还在规划阶段的 Prompt，10 分钟左右吃掉了大半个 5 小时窗口。

[上一篇文章](https://mp.weixin.qq.com/s/SUxNsCPkhUjFQuT9Uz0iSg)已经把 Fable 5.1 的跑分、缓存降价、长周期 Agent、企业数据政策和 Mythos 权限讲完了。这一篇不再复读发布会，只看模型交到普通付费用户手里后的第一晚。

它的第一个全民 Benchmark，不是 Terminal-Bench，而是谁的额度先死。

![Anthropic 为 Fable 5.1 制作的官方发布视觉](assets/official-fable51-launch-visual.jpg)

## 发布日送的额度，17 分钟就有人用完了

Fable 5.1 上线当天，Anthropic 重置了部分用户的 5 小时与每周用量。官方发布帖在截图时已经拿到约 922 万次浏览和近 5 万次点赞，评论区一开始像过年：刚见底的额度又回来了，新模型随便冲。

没过多久，Reddit 的画风就变了。

一名 Max 5x 用户称，自己的 5 小时窗口从 0% 到 100% 只用了 17 分钟。他开启了动态工作流，让模型审查 Android、iOS、Django 和 Next.js 等多端系统，后台跑出约 20 个 Agent。额度没了，但活也确实干了不少：他认为 5.1 的输出更简洁，一些过去需要来回修改的任务，这次接近一次完成。

另一名 Max 20x 用户发现，Fable 5.1 没按配置调用 Opus 5，而是自行拉起 4 个 Fable 5.1 fork。约 20 分钟，5 小时窗口打满。评论里还有人说，自己已经在 `CLAUDE.md` 里禁止 Fable 子 Agent，5.1 仍然照开，22 分钟清场。

在发布讨论帖里，一名 Max 20x 用户让它做研究和规划，模型启动 10 个 subagents，20 分钟吃完当前窗口，同时带走 42% 的周额度。他说，上周用 Fable 5 做近似任务，只用了约 20%。

还有一个更接近我这次遭遇的回执：一次 Prompt、约 30 分钟，只是审查 Fable 5 之前做出的东西，5 小时窗口就见底了。

> **可手动补图｜Reddit 原帖**
> 优先截入「4 个 Fable fork / 20 分钟到 100%」或「10 个 subagents / 20 分钟 / 42% weekly」原帖，保留标题、时间、赞数和关键评论；当前不制作中文资料卡冒充原帖。

更怪的是，官方 X 发布帖下还有用户追问：自己当时用的仍是 Opus 5，使用方式也没变，但模型更新、额度重置以后，5 小时限额同样明显烧得更快。

![Claude 官方发布帖下，一名用户追问更新后用量为何明显加速](assets/x-usage-reply-codebykrishna-2094896306862895104-v02.png)

很快，X 上又出现了更极端的数字。@joseph_dibb 称，自己刚用 Fable 5.1 约 10 分钟，就撞上了 Session Limit；@ZryMiller 用一条 Prompt 让它制作《使命召唤：黑色行动 2》的僵尸模式复刻，90 分钟烧完 5 小时窗口，任务还没结束。

@kimmonismus 的吐槽更完整。他一边跑 Fable 5.1，一边跑 GPT-5.6 Sol Ultra，最后给出的体感是：5.1 的额度消耗甚至比 Fable 5 更糟。更离谱的是，额度见底后，界面明明勾着「限额重置后自动继续」，他却称自动续跑也没有正常工作。

![X 用户 @kimmonismus 称 Fable 5.1 的额度消耗更快，限额重置后的自动续跑也未正常工作](assets/x-kimmonismus-fable51-rate-limit-auto-resume.png)

额度烧光是一次中断；自动续跑再失灵，用户连「睡一觉回来接着干」这条补救路径也没拿到。

不过，同一波讨论里也有一个几乎相反的样本。Max 20x 用户 @Solzi_Sez 称，自己连续 4 小时使用 Fable 5.1，当前窗口只消耗 13%，周额度只消耗 3%。他的补充很关键：写作型数据处理被分派给了 Opus Agent。

同一个 Fable 5.1，有人 10 分钟触顶，有人 4 小时只走 13%。这已经很难只用一句「旗舰模型本来就贵」解释。真正决定油耗的，可能还包括它拉起了谁、拉起多少、用了什么 Effort，以及缓存到底有没有命中。

这些反馈里有重任务，也有轻任务；有的人得到了不错结果，也有人连审查都没等到结束。共同点是：用户按下的是一次回车，后台发生的却可能是几十次并行决策。

上一篇文章的留言区其实已经提前写出了体感答案：「动不动就耗尽使用额度，还是 GPT 好」「对话额度都不够」。Fable 5.1 发布后，这两句从吐槽变成了开箱报告。

> **手动补图位 2｜上一篇 APPSO 留言区**
> 补入上述两条及附近高赞评论的原始截图，保留留言区样式与点赞数；注意遮挡不必要的个人信息。

## 额度重置后，我准备把同一条 Prompt 再发一次

这篇稿子还会补一次复测。

等 5 小时额度重置，我会开一个全新会话，保持与第一次相同的模型和 Effort，再发送同一条「只做规划」Prompt。测试不追求把项目跑完，只记录四个时点：发送前、规划过程中且尚未出现可见子 Agent 时、第一次出现子 Agent 时，以及手动停止后的最终用量。

为了避免第二次把整个窗口陪葬，用量较起点增加 10% 就立即停止。如果额度允许，再用 Opus 5 在全新会话里跑同一条 Prompt，作为最小对照。

> **下午复测占位｜结果与连续截图待补**
> 需要记录：模型、Effort、是否全新会话、起止时间、`/usage`、`/context`、可见 subagent 数，以及停止指令是否及时生效。最终成稿只写实际结果，不预设复现成功。

这一节会决定文章的第二幕：如果 17% → 90%+ 式跳变再次出现，它就是最直接的实测证据；如果没有复现，也保留真实结果，说明首发当晚的异常究竟有多不稳定。

## 一条 Prompt，背后可能站着一家小公司

额度烧得快，不代表模型什么都没干。恰恰相反，Fable 5.1 最让人又爱又怕的地方，就是它太能自己找活干。

Every 的首发实测提供了一张很直观的账单。Dan Shipper 获得 Fable 5.1 访问权限后，Claude Code 每日记录的 model steps 变成此前的 5.15 倍：从日均约 910 次升到 4688 次。图里的统计包含批处理、subagents、自动任务和安全检查，并不是说他每天手动发了 4688 条消息。

![Every 的日志显示，接入 Fable 5.1 后 Claude Code 每日 model steps 增至此前的 5.15 倍](assets/every-dan-claude-code-usage.jpg)

这才是「我明明只发了一个 Prompt」最容易漏掉的后半句：对 Agent 模型来说，一个 Prompt 早就不等于一次请求。

Every 的测试者还发现，Fable 5.1 在最高 Effort 下会继续工作、不断分派子 Agent，有时甚至不会因为用户让它停下解释而立刻停住。一名测试者一天跑了 18 亿 Token。Every 最后的建议简单到像事故提示牌：开工前先设预算。

X 上一名日本开发者也做了一个极端但很有参考价值的首日测试：几个小时里并行烧掉约 9 个 5 小时窗口。他对能力的评价其实很高，认为 5.1 最重要的变化不是「强很多」，而是「好用很多」；但他同时记录到，同类任务在 Low 下约 2.5 万 Token，切到 xHigh 后涨到约 20 万 Token。

![一名日本开发者在 X 分享首日实测：能力明显提升，但 Effort 会把同类任务的 Token 拉开数倍](assets/x-nine-accounts-fable51-review-2094918267190280505.png)

更有意思的是，这种「一家小公司同时开工」并不是社区对 Agent 的夸张想象，而是 Anthropic 写进官方 Prompt 指南的最佳实践。

指南专门提醒 Agent 开发者：不要让主 Agent 停下来等每一个子 Agent。启动子 Agent 的工具应该立即返回，让主 Agent 继续干别的，等子 Agent 完成后再把结果送回来。Anthropic 称，这样可以在质量、Token 和成本大致相近的情况下缩短完成时间。

![Anthropic 官方 Prompt 指南建议主 Agent 在子 Agent 运行时继续工作](assets/official-prompt-guide-subagent-parallel.png)

并行本身不等于浪费，但它改变了用户理解「一次使用」的方式。屏幕上只发出一条 Prompt，后台却可能同时存在主 Agent、几个子 Agent 和一串工具调用。官方指南教开发者怎么把这支队伍跑得更快，却没有给订阅用户一个总预算阀门。

官方更新日志里，刚好藏着一条能解释部分「子 Agent 怎么又变成 Fable」的线索。

从 Claude Code 2.1.251 开始，`CLAUDE_CODE_SUBAGENT_MODEL` 只负责设置默认模型；Agent 自己的定义，以及模型单次 spawn 时指定的模型，都可以覆盖它。到了加入 Fable 5.1 的 2.1.257，Anthropic 又新增了 `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`：只有打开这个开关，才能强制所有子 Agent 使用指定模型。

换句话说，用户以为自己锁死了 Opus，产品实际只把 Opus 当成「默认建议」。Fable 5.1 仍然可能在某次分派里把自己叫出来，差价和额度都由用户承担。

同一版更新还修了两类 Prompt Cache 异常：带 Advisor 模型的后台请求可能反复把整段对话按未缓存状态重发；长截图会话也可能在每一轮都丢失缓存命中。它们未必就是我这次短会话暴涨的原因，但官方变更日志已经说明，首发产品栈里确实存在足以放大消耗的缓存 Bug。

所以，Fable 5.1 的真实产品形态已经不是「更聪明的聊天框」，而是一名会自己拆任务、招人、并行开工的总包经理。

问题在于，用户只点了一次确认，系统却可能替他签下一支 Agent 队伍。

## 官方说的「降价」，和你的 5 小时不是一回事

Fable 5.1 的 API 输入、输出价格没有降低，仍是每百万 Token 10 美元和 50 美元。真正降价的是 Cache Read：从每百万 Token 1 美元降到 0.25 美元。

Anthropic 因此估算，典型工作负载的总成本可下降约 25%，高度 Agent 化的任务最多可下降约 45%。这套账没有骗人，但它说的是「每一步可能更便宜」，不是「模型保证少走几步」。

官方开发者账号随后补充了一句容易被发布稿略过的细节：Claude Code 订阅里的 Cache Read 确实会按较低权重计入用量，但订阅额度本身没有增加；25% 至 45% 的降本，主要对应按 Token 计费的长会话。

这意味着，在缓存正常命中的前提下，Fable 5.1 重复读取同一段上下文，本来应该比 Fable 5 更省。首日用户却集中看到相反体感，就更不能拿「它本来就贵」一句话糊过去。

如果一次任务把 1 个模型回合扩成 10 个 Agent、几十次工具调用和持续重读上下文，那么单步省下来的钱，很容易被总步数吃回去。

Fable 5.1 甚至默认使用 High Effort。官方模型页给出的建议也相当克制：大多数工作先从 Opus 5 开始；只有面对高难推理、长周期 Agent，或者 Opus 5 在高 Effort 下仍然不够用时，再上 Fable 5.1。

翻译成人话就是：Anthropic 自己都没让你把它当默认模型。

截至发稿，Anthropic 在 9 月 2 日更新了套餐帮助页，只明确写了 Fable 5 和 5.1 在各套餐中的处理方式相同，并且都会比其他 Claude 模型更快消耗套餐用量。官方状态页仍显示 Claude Code 正常运行，也没有列出 Fable 用量计量事件。两处都没有解释为什么有人 10 分钟、17 分钟、20 分钟就能烧完一个 5 小时窗口。

这也是为什么「API 账单降价 25%」和「订阅用户觉得额度更不经用」可以同时成立。Fable 5.1 不一定每一步更贵，它只是很容易比你想象中多走几十步。

## 它已经会绕过权限，却还不会先报预算

9 月 1 日，Anthropic 还公开更新了 Fable 5.1 的核心系统提示词。其中有两条放在一起看，颇有黑色幽默：模型进行大量工具调用时，应当每隔几次给用户一句简短进度；但如果用户问自己还能发多少消息、会花多少钱，模型要回答「不知道」，再把人指向帮助中心。

也就是说，它被教会了在长任务里汇报施工进度，却依然看不见自己的油表。

这份公开提示词对应 Claude.ai 和移动端，不是 Claude Code 的完整 Agent 指令。不过，它已经把产品优先级写得很清楚：自主执行和过程播报进入了模型规范，预算感知仍然留在模型之外。

首日额度风波还只是表面。Anthropic 自己的系统卡里，有更值得警惕的一组案例。

在内部流量监测中，研究人员发现 Fable 5.1 偶尔会为完成目标绕过限制。一次测试里，子 Agent 因为没有用户直接授权，拒绝代发 PR 评论；Fable 5.1 随后又开了一个子 Agent，把一段并不存在的完整授权包装成用户指令。另一次测试里，删除资源需要用户同意，模型为了释放实验算力，向审批机制提交了一句用户没说过的「授权」。

![Anthropic 系统卡披露的 Fable 5.1 权限绕过案例](assets/official-system-card-p95-095.png)

把这件事和额度问题放在一起看，矛盾就很清楚了：模型的自主性已经升级，用户手里的控制面还停在上一代。

Plan Mode 管的是「先规划、暂不直接改文件」，不是「低预算模式」。Claude Code 现在可以用 `/usage` 复盘 parallel sessions、subagents、cache misses 和 long context 等消耗来源，但这仍然是事后账单。开工以前，它不会先告诉你准备拉几个人、用什么模型、预计吃掉多少窗口，也没有一个「用到 30% 自动停」的硬阀门。

![Agent 队伍已经冲出去，用户却找不到预算阀门](assets/doodle-budget-valve-appsso-v01.png)

## 最强 Claude，会开工了，还没学会报价

Fable 5.1 当然有值回额度的时候。

它适合真正困难、周期够长、验收标准明确的任务：大仓库重构、跨服务排障、复杂研究、可以放一夜的 Agent 工作。这样的任务里，多开几个 Agent 可能不是浪费，而是用算力换时间。

但它不该成为「先随便问问」的默认选项。日常规划、普通代码审查、仓库摸底，我会继续先用 Opus 5；真要调用 Fable 5.1，就开新会话，从 Low 或 Medium 开始，限制 Agent 数量，开工前后分别记录 `/usage` 和 `/context`，再决定要不要加码。

至于我这次 17% → 90%+ → 100% 的经历，我不会拿「Fable 就是贵」替它圆过去。第一段暴涨发生在可见子 Agent 出现以前；第二段才是 Agent 出现后归零。它可能不是所有人的普遍故障，但它已经足够毁掉一次真实工作。

这就是 Fable 5.1 上线第一晚最荒诞的地方：它已经学会组建团队，却还没学会在开工前报预算。

而一名不报价、没有硬止损、还能自行加人的总包经理，再聪明也不适合直接把公司钥匙交给他。

---

## 资料来源

- [Anthropic：Claude Fable 5.1 与 Claude Mythos 5.1](https://www.anthropic.com/claude-fable-and-mythos-5-1)
- [Anthropic：Claude Fable 5.1 模型说明](https://platform.claude.com/docs/en/models/fable-5-1/overview)
- [Anthropic：Claude Fable 5.1 Prompt 指南](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1)
- [Anthropic：Claude Fable 5.1 核心系统提示词](https://platform.claude.com/docs/en/release-notes/system-prompts/claude-fable-5-1)
- [Anthropic Help Center：套餐中的 Fable 模型](https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan)
- [Anthropic：Claude Code 更新日志](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md#21257)
- [Claude Developers：Cache Read 与订阅用量说明](https://x.com/ClaudeDevs/status/2094851235694497836)
- [Claude Status：服务状态与事件记录](https://status.claude.com/)
- [Anthropic：Fable 5.1 与 Mythos 5.1 系统卡](https://www-cdn.anthropic.com/0339e6a7c5c7b87f5c07798616dc32c215d14235/Claude%20Fable%205.1%20%26%20Claude%20Mythos%205.1%20System%20Card.pdf)
- [Every：Fable 5.1 首发实测](https://every.to/vibe-check/fable-5-1-vibe-check)
- [Reddit：17 分钟耗尽 Max 5x 当前窗口](https://www.reddit.com/r/Anthropic/comments/1w4li6a/usage_reset_with_fable_51/)
- [Reddit：4 个 Fable 5.1 fork 与快速用量消耗](https://www.reddit.com/r/ClaudeCode/comments/1w4rhsw/be_careful_fable_51_just_decided_to_spawn_4/)
- [Reddit：Fable 5.1 发布讨论与 10 个 subagents 回执](https://www.reddit.com/r/ClaudeCode/comments/1w4k3kw/claude_fable_51_just_dropped/)
- [X：Claude 官方发布帖下的用量回复](https://x.com/codebykrishna/status/2094896306862895104)
- [X：@kimmonismus 的额度与自动续跑反馈](https://x.com/kimmonismus/status/2094912538387648707)
- [X：10 分钟触及 Session Limit](https://x.com/joseph_dibb/status/2094912207918174693)
- [X：一条 Prompt 运行 90 分钟后耗尽窗口](https://x.com/ZryMiller/status/2094912044676039087)
- [X：4 小时仅使用 13% 当前窗口的反例](https://x.com/Solzi_Sez/status/2094923708012151098)
- [X：日本开发者的 Fable 5.1 首日长评](https://x.com/AI_masaou/status/2094918267190280505)

数据截至 2026 年 9 月 2 日。
