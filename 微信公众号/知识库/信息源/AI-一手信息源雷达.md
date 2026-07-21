# AI 一手信息源雷达

- 建档日期：2026-07-10
- 目标：比中文媒体转载更早发现大模型、Physical AI、机器人、世界模型、AI 基础设施、产品、价格、额度、论文、开源和监管变化。
- 原则：发现可以靠聚合，落稿必须回到原始材料；入口本身也可能迁移，每季度复核一次。

## 来源分级

### P0：原始事实源

- 公司新闻、产品发布页、官方文档和更新日志；
- 论文、模型卡、系统卡、技术报告；
- 官方 GitHub、Hugging Face、ModelScope 和许可证；
- 定价、额度、模型列表、状态页和退役公告；
- 当事人原帖、演讲视频、采访原文和会议记录；
- 监管原文、交易所公告、公司财报和投资者关系材料。

P0 可以证明“对方发布或声称了什么”，不自动证明效果最好。

### P1：独立验证源

有公开方法、版本和限制的独立评测、数据机构或研究组织。用于校准厂商说法，不能只摘排行榜名次。

### P2：可信报道与专业分析

适合发现人事、融资、组织、供应链和行业背景。涉及独家消息时保留媒体归属，继续寻找文件、当事人或第二家独立确认。

### P3：线索雷达

X、Reddit、Hacker News、小红书、B 站、Product Hunt、GitHub Trending 等。只证明“有人发布或讨论”，不证明动机、真实性和普遍性。

## 新鲜度口径

每条候选至少记录三个时间，公众号统一换算为北京时间（UTC+8）：

| 字段 | 含义 | 是否可进入“最新”窗口 |
|---|---|---|
| `source_created_at` | 论文、代码、文件或事件真正出现的时间 | 可以 |
| `official_announced_at` | 官方首次对外宣布的时间 | 可以 |
| `rediscovered_at` | 媒体、聚合站或社区重新炒热的时间 | 只能标成“重新发酵” |

- 优先级：近 4 小时 → 近 12 小时 → 近 24 小时 → 近 72 小时。
- 官方页面只有日期、没有时分时，只能写“今天发布”，不能硬塞进“近 4 小时”。
- arXiv 列表在周末后集中刷新时，以论文页 `Submission history` 为准，不能把列表刷新日当成论文发布日期。
- 旧材料因媒体报道重新进入讨论，正文必须同时交代原始事件时间和本轮讨论时间。

## 全球模型与产品：核心监测

