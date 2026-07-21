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

Install the validator's pinned parser dependencies once in a fresh checkout:

```powershell
python -m pip install -r .agents/skills/self-media-ops/requirements.txt
```

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
version: 2
updated: "2026-07-21"
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

Keep manifests in the validator's normalized project subset shown above: root-level `version`, optional `updated`, then root-level `assets`; indent each `- file` by 2 spaces and its fields by 4 spaces. Use quoted scalars plus inline or indented scalar lists. Do not use YAML anchors, aliases, block scalars, or inline comments in this file.

For `source_type: "ai_generated"`, also record the runtime and reproducibility fields when available:

```yaml
    generator: "Codex built-in image_gen"
    model: "gpt-image-2"
    generation_mode: "text_to_image or referenced_edit or image_edit"
    prompt_ref: "appsso-004 or a governed prompt asset"
    prompt_sha256: "64-lowercase-hex-characters"
    generation_constraints: "Aspect ratio, preserved elements, forbidden elements, and text rules"
    input_assets: ["source reference or conversation attachment"]
    generated_on: "2026-07-21"
```

`input_assets` may be empty for `text_to_image`, but `referenced_edit`, `image_edit`, and `prompt_ref: "appsso-004"` must identify every input and its rights record. `prompt_sha256` hashes the exact governed prompt referenced by `prompt_ref`; keep non-secret run-specific constraints in `generation_constraints` rather than mutating a fixed style prompt.

Before a referenced generation becomes `ready`, every conversation attachment must be persisted under `research/source-assets/` and registered as its own manifest item. Its `rights_status` must explicitly permit derivative use: `project_owned`, `user_confirmed_derivative_use`, `licensed_derivative_use`, `cc0_verified`, `public_domain_verified`, or `project_owned_with_cc0_component`. A generic `user_supplied`, `research_reference`, or unknown status is not permission to redraw. Inputs form an acyclic provenance graph: an output cannot name itself, a path alias of itself, or a downstream derivative as an input.

New or materially edited manifests use `version: 2`. The validator treats publication-bound assets (`used_in_draft: true`, `used_as_cover: true`, a real Markdown reference, or a declared release `use`, such as `wechat_cover`) as follows:

- Before `ready`, incomplete version 2 metadata is a warning so work can continue visibly.
- At `ready` or `published`, missing generation provenance, unresolved rights, or a platform mismatch is an error.
- A real Markdown or raw HTML image reference is publication-bound even if its manifest falsely says `used_in_draft: false`; the contradiction is reported. At `ready` or `published`, remote and embedded data images are blocked instead of bypassing the package manifest. Declared release uses are `wechat_cover`, `wechat_body_header`, `wechat_body_footer`, and `x_media`; `research_reference` and `unused` remain non-release uses.
- Raw active HTML, event-handler attributes, non-allowlisted URL schemes, duplicate HTML attributes, alternate resource attributes, and CSS resource references are rejected before preview or release. Put HTML examples in fenced, indented, or inline code so they remain text.
- Release-bound version 2 assets use this rights allowlist: `project_owned`, `project_owned_with_cc0_component`, `user_confirmed_editorial_commentary`, `user_confirmed_editorial_use`, `licensed`, `cc0_verified`, and `public_domain_verified`. Unknown labels never imply clearance; adding a new cleared status requires a reviewed schema/SOP change.
- Unused research and rejected assets remain warnings and do not block release.
- Version 1 or unversioned historical AI assets remain readable and emit migration warnings; migrate them when the package is next materially edited.

Follow the project [Image2 generation workflow](<../../../../共享/运营/SOP/Image2 生图工作流.md>) for tool mapping, quality review, versioning, and fallback rules.

## WeChat publish configuration

WeChat packages use `publish.yml` for the API-safe title, digest, cover, comments, allowlisted layout profile, and optional package-local body header/footer components. `draft.md` remains the only editable article source. See [wechat-publishing.md](wechat-publishing.md).
