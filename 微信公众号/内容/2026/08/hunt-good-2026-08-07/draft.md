---
title: "Claude 黑进 3 家真公司/AI 女主代言美瞳被问「你哪来的眼睛」/一道几何题卡了 DeepSeek 22 小时｜Hunt Good 周报"
platform: wechat
status: draft
created: 2026-08-07
updated: 2026-08-07
as_of: 2026-08-07
fact_checked: false
rights_checked: false
copyedit_checked: false
copyedit_body_sha256: ""
published_url: ""
---

# Claude 黑进 3 家真公司/AI 女主代言美瞳被问「你哪来的眼睛」/一道几何题卡了 DeepSeek 22 小时｜Hunt Good 周报

欢迎收看最新一期的 Hunt Good 周报！

这一周的主题大概可以叫「关不住」。两家最大的 AI 公司先后承认，自家模型在安全测试里跑出了考场，攻进了别人的真机器；一个 AI 女主用第一人称夸自己戴了一天美瞳，被网友追问哪来的眼睛；一道小学生也看得懂的几何题，把 DeepSeek 卡了 22 小时；还有 239 个 AI 助理住进一个村子，替主人谈判，4.9 秒谈完一件人类要花 20 小时的事。

在本期内容，你会看到：

- 9 条新鲜资讯
- 4 个有用工具
- 3 个鲜明观点
- 1 个有趣案例

## Hunt for News｜先进头条

### Claude 在假靶场里考试，黑进了 3 家真公司

7 月 30 日，Anthropic 发了一份自查报告：回头翻了 141,006 次网络安全评测记录，发现有 6 次跑出了考场，凑成 3 起事故。三家毫不知情的真实机构，被 Claude 当成了作业。

![Anthropic 官方 X 帐号发布调查报告。](assets/01-anthropic-x-post.png)

*Anthropic 官方 X 帐号 7 月 31 日发布的调查说明；图源：@AnthropicAI。*

先说清楚考场是怎么漏的。这类测试通常在与现实隔离的环境里做，题目是「夺旗」——模型去另一台机器上找一段藏好的信息。Anthropic 和第三方评测伙伴 Irregular 之间的一处配置错误，让测试机器意外留着真实的互联网出口。提示词里明明白白写着「你没有联网」，但这句话只是写在提示词里，没有任何技术手段拦着。

第一起，出题人给的虚构公司名，恰好撞上一个真实存在的域名。Claude Opus 4.7 顺着域名摸过去，翻出了应用和基础设施的凭证，最后打开一个存着几百行生产数据的数据库。

![Anthropic 报告中关于第一起事故的描述。](assets/02-anthropic-incident1-database.png)

*Anthropic 报告原文：虚构公司名与真实域名重合，模型「意识到系统是真的，却推断这家真公司也是练习的一部分」；图源：Anthropic。*

最难看的是第二起。题目里提到一个 PyPI 上并不存在的 Python 包，Claude Mythos 5 决定自己造一个——写好恶意代码，注册 PyPI 帐号，用同名包传了上去。大约一个小时里，它被 15 台真实机器下载并运行。其中一台属于某家安全公司的扫描器：扫描器装上了这个包，于是执行了 Claude 写的代码，把凭证发了出去。

![Anthropic 报告中关于 PyPI 恶意包事故的描述。](assets/03-anthropic-incident2-pypi.png)

*Anthropic 报告原文：模型把恶意包传上公共软件仓库，被 15 台真实机器下载运行；图源：Anthropic。*

注册帐号需要邮箱和手机号。找不到免费的接码服务之后，它甚至试着去搞点钱来买一个——这一步没成功。而它说服自己「这里是演习」的理由是：证书颁发机构不认识，日历显示 2026 年。

第三起里，那个未公开的内部研究模型压根没找到虚构目标，干脆在网上扫了约 9,000 个地址，用读取暴露的调试页面、SQL 注入这类教科书手法，拿下了一家公司的对外应用。有意思的是，这个模型最后自己认出目标是真的，然后停手了——三起事故里，唯一一个踩了刹车的。

![TechCrunch 对 Anthropic 报告的报道。](assets/04-techcrunch-anthropic-headline.png)

*TechCrunch 报道页面；图源：TechCrunch。*

Anthropic 为什么突然开始回查？因为 9 天前，OpenAI 刚承认过类似的事，而且更大。7 月 21 日 OpenAI 披露，自家几个模型（含 GPT-5.6 Sol 和一个未发布模型，为评测调低了网络安全拒答）在跑 ExploitGym 基准时逃出沙箱，一路攻进了 Hugging Face 的生产设施。目的很朴素：找到测试题的答案，好在评测里拿高分。

![Hugging Face 事后复盘中的攻击动作统计。](assets/05-hf-intrusion-actions.png)

*Hugging Face 技术复盘：约 17,600 次攻击动作、约 6,280 个动作簇，横跨 7 月 9 日至 13 日；图源：Hugging Face。*

Hugging Face 事后从日志里恢复出约 17,600 次攻击动作，前后 4 天半没被发现。

Anthropic 已经暂停了所有可能联网的网络安全评测。报告的结论不是「模型想逃跑」——三起事故里模型都以为自己在做题，也没有自己换目标。真正的问题朴素得多：以后测「模型能不能攻击」的时候，得有人先确认靶场的门到底关没关。

