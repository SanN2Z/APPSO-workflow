# QwenWork 候选 round-01｜冷读交接

---
status: awaiting_user_cold_read
created_on: 2026-08-03
canonical_draft_changed: false
formal_blind_selection_completed: false
---

本轮使用同一份事实底稿与故事合同，生成 3 条叙事路线。当前会话没有启用隔离写作与匿名评审，因此这里不宣布胜出稿，也不把任何候选复制到 `draft.md`。

| 候选 | 叙事入口 | 推进方式 | 正文字符数（去空白，含 Markdown 标记） | SHA-256 |
|---|---|---|---:|---|
| [A](candidate-a.md) | 任务结束后留下的一组文件 | 按实测时间顺序检查交付、页面事实和数据入口 | 2725 | `b9f6d3ad61a1d83e4e351fa973de6b998a8404e70a0494c712f539ee5090b75e` |
| [B](candidate-b.md) | 一张很像官网的生成网页 | 从未确认文案倒查资料、生成过程与公开使用边界 | 2720 | `471183658fa7652eaa41aeb04fbbc37a8e5bf021811c48912eb35665d95678cf` |
| [C](candidate-c.md) | 微信消息触发桌面任务 | 用「少一次手工搬运」贯穿手机、文件、网页和业务数据 | 2663 | `803b49ce4181a55058c4714c1519cbdc3030b989ea1b5294af1364d8d45b92cc` |

## 冻结前检查

- 共同事实与边界：pass。
- 图片相对路径：全部可解析。
- `PROJECT-WECHAT-PRAGMATIC-001` 轻量自检：3 / 3 已记录。
- `PROJECT-WECHAT-AI-LEXICON-001`：
  - A：正文仅保留 1 处用户实测生成页原文，已记录 `WX-EXPR-014` / `WX-EXPR-015` 窄豁免；
  - B：正文仅保留同一处用户实测生成页原文，已记录窄豁免；
  - C：无未处理命中，无豁免。
- 完整 human-voice、AI-pattern、事实硬门与逐句终校：候选阶段未运行。

## 冷读方式

先只读正文，不看各文件末尾的 HTML 注释。选择可以是 A、B、C 或「一篇都不要」。判断时优先回答：

- 哪篇让你最快知道千问办公适合什么工作？
- 哪一段开始想退出？
- 哪句话一看就不喜欢？
- 哪篇的结尾最像一个真实使用决定？
