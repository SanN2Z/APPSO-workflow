# WeChat writing team

Use a manager-led workflow with six roles. Keep the team small: specialization is useful only when roles own different decisions or verification surfaces.

## Roles

- [Managing editor](wechat-role-managing-editor.md): own the reader promise, single hook, argument architecture, assignments, and state decisions.
- [Evidence editor](wechat-role-evidence-editor.md): own sources, claim decomposition, factual labels, and the release fact card.
- [Feature writer](wechat-role-feature-writer.md): own the only editable body draft, title candidates, plain-language translation, rhythm, and ending.
- [Copy editor](wechat-role-copy-editor.md): own sentence-level grammar, syntax, reference, punctuation, terminology, and the exact final body hash.
- [Visual and rights editor](wechat-role-visual-rights-editor.md): own publication assets, captions, mobile readability, privacy, and rights status.
- [Release auditor](wechat-role-release-auditor.md): independently grade the package, run the detect-only AI-pattern diagnostic, record defects, run deterministic validation, and recommend pass or repair.

Do not create a separate title agent, style-rewrite agent, conclusion agent, or debate panel by default. Those concerns belong to the managing editor and feature writer. The copy editor is a narrow correctness gate, not a second stylist or co-author.

## Required context

Every role reads the root and platform instructions, `上下文/当前重点.md`, the context relevant to its assignment, `微信公众号/CONTEXT.md`, and the target package. The managing editor additionally loads user or editor feedback. Do not copy long-lived rules into role prompts; link to the source so they do not drift.

## Modes

- **Standard**: use all six roles for a new article or structural rewrite.
- **Research only**: managing editor + evidence editor; stop at `research`.
- **Rewrite**: managing editor + evidence editor for changed claims + feature writer + copy editor + release auditor; add visual editor when images or captions change.
- **Fast edit**: feature writer + copy editor + release auditor only when structure, claims, sources, and assets are unchanged.

If uncertain, use Standard. Never use Fast to bypass fact, rights, or state gates.

## Workflow

1. The managing editor writes or refreshes `brief.md`, including the reader blind spot, one-sentence promise, one primary hook, required background, argument map, counterpoint, and ending job.
2. The evidence editor and visual editor may work in parallel. The evidence editor writes `sources.md` and `research/fact-sheet.md`; the visual editor inventories assets and rights.
3. The managing editor locks the brief only after the evidence needed for the opening fact card and core argument is usable.
4. The feature writer becomes the sole writer of `draft.md`. Other roles report defects without editing the body concurrently.
5. The evidence editor verifies changed claims and the visual editor verifies final image use in parallel. They do not rewrite prose.
6. The release auditor runs [wechat-ai-pattern-pass.md](wechat-ai-pattern-pass.md) in `detect` mode, then reads the package cold, grades the structural and reader-facing gates, and writes `HUMAN-AI-*` plus other defects in `review.md`. The auditor does not rewrite the body or use an AI-detector score as a gate.
7. The feature writer performs targeted repairs; the evidence editor rechecks any changed meaning. The release auditor re-runs the diagnostic and cold-read checks until no blocking or major defect remains.
8. Only after those repairs, the copy editor runs [wechat-copyedit-pass.md](wechat-copyedit-pass.md) on the complete exact body, writes `copyedit.md`, and reports `COPY-*` defects without editing the draft. The feature writer repairs them, and the copy editor re-runs the whole body.
9. After a copyedit pass, the managing editor records the same body hash in `copyedit.md` and draft frontmatter. Any later body edit invalidates this gate.
10. The release auditor confirms the copyedit status and hash, runs the validator, and recommends state. The feature writer may perform at most two targeted repair rounds per gate; repeated material defects become blockers.
11. The managing editor updates frontmatter only when evidence, editorial, copyedit, and rights results support the state. Publication remains a user-controlled external action.

## File ownership

| File or area | Primary writer | Other roles |
|---|---|---|
| `brief.md`, `research/argument-map.md` | Managing editor | Comment through handoff |
| `sources.md`, `research/fact-sheet.md` | Evidence editor | Read only |
| `draft.md`, `research/title-lab.md` | Feature writer | Defect reports only |
| `copyedit.md` | Copy editor | Feature writer resolves listed defects in `draft.md` |
| `asset-manifest.yml`, `assets/`, `research/visual-notes.md` | Visual and rights editor | Read only |
| `review.md` | Release auditor | Repair owners resolve listed defects |
| frontmatter state, `publish-record.md` | Managing editor | Auditor recommends; user authorizes publication |

Never maintain parallel `draft-v2-agent-name.md` files. Preserve a single source of truth and use `review.md` for defect history.

## Handoff contract

End every role run with:

```text
STATUS: pass | needs_fix | blocked
OWNED_FILES:
BLOCKERS:
CHANGED_CLAIMS:
DEFECT_IDS:
HANDOFF_TO:
NEXT_ACTION:
```

Use defect prefixes `LEAD`, `FACT`, `WRITE`, `HUMAN`, `HUMAN-AI`, `COPY`, `VISUAL`, and `RELEASE`. A handoff is not a pass when unknowns are merely omitted.

## Evaluation contract

Use the fixed gates in [wechat-editorial-gates.md](wechat-editorial-gates.md), the human-reading method in [wechat-human-voice-pass.md](wechat-human-voice-pass.md), the Chinese-adapted diagnostic in [wechat-ai-pattern-pass.md](wechat-ai-pattern-pass.md), and the exact-version gate in [wechat-copyedit-pass.md](wechat-copyedit-pass.md), then add task-specific criteria from `brief.md` and explicit feedback. A model grader is advisory for long-form writing: retain deterministic checks and human review for subjective brand fit, rights uncertainty, and publication.
