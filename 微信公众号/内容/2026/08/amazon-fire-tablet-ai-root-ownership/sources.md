# 来源

核验时点：2026-08-24 10:59+09:00。公开正文只保留正常归属与会改变事实含义的限制，核验路径与冲突留在本文件。

| ID | 来源 | URL | 类型 | 访问日期 | 支持表述 | 限制与备注 |
|---|---|---|---|---|---|---|
| S1 | Eric Pardee：Amazon kept shutting down my tablet, so I spent $266 on four AI models to own it | https://ericpardee.github.io/fire-hd-ownership/ | 当事人原文／项目总述 | 2026-08-24 | 购买价格、用途、关机日志、AI 分工与费用、500 多次尝试、root 结果、移除约 100 个包、作者背景 | 主要事实来自作者自述；关机机制只能写日志与处理结果，不能升级为 Amazon 远程下令；Claude Max 的既有订阅费用未计入 266.15 美元 |
| S2 | HANDOFF：CVE-2022-38181 root exploit technical handoff | https://ericpardee.github.io/fire-hd-ownership/HANDOFF.html | 一手技术交接记录 | 2026-08-24 | `KFTRWI`、Fire OS 7.3.2.6、失败路径、GLM-5.2 修复、GLM-5.3 最终解法、root 验证 | 文件标题把设备写成 2019，正文设备 ID `KFTRWI` 对应 2021 年型号；公开稿不复述可执行 exploit 细节 |
| S3 | GitHub Security Lab：GHSL-2022-054 / CVE-2022-38181 | https://securitylab.github.com/advisories/GHSL-2022-054_Arm_Mali/ | 漏洞发现方技术公告 | 2026-08-24 | Arm Mali 驱动 use-after-free、发现者、影响与触发机制 | 证明漏洞本身，不证明作者设备上的最终利用链 |
| S4 | NVD：CVE-2022-38181 | https://nvd.nist.gov/vuln/detail/CVE-2022-38181 | 美国国家漏洞数据库 | 2026-08-24 | 非特权用户可访问已释放内存、受影响 Mali 驱动范围 | 不提供 Fire HD 特定固件是否已修复的结论 |
| S5 | CISA Known Exploited Vulnerabilities Catalog | https://www.cisa.gov/known-exploited-vulnerabilities-catalog?search_api_fulltext=CVE-2022-38181 | 美国政府漏洞目录 | 2026-08-24 | CVE-2022-38181 于 2023-03-30 加入已知被利用漏洞目录，可导致 root 权限提升或信息泄露 | 动态目录；只用于证明它不是 2026 年新发现的零日漏洞 |
| S6 | Amazon Fire Tablet Specifications：Fire HD 10 | https://developer.amazon.com/docs/device-specs/ft-device-specifications-firehd-models.html | 厂商官方规格 | 2026-08-24 | `KFTRWI` 是 Fire HD 10（2021，第 11 代）3 GB 型号；采用 MediaTek MT8183 | 用于解决 S2 标题年份误写；不证明具体购买凭证 |
| S7 | Amazon Source Code Notice for Kindle E-Readers and Fire Tablets | https://digprjsurvey.amazon.com/csad/help/node/200203720 | 厂商官方源码版本列表 | 2026-08-24 | Fire HD 10 第 11 代存在 7.3.2.6 与 7.3.2.9 源码包 | 页面列出的 7.3.2.9 包日期为 2023-11-03，与作者「2024 年 6 月」的表述不一致；正文只写「后续版本已修复」，不写具体月份；该页也不单独证明 CVE 修补内容 |
| S8 | Hacker News 原帖 #49409073 | https://news.ycombinator.com/item?id=49409073 | 社区原帖／动态热度 | 2026-08-24 | 投稿作者 `dr_pardee`；核验时 615 points、266 comments；作者在评论补充设备与模型分工 | 票数和评论数持续变化；公开稿写「超过 600 票、260 多条评论」或在进入 ready 前重查 |
| S9 | 用户本人的 iPhone 经历 | 本轮对话（不外链） | 用户一手经历 | 2026-08-24 | 用户忘记过一次 iPhone 密码，最后由 AI 帮助找到恢复办法 | 密码类型、恢复步骤和数据是否保留均未确认；不能写成 AI 破解或绕过了设备锁 |

## Claim mapping

