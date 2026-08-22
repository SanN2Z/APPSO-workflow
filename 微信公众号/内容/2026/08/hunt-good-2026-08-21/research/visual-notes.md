# Hunt Good 2026-08-21 配图决策与视觉验收

## 用户反馈与失效复盘

- 用户第一次反馈：不能把「每条有图」理解成「每条都自制信息图」；只有关键数字、机制与关系值得做信息图，其余条目应搜索线上高质量相关配图。
- 用户第二次反馈：「信息图做的太丑，内容也不够丰富。视觉检验不过关。」
- 用户第三次反馈：用一张成功的火箭信息图指出「里面有图有文字」，而 v2 仍然是「纯文字」；随后追问「信息图有 prompt，你看了吗」。
- 首版问题不是缺 Logo 或缺数量，而是 5 张竖版信息图共用「大标题 + 白卡片 + 少量图标」骨架：留白过多、关系层次少、像批量模板；研究观点还用简化图标替代了论文原始证据。
- 首轮只看了 contact sheet 和规范字段，错误地把「没有缺图、Logo 可见、文字未溢出」当成视觉通过。该结论作废。
- v2 虽然补了文字与数据层，却仍把主逻辑放在白卡片和段落里。更直接的流程错误是：已经读过桌面 `信息图.md`，但没有把受控 Prompt 与成功案例绑定进实际 Image2 任务，只凭摘要规则做了确定性排版；因此「读过」没有转化为工具输入，v2 结论同样作废。

## 最终策略

- 14 个正文条目全部有配图：11 条以官方／原作者／论文来源图为主，3 条使用原创信息图。
- Cursor、ChatGPT Ads 与 Agent Coordination 各需要第二张来源图补足产品集成或论文证据，正文实际为 19 张图。
- 自制信息图仅保留 Google–Marvell 权证、OpenAI ZDR、ChatGPT Ads 方法 3 个确实需要解释机制的条目。
- Model Hypnosis 与 Agent Coordination 改用论文 Figure 1 / Figure 8；观点段优先让读者看见原始证据，不再画幼态替身。
- 两张封面与彩蛋继续使用横向编辑卡；3 张关键信息图改成插画叙事：芯片订单／计数器／权证钥匙、客户机房／加密保险库／自动扫描器、模拟帐号／代理地点／提问表／广告卡分别承担主逻辑，文字只做编号标注。

## 设计真源与品牌资产

- 信息图规范：`APPSO-数字资产/01-栏目与品牌/品牌视觉/原始资料/Markdown 示意图设计系统规范.md`
- 规范 SHA-256：`c8c191665a99da9af14f8ba84b0f7ef769cbadefe347f5d197635264b024c043`
- 本期插画信息图 Prompt：`APPSO-数字资产/01-栏目与品牌/品牌视觉/生图-Prompt/Hunt Good 插画信息图.md`
- Prompt 档案：`appsso-hunt-good-illustrated-infographic-v1`；SHA-256：`f5a11af4fcf522774cd53f5317e5b38f8a0818b657c9a641806edbbd2110d2d3`
- 绑定参考图：`research/source-assets/hunt-good-infographic-style-reference.png`；它与当前任务用户提供的成功案例 SHA-256 一致。
- 生成计划：`research/image-generation-plan.json`；每个任务均保留 Prompt 档案、参考图输入顺序、事实卡输入、约束与 preflight receipt。
- APPSO 标识：`APPSO-数字资产/01-栏目与品牌/品牌视觉/原始资料/APPSO Logo 红底白字.png`
- 标识 SHA-256：`8160db79fc8cafdd864312b32bb6b01ee4d720187bc4acc6a875e273eecd04ff`
- 使用方式：按原比例作为克制锁定块；不抠底、不改色、不拉伸；图内不重复「爱范儿制图」。
- 字体：未发现已授权的 OPPO Sans 文件。本期使用 Microsoft YaHei 回退，不从权利不明站点下载字体。
- 插画生成：Codex 内置 `image_gen`，模型 `gpt-image-2`；Google 图经过两轮单点事实修正，ChatGPT Ads 图经过一轮样本与图表语义修正。
- 确定性收尾：`research/finalize_illustrated_infographics.py` 只做 1080 × 1440 适配、页脚分隔线和登记版 APPSO Logo 合成，不改语义内容。

## 逐条决策

