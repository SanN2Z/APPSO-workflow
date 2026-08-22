# HubSpot 的 AI 销售员「干完活才收费」，可客户还没回信

一个产品最尴尬的发布日期，大概是日历翻到了那天，介绍它的公告却先失效了。

HubSpot 原定在 8 月 4 日上线 Contact Discovery：帮销售找出、核验并添加新的联系人。可到了这个时间点，7 月 1 日的原公告顶部已经挂出更新，明确说相关更新与条款不再生效。HubSpot 在 7 月 5 日撤回条款时承诺，会重新把数据补全的 opt-in 和治理讲清楚。

这不等于产品取消，也不代表它已经延期。截至本轮核查，官方只留下一个不能硬填的空格：Contact Discovery 究竟有没有按原计划上线，尚未在已核入口重新确认。

但这条反常时间线，恰好戳中了 HubSpot 另一句更抓眼球的话：AI 销售员可以「干完活再收费」。

官方给 Prospecting Agent 挂出的价签是每个 lead 1 美元。问题来了——一名陌生客户连邮件都没回，AI 到底把什么活干完了？

## 这 1 美元，停在回复之前

HubSpot 把这套方式叫作 outcome-based pricing，也就是「按结果收费」。

再往计费表里看一层，这个结果的落点很具体：为一名 lead「推荐外联」，消耗 100 credits；产品页的写法略有不同，是 Agent 为 lead 草拟外联时收费。额外 credits 的公开单价为 0.01 美元，因此对应 1 美元。套餐里也可能已经包含 credits，所以这不一定表现为每次单独刷走 1 美元，但计费事件没有变。

此时，客户还没有回复。会议没约，订单更没签。

「结果」这个词，被提前了好几站。

把这条收费线画在销售漏斗上，它更像设在中途的闸机：AI 找到了一个值得联系的人，准备好了外联内容，系统便认为任务完成。至于这封信后来有没有被打开、有没有换来一次对话，都在闸机后面。

所以，1 美元买到的不是成交承诺。它买的是一段已经打包的销售准备工作。

这段工作够不够值钱，要继续往前拆。

## 写邮件，反而是容易看见的那一步

Prospecting Agent 并非只负责憋出一封「您好，注意到贵司最近……」式邮件。

按官方产品页和知识库的描述，它会监测购买信号、研究目标账户、识别联系人，再草拟个性化外联。销售可以先审核再发送，也可以配置自动发送。也就是说，计费单位里至少塞进了找公司、找人、判断时机和写第一封信这几步。

其中最容易展示的是文案。几十秒生成一封像样的邮件，录屏看起来很顺。

更难验收的是前面那个人选。

联系人职位已经变化，工作邮箱无法送达，或者这个人压根不负责采购，后面的个性化写得越认真，浪费得越完整。反过来，只要人和时机选得准，哪怕销售最后自己改写邮件，Agent 仍然可能省下大量搜索和整理时间。

于是，1 美元的含金量没有落在一句文案上。它被联系人质量、购买信号和账户上下文托着。也正因如此，一款 AI 销售工具越想证明自己「懂客户」，就越绕不开一个不太适合放进炫技 Demo 的问题：这些信息从哪来？

## 找对人之前，先说清数据从哪来

原定上线的 Contact Discovery，正是为了补上「找人」这块。HubSpot 当时说，它能找到、核验并添加 CRM 中原本没有的联系人，还把可靠性与一个共享数据集联系起来。

争议随即从功能滑到了数据边界。4 天后，HubSpot 撤回了对应的条款变更，称此前没有把选择权解释清楚，并承诺未来凡是使用客户数据的新 enrichment 能力，都要透明 opt-in。

这里得踩一下刹车：这件事不能简写成「HubSpot 要把整个 CRM 拿去卖」。当前数据补全文档写得更窄——enrichment 默认关闭，用姓名、工作邮箱、公司域名等有限商务字段做匹配；经过特定补全流程并核验通过的有限字段，可能进入 HubSpot 的商业数据集。文档也明确说，不会使用整个 CRM。

现行 enrichment 和原公告里的 Contact Discovery 也不能直接画等号。前者是当前文档说明，后者的相关更新和条款已经失效，产品去向仍待官方确认。

