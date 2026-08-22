---
workflow_rule: CORE-COAUTHOR-001
opening_rule_id: PROJECT-WECHAT-OPENING-001
status: planning
mode: guided
story_contract_ref: "../brief.md"
selected_route_ref: "not_required"
started_on: "YYYY-MM-DD"
updated_on: "YYYY-MM-DD"
locked_unit_count: 0
reopened_unit_count: 0
---

# 分阶段共写记录

本文件只保存内部协作状态，不进入公开正文。相邻普通段落承担同一任务时可以共用一个小节契约，不为每句话建表。

## 不可逆决定

- 读者问题：
- 核心判断：
- 正文采用的事实与实例：
- 明确不采用的事实与方向：
- 开场发动机：
- 开场压力：
- `time_first_exception`：none / 仅在时间本身构成核心因果压力时填写
- 开场检查：`python .agents/skills/self-media-ops/scripts/check_wechat_opening.py <file>`
- 结尾落点：
- 用户确认方式：逐节确认 / 按锁定合同直接写后整体冷读
- 确认记录：

## 声音锚点

保存稳定引用和信息关系，不把表面词句做成正向模板。

| ID | 稳定引用 | 被认可的信息关系 | 不复制什么 | 状态 |
|---|---|---|---|---|
| V1 |  |  |  | proposed / accepted / retired |

## 小节／段落契约

`owner_mode`：`human_first` / `ai_candidate` / `critique_only`。

| Unit | 范围 | owner_mode | 读者进入时怎样理解 | 本单元新增／纠正什么 | 证据或实例 | 必须保留的限制 | 读完把读者送到哪里 | 状态 |
|---|---|---|---|---|---|---|---|---|
| U1 |  |  |  |  |  |  |  | planned / presented / locked / reopen / dropped |

## 确认与返工

标签只描述决定，不合成为「人味分数」。

| Unit | 呈现时间 | 决定 | 用户／编辑原意 | 锁定引用或 SHA-256 | 后续动作 |
|---|---|---|---|---|---|
| U1 |  | keep / meaning_right_wording_wrong / wrong_direction / delete |  |  |  |

## 重开记录

只有事实错误、已经证明的链条断裂或用户明确要求可以重开 `locked` 单元。

| Unit | 重开原因 | 旧文稳定引用 | 局部 diff | 决定人 | 结果 |
|---|---|---|---|---|---|
| none | — | — | — | — | — |

## 问题优先审稿与补丁

| Issue | 位置 | 读者损失 | 理由 | 通过条件 | 建议局部 diff | 决定 | 结果 |
|---|---|---|---|---|---|---|---|
| none | — | — | — | — | — | — | — |

## 试跑指标

- `T_intake`：
- `T_evidence_ready`：
- `T_contract_locked`：
- `T_first_text_handoff`：
- `T_owner_reviewed`：
- 首次整体冷读是否要求重做核心判断、开场发动机或章节依赖：null
- `keep`：0
- `meaning_right_wording_wrong`：0
- `wrong_direction`：0
- `delete`：0
- 锁定单元：0
- 无理由改写的锁定单元：0
- 新增重大事实／引语／权利／隐私阻断项：0
- 实测人工分钟：null
- 说明：缺失数据保持 `null`，不从聊天时长、token 或 Git 时间推算。
