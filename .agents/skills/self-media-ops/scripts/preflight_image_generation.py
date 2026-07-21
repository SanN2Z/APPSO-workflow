# -*- coding: utf-8 -*-
"""Build and validate a deterministic image-generation request before tool use."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any


sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_content_package import (  # noqa: E402
    DERIVATIVE_INPUT_RIGHTS_STATUSES,
    parse_asset_manifest,
)


SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
WINDOWS_ABSOLUTE_PATTERN = re.compile(r"^[A-Za-z]:[\\/]")
URL_SCHEME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
SUPPORTED_PLAN_VERSION = 1
SUPPORTED_PROFILE_REGISTRY_VERSION = 1
STYLE_SCOPES = {"task", "all_ai_generated_editorial_images"}
NEW_IMAGE_STRATEGIES = {
    "direct",
    "reference_required",
    "two_stage_reference_then_redraw",
}
REFERENCE_STRATEGIES = {"none", "generated_base", "provided_local", "conversation_attachment"}
INPUT_BINDINGS = {"none", "referenced_image_paths", "num_last_images_to_include"}
STAGE_KEYS = {"reference": "reference_stage", "final": "final_stage"}
PROJECT_ADAPTERS = {"appsso", "generic"}
APPSO_DEFAULT_STYLE_PROFILE = "appsso-004"
APPSO_GENERATABLE_VISUAL_TYPES = {
    "ai_editorial_creative",
    "qualitative_explainer",
}
APPSO_NON_GENERATABLE_VISUAL_TYPES = {
    "official_evidence",
    "real_ui",
    "logo",
    "news_reconstruction",
    "precision_chart",
}
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


class ContractError(ValueError):
    """Raised when an image-generation request violates the project contract."""


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_input_sha256(path: Path) -> str:
    if path.is_symlink():
        raise ContractError(f"input asset must not be a symlink: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        before = os.fstat(handle.fileno())
        if before.st_nlink != 1:
            raise ContractError(f"input asset must not be a hard link: {path}")
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
        after = os.fstat(handle.fileno())
    before_signature = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
    )
    after_signature = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    )
    if before_signature != after_signature:
        raise ContractError(f"input asset changed while it was being hashed: {path}")
    return digest.hexdigest()


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"{label} not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ContractError(
            f"{label} is not valid JSON at line {exc.lineno}, column {exc.colno}: {path}"
        ) from exc
    if not isinstance(loaded, dict):
        raise ContractError(f"{label} must be a JSON object: {path}")
    return loaded


def declared_publish_value(package: Path, key: str) -> str | None:
    publish_path = package / "publish.yml"
    if not publish_path.is_file():
        return None
    for raw_line in publish_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or not line.startswith(f"{key}:"):
            continue
        value = line.split(":", 1)[1].strip()
        if " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        return value.strip("\"'") or None
    return None


def validate_explicit_user_override(style_policy: dict[str, Any]) -> None:
    override = require_mapping(
        style_policy.get("user_override"),
        "style_policy user_override",
    )
    if override.get("source") != "explicit_current_task_user":
        raise ContractError(
            "APPSO style override source must be explicit_current_task_user"
        )
    require_nonempty_string(override.get("reason"), "style_policy user_override reason")
    confirmed_on = require_nonempty_string(
        override.get("confirmed_on"),
        "style_policy user_override confirmed_on",
    )
    if not ISO_DATE_PATTERN.fullmatch(confirmed_on):
        raise ContractError(
            "style_policy user_override confirmed_on must be an ISO date"
        )
    try:
        date.fromisoformat(confirmed_on)
    except ValueError as exc:
        raise ContractError(
            "style_policy user_override confirmed_on must be an ISO date"
        ) from exc


def require_mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be an object")
    return value


def require_nonempty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} must be a non-empty string")
    return value.strip()


def require_string_list(value: object, label: str, *, allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list):
        raise ContractError(f"{label} must be a list")
    if not allow_empty and not value:
        raise ContractError(f"{label} must not be empty")
    normalized: list[str] = []
    for index, item in enumerate(value, start=1):
        normalized.append(require_nonempty_string(item, f"{label}[{index}]"))
    return normalized


def find_workspace_root(start: Path) -> Path:
    resolved = start.resolve()
    candidates = (resolved, *resolved.parents)
    for candidate in candidates:
        if (
            (candidate / "AGENTS.md").is_file()
            and (candidate / "上下文").is_dir()
            and (candidate / "共享").is_dir()
        ):
            return candidate
    raise ContractError(f"could not locate workspace root from: {start}")


def normalize_relative_path(raw_value: object, label: str) -> str:
    value = unicodedata.normalize(
        "NFC",
        require_nonempty_string(raw_value, label).replace("\\", "/"),
    )
    if WINDOWS_ABSOLUTE_PATTERN.match(value) or URL_SCHEME_PATTERN.match(value):
        raise ContractError(f"{label} must be a relative local path: {value}")
    pure = PurePosixPath(value)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ContractError(f"{label} contains unsafe path segments: {value}")
    for part in pure.parts:
        if ":" in part:
            raise ContractError(f"{label} must not contain a colon or NTFS ADS: {value}")
        if part.endswith((" ", ".")):
            raise ContractError(f"{label} has a Windows-unsafe trailing character: {value}")
        basename = part.split(".", 1)[0].upper()
        if basename in WINDOWS_RESERVED_NAMES:
            raise ContractError(f"{label} contains a Windows reserved name: {value}")
    return pure.as_posix()


def normalize_input_reference(raw_value: object, label: str) -> str:
    value = require_nonempty_string(raw_value, label)
    if value.startswith(("conversation:", "user_attachment:")):
        prefix, identifier = value.split(":", 1)
        if not identifier.strip():
            raise ContractError(f"{label} has an empty {prefix} identifier")
        return f"{prefix}:{identifier.strip()}"
    return normalize_relative_path(value, label)


def resolve_within(base: Path, raw_value: object, label: str) -> tuple[str, Path]:
    normalized = normalize_relative_path(raw_value, label)
    unresolved = base.resolve() / Path(*PurePosixPath(normalized).parts)
    current = base.resolve()
    for part in PurePosixPath(normalized).parts:
        current = current / part
        if current.exists() and (
            current.is_symlink()
            or (hasattr(current, "is_junction") and current.is_junction())
        ):
            raise ContractError(f"{label} must not traverse a link or junction: {normalized}")
    candidate = unresolved.resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError as exc:
        raise ContractError(f"{label} escapes its allowed root: {normalized}") from exc
    return normalized, candidate


def require_prefix(path: str, prefix: str, label: str) -> None:
    normalized_prefix = prefix.rstrip("/") + "/"
    if not path.startswith(normalized_prefix):
        raise ContractError(f"{label} must be under {normalized_prefix}: {path}")


def load_profile(
    workspace_root: Path,
    plan: dict[str, Any],
    profile_id: str,
    *,
    registry_value: object | None = None,
) -> tuple[dict[str, Any], str, Path]:
    if registry_value is None:
        registry_value = plan.get("profile_registry")
    registry_relative, registry_path = resolve_within(
        workspace_root,
        registry_value,
        "profile_registry",
    )
    registry = load_json_object(registry_path, "profile registry")
    if registry.get("schema_version") != SUPPORTED_PROFILE_REGISTRY_VERSION:
        raise ContractError(
            "unsupported profile registry schema_version: "
            f"{registry.get('schema_version')}"
        )
    profiles = require_mapping(registry.get("profiles"), "profile registry profiles")
    profile = require_mapping(profiles.get(profile_id), f"profile {profile_id}")
    return profile, registry_relative, registry_path


def extract_governed_prompt(
    workspace_root: Path,
    profile_id: str,
    profile: dict[str, Any],
) -> tuple[str, str, str]:
    prompt_relative, prompt_path = resolve_within(
        workspace_root,
        profile.get("prompt_source"),
        f"profile {profile_id} prompt_source",
    )
    if not prompt_path.is_file():
        raise ContractError(
            f"governed prompt source is unavailable for {profile_id}: {prompt_relative}"
        )
    heading = require_nonempty_string(
        profile.get("prompt_heading"),
        f"profile {profile_id} prompt_heading",
    )
    lines = prompt_path.read_text(encoding="utf-8").splitlines()
    try:
        heading_index = next(index for index, line in enumerate(lines) if line.strip() == heading)
    except StopIteration as exc:
        raise ContractError(
            f"governed prompt heading not found for {profile_id}: {heading}"
        ) from exc
    prompt_line = next(
        (line for line in lines[heading_index + 1 :] if line.strip()),
        "",
    )
    if not prompt_line.startswith("> "):
        raise ContractError(
            f"governed prompt for {profile_id} must be one Markdown quote line"
        )
    prompt = prompt_line[2:]
    expected_hash = require_nonempty_string(
        profile.get("prompt_sha256"),
        f"profile {profile_id} prompt_sha256",
    )
    if not SHA256_PATTERN.fullmatch(expected_hash):
        raise ContractError(f"profile {profile_id} prompt_sha256 is invalid")
    actual_hash = sha256_text(prompt)
    if actual_hash != expected_hash:
        raise ContractError(
            f"governed prompt hash mismatch for {profile_id}: "
            f"expected {expected_hash}, got {actual_hash}"
        )
    expected_characters = profile.get("prompt_characters")
    if expected_characters is not None and (
        not isinstance(expected_characters, int) or len(prompt) != expected_characters
    ):
        raise ContractError(
            f"governed prompt character count mismatch for {profile_id}: "
            f"expected {expected_characters}, got {len(prompt)}"
        )
    return prompt, expected_hash, prompt_relative


def find_forbidden_style_terms(
    profile: dict[str, Any],
    values: list[str],
) -> list[str]:
    terms = require_string_list(
        profile.get("forbidden_positive_terms", []),
        "profile forbidden_positive_terms",
    )
    haystack = normalize_style_text("\n".join(values))
    return sorted({term for term in terms if normalize_style_text(term) in haystack})


def normalize_style_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    normalized = normalized.replace("\u200b", "").replace("\u200c", "").replace("\u200d", "")
    normalized = "".join(
        character if character.isalnum() or "\u3400" <= character <= "\u9fff" else " "
        for character in normalized
    )
    return " ".join(normalized.split())


def find_forbidden_avoid_terms(
    profile: dict[str, Any],
    values: list[str],
) -> list[str]:
    terms = require_string_list(
        profile.get("forbidden_avoid_terms", []),
        "profile forbidden_avoid_terms",
    )
    haystack = normalize_style_text("\n".join(values))
    return sorted({term for term in terms if normalize_style_text(term) in haystack})


def compose_prompt(
    base: str,
    *,
    output_constraints: list[str],
    preserve: list[str],
    avoid: list[str],
) -> str:
    sections = [base.strip()]
    for heading, items in (
        ("Output constraints", output_constraints),
        ("Preserve", preserve),
        ("Avoid", avoid),
    ):
        if items:
            sections.append(heading + ":\n" + "\n".join(f"- {item}" for item in items))
    return "\n\n".join(sections)


def load_manifest_records(package: Path) -> dict[str, dict[str, object]]:
    manifest_path = package / "asset-manifest.yml"
    try:
        text = manifest_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ContractError(f"asset manifest not found: {manifest_path}") from exc
    version, assets, issues = parse_asset_manifest(text)
    if version != 2:
        raise ContractError(
            f"image-generation preflight requires asset-manifest.yml version 2, got {version}"
        )
    if issues:
        raise ContractError("invalid asset manifest: " + "; ".join(issues))
    records: dict[str, dict[str, object]] = {}
    for asset in assets:
        raw_file = asset.get("file")
        if not isinstance(raw_file, str) or not raw_file.strip():
            continue
        normalized = normalize_relative_path(raw_file, "manifest asset file")
        records[normalized] = asset
    return records


def validate_registered_inputs(
    package: Path,
    input_assets: list[str],
) -> list[dict[str, str]]:
    records = load_manifest_records(package)
    fingerprints: list[dict[str, str]] = []
    for input_asset in input_assets:
        _, input_path = resolve_within(package, input_asset, "final_stage input asset")
        if not input_path.is_file():
            raise ContractError(f"final_stage input asset does not exist: {input_asset}")
        record = records.get(input_asset)
        if record is None:
            raise ContractError(
                f"final_stage input asset lacks a manifest rights record: {input_asset}"
            )
        rights_status = record.get("rights_status")
        if rights_status not in DERIVATIVE_INPUT_RIGHTS_STATUSES:
            raise ContractError(
                "final_stage input asset is not cleared for derivative use: "
                f"{input_asset} ({rights_status})"
            )
        fingerprints.append(
            {
                "file": input_asset,
                "sha256": stable_input_sha256(input_path),
                "rights_status": str(rights_status),
            }
        )
    return fingerprints


def build_request(
    package: Path,
    task_id: str,
    stage_name: str,
    *,
    plan_path: Path | None = None,
    include_prompt: bool = False,
) -> tuple[dict[str, Any], str, Path]:
    package = package.resolve()
    workspace_root = find_workspace_root(package)
    selected_plan_path = (
        plan_path.resolve()
        if plan_path is not None
        else package / "research" / "image-generation-plan.json"
    )
    try:
        selected_plan_path.relative_to(package)
    except ValueError as exc:
        raise ContractError("image-generation plan must be inside the content package") from exc
    plan = load_json_object(selected_plan_path, "image-generation plan")
    if plan.get("schema_version") != SUPPORTED_PLAN_VERSION:
        raise ContractError(
            f"unsupported image-generation plan schema_version: {plan.get('schema_version')}"
        )
    if plan.get("template_only") is True:
        raise ContractError(
            "image-generation plan is still marked template_only; copy it into the "
            "content package, replace every placeholder, and remove template_only"
        )

    project_adapter = require_nonempty_string(
        plan.get("project_adapter"),
        "project_adapter",
    )
    if project_adapter not in PROJECT_ADAPTERS:
        raise ContractError(f"unsupported project_adapter: {project_adapter}")
    layout_profile = declared_publish_value(package, "layout_profile")
    publish_adapter = declared_publish_value(package, "project_adapter")
    if publish_adapter is not None and publish_adapter not in PROJECT_ADAPTERS:
        raise ContractError(
            f"publish.yml declares unsupported project_adapter: {publish_adapter}"
        )
    if publish_adapter is not None and publish_adapter != project_adapter:
        raise ContractError(
            "image-generation project_adapter does not match publish.yml: "
            f"{project_adapter} != {publish_adapter}"
        )
    if layout_profile == "appsso-article-v1" and project_adapter != "appsso":
        raise ContractError(
            "publish.yml selects appsso-article-v1, so image-generation "
            "project_adapter must be appsso"
        )
    if (
        project_adapter == "appsso"
        and publish_adapter != "appsso"
        and layout_profile != "appsso-article-v1"
    ):
        raise ContractError(
            "APPSO image generation requires an independent package declaration: "
            "set project_adapter: appsso in publish.yml"
        )

    style_policy = require_mapping(plan.get("style_policy"), "style_policy")
    profile_id = require_nonempty_string(style_policy.get("profile"), "style_policy profile")
    scope = require_nonempty_string(style_policy.get("scope"), "style_policy scope")
    if scope not in STYLE_SCOPES:
        raise ContractError(f"unsupported style_policy scope: {scope}")
    if project_adapter == "appsso" and scope != "all_ai_generated_editorial_images":
        raise ContractError(
            "APPSO image plans must apply style_policy to all AI-generated editorial images"
        )
    strategy = require_nonempty_string(
        style_policy.get("new_image_strategy"),
        "style_policy new_image_strategy",
    )
    if strategy not in NEW_IMAGE_STRATEGIES:
        raise ContractError(f"unsupported new-image strategy: {strategy}")
    allow_final_text_to_image = style_policy.get("allow_final_text_to_image")
    if not isinstance(allow_final_text_to_image, bool):
        raise ContractError("style_policy allow_final_text_to_image must be true or false")

    profile, registry_relative, registry_path = load_profile(
        workspace_root,
        plan,
        profile_id,
    )
    requires_reference = profile.get("requires_reference")
    if not isinstance(requires_reference, bool):
        raise ContractError(f"profile {profile_id} requires_reference must be boolean")
    profile_strategy = require_nonempty_string(
        profile.get("new_image_strategy"),
        f"profile {profile_id} new_image_strategy",
    )
    if strategy != profile_strategy:
        raise ContractError(
            f"style_policy strategy {strategy} does not match profile {profile_id}: "
            f"{profile_strategy}"
        )
    if project_adapter == "appsso" and profile_id != APPSO_DEFAULT_STYLE_PROFILE:
        raise ContractError(
            "APPSO root style_policy must remain appsso-004; put an explicit "
            "current-task user override on the individual task"
        )

    tasks = plan.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ContractError("image-generation plan tasks must be a non-empty list")
    seen_ids: set[str] = set()
    seen_paths: dict[str, str] = {}
    selected_task: dict[str, Any] | None = None
    for index, raw_task in enumerate(tasks, start=1):
        task = require_mapping(raw_task, f"tasks[{index}]")
        current_id = require_nonempty_string(task.get("id"), f"tasks[{index}] id")
        if current_id in seen_ids:
            raise ContractError(f"duplicate image-generation task id: {current_id}")
        seen_ids.add(current_id)
        if project_adapter == "appsso":
            visual_type = require_nonempty_string(
                task.get("visual_type"),
                f"task {current_id} visual_type",
            )
            if visual_type in APPSO_NON_GENERATABLE_VISUAL_TYPES:
                raise ContractError(
                    f"APPSO visual_type {visual_type} must not use image generation"
                )
            if visual_type not in APPSO_GENERATABLE_VISUAL_TYPES:
                raise ContractError(
                    f"unsupported APPSO visual_type for image generation: {visual_type}"
                )
        for current_stage_key in STAGE_KEYS.values():
            raw_stage = task.get(current_stage_key)
            if raw_stage is None:
                continue
            current_stage = require_mapping(
                raw_stage,
                f"task {current_id} {current_stage_key}",
            )
            for path_field in ("output", "receipt"):
                if path_field not in current_stage:
                    continue
                normalized_path = normalize_relative_path(
                    current_stage.get(path_field),
                    f"task {current_id} {current_stage_key} {path_field}",
                )
                collision_key = unicodedata.normalize("NFC", normalized_path).casefold()
                previous = seen_paths.get(collision_key)
                current_label = f"{current_id}.{current_stage_key}.{path_field}"
                if previous is not None:
                    raise ContractError(
                        "image-generation plan path collision after Windows normalization: "
                        f"{previous} and {current_label}"
                    )
                seen_paths[collision_key] = current_label
        if current_id == task_id:
            selected_task = task
    if selected_task is None:
        raise ContractError(f"image-generation task not found: {task_id}")

    style_override_source: str | None = None
    raw_style_override = selected_task.get("style_override")
    if raw_style_override is not None:
        if project_adapter != "appsso":
            raise ContractError("task style_override is only supported by the appsso adapter")
        override = require_mapping(raw_style_override, f"task {task_id} style_override")
        validate_explicit_user_override({"user_override": override})
        override_profile_id = require_nonempty_string(
            override.get("profile"),
            f"task {task_id} style_override profile",
        )
        override_registry = require_nonempty_string(
            override.get("profile_registry"),
            f"task {task_id} style_override profile_registry",
        )
        profile, registry_relative, registry_path = load_profile(
            workspace_root,
            plan,
            override_profile_id,
            registry_value=override_registry,
        )
        profile_id = override_profile_id
        requires_reference = profile.get("requires_reference")
        if not isinstance(requires_reference, bool):
            raise ContractError(f"profile {profile_id} requires_reference must be boolean")
        strategy = require_nonempty_string(
            profile.get("new_image_strategy"),
            f"profile {profile_id} new_image_strategy",
        )
        if strategy not in NEW_IMAGE_STRATEGIES:
            raise ContractError(f"unsupported new-image strategy: {strategy}")
        override_modes = require_string_list(
            profile.get("allowed_final_modes"),
            f"profile {profile_id} allowed_final_modes",
            allow_empty=False,
        )
        allow_final_text_to_image = "text_to_image" in override_modes
        scope = "task"
        style_override_source = str(override.get("source"))

    purpose = require_nonempty_string(selected_task.get("purpose"), f"task {task_id} purpose")
    visual_type = (
        require_nonempty_string(selected_task.get("visual_type"), f"task {task_id} visual_type")
        if project_adapter == "appsso"
        else require_nonempty_string(
            selected_task.get("visual_type", "general_editorial"),
            f"task {task_id} visual_type",
        )
    )
    default_reference_strategy = (
        "generated_base"
        if requires_reference and strategy == "two_stage_reference_then_redraw"
        else "none"
    )
    reference_strategy = require_nonempty_string(
        selected_task.get("reference_strategy", default_reference_strategy),
        f"task {task_id} reference_strategy",
    )
    if reference_strategy not in REFERENCE_STRATEGIES:
        raise ContractError(
            f"task {task_id} has unsupported reference_strategy: {reference_strategy}"
        )
    if requires_reference and reference_strategy == "none":
        raise ContractError(f"profile {profile_id} requires a reference strategy")
    if not requires_reference and reference_strategy != "none":
        raise ContractError(
            f"profile {profile_id} does not require reference_strategy {reference_strategy}"
        )
    if stage_name not in STAGE_KEYS:
        raise ContractError(f"unsupported stage: {stage_name}")
    stage_key = STAGE_KEYS[stage_name]
    stage = require_mapping(selected_task.get(stage_key), f"task {task_id} {stage_key}")
    mode = require_nonempty_string(stage.get("mode"), f"task {task_id} {stage_key} mode")
    present_to_user = stage.get("present_to_user")
    if not isinstance(present_to_user, bool):
        raise ContractError(
            f"task {task_id} {stage_key} present_to_user must be true or false"
        )
    output, _ = resolve_within(package, stage.get("output"), f"task {task_id} {stage_key} output")
    receipt, receipt_path = resolve_within(
        package,
        stage.get("receipt"),
        f"task {task_id} {stage_key} receipt",
    )
    require_prefix(receipt, "research/image-generation-runs", f"task {task_id} receipt")

    output_constraints = require_string_list(
        stage.get("output_constraints", []),
        f"task {task_id} {stage_key} output_constraints",
    )
    preserve = require_string_list(
        stage.get("preserve", []),
        f"task {task_id} {stage_key} preserve",
    )
    avoid = require_string_list(
        stage.get("avoid", []),
        f"task {task_id} {stage_key} avoid",
    )

    input_assets: list[str] = []
    input_fingerprints: list[dict[str, str]] = []
    input_binding = "none"
    num_last_images_to_include: int | None = None
    conversation_derivative_rights_confirmed = False
    prompt_source: str | None = None
    if stage_name == "reference":
        if strategy != "two_stage_reference_then_redraw":
            raise ContractError("reference stage is only valid for the two-stage strategy")
        if reference_strategy != "generated_base":
            raise ContractError(
                "reference stage is only valid when reference_strategy is generated_base"
            )
        if mode != "text_to_image":
            raise ContractError("reference_stage mode must be text_to_image")
        if present_to_user:
            raise ContractError(
                "reference_stage is an internal structural input and must not be presented to the user"
            )
        require_prefix(output, "research/source-assets", f"task {task_id} reference output")
        content_prompt = require_nonempty_string(
            stage.get("content_prompt"),
            f"task {task_id} reference_stage content_prompt",
        )
        reference_style_conflicts = find_forbidden_style_terms(
            profile,
            [content_prompt, purpose, *preserve, *output_constraints],
        )
        if reference_style_conflicts:
            raise ContractError(
                "reference_stage contains style language that can bleed into "
                f"{profile_id}: {', '.join(reference_style_conflicts)}"
            )
        prompt_payload = compose_prompt(
            content_prompt,
            output_constraints=output_constraints,
            preserve=preserve,
            avoid=avoid,
        )
        prompt_ref = require_nonempty_string(
            stage.get("prompt_ref"),
            f"task {task_id} reference_stage prompt_ref",
        )
        prompt_sha256 = sha256_text(prompt_payload)
    else:
        allowed_final_modes = require_string_list(
            profile.get("allowed_final_modes"),
            f"profile {profile_id} allowed_final_modes",
            allow_empty=False,
        )
        if mode not in allowed_final_modes:
            raise ContractError(
                f"final_stage mode {mode} is not allowed by profile {profile_id}: "
                f"{', '.join(allowed_final_modes)}"
            )
        if mode == "text_to_image" and not allow_final_text_to_image:
            raise ContractError("style_policy forbids text_to_image as a final deliverable")
        if not present_to_user:
            raise ContractError("final_stage must be marked present_to_user: true")
        require_prefix(output, "assets", f"task {task_id} final output")
        input_assets = [
            normalize_input_reference(item, f"task {task_id} final_stage input_assets")
            for item in require_string_list(
                stage.get("input_assets", []),
                f"task {task_id} final_stage input_assets",
                allow_empty=not requires_reference,
            )
        ]
        if requires_reference and not input_assets:
            raise ContractError(f"profile {profile_id} requires at least one input asset")
        output_key = unicodedata.normalize("NFC", output).casefold()
        for input_asset in input_assets:
            if input_asset.startswith(("conversation:", "user_attachment:")):
                continue
            if unicodedata.normalize("NFC", input_asset).casefold() == output_key:
                raise ContractError(
                    "final_stage output must not overwrite or alias an input asset: "
                    f"{input_asset}"
                )
        if reference_strategy == "generated_base":
            reference_stage = require_mapping(
                selected_task.get("reference_stage"),
                f"task {task_id} reference_stage",
            )
            reference_output = normalize_relative_path(
                reference_stage.get("output"),
                f"task {task_id} reference_stage output",
            )
            if reference_output not in input_assets:
                raise ContractError(
                    "final_stage must consume the configured reference_stage output: "
                    f"{reference_output}"
                )
            input_binding = "referenced_image_paths"
            input_fingerprints = validate_registered_inputs(package, input_assets)
        elif reference_strategy == "provided_local":
            if any(
                value.startswith(("conversation:", "user_attachment:"))
                for value in input_assets
            ):
                raise ContractError(
                    "provided_local inputs must be package-relative files, not conversation references"
                )
            input_binding = "referenced_image_paths"
            input_fingerprints = validate_registered_inputs(package, input_assets)
        elif reference_strategy == "conversation_attachment":
            if not all(
                value.startswith(("conversation:", "user_attachment:"))
                for value in input_assets
            ):
                raise ContractError(
                    "conversation_attachment inputs must use conversation: or user_attachment: references"
                )
            input_binding = "num_last_images_to_include"
            raw_count = stage.get("num_last_images_to_include")
            if not isinstance(raw_count, int) or isinstance(raw_count, bool) or not 1 <= raw_count <= 5:
                raise ContractError(
                    "conversation_attachment requires num_last_images_to_include between 1 and 5"
                )
            num_last_images_to_include = raw_count
            if stage.get("derivative_rights_confirmed") is not True:
                raise ContractError(
                    "conversation_attachment requires derivative_rights_confirmed: true"
                )
            conversation_derivative_rights_confirmed = True
        elif input_assets:
            raise ContractError("reference_strategy none cannot declare input_assets")
        has_governed_prompt = isinstance(profile.get("prompt_source"), str) and bool(
            profile.get("prompt_source", "").strip()
        )
        for forbidden_key in ("prompt", "style_prompt", "style", "style_medium"):
            if forbidden_key in stage:
                raise ContractError(
                    f"final_stage must not define {forbidden_key}; use the governed style base "
                    "plus separate preserve/output_constraints/avoid fields"
                )
        conflicts = find_forbidden_style_terms(
            profile,
            [purpose, *preserve, *output_constraints],
        )
        if conflicts:
            raise ContractError(
                "final_stage contains style language that conflicts with "
                f"{profile_id}: {', '.join(conflicts)}"
            )
        avoid_conflicts = find_forbidden_avoid_terms(profile, avoid)
        if avoid_conflicts:
            raise ContractError(
                "final_stage avoid list rejects required traits of "
                f"{profile_id}: {', '.join(avoid_conflicts)}"
            )
        prompt_ref = require_nonempty_string(
            stage.get("prompt_ref"),
            f"task {task_id} final_stage prompt_ref",
        )
        if prompt_ref != profile_id:
            raise ContractError(
                f"final_stage prompt_ref must match selected profile {profile_id}: {prompt_ref}"
            )
        if has_governed_prompt:
            if "content_prompt" in stage:
                raise ContractError(
                    "final_stage must not define content_prompt for a governed profile; "
                    "use preserve/output_constraints/avoid fields"
                )
            declared_prompt_hash = require_nonempty_string(
                stage.get("prompt_sha256"),
                f"task {task_id} final_stage prompt_sha256",
            )
            governed_prompt, prompt_sha256, prompt_source = extract_governed_prompt(
                workspace_root,
                profile_id,
                profile,
            )
            if declared_prompt_hash != prompt_sha256:
                raise ContractError(
                    f"final_stage prompt_sha256 does not match profile {profile_id}"
                )
            prompt_payload = compose_prompt(
                governed_prompt,
                output_constraints=output_constraints,
                preserve=preserve,
                avoid=avoid,
            )
        else:
            content_prompt = require_nonempty_string(
                stage.get("content_prompt"),
                f"task {task_id} final_stage content_prompt",
            )
            prompt_payload = compose_prompt(
                content_prompt,
                output_constraints=output_constraints,
                preserve=preserve,
                avoid=avoid,
            )
            prompt_sha256 = sha256_text(prompt_payload)
            declared_prompt_hash = stage.get("prompt_sha256")
            if declared_prompt_hash is not None and declared_prompt_hash != prompt_sha256:
                raise ContractError(
                    f"final_stage prompt_sha256 does not match the composed prompt for {profile_id}"
                )

    plan_relative = selected_plan_path.relative_to(package).as_posix()
    receipt_payload: dict[str, Any] = {
        "schema_version": 1,
        "status": "pass",
        "checked_on": date.today().isoformat(),
        "task_id": task_id,
        "stage": stage_name,
        "project_adapter": project_adapter,
        "visual_type": visual_type,
        "style_override_source": style_override_source,
        "style_profile": profile_id,
        "style_scope": scope,
        "new_image_strategy": strategy,
        "reference_strategy": reference_strategy,
        "mode": mode,
        "input_binding": input_binding,
        "num_last_images_to_include": num_last_images_to_include,
        "conversation_derivative_rights_confirmed": (
            conversation_derivative_rights_confirmed
        ),
        "prompt_ref": prompt_ref,
        "prompt_sha256": prompt_sha256,
        "invocation_prompt_sha256": sha256_text(prompt_payload),
        "input_assets": input_assets,
        "input_fingerprints": input_fingerprints,
        "output": output,
        "present_to_user": present_to_user,
        "plan": plan_relative,
        "plan_sha256": sha256_file(selected_plan_path),
        "profile_registry": registry_relative,
        "profile_registry_sha256": sha256_file(registry_path),
        "prompt_source": prompt_source,
        "constraints_sha256": sha256_text(
            json.dumps(
                {
                    "output_constraints": output_constraints,
                    "preserve": preserve,
                    "avoid": avoid,
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        ),
        "receipt": receipt,
    }
    if include_prompt:
        receipt_payload["prompt_payload"] = prompt_payload
        tool_request: dict[str, Any] = {"prompt": prompt_payload}
        if input_binding == "referenced_image_paths":
            tool_request["referenced_image_paths"] = [
                str((package / input_asset).resolve())
                for input_asset in input_assets
            ]
        elif input_binding == "num_last_images_to_include":
            tool_request["num_last_images_to_include"] = num_last_images_to_include
        receipt_payload["tool_request"] = tool_request
    return receipt_payload, prompt_payload, receipt_path


def write_receipt(receipt: dict[str, Any], receipt_path: Path) -> None:
    if receipt_path.exists() and receipt_path.is_symlink():
        raise ContractError(f"refusing to overwrite symlink receipt: {receipt_path}")
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    persisted = {
        key: value
        for key, value in receipt.items()
        if key not in {"prompt_payload", "tool_request"}
    }
    receipt_path.write_text(
        json.dumps(persisted, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a content package image-generation route and build the exact tool prompt."
        )
    )
    parser.add_argument("package", help="Path to one content package")
    parser.add_argument("--task", required=True, help="Task id from image-generation-plan.json")
    parser.add_argument(
        "--stage",
        required=True,
        choices=sorted(STAGE_KEYS),
        help="Preflight the internal reference stage or the final deliverable stage",
    )
    parser.add_argument(
        "--plan",
        help="Optional plan path; defaults to research/image-generation-plan.json",
    )
    parser.add_argument(
        "--include-prompt",
        action="store_true",
        help="Include the exact prompt payload in stdout only; receipts never store it",
    )
    parser.add_argument(
        "--write-receipt",
        action="store_true",
        help="Write the non-secret preflight receipt declared by the selected stage",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        receipt, _, receipt_path = build_request(
            Path(args.package),
            args.task,
            args.stage,
            plan_path=Path(args.plan) if args.plan else None,
            include_prompt=args.include_prompt,
        )
        if args.write_receipt:
            write_receipt(receipt, receipt_path)
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
    except ContractError as exc:
        print(f"[fail] {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
