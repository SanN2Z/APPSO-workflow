# 来源记录

访问日期均为 2026-07-13；正文时间统一换算为北京时间。

| 来源 | URL / 路径 | 类型 | 支持表述 | 备注 |
|---|---|---|---|---|
| arXiv 摘要页：B-spline Policy | https://arxiv.org/abs/2607.09648 | 论文原文 / 官方索引 | 标题、作者、机构、摘要、arXiv 分类、v1 提交时间、许可入口 | v1 提交为 2026-07-10 17:46:32 UTC，即北京时间 7 月 11 日 01:46:32；当前为预印本 |
| arXiv PDF：B-spline Policy | https://arxiv.org/pdf/2607.09648 | 论文原文 | 方法、公式、实验设置、表格数字、消融、局限、四张正文图 | 本地存档：`research/source-assets/arxiv-2607.09648.pdf`；图表与结论均为作者报告，尚无独立复现 |
| B-spline Policy 官方项目页 | https://b-spline-policy.github.io/ | 作者官方项目页 | 项目 TL;DR、视频对比、真实实验表格、代码和 Colab 入口 | 视频和结果均由论文团队提供 |
| B-spline Policy GitHub | https://github.com/B-spline-policy/bspline-policy | 作者官方代码仓库 | 代码已公开、MIT License、项目 Quick Start | 代码许可不自动等于论文插图获得同一许可 |
| arXiv cs.RO recent | https://arxiv.org/list/cs.RO/recent | 官方索引 | 2026-07-13 批次共 33 篇，B-spline Policy 列第 1 位 | 列表日期不等于实际提交日期 |
| BEAST: Efficient Tokenization of B-Splines Encoded Action Sequences | https://arxiv.org/abs/2506.06072 | 相关论文原文 | 2025 年已有 B 样条动作 tokenizer；BEAST 被 NeurIPS 2025 接收 | 用于限定创新边界，不把 B 样条动作编码写成 BSP 首创 |

## 主要 claim 对照

| Claim | 证据位置 | 标签 |
|---|---|---|
| BSP 把离散动作块替换成连续 B 样条参数 | 论文摘要、Sec. 3–4、Fig. 1–3 | 已核事实 |
| 策略 10Hz、低层控制 100Hz | Fig. 3；Appendix A.1 | 已核事实，10Hz 为流程图所示设置 |
| Table Cleaning / Regression / 4X：23.57s→11.80s，13/20→14/20 | Table 1、Sec. 5.2 | 作者实验结果 |
| Fig. 5：20.5s→9.6s，2.14X | Fig. 5 | 作者展示的代表性定性轨迹，不是均值 |
| 对齐在 4X 下把 1.7X→2.2X、15%→35% | Fig. 6 | 作者消融实验 |
| 极端速度受低成本机械臂控制器限制 | Sec. 6 | 作者解释，不是独立结论 |
| BSP 更像动作接口改造，而非模型认知升级 | 对方法与实验范围的编辑归纳 | 作者判断 / 推断 |

## 版权说明

arXiv 页面给出的论文许可为 non-exclusive distribution。正文裁图只用于对论文进行评论、说明和研究分享，保留紧邻出处；发布前仍需人工确认公众号使用边界，不能标为获得作者商业授权。
