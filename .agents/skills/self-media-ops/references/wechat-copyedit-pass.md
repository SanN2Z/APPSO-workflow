# Sentence-level copyedit gate

Run this gate after the argument and facts are stable, and before the release audit. It is separate from the human-voice cold read: cold read tests whether the article works; copyedit tests whether every sentence is grammatically clean and unambiguous.

## Order of work

1. Set `copyedit_checked: false` and clear `copyedit_body_sha256` whenever the Markdown body changes.
2. Give the copy editor only the exact `draft.md` title and body first. Include headings, bullets, captions, blockquotes, and the final note.
3. Read sentence by sentence, then read the full article aloud. Do not infer missing subjects or intended referents from the private outline.
4. Record exact defects in `copyedit.md` with `COPY-*` IDs. Quote the sentence, name the defect, and give a repair direction; do not silently rewrite `draft.md`.
5. Let the feature writer repair the only draft. Send any wording that may change a fact, comparison, scope, or source meaning back to the evidence editor.
6. Re-run the complete copyedit pass on the repaired body, not only the changed lines.
7. After a pass, print the exact body hash:

   ```powershell
   python .agents/skills/self-media-ops/scripts/validate_content_package.py <content-package-path> --print-copyedit-hash
   ```

8. Put the same hash in `copyedit.md` and `draft.md`, set `copyedit_checked: true`, then run the normal package validator.

Any later body change invalidates the hash and requires the complete gate again. Frontmatter-only state changes do not invalidate a body copyedit.

## Sentence checks

Check every sentence for:

- **Complete structure**: the subject, predicate, object, and modifier attachment are recoverable without guessing.
- **Parallel comparison**: both sides of `和 / 跟 / 比 / 而不是 / 不同于` have matching grammatical roles.
- **Parallel clauses and punctuation**: long lists use colons, semicolons, or dashes where commas would blur the hierarchy.
- **Anchored connectors**: words such as `又、也、仍、更、其实、正是` have a visible earlier item or contrast.
- **Clear reference**: `它、这、该方案、该文档、上述机制` point to one unmistakable noun. Write the official document or feature name at first mention.
- **One logical step at a time**: split sentences that stack model size, test conditions, limitations, and conclusions into one chain.
- **Terminology**: give the full official or plain-language name at first use; abbreviations and English labels remain consistent afterward.
- **Chinese typography**: use `「」` for Chinese quotations and `『』` for nested quotations; require one half-width space between Chinese and English and between Chinese and Arabic numerals. Do not alter code, commands, URLs, paths, environment variables, Markdown link targets, YAML/JSON syntax, fixed product strings, or verbatim source text.
- **Readable rhythm**: read the sentence aloud without needing to restart or mentally insert omitted words.
- **Publication-only language**: remove internal workflow terms, defect IDs, evidence-desk instructions, and package paths from the reader-facing copy.
- **Semantic preservation**: a grammar repair must not strengthen certainty, erase a limitation, or change who did what.

## Pass condition

- No unresolved `COPY-*` defect remains.
- No unresolved Chinese quotation-mark or Chinese/English/number spacing defect remains.
- The title, body, headings, lists, captions, quotes, and final note were all checked.
- The exact body hash in `copyedit.md` matches `copyedit_body_sha256` in `draft.md`.
- The validator accepts the package.

## `copyedit.md` format

```markdown
---
status: pass
checked_at: "2026-07-12 21:45:00+08:00"
body_sha256: "64-lowercase-hex-characters"
scope: "title, body, headings, lists, captions, quotes, notes"
---

# 语法终校

## 检查结果

- 主谓与比较结构：pass
- 并列、标点与长句：pass
- 指代与术语全称：pass
- 连接词着落：pass
- 朗读与内部话术：pass

## 缺陷记录

无 open `COPY-*` 缺陷。
```
