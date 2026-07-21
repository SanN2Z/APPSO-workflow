# 二轮事实卡

- **as_of**：2026-07-12
- **角色**：Evidence editor
- **用途**：供主编锁 brief、主笔重写前置信息卡，以及重写后的逐项事实复核。
- **结论**：产品、价格、入口、reset 定义、人物身份和主要跑分已有可用证据；时间线只能保留“约一小时”的降级口径；Arena 与 Fable promotional access 页面本轮不可用。

## 可直接用于开场的 60 秒事实卡

> - **三档不是三个推理模式。** Sol 是旗舰，适合最难、最需要质量的任务；Terra 是成本更低的日常均衡档；Luna 最快、最便宜，适合预算敏感和大量常规调用。这后半句是对 OpenAI 官方定位的人话翻译，不是独立性能结论。
> - **标准短上下文 API 价**按每百万 token 计：Luna 输入 / 输出 **$1 / $6**，Terra **$2.50 / $15**，Sol **$5 / $30**。发布页与 7 月 12 日定价页一致；长上下文、缓存、Batch / Flex / Priority 另算。
> - **`max` 和 `ultra` 不是一回事。** `max` 是让单个 GPT-5.6 比 `xhigh` 花更多时间推理、检查和返工；`ultra` 默认让 4 个 agent 并行协作，以更多 token 换更强结果和更短完成时间。
> - **入口也变了。** ChatGPT 新增 Work 这个长任务 agent；原 Codex app 合并进新版 ChatGPT 桌面端，但 Codex 能力、项目和默认视图仍保留。准确说法是“入口合并 / 搬家”，不是“Codex 被砍”。

## 原子事实与可用口径

