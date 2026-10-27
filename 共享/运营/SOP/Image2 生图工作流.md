# Image2 生图工作流

Version: 1.6

Updated: 2026-10-27

资料属性：internal

## 定位

本文件是项目内 AI 生图与参考图重绘的调用真源。它规定运行时选择、输入合同、质量迭代、内容包回填和降级边界；品牌 Prompt、栏目视觉和保密规则由各项目 adapter 提供。

适用对象是作者为文章另制的 AI 编辑配图。产品实测中由被测模型生成的关键图、视频、真实抽帧，以及直接保存的产品截图，按实测任务取得并保留真实归属；不为统一文章风格重新生成，也不把其他工具结果冒充被测结果。精确成本或统计图使用标准绘图工具与真实数据。两类素材按[内容包素材合同](../../../.agents/skills/self-media-ops/references/content-package.md)记录任务或数据及渲染来源，不进入 Image2 风格生成流程；发布权利、平台与两类视觉路线要求继续执行。APPSO 视频产品体验的执行入口由品牌 adapter 指向。

## 当前结论

- 默认走 Codex 内置 `$imagegen` / `image_gen`，不再让用户手动复制 Prompt 到 Web 端。
- OpenAI 官方 Codex 文档于 2026 年 7 月 21 日核验：内置生图使用 `gpt-image-2`。当前会话工具不暴露 `model` 参数，是因为模型由内置路径托管，不代表它使用旧模型。
- ChatGPT Web 的 Images 2.0 是可选界面，不是默认必经步骤。只有用户明确要求 Web 端特性，且当前 Session 具备可控的交互式浏览器与有效登录态时，才走 Web adapter。
- `web` 搜索工具只能查资料，不能代替 ChatGPT Web 生图。

核验来源：

