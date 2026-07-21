# Research basis for the WeChat writing system

Accessed: 2026-07-10

There is no credible public benchmark that ranks complete writing skills, plugins, and agent teams across Chinese WeChat work. Use research-backed components and evaluate them on this project's own articles.

| Source | Finding used here | Design decision |
|---|---|---|
| [STORM, NAACL 2024](https://aclanthology.org/2024.naacl-long.347/) | Multi-perspective research before outlining improved organization and coverage over an outline-driven retrieval baseline; the paper also notes source-bias and over-association risks. | Let the evidence editor collect perspectives before the managing editor locks the outline; retain claim and source labels. |
| [WriteHERE, EMNLP 2025](https://aclanthology.org/2025.emnlp-main.1254/) | Long-form writing benefits from interleaving retrieval, reasoning, and composition instead of treating the outline as irreversible. | Permit the writer to hand evidence or structure gaps back upstream; do not improvise through a broken outline. |
| [WritingBench, 2025](https://arxiv.org/abs/2503.05244) | Writing evaluation spans many domains and benefits from query-dependent, criteria-aware rubrics. | Combine fixed platform gates with task-specific checks generated from the brief and editor feedback. |
| [FASTFACT, Findings of EMNLP 2025](https://aclanthology.org/2025.findings-emnlp.1295/) | Long-form factuality checking becomes more efficient by extracting claims in chunks, prioritizing uncertain claims, and using document-level evidence. | Maintain an atomic claim ledger and verify high-risk claims first; reject snippet-only support. |
| [LongJudgeBench, 2026](https://arxiv.org/abs/2606.01629) | Long-form LLM judges remain unstable across scenarios; rubrics and references help but are not always sufficient. | Keep the release auditor independent but advisory; retain deterministic checks and human judgment. |
| [Why Do Multi-Agent LLM Systems Fail?, 2025](https://arxiv.org/abs/2503.13657) | Multi-agent gains can be small; failures cluster around specification, inter-agent alignment, verification, and termination. | Use six non-overlapping roles, explicit file ownership, structured handoffs, defect owners, and bounded repair rounds. The sixth role was added only after a measured sentence-level failure escaped the original five. |
| [OpenAI practical guide to building agents](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/) | Maximize a single agent first; multi-agent systems add overhead and are justified by complex logic or tool/role overload. | Keep one managing editor and add specialists only for distinct verification surfaces. The copy editor checks correctness rather than creating another style or title agent. |
| [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | Simple composable workflows, evaluator-optimizer loops, and measured complexity are preferred over framework-heavy autonomy. | Implement a transparent local workflow through Markdown, content-package artifacts, and validation rather than a new framework. |
| [LangChain Open Deep Research](https://github.com/langchain-ai/open_deep_research) | Its maintained workflow separates summarization, research, compression, and final-report responsibilities; the repository keeps an older supervisor/multi-researcher implementation mainly as an alternative. | Borrow stage-specific responsibilities and evaluation, but do not install a research framework for a local editorial workflow. |
| [Microsoft AutoGen teams and termination](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html) | Team frameworks still recommend starting with a single agent and require explicit termination conditions for multi-agent loops. | Use role handoffs only where expertise differs, cap repair rounds, and record blockers rather than allowing open-ended debate. |
| [Anthropic public Agent Skills repository](https://github.com/anthropics/skills) | Skills package focused instructions and resources through progressive disclosure; plugins mainly distribute collections of capabilities. | Extend the existing project skill and load WeChat references only when needed. Do not add a plugin until distribution or external integration justifies it. |

## Local evaluation plan

Track three layers separately:

1. **Do not break things**: package validity, paths, state, secrets, and rights metadata.
2. **Do what the brief asks**: title promise, required facts, argument map, platform fit, and explicit feedback.
3. **Do it well**: cold-reader comprehension, voice consistency, evidence strength, mobile readability, and ending force.

Calibrate automated or model grading against human editor feedback. Add a regression case whenever a real article reveals a new failure mode.

## Copyedit regression case

On 2026-07-12, the Step Edge draft passed factual, structural, cold-read, and package validation gates but still contained six sentence-level defects: a stiff comparison, comma-stacked parallel questions, an unclear document reference, an unanchored `又`, a missing subject, and an overloaded model-size sentence. A separate Sonnet copyedit caught them. This establishes a local failure mode: comprehension-level review and deterministic package validation do not prove grammatical correctness.

Design response:

- add a narrow copy editor rather than another style writer;
- require sentence-by-sentence and aloud review of the exact final body;
- record `COPY-*` defects separately from structural `HUMAN-*` defects;
- bind the pass to a deterministic body SHA-256 so later edits automatically invalidate it;
- keep the release auditor responsible for checking the signed hash, not for claiming that cold reading covered grammar.

### Forward test after the copyedit gate

Two fresh read-only agents received the revised skill and one existing content package each, without the known-defect list.

- The Step Edge package initially produced 19 `COPY-*` defects. After repair, complete re-reads found 5 and then 2 residual defects before the fourth exact body passed. The passing hash was `760ec409…a36a0`; fact-sensitive repairs were independently rechecked.
- The Tibo quota package produced 34 `COPY-*` defects, including a private Typora absolute image path and reader-facing internal release notes. It was correctly downgraded from `ready` to `editorial_review`.
- A temporary stale-hash test changed one body sentence after a pass. The validator failed with `copyedit body hash is stale`, confirming that later body edits cannot silently retain `ready`.

Keep both packages as regression cases. A successful copyedit gate must find the open issues in the Tibo package, pass the exact Step Edge body, and reject any modified copy with the old hash.

## Initial forward test

On 2026-07-10, a fresh read-only agent received only the skill, team/gate references, and the current Tibo package. It correctly selected Standard mode, surfaced the framework, missing early fact card, and weak ending as the top owned defects, reconstructed the article's claim, and refused `ready` because major issues and `rights_checked: false` remained. Keep this package as the first regression case after the structural rewrite.
