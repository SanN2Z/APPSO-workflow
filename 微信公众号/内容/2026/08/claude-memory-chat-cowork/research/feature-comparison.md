# Claude、ChatGPT、Gemini 记忆能力对照

`as_of: 2026-08-26`

这份表是草稿事实底稿。产品持续更新，正式发布前需重新打开所有一手文档。

| 轴 | Claude | ChatGPT | Gemini |
|---|---|---|---|
| 记忆基本单元 | Profile、Preferences、Topics 等短主题文件；新系统在聊天中更新 | 自动更新的 memory summary；可查看 memory sources；旧式 saved memories 仍有管理入口 | 过去聊天、Saved info；Personal Intelligence 可引入连接的 Google 应用数据 |
| 用户可见性 | Memory 面板列出主题条目，可展开摘要与细节 | 可编辑摘要并查看来源，但官方明确摘要不展示系统记住的全部内容 | 可直接询问 Gemini 使用了哪些过去聊天；没有 Claude 式完整主题文件列表 |
| 编辑与删除 | 逐项修改／删除，可暂停或重置；删除源聊天不自动删记忆条目 | 可删记忆；要彻底清除通常需同时处理 saved memory 与源聊天 | 可在对话中纠正；过去聊天形成的记忆通常靠删除相关聊天清除；连接应用还需处理数据源／连接 |
| 跨产品表面 | 2026-08-25 公告明确 Chat ↔ Cowork 双向；Claude Code 未被点名 | 普通聊天、Projects、文件和部分 connected apps | Gemini 网页／移动等；过去聊天记忆不用于 Gems 和 Gemini Live |
| 项目隔离 | 帮助页描述各 Project 有分离记忆；与新共享记忆的组合边界待实测 | default memory 与 project-only memory；后者不引用项目外对话／记忆 | Gems 不使用过去聊天记忆；账号、地区和表面限制较多 |
| 临时模式 | Incognito；不进入普通历史／记忆。Team／Enterprise 仍受组织导出与保留策略影响 | Temporary Chat | Temporary Chat；也可按聊天关闭 Personal Intelligence |
| 敏感信息 | 默认排除健康、种族／族裔、宗教、政治、性别认同等；主动开关只向前生效；更高敏信息仍不保存 | 通过 Memory 开关与 Temporary Chat 控制是否引用／写入；本轮不比较三家的敏感信息分类准确率 | 控制主要围绕 Past chats、Personal Intelligence、连接应用和 Temporary Chat，没有同构的主题级敏感开关 |
| 跨服务导入 | 用引导提示从其他 AI 服务提炼并导入记忆；实验性；不含完整聊天历史 | 官方支持数据导出；本轮未找到同级的官方跨服务记忆导入入口 | 支持 ZIP 导入完整聊天历史；单个 ZIP 最多 5 GB，每日数量和地区／账号受限 |
| 导出 | 可要求 Claude 逐字写出记忆，或使用账号数据导出 | ZIP 数据导出包含聊天历史和账号数据 | Activity 和账号数据体系可导出；本文只比较官方跨服务导入，不展开 Takeout |
| 当前最大优势 | 可维护主题文件 + Chat/Cowork 执行场景联动 + 显式敏感主题控制 | 来源可见、Projects 的 project-only 隔离、成熟的聊天／文件／应用上下文 | 完整聊天历史导入与更广的 Google 数据连接 |
| 当前最大缺口 | 公告与帮助页未同步；Claude Code、完整历史、Skills／自动化和版本历史未纳入承诺 | 记忆摘要不完整暴露；项目记忆无独立条目表；跨服务迁移入口不明确 | 删除和数据用途链条更复杂；账号、地区与表面限制较多 |

## 一手来源

- Claude：[发布公告](https://claude.com/blog/claudes-memory-works-everywhere-and-you-decide-whats-in-it)、[聊天搜索与记忆](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context)、[记忆导入导出](https://support.claude.com/en/articles/12123587-import-and-export-your-memory-from-claude)
- ChatGPT：[Memory and projects](https://help.openai.com/en/articles/8590148-memory-and-projects)、[Projects in ChatGPT](https://help.openai.com/en/articles/10169521-projects-in-chatgpt)、[数据导出](https://help.openai.com/en/articles/7260999-how-do-i-export-my-chatgpt-history-and-data)
- Gemini：[过去聊天记忆](https://support.google.com/gemini/answer/16598469?co=GENIE.Platform%3DDesktop&hl=en)、[聊天与记忆导入](https://support.google.com/gemini/answer/16868299?co=GENIE.Platform%3DDesktop&hl=en)、[Personal Intelligence](https://support.google.com/gemini/answer/16598406?co=GENIE.Platform%3DAndroid&hl=en)

## 对外表达边界

- 不写「Claude 首次支持记忆」或「Claude 记忆全面领先」。
- 可以写「Claude 把可逐项维护的记忆带进 Cowork，并与 Chat 双向连接」。
- 「最突出」「更透明」「迁移更完整」必须绑定具体轴，不做总榜排名。
- Claude 的产品行为在用户实测前归为厂商自报。
