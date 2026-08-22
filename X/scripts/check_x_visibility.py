import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
X_ROOT = Path(__file__).resolve().parents[1]


def load_dotenv(path: Path) -> None:
    if not path.exists():
        print(f"[fail] Missing {path}.")
        raise SystemExit(1)
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            print(f"[fail] Invalid .env line {line_number}: expected KEY=value")
            raise SystemExit(1)
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


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


def print_user(username: str) -> None:
    params = urlencode(
        {
            "user.fields": "created_at,description,public_metrics,verified,verified_type,protected",
        }
    )
    data = get_json(f"https://api.x.com/2/users/by/username/{username}?{params}")
    print("[user]")
    print(json.dumps(data.get("data", data), ensure_ascii=False, indent=2))


def print_posts(ids: list[str]) -> None:
    if not ids:
        return
    params = urlencode(
        {
            "ids": ",".join(ids),
            "tweet.fields": "created_at,public_metrics,reply_settings,author_id",
        }
    )
    data = get_json(f"https://api.x.com/2/tweets?{params}")
    print("[posts]")
    for post in data.get("data", []):
        metrics = post.get("public_metrics", {})
        print(
            f"{post.get('id')} | {post.get('created_at')} | "
            f"impressions={metrics.get('impression_count', 'n/a')} "
            f"likes={metrics.get('like_count', 0)} replies={metrics.get('reply_count', 0)} "
            f"reposts={metrics.get('retweet_count', 0)} quotes={metrics.get('quote_count', 0)} "
            f"reply_settings={post.get('reply_settings', 'n/a')}"
        )


def print_search(username: str) -> None:
    params = urlencode(
        {
            "query": f"from:{username} -is:retweet",
            "max_results": "10",
            "sort_order": "recency",
            "tweet.fields": "created_at,public_metrics,reply_settings",
        }
    )
    data = get_json(f"https://api.x.com/2/tweets/search/recent?{params}")
    print("[recent_search]")
    posts = data.get("data", [])
    print(f"result_count={len(posts)}")
    for post in posts:
        metrics = post.get("public_metrics", {})
        print(
            f"{post.get('id')} | {post.get('created_at')} | "
            f"impressions={metrics.get('impression_count', 'n/a')} "
            f"likes={metrics.get('like_count', 0)} replies={metrics.get('reply_count', 0)} "
            f"reposts={metrics.get('retweet_count', 0)}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check basic public X account and post visibility.")
    parser.add_argument("--username", required=True)
    parser.add_argument("--post-id", action="append", default=[])
    return parser


def main() -> None:
    args = build_parser().parse_args()
    load_dotenv(X_ROOT / ".env")
    print_user(args.username)
    print_posts(args.post_id)
    print_search(args.username)


if __name__ == "__main__":
    main()
