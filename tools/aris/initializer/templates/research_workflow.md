<!-- ARIS-WORKFLOW:BEGIN -->
# Shared research workflow for Claude, Codex, and Gemini

Version: 2026-10-19. User-adopted defaults, maintained by `aris-init`. Read alongside the project's state, research brief, prior attempts, and resource rules. Existing project requirements for preregistration, leakage prevention, reviewer models, Baton, deployment and spending continue to apply. This file assigns research roles; it does not reopen a frozen design or authorize a new production run.

## Roles and available channels

The user has Codex, Claude including **Fable**, and **agy (Antigravity)**. Explicit correction from the user on 2026-10-19: Gemini access in this workflow now uses **agy**, replacing the old Gemini CLI route. Use agy for the Gemini role; do not select the legacy `gemini` CLI as a default or automatic fallback. This is the user's routing preference, not a claim that the Google project is universally discontinued.

| Role | Preferred allocation | How to substitute |
|---|---|---|
| Research lead and conductor | **Claude/Fable**, when quota is available; maintain the question, decisions, context and handoffs | Codex/Astra can conduct during Claude quota exhaustion. Fable can participate in ideas, plans, experiments and writing; it is not excluded from any stage |
| Deep idea analysis, experiment decisions, independent critique | **Astra** working with Fable; use the project's exact reviewer model/effort when specified | Use the strongest available reasoner and disclose any substitution. Independent context matters more than a claimed panel consensus |
| Alternative hypotheses, broad exploration, prose drafting | **Gemini**, with Fable/Astra evaluating proposals and evidence | Fable or Astra can draft. A fluent or enthusiastic response is not validation |
| Code, data tooling, bounded batch execution | **Sol** by default, using Baton where the project requires it | Fable can execute suitable tasks, but existing coding/deployment ownership rules take precedence. **Grok is optional; Sol covers its execution slot** |
| Factual checks and result integrity | Codex checks source claims, code, logs and manuscript numbers; use independent review where it adds value | Reviewers receive primary artifacts and limitations, not only the author's interpretation |
| Final scientific and editorial judgment | Human researcher, supported by the above roles | Model agreement does not replace evidence or the human's final reading |

Names such as Astra, Sol, Fable, Opus and Gemini here are role/model labels from the user's workflow. Inspect the actual client/model selector before invoking a bridge. Do not guess API IDs, silently downgrade a mandated reviewer, or claim to have consulted an unavailable model. Do not install another provider just to fill an optional role.

Fable being available changes the original screenshot's access-constrained allocation: it may lead the whole workflow, with Astra as a strong decision partner and critic. Sol remains the economical default for the project's existing coding path. Current quota and observed task quality determine who performs the work; these assignments are not a universal model ranking.

## Gemini access through agy

- The 2026-10-19 native headless connectivity probe succeeded: `SUCCESS`, expected canary, init model `gemini-4-argon-high`, and CLI-selected label Gemini 4 Argon (High). This is a dated native-route check, not proof that an MCP tool is loaded or that future quota/network availability is guaranteed.
- agy is an installed host runtime. Resolve it from `AGY_BIN`, `.aris/runtime.local.json` or PATH; use `tools/workflow.ps1 gemini-writer` for the existing native route. Do not infer that it is absent merely because PATH does not expose it. Host paths and login state are local inputs, not portable source.
- On 2026-10-19, `agy --version` reported 1.4.2 and `agy models` listed `gemini-4-argon-high` / Gemini 4 Argon (High), also selected in local settings. Pass the intended model and effort explicitly and record actual returned/logged metadata. A configured label is not independent proof of a remote model.
- Prefer an already exposed ARIS `antigravity-exec` MCP with explicit `cwd`, `AGY_BIN`, model and effort. If this session has not loaded that MCP, direct agy headless calls can supply the independent Gemini role; report which route was actually used. Do not claim a registered tool merely because its server code exists.
- ARIS bridge defaults may name an older Flash model; do not silently substitute that default for the user's selected Gemini 4. Antigravity also lists non-Gemini models, which do not count as the Gemini role.
- Old ARIS instructions mentioning the standalone Gemini CLI are historical for this user's setup. If agy is unavailable, report the concrete blocker and use file handoff; switch providers/routes only on an explicit user instruction.
- While Fable quota is unavailable, Astra may conduct the refinement with agy/Gemini providing an independent proposal or critique. Preserve the project's exact reviewer model/effort and use a fresh review context rather than rating the conductor's own proposal as independently reviewed.

## 1. Ground the question, then explore ideas

Use `research-lit` / `research-wiki`, then `idea-discovery` or `research-refine` as the state requires. Continue an existing direction rather than restarting discovery by default.

- Start with the researcher's domain knowledge, papers, observations and intended capability. Read negative results and nearby attempts before proposing a new method.
- Fable/Astra formulate the problem and competing explanations. Gemini supplies alternative hypotheses and perspectives; it can also challenge the favored idea. Fable is welcome in this stage.
- When exploration benefits from breadth, split independent literature/candidate tasks across agents, then merge with deduplication and primary-source checks. Keep one coordinator and one decision record. Use enough breadth to answer the question, not a mandatory large agent count.
- Separate proposal generation from critique. Astra or another independent critic asks what is new, what is already solved, which assumption fails, and which small experiment would change the decision. Neither praise nor generic caution is sufficient.
- Filter ideas against actual related work and run the smallest premise check the project authorizes. Record rejected ideas and why. Do not choose complexity merely to look novel, or discard a useful idea because every possible risk has not been removed.

