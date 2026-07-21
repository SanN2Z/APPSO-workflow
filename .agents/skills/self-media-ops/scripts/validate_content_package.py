# -*- coding: utf-8 -*-
"""Validate a self-media content package without external dependencies."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


REQUIRED_FILES = (
    "brief.md",
    "draft.md",
    "sources.md",
    "copyedit.md",
    "review.md",
    "asset-manifest.yml",
    "publish-record.md",
)
ALLOWED_PLATFORMS = {"wechat", "x"}
ALLOWED_STATES = {
    "idea",
    "research",
    "draft",
    "fact_checked",
    "editorial_review",
    "ready",
    "published",
    "archived",
}
BOOLEAN_VALUES = {"true", "false"}
COPYEDIT_STATES = {"pass", "needs_fix"}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
IMAGE_SUFFIXES = {".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}
IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
MANIFEST_FILE_PATTERN = re.compile(r"^\s*-?\s*file:\s*[\"']?([^\"'\n]+)", re.MULTILINE)
WINDOWS_ABSOLUTE_PATTERN = re.compile(r"\b[A-Za-z]:[\\/]")
SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{16,}\b"),
    re.compile(
        r"^(?:[A-Z0-9_]*(?:API_KEY|ACCESS_TOKEN|SECRET|BEARER_TOKEN))\s*=\s*(?!replace_|$).+",
        re.MULTILINE,
    ),
)


def split_frontmatter(text: str, source_name: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{source_name} must start with YAML frontmatter")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise ValueError(f"{source_name} frontmatter is not closed") from exc

    values: dict[str, str] = {}
    for raw_line in lines[1:end]:
        line = raw_line.rstrip("\r\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"invalid {source_name} frontmatter line: {line}")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"\'')
    return values, "".join(lines[end + 1 :])


def parse_frontmatter(text: str, source_name: str) -> dict[str, str]:
    values, _ = split_frontmatter(text, source_name)
    return values


def copyedit_body_sha256(draft: str) -> str:
    _, body = split_frontmatter(draft, "draft.md")
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def normalize_markdown_target(target: str) -> str:
    target = target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    return target.split("#", 1)[0]


def validate(package: Path) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    warnings: list[str] = []
    package = package.resolve()

    if not package.is_dir():
        return [f"package does not exist or is not a directory: {package}"], warnings, 0

    for name in REQUIRED_FILES:
        if not (package / name).is_file():
            errors.append(f"missing required file: {name}")

    draft_path = package / "draft.md"
    copyedit_path = package / "copyedit.md"
    manifest_path = package / "asset-manifest.yml"
    if not draft_path.is_file() or not manifest_path.is_file():
        return errors, warnings, 0

    draft = draft_path.read_text(encoding="utf-8")
    manifest = manifest_path.read_text(encoding="utf-8")

    try:
        metadata = parse_frontmatter(draft, "draft.md")
    except ValueError as exc:
        errors.append(str(exc))
        metadata = {}

    try:
        actual_copyedit_hash = copyedit_body_sha256(draft)
    except ValueError as exc:
        errors.append(str(exc))
        actual_copyedit_hash = ""

    copyedit_metadata: dict[str, str] = {}
    if copyedit_path.is_file():
        copyedit = copyedit_path.read_text(encoding="utf-8")
        try:
            copyedit_metadata = parse_frontmatter(copyedit, "copyedit.md")
        except ValueError as exc:
            errors.append(str(exc))

    for key in (
        "title",
        "platform",
        "status",
        "created",
        "updated",
        "as_of",
        "fact_checked",
        "rights_checked",
        "copyedit_checked",
        "copyedit_body_sha256",
        "published_url",
    ):
        if key not in metadata:
            errors.append(f"missing frontmatter field: {key}")

    platform = metadata.get("platform", "")
    status = metadata.get("status", "")
    if platform and platform not in ALLOWED_PLATFORMS:
        errors.append(f"unsupported platform: {platform}")
    if status and status not in ALLOWED_STATES:
        errors.append(f"unsupported status: {status}")
    for key in ("fact_checked", "rights_checked", "copyedit_checked"):
        value = metadata.get(key, "").lower()
        if value not in BOOLEAN_VALUES:
            errors.append(f"{key} must be true or false, got: {metadata.get(key, '')}")

    for key in ("status", "checked_at", "body_sha256", "scope"):
        if copyedit_path.is_file() and key not in copyedit_metadata:
            errors.append(f"missing copyedit.md frontmatter field: {key}")
    copyedit_status = copyedit_metadata.get("status", "")
    copyedit_report_hash_raw = copyedit_metadata.get("body_sha256", "")
    copyedit_report_hash = copyedit_report_hash_raw.lower()
    if copyedit_status and copyedit_status not in COPYEDIT_STATES:
        errors.append(f"unsupported copyedit.md status: {copyedit_status}")
    if copyedit_report_hash_raw and not SHA256_PATTERN.fullmatch(copyedit_report_hash_raw):
        errors.append("copyedit.md body_sha256 must be 64 lowercase hexadecimal characters")

    copyedit_checked = metadata.get("copyedit_checked", "").lower()
    declared_copyedit_hash_raw = metadata.get("copyedit_body_sha256", "")
    declared_copyedit_hash = declared_copyedit_hash_raw.lower()
    if declared_copyedit_hash_raw and not SHA256_PATTERN.fullmatch(declared_copyedit_hash_raw):
        errors.append("copyedit_body_sha256 must be 64 lowercase hexadecimal characters")
    if copyedit_checked == "true":
        if not declared_copyedit_hash:
            errors.append("copyedit_checked: true requires copyedit_body_sha256")
        elif actual_copyedit_hash and declared_copyedit_hash != actual_copyedit_hash:
            errors.append(
                "copyedit body hash is stale; set copyedit_checked: false and re-run the full copyedit gate"
            )
        if copyedit_status != "pass":
            errors.append("copyedit_checked: true requires copyedit.md status: pass")
        if copyedit_report_hash != declared_copyedit_hash:
            errors.append("copyedit.md body_sha256 must match draft copyedit_body_sha256")

    if status in {"ready", "published"}:
        if metadata.get("fact_checked", "").lower() != "true":
            errors.append(f"{status} status requires fact_checked: true")
        if metadata.get("rights_checked", "").lower() != "true":
            errors.append(f"{status} status requires rights_checked: true")
        if copyedit_checked != "true":
            errors.append(f"{status} status requires copyedit_checked: true")
    if status == "published" and not metadata.get("published_url", ""):
        errors.append("published status requires published_url")

    if WINDOWS_ABSOLUTE_PATTERN.search(draft):
        errors.append("draft.md contains an absolute Windows path")

    manifest_files = {value.replace("\\", "/") for value in MANIFEST_FILE_PATTERN.findall(manifest)}
    image_count = 0
    for raw_target in IMAGE_PATTERN.findall(draft):
        target = normalize_markdown_target(raw_target)
        if target.startswith(("http://", "https://", "data:")):
            warnings.append(f"remote image is not packaged locally: {target}")
            continue
        image_count += 1
        if WINDOWS_ABSOLUTE_PATTERN.search(target) or target.startswith("/"):
            errors.append(f"image path must be package-relative: {target}")
            continue
        resolved = (package / target).resolve()
        if not resolved.is_relative_to(package):
            errors.append(f"image path escapes package: {target}")
            continue
        if not resolved.is_file():
            errors.append(f"missing image: {target}")
        if target.replace("\\", "/") not in manifest_files:
            errors.append(f"image is not registered in asset-manifest.yml: {target}")

    for value in manifest_files:
        path = (package / value).resolve()
        if not path.is_relative_to(package):
            errors.append(f"manifest path escapes package: {value}")
        elif not path.is_file():
            errors.append(f"manifest file does not exist: {value}")

    for directory in (package / "assets", package / "research" / "source-assets"):
        if not directory.is_dir():
            continue
        for path in directory.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            relative = path.relative_to(package).as_posix()
            if relative not in manifest_files:
                errors.append(f"image file is not registered in asset-manifest.yml: {relative}")

    sources_path = package / "sources.md"
    if sources_path.is_file():
        sources = sources_path.read_text(encoding="utf-8")
        if "http://" not in sources and "https://" not in sources:
            warnings.append("sources.md contains no web source URL")
        normalized_sources = sources.lower()
        if "访问日期" not in sources and "access date" not in normalized_sources:
            errors.append("sources.md must record an access date for each source")

    scan_paths = [package / name for name in REQUIRED_FILES if (package / name).is_file()]
    for path in scan_paths:
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"possible credential in {path.name}; value not printed")
                break

    return errors, warnings, image_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, help="Path to one content package")
    parser.add_argument(
        "--print-copyedit-hash",
        action="store_true",
        help="Print the SHA-256 of the Markdown body after draft frontmatter and exit",
    )
    args = parser.parse_args()

    if args.print_copyedit_hash:
        draft_path = args.package.resolve() / "draft.md"
        if not draft_path.is_file():
            print(f"[fail] missing draft.md: {draft_path}", file=sys.stderr)
            return 1
        try:
            draft = draft_path.read_text(encoding="utf-8")
            body_hash = copyedit_body_sha256(draft)
        except (OSError, UnicodeError, ValueError) as exc:
            print(f"[fail] could not compute copyedit body hash: {exc}", file=sys.stderr)
            return 1
        print(f"[copyedit] body_sha256={body_hash}")
        return 0

    errors, warnings, image_count = validate(args.package)
    for warning in warnings:
        print(f"[warn] {warning}")
    for error in errors:
        print(f"[fail] {error}", file=sys.stderr)

    if errors:
        print(f"[fail] validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1

    print(f"[ok] content package valid; markdown_images={image_count} warnings={len(warnings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
