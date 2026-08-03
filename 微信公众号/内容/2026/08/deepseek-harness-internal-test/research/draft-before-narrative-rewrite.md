---
title: "DeepSeek 的新东西还没发布，跑分已经先用上了"
platform: wechat
status: draft
created: 2026-08-02
updated: 2026-08-02
as_of: "2026-08-02 13:19+09:00"
fact_checked: false
rights_checked: false
copyedit_checked: false
copyedit_body_sha256: ""
judgment_workshop: "research/judgment-workshop.md"
published_url: ""
---

# DeepSeek 的新东西还没发布，跑分已经先用上了

> 一条只收 GitHub 仓库的内测帖，露出了 Agent 竞争正在换挡的地方。

8 月 1 日，DeepSeek Harness 团队成员 [Tianyi Cui](https://x.com/tianyi/status/2083519855203078320) 在 X 上开了一扇很窄的门。

想参加 DeepSeek Harness 内测，可以。但你得先是 Agent Harness 相关开源项目的开发者，再附上 GitHub ID 和代表作。

这不是常见的产品内测。没人问手机型号，也没有「转发抽邀请码」。报名者要把自己造过的东西摆上桌。

回复区很快像一场临时开起来的开源项目路演。有人带来能跑长任务的 [DeerFlow](https://github.com/bytedance/deer-flow)，有人带来本地桌面与终端工作区 [Kun](https://github.com/KunAgent/Kun)，有人研究记忆，有人做沙箱、文件系统、系统观测和安全。Raven、Maka、LobeHub、AgentSight 等项目也出现在队伍里。

还有人开玩笑，要先花一个小时现写一个，再来报名。

![Tianyi Cui 招募开源 Harness 开发者参加 DeepSeek Harness 内测](assets/x-tianyi-harness-internal-test.png)

*Tianyi Cui 在 X 上公开招募开源 Agent Harness 开发者参加内测。截图：@tianyi / X*

笑点过去，问题反而更清楚了：DeepSeek 为什么不先找普通用户，偏偏要找一群已经造过 Harness 的人？

更反常的线索藏在前一天。

![DeepSeek Harness 从组建团队到进入模型卡和定向内测的公开时间线](assets/timeline-harness-public-signals.png)

*从团队招聘到模型卡和定向内测。图：作者根据 Tianyi Cui 公开帖与 DeepSeek 官方模型卡整理*

## 前一天，它已经替 V4 跑过分

7 月 31 日，DeepSeek 发布 [DeepSeek-V4-Flash-0731](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731)。官方模型卡列出 Terminal Bench、NL2Repo、DeepSWE 等多项 Agent 基准成绩，又在表格下面加了一行很容易略过的说明：

公开基准里的 Code Agent 任务，使用 DeepSeek Harness 的 minimal mode 作为 Agent 框架，推理强度设为 max，temperature 为 1.0，top_p 为 0.95。括号里还写着，这套 Harness 「待发布」。

也就是说，外界还没见过它长什么样，它已经坐进了 V4 的考场。

不过，模型卡里的数字是 DeepSeek 自报，不是第三方复现。DeepSeek 也没有同时公开 Harness 代码、完整任务轨迹、系统提示词和全部实验条件。我们不能看到一个高分，就把功劳全部算给 Harness；更不能拿不同公司、不同运行框架下的数字直接横比。

![DeepSeek V4 Flash 两个版本在 7 项公开 Agent 基准上的官方自报成绩](assets/benchmark-agent-scores.png)

*DeepSeek 官方模型卡中的 7 项公开 Agent 基准。数值为厂商自报；图表仅复现官方表格，不能把分数变化单独归因于 Harness。图：作者根据官方模型卡整理*

这个脚注把 DeepSeek Harness 从招聘帖带进了实际评测。它已经能在内部承担 Code Agent 任务，并进入公开成绩的生成过程。

第二天，团队开始找外部开发者内测。两件事连起来，招募帖的分量就变了。

DeepSeek 可能不只是在问「这个工具好不好用」。它还在问：V4 被放进一套真实的 Agent 系统后，到底怎样才能稳定干活？

## 同一个模型，换一套 Harness，可能就不是同一个 Agent

Harness 这个词不好翻。叫「运行框架」太轻，叫「智能体系统」又太宽。

可以先把模型看成大脑。Harness 是大脑周围的身体和工作台：它把用户目标交给模型，准备上下文，开放文件、终端和网络工具，保存任务进度，安排失败后的重试，决定危险动作何时需要确认，最后再检查事情是不是真的做完了。

![Agent Harness 连接模型、上下文、工具、权限和验收环节的示意图](assets/harness-system-stack.png)

*Harness 负责把模型接到上下文、工具、权限和验收环节。图：作者绘制*

聊天时，这些环节不一定显眼。让 Agent 修改一个大型代码仓库，差别就会被放大。

它该一次读多少文件？上下文塞满以后删掉什么？终端命令能不能直接执行？测试失败后继续修，还是回到上一个节点？模型说「完成了」，谁去检查代码能不能运行？

这些问题很少写在模型参数表里，却会直接改变任务结果。

所以，同一颗模型装进不同 Harness，最后看起来可能像两个水平不同的 Agent。模型决定它能想到什么，Harness 决定这些想法怎样接触文件、工具和现实，以及犯错以后有没有机会拉回来。

![相似的大脑进入不同 Harness 后得到不同结果的笨拙涂鸦](assets/doodle-same-brain-different-harness.png)

*同一个模型进入不同运行框架，最终表现可能不同。AI 生成的编辑涂鸦，不是产品结构图*

这也是 DeepSeek 在模型卡里写明 Harness 的意义。那个分数记录的是模型和运行框架一起工作的结果，不能当成模型权重的单项成绩。

对普通读者，这个区别不只属于工程师。以后再看到某个模型「编程超过谁」，真正该追问的是：它们是不是在同一种工作台里、拿着相同工具、用同样的推理预算完成任务？

如果答案不是，排行榜仍然有参考价值，只是它回答的问题没有标题看起来那么简单。

## DeepSeek 找来的，是一群拆过机器的人

这时再看回复区，那些 GitHub 仓库也把 DeepSeek 想找的问题摊开了。

DeerFlow 把子 Agent、记忆、沙箱、工具和 Skills 组织进长任务；Kun 同时做桌面界面和终端工作区；Raven 把记忆放在核心位置；AgentSight 盯着 Agent 在系统里做了什么；LobeHub 试着组织和调度一组 Agent。

这些项目没有采用同一套答案。恰恰因为不同，它们的作者知道问题通常坏在哪里。

做过长任务的人，会追问上下文压缩后丢了什么。做过沙箱的人，会先看权限边界。做桌面 Agent 的人，会盯住接管与用户确认。做观测工具的人，则会问一次任务失败以后，开发者能不能沿着轨迹找到原因。

普通体验官可以告诉 DeepSeek 一个按钮顺不顺手。这群开发者更可能在几轮任务后指出：工具调用协议哪里别扭，状态怎样丢失，哪个错误被模型吞掉了，哪种安全设计让任务根本跑不起来。

所以，这次定向内测更像一轮外部压力测试。DeepSeek 找来的不是一群等着看新界面的用户，而是一群已经为 Agent 造过不同身体、知道螺丝会从哪里松掉的人。

![开源 Harness 开发者带着各自工程经验进入内测的笨拙涂鸦](assets/doodle-open-source-builders-test.png)

*开源 Harness 作者带着各自做过的工程选择进入内测。AI 生成的编辑涂鸦，不代表正式合作关系*

当然，还有更朴素的解释。新团队需要高质量测试者，也可能顺便寻找人才；开源作者比随机用户更容易给出可执行的反馈。现在还没有公开的测试协议、产品截图或反馈去向，不能仅凭一条招募帖，就宣布 DeepSeek 已经组好了某个开源生态联盟。

但无论动机停在哪一层，这个筛选条件都说明了 DeepSeek 眼下要什么：能碰到系统边界的工程反馈，远比一轮「好不好玩」的第一印象重要。

## 一边进入别人的工作台，一边搭自己的

与此同时，DeepSeek 也在让 V4 进入第三方 Harness。

它的官方 [Awesome DeepSeek Agent](https://github.com/deepseek-ai/awesome-deepseek-agent) 仓库正在整理大量接入指南，覆盖 Claude Code、Codex、OpenCode、Pi、Hermes、LobeHub 等 Agent 与编程助手。路线很直接：开发者已经在哪个工作台里，就尽量让 DeepSeek 模型进去。

这条路能最快抵达用户，也省去了从头教育市场的成本。可一旦模型进入别人的 Harness，怎样准备上下文、调用工具、压缩记忆和验收结果，主要由那套工具决定。用户看到的最终体验，不完全掌握在模型公司手里。

自己的 Harness 补上了另一半。

它可以成为 DeepSeek 模型的参考用法：面对长任务时怎样分配推理强度，怎样安排工具循环，怎样把失败暴露出来。它也可能成为更贴近模型团队的反馈入口，让「模型为什么没做成」不只剩下一句模糊的用户抱怨。

再往前走一步，它还可能成为评测基线。DeepSeek 已经在 V4-Flash-0731 的模型卡里这样使用它了。

这三件事——产品入口、反馈入口、评测框架——目前都还只是根据公开动作得出的推测。DeepSeek 没有公布 Harness 的正式定位，也没有说它会不会开源、面向谁、是否只做编程任务。

到现在为止，我能下的判断是：DeepSeek 正在补从模型供应商到 Agent 系统供应商的最后一公里。

它一边让 V4 进入别人的工作台，一边搭一张自己的工作台。前者解决模型能不能被更多人用，后者决定 DeepSeek 能不能亲自回答一个越来越重要的问题：这颗模型究竟该怎样用，才能把能力稳定变成结果？

## 这条内测帖还没有证明什么

现在最容易犯的错，是替一个尚未发布的东西把故事写完。

我们还不知道 DeepSeek Harness 有没有独立界面，是内部评测框架还是面向用户的完整产品；不知道第一版是否以 Coding Agent 为主，也不知道发布日期、价格和开源方式。

「待发布」只证明公开发布在计划里，不等于本周上线。邀请开源作者，不等于产品也会开源。V4 用它跑出高分，也不等于它已经在真实工作里赢过 Claude Code、Codex 或 OpenCode。

产品截图只能告诉我们界面长什么样。更能检验这套 Harness 的，是任务轨迹能不能复现，失败后怎样恢复，危险工具如何受控，同一个模型换进别的 Harness 后成绩会变多少，以及外部开发者究竟挑出了什么问题。

6 月 21 日，Tianyi Cui [曾公开说](https://x.com/tianyi/status/2068652453797724562)，DeepSeek Harness 是一个新成立的部门，正在招研究员、工程师和产品经理。一个多月后，它先进入模型卡，再打开一轮定向内测。至少在向外部开发者开门之前，这套内部系统已经跑过 Code Agent 基准任务。

故事还缺正式发布那一幕。

不过，回复区已经提前画出了一张轮廓。大家递上来的不只是 GitHub 仓库，还有一份 Agent 真正开始干活以后绕不开的清单：记忆、工具、沙箱、文件、权限、验证、安全，以及失败以后怎么回来。

过去判断一家模型公司有没有追上前沿，大家盯参数、价格和排行榜。DeepSeek 这条只有几句话的内测帖提醒我们，以后还得多问一句：

它给这颗大脑配了什么身体，又准备让谁握住方向盘？
