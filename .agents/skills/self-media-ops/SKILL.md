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
| `PROJECT-WECHAT-JUDGMENT-001` applies, or the user explicitly asks for co-creation | [wechat-judgment-workshop.md](references/wechat-judgment-workshop.md) |
| Freeze or select candidates for a WeChat analytical draft | `CORE-SELECTION-001` and `CORE-CHAIN-001` in the core workflow; the frozen input, candidate bodies, and selection record only |
| User explicitly asks to test the clumsy-writing method after a substantive draft exists | [wechat-clumsy-writing.yml](references/wechat-clumsy-writing.yml) |
| Voice repair after the article has passed the value gate | [wechat-human-voice-pass.md](references/wechat-human-voice-pass.md) and [wechat-ai-pattern-pass.md](references/wechat-ai-pattern-pass.md) |
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

### 1. Free judgment layer

Decide whether the material deserves an article before deciding how to package it. Record:

- what the sources already say;
- one non-obvious claim the article adds;
- the evidence relationship that supports or limits that claim;
- the concrete consequence for the reader;
- the strongest alternative explanation and what would make the claim change.

Browse current claims when dates, prices, roles, rankings, policies, models, or「latest」information appear. Prefer primary sources. Record the source, access date, supported wording, type, and limitation in `sources.md`.

If the only available output is source summary, generic background, a larger narrative, or a fact boundary with no reader consequence, stop at `research`. Deliver a factual brief, research note, topic card, or a clear recommendation not to write. Do not use a hook, personal voice, narrative template, or section count to manufacture an article.

### 2. Prewriting calibration layer

After the value gate passes, but before candidate drafting, follow `PROJECT-WECHAT-JUDGMENT-001` and proactively submit a story-contract proposal to the user. Build it in this order: one recommended reader question and core judgment; a one-sentence story line; the reader's question chain; the `CORE-CHAIN-001` four-cell narrative chain; one narrative engine; the strongest opponent and the beat that answers it; then 2–3 title options and provisional section headings. Also state the concrete communication job of any planned high-salience metaphor, reveal, abstract judgment, or concluding line. Do not use「this needs a golden sentence」as a communication job, and do not ask the user to invent the framework from a blank page.

Record revisions and explicit confirmation in `research/judgment-workshop.md`; until `user_confirmed: true`, continue research or wait, but do not generate full candidates. Trigger and exemptions come only from `PROJECT-WECHAT-JUDGMENT-001`. This layer is separate from free judgment so a viable topic cannot silently lock itself into the first available outline.

### 3. Parallel candidate layer

For a new WeChat analytical draft or a structural rewrite that has passed the value gate and the user-confirmed story-contract gate, follow `CORE-SELECTION-001` in the core workflow. Freeze the locked title direction, reader question, single core judgment, four-cell narrative chain, narrative engine, section turns and logical dependencies together with the source packet, fact boundary, target range, and stop condition. Launch 3 isolated writing agents at the same time by default; expand to 4—5 only when the material supports more genuinely different execution routes. If concurrency is lower than the candidate count, use the fewest waves. Never ask one agent to write the candidates sequentially.

Each agent writes one complete candidate under `research/candidates/<round>/` and cannot see the other branches. Every agent may read the same locked story contract, but cannot share a sentence-level plan or inherit another candidate. Differences must be non-lexical and reach scene or character choice, information-reveal order, technical compression, or narrative execution; title, tone, or synonym changes do not count. Within each candidate, every fact, image, and caveat must prove, complicate, falsify, make concrete, or show a consequence of the shared main claim.

Before freezing, each candidate writer checks only two things: facts stay within the frozen boundary, and the draft does not reuse a ready-made skeleton outside `frozen-input.md`. Record `pass` or the concrete issue for both. Do not load the full rhythm, pragmatic, project-lexicon, red-corpus, or human-voice checks for every branch.

