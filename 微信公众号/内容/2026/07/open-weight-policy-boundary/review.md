# Editorial review

## AI-pattern diagnostic

- Skill: avoid-ai-writing 3.15.0
- Mode: detect
- Context: blog
- Scope: title / headings / body / captions / final note
- Applied: workflow leakage；empty authority；template structure；rhythm；manufactured personality；speculative gaps
- Ignored as hard gates: English word lists；stylometric thresholds；punctuation quotas；detector score
- Status: pass

| ID | Severity | Evidence | Reader harm | Repair owner | Pass condition | Status |
|---|---|---|---|---|---|---|
| HUMAN-AI-001 | major | 旧稿从「7 月 24 日，一封只有 3 页的公开信」开始，随后依次播报名单、定义和文件 | 开头像新闻通稿，OpenAI 先缺席后出现的反常点没有成为贯穿全文的问题 | feature writer | 开头先呈现 Sam Altman 支持而 OpenAI 缺席，结尾回到团队有没有替代模型；中间证据都服务这条线 | resolved |
| HUMAN-AI-002 | major | 政策段按 NSTM-4、H.R. 8283、CFAA 逐份解释，并连续出现授权、模型提取攻击、受关注实体等术语 | 读者能看到文件摘要，却难以复述平台条款怎样进入美国公共政策，以及这与中国企业有什么关系 | feature writer | 隐去小标题后，仍能按「模型公司后台 → 白宫文件 → 法案提案 → 名单与制裁风险」复述推进关系 | resolved |
| HUMAN-AI-003 | minor | 用户素材稿中的「先别急着把它叫开源」「有趣的是」「真正希望推动」「抢这条线」均非来源原话；删除后不损失事实，仅承担通用转场 | 多个可迁移到其他 AI 文章的套话会制造故事感，却没有增加信息 | feature writer | 删除通用框架，分别改写为机房部署、OpenAI 回到故事主线和公司条款进入公共权力的具体动作 | resolved |
| HUMAN-AI-004 | major | 政策段虽然已有「后台 → 白宫 → 法案」顺序，正文仍由 NSTM-4、H.R. 8283、CFAA 等代号和抽象判断领头 | 普通读者需要先记文件名，再反推封号、合同与政府限制之间发生了什么 | feature writer | 先写平台动作和风险升级，再各出现一次必要代号；冷读者能复述「封号与合同 → 国家安全备忘录 → 法案提案 → 名单和制裁风险」 | resolved |
| HUMAN-AI-005 | major | 旧结构同时以 OpenAI 名单变化、开放权重定义、蒸馏边界、美国政策和产业利益为中心；黄仁勋与公开信在开头后退场 | 标题承诺一件事，正文依次解释五件事，读者只能记住材料，无法复述一条主线 | feature writer | 全文围绕「一封开放权重公开信为什么要讨论蒸馏」推进；OpenAI、政策和公司利益均降为解释或后果 | resolved |
| HUMAN-AI-006 | major | 「这点差别会直接落到业务里」「冲突也发生在这里」「问题因此落到了」「绕了一圈，故事又回到 OpenAI」等通用转场连续承担结构 | 删除这些短语几乎不损失事实，段落依然像按模板拼接，形成明显的机器化节奏 | feature writer | 由公开信、蒸馏案例、Anthropic 调查、白宫文件和 OpenAI 产品位置直接带出下一段；不再用可迁移套话模拟推进 | resolved |
| HUMAN-AI-007 | major | 上一版虽然统一为「公开信为什么讨论蒸馏」，仍按「开放权重定义 → 蒸馏定义 → 政策文件 → 公司利益 → 应用」顺序解释 | 逻辑正确但像课程讲义；没有冲突升级和时间变化，黄仁勋的公开信仍只是开头提出的问题 | feature writer | 以 7 月公开信冷开场，回到 2 月 Anthropic 调查与 4 月白宫文件，再返回 7 月解释签署方和 OpenAI；结尾落到一支团队的模型选择 | resolved |
| HUMAN-AI-008 | major | 时间线版本继续扩展为政策文件、公司名单、企业影响、国内风险与普通用户影响；NVIDIA 和 OpenAI 的利益只占后半段 | 事件顺序替代了论证顺序，读者能复述月份，却不能复述文章要证明的商业冲突 | feature writer | 政策只承担压力背景；正文按「NVIDIA 利益 → OpenAI 利益 → 三项权利 → 学习权」推进 | resolved |
| HUMAN-AI-009 | minor | 新稿初版集中出现「不是 A，而是 B」「不只是 A，而是 B」式转折，并在段尾和结尾重复收束三项权利 | 主线已经收紧，句式却再次显得过度工整，削弱作者口吻 | feature writer | 只保留最终结论中承担真实排除的转折，其余改为直接陈述 | resolved |
| HUMAN-AI-010 | major | 上一版虽已按 NVIDIA、OpenAI 与三项权利收束，仍完整展开政策代号、Meta 与 DeepSeek 案例、合同例外和蒸馏收费分类 | 读者不断停下来理解术语和分类，文章像整理良好的讲义，人物行动无法连续推动故事 | feature writer | 政策只用一段交代压力；模型案例只留一个；OpenAI 的产品、合同与旧蒸馏工具合并为同一利益证明；可见正文少于 3000 字符 | resolved |
| HUMAN-AI-011 | minor | 「第一个问题／第二个问题／第三个问题」与多个段尾小结形成整齐的枚举节奏 | 三项权利被重复讲解，结尾到来前已经失去推进感 | feature writer | 用一家企业付费取得回答后训练内部模型的场景自然带出「谁能学、学到何种程度、向谁付费」；全文保留短句、长段和停顿变化 | resolved |
| HUMAN-AI-012 | major | 用户提供的趣味素材同时堆叠「打起来」、OpenAI 名字梗、员工互怼、互动量、公司阵营和 Denny’s 彩蛋 | 若整体移植，文章会从商业利益分析重新滑回事件与段子盘点，开头和结尾也会像两种声音 | feature writer | 只保留能提出主问题的「Anthropic 显眼缺席」「CUDA 反讽」和一次 OpenAI 名字梗；其余趣味材料不进入正文 | resolved |
| HUMAN-AI-013 | minor | 「Everyone except Anthropic」是社交平台上的情绪化概括，按字面写成「全行业只剩 Anthropic 没签」会扩大事实范围 | 为了戏剧性牺牲名单口径，也会把员工个人表态误读成公司回应 | feature writer | 正文写成「舆论把 Anthropic 推成最后一个没签的」，并紧接「员工个人发言，不代表 Anthropic」；来源台账注明该帖子只代表传播框架 | resolved |
| HUMAN-AI-014 | minor | 开场只把 Julian Schrittwieser 写成「一名技术人员」，随后用中文转述其 CUDA 反讽，没有人物分量或原帖视觉证据 | 陌生人物承担关键转折却缺少最低身份说明，读者既不知道为什么要听他，也无法查看发言语气和引用上下文 | feature writer | 用一段写清其 Anthropic 现职、AlphaGo Zero 经历和 MuZero 第一作者身份；紧接完整 X 嵌入页截图，并在图注明确个人发言不代表公司 | resolved |
| HUMAN-AI-015 | major | 「开放权重」与「蒸馏」连续定义后，直接写「美国正在给这条学习通道画线」 | 把不同维度的技术与政策问题压成一条线，既形成术语堆叠，也误导读者理解美国正在限制的对象 | feature writer | 明确开放权重讲模型能否下载部署，蒸馏讲输出能否训练另一模型；政策边界写成蒸馏内部的授权、访问方式与后续用途之争 | resolved |
| HUMAN-AI-016 | major | 调整前开场约 919 个可见字符并连续放置两张纵向 X 截图，NVIDIA 与 OpenAI 两节分别只有约 402 和 554 字 | 标题承诺解释两家公司的利益，正文却把多数注意力耗在事件与政策铺垫，形成明显头重脚轻 | feature writer | 开场只保留事件、缺席者与主问题；政策和 Julian 反讽进入 NVIDIA，企业训练场景和授权收费进入 OpenAI；结尾压缩为差异与学习权 | resolved |

