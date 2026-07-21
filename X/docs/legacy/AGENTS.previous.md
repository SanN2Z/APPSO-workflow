# Project Instructions

## Project Intent

This project exists to build an X/Twitter operations assistant for a human operator.
The product should help with content planning, account positioning, trend research,
drafting, scheduling, analytics, lead tracking, and monetization experiments.

Treat "running X/Twitter can make money" as a hypothesis to validate, not as an
assumption. Every feature should connect to an observable workflow or metric.

## Product Boundaries

- Build for human-in-the-loop operation first.
- Prefer analytics, editorial planning, CRM-style tracking, and draft assistance.
- Use official APIs and documented export/import paths where possible.
- Keep account credentials, tokens, cookies, and private audience data out of the repo.
- Do not implement fake engagement, mass follow/unfollow, mass DM spam, scraping behind login, CAPTCHA bypass, rate-limit bypass, or coordinated inauthentic behavior.
- Do not ship automation that posts, replies, likes, follows, or DMs without an explicit user confirmation step unless the user later defines a compliant production protocol.

## Reference Direction

The user mentioned "Masked"; this likely refers to Mask Network rather than a
generic "masked" project. Use it only as a directional reference:

- overlay useful tools onto existing social platforms instead of trying to replace them;
- make social workflows richer without stealing user control;
- keep Web3/crypto ideas optional until a concrete monetization reason exists.

Do not clone another product blindly. Extract the useful pattern: a focused tool
layer on top of an existing social platform.

## Engineering Rules

- Fail loud in scripts: no bare `except: pass` or silent skips.
- On Windows Python scripts, configure stdout/stderr as UTF-8 with replacement errors.
- Keep files and generated artifacts reproducible; avoid hidden state in notebooks or local caches.
- Before long-running or production-like jobs, run a dry check for: no errors, non-zero effect, expected sample counts / monotonicity / NaN handling.
- For anything involving X/Twitter API behavior, platform rules, pricing, or rate limits, verify current documentation before coding.

## Suggested MVP

1. Account strategy workspace: niche, audience, offers, content pillars.
2. Content pipeline: idea backlog, drafts, review status, publishing calendar.
3. Post analytics import: impressions, engagement, follower delta, link clicks.
4. Experiment log: hooks, formats, posting time, CTA, result, next action.
5. Lead tracker: people/accounts worth engaging with, context, last interaction.

## Default Implementation Bias

- Start local-first with simple structured files or SQLite before adding services.
- Prefer a small web app/dashboard if the workflow becomes interactive.
- Keep posting destructive side effects separate from planning and analytics.
- Make all external calls explicit, logged, and easy to dry-run.
