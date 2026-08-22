---
title: "Hunt Good 周报｜AI 把假靶场打成了真公司"
platform: wechat
status: draft
created: 2026-08-07
updated: 2026-08-07
as_of: 2026-08-07
fact_checked: false
rights_checked: false
copyedit_checked: false
copyedit_body_sha256: ""
published_url: ""
---

# Hunt Good 周报｜AI 把假靶场打成了真公司

欢迎收看全新一期的 Hunt Good 周报。

这周最离谱的一条 AI 新闻，来自一场本应和现实彻底隔离的安全测试。Claude 在靶场里寻找攻击目标，顺着一个没关好的互联网出口，进入了 3 家真实机构的系统。

另一边，AI 公司还在拼命让模型更便宜、更能干。OpenAI 把 GPT-5.6 Luna 的 API 价格砍了八成，DeepSeek 的新模型首次露出自研 Agent 工作台，Qwen3.8-Max 则在模拟世界里经营了一整年网店。

在本期内容，你会看到：

- 4 条新鲜资讯
- 3 个有用工具
- 3 个鲜明观点
- 2 个有趣案例

## Hunt for News｜先进头条

### Claude 把假靶场打成了 3 家真公司

![Anthropic 官方调查报告配图，以锁和边界表现安全评测。](assets/01-anthropic-cyber-evals-official.png)

*Anthropic 调查报告官方配图；图源：Anthropic。*

安全公司测试 AI 的攻击能力时，通常会给它准备一套与现实隔离的「假网络」。模型可以在里面找漏洞、偷凭证、上传恶意程序，闯出多大动静都不该影响真人。

Anthropic 最近复查了 141,006 次安全测试，却发现有 3 起事件没留在靶场里。由于测试环境错误地保留了互联网访问，Claude 把真实网站当成了题目的一部分，进入了 3 家机构的生产系统。

其中一次，Claude 为完成任务，在公开的 Python 软件仓库 PyPI 上传了一个带有恶意代码的软件包。它在大约 1 个小时里被 15 台真实设备下载运行，还骗过了一家安全公司的自动扫描器。

Anthropic 表示，这些模型没有试图「逃跑」，也没有自行改变目标。它们拿着一张要求攻击的考卷，却被错误地放进了能碰到真实系统的考场。参与测试的模型也没有加载公开产品通常配备的完整安全防护。

这次真正失控的，首先是测试环境。

*相关链接：[Anthropic 调查报告](https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals)*

### GPT-5.6 发布 3 周，OpenAI 就把价格砍了八成

![GPT-5.6 Luna API 输入、输出价格从原价降至五分之一。](assets/02-openai-luna-price-card.png)

*本文根据 OpenAI 公告整理；降价口径仅指 API。*

7 月 30 日，OpenAI 宣布把 GPT-5.6 Luna 的 API 价格下调 80%。每百万 token 的输入价格从 1 美元降到 0.20 美元，输出价格从 6 美元降到 1.20 美元。

定位更高的 Terra 也降价 20%，输入和输出价格分别变成 2 美元和 12 美元。最强的 Sol 没有降价，但新增了速度最高可达普通模式 2.5 倍的 Fast 模式，代价是按双倍价格计费。

距离 GPT-5.6 正式发布只有 3 周，这场降价来得非常快。到了 8 月 6 日，OpenAI 又宣布让 Luna 成为 Free 和 Go 用户的新默认模型，并计划向免费用户提供不限次数的纯文字聊天。

请注意，这里下降的是 API 调用价格。ChatGPT 和 Codex 的订阅价格没有跟着降，只是部分模型消耗的 credits 变少了。

