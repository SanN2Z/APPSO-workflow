# 来源

访问日期：2026-09-02。公开正文只保留必要归属；证据强弱、替代解释和发布前重开项留在本文件。

## 作者与上一篇

| 来源 | URL / 路径 | 支持内容 | 使用限制 |
|---|---|---|---|
| 用户本轮补充 | 当前对话 | 17% → 90%+ 发生在可见子 Agent 之前；随后子 Agent 启动才到 100%；约 10 分钟、Plan Mode、正式实现未开始 | 作者亲历，尚未附个人用量与 Agent 轨迹截图 |
| APPSO 上一篇 Fable 5.1 发布稿 | https://mp.weixin.qq.com/s/SUxNsCPkhUjFQuT9Uz0iSg | 确定本稿不再重复 Benchmark、价格、EFS、Mythos、反蒸馏和水印 | 作为选题边界，不用它证明本稿新增事实 |

## 官方来源

| 来源 | URL / 路径 | 支持内容 | 使用限制 |
|---|---|---|---|
| Anthropic 发布页 | https://www.anthropic.com/claude-fable-and-mythos-5-1 | 2026-09-01 发布；API 单价；Cache Read 降价；典型任务与 Agent 任务降本估算；默认 Effort | 能力与降本为厂商口径 |
| Fable 5.1 overview | https://platform.claude.com/docs/en/models/fable-5-1/overview | 1M 上下文、128K 输出、$10 / $50、$0.25 Cache Read；多数任务先用 Opus 5 | API 口径不能直接换算订阅百分比 |
| Fable 5.1 Prompt 指南 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1 | Effort 控制质量、时延和成本；官方建议启动子 Agent 的工具立即返回，让主 Agent 与子 Agent 并行工作，结果稍后回传；官方称可在质量、Token 与成本相近时缩短平均完成时间 | 面向集成与 Agent 设计；证明并发设计取向，不证明并行必然增加总消耗，也没有提供订阅窗口的总预算闸门 |
| Fable 5.1 核心系统提示词 | https://platform.claude.com/docs/en/release-notes/system-prompts/claude-fable-5-1 | 9 月 1 日公开版本：大量工具调用时可每隔几次给简短更新；用户询问消息数量、成本或产品用法时，模型应回答不知道并指向帮助中心 | 页面明确只覆盖 claude.ai、iOS 与 Android 的核心提示词，不是 Claude Code 完整 Agent 指令 |
| Claude Code Permission modes | https://code.claude.com/docs/en/permission-modes | Plan Mode 可读文件、跑探索命令、生成方案，但不写源文件 | 只读不等于低计算量 |
| Claude Code Subagents | https://code.claude.com/docs/en/subagents | Plan Mode 可委派 Plan subagent；子 Agent 有模型与 Effort 设置；多个 Agent 消耗额外上下文 | 不证明作者本次隐藏调用了多少 Agent |
| Claude Code Costs | https://code.claude.com/docs/en/costs | 模型、上下文、Effort、Thinking、并行 Agent 影响用量 | 官方未公开订阅百分比的逐项账单公式 |
| Claude Code Changelog 2.1.251 / 2.1.257 | https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md#21257 | 2.1.251 将 `CLAUDE_CODE_SUBAGENT_MODEL` 明确为默认值，允许 Agent 定义或单次 spawn 覆盖；2.1.257 新增 `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`；同版修复 Advisor 后台请求整段未缓存重发、长截图会话逐轮 Cache Miss 等问题 | 官方变更日志可证明配置语义和特定缓存 Bug，不能直接认定作者会话命中这些 Bug |
| @ClaudeDevs 缓存计入说明 | https://x.com/ClaudeDevs/status/2094851235694497836 | Claude Code 订阅中的 Cache Read 按较低权重计入用量，但订阅限额不变；按 API Token 计费的长会话可降低约 25%—45% | 官方开发者账号说明；不提供订阅百分比换算公式 |
| Fable models on your plan | https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan | 9 月 2 日更新；Fable 5 与 5.1 在套餐中处理方式相同，会比其他 Claude 模型更快消耗计划用量；Max 等套餐最多可将周额度的 50% 用于 Fable | 未定义十几分钟耗尽是否正常 |
| Claude Status | https://status.claude.com/ | 9 月 2 日查询时 Claude Code Operational，未列 Fable 用量计量事件；当日列出的事件是新购 Usage Credits 延迟到账 | 状态页未列报不等于个别账户无异常；Usage Credits 事件与订阅 5 小时窗口不是同一问题 |
| @ClaudeDevs 限额重置公告镜像 | https://www30.twstalker.com/ClaudeDevs | 官方账号原文称 Fable 5.1 发布时为所有用户重置 5 小时和周度限额 | 镜像用于恢复 X 原文；互动数字随时间变化 |
| Fable 5.1 / Mythos 5.1 System Card | https://www-cdn.anthropic.com/0339e6a7c5c7b87f5c07798616dc32c215d14235/Claude%20Fable%205.1%20%26%20Claude%20Mythos%205.1%20System%20Card.pdf | 第 94—95 页：少于 0.01% 的受监测完成中出现绕过限制、夸大用户意图；少于 0.001% 中出现计划以 bypassPermissions 启动 Agent | 监测样本与产品防护条件由 Anthropic 定义；不能外推总体发生率 |
| 系统卡本地原件 | `research/source-assets/claude-fable-5-1-system-card.pdf` | 配图与逐页核验真源 | 原 PDF 不直接发布；正文使用第 95 页渲染图 |

