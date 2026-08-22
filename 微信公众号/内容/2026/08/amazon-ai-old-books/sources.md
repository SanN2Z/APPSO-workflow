# 来源

核验时点：2026-08-18 09:52+08:00。公开正文只保留正常来源归属与会改变事实含义的不确定性；信源强弱和访问情况留在本文件。

| ID | 来源 | URL/路径 | 类型 | 访问日期 | 支持表述 | 备注 |
|---|---|---|---|---|---|---|
| S1 | 404 Media：We Tracked a Shipment of Rare Books. It Ended at an Amazon AI Training Facility | https://www.404media.co/we-tracked-a-shipment-of-rare-books-it-ended-at-an-amazon-ai-training-facility/ | 原始追踪调查 | 2026-08-18 | 追踪器、Amazon 拉斯维加斯设施、VGT3 员工描述、Amazon 回应 | 当前事件主源；正文位于付费墙后；只证明一次追踪及其采访结果，不给出总体规模，也没有 Amazon 对模型用途的逐项确认 |
| S2 | 404 Media：AI Companies Are Buying Tons of Old Books Because They're Free of AI Slop | https://www.404media.co/ai-companies-are-buying-tons-of-old-books-because-theyre-free-of-ai-slop/ | 行业调查／厂商页面记录 | 2026-08-18 | 旧书采购需求、出版物作为经过编辑的人类文本、行业对 AI 生成内容污染的担忧 | 其中 ISBNdb 的宣传属于厂商自报；该公司随后删除页面并称服务未实际落地，不能用来证明 Amazon 动机或采购链 |
| S3 | The Atlantic：Someone Is Mysteriously Snapping Up Used Books Around the World | https://www.theatlantic.com/technology/2026/08/ai-companies-buying-used-books-for-data/688167/ | 独立质疑／背景 | 2026-08-18 | 「rare」与真正稀缺、不可替代之间存在差距；此前旧书大单买家身份和供应链不透明 | 文章早于 S1；用于校正「数百万珍本被毁」的过度说法，不反驳后来追踪到 Amazon 的单个案例 |
| S4 | Bartz v. Anthropic PBC，Document 231 | https://storage.courtlistener.com/recap/gov.uscourts.cand.434709/gov.uscourts.cand.434709.231.0_1.pdf | 美国联邦法院裁定原文 | 2026-08-18 | Anthropic 购买大量纸书、拆除装订、裁页扫描、用数字副本替代纸本；法院对特定格式转换与训练用途的分析 | 仅解释 Anthropic 案件和美国特定事实；不能证明 Amazon 的主观动机，也不能写成「法律要求毁书」或普遍合法许可 |
| S5 | AP：Anthropic wins ruling on AI training in copyright lawsuit but must face trial on pirated books | https://apnews.com/article/anthropic-ai-fair-use-copyright-pirated-libraries-1e5cece51c2e4bd0bb21d94de2abb035 | 独立法律报道 | 2026-08-18 | 购买纸书扫描与盗版书库在裁定中被分开处理；训练用途与取得方式是不同问题 | 用于把法院原文翻译成普通读者可理解的背景；不是 Amazon 事件的独立核验 |
| S6 | Library of Congress：Preservation Guidelines for Digitizing Library Materials | https://www.loc.gov/preservation/care/scan.html | 官方保存与数字化指南 | 2026-08-18 | 有价值或脆弱的装订材料可使用书托和合适设备非破坏性扫描；进纸设备不适合高价值材料 | 证明「数字化不必然毁书」；不证明非破坏性方案能以相同成本和速度覆盖工业规模 |
| S7 | Library of Congress：Third-Party Digitization Agreements | https://www.loc.gov/about/doing-business-with-the-library/third-party-digitization-agreements/ | 官方数字化合作规范 | 2026-08-18 | 国会图书馆一般不允许合作方拆装订或损坏、销毁馆藏 | 说明文化保存场景的目标函数不同；不能直接套用为商业旧书扫描的法律义务 |
| S8 | Nature：AI models collapse when trained on recursively generated data | https://www.nature.com/articles/s41586-024-07566-y | 同行评审论文 | 2026-08-18 | 不加甄别地递归使用模型生成数据会丢失原始分布尾部；真实人类数据在 AI 内容增多时更有价值 | 不能改写为「任何合成数据都会令模型崩溃」，也不能单独证明 Amazon 采购旧书的原因 |
| S9 | Ars Technica：Anthropic destroyed millions of print books to build its AI models | https://arstechnica.com/ai/2025/06/anthropic-destroyed-millions-of-print-books-to-build-its-ai-models/ | 技术媒体背景 | 2026-08-18 | 破坏性扫描的吞吐量／成本逻辑、Google Books 非破坏性扫描对照 | 只作机制辅助；具体法律表述以 S4 为准 |
| S10 | TechCrunch：Amazon once an online bookseller, is destroying rare books to train AI models | https://techcrunch.com/2026/08/17/amazon-once-an-online-bookseller-is-destroying-rare-books-to-train-ai-models/ | 二次报道 | 2026-08-18 | 对 S1 和 Amazon 回应的归拢 | 当前抓取失败，未取得正文；不进入独立 claim mapping，不算第二个独立发现 |
| S11 | The Guardian：Secondhand booksellers in UK and Ireland suspect AI firms behind ‘strange’ bulk orders | https://www.theguardian.com/technology/2026/aug/15/uk-ireland-booksellers-suspect-ai-companies-bulk-orders-data-acquisition | 一手采访汇总 | 2026-08-18 | 英国与爱尔兰旧书商收到跨题材、价格不敏感的大宗订单；部分书商认为订单扰动正常交易 | 《卫报》报道的是书商对买家用途的推测，并未确认所有订单最终来自 AI 公司；正文中的数量表述需继续对照原文收窄 |

## 使用约束

- S1 是当前 Amazon 事件的唯一直接调查；所有 VGT3 流程必须保留「据 404 Media 调查／员工向该媒体表示」。
- S4—S5 只说明行业里已经存在并被法院审理的相似流程，不得把 Anthropic 的「数百万本」移植给 Amazon。
- S6—S7 只证明存在保存原书的扫描方式与规范；不得暗示它与破坏性流水线成本、速度相同。
- S8 解释真实人类材料的长期数据价值；不得把「模型崩溃」写成 Amazon 已公开承认的采购理由。
- 不使用 Reddit 转帖作为正文事实来源；搜索结果仅用于发现原始链接与争议点。
- S11 可证明「有书商自 2026 年初累计收到约 6,000 本订单」「数百本跨类别订单」「买家不寻求折扣」；当前不能证明《卫报》所访书商中有人在单笔交易里卖出数千本。