### WECHAT-HUMAN-002 语义记录

- 原短语：先别急着把它叫「开源」；7 月 24 日的公开信，正是在抢这条线。
- Literal / sourced：均不是来源原话，也不是必须保留的技术名词。
- Deletion test：删除后不损失事实、证据或作者立场，只失去通用转场。
- Concrete repair：标题改为「模型能不能搬回自己的机房」；政策段直接写平台条款怎样进入政府文件、名单和制裁程序。

- 本轮追加短语：「这点差别会直接落到业务里」「冲突也发生在这里」「问题因此落到了」「绕了一圈，故事又回到 OpenAI」。
- Literal / sourced：均不是来源原话或必要术语。
- Deletion test：删除后不损失事实，只会暴露旧稿各节之间没有单一问题承接。
- Concrete repair：改用「公开信为何讨论蒸馏」作为全文问题，后续段落分别回答技术关联、争议行为、政策后果和企业利益。

- 本轮结构测试：上一版各知识板块可以单独搬动，说明材料仍按主题分类，不按事件推进。
- Concrete repair：改用「2 月企业定性 → 4 月政策升级 → 7 月联合表态」的真实时间顺序；定义只在事件需要时出现，不再单独承担章节。

- 2026-07-27 冷读：时间线仍然能独立扩展，说明它没有把 NVIDIA、OpenAI 和「合法蒸馏」锁进同一条论证链。
- Concrete repair：政策线压为开场背景；隐藏小标题后，正文仍可复述「反常动作 → NVIDIA 算力利益 → OpenAI 双重位置 → 三项权利 → 学习权」。同时删除重复的「不是 A，而是 B」模板转折。

