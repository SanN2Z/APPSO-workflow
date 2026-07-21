# -*- coding: utf-8 -*-
"""Validate a self-media content package without external dependencies."""

from __future__ import annotations

import argparse
import ast
import hashlib
import re
import sys
from datetime import date
from html import unescape
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

from markdown_it import MarkdownIt
from tinycss2 import parse_declaration_list


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
ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
IMAGE_SUFFIXES = {".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}
MARKDOWN_LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
MARKDOWN_AUTOLINK_PATTERN = re.compile(r"<\s*((?:javascript|vbscript)\s*:[^>]*)>", re.I)
WINDOWS_ABSOLUTE_PATTERN = re.compile(r"\b[A-Za-z]:[\\/]")
URL_SCHEME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
FORBIDDEN_HTML_TAGS = {
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
URL_ATTRIBUTES = {
    "action",
    "background",
    "cite",
    "data",
    "formaction",
    "href",
    "poster",
    "src",
    "srcset",
    "xlink:href",
}
UNSUPPORTED_RESOURCE_ATTRIBUTES = {"background", "data-src", "poster", "srcset"}
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
SUPPORTED_MANIFEST_VERSION = 2
MANIFEST_V2_REQUIRED_FIELDS = (
    "file",
    "used_in_draft",
    "source_type",
    "source",
    "creator_or_rightsholder",
    "obtained_on",
    "modifications",
    "rights_status",
    "allowed_platforms",
    "attribution",
)
AI_GENERATED_REQUIRED_FIELDS = (
    "generator",
    "model",
    "generation_mode",
    "prompt_ref",
    "prompt_sha256",
    "generation_constraints",
    "input_assets",
    "generated_on",
)
AI_GENERATION_MODES = {"text_to_image", "referenced_edit", "image_edit"}
REFERENCE_GENERATION_MODES = {"referenced_edit", "image_edit"}
MARKDOWN_PARSER = MarkdownIt("commonmark", {"html": True})
# Parse the same URL shapes that downstream renderers may accept. Safety is
# enforced below by our own scheme and local-image checks, not parser defaults.
MARKDOWN_PARSER.validateLink = lambda _url: True
RELEASE_ASSET_USES = {
    "wechat_body_footer",
    "wechat_body_header",
    "wechat_cover",
    "x_media",
}
NON_RELEASE_ASSET_USES = {"research_reference", "unused"}
GOVERNED_PROMPT_HASHES = {
    "appsso-004": "6ba5e092a4f8d6fb2bd33602424ba4792715aa59f2bf5f916b90d8bb3f0bbd0a",
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
DERIVATIVE_INPUT_RIGHTS_STATUSES = {
    "cc0_verified",
    "licensed_derivative_use",
    "project_owned",
    "project_owned_with_cc0_component",
    "public_domain_verified",
    "user_confirmed_derivative_use",
}
SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{16,}\b"),
    re.compile(
        r"^(?:[A-Z0-9_]*(?:API_KEY|ACCESS_TOKEN|SECRET|BEARER_TOKEN))\s*=\s*(?!replace_|$).+",
        re.MULTILINE,
    ),
)


def parse_manifest_scalar(raw_value: str) -> object:
    """Parse the small, deterministic YAML subset used by asset manifests."""

    value = raw_value.strip()
    if not value:
        return None
    if value.startswith("[") and value.endswith("]"):
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            inner = value[1:-1].strip()
            if not inner:
                return []
            return [item.strip().strip("\"'") for item in inner.split(",")]
        return parsed
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"\"", "'"}:
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value[1:-1]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "~"}:
        return None
    if re.fullmatch(r"\d+", value):
        return int(value)
    return value


