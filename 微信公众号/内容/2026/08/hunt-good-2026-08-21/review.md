---
status: in_progress
checked_at: "2026-08-21T14:05:00+09:00"
scope: "Hunt Good L1 structure, source mapping, information density, visual quality, rights, release readiness"
---

# 编辑审查

## 2026-08-21 追加轮｜真实来源截图补充与解释密度削减

用户反馈观感与配图不够生动，要求补充真实配图，同时按指定规则只处理「解释过多」。本轮不改变任何判断、用词习惯与段落顺序，只做删除与配图增补。

**新增 8 张真实页面截图**（均为第三方公开页面的完整截图，非 AI 生成、非本项目绘制）：

- `01-stripe-openrouter-newsroom.png` 替换原联合标识图。原图只有 Logo，新图含标题、2026-08-19 日期、官方联合标识与正文首段，并可直接看到「400+ models from more than 80 providers」，与正文数字互证。
- `03b-axios-gop-memo.png`（新增）：Axios 独家报道页，含标题、日期、署名 Alex Isenstadt 与 Sarah Grillo 的国会大厦／机架插画。备忘录原件未公开，图注已写明本文依据报道转述。
- `04a-marvell-8k-sec.png`（新增）：Marvell 提交 SEC 的 Form 8-K 首页，报告日期 2026-08-18，作为权证条款的一手文件证据，置于既有机制插画之前。
- `05a-cursor-origin-changelog.png`（新增）：Cursor 官方更新日志页，含 Aug 17, 2026 与「Cursor can now host your code」，补上产品界面图缺少的时间与官方口径。
- `10-kitbitz-home.png` 替换原素材拼图预览，改用官方首页，视觉密度更高且可见 Vector／CC0／2K+／Figma 标签。
- `11-chatgpt-ads-arxiv.png` 替换原 AI 生成的 5 阶段方法插画。论文 arXiv 页摘要即含 91 个 sock puppet、3×3 因子设计、3000+ 广告、186 广告主、335 提示词、14 天等全部关键数字，比插画更接近一手证据。
- `12a-model-hypnosis-arxiv.png`（新增）：论文 arXiv 页，含标题、作者与 2026-08-17 提交日期。
- `14a-cuda-island-challenge.png`（新增）：作者技术记录页顶部，含题目原始航拍照片，置于该条第一张。作者页面开头的「genuine human work, didnt use LLM generation」已并入图注，正文相应的独立说明句删除。

被替换的 3 张（`01-stripe-openrouter-official.png`、`10-kitbitz-official.webp`、`11-chatgpt-ads-illustrated-v3.png`）已在台账改为 `used_in_draft: false` / `use: "unused"`，文件保留。正文配图从 19 张增至 24 张。

**未取得的截图**：OpenAI 的 ChatGPT for Teens 与 Private Safety Processing 两个公告页，直连被反爬拦截，经 web.archive.org 存档截图亦反复失败，故 06 与 07 两处维持原有配图（官方主题图与 AI 生成插画）。Gemini 定价页截图只显示 Free／Paid／Enterprise 概览，看不到 3.7 Flash 的具体价格与 2027 年调价，无证据价值，未采用。

**解释密度削减**（只删除，不把语义并入其他句子）：

- Stripe：删「同时站在两条流水线上」的总结句，前一段已说明收入与推理成本两侧。
- Amazon：删「听起来像是外卖骑手换成飞机，飞起来却只是第一步」的反转起句；删「后面的时间状语决定了这条新闻的口径」的元话语，保留其后的事实边界本身。
- 数据中心：删「AI 的算力竞赛于是多了一项地方政治成本／选票会替它打分」整段段尾结论。
- Marvell：删「更像一条很长的利益捆绑带」的重复解释；删「数字很大，但两条边界必须一起记住」的框架句，直接保留两条边界。
- Cursor：删「不再满足于坐在开发流程的副驾驶位」的修辞收尾。
- ChatGPT for Teens：删「以后同一个 AI 产品，可能先判断你是谁……」的推论句，保留前一句事实。
- OpenAI ZDR：删「想同时保住两件彼此冲突的东西」的复述句，该意思在本节首段已给出。
- ChatGPT Ads：删「分发系统仍可能对不同人形成不同待遇／以后审计还要记录展示了什么」的推论与建议。
- 多 Agent：删「共享文件不是万能药」的归纳、「不会自动长出项目管理能力」的金句、「以后评多 Agent 还要记录……」的建议，三处均在其前一句已有事实陈述。
- CUDA：删「非常工程师的浪漫」的评价，保留方法本身的形象描述；删末尾「顺便一提，作者特意写了……」，该信息移入新增截图的图注。

