---
name: content-retrospective
description: Capture substantive content feedback, delivery or publication outcomes, version diffs, audience evidence, and production failures; keep one-off changes in the case and promote only repeatable mechanisms into the narrowest SOP. Use after material feedback, delivery, publication, scheduled weekly or monthly review, or an explicit workflow-migration request.
---

# Content Retrospective

Record evidence without turning every edit into a new rule.

## Choose the smallest mode

| Mode | Use when | Load |
|---|---|---|
| Quick intake | One substantive user or editor correction arrives | Target package and its `retrospective.md` only |
| Cycle review | A draft was delivered or published | Brief, delivered/final versions, feedback, assets, and available results |
| Weekly review | Feedback or review dates are due | Schedule and active ledger items only |
| Monthly review | SOP duplication, conflicts, stale rules, or migration candidates need review | Schedule, ledgers, affected SOPs, and [promotion rules](references/promotion-rules.md) |
| Migration review | Export a reusable workflow | Core flow, adapters, evidence links, and [promotion rules](references/promotion-rules.md) |

Typos, punctuation fixes, and isolated wording choices can stay in the existing case history; they do not require a full retrospective or central ledger update.

## Capture the feedback

Use `scripts/init_retrospective.py <content-package>` only when a package needs a new record. Never overwrite an existing one.

For each material item, preserve:

- stable ID, date, source, and workflow stage;
- faithful feedback or a restricted source pointer;
- requested change and reader or business harm;
- likely mechanism, actual repair, and verification;
- confidentiality and disposition: `case_only`, `watch`, `sop_candidate`, `promoted`, or `rejected`.

Keep faithful detail in the package. Central ledgers receive only a sanitized pattern and source IDs.

## Explain the mechanism

```text
symptom
→ harm
→ mechanism
→ repair
→ verification
→ scope and counterexample
```

Separate failures in the brief, evidence, structure, prose, visuals, copyedit, handoff, rendering, publication, or measurement. A late rewrite may reveal an earlier process problem.

## Promote sparingly

Read [promotion-rules.md](references/promotion-rules.md) only when considering an SOP change or migration.

- One preference or one-off wording: keep in the case.
- One plausible failure: watch.
- Two independent cases with the same mechanism: consider a scoped rule.
- Facts, rights, privacy, credentials, publication, or irreversible actions may use the severe single-case exception.

Every promoted rule needs a trigger, action, pass condition, failure signal, scope, source cases, and regression check. Edit one authoritative source and link to it; do not repeat the rule across root instructions, Skill, platform files, and brand SOPs.

## Validate

When files changed:

1. Re-run the relevant package or script checks.
2. Confirm the rule would catch the source failure.
3. Test a counterexample.
4. Confirm restricted details were not copied into generalized docs.
5. Record unresolved questions and the next review date.

Use `scripts/audit_retrospectives.py --root <repository>` only for scheduled review or an explicit audit, not for every feedback item.

## Finish

Report what was captured, what stayed case-only, what was promoted, validation results, the next review date, and Git status.
