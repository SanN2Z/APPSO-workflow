---
schema_version: 1
content_id: 'qwen38max-ecommerce-365-days'
title: 'Qwen3.8-Max 开了一年网店，把 10 万滚到了 41 万'
platform: wechat
source_status: research
review_kind: feedback
review_status: open
created: 2026-08-04
updated: 2026-08-04
next_review_on: 2026-08-11
sop_promotions: 0
---

# 内容复盘：Qwen3.8-Max 开了一年网店，把 10 万滚到了 41 万

## 本轮结果

- 交付阶段：选题调研与故事合同讨论
- 目标：用调整后的 SOP 先锁定 APPSO 大纲，再进入完整正文
- 观察结果：第 1 版把 MerchantBench 当成新闻主体，虽然论证完整，却错过 Qwen3.8-Max 正式发布的热点入口
- 当前修复：第 2 版以 Qwen3.8-Max 官方 E-Commerce Bench 为主体，MerchantBench 后置为多角度辅助

## 证据清单

- brief：brief.md
- 写作真源：draft.md
- 故事合同：research/judgment-workshop.md
- 第 1 版大纲：research/outline-v1-merchantbench.md
- 第 1 版故事合同：research/judgment-workshop-v1-merchantbench.md
- 用户与编辑反馈：本文件反馈台账

## 反馈台账

| ID | 来源 / 日期 | 阶段 | 反馈 | 要求修改 | 读者 / 业务损失 | 根因 | 修复与版本 | 验证 | 分级 | 去向 |
|---|---|---|---|---|---|---|---|---|---|---|
| FB-20260804-001 | 用户 / 2026-08-04 | research / 故事合同讨论 | 「没蹭上 Qwen3.8-Max 的热点，主体还得是官方发布页的电商模拟，然后 MerchantBench 做多角度辅助」 | 交换主体与辅助材料的层级 | 标题、开场和第一追问都像论文解释稿；读者看不出当天发布事件，APPSO 的时效价值被削弱 | 来源层级与叙事角色倒置：最新一手事件被降为背景，辅助研究反而控制整条结构 | 第 2 版重写标题、开场、四拍叙事链和对照表；旧版完整归档 | draft.md 首屏即出现 Qwen3.8-Max、10 万到 41 万和官方任务；MerchantBench 到第二节才进入，移除它仍不影响新闻事实成立 | internal | case_only |

## 因果复盘

先发现 MerchantBench 的研究信息密度更高
→ 把最容易展开的材料误当成最该占据标题的材料
→ 大纲具备解释深度，却失去 Qwen3.8-Max 正式发布这一时间锚
→ 用户无法从标题与开场判断文章为何现在要发
→ 重开故事合同，把官方发布设为主体，把 MerchantBench 拆成机制、代际、框架和边界四类辅助
→ 用首屏主体测试与删除辅助材料测试验证

## 经验分级

### 仅保留在本案例

- Qwen3.8-Max 官方 E-Commerce Bench 是本稿的热点主体。
- MerchantBench 只作机制解释、Qwen3.7-Max 上一代切片、框架效应与证据边界。
- 4.16× 是期末总现金相对启动资金的倍数，不写成能力提升 4 倍。

### 继续观察

- 若后续反复出现「研究材料比新闻事件更详细，于是抢走主体」的问题，再评估是否需要加入通用回归检查。

### SOP 候选

- 无。本轮属于单案的事件层级判断，不新增通用规则。

## SOP 变更

| 规则 ID | 真源 SOP | 触发条件 | 动作 | 通过标准 | 来源案例 | 回归检查 | 结果 |
|---|---|---|---|---|---|---|---|

## 下一轮动作

- [x] 核对 Qwen 官方电商模拟的设置、比较基线和 4.16× 口径
- [x] 核对它与 MerchantBench 是否共用环境
- [x] 重写 brief、事实卡、故事合同和大纲
- [ ] 用户确认第 2 版标题、结构与结尾后，再进入完整正文
- [ ] 出稿前重查 E-Commerce Bench 是否新增论文、代码或复现协议

## 未解决问题

- Qwen 官方尚未公开 E-Commerce Bench 的重复运行次数、随机种子、推理成本与完整模型列表。
- 官方视频中的可用画面仍需逐帧核对并完成权利登记。
