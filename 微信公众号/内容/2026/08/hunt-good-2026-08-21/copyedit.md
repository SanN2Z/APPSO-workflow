---
status: pass
checked_at: "2026-08-21T12:31:08+09:00"
body_sha256: "bf764522fccc6935974a0fa76aff3e422e51f4d83ec7fcebe440bca56e7a5b4c"
scope: "title, body, headings, lists, captions, links, figures, final notes"
---

# 语法终校

## 检查结果

- 主谓、比较对象与事实边界：pass
- 并列、标点、长句和指代：pass
- 中文／英文／数字间距：pass
- 图注、图号、署名和链接：pass
- 朗读节奏与内部话术：pass

## 本轮新增修复

| ID | 位置 | 缺陷 | 修复 | 状态 |
|---|---|---|---|---|
| COPY-009 | ChatGPT Ads 结果段 | 「低收入更容易收到广告」会把首次曝光与曝光后频率混成一个结论 | 拆成两个研究问题，补赔率比、置信区间、`p = 0.0438` 与效应边界 | fixed |
| COPY-010 | Agent Coordination 结果段 | 单写「省 42%」省略任务条件 | 补消息密集前提、缓存变化和文件优先任务反例 | fixed |
| COPY-011 | 论文图注 | 原创重绘表述与最终论文图不一致 | 改为准确 Figure 编号、作者、arXiv 编号或 CC BY 4.0 署名 | fixed |
| COPY-012 | Cursor 段 | 旧 Open Graph 图无法支持产品集成细节 | 改用两张官方界面并补 Vercel、Depot、Buildkite 的对应正文 | fixed |
| COPY-013 | 3 张机制图图注 | v2 的「APPSO 制图」无法准确披露生成方式，且旧路径与最终插画资产不一致 | 替换为最终 v3／v4 插画路径，图注明确「AI 生成插画信息图，APPSO 编辑」，保留事实边界 | fixed |

完整复读在插画信息图、信息增补和图注替换后重新执行；无 open `COPY-*` 缺陷。
