# Editorial review checklist

## Shared checks

- Re-open time-sensitive sources at the draft's `as_of` date.
- Verify names, roles, quotes, dates, time zones, prices, percentages, and comparison settings.
- Label vendor self-report and inference honestly.
- Confirm every Markdown image resolves inside the package.
- Confirm every image appears in `asset-manifest.yml` with a usable rights status.
- Scan for credentials, private audience data, temporary paths, and accidental personal information.
- Read the copy aloud; remove duplicated points and generic AI transitions.
- Run the Chinese-adapted AI-pattern diagnostic in `detect` mode before copyedit. Record its scope, applied rule groups, ignored English-only rules, and any `HUMAN-AI-*` defects in `review.md`; do not use a detector score as a gate.
- Run the separate sentence-level copyedit gate on the exact final body. Check complete subjects, parallel comparisons, clause hierarchy, referents, connector anchors, terminology, and overloaded technical sentences.
- Confirm `copyedit.md`, draft frontmatter, and the validator report the same body SHA-256.
- Confirm title and opening deliver the same promise.
- Keep status below `ready` when any blocking item remains.

## X

- One central idea per post.
- Current source or original-post context is available.
- CTA is relevant and not repetitive.
- No bulk or deceptive engagement pattern.
- External actions remain dry-run until explicitly approved.

## WeChat Official Account

- Story has a clear throughline rather than a stack of summaries.
- Charts explain their data source and comparison limits.
- Wide images remain readable on a phone.
- Social screenshots preserve context and required privacy treatment.
- Official images keep attribution and receive a final rights review.
- Markdown uses package-relative image paths.
- No blocking or major `HUMAN-AI-*` defect remains open.
- No open `COPY-*` defect remains; captions and final notes were included in the copyedit scope.
- `publish.yml` has an API-safe title, explicit registered `project_adapter`, explicit `delivery_mode`, a compatible `layout_profile`, and a rights-cleared cover.
- The pinned Wenyan renderer generated `dist/wechat-preview.html`; title, headings, lists, captions, and wide images were checked at phone width.
- For `manual_editor`, the `handoff` command completed with no blocker, the versioned copy source contains every local image, and API draft commands are rejected.
- For `sealed_draft`, the draft command completed its default dry-run with no blocker. `--execute` remains a separately authorized external write; the explicit credential file and displayed account fingerprint were checked, and any execute-time failure triggers a backend/material-library inspection before retry.
- For an approved `company_browser` execution route, `publish-record.md` identifies the restricted company final, exact extension version, explicit brand selection, target draft and permitted image mapping. The write has current-task authorization, only one editor tab is open, every warning is treated as a failure, the saved draft is reopened and checked, and the extension cache is cleared afterward.
- After manual copy or API draft creation, a human checks the real WeChat editor result before any publish or mass-send action; do not mark a mode backend-validated before copy/edit/save/reopen or draft/save/reopen passes.
