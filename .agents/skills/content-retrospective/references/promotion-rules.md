# SOP promotion and migration rules

## Evidence ladder

| Level | Evidence | Default treatment |
|---|---|---|
| E0 | One preference, wording choice, or unverified interpretation | Keep in the case by default; if the owner explicitly makes it binding, record a scoped project configuration without claiming general validity |
| E1 | One clear failure with a plausible mechanism | Add to watch list |
| E2 | Two independent cases with the same mechanism, or one case reproduced across contexts | Promote to a scoped rule |
| E3 | Rule prevents recurrence and passes a counterexample or regression check | Treat as stable SOP |

Safety, privacy, factual accuracy, rights, credentials, publication, and irreversible external actions may bypass the repetition requirement after one severe incident. They still need a precise trigger and pass condition.

## Promotion gate

Promote a lesson only when all applicable checks pass:

- The source feedback is faithfully recorded and traceable.
- The root mechanism is more specific than「写得不好」or「不够自然」。
- Evidence comes from independent cases, unless the severity exception applies or the change is explicitly labeled as an owner-binding project configuration rather than a portable claim.
- The rule names where it applies and where it does not.
- The rule does not expose restricted copy, people, analytics, or company-only decisions.
- The rule can be executed by another operator without seeing the original case.
- A pass condition and a failure signal are observable.
- A regression check, checklist item, script, or review question exists.
- The authoritative SOP is known and no duplicate rule is created elsewhere.

## SOP rule contract

Write promoted rules using this contract:

```yaml
id: stable-rule-id
trigger: when the rule applies
action: required operator behavior
pass_condition: observable completion criterion
failure_signal: evidence that the rule was missed
scope: platforms, content types, and exclusions
source_cases:
  - content package or feedback ID
regression_check: how recurrence will be detected
classification: public | public-derived | internal | restricted-index
owner: responsible workflow or role
introduced_on: YYYY-MM-DD
review_on: YYYY-MM-DD
```

The SOP prose may be more readable, but these fields must remain recoverable from the rule or its change ledger.

## Reject these upgrades

- Copying the editor's final sentence into a generic template.
- Turning one person's stylistic preference into a universal ban.
- Treating an owner-binding project preference as if it required academic proof before the current project can act on it.
- Writing a rule that says only「注意」「优化」「更有网感」or「加强审核」。
- Duplicating a root rule in every platform document.
- Promoting a metric change without confirming attribution and measurement consistency.
- Removing a useful exception just to make the checklist shorter.

## Generalization and migration

Split the workflow into two layers:

### Portable core

- lifecycle states and handoffs;
- evidence and feedback schemas;
- promotion gates;
- validation contracts;
- external-action and confidentiality interfaces;
- review cadence.

### Project adapters

- brand and platform names;
- directory paths and frontmatter fields;
- content types, roles, and approval owners;
- source tiers and visual rules;
- owner-approved voice preferences and project-only expression bans;
- repository visibility and classification labels;
- publishing tools and commands.

Before exporting, replace project paths and brand names with parameters, include a minimal adapter example, and remove restricted evidence. A generalized workflow must still say which decisions the adopter must configure.
