---
name: insight-to-asset
description: Turn a strategic observation or core insight into a scoped, falsifiable hypothesis, a bounded experiment, evidence updates, and a reusable workflow asset. Use when Codex needs to operationalize an abstract idea, test whether a feedback loop compounds, design a measurable proof-of-work cycle, review an active insight experiment, or migrate a supported mechanism without treating a personal interpretation as established fact.
---

# Insight To Asset

Convert an idea into evidence and an artifact. Keep the claim narrower than the ambition: this repository can test self-media workflow mechanisms, not prove a person's career ceiling or a universal theory of AI competition.

## Load the experiment context

1. Locate the workspace root containing `AGENTS.md` and read its project boundary.
2. Read `上下文/当前重点.md`.
3. Read `共享/研究/洞察实验室/README.md`, `洞察台账.yml`, and the active insight record.
4. Follow record links to the original brief, retrospective, evidence, or workflow asset. Do not copy raw feedback into the laboratory.
5. Read [references/insight-contract.md](references/insight-contract.md) before framing, evaluating, or assetizing a claim.
6. When an experiment uses a content cycle, also use [self-media-ops](../self-media-ops/SKILL.md). When a result may change an SOP, use [content-retrospective](../content-retrospective/SKILL.md) and its promotion gate.

## Choose the operation

- **Capture**: preserve a useful observation without implying that its mechanism is true.
- **Frame**: define the claim, scope, mechanism, exclusions, prediction, failure condition, and alternative explanations.
- **Prepare an experiment**: freeze the comparison, metric definitions, success threshold, guardrails, and end condition before execution.
- **Review evidence**: classify every result as `supports`, `contradicts`, or `neutral`; record missing data instead of guessing it.
- **Decide**: choose a scoped support, refinement, rejection, or another test. One successful cycle does not prove a general claim.
- **Assetize**: point to the authoritative checklist, template, script, Skill, or product change and test whether another Session can use it.
- **Migrate**: keep the claim and validation contract portable; move brand, platform, paths, metrics, rights, and approvals into an adapter.

## Run the loop

1. Separate what was observed from the explanation proposed for it.
2. Rewrite the idea so that one repository-scoped experiment could make it weaker, not only stronger.
3. Name the comparison and plausible alternatives such as task difficulty, operator practice, model changes, or extra planning time.
4. Select one primary metric. Track quality, rights, facts, privacy, and external actions as guardrails. Do not hide them in a composite score.
5. Keep at most one experiment in `running` state across the laboratory.
6. Execute the content work through the existing production workflow. Preserve original evidence at its source and link to it.
7. At the end condition, compare against the frozen threshold before changing the threshold. Count the maintenance cost of the new workflow.
8. Update the evidence level and decision. Negative and inconclusive results remain useful because they narrow the claim.
9. Create or update a reusable asset only after the result justifies it. An SOP promotion still requires the retrospective evidence ladder and regression contract.
10. Set `next_review_on`, validate the laboratory, and commit the complete evidence unit without publishing or contacting anyone.

## Use the deterministic entry

Run from the repository root. Initialize all pinned workflow dependencies once in a fresh checkout:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/bootstrap.ps1
```

Create a record without overwriting an existing insight:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 insight new `
  --id INSIGHT-002 `
  --slug concise-slug `
  --title "洞察标题" `
  --statement "可被现实削弱的命题" `
  --scope "本轮适用范围" `
  --owner strategy_editor `
  --next-review-on 2026-08-01
```

Inspect before writing with `--dry-run`. Validate records and show due reviews with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 insight validate
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 insight status --as-of 2026-07-22
```

The script scaffolds and validates structure; it never invents evidence, evaluates a result, changes an SOP, publishes content, or sends an external message.

## Protect the boundary

- Keep personal comparisons and identifiable career judgments outside this company content repository. Store only the sanitized operational mechanism that the project can test.
- Treat access to company feedback as permission-bounded. Owning a feedback loop does not mean owning restricted copy, analytics, contacts, or brand assets.
- Central records may contain public, public-derived, internal, or restricted-index references. Full restricted material stays at its governed source.
- Do not infer missing time, performance, or audience data. Mark it unavailable and choose a metric that can be collected prospectively.
- Do not read external research projects to strengthen the claim unless the user explicitly brings them into scope.
- Do not publish, schedule, message, or change an external account without current-task authorization.

## Finish

Report the narrowed claim, current evidence level, active experiment, falsifier, produced asset, unresolved alternatives, next review date, validation result, and Git status.
