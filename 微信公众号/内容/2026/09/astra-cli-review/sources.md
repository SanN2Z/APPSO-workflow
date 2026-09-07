# 来源与可写边界

游戏方案补充：2026-09-05 新核验的 X 原帖、互动快照、国内热点与旧发布日期纠错见 [game-idea.md](research/game-idea.md)。X 预览原件及公开字段回执在 research/source-assets/，本轮没有把第三方演示计作作者亲测。

访问日期：2026-09-05（Asia/Tokyo）。发布日与访问日分开记录。以下均为公开资料，不复用公司受限素材或既有成稿。

本轮正文的主要事实与图片索引见 [「黄金周」来源卡](research/goldweek-sources.md)：已核官推原始时间、两种重置条件、网友游戏案例及补充测评。正文统一使用北京时间；下表保留各原站日期。

| ID | 原始来源 | 发布日／状态 | 类型与支持范围 | 使用限制 |
|---|---|---|---|---|
| S01 | [OpenAI 发布页](https://openai.com/index/gpt-6-astra/) | 9 月 3 日发布背景由 S05／S06 交叉确认；本页已读取 | 官方发布、能力定位、评测表 | 能力为厂商主张；榜单含不同工具、推理和框架条件；浏览器下载本页被 403 拦截，正文可经检索工具读取 |
| S02 | [OpenAI 系统卡](https://deploymentsafety.openai.com/gpt-6-astra) | 已读取 | 官方评估方法、图表、限制 | 高难度定向评估不能解释成普通用户出错率；图片原件从该站下载 |
| S03 | [Fable 套餐帮助页](https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan) | 页面显示本周更新 | Max 套餐纳入 Fable，使用普通周额度并有 Fable 上限 | 没有订阅百分比对应 Token 的固定公式；不把 5x 当推理档 |
| S04 | [Anthropic Fable 产品页](https://www.anthropic.com/claude/fable) | 列 9 月 1 日发布 | Fable 5.1 产品身份、功能定位 | 当前稿只作视觉任务对照，不能由一题评价全部能力 |
| S05 | [ARC Prize 原始评测](https://arcprize.org/blog/astra) | 9 月 3 日 | 基准主办方的直接评测 | Standard 与 Provider Adapter 分开；不证明 AGI |
| S05a | [ARC Prize 结果页](https://arcprize.org/results/openai-gpt-6-astra) | 标注 9 月 2 日结果 | 配置与成本的精确结果 | 日期是结果记录日，不代替商业发布日期 |
| S06 | [Cognition／Devin 实测](https://devin.ai/blog/gpt-6-astra) | 9 月 3 日 | 合作产品方自有工程评测 | 商业集成方，非完全独立公众随机测试；质量／可合并性与成本均依赖其框架 |
| S07 | [Every Vibe Check](https://every.to/vibe-check/gpt-6-astra-vibe-check) | 9 月 3 日 | 实测作者公开摘要，署名 Katie Parrott and GPT | 只读到公开导语，付费正文未读；不能声称掌握完整测试过程或全部结论 |
| S08 | [Irregular 评测](https://www.irregular.cv/research/assessing-gpt-6-astra) | 9 月 3 日 | 与 OpenAI 合作的外部专业安全评估 | 授权评测环境，不能当普通订阅能力；本文不运行攻击测试 |
| S09 | [Reddit 首发讨论串](https://www.reddit.com/r/codex/comments/1w7j5jf/astra_release_megathread/) | 访问时为首发动态讨论 | 公开用户体验，有正负案例 | 自述未独立复现；帖子与回复时间显示相对值，不能强行换成精确日期；页面没返回可靠互动数 |
| S10 | [Artificial Analysis 模型页](https://artificialanalysis.ai/models/gpt-6-astra) | 已打开 | 补充核查入口 | 当前抽取未得到可独立核对的分数；不把官方发布表中的 AA 项误称该机构已复测 |
| S11 | [OpenAI 官方发布视频帖](https://x.com/OpenAI/status/2095595741528125780) | 原帖 ID 与账号已通过公开 syndication 返回核验 | 官方宣传视频、封面原图 | X 网页直接打开失败；公开媒体数据确认账号为 OpenAI、媒体类型为视频；保存的是视频封面，不是亲测截图 |

## 官方介绍摘编（中文改写，供后续稿件选用）

OpenAI 将 GPT-6 Astra 的重点放在电脑操作、软件开发和多步骤专业工作，也强调文档、表格、演示文稿的成品质量，以及收到新要求后继续完成原任务的能力。发布页列出的是特定评测设置下的成绩，不能直接视为 CLI 实测结果。来源：S01。

## 必须保留的比较口径

S01 发布表：AutomationBench，Astra 41.4%、Fable 5.1 31.4%；Terminal-Bench 4.0，57.9%、55.8%；AA Intelligence Index，61.2、65.7；HLE with tools，57.2%、65.0。这些只用于说明优势并不覆盖所有指标，不制成总体胜负表。该页说明取各推理档的最佳分数，研究／API 环境与产品端可能不同。

S05／S05a：Standard 的最佳记录为 max、62.7%、26,098 美元；Provider Adapter 的最佳记录为 high、99.9%、18,817 美元。成本是对应评测整次运行口径，不是用户完成一道工作题的费用。不能把配置差异省略后声称「99.9% 击败人类就等于 AGI」。

S03：Max 用户的 Fable 使用最多占普通周使用上限的 50%，消耗速度可能快于其他模型；这不是额外赠送 50% 的普通额度。本方案自行制定更低的实验停止阈值。

## 禁止从本次资料推出

- 不写 Astra「所有榜单第一」、订阅「无限用」、或某个参数规模已获官方确认。
- 不把 Every 的 Fable 泛称自动精确成本文所测的 Fable 5.1 配置。
- 不把模型宣称完成、网页截图漂亮或测试脚本存在写成实际验收成功。
- 不把官方宣传视频、合作方评测、社区自述变成本人的使用经历。

## 发布前重开

再次打开 S01—S05，检查上线范围、用量口径和榜单有无修改；若引用 S09，重开具体回复，补永久链接与原始截图；检查图片授权。实测完成前保持 research。

## 本轮外部内容与结尾增补

Every 与 Cognition 重新读取；Berman 5 天长任务保留同日一手回执及提前访问上下文。精确支持范围见 [ending-evidence.md](research/ending-evidence.md)。


## 当前结尾来源｜FB024

用户撤下性能与费用展开，只保留六项信息图。新增 Anshu 概念图流程与 Paul 原帖反馈，原始链接、上下文和限制见 [creative-ending-evidence.md](research/creative-ending-evidence.md)。上文旧成本结尾记录仅作历史。


## 当前末节｜FB026

AGI 话题替换此前全部末节网友案例。当前原始报道、官方主张与作者判断边界见 [agi-ending-evidence.md](research/agi-ending-evidence.md)。FB024 及以前的结尾记录仅作历史，不代表当前正文。


## FB027｜补充高质量原始配图

- [TIME 对 Greg Brockman 的 AGI 专访封面](https://www.youtube.com/watch?v=dnSpKF5pWNQ)，权利人：TIME。采访官方封面原图，未经改动；不冒充发布会现场或本次 AGI 发言发生时的画面。
- [Anthropic 发布专题首页](https://www.anthropic.com/claude-fable-and-mythos-5-1)，权利人：Anthropic。官网原生首页截图，含导航、标题、天空与月亮，以及 Made with Fable 5.1 标记。
- [OpenAI 发布 Astra 的完整 X 帖子](https://x.com/OpenAI/status/2095595741528125780)，权利人：OpenAI / X。原生嵌入截图，完整保留账号、正文、视频封面、日期与互动栏；显示北京时间。图中的播放按钮属于静态截图。
- [TechRepublic 报道标题与配图](https://www.techrepublic.com/article/news-openai-gpt-6-astra-agi-era-2026/)，权利人：TechRepublic / TechnologyAdvice；配图署名 OpenAI。原网页连续区域截图，保留标题与完整配图，避开广告留白；未改字、重排或拼接。备选，不与采访图堆叠。


## FB030｜开头更新

今日 Max 周额度重置使用 [Lydia 原帖](https://x.com/lydiahallie/status/2095967323412930677)，与早前 ClaudeDevs 的全体用户重置分开。原文、UTC 时间及完整截图指纹见 research/claude-max-weekend-reset.json；其余开头原帖重新获取记录见 research/opening-posts-20260905.json。没有竞争导致重置的证据。


## FB032｜学习、复杂任务与 Paperweave

新增引语采用[印度科学理工学院的 Hassabis 对谈实录](https://eecs.iisc.ac.in/fireside-chat-sir-demis-hassabis-and-prof-govindan-rangarajan/)，活动为 2026-02-17，谈学习方法而非 Astra。用户项目用独立演示实例截图。事实边界见 [核对记录](research/paperweave-learning-evidence.md)。
