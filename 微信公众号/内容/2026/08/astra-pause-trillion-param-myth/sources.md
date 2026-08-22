# 来源

访问日期：2026 年 8 月 10 日（北京时间），经两轮独立 Agent 调研交叉核对。2026 年 8 月 11 日按改稿 SOP 重新打开 gpt-oss-120b、Kimi K3、M6-10T、Epoch AI 两篇分析与 Seed2 官方页面，均返回 HTTP 200，本文使用的关键字段未变。openai.com 官方原始页面直连仍返回 403，Reuters 原文直连仍返回 401；这两项继续使用 8 月 10 日已经留存并交叉核对的页面、截图与媒体记录，不把本次无法直连写成新的事实确认。下表各来源沿用这一访问日期；单独重开或取得日期不同的，写在对应备注中。

## 一、Astra 暂停（硬事实）

| 来源 | URL | 类型 | 支持表述 | 备注 |
|---|---|---|---|---|
| OpenAI 官方公告 | https://openai.com/index/responding-next-frontier-critical-cyber-capabilities/ | P0 / 厂商一手 | **已通过 Wayback Machine 存档（2026-08-10 抓取的快照）取得完整原文，并用第三方截图服务留存页面截图**。原文关键句：「Our latest internal evaluations of Astra, one of our upcoming models...have led us to conclude last night that we cannot rule out critical cyber capabilities under our Preparedness Framework.」「We first published our Preparedness Framework in **December 2023**...」「Previous models, including **GPT-5.6-Sol**, have been evaluated for frontier cyber capabilities and assessed at the **High (rather than Critical) threshold**.」「We are **pausing internal activities involving Astra** that do not yet meet these strengthened security control requirements.」「Astra is an upcoming model, and **was not involved in exploiting Hugging Face**.」Critical 网络安全阈值的官方定义：能在无人工干预下对多个加固的真实关键系统识别并开发全严重级别的零日漏洞利用，或仅凭高层目标就能设计并执行端到端的新型网络攻击策略。Preparedness Framework 覆盖的是生物、化学、网络安全、AI 自我提升等多类风险，不只是网络安全一项 | 直连 openai.com 返回 403（疑似机器人防护），改用 web.archive.org 存档页面成功获取；已交叉核对 MacRumors 此前的转述，内容一致 |
| OpenAI 公告页面截图 | 经 image.thum.io 截图服务对 openai.com 原始 URL 截图 | P0 / 页面视觉留存 | 截图内容与上述存档文字一致，可作为"确有此公告"的视觉证据 | 截图服务本身不是 OpenAI 官方渠道，只是抓取工具；发布前建议再用另一种方式交叉确认页面未被篡改 |
| TechCrunch | https://techcrunch.com/2026/08/07/openai-says-it-slowed-astra-model-development-over-security-concerns/ | P1 | 明确定性为"按既定协议的有序暂停"，非 emergency halt；Astra 未涉及此前的 Hugging Face 入侵事件 | |
| The Verge | https://www.theverge.com/ai-artificial-intelligence/976948/openai-astra-model-pause-critical-cyber-capabilities | P1 | 交叉确认 | |
| The Guardian | https://www.theguardian.com/technology/2026/aug/08/openai-astra-security-concerns | P1 | 交叉确认，发布于 2026-08-08 | |
| Bloomberg Law | https://news.bloomberglaw.com/private-equity/openai-pauses-some-work-on-new-astra-model-on-cyber-concerns-1 | P1 | 交叉确认 | |
| The Information | https://www.theinformation.com/briefings/openai-pauses-astra-work-cyber-concerns | P1 | 交叉确认；作者 Laura Mandaro | 付费墙，仅取得标题与摘要 |
| MacRumors | https://www.macrumors.com/2026/08/07/openai-astra-model-hacking-concerns/ | P2 | 完整转述官方原文 | |

关键限定：Astra 于 8 月 1 日才被 OpenAI 首次公开提及（据报道其内部版本解决过 10 个未解数学问题）；官方**未确认** Astra 是否等同于外界所称的"GPT-6"，也**未公布过任何参数量**。

## 二、"10 万亿参数"数字溯源（查无实据）

**⚠️ 防混淆提示**：以下是两条完全独立的"10 万亿"传闻，写作时不得互相借用细节。GPT-6/Astra 这条**没有**可查证的"3 月泄露文档 + 内容农场转抄链条"——那套具体细节（2026-03-26 CMS 泄露、aimagicx/buildfastwithai 等具名 SEO 站点）属于 Claude Mythos 5 的参数传闻，是另一家公司、另一个模型。GPT-6/Astra 的"10 万亿"经两个核查站点溯源后的结论只有一句：查无出处，没有更多细节可用。draft.md 曾在一次改写中把两条线索的细节混用，已于 2026-08-10 发现并改正，见 `review.md`。

