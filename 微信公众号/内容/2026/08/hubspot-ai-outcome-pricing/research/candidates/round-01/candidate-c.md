# AI 销售员显示「Ready for review」时，1 美元已经花出去了

HubSpot 的官方文档里，有个很平常的状态：`Ready for review`。

意思不难懂。AI 销售员找到了值得联系的人，做完账户研究，也写好了第一封外联，正等真人看一眼。客户还没回复，会议自然也没开，更别说成交。

但收费线已经到了。

HubSpot 给 Prospecting Agent 挂出的价签是每个 lead 1 美元。产品页说，Agent 为 lead 草拟外联时收费；产品与服务目录的写法则是，每次「Recommend outreach for one lead」消耗 100 credits。额外 credits 的公开单价为 0.01 美元，正好也是 1 美元。不同套餐可能自带 credits，所以它不等于每次都要额外刷 1 美元，但「哪一步算完成」已经写得很明白。

HubSpot 把这种模式叫 outcome-based pricing，还强调任务完成才收费。问题随之冒出来：销售还在 review，谁的 outcome 已经发生了？

## 一条待审记录，里面塞了四份活

先别急着把这 1 美元理解成「AI 写了一封邮件」。

按 HubSpot 的产品说明，Prospecting Agent 会监测购买信号、研究账户、识别联系人，再生成个性化外联。销售可以审核后发送，也可以按配置自动发送。当前的 buying signals 与 contact sourcing beta 还能接入 Apollo、Surfe、ZoomInfo、Seamless 等第三方联系人来源。

也就是说，`Ready for review` 前面压着一段完整的销售准备工作：现在找谁、为什么找他、对这家公司知道多少、第一句话该怎么说。写信只是最后露在水面上的那一点。

这也让 review 变得很实在。从任务组成看，销售至少要判断：联系人是否对路，购买信号是否足以支撑这次触达，账户研究有没有跑偏，草稿能不能直接发。任何一项拿不准，人工审核就不能只看两眼语气。

遗憾的是，公开材料没有给出这部分最有用的数字：推荐准确率是多少，平均要审多久，错误联系人能不能拒收，重做是否再次扣 credit。于是 1 美元买到多少准备工作可以看见，验收它还要花多少人的时间，看不见。

## 审核「找谁」，迟早会追到数据从哪来

外联文案写得普通，销售还能改。人找错了，后面的个性化往往只是把错误写得更像真的。

HubSpot 自己也把 Agent 的表现和 context 连在一起：CRM 里的记录与互动、用户设定的销售 plays、购买信号，以及外部联系人来源，都会影响它为何推荐这个人。模型能不能写出一封顺口的邮件，只是其中一环；它有没有找到一个可联系、值得此刻联系的人，才决定那张待审记录有没有用。

这条线在 7 月碰上了一次急刹车。

HubSpot 原定在 8 月 4 日推出 Contact Discovery，用来寻找、核验并添加新的联系人。原公告把联系人可靠性和一个共享数据集联系起来。7 月 5 日，HubSpot 撤回了 7 月 1 日公布的条款变更，承认此前做法没有把选择权和控制讲清楚，并承诺未来凡是使用客户数据的新 enrichment 能力，都要透明 opt-in。原公告顶部现在也明确标注：相关更新和条款不再生效。

这里不能顺手补一个戏剧性结局。截至本轮核查，已查官方入口没有重新确认 Contact Discovery 究竟按计划上线、延期还是取消；核查发生在东京 8 月 4 日凌晨，当时美国仍是 8 月 3 日。能写的只有「原定」，不能拿暂时没看见公告替产品判状态。

## 不是整座 CRM 被搬走，但开关也没简单到一个

现行 enrichment 文档给出的边界，比「拿客户数据做共享库」这句话细得多。

当前 enrichment 默认关闭，需要用户启用。用于匹配的是姓名、工作邮箱、公司域名等有限商务字段；部分经过 enrichment 处理并核验通过的字段，可能进入 HubSpot 的商业数据集。官方同时写明，不会把整个 CRM 用于 enrichment。

所以，把争议压成「HubSpot 要卖掉整座 CRM」，并不准确。可默认关闭也没有自动回答另一串问题：哪些记录会进入数据集，谁有权限开启，数据主体退出后怎么处理，销售在审核联系人时能否看懂来源。

