#!/usr/bin/env python3
"""Bridge project content packages to the pinned Wenyan CLI.

Wenyan owns Markdown rendering, image uploads, and WeChat API calls. This file
only adapts the project's content-package schema and enforces local release
gates. The default is preview/dry-run; ``draft --execute`` is the only command
that can create an external WeChat draft.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import mimetypes
import os
import re
import secrets
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlparse

import yaml
from PIL import Image, UnidentifiedImageError
from tinycss2 import parse_declaration_list


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
WECHAT_ROOT = Path(__file__).resolve().parents[1]
WENYAN_CMD = WECHAT_ROOT / "node_modules" / ".bin" / "wenyan.cmd"
VALIDATOR = (
    WORKSPACE_ROOT
    / ".agents"
    / "skills"
    / "self-media-ops"
    / "scripts"
    / "validate_content_package.py"
)
WENYAN_RUNTIME = WECHAT_ROOT / ".wenyan-runtime"
THEMES_ROOT = WECHAT_ROOT / "themes"
EDITORIAL_TIMEZONE = timezone(timedelta(hours=8), name="Asia/Shanghai")
MAX_FOOTER_REVIEW_DAYS = 365

FRONTMATTER_RE = re.compile(r"\A---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)\Z", re.S)
HTML_IMAGE_RE = re.compile(
    r"(?P<prefix><img\b(?:(?!\s+src\s*=)[^>])*\s+src\s*=\s*)"
    r"(?:(?P<quote>[\"'])(?P<quoted_target>.*?)(?P=quote)|"
    r"(?P<unquoted_target>[^\s>]+))",
    re.I,
)
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RELEASE_IMAGE_FORMATS = {
    ".gif": "GIF",
    ".jpeg": "JPEG",
    ".jpg": "JPEG",
    ".png": "PNG",
    ".webp": "WEBP",
}
BLOCKED_REMOTE_IMAGE = (
    "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="
)
ACTIVE_HTML_TAGS = {
    "audio",
    "base",
    "embed",
    "form",
    "iframe",
    "link",
    "meta",
    "object",
    "picture",
    "script",
    "source",
    "style",
    "svg",
    "track",
    "video",
}
SCRIPTABLE_URL_ATTRIBUTES = {
    "action",
    "formaction",
    "href",
    "src",
    "srcdoc",
    "xlink:href",
}
ALLOWED_NAVIGATION_SCHEMES = {"http", "https", "mailto", "tel"}
CSS_RESOURCE_FUNCTIONS = {
    "-moz-element",
    "-webkit-cross-fade",
    "-webkit-image-set",
    "cross-fade",
    "element",
    "image",
    "image-set",
    "paint",
    "url",
}

RELEASE_RIGHTS_STATUSES = {
    "cc0_verified",
    "licensed",
    "project_owned",
    "project_owned_with_cc0_component",
    "public_domain_verified",
    "user_confirmed_editorial_commentary",
    "user_confirmed_editorial_use",
}
WENYAN_NOTES = [
    "Wenyan CLI 2.0.11 does not forward a custom digest to draft/add; WeChat will derive it, so check or edit the digest in the backend.",
    "Wenyan CLI 2.0.11 uploads body images as permanent image materials and caches repeat uploads.",
]


class WorkflowError(RuntimeError):
    """A user-actionable workflow failure."""


@dataclass(frozen=True)
class LayoutProfile:
    profile_id: str
    custom_theme: Path | None = None
    required_header: bool = False
    supports_body_components: bool = False
    component_class_prefix: str | None = None


LAYOUT_PROFILES = {
    "default": LayoutProfile(profile_id="default"),
    "appsso-article-v1": LayoutProfile(
        profile_id="appsso-article-v1",
        custom_theme=WECHAT_ROOT / "themes" / "appsso-article-v1.css",
        required_header=True,
        supports_body_components=True,
        component_class_prefix="appsso-body",
    ),
}


@dataclass(frozen=True)
class PublishConfig:
    title: str
    author: str = ""
    digest: str = ""
    cover: str = ""
    source_url: str = ""
    theme: str = "default"
    layout_profile: str = "default"
    highlight: str = "solarized-light"
    mac_style: bool = False
    footnote: bool = True
    need_open_comment: bool = False
    only_fans_can_comment: bool = False
    header_image: str = ""
    header_alt: str = ""
    footer_image: str = ""
    footer_alt: str = ""
    footer_valid_until: str = ""


@dataclass(frozen=True)
class BuildSnapshot:
    package_files: dict[str, str]
    package_sha256: str
    staged_files: dict[str, str]
    staged_sha256: str
    source_sha256: str
    theme_snapshot_sha256: str | None
    canonical_theme_sha256: str | None


@dataclass(frozen=True)
class PreviewBuild:
    preview_path: Path
    source: Path
    theme_snapshot: Path | None
    metadata: dict[str, Any]
    config: PublishConfig
    blockers: list[str]
    validator_ok: bool
    validator_report: str
    snapshot: BuildSnapshot


class ImageSourceParser(HTMLParser):
    """Extract rendered image sources and reserved APPSO component wrappers."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sources: list[str] = []
        self.component_counts = {"header": 0, "footer": 0}

    def inspect(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attribute_map: dict[str, str] = {}
        for name, value in attrs:
            attribute_map.setdefault(name.casefold(), value or "")
        if tag.casefold() == "section":
            classes = set(attribute_map.get("class", "").split())
            for kind in self.component_counts:
                if f"appsso-body-{kind}" in classes:
                    self.component_counts[kind] += 1
        if tag.casefold() == "img" and "src" in attribute_map:
            self.sources.append(attribute_map["src"])

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.inspect(tag, attrs)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.inspect(tag, attrs)


class PassiveHtmlParser(HTMLParser):
    """Reject active markup before a rendered fragment enters the local preview."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.problems: list[str] = []

    def inspect(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        normalized_tag = tag.casefold()
        if normalized_tag in ACTIVE_HTML_TAGS:
            self.problems.append(f"active HTML tag <{normalized_tag}> is not allowed")
        normalized_names = [name.casefold() for name, _ in attrs]
        if normalized_tag == "img":
            src_count = normalized_names.count("src")
            if src_count != 1:
                self.problems.append(
                    f"rendered img must contain exactly one src attribute; found {src_count}"
                )
        for raw_name, raw_value in attrs:
            name = raw_name.casefold()
            if name in {"background", "data-src", "poster", "srcset"}:
                self.problems.append(
                    f"resource-loading attribute {raw_name} is not allowed"
                )
            if name == "src" and normalized_tag != "img":
                self.problems.append(
                    f"resource-loading src on <{normalized_tag}> is not allowed"
                )
            if name.startswith("on"):
                self.problems.append(
                    f"event-handler attribute {raw_name} is not allowed"
                )
            if name == "style" and style_has_resource_reference(raw_value or ""):
                self.problems.append(
                    "resource reference in a rendered style attribute is not allowed"
                )
            if raw_value is None or name not in SCRIPTABLE_URL_ATTRIBUTES:
                continue
            compact_value = re.sub(
                r"[\x00-\x20]+", "", unquote(raw_value)
            ).casefold()
            scheme_match = re.match(r"^([a-z][a-z0-9+.-]*):", compact_value)
            if scheme_match and scheme_match.group(1) not in ALLOWED_NAVIGATION_SCHEMES:
                self.problems.append(
                    f"URL scheme in attribute {raw_name} is not allowed"
                )

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.inspect(tag, attrs)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.inspect(tag, attrs)


def css_tokens_have_resource(tokens: list[Any]) -> bool:
    for token in tokens:
        token_type = getattr(token, "type", "")
        if token_type in {"error", "url"}:
            return True
        if token_type == "function":
            if getattr(token, "lower_name", "") in CSS_RESOURCE_FUNCTIONS:
                return True
            if css_tokens_have_resource(list(getattr(token, "arguments", []))):
                return True
        content = getattr(token, "content", None)
        if content and css_tokens_have_resource(list(content)):
            return True
    return False


def style_has_resource_reference(style: str) -> bool:
    declarations = parse_declaration_list(
        html.unescape(unquote(style)), skip_comments=True, skip_whitespace=True
    )
    for declaration in declarations:
        if getattr(declaration, "type", "") == "error":
            return True
        if css_tokens_have_resource(list(getattr(declaration, "value", []))):
            return True
    return False


def is_link_or_junction(path: Path) -> bool:
    is_junction = getattr(os.path, "isjunction", lambda _: False)
    return path.is_symlink() or bool(is_junction(path))


def is_multiply_linked_file(path: Path) -> bool:
    return path.is_file() and path.stat().st_nlink != 1


def canonical_package_relative_path(
    raw_path: str,
    label: str,
    *,
    require_assets: bool = False,
) -> str:
    decoded = decode_image_target(raw_path).replace("\\", "/")
    parsed = urlparse(decoded)
    if (
        parsed.scheme
        or parsed.netloc
        or parsed.query
        or parsed.fragment
        or decoded.startswith("/")
        or re.match(r"^[A-Za-z]:", decoded)
    ):
        raise WorkflowError(f"{label} must be a package-relative local path")
    parts = PurePosixPath(decoded).parts
    if not parts or any(part in {"", ".", ".."} or ":" in part for part in parts):
        raise WorkflowError(
            f"{label} contains an unsafe path segment; '.', '..', and ':' are not allowed"
        )
    if require_assets and parts[0].casefold() != "assets":
        raise WorkflowError(f"{label} must be stored under the package assets/ directory")
    return PurePosixPath(*parts).as_posix()


def safe_dist(package: Path) -> Path:
    package_resolved = package.resolve()
    dist = package / "dist"
    if dist.exists() or dist.is_symlink():
        if is_link_or_junction(dist):
            raise WorkflowError(f"dist must not be a symlink or junction: {dist}")
        if not dist.is_dir():
            raise WorkflowError(f"dist exists but is not a directory: {dist}")
    else:
        dist.mkdir(parents=True, exist_ok=False)
    try:
        dist.resolve().relative_to(package_resolved)
    except ValueError as exc:
        raise WorkflowError(f"dist escapes the content package: {dist}") from exc
    return dist


def create_build_dir(package: Path) -> Path:
    dist = safe_dist(package)
    builds = dist / "builds"
    if builds.exists() or builds.is_symlink():
        if is_link_or_junction(builds) or not builds.is_dir():
            raise WorkflowError(f"dist/builds must be a regular directory: {builds}")
    else:
        builds.mkdir(exist_ok=False)
    for _ in range(8):
        candidate = builds / f"build-{secrets.token_hex(12)}"
        try:
            candidate.mkdir(exist_ok=False)
        except FileExistsError:
            continue
        return candidate
    raise WorkflowError("could not allocate a unique Wenyan build directory")


def atomic_write_bytes(path: Path, data: bytes) -> None:
    if path.exists() or path.is_symlink():
        if is_link_or_junction(path):
            raise WorkflowError(f"generated output must not be a symlink or junction: {path}")
        if not path.is_file():
            raise WorkflowError(f"generated output is not a regular file: {path}")
    parent = path.parent
    if is_link_or_junction(parent):
        raise WorkflowError(f"generated output parent must not be a link: {parent}")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def atomic_write_text(path: Path, content: str) -> None:
    atomic_write_bytes(path, content.encode("utf-8"))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        before = os.fstat(handle.fileno())
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
        after = os.fstat(handle.fileno())
    fingerprint_before = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
    )
    fingerprint_after = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    )
    if fingerprint_before != fingerprint_after:
        raise WorkflowError(f"file changed while hashing: {path}")
    return digest.hexdigest()


def stable_file_bytes(path: Path) -> bytes:
    if is_link_or_junction(path):
        raise WorkflowError(f"input must not be a symlink or junction: {path}")
    with path.open("rb") as handle:
        before = os.fstat(handle.fileno())
        if before.st_nlink != 1:
            raise WorkflowError(f"input must not be a hardlink: {path}")
        payload = handle.read()
        after = os.fstat(handle.fileno())
    fingerprint_before = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
    )
    fingerprint_after = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    )
    if fingerprint_before != fingerprint_after:
        raise WorkflowError(f"file changed while reading: {path}")
    return payload


def package_input_hashes(package: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(package.rglob("*"), key=lambda item: item.as_posix().casefold()):
        relative = path.relative_to(package)
        if relative.parts and relative.parts[0].casefold() == "dist":
            continue
        if is_link_or_junction(path):
            raise WorkflowError(f"content package input must not be a link: {relative.as_posix()}")
        if path.is_file():
            if is_multiply_linked_file(path):
                raise WorkflowError(
                    f"content package input must not be a hardlink: {relative.as_posix()}"
                )
            hashes[relative.as_posix()] = file_sha256(path)
    return hashes


def build_input_hashes(build_dir: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(build_dir.rglob("*"), key=lambda item: item.as_posix().casefold()):
        relative = path.relative_to(build_dir)
        if is_link_or_junction(path):
            raise WorkflowError(f"staged build input must not be a link: {relative.as_posix()}")
        if path.is_file():
            if is_multiply_linked_file(path):
                raise WorkflowError(
                    f"staged build input must not be a hardlink: {relative.as_posix()}"
                )
            hashes[relative.as_posix()] = file_sha256(path)
    return hashes


@contextmanager
def sealed_package_snapshot(
    package: Path, expected_hashes: dict[str, str]
):
    """Yield a temporary package copy whose bytes match the initial preflight hash."""

    with tempfile.TemporaryDirectory(prefix="wechat-package-snapshot-") as temp_dir:
        snapshot = Path(temp_dir) / "package"
        snapshot.mkdir()
        for relative, expected_hash in expected_hashes.items():
            relative_path = Path(relative)
            if any(part.casefold() == ".env" for part in relative_path.parts):
                continue
            source = package / relative_path
            payload = stable_file_bytes(source)
            actual_hash = hashlib.sha256(payload).hexdigest()
            if actual_hash != expected_hash:
                raise WorkflowError(
                    f"content package changed while sealing input: {relative}"
                )
            destination = snapshot / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            atomic_write_bytes(destination, payload)
        yield snapshot


@contextmanager
def exclusive_publish_lock(package: Path):
    lock_path = safe_dist(package) / ".wechat-publish.lock"
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise WorkflowError(
            "another WeChat draft operation holds the package publish lock"
        ) from exc
    try:
        os.write(descriptor, f"pid={os.getpid()}\n".encode("ascii"))
        os.fsync(descriptor)
        yield
    finally:
        os.close(descriptor)
        if lock_path.exists():
            lock_path.unlink()


def combined_hash(items: dict[str, str]) -> str:
    payload = json.dumps(items, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def decode_image_target(target: str) -> str:
    clean = html.unescape(target.strip())
    if clean.startswith("<") and clean.endswith(">"):
        clean = clean[1:-1]
    return unquote(clean)


def matched_html_image_target(match: re.Match[str]) -> str:
    quoted = match.group("quoted_target")
    return quoted if quoted is not None else match.group("unquoted_target")


def replace_html_image_target(match: re.Match[str], target: str) -> str:
    quote = match.group("quote") or '"'
    return match.group("prefix") + quote + target + quote


def raw_html_image_sources(fragment: str) -> list[str]:
    parser = ImageSourceParser()
    parser.feed(fragment)
    parser.close()
    return parser.sources


def ensure_passive_preview_html(fragment: str) -> None:
    parser = PassiveHtmlParser()
    parser.feed(fragment)
    parser.close()
    if parser.problems:
        unique = list(dict.fromkeys(parser.problems))
        raise WorkflowError(
            "rendered content contains active HTML that is unsafe for local preview:\n- "
            + "\n- ".join(unique)
        )


def image_file_problem(path: Path) -> str | None:
    expected_format = RELEASE_IMAGE_FORMATS.get(path.suffix.casefold())
    if expected_format is None:
        allowed = ", ".join(sorted(RELEASE_IMAGE_FORMATS))
        return f"unsupported image extension {path.suffix or '(none)'}; allowed: {allowed}"
    try:
        with Image.open(path) as image:
            actual_format = image.format
            width, height = image.size
            image.verify()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        return f"image cannot be decoded: {type(exc).__name__}"
    if actual_format != expected_format:
        return f"image format {actual_format or 'unknown'} does not match {path.suffix}"
    if width <= 0 or height <= 0:
        return "image dimensions must be positive"
    return None


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        raise WorkflowError(f"YAML root must be an object: {path}")
    return loaded


def load_draft(package: Path) -> tuple[dict[str, Any], str]:
    path = package / "draft.md"
    if not path.is_file():
        raise WorkflowError(f"draft not found: {path}")
    match = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if not match:
        raise WorkflowError(f"draft frontmatter is missing or malformed: {path}")
    metadata = yaml.safe_load(match.group(1)) or {}
    if not isinstance(metadata, dict):
        raise WorkflowError("draft frontmatter must be a YAML object")
    return metadata, match.group(2).strip() + "\n"


def strip_leading_h1(body: str) -> str:
    lines = body.splitlines()
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        if line.startswith("# "):
            lines.pop(index)
            while index < len(lines) and not lines[index].strip():
                lines.pop(index)
        break
    clean = "\n".join(lines).strip() + "\n"
    if not clean.strip():
        raise WorkflowError("draft body is empty after removing the editorial H1")
    return clean


def load_publish_config(package: Path, metadata: dict[str, Any]) -> PublishConfig:
    raw = load_yaml(package / "publish.yml")
    source_url = raw.get("source_url") or raw.get("content_source_url") or ""
    return PublishConfig(
        title=str(raw.get("title") or metadata.get("title") or "").strip(),
        author=str(raw.get("author") or "").strip(),
        digest=str(raw.get("digest") or "").strip(),
        cover=str(raw.get("cover") or "").strip(),
        source_url=str(source_url).strip(),
        theme=str(raw.get("theme") or "default").strip(),
        layout_profile=str(raw.get("layout_profile") or "default").strip(),
        highlight=str(raw.get("highlight") or "solarized-light").strip(),
        mac_style=bool(raw.get("mac_style", False)),
        footnote=bool(raw.get("footnote", True)),
        need_open_comment=bool(raw.get("need_open_comment", False)),
        only_fans_can_comment=bool(raw.get("only_fans_can_comment", False)),
        header_image=str(raw.get("header_image") or "").strip(),
        header_alt=str(raw.get("header_alt") or "").strip(),
        footer_image=str(raw.get("footer_image") or "").strip(),
        footer_alt=str(raw.get("footer_alt") or "").strip(),
        footer_valid_until=str(raw.get("footer_valid_until") or "").strip(),
    )


def get_layout_profile(config: PublishConfig) -> LayoutProfile:
    profile = LAYOUT_PROFILES.get(config.layout_profile)
    if profile is None:
        choices = ", ".join(sorted(LAYOUT_PROFILES))
        raise WorkflowError(
            f"unknown layout_profile {config.layout_profile!r}; choose one of: {choices}"
        )
    if profile.custom_theme is not None:
        if is_link_or_junction(profile.custom_theme):
            raise WorkflowError(
                f"layout theme must not be a symlink or junction: {profile.custom_theme}"
            )
        if not profile.custom_theme.is_file():
            raise WorkflowError(
                f"layout theme is missing for {profile.profile_id}: {profile.custom_theme}"
            )
        try:
            profile.custom_theme.resolve().relative_to(THEMES_ROOT.resolve())
        except ValueError as exc:
            raise WorkflowError(
                f"layout theme escapes the allowlisted themes directory: {profile.custom_theme}"
            ) from exc
    return profile


def is_remote_or_special(target: str) -> bool:
    parsed = urlparse(target)
    return bool(parsed.scheme) or target.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:[\\/]", target) is not None


def resolve_layout_asset(package: Path, raw_path: str, field: str) -> Path:
    normalized = canonical_package_relative_path(
        raw_path, field, require_assets=True
    )
    resolved = (package / normalized).resolve()
    try:
        resolved.relative_to(package.resolve())
    except ValueError as exc:
        raise WorkflowError(f"{field} path escapes the content package") from exc
    if not resolved.is_file():
        raise WorkflowError(f"{field} does not exist: {raw_path}")
    if is_link_or_junction(resolved) or is_multiply_linked_file(resolved):
        raise WorkflowError(f"{field} must not be a symlink, junction, or hardlink")
    problem = image_file_problem(resolved)
    if problem is not None:
        raise WorkflowError(f"{field} is not a valid release image: {problem}")
    return resolved


def layout_image_section(
    package: Path,
    raw_path: str,
    alt: str,
    kind: str,
    class_prefix: str,
) -> str:
    field = f"{kind}_image"
    resolve_layout_asset(package, raw_path, field)
    target = html.escape(
        canonical_package_relative_path(raw_path, field, require_assets=True),
        quote=True,
    )
    escaped_alt = html.escape(alt, quote=True)
    return (
        f'<section class="{class_prefix}-{kind}">'
        f'<img src="{target}" alt="{escaped_alt}">'
        "</section>"
    )


def apply_layout_components(package: Path, body: str, config: PublishConfig) -> str:
    profile = get_layout_profile(config)
    if (config.header_image or config.footer_image) and not profile.supports_body_components:
        raise WorkflowError(
            f"layout_profile {profile.profile_id} does not support header_image or footer_image"
        )
    class_prefix = profile.component_class_prefix
    if profile.supports_body_components and not class_prefix:
        raise WorkflowError(
            f"layout_profile {profile.profile_id} has no component class prefix"
        )
    parts: list[str] = []
    if config.header_image:
        parts.append(
            layout_image_section(
                package,
                config.header_image,
                config.header_alt,
                "header",
                class_prefix or "",
            )
        )
    parts.append(body.strip())
    if config.footer_image:
        parts.append(
            layout_image_section(
                package,
                config.footer_image,
                config.footer_alt,
                "footer",
                class_prefix or "",
            )
        )
    return "\n\n".join(parts).strip() + "\n"


def generated_frontmatter(config: PublishConfig) -> dict[str, Any]:
    frontmatter: dict[str, Any] = {"title": config.title}
    for key, value in (
        ("cover", config.cover),
        ("author", config.author),
        ("source_url", config.source_url),
    ):
        if value:
            frontmatter[key] = value
    frontmatter["need_open_comment"] = config.need_open_comment
    frontmatter["only_fans_can_comment"] = config.only_fans_can_comment
    return frontmatter


def prepare_source(
    package: Path, build_dir: Path | None = None
) -> tuple[Path, dict[str, Any], PublishConfig, str]:
    metadata, body = load_draft(package)
    config = load_publish_config(package, metadata)
    stripped_body = strip_leading_h1(body)
    layout_body = apply_layout_components(package, stripped_body, config)
    frontmatter = yaml.safe_dump(
        generated_frontmatter(config),
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    ).strip()
    selected_build_dir = build_dir or create_build_dir(package)
    source_path = selected_build_dir / "wenyan-source.md"
    atomic_write_text(source_path, f"---\n{frontmatter}\n---\n\n{layout_body}")
    return source_path, metadata, config, layout_body


def stage_layout_theme(dist: Path, config: PublishConfig) -> Path | None:
    profile = get_layout_profile(config)
    if profile.custom_theme is None:
        return None
    snapshot = dist / "layout-theme.css"
    atomic_write_bytes(snapshot, profile.custom_theme.read_bytes())
    return snapshot


def wenyan_args(
    command: str,
    source: Path,
    config: PublishConfig,
    custom_theme_path: Path | None = None,
) -> list[str]:
    if not WENYAN_CMD.is_file():
        raise WorkflowError(
            "Wenyan is not installed. Run `npm.cmd install` inside 微信公众号 first."
        )
    profile = get_layout_profile(config)
    args = [str(WENYAN_CMD), command, "-f", str(source), "-t", config.theme, "-h", config.highlight]
    selected_theme = custom_theme_path or profile.custom_theme
    if selected_theme is not None:
        if is_link_or_junction(selected_theme) or not selected_theme.is_file():
            raise WorkflowError(f"selected custom theme is not a regular file: {selected_theme}")
        args.extend(["--custom-theme", str(selected_theme.resolve())])
    args.append("--mac-style" if config.mac_style else "--no-mac-style")
    args.append("--footnote" if config.footnote else "--no-footnote")
    return args


def wenyan_environment() -> dict[str, str]:
    """Keep Wenyan token/material caches private and local to this project."""
    environment = os.environ.copy()
    environment["XDG_CONFIG_HOME"] = str(WENYAN_RUNTIME)
    return environment


def run_wenyan_render(
    source: Path, config: PublishConfig, custom_theme_path: Path | None = None
) -> str:
    result = subprocess.run(
        wenyan_args("render", source, config, custom_theme_path),
        cwd=WECHAT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        env=wenyan_environment(),
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise WorkflowError(f"Wenyan render failed ({result.returncode}): {detail}")
    rendered = result.stdout.strip()
    if not rendered:
        raise WorkflowError("Wenyan render returned empty HTML")
    return rendered


def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def inline_preview_images(fragment: str, image_base: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        target = decode_image_target(matched_html_image_target(match))
        if target.startswith("data:"):
            return match.group(0)
        if is_remote_or_special(target):
            return replace_html_image_target(match, BLOCKED_REMOTE_IMAGE)
        resolved = (image_base / target).resolve()
        try:
            resolved.relative_to(image_base.resolve())
        except ValueError as exc:
            raise WorkflowError(f"rendered image path escapes staged build: {target}") from exc
        if not resolved.is_file():
            raise WorkflowError(f"rendered local image is missing: {target}")
        problem = image_file_problem(resolved)
        if problem is not None:
            raise WorkflowError(
                f"rendered local image is not a valid preview image ({target}): {problem}"
            )
        return replace_html_image_target(match, data_uri(resolved))

    return HTML_IMAGE_RE.sub(replace, fragment)


def stage_asset_bytes(source: Path, build_dir: Path, relative_path: str) -> None:
    if is_link_or_junction(source) or is_multiply_linked_file(source):
        raise WorkflowError(
            f"release asset must not be a symlink, junction, or hardlink: {relative_path}"
        )
    destination = build_dir / Path(relative_path)
    try:
        destination.resolve().relative_to(build_dir.resolve())
    except ValueError as exc:
        raise WorkflowError(f"staged asset path escapes build: {relative_path}") from exc
    destination.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_bytes(destination, source.read_bytes())
    if file_sha256(destination) != file_sha256(source):
        raise WorkflowError(f"staged asset copy hash mismatch: {relative_path}")


def rendered_image_gate_and_stage(
    package: Path,
    build_dir: Path,
    rendered: str,
    config: PublishConfig,
) -> list[str]:
    """Audit the actual Wenyan image graph, then copy approved inputs to this build."""

    blockers: list[str] = []
    rendered_parser = ImageSourceParser()
    rendered_parser.feed(rendered)
    rendered_parser.close()
    manifest = load_yaml(package / "asset-manifest.yml")
    raw_assets = manifest.get("assets") or []
    assets = [item for item in raw_assets if isinstance(item, dict)]
    manifest_by_path: dict[str, dict[str, Any]] = {}
    for entry in assets:
        raw_file = str(entry.get("file") or "").strip()
        if not raw_file:
            continue
        try:
            normalized = canonical_package_relative_path(
                raw_file, "manifest asset", require_assets=True
            )
        except WorkflowError:
            continue
        manifest_by_path.setdefault(normalized, entry)

    component_uses: dict[str, str] = {}
    for raw_path, expected_use, label in (
        (config.header_image, "wechat_body_header", "header_image"),
        (config.footer_image, "wechat_body_footer", "footer_image"),
    ):
        if not raw_path:
            continue
        try:
            normalized = canonical_package_relative_path(
                raw_path, label, require_assets=True
            )
        except WorkflowError as exc:
            blockers.append(str(exc))
        else:
            component_uses[normalized] = expected_use

    rendered_counts: dict[str, int] = {}
    staged: set[str] = set()
    for raw_target in rendered_parser.sources:
        label = f"rendered body image {raw_target!r}"
        try:
            normalized = canonical_package_relative_path(
                raw_target, label, require_assets=True
            )
        except WorkflowError as exc:
            blockers.append(str(exc))
            continue
        rendered_counts[normalized] = rendered_counts.get(normalized, 0) + 1
        source = (package / normalized).resolve()
        try:
            source.relative_to(package.resolve())
        except ValueError:
            blockers.append(f"{label} escapes the content package")
            continue
        if not source.is_file():
            blockers.append(f"{label} does not exist in the content package")
            continue
        if is_link_or_junction(source) or is_multiply_linked_file(source):
            blockers.append(f"{label} must not be a symlink, junction, or hardlink")
            continue
        problem = image_file_problem(source)
        if problem is not None:
            blockers.append(f"{label} is not a valid release image: {problem}")
            continue

        entry = manifest_by_path.get(normalized)
        if entry is None:
            blockers.append(f"{label} is not registered in asset-manifest.yml")
        else:
            rights = str(entry.get("rights_status") or "").strip()
            platforms = entry.get("allowed_platforms") or []
            if rights not in RELEASE_RIGHTS_STATUSES:
                blockers.append(
                    f"{label} rights_status is not release-cleared: {rights or 'missing'}"
                )
            if not isinstance(platforms, list) or "wechat" not in platforms:
                blockers.append(f"{label} is not allowed for the wechat platform")
            expected_component_use = component_uses.get(normalized)
            if expected_component_use is not None:
                if str(entry.get("use") or "") != expected_component_use:
                    blockers.append(
                        f"{label} manifest use must be {expected_component_use}"
                    )
            elif entry.get("used_in_draft") is not True:
                blockers.append(
                    f"{label} manifest must declare used_in_draft: true"
                )

        if normalized not in staged:
            stage_asset_bytes(source, build_dir, normalized)
            staged.add(normalized)

    for normalized, expected_use in component_uses.items():
        count = rendered_counts.get(normalized, 0)
        if count != 1:
            blockers.append(
                f"{expected_use} must appear exactly once after Wenyan render; found {count}"
            )

    for kind, configured_path in (
        ("header", config.header_image),
        ("footer", config.footer_image),
    ):
        expected_count = 1 if configured_path else 0
        actual_count = rendered_parser.component_counts[kind]
        if actual_count != expected_count:
            blockers.append(
                f"appsso-body-{kind} wrapper must appear {expected_count} time(s) "
                f"after Wenyan render; found {actual_count}"
            )

    if config.cover:
        try:
            normalized_cover = canonical_package_relative_path(
                config.cover, "cover", require_assets=True
            )
            cover_source = (package / normalized_cover).resolve()
            cover_source.relative_to(package.resolve())
            if not cover_source.is_file():
                raise WorkflowError(f"cover does not exist: {config.cover}")
            if image_file_problem(cover_source) is not None:
                raise WorkflowError(f"cover is not a valid release image: {config.cover}")
            if normalized_cover not in staged:
                stage_asset_bytes(cover_source, build_dir, normalized_cover)
        except (ValueError, WorkflowError) as exc:
            message = str(exc)
            if message and message not in blockers:
                blockers.append(message)

    return list(dict.fromkeys(blockers))


def validator_report(package: Path) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(package)],
        cwd=WORKSPACE_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    report = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
    return result.returncode == 0, report


def publication_blockers(package: Path, metadata: dict[str, Any], config: PublishConfig) -> list[str]:
    blockers: list[str] = []
    if not config.title:
        blockers.append("publish title is empty")
    if len(config.title) > 32:
        blockers.append(f"publish title has {len(config.title)} characters; WeChat API limit is 32")
    if len(config.author) > 16:
        blockers.append(f"author has {len(config.author)} characters; WeChat API limit is 16")
    if len(config.digest) > 128:
        blockers.append(f"digest has {len(config.digest)} characters; WeChat API limit is 128")
    if str(metadata.get("status") or "") != "ready":
        blockers.append(f"content status is {metadata.get('status') or 'missing'}, not ready")
    for flag in ("fact_checked", "rights_checked", "copyedit_checked"):
        if metadata.get(flag) is not True:
            blockers.append(f"draft frontmatter has {flag} != true")

    manifest = load_yaml(package / "asset-manifest.yml")
    assets = manifest.get("assets") or []
    if not isinstance(assets, list):
        assets = []

    def asset_entry(raw_path: str) -> dict[str, Any] | None:
        try:
            normalized = canonical_package_relative_path(
                raw_path, "manifest asset", require_assets=True
            )
        except WorkflowError:
            return None
        return next(
            (
                item
                for item in assets
                if isinstance(item, dict)
                and _manifest_path_matches(item, normalized)
            ),
            None,
        )

    def _manifest_path_matches(item: dict[str, Any], expected: str) -> bool:
        try:
            candidate = canonical_package_relative_path(
                str(item.get("file") or ""),
                "manifest asset",
                require_assets=True,
            )
        except WorkflowError:
            return False
        return candidate == expected

    def check_release_asset(
        raw_path: str,
        label: str,
        expected_use: str | None = None,
        allow_cover_flag: bool = False,
    ) -> None:
        try:
            normalized = canonical_package_relative_path(
                raw_path, label, require_assets=True
            )
        except WorkflowError as exc:
            blockers.append(str(exc))
            return
        path = (package / normalized).resolve()
        try:
            path.relative_to(package.resolve())
        except ValueError:
            blockers.append(f"{label} path escapes the content package")
            return
        if not path.is_file():
            blockers.append(f"{label} does not exist: {raw_path}")
        elif is_link_or_junction(path) or is_multiply_linked_file(path):
            blockers.append(
                f"{label} must not be a symlink, junction, or hardlink"
            )
        else:
            problem = image_file_problem(path)
            if problem is not None:
                blockers.append(f"{label} is not a valid release image: {problem}")
        entry = asset_entry(normalized)
        if entry is None:
            blockers.append(f"{label} is not registered in asset-manifest.yml")
            return
        rights = str(entry.get("rights_status") or "").strip()
        platforms = entry.get("allowed_platforms") or []
        if rights not in RELEASE_RIGHTS_STATUSES:
            blockers.append(
                f"{label} rights_status is not release-cleared: {rights or 'missing'}"
            )
        if not isinstance(platforms, list) or "wechat" not in platforms:
            blockers.append(f"{label} asset is not allowed for the wechat platform")
        if expected_use is not None and str(entry.get("use") or "") != expected_use:
            if not (allow_cover_flag and entry.get("used_as_cover") is True):
                blockers.append(
                    f"{label} manifest must declare use: {expected_use}"
                    + (" or used_as_cover: true" if allow_cover_flag else "")
                )

    if not config.cover:
        blockers.append("publish.yml has no cover; an explicit rights-cleared cover is required")
    else:
        check_release_asset(
            config.cover,
            "cover",
            "wechat_cover",
            allow_cover_flag=True,
        )

    profile = get_layout_profile(config)
    if profile.required_header and not config.header_image:
        blockers.append(
            f"layout_profile {profile.profile_id} requires a rights-cleared header_image"
        )
    if config.header_image:
        check_release_asset(config.header_image, "header_image", "wechat_body_header")
        if not config.header_alt:
            blockers.append("header_image requires non-empty header_alt")
    if config.footer_image:
        check_release_asset(config.footer_image, "footer_image", "wechat_body_footer")
        if not config.footer_alt:
            blockers.append("footer_image requires non-empty footer_alt")
        if not config.footer_valid_until:
            blockers.append("footer_image requires footer_valid_until as YYYY-MM-DD")
        elif not ISO_DATE_RE.fullmatch(config.footer_valid_until):
            blockers.append("footer_valid_until must be YYYY-MM-DD")
        else:
            try:
                valid_until = date.fromisoformat(config.footer_valid_until)
            except ValueError:
                blockers.append("footer_valid_until must be YYYY-MM-DD")
            else:
                editorial_today = datetime.now(EDITORIAL_TIMEZONE).date()
                if valid_until < editorial_today:
                    blockers.append(
                        f"footer_image review is overdue since {config.footer_valid_until}; reconfirm or remove it"
                    )
                elif valid_until > editorial_today + timedelta(
                    days=MAX_FOOTER_REVIEW_DAYS
                ):
                    blockers.append(
                        f"footer_valid_until exceeds the {MAX_FOOTER_REVIEW_DAYS}-day review window"
                    )
    return blockers


def layout_plan(
    config: PublishConfig, theme_snapshot: Path | None = None
) -> dict[str, Any]:
    profile = get_layout_profile(config)
    custom_theme = profile.custom_theme
    if custom_theme is None:
        theme_path = None
        theme_sha256 = None
    else:
        theme_path = custom_theme.relative_to(WECHAT_ROOT).as_posix()
        theme_sha256 = hashlib.sha256(custom_theme.read_bytes()).hexdigest()
    return {
        "profile": profile.profile_id,
        "custom_theme": theme_path,
        "custom_theme_sha256": theme_sha256,
        "theme_snapshot": theme_snapshot.name if theme_snapshot else None,
        "theme_snapshot_sha256": (
            file_sha256(theme_snapshot) if theme_snapshot else None
        ),
        "header_image": config.header_image or None,
        "footer_image": config.footer_image or None,
        "footer_valid_until": config.footer_valid_until or None,
    }


def capture_build_snapshot(
    package: Path,
    source: Path,
    theme_snapshot: Path | None,
    config: PublishConfig,
    package_files: dict[str, str],
) -> BuildSnapshot:
    profile = get_layout_profile(config)
    canonical_theme_sha256 = (
        file_sha256(profile.custom_theme) if profile.custom_theme else None
    )
    staged_files = build_input_hashes(source.parent)
    return BuildSnapshot(
        package_files=package_files,
        package_sha256=combined_hash(package_files),
        staged_files=staged_files,
        staged_sha256=combined_hash(staged_files),
        source_sha256=file_sha256(source),
        theme_snapshot_sha256=(
            file_sha256(theme_snapshot) if theme_snapshot else None
        ),
        canonical_theme_sha256=canonical_theme_sha256,
    )


def verify_build_snapshot(package: Path, build: PreviewBuild) -> None:
    current_package_files = package_input_hashes(package)
    if current_package_files != build.snapshot.package_files:
        raise WorkflowError(
            "content package changed after preflight; rebuild the preview before creating a draft"
        )
    if file_sha256(build.source) != build.snapshot.source_sha256:
        raise WorkflowError(
            "generated Wenyan source changed after preflight; rebuild before creating a draft"
        )
    current_staged_files = build_input_hashes(build.source.parent)
    if current_staged_files != build.snapshot.staged_files:
        raise WorkflowError(
            "sealed Wenyan build changed after preflight; rebuild before creating a draft"
        )
    if build.theme_snapshot is not None:
        if (
            file_sha256(build.theme_snapshot)
            != build.snapshot.theme_snapshot_sha256
        ):
            raise WorkflowError(
                "staged layout theme changed after preflight; rebuild before creating a draft"
            )
    profile = get_layout_profile(build.config)
    current_theme_sha256 = (
        file_sha256(profile.custom_theme) if profile.custom_theme else None
    )
    if current_theme_sha256 != build.snapshot.canonical_theme_sha256:
        raise WorkflowError(
            "canonical layout theme changed after preflight; rebuild before creating a draft"
        )


def preview_document(
    title: str,
    fragment: str,
    validator_ok: bool,
    report: str,
    blockers: list[str],
) -> str:
    status = "内容包校验通过" if validator_ok else "内容包校验未通过"
    issues = "".join(f"<li>{html.escape(item)}</li>" for item in blockers)
    blocker_box = f"<ul>{issues}</ul>" if issues else "<p>草稿箱门禁无阻塞项。</p>"
    notes = "".join(f"<li>{html.escape(item)}</li>" for item in WENYAN_NOTES)
    nonce = secrets.token_urlsafe(18)
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'nonce-{nonce}'; connect-src 'none'; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} - 公众号本机预览</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#eef1f5;color:#222;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}}
.bar{{position:sticky;top:0;z-index:2;padding:10px 16px;background:#20242a;color:#fff;text-align:center;font-size:13px}}
.gate{{width:min(720px,calc(100% - 24px));margin:16px auto;padding:12px 16px;border:1px solid #e1bb68;border-radius:8px;background:#fff8e8;font-size:13px;line-height:1.6}}
.gate pre{{white-space:pre-wrap;word-break:break-word;color:#666}}.gate ul{{margin:6px 0;padding-left:20px}}
.viewport{{display:flex;justify-content:center;gap:8px;margin:12px auto 0;font-size:13px}}.viewport button{{padding:5px 10px;border:1px solid #c8cdd4;border-radius:6px;background:#fff;color:#333;cursor:pointer}}
.phone{{width:390px;max-width:100%;min-height:100vh;margin:18px auto 40px;padding:28px 0 54px;background:#fff;box-shadow:0 12px 40px rgba(24,31,43,.15)}}
.title{{margin:0 16px 22px;font-size:24px;line-height:1.4;color:#111}}@media(max-width:520px){{.phone{{margin:0 auto;box-shadow:none}}}}
</style></head><body><div class="bar">本机预览 · Wenyan 渲染 · 不会上传</div>
<aside class="gate"><strong>{html.escape(status)}</strong>{blocker_box}<details><summary>查看 Wenyan 版本说明</summary><ul>{notes}</ul></details><details><summary>查看校验输出</summary><pre>{html.escape(report)}</pre></details></aside>
<nav class="viewport" aria-label="预览宽度"><button type="button" data-width="375">375 px</button><button type="button" data-width="390">390 px</button></nav>
<main class="phone" id="phone-preview" data-preview-width="390"><h1 class="title">{html.escape(title)}</h1>{fragment}</main>
<script nonce="{nonce}">(function(){{var phone=document.getElementById('phone-preview');function setWidth(width){{if(width!=='375'&&width!=='390')return;phone.style.width=width+'px';phone.setAttribute('data-preview-width',width);}}document.querySelectorAll('[data-width]').forEach(function(button){{button.addEventListener('click',function(){{setWidth(button.getAttribute('data-width'));}});}});setWidth(new URLSearchParams(window.location.search).get('width'));}})();</script></body></html>"""


def build_preview(package_arg: str | Path) -> PreviewBuild:
    package = Path(package_arg).resolve()
    if not package.is_dir():
        raise WorkflowError(f"content package is not a directory: {package}")
    initial_package_files = package_input_hashes(package)
    build_dir = create_build_dir(package)
    dist = safe_dist(package)
    with sealed_package_snapshot(package, initial_package_files) as sealed_package:
        source, metadata, config, _ = prepare_source(sealed_package, build_dir)
        profile = get_layout_profile(config)
        canonical_theme_before = (
            file_sha256(profile.custom_theme) if profile.custom_theme else None
        )
        theme_snapshot = stage_layout_theme(build_dir, config)
        source_before_render = file_sha256(source)
        theme_snapshot_before_render = (
            file_sha256(theme_snapshot) if theme_snapshot else None
        )
        rendered = run_wenyan_render(source, config, theme_snapshot)
        if file_sha256(source) != source_before_render:
            raise WorkflowError(
                "generated Wenyan source changed while rendering; run the command again"
            )
        if theme_snapshot is not None and (
            file_sha256(theme_snapshot) != theme_snapshot_before_render
        ):
            raise WorkflowError(
                "staged layout theme changed while rendering; run the command again"
            )
        ensure_passive_preview_html(rendered)
        validator_ok, report = validator_report(sealed_package)
        blockers = publication_blockers(sealed_package, metadata, config)
        blockers.extend(
            rendered_image_gate_and_stage(
                sealed_package, build_dir, rendered, config
            )
        )
        blockers = list(dict.fromkeys(blockers))
        rendered_for_preview = inline_preview_images(rendered, build_dir)
    final_package_files = package_input_hashes(package)
    if final_package_files != initial_package_files:
        raise WorkflowError(
            "content package changed while building the preview; run the command again"
        )
    canonical_theme_after = (
        file_sha256(profile.custom_theme) if profile.custom_theme else None
    )
    if canonical_theme_after != canonical_theme_before:
        raise WorkflowError(
            "layout theme changed while building the preview; run the command again"
        )
    if theme_snapshot is not None and (
        file_sha256(theme_snapshot) != canonical_theme_before
    ):
        raise WorkflowError("staged layout theme does not match the canonical theme")
    content_path = dist / "wechat-content.html"
    preview_path = dist / "wechat-preview.html"
    atomic_write_text(content_path, rendered)
    atomic_write_text(
        preview_path,
        preview_document(
            config.title, rendered_for_preview, validator_ok, report, blockers
        ),
    )
    snapshot = capture_build_snapshot(
        package,
        source,
        theme_snapshot,
        config,
        final_package_files,
    )
    if snapshot.source_sha256 != source_before_render:
        raise WorkflowError(
            "generated Wenyan source changed while recording the build; run the command again"
        )
    if snapshot.canonical_theme_sha256 != canonical_theme_before:
        raise WorkflowError(
            "canonical layout theme changed while recording the build; run the command again"
        )
    plan = {
        "renderer": "@wenyan-md/cli@2.0.11",
        "source": source.relative_to(dist).as_posix(),
        "preview": preview_path.name,
        "config": asdict(config),
        "layout": layout_plan(config, theme_snapshot),
        "snapshot": {
            "package_sha256": snapshot.package_sha256,
            "package_file_count": len(snapshot.package_files),
            "staged_sha256": snapshot.staged_sha256,
            "staged_file_count": len(snapshot.staged_files),
            "source_sha256": snapshot.source_sha256,
            "theme_snapshot_sha256": snapshot.theme_snapshot_sha256,
            "canonical_theme_sha256": snapshot.canonical_theme_sha256,
        },
        "content_status": metadata.get("status"),
        "validator_ok": validator_ok,
        "blockers": blockers,
        "known_limitations": WENYAN_NOTES,
        "external_effect": "none; local render only",
    }
    atomic_write_text(
        dist / "publish-plan.json",
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
    )
    print(f"[preview] {preview_path}")
    print(f"[renderer] Wenyan CLI 2.0.11; html_chars={len(rendered)}")
    if report:
        print(report)
    if blockers:
        print("[draft blockers]")
        for item in blockers:
            print(f"- {item}")
    for item in WENYAN_NOTES:
        print(f"[wenyan note] {item}")
    return PreviewBuild(
        preview_path=preview_path,
        source=source,
        theme_snapshot=theme_snapshot,
        metadata=metadata,
        config=config,
        blockers=blockers,
        validator_ok=validator_ok,
        validator_report=report,
        snapshot=snapshot,
    )


def command_preview(args: argparse.Namespace) -> int:
    build = build_preview(args.package)
    if args.open:
        if os.name != "nt":
            raise WorkflowError("--open is currently implemented for Windows only")
        os.startfile(build.preview_path)  # type: ignore[attr-defined]
    return 0


def command_draft(args: argparse.Namespace) -> int:
    package = Path(args.package).resolve()
    build = build_preview(package)
    if not build.validator_ok:
        raise WorkflowError(
            f"content-package validator blocks draft creation:\n{build.validator_report}"
        )
    if build.blockers:
        raise WorkflowError(
            "draft creation is blocked:\n- " + "\n- ".join(build.blockers)
        )
    if not args.execute:
        print(
            "[dry-run pass] preflight passed; no network call or external write was performed; "
            "add --execute to create one draft"
        )
        return 0
    env_path = Path(args.env).resolve() if args.env else WECHAT_ROOT / ".env"
    if not env_path.is_file():
        raise WorkflowError(
            "credential file is missing. Copy 微信公众号/.env.example to 微信公众号/.env and fill it locally; never paste the secret into chat."
        )
    command = wenyan_args(
        "publish", build.source, build.config, build.theme_snapshot
    ) + ["--env-file", str(env_path)]
    with exclusive_publish_lock(package):
        verify_build_snapshot(package, build)
        print("[execute] invoking pinned Wenyan CLI to upload assets and create one WeChat draft")
        result = subprocess.run(
            command,
            cwd=WECHAT_ROOT,
            env=wenyan_environment(),
            check=False,
        )
        if result.returncode != 0:
            raise WorkflowError(f"Wenyan publish failed with exit code {result.returncode}")
        try:
            verify_build_snapshot(package, build)
        except WorkflowError as exc:
            raise WorkflowError(
                "one draft may have been created, but sealed build integrity changed during upload; "
                "inspect and delete the draft before retrying"
            ) from exc
    record = {
        "renderer": "@wenyan-md/cli@2.0.11",
        "title": build.config.title,
        "package_sha256": build.snapshot.package_sha256,
        "source_sha256": build.snapshot.source_sha256,
        "theme_sha256": build.snapshot.theme_snapshot_sha256,
        "external_effect": "created one WeChat draft; did not publish or mass-send",
    }
    dist = safe_dist(package)
    atomic_write_text(
        dist / "wechat-draft-result.json",
        json.dumps(record, ensure_ascii=False, indent=2) + "\n",
    )
    print("[done] one WeChat draft was created; nothing was published or mass-sent")
    return 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preview a content package with Wenyan and optionally create one WeChat draft."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    preview = subparsers.add_parser("preview", help="render a local phone-width preview")
    preview.add_argument("package", help="path to a WeChat content package")
    preview.add_argument("--open", action="store_true", help="open preview in the default browser")
    preview.set_defaults(func=command_preview)
    draft = subparsers.add_parser("draft", help="dry-run by default; --execute creates one draft")
    draft.add_argument("package", help="path to a WeChat content package")
    draft.add_argument("--execute", action="store_true", help="create one WeChat draft through Wenyan")
    draft.add_argument("--env", help="path to a local credential .env file")
    draft.set_defaults(func=command_draft)
    return parser


def main() -> int:
    args = make_parser().parse_args()
    try:
        return int(args.func(args))
    except WorkflowError as exc:
        print(f"[fail] {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"[fail] unexpected error: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