| Claim ID | 可写事实 | 来源 | 证据类型 | 写作边界 |
|---|---|---|---|---|
| F1 | 作者 2022 年 11 月以 114.26 美元买到一台全新未拆封 Fire HD 10 | S1 | 当事人记录 | 不扩成当时市场普遍售价 |
| F2 | 设备用作 24 小时通电的 Home Assistant 控制面板 | S1 | 当事人记录 | 可解释关机为何影响使用 |
| F3 | 关机始于 2025 年 11 月，日志显示 `Software_Shutdown` | S1 | 当事人日志摘录 | 不写成 Amazon 后台远程下令 |
| F4 | 作者与 Claude 禁用过 5 个持有关机／重启权限的 Amazon 服务；仍有 3 个受保护包无法禁用 | S1 | 当事人技术记录 | 「3 个包导致每次关机」没有逐次因果证明 |
| F5 | 项目约持续 5 个月；Claude 后期受到安全机制限制 | S1 | 当事人记录／产品响应截图 | 不能概括为 Claude 从未参与或美国模型一律拒绝 |
| F6 | Kimi K3 核对固件后选中 CVE-2022-38181，并在约 30 小时、621 条消息中构建工具 | S1、S2 | 当事人记录 + 技术交接 | 「找到」指找到设备上未修补的已知漏洞，不是发现新 CVE |
| F7 | CVE-2022-38181 是 Arm Mali 驱动 use-after-free，2022 年已公开，2023 年进入 CISA KEV | S3—S5 | 原始公告 + 政府目录 | 不称零日漏洞 |
| F8 | 设备为 2021 年第 11 代 Fire HD 10，型号 `KFTRWI`，运行 Fire OS 7.3.2.6 | S1、S2、S6 | 当事人记录 + 厂商规格 | S2 标题年份错误，不引用该标题描述型号 |
| F9 | 作者称后续 7.3.2.9 已修复该漏洞，而他的设备没有升级 | S1、S7 | 当事人二进制核对 + 厂商版本存在性 | 不写修复月份；厂商页面未逐条列出 CVE |
| F10 | Kimi 的 exploit 自动重试，累计超过 500 次，多数失败伴随重启 | S1、S2 | 当事人记录 + 工程日志 | 不是 500 次不同方案 |
| F11 | GLM-5.2 花费 21.90 美元，修复两处致命问题，但又给出后来被推翻的缓存一致性判断 | S1、S2 | 当事人记录 + 技术交接 | 同时保留贡献与错误，不写成单向胜利 |
| F12 | GLM-5.3 在 8 小时 5 分钟内取得 root，并冷重启后在 4 分钟内再次取得 root | S1 | 当事人计时与截图描述 | 可概括为一天内完成；不声称适用于其他固件 |
| F13 | 最终移除约 100 个 Amazon 包，关机问题此后未再出现 | S1 | 当事人结果记录 | 是单设备后续观察，不是受控实验 |
| F14 | 新增明确费用为 Kimi 164.25 美元、GLM-5.2 21.90 美元、GLM-5.3 月订阅 80 美元，合计 266.15 美元 | S1 | 当事人账单汇总 | Claude Max 为既有订阅，不在该合计内；不推算 token 单价 |
| F15 | 作者有 20 年技术从业经历和 InfoSec 背景 | S1 | 作者自述 | 不能称普通零基础用户 |
| F16 | Hacker News 原帖核验时有 615 票、266 条评论 | S8 | 平台原帖动态字段 | 进入 ready 前重开更新；正文可用模糊量级 |
| F17 | 用户忘记过一次 iPhone 密码，最后由 AI 帮助找到恢复办法 | S9 | 用户一手经历 | 不补写密码类型、操作路径、是否保留数据，也不称破解或绕过设备锁 |

## 关键冲突处理

1. S2 标题写「Fire HD 10 2019」，但同一文件给出的型号是 `KFTRWI`。S6 官方规格明确该型号属于 2021 年第 11 代，因此采用 2021 年型号，并在公开稿中不引用错误标题。
2. S1 写 Amazon 在 2024 年 6 月的 7.3.2.9 修复漏洞；S7 官方源码页列出的第 11 代 7.3.2.9 包日期为 2023-11-03。当前无法确认发布日期、分批推送日期或作者所指补丁日期，公开稿只写「后续 7.3.2.9 已修复」。
3. S1 的 `Software_Shutdown`、受保护包权限和移除后稳定共同支持「Amazon 软件与问题相关」。当前没有逐次调用链证明具体哪个包发起每一次关机，因此不写「Amazon 远程故意关机」。

## 使用约束

- 不复制 HANDOFF 中的内存地址、命令、利用链细节或可执行步骤。
- 不把一台旧固件设备的成功扩成「任意人一句话破解任意硬件」。
- 不用 Hacker News 评论作为核心事实来源；只用原帖页记录热度与作者补充。
- 引语只保留「It’s my device」和「You own the device」等极短片段，不复制原文长段。
