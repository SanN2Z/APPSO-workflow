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
- `publish.yml` has an API-safe title and an explicit, registered, rights-cleared cover.
- The pinned Wenyan renderer generated `dist/wechat-preview.html`; title, headings, lists, captions, and wide images were checked at phone width.
- The draft command completed its default dry-run with no blocker. `--execute` remains a separately authorized external write.
- After API draft creation, a human checks the real WeChat draft before any publish or mass-send action.