- 2026-07-27 再次冷读：逻辑链已经成立，但政策编号、模型型号、合同例外和三项权利仍各自占据解释段，造成术语重新堆回主线。
- Concrete repair：把政策压成「公司定性 → 白宫介入 → 争议从偷取回答走向输出能否训练」；正文只保留 3 个功能小标题、4 张图片和一个模型案例；用企业训练内部模型的场景完成三项权利，去格式可见正文约 2200 字符。

- 2026-07-27 趣味素材检测：完整照搬「打起来／太勇了／真 Open·AI／Denny’s 卖 Chips」会制造连续情绪，却没有让 NVIDIA、OpenAI 和学习权的关系更清楚。
- Literal / sourced：CUDA 反讽与「Anthropic 是显眼缺席者」均有公开 X 帖；后者只是社交概括，不能作为全行业事实。Denny’s 帖存在，但只承担谐音彩蛋。
- Deletion test：删除 CUDA 反讽会损失「黄仁勋是否只在别人开放时获利」这一尖锐问题；删除 Denny’s、互动量和重复 Windows 反讽不损失核心判断。
- Concrete repair：开场加入动态名单、Anthropic 缺席和 Julian 个人反讽；OpenAI 段只保留一次名字梗；正文继续以商业利益和学习权收束。

- 2026-07-27 人物证据检测：Julian 的话承担开场转折，只有「技术人员」和中文转述不足以解释引用价值。
- Concrete repair：补一段最短身份卡；原帖截图保留姓名、账号、原文和引用的黄仁勋帖子；图注继续限定为员工个人发言。

- 2026-07-27 政策边界检测：「这条学习通道」把开放权重、蒸馏和监管写成同一条递进关系，删除比喻后才暴露真正区分标准缺席。
- Concrete repair：把现有政策落到「怎样取得回答」，把拟议法案新增争议落到「取得后能否训练另一个模型」，不再把边界写在开放权重与蒸馏之间。

- 2026-07-27 章节比例检测：开场的政策史与两张纵向截图共同形成视觉和文本前重，两个标题章节不能兑现标题承诺。
- Concrete repair：开场缩至约 386 字；NVIDIA 与 OpenAI 两节扩至约 950 和 937 字；结尾缩至约 362 字，Julian 原帖图随相关分析进入第一节。

未发现仍开放的 blocker 或 major 缺陷。稿件保持 draft，本记录不替代正式终校与 exact-body copyedit。