def parse_asset_manifest(text: str) -> tuple[int, list[dict[str, object]], list[str]]:
    """Parse manifest version and asset mappings without a third-party YAML runtime."""

    version = 1
    assets: list[dict[str, object]] = []
    issues: list[str] = []
    in_assets = False
    assets_seen = False
    current: dict[str, object] | None = None
    pending_list_key: str | None = None
    pending_list_indent = -1

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if "\t" in raw_line[: len(raw_line) - len(raw_line.lstrip())]:
            issues.append(f"asset-manifest.yml line {line_number} uses tab indentation")
            continue
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))

        if not in_assets:
            if indent == 0 and stripped.startswith("version:"):
                parsed_version = parse_manifest_scalar(stripped.split(":", 1)[1])
                if isinstance(parsed_version, int) and parsed_version >= 1:
                    version = parsed_version
                else:
                    issues.append("asset-manifest.yml version must be a positive integer")
            if indent == 0 and stripped.startswith("assets:"):
                assets_seen = True
                inline_assets = stripped.split(":", 1)[1].strip()
                if inline_assets and inline_assets != "[]":
                    issues.append("asset-manifest.yml assets must be a YAML list")
                in_assets = inline_assets != "[]"
            continue

        if indent == 0:
            in_assets = False
            current = None
            pending_list_key = None
            continue

        if indent == 2 and stripped.startswith("-"):
            item = stripped[1:].strip()
            if ":" not in item:
                issues.append(
                    f"asset-manifest.yml line {line_number} must start an asset mapping"
                )
                current = None
                continue
            key, raw_value = item.split(":", 1)
            current = {key.strip(): parse_manifest_scalar(raw_value)}
            assets.append(current)
            pending_list_key = key.strip() if not raw_value.strip() else None
            pending_list_indent = indent
            continue

        if current is None:
            issues.append(f"asset-manifest.yml line {line_number} is outside an asset mapping")
            continue

        if stripped.startswith("-") and pending_list_key and indent > pending_list_indent:
            value = parse_manifest_scalar(stripped[1:])
            existing = current.get(pending_list_key)
            if existing is None:
                current[pending_list_key] = []
                existing = current[pending_list_key]
            if isinstance(existing, list):
                existing.append(value)
            else:
                issues.append(
                    f"asset-manifest.yml line {line_number} cannot append to {pending_list_key}"
                )
            continue

        if ":" not in stripped:
            issues.append(f"invalid asset-manifest.yml line {line_number}: {stripped}")
            continue
        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        if key in current:
            issues.append(
                f"asset-manifest.yml line {line_number} duplicates field {key}"
            )
        current[key] = parse_manifest_scalar(raw_value)
        pending_list_key = key if not raw_value.strip() else None
        pending_list_indent = indent

    if not assets_seen:
        issues.append("asset-manifest.yml must contain an assets list")
    return version, assets, issues


def is_iso_date(value: object) -> bool:
    if not isinstance(value, str) or not ISO_DATE_PATTERN.fullmatch(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def is_missing_value(value: object) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def canonical_package_key(package: Path, raw_path: str) -> str | None:
    """Return a case-folded package-relative key after resolving path aliases."""

    value = raw_path.strip().replace("\\", "/")
    path_parts = PurePosixPath(value).parts
    if (
        not value
        or value.startswith("/")
        or WINDOWS_ABSOLUTE_PATTERN.search(value)
        or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value)
        or any(part in {"", ".", ".."} or ":" in part for part in path_parts)
    ):
        return None
    try:
        resolved = (package / value).resolve()
    except OSError:
        return None
    if not resolved.is_relative_to(package):
        return None
    return resolved.relative_to(package).as_posix().casefold()


