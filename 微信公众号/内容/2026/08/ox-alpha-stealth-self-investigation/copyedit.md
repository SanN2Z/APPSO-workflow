---
status: pass
checked_at: "2026-08-22 11:17:43+09:00"
body_sha256: "a72e5d88ae37e3e9c664125bdd6d340c39b4e376aa9624e5883baf712ed855ff"
scope: "title, body, headings, image captions, lists, links, numbers, final sentence"
---

# 语法终校

## 检查结果

- 主谓、指代与比较结构：pass
- 数字、日期、模型名与产品名：pass
- 中文与英文／数字间距：pass
- 标点、长句与 Markdown：pass
- 图片替代文本、图注与链接：pass
- 事实语义保持：pass
- 朗读节奏与内部话术：pass

## 修复记录

- `COPY-001`：将「随材料附带」改为网页公开标题，移除读者不可见的内部指代。
- `COPY-002`：将 100T 从「请求数」改为「平台每天能处理的 token」，避免单位解释失真。
- `COPY-003`：把整齐的镜子／帽子／工牌排比改成具体动作句，降低模板化收口。
- `COPY-004`：统一 Ox Alpha、OpenRouter、OpenCode Zen、DeepSWE、Hermes Agent 与模型 ID 的写法和中英文间距。
- `COPY-005`：逐一核对 7 个图片路径、替代文本、署名和原帖链接，未发现空引用。
- `COPY-006`：将笨拙涂鸦从 Markdown 正文移至 `publish.yml` 头图并兼作封面；补充可见「AI 生成示意图」标记，避免预览中重复出现同一张图。

上述问题均已修复；完整正文重新逐句检查，无开放 `COPY-*` 缺陷。