Output: a grounded problem, closest-work comparison, candidate mechanisms, unresolved assumptions and a decisive next check. Follow the project's existing artifact names; record evidence in the wiki and handoff.

## 2. Make a claim-driven experiment plan

Use `research-refine-pipeline` / `experiment-plan`. Fable leads synthesis; Astra helps make difficult experiment decisions. Opus or other available Claude models can contribute without becoming a required dependency.

Define the main claim, strongest simple alternative, relevant specialist, fair information/compute budget, independent acceptance data, failure interpretation and run order. Prefer experiments that distinguish explanations. Add parameter sweeps, ablations or robustness studies when they resolve a live uncertainty or support an actual claim; avoid automatic grids.

Apply the screenshot's **Hero / Anti-Overdefense** intent as a planning principle: state the critical risk, choose a bounded falsifying check, and proceed when the existing evidence and authorization support it. This file does not assert that a Hero skill is installed or grant permission for an unavailable plugin. Preserve project scientific gates and user-required protocol locks.

Output: a concrete experiment plan and tracker, with budgets and explicit claims. Model review scores are readiness opinions, not experimental results.

## 3. Implement and execute

Use `experiment-bridge` and the project's execution tools. Delegate code and bounded data/experiment tasks to Sol; use Baton where required. The conductor reviews the implementation against the plan and owns deployment, GPU allocation and registry changes where the project says so.

Give the executor a bounded task with input paths, intended behavior, output paths and a meaningful check. Verify controls, data isolation and raw artifacts before scaling. Preserve failed attempts and resource usage. Model access or a workflow preference does not reset a ledger or authorize extra paid calls.

If Fable/Claude quota is exhausted, Codex can continue already authorized work and produce a file handoff. Avoid consuming Claude quota merely to narrate routine logs. Ask only for genuinely missing decisions or permissions; do not reopen approvals already given in the session.

## 4. Read results before expanding the claim

Use `analyze-results` → `result-to-claim`, and the relevant integrity checks. Separate diagnosis quality, learning-decision value, student-weight gains, frozen-model harness gains, transfer, retention and cost as the project requires.

The critic receives raw results and the planned claim. Record supported, inconclusive and refuted claims, along with implementation or measurement limitations. Do not turn a fresh evaluation draw into a new training seed or a selected development curve into an independent test. Choose the next action from evidence, rather than adding components to rescue a story.

## 5. Draft and illustrate the paper

Use `paper-writing` after results support a coherent narrative. Gemini may lead prose drafting; Fable can coauthor, organize and edit. Codex checks factual statements, citations, numbers, comparisons and claim scope against primary sources and raw outputs. Astra can provide an independent scientific reading.

Aim for direct scientific prose with a clear problem, evidence and limitations; avoid excessive defensive paragraphs and unsupported promotional language. Use ARIS figure workflows for diagrams and standard plotting tools for quantitative figures. Native image generation (the screenshot suggests GPT Image) is optional for conceptual illustrations; verify actual tool availability. It must not fabricate scientific plots, measurements or evidence.

## 6. Human reading and durable handoff

The human closely reads the full paper/slides and edits the final argument. Model review is an aid to that judgment.

After a meaningful phase, update the project's state through its designated owner and save: decisions, sources, actual results, failed attempts, open questions, next action, resource state and read-first paths. Mirror concise durable pointers into the relevant project memory. Respect a rule that only Claude edits a particular Pipeline Status block; another client should leave a proposed status update in the handoff instead.

## Crossing clients without losing evidence

Use an existing authorized bridge when it is configured. Otherwise write a bounded task brief and accept the other client's response as an artifact. A useful handoff includes the question, primary input paths, required outputs, constraints, evidence standard and unresolved uncertainty. Never report a manual handoff as an automatically executed call.

Keep one canonical set of project artifacts. Claude, Codex and AGY should read this file plus the current handoff; chats alone are not project state. Do not assume AGY imports `CLAUDE.md` or `AGENTS.md`; open this shared file explicitly in that client unless its integration is verified.

## Provenance and interpretation

The user supplied two screenshots on 2026-10-19 and explicitly asked to adopt and improve the workflow. The first recommends Astra/Gemini idea work, strong-model planning, Sol/Grok execution, Gemini prose, Codex factual checking, ARIS figures and human final editing. The second says Claude's absence reflected access constraints and that Fable can be a main executor; it also recommends Astra's scrutiny during Gemini-assisted exploration.

We adopt complementary roles, not claims of an inherent Claude ideation deficit, universal Gemini sycophancy, or a proven ranking of model versions. The user specifically has Fable and accepts Sol in Grok's execution role. These additions supersede an interpretation that Claude must be absent from ideas or that Grok must be installed.
<!-- ARIS-WORKFLOW:END -->
