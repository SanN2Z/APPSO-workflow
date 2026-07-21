import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


PRESETS = {
    "zh-tech": '(AI OR OpenAI OR ChatGPT OR Claude OR Gemini OR Grok OR "Cursor" OR 独立开发 OR 出海 OR 创业 OR 变现 OR SaaS OR 产品增长) lang:zh -is:retweet -is:reply',
    "zh-creator": "(推特 OR X OR 小红书 OR 公众号 OR 自媒体 OR 流量 OR 爆款 OR 变现 OR 私域 OR IP) lang:zh -is:retweet -is:reply",
    "zh-crypto": "(比特币 OR 以太坊 OR 加密 OR 空投 OR 币圈 OR Web3 OR Solana OR Base) lang:zh -is:retweet -is:reply",
}


WOEIDS = {
    "worldwide": "1",
    "japan": "23424856",
    "tokyo": "1118370",
    "united-states": "23424977",
    "new-york": "2459115",
    "los-angeles": "2442047",
}


def load_dotenv(path: Path) -> None:
    if not path.exists():
        print(f"[fail] Missing {path}. Copy .env.example to .env and fill it locally.")
        raise SystemExit(1)

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            print(f"[fail] Invalid .env line {line_number}: expected KEY=value")
            raise SystemExit(1)
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            print(f"[fail] Invalid .env line {line_number}: empty key")
            raise SystemExit(1)
        os.environ.setdefault(key, value)


def bearer_token() -> str:
    token = os.environ.get("X_BEARER_TOKEN", "").strip()
    if not token or token.startswith("replace_with"):
        print("[fail] X_BEARER_TOKEN is missing or still a placeholder.")
        raise SystemExit(1)
    return token


def get_json(url: str) -> dict:
    request = Request(url, headers={"Authorization": f"Bearer {bearer_token()}"}, method="GET")
    try:
        with urlopen(request, timeout=25) as response:
            body = response.read().decode("utf-8", errors="replace")
            return json.loads(body) if body else {}
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {"raw": body[:1000]}
        print(f"[fail] X API request failed with HTTP {exc.code}.")
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
        raise SystemExit(1)
    except URLError as exc:
        print(f"[fail] Network error: {exc.reason}")
        raise SystemExit(1)


def resolve_query(args: argparse.Namespace) -> str:
    if args.query:
        return args.query
    if args.preset:
        return PRESETS[args.preset]
    print("[fail] Provide --query or --preset.")
    raise SystemExit(1)


def resolve_woeid(value: str) -> str:
    return WOEIDS.get(value.lower(), value)


def dry_run(args: argparse.Namespace, url: str, estimate: str) -> bool:
    print(f"[info] Mode: {args.mode}")
    print(f"[info] Request URL: {url}")
    print(f"[info] Estimated API cost: {estimate}")
    if args.confirm_spend:
        return False
    print("[dry-run] No network request was made.")
    print("[dry-run] Add --confirm-spend to execute this read request.")
    return True


def print_trends(data: dict) -> None:
    trends = data.get("data", [])
    if not trends:
        print("[info] No trends returned.")
        return
    for idx, trend in enumerate(trends, start=1):
        name = trend.get("trend_name") or trend.get("name") or "<unknown>"
        count = trend.get("tweet_count") or trend.get("post_count") or "n/a"
        print(f"{idx:02d}. {name} | count={count}")


def print_counts(data: dict) -> None:
    meta = data.get("meta", {})
    print(f"[info] total_tweet_count={meta.get('total_tweet_count', 'n/a')}")
    for item in data.get("data", []):
        print(f"{item.get('start')} -> {item.get('end')}: {item.get('tweet_count')}")


def print_posts(data: dict) -> None:
    users = {user["id"]: user for user in data.get("includes", {}).get("users", [])}
    posts = data.get("data", [])
    if not posts:
        print("[info] No posts returned.")
        return
    for idx, post in enumerate(posts, start=1):
        author = users.get(post.get("author_id"), {})
        metrics = post.get("public_metrics", {})
        username = author.get("username", post.get("author_id", "unknown"))
        print(f"\n{idx:02d}. @{username} | {post.get('created_at')}")
        print(f"reply_settings={post.get('reply_settings', 'n/a')}")
        print(
            "metrics="
            f"like:{metrics.get('like_count', 0)} "
            f"repost:{metrics.get('retweet_count', 0)} "
            f"reply:{metrics.get('reply_count', 0)} "
            f"quote:{metrics.get('quote_count', 0)}"
        )
        print(post.get("text", "").replace("\n", " ")[:500])
        post_id = post.get("id")
        if post_id and username != "unknown":
            print(f"https://x.com/{username}/status/{post_id}")


def run_trends(args: argparse.Namespace) -> None:
    woeid = resolve_woeid(args.woeid)
    url = f"https://api.x.com/2/trends/by/woeid/{woeid}"
    if dry_run(args, url, "about $0.010 per request"):
        return
    print_trends(get_json(url))


def run_counts(args: argparse.Namespace) -> None:
    query = resolve_query(args)
    end = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(minutes=2)
    start = end - timedelta(hours=args.hours)
    params = {
        "query": query,
        "start_time": start.isoformat().replace("+00:00", "Z"),
        "end_time": end.isoformat().replace("+00:00", "Z"),
        "granularity": args.granularity,
    }
    url = "https://api.x.com/2/tweets/counts/recent?" + urlencode(params)
    if dry_run(args, url, "about $0.005 per request"):
        return
    print(f"[info] query={query}")
    print_counts(get_json(url))


def run_search(args: argparse.Namespace) -> None:
    query = resolve_query(args)
    params = {
        "query": query,
        "max_results": str(args.max_results),
        "sort_order": args.sort_order,
        "tweet.fields": "created_at,author_id,public_metrics,lang,entities,reply_settings",
        "expansions": "author_id",
        "user.fields": "username,name,verified,public_metrics",
    }
    url = "https://api.x.com/2/tweets/search/recent?" + urlencode(params)
    estimate = f"about ${args.max_results * 0.005:.3f} if {args.max_results} posts are returned"
    if dry_run(args, url, estimate):
        return
    print(f"[info] query={query}")
    print_posts(get_json(url))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan X trends/search with a spending confirmation gate.")
    parser.add_argument("--mode", choices=["trends", "counts", "search"], required=True)
    parser.add_argument("--confirm-spend", action="store_true", help="Actually call X API and spend credits.")
    parser.add_argument("--woeid", default="worldwide", help="WOEID or known alias for --mode trends.")
    parser.add_argument("--preset", choices=sorted(PRESETS), help="Preset query for counts/search.")
    parser.add_argument("--query", help="Custom X search query for counts/search.")
    parser.add_argument("--hours", type=int, default=24, help="Lookback hours for counts mode.")
    parser.add_argument("--granularity", choices=["minute", "hour", "day"], default="hour")
    parser.add_argument("--max-results", type=int, default=10)
    parser.add_argument("--sort-order", choices=["recency", "relevancy"], default="recency")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.max_results < 10 or args.max_results > 100:
        print("[fail] --max-results must be between 10 and 100.")
        raise SystemExit(1)
    if args.hours < 1 or args.hours > 168:
        print("[fail] --hours must be between 1 and 168.")
        raise SystemExit(1)

    load_dotenv(Path(".env"))

    if args.mode == "trends":
        run_trends(args)
    elif args.mode == "counts":
        run_counts(args)
    elif args.mode == "search":
        run_search(args)
    else:
        print(f"[fail] Unsupported mode: {args.mode}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