- OpenAI Codex 文档：[Image generation](https://learn.chatgpt.com/docs/image-generation)
- OpenAI API 模型页：[GPT Image 2](https://developers.openai.com/api/docs/models/gpt-image-2)
- OpenAI Help Center：[Images in ChatGPT](https://help.openai.com/en/articles/11084440-chatgpt-images-faq)

模型和产品能力会变化。执行器升级后重新核验，不把本次检查结果永久写死为无条件事实。

## 调用架构

```text
用户给出用途与参考图
→ 读取内容包视觉任务、项目 adapter 和权利边界
→ 写入 research/image-generation-plan.json
→ 路由：显式 task 用户覆盖 > 项目 adapter 固化的 package style_policy > 通用 profile
→ 逐阶段执行生图预检，生成临时 tool_request 并写入非敏感 receipt
→ Codex 内置 image_gen（gpt-image-2）
→ 原尺寸视觉检查
→ 单变量定向迭代
→ 最终图回填 assets/ 与 asset-manifest.yml
→ 正文相对路径、图注和发布门禁
```

用户只需要提供：

1. 要制作哪张图，以及它在文章中的作用。
2. 有参考图时附上原图。
3. 必须保留或禁止出现的元素。
4. 已知的比例、尺寸、文字或裁切要求；未给出时由内容包和平台 adapter 补齐。

## 路由与调用前硬门

需要 AI 新图、重绘或编辑的内容包，先创建 `research/image-generation-plan.json`。计划声明 `project_adapter`、每项 `visual_type`、`visual_route`、风格档案引用、参考策略、输出约束和文件路径，不复制 `local-only` Prompt 原文。发布文章的 AI 任务只允许 `clumsy_doodle` 或 `infographic`；网上社区讨论截图、X 截图和官方原图属于 `source_original`，保留原图像素并登记来源，不进入生图计划。明确选择「笨拙涂鸦」时从 `共享/模板/生图计划/笨拙涂鸦直出计划模板.json` 创建；APPSO 任务使用自己的 adapter 模板，其中信息图任务必须走 `appsso-infographic-v1`。计划的 `project_adapter` 必须与 `publish.yml` 的独立声明一致；`appsso-article-v1` 仍作为额外反查，不能作为 Hunt Good 等其他 APPSO 稿型的唯一品牌证据。通用直出与通用参考编辑模板只用于不受三路线文章合同约束的研究资产或用户明确的非文章任务，不能作为微信公众号发布图的默认路线。

路由优先级从高到低为：

1. 用户在当前任务中明确指定并确认的单项覆盖，记录在对应任务的 `style_override`，同时显式指向覆盖 profile 所属 registry。
2. `publish.yml` 声明的项目或品牌 adapter，以及它固化到内容包根 `style_policy` 的默认风格。
3. 没有品牌 adapter 时使用的通用 profile。

根 `style_policy` 是 adapter 解析后的执行记录，不是独立授权源，不能自行压过品牌默认。APPSO 编辑创意图默认使用 `appsso-004`；固定的信息图路线用任务级 `project_visual_route` 绑定 `appsso-infographic-v1`，不属于临时风格发挥。除此之外，只有用户在当前任务明确要求的单项覆盖可以保存 `explicit_current_task_user`、原因与确认日期；覆盖不得扩散到其他任务。固定风格不能与「高质量科技媒体」「干净矢量」「电影感」等相反的正向风格要求同时存在；若确需改变风格，先修改内容包任务并重新预检，不能在工具调用时临时拼接。

确定性 preflight 只能检查结构化合同，不能理解自然语言中的语义矛盾。对本地参考图先做原图检查，逐项对齐参考图的对象数量、顺序、标签与关系，以及计划中的 `purpose`、`preserve` 和 `output_constraints`。例如参考图有 5 个节点而约束写「4 步」，即使脚本通过也必须停止并修正计划。

每次工具调用前执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 image-preflight `
  <content-package-path> --task <task-id> --stage <reference|final> `
  --include-prompt --write-receipt
```

预检负责校验风格档案、原始 Prompt 哈希、生成模式、参考图存在性与改编权、输入绑定、输出位置、路径安全和冲突风格词。只有退出码为 `0` 且 receipt 的 `status` 为 `pass` 时，才能调用生图工具。

`--include-prompt` 的 stdout 会额外返回临时 `tool_request`：它已按当前输入绑定组成 `prompt`、`referenced_image_paths` 或 `num_last_images_to_include`。执行器必须在同一次编排动作中解析 stdout JSON，把 `tool_request` 对象原样传给 `image_gen`；禁止人工复制、摘录或重组 Prompt。当前运行时无法保证这种程序化交接时，必须停止，不允许退回手工输入。`tool_request` 和 `prompt_payload` 只在当次 stdout 存在，receipt 会强制删除两者，不把受控 Prompt 原文落盘。

`reference` 与 `final` 是两个独立调用，必须分别预检。缺少计划、风格档案、合法参考图或通过记录时停止；不静默退回通用风格，也不把预检通过当作图片已经生成。

## 输入与工具映射

### 新图生成

- 通用 profile 明确允许直接生成且没有参考图时，只向内置工具传入预检输出的 `prompt`。
- 先复用已登记且构图任务匹配的本地参考图，包括因风格不符而被否决、但结构仍可用的上一版成图；不为了形式上的「两阶段」重复生成。
- 固定风格要求参考图而当前没有参考图时，采用两阶段策略：先生成仅表达构图关系的内部结构参考图，再以该图作为输入执行固定风格重绘。结构参考图不得作为候选或交付图、不得进入正文。
- 内部结构参考图必须保存到 `research/source-assets/`，以标准 `source_type: "ai_generated"`、`use: "research_reference"` 和明确的 `project_owned` 权利状态登记；随后 `final` 阶段才可消费它。
- `present_to_user: false` 表示「不可当作候选或成品交付」，不代表 Codex 界面一定能隐藏生图工具的返回图。如果当前界面会显示该图，在调用前明确告知用户它只是结构中间件；若生图工具会结束当前响应，`reference` 与 `final` 分两个工具回合执行，不声称在单回合内隐式完成。
- 不为普通质量、尺寸或保存路径切换到 API / CLI。

### 参考图重绘或编辑

- 本地参考图均有可访问路径时，先原图检查，再使用 `referenced_image_paths`。
- 至少有一张图只存在于当前对话时，使用能覆盖全部目标图的最小 `num_last_images_to_include`，上限为 5。
- `referenced_image_paths` 与 `num_last_images_to_include` 不能同时使用。
- 参考图不在当前对话或工作区时停止，不凭文字描述伪造「attached image」，请用户重新附图。
- 多张不同用途的成品分别调用；一次调用只承担一个清晰的视觉任务。
- 固定风格 profile 声明 `requires_reference: true` 时，最终调用禁止 `text_to_image`；必须使用 `referenced_edit` 或档案允许的编辑模式。

Codex CLI 的人工入口可以用自然语言或 `$imagegen`，参考图可通过 `-i` / `--image` 附加。仓库 SOP 约束的是语义合同，不依赖某一版界面参数名。

## 受控风格 Prompt

- 通用 profile 真源为 `共享/运营/SOP/生图风格档案.json`；品牌固定 profile 由对应项目 adapter 的独立 registry 提供。核心层不复制品牌 Prompt 路径、哈希或视觉特征。
- 笨拙涂鸦使用独立 registry `共享/运营/SOP/笨拙涂鸦风格档案.json`，避免新增 profile 改变通用 registry 哈希并让历史生图回执整体失效。
- profile 选中受控 Prompt 时，预检从 registry 读取真源路径、格式、哈希、允许模式和冲突词，并校验本地原文。短 Prompt 使用登记标题下的单行原文；完整设计规范使用 `prompt_format: "full_file"`，逐字把整个 UTF-8 文件作为 Prompt 基底交给 Image2。两种格式都不得润色、翻译、摘要或按记忆重写。
- 比例、用途、裁切安全区、精确文字和禁用元素作为独立的 `Output constraints` / `Preserve` / `Avoid` 追加，不改写风格基底。
- 已由主理人于 2026-09-07 授权打包的 Prompt、规范与 Logo 随私有仓库保存，清单见 `tools/workflow-source-assets.json`；不再要求换机另行导入。计划和 receipt 继续只保留引用与哈希，避免同一原文多处漂移。

### 笨拙涂鸦 profile

- 用户或视觉 brief 明确选择「笨拙涂鸦」时，使用 `clumsy-doodle-v1` 和[《笨拙涂鸦 Prompt 模板》](<../../模板/生图Prompt/笨拙涂鸦-v1.md>)；每项任务只在 `Preserve` 填写「本图只画：一个主体关系 + 一个段落判断」，不得重写风格基底。
- 常规公众号长稿的正文图片总量默认 6–10 张，官方资料图、截图、图表和笨拙涂鸦合计计算。先覆盖关键转折、核心机制、作者经验和结尾判断，不按段落平均配图；已有官方图时相应减少涂鸦。
- 该 profile 只用于明确选中的正文解释图，不自动覆盖品牌 adapter、官方资料图、数据图表、真实界面截图或封面要求。品牌任务需要使用它时，按单项显式用户覆盖记录，不扩散到其他任务。
- 生成后先做原尺寸与手机宽度检查；失败时只修一个主要问题。选中版本后必须在同一交付单元同步 `draft.md`、`asset-manifest.yml` 和最新预览，只生成文件不算交付。

### APPSO 信息图 profile

- `appsso-infographic-v1` 的 Prompt 真源是 `APPSO-数字资产/01-栏目与品牌/品牌视觉/原始资料/Markdown 示意图设计系统规范.md`，按 `full_file` 读取；不得只读速查后自行用 HTML、CSS 或通用科技风重做。
- 每次最终调用都把已登记的「APPSO Logo 红底白字 PNG」作为 `referenced_image_paths` 输入，同时发送完整规范和本图的事实、节点、顺序、数字、来源与限定。Logo 保持原比例和完整红底白字，不抠底、不改色、不拉伸。
- 未另指定尺寸时输出为 1080 × 1440 px 竖图，遵守安全区、6 栏网格、暖白背景、品牌色和页脚。手机显示字号按 APPSO 速查换算并追加到 Output constraints；不能把画布上的 12 px 当作手机上的 12 px。内容超载先拆图。
- 该 profile 只用于 APPSO 公司稿与获授权的 Hunt Good 信息图；个人稿、其他品牌和普通研究资产不得引用公司 Prompt 或 Logo。

## 质量迭代

每次生成后都在原尺寸检查，不把「工具已返回图片」当作完成：

- 是否完成该图在正文中的论证任务。
- 参考图的主体关系是否仍可辨认，固定风格要求是否成立。
- 固定风格的可观察验收标准必须由项目 adapter 提供；成品不满足时判失败，不能只凭 Prompt 哈希放行。
- 比例、留白、裁切安全区和手机端可读性是否合格。
- 中文、数字、Logo 和界面文字是否准确；不需要文字时是否出现伪文字。
- 是否意外生成第三方标志、真实界面、新闻现场感或其他冒充风险。
- 是否违反输入图的改编权、允许平台或品牌使用边界。

失败时只针对一个主要问题迭代，并重复必须保持不变的约束。文件使用非破坏性版本名，例如 `cover-image2-v01.png`、`cover-image2-v02.png`；选中的最终版本再进入正文，弃稿放入 `research/source-assets/` 或按内容包规则清理。

封面等需要用户选版的成图，初次落盘按「候选」处理：`used_in_draft: false`、`used_as_cover: false`、`use: "unused"`，不提前替换 `publish.yml` 的现有绑定。用户明确选中后，在同一次文件更新中：

1. 把 `publish.cover` 或正文图片路径指向新图。
2. 把新图更新为 `used_as_cover: true` / `use: "wechat_cover"` 或对应正文用途。
3. 撤销旧图的发布绑定，保留历史记录。
4. 运行内容包 validator 和发布 dry-run；四项未一次完成时不得进入 `ready`。

## 落盘与资产登记

内置工具默认产物可能先位于 Codex 管理目录。项目成品必须复制或移动到目标内容包 `assets/`，不能只保留在临时目录。

AI 生成项至少登记：

```yaml
version: 3
updated: "YYYY-MM-DD"
assets:
  - file: "assets/<name>.png"
    used_in_draft: true
    visual_route: "clumsy_doodle | infographic"
    source_type: "ai_generated"
    source: "<generation task and provenance>"
    creator_or_rightsholder: "This project / AI-generated"
    obtained_on: "YYYY-MM-DD"
    generator: "Codex built-in image_gen"
    model: "gpt-image-2"
    generation_mode: "text_to_image | referenced_edit | image_edit"
    prompt_ref: "<selected profile id>"
    prompt_sha256: "<hash of the exact prompt referenced above>"
    preflight_receipt: "research/image-generation-runs/<task>-<stage>-preflight.json"
    invocation_prompt_sha256: "<hash of the complete Prompt emitted by preflight>"
    generation_constraints: "<ratio, preserve, avoid, text and crop constraints>"
    input_assets: ["research/source-assets/<reference-file>"]
    generated_on: "YYYY-MM-DD"
    modifications: "<iteration and post-processing>"
    rights_status: "<reviewed status>"
    allowed_platforms: ["<platform>"]
    attribution: "AI 生成"
```

`prompt_sha256` 校验 `prompt_ref` 指向的治理 Prompt，并与所选 registry 一致；比例、保留元素、禁用元素、文字和裁切要求单独写入 `generation_constraints`，不能混进风格 Prompt。参考图必须在进入 `ready` 前落到 `research/source-assets/` 并作为独立资产登记；`referenced_edit`、`image_edit` 和任何声明 `requires_reference: true` 的 profile 禁止使用空 `input_assets`。

每个 version 3 AI 资产都应在 `research/image-generation-runs/` 保存对应阶段的 preflight receipt，并在 manifest 引用它、记录 `visual_route` 与 `invocation_prompt_sha256`。发布校验会复算计划、profile registry 与本地输入文件哈希，并核对输入权利和顺序；Prompt、计划、registry、模式、约束、输入内容或输出任一变化，都必须重新预检并废弃旧 receipt，最小手写记录不能替代真实 preflight。

参考图的 `rights_status` 必须明确允许制作衍生图，例如 `project_owned`、`user_confirmed_derivative_use`、`licensed_derivative_use`、`cc0_verified` 或 `public_domain_verified`。`user_supplied` 只说明文件从哪里来，`research_reference` 只允许内部核对，两者都不自动授予改编权。只存在于对话中的 `conversation:` / `user_attachment:` 引用可以在草稿阶段保留为警告，但到 `ready` 前必须持久化并登记。输入依赖必须无环；成品不能把自己、自己的路径别名或下游派生图伪装成参考输入。

正文只使用相对路径，并在图片附近保留必要图注。新建或实质编辑的清单使用 `version: 3`：validator 会把正文真实引用与 `used_in_draft`、`visual_route` 交叉核对，并对发布权利使用 allowlist；在 `draft` / `editorial_review` 阶段，缺项会产生可见警告；发布绑定图片到 `ready` / `published` 时，缺生成记录、权利未清、平台不匹配、路线合同错误或微信公众号文章不足 2 类视觉路线都会直接失败。旧版清单保持只读兼容，并在下次实质编辑时迁移。

## 降级顺序

1. **默认**：Codex 内置 `image_gen`，已核验为 `gpt-image-2`。
2. **Web adapter**：用户明确要求 ChatGPT Web 特性，且当前 Session 有交互式浏览器和有效登录态；不得索取或保存 Cookie、密码和验证码。
3. **API / CLI adapter**：用户明确要求程序化批量、模型参数或 CLI，并已在本机设置 `OPENAI_API_KEY`；按安装的 `imagegen` skill 执行。
4. **不可用**：工具、额度或参考图阻塞时说明原因；不静默换模型，不把「只交付 Prompt」冒充生图完成。

## 规则合同

```yaml
id: "PROJECT-IMAGE2-001"
trigger: "内容任务需要 AI 新图、参考图重绘或图片编辑"
action: "先按显式 task 用户覆盖、项目 adapter 固化的 package style_policy、通用 profile 的顺序路由并逐阶段预检，再由 Codex 内置 gpt-image-2 生成，完成原图检查、定向迭代、落盘和权利登记"
pass_condition: "调用前 plan 与 receipt 通过；最终图进入目标 assets，正文使用相对路径，manifest 和视觉门禁完整"
failure_signal: "固定风格被通用风格覆盖、缺参考图仍直接出最终图、未预检、让用户手动复制 Prompt、未质检、只留临时文件或漏记权利"
scope: "本项目视觉 adapter；品牌 Prompt 与平台尺寸由下级 adapter 提供"
source_cases:
  - "user-feedback:2026-07-21-image2-direct-generation"
  - "user-feedback:2026-07-21-image2-codex-owned-workflow"
  - "user-feedback:2026-07-22-governed-style-routing-regression"
  - "hunt-good-2026-08-21:FB-006"
  - "tibo-codex-recursive-self-improvement:FB-005"
regression_check: "正例检查笨拙涂鸦按固定风格生成、APPSO 信息图把完整规范与登记 Logo 同时传入 Image2；反例检查通用科技 3D、只读规范不进工具输入、缺 Logo、冲突风格词与未授权参考图均在调用前或 ready 门失败"
classification: "internal"
owner: "visual_rights_editor"
introduced_on: "2026-07-21"
review_on: "2026-08-21"
```