| 来源 | URL | 类型 | 支持表述 | 备注 |
|---|---|---|---|---|
| OrcaRouter 独立溯源 | https://www.orcarouter.ai/blog/openai-astra-gpt-6-leak | P2 | 原话："Approximately 10 trillion parameters. No attribution anywhere we could trace. The most-repeated and least-supported number in the entire story." | |
| AIToolsReview 独立溯源 | https://aitoolsreview.co.uk/insights/gpt-5-7-gpt-6-rumours | P2 | 原话：未找到任何官方来源证实 8 月发布、10 万亿参数或 GPT-5.7/GPT-6 的具体规格 | |
| ChrisGPT（X 账号） | https://x.com/ChrisGPT | P3 / 匿名未核验 | 显示名仅"Chris"，**账号注册于 2023 年 1 月**；自称"AI Insider"，无真实姓名、无任职机构核验；bio 自述"被 The Information/NYT/TechCrunch 报道过"，未查到任何一篇被引用的报道 | 注册时间此前未记入本表，已补记；来源为调研 Agent 直接查看账号资料页 |
| ChrisGPT 此前预测 | https://x.com/ChrisGPT/status/2079632269967593574 | P3 | 7 月称"GPT-6 将于 8 月初发布"，最终结果是 Astra 被暂停，预测已落空 | 不作为信源引用，仅用于说明该账号可信度 |
| Claude Mythos 5 官方页面 | https://www.anthropic.com/claude/mythos | P0 | Mythos 5 本身真实存在（2026-06-09 发布），但页面**无任何参数量披露** | |
| Technology.org（8 万亿估算出处之一） | https://www.technology.org/2026/08/08/bytedance-10-trillion-parameter-ai-model-mythos/ | P2 | "industry estimates place... Mythos 5 at roughly 8 trillion parameters" | 未点名任何具体估算方，与另一流传的"约 10 万亿"互相矛盾，均不采信 |
| ByteDance 10T 预训练传闻 | Financial Times（经 Reuters 转载）https://www.reuters.com/technology/bytedance-targets-mega-ai-model-nearing-anthropics-mythos-ft-reports-2026-08-07/ | P2 | 三名知情人士称字节处于预训练早期阶段，最终规模"最高可达 10 万亿参数"，字节未予置评 | 有编辑标准媒体报道，但仍是未证实的早期阶段传闻，不作为"10 万亿模型已存在"的证据 |
| SemiAnalysis "Doug" | https://newsletter.semianalysis.com/p/gemini-is-cooked-but-gcp-is-cooking | P2 | 2026-08-07 发布；引用自家 7 月 9 日机构订阅简报："OpenAI has overcome their pre-training issues, and a much larger model code named 'Doug' is actively in the works." | 若引用须明确写"SemiAnalysis 机构简报称"，OpenAI 零确认，无参数量、无时间表；同一段引文的前半句已表明"预训练难题已解决"，与"两年多没做预训练"的旧说法矛盾 |

## 三、参数量科普锚点（已核实）