| Claim ID | 标签 | 状态 | 可用表述 | 证据 | 限制 / 禁用表述 |
|---|---|---|---|---|---|
| FACT-5.6-01 | 事实 + 厂商定位 | verified | GPT-5.6 有 Sol、Terra、Luna 三个持久能力档：Sol 旗舰；Terra 较低成本、官方称能力可与 GPT-5.5 竞争；Luna 最快且最便宜。 | OpenAI GPT-5.6 发布页 | “适合最难 / 日常均衡 / 批量常规”是编辑的人话映射，需写成定位而非实测结论。不要把三档写成 low / medium / high reasoning effort。 |
| FACT-5.6-02 | 事实 | verified | 标准**短上下文**每百万 token 输入 / 输出价：Sol $5 / $30；Terra $2.50 / $15；Luna $1 / $6。 | OpenAI 发布页；API Pricing | 两页该口径一致、未变化。当前定价页另列标准**长上下文**：Sol $10 / $45；Terra $5 / $22.50；Luna $2 / $9。正文若只给发布页价格，必须写“标准短上下文公开价”。 |
| FACT-5.6-03 | 事实 + 人话解释 | verified | `max` 给单个模型更多推理时间；`ultra` 默认协调 4 个 agent 并行，通常多耗 token，目标是提高困难任务结果并缩短 wall-clock time。 | OpenAI GPT-5.6 发布页 | 不写成“max = 一个模型、ultra = 四个相同模型必然更好”。API 仅提供可构建 ultra-like 体验的 multi-agent beta；产品可用套餐也不同。 |
| FACT-WORK-01 | 事实 | verified | ChatGPT Work 是 ChatGPT 内面向长任务的 agent，可跨应用和文件工作；7 月 9 日开始按套餐分批 rollout。 | OpenAI ChatGPT Work | “什么活都接的通用工作台”是作者判断，不能冒充官方产品定义。 |
| FACT-WORK-02 | 事实 | verified | Codex app 合并进新版 ChatGPT 桌面 app；更新后原 Codex app 变成新版 ChatGPT 桌面端，Codex 可设默认视图，Codex 项目仍可在移动端访问；旧 ChatGPT 桌面端改名 ChatGPT Classic。 | OpenAI ChatGPT Work | 可写“搬进统一入口”，不可写“Codex 消失 / 下线 / 被砍”。 |
| FACT-WORK-03 | 厂商自报 | verified_with_limit | OpenAI 称 Codex 每周用户超过 500 万，超过 100 万用于软件开发之外的工作。 | OpenAI ChatGPT Work | 未公开去重、统计窗口与任务分类细则；只能保留“OpenAI 称”。 |
| FACT-RESET-01 | 社交原帖事实 | verified_from_screenshot | ClaudeDevs 公告原文是：`We've reset 5-hour and weekly rate limits for all users.` | `assets/claude-reset-tibo.png` | 原帖 X 直链未取得；截图是用户提供素材。不要自行补出具体套餐范围或原因。 |
| FACT-RESET-02 | 事实 + 有边界的解释 | verified | Claude 帮助页把订阅用量分为 five-hour session 与 weekly usage limits，并在 Usage 页分别显示已消耗进度和下次 reset。本文可把公告写成“把当期五小时与每周用量计数重置，让用户重新获得当前周期可用量”。 | Claude Usage limit best practices | reset 不是 API rate-limit 重置，不是永久提高上限，不是 unlimited，也不证明以后每周可用量变多。消息数还受模型、消息长度、附件、对话长度与工具使用影响。 |
| FACT-RESET-03 | 未知 / 推断边界 | unresolved | Anthropic 没在这条公告中解释动机。7 月 7–10 日官方状态页确有多次模型与 Claude Code / Cowork 故障，这只构成背景。 | 截图；Claude Status | 不写“Anthropic 看到 GPT-5.6 后临时应激”“因 Fable 延期而补偿”。Fable promotional access 帮助页本轮 Internal Error，不能用来确认替代解释。 |
| FACT-TIBO-01 | 事实 | verified | Thibault “Tibo” Sottiaux 是 OpenAI Member of Technical Staff；OpenAI Forum 称其 Head of Codex，并说他 leads Codex。 | OpenAI Forum | 可写“Codex 负责人”。不要沿用二手报道的“Head of ChatGPT and Codex”。 |
| FACT-TIBO-02 | 原帖事实 + 玩梗/评论 | verified_with_limit | Tibo 在 ClaudeDevs reset 公告下回复 `I smell fear`。直译是“我闻到了恐惧”；结合回复位置，更稳妥的中文处理是竞争性贴脸阴阳，例如“哇，我好怕怕哦～”。 | 包内截图；Tibo 原帖直链；OfficeChai 交叉确认 | “我好怕怕哦”是语气转译，不是逐字引语；不能写成 Tibo 真的害怕，也不能把他的嘲讽当成 Anthropic 动机证据。 |
| FACT-TIME-01 | 时间事实 | verified_with_limit | OpenAI 官方预告 GPT-5.6 / ChatGPT Work 发布直播为 7 月 9 日 10:00 PT（17:00 UTC）。包内 reset 截图显示本地时间 7 月 10 日 03:01；若按项目当前 JST 解释，即 18:01 UTC，约晚 61 分钟。 | OpenAI 原帖直链（经 Digg 镜像呈现）；包内截图；OpenAI 发布页 | 截图自身没有印时区，OpenAI 发布页又明确是 24 小时渐进 rollout。正文只可写“发布会预定开播约一小时后（按截图本地时区换算）”，不能写“GPT-5.6 广泛上线后精确 61 分钟”。 |
| FACT-BENCH-01 | 厂商自报 | verified | OpenAI 发布表中：AA Intelligence Index v4.1 为 Sol 58.9、Fable 59.9；Terminal-Bench 2.1 为 Sol Ultra 91.9、Mythos 88；BrowseComp 为 Sol Ultra 92.2、Mythos 88；SWE-Bench Pro 为 Sol 64.6、Mythos 80.3；FrontierMath Tier 4 为 Sol 83、Fable 87.8；HealthBench Professional 为 Sol 60.5、Fable 60.9。 | OpenAI GPT-5.6 发布页 | 这是 OpenAI 汇总的厂商表，混合 Sol / Sol Ultra、Fable / Mythos 和不同工具 / effort；不能称“六场统一预算同场考试”，也不能从所选六项推出全面胜负。HealthBench 脚注称其官方 scoring 与 Anthropic system card 报告不可比。 |
| FACT-BENCH-02 | 第三方结果 | verified | 7 月 12 日 Artificial Analysis 总榜为 Fable 5（max，含 Opus 4.8 fallback）60 分第 1，GPT-5.6 Sol max 59 分第 2；其专题文称 Sol 在 Coding Agent Index 为 80 分、列首位。 | AA 总榜；AA GPT-5.6 专题；AA 两个模型页 | 综合指数不是所有任务的“总智商”。Coding Agent Index 配的是各自 agent harness（如 Codex、Claude Code），不是裸模型同环境；Fable 条目含 fallback。旧稿“GPT-5.6 独立页面还没出来”已失效，必须改。 |
| FACT-BENCH-03 | 独立研究 | verified_with_limit | METR 的预部署评估认为现有证据不足以说明 GPT-5.6 Sol 在软件与 R&D 任务上显著超出现有前沿。 | METR | METR 的 time-horizon 结果受作弊判定强烈影响；其 11.3h、71h、270h+ 均被 METR 明确称为不稳健，正文不应摘单个数字。 |
| FACT-SWE-01 | 官方审计 / 厂商自报 | verified | OpenAI 对 SWE-Bench Pro 731 个公开任务的审计中，datapoint pipeline 标出 200 个（27.4%）问题任务，人工标注活动标出 249 个（34.1%），并估计约 30% 任务有破损问题，建议开发者谨慎审视结果。 | OpenAI SWE-Bench Pro 审计 | OpenAI 是参赛厂商，不是外部独立审计。原文没有明确说“撤回此前推荐”；“独立人工标注认为”也会让读者误以为机构独立，应改成“人工标注活动”。审计不自动抹掉任一模型的原始分数。 |
| FACT-ARENA-01 | 第三方结果 | blocked | 本轮无法核对 GPT-5.6 在 Arena 的票数、置信区间或名次。 | Arena Leaderboard | 页面只返回导航，不返回榜单行。必须删除旧稿“没有攒够足以稳定判断的新模型票数”，或由人工浏览器看到模型行后补证据。 |