def validate_manifest_assets(
    package: Path,
    assets: list[dict[str, object]],
    version: int,
    status: str,
    platform: str,
    draft_image_targets: set[str],
) -> tuple[list[str], list[str]]:
    """Validate v2 manifests strictly while keeping legacy manifests readable."""

    errors: list[str] = []
    warnings: list[str] = []
    strict = version >= 2
    assets_by_file: dict[str, dict[str, object]] = {}

    for asset in assets:
        raw_file = asset.get("file")
        if not isinstance(raw_file, str) or not raw_file.strip():
            continue
        file_key = canonical_package_key(package, raw_file)
        if file_key is None:
            continue
        if file_key in assets_by_file:
            errors.append(f"duplicate manifest file target: {raw_file.strip()}")
        else:
            assets_by_file[file_key] = asset

    input_graph: dict[str, list[str]] = {}
    for file_key, asset in assets_by_file.items():
        input_assets = asset.get("input_assets")
        if not isinstance(input_assets, list):
            continue
        input_graph[file_key] = [
            input_key
            for value in input_assets
            if isinstance(value, str)
            and (input_key := canonical_package_key(package, value)) in assets_by_file
        ]

    visit_state: dict[str, int] = {}
    visit_stack: list[str] = []
    reported_cycles: set[tuple[str, ...]] = set()

    def visit_input_graph(node: str) -> None:
        visit_state[node] = 1
        visit_stack.append(node)
        for child in input_graph.get(node, []):
            child_state = visit_state.get(child, 0)
            if child_state == 0:
                visit_input_graph(child)
            elif child_state == 1:
                cycle_start = visit_stack.index(child)
                cycle = tuple(visit_stack[cycle_start:] + [child])
                if cycle not in reported_cycles:
                    reported_cycles.add(cycle)
                    errors.append(
                        f"asset input dependency cycle: {' -> '.join(cycle)}"
                    )
        visit_stack.pop()
        visit_state[node] = 2

    for node in input_graph:
        if visit_state.get(node, 0) == 0:
            visit_input_graph(node)

    def add_contract_issue(message: str, release_bound: bool) -> None:
        if strict and release_bound and status in {"ready", "published"}:
            errors.append(message)
        else:
            warnings.append(message)

    for index, asset in enumerate(assets, start=1):
        raw_file = asset.get("file")
        file_value = raw_file.strip() if isinstance(raw_file, str) else ""
        label = file_value or f"asset #{index}"
        used_in_draft = asset.get("used_in_draft")
        declared_use = asset.get("use")
        used_as_cover = asset.get("used_as_cover")
        file_key = canonical_package_key(package, file_value) if file_value else None
        if file_value and file_key is None:
            errors.append(
                f"manifest path must be package-relative and contain no unsafe path segments: {file_value}"
            )
        referenced_in_draft = file_key in draft_image_targets if file_key else False
        release_bound = (
            referenced_in_draft
            or used_in_draft is True
            or used_as_cover is True
            or (
                isinstance(declared_use, str)
                and declared_use in RELEASE_ASSET_USES
            )
        )
        binding_unknown = is_missing_value(used_in_draft)

        if strict and not is_missing_value(declared_use) and (
            not isinstance(declared_use, str)
            or declared_use not in RELEASE_ASSET_USES | NON_RELEASE_ASSET_USES
        ):
            add_contract_issue(
                f"manifest {label} use must be one of: "
                f"{', '.join(sorted(RELEASE_ASSET_USES | NON_RELEASE_ASSET_USES))}",
                True,
            )
        if strict and not is_missing_value(used_as_cover) and not isinstance(
            used_as_cover, bool
        ):
            add_contract_issue(
                f"manifest {label} used_as_cover must be true or false",
                True,
            )

        if strict:
            missing = [
                field
                for field in MANIFEST_V2_REQUIRED_FIELDS
                if field != "file" and is_missing_value(asset.get(field))
            ]
            if missing:
                add_contract_issue(
                    f"manifest {label} missing required field(s): {', '.join(missing)}",
                    release_bound or binding_unknown,
                )
            if not file_value:
                errors.append(f"manifest asset #{index} missing required field: file")
            for field in (
                "source_type",
                "source",
                "creator_or_rightsholder",
                "modifications",
                "rights_status",
                "attribution",
            ):
                value = asset.get(field)
                if not is_missing_value(value) and not isinstance(value, str):
                    add_contract_issue(
                        f"manifest {label} {field} must be a string",
                        release_bound,
                    )

        if strict and not isinstance(used_in_draft, bool):
            add_contract_issue(
                f"manifest {label} used_in_draft must be true or false",
                True,
            )
        if referenced_in_draft and used_in_draft is not True:
            add_contract_issue(
                f"manifest {label} is referenced by draft.md but used_in_draft is not true",
                True,
            )

        allowed_platforms = asset.get("allowed_platforms")
        if strict and not isinstance(allowed_platforms, list):
            add_contract_issue(
                f"manifest {label} allowed_platforms must be a list",
                release_bound,
            )
        if isinstance(allowed_platforms, list) and not all(
            isinstance(value, str) and value.strip() for value in allowed_platforms
        ):
            add_contract_issue(
                f"manifest {label} allowed_platforms must contain non-empty strings",
                release_bound,
            )
        if release_bound and isinstance(allowed_platforms, list) and platform:
            if platform not in allowed_platforms:
                add_contract_issue(
                    f"manifest {label} is release-bound but does not allow platform {platform}",
                    True,
                )

        if strict and not is_iso_date(asset.get("obtained_on")):
            add_contract_issue(
                f"manifest {label} obtained_on must be an ISO date (YYYY-MM-DD)",
                release_bound,
            )

        rights_status = asset.get("rights_status")
        if strict and release_bound and (
            not isinstance(rights_status, str)
            or rights_status not in RELEASE_RIGHTS_STATUSES
        ):
            add_contract_issue(
                f"manifest {label} rights_status is not release-cleared: {rights_status}",
                True,
            )

        if asset.get("source_type") != "ai_generated":
            continue

        missing_ai = [
            field
            for field in AI_GENERATED_REQUIRED_FIELDS
            if is_missing_value(asset.get(field))
        ]
        if missing_ai:
            message = f"manifest {label} missing AI generation field(s): {', '.join(missing_ai)}"
            if strict:
                add_contract_issue(message, release_bound)
            else:
                warnings.append(f"legacy {message}; migrate manifest to version 2 when edited")

        generation_mode = asset.get("generation_mode")
        if not is_missing_value(generation_mode) and (
            not isinstance(generation_mode, str) or generation_mode not in AI_GENERATION_MODES
        ):
            add_contract_issue(
                f"manifest {label} generation_mode must be one of: {', '.join(sorted(AI_GENERATION_MODES))}",
                release_bound,
            )

        for field in (
            "generator",
            "model",
            "prompt_ref",
            "generation_constraints",
        ):
            value = asset.get(field)
            if not is_missing_value(value) and not isinstance(value, str):
                add_contract_issue(
                    f"manifest {label} {field} must be a string",
                    release_bound,
                )

        prompt_sha256 = asset.get("prompt_sha256")
        if not is_missing_value(prompt_sha256) and (
            not isinstance(prompt_sha256, str) or not SHA256_PATTERN.fullmatch(prompt_sha256)
        ):
            add_contract_issue(
                f"manifest {label} prompt_sha256 must be 64 lowercase hexadecimal characters",
                release_bound,
            )

        prompt_ref = asset.get("prompt_ref")
        governed_hash = GOVERNED_PROMPT_HASHES.get(prompt_ref) if isinstance(prompt_ref, str) else None
        if governed_hash and prompt_sha256 != governed_hash:
            add_contract_issue(
                f"manifest {label} prompt_sha256 does not match governed prompt {prompt_ref}",
                release_bound,
            )

        input_assets = asset.get("input_assets")
        if not is_missing_value(input_assets) and not isinstance(input_assets, list):
            add_contract_issue(
                f"manifest {label} input_assets must be a list",
                release_bound,
            )
        requires_input = (
            isinstance(generation_mode, str)
            and generation_mode in REFERENCE_GENERATION_MODES
        ) or prompt_ref == "appsso-004"
        if isinstance(input_assets, list):
            if requires_input and not input_assets:
                add_contract_issue(
                    f"manifest {label} referenced generation requires input_assets",
                    release_bound,
                )
            for input_asset in input_assets:
                if not isinstance(input_asset, str) or not input_asset.strip():
                    add_contract_issue(
                        f"manifest {label} input_assets must contain non-empty strings",
                        release_bound,
                    )
                    continue
                normalized_input = input_asset.strip().replace("\\", "/")
                if normalized_input.startswith(("conversation:", "user_attachment:")):
                    add_contract_issue(
                        f"manifest {label} input asset must be persisted and registered before release: {normalized_input}",
                        release_bound,
                    )
                    continue
                input_key = canonical_package_key(package, normalized_input)
                if input_key is not None and input_key == file_key:
                    add_contract_issue(
                        f"manifest {label} cannot use itself as an input asset",
                        release_bound,
                    )
                    continue
                input_record = assets_by_file.get(input_key) if input_key else None
                if input_record is None:
                    add_contract_issue(
                        f"manifest {label} input asset lacks its own rights record: {normalized_input}",
                        release_bound,
                    )
                    continue
                input_rights = input_record.get("rights_status")
                if (
                    not isinstance(input_rights, str)
                    or input_rights not in DERIVATIVE_INPUT_RIGHTS_STATUSES
                ):
                    add_contract_issue(
                        f"manifest {label} input asset is not cleared for derivative use: "
                        f"{normalized_input} ({input_rights})",
                        release_bound,
                    )

        generated_on = asset.get("generated_on")
        if not is_missing_value(generated_on) and not is_iso_date(generated_on):
            add_contract_issue(
                f"manifest {label} generated_on must be an ISO date (YYYY-MM-DD)",
                release_bound,
            )

    return errors, warnings


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
    """Return the destination portion of a Markdown link or image target."""

    value = unescape(target.strip())
    if value.startswith("<"):
        closing = value.find(">", 1)
        value = value[1:closing] if closing >= 0 else value[1:]
    else:
        value = value.split(None, 1)[0] if value else ""
    return normalize_html_target(value)


