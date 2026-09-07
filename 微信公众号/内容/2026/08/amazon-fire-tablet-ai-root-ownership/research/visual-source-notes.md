# 视觉素材记录

核验日期：2026-08-24。

## 任务

- 原创封面：使用 `clumsy-doodle-v1`，表现「买下设备后仍要夺回控制权」，不做价格图表。
- 原创正文图：使用 `clumsy-doodle-v1`，分别表现权限墙、4 个 AI 依靠同一份文件接力、500 多次重启。
- 资料图：正文使用 Amazon 官方设备图、作者原文中的 Claude 拒绝截图和 Hacker News 网友评论原始网页截图。
- 数量：正文 6 张图，封面候选另计 1 张。
- 权利边界：外部图只用于本内容包的署名编辑评论预览，不视为一般转载许可；稿件维持 `rights_checked: false`，用户复看前不进入 `ready`。

## 正文接入原则

- 封面候选生成后由用户选定，再建立 `publish.yml` 和正式封面绑定。
- 正文图按信息任务分布，不按段落平均插图。
- 官方图与作者截图保留来源和图注；网友评论截图只截一条短评，保留 HN 原始样式、用户名、时间和上下文入口。

## 已收集候选

| 文件 | 类型 | 信息任务 | 当前判断 |
|---|---|---|---|
| `amazon-fire-hd10-2021-spec-official.png` | Amazon 官方产品图 | 让读者看到 2021 款 Fire HD 10 的外观 | 已复制到 `assets/` 并接入正文，保留 Amazon 署名 |
| `amazon-fire-hd10-2021-blog-official.jpg` | Amazon 官方发布图 | 提供横向版设备图片 | 与规格图重复，优先级较低；转载边界待确认 |
| `author-kimi-working-bug.png` | 作者原文截图 | 记录 Kimi 找到可用漏洞后的状态 | 含利用链和命令，只留研究区，不原样发布 |
| `author-claude-cyber-refusals.png` | 作者原文截图 | 记录 Claude 两次触发 cyber 安全限制 | 原图保留在研究区；因手机宽度不可读，正文改用只摘两句原文的可读引文卡 |
| `author-glm53-root-verified.png` | 作者原文截图 | 记录 8 小时 5 分钟后 root 成功 | 含可执行命令，只留研究区，不原样发布 |
| `author-openrouter-card-declined.png` | 作者原文趣味截图 | 记录预算消耗期间银行卡被拒 | 当前正文没有这条支线，暂不使用 |
| `hn-comment-fame-promise-49409832.png` | Hacker News 重排短评卡 | 网友调侃「承诺上 HN 就能让模型破解硬件」 | 退出正文；它是项目重排卡，不是用户要求的原始评论截图 |
| `hn-comment-fame-promise-49409832-screenshot.png` | Hacker News 原始网页截图 | 同一条 Shuddown 顶层评论 | 已从完整讨论页按评论 ID 截取，复制到 `assets/` 并放在 AI 账单之后；只裁评论节点，不改网页内容 |
| `hn-comment-iphone-jailbreak-49409918.png` | Hacker News 短评卡 | 网友期待 AI 带回 iPhone 越狱 | 退回研究候选，不再放在用户 iPhone 例子之前，避免打断结尾 |

原始图片、短评来源、尺寸、哈希和权利状态见 `asset-manifest.yml`。

## 原创图结果

| 文件 | 用途 | 质检结果 | 使用状态 |
|---|---|---|---|
| `assets/cover-ownership-doodle-v01.png` | 微信封面候选 | 约 2.35:1；白底、大色块、硬像素边；人物、锁、钥匙和 4 个机器人在中心裁切区内 | 等用户确认后再建立封面绑定 |
| `assets/doodle-ownership-wall-v01.png` | 权限墙解释图 | 1 个买家、1 堵带锁的墙和墙后 3 个红色软件包清楚；无文字或品牌 | 已接入正文 |
| `assets/doodle-four-ai-handoff-v01.png` | 4 个 AI 交接图 | 第二次生成；4 个机器人只传递 1 份文件，最后一棒拿着钥匙；无文字或品牌 | 已接入正文 |
| `assets/doodle-reboot-grind-v01.png` | 反复重启解释图 | 疲惫的人、仍上锁的平板和失败纸团堆在手机宽度可辨 | 已接入正文 |

4 张 AI 图均已完成原尺寸检查。正文 6 张图与封面候选均已按 390 像素宽度检查；Claude 原截图因不可读被替换，其余交付图通过。

## 弃稿

- 上一版 `generic-direct-v1` 的纸黏土封面与正文图已移到仓库忽略的 `.tmp/amazon-fire-rejected-visuals-20260824/`，不再参与预览。
- 第一张笨拙涂鸦交接图把一份交接文件画成了三份，已移到同一临时弃稿区。第二次生成修正了这一关系。
- Claude 原始截图的发布副本在 390 像素宽度下只有 83 像素高，文字不可读；已改为 `assets/author-claude-cyber-refusals-card.png`，原始截图仍留在研究区。
- 原 iPhone 越狱评论卡的发布副本已移到同一临时弃稿区；研究原件与来源登记仍保留。
- Shuddown 评论的重排卡发布副本也已移到临时弃稿区，正文改用原始网页截图；重排卡研究原件仍保留。
