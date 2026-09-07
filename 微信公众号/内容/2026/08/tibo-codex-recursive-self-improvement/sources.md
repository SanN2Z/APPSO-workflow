# 来源与事实映射

访问日期均为 2026 年 8 月 25 日。公司博客中的内部效率、代码占比和生产表现均为厂商自报；论文结果只支持其特定实验设置。

## 采访与人物

| ID | 来源 | URL | 类型 | 支持表述 | 边界／备注 |
|---|---|---|---|---|---|
| S01 | Matthew Berman：Tibo Sottiaux 完整访谈 | https://x.com/MatthewBerman/status/2091959711423996249 | 一手视频 | 8 月 24 日发布；30:25 起谈 RSI；采访总时长约 44 分钟 | 机器转写后按视频复听重点段落；短引语仅用于核义 |
| S02 | Matthew Berman：Codex 两三个月短片 | https://x.com/MatthewBerman/status/2091985979800494354 | 一手视频 | 主持人追问「Codex 两三个月后会显得原始」；Tibo 解释当前工作流的笨重、并行 Agent 与超出笔记本的资源需求 | 该判断最早来自 8 月 4 日原帖，不是采访首发 |
| S03 | The New Stack：Today’s Codex will feel “primitive” by fall | https://thenewstack.io/openai-codex-cloud-evolution/ | 二手报道／原帖存档线索 | 保存 Tibo 8 月 4 日原帖的完整文字与日期 | 原始 X 帖未被搜索服务稳定索引；正文只用采访已复述的核心句 |
| S04 | WIRED：Model Behavior 访谈 | https://www.wired.com/story/model-behavior-interview-with-openai-codex-lead-tibo-sottiaux/ | 人物报道 | Tibo 负责 OpenAI 核心产品，统筹 ChatGPT 与 Codex | 2026 年 6 月报道；人物职责可能变化，本文写明报道口径 |
| S05 | OpenAI Forum：Codex is for everyone | https://forum.openai.com/public/events/codex-is-for-everyone-why-codex-matters-beyond-code-fa40puy7wi | 官方活动页 | OpenAI 官方将 Tibo 标为 Head of Codex | 5 月页面早于 WIRED 对职责扩大的报道 |

## 业界案例与独立观察

| ID | 来源 | URL | 类型 | 支持表述 | 边界／备注 |
|---|---|---|---|---|---|
| S06 | OpenAI：How GPT-5.6 fuses frontier intelligence with frontier efficiency | https://openai.com/index/gpt-5-6-frontier-intelligence-efficiency/ | 公司工程复盘 | Sol 经 Codex 分析生产流量、改写生产内核、优化自己的 draft model；公司称综合内核工作令端到端服务成本下降 20%，draft model 令生成效率提高逾 15% | 厂商自报；有验证工具与人工工程体系，不等于模型独立训练继任者 |
| S07 | OpenAI：GPT-5.6 | https://openai.com/index/gpt-5-6/ | 公司发布页／内部评测图 | RSI Index 中 Sol 为 57.9%、GPT-5.5 为 41.7%，相差 16.2 个百分点；任务覆盖研究调试、内核、训练配方与实验执行 | 厂商内部评测；没有外部模型对照，不是独立验证，也不能单独证明严格 RSI |
| S08 | Anthropic：When AI builds itself | https://www.anthropic.com/institute/recursive-self-improvement | 公司研究院分析 | Anthropic 明确称严格 RSI 尚未到来；梳理内部代码生成、实验自动化与研究品味缺口 | 厂商内部数据；文章同时给出限制，正文不摘掉限制单独使用数字 |
| S09 | Anthropic：Automated Weak-to-Strong Researcher | https://alignment.anthropic.com/2026/automated-w2s-researcher/ | 公司研究报告 | 9 个自动研究 Agent、累计约 800 小时、约 1.8 万美元；报告给出 PGR 0.97，并记录多种奖励投机 | 任务与评分由人类选择；不能外推为开放式研究能力 |
| S10 | Google DeepMind：AlphaEvolve | https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/ | 公司研究博客 | LLM 候选生成、自动评估与进化搜索用于数据中心调度、芯片设计和训练内核；部分改进又用于训练支撑 AlphaEvolve 的模型 | 公司自报；依赖人类可形式化的评测器 |
| S11 | Sakana AI：Darwin Gödel Machine | https://sakana.ai/dgm/ | 公司研究页／论文配套 | 冻结基础模型、让 Agent 修改自身 Python 脚手架，在 SWE-bench 与 Polyglot 上迭代 | 固定沙盒和基准；改的是 Agent 代码，不是基础模型权重 |
| S12 | Sakana AI：RSI Lab | https://sakana.ai/rsi-lab/ | 公司项目页 | 将 LLM²、DGM、ShinkaEvolve、ALE-Agent、Digital Red Queen 和 AI Scientist 串成 RSI 研究路线 | 研究愿景，不是严格 RSI 已实现的证明 |
| S13 | METR：The Economics of Recursive Self-Improvement | https://metr.org/notes/2026-07-22-economics-of-recursive-self-improvement/ | 独立研究机构分析 | RSI 定义混乱；更有用的是观察反馈强度、是否自持加速，以及数据、算力、实验和研发能力瓶颈 | 理论／经济分析，不提供产品完成度证明 |
| S14 | Andrej Karpathy：autoresearch | https://github.com/karpathy/autoresearch | 开源工程原型 | Agent 在单 GPU、固定 5 分钟训练和 val_bpb 指标下连续修改 `train.py`，自动保留或回退实验 | 工程演示，非同行评审；问题与评分均由人预先固定 |
| S15 | METR：Measuring AI Ability to Complete Long Tasks | https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/ | 独立评测 | 用任务时长衡量 Agent 能完成多长的人类工作；为研究自动化的时间跨度讨论提供方法 | 早期曲线不是所有研发工作的统一预测 |

