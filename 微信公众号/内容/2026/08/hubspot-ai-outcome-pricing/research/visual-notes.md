# 视觉候选池

目标：多准备高质量、能回答文章问题的官方视觉。当前均为候选，不等于已获转载授权，也未写入正文。进入 `ready` 前须由编辑确认使用权、下载原图、登记修改和平台许可。

## 推荐编排

| 优先级 | 候选 | 画面回答的问题 | 原始页面／原图 | 质量与裁切建议 | 权利状态 |
|---|---|---|---|---|---|
| P0 | Prospecting Agent「$1/per lead」产品页截屏 | 这 1 美元到底在什么动作上发生？ | https://www.hubspot.com/products/sales/ai-prospecting-agent | 截取「Pay when work gets done」至「You pay when ... drafts outreach」完整语境；保留页面品牌与日期说明，不只截孤立价格 | 官方页面；`needs_editorial_confirmation` |
| P0 | HubSpot Credits Rate Sheet 截屏 | 100 credits 对应的正式计费动作是什么？ | https://legal.hubspot.com/hubspot-product-and-services-catalog | 截 AI Agents 表头与 Prospecting agent 一行；适合做正文证据图，可加中文框线但不得改原文 | 官方产品目录；`needs_editorial_confirmation` |
| P3 | 4 月 outcome-based pricing 公告主图 | 厂商如何包装「按结果付费」？ | https://www.hubspot.com/hubfs/Untitled%20design%20%281%29-Mar-31-2026-04-59-16-3850-PM.png | 已核原图仅 610 × 410，主体基本是橙色 HubSpot 标识，信息量低；不建议占正文图位，只保留兜底 | 官方新闻稿素材；`needs_editorial_confirmation` |
| P1 | Prospecting Agent 官方交互 Demo | Agent 怎样从信号走到推荐与外联？ | https://www.hubspot.com/products/sales/ai-prospecting-agent （「See prospecting agent in action」） | 从官方 Storylane 演示选一个能同时看到联系人、推荐理由和草稿的界面；不得用低清播放截图 | 官方交互演示；`needs_editorial_confirmation` |
| P1 | Data enrichment 设置页 | 用户在哪里打开／关闭数据补全？ | https://53.fs1.hubspotusercontent-na1.net/hub/53/hubfs/Knowledge_Base_2023-24-25/KB-Records/records-data-enrichment-settings.png | 官方 KB 原图；适合说明 default-off 与管理员控制。发布前核对界面版本 | 官方知识库截图；`needs_editorial_confirmation` |
| P1 | AI model training 设置页 | 为什么训练和 enrichment 不是同一个开关？ | https://53.fs1.hubspotusercontent-na1.net/hub/53/hubfs/Knowledge_Base_2023-24-25/KB-AI-settings/AI-settings-AI-model-training-settings.png | 与 enrichment 设置图并排或二选一；不要裁掉开关标题和说明 | 官方知识库截图；`needs_editorial_confirmation` |
| P1 | AI data access 设置页 | Agent 使用 CRM、对话和文件数据时，管理员能看到哪些控制？ | https://53.fs1.hubspotusercontent-na1.net/hub/53/hubfs/Knowledge_Base_2023-24-25/KB-AI-settings/AI-settings-generative-ai.png | 官方 KB 原图；适合放在「context 不是一句魔法」之后 | 官方知识库截图；`needs_editorial_confirmation` |
| P2 | Contact Discovery 原公告顶部 | 为什么正文只能写「原定 8 月 4 日」？ | https://community.hubspot.com/t/july-1-2026-contact-discovery-is-coming-soon-legal-update/151430 | 截到标题、失效提示和 8 月 4 日句子；若手机端信息过密，拆成两张证据卡 | 官方社区页面；`needs_editorial_confirmation` |
| P2 | 7 月 5 日撤回公告 | 数据边界为何成为产品问题？ | https://community.hubspot.com/t/we-got-this-wrong-and-we-are-fixing-it/152063 | 截撤回条款、重新评估 opt-in 和透明控制三处，避免截用户评论头像 | 官方社区页面；`needs_editorial_confirmation` |

## 已下载的官方原图

原图统一放在 `research/visual-candidates/`。它们只是编辑备选，不是正文资产；因此 `asset-manifest.yml` 仍保持空清单，权利检查仍为 `false`。

| 优先级 | 本地文件 | 原始像素 | 最适合回答的问题 | 编辑判断 |
|---|---|---:|---|---|
| P0 | `prospecting-enrollments-tab.png` | 2206 × 364 | 为什么「Ready for review」还没发送，而「Finished」也可能没有回复？ | 信息与正文核心判断贴得最近；适合保留完整状态栏，再放大两处状态说明 |
| P1 | `data-enrichment-settings.png` | 1811 × 1696 | enrichment 是否默认关闭、管理员能控制什么？ | 纵向原图清晰，适合手机端按设置区块裁切；发布前复核界面版本 |
| P1 | `ai-data-access-settings.png` | 1890 × 1170 | Agent 可以访问哪些 CRM、对话和文件数据？ | 信息密度高，宜只截相关开关并保留页签名称，避免小字糊成一片 |
| P1 | `ai-model-training-settings.png` | 1728 × 218 | AI model training 为什么是独立开关？ | 横向窄图，适合与 enrichment 图组成上下对照，不宜单独充当大图 |
| P2 | `prospecting-outreach-options.png` | 2390 × 1610 | 人工审核与自动发送如何切换？ | 原图质量高，但与主判断关系次于状态栏；正文图位不足时舍弃 |
| P3 | `outcome-pricing-hero.png` | 610 × 410 | 无法独立回答正文问题 | 只有品牌标识感，已降级为兜底，不建议使用 |

目录里的 `preview-*` 与 `small-*` 只用于本地快速查看，不作为发布候选。

## 备选原则

- 优先顺序：价格／计费证据图 > 产品工作流界面 > 数据控制界面 > 时间线页面。
- 不使用泛化 AI 机器人、握手、销售坐办公室等图库图。
- 不把营销效果数字图当成独立验证；若使用，图注必须标「HubSpot 自报」。
- 未获转载确认前，只保留链接与编辑建议，不将图片状态标为 `approved`。
- 若官方截图信息太密，优先用项目原创示意图重画「收费线」，原页面仅作来源；原创图也必须在 `asset-manifest.yml` 登记数据与修改。
