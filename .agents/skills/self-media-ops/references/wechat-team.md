# WeChat execution modes

Default to one operator and one editable draft. Roles are review lenses, not a standing six-agent team.

## Modes

| Mode | Use when | Operators |
|---|---|---|
| Quick edit | Claims, structure, assets, and state do not change | One writer |
| Standard | New article or ordinary rewrite | One managing writer; add one cold reviewer at `editorial_review` |
| High risk | Dense claims, uncertain rights, sensitive company material, or release preparation | Managing writer plus only the needed evidence, rights, copyedit, or release reviewer |
| Parallel | Research and asset work are independent and time-sensitive | Explicitly assigned specialists; never parallel-edit `draft.md` |

Do not spawn title, style, conclusion, debate, or generic review agents. If one operator can safely finish the task, use one operator.

## Context

Each operator reads only:

- root hard rules;
- target platform profile;
- assigned package files;
- the one reference required for its decision.

Do not make every reviewer load `当前重点.md`, all APPSO assets, publishing docs, or another role's instructions.

## Workflow

1. The managing writer fixes the reader question and affected scope.
2. Research and visual inventory may run in parallel only when both are genuinely needed.
3. An applicable analytical long-form article completes [the judgment workshop](wechat-judgment-workshop.md) before outlining.
4. One writer owns `draft.md`; reviewers report defects in `review.md` or `copyedit.md`.
5. Verify changed claims and changed assets, not the whole package after every small edit.
6. At `editorial_review`, one cold reviewer runs the human-voice and AI-pattern checks.
7. Before `ready`, run exact-body copyedit, rights review, platform checks, and the validator.
8. The managing writer updates state only when the recorded checks support it.

## Optional specialist lenses

- [Managing editor](wechat-role-managing-editor.md): central question, structure, scope, and state.
- [Evidence editor](wechat-role-evidence-editor.md): changed claims, sources, and factual labels.
- [Feature writer](wechat-role-feature-writer.md): sole body writer.
- [Copy editor](wechat-role-copy-editor.md): exact-body correctness and hash.
- [Visual and rights editor](wechat-role-visual-rights-editor.md): used assets, captions, privacy, and rights.
- [Release auditor](wechat-role-release-auditor.md): independent final gate.

Load a role file only when that lens is assigned.

## File discipline

- Keep one `draft.md`; never create agent-named parallel drafts.
- Use `review.md` for editorial defects and `copyedit.md` for exact-body defects.
- A reviewer does not silently rewrite another operator's owned file.
- Publication remains a user-authorized external action.

Use [wechat-editorial-gates.md](wechat-editorial-gates.md) as the single WeChat final checklist. Human voice, AI-pattern, copyedit, image, and publishing references are loaded only when their stage is reached.
