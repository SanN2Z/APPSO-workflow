# 来源与证据

- 初次访问日期：2026-07-13
- 证据截止：北京时间（UTC+8）2026-07-13 14:27
- 适用范围：`微信公众号/内容/2026/07/apple-m7-ultra-local-ai-memory/`
- 证据原则：M7 Ultra 路线图属于 Mark Gurman / Bloomberg 的记者爆料，不写成 Apple 公告；Apple 与 MLX 官方资料用于解释现有产品和统一内存，不反向证明爆料为真；容量、性能和最终上市配置分别核对。

## 来源清单

| ID | 来源 | URL | 类型 | 访问日期 | 支持的事实 | 口径与限制 |
|---|---|---|---|---|---|---|
| S-01 | Mark Gurman / Bloomberg：*Apple’s M6, M7 and M8 Chips Show How AI Is Reshaping the Company* | <https://www.bloomberg.com/news/newsletters/2026-07-12/apple-s-chip-plans-m6-m7-pro-m7-max-m7-ultra-m8-details-touch-macbook-pro> | 记者报道 / 一手爆料载体 | 2026-07-13 | M7 系列路线图；M7 Ultra 按最高 1.5TB 内存支持能力设计；是否实际提供取决于行业状态；M7 Ultra 目标年份为 2028 | 不是 Apple 公告。正文受订阅墙和 robots 限制，本轮用作者原始 X 帖及 Techmeme 聚合页核对关键原文；不得把设计上限写成已定 SKU。 |
| S-02 | Mark Gurman 原始 X 帖：Power On 路线图入口 | <https://x.com/markgurman/status/2076305950634279381> | 记者本人原始社交帖 | 2026-07-13 | 原文：`Power On: Apple's Mac chip shake-up around the M6, M7, M7 Pro, M7 Max, M7 Ultra and M8 show how AI is continuing to reshape the company. New details on Apple's chip plans.`；发帖时间 | X Snowflake 解码为 UTC `2026-07-12 14:01:29.187`，即北京时间 `2026-07-12 22:01:29.187`。Snowflake 只锁定创建时间，不替代正文事实核查。 |
| S-03 | Mark Gurman 原始 X 帖：1.5TB 条件句 | <https://x.com/markgurman/status/2076306380583997665> | 记者本人原始社交帖 | 2026-07-13 | 原文：`The M7 Ultra is designed to support as much as 1.5 terabytes of memory — double the capacity planned for the M5 Ultra — though whether Apple ultimately offers that configuration will depend on the state of the industry.`；发帖时间 | X Snowflake 解码为 UTC `2026-07-12 14:03:11.695`，即北京时间 `2026-07-12 22:03:11.695`。关键词必须保留 `designed to support`、`as much as` 和最终配置条件。 |
| S-04 | Mark Gurman 原始 X 跟帖：当前内存环境 | <https://x.com/markgurman/status/2076336190400123362> | 记者本人原始社交帖 | 2026-07-13 | 原文：`This would match the 2019 Mac Pro, of course, if it's able to actually happen in the current memory environment.` | 北京时间 `2026-07-13 00:01:38.909`。只支持“当前内存环境可能阻碍配置落地”，不能单独证明具体供应量或价格。 |
| S-05 | Techmeme 01:35 ET 归档入口 | <https://www.techmeme.com/260713/h0135> | 新闻聚合快照 | 2026-07-13 | 目标快照时点；当时头条聚合标题 | 2026-07-13 的 ET 为 EDT（UTC−4），因此 `01:35 ET` = 北京时间 `13:35`。本环境直开该精确归档入口返回 403；标题通过同一时段相邻快照和永久聚合页核对，精确 01:35 页面渲染仍列为证据缺口。 |
| S-06 | Techmeme：Bloomberg 报道永久聚合页 | <https://www.techmeme.com/260712/p6> | 新闻聚合页 | 2026-07-13 | 聚合标题：`Sources: Apple is already taping out M7 with major NPU upgrades, and plans M7 Ultra with 1.5TB RAM, and M8, for 2028; new Pencils are coming with a new iPad Pro`；汇集 S-02～S-04 原帖 | Techmeme 是聚合编辑标题，不是 Bloomberg 原文，更不是 Apple 表述。`1.5TB RAM` 是标题压缩，正文必须恢复 S-03 的条件句。 |
| S-07 | 9to5Mac：M7 Ultra 1.5TB 报道 | <https://9to5mac.com/2026/07/12/m7-ultra-mac-studio-to-support-up-to-1-5-tb-unified-memory/> | 二手媒体 / 原文摘录 | 2026-07-13 | 完整转录 Bloomberg 的 1.5TB 条件句；补充转录：`Widespread memory-chip shortages have made the component harder to find and more expensive.` | 只用于弥补 Bloomberg 订阅墙下的原文可见性；仍应归因 Gurman / Bloomberg。其价格推算、评论和标题不能当产品事实。 |
| S-08 | 9to5Mac：M7 Ultra Mac Studio 路线图 | <https://9to5mac.com/2026/06/28/m7-ultra-mac-studio-coming-in-2028-after-m5-ultra-model-later-this-year/> | 二手媒体 / Bloomberg 摘录 | 2026-07-13 | 转录此前 Gurman 报道：`There are two Mac Studio updates in Apple’s pipeline: an M5 Ultra version due this year and an M7 Ultra update targeted for 2028.` | 这是与 7 月 12 日 1.5TB 爆料分开的较早路线图信息。可以并列交代，不能合并成“2028 年必售 1.5TB Mac Studio”。 |
| S-09 | Apple Newsroom：2025 Mac Studio 发布稿 | <https://www.apple.com/newsroom/2025/03/apple-unveils-new-mac-studio-the-most-powerful-mac-ever/> | Apple 官方发布稿 | 2026-07-13 | M3 Ultra Mac Studio 可配置至 512GB；超过 800GB/s 内存带宽；Apple 称可运行 600B+ 参数 LLM 且 entirely in memory | 厂商自报，不是独立测试。发布稿原文是 `capable of running ... entirely in memory`，不是 `can fit entirely into memory`；引用时不得擅自换成“所有 600B+ 模型都装得下/都跑得快”。 |
| S-10 | Apple Newsroom：M3 Ultra 发布稿 | <https://www.apple.com/newsroom/2025/03/apple-reveals-m3-ultra-taking-apple-silicon-to-a-new-extreme/> | Apple 官方发布稿 | 2026-07-13 | 统一内存从 96GB 起、可配置至 512GB；Apple 称 600B+ 参数 LLM 可直接在设备上运行；列举 3D、视觉特效和 AI 等大内存负载 | 厂商自报。它还把容量和 `over 800GB/s` 带宽分开列出，可用于说明“容量不是速度的同义词”，但不能推导 M7 Ultra 的带宽。 |
| S-11 | MLX 官方文档：Unified Memory | <https://ml-explore.github.io/mlx/build/html/usage/unified_memory.html> | Apple MLX 官方技术文档 | 2026-07-13 | Apple silicon 的 CPU 与 GPU 可直接访问同一内存池；MLX 数组无需在 CPU/GPU 内存位置之间搬移即可由两者执行操作 | 结论限定在 Apple silicon 与 MLX 的内存模型。不能扩大为“所有软件零拷贝”“整机标称容量全部无条件供 GPU 使用”或性能保证。 |
| S-12 | MLX 官方 GitHub 仓库 | <https://github.com/ml-explore/mlx> | Apple 开源项目官方仓库 | 2026-07-13 | MLX 数组位于 shared memory；CPU/GPU 操作无需转移数据；MLX 当前支持 CPU 与 GPU | 与 S-11 交叉核对；仍是框架设计说明，不是 M7 Ultra 产品规格。 |
| S-13 | Apple Developer WWDC26：*Run local agentic AI on the Mac using MLX* | <https://developer.apple.com/videos/play/wwdc2026/232/> | Apple 官方开发者视频与逐字稿 | 2026-07-13 | 全本地 Agent 栈；Agent 会话通常达数十万 token；某些模型单台 512GB Mac 仍装不下；Apple 举例称最近的 DeepSeek 模型有 1.6T 参数，仅权重就需 800GB 以上 | Apple 技术演讲中的官方说明和演示，不是第三方基准。`the most recent DeepSeek model` 未在逐字稿中给出具体版本；800GB 只指 weights，不含 KV cache、运行时和系统余量；不能用于证明 M7 Ultra 或 1.5TB SKU 的速度。 |

