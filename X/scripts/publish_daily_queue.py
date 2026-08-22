import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from post_x import load_dotenv, post_to_x, require_env


sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
X_ROOT = Path(__file__).resolve().parents[1]


def today_jst() -> str:
    return datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d")


def queue_path_for(date_value: str) -> Path:
    return X_ROOT / "content" / f"{date_value}_daily_viral_queue.md"


def log_path_for(date_value: str) -> Path:
    return X_ROOT / "content" / f"{date_value}_auto_publish_log.json"


def load_log(path: Path) -> dict:
    if not path.exists():
        return {"published": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[fail] Invalid JSON log file {path}: {exc}")
        raise SystemExit(1)


def save_log(path: Path, log_data: dict) -> None:
    path.write_text(json.dumps(log_data, ensure_ascii=False, indent=2), encoding="utf-8")


def extract_drafts(markdown: str) -> dict[int, str]:
    drafts: dict[int, str] = {}
    pattern = re.compile(
        r"^###\s+Draft\s+(\d+)\s*$.*?```(?:text)?\s*\n(.*?)\n```",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    for match in pattern.finditer(markdown):
        index = int(match.group(1))
        text = match.group(2).strip()
        drafts[index] = text
    return drafts


def validate_text(text: str) -> None:
    if not text:
        print("[fail] Draft text is empty.")
        raise SystemExit(1)
    if len(text) > 280:
        print(f"[fail] Draft is too long for auto-publish: {len(text)} chars > 280.")
        raise SystemExit(1)
    if "http://" in text or "https://" in text:
        print("[fail] Auto-publish drafts may not contain URLs.")
        raise SystemExit(1)
    if "@" in text:
        print("[fail] Auto-publish drafts may not contain @ mentions.")
        raise SystemExit(1)
    if "#" in text:
        print("[fail] Auto-publish drafts may not contain hashtags.")
        raise SystemExit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Publish one draft from today's daily viral queue.")
    parser.add_argument("--date", help="Queue date in YYYY-MM-DD, defaults to Asia/Tokyo today.")
    parser.add_argument("--draft", type=int, required=True, help="Draft number to publish.")
    parser.add_argument("--confirm", action="store_true", help="Actually publish. Without this flag, dry-run only.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.date = args.date or today_jst()
    queue_path = queue_path_for(args.date)
    log_path = log_path_for(args.date)

    if not queue_path.exists():
        print(f"[fail] Missing queue file: {queue_path}")
        raise SystemExit(1)

    drafts = extract_drafts(queue_path.read_text(encoding="utf-8"))
    if args.draft not in drafts:
        print(f"[fail] Draft {args.draft} not found in {queue_path}. Expected sections like '### Draft {args.draft}'.")
        raise SystemExit(1)

    text = drafts[args.draft]
    validate_text(text)

    log_data = load_log(log_path)
    key = str(args.draft)
    if key in log_data.get("published", {}):
        print(f"[fail] Draft {args.draft} was already published.")
        print(json.dumps(log_data["published"][key], ensure_ascii=False, indent=2))
        raise SystemExit(1)

    print(f"[info] Queue: {queue_path}")
    print(f"[info] Draft: {args.draft}")
    print("[info] Prepared auto-publish text:")
    print(text)
    print(f"[info] Character count: {len(text)}")

    if not args.confirm:
        print("[dry-run] No network request was made and no post was published.")
        print("[dry-run] Add --confirm to publish this exact draft.")
        return

    load_dotenv(X_ROOT / ".env")
    require_env()
    data = post_to_x(text)
    post_data = data.get("data", {})
    post_id = post_data.get("id")
    if not post_id:
        print("[fail] X API returned success-like response without a post id.")
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
        raise SystemExit(1)

    log_data.setdefault("published", {})[key] = {
        "post_id": post_id,
        "url": f"https://x.com/syz277527/status/{post_id}",
        "text": text,
        "published_at_jst": datetime.now(ZoneInfo("Asia/Tokyo")).isoformat(),
    }
    save_log(log_path, log_data)

    print(f"[ok] Published draft {args.draft}: {post_id}")
    print(f"[ok] URL: https://x.com/syz277527/status/{post_id}")


if __name__ == "__main__":
    main()
