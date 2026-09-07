# 事实卡

取证截止：2026-08-26。`厂商自报` 表示官方声明的产品行为，尚未在本文作者账号逐项复现；`第三方结果` 只约束到对应用户与样本。

| Claim ID | 原子表述 | 标签 | 来源 | 访问日期 | 可用措辞 | 限制 | 状态 |
|---|---|---|---|---|---|---|---|
| C01 | Anthropic 于 2026-08-25 发布 Claude 新记忆公告 | 事实 | Claude 官方公告 | 2026-08-26 | 「Anthropic 于 8 月 25 日宣布」 | 不据此推断所有账号已到账 | verified |
| C02 | Chat 与 Cowork 开始使用同一套记忆，信息可双向流动 | 厂商自报 | Claude 官方公告 | 2026-08-26 | 「官方称 Chat 与 Cowork 双向共享记忆」 | 帮助中心仍保留旧边界；需账号实测 | verified_with_rollout_caveat |
| C03 | 新记忆会在聊天过程中更新，并保存为可读、可改、可删的短主题文件 | 厂商自报 | Claude 官方公告；聊天记忆帮助页 | 2026-08-26 | 「官方将新记忆描述为实时更新的主题文件」 | 更新时机、冲突处理和版本历史待实测 | verified_with_test_pending |
| C04 | 健康、宗教、政治、性别认同等敏感主题默认不写入记忆，用户可主动打开；部分高敏信息仍排除 | 厂商自报 | Claude 官方公告 | 2026-08-26 | 「敏感主题默认排除，并设显式开关」 | 只对之后产生的记忆生效；实际分类准确性待测 | verified_with_test_pending |
| C05 | Free、Pro、Max 默认开放；Team、Enterprise 由管理员控制且用户初始关闭 | 厂商自报 | Claude 官方公告 | 2026-08-26 | 「官方公布的开放范围是……」 | 可能分批上线；移动端需更新应用 | verified_with_rollout_caveat |
| C06 | 两篇 Claude 帮助页在取证时仍称 Chat 记忆不用于 Cowork | 事实 | 聊天记忆帮助页；Cowork 入门页 | 2026-08-26 | 「帮助页仍保留旧说明，与新公告冲突」 | 「文档更新滞后」只是最可能解释，不是已证实原因 | verified |
| C07 | 删除或让源聊天过期不会自动删除生成的 Claude 记忆条目 | 厂商自报 | Claude 聊天记忆帮助页 | 2026-08-26 | 「源聊天和记忆条目需要分别处理」 | 新系统逐账号 rollout，界面可能不同 | verified_with_test_pending |
| C08 | Claude 提供跨 AI 服务的记忆导入，但不导入完整聊天历史 | 厂商自报 | Claude 记忆导入导出帮助页 | 2026-08-26 | 「导入的是提炼记忆，不是完整历史」 | 官方标记为实验性，可能失败 | verified |
| C09 | ChatGPT 当前使用自动更新的记忆摘要，可查看来源，但摘要不展示记住的全部内容 | 厂商自报 | OpenAI Memory and projects | 2026-08-26 | 「ChatGPT 也已具备自动更新与来源查看」 | 账号、地区与套餐可影响可用性 | verified |
| C10 | ChatGPT Projects 支持 default 与 project-only memory；项目记忆没有独立条目列表 | 厂商自报 | OpenAI Projects in ChatGPT | 2026-08-26 | 「ChatGPT 的项目隔离更明确」 | 旧项目无法事后切成 project-only，需新建项目 | verified |
| C11 | Gemini 可从 ZIP 导入完整聊天历史，单次文件上限 5 GB | 厂商自报 | Google Import chats and memory | 2026-08-26 | 「Gemini 当前能导入更完整的历史」 | 仅部分个人账号／地区；每天文件数量有限 | verified |
| C12 | Gemini 可基于过去聊天和已连接的 Google 应用做个性化 | 厂商自报 | Google Gemini 帮助页 | 2026-08-26 | 「Gemini 的数据面更广」 | Gems、Live、工作／学校账号和地区存在限制 | verified |
| C13 | Cowork 用户在更新前使用 Project Instructions 与 Markdown 文件弥补跨会话失忆 | 第三方结果 | r/ClaudeCowork 讨论 | 2026-08-26 | 「在抽样讨论中，用户已经手工维护外部记忆」 | 单一社区定向样本，不代表总体 | sampled |
| C14 | 一位用户在 Claude 数据导出中观察到按 Profile、Preferences、Topics 组织的记忆文件 | 第三方结果 | r/ClaudeAI 数据导出讨论 | 2026-08-26 | 「一位用户的导出实查显示……」 | 单账号、第三方观察；文件名和结构可能变动 | sampled |
| C15 | 有用户报告旧记忆迁移后被重写或缺失 | 第三方结果 | r/claudexplorers 个案 | 2026-08-26 | 「个别用户报告……」 | 未验证为系统性问题，不可写成普遍故障 | anecdotal |
| C16 | Chat/Cowork 共享记忆使错误上下文更可能进入任务执行 | 推断 | C02、C03 + Cowork 执行场景 | 2026-08-26 | 「这会提高记忆校验的重要性」 | 风险大小取决于任务权限、确认步骤和实际调用方式 | supported_inference |
| C17 | Claude 的突出点是主题可维护性、Chat/Cowork 联动与敏感主题控制的组合，而非每个单项全面领先 | 推断 | C02～C12 | 2026-08-26 | 「Claude 的优势来自组合」 | 若竞品快速更新，比较结论需按 `as_of` 重核 | supported_inference |
| C18 | 平台记忆宜作为便利缓存，关键项目事实仍保存在用户可版本控制的真源中 | 作者判断 | C07、C08、C13～C16 | 2026-08-26 | 明确标为使用建议 | 不是厂商规定，也不是对所有低风险用途的强制要求 | editorial_judgment |