## 给主笔的强制修改清单

1. 把“7 月 9 日 17:00 UTC 广泛上线、约 61 分钟后 reset”降为“发布会预定开播约一小时后，ClaudeDevs 发出 reset 公告”；脚注说明截图本地时区换算与 24 小时渐进 rollout。
2. 价格卡写“标准短上下文 API 价”，不要把它写成所有上下文、所有处理模式的统一价格。
3. 保留“Codex 搬家”判断，但准确写成 app 合并、能力与默认视图保留。
4. reset 只写当前五小时 / 每周用量计数重置；不要写永久提额、API 限流或确认动机。
5. 独立评测段更新为：AA 已有 GPT-5.6 完整结果；Fable 60、Sol 59，Coding Agent Index 则 Sol 80。必须交代 Fable fallback 与 harness 差异。
6. 删除 Arena “票数不足”的断言，除非发布前人工浏览器补到可见票数与置信区间。
7. SWE-Bench Pro 段把“独立人工标注”改为“人工标注活动”，把“撤回推荐”改为“估计约 30% 任务有问题，并建议谨慎审视结果”。

## 本轮缺陷

| ID | 严重度 | 问题 | 关闭条件 |
|---|---|---|---|
| FACT-002 | major | 旧稿把直播开播时刻写成“广泛上线”精确时刻，且截图未标时区。 | 按 `FACT-TIME-01` 降级，并保留 24 小时 rollout 限制。 |
| FACT-003 | major | 旧稿独立评测状态过期：AA 已发布 GPT-5.6 完整结果。 | 更新 AA 60 / 59 与 Coding Agent Index 80，写清 fallback / harness。 |
| FACT-004 | major | Arena 页面本轮不可用，旧稿“票数不足”没有可复核页面证据。 | 删除断言，或人工浏览后补模型行、票数和置信区间。 |
| FACT-005 | major | SWE-Bench Pro 审计被写成“独立人工标注”及“撤回推荐”，均超出原文。 | 按审计原文改为人工标注活动、约 30% 问题与谨慎审视。 |
| FACT-006 | minor | Fable promotional access 页面返回 Internal Error，不能支撑 reset 的替代动机。 | 删除该动机，或发布前重新打开一手页面并只写它直接支持的内容。 |

