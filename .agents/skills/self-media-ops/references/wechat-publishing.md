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

Fill `WECHAT_APP_ID` and `WECHAT_APP_SECRET` in the local `.env`. Never paste the secret into chat, a draft, logs, or committed files. `.env`, Wenyan token/material caches, and generated preview artifacts are ignored by Git.

The WeChat account must expose the required material and draft APIs. The machine's public egress IP must be allowed in the Official Account developer configuration, unless a separately reviewed fixed-egress deployment is used.

## Per-article configuration

Create `publish.yml` in the content package:

```yaml
title: "API title, at most 32 characters"
author: ""
digest: "Feed summary"
cover: "assets/cover.png"
source_url: ""
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

## APPSO 普通长文版式

APPSO 普通长文使用 `layout_profile: "appsso-article-v1"`。该 profile 只映射到仓库内受控的 [`themes/appsso-article-v1.css`](../../../../微信公众号/themes/appsso-article-v1.css)，不接受内容包传入任意 CSS 路径。CSS 是样式参数的唯一真源；样本依据、头尾图识别结果和适用边界见 [`themes/README.md`](../../../../微信公众号/themes/README.md)。

头尾图不写入 `draft.md`，由 `publish.yml` 指向内容包内文件后自动注入：

```yaml
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

预览默认使用 390 px 内容宽度，并提供 375 px / 390 px 切换按钮；两档都要检查溢出、正文缩进、全宽头图和尾图位置。

Draft preflight; still no network or external write:

```powershell
python 微信公众号/tools/wechat_publish.py draft <content-package>
```

Create exactly one draft after explicit current-task authorization:

```powershell
python 微信公众号/tools/wechat_publish.py draft <content-package> --execute
```

`--execute` delegates rendering, image uploads, cover material upload, and draft creation to `@wenyan-md/cli`. It does not publish or mass-send. After success, a human still checks the actual draft in the Official Account backend.

Pinned-version notes:

- Wenyan CLI 2.0.11 does not forward a custom `digest` field to `draft/add`; WeChat derives an excerpt. Treat `publish.yml`'s `digest` as the desired backend check/edit value.
- Wenyan CLI 2.0.11 uploads body images as permanent image materials and reuses its local upload cache for duplicate assets. Review material-library growth during normal operations.

## Generated files

`dist/builds/build-<random>/` contains the run-specific `wenyan-source.md`, theme snapshot, and structurally valid package-local images needed for the local preview. A staged image is not evidence of rights clearance: any validator or rendered-resource blocker prevents `--execute`. `dist/` also contains the latest `wechat-content.html`, `wechat-preview.html`, and `publish-plan.json`. The plan records package, staged-build, source, and theme SHA-256 values so a blocker-free build's exact inputs are checked again before and after draft creation. Shared or stale `dist/assets/` files are never publication inputs.

These generated files can be regenerated and must not be edited as canonical content. Old build directories may be removed only when no preview or draft command is running; a later command always creates a new unique directory.

Wenyan's local token and upload cache live under `微信公众号/.wenyan-runtime/`; the directory is private and Git-ignored.
