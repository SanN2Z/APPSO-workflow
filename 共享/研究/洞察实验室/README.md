# 洞察实验室

这是把「有启发的判断」压回现实的统一入口。它不保存漂亮观点，而是要求每条洞察依次经过：范围、机制、反证、实验、证据、决策、资产和下一轮复用。

洞察实验室位于单篇内容包之上、SOP 之下：原始事实和反馈仍留在内容包；跨稿反馈仍由 `content-retrospective` 判断是否升级 SOP；这里仅追踪一个更上游的问题——某个机制是否真的在多个现实周期中成立。

## 两个入口

对话入口：

```text
使用 $insight-to-asset，把这条洞察缩成一个可证伪命题，并设计下一轮实验。
```

命令入口：

```powershell
# 查看当前洞察和到期复核
python .agents/skills/insight-to-asset/scripts/insight_loop.py status

# 校验台账、记录、WIP 和反证合同
python .agents/skills/insight-to-asset/scripts/insight_loop.py validate

# 新建洞察；先加 --dry-run 检查，不覆盖旧记录
python .agents/skills/insight-to-asset/scripts/insight_loop.py new `
  --id INSIGHT-002 `
  --slug concise-slug `
  --title "洞察标题" `
  --statement "可能被现实结果削弱的命题" `
  --scope "明确适用范围" `
  --owner strategy_editor `
  --next-review-on 2026-08-01
```

## 工作流

```text
观察到的现象
→ 可证伪的窄命题
→ 冻结基线、指标、阈值和护栏
→ 运行一个现实实验
→ 支持 / 反对 / 中性证据
→ 支持特定范围 / 修正 / 否定
→ Skill、模板、脚本或 SOP 候选
→ 独立复用、反例和迁移检查
```

全实验室同时最多运行 `1` 个实验。先关掉到期实验，再开启新实验，避免把「持续思考」误当成「持续验证」。

## 每轮必须留下的证据单元

一次迭代只有同时留下以下内容，才算从观点变成作品：

- 一个来自真实内容周期的问题和原始证据引用；
- 一个在看到结果前写下的预测与失败条件；
- 一份可比较的基线、结果和缺失数据说明；
- 一个可被下一 Session 使用的 Skill、模板、脚本或规则真源；
- 一次独立复用、反例或迁移检查；
- 一个明确的继续、修正、否定或退役决定。

Git 提交可以作为证据单元的版本边界，但提交次数、代码行数和文件数量本身不证明洞察成立。

## 当前主洞察

| ID | 命题 | 当前状态 | 证据 | 下一步 |
|---|---|---|---|---|
| [`INSIGHT-001`](insights/INSIGHT-001-feedback-loop-compounding/evidence.md) | 反馈资产只有分层后才会形成工作流复利吗 | `framed` | `E1` | 不推广文章编译器 0.2，保留反向结果 |
| [`INSIGHT-002`](insights/INSIGHT-002-parallel-best-of-n-selection/evidence.md) | 并行生成 3—5 篇完整候选并匿名评选，能否避免首稿路径锁定 | `retired` | `E1` | 保留历史反向结果；默认流程已被 INSIGHT-004 的人控单线试跑取代 |
| [`INSIGHT-003`](insights/INSIGHT-003-red-corpus-without-new-stencils/insight.yml) | 红库能否减少表达返工又不制造新套话 | `framed` | `E0` | 在后续 3 篇适用稿做匿名黑库／红黑库配对冷读 |
| [`INSIGHT-004`](insights/INSIGHT-004-stage-routed-cowriting/insight.yml) | 分阶段人控共写能否减少中心重置与语义返工 | `test_ready` | `E0` | 后续 3 个适用稿前瞻记录中心重置、单元返工、锁定保留、实耗和质量护栏 |

这里验证的是自媒体工作流机制，不是「谁未来发展更好」。职业上限、组织竞争力和所有 AI 工作的长期规律仍属于未证实的远期命题。

## 每周节奏

周初：

1. 先处理 `status` 报告的到期记录。
2. 一次只选择一个高决策价值、可证伪、可复用且验证成本可控的命题。
3. 写清「观察到了什么」「猜测的机制是什么」「下次会出现什么」「什么结果让我改口」。
4. 在实验开始前冻结主指标、阈值、维护成本和质量护栏。

周末：

1. 先登记反对证据、缺失数据和替代解释。
2. 不根据结果临时改变成功阈值。
3. 选择支持特定范围、修正、否定或继续收集，不使用含糊的「大体有效」。
4. 设置下一动作和复核日期；需要修改 SOP 时转入 `content-retrospective` 晋升门。

每月检查资产是否真的被复用、是否误报、维护成本是否超过减少的返工，以及只更换 adapter 能否迁移。

## 真源边界

- [`洞察台账.yml`](洞察台账.yml)：状态、记录路径、负责人和复核日期索引。
- `insights/<id>/insight.yml`：命题、反证、实验、结果和资产化真源。
- `insights/<id>/evidence.md`：可选的人类可读证据说明，只链接原始案例；结构化证据关系仍以 `insight.yml` 为准。
- `insights/<id>/review.md`：可选的长篇复核说明；当前状态、证据等级、决定和日期仍须同步回 `insight.yml` 与台账。
- [洞察合同](../../../.agents/skills/insight-to-asset/references/insight-contract.md)：状态、证据、实验和迁移规范。
- [反馈模式台账](../../运营/复盘/反馈模式台账.yml)：重复内容缺陷与 SOP 规则，不承载战略洞察。
- [SOP 变更台账](<../../运营/复盘/SOP 变更台账.yml>)：真正落地的流程修改，不复制到洞察记录。

个人比较、完整公司反馈、终稿版本链、后台数据、联系人、凭据和品牌原件不得复制进本目录。确需引用受限证据时，只保存受治理的索引；未经确认远端为 Private，不推送本目录的新资产。
