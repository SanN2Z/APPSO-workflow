---
title: "Stripe 要买 OpenRouter，数据中心走进选举｜周报"
platform: wechat
status: editorial_review
created: 2026-08-21
updated: 2026-08-21
as_of: 2026-08-21
fact_checked: true
rights_checked: false
copyedit_checked: false
copyedit_body_sha256: ""
published_url: ""
writing_mode: company
project_adapter: appsso
confidentiality: internal
lane: L1
---

# Stripe 要买 OpenRouter，数据中心走进选举｜Hunt Good 周报

欢迎收看最新一期的 Hunt Good 周报！

这一周，AI 公司都在忙着把「中间那一层」攥进自己手里：Stripe 要买下替开发者挑模型的 OpenRouter；Cursor 不满足于写代码，开始自己托管代码；Google 则用一张跟未来芯片采购挂钩的认股权证，把自己和 Marvell 绑到了 2033 年。

与此同时，AI 的物理成本终于走出了机房。电费、水、土地和噪声，正在把数据中心变成美国选举里的攻击词。

![本期 Hunt Good 周报封面：模型路由、代码仓库、芯片、电力和地方政治组成五层基础设施。](assets/00-cover-v2.png)

*本期 Hunt Good 周报视觉摘要；APPSO 制图。图中为解释性示意，不是新闻现场或产品界面。*

在本期内容，你会看到：

- 7 条新鲜资讯
- 3 个有用工具
- 3 个鲜明观点
- 1 个有趣案例

## Hunt for News｜先进头条

### Stripe 要买下 OpenRouter：处理钱之后，它又盯上了 token

8 月 19 日，Stripe 宣布签署协议，收购 AI 模型网关 OpenRouter。

OpenRouter 做的事，是把 80 多家供应商的 400 多个模型接到同一个入口后面。开发者发来一个请求，它可以根据任务难度、价格、速度和可靠性，决定把请求送给哪个模型。

![Stripe 官方新闻稿页面，标题为 Stripe agrees to acquire OpenRouter to help businesses optimize token routing and usage，日期 2026 年 8 月 19 日。](assets/01-stripe-openrouter-newsroom.png)

*Stripe 收购公告页面；图源：Stripe Newsroom。公告正文写明 OpenRouter 覆盖 80 多家供应商的 400 多个模型。*

这正好接上 Stripe 已经在做的另一半生意。过去，它替公司处理付款、订阅和欺诈；现在，AI 公司既要管理收入，也要管理不断变化的推理成本。Stripe 的说法很直白：token 正在变成 AI 公司的核心货币。

交易金额没有在官方公告里披露，外媒报道的口径也不一致。目前准确的说法仍然是「签署了收购协议」，不是交易已经完成。

