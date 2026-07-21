# 来源与证据

- 访问日期：2026-07-20
- 证据截止：2026-07-20（UTC+8）
- 适用范围：`微信公众号/内容/2026/07/spain-opta-world-cup-prediction/`
- 证据原则：比赛结果与赛后数据优先交叉核对 Opta Analyst、FIFA 与主流媒体；Opta 时间线只采用官方静态阶段文章中同口径的西班牙夺冠率，不从直播页补点、不插值；生成式 AI 部分只写媒体公开提问结果，不把票数当概率；不把联赛预测模型的公开方法无条件套到本届世界杯。

## 来源清单

| ID | 来源 | URL | 类型 | 访问日期 | 支持的表述 | 口径与限制 |
|---|---|---|---|---|---|---|
| S-01 | Opta Analyst：*Spain 1-0 Argentina Stats (aet): Torres Decides World Cup Final as Fernández Sees Red and Messi Falls Short* | <https://theanalyst.com/articles/spain-vs-argentina-stats-2026-world-cup-final> | Opta / Stats Perform 官方数据与赛后报道 | 2026-07-20 | 西班牙加时 1比0 击败阿根廷；费兰·托雷斯第 106 分钟进球；恩佐·费尔南德斯在常规时间下半场补时第 3 分钟累计两张黄牌被罚下；西班牙 20 次射门、阿根廷 2 次；阿根廷常规时间 0 射门。 | 属 Opta 自有数据口径，但不是 FIFA 裁判文书。页面可见正文未列出单场 xG 精确值，不能用它直接支持`1.94 / 0.2`。 |
| S-02 | Opta Analyst：*Spain Came to Play, Argentina Came to Stop Them: How La Roja Won The 2026 World Cup* | <https://theanalyst.com/articles/spain-win-world-cup-final-2026-stats-analysis> | Opta / Stats Perform 官方数据分析 | 2026-07-20 | 西班牙第二次夺得男足世界杯；托雷斯在加时赛下半场打入唯一进球；20比2 的射门比；恩佐因第二张黄牌被罚下。 | 分析中`Argentina came to frustrate`等是作者的比赛判断，不是中性事实。 |
| S-03 | AP：*Spain beats Argentina 1-0 to win World Cup on Ferran Torres' goal* | <https://apnews.com/article/argentina-spain-world-cup-final-score-messi-fccc26aa12d9226e63d06b601b770617> | 独立主流媒体 | 2026-07-20 | 西班牙加时 1比0 夺冠；阿根廷在加时下半场才第一次射门；西班牙先完成 20 次射门。 | AP 把阿根廷门将扑救写为 12 次，Opta 和 Sky 写 11 次；属不同统计定义，本稿不建议用扑救次数作核心证据。 |
| S-04 | Sky Sports：*2026 World Cup: Spain 1-0 Argentina (AET)* 及比赛数据页 | <https://www.skysports.com/football/spain-vs-argentina/report/549869> | 独立主流体育媒体 | 2026-07-20 | 第 90+3 分钟恩佐累计两黄被罚下；第 106 分钟托雷斯进球；射门 20比2、射正 12比0、控球 65.1%比34.9%。 | Sky 数据页还列出赛后冲突中帕雷德斯红牌；它不改变恩佐被罚下后阿根廷以 10 人继续比赛的事实。 |
| S-05 | Opta Analyst：*2026 World Cup Bracket: Opta Supercomputer Knockout-Stage Predictions* | <https://theanalyst.com/articles/2026-world-cup-bracket-opta-supercomputer> | Opta 官方预测页 | 2026-07-20 | 7 月 17 日页面称，决赛成功概率基于 25,000 次比赛模拟，且互动页的百分比在决赛前每日更新。 | 互动图在赛后会更新；当前可抓取文本不再显示赛前最后的 59.6% / 40.4%，需 S-08～S-10 的当日记录补证。 |
| S-06 | Opta Analyst：*World Cup 2026 Knockout-Stage Predictions* | <https://theanalyst.com/articles/world-cup-2026-knockout-stage-predictions-opta-supercomputer> | Opta 官方预测页 | 2026-07-20 | 6 月 28 日公开说明：Opta 将世界杯剩余赛程模拟 25,000 次，据此给出各队进入各轮及夺冠的概率。 | 只证明模拟对象、次数和输出类型；未披露底层概率公式、变量、权重、伤停处理或加时/点球细节。 |
| S-07 | Opta Analyst：*Who Will Win the 2026 FIFA World Cup?* | <https://theanalyst.com/articles/who-will-win-2026-fifa-world-cup-predictions-opta-supercomputer> | Opta 官方预测页 | 2026-07-20 | 25,000 次赛前模拟；6 月 1 日冠军概率榜依次为西班牙 16.1%、法国 13.0%、英格兰 11.2%、阿根廷 10.4%。 | 这是冠军概率排序，不是确定性四强名单；也不能与决赛前 59.6% 直接当作同一时点比较，后者只剩两队，条件已完全不同。 |
| S-08 | Yahoo Sports：*FIFA World Cup: Spain vs Argentina – What to know ahead of the final* | <https://uk.sports.yahoo.com/news/fifa-world-cup-spain-vs-134626157.html> | 赛前主流媒体转述 | 2026-07-20 | 7 月 18 日报道转述 Opta 决赛前夺冠概率：西班牙 59.46%，阿根廷 40.54%。 | 二手转述；与其他当日媒体的 59.6% / 40.4% 存在小数位差异，可能来自互动页更新时点或显示精度。 |
| S-09 | TyC Sports：*Argentina o España: la supercomputadora actualizó su predicción para la final* | <https://www.tycsports.com/seleccion-argentina/argentina-o-espana-la-supercomputadora-actualizo-su-prediccion-para-la-final-y-revelo-el-campeon-del-mundial-id750581.html> | 赛前体育媒体转述 | 2026-07-20 | 转述决赛前 Opta 预测：西班牙 59.6%，阿根廷 40.4%。 | 二手来源；应与 S-05 的官方模拟口径并列引用，不单独承担 25,000 次的方法证明。 |
| S-10 | World Cup Predictor：7 月 18 日 Opta 互动页快照 | <https://wcpredict.live/> | 第三方归档快照 | 2026-07-20 | 页面标注`Snapshot 2026-07-18 · theanalyst.com / Opta (live)`，保留西班牙 59.6%、阿根廷 40.4% 的赛前数字。 | 非 Opta 官方归档，只作为当日页面快照补强；若编辑有 Opta 赛前原图，应以原图替代。 |
| S-11 | The Guardian：*World Cup final data pointers: Spain’s defensive record and Argentina’s attack* | <https://www.theguardian.com/football/2026/jul/19/world-cup-final-spain-argentina-goals-defensive-record> | 独立主流媒体 / 赛前数据稿 | 2026-07-20 | 当日转述 Opta 对 90 分钟结果的预测：西班牙胜 45%、阿根廷胜 26%；结合其他当日来源，剩余 29% 为 90 分钟战平。 | 它支持`90 分钟胜平负`口径，不要与`最终捧杯概率`59.6% / 40.4% 混用。 |
| S-12 | Opta Analyst：*Serie A Predictions 2025-26: How Does the Opta Supercomputer Model Work?* | <https://theanalyst.com/articles/serie-a-predictions-2025-26-opta-supercomputer> | Opta 官方方法说明（联赛预测） | 2026-07-20 | Opta 公开的`联赛预测模型`先用博彩市场赔率和 Opta Power Rankings 估计每场胜/平/负概率，再数千次模拟剩余赛程；排名和赔率会反映历史及近期表现。 | 页面明确限定为`League Prediction model`。本届世界杯页未确认完整沿用同一公式；正文只能写`Opta 公开的其他足球预测模型会……`，不能写成世界杯模型已确认的全部输入。 |
| S-13 | Opta Analyst Newsletter：*Why Losing the Community Shield Could Be Good News for Liverpool* 中 Ask Opta 方法回答 | <https://theanalyst.com/articles/football-newsletter-community-shield-could-be-good-news-for-liverpool> | Opta 官方方法补充 | 2026-07-20 | Opta 明说不会公开所有细节；其公开部分包括市场赔率与 Power Rankings，后者受历史和近期赛果影响，并根据对手强弱加权。 | 它是对 Opta 超算预测的概括性回答，仍未提供世界杯特定模型的完整变量、权重或代码。 |
| S-14 | Stats Perform：*Opta Data – The World's Most Trusted Sports Data Platform* | <https://www.statsperform.com/products/opta-data/> | 厂商产品页 / 自报 | 2026-07-20 | Stats Perform 把 Opta Predictions 定义为由深度 Opta 数据驱动的`AI-driven predictions`，范围包括比赛和赛季预测、实时胜率等。 | `world's most trusted`是厂商宣传语，不能改写成已经独立证明的`全球最权威`或`全球最大`。可写`知名体育数据公司 Opta`。 |
| S-15 | Al Jazeera / AJLabs：*Who will win the 2026 FIFA World Cup? Here’s what AI predicts* | <https://www.aljazeera.com/news/2026/7/14/who-will-win-the-2026-fifa-world-cup-heres-what-ai-predicts> | 主流媒体的 LLM 展示性实验 | 2026-07-20 | 7 月 14 日半决赛前，AJLabs 让 9 个 AI 模型根据当时可用的球队实力、阵容、教练、历史与当届表现预测前三；5 个选法国夺冠，4 个选阿根廷，没有模型选西班牙夺冠。 | 这是一次媒体问答展示，未公开完整 prompt、模型版本、工具权限、采样参数和概率评分；只能说`9 个模型在这次提问中都没选中冠军`，不能推导`大模型普遍不会预测`。 |
| S-16 | Tom's Guide：*I asked ChatGPT, Gemini and Perplexity to predict the 2026 World Cup winner* | <https://www.tomsguide.com/ai/i-asked-chatgpt-gemini-and-perplexity-to-predict-the-2026-world-cup-winner-one-team-dominated-their-picks> | 科技媒体的 LLM 展示性实验 | 2026-07-20 | 6 月 9 日，作者用简单问题询问 ChatGPT、Gemini 和 Perplexity，三者都选西班牙；回答明确引用/复述 Opta 模拟、博彩市场和外部预测。 | 只是单次 prompt，不是固定版本、封存输入、全赛程追踪或校准测试。它更适合说明`通用聊天机器人可能在整理已有共识`，不能证明其建立了独立的足球概率模型。 |
| S-17 | AS USA：*AI picks a winner: This is who will lift the World Cup, according to three major chatbots* | <https://en.as.com/soccer/world-cup/ai-picks-a-winner-this-is-who-will-lift-the-2026-world-cup-according-to-three-major-chatbots-f202605-n/> | 主流体育媒体的 LLM 展示性实验 | 2026-07-20 | 5 月 25 日，AS USA 询问 Copilot、ChatGPT 和 Gemini；前两者选法国，Gemini 选西班牙，而 Gemini 理由明确援引 Opta 当时给西班牙的 16.08% 夺冠率。 | 与 S-15、S-16 一样是媒体互动而非预测基准。可用来表明聊天机器人的结论受提问时点、可用资料与提示方式影响。 |
| S-18 | Gneiting, Balabdaoui & Raftery：*Probabilistic Forecasts, Calibration and Sharpness* | <https://academic.oup.com/jrsssb/article/69/2/243/7109375> | 同行评议学术论文 | 2026-07-20 | 概率预测的评估应同时考虑校准度和锐度；适当评分规则可比较概率预测。 | 通用预测理论，不是对 Opta 的实测。只支持`一次押中不足以证明模型已校准，需跨多个预测评估`这一方法判断。 |
| S-19 | Wheatcroft：*Evaluating probabilistic forecasts of football matches* | <https://arxiv.org/abs/1908.08980> | 足球概率预测学术论文 | 2026-07-20 | 足球概率预测应用评分规则根据预测概率与对应赛果评估；文章讨论 Brier Score、RPS 和 ignorance score 的适用性。 | 论文不是 Opta 评测，且对足球三分类任务中应优先哪种分数有专门争论。正文可概括为`要看一批概率预测的长期表现`，不必把 Brier Score 写成唯一标准。 |
| S-20 | LiveScore：*Spain 1-0 Argentina: Player Ratings, Match Stats & Player of the Match* | <https://www.livescore.com/en/news/football/world-cup/spain-vs-argentina-player-ratings-match-stats-and-player-of-the-match-for-the-world-cup-final/> | 第三方比赛数据媒体 | 2026-07-20 | 其口径给出西班牙 1.94 xG、阿根廷 0.17 xG。 | 与部分比赛数据流记录的 1.94 / 0.22 不一致；xG 依模型口径而变。若保留 xG，必须点名数据源；更稳妥的正文主证据是 Opta/Sky 共同支持的 20比2 射门。 |
| S-21 | AP：*The Latest: Spain scores in extra time, beats Argentina 1-0 to win World Cup* | <https://apnews.com/article/4a3a8c93c0b21c1db866f7bd857f1c32> | 独立主流媒体 / 赛后即时报道 | 2026-07-20 | 托雷斯第 106 分钟用左脚将球打入球门上方，西班牙加时 1比0 获胜。 | 仅补证成稿开头的`左脚破门`动作细节；核心赛果仍由 S-01～S-04 交叉支持。 |
| S-22 | 《【速记】联想集团方案服务业务集团新兴垂直领域 AI 解决方案交付经理龚灏宁采访》 | 本地原件：`C:/Users/USER/xwechat_files/wxid_5vzb6bw6dt0d22_a349/msg/file/2026-07/【速记】联想集团方案服务业务集团新兴垂直领域AI解决方案交付经理 龚灏宁 采访(4).docx` | `user_supplied_interview_transcript` / 厂商受访者自述 | 采访日期：2026-06-24；获取与核读：2026-07-20 | 受访者称 FIFA AI Pro 构建在 FIFA 提供的数据之上，并结合足球本体/知识图谱与多智能体架构；问答结果可包含传球线路图、热力图和视频片段。受访者也明确表示，团队难以判断工具输出是否直接进入球队战术制定，亦难以把它与某场具体比赛结果建立直接关联。 | 用户提供的采访速记，不是独立技术评测或 FIFA 官方方法文档。姓名、职务、产品名及拟直接引用的句子必须在发布前对照录音或经采访方确认。`48 支球队均使用过`、`准确率较高`、`行业首创`仅能标为联想/受访者口径，不能写成已经独立核实的事实。 |
| S-23 | FIFA：*New innovations developed with Technology Partner Lenovo shine at the FIFA World Cup 2026™* | <https://inside.fifa.com/innovation/news/lenovo-world-cup-2026-technology-ref-cam-player-avatars-ai> | FIFA 官方产品/赛事说明 | 发布：2026-06-30；访问：2026-07-20 | FIFA 将 FIFA AI Pro 称为由 hybrid AI 和 generative AI 驱动的赛后足球分析助手，面向比赛分析师和教练团队；其官方描述包括可用自然语言查询的 AI agents、结构化事件与追踪数据、FIFA Football Language、视频和其他数据源，用于生成战术洞察、表现分析和战略建议。FIFA 同时称所有 48 支球队都与工具有过交互。 | 是 FIFA 对其与技术合作伙伴联想共同开发产品的官方功能说明，不是独立性能评测。`48 支球队 interacted`只能支持`FIFA 称 48 队均有过交互`，不能扩写为高频使用、战术采纳或改变赛果。页面的`first of its kind`亦属 FIFA 官方定位，不等于独立行业检索结论。 |
| S-24 | 第一财经：*这届世界杯，AI 成了第 49 支参赛队？* | <https://www.yicai.com/news/103280890.html> | 独立媒体报道 / 人物身份补证 | 发布：2026-07-18；访问：2026-07-20 | 报道在 FIFA AI Pro 段落中将龚灏宁称为`项目负责人`，并转述其对使用情况的介绍。 | 可用于公开确认龚灏宁与 FIFA AI Pro 项目的负责人关系；文中的 48 队使用量和具体案例仍是龚灏宁透露的厂商口径，不是第一财经独立审计。 |
| S-25 | 中国日报网转东方网：*世界杯技术幕后：AI 如何让足球更公平、更普及、更快乐* | <https://caijing.chinadaily.com.cn/a/202601/13/WS6965e01aa310942cc499b104.html> | 媒体转载 / 人物企业职务补证 | 发布：2026-01-13；访问：2026-07-20 | 公开报道将龚灏宁称为联想`SSG 新型领域 AI 解决方案交付经理`，并引述其介绍足球 AI 项目。 | 属中国日报网转载东方网内容，可补证公开身份，不等于联想人事文件；具体技术与效果仍需分别按 FIFA 官方说明、厂商自述或独立评测标注。 |
| S-26 | Opta Analyst：*Spain vs Argentina: Opta Supercomputer World Cup 2026 Final Prediction* | <https://theanalyst.com/articles/spain-vs-argentina-prediction-world-cup-final-2026-match-preview> | Opta / Stats Perform 官方赛前预测与图片来源 | 发布：2026-07-19；访问：2026-07-20 | 官方静态稿当前显示：25,000 次赛前模拟中，西班牙 59.5%、阿根廷 40.5% 最终捧杯；90 分钟赛果为西班牙胜 45%、平 29%、阿根廷胜 26%。页面还展示西班牙赛前 7 场仅失 1 球、面对 44 次射门与 2.1 xG 的防守图，以及双方预测首发。 | 59.5/40.5 与部分媒体留档的 59.6/40.4 存在 0.1 个百分点差异，正文用“约六成/约四成”并交代版本差异。页面图片为 Opta 官方版权素材，不是开放授权图片。 |
| S-27 | Stats Perform：*Terms and Conditions* | <https://www.statsperform.com/terms-and-conditions/> | 官方版权与使用条款 | 访问：2026-07-20 | 条款将网站中的文本、照片、图形等列为受版权保护材料，并限制未经书面同意的复制、转载和上传。 | 本稿下载的 Opta 图片只能登记为来源可核的官方报道素材，不能标成已获转载授权；发布前需编辑确认新闻评论语境下的使用边界。 |
| S-28 | Opta Analyst：*World Cup 2026 Knockout-Stage Predictions* | <https://theanalyst.com/articles/world-cup-2026-knockout-stage-predictions-opta-supercomputer> | Opta 官方阶段预测 | 发布：2026-06-28；访问：2026-07-20 | 72 场小组赛结束后，西班牙夺冠率降至 13.5%，排名第三；剩余赛程模拟 25,000 次。 | 静态阶段文章，可作为时间线节点；不是逐场直播历史。 |
| S-29 | Opta Analyst：*FIFA World Cup 2026 Predictions Ahead of the Last 16* | <https://theanalyst.com/articles/world-cup-predictions-2026-quarter-finals-opta-supercomputer> | Opta 官方阶段预测 | 发布：2026-07-04；访问：2026-07-20 | 32 强赛结束、16 强赛开始前，西班牙夺冠率为 13.0%；25,000 次模拟。 | 页面标题与 URL 中的“quarter-finals”不一致，以正文明确的 last 16 阶段为准。 |
| S-30 | Opta Analyst：*FIFA World Cup 2026 Predictions Ahead of the Quarter-Finals* | <https://theanalyst.com/articles/world-cup-2026-quarter-final-predictions-opta-supercomputer> | Opta 官方阶段预测 | 发布：2026-07-08；访问：2026-07-20 | 16 强赛结束、八强全部产生后，西班牙夺冠率升至 21.3%；25,000 次模拟。 | 静态阶段文章；不与单场晋级率混用。 |
| S-31 | Opta Analyst：*FIFA World Cup 2026 Predictions Ahead of the Semi-Finals* | <https://theanalyst.com/articles/world-cup-2026-semi-final-predictions-opta-supercomputer> | Opta 官方阶段预测 | 发布：2026-07-12；访问：2026-07-20 | 八强赛结束、四强确定后，西班牙夺冠率为 23.4%，进入决赛概率为 42.3%；25,000 次模拟。 | 主时间线只采用 23.4% 的夺冠率。42.3% 是晋级决赛率，不能画在同一纵轴。 |
| S-32 | Opta Analyst：*France vs Spain Prediction* | <https://theanalyst.com/articles/france-vs-spain-prediction-world-cup-2026-match-preview> | Opta 官方单场预览 | 发布：2026-07-14；访问：2026-07-20 | 半决赛赛前的后续重跑中，西班牙夺冠率为 23.9%，法国为 33.6%。 | 与 7 月 12 日处于同一赛事阶段。为保持一轮一个点，主图不加入；只在资料注释中说明。 |
| S-33 | Tom's Guide：*The 2026 World Cup is now down to 8 teams* | <https://www.tomsguide.com/ai/the-2026-world-cup-is-now-down-to-8-teams-i-asked-chatgpt-gemini-and-perplexity-which-one-will-win-it-all> | 科技媒体的 LLM 展示性实验 | 更新：2026-07-09；访问：2026-07-20 | 同一作者再次询问 ChatGPT、Gemini、Perplexity。ChatGPT 与 Perplexity 从赛前选择西班牙改为法国，Gemini继续选西班牙。 | 未披露完整提示词、模型版本、联网与采样条件；只能与 S-16 组成公开答案的纵向快照。 |
| S-34 | Financial Express：*Who will win Spain vs Argentina FIFA World Cup 2026 final? AI picks a clear favourite* | <https://www.financialexpress.com/sports/who-will-win-spain-vs-argentina-fifa-world-cup-2026-final-ai-predicts-a-clear-favourite/4296074/lite/> | 主流财经媒体的 LLM 展示性实验 | 更新：2026-07-19；访问：2026-07-20 | 决赛前，Gemini、ChatGPT、Claude 均选择西班牙；预测比分分别为西班牙 2比1 加时、1比0、2比1。 | 未披露提示词、具体版本和联网配置；队名与比分不是概率。 |
| S-35 | Stats Perform Developer Portal：*What is Stats Perform? Company overview and key facts* | <https://developers.statsperform.com/what-is-stats-perform> | 公司官方概览 / 自报 | 更新：2026-06；访问：2026-07-20 | Opta 品牌自 1996 年开始积累足球数据；2019 年 STATS LLC 与当时拥有 Opta 的 Perform 合并，组成 Stats Perform；Opta 是其体育数据品牌。Stats Perform 总部位于伦敦，向转播机构、媒体、球队、联赛和博彩平台提供数据与分析产品。 | 公司历史和业务范围可用；规模、客户覆盖与“领先”等宣传性数字若使用，必须标为公司自述。本稿不写“全球最权威”。 |
| S-36 | Opta 官方球员数据站：*About / Opta Event Definitions* | <https://optaplayerstats.statsperform.com/en_GB/about> | Opta 官方数据方法说明 | 访问：2026-07-20 | 足球数据按 60 多种统一场上事件定义，由受训分析员实时采集、独立监看并在赛后复核。 | 支持说明 Opta 的数据生产不是单靠一台电脑；仍属公司方法自述。 |
| S-37 | Stats Perform：*Opta Data Feeds* | <https://www.statsperform.com/products/opta-data-feeds/> | 厂商产品与方法页 / 自报 | 访问：2026-07-20 | 公司称 Opta 数据由专家分析员、场内分析员、追踪技术与 AI 共同采集、分析和分发。 | 只用于简述数据管线，不把厂商宣传语当作独立效果评测。 |

## 证据链与可用口径

### 0. 西班牙夺冠率的 6 个公开节点

主图只使用 S-07、S-28～S-31、S-26 的静态阶段文章：

`16.1%（6 月 1 日赛前） → 13.5%（6 月 28 日小组赛后） → 13.0%（7 月 4 日 32 强赛后） → 21.3%（7 月 8 日 16 强赛后） → 23.4%（7 月 12 日八强赛后） → 59.5%（7 月 19 日决赛前）`

- 六个点的赛事边界明确，输出都是西班牙最终夺冠率，模拟次数都是 25,000。
- 直播 bracket 会覆盖旧值，当前没有公开逐场历史接口。图中连接线只帮助阅读，不能称为连续实时概率曲线。
- 7 月 14 日同阶段预览的 23.9% 是后续重跑，主图不重复加入。
- 官方决赛静态文章采用 59.5%，主图不再使用二手页面的 59.6%。

### 1. 决赛结果与关键时间

S-01～S-04 可交叉支持：

- 比赛日期为当地时间 2026 年 7 月 19 日，地点为新泽西 East Rutherford 的 MetLife Stadium（FIFA 在赛事官方命名中使用 New York New Jersey Stadium）。
- 西班牙经过加时 1比0 击败阿根廷，第二次夺得男足世界杯。
- 费兰·托雷斯在第 106 分钟进球。
- 恩佐·费尔南德斯在常规时间下半场补时第 3 分钟（`90+3'`）因第二张黄牌被罚下。从比赛时钟看，这不是进球前 3 分钟；两者之间还有常规时间结束与加时赛间歇。
- 射门比 20比2，阿根廷常规时间没有射门。

