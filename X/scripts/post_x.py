import argparse
import base64
import hashlib
import hmac
import json
import os
import secrets
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


REQUIRED_KEYS = [
    "X_API_KEY",
    "X_API_KEY_SECRET",
    "X_ACCESS_TOKEN",
    "X_ACCESS_TOKEN_SECRET",
]


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


def is_placeholder(value: str) -> bool:
    lowered = value.strip().lower()
    return not lowered or lowered.startswith("replace_with") or lowered in {"...", "todo", "changeme"}


def require_env() -> None:
    missing = [key for key in REQUIRED_KEYS if is_placeholder(os.environ.get(key, ""))]
    if missing:
        print("[fail] Missing or placeholder X API settings:")
        for key in missing:
            print(f"  - {key}")
        raise SystemExit(1)


def percent(value: str) -> str:
    return quote(value, safe="")


def oauth1_header(method: str, url: str) -> str:
    consumer_key = os.environ["X_API_KEY"]
    consumer_secret = os.environ["X_API_KEY_SECRET"]
    access_token = os.environ["X_ACCESS_TOKEN"]
    access_token_secret = os.environ["X_ACCESS_TOKEN_SECRET"]

    oauth_params = {
        "oauth_consumer_key": consumer_key,
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": access_token,
        "oauth_version": "1.0",
    }
    normalized = "&".join(
        f"{percent(k)}={percent(v)}" for k, v in sorted(oauth_params.items())
    )
    base_url = urlparse(url)._replace(query="", fragment="").geturl()
    base_string = "&".join([method.upper(), percent(base_url), percent(normalized)])
    signing_key = f"{percent(consumer_secret)}&{percent(access_token_secret)}"
    digest = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    oauth_params["oauth_signature"] = base64.b64encode(digest).decode()

    return "OAuth " + ", ".join(
        f'{percent(k)}="{percent(v)}"' for k, v in sorted(oauth_params.items())
    )


def post_to_x(text: str, reply_to: str | None = None) -> dict:
    url = "https://api.x.com/2/tweets"
    payload = {"text": text}
    if reply_to:
        payload["reply"] = {"in_reply_to_tweet_id": reply_to}
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={
            "Authorization": oauth1_header("POST", url),
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=20) as response:
            raw_body = response.read().decode("utf-8", errors="replace")
            return json.loads(raw_body) if raw_body else {}
    except HTTPError as exc:
        raw_body = exc.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw_body) if raw_body else {}
        except json.JSONDecodeError:
            data = {"raw": raw_body[:1000]}
        print(f"[fail] X post failed with HTTP {exc.code}.")
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
        raise SystemExit(1)
    except URLError as exc:
        print(f"[fail] Network error: {exc.reason}")
        raise SystemExit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Publish a post to X with an explicit confirmation gate.")
    parser.add_argument("--text", required=True, help="Post text to publish.")
    parser.add_argument("--reply-to", help="Post ID to reply to. Omit for a standalone post.")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Actually publish. Without this flag the command is a dry run.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    text = args.text.strip()
    if not text:
        print("[fail] --text cannot be empty.")
        raise SystemExit(1)

    load_dotenv(Path(".env"))
    require_env()

    print("[info] Prepared X post:")
    print(text)
    print(f"[info] Character count: {len(text)}")
    if args.reply_to:
        print(f"[info] Reply target post id: {args.reply_to}")

    if "http://" in text or "https://" in text:
        print("[warn] Text contains a URL; X API pricing may charge this as a URL post.")

    if not args.confirm:
        print("[dry-run] No network request was made and no post was published.")
        print("[dry-run] Add --confirm to publish this exact text.")
        return

    data = post_to_x(text, args.reply_to)
    post_data = data.get("data", {})
    post_id = post_data.get("id")
    if not post_id:
        print("[fail] X API returned success-like response without a post id.")
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
        raise SystemExit(1)

    print(f"[ok] Published post id: {post_id}")
    print(f"[ok] URL: https://x.com/syz277527/status/{post_id}")


if __name__ == "__main__":
    main()
