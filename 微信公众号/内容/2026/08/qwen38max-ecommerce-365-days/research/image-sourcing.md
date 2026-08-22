# Qwen3.8-Max 电商稿配图候选与权利台账

更新：2026-08-04

本轮只搜集、截取和登记候选图，没有改动 `draft.md`，也没有把任何图片标记为可直接发布。

## 先看这 6 张

### 1. 官方演示最终排名卡

- 文件：`source-assets/qwen38-ecommerce-video-65s-final-ranking.png`
- 画面：Qwen3.8-Max、GLM 5.2、Kimi K3、DeepSeek V4 Pro、Qwen3.7-Max 的最终排名，画面显示约 416K、301K、265K、190K、165K。
- 建议位置：开场讲完「一年网店」后，作为第一张证据图。
- 优点：一眼能读懂主角、结果和比较对象，最贴文章主钩子。
- 图注口径：图上使用取整值 416K；正文若写 416,252，要说明这是官方发布页披露的精确值，避免读者误以为数字冲突。
- 决策：A，优先使用。

### 2. 官方演示整年资产曲线

- 文件：`source-assets/qwen38-ecommerce-video-60s-final-curve.png`
- 画面：五个模型在完整模拟过程中的资产轨迹，纵轴到约 400K。
- 建议位置：「这 41 万是怎么跑出来的」或「为什么偏偏要开满一年」。
- 优点：比终局排名多出过程信息，能让读者看见领先不是只在最后一刻出现。
- 图注限制：这是 Qwen 官方演示中的一次模拟轨迹，不能写成多次重复实验后的稳定结论。
- 决策：A，正文主图。

### 3. 官方电商演示标题页

- 文件：`source-assets/qwen38-ecommerce-official-poster.png`
- 画面：Qwen3.8-Max「电商经营评测／模拟经营网店一整年」官方标题页。
- 建议位置：头图底图、开场分隔图，或视频链接封面。
- 优点：6667 × 3752，干净、官方、裁切余量大。
- 缺点：只有议题，没有结果；单独承担文章首图会偏空。
- 决策：A-，适合设计加工，不宜作为唯一证据图。

### 4. MerchantBench 延迟反馈机制图

- 文件：`source-assets/merchantbench-fig1-delayed-feedback.png`
- 画面：新订单立刻占用现金，异常结果和店铺评分变化延后出现。
- 建议位置：解释「为什么开满一年比跑一次任务难」。
- 优点：是 MerchantBench 最适合手机端阅读的一张图，也最能补足文章的核心判断——长期经营难在后果姗姗来迟。
- 决策：A，优先引用；发布前确认论文图复用边界。

### 5. MerchantBench 总体机制图

- 文件：`source-assets/merchantbench-fig2-overview.png`
- 画面：选品、定价、现金流、混合延迟反馈，以及供应商、店铺、订单模拟之间的关系。
- 建议位置：介绍两套电商评测为什么不是同一张考卷。
- 优点：信息完整。
- 缺点：英文小字较多，公众号原图直发会显得密；更适合作为 APPSO 自制中文简图的事实底稿。
- 决策：B+，优先重绘，不建议原样塞正文。

### 6. MerchantBench 三次运行波动图

- 文件：`source-assets/merchantbench-fig4-run-variance.png`
- 画面：各模型在 Hermes 与 ReAct 下三次重复运行的终局净资产分布。
- 建议位置：讨论「一次跑得高」和「长期稳定地跑得高」不是一回事。
- 优点：能给 Qwen 官方单次演示补上稳定性维度。
- 限制：论文测的是 Qwen3.7-Max，不是 Qwen3.8-Max；只能作为评测方法和上一代模型的旁证，不能用来推断新模型结果。
- 决策：B+，有对应段落再用。

## 官方视频过程帧备用

以下 4 张都来自同一段 Qwen 官方电商演示，时间点按视频播放时间记录：

| 文件 | 时间点 | 内容 | 建议 |
|---|---:|---|---|
| `qwen38-ecommerce-video-25s-progress.png` | 00:25 | 早中期资产曲线 | 与 45 秒、60 秒帧组成三阶段变化时使用 |
| `qwen38-ecommerce-video-45s-progress.png` | 00:45 | 中后期资产曲线 | 备用；单独使用不如 60 秒帧完整 |
| `qwen38-ecommerce-video-60s-final-curve.png` | 01:00 | 完整资产曲线 | 正文主图 |
| `qwen38-ecommerce-video-65s-final-ranking.png` | 01:05 | 最终排名卡 | 开场第一证据图 |

