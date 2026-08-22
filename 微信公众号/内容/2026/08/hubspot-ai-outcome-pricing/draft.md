---
title: "HubSpot 的 AI 销售员「干完活才收费」，可客户还没回信"
platform: wechat
status: editorial_review
created: 2026-08-04
updated: 2026-08-04
as_of: "2026-08-04 02:00+09:00"
fact_checked: true
rights_checked: false
copyedit_checked: true
copyedit_body_sha256: "b51a3a1f684b81b66d520f280da01cc75b129075e5a593bacc13fd9fcf28e1f2"
published_url: ""
selection_round: "research/candidates/round-01"
selected_candidate: "A"
selected_candidate_sha256: "d9b931e5da868804267a6fe11f803ddea954f25e7268692f49a5135b0789be4c"
writing_mode: company
project_adapter: appsso
---

# HubSpot 的 AI 销售员「干完活才收费」，可客户还没回信

客户没有回复。

邮件还可能躺在销售的「待审核」列表里。会议没约上，合同更没影。但按 HubSpot 的公开说明，系统这时已经可能扣掉 HubSpot Credits。

可 HubSpot 的三份公开说明没有把扣费线画在完全同一个按钮上：[产品目录](https://legal.hubspot.com/hubspot-product-and-services-catalog)写的是「为一个 lead（销售线索）推荐外联」，消耗 100 credits；[产品页](https://www.hubspot.com/products/sales/ai-prospecting-agent)写的是「为 lead 草拟外联」，价格为每个 lead 1 美元；[7 月 3 日更新的设置指南](https://knowledge.hubspot.com/prospecting/use-the-prospecting-agent)则说，lead 被加入销售跟进流程（enrolled for prospecting）时消耗 credits。

页面没有解释这处错位，可能涉及版本或更新节奏。能确定的共同点只有一个：扣费发生时，客户还没回复，会议和成交更在后面。

HubSpot 把它叫作 [outcome-based pricing](https://www.hubspot.com/company-news/hubspots-customer-agent-and-prospecting-agent-now-you-pay-when-the-task-is-complete)，也就是「按结果收费」。那就得多问一句：谁的结果？

## 这 1 美元，停在漏斗半路

把一次销售外联摊开，大致会经过这些动作：盯购买信号、挑公司、找联系人、研究账户、写第一封信、审核、发送，然后才轮到回复、会议和成交。

三份说明虽然没对齐，却都挤在这条漏斗的前半段。站在 Agent 这边，加入跟进流程、推荐外联或草拟外联，已经足够形成一次可计费工作；站在付钱的团队这边，能影响收入的结果还没登场。

当前知识库还把任务分成了几个状态。「Ready for review」代表邮件已经写好、还没发送；「Finished」也不只代表客户回复或约了会议，还可能代表客户一直没回，但预定邮件已经全部发完。

HubSpot 所说的 outcome，是产品定义的工作节点，不是客户定义的生意结果。相较于按 token 或调用次数收费，这条线确实往业务流程里多走了几步，只是还没走到客户回复。

这里的「每个 lead 1 美元」是官方标出的单价，不代表每执行一次就从银行卡另扣 1 美元，套餐本身也可能带 credits。要判断划不划算，得先看这笔 credits 究竟买下了什么。

## 一张收费单里，塞进了一段销售准备

按 HubSpot 的产品页和知识库，Prospecting Agent 会研究账户、寻找联系人，再草拟个性化外联。销售可以逐封审核，也可以让它自动发送。

按产品目录和产品页的口径，100 credits 买下的是一段打包好的销售准备：从「这家公司可能值得看」，一路做到「这位联系人已经有一封可发的信」。

这个交付物当然可能值钱。人工找人、翻资料、整理联系理由、起草第一封信，同样要付出时间。要是 Agent 找得准、写得能用、销售看一眼就能放行，1 美元并不离谱。

可一旦收件人找错，文案写得再顺，整段准备工作都会变成一张精致的废票。Agent 的含金量，也就从「会不会写」滑到了「凭什么认定该联系这个人」。

这个问题往回追，落脚点很快就从文案移到了数据。

## 找对一个人，要先说清数据从哪来

HubSpot 曾宣布，Contact Discovery 会在 8 月 4 日上线。[原公告](https://community.hubspot.com/t/july-1-2026-contact-discovery-is-coming-soon-legal-update/151430)称，它可以寻找、核验并添加新联系人，而联系人可靠性来自一套共享数据集。

这项计划一公布，CRM 里的数据会不会被拿去帮别人找人，立刻成了争议中心。HubSpot 在 7 月 1 日发布相关条款，4 天后又[撤回变更](https://community.hubspot.com/t/we-got-this-wrong-and-we-are-fixing-it/152063)，承认透明度没做到位，并表示会重新设计更清楚、更容易治理的 opt-in。

撤回的是条款，不能顺手推导成产品一定取消。原公告顶部现在只写着「这次更新及相关条款不再生效」。截至东京时间 8 月 4 日 2 时、美国仍是 8 月 3 日，HubSpot 的官方新闻中心、社区公告和知识库中，尚未见到另一份公告确认 Contact Discovery 会照常上线、延期或取消。此时没有新消息，不能替产品补结局。

能确认的是当前规则。[最新 enrichment 文档](https://knowledge.hubspot.com/records/how-data-enrichment-works-in-hubspot)写明，这项能力默认关闭；用于匹配的是姓名、工作邮箱和公司域名等有限商务字段，经过 enrichment 且验证通过的少量字段可能进入 HubSpot 的商业数据集。HubSpot 同时明确称，不会用整个 CRM 做 enrichment。

[AI model training](https://knowledge.hubspot.com/account-management/hubspot-ai-mode-training) 又是另一只开关：普通账户中默认开启，管理员可以关闭；启用 Sensitive Data 的账户默认退出 AI model training，且不能选择加入。关掉训练不会连带关掉 enrichment，反过来也一样。

所以，把这场争议说成「HubSpot 要卖掉整个 CRM」并不准确。争议落到具体操作上，就是哪些字段会进入共享商业数据集，谁点下同意，管理员能不能看懂并收回选择。

AI 销售员越想显得「懂客户」，越依赖可用、准确、又能被治理的上下文。写信模型只是台前那一小块。

## 这条收费线可以合理，但还没通过验收

站在 HubSpot 一边，也有一个很有力的解释：回复和成交并不完全受软件控制。销售怎么跟进、产品有没有竞争力、报价是否合适、市场当时冷不冷，都会改写最后结果。把「推荐一个适合外联的销售线索」设为收费单位，边界清楚，也更容易执行。

这个解释成立，但还不够完成验收。HubSpot 自己的三份公开说明都没有把扣费点写在同一步；现有公开材料也没有给出独立的推荐准确率，没有回答销售平均要花多少时间复核、错误联系人能否免费重试或退回 credits，更没有足够证据把一次推荐和最终回复、会议、成交稳定地连起来。

评估这类 Agent 时，可以把四个问题直接贴在产品动作上：

第一，你正在使用的版本，究竟在哪个动作上消耗 credits？是加入跟进流程、推荐外联、生成草稿，还是邮件真正发出？

第二，谁来验收「完成」？销售拒绝一条明显不合格的推荐时，它还算结果吗？

第三，错人、重复联系人和低质量草稿怎样返工？能否免费重试、能否退还 credits，加上人工复核要多久，都会改写 1 美元的真实成本。

第四，联系人来自哪里？补全是否默认关闭、怎样 opt-in，AI 训练和 enrichment 能否分别控制？

无论扣费点最终落在加入跟进流程、推荐还是草拟，HubSpot 的这 1 美元都不买回信。它买的是一段准备好交给销售处理的外联工作。

联系人找得准、草稿改两下就能发，这笔钱可能很划算；找错人、重复推荐、每封都得重写，它只是把搜索时间换成了更贵的人工复核。公开材料还不够替任何团队做判断。

下次再看到「按结果收费」，别先算每单多少钱。先看系统在哪个动作上扣掉 credits，再数这个动作离你要的结果还有几步。
