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
├─ research/judgment-workshop.md  # conditional requirement for analytical long-form and structural rewrites
├─ publish.yml          # WeChat API and Wenyan settings
└─ publish-record.md
```

Optional directories:

- `research/`: internal notes, reference text, and unused source assets.
- `research/image-generation-plan.json`: required when the package uses AI-generated images; stores `project_adapter`, task `visual_type`, style routing, stages, references, constraints, outputs, and receipt paths without copying local-only Prompt text.
- `research/image-generation-runs/`: non-sensitive preflight receipts for AI-image calls.
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
rounds_completed: 0
user_confirmed: false
confirmed_on: ""
reason: ""
---
```

Allowed states are `discussing`, `locked`, and `not_required`. An applicable package cannot enter `draft` or a later state while the workshop is `discussing`. `locked` requires 3–5 real user-response rounds, `personal` or `company` voice mode, explicit user confirmation, and non-empty sections for the ordinary-person situation, main judgment, 2–4 supporting judgments, rejected directions, and reader takeaway. `not_required` needs a concrete reason such as a pure factual brief or an unchanged fast edit.

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

For every version 2 `source_type: "ai_generated"` item, record the runtime, preflight, and reproducibility fields:

```yaml
    generator: "Codex built-in image_gen"
    model: "gpt-image-2"
    generation_mode: "text_to_image or referenced_edit or image_edit"
    prompt_ref: "appsso-004 or a governed prompt asset"
    prompt_sha256: "64-lowercase-hex-characters"
    generation_constraints: "Aspect ratio, preserved elements, forbidden elements, and text rules"
    input_assets: ["source reference or conversation attachment"]
    generated_on: "2026-07-21"
    preflight_receipt: "research/image-generation-runs/<task>-final-preflight.json"
    invocation_prompt_sha256: "64-lowercase-hex-characters"
```

`input_assets` may be empty for `text_to_image`, but `referenced_edit`, `image_edit`, and any profile declaring `requires_reference: true` must identify every input and its rights record. `prompt_sha256` hashes the exact preflight prompt basis referenced by `prompt_ref`, while `invocation_prompt_sha256` binds the complete Prompt actually sent after constraints are appended. Keep non-secret run-specific constraints in `generation_constraints` rather than mutating a fixed style prompt.

Before a referenced generation becomes `ready`, every conversation attachment must be persisted under `research/source-assets/` and registered as its own manifest item. Its `rights_status` must explicitly permit derivative use: `project_owned`, `user_confirmed_derivative_use`, `licensed_derivative_use`, `cc0_verified`, `public_domain_verified`, or `project_owned_with_cc0_component`. A generic `user_supplied`, `research_reference`, or unknown status is not permission to redraw. Inputs form an acyclic provenance graph: an output cannot name itself, a path alias of itself, or a downstream derivative as an input.

When a governed fixed style requires a reference, first reuse a suitable registered local input. If none exists, the plan must declare `two_stage_reference_then_redraw`. Generate the first-stage composition into `research/source-assets/`, mark it with the standard `source_type: "ai_generated"`, `use: "research_reference"`, `used_in_draft: false`, and a derivative-cleared rights status, then register its own generation metadata. Do not invent `source_type: "ai_generated_reference"`; using a nonstandard label must not bypass AI provenance checks.

Run the preflight immediately before each call:

```powershell
python .agents/skills/self-media-ops/scripts/preflight_image_generation.py `
  <content-package-path> --task <task-id> --stage <reference|final> `
  --include-prompt --write-receipt
```

With `--include-prompt`, preflight returns an ephemeral `tool_request` containing the exact `prompt` and, when required, `referenced_image_paths` or `num_last_images_to_include`. Parse that object and pass it unchanged to `image_gen` in the same orchestration action; never transcribe or reconstruct it. A changed Prompt, plan, profile registry, input file content or rights, input order, mode, constraints, or output invalidates the receipt and requires another preflight. The release validator recomputes the plan, registry, and local-input hashes and rejects minimal handwritten receipts. Receipts do not store `tool_request` or the governed Prompt original.

