# 审校记录

审校日期：YYYY-MM-DD

## 固定质量门

- [ ] 读者、盲区、单一主钩子和文章承诺明确
- [ ] 适用长稿的 `research/judgment-workshop.md` 已经用户确认并锁定，含 3–5 个候选判断、3–5 个真实决策点、1 个主判断和 2–4 个支撑判断
- [ ] 普通人的共同处境贯穿开头、证据和结尾，没有在末尾临时补一段
- [ ] `personal` / `company` 模式明确；公司稿没有把个人经历改写成普遍事实
- [ ] 标题五秒可复述，开头快速兑现同一承诺
- [ ] 分析前已有理解全文所需的极简事实卡
- [ ] 核心框架在正文前 25% 用文字提出，图文口径一致
- [ ] 主要段落形成「判断—证据—限制—读者后果」
- [ ] 重要术语首次出现已翻译成人话
- [ ] 主笔人话自检已完成
- [ ] `avoid-ai-writing` 中文适配诊断已用 `detect` 模式完成，未用检测分数或英文阈值硬判
- [ ] 无未解决的阻断/重大 `HUMAN-AI-*` 问题
- [ ] 独立冷读能复述发生了什么、作者判断和读者关系
- [ ] 开头、中段、结尾声音一致，无反复模板腔
- [ ] 已按 `.agents/skills/self-media-ops/references/wechat-clumsy-writing.yml` 的声明模式生成或重写初稿；终校只修复影响理解与正确性的地方，没有机械磨平全部节奏
- [ ] 「笨拙」没有引入错字、病句、事实错误、逻辑断裂、虚构案例、假共识或刻意网络用语
- [ ] 最后两三段回答标题，末句落在核心判断

## 事实、视觉与状态

- [ ] 数字、日期、价格、榜单已按 `as_of` 复核
- [ ] 引语、身份与语境已核对
- [ ] 厂商口径、第三方结果与作者判断已区分
- [ ] 所有正文图片路径存在且移动端可读
- [ ] `asset-manifest.yml` 已登记全部图片
- [ ] 图片权利与图注已检查
- [ ] 验证脚本 0 error；warning 已说明
- [ ] `fact_checked`、`rights_checked` 与状态字段真实

## 任务特定标准

- [ ] 从 `brief.md` 和编辑反馈补充 3–8 个可观察标准

## 核心判断与笨拙写作记录

- Workshop：`research/judgment-workshop.md`
- Workshop status：discussing | locked | not_required
- Rounds completed：
- Voice mode：personal | company
- User confirmed：true | false
- Clumsy Prompt：`.agents/skills/self-media-ops/references/wechat-clumsy-writing.yml`
- Prompt version：0.1
- Prompt SHA-256：
- Applied mode：personal_visible | company_restrained
- Result：pass | needs_fix | blocked

## AI-pattern diagnostic

- Skill：avoid-ai-writing 3.15.0
- Mode：detect
- Scope：title / deck / headings / body / captions / notes
- Applied：workflow leakage / empty authority / template structure / rhythm / manufactured personality / speculative gaps
- Ignored as hard gates：English word lists / stylometric thresholds / punctuation quotas / detector score
- Status：pass | needs_fix | blocked

### `WECHAT-HUMAN-002` 语义检查

不把「革命」「到账」「账单」「考试」设为禁词。候选句必须记录字面／来源判断、整句可迁移测试、删除测试和具体修复；没有候选时写 `none found`。

| 候选原文 | 字面事实／来源原话 | 可迁移测试 | 删除后损失 | 具体修复或放行理由 |
|---|---|---|---|---|
| none found | — | — | — | — |

### 表达候选库

APPSO 稿按仓库根路径 `.agents/skills/self-media-ops/references/wechat-expression-library.yml` 先审 `P0 / default_avoid`，再审 `P1 / semantic_review`。只记录完成语义检查后的实际缺陷或放行项，不粘贴关键词扫描结果；非 APPSO 项目需要先确认是否声明了自己的 adapter。`WX-EXPR-020` 若已记入上一张 `WECHAT-HUMAN-002` 表，本表只引用对应 `HUMAN-AI-*`，不重复抄候选原文和五步判断。

| `WX-EXPR-*` | 优先级 | 候选原文 | 字面／来源 | 信息任务／删除测试 | 可迁移 | 邻近重复 | 修复或放行理由 | `HUMAN-AI-*` |
|---|---|---|---|---|---|---|---|---|
| none found | — | — | — | — | — | — | — | — |

## 待处理

| ID | 严重度 | 责任人 | 问题证据 | 通过条件 | 状态 |
|---|---|---|---|---|---|
