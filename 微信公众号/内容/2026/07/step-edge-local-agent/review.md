# 审校记录

首次审校：2026-07-12
最近审校：2026-07-12

## 当前发布门

| ID | 严重度 | 责任人 | 问题 / 风险 | 通过条件 | 状态 |
|---|---|---|---|---|---|
| TIME-001 | blocker | 证据编辑 | 需证明信息处于 12 小时窗口，并区分官方日期与媒体时点 | 官方页标注 7 月 12 日；IT之家北京时间 11:42:29 距复核时点 8:40:31；正文不把媒体时间当官方时间 | closed |
| FD-TIME-001 | blocker | 主编 / 证据编辑 | 成稿把页面日期标签写成“官方页标注当日发布” | 已精确改为“官方页标注日期为 7 月 12 日”；新版本哈希与命中次数定点复核通过 | closed |
| FACT-001 | blocker | 证据编辑 | `100ms` 容易被误写成全任务延迟 | 正文明确只指本地 toolcall | closed |
| FACT-002 | major | 证据编辑 | 厂商自测可能被写成独立成绩 | 所有相关数字保留“厂商自报 / 内部自测” | closed |
| ARG-001 | major | 主编 | 容易写成 Step Edge 通稿 | 文章以端侧闭环和四问为主轴，产品只做当日触发器 | closed |
| ARG-002 | major | 主笔 | “本地 = 绝对隐私”过度外推 | 写明复杂任务上云，隐私取决于路由与告知 | closed |
| HUMAN-001 | major | 主笔 | 端侧、GUI Grounding、toolcall 等术语密集 | 首次出现即用具体动作翻译，全篇不靠缩写推进 | closed |
| VISUAL-001 | major | 视觉与版权编辑 | 架构图可能照抄厂商图或手机端字太小 | 三张图均为项目原创、已登记并逐张实看；正文不依赖图片定义核心判断 | closed |
| RELEASE-001 | blocker | 独立终审 | 尚未完成零上下文冷读 | 六项复述通过，硬门无 open defect | closed |

## 当前结论

内容包处于 `ready`。事实、视觉权利、内部话术清理与独立冷读均已通过，当前无 open defect；尚未发布。

## 视觉与版权签字（2026-07-12）

- 正文共 3 个 Markdown 图片引用，全部为包内相对路径，文件存在，manifest 登记一致。
- 三张图均由项目脚本确定性生成；未使用厂商 Logo、产品截图、社交截图或外部新闻图，权利状态均为 `project_owned`。
- 架构图依据官方文字信息原创重绘，近邻图注明确来源；`100ms` 限制在图内和正文中同时出现。
- 三张 1080px 宽图已逐张实看，标题、主体卡片、限制文字与图注适合手机纵向阅读。
- 视觉与权利侧同意当前稿设置 `rights_checked: true`；实际发布前仍需在公众号编辑器做最终压缩预览。

---

## 独立发布终审（2026-07-12）

- **角色**：Release auditor
- **方法**：先只读 `draft.md` 的 frontmatter、标题与正文，固定六项冷读复述；之后才读取 brief、argument map、fact sheet、sources、manifest、visual notes、title lab 和旧 review。
- **结论**：没有 unresolved blocker、major 或 minor。事实签字、视觉权利、状态字段与确定性校验均支持推进；HUMAN-002 已定点关闭。**STATUS: pass，可由主编推进到 `ready`。**

### 六项冷读复述

1. **发生了什么**：Step Edge 官方页标注日期为 7 月 12 日；当天北京时间 11:42 已有公开报道。Step Edge 发布的是一套面向端侧 Agent 的 `1 + N` 架构：文本 + 视觉底座连接 Audio、GUI、Gen 三类专用模型，并主张简单任务本地响应、复杂任务上云。
2. **作者主判断**：AI 手机的下一阶段不是把云端聊天模型缩小后塞进设备，而是把本地感知、执行、端云路由和用户控制接成可靠闭环；架构图清楚不等于实机产品已经成熟。
3. **主要证据链**：官方架构、组件分工、`100ms` 本地 toolcall 与端云分工建立事件底座；Apple Foundation Models framework 与 Android 的 Gemini Nano、AppFunctions、ADK、Hybrid 文档证明相关路线并非 Step Edge 首创；离线、跨应用、安全恢复和设备耐力四问把架构转成产品判断。
4. **最强限制 / 替代解释**：`100ms` 只指局部 toolcall，不是整项任务；数据主要来自厂商自测，缺少具体终端、功耗发热、长期稳定性和独立第三方实机验证。公开页“未见披露”也不能外推成产品绝对没有相关机制。
5. **与非专业读者的关系**：读者不必看懂所有模型名和跑分，也能用四问判断一场 AI 手机演示究竟只是会指出按钮，还是能离线、跨应用、可叫停并长期稳定地把事情做完。
6. **末句留下什么**：谁先把本地执行做成用户敢放手的系统能力，谁才真正拿到 AI 手机的入口。