## 独立与厂商实测

| 来源 | URL | 支持内容 | 使用限制 |
|---|---|---|---|
| Devin / Cognition | https://devin.ai/blog/fable-5-1 | Medium 任务成本 $5.84 → $2.68；该 Harness 超过 95% Token 为 Cache Read | Devin 自家 Harness，属于产品厂商实测 |
| Artificial Analysis | https://artificialanalysis.ai/articles/claude-fable-5-1/ | 最高分 66；Max 单任务 $3.76 vs Fable 5 的 $3.14；输出约 1.7 倍 | 预发布评测、特定题集与最大 Effort |
| CodeRabbit | https://www.coderabbit.ai/blog/fable-5-1-model-review | 45 个代码审查任务；Low 18:38 / 61.0%，High 21:36 / 57.1% | 代码审查专用 Harness；跨版本对照有流水线差异 |
| Cursor Value Calculator | https://cursor.com/en-US/cost-savings | Fable 5.1 不同 Effort 的成本、Token 和得分差异 | 作为备选交叉验证，正文未直接采用 |
| Box 首轮企业测试 | https://blog.box.com/first-look-claude-fable-51-improves-accuracy-latency-and-efficiency-complex-enterprise-work | 文档与企业任务中准确率、速度与 Token 效率提升 | 合作伙伴自有评测，正文未直接采用 |
| Every Vibe Check | https://every.to/vibe-check/fable-5-1-vibe-check | Dan 获得 Fable 5.1 访问后，Claude Code 日均记录 model steps 从约 910 增至 4688，即 5.15 倍；最高 Effort 下持续分派 subagents、停止不及时；一名测试者单日运行 18 亿 Token | Anthropic 提供预发布访问但未参与成稿；日志图中的 model steps 包含批处理、subagents、自动任务与安全检查，不等于用户手动消息数 |

## 首日社区回执

社区材料只作为具体用户案例，不计算故障率；互动量是收集时可见快照。

