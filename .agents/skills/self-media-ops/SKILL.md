---
name: self-media-ops
description: Operate a structured self-media workflow for X/Twitter and WeChat Official Account content. Use when Codex needs to research a topic, create or rewrite posts/articles, adapt one verified topic across platforms, organize a content package, manage sources and image rights, perform editorial review, or prepare content for human-approved publishing in the 自媒体运营 workspace.
---

# Self Media Ops

Use the project as a content operating system, not a loose folder of drafts.

## Load the right context

1. Locate the workspace root containing `AGENTS.md`, `上下文/`, `X/`, and `微信公众号/`.
2. Read root `AGENTS.md`.
3. Read `上下文/当前重点.md` plus the context files relevant to the request:
   - voice or rewriting: `作者声音.md`
   - research or claims: `事实与引用规范.md`
   - images: `视觉与版权规范.md`
   - cross-platform work: `平台差异.md`
   - strategy: `品牌定位.md` and `运营目标.md`
4. Read the target platform's `AGENTS.md` and `CONTEXT.md`.

Do not load unrelated research-project instructions unless the user explicitly brings that project into scope.

## Classify the task

- **New topic**: create a content package from a template.
- **Research**: build or update `sources.md`; do not manufacture a draft before the evidence is usable.
- **Draft or rewrite**: edit `draft.md` while preserving the package's sources and status.
- **Cross-platform adaptation**: create a separate package for the target platform; share verified facts, not final prose.
- **Editorial review**: record findings in `review.md` and update frontmatter only when requirements pass.
- **Publishing preparation**: for WeChat, read [references/wechat-publishing.md](references/wechat-publishing.md), build the local Wenyan preview, and keep draft creation dry-run unless the current task explicitly authorizes the external write.
- **Post-delivery or post-publication retrospective**: load [content-retrospective](../content-retrospective/SKILL.md), capture user and editor feedback in the content package, and update SOPs only after the promotion gate passes.

Read [references/content-package.md](references/content-package.md) when creating or restructuring a package. Read [references/review-checklist.md](references/review-checklist.md) before changing a draft to `ready`.

For a WeChat new article, research package, rewrite, or full editorial review, also read [references/wechat-team.md](references/wechat-team.md). It defines the manager-led writing team, file ownership, handoffs, and stopping rules. Read [references/wechat-editorial-gates.md](references/wechat-editorial-gates.md) before approving the brief or final copy.
For drafting, rewriting, or voice polishing, read [references/wechat-human-voice-pass.md](references/wechat-human-voice-pass.md) and [references/wechat-ai-pattern-pass.md](references/wechat-ai-pattern-pass.md). Run the writer self-pass, the Chinese-adapted detect-only AI-pattern diagnostic, repairs, and the independent cold-read pass in that order. The diagnostic uses the globally installed `avoid-ai-writing` skill as a supplemental checklist; it is not a detector-score gate or an automatic rewrite command.
Before any draft can become `ready`, read [references/wechat-copyedit-pass.md](references/wechat-copyedit-pass.md) and run its sentence-level grammar gate on the exact final body. Do not treat cold-read comprehension or validator success as a substitute for copyediting.

## Run the workflow

1. **Brief**
   - Define reader, one-sentence angle, desired takeaway, deadline, required facts, and exclusions.
   - Mark unknown brand or business decisions as unresolved instead of inventing them.

2. **Research**
   - Browse for current claims whenever prices, models, rankings, policies, roles, dates, or “latest” information appear.
   - Prefer primary sources. Use independent evaluations to challenge vendor claims.
   - Record what each source supports, its type, access date, and limitations in `sources.md`.
   - Separate fact, vendor self-report, third-party result, inference, and joke/commentary.

3. **Assets**
   - Keep publication assets in `assets/`; put unused originals and superseded versions in `research/source-assets/`.
   - Register every asset in `asset-manifest.yml`.
   - Do not mark rights as cleared merely because a file was supplied by the user.
   - Keep attribution near official images and social screenshots.
   - Follow the project [Image2 generation workflow](<../../../共享/运营/SOP/Image2 生图工作流.md>). Use Codex built-in `image_gen` directly; the runtime was verified against official OpenAI documentation as `gpt-image-2` on 2026-07-21.
   - For the project clumsy-scribble redraw, load the exact internal prompt asset under `APPSO-数字资产/01-栏目与品牌/品牌视觉/生图-Prompt/`; keep output constraints separate from the verbatim style prompt.
   - Do not attempt a referenced-image edit when the referenced image is unavailable in the current conversation or workspace. Ask the user to attach it again.
   - Inspect the result at original resolution, iterate with one targeted change at a time, then save the selected output in the target package, label it as AI-generated, and record both the input-image rights and generation details.
   - Use asset manifest `version: 2` for new or materially edited packages. Record generation mode, governed prompt hash, run constraints, input assets, runtime, model, and generation date. Missing release-bound metadata may remain visible as warnings during drafting but blocks `ready`.