**状态回退**：正文已变更，按内容工作流将 `status` 由 `ready` 降为 `editorial_review`，`copyedit_checked` 与 `rights_checked` 置 false，清空 `copyedit_body_sha256`。新增截图的权利状态均按既有口径登记为 `user_confirmed_editorial_commentary`，进入 `ready` 前仍需重跑逐句终校与最终人工权利复核。内容包校验通过：`markdown_images=24`，6 条 warning 均为既有 AI 插画的 profile_registry 定位提示，非本轮引入。

---

# 编辑审查（2026-08-21 首轮）

## 栏目与读者路径

- 栏目合同：7 条 News、3 个 Tools、3 个 Insights、1 个 Fun；彩蛋单独计算。
- 首屏主线：模型路由、代码仓库、芯片订单与数据中心账单共同把 AI 竞争推向基础设施层。
- 标题边界：Stripe 仍是「签署收购协议」，没有写成交割完成；无人机扩张是 2026 年底计划；Marvell 权证不是 Google 已投资 121.8 亿美元。
- Tools 均保留适用对象、入口、实测状态或厂商口径与限制；Insights 均保留实验设计、结果、反例或外推边界。

## 信息密度复核

- ChatGPT Ads 不再只写「低收入帐号更容易收到广告」：正文区分首次曝光与曝光后频率，补充 14 天等待、每 1000 美元的赔率比、95% 置信区间、显著性边界和小样本限制。
- Agent Coordination 不再只写「共享文件省 42%」：补充 36%—49% 范围、缓存上下文变化、文件优先任务的 8／16 Agent 反例、协调者无稳定改善与隐藏评分材料风险。
- Model Hypnosis 保留二选一任务、大量查询优化和现实开放对话尚未回答的边界。
- 以上新增内容均回映 `sources.md` 和论文一手来源；厂商自报、论文结果与作者判断分开。

## AI 痕迹诊断

- 状态：pass
- 正文没有研究路径、证据等级、缺陷 ID、提示词、内部文件名或审核转场等后台话术。
- 固定周报结构中的「适合／坑／入口」属于栏目合同，不被误判为机械三段式；各条仍由具体事实、数字、条件和限制推进。
- 揭晓式句法和空泛总结已压低；保留的否定句都承担事实排除，例如收购未交割、权证非当前投资、相关主题图非产品界面。
- 新增统计量与论文反例均紧邻对应对象，没有把「更丰富」执行成参数堆砌或方法审计泄漏。

## 视觉复核

- 用户否决的首版视觉不予追认：5 张稀疏竖卡、旧封面与旧彩蛋均退出正文和发布清单。
- 14 个条目最终均有配图：11 条以官方／原作者／论文来源图为主，3 条使用原创信息图；正文共 19 张图。
- 3 张信息图只解释 Google–Marvell 权证、OpenAI ZDR、ChatGPT Ads 方法；用户提供的成功案例与受控 Prompt 已绑定到 Image2 计划和 receipt。插画对象、动作、编号与箭头承担主流程，文字仅作标注，不再使用 v2 纯文字编辑卡。
- 原尺寸检查：Google 图的 58,970,907 股、206.58 美元、`$120B` 与 121.8 亿美元，ChatGPT Ads 图的 91 个帐号、14 天、头 7 天 0 个帐号和 ×0.98 均逐项核对；标题、数字、箭头、边界、图注、Logo 均无重叠、越界、裁切残字或变形。
- 手机检查：已查看 `research/mobile-visual-check-v3.png`；3 张插画图均按 390 px 实际正文宽度渲染，主判断、编号路线、具体对象、核心数字和边界可辨。
- 整期检查：已查看 `research/contact-sheet-v3.png`；照片、产品截图、论文图和信息图交替出现，没有连续复用同一骨架，来源图仍占多数。
- 所有发布资产均已登记来源、权利人、修改、允许平台、许可状态与哈希；第三方编辑评论不宣称取得通用许可，CC BY 4.0 论文图保留署名。

## 发布门禁

- 正文无本地绝对路径、密钥、Cookie、内部审核话术或未解释的占位符。
- `publish.yml` 继续指向 v2 横版封面；未执行公众号草稿覆盖、群发或发布。
- 栏目计数、6 个生图任务 preflight、YAML 解析、图片路径、资产台账和内容包校验均通过。
- 精确正文终校哈希：`bf764522fccc6935974a0fa76aff3e422e51f4d83ec7fcebe440bca56e7a5b4c`。