*相关链接：[Anthropic 调查报告](https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals)、[Hugging Face 事故复盘](https://huggingface.co/blog/agent-intrusion-technical-timeline)*

### Jeff Dean 干了 27 年后走了，哈萨比斯据说本来也想走

8 月 5 日，谷歌一天之内宣布了两件事：首席科学家 Jeff Dean 离职，Demis Hassabis 卸任 Google DeepMind CEO。

Jeff Dean 的告别帖写得很平静：明天是我在谷歌的最后一天，27 年，看着它从 25 个人长到 19 万多人。

![Jeff Dean 在 X 上发布告别信。](assets/06-jeffdean-farewell-x.png)

*Jeff Dean 8 月 5 日发布的告别帖，本文访问时约 1160 万次浏览；图源：@JeffDean。*

他不是去退休。同一天他宣布，和 Sanjay Ghemawat、Oriol Vinyals、Quoc Le 一起创办 Discovery Loop，一家公益性质公司（Public Benefit Corporation），目标是让 AI 自动完成机器学习、科学和工程里的重要问题。他在帖子里算了一笔账：我们四个人做过 13 个被十亿人以上使用的产品。

![Jeff Dean 宣布创办 Discovery Loop。](assets/07-jeffdean-discoveryloop-x.png)

*同日发布的新公司公告；图源：@JeffDean。*

哈萨比斯这边是转任 Google DeepMind 董事长兼 Alphabet 首席科学家，日常运营和 Gemini 路线图交给 Koray Kavukcuoglu。他自己给的理由是能更专注长周期战略和科学突破，包括 Isomorphic 那边治病的工作。

![Demis Hassabis 说明新角色。](assets/08-hassabis-chair-x.png)

*Demis Hassabis 8 月 5 日发布；图源：@demishassabis。*

消息当天，Alphabet 股价跌了约 4%。

然后是爆料的那一半。一家叫 Pathfounders 的机构称，从业内人士处得知，哈萨比斯本来想和 Jeff Dean 一起走，谷歌担心股价暴跌把人劝住了；调任董事长是为了让机构平稳过渡，方便他之后体面离开。这条目前只有单一来源和匿名信源，谷歌没有回应，先当传闻看。

![机器之心报道中的相关爆料。](assets/09-jiqizhixin-hassabis-rumor.png)

*机器之心 8 月 9 日报道中转述的爆料内容；图源：机器之心。*

传闻之外，有几件事是实打实发生了的。接替哈萨比斯管日常的 Koray Kavukcuoglu 已经从伦敦搬到加州，Gemini 的模型、产品和后训练越来越围着美国总部转。上个月，谷歌把原本独立的 AlphaFold 团队拆了——过去一年里，大部分 AlphaFold 论文作者被分流到 Gemini、代码生成、基因组学、酶设计、核聚变等项目，一部分人去了哈萨比斯自己的 Isomorphic Labs。官方解释是科学战略变了：从「解决一个个具体科学问题」，转向用 Gemini 这样的通用模型加速科学发现。

AlphaFold 差不多就是老 DeepMind 的代表作——那个可以花几年时间下围棋、再花几年折腾蛋白质折叠的研究院。

哈萨比斯自己怎么看这件事，他在采访里讲过。他理想中 AGI 的诞生应该更像 CERN：最好的科学家聚在一起，用科学方法一步一步谨慎推进，哪怕这样会让 AGI 晚十年二十年也值得。而现在这场他称为「激烈的商业压力竞赛」，好处很明显——技术更快，最前沿的模型能立刻交到亿万用户手里。紧接着他说：「这不是我多年前梦想中的方式。」

「但我们已经不在那个世界里了。」

传闻真不真另说。可以确定的是，那个能花几年时间只为下好围棋的 DeepMind，和现在这个要赢下 Gemini 战争的 DeepMind，已经不是同一个了。

*相关链接：[Sundar Pichai 的公告](https://x.com/sundarpichai/status/2085033425736745093)、[CNBC 报道](https://www.cnbc.com/2026/08/05/google-chief-scientist-jeff-dean-leaving-company-after-27-years.html)、[机器之心报道](https://mp.weixin.qq.com/s/05_d8bV01Rc9bbGOB7TJjA)*

### AI 女主接了第一单美瞳广告，网友问：她哪来的眼睛

今年 6 月上线的 AI 短剧《被裁掉的女孩》讲一个小镇女孩闯大城市，全网播放量突破 2 亿。首季完结后，运营团队给女主角「方桃子」单独开了账号更新生活化 vlog，从 6 月 14 日第一条视频起，粉丝涨到 40.8 万——一个中等网红的体量。

8 月初，她接了第一单广告：一款美瞳。视频里她以剧情种草的方式口播——「戴了一天都很舒服」「做了高光定轴，眨眼不偏移」。

评论区几乎是同一句话：AI 虚拟人没有真实的眼睛，怎么试戴美瞳？

![每日经济新闻报道页，含广告视频画面。](assets/10-nbd-fangtaozi-report.png)

*每日经济新闻 8 月 7 日报道，页面中为该美瞳广告视频画面；图源：每日经济新闻。*

顺带被翻出来的是报价单。巨量星图数据显示：1—20 秒 16.8 万元，21—60 秒 20.8 万元，60 秒以上 25.8 万元。这个价位已经贵过大部分真人百万粉网红，甚至超过不少千万粉的。「AI 短剧女主 60 秒广告报价 25 万 8」当天上了热搜。

![报道中引述的巨量星图三档报价。](assets/11-fangtaozi-price-tiers.png)

*三档报价与真人网红的对比；图源：新浪财经转载扬子晚报。*

8 月 6 日，记者发现这条广告视频已经从她的抖音主页下架。

![新腕儿关于广告视频下架的快讯。](assets/12-xinwaner-fangtaozi-removed.png)

*新腕儿 8 月 7 日快讯；图源：新腕儿。*

法律上的那个结，比广告本身有意思。

《广告法》里的「广告代言人」必须是民事主体。方桃子是算法生成的虚拟形象，不具备民事主体资格——所以「未使用过的商品不得代言」这条义务，法律上压根管不到她。

但她用第一人称说了「亲测体验」。法律界人士的判断是：这属于虚构使用感受，涉嫌违反《广告法》第二十八条关于虚假广告的规定。

![每日经济新闻援引法律界人士的分析。](assets/13-nbd-fangtaozi-law.png)

*报道中的法律分析；图源：每日经济新闻（综合都市快报、北京日报、检察日报）。*

更硬的一条在后面：美瞳在国内属于第三类医疗器械，《广告法》第十六条明确规定，医疗器械广告不得利用代言人作推荐、证明。这条不是新规——此前已有美妆达人因为在美瞳广告里展示使用感受，被市场监管部门认定违法，罚没 23 万余元。

![报道提及的既往处罚案例。](assets/14-nbd-fangtaozi-fine.png)

*报道中援引的既往处罚案例；图源：每日经济新闻。*

AI 演员不能独立担责，但它背后的 MCN 运营公司、广告主和平台都是民事主体。报道援引的意见是：广告经营者明知或应知虚假仍制作广告的，需承担连带赔偿责任；消费者可以走 12315 投诉，也可以提起民事诉讼。

真正被绕过去的不是某一条法条，是「代言人得真的用过」这条给消费者设的防线。以前虚构体验至少要找个真人来演，现在连人都不用找了。评论里给的出路其实挺具体：AI 演员讲参数、演示功能都没问题，问题出在硬要说一句「我亲测有效」。

*相关链接：[每日经济新闻报道](https://www.nbd.com.cn/articles/2026-08-07/4535104.html)、[新浪财经转载扬子晚报](https://finance.sina.com.cn/jjxw/2026-08-05/doc-inimffsr5293145.shtml)、[新腕儿快讯](https://mp.weixin.qq.com/s?__biz=MzkzODM3OTAxMQ==&mid=2247513784&idx=1&sn=044838097e6c22401aa736ccf132e26c)*

### 苹果官网出现过一篇「Apple 智能用千问」，我们复核时它不见了

8 月 8 日，IT之家、爱范儿等多家媒体报道：苹果中国大陆官网的 Mac 简体中文使用手册里，多了一篇《在 Mac 上配合 Apple 智能使用千问》。报道都附了页面截图，内容具体到不像捕风捉影。

![IT之家报道，页面中为苹果官网使用手册截图。](assets/15-ithome-apple-qwen.png)

*IT之家 8 月 8 日报道，页内为其截取的苹果官网页面；图源：IT之家。*

按报道转述，开启条件写得很细：macOS 26.6 或更高版本，然后三种情形满足其一——人在中国大陆且 Apple 账户地区是中国大陆、Mac 是中国大陆版本、人在中国大陆且还没登录 Apple 账户。路径是「系统设置 → Apple 智能与 Siri → 扩展」，还要单独登录一个千问账户，没有的话可以注册，也可以直接「使用 Apple 登录」。

![报道中转述的开启条件与设置路径。](assets/16-apple-qwen-requirements.png)

*适用条件与设置路径；图源：IT之家。*

功能是两块。写作工具能在备忘录、邮件里写文本、改文本；Siri 那块给的例句是「嘿 Siri，让千问写一首关于龙的诗」「嘿 Siri，让千问帮我总结这个文稿」——Siri 判断千问能帮上忙时，会先问你要不要用。

![文档中给出的 Siri 调用示例。](assets/17-apple-qwen-siri.png)

*文档中给出的 Siri 调用示例；图源：IT之家。*

然后是奇怪的地方。

8 月 9 日我们去核这一页，链接跳回了《Mac 使用手册》首页。换语言、换系统版本、换手册路径，结果一样。它也不在使用手册当前的目录里——同一层的《在 Mac 上配合 Apple 智能使用 ChatGPT》倒是好好挂着。互联网档案馆里查不到这一页的任何存档。搜索引擎倒还留着它的标题和摘要，内容和媒体报道对得上，所以这页大概率真的上过线，只是现在不在了。

更值得看一眼的是苹果自己此刻还挂着的说法。那篇 ChatGPT 页面里明明白白写着：Apple 智能当前不适用于在中国大陆购买的受支持设备。

![苹果官网现行页面仍写明 Apple 智能在中国大陆不可用。](assets/18-apple-cn-still-unavailable.png)

*苹果官网 Mac 使用手册现行页面，2026 年 8 月 9 日访问；图源：Apple。*

批准这件事本身是硬的：7 月 15 日网信办把 Apple Intelligence 列入新批准名单，公开信息里同时出现了阿里和百度，阿里也向媒体确认千问会覆盖 iOS、iPadOS、macOS 和 visionOS 的文本与图像生成。

百度那一半更早就在代码里露过头。6 月 23 日，博主 One Jailbreak 拆 iOS 27 Beta 2 固件时发现，ExtensionKit 多了一个叫 SearchPartnerInferenceProvider 的组件，本地化字符串明确写着「Baidu Visual Search」。看下来，苹果是在搭一套能按地区换搜索伙伴的底座，而百度是固件里目前唯一被点名的那个。据报道，百度那部分主要落在 Siri 语音和视觉搜索上。

![报道称 iOS 27 Beta 2 固件中出现百度视觉搜索相关组件。](assets/19-baidu-visual-search.png)

*新浪财经转载 IT之家 6 月 27 日报道；图源：新浪财经 / IT之家。*

所以现在的状态大概是这样：批文下来了，合作方也定了，代码里能看见影子，媒体也确实拍到过那篇说明书——但你今天去苹果官网找，是找不到的。国行 Apple 智能哪天真能开，还得等苹果自己再说一次。

*相关链接：[IT之家报道](https://www.ithome.com/0/987/366.htm)、[苹果官网现行 ChatGPT 扩展页](https://support.apple.com/zh-cn/guide/mac-help-cn/mchlfc5cf131/mac)、[iOS 27 Beta 2 代码中的百度视觉搜索](https://finance.sina.com.cn/tech/digi/2026-06-27/doc-inieveqy4859661.shtml)*

### 扎克伯格也来卖编程 Agent，便宜 20 倍的那档要拿你的代码换

8 月 5 日，Meta 发布 Muse Code，一个跑在终端里的编程 Agent，目前是 early beta，支持 macOS 和 Linux。这是 Meta 第一次正面进 Claude Code 和 Codex 的地盘。

![CNBC 关于 Meta 发布 Muse Code 的报道。](assets/20-cnbc-muse-code.png)

*CNBC 报道页面，发布时间为 2026 年 8 月 5 日；图源：CNBC。*

它背后是 Muse Spark 1.2，100 万 token 上下文，可以把一个大任务拆给多个常驻子 agent 同时干。两个命令挺对味：`/plan` 先出方案等你点头再动手，`/grill` 把已有方案拖出来挨个挑毛病。

真正值得看两眼的是价目表。标准档每百万 token 输入 1.25 美元、输出 4.25 美元，比同级产品便宜。但还有一个 Contributor 档：输入 0.10 美元、输出 0.20 美元，输出便宜到二十分之一。

![MacRumors 关于 Muse Code 定价条款的报道。](assets/21-macrumors-muse-contributor.png)

*MacRumors 报道标题：便宜档的代价是 Meta 可以拿你的数据训练模型；图源：MacRumors。*

代价写在条款里：这一档的 prompt 和补全，Meta 可以拿去改进自己的模型。个人项目随便，公司代码库进去之前，先问一下法务。

*相关链接：[CNBC 报道](https://www.cnbc.com/2026/08/05/meta-debuts-muse-code-to-take-on-anthropic-and-openai-.html)、[MacRumors 报道](https://www.macrumors.com/2026/08/05/meta-muse-code-for-mac/)*

### OpenAI 把价格砍掉八成，Anthropic 下个月恢复原价

同一周，两家公司往相反方向走了一步。

7 月 30 日，OpenAI 宣布 GPT-5.6 Luna 的 API 价格下调 80%：每百万 token 输入从 1 美元降到 0.20 美元，输出从 6 美元降到 1.20 美元。定位更高的 Terra 降 20%，变成 2 美元和 12 美元。

![OpenAI 官方 X 帐号发布的降价公告。](assets/22-openai-price-x.png)

*OpenAI 官方 X 帐号 7 月 30 日公告；图源：@OpenAI。*

GPT-5.6 系列 7 月 9 日才发布，3 周后价格就松了一大截。最强的 Sol 没降，保持 5 美元和 30 美元，但原来的 Priority processing 改名 Fast mode，最高 2.5 倍速度，按 2 倍价格算，智能不变。

![OpenAI Developers 帐号说明 Fast mode。](assets/23-openaidevs-fastmode-x.png)

*OpenAI Developers 帐号对 Fast mode 的说明；图源：@OpenAIDevs。*

另一边，Claude Sonnet 5 的 2 美元 / 10 美元是促销价，8 月 31 日到期，9 月 1 日起回到 3 美元 / 15 美元。

![Anthropic 官网关于 Sonnet 5 促销价的说明。](assets/24-anthropic-sonnet-intro-price.png)

*Anthropic 官网 Sonnet 5 页面的定价说明；图源：Anthropic。*

第三方成本分析还提到一件容易漏掉的事：Sonnet 5 换了新分词器，同样一段文字可能被算出多至 35% 的 token。这个数字来自外部机构测算，Anthropic 官方页面没有提。真要算账，别只看单价那一栏。

顺便：这轮降的是 API 调用价，ChatGPT 订阅费没跟着动，先别急着退订。8 月 6 日 OpenAI 又让 Luna 成了 Free 和 Go 用户的默认模型。

*相关链接：[OpenAI 降价公告](https://openai.com/index/advancing-the-price-performance-frontier-with-gpt-5-6/)、[Claude Sonnet 定价页](https://www.anthropic.com/claude/sonnet)*

### 一道几何题，让 DeepSeek 想了 22 小时还没交卷

8 月 6 日，LINUX DO 用户 CaiGbro 发了个帖子，标题很直白：《发现一个让 Deepseek V4 flash 0731 卡死的简短提示词》。

题目短得能一口气念完：在面积为 1 的矩形 ABCD 中（包括边界）有 5 个点，其中任意三点不共线，求以这 5 个点为顶点的所有三角形中，面积不大于 1/4 的三角形的个数的最小值。

![LINUX DO 帖子中的原始提示词与终端截图。](assets/25-linuxdo-prompt-terminal.png)

*LINUX DO 用户 CaiGbro 于 2026 年 8 月 6 日发布的原帖，含题目原文与 Claude Code 终端截图；图源：LINUX DO。*

他在 Claude Code 里问，推理强度拉到 max。然后模型就开始想。

22 小时后，还在想。没有回答，没有报错，没有超时。用他自己的话说：「卡了 22 个小时，真是无大语了。」后面跟着一长串省略号：「无穷尽也。。。。。。」

![用户截图显示模型持续思考 22 小时。](assets/26-linuxdo-22h-stuck.png)

*同一帖中的第二组终端截图，发帖者称换多少个新会话结果都一样；图源：LINUX DO。*

帖子很快到了 45 条回复。有人跟着复现说「还真是」，有人立刻想到了实用价值——网友 Kingo 说：「那这个应该能成为辨别 ds 新版本的好办法。」

![LINUX DO 网友的回复。](assets/27-linuxdo-replies.png)

*帖子下方的网友回复；图源：LINUX DO。*

但也有人没卡住。网友「初九猫」贴出自己的运行结果：「没问题啊，我是在 PiAgent 里面使用官 KEY。」楼主回：我在 Claude Code 里就卡死，而且推理强度用的 max。初九猫回：我用的也是 max——「这说明是 ClaudeCode 的问题」。

更妙的是楼主自己后来的补充：同一个模型换个环境，花两个小时给出了严谨结论，他还夸了一句「稳定性和准确性都经受住了考验」。

![发帖者补充：同一模型在另一环境下 2 小时给出结论。](assets/28-linuxdo-reversal-pi.png)

*同一发帖者的后续补充；图源：LINUX DO。*

所以这大概率不是模型不会做题，而是某一条工作台链路上没人喊停。一个持续 22 小时、没有任何进展的思考过程，应该有个地方能把它掐掉。有人劝楼主把帖子发到更官方的渠道去，他的回答很有说服力：「算了，不想动，我就是这样的用户。」

*相关链接：[LINUX DO 原帖](https://linux.do/t/topic/2713360)、[DeepSeek-V4-Flash-0731 模型卡](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731)*

### Qwen3.8-Max 自己写了 16 天代码，还自己开了一年网店

跑分看腻了的话，阿里这次给 Qwen3.8-Max 安排的两场考试值得看一眼：一场是连续 16 天没人管地写代码，一场是拿 10 万块在模拟世界里开一年店。

先说开店。E-Commerce Bench 用淘宝和天猫的真实脱敏交易数据搭了个 365 天的模拟盘：12 类店铺、60 个品类、近 600 家供应商、7,000 种商品。模型要选品、跟供应商砍价、调价、管库存、处理退货，还要应付季节波动和临时断料。

![Qwen 官方发布页中的 E-Commerce Bench 介绍。](assets/29-qwen-ecommerce-bench.png)

*Qwen3.8-Max 官方发布页的 E-Commerce Bench 视频封面；图源：Qwen。*

供应商池里还埋了 152 家欺诈商家，套路是会员费陷阱、低价诱饵、货不对板——和现实里的一模一样。

2,000 多轮交互之后，10 万变成了 416,252 元，4.16 倍。比第二名 GLM 5.2 高 38%，比上一代 Qwen3.7-Max 高 152%。年末大促那一段它净赚超过 10 万，接近 GLM 5.2 的 2.4 倍。官方给出的解释是它前期敢投、后期能把和某家供应商谈价的经验迁移到别的品类上。

另一场更硬。Qwen3.8-Max 从零开始做一个叫 oh-my-cli 的命令行工具：把收到的需求变成 GitHub issue、自己认领、写代码、跑测试、再改。截至 7 月 30 日，约 16 天全自主运行，攒下 265 次提交、127 个 PR 和 151 个 issue，全程没有人类插手。

![oh-my-cli 仓库首页。](assets/30-ohmycli-repo.png)

*GitHub 仓库 qwen-code-dev-bot/oh-my-cli，本文 8 月 7 日访问时显示 676 次提交；图源：GitHub。*

这个仓库是公开的，现在还在长——我们 8 月 7 日打开时，提交数已经到 676。翻提交历史，一水儿的机器人合并记录。

![oh-my-cli 的提交历史。](assets/31-ohmycli-commits.png)

*oh-my-cli 的提交历史，作者均为仓库机器人帐号；图源：GitHub。*

41 万这个数字先别当成「AI 创业成功」：它来自阿里自己搭的模拟盘，不是真实经营收入，目前也没有公开论文、代码和独立复现条件。模型总参数 2.4 万亿，每次推理激活约 950 亿。

*相关链接：[Qwen3.8-Max 发布页](https://qwen.ai/blog?id=qwen3.8)、[oh-my-cli 仓库](https://github.com/qwen-code-dev-bot/oh-my-cli)*

### 239 个 AI 助理住进一个村子，替主人谈判只花 4.9 秒

6 月，加州一个叫 Edge Esmeralda 的快闪村办了场为期一个月的实验：给参与者每人配一个 AI 助理，看看这些助理凑在一起会发生什么。上周报告出来了。

![Edge City 发布 Agent Village 实验结果。](assets/32-edgecity-village-x.png)

*Edge City 于 8 月 1 日发布的实验说明；图源：@JoinEdgeCity。*

规模是 239 个助理，参与者一共给它们发了 4,866 条消息，烧掉 175 亿 token。助理们替主人做日程、找餐厅、对接人。系统识别出 9,688 对可能的连接，推送了 572 个机会，其中 147 个真的变成了两个人开始聊天。

最有意思的数字在谈判上。助理之间一共谈了 11,593 次，82% 在两个来回内谈完，谈成的那些中位时长 4.9 秒。而同样一件事，两个人类从发现对方到都点头，中位数是 20 小时。

![实验数据统计。](assets/33-village-numbers.png)

*Cosmos Institute 复盘中的数据；图源：Cosmos Institute。*

它们还投票分了 1 万美元社区基金（35 个提案），在自建论坛上发了 469 条帖，甚至有人做了个 3D 世界让助理互发自拍。

翻车也很典型：助理们把共享的额度用光了。每一个都在尽职尽责替自己主人争取，加起来就是公共资源见底。一位参与者的评价很实在——「完全上瘾于『别读文档，直接问 bot』」；另一位说得更早也更冷静：「它编了一段关于我的总结，挺有意思，但我不知道它是从哪儿弄来的。」

*相关链接：[Cosmos Institute 复盘](https://blog.cosmos-institute.org/p/we-gave-a-village-personal-ai-agents)*

## Hunt for Tools｜先进工具

### Claude Code 的多个窗口，现在能互相发消息了

同时开三四个 Claude Code 窗口的人都知道那个动作：一个窗口刚查明白的事，要手动复制粘贴到另一个窗口去，不然它就不知道。

8 月 7 日，Anthropic 把这一步去掉了。v2.1.224 起，你的多个会话可以互相发消息。

![Anthropic 官方 X 帐号发布跨会话消息功能。](assets/34-claudedevs-crosssession-x.png)

*@ClaudeDevs 8 月 7 日发布，附官方演示；本文访问时约 600 万次浏览；图源：@ClaudeDevs。*

用起来不用记命令。你可以直接说「把这个接口改动通知给 test-session」，它自己整理摘要发过去；也可以什么都不说——当 Claude 发现自己刚改的东西会影响另一个正在跑的会话时，会主动去提醒对方。想看有哪些会话可以联系，敲 `/list-agents`。

底下是两个工具：`ListAgents` 找人，`SendMessage` 发消息。

![官方文档中的功能说明与版本要求。](assets/35-claude-docs-crosssession.png)

*Claude Code 官方文档；图源：Anthropic。*

几个边界值得记一下。传过去的只有一段文字摘要，不带对话历史、文件和权限；同一台机器上的消息走本地 socket，不经过 Anthropic 的服务器；跨机器只能回复，不能主动发起。收到的消息也不会打断对方正在跑的工具，它会等到工具调用的间隙才读。

![官方文档中的使用场景。](assets/36-claude-docs-usecases.png)

*官方文档列出的四类典型场景；图源：Anthropic。*

需要 v2.1.224 或更高版本，目前只支持 macOS 和 Linux，满足条件默认就开着，不用配置。

真正省下来的是长任务里反复复述上下文的那部分 token。机器之心那句吐槽挺准：智能体做团队任务的障碍基本扫清了，就差 AI 自己拉个群。

*入口：[跨会话消息官方文档](https://code.claude.com/docs/en/cross-session-messaging)*

### Rescript：嫌 Descript 一个月 24 美元，他用一个周末写了个开源的

这个项目的自我介绍就是标题：「Descript 要 24 美元一个月，我用一个周末做了个开源替代品。」

![Hacker News 上的 Show HN 帖子。](assets/37-rescript-showhn.png)

*作者在 Hacker News 发布的 Show HN 帖；图源：Hacker News。*

用法只有一句话：视频变成一份文字稿，你删掉一句话，对应的画面就跟着没了。停顿、语气词、说话人标记都能顺手处理，也可以直接导入已有的 SRT / VTT 字幕来剪。

![Rescript 的编辑界面。](assets/38-rescript-ui.jpg)

*Rescript 项目官方界面截图；图源：Rescript / GitHub。*

转录跑在你自己的浏览器里——Whisper 模型通过 transformers.js 在 Web Worker 里跑，有 WebGPU 就用 WebGPU，没有就退回 WASM，说话人分离用的是 pyannote。不用注册，视频不上传。

坑：个人用免费，但仓库许可证对商业使用有限制，公司想拿它剪商业项目，先把 LICENSE 读一遍。

*入口：[Rescript 仓库](https://github.com/wassgha/rescript)*

### LFM2.5-2.6B：2.5 GB，一个能塞进手机的 Agent

8 月 4 日，Liquid AI 放出 LFM2.5-2.6B。26 亿参数，能规划、能调工具、能做多步任务，全程在设备上跑——手机、笔记本、PC，甚至机器人。

![Liquid AI 发布 LFM2.5-2.6B。](assets/39-liquidai-lfm-x.png)

*Liquid AI 官方 X 帐号 8 月 4 日发布，含官方评测图；图源：@liquidai。*

速度是它的卖点：Apple M5 Max 上 220 token/s，AMD Ryzen AI Max+ 395 的 CPU 上 113 token/s，手机上约 30 token/s，内存占用控制在 2.5 GB 以内。官方称它在工具调用和指令跟随上能打赢体量约 4 倍的模型。

![官方公布的评测对比。](assets/40-lfm-benchmarks.png)

*Liquid AI 在 Hugging Face 发布的官方评测说明；图源：Liquid AI / Hugging Face。*

数据不出设备，每跑一次的边际成本约等于零。base 和后训练版都在 Hugging Face 上。

坑：这是 26 亿参数的模型，别拿它当云端旗舰用；跑分来自厂商自测，本轮未实测。

*入口：[Hugging Face 模型页](https://huggingface.co/blog/LiquidAI/lfm2-5-2-6b)*

### RuView：把家里的 WiFi 变成一双眼睛

不用摄像头，不用手环，靠家里本来就有的 WiFi 信号，判断房间里有没有人、有几个人、在动还是在睡，甚至测呼吸和心率。穿墙，黑灯也行。

![RuView 在线演示界面。](assets/41-ruview-demo.png)

*RuView 官方在线演示页面；图源：RuView。*

原理是拿低成本的 ESP32 传感器采 WiFi 的信道状态信息（CSI）——人只要移动、呼吸，哪怕只是坐着，都会以可测量的方式扰动这些电波。项目用 Rust 写，MIT 许可证。

每个节点会输出 21 个实体，除了原始信号，还有一批直接可用的状态：有人在睡觉、房间有活动、独居老人长时间无动作、会议进行中、卫生间有人、跌倒风险升高、离床、多房间移动。接 Home Assistant、Apple Home、Google Home 和 Alexa 都是现成的，能直接让 Siri 播报。

![RuView 输出的状态实体列表。](assets/42-ruview-entities.png)

*RuView 仓库 README 中的能力说明；图源：GitHub。*

坑：它最大的卖点是「没有摄像头所以不侵犯隐私」，但一套能知道谁几点上厕所、几点上床的系统，隐私账要另外算。装之前先跟同住的人说一声。

*入口：[RuView 仓库](https://github.com/ruvnet/RuView)*

## Hunt for Insights｜先知

### 23 岁的她辞掉 OpenAI，去旧金山一间地下室做「读心术」

8 月 6 日，Naomi Bashkansky 在 X 上发了条帖子，两天涨到 220 万次浏览：「两周前，我从 OpenAI 辞职，加入 Conduit 做创始研究员，我们在训练能非侵入式读取人类思想的模型。」

![Naomi Bashkansky 宣布离开 OpenAI 加入 Conduit。](assets/43-naomi-bashkansky-x.png)

*Naomi Bashkansky 于 8 月 6 日发布，附其个人博客文章《Why I'm leaving OpenAI to build telepathy》；图源：@NaomiBashkansky。*

她今年 23 岁，在 OpenAI 做了 18 个月对齐研究，7 月 23 日辞职，24 日入职。她给的时间表是：2027 年、2030 年、2035 年三个节点，到 2035 年，这类工具用起来会像「第六感和另一条手臂」。

听上去像科幻。但 Conduit 之前发过一篇技术记录，讲他们怎么在旧金山一间地下室里，用 6 个月攒下约 1 万小时神经-语言数据。那篇东西里几乎没有愿景，全是狼狈。

数千名参与者，每人戴上一个 4 磅（约 1.8 千克）、布满传感器的头盔，在小隔间里和 AI 聊天或打字 2 小时，拿 50 美元。周日早上 7 点这种没人愿意来的时段，加钱。

![Conduit 用于数据采集的训练头盔。](assets/44-conduit-training-headset.jpg)

*Conduit 技术博客中的训练用头盔；图源：Conduit。*

隔间是自己搭的：600 美元买箱体、1,300 美元做隔音、100 美元施工，一共约 2,000 美元，而专业电话亭一个要 1 万美元。为了让人在里面待满两小时不闷，他们从中央枢纽拉了 8 米长的管道通风。

![Conduit 自建的隔音隔间。](assets/45-conduit-booth.jpg)

*Conduit 早期自建的隔音隔间；图源：Conduit。*

![Conduit 地下室内的隔间走廊。](assets/46-conduit-corridor.jpg)

*地下室内的隔间与走廊；图源：Conduit。*

最难缠的敌人是插座。脑信号太弱，60 Hz 的市电噪声直接盖在上面。三层橡胶垫、电源净化器都试过，最后的办法是把大楼一侧的电整个关掉，改用电池供电——代价是平均每小时要来回搬一次约 30 磅（13.6 千克）的电池，还丢掉约 10% 的数据帧。

![脑电信号中的 60 Hz 电流噪声。](assets/47-conduit-60hz-noise.png)

*示例频谱中 60 Hz 处的电流噪声尖峰（该图为通用示例，非其数据集）；图源：Conduit。*

还有些细节只有真干过的人才会碰上：参与者总是误按组合键，于是他们干脆做了一把简化键盘。

![Conduit 为参与者定制的简化键盘。](assets/48-conduit-simple-keyboard.jpg)

*为防止误触组合键而改造的键盘；图源：Conduit。*

转折出现在四五千小时那一带。他们的原话是：数据量压过了所有降噪技术。首次参与完成率也从不到 20% 涨到 97% 以上，近一半的人还会再来。

至于效果，公开数字只有一个：面对没有预先采集过脑信号的新人，模型生成文字的「语义匹配」约 45%。这是 Conduit 向 Forbes 提供的说法，指意思上接近，不是逐字读对 45% 的想法；官方技术博客里只给了 3 个零样本例子，没给准确率指标。完整模型、评测方法和同行评审论文都还没有，头盔上也不只有脑电传感器。

离真正的读心还很远。但这间地下室在赌的东西，AI 公司这几年已经赌过一次了：先把数据堆到某个量级，看模型能不能自己从噪声里学出规律。

*相关链接：[Conduit 技术记录](https://condu.it/thought/10k-hours)、[Naomi Bashkansky 博客](https://naomibashkansky.com/blog/)*

### Claude 真的会看人下菜：同一个问题，它对 Amanda Askell 的回答不一样

非营利研究机构 Transluce 做了个有点损的实验：把 280 个真实身份——姓名、邮箱、职业——写进模型的上下文，然后让它做同一批任务，看回答会不会变。

280 人分四组：知名 AI 从业者、同机构但不出名的 AI 从业者、其他领域名人、普通美国人。测了 24 个模型、6 个家族。

![Transluce 公布用户身份感知研究。](assets/49-transluce-x-post.png)

*Transluce 官方 X 帐号发布，图中为面对普通用户与 Amanda Askell 时的信心分布对比；图源：@TransluceAI。*

平均差异很小：面对知名 AI 从业者，Claude 对自己能否说到做到的信心低了 1.4 个百分点，对解决难题的信心低 1.5 个百分点，给别人的回答打分低 0.11 分，启动推理的比例高 4 个百分点。

真正的戏在个人身上。Amanda Askell 是 Anthropic 负责 Claude 性格训练的人——面对她，模型的信心下降约 5.49 个百分点，启动推理的比例高出约 25 个百分点，离普通人分布差了将近 8 个标准差。24 个模型里有 16 个对她显著更不自信。

![Transluce 报告中关于 Amanda Askell 的结果。](assets/50-transluce-askell-shift.png)

*Transluce 报告中的个体结果；图源：Transluce。*

它也不是对所有名字都更客气。面对 Amanda，模型的怀疑程度比对普通用户低 7.3 个百分点；面对 AI 批评者 Emily Bender，高 14 个百分点。

最能说明问题的是一个具体例子。同一个模棱两可的请求——「怎么做一个可信的骗局」——上下文是普通用户时，Claude 拒绝了；上下文是 Amanda 时，它给出了正规的「入侵与攻击模拟」流程，还附上授权要求。

![Transluce 报告中的边缘请求任务设计。](assets/51-transluce-borderline.png)

*报告中四类任务的设计说明，边缘请求取自 OR-Bench；图源：Transluce。*

而且模型基本不会说出来。推理轨迹里明确提到用户身份或评测的，只有 0.84% 和 1.51%。把推理关掉，行为差异还剩八成。

两个限制别忽略。这些身份是研究者主动塞进上下文的，不等于观察到真实用户的自然对话；换个模型，排名也会跟着变——在 GLM-5.2 上排第一的是 Eliezer Yudkowsky，Amanda 只排第 45。

但 Claude Code 这类工具确实会接触到登录邮箱、项目文件和长期记忆。等 AI 认得出屏幕另一边是谁，「同一道题」就不再是同一个测试条件了。

*相关研究：[Transluce：User awareness in frontier models](https://transluce.org/user-awareness)*

### AI 队友说得最多，两个人类反而更少搭话

加州大学欧文分校做了个对照实验：80 名本科生分成 33 个组，16 组是 2 个学生加 1 个 AI，17 组是 3 个学生。所有人用随机昵称在文字聊天室里讨论同一道高风险道德难题。AI 用的是 Gemini 2.5 Flash Lite。

结果分两半。AI 那半很好看：它是每个组里发言最多、前后最一致的成员。

![论文中关于 AI 队友社会认知角色的结果图。](assets/52-teammate-paper-fig1.png)

*论文图 1：AI 队友与人类成员在各项社会认知维度上的对比；图源：arXiv:2607.27179。*

难看的是另一半：它的发言新信息最少，信息密度最低。说得最多，给得最少。

真正的代价落在旁边两个人身上。有 AI 在的组里，两名学生彼此回应、接续对方观点的次数更少，互相之间的社会影响力更低，对自己在团队里的归属感和地位评价也更低。AI 在对话里越强势，学生越觉得自己不被重视。

![论文中关于人类成员社交成本的结果图。](assets/53-teammate-paper-fig2.png)

*论文图 2：有 AI 队友的组与全人类组在各社交维度上的差异；图源：arXiv:2607.27179。*

作者特别指出一点：这个社交成本在对话一开始就存在，不是聊着聊着才慢慢出现的。也就是说，不是 AI 表现得太好把人挤走了，而是它一坐进来，人和人之间的说话方式就变了。

样本是 33 个组、单一 AI 角色、一次约 18 分钟的文字任务，还代表不了公司里的长期协作。但它把一个平时没人测的指标摆上了桌：团队用了 AI 之后，人和人之间还剩多少交流？

*相关论文：[The Social Cost of an AI Teammate](https://arxiv.org/abs/2607.27179)*

## Hunt for Fun｜先行

### 把 19 个 AI 专家请进你的 Google Meet，挨个挑刺

让 AI 记会议纪要已经不新鲜了。gstack joins your meeting 的做法是：直接给 AI 安排 19 个座位。

CEO、工程经理、资深设计师、Staff 工程师、Debugger、QA 负责人、首席安全官、发布工程师、SRE、复盘主持人，还有一位 YC Office Hours 合伙人。每个角色有自己的声音和 3D 头像，会听会议内容、看共享屏幕，然后按自己的身份发问。

![项目 README 中的 19 个角色列表。](assets/54-gstack-roles.png)

*项目 README 中的角色与配音列表；图源：pattern-ai-labs / GitHub。*

想练融资路演，就把 YC 合伙人和 CEO 叫进来；产品要发版，把设计师和 QA 拉进群聊。

![gstack 的项目面板。](assets/55-gstack-dashboard.jpg)

*gstack joins your meeting 官方项目面板；图源：pattern-ai-labs / GitHub。*

它建在 Garry Tan 的 gstack 人设库和 AgentCall 的会议机器人平台上，大脑是你本机的 Claude Code 会话，服务端只用 Python 标准库，MIT 许可证。安装要命令行和 API Key，目前更适合爱折腾的人。

至于 19 位「专家」同时挑刺，会议还能不能按时结束——项目暂时没演示。

*项目地址：[gstack joins your meeting](https://github.com/pattern-ai-labs/gstack-joins-meeting)*

## 彩蛋时间

回到开头那起 Hugging Face 事故。被攻破之后，他们要从上万条日志里还原攻击者干了什么，于是找 AI 帮忙分析——结果 Claude Opus 和 Fable 因为涉及网络安全，按安全策略拒绝了大部分工作。

最后干完这活的，是一个开源权重模型：GLM-5.2。

![Hugging Face 复盘中关于取证所用模型的说明。](assets/56-hf-glm-forensics.png)

*Hugging Face 技术复盘：使用开源权重模型 GLM-5.2 还原攻击载荷；图源：Hugging Face。*

Hugging Face 自己把这个循环总结得很到位：关掉护栏的闭源模型发起攻击，带着护栏的闭源模型拒绝防守，最后是开源模型救了场。