### 冷读与 locked brief 对照

- 冷读复述与 brief 的单一问题、核心判断、四问、最强事实边界和结尾任务一致；没有靠配图才能补出的论证缺口。
- **开头**从“把地址填进打车软件”的具体动作进入，并立即把 Agent 翻译成“理解目标、调用工具、继续下一步的程序”。
- **中段**虽然进入技术与证据边界，但始终回到网络中断、数据外发、权限、点错和手机耐力等具体后果。
- **结尾**明确分开“架构已经发布”与“实机还没交卷”，没有把厂商路线写成已经成熟的产品事实。
- `本轮`、`未见`、`不能`出现较多，但都在限定证据范围；全文没有“这意味着”“换句话说”“值得注意的是”“综上所述”等空转连接，也没有开头网感、中段通稿、结尾口号式的声音断裂。

### 重点风险审计

| 检查项 | 结论 | 证据 |
|---|---|---|
| 12 小时时效口径 | pass | 官方页只写 7 月 12 日，正文没有把 11:42 写成官方时点；11:42:29 至核查时点 19:03 相隔 7:20:31，处于 12 小时窗口、4 小时窗口外。该判断只对 `as_of: 2026-07-12 19:03` 有效。 |
| 是否像 StepFun 通稿 | pass | 产品仅作当日触发器；正文主动写明厂商自测、Apple/Android 先行、权限与实机缺口，主体篇幅用于四问和反证边界。 |
| `100ms` 范围 | pass | 事实卡、架构图图注和耐力段都把它限定为“官方自报的本地 toolcall”，并明确排除整项任务 100ms。 |
| Apple / Android 非首创对照 | pass | 只用一手开发文档证明相关范式此前存在；同时说明接口、权限和测量口径不同，不做榜单或能力等价。 |
| 四问正文闭环 | pass | 离线、跨应用、安全恢复、设备耐力各有独立小节，均包含判断、证据 / 已知机制、限制和读者该追问什么；不依赖四问图。 |
| 架构发布与实机验证 | pass | 结尾逐段区分已确认的技术拼图和仍缺的终端适配、功耗、恢复机制与第三方测试。 |
| 模板语言 / 声音 | pass | 三段声音一致，限定语虽密但承担证据职责；`NPU` 首次出现已补充人话释义，HUMAN-002 关闭。 |

### Gate 1–9

> 分数为审计辅助；硬门以 pass / fail 和缺陷严重度为准。

| Gate | 分数 | 结论 | 本轮证据 |
|---|---:|---|---|
| Gate 1：读者与承诺 | 5/5 | pass | 技术产品架构解释型观点稿；读者、单一问题、本地执行钩子、因果判断和实机边界均明确。 |
| Gate 2：标题与开头 | 5/5 | pass | 标题不堆厂商、模型和跑分；非专业读者可快速复述，开头用具体手机动作兑现。 |
| Gate 3：最小背景 | 5/5 | pass | 60 秒事实卡覆盖 1+N、组件分工、100ms、端云分工和自测边界；未披露的终端范围在后文如实说明。 |
| Gate 4：论证闭环 | 5/5 | pass | “本地接小动作、云端接复杂推理”的框架在前四分之一出现；四问逐项闭环，并处理非首创和实机缺口。 |
| Gate 5：可理解的人话 | 5/5 | pass | 冷读六项完整，三段声音连续，核心术语均用动作解释；`NPU` 首次出现已翻译。 |
| Gate 6：结尾 | 5/5 | pass | 回收标题和可靠闭环；末句是具体产品判断，未引入不受支持的新事实。 |
| Gate 7：事实与来源 | 5/5 | pass | 12 条事实卡和二轮 exact-version 签字完整；厂商自报、行业对照、作者判断和证据缺口分开。 |
| Gate 8：视觉与权利 | 5/5 | pass | 3 张图均存在、登记、`used_in_draft: true`、`project_owned`、允许 WeChat；图注和限制清楚，正文不依赖图片。 |
| Gate 9：状态与校验 | 5/5 | pass | `status: editorial_review`、`fact_checked: true`、`rights_checked: true` 合法且有签字；validator 0 error / 0 warning。 |