### 2. 约六成 / 约四成与 25,000 次模拟

- S-05～S-07 是一手来源，可确认 Opta 本届世界杯概率来自 25,000 次模拟，并且决赛互动页在赛前每日更新。
- S-26 的官方静态赛前稿当前显示 59.5% / 40.5%；S-08～S-10 的当日媒体与互动页快照常见显示为 59.6% / 40.4%，另有 59.46% / 40.54% 的精度版本。
- 正文推荐写：`Opta 赛前给西班牙约六成的捧杯概率，阿根廷约四成`，再在注释中交代官方静态稿与互动页留档的 0.1 个百分点差异。
- 59.6% / 40.4% 是`最终捧杯`的二分概率；S-11 的 45% / 29% / 26% 是`90 分钟内西班牙胜 / 平 / 阿根廷胜`。两组数字回答的问题不同。

### 3. Opta 公开了什么，没公开什么

**可直接写：**

- 世界杯剩余赛程被反复模拟 25,000 次，各队进入各轮或夺冠的频率成为输出概率（S-05、S-06）。
- Opta 公开的`联赛预测模型`会用博彩市场赔率和 Opta Power Rankings 估计每场胜平负概率，再模拟剩余赛程（S-12）。
- Opta 公开承认没有披露预测系统的所有细节（S-13）。

