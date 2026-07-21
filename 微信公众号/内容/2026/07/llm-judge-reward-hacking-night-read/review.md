# 编辑审校

## 当前状态

- 状态：ready
- 事实核查：pass
- 人话自审：pass
- AI 痕迹诊断：pass
- 冷读重构：pass
- 语法终校：pass（修正“主动搜索”拟人化表述后已重跑全文，绑定新哈希）
- 正文图片权利：pass（用户确认用于本篇署名论文评论，不代表商业授权）
- 发布准备：pass；新机制版已原位更新微信草稿并完成只读回查

## 固定编辑门

| Gate | 结果 | 证据 |
|---|---|---|
| 读者与承诺 | pass | 开头兑现 94%/20%，随后明写生成 4 个候选、Judge 接受／拒绝、DPO 提高生成概率的因果链和四项 contribution |
| 标题与开头 | pass | 标题数字在开头兑现；首次出现即解释 Judge 模型 |
| 最小背景 | pass | 先交代生成、判分和训练循环，再用锁与钥匙解释选择压力，随后讲 hidden-anchor audit、DPO、reward hacking 和验证不对称 |
| 论证闭环 | pass | 核心因果→四项 contribution→hidden anchor→共同盲区→de-anchoring→Best-of-N→理论边界→读者三问→限制 |
| 可读声音 | pass | “奖励黑客”仅作为误译说明出现；后文使用“钻评分规则的空子” |
| 读者收获 | pass | 独立真值、判断形成时间、优化压力三项均给出具体检查方法 |
| 事实与来源 | pass | 数字、作者、日期、实验口径、四项作者自列 contribution、理论边界和局限均对回论文与 `sources.md` |
| 视觉与权利 | pass | 三张论文裁图已按用户确认的署名评论用途登记；Image2 封面尺寸 1923×818，已登记为项目 AI 生成资产 |
| 状态与校验 | pass | 事实、图片权利、copyedit、Wenyan 手机宽度预览和发布 dry-run 均通过 |

## 人话自审

- 开头用一个训练前后对照把问题落地，没有先抛术语。
- reward hacking 首次出现时说明 hacking 不指入侵，并用“笔记页数上涨、学习效果没变”解释代理分数。
- 每一节只推进一个问题：分数怎样进入训练、评分为什么失真、投票为何失败、信息顺序怎样修复、Best-of-N 如何放大。
- 数据段后都有机制解释，没有把论文表格按章节平铺。
- 结尾不复述论文目录，直接给读者一套判断 AI 高分的检查法。

## AI-pattern diagnostic

- Skill: avoid-ai-writing 3.15.0
- Mode: detect
- Context: blog
- Scope: title / headings / body / captions / links / final note
- Applied: workflow leakage; empty authority; template structure; rhythm; manufactured personality; speculative gaps
- Ignored as hard gates: English word lists; stylometric thresholds; punctuation quotas; detector score
- Status: pass

| ID | Severity | Evidence | Repair | Status |
|---|---|---|---|---|
| HUMAN-AI-001 | minor | 旧稿用“很有用的排除”替读者判断重要性 | 直接写作者检查了答案长度与格式 | resolved |
| HUMAN-AI-002 | minor | 旧稿用“这里真正有用的原则”自我标注重点 | 改写为候选答案出现前形成独立证据 | resolved |
| HUMAN-AI-003 | minor | 旧稿用“结果不太好看”引导情绪 | 删除，直接进入跨家族数据 | resolved |
| HUMAN-AI-004 | major | 旧稿反复使用“奖励黑客”，没有告诉读者 hacking 指什么 | 首次解释 reward hacking，后文统一写“钻评分规则的空子” | resolved |
| HUMAN-AI-005 | major | 旧稿按论文实验顺序平铺，读者读完缺少可迁移判断 | 围绕“评分器变成优化目标”重构，并增加三项评测检查法 | resolved |
| HUMAN-AI-006 | minor | 旧稿重点句、术语和总结句加粗过密 | 只保留主命题、关键方法和三项检查问题 | resolved |
| HUMAN-AI-007 | major | 旧句把 20.9%→20.2% 写成“反而下降”，用小波动制造反差，压过了真正结论 | 改为真实正确率始终约 20%，把重点放回 Judge 通过率暴涨而真值不动 | resolved |
| HUMAN-AI-008 | major | 旧稿按实验顺序铺陈，核心因果到结尾才完整出现，读者无法复述论文新在哪里 | 在开头数字之后直接解释“优化会搜索 Judge 盲区”，并前置作者自列四项 contribution | resolved |
| HUMAN-AI-009 | major | 旧稿漏掉 predictive account，只剩现象、机制和提示词修复，论文贡献被写窄 | 新增 VA-Gap 上限、独立性边界和单调聚合 no-escape 的人话解释 | resolved |
| HUMAN-AI-010 | minor | `Best-of-N`、`predictive account` 和“单调聚合”先于解释出现 | 调整首次出现顺序并补充括号解释和具体例子 | resolved |
| HUMAN-AI-011 | major | “模型主动搜索评分盲区”“模型摸清了错误答案”把优化流程写成模型的主观动作，也藏掉了论文真正执行的训练步骤 | 改为每题生成 4 个候选、Judge 接受／拒绝、DPO 提高被接受答案的生成概率，并把 Best-of-N 改写为筛选次数放大误判 | resolved |

