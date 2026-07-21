# 视觉与版权复核

- 复核日期：2026-07-12
- 目标：关闭 `VISUAL-001`，确保正文、框架图和图注统一使用“峰值能力单列 + 四个产品化条件”。
- 结论：6 张 v2 图由项目确定性 Pillow 脚本生成并逐张实看；旧封面、旧时间线、旧公式图和旧 SWE 图已退出正文。用户已于 2026-07-12 确认社交截图与两张官方产品图可用于本篇公众号评论/报道；保留近邻出处，不暗示获得商业授权。

## 当前正文图片

| 图片 | 编辑任务 | 手机阅读检查 | 权利状态 |
|---|---|---|---|
| `assets/cover-v2.png` | 只兑现“用到一半没额度”一个标题钩子 | 大标题分三层，缩略后仍能读出“没额度 / 也白搭” | `project_owned` |
| `assets/claude-reset-tibo.png` | 交代 reset 原文、时间与 Tibo 回复语境 | 原帖正文与回复在窄屏仍可辨；不裁掉上下文 | `user_confirmed_editorial_commentary` |
| `assets/timeline-v2.png` | 区分预定开播、截图时间、24 小时 rollout 与因果边界 | 纵向卡片；JST 只是条件假设，限制在图内写明 | `project_owned` |
| `assets/api-pricing-v2.png` | 给出标准短上下文公开单价并显示口径限制 | 纵向四行；数字字号大，限制不依赖图注 | `project_owned` |
| `assets/usable-intelligence-v2.png` | 峰值能力单列，四条件名称与正文一致 | 纵向 1+4 布局；定义在正文也完整出现 | `project_owned` |
| `assets/benchmark-split-v2.png` | 展示本文选取的六行厂商表为何不能求总胜负 | 每行保留模型配置；底部限制已增加留白 | `project_owned` |
| `assets/swebench-warning-v2.png` | 准确呈现 200/731、249/731 与约 30% 审计结论 | 纵向两张大卡；没有“撤回推荐”等旧错误 | `project_owned` |
| `assets/chatgpt-work-official-web.jpg` | 展示 ChatGPT Work / Codex 统一入口 | 1600×900；正文不依赖它定义入口占有 | `user_confirmed_editorial_use` |
| `assets/chatgpt-work-plugins-official-web.jpg` | 展示统一插件目录 | 1600×900；图注保留官方发布页直链 | `user_confirmed_editorial_use` |

## 退出正文的旧图

| 图片 | 退出原因 |
|---|---|
| `assets/user-cover.png` | 标题堆叠 Tibo、三个词、Benchmark 和额度，违背单一钩子。 |
| `assets/timeline.png` | 把预定开播写成广泛发布、强调精确 61 分钟，并加入无法复核的替代动机。 |
| `assets/user-usable-intelligence-main.png` | 把模型能力塞入公式，缺少“入口占有”。 |
| `assets/user-usable-intelligence-summary.png` | 与主图重复，沿用同一不完整框架。 |
| `assets/user-api-pricing.png` | 内容大体可用，但权利待用户确认；由项目自有 v2 图替代。 |
| `assets/user-benchmark-split.png` | 权利待确认，且配置与限制不如 v2 图完整。 |
| `assets/swebench-warning.png` | 错写“撤回推荐”，并把人工标注口径写得过宽。 |

## 发布前检查

- [x] 用户确认社交截图可作为有出处的评论素材发布，并确认公开账号信息无需额外隐私处理；不暗示获得转载或商业授权。
- [x] 用户确认两张 OpenAI 官方产品图用于本篇公众号编辑内容；继续保留近邻图注和原始链接，不暗示商业授权。
- 在公众号编辑器中做最终手机预览，确认平台二次压缩没有让底部限制文字变糊。

当前使用素材的权利状态已如实复核，`rights_checked: true`。公众号编辑器中的最终压缩预览仍是实际发布前检查，不代表已经执行发布。
