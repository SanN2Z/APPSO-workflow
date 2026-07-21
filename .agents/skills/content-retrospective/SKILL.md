---
name: content-retrospective
description: Turn content delivery or publication outcomes, editor and user feedback, requested revisions, version diffs, audience data, and production failures into structured retrospectives and continuously improved SOPs. Use after a draft is delivered or published, whenever feedback or revision requests arrive, when asked to learn from a content cycle or update a workflow, and during scheduled weekly or monthly reviews of content operations.
---

# Content Retrospective

Build an evidence trail from a concrete content cycle to a durable, testable workflow improvement. Preserve one-off feedback without turning every preference into a universal rule.

## Load project context

1. Locate the repository root and read its `AGENTS.md`.
2. Read the project-specific retrospective schedule and ledger if present.
3. Read the content package, delivery record, published version, feedback files, relevant SOPs, and any available performance data.
4. Read [references/promotion-rules.md](references/promotion-rules.md) before changing an SOP or exporting a generalized workflow.

Treat raw feedback, company final copy, unpublished analytics, contacts, and authorization records according to the repository's confidentiality rules.

## Choose the review mode

- **Cycle review**: Run after delivery or publication. Compare brief, draft, delivered copy, final copy, feedback, assets, and results.
- **Feedback intake**: Run whenever the user, editor, client, or reader provides a correction or requested change. Append it to the active retrospective before editing the SOP.
- **Weekly review**: Triage new feedback, close resolved actions, identify repeated patterns, and check overdue follow-ups.
- **Monthly review**: Audit SOP conflicts, recurring defects, stale rules, missing regression checks, and candidates for generalization.
- **Migration review**: Separate invariant workflow logic from brand, platform, path, status, and confidentiality adapters so the workflow can move to another repository.

## Create or update the cycle record

Use `scripts/init_retrospective.py <content-package>` to create `retrospective.md` without overwriting an existing record. Use `--dry-run` when only inspecting.

For every feedback item, record:

- a stable ID;
- source and date;
- workflow stage;
- faithful feedback or a restricted source path;
- the requested change;
- reader or business harm;
- likely root mechanism;
- applied repair and version;
- verification evidence;
- confidentiality;
- disposition: `case_only`, `watch`, `sop_candidate`, `promoted`, or `rejected`.

Keep the faithful detail inside the content package. Put only a sanitized pattern summary in a central cross-case ledger.

## Reconstruct the causal chain

Do not stop at a diff or at「更自然」「更顺」。For each material change, write:

```text
observed symptom
→ reader or workflow harm
→ root mechanism
→ repair
→ verification
→ scope and counterexample
```

Separate problems caused by the brief, evidence, structure, prose, visual rights, copyedit, handoff, platform rendering, publication, or measurement. A late-stage rewrite may expose an earlier process failure.

## Decide whether to change an SOP

Classify each lesson as:

- **Case fact**: useful only for this item, person, campaign, or wording.
- **Watch item**: plausible pattern without enough independent evidence.
- **Local rule**: repeatable inside one brand, platform, or content type.
- **General workflow rule**: portable across brands or platforms after adapters are removed.
- **Hard gate**: a fact, rights, privacy, security, publication, or irreversible-action safeguard that may be promoted after one severe incident.

Promote only when the lesson passes [references/promotion-rules.md](references/promotion-rules.md). Every promoted rule must define a trigger, action, pass condition, failure signal, scope, source cases, and regression check.

Edit the narrowest authoritative SOP. Do not duplicate the same rule across several files; link to the true source. Update the SOP version or date and its change ledger.

## Validate the improvement

Before closing a review:

1. Re-run the content-package validator when the package changed.
2. Test deterministic scripts or checks that were added.
3. Confirm the new rule would have caught the source failure.
4. Test one counterexample so the rule does not overfit.
5. Confirm confidential details were not copied into generalized docs.
6. Record unresolved hypotheses and the next evidence date.

Run `scripts/audit_retrospectives.py --root <repository>` to identify published packages without a retrospective and open reviews whose `next_review_on` is due.

## Maintain the cadence

- On delivery or publication: initialize the cycle record and capture known changes.
- When feedback arrives: append it in the same work session, then repair the content if authorized.
- About 7 days after publication: review early qualitative and quantitative evidence.
- Weekly: triage all open feedback and promotion candidates.
- Monthly: review SOP health and portable workflow candidates.

Scheduled automation may report overdue work, but it must not invent feedback, edit an SOP, publish content, or contact people.

## Finish

Return a concise summary containing:

- what changed in the content cycle;
- feedback captured and where;
- lessons kept as cases versus promoted;
- exact SOP changes and their evidence;
- unresolved questions and next review date;
- validation and Git commit status.
