# Cold-reader and human-voice pass

The portable rule contract lives in [`共享/运营/SOP/内容工作流.md`](../../../../共享/运营/SOP/内容工作流.md). This file is its WeChat execution checklist; [wechat-ai-pattern-pass.md](wechat-ai-pattern-pass.md) is the detect-only specification.

Run two human-reading passes on the single L2 / L3 canonical draft. The feature writer performs Pass A while owning the draft. The release auditor then runs one complete rhythm / pragmatic diagnostic, reports `HUMAN-RHY-*` and `HUMAN-AI-*` defects, and performs Pass B cold without rewriting. These passes test reader path, voice, machine-shaped patterns, and argument reconstruction; they do not replace the sentence-level grammar gate in [wechat-copyedit-pass.md](wechat-copyedit-pass.md).

## Pass A: writer self-pass

Repair in this order:

1. **Remove the visible scaffold first**: Before polishing sentences, temporarily hide headings, numbers, transition labels, and section summaries. If the remainder becomes a news brief followed by an explainer and a slogan, or a set of equally weighted evidence cards, return to the story-beat table. Sentence-level variety cannot repair a missing narrative engine.
2. **First-screen pressure**: Can a reader follow the opening without the private outline? The first screen should show an actor or object in motion, or a supported result or decision that changes the reader's picture; it must also expose the unresolved pressure and the answer the article is pursuing. Delay biography, history, definitions, and secondary numbers until the reasoning needs them. Temporarily remove famous names, funding amounts, and hot terms: if no concrete tension remains, the draft has heat but no hook. A short fact bulletin may still begin with the event.
3. **Narrative dependency**: Do not order sections merely by source, company, research folder, chronology, or a research checklist. In a linear argument, each section should answer something left by the previous one and create a reason for the next. In a parallel comparison, sections may stand side by side when they share an explicit question, metric, or comparison scale. Write headings only after this relation works; headings should name a turn or judgment, not a topic bin. Temporarily hide the headings; if the reader can explain neither the sequence nor the parallel relation, repair the structure or split the topic.
4. **Paragraph jobs**: Compare each section or high-impact paragraph with its unit contract in `research/co-writing-log.md`: reader starting state, intended change, evidence or example, required limitation, and exit. Merge or delete paragraphs that only restate the previous one. Necessary definitions and lists may remain when readers must compare real categories or execute steps; do not use them to replace the argument.
5. **Plain language**: Translate jargon at first use. Replace abstract noun chains with a person, action, cost, interruption, or decision whenever accuracy allows.
6. **Natural transitions**: Remove template connectors such as “这意味着”“换句话说”“值得注意的是”“首先/其次/最后” when the logical relation is already visible. Prefer a concrete noun, question, actor, or consequence carried over from the previous paragraph. Write the relation itself when it is not visible.
7. **Rhythm by function**: Vary sentence and paragraph length according to meaning. A standalone short sentence should mark a real turn, correction, contrast, or consequence; a longer paragraph may carry evidence or mechanism. Do not force every section into the same cadence, impose a sentence-count quota, or end every section with a mini-summary.
8. **Voice continuity**: Compare an opening paragraph, a middle evidence paragraph, and the ending. They should sound like the same informed person, not “internet opening + report body + slogan ending”.
9. **Colloquial anchors**: Add or retain colloquial language only where it sharpens an author's judgment, makes an action visible, or states a reader consequence. Do not distribute slang evenly across sections. Delete it when removal loses no fact, stance, or comprehension.
10. **Optional contextual red moves**: Consult [wechat-red-black-corpus.yml](wechat-red-black-corpus.yml) only when current facts clearly support a more concrete move; zero use and no record are both valid.
11. **Pragmatic necessity**: Apply the authoritative `PROJECT-WECHAT-PRAGMATIC-001` contract in [the core workflow](../../../../共享/运营/SOP/内容工作流.md) to high-salience lines; do not restate or improvise a second checklist here.
12. **Rhetorical scarcity**: Reserve high-salience frames such as repeated “not A but B”, rhetorical reveals, or explanatory labels for distinctions that actually matter. Clustered frames dilute the thesis; rewrite rhythm-only repeats as direct statements. Do not ban a form when it performs a real logical exclusion, terminology distinction, sourced quotation, or problem model that continues to organize later evidence.
13. **Voice-anchor preservation**: Compare approved voice anchors and every `locked` unit with the current body. Preserve the information relationship and authorial choice; do not copy an anchor's connective words into unrelated sections or reopen it merely to make the whole article sound more uniform.
14. **Compression direction**: Apply `PROJECT-WECHAT-CONCRETE-001` after any compression or rewrite. Prefer removing abstract summaries, uplift lines, and repeated conclusions. If a real object, number, scene, failure, quotation, joke, or locked wording was changed, record the reason in `review.md` and `research/co-writing-log.md`; stop and restore the edit when the net effect is deleting concrete texture while retaining its abstract maxim.
15. **Humor discipline**: Keep jokes that sharpen a supported judgment. Remove jokes that need explanation, repeat the same beat, or change a person's meaning.
16. **Ending pressure test**: If deleting the final sentence makes the thesis stronger, rewrite or move that sentence. The ending must answer the same promise and add a consequence; do not introduce a new advice framework or checklist unless the brief promised one.

