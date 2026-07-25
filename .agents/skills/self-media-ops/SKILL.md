---
name: self-media-ops
description: Operate the shortest safe workflow for self-media topics, research, drafts, rewrites, images, editorial review, WeChat or X delivery preparation, and content-package maintenance in the 自媒体运营 workspace. Use for content work; load long-form, APPSO, image, publishing, retrospective, and insight modules only when the task actually triggers them.
---

# Self Media Ops

Use the shortest path that can safely finish the current task. Do not load every SOP by default.

## Start

1. Run `git status --short` and preserve unrelated changes.
2. Classify the request: idea, research, draft, rewrite, quick edit, image, review, delivery, feedback, or repository maintenance.
3. Read the target platform `AGENTS.md` / `CONTEXT.md` and the target content package.
4. Read `上下文/当前重点.md` only for a new task, cross-package switch, planning, or repository cleanup.
5. Use [the core workflow](../../../共享/运营/SOP/内容工作流.md) as the only lifecycle source.

## Load only what is triggered

| Trigger | Read |
|---|---|
| Create or restructure a package | [content-package.md](references/content-package.md) |
| WeChat analytical long-form or structural rewrite | [wechat-judgment-workshop.md](references/wechat-judgment-workshop.md), then [wechat-clumsy-writing.yml](references/wechat-clumsy-writing.yml) |
| Draft, rewrite, or voice repair | [wechat-human-voice-pass.md](references/wechat-human-voice-pass.md) and [wechat-ai-pattern-pass.md](references/wechat-ai-pattern-pass.md) |
| APPSO expression review | [wechat-expression-library.yml](references/wechat-expression-library.yml) plus the APPSO adapter |
| Final WeChat review | [wechat-editorial-gates.md](references/wechat-editorial-gates.md) and [wechat-copyedit-pass.md](references/wechat-copyedit-pass.md) |
| X final review | [review-checklist.md](references/review-checklist.md) |
| AI image generation or editing | [Image2 workflow](<../../../共享/运营/SOP/Image2 生图工作流.md>) |
| WeChat preview, handoff, or draft | [wechat-publishing.md](references/wechat-publishing.md) |
| APPSO, Hunt Good, company visual or company draft | `APPSO-数字资产/README.md`, its confidentiality rules, and the one relevant adapter |
| Material feedback, delivery, or publication | [content-retrospective](../content-retrospective/SKILL.md) |
| Long-term claim experiment | [insight-to-asset](../insight-to-asset/SKILL.md) |
| Explicit parallel or high-risk review | [wechat-team.md](references/wechat-team.md) |

A typo, one-sentence polish, link repair, or other edit that does not change claims, structure, assets, or state does not trigger the full writing team or retrospective.

## Run the task

### 1. Define

State the reader, one question, desired takeaway, deadline, required facts, and exclusions. For a quick edit, preserve the existing brief unless the request changes the article's central thought.

### 2. Research

Browse current claims when dates, prices, roles, rankings, policies, models, or「latest」information appear. Prefer primary sources. Record the source, access date, supported wording, type, and limitation in `sources.md`.

### 3. Discuss the judgment when required

For an applicable WeChat analytical long-form article, propose 3–5 candidate judgments and resolve 3–5 real decision points with the user. Lock one ordinary-person situation, one main judgment, 2–4 supporting judgments, evidence limits, voice mode, rejected directions, opening, and ending before drafting.

Treat the count as decision points, not ceremonial chat turns. Pure factual briefs, X posts, research-only work, and fast edits that keep the central thought may record `not_required`.

### 4. Draft or edit

Keep one editable `draft.md`. Write for the target platform, not by mechanically shortening another platform's copy. Apply the versioned clumsy-writing Prompt only after an applicable judgment workshop is locked.

### 5. Review at the right stage

- During drafting: fix only the claims, structure, voice, or assets affected by the task.
- At `fact_checked`: verify time-sensitive facts, numbers, names, quotes, identities, and comparison settings.
- At `editorial_review`: run the human-voice and Chinese AI-pattern passes; repair confirmed defects.
- Before `ready`: run sentence-level copyedit on the exact body, verify rights and platform rendering, and run the validator.

Do not use keyword counts or detector scores as Chinese writing gates.

### 6. Prepare delivery

Keep `draft.md` as the editorial source. Choose one route:

- `company_browser`: APPSO company extension after current-task authorization.
- `manual_editor`: versioned local handoff; no API write.
- `sealed_draft`: dry-run first, then create one WeChat draft only after explicit authorization.

No route publishes or mass-sends automatically.

### 7. Capture material feedback

When delivery, publication, or a substantive revision is confirmed, update the package retrospective. Keep one-off wording in the case; promote only repeatable mechanisms through the retrospective gate.

## Validate

Run only the checks required by the current stage. Before `ready`:

```powershell
python .agents/skills/self-media-ops/scripts/validate_content_package.py <content-package>
```

Fix every error. Warnings need review but do not automatically block an early-stage draft.

## External actions

Local research, writing, organization, preview, and dry-run are allowed. Publishing, messaging, scheduling, browser draft overwrite, or any external account change requires explicit authorization in the current task.
