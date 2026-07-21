# WeChat editorial gates

Apply every fixed gate, then add criteria derived from the current brief and explicit feedback. Record evidence in `review.md`; a single generic "quality passed" checkbox is insufficient.

## Gate 1: reader and promise

- Identify the reader and the knowledge gap the article must bridge.
- Name the article type and verify that its structure matches that job; a quick news item, product test, method guide, and opinion piece must not share a generic outline by default.
- Express one reader-facing promise and one primary hook.
- State the thesis as a causal claim with evidence needs and a boundary.

## Gate 2: title and opening

- The title creates one main curiosity; it does not stack a person, quote, product name, jargon, and second conclusion.
- A non-specialist can paraphrase the promise in about five seconds.
- The opening delivers the same promise quickly and does not require knowing an unfamiliar person or acronym.

## Gate 3: minimum background

- Before analysis, give readers the smallest fact set needed to follow the argument.
- For product launches, cover what launched, user/access scope, price or threshold, and workflow/entry changes.
- Keep the fact card compact and separate vendor claims from independent conclusions.

## Gate 4: argument closure

- Introduce the organizing framework in prose within the first quarter of the article.
- Use identical dimension names in prose, headings, and graphics.
- Map each major section to `judgment -> evidence -> limitation -> reader consequence`.
- Do not let one example ambiguously prove several dimensions without explaining the link.
- Address at least one serious counterexample, alternative explanation, or scope limit.

## Gate 5: accessible voice

- Translate important jargon at first use.
- Break two consecutive high-density paragraphs with a scene, analogy, or author judgment.
- The opening, middle, and ending sound like the same narrator.
- Humor serves the argument and preserves the original meaning of quotes and memes.
- A cold reader can answer: what happened, what the author thinks, and why it matters to them.
- The writer self-pass and independent cold-read pass in `wechat-human-voice-pass.md` both pass; a generic "AI flavor removed" claim does not count.
- The Chinese-adapted diagnostic in `wechat-ai-pattern-pass.md` was run in `detect` mode, its scope and exclusions were recorded, and no blocking or major `HUMAN-AI-*` defect remains open. English word lists, stylometric thresholds, and detector scores are not Chinese quality gates.
- The sentence-level gate in `wechat-copyedit-pass.md` passes on the exact final body; cold-read comprehension does not waive grammar defects.

## Gate 6: ending

- The last two or three paragraphs answer the title and recover the central framework.
- The final sentence is the article's judgment, not a generic CTA, slogan, or joke.
- The ending introduces no unsupported claim and does more than repeat the opening.

## Gate 7: facts and sources

- Recheck time-sensitive facts at `as_of`.
- Verify names, roles, quotes, dates, prices, rankings, policies, and product names.
- Give every source an access date and supported wording.
- Separate fact, vendor self-report, third-party result, inference, and commentary.
- For enterprise or sponsored material, include at least one independent source, one real limitation, and one inapplicable scenario; otherwise record a blocker.

## Gate 8: visuals and rights

- Every body image exists inside the package and is registered.
- Graphics are readable at phone width; essential logic is also in prose.
- Captions identify source and comparison limits.
- Used assets have a truthful, platform-compatible rights status.

## Gate 9: state and validation

- `fact_checked`, `rights_checked`, and `copyedit_checked` are booleans and reflect completed checks.
- Structural rewrites or changed factual claims invalidate the relevant previous pass. Any Markdown body edit invalidates the copyedit pass.
- `copyedit.md`, `copyedit_body_sha256`, and the validator must agree on the exact final body hash.
- The validator reports zero errors; warnings are resolved or documented.
- `ready` has no blocker, unresolved major defect, open blocking/major `HUMAN-AI-*` defect, open `COPY-*` defect, or stale copyedit hash. `published` still requires a real link or explicit user confirmation.

## Task-specific rubric

Add 3-8 observable checks from the brief, current topic, user feedback, and channel goal. Each check needs a pass condition; avoid vague criteria such as "more viral" or "sounds better".