4. **Draft**
   - Write for the target platform rather than mechanically shortening or expanding another platform's copy.
   - Use natural Chinese by default. Lead with the useful scene or judgment.
   - Remove repeated explanations, template transitions, empty conclusions, and numbers that do not change the story.
   - Preserve meaning when translating jokes or quotes; never turn inference into confirmed motive.

5. **Human voice and AI-pattern review**
   - Run the feature writer's human-voice self-pass first.
   - Run `avoid-ai-writing` in `detect` mode with the Chinese adaptation in `wechat-ai-pattern-pass.md`; record `HUMAN-AI-*` defects in `review.md` instead of rewriting automatically.
   - Let the feature writer repair confirmed defects, then re-run the diagnostic and the independent cold read.
   - Do not use English vocabulary lists, stylometric thresholds, or a detector score as a Chinese quality gate.

6. **Sentence-level copyedit**
   - Check the exact final body for grammar, comparison structure, parallel clauses, referents, connector anchors, punctuation, and terminology.
   - Record `COPY-*` defects in `copyedit.md`; the copy editor reports and the feature writer repairs.
   - Store the passing body SHA-256 in both `copyedit.md` and draft frontmatter. Any later body edit invalidates the pass.

7. **Review and state**
   - Build a task-specific rubric from the brief, user feedback, and fixed platform gates. Do not rely on a generic "writing quality" score.
   - Update `review.md` with completed and unresolved checks.
   - Use only the states defined in root `AGENTS.md`.
   - Do not use `ready` while facts, links, image rights, blocking/major `HUMAN-AI-*` defects, copyedit, or required platform checks remain unresolved.
   - Do not use `published` without a real publication URL or explicit user confirmation.

8. **Validate**
   - In a fresh checkout, install the pinned parser dependencies once:

     ```powershell
     python -m pip install -r .agents/skills/self-media-ops/requirements.txt
     ```

   - Run:

     ```powershell
     python .agents/skills/self-media-ops/scripts/validate_content_package.py <content-package-path>
     ```

   - Fix every reported error. Warnings require review but do not necessarily block a draft state.

9. **WeChat preview and draft handoff**
   - Keep `draft.md` as the editorial source and put API-specific title, cover, digest, and Wenyan theme in `publish.yml`.
   - Generate `dist/wechat-preview.html` locally with the pinned Wenyan CLI. Review the phone-width preview; generated `dist/` files are disposable artifacts, not new sources of truth.
   - Run the draft command without `--execute` first. It must pass the package validator, `ready` state, fact/rights/copyedit flags, API field limits, and cover rights gate.
   - Only after explicit current-task authorization, call `draft --execute`. This may upload body images and a permanent cover, then create one WeChat draft. It must never publish or mass-send.

10. **Retrospective and SOP evolution**
   - When delivery, publication, feedback, or a requested revision is confirmed, create or update `retrospective.md` with the `content-retrospective` skill.
   - Preserve the user's requested changes and the actual repair in the package; central ledgers receive only sanitized cross-case patterns.
   - Keep one-off wording and temporary decisions in the case. Promote repeatable mechanisms to the narrowest SOP with a regression check.
   - Run weekly due-review triage and a monthly SOP health review using the project retrospective schedule.

## External-action boundary

Drafting, local organization, source checks, and dry-runs are allowed. Posting, replying, liking, following, messaging, scheduling, or changing an external account requires explicit authorization in the current task. Log any authorized external action.

## Resources

- [references/content-package.md](references/content-package.md): required files, frontmatter, and state rules.
- [references/review-checklist.md](references/review-checklist.md): shared and platform-specific release checks.
- [references/wechat-team.md](references/wechat-team.md): reusable WeChat writing team and handoff protocol.
- [references/wechat-editorial-gates.md](references/wechat-editorial-gates.md): fixed and task-specific WeChat quality gates.
- [references/wechat-human-voice-pass.md](references/wechat-human-voice-pass.md): cold-reader comprehension and anti-template-language pass.
- [references/wechat-ai-pattern-pass.md](references/wechat-ai-pattern-pass.md): Chinese-adapted, detect-only use of the global `avoid-ai-writing` skill.
- [references/wechat-copyedit-pass.md](references/wechat-copyedit-pass.md): exact-version grammar, syntax, reference, and body-hash gate.
- [references/wechat-publishing.md](references/wechat-publishing.md): Wenyan-based local preview, developer credentials, draft dry-run, and external-action boundary.
- [references/wechat-writing-research.md](references/wechat-writing-research.md): research basis; read only when evolving or evaluating the team.
- `scripts/validate_content_package.py`: deterministic local package validation.
- `requirements.txt`: pinned semantic Markdown and CSS parser dependencies for validation.
- [content-retrospective](../content-retrospective/SKILL.md): feedback capture, post-publication review, SOP promotion, and workflow migration.