New or materially edited manifests use `version: 2`. The validator treats publication-bound assets (`used_in_draft: true`, `used_as_cover: true`, a real Markdown reference, or a declared release `use`, such as `wechat_cover`) as follows:

- Before `ready`, incomplete version 2 metadata is a warning so work can continue visibly.
- At `ready` or `published`, missing generation provenance, unresolved rights, or a platform mismatch is an error.
- A real Markdown or raw HTML image reference is publication-bound even if its manifest falsely says `used_in_draft: false`; the contradiction is reported. At `ready` or `published`, remote and embedded data images are blocked instead of bypassing the package manifest. Declared release uses are `wechat_cover`, `wechat_body_header`, `wechat_body_footer`, and `x_media`; `research_reference` and `unused` remain non-release uses.
- Raw active HTML, event-handler attributes, non-allowlisted URL schemes, duplicate HTML attributes, alternate resource attributes, and CSS resource references are rejected before preview or release. Put HTML examples in fenced, indented, or inline code so they remain text.
- Release-bound version 2 assets use this rights allowlist: `project_owned`, `project_owned_with_cc0_component`, `user_confirmed_editorial_commentary`, `user_confirmed_editorial_use`, `licensed`, `cc0_verified`, and `public_domain_verified`. Unknown labels never imply clearance; adding a new cleared status requires a reviewed schema/SOP change.
- Unused research and rejected assets remain warnings and do not block release.
- Version 1 or unversioned historical AI assets remain readable and emit migration warnings; migrate them when the package is next materially edited.

Follow the project [Image2 generation workflow](<../../../../共享/运营/SOP/Image2 生图工作流.md>) for tool mapping, quality review, versioning, and fallback rules.
For generic new images, start from `共享/模板/生图计划/通用直出计划模板.json`; for generic reference edits, use `共享/模板/生图计划/通用参考图编辑计划模板.json`. For APPSO packages, use `APPSO-数字资产/04-模板/APPSO 生图计划模板.json`. Copy the selected file into `research/image-generation-plan.json`, replace every task-specific placeholder, and remove `template_only` before preflight. The preflight rejects untouched templates by design.

## WeChat publish configuration

WeChat packages use `publish.yml` for three independently declared routing fields plus API-safe title, digest, cover, comments, and optional package-local body header/footer components:

- `project_adapter` declares the real brand or project owner. Changing delivery or layout must not erase it, and the image plan must declare the same adapter.
- `delivery_mode` declares exactly one handoff capability. `manual_editor` produces a local editor handoff and must reject every API draft command; `sealed_draft` permits the draft dry-run and, only after explicit current-task authorization, creation of one WeChat draft.
- `layout_profile` selects an allowlisted visual theme. It does not infer either the brand or the delivery mode. `manual_editor` uses `default`; a sealed draft selects a compatible controlled theme.

New packages and old packages being handed off again must declare all three fields explicitly. A legacy package without `delivery_mode` may be previewed for migration, but it cannot create an editor handoff or an API draft. `draft.md` remains the only editable article source inside the repository; generated handoff and preview files are disposable artifacts.

An approved company browser extension may be recorded separately in `publish-record.md` as `execution_route: company_browser`. Keep the two axes explicit: copy `project_adapter` and `delivery_mode` from `publish.yml`, then record the external `handoff_brand` and `execution_route` separately. This does not add a third `publish.yml` delivery mode and does not authorize `wechat_publish.py` to call the extension.

When company policy keeps the editor-approved final only in Feishu, record the restricted source identifier, allowed image mapping and sanitized diff without copying the full final into Git. If an older repository package only donates user-approved assets to that external final, mark it `package_role: asset_donor`; preserve its original `project_adapter`, image plan and preflight receipts, and record the company `handoff_brand` separately. Asset reuse does not retroactively turn a generic generation receipt into an APPSO preflight. The browser extension's capture or save result cannot certify repository `ready`, fact, rights or copyedit gates. See [wechat-publishing.md](wechat-publishing.md) for the execution and external-action contract.
