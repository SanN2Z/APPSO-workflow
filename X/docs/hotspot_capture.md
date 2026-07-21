# Chinese X Hotspot Capture Strategy

Last checked: 2026-07-04

## Goal

Find Chinese-language topics on X that can be connected to our offer without
spammy trend hijacking.

The correct pattern is:

Hot topic -> relevant angle -> useful post -> optional offer.

The wrong pattern is:

Hot hashtag -> unrelated sales pitch -> repeated posting.

## Official Data Sources

### 1. Trends by WOEID

Endpoint:

```text
GET /2/trends/by/woeid/:id
```

Use this to get current trending topics for a location. Start with:

- Worldwide: `1`
- Japan: `23424856`
- Tokyo: `1118370`
- United States: `23424977`
- Hong Kong: verify in API before relying on it
- Taiwan: verify in API before relying on it
- Singapore: verify in API before relying on it

The endpoint returns trend names and counts where available. It does not mean a
trend is Chinese-language. Filter trend names containing Chinese characters, then
validate with recent search.

### 2. Recent Search

Endpoint:

```text
GET /2/tweets/search/recent
```

Use it to fetch recent posts matching a query from the last 7 days. Useful
filters:

- `lang:zh`
- `-is:retweet`
- `-is:reply`
- `is:verified`
- `has:links`
- `has:images`
- `from:account`
- `list:list_id`

Example:

```text
(AI OR OpenAI OR ChatGPT OR Claude OR 创业 OR 出海 OR 独立开发 OR 变现) lang:zh -is:retweet -is:reply
```

### 3. Recent Counts

Endpoint:

```text
GET /2/tweets/counts/recent
```

Use this before fetching posts. Counts are cheaper and show whether a topic is
rising. Compare the last 1-3 hours against the previous 24-hour baseline.

### 4. Filtered Stream

Endpoint:

```text
GET /2/tweets/search/stream
POST /2/tweets/search/stream/rules
```

Use later. It is better for always-on monitoring, but it can burn credits and
engineering time. Start with scheduled counts/search requests.

## Practical Hotspot Pipeline

### Stage 1: Candidate Topics

Collect candidates from:

- WOEID trends;
- recent counts for fixed Chinese keywords;
- curated list of Chinese tech/founder accounts;
- manual X Explore scan;
- outside sources for context only: Weibo, Zhihu, Xiaohongshu, Product Hunt,
  Hacker News, AI product launches.

### Stage 2: Scoring

Score every topic 1-5:

- velocity: is the volume rising now?
- fit: can we connect it to X operations, AI tools, indie products, or monetization?
- originality: can we add a useful angle instead of repeating news?
- risk: politics, tragedy, health, finance, minors, private persons, or unclear facts lower the score.
- conversion path: can this attract potential clients?

Publish only when:

```text
velocity + fit + originality + conversion_path - risk >= 12
```

### Stage 3: Post Types

Use these formats:

1. **Explainer:** "这件事为什么会火？"
2. **Founder angle:** "如果你是产品创始人，这里有 3 个启发。"
3. **Before/after:** "同一个热点，普通账号这样发，能成交的账号这样发。"
4. **Mini teardown:** "我拆了 10 条相关爆帖，发现共同点是..."
5. **Contrarian:** "这个热点真正值得学的不是 X，而是 Y。"

### Stage 4: Guardrails

- Do not use unrelated hashtags just because they trend.
- Do not auto-reply to strangers based on keywords.
- Do not mass DM people discussing the topic.
- Do not post duplicate trend commentary repeatedly.
- Do not present unverified claims as facts.
- Avoid tragedy/disaster/personal scandal unless there is a clear public-interest reason.
- Use "what this suggests" when making an inference.

## Chinese Query Presets

### `zh-tech`

```text
(AI OR OpenAI OR ChatGPT OR Claude OR Gemini OR Grok OR "Cursor" OR 独立开发 OR 出海 OR 创业 OR 变现 OR SaaS OR 产品增长) lang:zh -is:retweet -is:reply
```

### `zh-creator`

```text
(推特 OR X OR 小红书 OR 公众号 OR 自媒体 OR 流量 OR 爆款 OR 变现 OR 私域 OR IP) lang:zh -is:retweet -is:reply
```

### `zh-crypto`

```text
(比特币 OR 以太坊 OR 加密 OR 空投 OR 币圈 OR Web3 OR Solana OR Base) lang:zh -is:retweet -is:reply
```

Use crypto only with caution. It can attract engagement, but also spam and scam
risk.

## MVP Tooling

Start with `scripts/trend_scan.py`:

- dry-run by default;
- `--mode trends` for WOEID trends;
- `--mode counts` for recent count curves;
- `--mode search` for example posts;
- `--confirm-spend` required before making API calls;
- strict max result limits;
- no automatic publishing.

The output should feed human drafting, not direct auto-posting.

## Sources

- X Trends by WOEID: https://docs.x.com/x-api/trends/trends-by-woeid/introduction
- X Personalized Trends: https://docs.x.com/x-api/trends/personalized-trends
- X Recent Search: https://docs.x.com/x-api/posts/search/introduction
- X Search Operators: https://docs.x.com/x-api/posts/search/integrate/operators
- X Recent Counts: https://docs.x.com/x-api/posts/get-count-of-recent-posts
- X Filtered Stream: https://docs.x.com/x-api/posts/filtered-stream/introduction
- X API pricing: https://docs.x.com/x-api/getting-started/pricing
- X Authenticity Policy: https://help.x.com/en/rules-and-policies/authenticity
