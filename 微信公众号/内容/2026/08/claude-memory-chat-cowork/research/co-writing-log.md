---
workflow_rule: CORE-COAUTHOR-001
opening_rule_id: PROJECT-WECHAT-OPENING-001
status: presented
mode: direct_write
story_contract_ref: "../brief.md"
selected_route_ref: "not_required"
started_on: "2026-08-26"
updated_on: "2026-08-26"
locked_unit_count: 0
reopened_unit_count: 0
---

# 分阶段共写记录

本文件只保存内部协作状态，不进入公开正文。用户本轮要求先形成草稿、梳理结构并找图，因此按 L2 单线直接写；所有单元均为候选稿，尚未由用户锁定。

## 不可逆决定

- 读者问题：Claude 记忆打通 Chat 与 Cowork 后，用户得到的是更方便的回忆，还是一层更可控、可迁移的工作上下文？
- 核心判断：记忆进入 Cowork 的任务执行层后，可见、可改、可隔离和可迁移比「记得更多」更重要；当前它仍不是完整的用户资产
- 正文采用的事实与实例：Claude 官方 4 项更新；帮助页冲突；删除源聊天不删记忆；ChatGPT 自动记忆／来源／project-only；Gemini 完整历史导入／Personal Intelligence；5 类社区样本
- 明确不采用的事实与方向：不采用无法稳定核对的社交互动量；不写全面领先；不把个别迁移故障写成系统性问题；不展开模型参数与订阅价格
- 开场发动机：从「Chat 已经知道、Cowork 还要重新入职」的具体摩擦切入
- 开场压力：Cowork 会接触文件并执行任务，错误记忆可能成为行动前提
- `time_first_exception`：none
- 开场检查：`python .agents/skills/self-media-ops/scripts/check_wechat_opening.py <file>`
- 结尾落点：平台记忆当缓存，可版本控制的外部文件当关键事实真源
- 用户确认方式：按锁定合同直接写后整体冷读
- 确认记录：2026-08-26 用户指令为「先做一篇草稿」「需要测试可占位」「先把结构梳理好，图找好」；未确认标题与正文单元

## 声音锚点

保存稳定引用和信息关系，不把表面词句做成正向模板。

| ID | 稳定引用 | 被认可的信息关系 | 不复制什么 | 状态 |
|---|---|---|---|---|
| V1 | 「把平台记忆当缓存，别把它当唯一数据库。」 | 用熟悉的工程关系解释便利层与真源层 | 不把全文写成技术黑话或口号合集 | proposed |
| V2 | 「它像刚来第一天的同事。」 | 用实际工作摩擦承接产品功能 | 不连续堆砌拟人化比喻 | proposed |

## 小节／段落契约

`owner_mode`：`human_first` / `ai_candidate` / `critique_only`。

| Unit | 范围 | owner_mode | 读者进入时怎样理解 | 本单元新增／纠正什么 | 证据或实例 | 必须保留的限制 | 读完把读者送到哪里 | 状态 |
|---|---|---|---|---|---|---|---|---|
| U1 | 开场 | ai_candidate | Chat 与 Cowork 是两个需要重复交代背景的入口 | 记忆进入执行场景会放大错误成本 | 官方双向记忆公告；Cowork 任务属性 | 官方行为未实测 | 追问到底改了什么 | presented |
| U2 | 更新拆解 | ai_candidate | 只知道「打通记忆」 | 增加实时、主题文件、敏感控制、开放范围 | Claude 官方公告与帮助页 | 文档冲突／rollout | 追问如何校验记错 | presented |
| U3 | 可审计性 | ai_candidate | 可见面板等于控制充分 | 区分源聊天与记忆条目的两层删除 | Claude 帮助页 | 版本历史待测 | 转到真实用户工作流 | presented |
| U4 | 社区反应 | ai_candidate | 可能期待一个统一正负口碑 | 展示痛点、外部真源、迁移与个案风险的多簇反应 | Reddit、HN、LinkedIn 抽样 | 不代表总体 | 需要用竞品校准新颖性 | presented |
| U5 | 竞品对照 | ai_candidate | Claude 可能是首个／全面领先 | ChatGPT 和 Gemini 各有成熟单项，Claude 强在组合 | 三家官方帮助文档 | 截止日期与账号差异 | 追问资产边界 | presented |
| U6 | 边界、实测与结尾 | ai_candidate | 可导入导出即等于所有权 | 完整历史、Claude Code、Skills、版本与项目隔离仍待解决 | 官方迁移范围、社区迁移问题、测试计划 | 未测试不下结论 | 给出三层上下文做法 | presented |

## 确认与返工

| Unit | 呈现时间 | 决定 | 用户／编辑原意 | 锁定引用或 SHA-256 | 后续动作 |
|---|---|---|---|---|---|
| U1-U6 | 2026-08-26 | pending | 等待用户整体冷读与实测选择 | — | 根据反馈局部修改，不并行重写 canonical draft |

## 重开记录

| Unit | 重开原因 | 旧文稳定引用 | 局部 diff | 决定人 | 结果 |
|---|---|---|---|---|---|
| none | — | — | — | — | — |

## 问题优先审稿与补丁

| Issue | 位置 | 读者损失 | 理由 | 通过条件 | 建议局部 diff | 决定 | 结果 |
|---|---|---|---|---|---|---|---|
| TEST-001 | 4 组待实测段落 | 把 rollout 或厂商承诺误认成作者实测 | 用户账号功能未知 | P0 测试至少完成 A、B、C、E，或正文保留明确占位 | 待回传后补 | pending | pending |
| VIS-001 | 竞品表 | 手机端横表可读性差 | 信息密度高 | 转成 1080×1440 信息图并预览 | 见 visual-notes | pending | pending |
| RIGHTS-001 | 3 张官方图 | 发布权利未人工确认 | 当前仅完成来源登记 | 用户确认 editorial use 或换成自制信息图 | 见 asset-manifest | pending | pending |

## 试跑指标

- `T_intake`：2026-08-26（精确时点未记录）
- `T_evidence_ready`：2026-08-26（精确时点未记录）
- `T_contract_locked`：2026-08-26（精确时点未记录）
- `T_first_text_handoff`：2026-08-26（精确时点未记录）
- `T_owner_reviewed`：null
- 首次整体冷读是否要求重做核心判断、开场发动机或章节依赖：null
- `keep`：0
- `meaning_right_wording_wrong`：0
- `wrong_direction`：0
- `delete`：0
- 锁定单元：0
- 无理由改写的锁定单元：0
- 新增重大事实／引语／权利／隐私阻断项：3
- 实测人工分钟：null
- 说明：缺失数据保持 `null`，不从聊天时长、token 或 Git 时间推算。
