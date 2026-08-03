---
title: "DeepSeek 自研 Harness 未发先跑分，内测先找同行"
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

# DeepSeek 自研 Harness 未发先跑分，内测先找同行

> X 上有人开玩笑，要让 Fable 5 花一小时现造一套来换门票。我顺着招募帖往前翻了一天：DeepSeek 的 Harness 还没公开，V4 已经用它跑过公开 Code Agent 任务。

LinearUncle 转发 DeepSeek 的内测帖时说，大意是：等一下，他现在去让 Fable 5 花一个小时搭个 Harness，再回来报名。

这个玩笑很像现在的开发者。缺一个项目，先让 Agent 生成；缺一张门票，先生成一个能交上去的项目。

我看到时也觉得，好像真有路。

8 月 1 日，DeepSeek Harness 团队成员 [Tianyi Cui](https://x.com/tianyi/status/2083519855203078320) 发出内测招募。条件只有几行：面向 Agent Harness 相关开源项目开发者，报名时附 GitHub ID 和开源代表作。

![LinearUncle 转发 DeepSeek Harness 内测帖时表示准备使用 Fable 5 现场搭建](assets/x-linearuncle-fable5-joke.png)

*LinearUncle 转发内测帖时开玩笑，准备让 Fable 5 花一小时现场搭一个。截图：@LinearUncle、@tianyi / X*

我没有先开 Fable 5。我去翻了 DeepSeek 前一天发布的模型卡。

往表格底下拖，一行脚注把这条招募帖变成了另一回事。

7 月 31 日发布的 [DeepSeek-V4-Flash-0731](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731) 模型卡写明：公开基准里的 Code Agent 任务，使用 DeepSeek Harness 的 minimal mode；推理强度为 max，temperature 为 1.0，top_p 为 0.95。Harness 后面还跟着一个括号：「待发布」。

也就是说，外界还没拿到这套东西，它已经进入了 V4 的成绩表。

往前再翻，6 月 21 日，Tianyi Cui [公开招人](https://x.com/tianyi/status/2068652453797724562)，称 DeepSeek Harness 组是新成立的部门，招聘研究员、工程师和产品经理。六周后，Harness 先出现在模型卡里；第二天，团队开始找其他 Harness 的开发者参加内测。

到这里，我想看的已经不是 DeepSeek 会不会再做一个 Agent 产品了。我更想知道：它为什么先让自己的 Harness 参与跑分，再请一群正在造其他 Harness 的人进来？

## Harness 还没公开，评测条件先出现了

模型卡列了 7 项公开 Agent 基准。下面这张图只把 DeepSeek 官方表格中的 0731 版和 Preview 版重画了一遍。

![DeepSeek V4 Flash 两个版本在 7 项公开 Agent 基准上的官方自报成绩](assets/benchmark-agent-scores.png)

*数值为 DeepSeek 厂商自报。不同基准的指标与难度不能横向比较，只能看同一行的版本差异；分数变化也不能单独归因于 Harness。图：作者根据官方模型卡整理*

这些数字有一个目前绕不过去的问题：别人还不能在同样的环境里把它们重新跑一遍。

DeepSeek 披露了 Harness 的名字、模式和采样设置，这是有用的信息。但代码没公开，任务轨迹、系统提示词和完整实验条件也没有。我们知道评测时它在场，不知道它具体做了什么，更拆不出模型和 Harness 各自贡献了多少。

这不只是一个脚注够不够详细的问题。

拿「修掉仓库里一个失败的测试」来说。有的 Harness 会先把整个仓库交给模型，有的只挑几份文件。模型要进终端时，一套框架直接放行，另一套会拦住某些命令。测试失败以后，任务可以结束，也可以把错误送回去再改一轮。模型说「完成」时，外面还会不会重新跑测试，又是一个分叉。

同一份模型权重走过这些分叉，最后可能一个通过，一个失败。

![Agent Harness 连接模型、上下文、工具、权限和验收环节的示意图](assets/harness-system-stack.png)

*常见 Agent Harness 所处位置的通用编辑示意，不代表 DeepSeek Harness 已公开架构。*

所以 V4 模型卡里的 Agent 分数，更准确地说，是 V4 在 DeepSeek Harness minimal mode 和那组评测设置下得到的系统结果。它不是一份脱离运行环境、换到任何 Agent 工具里都原样成立的模型单项成绩。

如果 DeepSeek 以后公开这套 Harness，它可能成为外界复现 V4 Agent 能力的一套参考环境。在公开以前，这件事还缺最后一块。

## 第一批内测者，自己也在造 Harness

再回到 8 月 1 日的招募帖，报名门槛就有意思了。

这张公开招募没有面向普通体验者。Tianyi Cui 找的是做过 Agent Harness 相关开源项目的人，还要求附上代表作。

我点开回复区里的 [DeerFlow](https://github.com/bytedance/deer-flow)。它处理长任务，里面有子 Agent、记忆、沙箱和工具。再点 [Kun](https://github.com/KunAgent/Kun)，它让 Agent 进入本地桌面和终端。两份仓库面对的是同一类问题，给出的工程答案并不一样。

这类开发者带进内测的，不只是一个 GitHub 链接。

他们可以拿自己熟悉的任务去跑。任务一长，上下文压缩以后还记不记得最初的要求；终端权限开到真实工作需要的程度，危险命令在哪里被挡住；模型交活以后，测试到底过没过。同一句「任务卡住了」，做过 Harness 的人还能继续往下拆：卡在上下文、工具协议、权限，还是验收。

![开源 Harness 开发者带着各自工程经验进入内测的笨拙涂鸦](assets/doodle-open-source-builders-test.png)

*开源 Harness 作者带着不同工程取舍进入内测。AI 生成的编辑涂鸦，不代表已经建立正式合作关系。*

我因此更愿意把这轮内测理解成外部校准：让做过其他运行框架的人，拿不同任务和不同工程假设来碰 DeepSeek 自己的实现。

这是推测。DeepSeek 没有公布测试协议，也没说反馈会怎样使用。更简单的解释同样成立：新团队需要能报出具体 bug 的测试者，也可能借此继续找人。6 月的招聘帖让后一种解释并不牵强。

但无论目的最后落在哪一边，这批人的价值都不是「比普通用户更懂行」这么空。他们手里有别的实现，可以制造对照。

## DeepSeek 可能在补一套参考环境

DeepSeek 并不缺让模型进入 Agent 工具的入口。

它的官方 [Awesome DeepSeek Agent](https://github.com/deepseek-ai/awesome-deepseek-agent) 仓库已经整理了 Claude Code、Codex、OpenCode、Pi、Hermes、LobeHub 等工具的接入指南。用户想在现成工具里调用 DeepSeek，不必等自研 Harness 发布。

这样看，自研 Harness 目前更确定的价值未必是「再做一个 Claude Code」。它已经承担了一件更靠里的工作：给 DeepSeek 自己的 Agent 评测提供运行环境。

如果这套环境能够稳定复现，DeepSeek 每次更新模型，就能在相对固定的上下文、工具、权限和验收方式下比较结果。失败轨迹也有机会留在自己的系统里，下一轮该改模型还是改框架，会更容易分辨。以后它也可能长成产品，但公开证据还没走到那里。

这条解释把三件事接到了一起：6 月组队，7 月底进入模型卡，8 月初找其他 Harness 开发者内测。它们还不足以证明 DeepSeek 已经定下完整的 Agent 产品战略，却足以说明这支团队不只是在给模型套一个界面。

我最后又回去看 LinearUncle 那句「一小时现搭一个」。

真要报名，我现在不会先让 Fable 5 新建仓库。我会先翻旧任务的日志，找一次真正失败的过程：它在哪里忘了要求，哪条命令本来应该被拦，最后又是谁发现那句「完成」其实没有完成。把这件事写清楚，再附上 GitHub ID。

一个小时新建的仓库还来不及遇到这些。它能交出地址，暂时还交不出反例。