| 案例 | URL | 公开回执 | 备注 |
|---|---|---|---|
| 17 分钟 0% → 100% | https://www.reddit.com/r/Anthropic/comments/1w4li6a/usage_reset_with_fable_51/ | Max 5x；动态工作流；约 20 个 Agent；同时肯定简洁度与一次通过率 | 高消耗与正面质量并存 |
| 4 个 Fable forks | https://www.reddit.com/r/ClaudeCode/comments/1w4rhsw/be_careful_fable_51_just_decided_to_spawn_4/ | Max 20x；约 20 分钟到顶；评论用户的 PR #122 触发 10 个 Subagent，不到 10 分钟到顶 | 可见 Agent 能解释该用户的一部分消耗，不能解释作者的预 Agent 跳变 |
| 30 分钟与周额度 -36% | https://www.reddit.com/r/Claude_reports/comments/1w4pyb2/rclaudeai_max_20x_usage_burn_after_30_mins_fable/ | Max 20x；当前窗口基本耗尽；周额度减少 36% | 原帖媒体 URL失效，正文使用项目整理资料卡，不伪造截图 |
| 1.5 小时用量比例 | https://www.reddit.com/r/ClaudeCode/comments/1w4mn5e/how_does_this_usage_math_even_make_sense/ | 当前窗口 100%；周度全模型 22%；Fable 36% | 长会话、缓存和切换模型等变量未控制 |
| 一个 Prompt → 约 14 个 Agent | https://www.reddit.com/r/ClaudeCode/comments/1w4qziv/ok_this_is_wild_used_claude_fable_51_and_said/ | 约 1 小时；29.77 万输入、190 万输出、1.182 亿 Cache Read、600 万 Cache Write；有可玩粗糙版本 | 正面案例；成果仍需独立验证 |
| 158 个 Agent / 650 万 Token | https://www.reddit.com/r/ClaudeCoding/comments/1w4u4q3/claude_fable_51_reviewed_my_9month_ai3d_codebase/ | 9 个月 AI / 3D 代码库审查；流程完成；作者称验证尚未完成 | 低互动但新鲜具体，适合作为规模回执 |
| 发布讨论 Hub | https://www.reddit.com/r/ClaudeAI/comments/1w4qgue/fable_51_and_mythos_51_release_discussion_hub/ | 有用户称相近任务从 14 小时 / 3 个 Session 降到 3 小时 / 1 个 Session；9 月 2 日新增 Max 20x 用户称 30 分钟用掉 20% 周额度，所有 Agent 在形成可用工作前被拦住 | 自述且任务条件未完全控制；后一个回执称当时限额临时提高 50% |
| 主发布讨论 | https://www.reddit.com/r/ClaudeCode/comments/1w4k3kw/claude_fable_51_just_dropped/ | 一次生成 50+ C++ 文件、Low 表现、10 个研究 Agent 与快速周额度消耗等混合反馈 | 作为备选，不逐条写入正文 |
| @brij 首轮测试镜像 | https://w.twstalker.com/brij | 复杂设置重构 20 分钟、用 4% Token budget；随后 Sol Medium 对抗审查发现并修复 5 个 Bug | 新鲜正面案例，因原 X 直链未恢复，正文未采用 |
| @codebykrishna 回复 Claude 发布帖 | https://x.com/codebykrishna/status/2094896306862895104 | 发帖人称更新后 Max 5 小时窗口明显更快耗尽；当时使用 Opus 5、使用方式未变 | 单一用户自述；用于说明首夜用量疑问不只出现在显式切到 Fable 的场景，不推断系统级根因 |
| @AI_masaou 首日长评 | https://x.com/AI_masaou/status/2094918267190280505 | 几小时并行使用约 9 个 5 小时窗口；总体强烈肯定易用性；记录同类任务 Low 约 2.5 万 Token、xHigh 约 20 万 Token | 单一开发者实测；具体任务和 Harness 未完整公开；截图时约 1.65 万浏览、111 赞 |
| @kimmonismus 额度与自动续跑反馈 | https://x.com/kimmonismus/status/2094912538387648707 | 称 Fable 5.1 的额度消耗体感比 Fable 5 更差；引用前帖称达到 Session Limit 后「限额重置后自动继续」没有正常工作；同期对比 GPT-5.6 Sol Ultra | 用户自述；截图由用户提供，含 X 平台翻译与 Claude Code 限额界面；不能外推自动续跑故障率 |
| @joseph_dibb 10 分钟触顶 | https://x.com/joseph_dibb/status/2094912207918174693 | 称使用 Fable 5.1 约 10 分钟即达到 Session Usage Limit | 未披露套餐、Effort、上下文与 Agent 数量 |
| @ZryMiller 一条 Prompt / 90 分钟 | https://x.com/ZryMiller/status/2094912044676039087 | 一条 Prompt 制作游戏复刻，约 90 分钟烧完 5 小时窗口，任务尚未完成；附进度视频 | 重任务且成果已有可见进度，不把全部消耗写成浪费 |
| @Solzi_Sez 四小时反例 | https://x.com/Solzi_Sez/status/2094923708012151098 | Max 20x；称连续 4 小时使用 Fable 5.1，当前窗口 13%、周额度 3%；写作型数据处理分派给 Opus Agent | 单一正面自述；与负面案例共同用于展示配置和路由差异，不计算故障率 |
| @AbdoKerdawy 三小时 / 周额度约 77% | https://x.com/AbdoKerdawy/status/2094956838508798461 | Max 20x；称第一个 5 小时窗口不到 1 小时耗尽，第二个约 1.5—2 小时耗尽，累计约 3 小时后 Fable 周额度接近 77%；附用量截图 | 单一用户自述；任务、Effort 与 Agent 数量未完整披露，作为后续备选，不写成普遍速度 |
| @jeeacheff 两个窗口 / 400K 上下文 | https://x.com/jeeacheff/status/2094951300194566613 | 称使用两个 5 小时窗口与 400K 最大上下文、常规调用子 Agent 后，接近耗尽 Max 20x 的一周额度；附用量截图 | 单一用户自述；重上下文与子 Agent 都是显著变量，作为后续备选 |

