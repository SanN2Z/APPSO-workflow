# 来源与证据

- 初次访问日期：2026-07-12
- 证据截止：北京时间（UTC+8）2026-07-12 20:23
- 时效窗口：12 小时窗口起点 08:23；优先 4 小时窗口起点 16:23
- 证据原则：技术事实只采用官方一手资料；IT之家只用于页面时间戳交叉核对，不承担性能或产品能力验证；公司背景由两家媒体交叉核对，不把融资规模直接写成技术胜负。

## 来源清单

| ID | 来源 | URL | 类型 | 访问日期 | 支持的事实 | 口径与限制 |
|---|---|---|---|---|---|---|
| S-01 | StepFun：Step Edge | <https://static.stepfun.com/blog/step-edge/> | 官方发布页 | 2026-07-12 | 页面日期；`1 + N` 架构；四个组件及用途；`低至 100ms 本地 toolcall`；简单任务本地、复杂任务上云；推理速度和评测说明 | 厂商一手自报，不是独立实测。页面只标 `2026-07-12`，未给官方发布时间点。 |
| S-02 | StepFun：Step Edge 页面数据脚本 | <https://static.stepfun.com/blog/step-edge/page.js> | 官方发布页公开资源 | 2026-07-12 | 图表模型名称、GUI 模型的 `4B` 标注、NPU 延迟和吞吐数值、对比模型与评测配置 | 仍属厂商发布材料；页面脚本中的图表数值不能脱离正文测试口径使用。 |
| S-03 | IT之家：阶跃星辰发布 Step Edge 端侧模型套件 | <https://www.ithome.com/0/975/681.htm> | 科技媒体 | 2026-07-12 | 页面显示北京时间 `2026/7/12 11:42:29`，用于校准公开传播时间 | 内容主要转述官方；不得用来证明性能、首创性或实机成熟度，也不能把媒体发稿时间写成官方发布时间。 |
| S-04 | Android Developers：Find the right AI/ML solution for your app | <https://developer.android.com/ai/overview> | Google 官方开发文档 | 2026-07-12 | Gemini Nano 端侧推理的离线、隐私和无额外云推理成本；AppFunctions 可让系统级助手发现并调用应用能力；本地与云端能力取舍 | 文档最后更新于 2026-06-17 UTC。只说明 Android 生态能力与行业取舍，不能外推 Step Edge 的性能。 |
| S-05 | Android Developers：Hybrid inference | <https://developer.android.com/ai/hybrid> | Google 官方开发文档 | 2026-07-12 | 本地与云端混合推理；可按网络延迟、设备健康和查询复杂度自定义路由 | 文档最后更新于 2026-06-01 UTC。是 Android 实现参考，不证明 Step Edge 已实现同样的路由、提示或降级机制。 |
| S-06 | Android Developers：Build ADK agents for Android | <https://developer.android.com/ai/adk> | Google 官方开发文档 | 2026-07-12 | ADK Agent 可在 Android 应用内运行；可使用 Gemini Nano 端侧推理并在无网络时运行；本地与云端模型可组成多 Agent 系统 | 文档最后更新于 2026-05-21 UTC。能力发生在 Android 应用与框架边界内，不等于任意系统操作均可执行。 |
| S-07 | Apple Developer：Meet the Foundation Models framework（WWDC25） | <https://developer.apple.com/videos/play/wwdc2025/286/> | Apple 官方开发者视频与逐字稿 | 2026-07-12 | Foundation Models framework 提供 Apple Intelligence 端侧大语言模型；tool calling 可让模型自主调用开发者在应用内定义的代码 | 证明 Apple 在 2025 年已公开端侧模型与工具调用能力；不证明其架构、权限范围或性能与 Step Edge 等价。 |
| S-08 | South China Morning Post：Geely-linked tech veteran Yin Qi joins Chinese AI start-up StepFun as chairman | <https://www.scmp.com/tech/big-tech/article/3341257/geely-linked-tech-veteran-yin-qi-joins-chinese-ai-start-stepfun-chairman> | 媒体 | 2026-07-12 | 阶跃星辰 2023 年成立于上海；由前微软亚洲研究院首席科学家姜大昕创立；2026 年 1 月完成 50 亿元 B+ 轮融资，并强化面向汽车、机器人等终端的 AI 路线 | 公司融资与战略报道，不用于证明 Step Edge 的技术性能或实机成熟度。 |
| S-09 | TechNode：Shanghai AI unicorn StepFun raises over $718 million in B+ round | <https://technode.com/2026/01/26/shanghai-ai-unicorn-stepfun-raises-over-718-million-in-b-round/> | 媒体 | 2026-07-12 | 阶跃星辰是上海大模型创业公司；B+ 轮融资超过 50 亿元人民币；腾讯、启明创投、五源资本等老股东继续跟投；资金用途包含推进 AI + 终端战略 | 融资金额与投资人信息来自媒体报道；资本投入不等于模型能力排名。 |

