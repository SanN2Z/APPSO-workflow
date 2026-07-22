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

## One-time setup

From the repository root:

```powershell
python -m pip install -r 微信公众号/requirements.txt
npm.cmd --prefix 微信公众号 install
Copy-Item 微信公众号/.env.example 微信公众号/.env
```

Fill `WECHAT_APP_ID` and `WECHAT_APP_SECRET` in the local `.env`. `draft --execute` rejects a missing or ambiguous credential file, removes ambient WeChat credentials and Node injection variables from the child process, and prints only a 12-character SHA-256 fingerprint of the selected AppID. Confirm that non-secret fingerprint against the intended account before proceeding. Never paste the secret into chat, a draft, logs, or committed files. `.env`, Wenyan token/material caches, and generated preview artifacts are ignored by Git.

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

## 两种交付模式

`project_adapter`、`delivery_mode` 和 `layout_profile` 是三个独立声明字段：前者声明品牌归属，中间字段决定如何交接，最后一个字段只选择视觉主题。新内容包和任何再次交付的旧内容包都必须显式填写 `delivery_mode`；缺失字段的旧包只能兼容预览，不能创建交接稿或 API 草稿。

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

### 密封草稿模式

用户明确要求按既定主题创建草稿，而且后台原则上不再重新排版时，使用：

```yaml
delivery_mode: "sealed_draft"
layout_profile: "<受控主题>"
```

预览与 API 草稿共用受控主题和密封构建。`draft` 默认只做 dry-run；只有当前任务明确授权后才可以执行 `draft --execute`。该命令最多创建 1 个公众号草稿，不发布、不群发。

新主题第一次启用或主题版本变化后，可以在明确授权下创建一条「资格验证草稿」完成后台 round-trip。验证前，任何使用该主题创建的草稿都只用于资格验证，不能作为生产交付；验证通过后，精确公众号账号与主题版本组合才取得生产密封草稿资格。

## APPSO 普通长文适配

APPSO 的模式选择以 [`APPSO 内容生产 SOP`](<../../../../APPSO-数字资产/03-SOP/APPSO 内容生产 SOP.md#7-排版与交付>) 为真源。本适配器接受人工交接的 `project_adapter: "appsso"`、`delivery_mode: "manual_editor"`、`layout_profile: "default"` 组合，以及密封草稿的 `delivery_mode: "sealed_draft"`、`layout_profile: "appsso-article-v1"` 组合。该 profile 只映射到仓库内受控的 [`themes/appsso-article-v1.css`](../../../../微信公众号/themes/appsso-article-v1.css)，不接受内容包传入任意 CSS 路径。样本依据、头尾图识别结果和适用边界见 [`themes/README.md`](../../../../微信公众号/themes/README.md)。截至 2026 年 7 月 22 日，它尚未通过真实后台往返验证，因此任何创建结果都只能作为资格验证草稿。

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

Local preview; no network or external write:

```powershell
python 微信公众号/tools/wechat_publish.py preview <content-package> --open
```

Editable handoff; no network or external write:

```powershell
python 微信公众号/tools/wechat_publish.py handoff <content-package> --open
```

预览默认使用 390 px 内容宽度，并提供 375 px / 390 px 切换按钮；两档都要检查溢出、正文缩进、全宽头图和尾图位置。

Draft preflight; still no network or external write:

```powershell
python 微信公众号/tools/wechat_publish.py draft <content-package>
```

Create exactly one draft after explicit current-task authorization:

```powershell
python 微信公众号/tools/wechat_publish.py draft <content-package> --execute
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