还有一个容易串线的地方：AI model training 和 enrichment 是两套独立设置。普通账户的模型训练开关默认开启，敏感数据账户例外；管理员可以关闭。但关闭训练不会顺手关闭 enrichment，反过来也一样。把「是否拿数据训练 AI」和「是否用数据补全联系人」揉成一个总开关，会把能控制什么也说糊涂。

这场条款风波至少揭开了一件事：AI 销售员的含金量，很大一部分埋在联系人和 context 里。文案模型再会说话，也补不了一个来源不清、职位过期或根本不该联系的人。后半句是产品常识，前半句还需要准确率和人工审核数据来证明。

## 「推荐外联」可以收费，但别把验收藏起来

替 HubSpot 说句公道话：把「推荐一个可外联的 lead」设成收费单位，并非天然不合理。

客户回不回复，会受销售执行、产品吸引力、报价和市场时机影响；会议开不开、订单成不成，就更难全算在 Agent 头上。厂商如果坚持成交后才收钱，双方很快会陷入归因扯皮。相比之下，推荐外联是厂商能够交付、用户也能检查的一步。

可「边界容易计费」与「结果已经被证明」之间，还隔着那次 review。HubSpot 目前没有公开独立准确率、平均复核时间、错误推荐的拒收与退 credit 规则，也没有足以把这 1 美元一路连到回复、会议或成交的独立证据。这些空白不能证明产品无效，却足以阻止人只看见 outcome 这个漂亮标签。

以后再遇到「只为结果付费」的 AI Agent，可以先沿产品动作找四个位置：credit 在哪一步扣掉，谁点头才算验收，拒绝或重做怎么计费，支撑结果的数据从哪来、由谁开启。

四个位置都说清楚，`Ready for review` 才可能是一份便宜的成品。否则，它更像一张 1 美元的待办：AI 说自己干完了，接下来轮到人类判断这活到底算不算数。

<!--
实际使用来源：
- HubSpot Prospecting Agent 产品页：https://www.hubspot.com/products/sales/ai-prospecting-agent
- HubSpot Product & Services Catalog：https://legal.hubspot.com/hubspot-product-and-services-catalog
- HubSpot outcome-based pricing 公告：https://www.hubspot.com/company-news/hubspots-customer-agent-and-prospecting-agent-now-you-pay-when-the-task-is-complete
- HubSpot buying signals 文档：https://knowledge.hubspot.com/prospecting/prospect-companies-with-buying-signals
- Contact Discovery 原公告（已标相关更新失效）：https://community.hubspot.com/t/july-1-2026-contact-discovery-is-coming-soon-legal-update/151430
- HubSpot 7 月 5 日撤回说明：https://community.hubspot.com/t/we-got-this-wrong-and-we-are-fixing-it/152063
- HubSpot data enrichment 文档：https://knowledge.hubspot.com/records/how-data-enrichment-works-in-hubspot
- HubSpot AI model training 文档：https://knowledge.hubspot.com/account-management/hubspot-ai-mode-training

作者推断：
- 计费发生在客户回复、会议和成交之前，因此厂商所称「结果」对应销售流程中的可交付节点。
- 从任务组成看，人工审核至少需要判断联系人、信号、研究内容和外联草稿；实际界面字段与审核时长未作推断。
- 推荐外联可能是合理收费边界，但其价值仍取决于准确率、验收时间、失败处理和数据治理。

保留未知项：
- Contact Discovery 在 8 月 4 日是否上线、延期或取消。
- 独立推荐准确率、平均人工复核时长、错误联系人比例、拒收／重试／退 credit 规则及端到端转化。
- 当前 beta、第三方 contact sourcing 与 Contact Discovery 的产品关系。

自查：
- 事实边界：通过。未越出 frozen-input、sources.md 与 fact-sheet.md；未把厂商自报当独立效果，未写 Contact Discovery 当前状态或法律结论，未写成出售整个 CRM。
- 骨架差异：通过。以 `Ready for review` 为入口，沿「审核内容 → 联系人质量 → 数据来源 → 验收条件」逆向展开；未读取或复用其他候选。
-->
