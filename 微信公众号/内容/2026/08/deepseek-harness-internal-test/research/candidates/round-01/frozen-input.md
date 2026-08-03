# 并行候选轮次｜round-01

---
status: frozen
candidate_count: 3
created_on: 2026-08-02
platform: wechat
content_type: analytical_short_feature
t0: "2026-08-02T19:40:03+09:00"
value_frozen_at: "2026-08-02T19:42:00+09:00"
candidate_freeze_deadline: "2026-08-02T20:02:03+09:00"
selection_freeze_deadline: "2026-08-02T20:08:03+09:00"
winner_check_deadline: "2026-08-02T20:18:03+09:00"
text_handoff_deadline: "2026-08-02T20:20:03+09:00"
baseline_candidate: A
---

## 预注册

- 实验：INSIGHT-002 / EXP-001。
- 单稿基线：在生成前按字母顺序预先指定 Candidate A；无论最终质量如何都不改。
- 写作波次：A、B、C 由 3 个隔离 Agent 同时生成，每个 Agent 只写 1 篇。
- 选择：候选冻结哈希后，交给未参与写作的 Agent 匿名选择；可选「一篇都不要」，不得拼稿。
- 当前稿 draft.md 在胜出稿冻结前不得覆盖。

## 共同输入

- 读者：关心 AI 产品和 Agent，但没有做过 Harness 的中文读者。
- 读者问题：为什么 Fable 5 一小时或许能搭出一个 Agent 仓库，却搭不出 DeepSeek 这张内测门票真正需要的东西？
- 核心材料关系：一条「现场搭一个」的玩笑，碰上一条只接受开源 Harness 开发者、GitHub ID 和代表作的定向内测邀请；前一天，待发布的 DeepSeek Harness 已经出现在 V4 的 Code Agent 评测脚注里。
- 公共落点：当生成代码越来越便宜，一个 Agent 项目真正有说服力的部分，可能是它怎样失败、怎样恢复、怎样证明任务真的完成。读者若展示项目或申请内测，应该带失败轨迹和取舍，而不只是一张能运行的首页。
- 稿型：个人可见的热点短特稿，不写行业宣言。
- 篇幅：1800—2400 个中文字符；内容不足可以更短，不得补背景凑长。
- 图片：候选阶段不插图；胜出后再决定是否放已有 X 截图。

## 本轮重新核过的事实

1. DeepSeek-V4-Flash-0731 官方模型卡当前仍写明：公开基准中的 Code Agent 任务使用待发布的 DeepSeek Harness minimal mode 作为 Agent framework，并披露 max reasoning effort、temperature 1.0、top_p 0.95。来源：https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731
2. DeepSeek 官方 awesome-deepseek-agent 仓库当前仍收录 Claude Code、Codex、OpenCode、Pi、Hermes、LobeHub 等多种 Agent 或 Coding Assistant 的接入指南。来源：https://github.com/deepseek-ai/awesome-deepseek-agent
3. 用户提供的 Tianyi Cui 截图写明：如果是 Agent Harness 相关开源项目开发者并希望参加 DeepSeek Harness 内测，可回复或私信，并附 GitHub ID 与开源代表作。正文身份只写「DeepSeek Harness 团队成员」。
4. 用户提供的 LinearUncle 截图中，他开玩笑说稍等，准备让 Fable 5 花一小时现场写一个再来报名。没有定位到 permalink，正文只能转述玩笑，不作逐字引语。

## 可以提出、但必须让读者看出是判断

- 一套跑得起来的新仓库和一套被真实任务折腾过的 Harness，提供给测试团队的信息量不同。
- 有代表作的 Harness 开发者更可能带来上下文丢失、工具失败、权限拦截、重试、验收和安全等具体反例。
- 这次筛选可能是在寻找能提交高质量 bug 的测试者，也可能兼有架构比较或人才发现；公开信息不能确定测试协议。

## 不得补写

- DeepSeek Harness 的产品形态、正式发布日期、价格、是否开源、是否只做 Coding Agent。
- 把 Tianyi Cui 写成负责人；把 LinearUncle 写成已经搭好或已经报名。
- 把自研 Harness 上升为既定生态战略、Agent 战争新标准或 Claude Code／Codex 替代品。
- 把模型卡跑分写成独立复现，或写成 Harness 单独贡献的成绩。
- 虚构作者已经实测、报名、收到邀请或看过测试协议。

## 三个分支种子

| 候选 | 只允许承担的中心 | 建议叙事发动机 |
|---|---|---|
| A｜预注册基线 | 门票不是新仓库，而是项目留下的失败史；读者最后得到一份「怎样展示 Agent 项目」的具体判断 | 玩笑 → 想报名 → 发现代表作门槛 → 拆开失败史 → 回答一小时够不够 |
| B | Fable 5 能压缩写代码的时间，却不能压缩系统在长任务里遇到边角故障的时间；重点解释 Harness 为什么有长尾 | 一小时挑战 → 第一处真实故障 → 故障层层外溢 → 回到时间无法跳过 |
| C | DeepSeek 找同行内测，是把不同 Harness 当成不同的故障探针；重点写这群测试者能暴露什么 | 窄门 → 来者各带一种工程取舍 → 被测对象浮现 → 一份高信号反馈怎样形成 |

每个 Agent 只写自己被分配的中心，不得把另外两条揉进结尾。

## 写作约束

- 前 150 个字内出现「我也想现场搭一个」的真实反应和报名门槛，不从日期、公司介绍或 Harness 定义起笔。
- 允许 2—3 个小标题，但小标题必须在动作推进后出现，不能叫「背景」「什么是 Harness」「影响」。
- 事实边界压在相关句子里，不得单独成章。
- 不摆跑分表，不逐项介绍开源项目，不用宏大主题收口。
- 「不是……而是……」「更重要的是」「关键在于」不得充当段落发动机；能删就删。
- 每一段必须带来动作、故障、解释、取舍或读者可执行的后果。纯总结句删除。
- 结尾回到「一个小时能得到什么、得不到什么」，不要升华到时代、战争、范式或未来。
- 正文后用 HTML 注释列出使用事实、作者判断、保留未知项；注释不算正文。