## 时间核对

- S-01 只能确认官方发布页日期为 `2026-07-12`，不能确认具体时分秒。
- S-03 的页面时间戳为北京时间 `2026-07-12 11:42:29`。相对本轮截止时点 `20:23:00`，相隔 `8 小时 40 分 31 秒`：该媒体报道处于 12 小时窗口内，但不处于优先 4 小时窗口内。
- 允许写：`7 月 12 日，阶跃星辰公布了 Step Edge；当天上午已有公开报道。`
- 禁止写：`阶跃星辰 11:42 发布 Step Edge`、`Step Edge 发布仅 7 小时`。现有证据不能把媒体发稿时间等同于官方发布时间。

## 官方页披露与未披露项

本轮逐项检查 S-01 及 S-02，并在 StepFun 官方域名内检索了补充资料。结论只限定到本轮可见的官方发布材料，不外推为永久或全公司范围的“没有”。

### 已披露

- 架构：一个文本 + 视觉基础模型，连接 Audio、GUI、Gen 三类模型，面向手机和车端硬件落地。
- 局部时延：`低至 100ms` 的对象明确为本地 `toolcall`。
- 端云分工：简单任务本地响应，复杂任务上云。
- GUI 模型：官方图表名称标作 `Step Edge GUI (4B)`。
- Gen 量化与速度：官方称在 `W8A16` 配置下，文生图约 3 秒、图像编辑约 4.5 秒。
- NPU 推理：官方称 1024 token 文本输入约 4.33 秒、768 分辨率图像理解约 5.61 秒、30 秒语音输入约 10.72 秒，预填充吞吐最高 1395 token/s。
- 评测口径：官方明确写明，外部对比模型全部分数为内部自测，并非相应厂商官方报告结果。

### 截至本轮未见披露

- Step Edge 基础模型、Step Edge Audio、Step Edge Gen 的参数规模；`W8A16` 是量化配置，不是参数规模。GUI 的 `4B` 不能套到其他组件。
- 可核对的具体手机/车机上市名单、芯片型号或兼容终端清单。
- 上述速度对应的具体设备、芯片 SKU、功耗模式，以及统一的内存、功耗、发热、续航和长时间稳定性数据。
- GUI Agent 在发送、付款、删除等高风险动作上的确认、撤销、日志、用户接管与失败恢复机制。
- 独立第三方实机测试。S-03 是新闻转述，不是第三方性能实测。

## 使用规则

- Step Edge 的性能数字必须紧邻`阶跃星辰称`、`官方自测`或同等限定语。
- `100ms` 后必须保留`本地 toolcall`，不得改写为完整任务、整次交互或任意手机的响应时间。
- Apple / Google 只用于证明相关能力范式此前已存在，不做榜单或性能横比。
- 对未披露项统一写成`本轮核到的官方发布页及公开页面数据未披露……`，不得写成绝对不存在。
