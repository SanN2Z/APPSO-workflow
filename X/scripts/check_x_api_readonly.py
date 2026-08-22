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
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen


sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
X_ROOT = Path(__file__).resolve().parents[1]


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


def percent(value: str) -> str:
    return quote(value, safe="")


def oauth1_header(method: str, url: str, query_params: dict[str, str]) -> str:
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
    signature_params = {**query_params, **oauth_params}
    normalized = "&".join(
        f"{percent(k)}={percent(v)}" for k, v in sorted(signature_params.items())
    )
    base_url = urlparse(url)._replace(query="", fragment="").geturl()
    base_string = "&".join([method.upper(), percent(base_url), percent(normalized)])
    signing_key = f"{percent(consumer_secret)}&{percent(access_token_secret)}"
    digest = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    oauth_params["oauth_signature"] = base64.b64encode(digest).decode()

    return "OAuth " + ", ".join(
        f'{percent(k)}="{percent(v)}"' for k, v in sorted(oauth_params.items())
    )


def get_json(url: str, headers: dict[str, str]) -> tuple[int, dict]:
    request = Request(url, headers=headers, method="GET")
    try:
        with urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status, json.loads(body) if body else {}
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body) if body else {}
        except json.JSONDecodeError:
            parsed = {"raw": body[:500]}
        return exc.code, parsed
    except URLError as exc:
        print(f"[fail] Network error: {exc.reason}")
        raise SystemExit(1)


def require_env(keys: list[str]) -> None:
    missing = [key for key in keys if is_placeholder(os.environ.get(key, ""))]
    if missing:
        print("[fail] Missing or placeholder settings:")
        for key in missing:
            print(f"  - {key}")
        raise SystemExit(1)


def check_bearer() -> bool:
    if is_placeholder(os.environ.get("X_BEARER_TOKEN", "")):
        print("[skip] X_BEARER_TOKEN is not set.")
        return False

    query = {"user.fields": "id,name,username,verified"}
    url = "https://api.x.com/2/users/by/username/xdevelopers?" + urlencode(query)
    status, data = get_json(url, {"Authorization": f"Bearer {os.environ['X_BEARER_TOKEN']}"})
    if status == 200 and "data" in data:
        user = data["data"]
        print(f"[ok] Bearer token can read public data: @{user.get('username')} ({user.get('id')})")
        return True

    print(f"[fail] Bearer token public read failed with HTTP {status}.")
    print(json.dumps(data, ensure_ascii=False, indent=2)[:1000])
    return False


def check_user_context() -> bool:
    require_env(["X_API_KEY", "X_API_KEY_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"])

    query = {"user.fields": "id,name,username"}
    base_url = "https://api.x.com/2/users/me"
    url = base_url + "?" + urlencode(query)
    headers = {"Authorization": oauth1_header("GET", base_url, query)}
    status, data = get_json(url, headers)
    if status == 200 and "data" in data:
        user = data["data"]
        print(f"[ok] Access token can read authorized account: @{user.get('username')} ({user.get('id')})")
        return True

    print(f"[fail] Authorized-account read failed with HTTP {status}.")
    print(json.dumps(data, ensure_ascii=False, indent=2)[:1000])
    return False


def main() -> None:
    argparse.ArgumentParser(
        description="Validate X API read access without performing a write."
    ).parse_args()
    load_dotenv(X_ROOT / ".env")
    bearer_ok = check_bearer()
    user_ok = check_user_context()

    if bearer_ok and user_ok:
        print("[ok] Read-only X API validation passed.")
        print("[ok] No write action was performed.")
        return

    print("[fail] One or more read-only X API checks failed.")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