Do not use “add more slang” or “hit more red entries” as the default repair. Do not use AI-detector scores as a quality gate. Preserve sourced meaning; return factual changes to the evidence editor.

Brand-specific counts, banned phrases, and voice ranges belong in a project adapter, not in this portable pass. For WeChat, the red-black corpus defines strict black bans and optional contextual red moves; its examples do not become reusable copy. For APPSO, the calm-analysis adapter may define candidate colloquial landing points. In every case, the information-role and counterexample tests above still decide what remains in the article.

After Pass A, the release auditor runs the one-round diagnostic in `wechat-ai-pattern-pass.md`. The feature writer repairs confirmed findings; the auditor then checks only those repair points before starting the independent cold read.

## Common template-language defects

Flag with `HUMAN-*` when the draft contains:

- several abstract nouns where a concrete actor and action would be clearer;
- a first screen that stacks date, company, financing, biography, and announcement but leaves no unresolved pressure;
- a hook that collapses after famous names, large numbers, and hot terms are removed;
- a research list exposed as numbered chapters, equal-weight cards, or topic-bin headings;
- a paragraph that announces a conclusion before showing the evidence;
- repeated “not A but B” constructions or balanced triplets used for rhythm rather than meaning;
- clusters of framing labels such as 「严格来说」「奇怪的是」「有意思的是」 or their equivalents that repeatedly announce a turn instead of carrying it;
- article-performance sentences that announce「这里有张力」「能力有差距」or a fast-moving business judgment without naming the concrete conflict, capability, decision, evidence, or consequence;
- unnecessary meta narration such as “下面我们来看看” or “通过以上分析可以发现”;
- evidence-audit narration that exposes internal source grading, verification, falsification, claim boundaries, or why the writer accepts a source; apply `CORE-EVIDENCE-SEAM-001` and keep only normal attribution or uncertainty that changes the fact;
- identical paragraph length and transition patterns across sections;
- fake intimacy, forced slang, or an unexplained meme pasted onto formal prose;
- excessive qualification that protects every sentence but prevents the reader from knowing the author's view;
- a conclusion that summarizes the table of contents instead of deepening the central judgment.
- a conclusion that has already answered the title, then starts an unpromised personal method, checklist, or second thesis.

## Pass B: independent cold read

Read only the title, deck if present, and `draft.md` body before opening `brief.md` or `research/argument-map.md`. Then write from memory:

1. What happened?
2. What unresolved pressure in the first screen made the next paragraph necessary?
3. What is the author's main judgment?
4. What evidence makes that judgment credible?
5. What is the strongest limitation or alternative explanation?
6. Why does this matter to a non-specialist reader?
7. What changed from one section to the next?
8. What exact idea does the final sentence leave behind?

Finish these eight answers before opening `brief.md`, `research/judgment-workshop.md`, or any outline. Then compare the answers with the brief. A mismatch is a structural defect, not merely a wording preference. Sample the opening, middle, and ending aloud and mark voice discontinuities.

Only after the cold read is complete, open the applicable narrative chain: `brief.md` for L2 or the locked `research/judgment-workshop.md` for L3. Map every finished section to its four cells and check beat by beat whether it answers the previous unresolved question and creates the need for the next section. Hide headings while checking. A section that can move earlier or disappear without collapsing the article is a structural defect. Departure from the contract is allowed only when the new chain still holds; record the departure in `review.md`.

Finally apply `PROJECT-WECHAT-CONCRETE-001`: inspect the current editing deletion log and `research/co-writing-log.md`. Record every deleted concrete detail and its fact, rights, relevance, or editorial reason; confirm voice anchors and locked units were not silently rewritten. If the net edit deletes scenes, numbers, failures, humor, or named objects while preserving abstract summaries, return the draft for re-editing.

## Pass condition

- The cold reader reconstructs the promised question, central claim, main evidence chain, boundary, and final judgment without relying on a graphic.
- Important terms are understandable at first encounter.
- No major template-language pattern recurs across the article.
- Every retained high-salience line has a concrete communication job and referent; deletion would remove real content rather than only article tone.
- Hiding the headings does not turn the evidence sections into an arbitrary source list; the post-cold-read mapping confirms each beat answers the previous unresolved question, or every parallel section uses one declared scale.
- The locked-unit and edit-log check passes `PROJECT-WECHAT-CONCRETE-001`; deleted concrete details and reopened units have reasons, and the net direction is not「删具体、留抽象」。
- The first screen contains a supported unresolved pressure, not only news heat, credentials, or a hypothetical scene.
- The article uses one main narrative engine; headings reveal turns but do not create a false sense of progress.
- No blocking or major `HUMAN-RHY-*` or `HUMAN-AI-*` defect remains open.
- Repairs do not add unsupported facts or flatten the author's real stance.

After this pass, run the copyedit gate on the exact final body. A draft can satisfy every condition above and still contain a missing subject, broken comparison, unclear referent, unanchored connector, or overloaded sentence.
