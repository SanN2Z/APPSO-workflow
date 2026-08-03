# 冻结材料包

访问与冻结时间：2026 年 8 月 2 日（UTC+9）

以下 12 张材料卡经过确定性乱序。卡片位置没有叙事含义。写作者不需要把所有材料写进正文，也不能补充外部事实。

## F09

几个开源项目把 Harness 做成了不同形态：Raven 强调记忆与自我改进；AgentSight 做 Agent 的系统级观测与分析；Maka Agent 是本地优先的桌面助手；LobeHub 提供多 Agent 组织、调度与汇报工作台。它们只能用来说明开源 Harness 开发者的经验类型很不一样，不能用来推断 DeepSeek 的产品形态或入选名单。

## F04

2026 年 6 月 21 日，DeepSeek 团队成员 Tianyi Cui 发帖称，DeepSeek Harness 是新成立的部门，招聘研究员、工程师和产品经理。该帖只能支持「团队正在建设」；不能把 Tianyi Cui 写成负责人，也没有披露具体产品。

## F08

Kun 项目把自己描述为本地优先的 AI Agent 工作区，同时提供桌面 GUI 与终端界面，覆盖编程、写作、设计、研究和自动化。它是公开项目实例，不是 DeepSeek 官方合作方信息。

## F06

DeepSeek 官方 API 文档已有 Codex 接入指南，说明开发者可以把 DeepSeek 模型放进现成的 Codex 工作流。页面与支持范围会更新；这条材料不证明 DeepSeek 自研 Harness 已经公开。

## F01

DeepSeek-V4-Flash-0731 官方模型卡称，7 月 31 日版本强化了 Agent 能力。脚注写明：公开 Code Agent 任务使用 DeepSeek Harness minimal mode、max reasoning effort、temperature 1.0、top_p 0.95；Harness 标为「to be released」。代码、系统提示词、轨迹和完整复现条件没有随模型卡公开。跑分与能力描述均为厂商自报。

## F07

ByteDance 的 DeerFlow 公开仓库把自己描述为开源 Super Agent Harness，编排子 Agent、记忆与沙箱，并提供工具和 Skills。它可说明一类报名者可能熟悉长任务、上下文、工具与执行环境，但不代表它已经参加内测。

## F05

DeepSeek 官方的 awesome-deepseek-agent 仓库收录多种外部 Agent 与 Coding Assistant 的接入指南，包括 Claude Code、Codex、OpenCode、Pi、Hermes 和 LobeHub。它说明 DeepSeek 此前已经走过「让模型接入别人 Harness」这条路线；不构成对这些工具性能或安全性的背书。

## F12

截至冻结时间，列入本材料包的公开来源没有给出 DeepSeek Harness 的正式产品名、界面、发布日期、价格、是否开源、首批人数、具体测试协议，也没有说明它是否只服务 Coding Agent。

## F11

用户提供的 X 截图中，LinearUncle 转发 Tianyi Cui 的邀请，大意是：「稍等，我用 Fable 5 花一个小时现场写一个，我想参加 DeepSeek Harness 内测。」这可以作为评论性开场。由于未定位到该回复的稳定原帖链接，不可把它当作关键事实或使用互动数。

## F02

DeepSeek-V4-Flash-0731 模型卡列出的部分 Agent 结果如下，均为厂商自报：

| 基准 | 0731 | Preview |
|---|---:|---:|
| Terminal Bench 2.1 | 82.7 | 61.8 |
| NL2Repo | 54.2 | 39.4 |
| Cybergym | 76.7 | 38.7 |
| DeepSWE | 54.4 | 7.3 |
| Toolathlon-Verified | 70.3 | 49.7 |
| Agents’ Last Exam | 25.2 | 15.8 |
| AutomationBench Public | 25.1 | 10.8 |
| DSBench-FullStack | 68.7 | 37.0 |
| DSBench-Hard | 59.6 | 25.8 |

其中模型卡把 DSBench-FullStack 与 DSBench-Hard 标为内部集合。数字不等于脱离 Harness 后仍会原样成立，也不是第三方独立复测。

## F03

2026 年 8 月 1 日，Tianyi Cui 公开邀请 Agent Harness 相关开源项目开发者参加 DeepSeek Harness 内测。申请者需附 GitHub ID 和开源代表作，可以回复或私信联系。原帖没有公布产品细节、名额、时间表或选拔结果。

## F10

本材料包把 Harness 当作一个功能位置，而不是某个固定产品：模型负责生成和推理，外层运行框架决定给它哪些上下文、记忆和工具，哪些命令可执行，失败后如何重试，以及完成后怎样验收。不同项目会选择不同组合；这段是根据公开项目共同功能所做的编辑性归纳，不是 DeepSeek 已公开架构。

## 来源

- DeepSeek-V4-Flash-0731 官方模型卡：https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731
- Tianyi Cui 8 月 1 日内测邀请：https://x.com/tianyi/status/2083519855203078320
- Tianyi Cui 6 月 21 日招聘帖：https://x.com/tianyi/status/2068652453797724562
- DeepSeek 官方 Agent 接入仓库：https://github.com/deepseek-ai/awesome-deepseek-agent
- DeepSeek 官方 Codex 接入文档：https://api-docs.deepseek.com/quick_start/agent_integrations/codex/
- DeerFlow：https://github.com/bytedance/deer-flow
- Kun：https://github.com/KunAgent/Kun
- Raven：https://github.com/EverMind-AI/Raven
- AgentSight：https://github.com/eunomia-bpf/agentsight
- Maka Agent：https://github.com/Maka-Agent/maka-agent
- LobeHub：https://github.com/lobehub/lobehub
- 两张 X 截图：用户提供，已在本内容包 assets 目录登记。