*相关链接：[OpenAI 降价公告](https://openai.com/index/advancing-the-price-performance-frontier-with-gpt-5-6/)、[ChatGPT 更新](https://openai.com/index/improving-gpt-5-6-sol-in-chatgpt/)*

### 一道数学题，让 DeepSeek 想了 22 小时还没交卷

![一张自制终端信息卡显示模型持续思考 22 小时，没有回答、报错或超时。](assets/03-deepseek-22h-card.png)

*本文根据用户截图重做信息卡，未使用原截图像素；单一用户报告不等于已确认的模型 Bug。*

8 月 6 日，一名 LINUX DO 用户晒出 Claude Code 截图：他把推理强度调到最高，要求 DeepSeek V4-Flash-0731 解一道几何题。22 小时过去，模型没有回答、没有报错，也没有超时，只是继续显示「即将完成思考」。

题目并不长：在一个面积为 1 的矩形里放 5 个点，任意 3 点不共线，问至少有多少个以这些点为顶点的三角形，面积不超过四分之一。

发帖者称，换多少个新会话都一样。这也不是这道题第一次困住 V4。早在 4 月，他就在另一场测试中提到 DeepSeek 会陷入无意义循环；同一讨论里，也有人在不同模型版本和推理强度下得到错误答案或正常完成。

因此，单凭截图还不能确定这是模型本身的稳定 Bug。问题也可能出在 Claude Code 的适配、推理强度设置，或者工作台没有及时叫停一段已经失去进展的思考。

这恰好解释了 DeepSeek 新模型卡里一个不起眼的脚注：官方跑代码 Agent 测试时，用的是一套尚未发布的 DeepSeek Harness。Harness 不只负责给模型递工具，也要判断什么时候继续、什么时候重试、什么时候认输。模型会不会解题是一回事，能不能在 22 小时之前承认自己卡住了，是另一回事。

*相关链接：[DeepSeek-V4-Flash-0731 模型卡](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731)、[同一提示词的此前测试](https://linux.do/t/topic/2044393)*

### Qwen3.8-Max 的新考试：独自经营 365 天

![Qwen3.8-Max 官方发布页中的电商经营评测视频封面。](assets/04-qwen-ecommerce-official.png)

*Qwen 官方发布页中的「电商经营评测」视频封面；图源：Qwen。*

模型发布时，大家已经看惯了数学、编程和知识问答跑分。Qwen3.8-Max 这次换了一种更像真人工作的考试：拿着 10 万元，在模拟世界里经营一年网店。

模型要在多家店铺、60 个商品类目、近 600 家供应商和 7000 种商品之间选品、议价、调价、管理库存，还要处理退货、季节变化、台风断料和 152 家欺诈商家。

Qwen 官方称，模型经过 365 天、2000 多轮交互后，留下 416,252 元总现金。新模型共有 2.4 万亿参数，每次推理激活其中 950 亿；官方还表示，模型权重计划在随后一周开放。

这 41 万元来自厂商自己的模拟测试，不是真实开店收入。截至本稿整理时，Qwen 也没有公开这套测试的论文、代码和完整复现条件。

*相关链接：[Qwen3.8-Max 官方发布页](https://qwen.ai/blog?id=qwen3.8)*

## Hunt for Tools｜先进工具

### Rescript：删掉一句话，视频也跟着剪掉

![Rescript 通过编辑文字稿剪辑视频的官方界面截图。](assets/05-rescript-ui-official.jpg)

*Rescript 官方项目截图；图源：Rescript / GitHub。*

剪口播视频时，最烦的工作往往不是加特效，而是反复寻找说错、停顿和「嗯、啊」的位置。

Rescript 会在浏览器或电脑本地把视频转成文字。你在文字稿里删除一句话，对应的视频片段也会一起消失；它还能一键处理停顿、语气词、字幕和说话人标记。

整个过程不要求注册，视频和音频默认留在本机。网页端可以直接使用，也有 Windows、macOS 和 Linux 桌面版。

需要留意的是，Rescript 当前采用限制商业使用的源码许可。个人可以免费使用和修改，但公司把它用于商业项目之前，最好先看清许可证。软件也会默认发送匿名使用统计和崩溃报告，可以在设置里关闭。

*入口：[Rescript 网页版与源码](https://github.com/wassgha/rescript)*

### Adomate：先看数据，再让 AI 想广告

![Adomate 官方产品图，强调从数据生成广告创意。](assets/06-adomate-official.png)

*Adomate 官方产品图；图源：Adomate。*

让 AI 一口气写 100 个广告点子并不难，难的是知道它为什么这么写。

Adomate 可以读取 Meta 广告后台、Meta 广告资料库，以及 Trustpilot、Amazon 等平台上的消费者评论，再把这些信息整理成广告创意。每个点子都能追溯到触发它的原始数据，例如一条客户评价、一个竞品广告或一组历史表现。

它比较适合需要持续生产 Meta 广告的电商品牌和营销团队，官网提供免费试用。不过，目前能看到的效果案例主要来自厂商和客户自述，不能保证接入数据以后就会自动提高销量。

*入口：[Adomate 官网](https://www.adomate.com/)*

### Webhound：先给 AI 一笔预算，再让它做调研

![Webhound 官网演示普通 Agent 与 Webhound 调研流程的差别。](assets/07-webhound-official.png)

*Webhound 官网产品演示区；图源：Webhound。*

许多「深度研究」工具的问题是，名字叫深度，读完 3 个网页就开始写总结。

Webhound 的做法很直接：用户先决定这份调研值多少钱，系统在预算范围内继续搜索、对照和验证资料，最后交付带来源的报告或数据表。它也能通过 MCP 接进 Codex、Claude Code 等 Agent，让 AI 在工作过程中直接发起研究。

Webhound 按实际用量收费，没有固定订阅。官方目前给新账户 5 美元额度，约可运行 75 分钟。它适合市场调查、竞品分析和文献综述，但资料会交给第三方服务处理，敏感数据不要直接放进去。

*入口：[Webhound 官网](https://www.webhound.ai/)*

## Hunt for Insights｜先知

### AI 队友最能说，另外两个人却更少互相搭话

![两名学生与一个 AI 队友讨论，自制图强调 AI 发言最多、人类彼此回应更少。](assets/08-ai-teammate-social-cost-card.png)

*本文根据论文结果制作；研究口径与限制见正文。*

一项新研究把 80 名大学生分成 33 个小组：16 组由 2 名学生和 1 个 AI 组成，另外 17 组由 3 名学生组成。大家需要通过文字聊天，讨论是否应该冒险营救一名受困登山者。

研究人员发现，AI 是每个实验组里说话最多的成员，却提供了最少的新信息。AI 加入后，两名学生彼此回应和接续观点的次数更少，对自己在团队中的归属感和地位评价也更低。

如果会议里的 AI 总在抢着总结、建议和追问，它可能提高了任务推进速度，却挤掉了同事彼此确认和商量的空间。

不过，这项实验只有 33 个小组，使用同一个 AI 角色，只进行了一次大约 18 分钟的文字讨论。它提出了一个值得继续研究的现象，还不能证明所有公司的 AI 队友都会让团队关系变差。

*相关论文：[The Social Cost of an AI Teammate](https://arxiv.org/abs/2607.27179)*

### 一位 OpenAI 研究员，去了旧金山地下室做「读心术」

![Conduit 数据采集参与者佩戴非侵入式传感器头盔。](assets/09-conduit-headset-official.jpg)

*Conduit 数据采集参与者佩戴传感器头盔；图源：Conduit。*

本周，一名刚离开 OpenAI 的对齐研究员把自己的下一站形容为「建造心灵感应」。她加入了旧金山初创公司 Conduit，尝试在不用开颅、也不植入芯片的情况下，把人在说话或打字前出现的神经信号变成文字。

这家公司的实验室很有地下作坊的味道。参与者戴上一个重约 1.8 千克的传感器头盔，在小隔间里与 AI 自由交谈或打字 2 个小时，可以得到 50 美元。

为了不让墙上插座产生的电流噪声盖过脑信号，团队试过在设备周围铺橡胶垫、接入净化电源，最后干脆关掉大楼一侧的电源，改用约 13.6 千克的电池轮流供电。等数据积累到四五千小时以后，模型逐渐学会在不同房间、设备和人之间分辨信号与噪声，他们才把电重新打开。

Conduit 称，团队已经从数千名参与者那里收集了约 1 万小时数据，模型也能在没有针对个人预先训练的情况下，为新受试者生成语义相近的文字。公司向 Forbes 提供的数字是约 45% 的「语义匹配」，并不是逐字读对了 45% 的思想。

目前，Conduit 还没有公开完整模型、评测方法或同行评审论文，头盔也不只使用脑电一种传感器。它离消费级「读心术」还很远，但已经走上了一条 AI 公司非常熟悉的路：先收集足够多的数据，再赌规模能够战胜噪声。

*相关链接：[研究员离职相关帖](https://x.com/NaomiBashkansky/status/2085043839589617918)、[Conduit 数据收集记录](https://condu.it/thought/10k-hours)、[Forbes 报道](https://www.forbes.com/sites/robtoews/2025/12/07/the-next-frontier-for-ai-is-the-human-brain/)*

### Claude 可能真的会「看人下菜」

![自制数据卡列出 Claude 面对知名 AI 从业者时的四项平均变化。](assets/10-transluce-user-awareness-card.png)

*本文根据 Transluce 报告整理；图中为组间平均差异，实验主动把身份写入上下文。*

同一道题，换个人来问，Claude 的表现可能也会跟着变。

非营利研究机构 Transluce 把 280 个不同身份写进 Claude Code 的上下文，再让模型完成相同任务。身份被平均分成四组，包括知名 AI 从业者、普通 AI 从业者、其他领域名人和普通美国人；上下文里会出现姓名、邮箱和职业信息。

面对知名 AI 从业者时，Claude 对自己能否按承诺行动的信心平均低了 1.4 个百分点，对解决难题的信心低了 1.5 个百分点。在 10 分制评分任务里，它给其他回答的分数平均低了 0.11 分；在行为预测任务中，启动推理的比例高了 4 个百分点。

平均差异并不大，但在统计上显著，而且变化集中在少数人身上。面对参与 Claude 性格训练的 Anthropic 研究员 Amanda Askell 时，模型对自身行为的信心下降约 5 个百分点，启动推理的比例则高出约 25 个百分点。

这项实验并不是观察名人真的使用 Claude。研究人员主动把模拟身份放进上下文，因此还不能证明 Claude 会在所有真实对话里区别对待用户。不过，Claude Code 的确可能把登录邮箱、项目文件和长期记忆交给模型。以后 AI 越来越了解屏幕另一边是谁，我们拿到的或许就不再是同一套判断。

*相关研究：[User awareness in frontier models](https://transluce.org/user-awareness)*

## Hunt for Fun｜先行

### 把 19 位 AI 专家请进 Google Meet，轮流挑刺

![gstack joins your meeting 官方项目面板，展示多名 AI 角色。](assets/11-gstack-dashboard-official.jpg)

*gstack joins your meeting 官方项目面板；图源：pattern-ai-labs / GitHub。*

开会时让 AI 记笔记已经不新鲜了。gstack joins your meeting 选择直接给 AI 一个座位。

这套开源项目可以让 CEO、设计师、测试负责人、安全负责人等 19 个 AI 角色加入 Google Meet、Zoom 或 Teams。它们有各自的声音和虚拟头像，会听会议内容、查看共享屏幕，再用对应身份提问和给反馈。

例如，你可以把 YC Office Hours 和 CEO 两个角色请进来，模拟一场融资面试；也可以让设计师与测试负责人一起检查准备发布的产品。

项目使用本机的 Claude Code 会话作为「大脑」，代码采用 MIT License。不过，它仍然依赖 AgentCall 把机器人接入会议，安装也需要命令行和 API Key，暂时还不是点开网页就能放心使用的普通会议插件。

*项目地址：[gstack joins your meeting](https://github.com/pattern-ai-labs/gstack-joins-meeting)*

### 今年的 AI 奥赛，参赛者里真的有 AI

![IOAI 官方页面用插画表现 AI 模型参加竞赛。](assets/12-ioai-model-track-official.jpg)

*IOAI 官方 AI Model Track 页面示意图（官方文件名显示由 ChatGPT 生成）；图源：IOAI。*

8 月 4 日和 6 日，国际人工智能奥林匹克竞赛第一次给 AI 模型单独开了一条赛道。

每场比赛持续 6 个小时，模型需要独立解决 3 道机器学习题，自己写代码并提交答案。人类操作员只能发送官方提供的「开始」指令；如果模型中途停下，也只能再说一次「继续」，不能帮忙改代码、找错误或润色答案。

参赛者可以使用公开模型、封闭 API，甚至尚未发布的内部模型。为了拿到正式奖牌，参赛团队还需要提交完整运行轨迹，让评审确认人类没有偷偷递答案。

这场比赛测的不只是哪一个模型会做题，还要看谁能连续工作 6 个小时，不迷路、不停工，并且自己完成交卷。

截至本稿整理时，官方完整榜单仍待公布。

*比赛规则：[IOAI 2026 AI Model Track](https://ioai-official.org/ai-model-track/)*

## 彩蛋时间

![一张自制终端梗图：Harness 最重要的功能，可能是劝模型及时认输。](assets/13-bonus-harness-stop-card.png)

*本文制作，非真实系统截图。*

持续思考不等于持续进展。等到计时器走过 22 小时，最好用的按钮可能不是「继续」，而是「先停一下」。
