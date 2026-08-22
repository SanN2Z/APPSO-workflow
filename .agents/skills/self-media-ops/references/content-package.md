# Content package specification

## Progressive package

Create files when the work reaches the stage that needs them. A new idea does not need a release package.

| Stage or trigger | Files |
|---|---|
| Any package | `draft.md` |
| `research` or later | `sources.md` |
| New or materially restructured L2 / L3 WeChat analysis | `brief.md` + `research/co-writing-log.md`; add `research/judgment-workshop.md` only when `PROJECT-WECHAT-JUDGMENT-001` applies |
| Explicit multi-version delivery | Separate version bodies and audit sidecars under `research/alternatives/<round>/`; the user selects, versions are never merged or AI-voted |
| First image or visual task | `asset-manifest.yml`, `assets/` and optional `research/source-assets/` |
| `editorial_review` or later | `review.md` |
| `ready` or later | `copyedit.md`; complete `asset-manifest.yml` even when the list is empty |
| Preview or delivery | `publish.yml` |
| External handoff or `published` | `publish-record.md` |
| Substantive feedback, delivery, or publication | `retrospective.md` |

Optional:

- `research/`: internal notes and unused source assets.
- `research/candidates/`: historical frozen multi-draft rounds from the retired default; keep as internal evidence and do not use as the current production path.
- `research/alternatives/`: optional complete versions only when the user explicitly asks for them; no automatic selector or promoted winner.
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

## L2 standard analysis

L2 is the default analytical lane when one core judgment and story route clearly dominate. Record the lane reason, `T_intake`, `T_evidence_ready`, compact story contract, irreversible decisions, and escalation condition in `brief.md`; then use `research/co-writing-log.md` to stage the canonical `draft.md` by section or high-impact paragraph. Do not create placeholder candidates or a selection record.

A reviewer who did not generate the body first reads only the public draft, records located problems, reader harm, reasoning, and pass conditions in `review.md`, and only then opens `brief.md` to map the finished draft back to the compact contract. The reviewer does not silently rewrite the body; accepted changes use local diffs and preserve locked units. Record `T_contract_locked`, `T_first_text_handoff`, `T_owner_reviewed`, and actual elapsed time. A local defect stays in L2; a failed center frame returns to research or escalates to L3 under `CORE-LANE-001`.

## Staged co-writing record

New or materially restructured L2 / L3 analysis uses `research/co-writing-log.md`. The record holds the collaboration mode (`guided` or `direct_write`), irreversible decisions, selected L3 route if any, voice anchors, unit contracts, acceptance labels, locks, reopen reasons, and issue-first patches. Adjacent ordinary paragraphs may share one section contract; do not turn every sentence into a form.

Use these acceptance labels without translating them into a score:

- `keep`
- `meaning_right_wording_wrong`
- `wrong_direction`
- `delete`

An accepted unit is `locked`. Reopen it only for a fact error, a demonstrated chain break, or an explicit user request, and record the old text reference plus a local diff. Public prose never contains the collaboration record or internal evidence grading.

## Judgment workshop record

The trigger and exemptions are defined only by [`PROJECT-WECHAT-JUDGMENT-001`](../../../../共享/运营/SOP/内容工作流.md#project-wechat-judgment-001公众号写前共创门试运行项目配置). The workshop is mandatory for L3 and applies to L2 only when a material choice needs explicit confirmation or the user explicitly asks to co-create. When the rule applies, declare `judgment_workshop: "research/judgment-workshop.md"` in draft frontmatter and copy the repository template into that path.

The workshop uses YAML frontmatter:

```yaml
---
status: discussing
voice_mode: ""
decision_points_completed: 0
user_confirmed: false
confirmed_on: ""
story_contract_version: 1
pragmatic_rule_id: PROJECT-WECHAT-PRAGMATIC-001
expression_calibrated: false
reason: ""
---
```

Allowed states are `discussing`, `locked`, and `not_required`. A package that enters the workshop cannot enter `draft` or a later state while the workshop is `discussing`. `locked` requires 3–5 real decision points resolved with the user, `personal` or `company` voice mode, explicit user confirmation, a complete four-cell narrative chain, a narrative engine, a non-empty strongest opponent or an explicit downgrade, and non-empty sections for the ordinary-person situation, main judgment, 2–4 supporting judgments, rejected directions, and reader takeaway. Several decisions may be resolved in one user response; do not create ceremonial turns. `not_required` needs a concrete reason.

Historical packages with or without the frontmatter pointer remain readable. New and materially restructured packages follow the current rule and template. L3 records the route selected by the user before prose; it does not start full-draft candidates by default.

## Historical candidate rounds and explicit alternatives

`research/candidates/round-XX/` remains readable for historical packages created under workflow v6.1 or earlier. Do not create a new candidate round merely because a task is L3, long, fact-dense, important, or under time pressure. Current L3 compares route cards before prose and then uses one canonical writer line.

When the user explicitly requests multiple complete versions, use `research/alternatives/<round>/` and freeze:

- one shared fact packet, allowed / forbidden claims, target range, and stop condition;
- one independent body and audit sidecar per requested version;
- a user decision record naming the adopted version, requested merge, or no selection.

Versions may be produced independently when that is useful, but AI reviewers do not vote on the final. Do not merge versions automatically. Only a user-selected version may enter `draft.md`; a requested synthesis starts a new canonical unit contract and records which decisions were retained.

Historical `candidate-round-frozen-input.md` and `candidate-selection.md` templates are evidence of the retired experiment and must not be mistaken for the current route. Current timing follows `CORE-TIME-001`: record actual intake, evidence-ready, contract-lock, text-handoff, and owner-review times without claiming an unverified SLA.

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
