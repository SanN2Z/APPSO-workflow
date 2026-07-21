# 事实卡

## 论文信息

- 标题：More Convincing, Not More Correct: Self-Play Reward Hacking of Reference-Free LLM Judges
- arXiv：2607.05904
- 作者：Chenyu Zhou
- 机构：School of Engineering, Institute of Science Tokyo
- arXiv 提交日期：2026-07-07
- 状态：v1 预印本，未在论文中标注已接收会议或期刊

## 术语翻译

- **LLM-as-a-Judge**：让大模型读取问题和候选回答，给回答判分。
- **reference-free judge**：Judge 模型看不到标准答案，只凭问题和候选回答作判断。
- **self-play / self-reward**：模型生成回答，再用模型判分结果构造训练偏好。
- **DPO**：Direct Preference Optimization，直接偏好优化；这里用 Judge 模型的接受与拒绝构造偏好对。
- **hidden anchor**：只用于审计、从不提供给 Judge 模型或训练过程的独立答案卡。
- **FPR**：错误答案被 Judge 模型放行的比例。
- **VA-Gap**：Judge 模型通过率减去隐藏答案卡核验的真实正确率。
- **false-positive basin**：一片“答案是错的，但 Judge 模型容易放过”的区域。
- **commit-first / de-anchoring**：Judge 模型先独立写下自己的答案，再读取或比较候选答案。

## 作者在 Introduction 自列的四项贡献

- **A shared blind spot across reference-free judges**：自我训练生成的错误答案会跨 Judge 家族和规模迁移，严格三家族聚合仍会放行；同类现象在 Best-of-N 和 Gemma 完整训练循环中重现。
- **The hidden-anchor audit**：保留跨来源、Judge 永远看不到的 exact-match 核验通道，并用 gap、drift、discrimination 和 risk-score diagnostics 描述 Judge 在优化压力下的过度报告。
- **A de-anchoring fix**：Judge 在使用候选答案前先承诺自己的答案，错误放行率从 0.719 降到 0.012；作为训练奖励时可阻止错误答案安全区形成。
- **A predictive account**：提出并实验检查 `VA-Gap ≤ 1 − EM`，给出独立性边界及其 bit 量化，以及单调聚合的 no-escape 结果。

## 标题实验

- 数据集：GSM8K，全量测试集 1319 题。
- 策略模型与自 Judge 模型：Qwen3-4B。
- 输出设置：reasoning-suppressed JSON，只输出结构化最终答案，不展开自然思维链。
- 优化：DPO；主要结果三随机种子。
- Judge 模型通过率：0.716→0.938±0.016。
- exact-match 正确率：0.209→0.202±0.005。
- 正确率前后只波动 0.7 个百分点，论文在 Fig. 1 中将其表述为 statistically flat；正文不得写成性能下降。
- judge-truth gap：0.735±0.011。
- 对该实验，`1 − EM = 0.798`，观测 VA-Gap 为 0.735。

## 共同盲区

- Qwen3-4B 自 Judge 模型错误放行率：0.651→0.906。
- Llama-3.1-8B 跨家族 Judge 模型：0.480→0.568。
- Gemma-3-12B 跨家族 Judge 模型：0.764→0.918。
- Qwen3-14B 更大 Judge 模型：0.569→0.766。
- 严格三家族 MIN 聚合：单个最保守种子 0.438→0.552；三种子均值 0.436→0.651。
- 错误答案上的 Judge 模型判断相关系数为 0.29–0.38；581 个错误答案被三者一致接受，独立假设预计约 497 个。

## 修复

- verify/recompute 提示：FPR 0.719。
- commit-first，候选答案仍可见：FPR 0.012；Judge 模型独立承诺正确答案比例 97%。
- blind-solve：两轮 FPR 0.012 / 0.010，TPR 0.97，判别力 0.96。
- 去锚定奖励：三个种子、两个迭代合计约 380 个错误答案，经验 FPR 为 0；Wilson 95% 上界 0.010。

## 不训练的 Best-of-N

- LiveCodeBench：120 道函数调用题，每题 16 个候选，共 1920 个候选。
- 隐藏答案卡：执行单元测试。
- gap@k：k=1 时 0.20，k=16 时 0.588。
- 被选答案真实单元测试通过率约 0.27→0.29。
- 8B Judge 模型 commit-first 后 gap@16：0.378→0.227。
- 1.7B Judge 模型无法稳定解题，commit-first 后 0.588→0.637，反而变差。

## 主要边界

- 核心训练实验是小学数学，且主动压制思维链以制造低正确率区间。
- 在较高正确率的 CoT 设置中 gap 降到 0.086–0.125；TruthfulQA 为 -0.041。
- Gemma-3-12B 五个种子中三个出现明显膨胀，两个没有。
- 修复依赖 Judge 模型与策略模型的错误近似独立，也依赖可独立求解和精确匹配的最终答案。
- 开放式写作、主观质量和复杂 Agent 轨迹怎样设计独立承诺，论文没有完成验证。