还有一处容易串台：AI model training 与 enrichment 是两套独立设置。关掉模型训练，不会顺手关掉数据补全；反过来也一样。管理员面对的不是一个总开关，而是几套各管一段的数据路径。

对 AI Agent 来说，context 越丰富，推荐可能越像样；对付费团队来说，数据从哪里进入、由谁同意、能否退出，同样属于产品成本。这些控制不直接证明 Agent 值 1 美元，却决定这 1 美元能不能放心地花。

## 「推荐外联」可以收费，前提是允许验货

公平地说，把推荐外联设成收费单位，并不荒唐。

回复、会议和成交还会受到销售执行、产品吸引力、报价与市场环境影响。若一定等到签单才向 Agent 计费，责任很难切清，反馈周期也会被拉得很长。相比之下，「已找到联系人并准备好外联」是厂商更能控制的交付节点。

这条边界可以操作，但「可以计费」不等于「已经证明有效」。目前缺的恰好是决定采购体验的数字：推荐联系人的独立准确率、销售复核一条需要多久、错误或重复联系人如何处理、被拒绝的推荐能否免费重试或退回 credits，以及端到端的回复、会议和成交有没有提升。

这些空白不能反过来证明产品无效。它们只说明，看见「按结果收费」四个字，先别急着把风险转移的奖杯递给厂商。

判断下一款 outcome-based Agent，可以先追着账单问 4 句：哪个动作会扣 credits？谁来验收，丢弃也算完成吗？联系人错误或外联失败，是否免费重做？用到了 CRM、第三方数据库还是共享 enrichment，管理员能关到哪一层？

问完这 4 句，「结果」才从营销词变成可以验货的产品单位。

HubSpot 的 1 美元并没有等到客户回信。它买到的是一次准备就绪的外联推荐。值不值，答案不在「干完活才收费」这句话里，而在那个联系人是否靠谱、销售还要补多少活，以及选错以后谁来付第二次钱。

<!--
实际来源：
- HubSpot Prospecting Agent 产品页：https://www.hubspot.com/products/sales/ai-prospecting-agent
- HubSpot Product & Services Catalog：https://legal.hubspot.com/hubspot-product-and-services-catalog
- HubSpot outcome-based pricing 公告：https://www.hubspot.com/company-news/hubspots-customer-agent-and-prospecting-agent-now-you-pay-when-the-task-is-complete
- HubSpot Prospecting Agent buying signals 文档：https://knowledge.hubspot.com/prospecting/prospect-companies-with-buying-signals
- HubSpot Contact Discovery 原公告：https://community.hubspot.com/t/july-1-2026-contact-discovery-is-coming-soon-legal-update/151430
- HubSpot 撤回说明：https://community.hubspot.com/t/we-got-this-wrong-and-we-are-fixing-it/152063
- HubSpot Data enrichment 工作方式：https://knowledge.hubspot.com/records/how-data-enrichment-works-in-hubspot
- HubSpot AI model training 文档：https://knowledge.hubspot.com/account-management/hubspot-ai-mode-training

作者推断：
- 计费发生在回复、会议、成交之前，因此 HubSpot 所称的 outcome 是厂商定义的工作流节点。
- 联系人质量与可治理的 context 会显著影响这项收费单位的含金量；把推荐外联设为收费节点有可控性上的合理性，但不能替代验收证据。

保留未知项：
- Contact Discovery 截至冻结时间究竟上线、延期还是取消。
- 推荐准确率、人工复核时长、错误／重复联系人比例、退 credit 或免费重试规则，以及端到端回复、会议、成交提升。
- 当前 beta、第三方 contact sourcing 与 Contact Discovery 是否被 HubSpot 视为同一产品。

自查：
- 事实边界：通过。仅使用 frozen-input、sources.md 与 fact-sheet.md 登记事实；未把厂商自报当独立效果，未猜测 Contact Discovery 状态，未把 enrichment 写成出售整个 CRM。
- 骨架差异：通过。按 Candidate B 合同从失效的 8 月 4 日原公告切入，首屏转向 1 美元 outcome，再用「上线谜团为何牵出找人质量」推进；未读取或复用其他候选与现成同题大纲。
-->
