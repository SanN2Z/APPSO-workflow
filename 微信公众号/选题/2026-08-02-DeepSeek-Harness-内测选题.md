---
title: DeepSeek Harness 内测选题：新东西还没发布，跑分已经先用上了
platform: wechat
type: topic_proposal
status: research
created: 2026-08-02
updated: 2026-08-02
as_of: 2026-08-02 13:10+09:00
confidentiality: internal
---

# DeepSeek Harness 内测选题

## 先说结论

**建议开稿，优先级 24 / 25。**

这不是一篇「DeepSeek 又要发新品」的传闻稿，而是一篇借内测招募解释 Agent 竞争正在怎样换战场的热点分析稿。

最值得写的反常点是：DeepSeek Harness 还没有正式发布，却已经被写进 DeepSeek-V4-Flash-0731 的官方模型卡，承担了公开 Code Agent 跑分；模型卡上线次日，团队成员 Tianyi Cui 又只向「Agent Harness 相关开源项目开发者」招募内测，并要求附 GitHub ID 与代表作。

这两步连起来，比单独一张内测截图更有信息量：DeepSeek 要测试的可能不只是一款尚未露面的工具，也是在测试「模型怎样通过 Harness 才能稳定干活」这套产品与评测方法。

## 一句话选题

**DeepSeek 为什么不找普通用户，而要让一群开源 Harness 作者先试一个尚未发布、却已经替 V4 跑过分的东西？**

## 最小 Brief

- **读者**：关心 AI 产品与行业竞争、但不熟悉 Agent 工程的中文读者。
- **希望读完记住**：Agent 的真实表现不只由模型决定；DeepSeek 正在补模型与任务之间的系统层。
- **时效窗口**：以 Harness 正式发布为截止点，适合在未来 24–48 小时内完成；一旦产品发布，稿型立即切换。
- **不写**：未经证实的发布日期、产品名、开源方式、价格和「取代 Claude Code」结论，也不把它写成使用教程或实测。

## 建议主标题

《DeepSeek 的新东西还没发布，跑分已经先用上了》

备选：

- 《DeepSeek 发了一条内测帖，开源 Agent 作者把 GitHub 仓库搬来了》
- 《有人准备一小时现写一个，DeepSeek 为什么突然找 Harness 作者内测》
- 《模型只是大脑，DeepSeek 开始争夺 Agent 的身体》
- 《DeepSeek 不只想卖模型，它开始补 Agent 的最后一公里》

其中「一小时现写一个」来自用户提供的 X 截图，只适合做开场趣闻。发稿前若仍找不到可访问的原帖链接，不把它放进主标题，也不作为关键事实。

## 故事开场

8 月 1 日晚，Tianyi Cui 在 X 上发了一条很短的招募：如果你开发过开源 Agent Harness，想参加 DeepSeek Harness 内测，就留下 GitHub ID 和代表作。

这不像普通产品内测，没有问手机型号，也没有抽邀请码。它更像一场临时搭起的开源项目路演。

回复区很快排起队来。有人带着通用 Agent，有人带着桌面助手，有人做记忆，有人做沙箱、虚拟文件系统和安全观测；字节跳动的 DeerFlow，以及 Kun、Maka、Raven、LobeHub 等项目或其开发者也留下了仓库。还有人半开玩笑地表示，稍等，先让 Fable 5 花一个小时现场写一个再来报名。

笑点到这里就够了。真正值得追问的是：DeepSeek 为什么要找的偏偏是这群人？

## 三幕时间线

### 第一幕：一个新团队公开说自己缺人

6 月 21 日，Tianyi Cui 在 X 上称 DeepSeek Harness 是「新成立的部门」，目标远、工作重，并公开招募 Harness 研究员、工程师和产品经理。DeepSeek 当前招聘站也仍列有「Agent Harness 团队」和「Agent Infra 研发工程师」。

这只能证明 DeepSeek 正在正式组建相关团队，不能据此推断具体产品形态。

### 第二幕：还没发布的 Harness，先出现在跑分脚注里

7 月 31 日，DeepSeek 发布 DeepSeek-V4-Flash-0731。官方模型卡给出多项 Agent 基准成绩，同时特别说明：其中公开 Code Agent 任务使用 DeepSeek Harness 的 minimal mode 评测，并明确标注「to be released」。

这意味着 Harness 至少已经能在 DeepSeek 内部稳定跑评测。它不是一张仍停留在招聘 JD 里的路线图，而是一套实际影响模型成绩的运行框架。

但这些成绩仍是 DeepSeek 自报。官方没有公开 Harness 代码、完整轨迹、系统提示词和全部复现实验设置，文章不能把它们写成独立验证结果。