def normalize_html_target(target: str) -> str:
    """Normalize an HTML URL attribute without treating encoded # as a fragment."""

    value = unescape(target.strip()).split("#", 1)[0]
    return unquote(value)


def compact_url_for_scheme_check(value: str) -> str:
    decoded = unquote(unescape(value))
    return re.sub(r"[\x00-\x20]+", "", decoded).casefold()


def has_dangerous_url_scheme(value: str) -> bool:
    compact = compact_url_for_scheme_check(value)
    return compact.startswith(("javascript:", "vbscript:"))


def has_forbidden_navigation_scheme(value: str) -> bool:
    compact = compact_url_for_scheme_check(value)
    match = re.match(r"^([a-z][a-z0-9+.-]*):", compact)
    return bool(match and match.group(1) not in ALLOWED_NAVIGATION_SCHEMES)


def css_tokens_have_resource(tokens: list[object]) -> bool:
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
        unescape(unquote(style)), skip_comments=True, skip_whitespace=True
    )
    for declaration in declarations:
        if getattr(declaration, "type", "") == "error":
            return True
        if css_tokens_have_resource(list(getattr(declaration, "value", []))):
            return True
    return False


class DraftHTMLInspector(HTMLParser):
    """Collect raw HTML images and reject active HTML that is unsafe to preview."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.image_targets: list[str] = []
        self.issues: list[str] = []

    @staticmethod
    def local_name(name: str) -> str:
        return name.casefold().rsplit(":", 1)[-1]

    def inspect_tag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized_tag = self.local_name(tag)
        if normalized_tag in FORBIDDEN_HTML_TAGS:
            self.issues.append(f"draft.md contains forbidden HTML tag <{normalized_tag}>")

        attribute_map: dict[str, str] = {}
        for raw_name, raw_value in attrs:
            name = raw_name.casefold()
            value = raw_value or ""
            if name in attribute_map:
                self.issues.append(
                    f"draft.md contains duplicate HTML attribute {name}"
                )
            else:
                attribute_map[name] = value
            if name.startswith("on"):
                self.issues.append(
                    f"draft.md contains forbidden HTML event attribute {name}"
                )
            if name in UNSUPPORTED_RESOURCE_ATTRIBUTES:
                self.issues.append(
                    f"draft.md contains unsupported HTML resource attribute {name}"
                )
            if name == "src" and normalized_tag != "img":
                self.issues.append(
                    f"draft.md contains unsupported HTML src on <{normalized_tag}>"
                )
            if name in URL_ATTRIBUTES:
                candidates = value.split(",") if name == "srcset" else [value]
                for candidate in candidates:
                    destination = candidate.strip()
                    if name == "srcset" and destination:
                        destination = destination.split(None, 1)[0]
                    if destination and has_forbidden_navigation_scheme(destination):
                        self.issues.append(
                            f"draft.md contains forbidden URL scheme in HTML attribute {name}"
                        )
                        break
            if name == "style" and style_has_resource_reference(value):
                self.issues.append(
                    "draft.md contains a resource reference in an HTML style attribute"
                )

        if normalized_tag == "img":
            source = attribute_map.get("src", "").strip()
            if source:
                self.image_targets.append(normalize_html_target(source))
            else:
                self.issues.append("draft.md contains an HTML img without a non-empty src")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.inspect_tag(tag, attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.inspect_tag(tag, attrs)


def inspect_draft_body(body: str) -> tuple[list[tuple[str, str]], list[str]]:
    """Return semantic Markdown/HTML images and active-content issues."""

    references: list[tuple[str, str]] = []
    issues: list[str] = []
    tokens = MARKDOWN_PARSER.parse(body)
    stack = list(reversed(tokens))
    while stack:
        token = stack.pop()
        if token.children:
            stack.extend(reversed(token.children))
        if token.type == "image":
            source = token.attrGet("src") or ""
            references.append(("Markdown", normalize_html_target(source)))
        elif token.type == "link_open":
            destination = token.attrGet("href") or ""
            if destination and has_forbidden_navigation_scheme(destination):
                issues.append(
                    "draft.md contains forbidden Markdown URL scheme"
                )
        elif token.type == "text":
            text_targets = MARKDOWN_LINK_PATTERN.findall(token.content)
            if any(
                has_forbidden_navigation_scheme(normalize_markdown_target(target))
                for target in text_targets
            ) or MARKDOWN_AUTOLINK_PATTERN.search(token.content):
                issues.append(
                    "draft.md contains forbidden Markdown URL scheme"
                )
        elif token.type in {"html_block", "html_inline"}:
            inspector = DraftHTMLInspector()
            inspector.feed(token.content)
            inspector.close()
            issues.extend(inspector.issues)
            references.extend(
                ("HTML", target) for target in inspector.image_targets
            )
            # CommonMark may keep a Markdown-looking line in the same HTML block.
            # Scan that token conservatively so a blocked URL scheme cannot disappear
            # merely because it follows block HTML without a blank-line boundary.
            text_targets = MARKDOWN_LINK_PATTERN.findall(token.content)
            if any(
                has_forbidden_navigation_scheme(normalize_markdown_target(target))
                for target in text_targets
            ) or MARKDOWN_AUTOLINK_PATTERN.search(token.content):
                issues.append(
                    "draft.md contains forbidden Markdown URL scheme"
                )

    return references, list(dict.fromkeys(issues))


def has_external_image_scheme(target: str) -> bool:
    value = target.strip()
    if value.startswith("//"):
        return True
    return URL_SCHEME_PATTERN.match(value) is not None


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
    manifest_version, manifest_assets, manifest_parse_issues = parse_asset_manifest(manifest)
    errors.extend(manifest_parse_issues)
    if manifest_version > SUPPORTED_MANIFEST_VERSION:
        errors.append(
            f"unsupported asset-manifest.yml version: {manifest_version}; "
            f"maximum supported version is {SUPPORTED_MANIFEST_VERSION}"
        )

    draft_body = ""
    try:
        metadata, draft_body = split_frontmatter(draft, "draft.md")
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

    manifest_files = {
        value.strip().replace("\\", "/")
        for asset in manifest_assets
        if isinstance((value := asset.get("file")), str) and value
    }
    manifest_file_keys = {
        key
        for value in manifest_files
        if (key := canonical_package_key(package, value)) is not None
    }
    image_references, html_issues = inspect_draft_body(draft_body)
    errors.extend(html_issues)
    draft_image_targets: set[str] = set()
    local_image_references: list[tuple[str, str, str]] = []
    image_count = 0
    for origin, target in image_references:
        if not target:
            errors.append(f"{origin} image target is empty")
            continue
        if WINDOWS_ABSOLUTE_PATTERN.search(target) or (
            target.startswith(("/", "\\")) and not target.startswith("//")
        ):
            errors.append(f"{origin} image path must be package-relative: {target}")
            continue
        if has_forbidden_navigation_scheme(target):
            errors.append(f"{origin} image contains a forbidden URL scheme: {target}")
            continue
        if target.startswith("//") or has_external_image_scheme(target):
            message = f"{origin} image is not packaged locally: {target}"
            if status in {"ready", "published"}:
                errors.append(message)
            else:
                warnings.append(message)
            continue
        image_count += 1
        target_key = canonical_package_key(package, target)
        if target_key is None:
            errors.append(f"{origin} image path escapes package: {target}")
            continue
        draft_image_targets.add(target_key)
        local_image_references.append((origin, target, target_key))
    manifest_errors, manifest_warnings = validate_manifest_assets(
        package,
        manifest_assets,
        manifest_version,
        status,
        platform,
        draft_image_targets,
    )
    errors.extend(manifest_errors)
    warnings.extend(manifest_warnings)
    for origin, target, target_key in local_image_references:
        resolved = (package / target).resolve()
        if not resolved.is_file():
            errors.append(f"missing {origin} image: {target}")
        if target_key not in manifest_file_keys:
            errors.append(
                f"{origin} image is not registered in asset-manifest.yml: {target}"
            )

    for value in manifest_files:
        if canonical_package_key(package, value) is None:
            continue
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
