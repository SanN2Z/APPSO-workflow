# 审校记录

审校日期：YYYY-MM-DD

## 固定质量门

- [ ] 读者、盲区、单一主钩子和文章承诺明确
- [ ] 标题五秒可复述，开头快速兑现同一承诺
- [ ] 分析前已有理解全文所需的极简事实卡
- [ ] 核心框架在正文前 25% 用文字提出，图文口径一致
- [ ] 主要段落形成“判断—证据—限制—读者后果”
- [ ] 重要术语首次出现已翻译成人话
- [ ] 主笔人话自检已完成
- [ ] `avoid-ai-writing` 中文适配诊断已用 `detect` 模式完成，未用检测分数或英文阈值硬判
- [ ] 无未解决的阻断/重大 `HUMAN-AI-*` 问题
- [ ] 独立冷读能复述发生了什么、作者判断和读者关系
- [ ] 开头、中段、结尾声音一致，无反复模板腔
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

## AI-pattern diagnostic

- Skill：avoid-ai-writing 3.15.0
- Mode：detect
- Scope：title / deck / headings / body / captions / notes
- Applied：workflow leakage / empty authority / template structure / rhythm / manufactured personality / speculative gaps
- Ignored as hard gates：English word lists / stylometric thresholds / punctuation quotas / detector score
- Status：pass | needs_fix | blocked

## 待处理

| ID | 严重度 | 责任人 | 问题证据 | 通过条件 | 状态 |
|---|---|---|---|---|---|
