# 来源

| 来源 | URL/路径 | 类型 | 访问日期 | 支持表述 | 备注 |
|---|---|---|---|---|---|
| Qwen3.8 官方发布页 | https://qwen.ai/blog?id=qwen3.8 | 厂商一手来源 | 2026-08-04 | 模型定位、2.4 万亿总参数与 950 亿激活参数；长程任务；E-Commerce Bench 设置与结果；2000 多轮交互 | 电商数据均为厂商自报；截至访问日未见该 benchmark 的论文、代码或复现入口 |
| Qwen 官方 X 公告 | https://x.com/Alibaba_Qwen/status/2084100707423289643 | 厂商一手来源 | 2026-08-04 | 2026 年 8 月 3 日发布；365 天电商策略；权重开放计划；API 与官方博客入口 | 用于核对发布时间与官方摘要 |
| Qwen 官方电商案例视频 | https://cloud.video.taobao.com/vod/o9WMOJ5_YDP8ewmaVJz8HoL1oZLmW8E2ZvCozb7qFWo.mp4 | 厂商一手视觉 | 2026-08-04 | 官方电商案例画面、资金与议价轨迹 | 仅作研究与备选；发布前必须完成图片权利登记，不默认可转载 |
| Qwen 官方电商视频封面 | https://img.alicdn.com/imgextra/i2/O1CN01VFGGPw23Iltqd8QIM_!!6000000007233-2-tps-6667-3752.png | 厂商一手视觉 | 2026-08-04 | 官方案例名称与视觉入口 | 6667 × 3752；封面主要是标题页，信息量有限 |
| MerchantBench arXiv 摘要页 | https://arxiv.org/abs/2607.28956 | 论文一手来源 | 2026-08-04 | 提交时间；365 天模拟；98,843 条记录；26 个工具；8 个模型、2 套框架、48 次运行；27.3% 口径 | arXiv v1；正式出稿前重查版本 |
| MerchantBench PDF | https://arxiv.org/pdf/2607.28956 | 论文一手来源 | 2026-08-04 | 作者单位；1688 数据；初始条件；Table 1；框架效应；活动衰减与终点记忆错误；人类样本限制 | 与 Qwen 官方 E-Commerce Bench 不同，不能横向换算结果 |

## 两套测试的关系核查

- Qwen 官方 E-Commerce Bench 使用淘宝天猫脱敏交易数据，设置为 10 万元、多家网店、约 600 家供应商与 7000 种商品，并加入自然语言议价和 152 家欺诈商家。
- MerchantBench 使用 1688 的 98,843 条商品记录与 36,576 家供应商，设置为单店、2000 元现金加 1000 元保证金、50 个商品位和订单级延迟反馈。
- Qwen 官方发布页没有提到 MerchantBench；MerchantBench v1 提交时也未评估 Qwen3.8-Max。
- 基于公开材料，只能说两者都在测 365 天电商经营中的长期一致性；不能说它们共用环境、存在直接续作关系，或用其中一套结果验证另一套。

## 历史材料

- 以 MerchantBench 为主体的第 1 版来源表已归档至 research/sources-v1-merchantbench.md。
- 旧 EcomBench 复合问答论文与遨虾商业案例退出本轮主论证，需要时只作背景检索，不进入正文结构。
