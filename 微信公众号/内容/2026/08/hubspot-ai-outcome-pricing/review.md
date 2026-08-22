# 审校记录

审校日期：2026-08-04

终检真源：`.agents/skills/self-media-ops/references/wechat-editorial-gates.md`

## 0. 独立冷读

冷读只看标题和公开正文，完成于 2026-08-04 02:08（UTC+09:00）。

1. 发生了什么：HubSpot 把 Prospecting Agent 称为「按结果收费」，但三个当前官方页面把 credits 触发分别写在加入 prospecting、推荐外联和草拟外联附近；这些动作都早于客户回复。
2. 首屏压力：客户没回复，邮件甚至可能还没发送，credits 却已能产生；官方页面还没有对齐扣费按钮。
3. 作者主判断：所谓 outcome 是厂商选定的工作流完成点，不自动等于用户要的业务结果；价值取决于联系人准确率、验收、返工和数据控制。
4. 可信证据：产品页、产品目录、7 月 3 日设置指南的当前口径；`Ready for review` 与 `Finished` 状态定义；Contact Discovery 原公告、7 月 5 日撤回说明和当前 enrichment／训练设置。
5. 最强限制：回复、会议和成交受销售、产品、报价与市场影响，厂商把可执行外联设为计费单位有现实合理性。
6. 普通读者为什么要看：以后面对任何「按结果收费」Agent，可以先定位扣费动作，再判断离自己的目标还有多远。
7. 章节变化：扣费线错位 → 1 美元买到的工作包 → 工作包依赖的联系人数据 → 合理边界与验收问题。
8. 结尾留下的具体想法：先看 credits 在哪一步扣掉，再数离目标还有几步。

与 `brief.md`、`research/judgment-workshop.md` 对照：一致。开头、中段和结尾朗读声线一致，均为克制的 APPSO 分析口吻；口语只落在「躺在待审核列表」「合同没影」「精致的废票」等具体动作或后果上。

## 1. 读者与文章承诺

- [x] 文章只有一个目标读者、一个问题和一个主承诺；标题、开头、证据与结尾回答同一件事
- [x] 首屏有已核动作或变化、未解决压力和继续阅读理由；写前共创记录已锁定并可追溯

## 2. 论证与声音

- [x] 已先独立冷读，再打开故事合同；成稿已逐节映射 `CORE-CHAIN-001` 四格叙事链
- [x] 胜出稿已完成一次 `PROJECT-WECHAT-RHYTHM-001` + `PROJECT-WECHAT-PRAGMATIC-001` 完整诊断；修复后只复核修复点
- [x] 候选稿到成稿的 diff 已按 `PROJECT-WECHAT-CONCRETE-001` 检查，没有「删具体、留抽象」
- [x] 术语首次出现可理解，普通人处境贯穿证据与结尾，结尾没有另起第二套主张

### 叙事链写后对照

| 拍 | 上一问 | 本节回答 | 留下的问题 | 下一节为何必须回答 | 结论 |
|---|---|---|---|---|---|
| 1 | 「按结果」到底在哪一步？ | 三份官方口径虽错位，但都早于回复；状态栏也把待审、发送中和完成分开 | 这笔 credits 实际买了多少工作？ | 要拆开工作包，才能判断这条收费线是否有价值 | pass |
| 2 | 1 美元买了什么？ | 找人、研究、写信和审核组成一段销售准备；错人会让整包失效 | Agent 凭什么找对人？ | 联系人质量把文章必然带到数据来源 | pass |
| 3 | 联系人数据从哪来、谁控制？ | 原方案与撤回时间线、当前 enrichment 有限字段和独立训练开关 | 这些控制是否足以证明产品值得买？ | 必须回到验收、返工和最强对手 | pass |
| 4 | 怎样公平评价？ | 承认全链路结果不可控，再列出扣费、验收、返工、数据四项检查 | 无新增主张 | 结尾把检查动作压回标题中的收费线 | pass |

- 成稿偏离锁定链的位置与理由：第 1 拍新增「三份当前官方页面扣费口径不一致」与状态栏证据；这是交付前重开来源后发现的精度修正，强化原链而未改换主线。
- 结论：pass

### AI-pattern diagnostic

- Mode：detect
- Scope：title / headings / body / links / final sentence
- Applied：RHYTHM / PRAGMATIC / workflow leakage / speculative gaps
- Ignored as hard gates：English word lists / stylometric thresholds / punctuation quotas / detector score
- Status：pass

| ID | Severity | 原句与位置 | 指纹类别 | 删除测试结果 | 信息任务与指向 | 处理 | Status |
|---|---|---|---|---|---|---|---|
| HUMAN-RHY-001 | minor | 「麻烦也藏在这里。」；原候选第 2 节 | RHY-IMPORTANCE | 删除只损失悬念腔 | 无具体新信息 | 改为收件人找错会让整段准备失效 | fixed |
| HUMAN-RHY-002 | minor | 「这条线并非天然不合理。」；原候选第 4 节 | RHY-DISCLAIMER / RHY-UPLIFT | 删除不损失让步，上一段已完整承接对手 | 让步重复 | 删除独立短段 | fixed |
| HUMAN-RHY-003 | minor | 「换句话说，100 credits 买的是……」；原候选第 2 节 | 解释标签 / PROJECT-PRAGMATIC | 删除标签不损失释义 | 100 credits 的工作包 | 直接写明产品目录与产品页口径 | fixed |
| HUMAN-RHY-004 | minor | 「这里需要把几件事拆开。」；原候选数据节 | RHY-IMPORTANCE | 删除只损失文章导航 | 无 | 直接进入当前 enrichment 规则 | fixed |
| HUMAN-AI-001 | blocker | 文末 HTML 注释中的「作者推断／保留未知项／自查」 | workflow leakage | 删除不损失读者正文；来源已转为正文链接和 `sources.md` | 内部审校记录 | 整段移出公开正文 | fixed |
| HUMAN-AI-002 | blocker | 「截至本轮核查」「已核入口」；原候选数据节 | workflow leakage | 改写后时点与未知边界仍完整 | Contact Discovery 截止时点 | 改为读者可见的时间与具体官方入口 | fixed |