Use the 40-minute text lane for an ordinary analytical draft after co-creation. Research, the value gate, and user discussion are Pre-T0. Start T0 only when the user has confirmed the story contract and the evidence is actionable: finish supplemental checks and frozen candidate input by minute 8; freeze 3 candidates in one parallel wave by minute 22; finish the two-reviewer parallel selection by minute 28; verify only the winner by minute 38; hand off readable text by minute 40. Finishing before minute 30 is valid. Discussion waiting is not draft time. If the story contract cannot be mapped to the evidence by minute 8, downgrade or stop instead of filling the remaining time. Five candidates never extend the deadline.

### 4. Blind selection layer

After every candidate is frozen, launch 2 fresh reviewer agents in parallel. They read anonymized bodies before source maps and choose one candidate or「一篇都不要」without scores. Candidate writers never judge. If the two reviewers disagree, run one independent final between the nominated candidates with the same none option.

Reviewers make three separate judgments: whether facts respect the frozen boundary; whether argument and narrative work, including a rough check against the narrative chain; and whether the draft contains a cross-topic portable performance sentence, quoted exactly. Vague reasons such as「more human」「more AI-like」or a detector score remain invalid. Reviewers do not merge drafts. If every candidate repeats a major performance sentence or breaks the chain, choose「一篇都不要」. Only the frozen winner becomes `draft.md`.

The 40-minute lane ends at a fact-checked-enough text handoff; image generation, layout, upload, and publication are outside that clock. When images are also in scope, start the visual lane concurrently during research. Never skip time-sensitive facts, numbers, identities, or quotes to meet the clock; narrow the scope, downgrade the format, or tell the user that the task needs the slow lane.

Candidate fact / skeleton checks and the three-part selection do not certify final prose. Hooks, first person, the red corpus, and the clumsy-writing Prompt remain optional repairs after selection. Run one complete human-voice and AI-pattern diagnosis only on the winner at `editorial_review`; after repair, recheck only the recorded repair points. None of these can supply the article's value.

### 5. Hard-gate layer

- At `fact_checked`: verify time-sensitive facts, numbers, names, quotes, identities, comparison settings, and fact / inference labels.
- At `editorial_review`: run Pass A, one winner-only rhythm / pragmatic diagnosis, independent cold read, post-cold-read narrative-chain mapping, and candidate-to-draft concrete-detail diff. Repair confirmed defects, then recheck only repair points.
- Before `ready`: run the project lexicon appendix once, then sentence-level copyedit on the exact body; verify rights, privacy, credentials, platform rendering, state, and authorization; finally run the validator.

Hard gates decide whether a draft can advance; they do not decide what the article should think or how many sections it should contain. Do not use keyword counts or detector scores as authorship gates. The WeChat `ban_entry_ids` list is a one-time terminal project-style appendix driven by user feedback; it may block publication copy, but never accuse an author of AI use. Red-corpus absence never blocks a draft, and red examples are not templates or minimum hit targets.

### 6. Prepare delivery

Keep `draft.md` as the editorial source. Choose one route:

- `company_browser`: APPSO company extension after current-task authorization.
- `manual_editor`: versioned local handoff; no API write.
- `sealed_draft`: dry-run first, then create one WeChat draft only after explicit authorization.

No route publishes or mass-sends automatically.

### 7. Capture material feedback

When delivery, publication, or a substantive revision is confirmed, update the package retrospective. Keep ordinary one-off wording in the case. An explicit owner rejection of WeChat expression may update `PROJECT-WECHAT-AI-LEXICON-001` immediately because it is the project's target loss. An explicit owner preference may update `PROJECT-WECHAT-RED-CORPUS-001` only with its content trigger, information job, and anti-stencil boundary. Label both as project preferences rather than universal rules.

## Validate

Run only the checks required by the current stage. Before `ready`:

```powershell
python .agents/skills/self-media-ops/scripts/validate_content_package.py <content-package>
```

Fix every error. Warnings need review but do not automatically block an early-stage draft.

## External actions

Local research, writing, organization, preview, and dry-run are allowed. Publishing, messaging, scheduling, browser draft overwrite, or any external account change requires explicit authorization in the current task.
