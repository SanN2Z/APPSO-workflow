# 来源记录

访问日期：2026-07-29（首次核查）；2026-07-30 复核 SSI 官网与 Updates，并新增 S18–S29。

## 来源表

| ID | 来源 | URL | 类型 | 支持的表述 | 限制与口径 |
|---|---|---|---|---|---|
| S01 | NVIDIA Newsroom：SSI 与 NVIDIA 长期战略合作 | https://nvidianews.nvidia.com/news/ilya-sutskevers-safe-superintelligence-inc-and-nvidia-announce-long-term-strategic-partnership | 联合官方新闻稿 / P0 | 2026-07-27 合作；NVIDIA 投资；Vera Rubin；算力扩大一个数量级；rare access；new research direction；Ilya 称研究值得扩大规模 | 投资额未披露；技术价值与进展为公司口径；没有公开研究内容 |
| S02 | SSI 官网与 Updates | https://ssi.inc/ ; https://ssi.inc/updates | 公司官网 / P0 | 公司目标、公开更新、10× 算力表述；网站当前公开页面范围 | 现行首页不是 2024 成立公告的完整存档；「官网未公开」不等于内部没有 |
| S03 | Dwarkesh Patel：Ilya Sutskever 访谈官方逐字稿 | https://www.dwarkesh.com/p/ilya-sutskever-2 | 播客方官方带时间戳转录 / P0 | generalization、value function、continual learning、superintelligent 15-year-old、age of research、SSI technical approach | 代表 Ilya 的公开判断；不是论文；不能据此命名 SSI 路线 |
| S04 | Dohare et al.：Loss of plasticity in deep continual learning | https://www.nature.com/articles/s41586-024-07711-7 | 同行评审论文 / P0 | loss of plasticity 与 catastrophic forgetting 不同；静态 Ant 实验；continual backprop | 实验不等同于前沿 LLM；干预存在超参数敏感性 |
| S05 | Huang et al.：Large Language Models Cannot Self-Correct Reasoning Yet | https://openreview.net/forum?id=IkmD3fKBPQ ; https://arxiv.org/html/2310.01798 | ICLR 2024 论文 / P0 | intrinsic self-correction 表格；oracle labels 的对照；正确改错问题 | 结论依赖模型、提示、任务和样本；标题比证据范围更广 |
| S06 | Benna & Fusi：Computational principles of synaptic memory consolidation | https://www.nature.com/articles/nn.4401 | 同行评审理论论文 / P0 | 多时间尺度快慢变量、双向耦合、近线性容量 scaling | 理论模型，不是真实人脑容量的直接测量 |
| S07 | McClelland et al.：Why There Are Complementary Learning Systems | https://doi.org/10.1037/0033-295X.102.3.419 | 同行评审理论论文 / P0 | 海马快速记忆、新皮层缓慢交错学习、系统巩固 | 1995 年理论框架；不能直接移植为 AI 架构 |
| S08 | Doya：Metalearning and neuromodulation | https://www.sciencedirect.com/science/article/pii/S0893608002000448 | 同行评审理论论文 / P0 | 神经调质作为元学习全局信号的四项假说 | 具体一一映射不是定论，需配合现代研究校准 |
| S09 | Redondo & Morris：Making memories last | https://www.nature.com/articles/nrn2963 | 同行评审综述 / P0 | synaptic tagging and capture；持久改变可由前后活动共同决定 | 生物机制，不直接验证任何 LLM 方法 |
| S10 | Rosen et al.：Catecholaminergic modulation of meta-learning | https://pmc.ncbi.nlm.nih.gov/articles/PMC6974360/ | 同行评审实验研究 / P0 | 人会按环境波动性调整学习率；儿茶酚胺与这种调节有关 | 神经实现仍不清楚；不支持 Doya 四项映射全部成立 |
| S11 | Grossman & Cohen：Neuromodulation and Neurophysiology on the Timescale of Learning and Decision-Making | https://www.annualreviews.org/content/journals/10.1146/annurev-neuro-092021-125059 | 同行评审综述 / P0 | 神经调质参与学习与决策的时间尺度调节 | 综述，不能承载具体工程结论 |
| S12 | Al-Shedivat et al.：Continuous Adaptation via Meta-Learning | https://arxiv.org/abs/1710.03641 | ICLR 2018 / P0 | Ilya 历史上参与过 nonstationary continuous adaptation 研究 | 只作历史背景；与 SSI 无公开承继关系 |
| S13 | Lightman et al.：Lets Verify Step by Step | https://arxiv.org/abs/2305.20050 | arXiv 论文 / P0 | 过程监督、PRM800K、Ilya 历史署名 | OpenAI 2023 工作；不是 SSI 或持续学习路线证据 |
| S14 | SSI 官方 X：宣布与 NVIDIA 长期合作 | https://x.com/ssi/status/2081732119194394763 | 公司官方社交原帖 / P0 | NVIDIA 投资；未来 12 个月算力扩大 10 倍；SSI 自称研究值得扩大规模 | 公司自述，不是独立验证；没有披露架构、模型或测试成绩 |
| S15 | Dwarkesh Patel 官方 X：发布 Ilya 完整访谈 | https://x.com/dwarkesh_sp/status/1993371363026125147 | 访谈方官方社交原帖 / P0 | 原帖目录含「人类为什么泛化得更好」「SSI 的模型将从部署中学习」「研究时代」 | 章节标题是访谈方概括；15 岁少年表述仍以官方逐字稿为准 |
| S16 | Krizhevsky、Sutskever 与 Hinton：ImageNet Classification with Deep Convolutional Neural Networks | https://proceedings.neurips.cc/paper_files/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf | NeurIPS 2012 原论文 / P0 | Ilya 是 AlexNet 论文作者之一；ILSVRC-2012 top-5 错误率 15.3%，第二名为 26.2% | 正文只用「把第二名甩开一大截」作普通人转述，不展开技术细节 |
| S17 | The Information：NVIDIA 投资 SSI 简讯 | https://www.theinformation.com/briefings/nvidia-makes-multibillion-dollar-investment-ilya-sutskevers-safe-superintelligence | 媒体报道转述 Ilya 对外声明 / P1 | Ilya 表示 SSI 关注人脑如何运作中被忽视的部分 | 方向性表述，不是架构披露；不能证明正文讨论的具体持续学习或神经调质机制已被 SSI 采用 |
| S18 | imjustnewatai：对 SSI 公开线索的个人分析长帖 | https://x.com/imjustnewatai/status/2081749227730809127 | X 个人分析 / P2 | 把理想中的持续学习拆为 5 项验收问题：少样本上手、提前发现失败、更新不忘旧技能、跨问题迁移、部署后继续学习 | 作者明确把整套推断称为自己的最高概率猜测，并另给「内部价值系统」40% 的主观置信度；不能作为 SSI 架构、实验结果或内部信息的证据。公开可见不等于获得转载许可，截图使用边界另见 `asset-manifest.yml` |
| S19 | Brown et al.：Language Models are Few-Shot Learners | https://proceedings.neurips.cc/paper/2020/hash/1457c0d6bfcb4967418bfb8ac142f64a-Abstract.html | NeurIPS 2020 / P0 | GPT-3 可仅凭上下文中的范例临场完成多种任务，测试时不更新参数 | 测的是上下文内表现，不能据此声称技能已永久留下 |
| S20 | Min et al.：Rethinking the Role of Demonstrations | https://aclanthology.org/2022.emnlp-main.759/ | EMNLP 2022 / P0 | 在所测分类与多选任务中，随机标签往往只造成有限下降；格式、标签空间与输入分布也在发挥作用 | 不能推广为「示范内容或正确答案永远不重要」 |
| S21 | Liu et al.：Few-Shot Parameter-Efficient Fine-Tuning is Better and Cheaper than In-Context Learning | https://proceedings.neurips.cc/paper_files/paper/2022/hash/0cde695b83bd186c1fd456302888454c-Abstract-Conference.html | NeurIPS 2022 / P0 | 用少量标注样本更新任务专属的少量参数，可把任务适应保存下来 | 受控分类与多选任务；保存的是适配器，不是通用模型自主长期进化 |
| S22 | Gou et al.：CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing | https://proceedings.iclr.cc/paper_files/paper/2024/hash/fef126561bbf9d4467dbb8d27334b8fe-Abstract-Conference.html | ICLR 2024 / P0 | 搜索、代码执行与计算器等外部工具可为纠错提供可核对反馈 | 属于推理时工具闭环，不等于模型权重在部署后持续更新 |
| S23 | Scialom et al.：Fine-tuned Language Models are Continual Learners | https://aclanthology.org/2022.emnlp-main.410/ | EMNLP 2022 / P0 | 连续学习会遗忘旧任务；穿插少量旧样本复习可显著缓解 | 实验覆盖论文所测语言任务，不能宣称遗忘已被根治；回放还涉及存储与隐私成本 |
| S24 | Min et al.：MetaICL: Learning to Learn In Context | https://aclanthology.org/2022.naacl-main.201/ | NAACL 2022 / P0 | 先在大量语言任务上学习，可提高模型对未见目标任务的少样本适应 | 仍在语言任务分布内；不是一次孤立经验迁移到任意无关问题 |
| S25 | Wang et al.：Super-NaturalInstructions | https://aclanthology.org/2022.emnlp-main.340/ | EMNLP 2022 / P0 | 更丰富的训练任务有助于模型泛化到保留的新任务 | 任务共享自然语言指令与输入输出框架，不能外推为任意现实职业迁移 |
| S26 | Wang et al.：Voyager: An Open-Ended Embodied Agent with Large Language Models | https://arxiv.org/abs/2305.16291 | arXiv 2023 / P0 | 自动课程、提示与可执行代码技能库让智能体在 Minecraft 中积累能力 | GPT-4 权重不更新；属于外部技能与上下文积累，不是底层模型持续训练 |
| S27 | Liu et al.：Monolith: Real Time Recommendation System With Collisionless Embedding Table | https://arxiv.org/abs/2209.07663 | RecSys 2022 / P0 | 生产推荐系统可把新行为数据持续用于线上训练和参数更新 | 窄任务、可统计反馈与 A/B 测试环境；不能证明通用 LLM 已能安全长期自我成长 |
| S28 | Wang et al.：MoCL: Data-driven Modular Continual Learning with Less Forgetting and More Transfer | https://aclanthology.org/2024.naacl-short.39/ | NAACL 2024 / P0 | 用模块化方法减少任务间干扰，并讨论回放方法的存储与隐私问题 | 模块化同样可能限制跨任务共享；不能据此声称遗忘已解决 |
| S29 | Reuters：NVIDIA 拟向 SSI 投资 50 亿美元 | https://www.investing.com/news/stock-market-news/nvidia-to-invest-5-billion-in-ilya-sutskevers-ai-startup-source-says-4814862 | 媒体报道 / P1 | 援引知情人士称 NVIDIA 将进行约 50 亿美元股权投资；路透注明彭博先行披露 | 双方官方公告未披露金额；正文必须保留媒体归因，不能写成黄仁勋或 Ilya 官方宣布 |

## 写作边界

- 公众号正文只把 SSI 当作新闻切口与证据边界案例。
- 所有生物机制都用「启发」「原则」「可能的需求」表述，不用「解法」「复制」「已经实现」。
- 所有 plasticity loss 结论都限定到论文所测任务；前沿 LLM 尺度仍列为开放问题。
- self-correction 数字明确限定到 Huang et al. 的实验设置。
- NVIDIA 公告中的研究价值与方向属于公司自述，不把它当成第三方 benchmark。
- 约 50 亿美元的投资额来自彭博、路透社援引知情人士的报道，不是双方官方公告披露的数据。
