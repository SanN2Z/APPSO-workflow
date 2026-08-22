# 自媒体运营项目指令

## 默认走最短路径

- 本仓库只处理选题、调研、写作、视觉、发布准备和复盘；不要读取无关科研项目。
- `X/` 与 `微信公众号/` 可以共享已核事实，成稿必须分别写。
- 开始任务先运行 `git status --short`，只读取目标平台、目标内容包和本次任务真正需要的规则。
- `上下文/当前重点.md` 只在新任务、跨内容包切换或仓库整理时读取；同一稿件的小改不重复加载。
- 使用 `.agents/skills/self-media-ops/SKILL.md` 做任务分流。详细流程只有一个真源：`共享/运营/SOP/内容工作流.md`。

## 按触发条件加载

| 触发条件 | 追加读取 |
|---|---|
| APPSO、Hunt Good、公司稿或公司资产 | `APPSO-数字资产/README.md`、保密分级及对应专项 SOP |
| L3 多路线稿、中心结构性重写或用户明确共创 | `wechat-judgment-workshop.md`；只有并行研究或独立定向审稿才加载 `wechat-team.md`，不得并行改 canonical prose |
| 用户明确要求文风实验且已有实质正文 | `wechat-clumsy-writing.yml` |
| 生图或图片编辑 | `共享/运营/SOP/Image2 生图工作流.md` |
| 预览、排版、草稿交接 | `wechat-publishing.md` 或公司浏览器排版 SOP |
| 收到实质修改意见、交付或发布 | `.agents/skills/content-retrospective/SKILL.md` |
| 把长期判断做成实验 | `.agents/skills/insight-to-asset/SKILL.md` |
| 整理或提交 Git | `共享/运营/SOP/Git 提交与仓库整理 SOP.md` |

错字、单句润色、补链接等不改变判断、事实、素材和发布状态的小改，不启动完整复盘或多角色评审。

## 不可省略的硬门

- 数字、日期、价格、人物身份、产品名、政策、榜单和「最新」信息必须核查；优先一手来源。
- 事实、厂商自报、第三方结果、作者判断、推断和玩梗必须分开；引语核对原文与说话人。
- 每张发布图片都要在进入 `ready` 前登记来源、权利人、修改、允许平台和权利状态。AI 图必须标记，不能伪装成新闻现场或官方截图。
- APPSO 的 `internal` / `restricted` 资料不得自动进入个人稿或公开环境。公司稿与个人稿只共享已核事实。
- 密钥只放本地 `.env`；不得在日志、稿件或提交中输出凭据、Cookie、登录态或完整请求头。
- 发布、群发、评论、私信、关注、排期以及浏览器覆盖草稿，需要用户在当前任务中明确授权；授权必须对应本次账号、正文、图片和动作，不复用旧授权。
- 不覆盖或混入用户尚未提交的无关修改；远端必须保持 Private。

## 内容状态

`idea → research → draft → fact_checked → editorial_review → ready → published → archived`

- 状态以 `draft.md` frontmatter 为真源，不靠目录名表达。
- Codex 最多自动推进到 `ready`。
- `ready` 必须通过事实、权利、终校、平台适配和敏感信息检查。
- 只有用户明确确认已发布，才能写成 `published` 并记录真实链接和日期。

## 中文交付规则

- 面向用户或读者的中文使用「」；嵌套引用使用『』。
- 中文与英文、中文与阿拉伯数字之间加 1 个半角空格，例如：`OpenAI 发布 GPT-5.6`、`7 月 20 日`。
- 中文标点与英文或数字之间不额外加空格；代码、命令、URL、路径和必须逐字保留的原文不机械替换。

## Git

- 一个可验证工作单元完成后再提交；不要把无关内容混进同一提交。
- 提交前运行 `powershell -ExecutionPolicy Bypass -File tools/repository_preflight.ps1`。
- 使用 `type(scope): 摘要`，例如 `docs(sop): 精简内容生产入口`。
- 不提交生成物、临时素材、依赖、凭据、浏览器 Profile、登录态或受限原件；禁止使用 `git add -f` 绕过忽略规则。
- 默认只向已确认的私有 `origin` 推送通过检查的提交。