| 机构 | 稳定入口 | 重点看什么 | 建议频率 |
|---|---|---|---|
| OpenAI | [News](https://openai.com/news/) · [产品更新日志](https://openai.com/products/release-notes/) · [系统卡](https://deploymentsafety.openai.com/) · [状态页](https://status.openai.com/) | 模型发布、ChatGPT/Codex 入口、价格额度、安全限制、静默更新 | 每日 |
| Anthropic | [Newsroom](https://www.anthropic.com/news) · [Research](https://www.anthropic.com/research) · [系统卡](https://www.anthropic.com/system-cards) · [平台更新日志](https://platform.claude.com/docs/en/release-notes/overview) · [状态页](https://status.anthropic.com/) | Claude/Claude Code、模型退役、API 行为、额度和系统卡 | 每日 |
| Google | [DeepMind News](https://deepmind.google/blog/) · [Gemini API 更新日志](https://ai.google.dev/gemini-api/docs/changelog) · [Vertex AI 更新](https://cloud.google.com/vertex-ai/generative-ai/docs/release-notes) · [Workspace Updates](https://workspaceupdates.googleblog.com/) | Gemini 模型、API、办公入口、研究与端侧能力 | 每日 |
| Meta | [Meta AI Blog](https://ai.meta.com/blog/) · [GitHub](https://github.com/meta-llama) · [Hugging Face](https://huggingface.co/meta-llama) | Llama、开源许可、权重、研究代码 | 每周；发布期每日 |
| xAI | [News](https://x.ai/news) · [API Docs 与更新日志](https://docs.x.ai/) | Grok、API、系统卡和 X 产品入口 | 每日 |
| Mistral | [News](https://mistral.ai/news/) · [文档更新日志](https://docs.mistral.ai/resources/changelogs) | 模型、Le Chat、API、开源权重和退役 | 每周 |
| GitHub | [Copilot Changelog](https://github.blog/changelog/label/copilot/) | Copilot 模型接入、套餐、额度、IDE 与 Agent 更新 | 每日 |
| Microsoft | [AI Blog](https://blogs.microsoft.com/ai/) · [Microsoft Research](https://www.microsoft.com/en-us/research/blog/) · [Foundry 更新](https://devblogs.microsoft.com/foundry/) | Copilot、Foundry、企业入口、研究和生态合作 | 每周 |
| AWS | [What's New](https://aws.amazon.com/about-aws/whats-new/) | Bedrock 模型上架、区域、价格、Agent 与企业能力 | 每周 |
| NVIDIA | [Developer Blog](https://developer.nvidia.com/blog/) · [Newsroom](https://nvidianews.nvidia.com/) | 芯片、推理栈、开源模型、企业合作 | 每周 |
| Apple | [Machine Learning Research](https://machinelearning.apple.com/) · [Newsroom](https://www.apple.com/newsroom/) · [Developer News](https://developer.apple.com/news/) | 端侧模型、系统入口、开发框架与隐私 | 每周；发布会期每日 |

## 国内模型与产品：核心监测

| 机构 | 稳定入口 | 重点看什么 | 建议频率 |
|---|---|---|---|
| DeepSeek | [API 更新日志](https://api-docs.deepseek.com/updates/) · [GitHub](https://github.com/deepseek-ai) · [Hugging Face](https://huggingface.co/deepseek-ai) | 新模型、接口、价格、权重、技术报告 | 每日 |
| Qwen | [官方博客](https://qwen.ai/blog) · [GitHub](https://github.com/QwenLM) · [Hugging Face](https://huggingface.co/Qwen) · [ModelScope](https://modelscope.cn/organization/qwen) · [阿里云模型更新](https://help.aliyun.com/en/model-studio/model-release-notes) | Qwen 模型、开源版本、许可证、云 API 和价格 | 每日 |
| 字节 Seed / 豆包 | [Seed 技术博客](https://seed.bytedance.com/blog) · [Hugging Face](https://huggingface.co/ByteDance-Seed) · [火山引擎发布中心](https://www.volcengine.com/news) | Seed、Seedance、Seedream、论文、方舟上架与退役 | 每日 |
| 腾讯混元 | [腾讯公司新闻](https://www.tencent.com/en-us/articles.html) · [GitHub](https://github.com/Tencent-Hunyuan) · [Hugging Face](https://huggingface.co/tencent) · [腾讯云产品动态](https://cloud.tencent.com/document/product/1729/97765) | Hy/混元、开源多模态、元宝与工作台入口、TokenHub 迁移 | 每日 |
| Kimi / Moonshot | [模型文档](https://platform.kimi.ai/docs/models) · [GitHub](https://github.com/MoonshotAI) · [Hugging Face](https://huggingface.co/moonshotai) | 模型可用性、退役、API、开源权重和 Kimi 产品 | 每日 |
| 智谱 / Z.ai | [官方博客](https://z.ai/blog) · [模型更新日志](https://docs.z.ai/release-notes/new-released) · [GitHub](https://github.com/zai-org) · [Hugging Face](https://huggingface.co/zai-org) | GLM、Coding Plan、价格额度、权重和工具链 | 每日 |
| MiniMax | [News](https://www.minimax.io/news) · [开放平台](https://platform.minimax.io/docs/) · [GitHub](https://github.com/MiniMax-AI) · [Hugging Face](https://huggingface.co/MiniMaxAI) | 文本、视频、语音模型，API、套餐与开源 | 每周；发布期每日 |
| 阶跃星辰 | [官方技术文章](https://static.stepfun.com/blog/) · [GitHub](https://github.com/stepfun-ai) · [Hugging Face](https://huggingface.co/stepfun-ai) | Step 模型、Agent、多模态和开源 | 每周 |
| 百度千帆 / ERNIE | [千帆文档](https://cloud.baidu.com/doc/qianfan/index.html) · [版本升级与退役](https://cloud.baidu.com/doc/qianfan/s/zmh4stou3) · [PaddlePaddle GitHub](https://github.com/PaddlePaddle) | ERNIE、平台版本、模型退役、价格与企业 Agent | 每周 |

## Physical AI 与机器人：核心监测

| 机构 | 稳定入口 | 重点看什么 | 建议频率 | 固定限制 |
|---|---|---|---|---|
| Google DeepMind | [Research](https://deepmind.google/research/) · [News](https://deepmind.google/blog/) | Gemini Robotics、SIMA、具身推理、跨本体迁移 | 每日 | 官方演示不等于跨实验室复现；核对模型访问范围和真机设置 |
| NVIDIA | [Physical AI Research](https://research.nvidia.com/research-area/physical-ai) · [Cosmos GitHub](https://github.com/nvidia/cosmos) · [Isaac GR00T](https://developer.nvidia.com/isaac/gr00t) | Cosmos、GR00T、仿真、合成数据、模型和许可证 | 每日 | NVIDIA 同时销售算力和生态；区分代码开源、权重开放与商业许可 |
| Physical Intelligence | [研究博客](https://www.pi.website/blog) · [GitHub](https://github.com/Physical-Intelligence) | π 系列、VLA、RL 后训练、开放权重 | 每日 | 自有数据和厂商评测较多；论文、权重和部署代码可能不同步 |
| Hugging Face LeRobot | [GitHub Releases](https://github.com/huggingface/lerobot/releases) · [博客](https://huggingface.co/blog/lerobot) | 模型接入、数据格式、硬件、仿真和 breaking changes | 每日 | 接入某模型不等于 Hugging Face 独立验证其能力 |
| Skild AI | [官方博客](https://www.skild.ai/blogs) | 跨机器人本体的基础模型、运动与操作 | 每周；发布期每日 | 演示导向强；必查遥操作、重置、试验次数和失败率 |
| Figure | [News](https://www.figure.ai/news) | Helix、工厂部署、连续运行和量产 | 每日 | 必查自治程度、人工介入、剪辑、失败次数和真实产线口径 |
| Boston Dynamics | [Blog](https://bostondynamics.com/blog/) · [News](https://bostondynamics.com/news/) | Atlas、Spot、学习控制、工程边界和合作 | 每周 | 产品营销和研究文章混合；通常没有标准模型卡 |
| 1X | [Discover](https://www.1x.tech/discover) | 家用机器人、世界模型、数据闭环 | 每周 | 世界模型生成的预测视频不等于真机策略达到同等成功率 |
| Toyota Research Institute | [News](https://www.tri.global/news) · [Publications](https://www.tri.global/publications) | 大行为模型、触觉、示教和可靠性 | 每周 | 公司新闻与正式论文分开记录 |
| Waymo | [Research](https://blog.waymo.com/research/) · [Blog](https://waymo.com/blog/) | 自动驾驶世界模型、闭环仿真、稀有场景 | 每周 | 驾驶专用结果不能直接外推到通用机器人 |
| Wayve | [Research](https://wayve.ai/thinking/category/research/) · [GAIA](https://wayve.ai/science/gaia/) | 自动驾驶世界模型、生成式仿真和评估 | 每周 | 区分生成场景、闭环评估与实车能力 |
| Helsing | [Newsroom](https://helsing.ai/newsroom) | 防务 AI、自主航空器、无人机、水下系统、机器人平台和重大融资 | 每日 | 防务公司材料有明确利益立场；订单、部署、自治程度和产品阶段分别核实 |
| 安川电机 | [Global News](https://www.yaskawa-global.com/newsrelease/) | 工业 Physical AI、柔性物体、学习模型与传统控制融合 | 每日 | 工业验证常缺完整试验表、失败数据和人工介入口径 |
| 软银 | [Press Releases](https://www.softbank.jp/en/corp/news/press/sbkk/) | Physical AI 云、MEC、AI-RAN 和机器人合作 | 每日 | 联合验证和基础设施计划不能当作模型能力的独立证据 |
| 智元机器人 | [官方文章](https://www.agibot.com.cn/article/) · [GitHub](https://github.com/AgibotTech) | AgiBot World、GO 模型、仿真和数据集 | 每周；发布期每日 | 核对数据许可、机器人本体、真实环境和厂商自测口径 |
| 灵波 / Robbyant | [GitHub](https://github.com/robbyant) · [LingBot-World 2.0](https://github.com/robbyant/lingbot-world-v2) | 世界模型、VLA、视频动作模型、权重和 TODO | 每日 | 核对非商业许可证、未开放模块和部署代码状态 |

### Physical AI 落稿前固定核对

- 真机还是仿真；自主还是遥操作；连续镜头还是剪辑；
- 任务数、试验数、成功率、平均耗时、人工介入、重置与失败恢复；
- 是否测试陌生物体、陌生环境和跨本体；
- 学习模型负责哪些环节，传统控制负责哪些环节；
- 代码、权重、数据和许可证实际开放到哪一步。

## 世界模型与空间智能：专项监测

| 机构 / 项目 | 稳定入口 | 重点看什么 | 固定限制 |
|---|---|---|---|
| World Labs | [Research & Insights](https://www.worldlabs.ai/blog) | Marble、World API、空间智能和世界模型分类 | 可探索 3D 世界的视觉质量不等于物理预测、规划或机器人可用性 |
| Meta FAIR | [Meta AI Research](https://ai.meta.com/research/) · [V-JEPA 2](https://github.com/facebookresearch/vjepa2) | JEPA、动作条件世界模型、视频预测和机器人规划 | 官方零样本结果不等于独立复现 |
| Google DeepMind | [Genie](https://deepmind.google/models/genie/) · [Research](https://deepmind.google/research/) | 可交互世界、SIMA、训练环境和具身 Agent | 核对动作空间、持续时间、多智能体和真实地点限制 |
| NVIDIA Cosmos | [产品页](https://www.nvidia.com/en-us/ai/cosmos/) · [GitHub Releases](https://github.com/NVIDIA/Cosmos/releases) | 世界生成、物理推理、策略和开放模型 | 同一品牌下不同模型功能不同，不能混成一个能力结论 |
| Wayve GAIA | [GAIA](https://wayve.ai/science/gaia/) | 自动驾驶世界生成、长时一致性和安全场景评估 | 驾驶域结果不外推为通用物理理解 |
| 腾讯混元 | [GitHub 组织](https://github.com/orgs/Tencent-Hunyuan/repositories) | HunyuanWorld、HY-World、WorldMirror 和权重 | 3D 生成、重建、可交互世界与机器人规划分开表述 |

“世界模型”必须强制打功能标签：

```text
renderer：生成给人看的画面
simulator：根据动作提供可交互反馈
predictor：预测未来状态
planner：利用内部模型选择行动
policy / VLA：直接输出机器人动作
```

同一项目可以覆盖多类，但必须分别提供证据。画面更漂亮不能直接写成更懂物理。

## 更广科技圈：发现与回源

| 类别 | 发现入口 | 回到哪里核实 |
|---|---|---|
| 全球科技头条 | [Techmeme](https://www.techmeme.com/) · [River](https://www.techmeme.com/river) · [Hacker News new](https://news.ycombinator.com/newest) | 公司公告、监管文件、法院文件、论文、代码或当事人原帖 |
| 半导体与 AI 基础设施 | Reuters Tech、Bloomberg Tech、SemiAnalysis | NVIDIA / AMD / Intel / TSMC / ASML 新闻室、IR、财报和政府公告 |
| 开发者基础设施 | [GitHub Changelog](https://github.blog/changelog/) · [Cloudflare Blog](https://blog.cloudflare.com/) · [AWS What's New](https://aws.amazon.com/about-aws/whats-new/) | 官方文档、更新日志、release 和状态页 |
| 创业与融资 | Bloomberg、Reuters、Financial Times、The Information、Crunchbase | 公司新闻稿、投资方公告、SEC / 交易所文件；独家消息保留媒体归属 |
| 深科技与工程 | [IEEE Spectrum](https://spectrum.ieee.org/) · Ars Technica | 论文、技术报告、标准、专利和公司原始材料 |

## 论文与开源雷达

| 来源 | 定位 | 用法 |
|---|---|---|
| [arXiv cs.AI](https://arxiv.org/list/cs.AI/recent) · [cs.CL](https://arxiv.org/list/cs.CL/recent) · [cs.LG](https://arxiv.org/list/cs.LG/recent) · [cs.RO](https://arxiv.org/list/cs.RO/recent) · [cs.CV](https://arxiv.org/list/cs.CV/recent) | 最新论文原文 | 搜标题和作者后读摘要、方法、限制；以 Submission history 计时，不能把预印本写成已被同行评审 |
| [OpenReview](https://openreview.net/) | 顶会投稿、评审与作者回应 | 看争议、复现和审稿意见，不只看论文摘要 |
| [Hugging Face Papers](https://huggingface.co/papers) | 论文发现和社区热度 | 只作发现入口，回到论文和代码 |
| GitHub Releases / Commits | 开源项目真实变化 | 关注 release、README、许可证和 tag；不要只看 Star 增长 |
| Hugging Face / ModelScope 模型卡 | 权重、配置、许可证和使用限制 | 核对模型 ID、大小、量化和许可证 |

## 独立评测与数据：优先保留

| 来源 | 适合回答 | 必须保留的限制 |
|---|---|---|
| [Artificial Analysis](https://artificialanalysis.ai/) · [方法](https://artificialanalysis.ai/methodology/intelligence-benchmarking) | 智能、速度、成本与多模态横向比较 | 综合指数会掩盖具体任务差异；核对模型日期和推理档位 |
| [Epoch AI Benchmarks](https://epoch.ai/benchmarks) · [方法说明](https://epoch.ai/benchmarks/about) | 能力趋势、算力、数据和多个公开评测 | 部分数据是汇总，区分 Epoch 自测与外部榜单 |
| [METR Time Horizons](https://evals.alignment.org/time-horizons/) | Agent 能连续完成多长的人类任务 | 依赖 scaffold、任务集和成功率定义，不能直接等同“替代几小时工作” |
| [Arena.ai](https://arena.ai/) · [方法与博客](https://arena.ai/blog/) | 开放式对话的人类偏好 | 风格、样本结构和模型身份可能影响票选 |
| [SWE-bench](https://www.swebench.com/) · [代码](https://github.com/princeton-nlp/SWE-bench) | 真实 GitHub issue 修复能力 | 比较时统一榜单版本、Agent scaffold、预算和是否人工筛选 |
| [WorldArena](https://world-arena.ai/) · [RoboArena](https://robo-arena.github.io/) | 世界模型功能效用和真实机器人社区 A/B 评估 | 先核任务、投票与真机设置；社区偏好不能替代成功率 |
| [NVIDIA PBench](https://research.nvidia.com/labs/cosmos-lab/pbench/) · [WorldBench](https://world-bench.github.io/) | 物理场景演化、世界生成和物理 AI 评估 | PBench 属 NVIDIA 自建；模型、版本和任务域必须对齐 |
| [QuantiPhy](https://quantiphy.stanford.edu/) | VLM 是否真能从视频估计速度、尺寸和加速度 | 核对视频数据、问题模板和误差指标，不只看总分 |

排行榜只负责提出问题。要写“谁更强”，至少再补官方设置、方法页和自己的同任务复测。

## 监管、资本与公司事实

| 来源 | 用途 |
|---|---|
| [中国网信网](https://www.cac.gov.cn/) · [工业和信息化部](https://www.miit.gov.cn/) · [国家市场监管总局](https://www.samr.gov.cn/) | 中国 AI 政策、备案、内容标识、平台治理和执法原文 |
| [欧盟 AI Act 页面](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) · [AI Office](https://digital-strategy.ec.europa.eu/en/policies/ai-office) | 欧盟法规、实施时间线、GPAI 义务与执法 |
| [NIST CAISI](https://www.nist.gov/caisi) | 美国模型评估、标准与安全研究 |
| [SEC EDGAR](https://www.sec.gov/edgar/search/) · [港交所披露易](https://www.hkexnews.hk/) | 融资、风险、营收、重大合同和上市公司正式披露 |
| 公司 Investor Relations 页面与财报电话会 | 管理层原话、业务数字和资本开支 |

政策稿必须引用法条或官方公告；媒体的“新规解读”只作解释，不代替原文。

## 高质量二级雷达

这些来源适合找角度和理解背景，不作为最终唯一证据：

- [Simon Willison's Weblog](https://simonwillison.net/)：模型与开发工具上手快，常保留原链接和可复现实验。
- [Interconnects](https://www.interconnects.ai/)：开源模型、训练与后训练方法，更新频率稳定。
- [Import AI](https://jack-clark.net/)：论文、能力趋势和政策；作者同时是 Anthropic 联合创始人，涉及 Anthropic 时应视为利益相关观点。
- [Techmeme](https://www.techmeme.com/)：适合看科技圈当前议程和报道聚合；必须回到原文，并区分事件发生时间与进入聚合站的时间。
- [IEEE Spectrum](https://spectrum.ieee.org/)：机器人、芯片和工程落地的高质量发现入口；技术结论继续回到论文或公司材料。
- Reuters、Bloomberg、Financial Times、The Information：人事、融资、组织和供应链线索；尽量寻找文件或第二来源。
- 晚点、36氪、机器之心、InfoQ：国内公司与技术线索；回到企业公告、论文、GitHub 或当事人原帖。

## 监测节奏

### 每日快扫，15–20 分钟

1. 头部实验室 Newsroom 与产品更新日志；
2. API 价格、额度、模型列表、退役和状态页；
3. GitHub/Hugging Face 新 release；
4. Physical AI、机器人公司、世界模型和自动驾驶的一手入口；
5. Techmeme、Hacker News、官方账号、核心研究者和产品负责人的原帖；
6. APPSO、主流媒体与社区只做漏斗入口。

### 每周深扫，60–90 分钟

1. arXiv、OpenReview 和实验室 Research；
2. Artificial Analysis、Epoch、METR、Arena 和 SWE-bench；
3. 监管、财报、招聘页和组织变化；
4. 把可重复的测试任务加入自己的实测库。

### 发布会或模型上线当天

按顺序同时打开：

```text
发布博客
→ 文档 / 定价 / 模型列表
→ 系统卡 / 模型卡 / 论文
→ 产品更新日志与状态页
→ 独立评测
→ 当事人和开发者原帖
→ 自家最小复测
```

媒体报道只负责提醒漏项，不负责替代上述原文。

## 落稿的最低来源门槛

- **发布事实**：至少一个适当的 P0 页面。
- **价格、额度、可用范围**：定价页或更新日志，不引用媒体摘要。
- **能力比较**：厂商结果 + 独立方法页 + 同任务实测；缺一项就降低语气。
- **人物引语**：原帖、原视频或逐字稿；截图必须保留时间和上下文。
- **人事、融资、内部调整**：公司文件 / 当事人确认，或两家相互独立的可信媒体；独家消息保留归属。
- **政策与法律**：官方原文和生效日期。
- **网友案例**：原帖 + 可运行项目或作者说明；不能从一个爆款案例推断普遍能力。

## 选题触发信号

- 更新日志与宣传稿不一致：适合“跑分之外”。
- 价格、额度、缓存、退役或默认入口变化：适合“可用智能”。
- GitHub/Hugging Face 先于发布会出现权重或模型卡：适合快讯，但确认后再发。
- 系统卡脚注与主发布叙事冲突：适合解释稿。
- 同一提示词新旧版本差异明显：适合产品实测。
- 招聘、财报或监管文件透露产品方向：适合趋势稿。
- Physical AI 把学习模型与传统控制拆开：适合写“真正落地不是端到端替代”。
- 世界模型只提升视觉质量、物理和规划指标没有同步改善：适合写“会画世界不等于懂世界”。
- 真机演示没有公布试验数、人工介入和失败恢复：适合做能力边界稿，不写成量产突破。
