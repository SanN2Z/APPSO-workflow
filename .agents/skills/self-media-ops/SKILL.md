---
name: self-media-ops
description: Operate the shortest safe workflow for self-media topics, research, drafts, rewrites, images, editorial review, WeChat or X delivery preparation, and content-package maintenance in the 自媒体运营 workspace. Use for content work; load long-form, APPSO, image, publishing, retrospective, and insight modules only when the task actually triggers them.
---

# Self Media Ops

Route the task once, load only the triggered module, and use [the core workflow](../../../共享/运营/SOP/内容工作流.md) as the single source for lifecycle and detailed rules.

## Start

1. Run `git status --short`; preserve unrelated changes.
2. Identify the target platform, package, requested state change, and external action.
3. Read only the target platform `AGENTS.md` / `CONTEXT.md`, target package, and directly triggered references.
4. Read `上下文/当前重点.md` only for a new task, cross-package switch, planning, or repository cleanup.
5. For analysis, pass `CORE-VALUE-001`; do not manufacture value with style, structure, or length.
6. When changing an SOP, Skill, dependency, workflow entry, or versioned tool, apply `CORE-PORTABILITY-001`; use the clone-local bootstrap and runner instead of relying on global packages or machine paths.

## Choose the lowest safe lane

| Lane | Use | Minimum path |
|---|---|---|
| L0 local | Idea, research, typo, sentence, link, or a change that does not alter claims, structure, assets, or state | Target files + local check |
| L1 factual | Verified quick news, status notice, fixed brief, translation, or source index | Fact packet → one short draft → fact mapping |
| L2 standard analysis | One core judgment and story route clearly dominate; default for WeChat analysis | Compact contract → staged co-writing log → one canonical draft → issue-first cold read |
| L3 multi-route | Competing substantive frames, central structural rewrite, flagship editorial / reputation risk, explicit route comparison, or failed L2 center frame | Up to 3 route cards → human selection → the same staged single-draft path as L2 |

Choose by uncertainty and change scope, not length. Dense facts, complex rights, sensitive company material, and release preparation add specialist gates but do not by themselves force L3. The exact triggers, escalation rules, route choice, co-writing control points, and timing live only in `CORE-LANE-001`, `CORE-STANDARD-001`, `PROJECT-WECHAT-JUDGMENT-001`, `CORE-ROUTE-001`, `CORE-COAUTHOR-001`, and `CORE-TIME-001`.

## Load only what is triggered

| Trigger | Read |
|---|---|
| Create or restructure a package | [content-package.md](references/content-package.md) |
| L1 WeChat quick news or status update | [wechat-quicknews-prompt.yml](references/wechat-quicknews-prompt.yml), after the verified fact packet |
| L2 standard analysis | `CORE-STANDARD-001` and `CORE-COAUTHOR-001`; package `brief.md`, `sources.md`, `research/co-writing-log.md`, and `draft.md` |
| L3, or a material choice that needs explicit co-creation | [wechat-judgment-workshop.md](references/wechat-judgment-workshop.md) |
| Parallel research or independent targeted review | [wechat-team.md](references/wechat-team.md); never parallel-edit canonical prose |
| User explicitly requests a style experiment after a substantive canonical draft exists | [wechat-clumsy-writing.yml](references/wechat-clumsy-writing.yml) |
| Voice repair after the value gate | [wechat-human-voice-pass.md](references/wechat-human-voice-pass.md) and [wechat-ai-pattern-pass.md](references/wechat-ai-pattern-pass.md) |
| Final WeChat review | [wechat-editorial-gates.md](references/wechat-editorial-gates.md) and [wechat-copyedit-pass.md](references/wechat-copyedit-pass.md) |
| X final review | [review-checklist.md](references/review-checklist.md) |
| AI image generation or editing | [Image2 workflow](<../../../共享/运营/SOP/Image2 生图工作流.md>) |
| WeChat preview, handoff, or draft | [wechat-publishing.md](references/wechat-publishing.md) |
| APPSO, Hunt Good, company visual, or company draft | `APPSO-数字资产/README.md`, confidentiality rules, and one relevant adapter |
| Material feedback, delivery, or publication | [content-retrospective](../content-retrospective/SKILL.md) |
| Turn a long-term claim into an experiment | [insight-to-asset](../insight-to-asset/SKILL.md) |

## Common gates

- Verify current numbers, dates, prices, roles, names, policies, rankings, quotes, and product claims; prefer primary sources and record support, type, access date, and limits.
- Keep facts, vendor self-report, third-party results, author judgment, inference, and jokes distinguishable.
- Apply `CORE-EVIDENCE-SEAM-001`: keep source strength, verification reasoning, and claim mapping in internal records; ordinary public copy keeps only normal attribution and uncertainty that changes factual meaning.
- L2 and L3 record irreversible decisions, unit contracts, voice anchors, accepted or reopened units, issue-first cold read, local patches, chain mapping, and concrete-detail deletions. L3 additionally records the human-selected route card. Explicit multi-version delivery remains user-selected and is never merged or AI-voted.
- At `editorial_review`, run one full rhythm / pragmatic / human-voice diagnosis on the canonical draft, then apply the authoritative `PROJECT-WECHAT-EXPLANATION-001` as a separate deletion-led over-explanation pass and recheck only repaired points. Do not use that pass for general rewriting or semantic compression. Before `ready`, run the project lexicon appendix once, exact-body copyedit, rights, privacy, credential, platform, state, and authorization checks.
- Images may begin source and rights research early; expensive generation waits for a stable L2 contract or a user-selected L3 route unless the image changes the topic decision.

## Validate and deliver

Before `ready`, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 validate <content-package>
```

On a fresh clone, run `tools/bootstrap.ps1` once before the command above. Keep `draft.md` canonical. Delivery routes are `company_browser`, `manual_editor`, and `sealed_draft`; load the publishing reference before choosing. Local research, writing, organization, preview, and dry-run are allowed. Publishing, messaging, scheduling, browser overwrite, API draft creation, or any external account change requires current-task authorization.