| 条目 | 最终视觉 | 决策 | 理由与口径 |
|---|---|---|---|
| News 01 Stripe / OpenRouter | `assets/01-stripe-openrouter-official.png` | 来源图 | 品牌关系本身就是新闻；官方联合标识比再画路由卡准确 |
| News 02 Amazon Prime Air | `assets/02-amazon-prime-air-official.jpg` | 来源图 | 真实机型提供现场感；图注明确不证明近 500 个城镇已开通 |
| News 03 数据中心政治 | `assets/03-pa-data-center-commonwealth.jpg` | 来源图 | 人物与政策现场优先真实照片；明确为 5 月 GRID 标准现场 |
| News 04 Google / Marvell | `assets/04-google-marvell-illustrated-v4.png` | 插画信息图 | 用订单、定制芯片、累计采购计数器、钥匙与权证证书区分 5 亿美元解锁、240 批、1200 亿美元条件采购、58,970,907 股和 121.8 亿美元潜在行权值；终检另修正 `$1200B` → `$120B` |
| News 05 Cursor Origin | `assets/05-cursor-origin-official-v2.png`、`assets/05b-cursor-origin-apps-official.png` | 来源图 × 2 | 官方仓库设置与 Apps 界面分别证明托管边界和 Vercel／Depot／Buildkite 集成 |
| News 06 ChatGPT for Teens | `assets/06-chatgpt-teens-official.png` | 来源图 | 官方青少年安全主题视觉；图注明确不是产品界面 |
| News 07 OpenAI ZDR | `assets/07-openai-zdr-illustrated-v3.png` | 插画信息图 | 用客户机房、加密保险库、客户密钥、自动扫描器与风险信号解释两种存储和有限回传；底部列出尚未公开的问题 |
| Tool 01 Gemini 3.7 Flash | `assets/08-gemini-37-flash-official.png` | 来源图 | 产品条目优先官方模型卡；价格由正文与定价页承担 |
| Tool 02 OpenMotion | `assets/09-openmotion-official.png` | 来源图 | 真实画布、时间线与对话区比抽象流程更能判断产品形态 |
| Tool 03 Kitbitz | `assets/10-kitbitz-official.webp` | 来源图 | 工具价值就在真实画风和素材密度 |
| Insight 01 ChatGPT Ads | `assets/11-chatgpt-ads-illustrated-v3.png`、`assets/11b-chatgpt-ads-income-paper.png` | 插画信息图 + 论文图 | 插画用人设、地点代理、统一提问、广告抓取和分开比较解释 91 帐号与 5 阶段；修正「9 类人设／91 帐号」分配矛盾，并明确曝光后频率与收入／族裔未见显著系统关系；Figure 6 继续承担首次曝光证据 |
| Insight 02 Model Hypnosis | `assets/12-model-hypnosis-paper-fig1.png` | 论文图 | 原始同义改写与 94% NO → 99.93% YES 是最有说服力的证据；不再用卡片代替 |
| Insight 03 Agent Coordination | `assets/13-agent-coordination-paper-fig1.png`、`assets/13b-agent-coordination-paper-fig8.png` | 论文图 × 2 | Figure 1 解释消息／读写网络，Figure 8 展示文件策略改变通信结构；正文补上何时节省、何时反增 |
| Fun 01 CUDA 小岛 | `assets/14-cuda-island-author.jpg` | 来源图 | 使用作者生成的 948 个候选分布图，不使用权利不清的挑战照片 |

## 封面与彩蛋

| 文件 | 类型 | 说明 |
|---|---|---|
| `assets/00-cover-wechat-v2.png` | 原创横版封面 | 1920 × 818；五层基础设施栈；用于公众号封面 |
| `assets/00-cover-v2.png` | 原创正文封面 | 1200 × 720；同一视觉母题，手机宽度仍可读 |
| `assets/15-egg-v2.png` | 原创彩蛋 | 1200 × 675；四段基础设施路径，不冒充新闻现场 |

首版 `00-cover.png`、`00-cover-wechat.png`、`04-google-marvell.png`、`07-openai-zdr.png`、`11-chatgpt-ads.png`、`12-model-hypnosis.png`、`13-agent-coordination.png`、`15-egg.png` 均已判废，不进入正文、封面或权利清单。

## 权利与视觉验收

- 最终 20 个发布资产（19 张正文图 + 1 张公众号封面）均在 `asset-manifest.yml` 登记来源、权利人、修改、平台、许可状态与 SHA-256。
- 第三方图的 `user_confirmed_editorial_commentary` 不等于权利人授权；Agent Coordination 论文图按 CC BY 4.0 使用，其余论文节选保留署名与未确认状态。
- 原尺寸检查：封面、3 张最终插画信息图、3 组论文证据与彩蛋逐张检查；Google 图的股数、价格、`$120B` 和 121.8 亿美元，ChatGPT Ads 图的 91 帐号、14 天、0 个帐号与 ×0.98 均按原尺寸复核；无裁切残字、重叠、越界或 Logo 变形。
- 手机宽度检查：`research/mobile-visual-check-v3.png`。3 张插画信息图均以真实 390 px 宽度并排渲染；标题、编号路线、主要对象、核心数字和边界可辨。
- 整期节奏检查：`research/contact-sheet-v3.png`。19 张正文图中，现场照、产品截图、论文图与 3 张插画信息图交替出现，来源图仍占多数，没有连续复用同一模板。
- 内容密度检查：每张信息图至少包含「主判断 + 关系／流程 + 数字或条件 + 边界」四层中的三层；不再用只有结论和装饰图标的卡片放行。
- Prompt／参考绑定检查：3 个初始插画任务和 3 个事实修复任务均通过 preflight；最终 receipt 可回溯当前任务指定 Prompt、用户成功案例、事实卡输入与输出路径。
- 本轮视觉验收：pass。该 pass 只对应正文绑定的 v3／v4 插画资产，不追认首版与 v2 文字卡。
