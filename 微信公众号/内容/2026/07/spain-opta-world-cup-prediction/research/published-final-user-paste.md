# 最终发表版｜待粘贴

> 请把公众号最终实际发表的版本粘贴到下面。尽量保留标题、小标题、正文、图注和图片位置；后台样式不方便复制的部分可以忽略。

<!-- 从下一行开始粘贴；不要粘到 draft.md，以免覆盖交付稿。 -->

费兰·托雷斯在加时赛第 106 分钟左脚破门，西班牙 1 比 0 力克阿根廷，时隔 16 年捧起大力神杯，梅西也完成了世界杯的最后一舞。

![img](https://ifanr.feishu.cn/space/api/box/stream/download/asynccode/?code=NGEzYjNlZDk3N2NhOTc2ZWI1MTNmNzk4ODk3NWQ3NTZfVDdnZHBadWEyZG5jV0JoU210RzF0OXVPTUJsTlhJNkxfVG9rZW46SlFHbmJjUnVzb3VGejh4N3RxaWNkU0s5bm1iXzE3ODQ2MDEyNDM6MTc4NDYwNDg0M19WNA&add_watermark=true&scene_type=CCM)

哨声一响，赛前的一组预测数字也被重新翻了出来：体育数据公司 Opta 曾用超级计算机模拟赛事，给西班牙约六成的捧杯概率，阿根廷约四成。

可这有啥好吹的，决赛就两支球队，光蒙也有一半的准头。

真正让 Opta「封神」的，是有网友扒出来，早在世界杯开赛前，它就把西班牙列成夺冠头号热门，而且它当时给出的夺冠概率前四，正好是最后杀进半决赛的那四支球队，一个不差。

![img](https://ifanr.feishu.cn/space/api/box/stream/download/asynccode/?code=NzEyZDY3MmZjMGEzOTk1YWVhMTllNDVlZTQ1MWMyNGNfalliYVgxRk4zSWV3c3BiM3JlM3JnSXd2R0FQNEJVNGVfVG9rZW46V0N1M2JuaFdrb1o3M2l4SFhtVWNMcG1nbndnXzE3ODQ2MDEyNDM6MTc4NDYwNDg0M19WNA&add_watermark=true&scene_type=CCM)

我在想，如果把这玩意用到博彩上，岂不是直接走上人生巅峰，于是 APPSO 接着扒了扒 Opta预测背后的 **2.5 万次模拟，** 看看 AI 预测真的能不靠运气吗？

*本文只复盘预测方法与公开数据，不提供投注建议。*

![img](https://ifanr.feishu.cn/space/api/box/stream/download/asynccode/?code=NzFkNmFiYjJiNTM3NjZiOThhNzk2ZDQ0ZDE5MDUwOWRfWGFCUW0weWJJTmtHTDdiaXlXUnhIdVUyb1dXQ0xpWUpfVG9rZW46TUxiQWJ0UnpBb3JVaHR4elJJU2Nwc3VNblZiXzE3ODQ2MDEyNDM6MTc4NDYwNDg0M19WNA&add_watermark=true&scene_type=CCM)

*图源：Opta Analyst，2026 年 7 月 19 日决赛前瞻。*

## Opta 从头到尾改了多少次答案?

Opta 是 Stats Perform 旗下的体育数据品牌，从 1996 年开始记录足球比赛。Stats Perform 总部在伦敦，主营比赛数据采集与分析，并向转播机构、媒体、球队和博彩平台提供统计和预测产品。

西班牙最终夺冠，Opta 也在决赛前把它列为更可能捧杯的一方。但那张「59.5% 对 40.5%」的图，只保留了最后一个节点。

同一篇决赛前瞻里，Opta 还预测了双方在 **90 分钟常规时间内** 的比赛结果。它给出的最高概率选项是西班牙获胜，但实际比赛踢到 90 分钟时，比分仍是 0 比 0。

我自己当时也按照这个结果，买了「西班牙常规时间获胜」，最后自然没有命中。西班牙虽然最终在加时赛夺冠，但对这笔投注来说，**「****猜中冠军****」****和****「****押中 90 分钟赛果****」****完全是两回事。**

![img](https://ifanr.feishu.cn/space/api/box/stream/download/asynccode/?code=OTM4MGQ1ZjU1YzI3OGRmYTM2YmY0Y2JhNzE2YTEyM2FfSHJiY2xkbjY4UVNNRVQ3Z3ZMZXdhdGNySFM4WXQ4UjRfVG9rZW46U01oTWJhSHpib3M0b254Zk16RmNIMks2blVkXzE3ODQ2MDEyNDM6MTc4NDYwNDg0M19WNA&add_watermark=true&scene_type=CCM)

*Opta 给出的 90 分钟赛果概率为西班牙胜 45%、平局 29%、阿根廷胜 26%。这与包含加时、点球的最终夺冠率不是同一口径。图源：Opta Analyst。*

开赛前，Opta 模拟了 2.5 万届世界杯。西班牙以 16.1% 的夺冠率排名第一，后面依次是法国（13.0%）、英格兰（11.2%）和阿根廷（10.4%）。一个多月后，真正站进半决赛的，正好也是这四支球队。

Opta 当时发布的是夺冠概率榜，并没有直接圈定四强名单。但榜单前四与实际四强恰好完整重合，这比「只押中西班牙」多了一层看点。

此后，西班牙的夺冠概率并非一路上涨：小组赛踢完降到 13.5%；32 强赛结束，又降到 13.0%；16 强赛结束回升到 21.3%；八强赛结束后为 23.4%。直到西班牙淘汰法国、进入决赛，夺冠率才跳到 59.5%。

![img](https://ifanr.feishu.cn/space/api/box/stream/download/asynccode/?code=N2QzY2E1ZGIwMGM4YjFlNDA3M2U1MmJkYTZhMmQ4OWZfMmVFWmlET3c3TVRiZXJRVFR6WnNtZzlVbmJaMUVYa3FfVG9rZW46SDJWSGIxdjNwb3JSR1l4c2s1UmNoZlJsbmdnXzE3ODQ2MDEyNDM6MTc4NDYwNDg0M19WNA&add_watermark=true&scene_type=CCM)

**把图里的六个数字连起来看，很容易产生一种错觉：Opta 好像随着比赛推进，越来越****「****看懂****」****了西班牙。**

但它并不是在对同一道题反复作答。每踢完一轮，模型面前的局面都变了：这队刚刚踢得怎么样、下一场碰谁、晋级路线顺不顺，全都会喂进下一次计算。

到半决赛结束，变化就更明显了。西班牙淘汰法国，阿根廷也过了关，冠军候选从四支缩到两支。这时候西班牙的夺冠率从 23.4% 蹦到 59.5%，不是模型突然开了天眼，而是它已经跨过半决赛，离冠军只剩最后一场。

换句话说，曲线往上爬的每一格，背后都是一场已经踢完、不用再猜的比赛，不确定性也被逐步消除。到决赛前只剩两支球队，59.5% 与其说是预测，不如说是算术。

至于「模拟 2.5 万次」，它解决的是另一个问题：让计算结果更加稳定。相同条件下多模拟几次，可以减少随机波动，但不能保证模型一开始估计的概率就是对的。

这就像一台没校准的体重秤，称一次显示 65 公斤，称一百次还是 65，稳得让你都想信了。可你实际可能是 75 公斤，一开始的数字就掺杂了误差。

更何况，Opta 并没公开足够完整的代码、输入和参数，外人没法把整套预测重跑一遍。西班牙这次夺冠，只能说明这一届的冠军方向押中了，没法只凭一个结果，就证明整套模型长期靠谱。

## 都是 AI 预测世界杯，做的却不是一套题

这届世界杯出现了至少四种「AI 预测」。把它们混在一起比较，准确率很容易越算越糊涂。

联想与咪咕至少留下了连续百场记录，比随手问一句「谁夺冠」扎实。AI vs the World Cup 再往前一步：统一资料与提示词、锁定版本，还要求模型给出概率；它另将赛前整套预测做成数字指纹留档。Opta 则根本不是聊天机器人，它是一条体育数据和概率的模拟pipeline。

![img](https://ifanr.feishu.cn/space/api/box/stream/download/asynccode/?code=YTYzNGM1OWM3ZGY2NjQyMTc4NGQ2ODFiNjkyNTJhOTNfTENGRE5jaEZ2dERJdk9lYmZwQ3RZdHhGcUlXQmI0Z0NfVG9rZW46QzJXdWJnTXZNb3FmSHl4azh4eWNBZXJ1bkg2XzE3ODQ2MDEyNDM6MTc4NDYwNDg0M19WNA&add_watermark=true&scene_type=CCM)

从目前公开的连续记录来看，大模型预测足球比赛，整体命中率大多在六成多。

联想和咪咕统计了世界杯前 100 场比赛。12 款模型每场都要判断主胜、平局还是客胜，攒下 1200 次预测，整体命中率 65.7%。同场活动里的普通用户呢，58.9%。

所以十二款模型加一块儿比来比去，也就比普通人多对了不到 7 个百分点。

另一个项目 **AI vs the World Cup**，则让 5 款模型使用同一份资料和同一套提问方式，持续预测整届世界杯。最终，各模型猜对比赛走向的比例约为 **68.0%—70.2%**。小组赛阶段，它们判断的是 90 分钟内谁胜、谁平、谁负；进入淘汰赛后，问题变成了哪支球队能够晋级。

不过，这两组数字不能直接拿来排高低。

它们测试的不是同一批模型，使用的资料、提问方式和更新时间不同，连「猜对」的定义也不完全一样。联想与咪咕主要统计胜平负，AI vs the World Cup 到淘汰赛阶段统计的则是晋级结果。因此，68% 不一定就比 65.7% 更强。

这些项目真正有价值的地方，是把每一场预测都提前记录下来，而不是比赛结束后只挑猜中的结果展示。至于大模型究竟比普通竞猜强多少，还需要在相同题目、相同信息和相同评分规则下，与简单预测方法以及赛前赔率进行比较。

而 Opta 做的事情又不太一样。

大模型往往是读完资料后，直接给出「谁会赢」的判断；Opta 则先建立一套专门的足球数据系统，再根据这些数据计算不同结果发生的概率。

它的数据来自长期、标准化的比赛记录。每场比赛都会有专业人员按照同一套规则，记录射门、传球、犯规等 60 多类场上事件。比赛进行时，还有其他工作人员同步检查；比赛结束后，数据还会再复核一遍，尽量减少漏记和错记。

说白了，Opta 的概率不是靠几篇赛前新闻「猜」出来的，背后依赖的是大量、长期、反复核对过的比赛数据。

下面这段 3D 重建来自 X 用户 Alexander Bogachev。他称每一次传球、射门和进球都根据 Opta 比赛事件数据还原。它不是 Opta 官方视频，但把一串结构化事件数据重新拼成了一场能看的比赛。

![img](https://ifanr.feishu.cn/space/api/box/stream/download/asynccode/?code=NzMxZDgxNGRkNzdmMGIzMzgxZTgxMTVlMWE2MDU1ZjFfUTJnVFhTNElENjVsMjRLdXR5Q1M1NExiWGh5RDNPd2JfVG9rZW46R1QwMWJsMTFkb0FzQnN4ZWNubmNmZ2pwblVoXzE3ODQ2MDEyNDM6MTc4NDYwNDg0M19WNA&add_watermark=true&scene_type=CCM)

*视频封面及视频：Alexander Bogachev / X；*

## AI 最容易栽在平局上

联想与咪咕的百场数据里，AI 对 76 场分出胜负的比赛，方向命中率达到 81.0%；遇到 24 场平局，命中率只剩 17.0%。15 场「12 款模型全错」的比赛中，11 场是平局。

APPSO 也用 Fable 5 做过一次小额实验：大模型帮我写代码、回测和查漏洞，概率则由球队实力评分（Elo）、进球分布和市场赔率来算。按本地记录拆分，23 笔投注净利 741.5 元，但样本太小，中途还有临时加注。回看 72 场小组赛，模型第一选择命中 44 场，却一次都没把平局列为最可能结果；

猜对六成，照样可能亏钱。假设每一笔赔率都是 1.60，命中率为 60%，粗略期望仍是 `0.6 × 1.6 - 1 = -4%`。

足球是低比分项目。一张红牌、一次折射或门将的一次判断，足以让最可能的结果输给第二、第三可能。模型可以给这些小概率结果留出位置，却没法提前知道意外会在哪一分钟发生。比如最后一场的冠军预测，模型虽然猜对了西班牙胜利，却没料到90分钟内0:0平局，而加时赛是不计入胜平负投注结果的。

![img](https://ifanr.feishu.cn/space/api/box/stream/download/asynccode/?code=Mzc4NDU4ZjEwMGY1YzY2ZDAwZmZiMWZlYTc4MWE1YWFfdVNIQ0xIcjZTbVJDOWRyV0ZVVm9ickp2ZU1NcU0wQTdfVG9rZW46WWM0dGJ5dU53bzRrUEd4TEhsc2MyQTU3bmJiXzE3ODQ2MDEyNDM6MTc4NDYwNDg0M19WNA&add_watermark=true&scene_type=CCM)

实际上，Opta 这套预测技术早就不只是用来做「谁会夺冠」的营销了，博彩公司也一直在用。Stats Perform 是一家专门收集和提供体育比赛数据的公司。FIFA 授权它把世界杯的官方比赛数据提供给合法博彩公司。博彩公司拿到这些数据后，会用来计算赔率、比赛过程中实时调整赔率，并在赛后确认投注结果。

另外，像 Sportradar 这样的体育数据公司也提到，机器学习会帮助博彩公司定赔率、根据投注情况调整赔率，以及发现异常投注、控制可能的损失。

这些合作说明，AI 和数据模型已经进入博彩公司的生产系统，用于提速、批量处理和辅助定价，是真的能「搞钱」。

但作为普通人要注意，**普通人拿到同一批公开信息，也不等于能长期赢过市场；博彩公司在用模型，赔率里还留着它们的利润****，他们早就把意外提前算进概率里。**

## 资料来源

- [Opta：2026 世界杯开赛前预测](https://theanalyst.com/articles/who-will-win-2026-fifa-world-cup-predictions-opta-supercomputer)
- [Opta：小组赛后预测](https://theanalyst.com/articles/world-cup-2026-knockout-stage-predictions-opta-supercomputer)
- [Opta：32 强赛后预测](https://theanalyst.com/articles/world-cup-predictions-2026-quarter-finals-opta-supercomputer)
- [Opta：16 强赛后预测](https://theanalyst.com/articles/world-cup-2026-quarter-final-predictions-opta-supercomputer)
- [Opta：八强赛后预测](https://theanalyst.com/articles/world-cup-2026-semi-final-predictions-opta-supercomputer)
- [Opta：西班牙对阿根廷决赛前预测](https://theanalyst.com/articles/spain-vs-argentina-prediction-world-cup-final-2026-match-preview)
- [Stats Perform：公司概览与 Opta 品牌关系](https://developers.statsperform.com/what-is-stats-perform)
- [Opta：足球事件定义与数据复核](https://optaplayerstats.statsperform.com/en_GB/about)
- [新浪财经转引联想与咪咕《世界杯预测人机大战百场观察》](https://finance.sina.com.cn/roll/2026-07-14/doc-inihuhix4097104.shtml)
- [新浪科技：12 款大模型的决赛前预测](https://finance.sina.com.cn/tob/2026-07-19/doc-iniikaqx3316612.shtml)
- [AI vs the World Cup：方法与固定协议](https://aiworldcup.io/methodology.html)
- [AI vs the World Cup：完赛排行榜数据](https://aiworldcup.io/data/grades/leaderboard.json)
- [Kimi：300 个 Agent 预测世界杯](https://www.kimi.com/zh-cn/showcases/websites/world-cup-2026-prediction)
- [FIFA：Stats Perform 成为官方投注数据分销商](https://inside.fifa.com/tournament-organisation/commercial/media-releases/stats-perform-official-worldwide-betting-data-streaming-rights-distributor-world-cup)
- [Sportradar 2025 年 20-F：AI 在赔率与风控中的用途](https://www.sec.gov/Archives/edgar/data/1836470/000110465926035485/srad-20251231x20f.htm)
- [Applied Economics：足球与网球投注市场的实际损失率研究](https://www.tandfonline.com/doi/full/10.1080/00036846.2025.2507979)
- [Alexander Bogachev：世界杯决赛事件数据 3D 重建原帖](https://x.com/bogachev_al/status/2078968779212816405/video/1)

> 注：联想与咪咕的准确率为活动方公布口径；AI vs the World Cup 的模型池、输入、更新时间和评分任务均不同，两者不能直接排名。个人实验只按本地记录复算，未经过票根或支付流水的独立核验。比赛与预测信息截至 2026 年 7 月 20 日。
