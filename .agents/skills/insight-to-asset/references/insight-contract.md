# Insight experiment contract

## Purpose and ownership

The experiment laboratory sits above individual content cycles and below long-term strategy:

```text
observation
→ scoped hypothesis
→ prospective experiment
→ content cycle
→ retrospective evidence
→ claim decision
→ reusable asset
→ transfer and recurrence check
```

`content-retrospective` remains the source of truth for feedback-to-SOP promotion. The laboratory asks whether a broader mechanism survives multiple cycles; it does not duplicate raw feedback, content-package state, or SOP rules.

Operational ownership of a feedback loop requires legitimate access to six capabilities:

1. **Goal**: define the outcome and quality standard.
2. **Observation**: receive real user, editor, platform, or execution feedback.
3. **Memory**: preserve evidence with provenance and confidentiality.
4. **Update**: change the workflow, rule, tool, or decision.
5. **Execution**: apply the update in another real cycle.
6. **Portability**: reuse the sanitized mechanism without exporting restricted material.

Missing one capability is an experiment constraint, not something to conceal. Access to feedback does not transfer the rights to company copy, analytics, contacts, credentials, or visual assets.

## State and evidence are separate

Use these record states:

| State | Meaning |
|---|---|
| `captured` | An observation exists; mechanism is not framed. |
| `framed` | Scope, mechanism, prediction, and failure condition exist. |
| `test_ready` | Baseline, metrics, guardrails, and end condition are frozen. |
| `running` | The prospective experiment has started. |
| `evaluated` | Results are recorded but the disposition is being decided. |
| `supported_scoped` | Evidence supports only the declared scope. |
| `refined` | The original mechanism or scope changed and needs another test. |
| `rejected` | The current prediction failed or guardrails regressed. |
| `assetized` | A reusable artifact exists with an authoritative source and check. |
| `monitoring` | The artifact is being checked for recurrence, cost, and false positives. |
| `stable` | The asset has prospective support plus a counterexample or transfer check. |
| `reopened` | New evidence weakened a previously supported or stable mechanism. |
| `retired` | The asset is no longer worth using. |
| `archived` | No active work remains; the evidence trail is preserved. |

Reuse the retrospective evidence ladder:

- `E0`: observation, preference, or unverified interpretation;
- `E1`: one clear result with a plausible mechanism;
- `E2`: two independent cases or one mechanism reproduced across contexts;
- `E3`: prospective prevention plus a counterexample, recurrence, or migration check.

Evidence level never widens scope automatically. `supported_scoped` means「supported within the recorded conditions」, not universal truth.

## Claim contract

Each `insight.yml` must recover:

- stable ID, title, owner, classification, dates, state, and evidence level;
- one statement that could become weaker after a real result;
- explicit scope and exclusions;
- the proposed causal mechanism;
- a prediction and failure condition written before the experiment;
- plausible alternative explanations;
- supporting, contradicting, and unknown evidence;
- one or more bounded experiments;
- assetization target and authoritative references;
- decision history, next action, and next review date.

Keep observation and explanation distinct. For example:

```text
Observation: an editor requested the same layout repair twice.
Hypothesis: converting that feedback into a pre-handoff gate reduces recurrence.
Prediction: the next comparable handoff has no same-mechanism escape.
Alternative: the next article is simply easier to lay out.
Failure condition: the defect recurs or maintenance cost exceeds avoided repair.
```

## Experiment contract

Freeze these fields before switching an experiment to `running`:

- question and target population;
- baseline or control and its immutable reference;
- intervention and artifact version;
- controlled variables and known confounders;
- one primary metric with denominator and direction;
- threshold chosen before the result;
- secondary metrics and collection method;
- fact, quote, rights, privacy, copyedit, and external-action guardrails;
- end condition and stop conditions;
- evidence destination and decision vocabulary.

An experiment may be a paired draft, a prospective sequence of comparable content cycles, a transfer test by an isolated Session, or a migration test using a new adapter. Do not claim causal evidence from a before/after comparison when task difficulty, model, operator, source quality, or review intensity changed materially.

Classify every result as:

- `supports`: directly moves the predeclared prediction in the expected direction;
- `contradicts`: directly moves against it or breaks a guardrail;
- `neutral`: useful context that does not decide the prediction.

Record missing data as missing. Never reconstruct work minutes, audience results, or reviewer decisions from memory merely to fill a metric.

Each evidence item records `relation`, `ref`, and `note`. Decisive `supports` or `contradicts` items should also record a stable `case_id`. `E2` requires decisive evidence from at least 2 different `case_id` values. `E3` additionally requires at least one item marked `prospective: true` and at least one decisive item marked `counterexample: true` or `transfer_test: true`; prose saying「already validated」does not replace these fields.

Before moving a record to `test_ready` or an execution / evaluation state, replace the scaffold mechanism, prediction, failure condition, threshold, and end condition; bind a non-empty frozen baseline reference plus the intervention artifact and version. A direct `captured → archived` decision may preserve the scaffold because no empirical claim is being advanced.

## Metric families

Keep metrics interpretable rather than collapsing them into a single「compounding score」:

| Family | Example definition |
|---|---|
| Production | Same-mechanism defects divided by declared trigger opportunities. |
| Effort | Total measured minutes for planning, review, repair, and asset maintenance. |
| First-pass quality | Packages passing the frozen gate before delivery divided by eligible packages. |
| Guardrail | Open fact, quotation, rights, privacy, copyedit, or external-action blockers. |
| Loop health | Due experiments closed with a decision divided by due experiments. |
| Asset reuse | Independent cycles in which the exact asset was actually invoked. |
| Asset precision | Helpful triggers divided by all triggers, with false positives retained. |
| Transfer | Isolated Sessions completing the task by changing only the declared adapter. |
| Audience | Completion, saves, shares, or comments as exploratory outcomes, not sole causal proof. |

Always store numerator, denominator, collection window, and missing-data rule when using a rate. Include the cost of maintaining the new workflow.

## Decision and assetization gates

- One successful case can reach at most `E1` and `supported_scoped`.
- `supported_scoped` requires at least one decisive `supports` item; `rejected` requires at least one decisive `contradicts` item. Evidence volume alone does not choose the direction of the decision.
- A quality guardrail regression rejects the experiment even when it is faster.
- An inconclusive result narrows or redesigns the experiment; it is not a quiet success.
- An asset must have a trigger, action, pass condition, failure signal, scope, authoritative source, regression check, and retirement condition.
- SOP promotion goes through `content-retrospective/references/promotion-rules.md`; do not write a second copy of the rule in the insight record.
- A transfer test must give another Session the Skill and source artifacts, not the original conversation or intended answer.

## Confidentiality and migration

The portable core is the state machine, claim contract, evidence relation, experiment contract, decision gate, and asset contract. Adapters contain brand names, platform states, paths, metrics, approval owners, tools, and confidentiality labels.

Central records may link to restricted evidence by an approved index, but must not copy the material. Before migration, remove company paths and identifiers, replace them with adapter parameters, and demonstrate that the workflow still works on one public or synthetic counterexample.
