# WeChat preview and draft workflow

Use the pinned open-source [Wenyan CLI](https://github.com/caol64/wenyan-cli) for Markdown rendering, inline image uploads, permanent cover upload, and WeChat `draft/add`. Do not maintain a separate renderer or WeChat API client in this project.

The project-owned adapter at `微信公众号/tools/wechat_publish.py` only:

- maps `draft.md` plus `publish.yml` to Wenyan frontmatter;
- removes the editorial-only leading H1 so the platform title is not duplicated;
- runs the existing content-package validator and release gates;
- produces a phone-width local preview;
- keeps the default draft command as a no-network dry-run.

## One-time setup

From `微信公众号/`:

```powershell
npm.cmd install
Copy-Item .env.example .env
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
highlight: "solarized-light"
mac_style: false
footnote: true
need_open_comment: false
only_fans_can_comment: false
```

The cover must exist inside the package, be registered in `asset-manifest.yml`, allow `wechat`, and have a resolved rights status. Do not use an unresolved paper figure or screenshot as the cover merely to satisfy the API.

## Commands

Local preview; no network or external write:

```powershell
python 微信公众号/tools/wechat_publish.py preview <content-package> --open
```

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

`dist/` contains `wenyan-source.md`, `wechat-content.html`, `wechat-preview.html`, and `publish-plan.json`. These files can be regenerated and must not be edited as canonical content.

Wenyan's local token and upload cache live under `微信公众号/.wenyan-runtime/`; the directory is private and Git-ignored.