### Brief 本轮 8 项发布门

| # | 发布门 | 结论 | 证据 |
|---:|---|---|---|
| 1 | 官方日期、媒体时间与 12 小时窗口分开 | pass | 媒体时点没有冒充官方发布时间；精确间隔和 as-of 已记录。 |
| 2 | 开头 20% 交代 Step Edge 和写作价值 | pass | 开场场景、事件、单一问题和 60 秒事实卡均位于前段。 |
| 3 | `100ms`、自测、端云路由边界准确 | pass | 三处均有明确限定，未外推整项体验或绝对本地。 |
| 4 | 四问逐项在正文解释 | pass | 四个独立小节完整覆盖。 |
| 5 | Apple / Google 只证明趋势，不机械比榜单 | pass | 明确写接口、权限和测量口径不同。 |
| 6 | 结尾区分架构发布和实机待验证 | pass | “已经发布 / 还不能确认”两段对照清楚。 |
| 7 | 图片权利和手机可读性 | pass | 3 张项目原创图、1080px 宽、权利签字与实看记录齐全。 |
| 8 | 独立冷读六项可复述 | pass | 六项答案与 locked brief 一致。 |

### 事实签字版本与抽查

- 当前 `draft.md` SHA-256 为 `6e8dc3e71be68edff8a386ba5f214297ecea0bd674c689393ed6e7b3218d2444`，9579 bytes。
- 事实表签字时预期的 `fact_checked: true` 版本为 `96ab0c6325fe70309e2310105004cf5cd50af02eb5cf163080ec1678da0cddc8`，9568 bytes。对当前文件**只在内存中**把 `status: editorial_review` 还原为签字时的 `status: draft` 后，哈希精确匹配该预期值；再把 `fact_checked` 还原为 `false`，又精确匹配签字前的 `c9f0b88045c59b67f7f5a0b8724d053cb5f178a004a72b26da678d772a6b7a7b`。
- 因此签字后唯一差异是主编推进了工作流状态，正文和事实字段没有额外变化，事实签字有效。
- 审计浏览器可打开 Apple 与 Android 一手页面，内容与 Apple 端侧模型 / 应用内 tool calling、Android 端侧推理和能力调用的正文边界一致。StepFun 与 IT之家直链在本轮审计浏览器被安全层拒绝直接打开；IT之家当前索引仍显示该报道为 11:42，未发现与已签字证据冲突。S-01 / S-03 的事实依据继续由证据编辑的原始页面记录和 exact-version 签字承担。

### 资产、路径、状态与敏感信息

- 正文共有 3 个 Markdown 图片引用，全部为包内相对路径、文件存在、manifest 已登记且 `used_in_draft: true`；不存在 used-flag mismatch、漏登记或 manifest 文件缺失。
- `cover.png` 为 1080×608；`edge-cloud-loop.png` 为 1080×1480；`ai-phone-four-checks.png` 为 1080×1500。三图逐张复看可读，架构图内也明确限定 `100ms`。
- 三图均为 `project_owned`，`allowed_platforms` 含 `wechat`；`rights_checked: true` 与视觉签字一致。
- 对包内 Markdown、YAML 与 Python 文件扫描凭据、私钥、邮箱和绝对个人路径等模式，结果为 `NO_SENSITIVE_PATTERN_MATCHES`。
- `published_url` 为空，符合尚未发布状态；本轮不执行任何外部发布动作。

### Validator

```text
python .agents/skills/self-media-ops/scripts/validate_content_package.py 微信公众号/内容/2026/07/step-edge-local-agent
[ok] content package valid; markdown_images=3 warnings=0
```

### 旧缺陷关闭结论

| Defect ID | 本轮结论 | 状态 |
|---|---|---|
| TIME-001 | 12 小时窗口与官方 / 媒体时间边界准确。 | closed |
| FD-TIME-001 | 缺陷句已替换，正文与签字版本精确匹配。 | closed |
| FACT-001 | `100ms` 全文限定为本地 toolcall。 | closed |
| FACT-002 | 厂商数据明确写成自测，不冒充独立结论。 | closed |
| ARG-001 | Step Edge 只作触发器，文章主轴是端侧闭环和四问。 | closed |
| ARG-002 | 正文写明复杂任务上云，隐私取决于路由与告知。 | closed |
| HUMAN-001 | Agent、端侧、toolcall、GUI 分工均在首次使用附近用动作解释。 | closed |
| VISUAL-001 | 3 张项目原创图已登记、实看并通过权利门。 | closed |
| RELEASE-001 | 独立六项冷读、Gate 1–9 和确定性校验已完成。 | closed |

