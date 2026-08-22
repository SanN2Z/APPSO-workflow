# WeChat execution modes

Default to the smallest mode that fits the task. Research and independent specialist review may fan out; public prose follows one human-directed canonical writer line. L3 compares route cards before prose, not full drafts after prose. Roles are concrete assignments, not a ceremonial standing team.

## Modes

| Mode | Use when | Operators |
|---|---|---|
| L0 local | Claims, structure, assets, and state do not change | One operator |
| L1 factual | Fast news, fixed-format brief, translation, or source index | One managing writer |
| L2 standard analysis | One core judgment and story route clearly dominate | One canonical writer working by unit contract, then one fresh issue-first cold reader |
| L3 route decision | Competing substantive frames, central structural rewrite, flagship risk, explicit route comparison, or failed L2 center frame | One managing editor proposes up to 3 route cards; the user selects; then the L2 staged single-draft path |
| Parallel research | Open-ended sources, independent fact questions, or asset / rights research can be separated | Bounded researchers return evidence cards to one managing editor |
| Targeted review | Fact, argument, rights, copyedit, or release questions are independent | Reviewers report located problems and pass conditions; they do not rewrite `draft.md` |
| Explicit alternatives | The user explicitly asks for multiple complete versions | Separate version writers may work independently; the user selects and AI never votes or merges automatically |

Do not spawn separate title, style, conclusion, or per-section writers. One operator owns canonical prose at a time. Parallel researchers and reviewers return structured evidence or issue reports to that owner; they never edit the canonical body concurrently.

## Context

Each operator reads only:

- root hard rules;
- target platform profile;
- assigned package files;
- the one reference required for its decision.

Do not make every reviewer load `当前重点.md`, all APPSO assets, publishing docs, or another role's instructions.

## Workflow

1. The managing editor researches enough to pass or reject `CORE-VALUE-001`, then records the lane and reason under `CORE-LANE-001`.
2. For L2, lock the compact story contract and irreversible decisions in `brief.md`. For L3, propose up to 3 route cards under `CORE-ROUTE-001`; only the user can select, modify, or reject them.
3. Open `research/co-writing-log.md`. Record the collaboration mode, voice anchors, and one unit contract per section or high-impact paragraph. Adjacent ordinary paragraphs may share a section contract.
4. Assign each unit `human_first`, `ai_candidate`, or `critique_only`. Fact explanation and mechanism units may use one AI candidate; opening, ending, core judgment, and existing voice anchors default to human-first or critique-only.
5. After a user or designated human editor accepts a unit, label it `locked`. Reopen only for a fact error, demonstrated chain break, or explicit user request, and record the reason plus local diff.
6. The cold reader first reads only the public body. Report each issue with location, reader harm, reasoning, and pass condition. Do not silently rewrite the body or synthesize a new full draft.
7. The canonical writer proposes a local patch only for accepted issues. Preserve locked units unless their reopen condition is recorded; the reviewer rechecks only repaired points.
8. Verify changed claims and changed assets, not the whole package after every small edit.
9. Before `ready`, run the one complete rhythm / pragmatic diagnosis, the project lexicon appendix once, exact-body copyedit, rights review, platform checks, and the validator. Update state only when records support it.

## Timing

Record `T_intake`, `T_evidence_ready`, `T_contract_locked`, `T_first_text_handoff`, and `T_owner_reviewed`. Distinguish research time, text time, user waiting, and unavailable human minutes. Do not infer work time from token usage, chat duration, or Git timestamps, and do not sacrifice quality gates to preserve the retired 40-minute candidate experiment.

## Optional specialist lenses

- [Managing editor](wechat-role-managing-editor.md): central question, route cards, unit contracts, scope, and state.
- [Evidence editor](wechat-role-evidence-editor.md): changed claims, sources, and factual labels.
- [Feature writer](wechat-role-feature-writer.md): sole owner of the canonical body during an assigned writing window.
- [Copy editor](wechat-role-copy-editor.md): exact-body correctness and hash.
- [Visual and rights editor](wechat-role-visual-rights-editor.md): used assets, captions, privacy, and rights.
- [Release auditor](wechat-role-release-auditor.md): independent issue-first final gate.

Load a role file only when that lens is assigned.

## File discipline

- Keep one canonical `draft.md` and one `research/co-writing-log.md` for the active body.
- Historical `research/candidates/` rounds remain evidence only. New explicit complete versions go under `research/alternatives/` and remain non-canonical until the user selects.
- Record voice anchors by stable reference and information relationship; do not turn their surface words into a stencil.
- A reviewer does not silently rewrite another operator's owned file. A patch records the issue, old location, proposed diff, human decision, and result.
- Multiple review reports may be compared, but they are never auto-merged into prose and cannot outvote the user.
- Publication remains a user-authorized external action.

Use [wechat-editorial-gates.md](wechat-editorial-gates.md) as the single WeChat final checklist. Human voice, AI-pattern, copyedit, image, and publishing references are loaded only when their stage is reached.