高显著句复核：

- 「HubSpot 所说的 outcome，是产品定义的工作节点，不是客户定义的生意结果。」承担全文唯一的核心术语区分，指向三份计费口径与状态栏；删除会丢失主判断，保留。
- 「精致的废票」只指向找错联系人后整段销售准备失效，不承担转场，也未形成隐喻链；删除会削弱具体后果，保留。
- 文末「先看 credits 在哪个动作上扣掉」回收标题承诺和四项验收维度，没有另起方法论，保留。

### APPSO 表达库一次性扫描

- Adapter：`PROJECT-APPSO-EXPR-001`，只检查 `WX-EXPR-001—020`。
- P0 / default_avoid：修复后无命中。
- P1 / semantic_review：
  - `WX-EXPR-015`：保留全文唯一的核心区分句「是产品定义的工作节点，不是客户定义的生意结果」；它是精度关键的术语边界，不把连续变量硬切为二选一。
  - `WX-EXPR-016`：保留「第一—第四」四问；四项是同尺度产品验收维度，且由 brief 明确承诺，不是报告式拆段。
  - `WX-EXPR-020`：复核「精致的废票」；隐喻紧贴错误联系人造成的工作包失效，未串成转场链，保留。
- 作者身份判断：未使用；扫描只服务项目表达审校。

### 具体性守恒 diff

| 被删具体细节 | 类型 | 删除理由 | 保留／新增的具体信息 | 净效果 | 处理 |
|---|---|---|---|---|---|
| 「监测购买信号」作为所有版本通用能力 | 具体产品动作 | 当前指南区分普通版与 buying-signals/contact-sourcing beta，避免把 beta 能力写成所有版本默认 | 保留销售漏斗中的购买信号，并新增三个当前扣费口径 | 精度上升 | pass |
| 文末 8 条裸来源与内部未知项 | 来源／内部记录 | 公开正文不应暴露审校脚手架 | 8 个关键来源改为就近可点击链接；完整边界保留在 `sources.md` | 读者路径更清楚 | pass |
| 「这条线并非天然不合理」等抽象转场 | 抽象总结 | 与相邻段重复，不承担新信息 | 保留完整最强对手，并新增 `Ready for review` / `Finished` 的可见状态 | 具体信息净增加 | pass |

## 3. 事实与来源

- [x] 已按 `as_of` 重开时效来源，核对名称、日期、价格、产品名与比较口径
- [x] 事实、厂商自报、作者判断和未知项已分开；未用厂商效果数字充当独立验证

关键精度决定：三个官方页面的扣费动作不完全一致，正文只写它们共同早于回复，不自行指定所有版本的唯一触发按钮。Contact Discovery 只写原公告、条款撤回和截至时间，不写已上线或已取消。

## 4. 视觉与权利

- [x] 正文当前未使用图片，`asset-manifest.yml` 如实为空
- [x] 候选图与原图仅放在 `research/`，未冒充发布资产；图源、像素、用途和待确认权利状态已记录
- [x] 正文不依赖图片才能理解核心逻辑

视觉候选：9 组官方页面方案；其中 6 张官方原图已下载，P0 为状态栏原图。营销 Logo 图因信息量低降为 P3。

## 5. 精确正文终校

- [x] 结构与表达修复完成后只运行一次 APPSO adapter 表达库扫描；命中均已修复或记录语义放行
- [x] `copyedit.md` 已完成逐句检查，正文 SHA-256 与 draft frontmatter 一致

## 6. 状态与交付

- [x] `fact_checked: true`、`rights_checked: false`、`copyedit_checked: true` 与当前实际进度一致；状态停在 `editorial_review`
- [x] 无开放 blocker 或 major；未执行发布、飞书同步、浏览器覆盖或其他外部写入

### 任务特定标准

- 不写新闻通稿：pass；不是「宣布—功能罗列—行业意义」顺序，而是收费线 → 工作包 → 数据 → 验收的依赖链。
- 有网感和活人感：pass；口语锚点有具体对象和后果，无虚构第一人称、硬梗或均匀撒俚语。
- 高质量网上配图不少于 5 组：pass；已记录 9 组方案并下载 6 张官方原图。
- 只使用 public / public-derived 事实：pass；未读取或转用 APPSO internal / restricted 原件。

### 待处理

- `COPY | — | copy editor | 完整逐句终校已通过 | 正文哈希与 draft / copyedit 一致 | closed`
- `VISUAL-RIGHTS | release | editor | 候选图尚未选用且未确认转载／平台许可 | 选图后登记 asset-manifest；本轮不进入 ready | expected`
