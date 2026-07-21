# Image2 生图工作流

版本：1.0

更新日期：2026 年 7 月 21 日

资料属性：internal

## 定位

本文件是项目内 AI 生图与参考图重绘的调用真源。它规定运行时选择、输入合同、质量迭代、内容包回填和降级边界；品牌 Prompt、栏目视觉和保密规则由各项目 adapter 提供。

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
→ 读取内容包视觉任务和权利边界
→ Prompt 路由：通用 Prompt / 品牌 Prompt / 固定风格资产
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

## 输入与工具映射

### 新图生成

- 没有参考图时，只向内置工具传入整理后的 `prompt`。
- 不为普通质量、尺寸或保存路径切换到 API / CLI。

### 参考图重绘或编辑

- 本地参考图均有可访问路径时，先原图检查，再使用 `referenced_image_paths`。
- 至少有一张图只存在于当前对话时，使用能覆盖全部目标图的最小 `num_last_images_to_include`，上限为 5。
- `referenced_image_paths` 与 `num_last_images_to_include` 不能同时使用。
- 参考图不在当前对话或工作区时停止，不凭文字描述伪造「attached image」，请用户重新附图。
- 多张不同用途的成品分别调用；一次调用只承担一个清晰的视觉任务。

Codex CLI 的人工入口可以用自然语言或 `$imagegen`，参考图可通过 `-i` / `--image` 附加。仓库 SOP 约束的是语义合同，不依赖某一版界面参数名。

## 固定风格 Prompt

「笨拙涂鸦重绘」使用 APPSO 本地资产 `appsso-004`：

- 真源：`APPSO-数字资产/01-栏目与品牌/品牌视觉/生图-Prompt/笨拙涂鸦重绘.md`
- 原始 Prompt SHA-256：`6ba5e092a4f8d6fb2bd33602424ba4792715aa59f2bf5f916b90d8bb3f0bbd0a`
- 哈希口径：`## 原始 Prompt` 下 443 个字符的单行英文原文，以 UTF-8 编码；不包含 Markdown 的 `> ` 前缀与行末换行。它不是整个 Markdown 文件的哈希。
- 调用时逐字使用原始英文，不润色、不翻译、不做同义改写。
- 比例、用途、裁切安全区、精确文字和禁用元素作为独立的 `Output constraints` / `Preserve` / `Avoid` 约束追加，不改写风格基底。
- 该 Prompt 是 `internal / local-only` 资产；Git 只保存引用、哈希、调用规则和权利边界，不保存原文。

## 质量迭代

每次生成后都在原尺寸检查，不把「工具已返回图片」当作完成：

- 是否完成该图在正文中的论证任务。
- 参考图的主体关系是否仍可辨认，固定风格要求是否成立。
- 比例、留白、裁切安全区和手机端可读性是否合格。
- 中文、数字、Logo 和界面文字是否准确；不需要文字时是否出现伪文字。
- 是否意外生成第三方标志、真实界面、新闻现场感或其他冒充风险。
- 是否违反输入图的改编权、允许平台或品牌使用边界。

失败时只针对一个主要问题迭代，并重复必须保持不变的约束。文件使用非破坏性版本名，例如 `cover-image2-v01.png`、`cover-image2-v02.png`；选中的最终版本再进入正文，弃稿放入 `research/source-assets/` 或按内容包规则清理。

## 落盘与资产登记

内置工具默认产物可能先位于 Codex 管理目录。项目成品必须复制或移动到目标内容包 `assets/`，不能只保留在临时目录。

AI 生成项至少登记：

```yaml
version: 2
updated: "YYYY-MM-DD"
assets:
  - file: "assets/<name>.png"
    used_in_draft: true
    source_type: "ai_generated"
    source: "<generation task and provenance>"
    creator_or_rightsholder: "This project / AI-generated"
    obtained_on: "YYYY-MM-DD"
    generator: "Codex built-in image_gen"
    model: "gpt-image-2"
    generation_mode: "text_to_image | referenced_edit | image_edit"
    prompt_ref: "appsso-004 or another governed prompt asset"
    prompt_sha256: "<hash of the exact prompt referenced above>"
    generation_constraints: "<ratio, preserve, avoid, text and crop constraints>"
    input_assets: ["research/source-assets/<reference-file>"]
    generated_on: "YYYY-MM-DD"
    modifications: "<iteration and post-processing>"
    rights_status: "<reviewed status>"
    allowed_platforms: ["<platform>"]
    attribution: "AI 生成"
```

`prompt_sha256` 校验 `prompt_ref` 指向的治理 Prompt。对于 `appsso-004`，它必须是本文件记录的固定原文哈希；比例、保留元素、禁用元素、文字和裁切要求单独写入 `generation_constraints`，不能混进风格 Prompt。参考图必须在进入 `ready` 前落到 `research/source-assets/` 并作为独立资产登记；`referenced_edit`、`image_edit` 和 `appsso-004` 禁止使用空 `input_assets`。

参考图的 `rights_status` 必须明确允许制作衍生图，例如 `project_owned`、`user_confirmed_derivative_use`、`licensed_derivative_use`、`cc0_verified` 或 `public_domain_verified`。`user_supplied` 只说明文件从哪里来，`research_reference` 只允许内部核对，两者都不自动授予改编权。只存在于对话中的 `conversation:` / `user_attachment:` 引用可以在草稿阶段保留为警告，但到 `ready` 前必须持久化并登记。输入依赖必须无环；成品不能把自己、自己的路径别名或下游派生图伪装成参考输入。

正文只使用相对路径，并在图片附近保留必要图注。新建或实质编辑的清单使用 `version: 2`：validator 会把正文真实引用与 `used_in_draft` 交叉核对，并对发布权利使用 allowlist；在 `draft` / `editorial_review` 阶段，缺项会产生可见警告；发布绑定图片到 `ready` / `published` 时，缺生成记录、权利未清或平台不匹配会直接失败。旧版清单保持只读兼容，并在下次实质编辑时迁移。

## 降级顺序

1. **默认**：Codex 内置 `image_gen`，已核验为 `gpt-image-2`。
2. **Web adapter**：用户明确要求 ChatGPT Web 特性，且当前 Session 有交互式浏览器和有效登录态；不得索取或保存 Cookie、密码和验证码。
3. **API / CLI adapter**：用户明确要求程序化批量、模型参数或 CLI，并已在本机设置 `OPENAI_API_KEY`；按安装的 `imagegen` skill 执行。
4. **不可用**：工具、额度或参考图阻塞时说明原因；不静默换模型，不把「只交付 Prompt」冒充生图完成。

## 规则合同

```yaml
id: "PROJECT-IMAGE2-001"
trigger: "内容任务需要 AI 新图、参考图重绘或图片编辑"
action: "优先由 Codex 内置 gpt-image-2 直接生成，完成原图检查、定向迭代、落盘和权利登记"
pass_condition: "最终图进入目标 assets，正文使用相对路径，manifest 和视觉门禁完整"
failure_signal: "让用户手动复制 Prompt、参考图不可访问仍生成、未质检、只留临时文件或漏记权利"
scope: "本项目视觉 adapter；品牌 Prompt 与平台尺寸由下级 adapter 提供"
source_cases:
  - "user-feedback:2026-07-21-image2-direct-generation"
  - "user-feedback:2026-07-21-image2-codex-owned-workflow"
regression_check: "下一次含参考图的任务检查运行时、Prompt 哈希、原尺寸复检、迭代记录、路径与 manifest"
classification: "internal"
owner: "visual_rights_editor"
introduced_on: "2026-07-21"
review_on: "2026-08-21"
```