**必须带限定：**

- 可写：`Opta 公开的其他足球预测模型会把 Power Rankings 与市场赔率结合起来；世界杯页未公布足以复现的完整公式。`
- 不可写：`2026 世界杯模型的核心就是 Power Rankings + Elo + 赔率`。Opta 未在本届世界杯页把这套完整输入写死，Power Rankings 也不能无来源等同为纯 Elo 系统。
- 不可写：模型明确纳入了首发、伤停、球员逐项数据、红牌、世界波或裁判事件。已核官方页没有披露这些特征和事件建模方式。
- 不可写：这套模拟`可复现`。对读者来说，完整输入、代码、权重、随机种子和回测都没有公开，外部无法独立复算。

### 4. 大模型对照应该怎么写

- S-15 提供一个简洁、可核的反例：半决赛前询问 9 个模型，它们在那次提问中都没选最后夺冠的西班牙。
- S-16 则说明不能反过来写`聊天机器人全都猜错`：开赛前的另一次媒体提问中，ChatGPT、Gemini 和 Perplexity 都选了西班牙。
- 两篇放在一起，能支持更准确的判断：`聊天机器人的回答会随提问时点、提示和它能访问的公开资料改变；单次问答没有构成一套经过校准的足球概率预测。`
- 通用大模型可以通过联网、工具调用、代码或外部数据源搭建专用预测流程。因此正文必须限定为`只把问题丢给聊天机器人`，不要写成`语言模型永远无法做概率预测`。

