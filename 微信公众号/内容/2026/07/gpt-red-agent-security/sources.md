# 来源记录

访问日期均为 2026-07-16；正文时间统一采用北京时间。

| 来源 | URL | 类型 | 支持表述 | 边界 / 备注 |
|---|---|---|---|---|
| GPT‑Red: Unlocking Self-Improvement for Robustness | https://openai.com/index/unlocking-self-improvement-gpt-red/ | 厂商官方发布 / 一手来源 | GPT‑Red 身份、自我对弈训练、84% 对 13%、售货机和 Codex 案例、GPT‑5.6 训练与改善、预印本计划 | 所有实验数字均为 OpenAI 自报；页面未公开完整实验协议、预算、模型规格和置信区间 |
| OpenAI 官方 X 帖子 | https://x.com/openai/status/2077446718728425686 | 厂商官方社交账号 | 官方宣布时间；北京时间 2026-07-16 01:34 | X 页面未稳定提供可抓取正文；时间由 status ID 的 Snowflake 时间戳复核 |
| GPT‑5.6 System Card | https://deploymentsafety.openai.com/gpt-5-6 | 厂商系统卡 / 一手来源 | GPT‑5.6 prompt injection 评测口径；Connectors 与 Search and Function-Calling 表格；分层安全控制背景 | 系统卡没有出现 GPT‑Red 名称和 84% 数据，不能替代 GPT‑Red 预印本 |
| Understanding prompt injections | https://openai.com/index/prompt-injections/ | 厂商安全说明 / 一手来源 | 提示词注入定义；网页、邮件、文档中的间接攻击；最小权限、确认、隔离、监控等分层防守 | 是 OpenAI 的产品安全说明，不是独立评测 |
| How Vulnerable Are AI Agents to Indirect Prompt Injections? | https://arxiv.org/abs/2603.15714 | 论文预印本 / 原始研究 | OpenAI 复刻实验所基于的 Arena；41 个场景、工具/编码/电脑操作、静态安全 benchmark 过时问题 | OpenAI 使用的是内部 mirror，不能把原论文竞赛数字与 GPT‑Red 结果直接混算 |
| PISmith: Reinforcement Learning-based Red Teaming for Prompt Injection Defenses | https://arxiv.org/abs/2603.13026 | 论文预印本 / 相关研究 | 公开研究已训练 RL 攻击模型针对提示词注入防守，支持“方向并非首次出现”的限定 | 不用于证明 GPT‑Red 的效果；两者训练设置、模型与评测不同 |
| AI threats in the wild: The current state of prompt injections on the web | https://blog.google/security/prompt-injections-web/ | Google 安全团队官方研究博客 | 公共网页上已出现恶意提示词注入尝试；间接注入可藏在网页内容中 | 观察到恶意尝试不等于证明这些攻击成功控制了生产 Agent |
| Project Vend | https://www.anthropic.com/research/project-vend-1 | Anthropic / Andon Labs 官方案例 | Vendy 类售货机 Agent 的业务和工具背景 | OpenAI 的 GPT‑Red 测试发生在 OpenAI 办公室的相似系统，不能与 Anthropic 2025 年实验混成同一次事件 |

## 主要 claim 对照

| Claim | 证据位置 | 标签 |
|---|---|---|
| GPT‑Red 是内部、隔离保存的自动化红队模型 | OpenAI GPT‑Red 页 Summary、Training GPT‑Red through self-play | 厂商已核事实 |
| 攻防模型共同训练，攻击者找有效失败，防守者既要抵抗也要完成任务 | OpenAI GPT‑Red 页 Training GPT‑Red through self-play | 厂商方法描述；待预印本补足细节 |
| GPT‑Red 在 84% 场景成功，人类红队为 13% | OpenAI GPT‑Red 页 How strong is GPT‑Red? | 厂商内部 mirror 结果；不是等预算人机能力排名 |
| 售货机三个目标全部完成 | OpenAI GPT‑Red 页 Realistic red-teaming case studies | 厂商受控红队案例；不是外部攻击事件 |
| GPT‑5.6 Sol 的最难直接注入 benchmark 失败量约降到对照的六分之一 | OpenAI GPT‑Red 页开头 | 厂商内部 benchmark；不能外推现实风险 |
| 若干间接注入 benchmark 已超过 97% 准确率 | OpenAI GPT‑Red 页 Improving robustness；GPT‑5.6 System Card Table 5 提供相邻评测背景 | 厂商内部评测；不同场景不可直接与售货机实验横向比较 |
| 自动化 RL 红队不是 OpenAI 首次提出 | PISmith 等公开预印本 | 编辑限定；不否定 OpenAI 在训练规模与生产接入上的工程推进 |
| GPT‑Red 当前公开贡献主要是把自适应攻击者接进生产模型训练 | 对 OpenAI 发布与相关研究的编辑归纳 | 作者判断，不是官方原句 |

## 时效状态

- 雷达截点：2026-07-16 06:43 +08:00。
- 成稿复核：2026-07-16 12:13 +08:00。
- 预印本：未找到；OpenAI 页面仍写“later this week”。发布前必须再次复核。

## 图片与版权

本轮不下载或嵌入官方图片。用户按 `research/image-prompts.md` 在 Image2 生成并回传四张图；封面和两张正文解释图通过原尺寸检查，已登记为 AI 生成的项目资产。售货机案例图因出现疑似第三方品牌标志，仅保留在研究目录，不进入发布稿。
