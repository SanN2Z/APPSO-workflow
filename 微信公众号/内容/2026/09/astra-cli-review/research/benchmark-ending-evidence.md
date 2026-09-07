# FB020｜权威跑分图与清晰结尾

核对日期：2026-09-05。作者不接受前版泛化的品牌／多智能体趋势结尾，要求评测节使用权威跑分图，并提供六组 OpenAI 对比数字。

## 原始数据

[OpenAI 发布页](https://openai.com/index/gpt-6-astra/) Professional / Coding / Academic 原表逐项核对：

| 指标 | Astra | Fable 5.1 |
|---|---:|---:|
| Terminal-Bench 4.0 | 57.9% | 55.8% |
| DeepSWE v1.1 | 74.1% | 67.4% |
| Terminal-Bench Science 0.1 | 64.6% | 52.6% |
| FrontierMath Tier 4（v2） | 97.6% | 87.8% |
| HLE（带工具） | 57.2% | 65.0% |
| AA Intelligence Index v4.1.1 | 61.2 | 65.7 |

全部与用户所给数字一致。版本名补全；最后一项不是百分比，也不声称是 AA 实时 v4.2 排名。官方页说明成绩取不同 effort 的最高值，研究环境／API 与实际产品可能不同。

## 真实跑分图

[Artificial Analysis，9 月 3 日测评](https://artificialanalysis.ai/articles/benchmarking-gpt-6-astra) 下载三张 CDN 原图，实际使用 1 和 3。原图、指纹和下载地址见 benchmark-originals-receipt.json。

- 原图 1：上为 Intelligence Index v4.1.1，下为 Coding Agent Index v1.4。编程 Astra / Codex / max 约 67；Fable 5.1 / Claude Code / max with fallback 约 70。图内数值取整，不能要求与官方表的小数逐位一致。
- 原图 2：Token 效率，研究备用，不为凑图加入正文。
- 原图 3：Coding Agent Index 对单任务 API 费用。Astra xhigh 3.27 美元、max 4.72 美元，指数都约 67；Fable 5.1 max with fallback 9.18 美元，约 70。成本是这套测试的均值，不是固定单任务售价、订阅扣额公式或用户本轮用量。
- [Cognition](https://devin.ai/blog/gpt-6-astra) 仍仅一句标为产品公司的自有测试，不能充当全部独立榜单结论。

本机浏览器打开 OpenAI 原页遇到 Cloudflare 验证，Cognition 遇到 Vercel 验证；未获得它们的原生图截图，也未重绘页面冒充官方图。OpenAI 数字通过 web 获取的原始正文核对，以可读表格摘录；权威图实际来自 AA 的第一方 CDN。

## 本次写作选择与局限

删除旧版 Figma 品牌库、Opus 4.5 游戏制作器与 Fusion 分工的结尾展开，历史保存在 history/2026-09-05-before-benchmark-ending.md。它们各自有来源，但在这一篇里引入太多话题，没形成清楚结论。

新版结尾只谈推理档位的分数／费用差别，以具体数值提供增量。末段是作者可审的用法建议，不冒充已测过不同档位。保留游戏、网页、作者判断与已更正的模型归属。

自查：没有写综合冠军、没有把 USD 换算订阅额度、没有用重绘图替代跑分原图；原图未经裁切或更改。来源版权状态仍 pending，整篇保持 draft。