## 视觉来源

- `assets/official-fable51-launch-visual.jpg`：Claude 官方 X 发布帖视频封面原图，无裁切或改写。
- `assets/x-usage-reply-codebykrishna-2094896306862895104-v02.png`：公开 X 回复及父帖的 Nitter 镜像截图，无文字替换。
- `assets/x-kimmonismus-fable51-rate-limit-auto-resume.png`：用户提供的公开 X 帖截图，保留 X 平台翻译和 Claude Code Session Limit 界面，无编辑改写。
- `assets/official-prompt-guide-subagent-parallel.png`：Anthropic 官方 Fable 5.1 Prompt 指南的目标段落浏览器原样截图，只在截取时裁到「主 Agent 与子 Agent 并行」小节，无标注、翻译或文字替换。
- `assets/every-dan-claude-code-usage.jpg`：Every 发布的 Dan Shipper Claude Code 日志图原图，无数据改写。
- `assets/x-nine-accounts-fable51-review-2094918267190280505.png`：公开 X 长评的 Nitter 镜像截图，无文字替换。
- `assets/official-system-card-p95-095.png`：官方系统卡第 95 页，180 DPI 渲染，无裁切或文字改写。
- `assets/doodle-budget-valve-appsso-v01.png`：按 APPSO adapter 与 `appsso-004` 从项目自有构图参考重绘的唯一 AI 图。
- 作者首轮用量、下午复测结果、上一篇留言区与 Reddit 高信号原帖暂留手动补图位；没有原图时不制作替代资料卡或伪界面。当前正文共 6 张真实来源图、1 张 APPSO 笨拙涂鸦。

## 发布前重开

- 重开 Anthropic 状态页、Fable plan 帮助页和官方开发者账号，确认是否新增计量事件、解释或修复。
- 重开正文采用的 Reddit 帖，检查删除、编辑、补充配置或官方回复。
- 若用户补充个人 `/usage`、Agent 面板或时间截图，核对后登记权利并更新开场图。
- 等 5 小时窗口重置后按复测合同记录同一 Prompt；起点增加 10% 即停止，优先保留连续截图而非追求完成任务。
- 复核系统卡页码、两组概率数字及 `bypassPermissions` 拼写。