四张均为 3840 × 2160 无浏览器控件截图。若正文图位有限，保留 60 秒和 65 秒两张即可；不要把四张近似曲线连续堆进正文。

## 其余备用图

| 文件 | 尺寸 | 用途判断 | 决策 |
|---|---:|---|---|
| `qwen38-official-performance.png` | 4364 × 3211 | Qwen3.8-Max 综合能力总图；内容过密，和电商主线关系弱 | C，发布背景备用 |
| `qwen38-official-release-x.jpg` | 4096 × 3014 | 官方 X 发布图，内容与综合能力总图基本重复 | C，仅作来源交叉备份 |
| `qwen38-training-env-scale.png` | 1971 × 1078 | 强化学习训练环境数量与综合得分关系 | B，只有正文谈「环境规模」时使用 |
| `qwen38-harness-generalization.png` | 4316 × 884 | 不同 Agent 框架下的泛化表现 | C，横向太长，且会把文章带离电商主线 |
| `merchantbench-fig5-operational-coherence.png` | 1162 × 383 | 月度活跃率、工具调用和净利润 | B，证据强但手机端过密，建议提炼重绘 |
| `merchantbench-fig6-product-sourcing.png` | 998 × 968 | 月度选品需求对齐变化 | C，只有正文展开季节性选品时使用 |

## 推荐的正文配图顺序

1. 官方电商标题页：告诉读者「这真是 Qwen 自己拿来展示的场景」。
2. 官方最终排名卡：尽快兑现标题里的 41 万结果。
3. 官方整年资产曲线：从终局数字转到过程。
4. MerchantBench 延迟反馈机制图：解释长期经营为什么难。
5. MerchantBench 总体机制中文重绘：区分 E-Commerce Bench 与 MerchantBench。
6. MerchantBench 三次运行波动图：只在正文确实讨论重复性和稳定性时出现。

如果要压缩到 4 张，保留 2、3、4、5；标题页可以并入封面设计。

## 来源与权利状态

### Qwen 官方素材

- 官方发布页：<https://qwen.ai/blog?id=qwen3.8>
- 官方电商演示视频：<https://cloud.video.taobao.com/vod/o9WMOJ5_YDP8ewmaVJz8HoL1oZLmW8E2ZvCozb7qFWo.mp4>
- 官方 X 帖子：<https://x.com/Alibaba_Qwen/status/2084100707423289643>
- 权利人：Qwen Team／Alibaba。
- 当前状态：`research_reference`、`review_required`。
- 原因：素材来自一手官方渠道，但页面未给出面向媒体再发布的明确开放许可。发布前需按公司编辑规范确认引用、裁切和图注方式。

### MerchantBench 论文素材

- 论文 HTML：<https://arxiv.org/html/2607.28956>
- 论文 PDF：<https://arxiv.org/pdf/2607.28956>
- 权利人：论文作者。
- 当前状态：`research_reference`、`review_required`。
- 原因：arXiv 页面标注的是 arXiv.org perpetual, non-exclusive license，不等于作者授予第三方任意商业复用。优先将 Figure 2、Figure 5 作为事实底稿重绘；若直接引用原图，保留论文题名、作者和图号。

### 平台与修改登记

- 允许平台：尚未确认。
- 已做修改：官方视频帧仅按指定时间点无控件截帧；其余均保留下载原图，没有生成式改图。
- AI 生成：否。
- 发布状态：全部未进入 `ready`。
- 第三方媒体图：本轮没有收录。搜索中出现的自媒体总榜、博客信息图和二次加工图，因版本易过时且权利链不清，已排除。

## 后续制作建议

- 封面：以官方标题页为底，另加 APPSO 自有标题排版；不要把密集 benchmark 总图直接做封面。
- 正文自制图 1：把 E-Commerce Bench 与 MerchantBench 做成中文双栏对照，所有字段逐项回链到官方发布页和论文。
- 正文自制图 2：若要讲稳定性，只提炼 MerchantBench 的三次运行差异，不把 Qwen3.7-Max 的结果偷换成 Qwen3.8-Max。
- 手机端：英文论文图发布前至少做一次 750 px 宽预览；字号读不清就重绘，不靠放大提示读者。
