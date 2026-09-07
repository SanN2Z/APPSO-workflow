# WeChat preview and draft workflow

Use the pinned open-source [Wenyan CLI](https://github.com/caol64/wenyan-cli) for Markdown rendering, inline image uploads, permanent cover upload, and WeChat `draft/add`. Do not maintain a separate renderer or WeChat API client in this project.

The project-owned adapter at `微信公众号/tools/wechat_publish.py` only:

- maps `draft.md` plus `publish.yml` to Wenyan frontmatter;
- removes the editorial-only leading H1 so the platform title is not duplicated;
- maps an allowlisted layout profile to a versioned repository CSS file;
- injects rights-cleared package-local body header/footer components without changing `draft.md`;
- runs the existing content-package validator, then audits the actual Wenyan-rendered image/resource graph;
- seals one hash-matched input snapshot and one unique build directory for every run;
- produces a phone-width local preview;
- keeps the default draft command as a no-network dry-run.

## 默认预览交付

主理人绑定设置（2026-09-05，`FEISHU-PREVIEW-20260905`）：本仓库稿件默认直接交付飞书在线文档链接，在飞书里预览和协作。使用当前已经连通并获得相应权限的飞书 MCP，新建文档或按本次要求修改指定文档；写入后读取并核对标题、正文与图片，再返回链接。普通飞书预览不以生成或打开本地 HTML 为前置步骤。

本地 `draft.md` 和登记素材继续作为写作来源；公众号最终排版、样式保真验收或用户明确要求本地预览时，才进入下文的 HTML／Wenyan 路线。飞书协作预览不承诺像素级复刻公众号 CSS。原 `$company-content-sync` 封存流程保留给需要精确公众号样式凭据的交付，不作为普通飞书预览的必经入口。

连接器、账号权限或目标目录缺失时，明确报告阻塞，不声称已经上传，也不自动改交 HTML。用户已明确要求的飞书稿件交付按该任务继续执行；配置 MCP 本身不触发上传、覆盖或删除现有文档。已有文档更新前先读取当前内容，保留编辑者修改并按本次要求选择范围；无法确认冲突时先新建版本。飞书工具未提供的整篇删除能力不得用清空正文冒充。

来源与复核见 [飞书默认预览配置记录](../../../../共享/运营/复盘/2026-09-05-飞书默认预览配置.md)。

## One-time setup

From the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/bootstrap.ps1
```

The bootstrap creates a clone-local `.venv`, restores exact Python pins, and runs `npm ci` against the tracked lockfile. It does not create credentials. Only when the current task actually needs `draft --execute`, copy `微信公众号/.env.example` to `微信公众号/.env` locally and fill `WECHAT_APP_ID` and `WECHAT_APP_SECRET`. `draft --execute` rejects a missing or ambiguous credential file, removes ambient WeChat credentials and Node injection variables from the child process, and prints only a 12-character SHA-256 fingerprint of the selected AppID. Confirm that non-secret fingerprint against the intended account before proceeding. Never paste the secret into chat, a draft, logs, or committed files. `.env`, Wenyan token/material caches, and generated preview artifacts are ignored by Git.

The WeChat account must expose the required material and draft APIs. The machine's public egress IP must be allowed in the Official Account developer configuration, unless a separately reviewed fixed-egress deployment is used.

## Per-article configuration

Create `publish.yml` in the content package:

```yaml
title: "API title, at most 32 characters"
author: ""
digest: "Feed summary"
cover: "assets/cover.png"
source_url: ""
project_adapter: "generic"
delivery_mode: "manual_editor"
theme: "default"
layout_profile: "default"
highlight: "solarized-light"
mac_style: false
footnote: true
need_open_comment: false
only_fans_can_comment: false
header_image: ""
header_alt: ""
footer_image: ""
footer_alt: ""
footer_valid_until: ""
```

The cover must exist inside the package, be registered in `asset-manifest.yml` with `use: "wechat_cover"` or `used_as_cover: true`, allow `wechat`, and have a resolved rights status. Do not use an unresolved paper figure or screenshot as the cover merely to satisfy the API.

## 仓库交付模式与公司执行通道

`project_adapter`、`delivery_mode` 和 `layout_profile` 是三个独立声明字段：前者声明品牌归属，中间字段决定仓库工具提供哪种交接能力，最后一个字段只选择仓库视觉主题。新内容包和任何再次交付的旧内容包都必须显式填写 `delivery_mode`；缺失字段的旧包只能兼容预览，不能创建交接稿或 API 草稿。

仓库发布适配器仍只实现 `manual_editor` 与 `sealed_draft` 两种 `delivery_mode`。公司提供的浏览器扩展属于单独的 `execution_route`：它不由 `publish.yml` 或 `wechat_publish.py` 自动调用，实际使用情况写入 `publish-record.md`。这样可以保留现有验证和降级能力，又不会把依赖浏览器 DOM 的直接写入伪装成哈希密封草稿。

### 人工编辑交接模式

稿件粘贴到公众号后台后还要调整字号、段距、缩进、对齐或图片时，使用：

```yaml
delivery_mode: "manual_editor"
theme: "default"
layout_profile: "default"
mac_style: false
```

Wenyan 仍负责 Markdown 与本地图片渲染。适配器先在 Markdown token 层阻断作者手写的表现层、隐藏或交互 HTML，再在原始渲染结果上检查图片和 APPSO 头尾组件，最后按文章语义标签与逐标签属性 allowlist 清理 HTML：删除 `style`、`class`、`data-*`、`width`、`align` 等表现层属性，展开 `font`、`center` 和无语义的空属性 `span`；`hidden`、`contenteditable`、`template`、`dialog` 等隐藏或交互标记直接阻断，不静默改写。标题、段落、强调、链接、图片、替代文本、图注和正文中作为文字出现的 `style="..."` 保持不变。构建会生成版本化的 `dist/handoffs/handoff-*/wechat-handoff.html`、结构化 `wechat-content.html`、实际复制输入 `wechat-copy-payload.html` 和配套 `assets/`；复制入口是 `wechat-handoff.html` 的「复制正文」按钮。预览页和交接页可以用页面级 CSS 约束大图，但这部分 CSS 不进入复制正文。

该模式只做本地交接，`handoff` 命令不访问网络，`draft` 与 `draft --execute` 均必须 fail loud。交接计划封存复制页、结构正文、复制输入和每张本地图的 SHA-256；`handoff --open` 会在调用浏览器前以限长稳定读取重新校验，届时检测到任一产物被替换、修改或异常膨胀都会阻断打开。浏览器打开后的文件或 DOM 状态不在这次校验的封存范围内。内容包快照采用分块稳定复制，发布图片在暂存前执行单图和累计字节上限；计划还记录图片尺寸、字节数、帧数、出现顺序和复制载荷体积，并在 Base64 编码及复制前再次执行资源上限。若图片没有随正文粘贴，交接页会按正文顺序列出本次版本化 `assets/` 作为人工上传降级路径。自动化只能证明结构、资源和本地门禁正确；首次启用或适配器变化后，仍需在公众号后台完成一次复制、修改、保存和重开检查。

#### 纵向滑动长图组件（离线交接）

`PROJECT-WECHAT-VERTICAL-SCROLL-HANDOFF-001`：公众号排版遇到长网页、长对话或连续步骤截图时，主动评估上下滑动窗口，不必等编辑再次点名工具。需要连续阅读且整张铺开会占用多屏时，优先列为滑动框候选；在内容包 `research/visual-notes.md` 记录输入顺序、正文插入位置和采用或不采用的原因。这是作者于 2026-09-05 指定的公众号项目偏好，不代表已证明滑动框适合所有长图。

当候选进入交接，或在线转换器不可用、编辑明确要求转换时，使用仓库现有发布适配器生成，不在内容包里保留一次性 HTML 构建器。图片必须位于内容包 `assets/`，按展示顺序逐张登记为 `use: "wechat_body_interactive"`，允许 `wechat`，且权利状态已经解决。

普通横图、短截图、需要并排比较的画面继续直接展示；GIF／视频继续用对应媒体格式。滑动框只限制显示高度，不压缩原图，也不用于解决飞书「复制的数据太多」。飞书协作文档保留原图与插入标记，不承诺保留公众号的交互 HTML；最终效果在公众号交接时验收。竖向长图窗口与公司扩展自动生成的横向图库是两种不同组件。

编辑明确要求在文章 HTML 中看到滑动框时，草稿阶段就应给出可滚动预览，不能只改 SOP 或把图片列为未来候选。将所选长图作为正常 Markdown 配图，alt 以 `上下滑动：` 开头，例如 `![上下滑动：完整网页](assets/long-page.png)`。统一预览适配器在本地预览页为该图建立 300 px 高、可用滚轮／触屏／键盘操作的窗口；普通图片保持原样。该标记仅影响本地预览 DOM，原始正文和导出载荷仍保留图片，正式公众号组件继续走下方 scroll-handoff 门禁。不能把本地成功写成公众号后台已验收。

预览验收须实际检查 `scrollHeight > clientHeight`，滚动前后 `scrollTop` 和画面发生变化，并保存截图。用户要求增加配图时，先检查手机宽度下的连续文字区，再把对应的原始案例图放入正文；素材仅下载到目录、或截到不对应的轮播页，不算完成。来源、权利、图片对应的事实仍按原门禁登记。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 wechat scroll-handoff <content-package> `
  --image "assets/scroll-01.png" `
  --image "assets/scroll-02.png" `
  --image "assets/scroll-03.png" `
  --title "公众号纵向滑动组件" `
  --height 260 `
  --open
```

执行合同：

- 触发：内容包已经是 `ready`，事实、权利与终校布尔门均为 `true`；输入为 1—9 张已登记静态图。单篇仅预览效果、未准备交付时不启动该命令。
- 动作：工具生成内层显式限高、`overflow-y:scroll` 的普通块布局组件，不用 flex 挤压图片。`--height` 接受 120—600 的整数，缺省为 300 px。图片经同一资源预算检查后转为 Base64，复制按钮只向剪贴板写入组件的 `text/html` 与纯文本，不复制门禁说明。
- 高度：按手机宽度下的图片实际高度调整，不把某个数值用于所有图片。本篇月屿采用 260 px，替代作者认为太矮的 180 px；在 375 / 390 px 预览确认窗口够大且仍有内容可滑。若图片已接近一屏，优先直接展示，不为滑动而过度压低窗口。所选高度写入交接回执。
- 编辑使用：以后提供长图并说「做成上下滑动框」即可触发。打开交接页，点「复制」按钮，把完整组件直接粘贴到公众号；不要只选图片复制，不经飞书中转。要调高时重新生成组件，再整体替换原组件。
- 通过：版本化真源位于 `dist/scroll-handoffs/scroll-handoff-*/wechat-scroll-handoff.html`，同目录回执记录图片顺序、尺寸、字节数、SHA-256、工具哈希和 `wechat_backend_roundtrip: "pending"`；`dist/wechat-scroll-handoff.html` 只是最近一次便利副本。
- 失败：图片不在 `assets/`、重复或超过 9 张，manifest 用途不符、权利未解决、未允许 `wechat`，内容包校验失败，或单图／累计资源超限时，一律 fail loud，不生成可复制的放行页。
- 范围：这是离线人工交接，不接受任意 HTML／CSS 输入，不访问在线转换器，不写公众号后台，也不替代整篇 `manual_editor` 交接。它只覆盖连续图片的竖向滑动组件。
- 验收：本机打开、可滚动和复制成功只证明离线载荷成立。首次启用或工具变化后，仍须在目标公众号草稿中粘贴、保存、重开并做手机预览；未完成前不得把回执中的 `wechat_backend_roundtrip` 改为通过。
- 来源与回归：工具合同来自 `ox-alpha-stealth-self-investigation` 的 FB-004—005；主动评估偏好来自 `astra-cli-review` 的 FB016（E0 / project_configuration）。FB033—035 补充作者确认可粘贴滑动、要求增高及固化流程；这不替代保存重开与手机端完整验收。排版检查应能找到长图候选的处理记录；普通图片不应被强制转换。工具回归覆盖自包含 3 图输出、1—9 图边界、路径逃逸、用途／权利／平台门禁、产物篡改、自定义高度与非法高度拒绝。维护范围为公众号发布适配器，首次正式采用或 2026-09-12 复核偏好是否造成多余操作。

### 密封草稿模式

用户明确要求按既定主题创建草稿，而且后台原则上不再重新排版时，使用：

```yaml
delivery_mode: "sealed_draft"
layout_profile: "<受控主题>"
```

预览与 API 草稿共用受控主题和密封构建。`draft` 默认只做 dry-run；只有当前任务明确授权后才可以执行 `draft --execute`。该命令最多创建 1 个公众号草稿，不发布、不群发。

新主题第一次启用或主题版本变化后，可以在明确授权下创建一条「资格验证草稿」完成后台 round-trip。验证前，任何使用该主题创建的草稿都只用于资格验证，不能作为生产交付；验证通过后，精确公众号账号与主题版本组合才取得生产密封草稿资格。

### 公司浏览器排版执行通道

公司明确提供并指定浏览器排版扩展时，可以在现有内容与权利门之后使用 `execution_route: "company_browser"`。该值只写入 `publish-record.md`，不是当前 `publish.yml` 的 `delivery_mode`。记录必须同时保留仓库 `project_adapter`、仓库 `delivery_mode`、外部 `handoff_brand` 和外部 `execution_route`，不能把两条轴压成一个「交付通道」字段。

该通道的共同合同：

- 公司编辑确认的飞书文档可以作为受限交付定稿；不得仅为自动化方便把 `restricted` 终稿完整复制进 Git。
- 扩展只负责飞书读取、固定样式转换、公众号编辑器写入、图片托管等待和草稿保存，不提供事实、权利、终校或发布授权。
- 外部公司终稿只复用旧内容包资产时，把旧包标为 `asset_donor`，保留原 `project_adapter` 与生图凭据；在 `publish-record.md` 另记公司 `handoff_brand` 和用户对具体图片的复用许可，不把历史 generic 凭据改写成 APPSO 凭据。
- 每次点击覆盖都属于外部写操作。必须明确目标公众号账号与草稿，取得当前任务授权，并只保留 1 个公众号编辑页。
- 扩展版本与运行时格式绑定。版本变化后先写空白资格验证草稿，完成保存、重开与手机预览，再授予精确账号 × 版本组合生产资格。
- 样式旁路、标题／摘要未确认、图片占位、保存未确认或重开不一致均为失败；因为页面可能已经自动保存，先检查草稿再重试。
- 公司扩展缓存的全文、来源 URL 和 Base64 图片在完成或终止后必须清除；技术详情脱敏后才能反馈。
- `manual_editor` 是结构不兼容、图片需要人工身份核对或浏览器写入失败时的默认降级路径；`sealed_draft` 只在用户另行明确选择仓库 API 草稿时使用。

具体 APPSO 版本、入口、样式合同、题图与尾图处理见 [`公司飞书到公众号浏览器排版 SOP`](<../../../../APPSO-数字资产/03-SOP/公司飞书到公众号浏览器排版 SOP.md>)。

## APPSO 普通长文适配

APPSO 的模式选择以 [`APPSO 内容生产 SOP`](<../../../../APPSO-数字资产/03-SOP/APPSO 内容生产 SOP.md#7-排版与交付>) 为真源。公司稿选定爱范儿一键排版 Chrome 扩展 v1.10.0 为格式来源；它走上节的 `company_browser` 执行通道，不由本适配器创建。

本适配器继续接受人工交接的 `project_adapter: "appsso"`、`delivery_mode: "manual_editor"`、`layout_profile: "default"` 组合，以及密封草稿的 `delivery_mode: "sealed_draft"`、`layout_profile: "appsso-article-v1"` 组合。该 profile 只映射到仓库内受控的 [`themes/appsso-article-v1.css`](../../../../微信公众号/themes/appsso-article-v1.css)，不接受内容包传入任意 CSS 路径。它是公司扩展不可用时的独立回退，不复刻扩展样式。样本依据、头尾图识别结果和适用边界见 [`themes/README.md`](../../../../微信公众号/themes/README.md)。

头尾图不写入 `draft.md`，由 `publish.yml` 指向内容包内文件后自动注入：

```yaml
project_adapter: "appsso"
delivery_mode: "sealed_draft"
layout_profile: "appsso-article-v1"
header_image: "assets/appsso-inspiration-guide.gif"
header_alt: "APPSO 灵感指南"

# 尾图可选。按 Asia/Shanghai 填写下一次复核截止日。
footer_image: "assets/appsso-footer.jpg"
footer_alt: "APPSO 招聘信息"
footer_valid_until: "2026-08-31"
```

对应图片必须在 `asset-manifest.yml` 分别声明 `use: "wechat_body_header"` 或 `use: "wechat_body_footer"`，允许 `wechat`，具有发布可用的权利状态，并填写与图片内容一致的非空替代文本。旧稿中的招聘尾图不是永久品牌组件；所有尾图都要按 Asia/Shanghai 填写 `footer_valid_until`。它是内部素材复核截止日，不是招聘或活动的真实截止日；从本次确认日起最长不得超过 365 天，复核逾期后适配器阻断草稿创建并要求重新确认或移除。

`appsso-article-v1` 仅用于 APPSO 普通长文。Hunt Good 已有独立的 24 px 栏目名规则，个人公众号也必须显式选择自己的 profile，二者都不得自动继承本主题。

## Commands

Run all commands below from the repository root.

Local diagnostic preview or explicitly accepted fallback; no network or external write:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 wechat preview <content-package> --open
```

Editable handoff; no network or external write:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 wechat handoff <content-package> --open
```

预览默认使用 390 px 内容宽度，并提供 375 px / 390 px 切换按钮；两档都要检查溢出、正文缩进、全宽头图和尾图位置。

Draft preflight; still no network or external write:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 wechat draft <content-package>
```

Create exactly one draft after explicit current-task authorization:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 wechat draft <content-package> --execute
```

`--execute` delegates rendering, image uploads, cover material upload, and draft creation to `@wenyan-md/cli`. It does not publish or mass-send. The local result receipt records the same non-secret account fingerprint. After success, a human still checks the actual draft in the Official Account backend.

Pinned-version notes:

- Wenyan CLI 2.0.11 does not forward a custom `digest` field to `draft/add`; WeChat derives an excerpt. Treat `publish.yml`'s `digest` as the desired backend check/edit value.
- Wenyan CLI 2.0.11 uploads body images as permanent image materials and reuses its local upload cache for duplicate assets. Review material-library growth during normal operations.
- `draft --execute` 不是跨多个微信接口的原子事务。若 Wenyan 返回失败，前序正文图或封面可能已经成为永久素材；若失败发生得更晚，草稿也可能已经存在。先检查公众号后台和素材库，再决定是否重试，避免重复素材或重复草稿。

## Generated files

`dist/builds/build-<random>/` contains the run-specific `wenyan-source.md`, theme snapshot, and structurally valid package-local images needed for the local preview or sealed draft. `dist/handoffs/handoff-<random>/` contains one versioned manual-editor handoff, its structure-only HTML, exact pre-DOM copy input, copied local images and a matching `publish-plan.json`. A staged or copied image is not evidence of rights clearance: any validator or rendered-resource blocker prevents the corresponding handoff or draft command from passing. `dist/` also contains the latest self-contained `wechat-content.html`, `wechat-preview.html`, and `publish-plan.json`; the versioned handoff directory is the stable copy source. The plan records delivery capability plus package, staged-build, source, theme, handoff page, handoff content, copy input and image SHA-256 values. Shared or stale `dist/assets/` files are never publication inputs.

浏览器可能规范化 DOM，因此复制输入哈希不等于公众号后台最终 HTML 哈希，后台 round-trip 仍不可省略。

These generated files can be regenerated and must not be edited as canonical content. Old build directories may be removed only when no preview or draft command is running; a later command always creates a new unique directory.

Wenyan's local token and upload cache live under `微信公众号/.wenyan-runtime/`; the directory is private and Git-ignored.
