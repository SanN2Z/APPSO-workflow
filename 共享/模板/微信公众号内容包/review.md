# 审校记录

审校日期：YYYY-MM-DD

终检真源：`.agents/skills/self-media-ops/references/wechat-editorial-gates.md`

## 1. 读者与文章承诺

- [ ] 文章只有一个目标读者、一个问题和一个主承诺；标题、开头、证据与结尾回答同一件事
- [ ] 首屏有已核动作或变化、未解决压力和继续阅读理由；适用稿件的共创记录已锁定并可追溯

## 2. 论证与声音

- [ ] 已先独立冷读，再打开故事合同；成稿已逐节映射 `CORE-CHAIN-001` 四格叙事链，偏离与断点均有记录
- [ ] 胜出稿已完成一次 `PROJECT-WECHAT-RHYTHM-001` + `PROJECT-WECHAT-PRAGMATIC-001` 完整诊断；修复后只复核修复点
- [ ] 候选稿到成稿的 diff 已按 `PROJECT-WECHAT-CONCRETE-001` 检查，没有「删具体、留抽象」
- [ ] 术语首次出现可理解，普通人处境贯穿证据与结尾，结尾没有另起第二套主张或方法清单

### 叙事链写后对照

- 冷读完成时间：
- 锁定故事合同：`research/judgment-workshop.md`
- 逐拍记录：
  - 第 1 拍：上一问 → 本节回答 → 留下的问题 → 下一节为何必须回答 → pass / defect
- 成稿偏离锁定链的位置与理由：none /
- 结论：pass / needs_fix / exempt

### AI-pattern diagnostic

- Mode：detect
- Scope：title / deck / headings / body / captions / notes
- Applied：RHYTHM / PRAGMATIC / workflow leakage / speculative gaps
- Ignored as hard gates：English word lists / stylometric thresholds / punctuation quotas / detector score
- Status：not_run / pass / needs_fix / blocked

| ID | Severity | 原句与位置 | 指纹类别 | 删除测试结果 | 信息任务与指向 | 处理 | Status |
|---|---|---|---|---|---|---|---|
| none found | — | — | — | — | — | — | — |

### 具体性守恒 diff

| 被删具体细节 | 类型 | 删除理由 | 保留的抽象概括 | 净效果 | 处理 |
|---|---|---|---|---|---|
| none | 对象 / 数字 / 场景 / 失败 / 引语 / 笑点 | — | none | pass | — |

## 3. 事实与来源

- [ ] 已按 `as_of` 重开时效来源，核对名称、身份、引语、日期、价格、榜单、政策、产品名与比较口径
- [ ] 事实、厂商自报、第三方结果、作者判断和推断已分开；企业或赞助材料有独立来源、真实限制和不适用场景

## 4. 视觉与权利

- [ ] 所有使用图片均在内容包内并登记来源、权利人、修改、允许平台和权利状态；无图时 manifest 如实为空
- [ ] 图注与比较边界准确，手机宽度可读，正文不依赖图片才能理解核心逻辑

## 5. 精确正文终校

- [ ] 结构与表达修复完成后、copyedit 前只运行一次 `PROJECT-WECHAT-AI-LEXICON-001` 附录扫描；命中均已修复或记录窄豁免
- [ ] `copyedit.md` 已通过语法、指代、比较、分句层级、标点、术语、图注与文末注释检查，正文 SHA-256 与 draft frontmatter 一致

## 6. 状态与交付

- [ ] `fact_checked`、`rights_checked`、`copyedit_checked` 和内容状态反映真实完成情况；validator 为 0 error，warning 已处理或说明
- [ ] 无 blocker、未关闭 major、开放的 `HUMAN-RHY-*` / `HUMAN-AI-*` / `COPY-*`、过期哈希、权利缺口、临时路径或敏感信息；外部动作有本次授权

### 任务特定标准

如 `brief.md` 或编辑反馈有会改变本稿放行决定的标准，逐条列出；没有配额。无则写 `none`。

- none

### 待处理

- `ID | 严重度 | 责任人 | 问题证据 | 通过条件 | 状态`
- none
