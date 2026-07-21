# Daily Viral Content Automation

This project uses a daily automation to generate X content candidates.

## Non-Negotiable Boundary

The automation may auto-publish standalone original posts only after the user has
given blanket approval for the daily queue.

It must not auto-publish replies, DMs, likes, follows, quote posts, reposts, or
mentions.

Auto-published standalone posts must be:

- original;
- no URLs;
- no `@` mentions;
- no hashtags;
- under 280 characters;
- non-duplicative;
- not direct political agitation;
- not hate, harassment, gambling, porn, scam, or grey-market promotion.

Comments/replies are still generated as manual drafts only.

## Current Schedule

All times are Asia/Tokyo.

- 09:00: generate `content/YYYY-MM-DD_daily_viral_queue.md`
- 10:00: auto-publish Draft 1
- 12:30: auto-publish Draft 2
- 15:00: auto-publish Draft 3
- 18:00: auto-publish Draft 4
- 21:00: auto-publish Draft 5

## Daily Job Output

Every run should create a file:

```text
content/YYYY-MM-DD_daily_viral_queue.md
```

The file must include:

- account metrics for recent posts;
- 3-5 high-performing comparable posts or accounts;
- extracted viral structures;
- 5 standalone post drafts;
- 5 manual reply drafts with target URLs;
- a recommended publishing order;
- risk notes.

Standalone drafts must use this exact format so `scripts/publish_daily_queue.py`
can parse them:

````text
### Draft 1

```text
POST TEXT
```
````

## Content Standard

Do not write operational diary posts as public content.

Public drafts should use:

- identity tension;
- contrarian framing;
- hidden class / information access / tool access tension;
- engineering vs market reality;
- concrete language;
- one quotable sentence.

Avoid:

- fake claims;
- hate or protected-class attacks;
- explicit political agitation;
- unrelated hashtag hijacking;
- duplicate engagement-bait;
- automatic follow-for-follow or mutual-like schemes.

## Useful Local Commands

Check visibility:

```powershell
python scripts/check_x_visibility.py --username syz277527 --post-id POST_ID
```

Scan topics:

```powershell
python scripts/trend_scan.py --mode search --query 'QUERY' --max-results 20 --sort-order relevancy --confirm-spend
python scripts/trend_scan.py --mode counts --query 'QUERY' --hours 24 --confirm-spend
```

Dry-run one queued post:

```powershell
python scripts/publish_daily_queue.py --draft 1
```

Auto-publish one queued post:

```powershell
python scripts/publish_daily_queue.py --draft 1 --confirm
```