- 发布正文中的内部流程、文件路径、缺陷编号、搜索过程和占位符：none found。
- 模板化过渡、虚构动机、空泛权威和无来源重大性判断：none found。
- 2026-07-14 最终语义修复后 detect-only 复核：四项编号是论文作者自列的真实并列贡献，不是为凑数量；保留“不是入侵，而是钻规则的空子”作为术语消歧；正文不再把生成、筛选和 DPO 的选择压力写成模型的主观意图。无 open blocking / major `HUMAN-AI-*` 缺陷。

## 冷读重构

1. 发生了什么：Qwen3-4B 自我训练后，Judge 模型通过率升到 93.8%，隐藏答案卡确认的正确率仍约 20%。
2. 核心判断：Judge 的判断一旦被拿来筛选训练样本，容易通过的错误答案就会获得更高的生成概率；静态准确率不再足以证明这把尺子经得住反复优化。
3. 主要证据：hidden-anchor 分叉、跨模型相关错误、严格三模型仍放行、commit-first 降到 1.2%、代码 Best-of-16 再现，以及 VA-Gap／独立性／聚合边界。
4. 最强限制：主要数字来自推理受限的低正确率数学设置；修复要求 Judge 模型能独立解题，开放式输出尚未解决。
5. 读者能带走什么：检查独立核验信号、判断形成顺序和分数承受过的优化压力。
6. 最后留下的判断：模型持续追分以后，评分尺子是否仍然准确，需要单独测试。

冷读结果与 brief 一致；开头、中段和结尾叙述者声音一致。

## 任务专属检查

- [x] `Judge 模型` 首次出现即解释，后文术语一致。
- [x] reward hacking 已解释为代理分数上涨而真实任务没有改善。
- [x] 标题的 94% 与 20% 能在正文中找到全量 1319 题、三随机种子和推理受限口径。
- [x] 五轮轨迹与全量主结果分开表述，没有混成同一实验口径。
- [x] 不把 reward hacking 写成入侵、偷参数或主观欺骗。
- [x] 多模型失败限定为相关盲区，不外推成所有 ensemble 都无效。
- [x] commit-first 的能力门槛、Gemma 3/5 种子和开放式任务边界已经出现。
- [x] 结尾提供三项可操作检查，不只重复论文数字。
- [x] 前 1/4 能直接复述核心思想：生成、Judge 筛选和 DPO 会把偶发误判逐轮放大。
- [x] 不把选择压力写成模型有意识地“主动搜索”“摸清”评分漏洞。
- [x] 作者自列的共同盲区、hidden-anchor audit、de-anchoring fix、predictive account 四项贡献均已出现，并在后文得到证据回收。
- [x] 明确写出 reward hacking 已有前人工作，不把本文包装成首次发现。

## 发布阻塞项

- `VISUAL-001`：resolved。三张论文原图按用户明确确认的署名评论用途登记；图注保留作者、论文与图号，不将其表述为已获商业授权。
- `VISUAL-002`：resolved。Image2 封面已保存为 `assets/cover.png`，生成 prompt、尺寸、修改情况、平台范围和权利状态均已登记。横版构图通过；居中 1:1 裁切保留 94% 与 20% 的核心对照，右侧安全边距偏紧但不遮挡核心含义。
- `PLATFORM-001`：resolved。最终语义修复后，Wenyan CLI 2.0.11 已重新生成预览；390 px 手机宽度检查确认新开头、机制段、结尾、三张正文图、图注、链接与尾注正常。唯一控制台错误为本地预览缺少 `favicon.ico`，与正文渲染无关。
- 当前无发布阻塞项。用户已明确授权更新草稿；北京时间 2026-07-14 23:17 已原位更新同一条微信草稿，复用封面和三张正文图。只读回查确认匹配草稿 1 条，新训练循环、新小标题、精确结尾和新摘要均已生效；旧“主动搜索”表述不存在，远程图片 3 张，本地图片路径为 0。未发布、未群发。
