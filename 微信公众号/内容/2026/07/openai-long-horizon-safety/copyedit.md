---
status: needs_fix
checked_at: ""
body_sha256: ""
scope: "title, body, headings, lists, captions, quotes, notes"
---

# 语法终校

> 2026 年 7 月 22 日热点开头改写后，上一版终校签字已失效。等待用户人工精修，再对精确正文重新终校并锁定哈希。以下记录仅保留为历史检查证据。

## 检查结果

- 主谓与比较结构：pass
- 并列、标点与长句：pass
- 指代与术语全称：pass
- 连接词着落：pass
- 中文引号与中英文数字空格：pass
- 朗读与内部话术：pass

## 缺陷记录

- `COPY-01`：resolved；开头改为「接连有用户投诉……」，保留用户报告边界。
- `COPY-02`：resolved；明确被扫描器拦下的是认证令牌。
- `COPY-03`：resolved；改用「像……这样的要求」统领 3 个示例。
- `COPY-04`：resolved；改为「在 Agent 执行层」明确防护层级。
- `COPY-05`：resolved；将 OpenAI 后的「他们」改为「团队」，消除组织与复数代词指代跳转。
- `COPY-06`：resolved；将「编号为 PR #287」改为「提交了 PR #287」，删除编号概念重复。
- `COPY-07`：resolved；补齐 GitHub 图注句末标点。
- `COPY-08`：resolved；将「其他系统成功但未公开的提交」改为「其他系统已经完成、但尚未公开的提交」，明确修饰关系。
- `COPY-09`：resolved；拆开「它甚至没有掩饰，模型自己……」的逗号拼接句。
- `COPY-10`：resolved；删除「完成任务，排在了……」中割裂主谓的逗号。
- `COPY-11`：resolved；删除「分类邮件，或者……」中不必要的顿挫。
- `COPY-12`：resolved；将段尾分号改为句号，保留结尾短段节奏但闭合句子。
- `COPY-13`：resolved；将热点开头拆成三句，并明确模型突破的是评测受限环境，避免读者误以为评测本身授权模型进入 Hugging Face 生产系统。

无 open `COPY-*` 缺陷。2026 年 7 月 22 日热点补丁加入后，完整正文已重新逐句检查并完成朗读复检。
