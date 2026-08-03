# WeChat execution modes

Default to the smallest mode that fits the task. New WeChat analytical drafts and structural rewrites use parallel full-draft candidates; quick edits and fixed factual formats still use one operator. Roles are concrete assignments, not a ceremonial standing team.

## Modes

| Mode | Use when | Operators |
|---|---|---|
| Quick edit | Claims, structure, assets, and state do not change | One writer |
| Standard factual | Fast news, fixed-format brief, translation, or ordinary local rewrite | One managing writer; add one cold reviewer only when needed |
| Parallel candidate | New analytical article or structural rewrite after the value gate | 3 isolated full-draft writers by default, up to 5 when real judgment branches exist; then 2 fresh selectors in parallel |
| High risk | Dense claims, uncertain rights, sensitive company material, or release preparation | Managing writer plus only the needed evidence, rights, copyedit, or release reviewer |
| Parallel specialist | Research and asset work are independent and time-sensitive | Explicitly assigned specialists; never parallel-edit `draft.md` |

Do not spawn separate title, style, conclusion, or per-section writers. Candidate writers each own one complete candidate; selectors have a frozen pairwise or pool-selection task. If one operator can safely finish an exempt task, use one operator.

## Context

Each operator reads only:

- root hard rules;
- target platform profile;
- assigned package files;
- the one reference required for its decision.

Do not make every reviewer load `当前重点.md`, all APPSO assets, publishing docs, or another role's instructions.

## Workflow

1. The managing writer researches enough to pass or reject the value gate without drafting a full article.
2. In a separate prewriting-calibration layer, submit the reader question, single core judgment, one-sentence story line, four-cell narrative chain, one narrative engine, strongest opponent and response beat, opening pressure, ending, omissions, and the concrete job of any planned high-salience rhetoric. Write provisional headings only after the chain works.
3. Apply the trigger and exemptions from `PROJECT-WECHAT-JUDGMENT-001`; applicable work completes [the story-contract gate](wechat-judgment-workshop.md) and freezes the user confirmation date before candidate work.
4. Start 3 candidate writers concurrently. Each reads the same frozen story contract and evidence packet, writes one complete anonymous candidate under `research/candidates/<round>/`, and cannot read another branch, share sentence-level plans, or inherit another branch.
5. Before freezing, each candidate writer records only two self-checks: compliance with the frozen fact boundary and no reuse of a ready-made skeleton outside `frozen-input.md`.
6. After all candidates freeze, start 2 new selector Agents concurrently. Each separately judges facts, argument / narrative with a rough narrative-chain check, and exact-quote evidence of cross-topic performance sentences, then chooses one candidate or none. A generic「more human」verdict is invalid. Disagreement triggers one final selector over the nominees. Generators never select.
7. Copy the frozen winner to `draft.md` without merging losing drafts. If all candidates repeat a major performance sentence or break the narrative chain, select none and return to the layer that caused it.
8. Verify changed claims and changed assets, not the whole package after every small edit.
9. At `editorial_review`, the writer runs Pass A; one auditor then runs a single rhythm / pragmatic diagnosis, performs the independent cold read, maps the finished draft back to the narrative chain, and checks the candidate-to-draft concrete-detail diff. After repair, the auditor rechecks only recorded repair points.
10. Before `ready`, run the project lexicon appendix once, then exact-body copyedit, rights review, platform checks, and the validator.
11. The managing writer updates state only when the recorded checks support it.

## 40-minute text lane

- Pre-T0: research, pass or fail the value gate, complete narrative and expression calibration, discuss the story contract, and wait for user confirmation.
- T0—8 minutes: run supplemental checks and freeze the user-confirmed story contract with the evidence packet.
- 8—22 minutes: 3 full-draft writers run in one concurrent wave.
- 22—28 minutes: 2 fresh selectors run in one concurrent wave and choose a winner or none.
- 28—38 minutes: verify only the frozen winner's necessary facts.
- 38—40 minutes: record hashes, elapsed time, and hand off readable text.

The deadline measures wall-clock draft time after user confirmation, not discussion waiting or summed Agent compute. Finishing early is allowed. Five candidates cannot extend the 40-minute limit; use them only when capacity and a real fourth or fifth execution route both exist. At minute 8, an evidence-to-story-contract mismatch means downgrade or stop. Images and layout run as a separate concurrent lane when requested.

## Optional specialist lenses

- [Managing editor](wechat-role-managing-editor.md): central question, structure, scope, and state.
- [Evidence editor](wechat-role-evidence-editor.md): changed claims, sources, and factual labels.
- [Feature writer](wechat-role-feature-writer.md): one complete candidate writer, or the post-selection owner of the winning body.
- [Copy editor](wechat-role-copy-editor.md): exact-body correctness and hash.
- [Visual and rights editor](wechat-role-visual-rights-editor.md): used assets, captions, privacy, and rights.
- [Release auditor](wechat-role-release-auditor.md): independent final gate.

Load a role file only when that lens is assigned.

## File discipline

- Keep one canonical `draft.md`. Parallel candidates are anonymous, round-scoped research artifacts rather than competing canonical drafts.
- Use `research/candidates/round-XX/candidate-a.md` through `candidate-e.md`; do not put Agent names in filenames or headings.
- Freeze candidates before selection. The selection record names the winner or none and preserves both raw reviewer choices.
- Use `review.md` for editorial defects and `copyedit.md` for exact-body defects.
- A reviewer does not silently rewrite another operator's owned file.
- Publication remains a user-authorized external action.

Use [wechat-editorial-gates.md](wechat-editorial-gates.md) as the single WeChat final checklist. Human voice, AI-pattern, copyedit, image, and publishing references are loaded only when their stage is reached.