### 本轮缺陷

| ID | Severity | Owner | 原句 / 位置 | 精确通过条件 | Status |
|---|---|---|---|---|---|
| HUMAN-002 | minor | 主笔 | `draft.md`“手机能不能长期扛住”段：`官方虽然给出了 NPU 自测数据……`；`NPU` 首次出现未翻译。 | 若下一轮仍编辑正文，将首次出现改为类似“手机 AI 加速芯片（NPU）上的自测数据”，且不改变厂商自测与硬件条件未披露的事实边界；由证据编辑定点复核 exact diff。该项不阻断当前 `ready`。 | closed |

定点复核记录（2026-07-12）：`draft.md` 唯一正文改动为 `NPU` → `端侧 AI 加速单元（NPU）`；证据编辑已在新 SHA-256 `8a837eef…` 上签字，确认事实边界未变且 `fact_checked: true` 继续有效，HUMAN-002 关闭。

### 最终建议

- **STATUS: pass。** 无 blocker、无 unresolved major，允许主编把内容包从 `editorial_review` 推进到 `ready`。
- HUMAN-002 已完成定点修复和事实复核；当前无 open defect。后续若再修改正文，必须按工作流重新定点核对事实签字版本。
- 12 小时判断只对 `as_of: 2026-07-12 19:03` 成立。若实际发布时已超过 IT之家 11:42:29 后 12 小时，应重新评估封面“12 小时科技雷达”标签和热点口径。
- 实际发布前仍需在公众号编辑器做最终压缩预览；发布行为继续由用户明确授权。

---

## 全新独立冷读（冻结版本 `974bfff1…`）

- **日期**：2026-07-12
- **冻结 SHA-256**：`974bfff1e71bd08d20dd35a984d5f7b9bd62934bf3a48deb1f67fdd0ed1bc5b8`
- **方法**：本轮重新从零开始，第一阶段只读标题和正文，不读取 brief、fact sheet、sources 或旧 review；冷读判断固定后，才对照三份证据材料。
- **总评**：工作台语言、高风险动作段、限定语、结构过渡和结尾均通过。公司介绍的事实充分、篇幅基本够用，也没有把融资写成产品胜负；但最后一句有轻微融资软文腔，记录为不阻断 `ready` 的 HUMAN-003。

### 第一阶段：零上下文冷读

| 重点 | 结论 | 冷读证据 |
|---|---|---|
| 1. 是否泄漏工作台语言 | pass | 正文已无“本轮核到”“未见披露”“不能断言”“证据编辑”等内部审计话术。`厂商自测`和`内部测试`是在说明评测来源；“发布页没有告诉我们”“不能把……”是面向读者的事实限定，不属于工作台泄漏。 |
| 2. 公司介绍是否自然、够用 | pass with minor | 读者能迅速知道阶跃星辰是谁、不是手机厂商、Step Edge 不是一部手机。成立年份、创始人履历、融资和腾讯跟投已经足够建立背景；`资金和技术班底都不弱、值得看`又替这些事实做了一次正面评价，略像融资材料。 |
| 3. 高风险动作段是否像人话 | pass | “二次确认、能不能撤销、是否留记录、怎么接管”都是具体动作；“也许已有计划，但发布页没告诉我们”既自然又没有把未披露写成绝对不存在。 |
| 4. 限定是否保留但不端着 | pass | `100ms`、厂商自测、上云、权限、模型规模和实机缺口都保留边界；表达改成“没有讲清楚”“现在缺的”“别急着打包看”等自然说法，没有牺牲准确性。 |
| 5. 开头 → 公司背景 → 核心问题 | pass with minor | 地址填入打车软件的场景先建立读者问题，随后用一句新闻交代 Step Edge，再补公司身份并回到核心问题，逻辑可跟随。公司段稍长且末句评价偏满，是唯一轻微节奏风险。 |
| 6. 结尾是否仍成立 | pass | “架构已经发布，实机还没交卷”与全文四问一致；芯片、终端、功耗、安全恢复和第三方实测缺口被再次回收，末句仍落在用户敢不敢放手。 |

### 第二阶段：与 brief、fact sheet、sources 对照

