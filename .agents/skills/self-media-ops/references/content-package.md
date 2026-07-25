# Content package specification

## Progressive package

Create files when the work reaches the stage that needs them. A new idea does not need a release package.

| Stage or trigger | Files |
|---|---|
| Any package | `draft.md` |
| `research` or later | `sources.md` |
| New analytical long-form or structural rewrite | `brief.md`, `research/judgment-workshop.md` |
| First image or visual task | `asset-manifest.yml`, `assets/` and optional `research/source-assets/` |
| `editorial_review` or later | `review.md` |
| `ready` or later | `copyedit.md`; complete `asset-manifest.yml` even when the list is empty |
| Preview or delivery | `publish.yml` |
| External handoff or `published` | `publish-record.md` |
| Substantive feedback, delivery, or publication | `retrospective.md` |

Optional:

- `research/`: internal notes and unused source assets.
- `research/image-generation-plan.json` and `research/image-generation-runs/`: required only for AI-image work.
- `tools/`: deterministic package-local transforms.
- `dist/`: disposable, generated, and Git-ignored.

The validator applies requirements by state. Historical full packages remain valid.

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
judgment_workshop: "research/judgment-workshop.md"
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

## Judgment workshop record

New WeChat analytical long-form packages and structural rewrites declare `judgment_workshop: "research/judgment-workshop.md"` in draft frontmatter and copy the repository template into that path.

The workshop uses YAML frontmatter:

```yaml
---
status: discussing
voice_mode: ""
decision_points_completed: 0
user_confirmed: false
confirmed_on: ""
reason: ""
---
```

Allowed states are `discussing`, `locked`, and `not_required`. An applicable package cannot enter `draft` or a later state while the workshop is `discussing`. `locked` requires 3–5 real decision points resolved with the user, `personal` or `company` voice mode, explicit user confirmation, and non-empty sections for the ordinary-person situation, main judgment, 2–4 supporting judgments, rejected directions, and reader takeaway. Several decisions may be resolved in one user response; do not create ceremonial turns. `not_required` needs a concrete reason such as a pure factual brief or an unchanged fast edit.

Historical packages without the frontmatter pointer remain readable. When a historical article receives a structural rewrite, add the pointer and workshop instead of inferring an old discussion record.

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

Create `asset-manifest.yml` when the first image enters the package. New or materially edited packages use `version: 2`.

```yaml
version: 2
updated: "2026-07-21"
assets:
  - file: "assets/example.png"
    used_in_draft: true
    source_type: "project_generated"
    source: "creation or source URL"
    creator_or_rightsholder: "This project"
    obtained_on: "2026-07-10"
    modifications: "Original chart"
    rights_status: "project_owned"
    allowed_platforms: ["wechat", "x"]
    attribution: "Cite underlying data"
```

Use package-relative paths. A user-supplied file is not automatically cleared for publication or derivative work.

For `source_type: "ai_generated"`, also record:

```yaml
    generator: "Codex built-in image_gen"
    model: "gpt-image-2"
    generation_mode: "text_to_image"
    prompt_ref: "governed prompt ID"
    prompt_sha256: "64-lowercase-hex-characters"
    generation_constraints: "ratio, preserved elements, and exclusions"
    input_assets: []
    generated_on: "2026-07-21"
    preflight_receipt: "research/image-generation-runs/<task>-final-preflight.json"
    invocation_prompt_sha256: "64-lowercase-hex-characters"
```

Referenced edits must identify every input and its derivative-use status. Persist conversation attachments before `ready`. Publication-bound assets with missing provenance, unresolved rights, or a platform mismatch block `ready`; unused research assets remain warnings.

The validator enforces schema, path, rights, provenance, input-cycle, and release-use details. Load the full [Image2 workflow](<../../../../共享/运营/SOP/Image2 生图工作流.md>) only when generating or editing images.

## WeChat publish configuration

Create `publish.yml` only for preview or delivery. The user chooses one route:

- `company_browser`: APPSO company extension; external write authorization required.
- `manual_editor`: local versioned handoff; API commands blocked.
- `sealed_draft`: dry-run first; one draft may be created after explicit authorization.

The configuration keeps `project_adapter`, `delivery_mode`, and `layout_profile` separate for validation, but users do not need to reason about those fields one by one. Use the project template for the selected route.

`draft.md` remains the editable source. Company finals may remain in restricted Feishu; record only a restricted pointer, permitted image mapping, and sanitized diff. See [wechat-publishing.md](wechat-publishing.md) for commands, fields, and failure handling.