## 证据编辑结论

`FACT-001` 所需的前置事实卡已有可用底座，但正文事实仍不能标记为二轮通过：`FACT-002` 至 `FACT-005` 会直接改变现稿表述，`FACT-006` 需要删除或重新取证。主笔完成重写后，证据编辑应再逐句核对所有姓名、日期、价格、榜单、产品入口与“最新”表述。

## 成稿复核 2026-07-12

- **复核对象**：`draft.md`（`updated: 2026-07-12`，`as_of: 2026-07-12`）
- **复核范围**：时间线、三档与价格、`max` / `ultra`、Work / Codex、Claude reset、Tibo、厂商六项评测、Artificial Analysis、METR、SWE-Bench Pro 审计、OpenAI 用户数，以及重写中新出现的高风险事实句。
- **复核结论**：`needs_fix`。前轮 `FACT-002` 至 `FACT-006` 均已按证据边界处理；另发现 2 个不改变主论点的轻微过宽表述，修正后可进行最终事实签字。

### 逐项结果

| 项目 | 结论 | 成稿核对结果 |
|---|---|---|
| 时间线 | pass_with_limit | 成稿写“按截图本地时间和项目当前时区换算”“发布会预定开播一小时后”，同时交代截图未标时区和 OpenAI 24 小时渐进上线；没有再写“广泛上线后精确 61 分钟”。 |
| 三档定位 | pass | Sol 旗舰 / 最难任务、Terra 日常均衡、Luna 最快最便宜 / 预算敏感批量调用，与官方定位及人话标签一致；明确说后两项不是独立实测。 |
| API 价格 | pass | 明确限定“标准短上下文”；Luna $1 / $6、Terra $2.50 / $15、Sol $5 / $30，输入输出顺序和每百万 token 单位均正确；注明长上下文、缓存和其他处理模式另算。 |
| `max` / `ultra` | pass | `max` 写成单模型增加推理、检查和返工时间；`ultra` 写成默认 4 agent 并行并增加 token，未写成独立模型档或必然更强。 |
| Work / Codex | pass | Work 写成 ChatGPT 内长任务 agent；Codex app 写成合并进新版桌面端，能力、项目和默认视图保留；“搬家而非被砍”符合官方页面。 |
| Claude reset | pass | 全文限定为当期五小时与每周用量计数重置；明确排除 API rate limit、永久提额、无限使用和已证实动机。 |
| Tibo 身份与语义 | pass | 写“OpenAI 的 Codex 负责人”符合 OpenAI Forum；`I smell fear` 的直译和“我好怕怕哦”均标成贴脸阴阳，没有写成真实害怕或 Anthropic 动机证据。 |
| 厂商六项评测 | needs_fix | 胜负方向、Fable / Mythos / Sol / Sol Ultra 混用限制和非统一预算说明均正确；但“OpenAI 发布页挑出的六项”误把本文编辑选择写成 OpenAI 主动选择，见 `FACT-007`。 |
| AA 60 / 59 / 80 | pass | Fable 5 max 60 第 1、Sol max 59 第 2、Sol Coding Agent Index 80 列首位均正确；Fable fallback 与 Codex / Claude Code harness 差异均已披露。 |
| METR | pass | 准确写成软件与 R&D 能力没有显著超出现有前沿的谨慎结论；明确 time-horizon 受作弊判定影响，没有摘录不稳健小时数。 |
| SWE-Bench Pro | pass | 731、200 / 27.4%、249 / 34.1%、约 30% 与“建议谨慎审视”均正确；使用“人工标注活动”，并声明 OpenAI 是参赛厂商、并非外部独立审计。 |
| OpenAI 用户数 | pass | “Codex 每周超过 500 万、超过 100 万用于软件开发之外”为 OpenAI 自报；去重、窗口和分类方法缺失的限制已保留。 |
| Arena / Fable promotional access | pass_by_omission | 成稿已删除 Arena “票数不足”及 promotional access 对 reset 动机的猜测，没有继续引用不可访问页面。 |
| 统一任务总成本实测 | needs_fix | 成稿用“目前没有”做全局不存在断言，现有证据只支持“本文未取得 / 未采用”，见 `FACT-008`。 |