## 论文与概念原页

| ID | 来源 | URL | 状态 | 正文用途 |
|---|---|---|---|---|
| P01 | I. J. Good, “Speculations Concerning the First Ultraintelligent Machine” | https://doi.org/10.1016/S0065-2458(08)60418-0 | 1965 年书章 | 「智能爆炸」的概念起点 |
| P02 | Schmidhuber, “Gödel Machines” | https://arxiv.org/abs/cs/0309048 | 技术报告／预印本 | 可证明自修改程序的理论路线 |
| P03 | Zelikman et al., “STOP” | https://arxiv.org/abs/2310.02304 | 2023 年预印本 | 种子改进器反复改写代码脚手架；作者明确不等于完整 RSI |
| P04 | Huang et al., “Large Language Models Cannot Self-Correct Reasoning Yet” | https://arxiv.org/abs/2310.01798 | ICLR 2024 | 没有外部反馈的自我纠错可能退化 |
| P05 | Yuan et al., “Self-Rewarding Language Models” | https://arxiv.org/abs/2401.10020 | 2024 年论文 | 模型生成训练指令并以 LLM-as-a-Judge 提供偏好信号 |
| P06 | Yin et al., “Gödel Agent” | https://arxiv.org/abs/2410.04444 | 2024 年预印本 | Agent 修改自身逻辑与提示词 |
| P07 | Wijk et al., “RE-Bench” | https://arxiv.org/abs/2411.15114 | 2024 年预印本／评测论文 | Agent 在短预算研发任务上占优，长预算下人类追回并反超 |
| P08 | Shumailov et al., “AI models collapse when trained on recursively generated data” | https://doi.org/10.1038/s41586-024-07566-y | Nature 2024 | 无差别递归使用生成数据会丢失分布尾部 |
| P09 | Zhang et al., “Darwin Gödel Machine” | https://arxiv.org/abs/2505.22954 | 2025 年预印本 | 开放式保留多条自改 Agent 分支 |
| P10 | Zweiger et al., “Self-Adapting Language Models” | https://arxiv.org/abs/2506.10943 | 2025 年预印本 | 模型生成自编辑指令和数据，产生持久权重更新 |
| P11 | Zhang et al., “R-Zero” | https://arxiv.org/abs/2508.05004 | ICLR 2026 会议论文 | Challenger 与 Solver 共演化，自造题目、训练数据和奖励 |
| P12 | Lu et al., “Towards end-to-end automation of AI research” | https://doi.org/10.1038/s41586-026-10265-5 | Nature 2026 | AI Scientist 的选题、实验、写作与评审闭环 |
| P13 | “The Red Queen Gödel Machine” | https://arxiv.org/abs/2606.26294 | 2026 年预印本 | Agent 与评测器共演化，尝试突破固定基准 |
| P14 | “A-Evolve-Training” | https://arxiv.org/abs/2606.20657 | 2026 年预印本 | 自动化 30B 模型后训练循环；结果尚待独立复现 |
| P15 | “Recursive Self-Improvement in AI” survey | https://arxiv.org/abs/2607.07663 | 2026 年预印本综述 | 从有限自我精炼到自动研究循环的层级与验证器瓶颈 |
| P16 | “Scaling Automatic Research Agents via World Models” | https://arxiv.org/abs/2608.12564 | 2026 年预印本 | 用世界模型降低真实实验沙盒成本；新近结果，正文不使用具体提升数字 |

## 未进入公开正文的线索

| ID | 线索 | 处理 |
|---|---|---|
| U01 | 「OpenAI 开发者社区昨天也转发了这场访谈」 | 搜索未取得可稳定复核的原帖；不影响主判断，因此不写入正文 |

## 论文校验说明

`research-lit` 约定的自动校验脚本在本仓库与技能目录中均不存在，`.aris/verify-papers/verified_papers.json` 因此按规则保守记录为 `unverified / verify_papers_unavailable`。上表题名、标识符与发表状态已逐条通过 DOI、arXiv、OpenReview 或出版方原页人工核对；正文不依赖仅由搜索摘要提供的论文元数据。