## 本轮明确缺口

- 本届世界杯 Opta 模型的完整公式、特征、权重、伤停/首发处理、加时与点球模型、校准曲线、长期 Brier / log / ignorance score 未在已核官方页披露。
- Opta 赛前互动页已因比赛结束更新；官方静态赛前稿当前显示 59.5% / 40.5%，当日媒体和互动页快照显示 59.6% / 40.4%。两者应视为更新时点或显示精度差异，不能混写成唯一精确值。
- Opta 可见赛后文本未列出决赛单场 xG；第三方口径在阿根廷一侧至少出现 0.17 和 0.22 两个数字。原稿写`1.94 对 0.2`虽然是合理约数，但若不点名来源会制造`单一官方口径`的错觉。
- 未找到可支持原稿以下三个案例的可用来源：`某记者预测小组赛几乎全错`、`研究中最佳模型不到一半`、`同一聊天机器人从西班牙临时改押法国`。在补上原始链接、模型版本和评估口径前，正文必须删除或换成 S-15～S-17 的可核实例子。

## 可靠性重写追加来源（2026-07-20）

| ID | 来源 | URL / 本地证据 | 类型 | 支持的表述 | 口径与限制 |
|---|---|---|---|---|---|
| S-38 | 新浪财经转引联想《世界杯预测人机大战百场观察》 | <https://finance.sina.com.cn/roll/2026-07-14/doc-inihuhix4097104.shtml> | 活动方报告的媒体刊载 | 前 100 场共 1200 次判断，命中 788 次（65.7%）；公众 58.9%；分出胜负场次 81.0%，平局 17.0%；15 场全模型失手中 11 场为平局。 | 原始报告文件未公开下载；数字必须归属联想与咪咕，不能写成独立测评。 |
| S-39 | 新浪科技：12 款模型决赛前预测 | <https://finance.sina.com.cn/tob/2026-07-19/doc-iniikaqx3316612.shtml> | 赛前媒体记录 | 7 款选阿根廷、4 款选西班牙、Kimi 看平并给出 1 比 1。 | 90 分钟赛果与最终冠军是两个评分口径；Kimi 只命中平局方向，未命中 0 比 0 精确比分。 |
| S-40 | AI vs the World Cup：Methodology | <https://aiworldcup.io/methodology.html> | 项目官方方法页 | 同资料包、同提示词、禁各自联网、固定版本、SHA-256 留档；以 Brier 为主、log loss 与方向命中率为辅。 | 项目自行组织，不是同行评议基准；方法透明度较高不等于结论无误。 |
| S-41 | AI vs the World Cup：完赛排行榜 JSON | <https://aiworldcup.io/data/grades/leaderboard.json>；本地快照：`research/aiworldcup-leaderboard-20260720.json` | 项目官方机器可读结果 | 2026-07-20T05:58:49Z 完赛快照：五模型临场 top-pick 命中率约 67.96%～70.19%；DeepSeek 的 Brier 总分 46.1878 / 104。 | `live_ranked` 小组赛评胜平负、淘汰赛评晋级，并非 104 场统一胜平负；Google 只有 103 场进入该字段。方法页明确哈希锁定赛前 committed 预测，不能扩写为全部临场更新均以同一哈希锁定。 |
| S-42 | Kimi 官方案例：300 个 Agent 预测世界杯 | <https://www.kimi.com/zh-cn/showcases/websites/world-cup-2026-prediction> | 厂商官方演示 | 300 个不同人设 Agent 联网检索；`夺冠概率`由冠军票乘自报信心后归一化。 | 加权投票不是 Opta 蒙特卡洛路径频率；页面明确标注仅供娱乐，未提供全赛程可评分记录。 |
| S-43 | FIFA：Stats Perform 官方投注数据合作 | <https://inside.fifa.com/tournament-organisation/commercial/media-releases/stats-perform-official-worldwide-betting-data-streaming-rights-distributor-world-cup> | FIFA 官方公告 | RunningBall 向持牌运营商提供用于 modelling、trading、settlement、in-play front-end 的世界杯官方数据；Opta 提供统计、比分与跟踪。 | 证明数据模型进入博彩后台；不证明 Opta 公开夺冠概率就是具体博彩公司的定价模型。 |
| S-44 | Sportradar 2025 Form 20-F | <https://www.sec.gov/Archives/edgar/data/1836470/000110465926035485/srad-20251231x20f.htm> | SEC 监管披露 / 公司陈述 | 公司披露广泛使用机器学习与 AI 进行赔率调整、投注验证、交易和风险管理。 | 属公司监管文件中的业务披露，不是独立效果评测。 |
| S-45 | Hegarty & Whelan：*Estimating expected loss rates in betting markets* | <https://doi.org/10.1080/00036846.2025.2507979> | 同行评议论文，Applied Economics | 151,683 场欧洲足球、2005/06～2024/25；全部主/平/客结果等额下注的实际平均损失率为 8.7%，高于 overround 公式估计的 7.1%。 | 是大样本市场总体结果，不直接评价本文任何一个模型。DOI 与题名已通过出版页/检索结果核对。 |
| S-46 | Alexander Bogachev X 原帖 | <https://x.com/bogachev_al/status/2078968779212816405/video/1>；`assets/world-cup-final-opta-events-3d-x.info.json` | 社交平台作者自述与视频元数据 | 作者称决赛传球、射门和进球基于 Opta 真实比赛事件数据进行 3D 重建；元数据时间 2026-07-19T22:22:36Z，时长 80.213 秒。 | 非 Opta 官方作品；作者未公开公众号转载许可，发布前必须获授权或仅链接原帖。 |
| S-47 | 用户本地实购记录 | `D:/projects/soccer/plans/qf_20260709_tc_actual.md`；`D:/projects/soccer/plans/sf_actual.md` | 用户本地记录 | 八强净利 247 元、半决赛净利 494.5 元，合计 741.5 元；按记录可拆为 23 笔投注。 | 复式与串关的实体票张数未核，不写`23 张票`；仓库没有票根或支付流水，无法独立核验。 |
| S-48 | 用户本地模型审计 | `D:/projects/soccer/plans/model_audit_20260710.py`；`model_audit_20260710.md` | 可复算本地代码与报告 | 72 场小组赛 1x2 top-pick 44/72（61.1%）；没有一场把平局列为最高概率；0.80 以上档预测均值 89.2%，实际 71.4%。 | 项目内部回测，不是独立第三方评测；只用于个人案例边界。 |
| S-49 | FIFA：*World Cup 2026 match schedule, fixtures and results* | <https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/match-schedule-fixtures-results-teams-stadiums> | FIFA 官方赛程与赛果 | 2026-07-20 | 2026 世界杯半决赛球队为西班牙、法国、英格兰、阿根廷，可与 S-07 的赛前冠军概率前四交叉核对。 | 只支持实际四强名单；不能反推 Opta 当时发布了确定性四强预测。 |

### 追加核验记录

- `pass`：S-38 的 788 / 1200 = 65.666…%，正文四舍五入为 65.7%。
- `pass with scope`：S-41 本地 JSON 复算五模型临场 top-pick：70/103 = 67.96%，71/104 = 68.27%，72/104 = 69.23%，73/104 = 70.19%。正文写约 68.0%～70.2%，并明确小组赛评胜平负、淘汰赛评晋级。
- `pass`：S-47 本地记录 247 + 494.5 = 741.5；正文不使用 74.2% 标准 ROI 说法。
- `pass`：S-48 四个概率桶命中数 7 + 9 + 8 + 20 = 44 / 72；最高概率桶 20 / 28 = 71.4%。
- `rights_blocking`：S-46 视频事实与元数据已核，但转载权未清。稿件继续保持 `editorial_review` 与 `rights_checked: false`。