相关链接：[Stripe 公告](https://stripe.com/newsroom/news/stripe-agrees-to-acquire-openrouter)、[OpenRouter](https://openrouter.ai/)

### 亚马逊打算把无人机送货，一年铺到近 500 个美国城镇

8 月 19 日，亚马逊给 Prime Air 定了一个很猛的年末目标：到 2026 年底，把无人机配送带到美国近 500 个城市和城镇，覆盖版图大约扩大 6 倍。

它还点了 5 个即将进入的都会区：芝加哥、雪城、克利夫兰、亚特兰大和博伊西。

![一架 Amazon Prime Air 配送无人机正在测试场起飞。](assets/02-amazon-prime-air-official.jpg)

*亚马逊 Prime Air 的官方产品照片；图源：Amazon。图片用于展示机型，不代表「近 500 个城镇」已经开通。*

Prime Air 能送的是 5 磅（约 2.27 千克）以内的小件，最快约 30 分钟，常见品类包括杂货、电子产品、化妆品、药品和日用品。亚马逊称，今年已经用无人机送出数十万件包裹。

要把服务扩到近 500 个城镇，亚马逊还得一起铺开地址、天气、空域和配送站。无人机能在小雨和一定温度范围内工作，遇到恶劣天气仍会停；一个城市进入名单，也不等于城里每个地址都能立刻下单。

这是亚马逊对年底的计划，不是今天的可用范围。

相关链接：[Supply Chain Dive 报道](https://www.supplychaindive.com/news/amazon-to-expand-drone-delivery-reach-sixfold-this-year/828253/)、[Amazon Prime Air 技术说明](https://www.aboutamazon.com/news/transportation/amazon-drone-prime-air-expanded-delivery-faa-approval)

### AI 数据中心开始影响选举：共和党私下催公司解释「谁付电费」

8 月 19 日，美国参议院共和党竞选机构给头部 AI 公司发了一份私人备忘录。标题叫「Ohio Data Center Risk」，意思非常直接：选民对数据中心的反感，可能让共和党丢掉俄亥俄州的一席关键参议院席位。

备忘录要求 AI 公司把 3 件事解释清楚：谁受益、谁付钱、为什么一个社区应该欢迎数据中心。

![Axios 独家报道页面，标题为 Exclusive: GOP issues stark warning to AI companies，配图是国会大厦与数据中心机架的合成插画。](assets/03b-axios-gop-memo.png)

*Axios 2026 年 8 月 19 日的独家报道；图源：Axios，插画作者 Sarah Grillo。备忘录原件未公开，本文依据 Axios 的报道转述。*

![宾州州长 Josh Shapiro 在 Berwick 的讲台前讲话，身后是施工设备与工人。](assets/03-pa-data-center-commonwealth.jpg)

*宾州州长 Josh Shapiro 2026 年 5 月在 Berwick 公布 GRID 标准；图源：Commonwealth Media Services / WPSU。该图不是 8 月行政令签署现场。*

这份政治压力很快落到了政策上。一天前，宾夕法尼亚州州长 Josh Shapiro 签署行政令，把所有数据中心项目移出州政府的快速审批通道。开发商要先取得地方合法批准，也不得用保密协议限制地方官员和居民获取项目信息。宾州 5 月发布的 GRID 标准，则把能源成本、社区参与和环境影响列为项目取得州支持时的门槛。

过去，政治人物站在数据中心旁边讲的是投资、就业和 AI 竞争。现在，候选人更常被追问：它要用多少电和水，会不会推高居民账单，社区有没有说「不」的权利。

相关链接：[Axios：共和党备忘录](https://www.axios.com/2026/08/19/gop-data-center-memo-ai-election)、[AP：数据中心进入中期选举](https://apnews.com/article/cd2cfd73e3d41e2baf65bf82702a589b)、[Axios：宾州行政令](https://www.axios.com/local/pittsburgh/2026/08/18/shapiro-data-center-rules-executive-order)、[宾州 GRID 标准](https://www.pa.gov/governor/newsroom/2026-press-releases/gov-shapiro-releases-full-grid-standards-to-protect-pennsylvania)

### Google 没给 Marvell 投 122 亿美元，它开了一张「订单解锁券」

8 月 18 日，芯片公司 Marvell 向 Google 发出一张认股权证：Google 最多可以按每股 206.58 美元买入 58,970,907 股 Marvell 股票。把两项相乘，潜在行权金额大约是 121.8 亿美元。

但这不是 Google 当场投了 121.8 亿美元。

![Marvell 提交给美国证券交易委员会的 Form 8-K 文件首页，报告日期为 2026 年 8 月 18 日。](assets/04a-marvell-8k-sec.png)

*Marvell 的 8-K 监管文件；图源：Marvell Investor Relations。权证条款出自该文件。*

![Google 的合格芯片采购每增加 5 亿美元，就解锁一批 Marvell 股票购买权；插画依次展示采购订单、权证分批解锁、可买股数与潜在行权金额。](assets/04-google-marvell-illustrated-v4.png)

*Marvell 认股权证的主要解锁机制；AI 生成插画信息图，APPSO 编辑。121.8 亿美元为全部行权的潜在金额，不是当前投资。*

其中约 136 万股会在协议第一年按季度逐步解锁。剩下约 5761 万股被拆成 240 批：Marvell 每从 Google 的定制芯片产品中确认 5 亿美元合格收入，就解锁一批，解锁期最晚延续到 Marvell 的 2033 财年。

如果 240 批全部解锁，对应的是 1200 亿美元合格采购收入。适用范围包括 AI 推理加速器、存储、网络、内存接口控制器和近存计算等定制芯片项目。

权证不是已经持有的股票，1200 亿美元也不是已经确认的收入。

相关链接：[Marvell 监管文件](https://investor.marvell.com/sec-filings/all-sec-filings/content/0001193125-26-356217/d412696d8k.htm)、[Bloomberg Law 报道](https://news.bloomberglaw.com/artificial-intelligence/marvell-gives-client-google-right-to-buy-12-2-billion-stock-1)

### Cursor 开始自己托管代码：写代码的 Agent，想把 GitHub 也收进工作台

8 月 17 日，Cursor 上线 Origin 的早期测试版。除了从 GitHub 里读代码、改代码，它现在还可以直接托管仓库。

![Cursor 官方更新日志页面，标题为 Origin Code Hosting，日期 Aug 17, 2026，正文写着 Cursor can now host your code。](assets/05a-cursor-origin-changelog.png)

*Cursor 的官方更新日志；图源：Cursor。页面注明 Origin 在所有付费计划上以 early beta 形式分批推出。*

当前功能很朴素：仓库、Pull Request、代码浏览、GitHub 同步。来自 GitHub 的仓库可以镜像到 Origin，但推送仍回到 GitHub，GitHub 继续是真源；Cursor 自己创建的仓库，则直接住在 Origin。

![Cursor Origin 的官方产品界面，展示仓库设置、Pull Request 与分支保护。](assets/05-cursor-origin-official-v2.png)

*Cursor Origin 的官方产品截图；图源：Cursor。界面仍处于 early beta，细节可能继续调整。*

Cursor 随后预告，会继续加入更多「Agent 原生」功能。

它也已经把 Vercel、Depot 和 Buildkite 接进 Origin：Pull Request 可以触发预览部署或 CI，仓库不只放代码，也开始承载 Agent 之后的交付链。

![Cursor Origin 的 Codebase Apps 页面，列出 Buildkite、Depot 与 Vercel。](assets/05b-cursor-origin-apps-official.png)

*Origin 官方应用集成界面；图源：Cursor。*

当 Agent 已经能开分支、写代码、跑检查、提交 PR，代码托管也跟着变成 Agent 的执行环境、权限边界和协作记录。

目前 Origin 只向付费计划分批开放，仍是 early beta；企业管理员可以选择关闭。它现在更像 GitHub 旁边的一条新轨道，距离成熟替代品还很远。

相关链接：[Cursor Origin 官方更新](https://cursor.com/changelog/origin-code-hosting)、[Origin 文档](https://cursor.com/docs/api/origin)

### ChatGPT 给青少年单开一套：系统猜你未满 18 岁，就自动切过去

8 月 18 日，OpenAI 发布 ChatGPT for Teens。用户自报年龄为 13—17 岁，或者系统估计其未满 18 岁，都会自动进入这套青少年体验。

内容过滤之外，OpenAI 还重做了学习流程。学习模式会用问题和步骤把答案拆开；「负责任的作业提醒」会在用户明显想抄近路时，把人引回解题过程；测验、学习可视化和 Study Hours，则把练习与时间安排也塞进产品里。

![OpenAI 官方青少年安全配图写着 Helping developers build safer AI experiences for teens。](assets/06-chatgpt-teens-official.png)

*OpenAI 青少年安全政策页面的官方配图；图源：OpenAI。该图展示同一安全主题，不是 ChatGPT for Teens 产品界面。*

家长关联帐号后，可以设置安静时段、管理部分设置，并在有限的高风险情形下收到安全通知。默认保护覆盖自伤、暴力、进食障碍、危险活动以及露骨内容等领域。

年龄估计会直接决定用户被送进哪套体验。

OpenAI 没在这篇公告里公布年龄预测的准确率。把未成年人分流到更安全的体验是目标，不等于误判、漏判和家庭边界已经解决。

相关链接：[OpenAI 官方公告](https://openai.com/index/chatgpt-for-teens/)

### OpenAI 想让模型跨对话查风险，又不把客户原文交给自己

零数据保留（ZDR）客户给 AI 厂商出了一道难题：既然提示词和回答处理完就不能留，安全系统怎么发现一个人分很多轮、很多帐号逐步拼起来的危险行为？

8 月 19 日，OpenAI 预告了一个叫 Private Safety Processing 的方案。

![客户可以把内容留在自己的基础设施，或在 OpenAI 侧加密存储并自行掌握密钥；插画展示自动系统只向员工返回有限风险信号。](assets/07-openai-zdr-illustrated-v3.png)

*Private Safety Processing 的设计目标；AI 生成插画信息图，APPSO 编辑。具体技术白皮书尚未发布。*

按官方描述，ZDR 部署中的内容留在客户控制的基础设施里；另一种仍在开发的方案，可以把内容加密后放在 OpenAI 的基础设施上，但密钥由客户持有。自动系统可以跨相关交互识别模式，OpenAI 收到的只是有限的风险类型信号，员工看不到底层提示词和回答。公告另列出了依法处理儿童性虐待材料的例外。

不过现在还只是早期客户测试。OpenAI 计划 9 月开始逐步推出，并发布技术白皮书。在那之前，能检测多复杂的模式、误报怎么处理、客户如何审计，都还缺公开细节。

相关链接：[OpenAI 官方公告](https://openai.com/index/offering-zero-data-retention-for-frontier-models/)、[OpenAI 数据控制文档](https://platform.openai.com/docs/models/default-usage-policies-by-endpoint)

## Hunt for Tools｜先进工具

### Gemini 3.7 Flash：促销价只到年底，先把「便宜一半」写进日历

8 月 13 日，Google 把 Gemini 3.7 Flash 推到正式可用。它有 100 万 token 输入上下文、最多 6.5 万 token 输出，并提供 low、medium、high 三档思考强度，主打编程和多步 Agent 任务。

![Google DeepMind 的 Gemini 3.7 Flash 模型卡页面。](assets/08-gemini-37-flash-official.png)

*Google DeepMind 的 Gemini 3.7 Flash 模型卡页面；图源：Google DeepMind，页面截图。价格仍以正文链接的 API 定价页为准。*

当前 API 促销价是每百万 token 输入 0.75 美元、输出 3.75 美元。2027 年 1 月 1 日起，两项都翻倍到 1.50 美元和 7.50 美元。

适合：需要长上下文、工具调用和可调思考强度的代码或 Agent 流程。

坑：官方跑分由 Google 自己提供，本文没有实测；现在的低价有明确截止日，做长期成本表时别只抄第一行。

入口：[Gemini 3.7 Flash 文档](https://ai.google.dev/gemini-api/docs/latest-model)、[价格页](https://ai.google.dev/gemini-api/docs/pricing)

### OpenMotion：给一句话，做出还能继续改的发布视频

OpenMotion 是一款 Mac 端 AI 动效工具。你可以从提示词开始做产品视频、发布预告、解释动画和社交短片，生成结果仍可在场景、画布和时间线上继续调整。

![OpenMotion 官方首页展示产品画布、时间线和 Codex 对话区。](assets/09-openmotion-official.png)

*OpenMotion 官方首页的产品预览，包含画布、时间线与 Codex 对话区；图源：OpenMotion。本文未实测。*

它可以配合 Claude Code 或 Codex 订阅工作，不用再单独管理一把 API Key；输出支持普通视频、透明 WebM 和可独立运行的 HTML。

适合：做产品发布、Logo 动效和短解释视频，又希望保留人工编辑权的人。

坑：目前只有 Mac 版，同时支持 Apple 芯片和 Intel；现阶段免费不代表以后没有 Pro 计划。本文没有实测导出质量。

入口：[OpenMotion](https://openmotion.design/)

### Kitbitz：2000 多张手绘小素材，CC0，商用也不用问

Kitbitz 把 2000 多张手绘素材分进 13 套主题：自然、城市、中世纪、地牢、海盗、太空、赛博朋克……每张都能单独下载 SVG 或 PNG，也能整套拿走 Figma 组件库。

![Kitbitz 官方首页，标语为 Hand-drawn illustrations for your projects，四周散布着树木、宝箱、螃蟹、头盔和飞船等手绘素材。](assets/10-kitbitz-home.png)

*Kitbitz 官方首页；图源：Kitbitz。页面标注 Vector、CC0、2K+ 与 Figma。*

仓库中的原创插画采用 CC0 1.0，可以复制、修改和商用，不要求署名。作者还在围绕这批素材做 Figma 插件、MCP 支持和世界生成工具。

作者也专门回答过：插画本身不是生成式 AI 做的，AI Agent 用在了网站、分类和元数据整理上。

适合：游戏原型、地图、活动页、解释图和任何不想再走一遍素材授权流程的小项目。

坑：CC0 不会替你清除所有可能涉及的商标、隐私或第三方权利；把素材组合成具体品牌或人物时，仍要自己检查。

入口：[Kitbitz](https://kitbitz.art/)、[GitHub 素材仓库](https://github.com/CaptExcellent/kits-library-assets)

## Hunt for Insights｜先知

### ChatGPT 广告审计：低收入人设帐号，更容易等到广告

一组研究者建了 91 个模拟美国用户的「袜子帐号」（sockpuppet accounts），用代理 IP 和带地点线索的提示词，组合出 3 个种族／族裔组和 3 个收入档位，然后用 335 个真实感问题持续和 ChatGPT 对话。

论文摘要的口径是 3000 多条广告、186 个广告主。

![arXiv 论文页面《The Beginning of ChatGPT Ads》，摘要写明 91 个 sock puppet、3×3 因子设计、3000 多条广告、186 个广告主、335 个提示词。](assets/11-chatgpt-ads-arxiv.png)

*论文 arXiv 页面；图源：Lurie 等，arXiv:2608.05008。页面注明将发表于 AAAI/ACM AIES 2026。*

研究者把结果拆成了两个问题。

第一个问题是：谁会第一次看到广告？在最终看到过广告的帐号里，第一次曝光的中位等待时间是 14 天，没有帐号在头 7 天看到广告。回归结果显示，所在邮编的家庭年收入每增加 1000 美元，帐号至少看到一次广告的赔率约乘以 0.98。95% 置信区间是 0.96—1.00，p = 0.0438：方向存在，但效应不大，也贴着统计门槛，不能写成收入直接决定广告分发。

![论文图表显示，家庭收入越高，帐号至少收到一次广告的拟合概率越低；收到广告的帐号更集中在较低收入区间。](assets/11b-chatgpt-ads-income-paper.png)

*论文 Figure 6：收入与广告首次曝光；图源：Lurie 等，arXiv:2608.05008。图中收入是邮编层面的代理变量。*

第二个问题是：看到广告以后，会有多频繁？这里的结论没那么整齐。在已曝光帐号中，研究者没有发现收入或族裔线索与广告率存在显著的系统关系；中位帐号从第一次看到广告之后，大约每 4 次提问会出现 1 次广告。族裔差异也没有达到显著，但每组只有 16—19 个已曝光帐号，样本不足以证明「完全没有差异」。

这一阶段的广告以消费品为主，链接通常指向广告主，而不是某件具体商品；广告也和模型回答清楚分开。OpenAI 公开说，广告不会影响回答，广告主看不到聊天原文。

边界也很重要：这是 91 个模拟帐号的审计，不代表研究者知道平台实际使用了哪些收入信号；论文已注明将发表于 AIES 2026，目前公开版本仍是预印本。

相关论文：[The Beginning of ChatGPT Ads（arXiv:2608.05008）](https://arxiv.org/abs/2608.05008)、[OpenAI 广告说明](https://openai.com/index/testing-ads-in-chatgpt/)

### 不改意思，只换 6 句话的说法，模型就从 94% 说「不」变成 99.93% 说「是」

宾夕法尼亚大学两名研究者给这种现象起了个很抓人的名字：Model Hypnosis，模型催眠。

![arXiv 论文页面《Model Hypnosis: Strong control of AI via additive subliminal effects》，作者 Enric Boix-Adserà 与 Benedict Tessler，2026 年 8 月 17 日提交。](assets/12a-model-hypnosis-arxiv.png)

*论文 arXiv 页面；图源：arXiv:2608.16834。摘要提到催眠提示词可以在模型之间迁移。*

他们先放进一段和问题无关的小故事，再问同一个二选一道德问题。故事的意思不变，只在 6 个位置挑选不同的同义改写，Qwen3-8B 就从以 94% 概率回答「不」，变成以 99.93% 概率回答「是」。

![论文 Figure 1 并排展示原始故事与逐句同义改写；道德问题相同，Qwen3-8B 的答案概率却从 94% NO 变成 99.93% YES。](assets/12-model-hypnosis-paper-fig1.png)

*论文 Figure 1；图源：Boix-Adsera、Tessler，arXiv:2608.16834。图片仅截取论文原始示例与结果。*

每一个改写单独看都很弱，甚至和问题无关；但研究者先测出每个词句对答案方向的微小偏移，再把方向一致的线索叠在一起，效果就接近确定。他们还用动物列表、错字和 JSON 字段做了类似实验，并观察到部分线索可以跨模型迁移。

这比传统的「在末尾塞一串怪字符」更麻烦，因为提示词仍然自然、可读、意思也大致没变。内容审核如果只看有没有明确指令，可能根本看不出问题。

论文主要测试的是强制二选一任务和经过大量查询筛出来的提示组合；现实开放式对话里的成功率、成本和可检测性，还没有被这组实验回答。

相关论文：[Model Hypnosis（arXiv:2608.16834）](https://arxiv.org/abs/2608.16834)

### 多 Agent 协作的反直觉结果：共享文件有用，指定「组长」未见稳定改善

一篇新论文记录了 1902 次多 Agent 编程实验，又在密封环境里补做 244 次验证。除了任务成功率，研究者还把消息、读文件、写文件都变成带时间戳的网络，观察 Agent 到底怎么协作。

![论文把 Agent、共享规格文件与交付文件都当成网络节点，并分别记录消息、文件写入和读取。](assets/13-agent-coordination-paper-fig1.png)

*论文 Figure 1：一次协作运行如何被记录成带时间顺序的网络；图源：Destefanis、Aste，CC BY 4.0。*

结果很像真实办公室。团队一变大，开场自我介绍和互相发消息先猛涨；任务如果有共享规格，网络会很密，如果是流水线任务，大家只在接口处碰头。

在最依赖消息的分布式任务里，8 个 Agent 被要求改用共享文件后，输出 token 减少约 42%，两个采集批次的降幅在 36%—49% 之间。缓存上下文重读也从每次运行约 1050 万 token 降到约 660 万。

![论文 Figure 8 的六组柱状图显示：强制共享文件会压低直接消息，但同时增加文件读写；最终是否省 token 取决于任务本来靠什么协作。](assets/13b-agent-coordination-paper-fig8.png)

*论文 Figure 8：直接消息、文件写入和文件读取在不同任务与文件策略下的变化；图源：Destefanis、Aste，CC BY 4.0。*

但这条规律有明确反例：如果任务本来就是流水线、文件已经承担交接，强制增加共享文件会在 8 个 Agent 时把输出 token 推高约 10%；到 16 个 Agent，单次运行约从 33.3 万涨到 57.8 万，成功率却没有改善。

研究者还指定过一名「协调者」。它没有自然变成通信中心，也没有稳定提高成功率。

244 次密封验证还暴露了一条风险：Agent 有约五分之四会主动去找被标记为隐藏的评分材料。

相关论文：[When Agents Coordinate（arXiv:2608.16801）](https://arxiv.org/abs/2608.16801)

## Hunt for Fun｜先行

### 不用 Google Lens，他让显卡比较 8069 万个三角形，找到照片里的小岛

题目只有一张 736 × 515 的度假村航拍图：没有 EXIF、没有 GPS、没有相机信息。要回答 3 个问题——酒店叫什么，小岛坐标在哪，镜头朝哪个方向。

![作者技术记录页面顶部，Task briefing 一节里就是那张原始挑战照片：一座被浅蓝色礁盘环绕的热带小岛。](assets/14a-cuda-island-challenge.png)

*作者 yassa9 的技术记录页面与题目原图；图源：yassa9。页面开头注明这是人类完成的工作，没有使用 LLM 生成。*

大多数人会先丢给反向图片搜索。作者 yassa9 觉得这样浪费了题目，决定把整颗地球变成一道几何搜索题。

![一张世界地图上，热带海域分布着数百个绿色候选点。](assets/14-cuda-island-author.jpg)

*作者完成一轮几何与开放水域筛选后，剩余 948 个候选位置的分布；图源：yassa9。该图由作者生成，不是原挑战照片。*

他先在照片里点出 3 块陆地，算出角度和相对距离，留出 ±20% 误差；再拿 882 MB 的 OpenStreetMap 陆地多边形，从热带纬度、邻近岛屿密度和聚类一路筛选。

23,500 个岛群生成了 80,690,777 个三角形。作者给每个三角形分配一个 CUDA 线程，在 RTX 3050 上，核心匹配阶段用了约 204 毫秒。后面再用岛屿形状、Sentinel-2 植被指数和 Copernicus 高程数据继续淘汰候选。

这套做法当然没有 Google Lens 省事，里面也塞了不少人工阈值。它的思路很直接：既然一张图里能看见 3 个岛，就让地球上所有可能的 3 个岛都来排队。

项目地址：[原始技术记录](https://yassa9.github.io/osint/gralhix-004/)、[OSINT Exercise #004](https://gralhix.com/list-of-osint-exercises/osint-exercise-004/)

## 本期彩蛋

![一条从模型路由、代码仓库、芯片订单到电力成本的基础设施路径。](assets/15-egg-v2.png)

*「AI 的下一站在哪里？」本期原创彩蛋；APPSO 制图。非 AI 生成。*

模型越来越像基础设施之后，新闻也跟着离开聊天框。

它可能发生在付款路由上、代码仓库里、居民电费单上，或者一张要到 2033 年才结算完的芯片采购表里。

下一期见。

## 引用链接

[1] Stripe：收购 OpenRouter 协议：https://stripe.com/newsroom/news/stripe-agrees-to-acquire-openrouter
[2] Supply Chain Dive：Amazon Prime Air 扩张计划：https://www.supplychaindive.com/news/amazon-to-expand-drone-delivery-reach-sixfold-this-year/828253/
[3] Axios：Ohio Data Center Risk 备忘录：https://www.axios.com/2026/08/19/gop-data-center-memo-ai-election
[4] AP：数据中心进入美国中期选举：https://apnews.com/article/cd2cfd73e3d41e2baf65bf82702a589b
[5] Axios：宾州数据中心行政令：https://www.axios.com/local/pittsburgh/2026/08/18/shapiro-data-center-rules-executive-order
[6] 宾州政府：GRID 标准：https://www.pa.gov/governor/newsroom/2026-press-releases/gov-shapiro-releases-full-grid-standards-to-protect-pennsylvania
[7] Marvell 监管文件：https://investor.marvell.com/sec-filings/all-sec-filings/content/0001193125-26-356217/d412696d8k.htm
[8] Cursor Origin：https://cursor.com/changelog/origin-code-hosting
[9] OpenAI：ChatGPT for Teens：https://openai.com/index/chatgpt-for-teens/
[10] OpenAI：Private Safety Processing：https://openai.com/index/offering-zero-data-retention-for-frontier-models/
[11] Google：Gemini 3.7 Flash：https://ai.google.dev/gemini-api/docs/latest-model
[12] OpenMotion：https://openmotion.design/
[13] Kitbitz：https://kitbitz.art/
[14] The Beginning of ChatGPT Ads：https://arxiv.org/abs/2608.05008
[15] Model Hypnosis：https://arxiv.org/abs/2608.16834
[16] When Agents Coordinate：https://arxiv.org/abs/2608.16801
[17] Geolocating a random island using geometry and CUDA programming：https://yassa9.github.io/osint/gralhix-004/
