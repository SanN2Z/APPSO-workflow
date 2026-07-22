# 审校记录

审校日期：2026-07-22

## 当前阶段

- 状态：事实、文字、独立冷审与文章视觉已通过；等待用户人工审稿，停留在 `editorial_review`
- 视觉：封面、时间线和 3 张 Anthropic 官方报道素材已入稿；本稿按公众号后台继续手调的交付方式使用中性排版，不注入固定 APPSO CSS

## 固定质量门

- [x] 读者、盲区、单一主钩子和文章承诺明确
- [x] 标题五秒可复述，开头快速兑现同一承诺
- [x] 分析前已有理解全文所需的极简事实卡
- [x] 核心框架在正文前 25% 用文字提出
- [x] 主要段落形成「判断—证据—限制—读者后果」
- [x] 重要术语首次出现已翻译成人话
- [x] 主笔人话自检已完成
- [x] `avoid-ai-writing` 中文适配诊断已用 `detect` 模式完成
- [x] 无未解决的阻断/重大 `HUMAN-AI-*` 问题
- [x] 独立冷读能复述发生了什么、作者判断和读者关系
- [x] 开头、中段、结尾声音一致，无反复模板腔
- [x] 最后两三段回答标题，末句落在核心判断

## 事实、视觉与状态

- [x] 数字、日期、型号已按 `as_of` 复核
- [x] 厂商口径、研究结论与作者判断已区分
- [x] 当前正文 4 张图片引用均可解析
- [x] `asset-manifest.yml` 与正文图片引用一致
- [x] 封面与当前文章视觉权利已检查
- [x] 人工编辑交接使用 `project_adapter: "appsso"`、`delivery_mode: "manual_editor"`、`layout_profile: "default"`；版本化交接包的结构、图片路径、哈希、375 px / 390 px 检查入口、页面级图片防溢出规则与 API 阻断已通过本地检查，Chromium smoke 已确认 4 张正文图加载且复制按钮可触发
- [ ] 在真实公众号后台完成复制、字号／段距／缩进／对齐／图片调整、保存和重开检查
- [x] 验证脚本 0 error；warning 已说明
- [x] `fact_checked`、`rights_checked` 与状态字段真实

## 任务特定标准

- [x] 按能力范式梳理 2022—2026，不写成型号清单
- [x] METR 的时间跨度没有外推为全部职业自动化时间表
- [x] Fable 5、Mythos 5 科研能力使用厂商限定语
- [x] loss 被明确说明为比喻，且包含延迟、噪声、多目标与代理指标问题
- [x] 没有宣布任何纯认知能力为永久人类护城河
- [x] 结尾落到预测、验收、难作弊反馈与自有闭环

## AI-pattern diagnostic

- Skill：avoid-ai-writing 3.15.0
- Mode：detect
- Scope：title / deck / headings / body / notes
- Applied：workflow leakage / empty authority / template structure / rhythm / manufactured personality / speculative gaps
- Ignored as hard gates：English word lists / stylometric thresholds / punctuation quotas / detector score
- Status：pass

诊断说明：保留了历史时间线所需的年份并列，但已按能力范式压缩；全文 4 个小标题，长短句和段落长度有变化；未发现工作流泄漏、空泛权威、虚构采访、制造个性或用推测填补事实缺口。英文词表、风格统计和检测分数未作为中文稿硬门。

## 待处理

| ID | 严重度 | 责任人 | 问题证据 | 通过条件 | 状态 |
|---|---|---|---|---|---|
| RELEASE-001—005 | major/minor | 主编 / 独立审校 | 初稿中核心框架出现偏晚、反馈到所有权存在跳步 | loss 与闭环框架前置，补足控制权、授权边界和完整小闭环；独立复审通过 | resolved |
| COPY-001—006 | major | 文字编辑 / 主笔 | 初稿型号密度、loss 与 METR 定义、模板转场、并列结构和结尾长句 | 按能力范式压缩并完成逐项修复；正文哈希锁定 | resolved |
| VISUAL-001 | minor | 视觉与版权编辑 | 本轮仅有文字，尚未确定封面和正文信息图 | 发布前完成视觉方案、素材权利与 manifest 登记 | resolved |
| VISUAL-002 | blocker | 视觉与版权编辑 | `publish.yml` 未绑定封面，manifest 无发布素材 | 生成或取得已授权封面并完成登记 | resolved |
| LAYOUT-001 | blocker | APPSO 资产管理员 / 主编 | `appsso-article-v1` 要求固定正文头图，但仓库明确没有可直接发布的内部原件 | 手动后台交付不启用固定 profile；仅在密封草稿模式另行取得并登记头图 | resolved |
| LAYOUT-002 | major | 排版编辑 | 固定字号、行高、缩进和图片样式进入公众号后台后难以继续手调 | 使用 `manual_editor + default` 生成版本化交接包；本地门禁通过后，再做真实后台复制、编辑、保存与重开验证 | local_pass / backend_pending |
