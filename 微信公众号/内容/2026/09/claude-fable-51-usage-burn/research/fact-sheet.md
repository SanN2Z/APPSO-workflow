# 事实与判断映射

截至：2026-09-02。

| ID | 类型 | 状态 | 可写表述 | 支持 | 禁写 / 限制 |
|---|---|---|---|---|---|
| USER-01 | 作者亲历 | 可写，待截图 | 开始时当前 5 小时用量 17%；约 10 分钟；仍在 Plan Mode；正式实现未开始 | 用户本轮陈述 | 不写成系统日志证明 |
| USER-02 | 作者亲历 | 可写，待截图 | 17% → 90%+ 发生在可见子 Agent 之前；可见子 Agent 启动后才到 100% | 用户最新纠正 | 不用后续子 Agent 解释前段跳变 |
| OFFICIAL-01 | 官方事实 | 已核 | Fable 5.1 于 9 月 1 日发布；API 输入 / 输出 $10 / $50 每 MTok；Cache Read $0.25 | 发布页与模型文档 | 不换算订阅百分比 |
| OFFICIAL-02 | 厂商估算 | 已核 | 典型任务约降本 25%，高度 Agent 化任务最高约 45% | 发布页 | 必须保留厂商估算与适用场景 |
| OFFICIAL-03 | 官方行为 | 已核 | Claude Code 默认 High Effort；Plan Mode 只读但会探索；Plan subagent 可继承主模型 | 发布页、Permission modes、Subagents | 不证明作者本次隐藏 Agent 数 |
| OFFICIAL-04 | 官方监测 | 已核 | 少于 0.01% 的受监测完成中出现绕过限制、夸大用户意图；少于 0.001% 中出现计划以 bypassPermissions 启动 Agent | 系统卡第 94—95 页 | 不外推为普通用户概率；案例操作被产品层拦截 |
| OFFICIAL-05 | 官方建议 | 已核 | 官方模型页建议多数任务先用 Opus 5；Fable 5.1 用于高难推理、长周期 Agent，或 Opus 5 高 Effort 仍不足的任务 | Fable 5.1 overview | 可作为使用建议，不写成产品禁令 |
| OFFICIAL-06 | 官方说明 | 已核 | Max 等套餐中的 Fable 5 / 5.1 会比其他 Claude 模型更快消耗计划用量；帮助页未给出十几分钟耗尽窗口的正常区间 | Fable models on your plan | 不把缺少说明写成官方承认故障 |
| OFFICIAL-07 | 官方功能 | 已核 | `/usage` 可事后拆分 parallel sessions、subagents、cache misses 与 long context 等用量驱动项 | Claude Code What's New / commands | 不等于开工前预算估算或硬止损 |
| OFFICIAL-08 | 官方提示词 | 已核 | Fable 5.1 的公开核心提示词要求在大量工具调用期间提供简短进度更新；如果用户询问消息数量、成本或产品用法，模型应回答不知道并指向帮助中心 | Fable 5.1 system prompts | 只覆盖 claude.ai / iOS / Android，不当作 Claude Code 完整 Agent 提示词 |
| OFFICIAL-09 | 官方配置 | 已核 | Claude Code 2.1.251 起，`CLAUDE_CODE_SUBAGENT_MODEL` 只是默认值，可被 Agent 定义或单次 spawn 覆盖；2.1.257 新增 `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` 才能强制所有子 Agent | Claude Code Changelog | 可解释部分「设为 Opus 却出现 Fable 子 Agent」报告，不证明每例都由此造成 |
| OFFICIAL-10 | 官方修复 | 已核 | Claude Code 2.1.257 修复 Advisor 后台请求整段对话未缓存重发、长截图会话逐轮 Prompt Cache Miss 等问题 | Claude Code Changelog | 属于特定会话条件，不能认定作者短会话命中 |
| OFFICIAL-11 | 官方计费说明 | 已核 | Claude Code 订阅中的 Cache Read 会按较低权重计入用量，但订阅限额不变；25%—45% 降本主要对应按 Token 计费的长会话 | @ClaudeDevs | 不把 API 降本百分比直接套到订阅窗口 |
| OFFICIAL-12 | 官方状态 | 已核 | 9 月 2 日状态页显示 Claude Code Operational，未列 Fable 用量计量事件；当日事件为新购 Usage Credits 延迟到账 | Claude Status | 状态页无事件不等于个别账户无异常 |
| OFFICIAL-13 | 官方 Agent 指南 | 已核 | Fable 5.1 Prompt 指南建议启动子 Agent 的工具立即返回，让主 Agent 在子 Agent 运行时继续工作，并在完成后异步回传结果；官方称平均完成时间降低而质量、Token 与成本相近 | Fable 5.1 Prompt 指南 | 证明官方鼓励并发式 Harness，不证明并发必然增加消耗；指南未提供订阅窗口硬预算 |
| THIRD-01 | 厂商 Harness | 已核 | Devin Medium 单任务 $5.84 → $2.68，超过 95% Token 来自 Cache Read | Devin | 不能外推所有任务 |
| THIRD-02 | 第三方评测 | 已核 | AA Max 单任务 $3.76，高于 Fable 5 的 $3.14；输出约 1.7 倍 | Artificial Analysis | 预发布、特定题集 |
| THIRD-03 | 第三方评测 | 已核 | CodeRabbit 45 个任务中，High 比 Low 更慢，召回率更低 | CodeRabbit | 只对该 Harness 成立 |
| THIRD-04 | 第三方实测 | 已核 | Every 图中，Dan 获得 Fable 5.1 后 Claude Code 日均记录 model steps 从约 910 增至 4688，即 5.15 倍；最高 Effort 下会过度分派 subagents；一名测试者一天运行 18 亿 Token | Every Vibe Check | 预发布访问；model steps 含自动任务与 subagents，不是用户消息数 |
| COMMUNITY-01 | 社区回执 | 可作案例 | Max 5x 17 分钟 0% → 100%，约 20 个 Agent；同时评价质量更好 | Reddit | 用户自述，不算故障率 |
| COMMUNITY-02 | 社区回执 | 可作案例 | Max 20x 4 个 forks、约 20 分钟到顶；PR #122 评论案例 10 个 Subagent、不到 10 分钟到顶 | Reddit | 可见并行工作量大，不等于调度 bug |
| COMMUNITY-03 | 社区回执 | 可作案例 | 一例约 30 分钟打满当前窗口并减少 36% 周额度；另一例 30 分钟减少 20% 周额度，Agent 在形成可用工作前被拦住 | Reddit | 两例账号与任务不同；配置未完整披露 |
| COMMUNITY-04 | 社区回执 | 可作案例 | 城市建造 Demo 约 14 个 Agent、1 小时；29.77 万输入、190 万输出、1.182 亿 Cache Read、600 万 Cache Write | Reddit | 成果为发帖人展示的粗糙版本 |
| COMMUNITY-05 | 社区回执 | 可作案例 | 9 个月代码库审查启动 158 个 Agent、650 万 Token；流程完成但未验证正确性 | Reddit | 不把「完成」写成「通过」 |
| COMMUNITY-06 | X 回执 | 可作案例 | @codebykrishna 称更新后即使使用 Opus 5，Max 5 小时窗口仍明显更快耗尽 | X | 单一自述，不推断系统级原因 |
| COMMUNITY-07 | X 回执 | 可作案例 | @AI_masaou 几小时并行使用约 9 个 5 小时窗口；总体肯定 5.1；同类任务 Low 约 2.5 万、xHigh 约 20 万 Token | X | 任务条件未完全公开 |
| COMMUNITY-08 | X 回执 | 可作案例 | @kimmonismus 称 Fable 5.1 的额度消耗体感比 Fable 5 更差，达到 Session Limit 后自动续跑也未正常工作 | X / 用户提供截图 | 单一自述；不外推自动续跑故障率 |
| COMMUNITY-09 | X 回执 | 可作案例 | @joseph_dibb 称约 10 分钟触及 Session Limit；@ZryMiller 称一条 Prompt 运行 90 分钟烧完窗口且任务未结束 | X | 任务规模与配置不同；后者已有可见成果 |
| COMMUNITY-10 | X 回执 | 可作反例 | @Solzi_Sez 称 Max 20x 连续使用 4 小时仅消耗当前窗口 13%、周额度 3%，写作型处理由 Opus Agent 承担 | X | 单一正面自述；用于显示路由与配置差异 |
| COMMUNITY-11 | X 回执 | 备选 | @AbdoKerdawy 称 Max 20x 约 3 小时后 Fable 周额度接近 77%；@jeeacheff 称两个 5 小时窗口与 400K 最大上下文、常规子 Agent 后接近耗尽一周额度 | X | 均为重任务单一自述，套餐、上下文与 Agent 变量不同；仅作备选 |
| JUDGMENT-01 | 作者判断 | 可写 | 作者前段跳变是 bug 级体验；技术根因未定不影响产品结论 | USER-01/02 | 不写 Anthropic 已确认 bug |
| JUDGMENT-02 | 作者判断 | 可写 | Fable 5.1 的工作单位已经从回答变成可扩张的 Agent 工单，而用量 UI 仍缺少事前预算 | 官方机制、社区回执 | 明确为产品判断 |
| RECOMMEND-01 | 作者建议 | 可写 | 常规任务先用 Opus；Fable 从新会话和 Medium / Low 开始，限制非必要 Subagent，记录 `/usage` 与 `/context` | 官方模型选择与 Effort 指南 | 不是官方故障规避保证 |

## 内部原因树

作者的前段 17% → 90%+ 与后段 90%+ → 100% 必须分开：

1. 后段发生在可见子 Agent 启动后，并行上下文与工具调用可以解释快速补满。
2. 前段发生在可见子 Agent 之前，不能用后段 Agent 数量倒推原因。
3. 前段仍可能包含不可见的规划推理、上下文读取、内置 Plan subagent、用量页面延迟更新或计量异常。
4. 目前没有逐项账单，无法从公开界面在第 3 项中选出根因。

公开正文不展开这棵原因树，只保留「预子 Agent 跳变」与「bug 级体验」。

## 受控复测合同

- 等 5 小时窗口重置后，开全新会话，先保持与第一次相同的模型、Effort、仓库和「只做规划」Prompt。
- 保存发送前、尚无可见 subagent、首次出现 subagent、手动停止后四个时点的 `/usage`、`/context`、Agent 面板和墙钟时间。
- 用量较起点增加 10% 即停止，避免为了复现再次烧完整个窗口。
- 额度允许时，再用 Opus 5 在全新会话跑同一 Prompt 作为最小对照；不为凑完整矩阵继续消耗。
- 将「首次百分比跳变」与「首次可见子 Agent」分别记时；最终正文照实写复现或未复现。