### 成稿新增缺陷

| ID | 严重度 | 成稿原句 | 问题 | 建议的事实边界 | 关闭条件 |
|---|---|---|---|---|---|
| FACT-007 | minor | “OpenAI 发布页挑出的六项评测里，GPT-5.6 在 Terminal-Bench 2.1 和 BrowseComp 的表中成绩更高……” | OpenAI 发布页列了远多于六项评测；这六项是本文为图表选出的对照，不是 OpenAI 明示挑出的六项。 | 改为“**本文从 OpenAI 发布页取出的六项对照里**……”或“**本文所列六项评测里**……”。 | 主语改为本文 / 本文图表，保留后文模型版本、工具与配置限制。 |
| FACT-008 | minor | “目前没有一组统一任务、统一工具、统一验收标准下的总成本实测，本文不能拿公开单价直接宣布谁更省。” | “目前没有”是难以穷尽核验的全局不存在断言；本轮来源只能证明本文没有取得可用的同口径实测。 | 改为“**本文没有找到（或没有采用）一组同时统一任务、工具和验收标准的总成本实测，因此不能……**”。 | 把全局不存在收窄为本文检索 / 采用范围，或补入一项可复核的系统性检索证据。 |

### 关闭建议

`FACT-002`、`FACT-003`、`FACT-004`、`FACT-005`、`FACT-006`：成稿中已关闭。
`FACT-007`、`FACT-008`：待主笔做两处单句修复；修复不需要改论证结构或重新浏览，证据编辑核对 exact diff 后即可建议 `fact_checked: true`。

## 最终签字 2026-07-12

- **FACT-007：closed。** Exact replacement 为“**本文从 OpenAI 发布页取出的六项对照里**……”，已把六项对照的选择主体从 OpenAI 收窄为本文，并继续保留 Sol / Sol Ultra、Fable / Mythos、工具与推理配置不统一的限制。
- **FACT-008：closed。** Exact replacement 为“**本文没有找到一组同时统一任务、工具和验收标准的总成本实测**……”，已把无法穷尽核验的全局不存在断言收窄为本文检索范围。
- **HUMAN-003：事实边界未改变。** 当前条件句为“**如果截图用的是日本时间，换算下来**……”，并继续明确“截图未标时区”“OpenAI 是 24 小时渐进上线”；图注仍写“约一小时”按截图本地时区换算，没有恢复成精确因果或所有用户同时上线的断言。
- **证据签字：pass。** 截至 `as_of: 2026-07-12`，当前 `draft.md` 的改动事实已完成逐句复核；证据侧同意将其设置为 **`fact_checked: true`**。该签字不覆盖图片权利、移动端视觉、独立冷读或发布日时效复查。