### 第三幕：模型卡上线次日，开源作者被请进内测

8 月 1 日，Tianyi Cui 定向招募开源 Harness 开发者。报名项目横跨长任务编排、桌面与移动端 Agent、记忆、沙箱、文件系统、观测和安全等不同方向。

这组测试者的价值不只是「懂技术」。他们各自已经做过一套关于上下文、工具、权限、失败恢复和用户交互的选择，能迅速指出另一套 Harness 在真实工程里哪里难用、哪里不兼容、哪里容易失控。

## 给普通读者的最小解释

可以把模型理解成大脑，把 Harness 理解成大脑周围那套身体和工作台。

它决定模型能看到哪些上下文，能不能读写文件、调用终端和联网工具，失败后怎样重试，什么时候压缩记忆，完成后由谁验收，以及危险动作是否需要拦截。同一个模型装进不同 Harness，最后能不能把工作做完，可能是两回事。

所以 DeepSeek 在模型卡里注明 Harness，不是补一个无关紧要的软件名。它实际上承认：Agent 跑分测到的是「模型 + 运行框架」组成的系统，而不只是模型权重。

## 核心判断

**DeepSeek 正在补从「模型供应商」到「Agent 系统供应商」的最后一公里。**

它目前表现出两条并行路线：一边让 V4 接入 Codex、Claude Code、OpenCode、OpenClaw、Pi、Hermes 等现有工具；另一边开发并准备发布自己的 Harness。前者让模型尽可能进入别人的工作台，后者则让 DeepSeek 有机会定义「怎样使用和评测 DeepSeek 模型才算正确」。

如果这条判断成立，DeepSeek Harness 的意义就不只是一款 Claude Code 同类产品。它还可能成为 DeepSeek 模型的参考实现、反馈入口和评测基线。

以上是根据公开动作形成的编辑判断，不是 DeepSeek 已公布的产品定位。

## 可以写的三层推测

### 高置信：公开发布已经在计划中

依据是官方模型卡直接写了「to be released」。但没有发布日期，不能写成「马上发布」「本周发布」。

### 中置信：第一版大概率从 Coding Agent 或工程任务切入

依据是 Harness 已被用于 Code Agent 基准，官方近期也重点适配 Codex、Claude Code 等开发工具，内测报名项目里有大量 Coding Agent 与工程基础设施。

反证是报名范围并不只包含代码工具，DeepSeek 招聘站也使用更宽泛的「Agent Harness」表述。因此可以写「Coding-first」，不能写成已经确认的「DeepSeek Code」。

### 中置信：这次定向内测更像外部验收组与生态摸底

要求 GitHub ID 和开源代表作，说明 DeepSeek 在筛选能读代码、比较架构并给出工程反馈的人。项目类型又覆盖记忆、沙箱、端侧、观测和安全，适合做跨架构压力测试与兼容性检查。

另一种朴素解释是：团队只是缺少高质量测试者或借机招人。正文应保留这个反解释，不能把一次招募直接写成已经成形的生态战略。

## 现在不能写的推测

- 不能写 DeepSeek Harness 将开源。招募对象来自开源项目，不等于被测产品也会开源。
- 不能写它一定免费、一定是桌面端、一定只做代码，也不能写已有正式产品名。
- 不能写它会取代 Claude Code、Codex 或 OpenCode；目前没有公开实测。
- 不能把 V4-Flash 的 Agent 跑分全部归功于 Harness，也不能把厂商自报成绩当成独立复现。
- 不能把内测理解为 DeepSeek 要收购、投资或抄用报名项目，没有证据。
- 不能根据这条时间线推断 V4-Pro 与 Harness 会同日发布。

## 建议叙事节拍

1. **开门**：从「只收 GitHub 仓库的内测」切入，快速带出有人想现场现写一个的玩笑。
2. **排队**：用几个不同类型的报名项目做蒙太奇，不按项目逐一介绍，只让读者看见这群测试者各自带着不同零件而来。
3. **倒带**：回到前一天的 V4-Flash 模型卡，揭示这个未发布 Harness 已经替模型跑过分。
4. **解释**：用「大脑 + 身体和工作台」解释 Harness 为什么能改变 Agent 表现。
5. **动机**：提出三种可能——外部压力测试、兼容性与反馈、建立自己的参考实现——并给每种推测配证据与反解释。
6. **升维**：写 DeepSeek 一边适配别人的 Harness，一边造自己的，说明它争夺的不是单一入口，而是模型到任务之间的控制层。
7. **收口**：回到回复区。大家带来的并不只是仓库，而是一张清单：模型要真正干活，还缺记忆、工具、沙箱、权限、验证和失败恢复。这张清单，正是 Agent 战争的新战场。

