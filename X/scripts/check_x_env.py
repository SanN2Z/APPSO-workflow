import argparse
import os
import sys
from pathlib import Path


sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


REQUIRED_KEYS = [
    "X_API_KEY",
    "X_API_KEY_SECRET",
    "X_ACCESS_TOKEN",
    "X_ACCESS_TOKEN_SECRET",
]
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


def main() -> None:
    argparse.ArgumentParser(
        description="Check local X API settings without making a network request."
    ).parse_args()
    load_dotenv(X_ROOT / ".env")

    missing = []
    for key in REQUIRED_KEYS:
        value = os.environ.get(key, "")
        if is_placeholder(value):
            missing.append(key)

    if missing:
        print("[fail] Missing or placeholder X API settings:")
        for key in missing:
            print(f"  - {key}")
        raise SystemExit(1)

    print("[ok] Required X API environment variables are present.")
    print("[ok] No network request was made and no post was published.")


if __name__ == "__main__":
    main()
