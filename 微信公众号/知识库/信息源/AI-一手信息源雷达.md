# AI 一手信息源雷达

- 建档日期：2026-07-10
- 最近复核：2026-07-26
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

## 分钟级发现层

这一层只用于发现近 4–12 小时的新信号，不直接承担事实证明。优先使用带明确时分和机器可读时间戳的入口；页面显示「今天更新」但没有对应条目发布时间时，不进入小时级窗口。

| 类别 | 分钟级入口 | 用法与限制 |
|---|---|---|
| 全球科技议程 | [Techmeme River](https://www.techmeme.com/river) · [Hacker News newest](https://news.ycombinator.com/newest) · [HN Algolia 按时间搜索](https://hn.algolia.com/api/v1/search_by_date?tags=story) | 记录首次进入聚合站的时间，只作为发现线索；回到公司公告、代码、文件或当事人原帖核实 |
| 通讯社与突发报道 | [Reuters AI](https://www.reuters.com/technology/artificial-intelligence/) · [AP Technology](https://apnews.com/hub/technology) | 适合发现事故、人事、融资、诉讼和监管变化；独家消息保留媒体归属，并继续找当事方回应或第二来源 |
| 官方更新订阅 | [OpenAI News RSS](https://openai.com/news/rss.xml) · [GitHub Changelog RSS](https://github.blog/changelog/feed/) · [Google Workspace RSS](https://workspaceupdates.googleblog.com/feeds/posts/default) · [AWS What's New RSS](https://aws.amazon.com/about-aws/whats-new/recent/feed/) | 使用条目自身的发布时间；Feed 的整体刷新时间不能冒充单条公告时间 |
| 模型与代码变化 | [GitHub Releases API](https://docs.github.com/en/rest/releases/releases) · [Hugging Face 最新模型 API](https://huggingface.co/api/models?sort=lastModified&direction=-1&limit=50) · [Hugging Face 最新数据集 API](https://huggingface.co/api/datasets?sort=lastModified&direction=-1&limit=50) | `lastModified`、commit 和 tag 只能证明仓库发生变化；README 小改、量化上传和镜像同步不等于新模型正式发布 |
| 公司与监管文件 | [SEC Current Filings](https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent) · [欧盟 Press Corner](https://ec.europa.eu/commission/presscorner/home/en) · [美国白宫 Briefing Room](https://www.whitehouse.gov/briefing-room/) | 以文件接受时间、公告发布时间和实际生效时间分别记录；搜索引擎收录时间不算事件时间 |
| 新闻稿补漏 | [PR Newswire AI](https://www.prnewswire.com/news-releases/latest-news-topics/artificial-intelligence-list/) · [Business Wire AI](https://www.businesswire.com/newsroom/industry/technology/artificial-intelligence) · [GlobeNewswire](https://www.globenewswire.com/) | 时间通常精确，但商业宣传密度高，统一列为 P3；融资、合作和产品能力必须回到公司、投资方、交易所或技术材料 |
| 官方与负责人原帖 | 公司官方账号、研究负责人、产品负责人、开源项目维护者的原帖 | 保存原帖 URL、账号身份和发布时间；转帖、截图和媒体引用不能代替原帖，删除或编辑过的帖子需注明 |

## 社区与工程信号层

社区入口负责提出问题、暴露异常和发现作品，不负责替事实背书。帖子分数、评论数、Star、下载量和 Trending 都是注意力信号，不是能力、质量、市场采用或真实性证明。

| 入口 | 最适合发现 | 证据边界 | 建议频率 |
|---|---|---|---|
| [HN Newest](https://news.ycombinator.com/newest) · [HN Best](https://news.ycombinator.com/best) | 尚未上首页的发布、冷门工程博客，以及过去 48 小时的高票议题 | 都是 P3；`Best` 只反映 HN 用户偏好，`Newest` 的垃圾与重复更多 | Newest 每日 3–4 次；Best 每日 1 次 |
| [Show HN](https://news.ycombinator.com/show) | 可运行 Demo、开源工具、独立开发产品和新交互 | Demo 存在不等于安全、稳定、有真实用户或效果成立；沿链接回到作者仓库和版本记录 | 每日 1 次 |
| [Ask HN](https://news.ycombinator.com/ask) | 开发者痛点、采购顾虑、真实用法和还没有好答案的问题 | 发帖者身份和经历通常未核实；只能形成问题池，不能外推问题规模 | 每日 1 次 |
| [Launch HNs](https://news.ycombinator.com/launches) | YC 公司正式亮相、创始人答疑、早期定位与价格 | 创始人回答可证明其公开说法，不证明市场需求；同时存在营销与 YC 样本偏差 | 每日 1 次 |
| [HN Algolia](https://hn.algolia.com/) · [API 文档](https://hn.algolia.com/api) · [按时间故事流](https://hn.algolia.com/api/v1/search_by_date?tags=story) | 按公司、模型、作者和域名搜索；追踪 `story`、`comment`、`show_hn`、`ask_hn` | 可能有索引延迟；搜索结果仍只是 HN 内容，不能升级帖子主张 | 关键词每日；发布期 15–30 分钟 |
| [官方 HN API](https://github.com/HackerNews/API) | 拉取 `newstories`、`beststories`、`showstories`、`askstories` 和条目变更 | 帖子 ID、时间和分数可视为平台元数据；帖子内容仍是 P3 | 自动化 10–30 分钟 |
| [Lobsters Active](https://lobste.rs/) · [Newest](https://lobste.rs/newest) · [AI 标签](https://lobste.rs/t/ai) | 系统、编程语言、安全、性能，以及较少炒作的工程讨论 | 邀请制小社区，精度较高但覆盖窄；标签依赖投稿者，不代表 AI 全景 | Active / Newest 每日；AI 每周 2 次 |
| [GitHub Trending](https://github.com/trending) · [Releases API](https://docs.github.com/en/rest/releases/releases) | 突然升温的 Agent、CLI、推理工具，以及白名单仓库的新版本 | Trending 是 P3；只有确认归属的官方仓库 release 才能证明维护者发布了该版本，仍不等于已经部署 | Trending 每日；核心仓库 15–60 分钟 |
| [HF Trending Models](https://huggingface.co/models?sort=trending) · [Recently Updated](https://huggingface.co/models?sort=modified) | 热门模型、权重抢跑、模型卡变化、量化与镜像同步 | Trending 不证明模型新、好或官方；`Updated` 可能只是 README、小文件或镜像变化，只对白名单组织追踪 | Trending 每日；官方组织 30–60 分钟 |
| [HF Daily Papers](https://huggingface.co/papers) · [Trending Spaces](https://huggingface.co/spaces?sort=trending) | 当日论文、代码关联、新应用和交互 Demo | 都是 P3 发现层；论文回原文，Space 还要核对实际后端、模型身份和可复现性 | Papers 工作日每日；Spaces 每周 2 次 |
| [r/MachineLearning New](https://www.reddit.com/r/MachineLearning/new/) · [r/LocalLLaMA New](https://www.reddit.com/r/LocalLLaMA/new/) | 论文复现、失败结果、开源抢跑、量化、VRAM / 速度实测和推理 Bug | 截图与单次跑分不能单独采用；保留硬件、版本、命令、样本和复现记录 | 每日 1–2 次 |
| [r/ClaudeAI New](https://www.reddit.com/r/ClaudeAI/new/) · [r/OpenAI New](https://www.reddit.com/r/OpenAI/new/) | 灰度上线、入口消失、限额变化、区域差异和性能事故先兆 | 可能是 A/B 测试、账号或地区差异；多名用户报告也只触发查状态页、更新日志与自测 | 平时每日；发布或事故期每 1–2 小时 |

每条社区线索固定记录：原帖 URL、作者与自报身份、首次发现时间、所链接的原始材料、是否可复现、独立报告数、官方回应和当前证据级别。多个账号转发同一截图、同一帖子或同一匿名说法，只算一个来源。

不进入核心雷达：通用 AI 工具目录、全球 Hugging Face `Recently Updated` 裸流、GitHub 全站「最近更新」、`r/singularity` 和没有方法信息的榜单截图。它们可以补漏，但噪音密度不值得常驻。

## X 核心账号雷达

- 本轮核验日期：2026-07-26。人物职务和利益关系属于易变信息，引用前重开个人页或机构页。
- 账号没有固定证据等级，单条内容按它实际提供的材料定级：本人宣布自己的动作可作为 P0 的「当事人说法」；转述别人、无日志实测和流量总结仍是 P3；记者独家属于 P2，并保留媒体归属。
- 不把粉丝数、蓝 V、被大 V 转发或历史上猜中过当作真实性证明。
- ★ 表示建议放入日常核心流；其余账号在对应公司、技术或事件进入议程时再重点查看。

### 实验室、公司负责人和研究者

| 人物与账号 | 身份核验 | 最适合看 | 固定限制 |
|---|---|---|---|
| Demis Hassabis [@demishassabis](https://x.com/demishassabis) | [Google DeepMind 联合创始人兼 CEO](https://deepmind.google/about/) | Gemini、AlphaFold、科学智能和实验室动向 | 公司一手源；只能证明 DeepMind 发布或主张了什么，不能独立证明能力 |
| Fei-Fei Li [@drfeifei](https://x.com/drfeifei) | [World Labs 联合创始人兼 CEO](https://www.worldlabs.ai/about) | 空间智能、世界模型、机器人和学术人才 | 创业公司 CEO；演示继续追论文、方法和真实部署条件 |
| ★ Andrej Karpathy [@karpathy](https://x.com/karpathy) | [个人页](https://karpathy.ai/) · [本人公布的当前去向](https://x.com/karpathy/status/2056753169888334312) | 预训练、编码智能、模型直觉和教育型拆解 | 当前与 Anthropic 存在雇佣利益关系；个人体验和预览不能当横向评测 |
| Ilya Sutskever [@ilyasut](https://x.com/ilyasut) | [SSI 官方页](https://ssi.inc/) | SSI 战略、研究方向和人才流动 | 发言少且高度战略化；愿景和招聘不等于已有研究结果 |
| ★ Jack Clark [@jackclarkSF](https://x.com/jackclarkSF) | [Anthropic Institute 官方身份](https://www.anthropic.com/news/the-anthropic-institute) | AI 政策、安全、产业影响和 Import AI | Anthropic 联合创始人；涉及 Anthropic 时不是独立分析源 |
| Jeff Dean [@JeffDean](https://x.com/JeffDean) | [Google Research 官方档案](https://research.google/people/jeff/) | Google 研究、Gemini、训练系统、芯片和基础设施 | Google 一手源；转发论文不代表结果已被独立复现 |
| ★ Jim Fan [@DrJimFan](https://x.com/DrJimFan) | [NVIDIA GEAR Lab](https://research.nvidia.com/labs/gear/) | Physical AI、机器人、世界模型和仿真 | NVIDIA 利益相关；强制区分仿真与实机、遥操作与自主完成 |
| ★ Clément Delangue [@ClementDelangue](https://x.com/ClementDelangue) | [Hugging Face 联合创始人兼 CEO](https://huggingface.co/blog/nvidia-training-cluster) | 开源模型、数据集、Hub、行业合作和政策 | 平台与投资利益明显；下载量和趋势榜不能直接等同模型质量 |
| François Chollet [@fchollet](https://x.com/fchollet) | [ARC Prize 官方团队页](https://arcprize.org/about) | 推理、AGI 定义、基准设计和能力批评 | 同时创建并推广 ARC 生态；单项基准不能外推为通用智能 |
| Daya Guo [@Guodaya](https://x.com/Guodaya) | [个人研究主页](https://guoday.github.io/) | DeepSeek 推理模型、训练方法和论文线索 | DeepSeek 研究者；自己的论文与公司方向是一手说法，跨模型优劣仍需独立评测 |

### 独立技术分析、实测和知识型博主

| 人物与账号 | 身份核验 | 最适合看 | 固定限制 |
|---|---|---|---|
| ★ Simon Willison [@simonw](https://x.com/simonw) | [个人 About 与披露](https://simonwillison.net/about/) | 新模型 / API 实测、提示注入、安全和工具调用 | 接受赞助、厂商预览与免费额度；单一设置实测要保留日志、模型版本和日期 |
| ★ Nathan Lambert [@natolambert](https://x.com/natolambert) | [Interconnects About 与披露](https://www.interconnects.ai/about) | 开源模型、后训练、RLHF 和模型发布评论 | 有付费订阅和顾问关系；旧履历可能滞后，涉及客户时视为利益相关 |
| ★ Hamel Husain [@HamelHusain](https://x.com/HamelHusain) | [个人页](https://hamel.dev/) | 产品评测、错误分析、编码 Agent 和可复现实验方法 | 从事评测咨询与付费课程；客户案例不能直接泛化 |
| Chip Huyen [@chipro](https://x.com/chipro) | [个人官网](https://huyenchip.com/) | 生产级 AI 系统、推理基础设施和 Agent 系统设计 | 作者和创业者身份；综合判断中的新闻事实继续回原始来源 |
| ★ Dylan Patel [@dylan522p](https://x.com/dylan522p) | [SemiAnalysis 创始人、CEO 和首席分析师](https://semianalysis.com/dylan-patel/) | 芯片、数据中心、供应链、训练成本和产业传闻 | 付费研究与咨询；匿名供应链消息保留归因，并找第二来源或公司文件 |
| Max Woolf [@minimaxir](https://x.com/minimaxir) | [个人官网](https://minimaxir.com/) | 图像模型、编码 Agent 和长时间真实使用测试 | 存在雇佣与 Patreon 利益；单用户、单硬件和单提示不能视为通用结论 |
| swyx [@swyx](https://x.com/swyx) | [Latent Space About](https://www.latent.space/about) | AI 工程生态、访谈、开发者趋势和选题线索 | 与会议、媒体、创业和投资生态关系密集；嘉宾表述与产品宣传分开核验 |
| Ethan Mollick [@emollick](https://x.com/emollick) | [Wharton 官方档案](https://mgmt.wharton.upenn.edu/profile/emollick/) | AI 在工作、教育和组织中的实验与实际用法 | 有图书、演讲和顾问利益；小样本任务不能外推整个就业市场 |

### 开源、工程和评测

| 人物与账号 | 身份核验 | 最适合看 | 固定限制 |
|---|---|---|---|
| ★ Georgi Gerganov [@ggerganov](https://x.com/ggerganov) | [GGML / llama.cpp 团队说明](https://huggingface.co/blog/ggml-joins-hf) · [GitHub](https://github.com/ggerganov) | 本地推理、GGUF、量化和 CPU / GPU 性能 | Hugging Face 员工兼项目维护者；项目公告是一手源，跨方案比较需独立基准 |
| ★ Jeremy Howard [@jeremyphoward](https://x.com/jeremyphoward) | [Answer.AI 创始说明](https://www.answer.ai/posts/2023-12-12-launch.html) | 实用开源 AI、模型训练、教育和本地运行 | Answer.AI 有投资与商业目标；教学演示不等于生产规模 |
| ★ Armin Ronacher [@mitsuhiko](https://x.com/mitsuhiko) | [个人官网](https://ronacher.eu/) | 编码 Agent、工具协议、开发体验、安全和工作流 | 当前创业项目利益相关；个人工作流体验不能直接当通用 benchmark |
| Tri Dao [@tri_dao](https://x.com/tri_dao) | [Princeton 官方档案](https://www.cs.princeton.edu/people/profile/td8762) | FlashAttention、Mamba、训练和推理系统 | 同时担任 Together AI 首席科学家；结果依赖硬件、序列长度和实现条件 |
| Sebastian Raschka [@rasbt](https://x.com/rasbt) | [个人 About](https://sebastianraschka.com/about/) | 从零构建 LLM、推理方法和清晰代码解释 | 有图书与教育产品；教学规模实验不能直接外推前沿模型 |
| Shreya Shankar [@sh_reya](https://x.com/sh_reya) | [个人官网](https://shreyashankar.com/) | LLM 评测、DocETL、数据管线和人机协同评估 | 任职时间等易变身份重新核查；课程和工具有自身推广利益 |
| ★ Sasha Rush [@srush_nlp](https://x.com/srush_nlp) | [个人主页](https://srush.github.io/) | 编码模型、后训练、长时程任务和模型研究 | 当前与 Cursor 存在雇佣关系；厂商结果需要第三方复现 |
| ★ Luca Soldaini [@soldni](https://x.com/soldni) | [个人官网](https://soldaini.net/) | 开放训练数据、OLMo、MAI-Thinking 和数据治理 | 当前与 Microsoft 存在雇佣关系；现任身份与此前 Ai2 工作分开写 |

### 流量与知识发现

这一组负责告诉编辑「大家正在看什么」和「哪些原始材料值得点开」，不是事实终点。

| 账号 | 身份核验 | 最适合看 | 固定限制 |
|---|---|---|---|
| Techmeme [@Techmeme](https://x.com/Techmeme) | [聚合与编辑方法](https://www.techmeme.com/about) | 当天科技议程、首发报道和多方评论 | 只作导航；引用回原报道或官方材料 |
| Elvis Saravia [@omarsar0](https://x.com/omarsar0) | [个人介绍](https://elvissaravia.com/about/) · [论文周报仓库](https://github.com/dair-ai/ML-Papers-of-the-Week) | 论文、开源项目和教程 | 回到论文、代码和模型卡，并核对版本与评审状态 |
| Alex Volkov [@altryne](https://x.com/altryne) | [ThursdAI About](https://thursdai.news/about) | 每周模型、开源项目和开发者访谈扫盘 | 嘉宾表述按厂商或当事人自述记录，继续找录音、转录、仓库和发布说明 |
| Gergely Orosz [@GergelyOrosz](https://x.com/GergelyOrosz) | [The Pragmatic Engineer About](https://blog.pragmaticengineer.com/about/) | AI 编程工具、公司采用、裁员和研发组织变化 | 匿名员工线索保留「据其报道」，再查备忘录、招聘页、文件或第二媒体 |
| Rowan Cheung [@rowancheung](https://x.com/rowancheung) | [The Rundown AI 作者页](https://www.therundown.ai/authors/4e458ac6-5b2d-4899-bb53-f7c818244c6d) | 高速传播的 AI 产品、演示和人物动态 | 只作流量预警；不引用线程总结，必须打开原链接并复现实测 |

### 中文转译与工具发现

| 账号 | 最适合看 | 固定限制 |
|---|---|---|
| 宝玉 [@dotey](https://x.com/dotey) | 英文长文、访谈、产品用法的中文转译与补充语境 | 转译不是原始引语；人物原话回原帖、视频或逐字稿逐句核对 |
| 歸藏 [@op7418](https://x.com/op7418) | AI 图像、视频、设计和工具上线 | 属 P3 产品发现；版本、价格、可用地区和案例回官方材料并自行复测 |
| 向阳乔木 [@vista8](https://x.com/vista8) | AI 工具、工作流和中文圈传播信号 | 区分亲测、转述和推广；联盟链接、赞助或赠送资格登记利益关系 |
| ZHO [@ZHO_ZHO_ZHO](https://x.com/ZHO_ZHO_ZHO) | 图像 / 视频生成工作流、提示与案例 | 案例只证明特定版本和设置能得到该结果，不证明稳定性与普遍效果 |

### 产品逆向与功能预告

| 账号 | 身份或方法核验 | 最适合看 | 固定限制 |
|---|---|---|---|
| Tibor Blaho [@btibor91](https://x.com/btibor91) | [TechCrunch 对其历史命中与 Operator 线索的说明](https://techcrunch.com/2025/01/20/openais-agent-tool-may-be-nearing-release/) | ChatGPT、Claude 的 bundle、APK、功能门控和价格线索 | 字符串或 flag 只能写「代码中出现痕迹」，不能写「即将发布」 |
| TestingCatalog [@testingcatalog](https://x.com/testingcatalog) | [方法与纠错说明](https://www.testingcatalog.com/about/) | ChatGPT、Gemini、Claude、Grok、Perplexity 和 Copilot 的 A/B 测试 | 保留其 Confirmed / Testing / Rumor 状态；只认 `testingcatalog.com` 官方站 |
| AssembleDebug [@AssembleDebug](https://x.com/AssembleDebug) | [Android Authority 作者页](https://www.androidauthority.com/author/AssembleDebug/) | Gemini、Google App、Android 和 Pixel | 记录 APK 版本、构建号和代码位置；隐藏功能可能永不发布 |
| Alessandro Paluzzi [@alex193a](https://x.com/alex193a) | [2026 年 Meta Pocket 线索的后续核实案例](https://techcrunch.com/2026/07/02/meta-quietly-launches-vibe-coded-gaming-app-pocket/) | Meta、Instagram、Threads、WhatsApp 和 AI 界面原型 | 区分内部原型、有限测试、商店上线和正式发布 |
| Aaron Perris [@aaronp613](https://x.com/aaronp613) | [MacRumors 作者页](https://www.macrumors.com/author/aaron-perris/) | Apple、iOS、Siri、AI 硬件、固件和设备标识 | 设备 ID、资源名和字符串不能推出最终名称、规格或发布时间 |
| WABetaInfo [@WABetaInfo](https://x.com/WABetaInfo) | [身份与方法说明](https://wabetainfo.com/about/) | WhatsApp、Meta AI 和消息产品 Beta 功能 | 保留版本及「开发中／部分测试／逐步推送」原状态 |

### 具编辑标准的记者与独家源

记者的 X 账号负责报警，署名报道才是可引用的 P2。匿名信源报道永远保留媒体和记者归属。

| 记者与账号 | 身份核验 | 最适合看 | 固定限制 |
|---|---|---|---|
| Deepa Seetharaman [@dseetharaman](https://x.com/dseetharaman) | [职业背景](https://nationalpress.org/speaker/deepa-seetharaman/) | OpenAI、AI 公司内部事故、战略和监管诉讼 | 写「Reuters 援引消息人士报道」，并查公司回应、法院文件或第二来源 |
| Kenrick Cai [@kenrickcai](https://x.com/kenrickcai) | [当前作者资料](https://muckrack.com/kenrick-cai) | Alphabet、Google DeepMind、云业务和 AI 投资 | 路线图、发布日期和产品规格等待 Google 官方材料确认 |
| Krystal Hu [@readkrystalhu](https://x.com/readkrystalhu) | X 简介与 Reuters 署名报道 | 融资、交易、VC 及中美 AI 公司动态 | 融资目标、估值和实际到账分开；另查监管文件、投资方和公司回应 |
| Alex Heath [@alexeheath](https://x.com/alexeheath) | [Sources 方法与履历](https://sources.news/about) | OpenAI、Meta、管理层、内部备忘录和组织变化 | 匿名独家始终保留归属；采访内容属于受访者自述 |
| Amir Efrati [@amir](https://x.com/amir) | [The Information 作者页](https://www.theinformation.com/u/amirefrati) · [编辑团队](https://www.theinformation.com/about) | OpenAI、Google、自动驾驶和公司内部消息 | 不依据付费墙外的二手摘要扩写；匿名信源需要第二来源或官方材料 |
| Mark Gurman [@markgurman](https://x.com/markgurman) | [Bloomberg 官方作者页](https://www.bloomberg.com/authors/AS7Hj1mBMGM/mark-gurman) | Apple 路线图、Siri、AI 硬件、供应链和高管变动 | 严格区分「讨论」「开发中」「测试中」「计划发布」和「已发布」 |
| Rachel Metz [@rachelmetz](https://x.com/rachelmetz) | [Bloomberg 官方作者页](https://www.bloomberg.com/authors/AWOWHOIGgDM/rachel-metz) | 模型公司、产品发布、AI 商业和政策 | 独家细节保留 Bloomberg 归属；能力和日期回厂商文档、论文及实测 |
| Casey Newton [@CaseyNewton](https://x.com/CaseyNewton) | [Platformer About](https://www.platformer.news/about) | Meta、X、内容治理、AI 平台政策和组织消息 | 分开登记独家事实、采访自述与作者分析；涉及 Anthropic 时查看其利益披露 |

### 「小道消息」验真门

不存在能够保证真实性的爆料账号。可以保证的只有核验路径、归因方式和在证据不足时不升级措辞。

| 状态 | 最低条件 | 可以怎么写 | 不可以怎么写 |
|---|---|---|---|
| 已确认 | 官方公告、文档、商店正式版本、监管 / 交易所 / 法院文件或当事人明确确认 | 按 P0 材料准确描述，并保留发布时间、范围和限制 | 不能把官方自报能力写成独立验证 |
| 可复现迹象 | 公开客户端或网页构建、明确版本、代码 / 资源位置、可访问测试入口或其他可复查工件 | 「在版本 X 的代码 / 测试入口中出现……」 | 不能推出最终名称、发布时间、价格、全量范围或一定会上线 |
| 具名独家 | 有编辑标准的媒体署名报道，清楚使用「据知情人士」「文件显示」等来源措辞，并尽量包含公司回应 | 「据 Reuters / Bloomberg / The Information 等报道……」 | 不能去掉媒体归属改写成「公司已经……」；同一独家的转述不算第二来源 |
| 未验证传闻 | 匿名截图、群聊转述、无原链流量帖、无法复现的「朋友说」或单个匿名账号 | 只进内部观察队列，继续找公开工件、当事人或记者报道 | 不进入标题、摘要、正文事实卡和「最新」窗口 |

每条非官方线索至少记录：`claim_text`、原帖 URL、账号身份、首次发布时间、发现时间、应用与构建版本、地区与账号条件、复现路径、公开工件 URL、独立来源数、官方回应、利益关系、当前状态和最后复核时间。

固定判定规则：

1. 多个账号转发同一截图、同一匿名爆料或同一媒体独家，只算一个来源；引用链不等于独立确认。
2. 逆向内容必须保存版本、构建号、地区、账号和复现路径；字符串、资源和 feature flag 只证明开发痕迹存在。
3. 记者独家必须保留媒体与记者归属；只有官方文件或第二个互不依赖的可靠来源出现，才升级为已证实事实。
4. 截图必须能回到原帖或可复查工件；只有截图、没有原链时，不承担事实证明。
5. 赞助、免费额度、预览资格、雇佣、咨询、课程、图书、投资、自有 benchmark 和联盟链接都属于利益关系。
6. 账号删错不改、反复把猜测写成事实、伪造截图或长期不给原链时，从核心池降为隔离观察；单条新内容只有附可复现工件时才重新进入核验队列。

### X 列表与扫描顺序

建议建立 4 个互不混合的列表，并使用按时间排序，不依赖「For You」：

1. `01-当事人与官方`：实验室负责人、研究者和官方账号；
2. `02-技术与实测`：知识型博主、开源维护者和评测账号；
3. `03-流量与议程`：聚合、中文转译和流量博主；
4. `04-逆向与独家`：产品逆向者和具编辑标准的记者。

日扫先看 `01` 和 `04`，再用 `02` 判断技术含义，最后用 `03` 判断传播热度。发现同一消息时，沿引用链回到最早的原帖、工件或署名报道，不以转发量最高的帖子作为源头。

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

### 近 6 小时扫描

1. 先固定当前北京时间和 6 小时窗口起点。
2. 先扫 RSS、API、Techmeme River、通讯社和官方原帖，再扫普通网页搜索。
3. 每条线索同时记录 `source_created_at`、`official_announced_at` 和 `rediscovered_at`；只有前两项能够进入小时级窗口。
4. 找到媒体独家时，立即寻找公司回应、监管文件、代码、模型卡或当事人原帖；暂时没有时保留媒体归属，不改写成已核官方事实。
5. 只有日期、没有时分的官方页面，只能列为「今天发布」；新闻稿平台、仓库 `lastModified` 和聚合站时间不能替代真正发布时间。
6. 没有同时满足「窗口内首次出现、一手材料可回源、读者后果具体」的候选时，明确报告暂无，不用旧新闻凑数。

### 每日快扫，15–20 分钟

1. 先扫分钟级发现层的 RSS、API、Techmeme River、通讯社和官方原帖；
2. 再看头部实验室 Newsroom 与产品更新日志；
3. 核对 API 价格、额度、模型列表、退役和状态页；
4. 检查 GitHub / Hugging Face 新 release、tag、模型卡和许可证；
5. 检查 Physical AI、机器人公司、世界模型和自动驾驶的一手入口；
6. APPSO、主流媒体、新闻稿平台与社区只做漏斗入口。

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
