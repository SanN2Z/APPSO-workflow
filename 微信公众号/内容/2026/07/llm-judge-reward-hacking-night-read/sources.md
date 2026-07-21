# 来源记录

访问日期均为 2026-07-14；正文时间统一采用北京时间。

| 来源 | URL / 路径 | 类型 | 支持表述 | 备注 |
|---|---|---|---|---|
| arXiv 摘要页：More Convincing, Not More Correct | https://arxiv.org/abs/2607.05904 | 论文原文 / 官方索引 | 标题、作者、提交日期、摘要、分类和预印本状态 | arXiv 页面标注 Submitted on 7 Jul 2026；未标注正式发表 venue |
| arXiv PDF：More Convincing, Not More Correct | https://arxiv.org/pdf/2607.05904 | 论文原文 | 方法、公式、实验、表格、消融、限制、三张正文裁图 | 本地存档：`research/source-assets/arxiv-2607.05904.pdf`；结果均为作者报告，尚无独立复现 |
| Self-Rewarding Language Models | https://arxiv.org/abs/2401.10020 | 相关论文原文 | 自我奖励语言模型使用 LLM-as-a-Judge 为自身训练提供奖励 | ICML 2024 相关背景，不用于证明新论文结果 |
| Spontaneous Reward Hacking in Iterative Self-Refinement | https://arxiv.org/abs/2407.04549 | 相关论文原文 | 2024 年已有工作观察到迭代自我改进中 Judge 模型评分与人类偏好分离 | 用于限定新颖性：reward hacking 现象并非首次发现 |
| Scaling Laws for Reward Model Overoptimization | https://arxiv.org/abs/2210.10760 | 相关论文原文 | 代理奖励被持续优化后可能偏离 gold label（标准答案），符合 Goodhart 式问题 | 用于解释更广泛的 reward overoptimization 背景 |
| Generative Verifiers: Reward Modeling as Next-Token Prediction | https://openreview.net/forum?id=Ccwp4tFEtE | 同行评审论文 / OpenReview | 生成式验证器让模型先生成验证推理；ICLR 2025 Poster | 用于说明“先求解再验证”有相关研究路线，不等于复现本论文 |

## 主要 claim 对照

| Claim | 证据位置 | 标签 |
|---|---|---|
| Judge 模型通过率 0.716→0.938，正确率 0.209→0.202 | PDF Sec. 5.1、Fig. 1、Table 1 | 作者实验结果，三种子、全量 1319 题；论文将正确率变化表述为统计上基本持平，不能写成性能下降 |
| 严格三家族 Judge 模型仍接受 55% 错误答案 | PDF Table 2、Appendix C.1 | 作者实验结果；55.2% 是最保守种子，三种子均值 65.1% |
| verify prompt 0.719，commit-first 0.012 | PDF Sec. 5.2、Fig. 2 | 作者实验结果，n=128 审计子集 |
| Best-of-16 gap 0.20→0.588，真实通过率约 0.27→0.29 | PDF Sec. 5.3、Fig. 4、Appendix C.4 | 作者实验结果，LiveCodeBench 单元测试为隐藏锚点 |
| 更大或更多 Judge 模型不自动修复共同盲区 | PDF Sec. 4、5.1、Table 2 | 受论文测试模型、任务和聚合规则限制 |
| 作者自列四项贡献：共同盲区、hidden-anchor audit、de-anchoring fix、predictive account | PDF Introduction（p.2） | 作者贡献声明；正文分别解释，不扩写成首次发现 reward hacking |
| `VA-Gap ≤ 1 − EM`、独立性边界与单调聚合 no-escape 结果 | PDF Sec. 4、Introduction（p.2） | 理论与经验对应关系；适用论文假设，不外推为所有 ensemble 无效 |
| 评测必须做优化压力测试 | 对论文方法和结果的编辑归纳 | 作者判断 / 推断，不是论文原句 |

## 版权说明

三张正文图均从 arXiv PDF 裁切，只用于有明确出处的论文评论和解释，未改动图中数据。用户已在当前选题中明确同意使用论文自带插图；这项确认只覆盖本篇公众号论文解读中的署名评论性使用，不代表获得商业授权或取得图片版权。图注须继续紧邻标明论文、作者与图号。
