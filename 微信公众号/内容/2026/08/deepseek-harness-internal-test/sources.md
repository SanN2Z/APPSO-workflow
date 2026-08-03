# 来源

访问基准：2026 年 8 月 2 日 19:52（UTC+9）。round-01 胜出后已再次重开 DeepSeek 官方模型卡与官方 Agent 接入仓库；X 正文仍以用户提供截图和公开 permalink 交叉核对。涉及产品状态的页面在进入 ready 前仍须再次核查。

| 来源 | URL/路径 | 类型 | 访问日期 | 支持表述 | 备注 |
|---|---|---|---|---|---|
| DeepSeek-V4-Flash-0731 官方模型卡 | https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731 | P0 / 厂商一手 | 2026-08-02 19:41+09:00 | 7 月 31 日版本强化 Agent 能力；公开 Code Agent 任务使用 DeepSeek Harness minimal mode、max reasoning effort、temperature 1.0、top_p 0.95 评测；Harness 标记为 to be released | round-01 胜出后已重开；跑分、方法与内部数据集均为厂商自报；Harness 代码、轨迹、系统提示词和完整复现条件未公开 |
| Tianyi Cui 招募开源 Harness 开发者参加内测 | https://x.com/tianyi/status/2083519855203078320 | P0 / 团队成员公开帖 | 2026-08-02 | 参加者需是 Agent Harness 相关开源项目开发者，并附 GitHub ID 与代表作 | 原帖可访问性受 X 限制；正文用用户截图与公开页面交叉核对，不引用持续变化的互动数 |
| Tianyi Cui 招聘帖 | https://x.com/tianyi/status/2068652453797724562 | P0 / 团队成员公开帖 | 2026-08-02 | DeepSeek Harness 是新成立的部门，公开招聘研究员、工程师和产品经理 | 只能支持团队建设，不能据此推出具体产品形态；Tianyi Cui 不写成团队负责人 |
| DeepSeek 招聘站 | https://talent.deepseek.com/ | P0 / 官方招聘页 | 2026-08-02 | 列有 Agent Harness 团队和 Agent Infra 研发工程师相关岗位 | 岗位会变动；进入 fact_checked 前重开 |
| Awesome DeepSeek Agent | https://github.com/deepseek-ai/awesome-deepseek-agent | P0 / DeepSeek 官方仓库 | 2026-08-02 | DeepSeek 为 Claude Code、Codex、OpenCode、Pi、Hermes、LobeHub 等多种 Agent 与 Coding Assistant 整理接入指南 | 证明外部工具接入路线，不证明 DeepSeek 对第三方工具的性能或安全背书 |
| DeepSeek Codex 接入文档 | https://api-docs.deepseek.com/quick_start/agent_integrations/codex/ | P0 / 官方文档 | 2026-08-02 | DeepSeek 模型可接入现有 Codex 工作流 | 页面与支持模型会更新；正文不写易过期的具体支持范围 |
| ByteDance DeerFlow | https://github.com/bytedance/deer-flow | P1 / 项目原始仓库 | 2026-08-02 | 开源 Super Agent Harness，涉及子 Agent、记忆、沙箱、工具和 Skills | 用于说明报名项目类型，不作为 DeepSeek 产品定位证据 |
| Kun | https://github.com/KunAgent/Kun | P1 / 项目原始仓库 | 2026-08-02 | 本地优先的桌面 GUI 与终端 Agent 工作区 | 同上 |
| Raven | https://github.com/EverMind-AI/Raven | P1 / 项目原始仓库 | 2026-08-02 | 以记忆与自我改进为重点的 Agent Harness | 同上 |
| AgentSight | https://github.com/eunomia-bpf/agentsight | P1 / 项目原始仓库 | 2026-08-02 | 面向 Agent 的系统级观测与分析工具 | 同上 |
| Maka Agent | https://github.com/Maka-Agent/maka-agent | P1 / 项目原始仓库 | 2026-08-02 | 本地优先的桌面 AI 助手 | 同上 |
| LobeHub | https://github.com/lobehub/lobehub | P1 / 项目原始仓库 | 2026-08-02 | 面向多 Agent 组织、调度与汇报的工作台 | 同上 |
| 用户提供的两张 X 截图 | 本轮对话附件；已持久化到 `assets/` 并登记于 `asset-manifest.yml` | 现场截图 / 研究材料 | 2026-08-02 | 主招募帖原文，以及 LinearUncle 准备用 Fable 5「一小时现写一个」的玩笑 | 组合截图进入正文并作评论性引用；LinearUncle 原帖链接未定位，因此正文标明「大意」，不把玩笑作为关键事实 |
| 本轮选题卡 | ../../../../选题/2026-08-02-DeepSeek-Harness-内测选题.md | 内部研究 | 2026-08-02 | 时间线、推测边界、标题与叙事节拍 | 不是公开证据，正文事实仍回到一手来源 |

## 证据分层

- 已核事实：模型卡脚注、内测对象与报名要求、6 月团队招募、官方外部工具接入清单、各项目自述定位。
- 厂商自报：V4-Flash-0731 的全部跑分，以及 DeepSeek 自己对 Agent 能力提升的描述。
- 作者判断：DeepSeek 正在补 Agent 系统层；自己的 Harness 可能承担参考实现、评测基线和反馈入口。
- 推测：定向内测可能兼具压力测试、兼容性摸底和生态观察。另一种解释是寻找高质量测试者或人才。
- 未知：产品名、界面、发布日期、价格、是否开源、首批测试范围、是否只做 Coding Agent。
