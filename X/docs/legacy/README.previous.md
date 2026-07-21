# X Operations Assistant

This repository is for building a practical X/Twitter operations system: content
planning, account positioning, analytics, lead tracking, and monetization
experiments for a human operator.

The starting assumption is conservative: "Twitter operations makes money" is not
a fact until this project produces evidence. The first version should help run
repeatable experiments and measure whether content actually creates leads,
audience growth, traffic, or sales.

## Product Thesis

Useful social-media tooling is not just auto-posting. The valuable workflow is:

1. choose a niche and offer;
2. generate and review post ideas;
3. publish with a consistent schedule;
4. import results;
5. identify which hooks, formats, and calls to action work;
6. turn attention into email subscribers, calls, customers, or community members.

## Safety Line

This project should not build spam infrastructure. Do not implement fake
engagement, account farming, mass DM, stealth scraping, CAPTCHA bypass,
rate-limit bypass, or coordinated inauthentic behavior. Any posting or outbound
message automation must be explicit, logged, and human-approved unless a later
production protocol says otherwise.

## Mask Network Note

The "Masked" reference is probably Mask Network. Its public site describes it as
a browser extension that adds Web3 functions to existing social platforms,
including X, Facebook, Instagram, Minds, and Mirror. The useful lesson for this
project is the "tool layer over existing social platform" pattern, not a direct
clone or a crypto-first product.

Sources to re-check when needed:

- https://www.mask.io/
- https://en.wikipedia.org/wiki/Mastodon_(social_network)
- https://en.wikipedia.org/wiki/Pixiv

## MVP Roadmap

- Strategy profile: target audience, content pillars, offer, positioning.
- Idea backlog: hooks, draft text, source notes, status, priority.
- Publishing calendar: reviewed posts only, explicit approval before posting.
- Analytics import: impressions, engagement, follows, clicks, conversion notes.
- Experiment dashboard: compare format, topic, CTA, and timing.
- Lead tracker: accounts, context, relationship status, last touch, next action.

## Operating SOP

The first operating playbook is in [docs/x_operations_sop.md](docs/x_operations_sop.md).
The first monetization sprint is in [docs/monetization_sprint.md](docs/monetization_sprint.md).
First-week X drafts are in [content/week1_x_posts.md](content/week1_x_posts.md).
Chinese hotspot capture strategy is in [docs/hotspot_capture.md](docs/hotspot_capture.md).

## X API Setup

Local credential setup is documented in [docs/x_api_setup.md](docs/x_api_setup.md).
Real credentials belong in `.env`, which is ignored by git.

## Repo Status

Initialized as an empty project on 2026-07-04. No app stack has been selected
yet.