## 推荐结尾

过去看一家公司有没有追上前沿模型，大家盯参数、价格和排行榜。现在还要多问一句：它给这颗大脑配了什么身体，又允许谁来握方向盘？

DeepSeek 那条只有两句话的内测帖，暂时没有回答 Harness 长什么样。可回复区已经先替它画出了一圈轮廓：记忆、工具、沙箱、文件、验证、安全，以及一群想把这些零件重新接一遍的人。

## 证据底座

### P0｜一手来源

- [DeepSeek-V4-Flash-0731 官方模型卡](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731)：支持「公开 Code Agent 任务使用 DeepSeek Harness minimal mode 评测；Harness 待发布」及具体评测设置。限制：成绩与方法均为厂商自报，Harness 尚未公开复现。
- [Tianyi Cui：招募开源 Harness 开发者参加内测](https://x.com/tianyi/status/2083519855203078320)：支持招募对象、GitHub ID 与代表作要求。2026 年 8 月 2 日复核时，第三方公开接口显示约 35.6 万次查看、580 条回复；互动数持续变化，只用于热度判断。
- [Tianyi Cui：DeepSeek Harness 团队招人](https://x.com/tianyi/status/2068652453797724562)：支持「新成立的部门」及研究员、工程师、产品经理招聘。属于团队成员公开表述。
- [DeepSeek 招聘站](https://talent.deepseek.com/)：当前列有「Agent Harness 团队」与「Agent Infra 研发工程师」。岗位列表会变化。
- [DeepSeek 官方 Codex 接入文档](https://api-docs.deepseek.com/quick_start/agent_integrations/codex/)：支持 V4-Flash 已原生接入 Responses API / Codex，以及 DeepSeek 正在适配外部 Agent 工具。
- [Awesome DeepSeek Agent](https://github.com/deepseek-ai/awesome-deepseek-agent)：支持 DeepSeek 正在为多种既有 Agent 与 Coding Assistant 建立接入指南。

### P1｜报名项目原始仓库，用于说明测试者类型

- [ByteDance DeerFlow](https://github.com/bytedance/deer-flow)：长任务编排、子 Agent、记忆、沙箱、Skills。
- [Kun](https://github.com/KunAgent/Kun)：本地优先的桌面与终端 Agent 工作区。
- [Maka Agent](https://github.com/Maka-Agent/maka-agent)：本地优先桌面助手。
- [Raven](https://github.com/EverMind-AI/Raven)：记忆优先、自改进的 Agent Harness。
- [LobeHub](https://github.com/lobehub/lobehub)：多 Agent 组织与调度。
- [AgentSight](https://github.com/eunomia-bpf/agentsight)：Agent 的系统级观测与安全基础设施。

### 截图边界

- 用户提供的截图可证明当时页面上出现过「一小时现场写一个」的玩笑性表述，但本轮未定位到仍可访问的对应 X 原帖。
- 正式发稿若要使用截图，需要将原图纳入内容包，登记来源、权利人、修改、允许平台与权利状态；找不到原帖链接时不把截图当作关键证据。

## 发稿前还需补的四项核查

1. 重开 DeepSeek 模型卡、招聘页和 Tianyi Cui 原帖，检查 Harness 是否已经正式发布；若已发布，整篇改成「发布 + 实测」，不再以猜测为主。
2. 确认首批内测是否有公开邀请、NDA、系统要求、产品截图或反馈；没有就明确写「尚未公开」。
3. 从报名回复中只选 3–5 个有可核仓库的代表案例，逐一核对账号与项目关系，不把普通转发者写成项目作者。
4. 如引用跑分，补对应基准官方说明、比较模型的 Harness 与设置，避免把不同框架下的数字直接横比。

## 选题评分

| 维度 | 分数 | 理由 |
|---|---:|---|
| 时效 | 5 / 5 | 模型卡与内测帖相隔一天，仍在发酵 |
| 故事张力 | 5 / 5 | 未发布却已跑分；只向开源作者开门 |
| 普通读者价值 | 4 / 5 | 可借具体场景讲清 Harness，但术语仍需翻译 |
| 账号匹配 | 5 / 5 | AI 产品、开源生态、跑分与产业判断交叉 |
| 证据就绪 | 5 / 5 | 关键时间线已有一手来源，产品细节未知但可作为边界 |

**总分：24 / 25。建议今天进入判断共创；如果只做快稿，可按 2500–3500 字完成。**