## 时间换算与传播链

| 事件 | 原始时区/时间 | 北京时间（UTC+8） | 证据 |
|---|---|---|---|
| Gurman 发布 Power On 路线图帖 | UTC `2026-07-12 14:01:29.187` | `2026-07-12 22:01:29.187` | S-02；由 X Snowflake ID 解码 |
| Gurman 发布 1.5TB 条件句 | UTC `2026-07-12 14:03:11.695` | `2026-07-12 22:03:11.695` | S-03；由 X Snowflake ID 解码 |
| Gurman 补充“当前内存环境” | UTC `2026-07-12 16:01:38.909` | `2026-07-13 00:01:38.909` | S-04；由 X Snowflake ID 解码 |
| 指定 Techmeme 快照 | EDT `2026-07-13 01:35` | `2026-07-13 13:35` | S-05；7 月美国东部采用 UTC−4 |

## 原文锁定

### M7 Ultra 1.5TB

S-03 的关键句必须按以下语义翻译：

> M7 Ultra 的设计目标是支持最高 1.5TB 内存——约为计划中的 M5 Ultra 容量两倍；但 Apple 最终是否提供这一配置，将取决于届时行业状况。

这里的`设计目标/设计上支持`、`最高`和`最终是否提供`缺一不可。S-07 进一步转录 Bloomberg 对行业状况的解释：广泛的内存芯片短缺使该元件更难获得、价格更高。