| 来源 | URL | 类型 | 支持表述 | 备注 |
|---|---|---|---|---|
| gpt-oss-120b 官方模型卡 | https://huggingface.co/openai/gpt-oss-120b | P0 | 总参数 116.8B（约 117B），每 token 激活 5.1B，激活占比约 4.36%，MoE 架构，128 专家，2025-08-05 发布，Apache 2.0 | |
| gpt-oss 论文 | https://arxiv.org/abs/2508.10925 | P0 | 确认 "efficient mixture-of-expert transformer architecture" | |
| Kimi K3 官方模型卡 | https://huggingface.co/moonshotai/Kimi-K3 | P0 | 总参数 2.8T，每 token 激活 104B，激活占比约 3.7%，MoE，896 个路由专家（每 token 选 16 个）+ 2 个共享专家，100 万 token 上下文，2026-07 发布。**架构细节（2026-08-11 重新读取页面与官方 `config.json` 确认）：93 层（69 KDA + 24 Gated MLA）、Attention Hidden Dimension 7168、Latent MoE Dimension 3584、MoE Hidden Dimension per Expert 3072、Dense Layers 1、视觉编码器 401M、MXFP4 权重 / MXFP8 激活** | **不得再用 `2.8T ÷ 896` 推算"单专家约 30 亿"**：2.8T 是跨全部层累计的总参数，896 是每个 MoE 层的专家数，两者聚合层级不同；此前稿件的这一估算已判定为口径错误。截图服务多次返回过期倒计时缓存页，故本条用页面正文与官方配置文件复核 |
| Kimi K3 技术报告 | https://arxiv.org/abs/2607.24653 | P0 | 架构细节交叉确认 | |
| 阿里达摩院 M6-10T 论文 | https://arxiv.org/abs/2110.03888 | P0 | 2021-10-08 提交；512 张 NVIDIA V100、约 10 天训练完成 10 万亿参数模型；MoE 架构。**架构细节（2026-08-11 通过 ar5iv 全文重开核实）：48 层、每个 MoE 层 10240 个专家、d_model = 1024、d_ff = 9984、80 个专家原型（expert prototypes）；论文未披露 gating 是 top-1 还是 top-k，因此无法计算精确的激活参数量** | 论文对 1.4B 级模型做了下游评测，但对 **M6-10T 本身**只展示训练 loss / log perplexity，并明确把它能否改善不同下游任务留作开放问题。因此可写成"这篇论文证明 10T 训练可行，未证明 10T 产品能力"，不可写成"它什么都不会"。M6 的 d_model 与 Kimi K3 的 attention hidden dimension 可以作为架构不同的事实对照，但不能单凭宽度推出能力高低；M6 的单层单专家粗算也不得与 `2.8T ÷ 896` 这种跨层口径比较 |
| 阿里云灵骏 M890 超节点 | https://www.ithome.com/0/978/578.htm | P2 | 2026-07-18 发布，官方原话"一台超节点实例即可承载十万亿参数级 MoE 大模型的推理" | 硬件厂商官方表态，证明行业在为该规模备货，不代表已有具体模型达到此规模 |
| Epoch AI：前沿模型变小分析 | https://epoch.ai/gradient-updates/frontier-language-models-have-become-much-smaller | P0 | 2024-12-13，作者 Ege Erdil；GPT-4 约 1.8T，GPT-4o 约 200B，Claude 3.5 Sonnet 约 400B，估算方法为输出速度、API 价格与硬件经济学三条交叉；作者自陈"可能有 2 倍误差"。配图 `token-economics.png`（CC-BY，已下载至 `assets/epoch-token-economics.png`） | |
| Epoch AI：GPT-5 训练算力低于上一代，GPT-6 预计反弹 | https://epoch.ai/gradient-updates/why-gpt5-used-less-training-compute-than-gpt45-but-gpt6-probably-wont | P0 | **2025-09-26（已由页面截图确认）；作者为 Yafah Edelman、Jean-Stanislas Denain、Jaime Sevilla、Anson Ho——注意不是第一篇的 Ege Erdil，正文不得写成"同一位作者"，只能写"同一家研究机构"**；GPT-5 是首个训练算力低于上一代的主线 GPT 模型，原因是靠扩展后训练（post-training）而非预训练拿到提升；文章判断该路径增长速度撑不了太久（原文："tripling post-training compute will soon be akin to tripling the entire compute budget"），因此预测"GPT-6 is likely to need much more training compute than GPT-5, and probably more than GPT-4.5"。配图 `gpt-5-gu-big.png`（CC-BY，已下载至 `assets/epoch-gpt6-compute-forecast.png`） | 这是对"下一代模型可能变大"更精确、可直接引用的信源，替换此前"发布日期待补充核实"的旧引用（原 `ai-progress-is-about-to-speed-up` 链接未再使用） |
| 字节 Seed2.0 官方页面 | https://seed.bytedance.com/zh/seed2 | P0 | 官方强调 Pro/Lite/Mini 三档通用 Agent 模型，重点是长程、多步骤任务的稳定推进，页面**不披露参数量** | 中文版；英文版 https://seed.bytedance.com/en/seed2 |

## 证据分层

- 已核事实：Astra 暂停公告本身；gpt-oss-120b、Kimi K3 的官方参数/激活数据；M6-10T 论文原文；阿里云 M890 官方表态；Epoch AI 两篇分析。
- 有编辑标准媒体报道但未证实：ByteDance 预训练早期传闻（最高可能到 10 万亿，规模未定）。
- 查无出处、不采信：Astra/GPT-6 的"10 万亿参数"具体数字；Mythos 5 的"8 万亿"或"10 万亿"参数数字；ChrisGPT 的全部单方面爆料。
- 需明确挂名才能引用：SemiAnalysis 关于"Doug"的机构简报判断。
- 作者判断：两条"10 万亿"消息的证据等级不同，不能互相替对方背书；即便把它们都作为思想实验的前提，总参数也不能单独推出模型能力或单次推理成本。本文的核心信息增量是：MoE 把总容量与每 token 激活计算部分分开了，同一个总参数标签下面可以是不同的深度、宽度、专家配置、训练目标与路由方式。此前把 GPT-6/Astra 传闻写成"CMS 泄露 → 内容农场复制"的传播链属于与 Claude Mythos 线索混用，禁止再次采用。
