---
name: feedback-to-system
description: Turn substantive feedback, recurring rework, delivery mismatches, or workflow gaps into a traceable case and decide whether to keep it local, make a scoped project configuration, run an experiment, or promote a reusable mechanism. Use automatically when an agent believes a real observation should change future content work, an AGENTS.md, SOP, Skill, template, validator, or automation; skip typos and ordinary one-off wording unless the owner explicitly makes them binding.
---

# Feedback to System

Convert feedback into one explicit disposition. Do not rely on conversational memory, and do not turn every correction into a global rule.

## Trigger automatically

Invoke this Skill without waiting for the user to name it when at least one signal is present:

- the user or editor says future work should follow the same preference;
- a delivered artifact reveals a missing gate, repeated rework, or a process mismatch;
- the same failure mechanism appears in two independent cases;
- an agent is about to change `AGENTS.md`, an SOP, another Skill, a template, validator, or automation because of a real case;
- a useful long-term judgment needs an experiment before it can become a rule.

Do not invoke it for a typo, isolated sentence repair, an unfinished task already tracked in the current plan, or an agent's unsupported hunch. An explicit owner-binding preference may still qualify after one case, but must remain a scoped project configuration.

## Capture before generalizing

Record the faithful feedback or a restricted pointer, date, source, affected artifact and workflow stage. Describe the reader or business harm and the likely mechanism separately from the requested wording.

When a content package exists, read [`content-retrospective`](../content-retrospective/SKILL.md) completely and use its smallest applicable mode. Keep raw feedback in the package `retrospective.md`; central ledgers receive only sanitized patterns and source IDs. Do not copy credentials, private analytics, restricted copy, or personal data into generalized records.

## Choose one disposition

| Disposition | Use when | Destination |
|---|---|---|
| `case_only` | One repair matters only to the current artifact | Target package or affected case record |
| `watch` | One plausible mechanism may recur | Case record plus a review date |
| `project_configuration` | The owner explicitly makes a preference binding for this repository, platform, brand, or content type | Narrowest authoritative adapter or project instruction |
| `experiment` | The claim is useful but its effect is uncertain | Read [`insight-to-asset`](../insight-to-asset/SKILL.md) and create a measurable asset |
| `sop_candidate` | Two independent cases support the same mechanism | Promotion review, not immediate global prose |
| `promoted` | The rule has an observable contract and passes regression plus counterexample checks | One authoritative SOP, Skill, template, or validator |
| `rejected` | Evidence is weak, scope is wrong, or the proposed rule causes larger harm | Case record with the reason |

If scope is clear, take the smallest safe action without asking a ceremonial question. Stop for direction only when choosing the scope would materially change unrelated work or require new authority.

## Promote through a contract

Before changing a shared workflow, read [`promotion-rules.md`](../content-retrospective/references/promotion-rules.md). Record:

- trigger;
- required action;
- observable pass condition;
- failure signal;
- scope and counterexample;
- source case IDs;
- regression check and review date.

Edit one authoritative source and leave pointers elsewhere. Do not duplicate full rules across root instructions, platform files, SOPs, and Skills. Tool or validator changes are warranted only when deterministic enforcement improves a real pass condition.

When changing a Skill, workflow entry, dependency, or versioned tool, apply `CORE-PORTABILITY-001` from the [core content workflow](../../../共享/运营/SOP/内容工作流.md). Preserve current authorization boundaries and unrelated dirty-tree changes.

## Verify the feedback loop

Run the narrowest relevant checks and test both directions:

1. Reproduce or inspect the source failure and show that the change would catch it.
2. Test a reasonable counterexample that should remain allowed.
3. Confirm restricted details were not generalized.
4. Record the disposition, actual repair, verification result, unresolved questions, and next review date.
5. Report what stayed case-only, what became project configuration, what was promoted, and the scoped Git status.

If no rule was promoted, say so explicitly. Capturing a case without changing an SOP is a valid outcome.