### Apple 600B+ 表述

S-09 的准确原文为：

> `Mac Studio is a powerhouse for AI, capable of running large language models (LLMs) with over 600 billion parameters entirely in memory, thanks to its advanced GPU and up to 512GB of unified memory with M3 Ultra.`

因此中文可写`Apple 官方称，M3 Ultra Mac Studio 凭借最高 512GB 统一内存，可让超过 6000 亿参数的 LLM entirely in memory 运行`。不要把`LLMs with over 600 billion parameters can fit entirely into memory`放进英文引号冒充 Apple 原句。

### WWDC26 容量实例

S-13 逐字稿的关键边界为：

- `Agentic sessions usually comprise hundreds of thousands of tokens and most of those are not generated.`
- `Sometimes a single machine, even one with 512GB of RAM, just isn't enough because the model is too large to fit in memory.`
- `The most recent DeepSeek model for instance has a whopping 1.6 trillion parameters and requires more than 800GB of memory just for the weights.`

允许把它用作`为什么大容量统一内存对本地大模型/Agent 有实际意义`的官方实例；禁止把它写成 M7 Ultra 已完成 1.5TB 实机验证、性能测试或发布承诺。

## 本轮明确缺口

- Apple 尚未在已核官方页面确认 M7 Ultra、1.5TB 配置、发布日期或对应整机。
- 爆料没有锁定最终可售内存档位、售价、内存带宽、推理吞吐、GPU/NPU 规模、整机功耗、散热设计和持续负载表现。
- `1.5TB` 是容量上限信息，不包含模型精度/量化方式、KV cache、上下文长度、并发、框架开销和系统预留。
- Techmeme `2026-07-13 01:35 ET` 精确归档 URL 在本环境返回 403；相邻时点与永久聚合页的头条一致，但若文章必须声称“01:35 页面截图所见”，发布前应由可访问浏览器人工再开 S-05 一次。
