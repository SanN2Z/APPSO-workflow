# -*- coding: utf-8 -*-
"""Validate a self-media content package without external dependencies."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
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
JUDGMENT_WORKSHOP_POINTER = "research/judgment-workshop.md"
JUDGMENT_WORKSHOP_STATUSES = {"discussing", "locked", "not_required"}
JUDGMENT_WORKSHOP_GATED_STATES = {
    "draft",
    "fact_checked",
    "editorial_review",
    "ready",
    "published",
}
JUDGMENT_WORKSHOP_VOICE_MODES = {"personal", "company"}
JUDGMENT_WORKSHOP_LOCKED_SECTIONS = (
    "共同处境",
    "主判断",
    "支撑判断",
    "放弃的方向",
    "读者带走什么",
)
JUDGMENT_WORKSHOP_PLACEHOLDERS = {
    "待讨论",
    "待锁定",
    "待记录",
    "（待讨论）",
    "（待锁定）",
    "（待记录）",
}
AI_PATTERN_DIAGNOSTIC_TITLES = {
    "ai-pattern diagnostic",
    "ai 痕迹诊断",
}
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
PROJECT_ADAPTERS = {"appsso", "generic"}
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


def normalize_generation_input_key(package: Path, raw_value: object) -> str | None:
    """Normalize manifest/receipt inputs without losing conversation bindings."""

    if not isinstance(raw_value, str) or not raw_value.strip():
        return None
    value = raw_value.strip().replace("\\", "/")
    if value.startswith(("conversation:", "user_attachment:")):
        prefix, identifier = value.split(":", 1)
        if not identifier.strip():
            return None
        return f"{prefix}:{identifier.strip()}"
    return canonical_package_key(package, value)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_workspace_root(package: Path) -> Path | None:
    for candidate in (package.resolve(), *package.resolve().parents):
        if (
            (candidate / "AGENTS.md").is_file()
            and (candidate / "上下文").is_dir()
            and (candidate / "共享").is_dir()
        ):
            return candidate
    return None


def read_publish_project_adapter(package: Path) -> tuple[str | None, str | None]:
    publish_path = package / "publish.yml"
    if not publish_path.is_file():
        return None, None
    values: list[object] = []
    try:
        lines = publish_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return None, f"cannot read publish.yml project_adapter: {exc}"
    for line in lines:
        if not line or line[0].isspace() or line.lstrip().startswith("#"):
            continue
        key, separator, raw_value = line.partition(":")
        if separator and key.strip() == "project_adapter":
            if " #" in raw_value:
                raw_value = raw_value.split(" #", 1)[0].rstrip()
            values.append(parse_manifest_scalar(raw_value))
    if len(values) > 1:
        return None, "publish.yml declares project_adapter more than once"
    if not values:
        return None, None
    value = values[0]
    if not isinstance(value, str) or not value.strip():
        return None, "publish.yml project_adapter must be a non-empty string"
    normalized = value.strip()
    if normalized not in PROJECT_ADAPTERS:
        return (
            normalized,
            "publish.yml project_adapter must be one of: "
            + ", ".join(sorted(PROJECT_ADAPTERS)),
        )
    return normalized, None


def _reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    parsed: dict[str, object] = {}
    for key, value in pairs:
        if key in parsed:
            raise ValueError(f"duplicate JSON key: {key}")
        parsed[key] = value
    return parsed


def _reject_json_constant(value: str) -> object:
    raise ValueError(f"non-standard JSON constant: {value}")


def _contains_json_key(value: object, forbidden_key: str) -> bool:
    pending = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            if forbidden_key in current:
                return True
            pending.extend(current.values())
        elif isinstance(current, list):
            pending.extend(current)
    return False


def load_strict_json_object(path: Path, label: str) -> tuple[dict[str, object] | None, str | None]:
    try:
        loaded = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_json_keys,
            parse_constant=_reject_json_constant,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, RecursionError) as exc:
        return None, f"{label} is not valid strict JSON: {exc}"
    if not isinstance(loaded, dict):
        return None, f"{label} root must be an object"
    return loaded, None


def resolve_json_file(
    root: Path,
    raw_value: object,
    label: str,
) -> tuple[str | None, Path | None, str | None]:
    if not isinstance(raw_value, str) or not raw_value.strip():
        return None, None, f"{label} must be a non-empty relative path"
    normalized = raw_value.strip().replace("\\", "/")
    if not normalized.endswith(".json") or canonical_package_key(root, normalized) is None:
        return None, None, f"{label} must be a root-relative package-local JSON file"
    declared = root / normalized
    if declared.is_symlink():
        return None, None, f"{label} must not be a symlink: {normalized}"
    resolved = declared.resolve()
    if not resolved.is_file():
        return None, None, f"{label} file does not exist: {normalized}"
    return normalized, resolved, None


def validate_ai_preflight_receipt(
    package: Path,
    asset: dict[str, object],
    label: str,
    file_key: str | None,
    assets_by_file: dict[str, dict[str, object]],
    release_bound: bool,
    platform: str,
    publish_project_adapter: str | None,
    publish_adapter_issue: str | None,
) -> list[str]:
    """Bind an AI manifest record to the complete persisted preflight contract."""

    issues: list[str] = []
    invocation_hash = asset.get("invocation_prompt_sha256")
    if is_missing_value(invocation_hash):
        issues.append(
            f"manifest {label} missing AI preflight field: invocation_prompt_sha256"
        )
    elif not isinstance(invocation_hash, str) or not SHA256_PATTERN.fullmatch(
        invocation_hash
    ):
        issues.append(
            f"manifest {label} invocation_prompt_sha256 must be 64 lowercase hexadecimal characters"
        )

    raw_receipt = asset.get("preflight_receipt")
    if is_missing_value(raw_receipt):
        issues.append(f"manifest {label} missing AI preflight field: preflight_receipt")
        return issues
    if not isinstance(raw_receipt, str):
        issues.append(f"manifest {label} preflight_receipt must be a string")
        return issues

    normalized_receipt = raw_receipt.strip().replace("\\", "/")
    receipt_parts = PurePosixPath(normalized_receipt).parts
    if (
        len(receipt_parts) != 3
        or receipt_parts[0].casefold() != "research"
        or receipt_parts[1].casefold() != "image-generation-runs"
        or not receipt_parts[2].endswith(".json")
        or receipt_parts[2] == ".json"
        or canonical_package_key(package, normalized_receipt) is None
    ):
        issues.append(
            f"manifest {label} preflight_receipt must be a package-local JSON file "
            "directly under research/image-generation-runs/"
        )
        return issues

    declared_receipt_path = package / normalized_receipt
    if declared_receipt_path.is_symlink():
        issues.append(
            f"manifest {label} preflight_receipt must not be a symlink: {normalized_receipt}"
        )
        return issues
    receipt_path = declared_receipt_path.resolve()
    if not receipt_path.is_file():
        issues.append(
            f"manifest {label} preflight_receipt file does not exist: {normalized_receipt}"
        )
        return issues
    receipt, receipt_error = load_strict_json_object(
        receipt_path,
        f"preflight_receipt {normalized_receipt}",
    )
    if receipt_error:
        issues.append(f"manifest {label} {receipt_error}")
        return issues
    assert receipt is not None
    if _contains_json_key(receipt, "prompt_payload"):
        issues.append(
            f"manifest {label} preflight_receipt must not contain prompt_payload: "
            f"{normalized_receipt}"
        )
    if _contains_json_key(receipt, "tool_request"):
        issues.append(
            f"manifest {label} preflight_receipt must not contain tool_request: "
            f"{normalized_receipt}"
        )

    prompt_ref = asset.get("prompt_ref")
    expected_values: dict[str, object] = {
        "status": "pass",
        "style_profile": prompt_ref,
        "prompt_ref": prompt_ref,
        "prompt_sha256": asset.get("prompt_sha256"),
        "invocation_prompt_sha256": invocation_hash,
        "mode": asset.get("generation_mode"),
    }
    for field, expected in expected_values.items():
        if receipt.get(field) != expected:
            issues.append(
                f"manifest {label} preflight_receipt {field} does not match "
                f"the required manifest value: {normalized_receipt}"
            )

    if receipt.get("schema_version") != 1:
        issues.append(
            f"manifest {label} preflight_receipt schema_version must be 1: "
            f"{normalized_receipt}"
        )
    if not is_iso_date(receipt.get("checked_on")):
        issues.append(
            f"manifest {label} preflight_receipt checked_on must be an ISO date: "
            f"{normalized_receipt}"
        )
    for field in (
        "task_id",
        "project_adapter",
        "visual_type",
        "style_profile",
        "style_scope",
        "new_image_strategy",
        "reference_strategy",
        "mode",
        "input_binding",
        "prompt_ref",
        "output",
        "plan",
        "profile_registry",
        "receipt",
    ):
        if not isinstance(receipt.get(field), str) or not str(receipt.get(field)).strip():
            issues.append(
                f"manifest {label} preflight_receipt {field} must be a non-empty string: "
                f"{normalized_receipt}"
            )
    for field in (
        "plan_sha256",
        "profile_registry_sha256",
        "constraints_sha256",
    ):
        value = receipt.get(field)
        if not isinstance(value, str) or not SHA256_PATTERN.fullmatch(value):
            issues.append(
                f"manifest {label} preflight_receipt {field} must be 64 lowercase "
                f"hexadecimal characters: {normalized_receipt}"
            )
    if receipt.get("style_scope") not in {
        "task",
        "all_ai_generated_editorial_images",
    }:
        issues.append(
            f"manifest {label} preflight_receipt style_scope is unsupported: "
            f"{normalized_receipt}"
        )
    if receipt.get("new_image_strategy") not in {
        "direct",
        "reference_required",
        "two_stage_reference_then_redraw",
    }:
        issues.append(
            f"manifest {label} preflight_receipt new_image_strategy is unsupported: "
            f"{normalized_receipt}"
        )
    if receipt.get("reference_strategy") not in {
        "none",
        "generated_base",
        "provided_local",
        "conversation_attachment",
    }:
        issues.append(
            f"manifest {label} preflight_receipt reference_strategy is unsupported: "
            f"{normalized_receipt}"
        )
    if receipt.get("input_binding") not in {
        "none",
        "referenced_image_paths",
        "num_last_images_to_include",
    }:
        issues.append(
            f"manifest {label} preflight_receipt input_binding is unsupported: "
            f"{normalized_receipt}"
        )
    if not isinstance(receipt.get("present_to_user"), bool):
        issues.append(
            f"manifest {label} preflight_receipt present_to_user must be boolean: "
            f"{normalized_receipt}"
        )
    stage = receipt.get("stage")
    if release_bound and stage != "final":
        issues.append(
            f"manifest {label} release-bound AI asset requires a final-stage "
            f"preflight_receipt: {normalized_receipt}"
        )
    elif not release_bound and stage not in {"reference", "final"}:
        issues.append(
            f"manifest {label} research AI asset receipt stage must be reference or final: "
            f"{normalized_receipt}"
        )
    if stage == "final" and receipt.get("present_to_user") is not True:
        issues.append(
            f"manifest {label} final-stage preflight_receipt requires "
            f"present_to_user=true: {normalized_receipt}"
        )
    if stage == "reference" and receipt.get("present_to_user") is not False:
        issues.append(
            f"manifest {label} reference-stage preflight_receipt requires "
            f"present_to_user=false: {normalized_receipt}"
        )

    for optional_string in ("style_override_source", "prompt_source"):
        value = receipt.get(optional_string)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            issues.append(
                f"manifest {label} preflight_receipt {optional_string} must be null or "
                f"a non-empty string: {normalized_receipt}"
            )
    if not isinstance(receipt.get("conversation_derivative_rights_confirmed"), bool):
        issues.append(
            f"manifest {label} preflight_receipt "
            f"conversation_derivative_rights_confirmed must be boolean: {normalized_receipt}"
        )
    image_count = receipt.get("num_last_images_to_include")
    if receipt.get("input_binding") == "num_last_images_to_include":
        if (
            not isinstance(image_count, int)
            or isinstance(image_count, bool)
            or not 1 <= image_count <= 5
        ):
            issues.append(
                f"manifest {label} preflight_receipt num_last_images_to_include must be "
                f"between 1 and 5: {normalized_receipt}"
            )
    elif image_count is not None:
        issues.append(
            f"manifest {label} preflight_receipt num_last_images_to_include must be null "
            f"for {receipt.get('input_binding')}: {normalized_receipt}"
        )

    receipt_self = receipt.get("receipt")
    if (
        not isinstance(receipt_self, str)
        or canonical_package_key(package, receipt_self) != canonical_package_key(
            package, normalized_receipt
        )
    ):
        issues.append(
            f"manifest {label} preflight_receipt receipt field does not identify itself: "
            f"{normalized_receipt}"
        )

    receipt_adapter = receipt.get("project_adapter")
    if receipt_adapter not in PROJECT_ADAPTERS:
        issues.append(
            f"manifest {label} preflight_receipt project_adapter is unsupported: "
            f"{normalized_receipt}"
        )
    if publish_adapter_issue:
        issues.append(f"manifest {label} {publish_adapter_issue}")
    if publish_project_adapter is not None and receipt_adapter != publish_project_adapter:
        issues.append(
            f"manifest {label} preflight_receipt project_adapter does not match "
            f"publish.yml: {normalized_receipt}"
        )
    if platform == "wechat" and release_bound and publish_project_adapter is None:
        issues.append(
            f"manifest {label} WeChat release AI asset requires an independent "
            "publish.yml project_adapter declaration"
        )

    receipt_output = receipt.get("output")
    receipt_output_key = (
        canonical_package_key(package, receipt_output)
        if isinstance(receipt_output, str)
        else None
    )
    if receipt_output_key is None or receipt_output_key != file_key:
        issues.append(
            f"manifest {label} preflight_receipt output does not match the asset path: "
            f"{normalized_receipt}"
        )

    manifest_inputs = asset.get("input_assets")
    receipt_inputs = receipt.get("input_assets")
    normalized_manifest_inputs: list[str | None] = []
    normalized_receipt_inputs: list[str | None] = []
    if not isinstance(receipt_inputs, list):
        issues.append(
            f"manifest {label} preflight_receipt input_assets must be a list: "
            f"{normalized_receipt}"
        )
    elif not isinstance(manifest_inputs, list):
        issues.append(
            f"manifest {label} preflight_receipt input_assets cannot match a non-list "
            f"manifest value: {normalized_receipt}"
        )
    else:
        normalized_manifest_inputs = [
            normalize_generation_input_key(package, value) for value in manifest_inputs
        ]
        normalized_receipt_inputs = [
            normalize_generation_input_key(package, value) for value in receipt_inputs
        ]
        if (
            any(value is None for value in normalized_manifest_inputs)
            or any(value is None for value in normalized_receipt_inputs)
            or normalized_receipt_inputs != normalized_manifest_inputs
        ):
            issues.append(
                f"manifest {label} preflight_receipt input_assets do not match the "
                f"manifest after path normalization: {normalized_receipt}"
            )

    fingerprints = receipt.get("input_fingerprints")
    if not isinstance(fingerprints, list):
        issues.append(
            f"manifest {label} preflight_receipt input_fingerprints must be a list: "
            f"{normalized_receipt}"
        )
        fingerprints = []
    local_inputs: list[tuple[str, str, Path, dict[str, object] | None]] = []
    if isinstance(manifest_inputs, list):
        for raw_input, input_key in zip(manifest_inputs, normalized_manifest_inputs):
            if (
                not isinstance(raw_input, str)
                or raw_input.strip().startswith(("conversation:", "user_attachment:"))
                or input_key is None
            ):
                continue
            normalized_input = raw_input.strip().replace("\\", "/")
            local_inputs.append(
                (
                    normalized_input,
                    input_key,
                    (package / normalized_input).resolve(),
                    assets_by_file.get(input_key),
                )
            )
    if len(fingerprints) != len(local_inputs):
        issues.append(
            f"manifest {label} preflight_receipt input_fingerprints count does not "
            f"match local input_assets: {normalized_receipt}"
        )
    for index, (input_path_value, input_key, input_path, input_record) in enumerate(
        local_inputs
    ):
        if index >= len(fingerprints):
            break
        fingerprint = fingerprints[index]
        if not isinstance(fingerprint, dict):
            issues.append(
                f"manifest {label} preflight_receipt input_fingerprints[{index}] must "
                f"be an object: {normalized_receipt}"
            )
            continue
        fingerprint_key = normalize_generation_input_key(package, fingerprint.get("file"))
        if fingerprint_key != input_key:
            issues.append(
                f"manifest {label} preflight_receipt input_fingerprints[{index}].file "
                f"does not match input_assets order: {normalized_receipt}"
            )
        fingerprint_hash = fingerprint.get("sha256")
        if not isinstance(fingerprint_hash, str) or not SHA256_PATTERN.fullmatch(
            fingerprint_hash
        ):
            issues.append(
                f"manifest {label} preflight_receipt input_fingerprints[{index}].sha256 "
                f"is invalid: {normalized_receipt}"
            )
        elif not input_path.is_file():
            issues.append(
                f"manifest {label} preflight input file does not exist: {input_path_value}"
            )
        elif file_sha256(input_path) != fingerprint_hash:
            issues.append(
                f"manifest {label} preflight input SHA-256 changed after receipt: "
                f"{input_path_value}"
            )
        current_rights = input_record.get("rights_status") if input_record else None
        if fingerprint.get("rights_status") != current_rights:
            issues.append(
                f"manifest {label} preflight input rights_status changed after receipt: "
                f"{input_path_value}"
            )

    has_conversation_inputs = isinstance(manifest_inputs, list) and any(
        isinstance(value, str)
        and value.strip().startswith(("conversation:", "user_attachment:"))
        for value in manifest_inputs
    )
    expected_binding = (
        "referenced_image_paths"
        if local_inputs
        else "num_last_images_to_include"
        if has_conversation_inputs
        else "none"
    )
    if receipt.get("input_binding") != expected_binding:
        issues.append(
            f"manifest {label} preflight_receipt input_binding does not match "
            f"input_assets: {normalized_receipt}"
        )

    raw_plan = receipt.get("plan")
    plan_value, plan_path, plan_path_issue = resolve_json_file(
        package,
        raw_plan,
        "preflight_receipt plan",
    )
    plan: dict[str, object] | None = None
    if plan_path_issue:
        issues.append(f"manifest {label} {plan_path_issue}")
    elif plan_path is not None:
        if receipt.get("plan_sha256") != file_sha256(plan_path):
            issues.append(
                f"manifest {label} preflight_receipt plan SHA-256 is stale: {plan_value}"
            )
        plan, plan_error = load_strict_json_object(plan_path, f"plan {plan_value}")
        if plan_error:
            issues.append(f"manifest {label} {plan_error}")

    if plan is not None:
        if plan.get("schema_version") != 1:
            issues.append(f"manifest {label} image-generation plan schema_version must be 1")
        if plan.get("project_adapter") != receipt_adapter:
            issues.append(
                f"manifest {label} preflight_receipt project_adapter does not match plan"
            )
        style_policy = plan.get("style_policy")
        if not isinstance(style_policy, dict):
            issues.append(
                f"manifest {label} image-generation plan style_policy must be an object"
            )
        tasks = plan.get("tasks")
        task_id = receipt.get("task_id")
        matched_tasks = (
            [
                item
                for item in tasks
                if isinstance(item, dict) and item.get("id") == task_id
            ]
            if isinstance(tasks, list)
            else []
        )
        if len(matched_tasks) != 1:
            issues.append(
                f"manifest {label} preflight_receipt task_id does not identify exactly "
                f"one plan task"
            )
        else:
            task = matched_tasks[0]
            style_override_source = receipt.get("style_override_source")
            task_override = task.get("style_override")
            if style_override_source is None:
                if task_override is not None:
                    issues.append(
                        f"manifest {label} preflight_receipt style_override_source "
                        "does not match plan task"
                    )
                if isinstance(style_policy, dict):
                    for field, receipt_field in (
                        ("profile", "style_profile"),
                        ("scope", "style_scope"),
                        ("new_image_strategy", "new_image_strategy"),
                    ):
                        if style_policy.get(field) != receipt.get(receipt_field):
                            issues.append(
                                f"manifest {label} preflight_receipt {receipt_field} "
                                "does not match plan style_policy"
                            )
                    if plan.get("profile_registry") != receipt.get("profile_registry"):
                        issues.append(
                            f"manifest {label} preflight_receipt profile_registry "
                            "does not match plan"
                        )
            elif not isinstance(task_override, dict):
                issues.append(
                    f"manifest {label} preflight_receipt style_override_source "
                    "has no matching plan task style_override"
                )
            else:
                for field, expected in (
                    ("source", style_override_source),
                    ("profile", receipt.get("style_profile")),
                    ("profile_registry", receipt.get("profile_registry")),
                ):
                    if task_override.get(field) != expected:
                        issues.append(
                            f"manifest {label} preflight_receipt style override {field} "
                            "does not match plan task"
                        )
                if receipt.get("style_scope") != "task":
                    issues.append(
                        f"manifest {label} preflight_receipt style_scope must be task "
                        "for a plan task style_override"
                    )
            if task.get("visual_type", "general_editorial") != receipt.get("visual_type"):
                issues.append(
                    f"manifest {label} preflight_receipt visual_type does not match plan"
                )
            if task.get("reference_strategy", "none") != receipt.get(
                "reference_strategy"
            ):
                issues.append(
                    f"manifest {label} preflight_receipt reference_strategy does not match plan"
                )
            stage_key = "reference_stage" if stage == "reference" else "final_stage"
            plan_stage = task.get(stage_key)
            if not isinstance(plan_stage, dict):
                issues.append(
                    f"manifest {label} preflight_receipt stage is absent from plan task"
                )
            else:
                plan_stage_inputs = plan_stage.get("input_assets", [])
                stage_expected = {
                    "mode": receipt.get("mode"),
                    "prompt_ref": receipt.get("prompt_ref"),
                    "present_to_user": receipt.get("present_to_user"),
                }
                for field, expected in stage_expected.items():
                    if plan_stage.get(field) != expected:
                        issues.append(
                            f"manifest {label} preflight_receipt {field} does not match plan stage"
                        )
                declared_stage_prompt_hash = plan_stage.get("prompt_sha256")
                if (
                    declared_stage_prompt_hash is not None
                    and declared_stage_prompt_hash != receipt.get("prompt_sha256")
                ):
                    issues.append(
                        f"manifest {label} preflight_receipt prompt_sha256 does not "
                        "match plan stage"
                    )
                for field, expected_key in (
                    ("output", file_key),
                    ("receipt", canonical_package_key(package, normalized_receipt)),
                ):
                    stage_value = plan_stage.get(field)
                    stage_value_key = (
                        canonical_package_key(package, stage_value)
                        if isinstance(stage_value, str)
                        else None
                    )
                    if stage_value_key != expected_key:
                        issues.append(
                            f"manifest {label} preflight_receipt {field} does not match plan stage"
                        )
                if isinstance(receipt_inputs, list):
                    normalized_plan_inputs = (
                        [
                            normalize_generation_input_key(package, value)
                            for value in plan_stage_inputs
                        ]
                        if isinstance(plan_stage_inputs, list)
                        else []
                    )
                    if normalized_plan_inputs != normalized_receipt_inputs:
                        issues.append(
                            f"manifest {label} preflight_receipt input_assets do not match plan stage"
                        )
                computed_constraints_hash = hashlib.sha256(
                    json.dumps(
                        {
                            "output_constraints": plan_stage.get("output_constraints", []),
                            "preserve": plan_stage.get("preserve", []),
                            "avoid": plan_stage.get("avoid", []),
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest()
                if receipt.get("constraints_sha256") != computed_constraints_hash:
                    issues.append(
                        f"manifest {label} preflight_receipt constraints_sha256 does not "
                        f"match plan stage"
                    )

    workspace_root = find_workspace_root(package)
    if workspace_root is None:
        issues.append(
            f"manifest {label} cannot locate workspace root for profile_registry validation"
        )
    else:
        registry_value, registry_path, registry_path_issue = resolve_json_file(
            workspace_root,
            receipt.get("profile_registry"),
            "preflight_receipt profile_registry",
        )
        if registry_path_issue:
            issues.append(f"manifest {label} {registry_path_issue}")
        elif registry_path is not None:
            if receipt.get("profile_registry_sha256") != file_sha256(registry_path):
                issues.append(
                    f"manifest {label} preflight_receipt profile_registry SHA-256 is stale: "
                    f"{registry_value}"
                )
            registry, registry_error = load_strict_json_object(
                registry_path,
                f"profile_registry {registry_value}",
            )
            if registry_error:
                issues.append(f"manifest {label} {registry_error}")
            elif registry is not None:
                profiles = registry.get("profiles")
                profile = (
                    profiles.get(receipt.get("style_profile"))
                    if isinstance(profiles, dict)
                    and isinstance(receipt.get("style_profile"), str)
                    else None
                )
                if registry.get("schema_version") != 1 or not isinstance(profile, dict):
                    issues.append(
                        f"manifest {label} preflight_receipt style_profile is absent from "
                        f"the declared schema_version 1 profile_registry"
                    )
                elif profile.get("new_image_strategy") != receipt.get(
                    "new_image_strategy"
                ):
                    issues.append(
                        f"manifest {label} preflight_receipt new_image_strategy does not "
                        f"match profile_registry"
                    )
                else:
                    governed_profile_hash = profile.get("prompt_sha256")
                    if governed_profile_hash is not None:
                        if not isinstance(
                            governed_profile_hash, str
                        ) or not SHA256_PATTERN.fullmatch(governed_profile_hash):
                            issues.append(
                                f"manifest {label} profile_registry prompt_sha256 must "
                                "be 64 lowercase hexadecimal characters"
                            )
                        elif governed_profile_hash != receipt.get("prompt_sha256"):
                            issues.append(
                                f"manifest {label} preflight_receipt prompt_sha256 does "
                                "not match profile_registry"
                            )
                    elif profile.get("prompt_source") is not None:
                        issues.append(
                            f"manifest {label} profile_registry prompt_source requires "
                            "prompt_sha256"
                        )
                    if profile.get("prompt_source") != receipt.get("prompt_source"):
                        issues.append(
                            f"manifest {label} preflight_receipt prompt_source does not "
                            "match profile_registry"
                        )
                    allowed_modes = profile.get("allowed_final_modes")
                    if (
                        stage == "final"
                        and (
                            not isinstance(allowed_modes, list)
                            or receipt.get("mode") not in allowed_modes
                        )
                    ):
                        issues.append(
                            f"manifest {label} preflight_receipt mode is not allowed by "
                            "profile_registry"
                        )

    return issues


def validate_manifest_assets(
    package: Path,
    assets: list[dict[str, object]],
    version: int,
    status: str,
    platform: str,
    draft_image_targets: set[str],
    publish_project_adapter: str | None,
    publish_adapter_issue: str | None,
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

        source_type = asset.get("source_type")
        ai_generated_like = (
            isinstance(source_type, str)
            and source_type.strip().casefold().startswith("ai_generated")
        )
        if not ai_generated_like:
            continue
        if source_type != "ai_generated":
            add_contract_issue(
                f"manifest {label} uses non-standard AI source_type {source_type!r}; "
                'use source_type: "ai_generated" so generation provenance cannot be bypassed',
                release_bound,
            )

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

        if strict:
            for issue in validate_ai_preflight_receipt(
                package,
                asset,
                label,
                file_key,
                assets_by_file,
                release_bound,
                platform,
                publish_project_adapter,
                publish_adapter_issue,
            ):
                add_contract_issue(issue, release_bound)

        input_assets = asset.get("input_assets")
        if not is_missing_value(input_assets) and not isinstance(input_assets, list):
            add_contract_issue(
                f"manifest {label} input_assets must be a list",
                release_bound,
            )
        requires_input = (
            isinstance(generation_mode, str)
            and generation_mode in REFERENCE_GENERATION_MODES
        )
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


def markdown_inline_text(token: object) -> str:
    """Return visible text from a markdown-it inline token."""

    children = getattr(token, "children", None)
    if children is None:
        return " ".join(str(getattr(token, "content", "")).split())
    text = "".join(
        str(getattr(child, "content", ""))
        for child in children
        if getattr(child, "type", "") in {"text", "code_inline"}
    )
    return " ".join(text.split())


def nonempty_markdown_sections(
    body: str,
    required_titles: tuple[str, ...],
) -> dict[str, bool]:
    """Return whether each named Markdown section has non-heading content."""

    tokens = MARKDOWN_PARSER.parse(body)
    results = dict.fromkeys(required_titles, False)
    for index, token in enumerate(tokens):
        if token.type != "heading_open" or index + 1 >= len(tokens):
            continue
        title_token = tokens[index + 1]
        if title_token.type != "inline":
            continue
        title = markdown_inline_text(title_token)
        if title not in results:
            continue

        level = int(token.tag[1:])
        end_index = len(tokens)
        for later_index in range(index + 2, len(tokens)):
            later = tokens[later_index]
            if (
                later.type == "heading_open"
                and int(later.tag[1:]) <= level
            ):
                end_index = later_index
                break

        has_content = False
        for content_index in range(index + 2, end_index):
            content_token = tokens[content_index]
            if content_token.type == "inline":
                if (
                    content_index > 0
                    and tokens[content_index - 1].type == "heading_open"
                ):
                    continue
                visible_text = markdown_inline_text(content_token)
                if (
                    visible_text
                    and visible_text not in JUDGMENT_WORKSHOP_PLACEHOLDERS
                ):
                    has_content = True
                    break
            elif content_token.type in {"code_block", "fence", "html_block"}:
                if str(content_token.content).strip():
                    has_content = True
                    break
        results[title] = results[title] or has_content
    return results


def validate_judgment_workshop(
    package: Path,
    draft_metadata: dict[str, str],
    draft_status: str,
) -> list[str]:
    """Validate the opt-in judgment workshop record referenced by draft.md."""

    if draft_metadata.get("judgment_workshop") != JUDGMENT_WORKSHOP_POINTER:
        return []

    workshop_path = package / JUDGMENT_WORKSHOP_POINTER
    if not workshop_path.is_file():
        return [
            "draft.md judgment_workshop points to missing file: "
            f"{JUDGMENT_WORKSHOP_POINTER}"
        ]

    try:
        workshop = workshop_path.read_text(encoding="utf-8")
        workshop_metadata, workshop_body = split_frontmatter(
            workshop,
            JUDGMENT_WORKSHOP_POINTER,
        )
    except (OSError, UnicodeError, ValueError) as exc:
        return [f"could not parse {JUDGMENT_WORKSHOP_POINTER}: {exc}"]

    issues: list[str] = []
    workshop_status = workshop_metadata.get("status", "")
    if workshop_status not in JUDGMENT_WORKSHOP_STATUSES:
        issues.append(
            "judgment workshop status must be discussing, locked, or not_required; "
            f"got: {workshop_status or '<empty>'}"
        )
        return issues

    if (
        workshop_status == "discussing"
        and draft_status in JUDGMENT_WORKSHOP_GATED_STATES
    ):
        issues.append(
            f"{draft_status} status cannot use a discussing judgment workshop"
        )

    if workshop_status == "locked":
        voice_mode = workshop_metadata.get("voice_mode", "")
        if voice_mode not in JUDGMENT_WORKSHOP_VOICE_MODES:
            issues.append(
                "locked judgment workshop voice_mode must be personal or company; "
                f"got: {voice_mode or '<empty>'}"
            )

        rounds_completed = workshop_metadata.get("rounds_completed", "")
        if re.fullmatch(r"[3-5]", rounds_completed) is None:
            issues.append(
                "locked judgment workshop rounds_completed must be an integer "
                f"from 3 to 5; got: {rounds_completed or '<empty>'}"
            )

        if workshop_metadata.get("user_confirmed", "").lower() != "true":
            issues.append("locked judgment workshop requires user_confirmed: true")

        confirmed_on = workshop_metadata.get("confirmed_on", "")
        if not is_iso_date(confirmed_on):
            issues.append(
                "locked judgment workshop confirmed_on must be an ISO date "
                "(YYYY-MM-DD)"
            )

        sections = nonempty_markdown_sections(
            workshop_body,
            JUDGMENT_WORKSHOP_LOCKED_SECTIONS,
        )
        for title in JUDGMENT_WORKSHOP_LOCKED_SECTIONS:
            if not sections[title]:
                issues.append(
                    "locked judgment workshop section is missing or empty: "
                    f"{title}"
                )

    if (
        workshop_status == "not_required"
        and not workshop_metadata.get("reason", "").strip()
    ):
        issues.append(
            "not_required judgment workshop requires a non-empty reason"
        )

    return issues


def extract_ai_pattern_diagnostic(review: str) -> str | None:
    """Return the diagnostic section through its next peer or ancestor heading."""

    lines = review.splitlines()
    tokens = MARKDOWN_PARSER.parse(review)
    for index, token in enumerate(tokens):
        if token.type != "heading_open" or index + 1 >= len(tokens):
            continue
        title_token = tokens[index + 1]
        if title_token.type != "inline":
            continue
        title = " ".join(title_token.content.casefold().split())
        if title not in AI_PATTERN_DIAGNOSTIC_TITLES:
            continue

        level = int(token.tag[1:])
        start_line = token.map[1] if token.map else 0
        end_line = len(lines)
        for later in tokens[index + 2 :]:
            if later.type != "heading_open":
                continue
            later_level = int(later.tag[1:])
            if later_level <= level and later.map:
                end_line = later.map[0]
                break
        return "\n".join(lines[start_line:end_line])
    return None


def split_markdown_table_row(line: str) -> list[str]:
    """Split one simple Markdown table row into normalized, unescaped cells."""

    stripped = line.strip().replace("｜", "|")
    if "|" not in stripped:
        return []
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip().replace(r"\|", "|") for cell in stripped.split("|")]


def is_markdown_table_separator(cells: list[str]) -> bool:
    return bool(cells) and all(
        re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) is not None
        for cell in cells
    )


def normalize_review_cell(cell: str) -> str:
    return re.sub(r"[*`]", "", cell).strip().casefold()


def open_major_ai_pattern_items(section: str) -> list[tuple[str, str]]:
    """Return open blocker/major HUMAN-AI rows from diagnostic Markdown tables."""

    lines = section.splitlines()
    open_items: list[tuple[str, str]] = []
    for line_index, line in enumerate(lines[:-1]):
        header_aliases = {
            "id": "id",
            "severity": "severity",
            "级别": "severity",
            "严重度": "severity",
            "status": "status",
            "状态": "status",
        }
        headers = [
            header_aliases.get(normalize_review_cell(cell), "")
            for cell in split_markdown_table_row(line)
        ]
        if not {"id", "severity", "status"}.issubset(headers):
            continue
        separator = split_markdown_table_row(lines[line_index + 1])
        if len(separator) != len(headers) or not is_markdown_table_separator(separator):
            continue

        column = {header: index for index, header in enumerate(headers)}
        for row_line in lines[line_index + 2 :]:
            cells = split_markdown_table_row(row_line)
            if not cells:
                break
            if is_markdown_table_separator(cells):
                continue
            if len(cells) < len(headers):
                cells.extend([""] * (len(headers) - len(cells)))
            item_id = normalize_review_cell(cells[column["id"]]).upper()
            severity = normalize_review_cell(cells[column["severity"]])
            item_status = normalize_review_cell(cells[column["status"]])
            if (
                item_id.startswith("HUMAN-AI-")
                and severity in {"blocker", "major"}
                and item_status == "open"
            ):
                open_items.append((item_id, severity))
    return open_items


def validate_ai_pattern_review(review: str) -> list[str]:
    """Validate the structured, detect-only AI-pattern review record."""

    section = extract_ai_pattern_diagnostic(review)
    if section is None:
        return [
            "review.md missing required AI-pattern diagnostic section for WeChat"
        ]

    status_match = re.search(
        r"(?im)^[ \t]*[-*+][ \t]+(?:\*\*)?(?:status|状态)(?:\*\*)?[ \t]*[:：]"
        r"(?:\*\*)?[ \t]*([^\r\n]+?)[ \t]*$",
        section,
    )
    issues: list[str] = []
    if status_match is None:
        issues.append("review.md AI-pattern diagnostic is missing Status")
    else:
        diagnostic_status = normalize_review_cell(status_match.group(1))
        if diagnostic_status != "pass":
            issues.append(
                "review.md AI-pattern diagnostic Status must be pass, "
                f"got: {diagnostic_status or '<empty>'}"
            )

    for item_id, severity in open_major_ai_pattern_items(section):
        issues.append(
            f"review.md AI-pattern diagnostic has open {severity} item: {item_id}"
        )
    return issues


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
    review_path = package / "review.md"
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
    publish_project_adapter, publish_adapter_issue = read_publish_project_adapter(
        package
    )
    if platform and platform not in ALLOWED_PLATFORMS:
        errors.append(f"unsupported platform: {platform}")
    if status and status not in ALLOWED_STATES:
        errors.append(f"unsupported status: {status}")
    errors.extend(validate_judgment_workshop(package, metadata, status))
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

    if platform == "wechat" and review_path.is_file():
        ai_pattern_issues = validate_ai_pattern_review(
            review_path.read_text(encoding="utf-8")
        )
        if status in {"ready", "published"}:
            errors.extend(ai_pattern_issues)
        else:
            warnings.extend(ai_pattern_issues)

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
        publish_project_adapter,
        publish_adapter_issue,
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
