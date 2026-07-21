# Content package specification

## Required files

```text
content-package/
├─ brief.md
├─ draft.md
├─ sources.md
├─ copyedit.md
├─ review.md
├─ asset-manifest.yml
├─ assets/
├─ publish.yml          # WeChat API and Wenyan settings
└─ publish-record.md
```

Optional directories:

- `research/`: internal notes, reference text, and unused source assets.
- `tools/`: deterministic scripts used to create charts or transform local assets.
- `dist/`: generated previews and upload inputs; disposable and Git-ignored.

## Draft frontmatter

```yaml
---
title: "Human-readable title"
platform: wechat
status: draft
created: 2026-07-10
updated: 2026-07-10
as_of: 2026-07-10
fact_checked: false
rights_checked: false
copyedit_checked: false
copyedit_body_sha256: ""
published_url: ""
---
```

Allowed platforms: `wechat`, `x`.

Allowed states:

`idea`, `research`, `draft`, `fact_checked`, `editorial_review`, `ready`, `published`, `archived`.

Rules:

- `ready` requires `fact_checked: true`, `rights_checked: true`, `copyedit_checked: true`, and a current `copyedit_body_sha256`.
- `copyedit.md` must be `pass` and record the same body hash. The hash covers everything after the closing draft frontmatter delimiter.
- Any body edit invalidates the copyedit pass. Set `copyedit_checked: false`, clear the hash, and re-run the complete sentence-level gate.
- `published` requires a real `published_url` or an explicit user-confirmed offline record.
- Use an ISO date for `created`, `updated`, and `as_of`.

## Copyedit record

Use YAML frontmatter so the validator can match the exact body:

```yaml
---
status: pass
checked_at: "2026-07-12 21:45:00+08:00"
body_sha256: "64-lowercase-hex-characters"
scope: "title, body, headings, lists, captions, quotes, notes"
---
```

Record sentence defects as `COPY-*` items below the frontmatter. See [wechat-copyedit-pass.md](wechat-copyedit-pass.md).

## Asset manifest

Register publication and archived source assets. Minimum fields:

```yaml
assets:
  - file: "assets/example.png"
    used_in_draft: true
    source_type: "project_generated"
    source: "Data and creation source"
    creator_or_rightsholder: "This project"
    obtained_on: "2026-07-10"
    modifications: "Original chart"
    rights_status: "project_owned"
    allowed_platforms: ["wechat", "x"]
    attribution: "Cite underlying data"
```

Keep paths relative to the package. Never point a publication draft at a temporary attachment path.

## WeChat publish configuration

WeChat packages use `publish.yml` for the API-safe title, digest, cover, comments, and Wenyan theme. `draft.md` remains the only editable article source. See [wechat-publishing.md](wechat-publishing.md).
