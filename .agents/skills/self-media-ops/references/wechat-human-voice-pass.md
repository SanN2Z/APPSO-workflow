# Cold-reader and human-voice pass

Run two human-reading passes. The feature writer performs Pass A while owning the draft. The release auditor then runs the detect-only bridge in [wechat-ai-pattern-pass.md](wechat-ai-pattern-pass.md), reports `HUMAN-AI-*` defects, and performs Pass B cold without rewriting. These passes test reader path, voice, machine-shaped patterns, and argument reconstruction; they do not replace the sentence-level grammar gate in [wechat-copyedit-pass.md](wechat-copyedit-pass.md).

## Pass A: writer self-pass

Repair in this order:

1. **Reader path**: Can a reader follow the article without the private outline? Move definitions and background before the reasoning that depends on them.
2. **Paragraph jobs**: Give every paragraph one job: scene, fact, judgment, evidence, limitation, transition, or consequence. Merge or delete paragraphs that only restate the previous one.
3. **Plain language**: Translate jargon at first use. Replace abstract noun chains with a person, action, cost, interruption, or decision whenever accuracy allows.
4. **Natural transitions**: Remove template connectors such as “这意味着”“换句话说”“值得注意的是”“首先/其次/最后” when the logical relation is already visible. Write the relation itself when it is not.
5. **Rhythm**: Vary sentence and paragraph length according to meaning. Do not force every section into the same three-part cadence or end every section with a mini-summary.
6. **Voice continuity**: Compare an opening paragraph, a middle evidence paragraph, and the ending. They should sound like the same informed person, not “internet opening + report body + slogan ending”.
7. **Humor discipline**: Keep jokes that sharpen a supported judgment. Remove jokes that need explanation, repeat the same beat, or change a person's meaning.
8. **Ending pressure test**: If deleting the final sentence makes the thesis stronger, rewrite or move that sentence.

Do not use “add more slang” as the default repair. Do not use AI-detector scores as a quality gate. Preserve sourced meaning; return factual changes to the evidence editor.

After Pass A, run the Chinese-adapted diagnostic in `wechat-ai-pattern-pass.md`. It uses `avoid-ai-writing` in `detect` mode only. The feature writer repairs confirmed findings before the release auditor completes the final cold-read pass.

## Common template-language defects

Flag with `HUMAN-*` when the draft contains:

- several abstract nouns where a concrete actor and action would be clearer;
- a paragraph that announces a conclusion before showing the evidence;
- repeated “not A but B” constructions or balanced triplets used for rhythm rather than meaning;
- unnecessary meta narration such as “下面我们来看看” or “通过以上分析可以发现”;
- identical paragraph length and transition patterns across sections;
- fake intimacy, forced slang, or an unexplained meme pasted onto formal prose;
- excessive qualification that protects every sentence but prevents the reader from knowing the author's view;
- a conclusion that summarizes the table of contents instead of deepening the central judgment.

## Pass B: independent cold read

Read only the title, deck if present, and `draft.md` body before opening `brief.md` or `research/argument-map.md`. Then write from memory:

1. What happened?
2. What is the author's main judgment?
3. What evidence makes that judgment credible?
4. What is the strongest limitation or alternative explanation?
5. Why does this matter to a non-specialist reader?
6. What exact idea does the final sentence leave behind?

Compare the answers with the brief. A mismatch is a structural defect, not merely a wording preference. Afterward, sample the opening, middle, and ending aloud and mark voice discontinuities.

## Pass condition

- The cold reader reconstructs the promised question, central claim, main evidence chain, boundary, and final judgment without relying on a graphic.
- Important terms are understandable at first encounter.
- No major template-language pattern recurs across the article.
- No blocking or major `HUMAN-AI-*` defect remains open.
- Repairs do not add unsupported facts or flatten the author's real stance.

After this pass, run the copyedit gate on the exact final body. A draft can satisfy every condition above and still contain a missing subject, broken comparison, unclear referent, unanchored connector, or overloaded sentence.