- 当前文件 hash 与 fact sheet 为 `fact_checked: true` 预先计算的 SHA-256 **逐字一致**；冻结版本的事实签字有效。
- `7 月 12 日，阶跃星辰公布了 Step Edge`是日期级表述，没有把 IT之家 `11:42:29` 写成官方发布时间；相对 `20:23` 的 12 小时窗口口径与 brief / sources 一致。
- 公司段的 2023 年、上海、姜大昕履历、2026 年 1 月、超过 50 亿元 B+ 轮和腾讯等老股东继续跟投，均由 S-08 / S-09 交叉支持。
- FACT-013 只允许公司背景回答“它是谁、为什么值得关注”，不能替代产品证据。正文随后明确“产品到底行不行，仍要看实机”，因此没有形成事实越界或通稿式胜负结论。
- 高风险动作、离线清单、独立实机、模型规模和 NPU 条件均使用阶段性缺口表述，没有把“发布材料没说”扩写成“产品绝对没有”。
- `100ms` 仍只指本地 toolcall；Apple / Android 仍只证明路线并非首创；四问和“架构发布≠量产验收”闭环未被公司背景打断。

### 本轮 defect

| ID | Severity | Owner | 精确原句 / 位置 | 替换方向与精确通过条件 | Status |
|---|---|---|---|---|---|
| HUMAN-003 | minor | 主笔 | 开头公司介绍末句：`简单说，这是个资金和技术班底都不弱、正在重押“AI 进入终端”的选手——值得看，但产品到底行不行，仍要看实机。` | 保留 FACT-013 的公司身份、资源规模和“产品仍看实机”，删去或中性化`资金和技术班底都不弱`、`值得看`这类替事实下正面评语的措辞。可沿“这些背景只说明它有资源继续押注 AI+终端，不说明 Step Edge 已经做成；产品行不行，仍要看实机”方向收束。修复后须由证据编辑对 exact diff 定点确认，不得新增技术领先或量产判断。 | closed |

定点关闭记录（2026-07-12）：当前 `draft.md` SHA-256 为 `09790525dea19f92f823002b6bd296da3ad9bb4fa55b917696a324805eb783c3`；公司段末句已改为“公司正在重押‘AI 进入终端’，这条路线能不能走通，还是要看真机。”新句删除了融资与团队的正面背书腔，保留路线判断和真机证据门；开头“场景 → 事件 → 公司身份 → 核心问题”仍顺畅，正文工作台语言扫描无命中。证据编辑已对该冻结版本签字，HUMAN-003 关闭。

### 最新状态

```text
STATUS: pass
BLOCKERS: none
DEFECT_IDS: HUMAN-003 (closed)
FROZEN_HASH: 09790525dea19f92f823002b6bd296da3ad9bb4fa55b917696a324805eb783c3
```

HUMAN-003 已定点关闭；当前无 open defect，仍可由主编推进 `ready`。

---

## 新版语法硬门最终 Release Check（2026-07-12）

- 已按新版 `self-media-ops` 与 `wechat-copyedit-pass.md` 核对精确最终正文。
- `copyedit.md` 当前 frontmatter 为 `status: pass`，检查范围覆盖 title、body、headings、lists、captions、quotes、notes；当前审校明确写明无 open `COPY-*` 缺陷。后文 `needs_fix` 与 COPY-001～COPY-026 均为带 hash 的历史审校记录，已被当前完整复审取代，不属于当前 open defect。
- `draft.md` frontmatter 为 `status: editorial_review`、`fact_checked: true`、`rights_checked: true`、`copyedit_checked: true`。
- `copyedit.md` 的 `body_sha256`、`draft.md` 的 `copyedit_body_sha256` 与 validator 对当前正文重新计算的 hash 三方一致：`760ec409a87e4a1e9d0d3304704ab1f0df59b3ab7f9dee3fc61c8defae7a36a0`。

Hash 门命令与真实输出：

```text
python .agents/skills/self-media-ops/scripts/validate_content_package.py 微信公众号/内容/2026/07/step-edge-local-agent --print-copyedit-hash
[copyedit] body_sha256=760ec409a87e4a1e9d0d3304704ab1f0df59b3ab7f9dee3fc61c8defae7a36a0
```

普通 validator 命令与真实输出：

```text
python .agents/skills/self-media-ops/scripts/validate_content_package.py 微信公众号/内容/2026/07/step-edge-local-agent
[ok] content package valid; markdown_images=3 warnings=0
```

### Release 决定

```text
STATUS: pass
BLOCKERS: none
DEFECT_IDS: none open (COPY-* current pass)
COPYEDIT_BODY_SHA256: 760ec409a87e4a1e9d0d3304704ab1f0df59b3ab7f9dee3fc61c8defae7a36a0
```

新版句级语法硬门、事实门、权利门与普通 validator 均已通过；**允许由主编把内容包从 `editorial_review` 恢复为 `ready`**。任何后续正文改动都会使当前 copyedit hash 失效，届时必须重新跑完整语法终校。
