# WeChat AI-pattern diagnostic

Use this as a supplemental diagnostic for Chinese WeChat copy. It catches recurring machine-shaped writing patterns and internal workflow leakage that ordinary grammar review may miss. It does not replace fact-checking, the human-voice pass, the independent cold read, or the exact-version copyedit gate.

## Position in the workflow

Run the gates in this order:

1. The feature writer completes Pass A in [wechat-human-voice-pass.md](wechat-human-voice-pass.md).
2. The release auditor runs this diagnostic on the draft and reports defects without rewriting it.
3. The feature writer repairs confirmed defects; factual changes return to the evidence editor.
4. The release auditor re-runs this diagnostic and completes the independent cold read.
5. Only then does the copy editor run [wechat-copyedit-pass.md](wechat-copyedit-pass.md) and lock the exact body hash.

Any edit after copyedit invalidates the copyedit pass. This diagnostic therefore belongs before copyedit, not after it.

## Required skill and mode

Load the globally installed `~/.codex/skills/avoid-ai-writing/SKILL.md` when it is available.

- Mode: `detect`
- Context: `blog`
- Voice reference: `上下文/作者声音.md`, the current brief, and the article itself
- Scope: title, deck, headings, body, quotes, captions, and final notes
- Output: numbered `HUMAN-AI-*` defects in `review.md`

Do not use `rewrite` or `edit` mode as an automatic pipeline step. The feature writer decides how to repair each confirmed defect while preserving sourced meaning and the author's actual position. If the global skill is unavailable, run the project checklist below and record that the external skill was not loaded.

## Apply these rule groups to Chinese copy

### 1. Internal workflow and model leakage

Flag text that belongs in research or review notes rather than the public article, including:

- “本轮核到”“当前公开材料尚未回答”“根据 `sources.md`”“在 brief 里锁定”；
- tool, prompt, model, search, file-path, defect-ID, hash, or review-process language;
- raw citation tokens, tracking parameters, placeholders, TODOs, or instructions to the writer;
- claims framed around what the writing system did instead of what readers need to know.

Clear internal leakage is a `blocker` because it breaks publication readiness.

### 2. Empty authority and inflated significance

Flag vague attribution such as “有研究表明”“业内普遍认为” when the authority is neither named nor supported. Also flag unsupported declarations that an event “标志着”“重新定义了”“开启了新时代”. Cross-tag factual support problems as `FACT-*`; this pass diagnoses the writing symptom but does not clear the evidence.

### 3. Template structure with low information gain

Flag sections that remain equally valid after paragraph shuffling, repeat the same claim in new wording, or use headings and transitions to simulate progress. Common symptoms include:

- formulaic scene-setting that delays the actual event;
- repeated “不是 A，而是 B” or three-part cadence without a real distinction;
- “下面来看”“值得注意的是”“这意味着”等 meta narration where the relation should be stated directly;
- self-labeling such as “最关键的一点是” without evidence that earns the emphasis;
- generic future-looking endings that could close any AI article.

### 4. Uniform rhythm and over-organization

Flag identical paragraph lengths, repeated section shapes, every paragraph ending in a mini-conclusion, excessive bullets, or prose forced into symmetrical clauses. Repair for meaning and reading rhythm, not merely for sentence-length variation.

### 5. Manufactured personality

Flag fake emotional reactions, forced slang, unexplained memes, canned agreement, or invented labels that are not used by the source or helpful to the reader. Do not “humanize” copy by injecting casual language at random.

Also flag stock Chinese colloquial frames and nonliteral metaphors that manufacture emphasis without carrying information, such as「先别急着……」「喊革命」「……到账」「这笔账……」or a repeated exam / war / finance metaphor chain. Apply a transfer test: if the whole phrase could move unchanged to another AI product article and deleting it loses no fact or judgment, remove it. If it has a real job, rewrite it with a concrete actor, action, condition, cost, or result. Preserve sourced quotations and literal uses such as an actual bill, payment arrival, historical revolution, or real examination.

### 6. Speculative gap filling

Flag precise motives, causes, product mechanisms, safety guarantees, or future outcomes that are not supported by sources. A limitation should say what remains unknown in reader-facing language; it should not narrate the research process or turn missing evidence into a product accusation.

## Do not use these as Chinese pass/fail rules

- English word-replacement tiers or English-specific vocabulary bans;
- type-token-ratio, lexical-diversity, sentence-length, or punctuation thresholds;
- English em-dash limits or a ban on Chinese curly quotation marks;
- a generic AI-detector score, probability, or “sounds AI” verdict;
- forced first-person anecdotes, slang, typos, or sentence fragments added only to appear human.

These may be observations when they reveal a concrete reader problem, but none is a gate by itself.

## Severity and pass condition

- `blocker`: internal workflow leakage, raw instruction/citation artifacts, unresolved placeholders, or invented facts.
- `major`: a recurring pattern that obscures the article's claim, evidence, boundary, or narrator.
- `minor`: a local phrase or rhythm issue that does not distort meaning.

The pass is `needs_fix` while any `blocker` or `major` `HUMAN-AI-*` defect remains open. Minor style calls are resolved by the managing editor against `上下文/作者声音.md`; the skill does not overrule deliberate brand voice.

## Record in `review.md`

```markdown
## AI-pattern diagnostic

- Skill: avoid-ai-writing 3.15.0
- Mode: detect
- Scope: title / deck / headings / body / captions / notes
- Applied: workflow leakage; empty authority; template structure; rhythm; manufactured personality; speculative gaps
- Ignored as hard gates: English word lists; stylometric thresholds; punctuation quotas; detector score
- Status: pass | needs_fix | blocked

| ID | Severity | Evidence | Reader harm | Repair owner | Pass condition | Status |
|---|---|---|---|---|---|---|
| HUMAN-AI-001 | major | Exact phrase or pattern | Concrete effect | Feature writer | Observable repair | open |
```

Record a real finding or `none found`; never treat an unchecked box or a detector score as evidence of a pass.
