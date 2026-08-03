#!/usr/bin/env python3
"""Fast Agent-first entry for company formatting and collaboration state.

The CLI keeps external orchestration small: status is read-only, build invokes
the pinned Chrome renderer, and Feishu commands only seal intents or verify
allowlisted receipts. MCP credentials and network calls stay in the Agent host;
this process never performs Feishu or WeChat writes.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tomllib
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

_TOOL_IMPORT_ROOT = Path(__file__).resolve().parent
if str(_TOOL_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(_TOOL_IMPORT_ROOT))

from locked_format_adapter import (  # noqa: E402
    FRONTMATTER_RE,
    YAML_KEY_RE,
    LockedFormatError,
    audit_locked_profile,
    MAX_MARKDOWN_BYTES,
    MAX_RENDERED_HTML_BYTES,
    MAX_TOTAL_IMAGE_BYTES,
    SUPPORTED_IMAGE_MIMES,
    canonical_json,
    markdown_blocks,
    parse_top_level_yaml,
    read_bounded,
    read_draft,
    render_locked_article,
    safe_image_path,
    sha256_bytes,
    sha256_file,
)

WorkflowError = LockedFormatError

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


TOOL_VERSION = "0.3.0"
SCHEMA_VERSION = 1
FEISHU_PROTOCOL_VERSION = "feishu-agent-mcp/v1"
FEISHU_MCP_SERVER_ID = "official-feishu-remote-mcp"
TOOL_ROOT = Path(__file__).resolve().parent
REPO_ROOT = TOOL_ROOT.parents[1]
JOURNAL_ROOT = REPO_ROOT / ".company-content-sync" / "journal"
PROFILE_PATH = TOOL_ROOT / "profile.json"
VALIDATOR = (
    REPO_ROOT
    / ".agents"
    / "skills"
    / "self-media-ops"
    / "scripts"
    / "validate_content_package.py"
)
WECHAT_PUBLISHER = REPO_ROOT / "微信公众号" / "tools" / "wechat_publish.py"
STATE_RELATIVE_PATH = Path("dist") / "content-sync" / "state.json"
BUILD_RELATIVE_PATH = Path("dist") / "content-sync" / "build.json"
HTML_RELATIVE_PATH = Path("dist") / "content-sync" / "article.html"
OPS_RELATIVE_PATH = Path("dist") / "content-sync" / "ops"
WECHAT_API_DELIVERY_MODE = "sealed_draft"
WECHAT_API_LAYOUT_PROFILE = "appsso-article-v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
QUALIFICATION_CONFIRMATIONS = (
    "layout_style_confirmed",
    "metadata_confirmed",
    "save_confirmed",
    "reopen_confirmed",
    "no_truncation_confirmed",
    "images_resolved_confirmed",
    "no_style_bypass_confirmed",
)
FEISHU_REMOTE_MCP_URL = "https://mcp.feishu.cn/mcp"
FEISHU_REMOTE_MCP_TOOLS = ("create-doc", "fetch-doc")
FEISHU_REMOTE_MCP_CREDENTIAL_ENV = "FEISHU_MCP_UAT"
FEISHU_REMOTE_MCP_HOST_ATTESTATION_ENV = "FEISHU_MCP_HOST_TOOLS_ATTESTED"
FEISHU_DEFAULT_PARENT_ID = "my_library"
FEISHU_DEFAULT_PARENT_KIND = "wiki_space"
FEISHU_REMOTE_MCP_SAFE_CONFIG_TEMPLATE = """[mcp_servers.feishu_docs]
url = "https://mcp.feishu.cn/mcp"
enabled = true
required = false
enabled_tools = ["create-doc", "fetch-doc"]
default_tools_approval_mode = "prompt"
startup_timeout_sec = 20
tool_timeout_sec = 120
http_headers = { "X-Lark-MCP-Allowed-Tools" = "create-doc,fetch-doc" }
env_http_headers = { "X-Lark-MCP-UAT" = "FEISHU_MCP_UAT" }
"""


def live_feishu_connector_available() -> bool:
    """Return true only after this host attests the exact loaded tool allowlist."""
    return bool(feishu_remote_mcp_report()["trusted_executor_available"])


def live_wechat_draft_adapter_available() -> bool:
    """Return true only after the existing WeChat publisher is safely bound here."""
    return False


def active_codex_config_path() -> Path:
    configured_home = os.environ.get("CODEX_HOME")
    codex_home = (
        Path(configured_home).expanduser()
        if configured_home
        else Path.home() / ".codex"
    )
    return codex_home / "config.toml"


def _exact_feishu_tool_allowlist(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == len(FEISHU_REMOTE_MCP_TOOLS)
        and all(isinstance(item, str) for item in value)
        and set(value) == set(FEISHU_REMOTE_MCP_TOOLS)
    )


def _exact_feishu_allowed_tools_header(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    tools = [item.strip() for item in value.split(",")]
    return len(tools) == len(FEISHU_REMOTE_MCP_TOOLS) and set(tools) == set(
        FEISHU_REMOTE_MCP_TOOLS
    )


def feishu_remote_mcp_report() -> dict[str, Any]:
    """Inspect only connector configuration shape and credential-key presence."""
    config_path = active_codex_config_path()
    config_present = False
    config_valid = False

    if config_path.is_file():
        try:
            raw = read_bounded(config_path, 2 * 1024 * 1024)
            config = tomllib.loads(raw.decode("utf-8"))
            servers = config.get("mcp_servers")
            server = servers.get("feishu_docs") if isinstance(servers, dict) else None
            if isinstance(server, dict):
                config_present = True
                http_headers = server.get("http_headers")
                env_http_headers = server.get("env_http_headers")
                header_names = (
                    {str(key).casefold() for key in http_headers}
                    if isinstance(http_headers, dict)
                    else set()
                )
                static_credentials_absent = not header_names.intersection(
                    {"x-lark-mcp-uat", "x-lark-mcp-tat"}
                )
                config_valid = (
                    server.get("url") == FEISHU_REMOTE_MCP_URL
                    and server.get("enabled", True) is True
                    and server.get("required", False) is False
                    and server.get("default_tools_approval_mode") == "prompt"
                    and _exact_feishu_tool_allowlist(server.get("enabled_tools"))
                    and isinstance(http_headers, dict)
                    and set(http_headers) == {"X-Lark-MCP-Allowed-Tools"}
                    and _exact_feishu_allowed_tools_header(
                        http_headers.get("X-Lark-MCP-Allowed-Tools")
                    )
                    and static_credentials_absent
                    and isinstance(env_http_headers, dict)
                    and set(env_http_headers) == {"X-Lark-MCP-UAT"}
                    and env_http_headers.get("X-Lark-MCP-UAT")
                    == FEISHU_REMOTE_MCP_CREDENTIAL_ENV
                    and "bearer_token_env_var" not in server
                )
        except (
            OSError,
            UnicodeDecodeError,
            tomllib.TOMLDecodeError,
            WorkflowError,
        ):
            config_valid = False

    # Membership checks the credential key only. The value is never read or reported.
    credential_env_present = FEISHU_REMOTE_MCP_CREDENTIAL_ENV in os.environ
    host_tools_attested = (
        os.environ.get(FEISHU_REMOTE_MCP_HOST_ATTESTATION_ENV)
        == ",".join(FEISHU_REMOTE_MCP_TOOLS)
    )
    trusted_executor_available = bool(
        config_valid and credential_env_present and host_tools_attested
    )
    return {
        "config_present": config_present,
        "config_valid": config_valid,
        "credential_env_present": credential_env_present,
        "restart_required_or_unknown": bool(
            config_valid and credential_env_present and not host_tools_attested
        ),
        "host_tools_attested": host_tools_attested,
        "trusted_executor_available": trusted_executor_available,
        "safe_config_template": FEISHU_REMOTE_MCP_SAFE_CONFIG_TEMPLATE,
    }


def connector_doctor_report() -> dict[str, Any]:
    connector = feishu_remote_mcp_report()
    return {
        "schema_version": SCHEMA_VERSION,
        "tool_version": TOOL_VERSION,
        "ok": bool(connector["config_valid"] and connector["credential_env_present"]),
        "connectors": {"feishu_remote_mcp": connector},
        "external_writes_performed": False,
    }


def normalized_warning_codes(value: Any) -> list[str] | None:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item for item in value
    ):
        return None
    return sorted(set(value))


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def read_publish(package: Path) -> dict[str, Any]:
    path = package / "publish.yml"
    if not path.is_file():
        return {}
    raw = read_bounded(path, 512 * 1024)
    try:
        return parse_top_level_yaml(raw.decode("utf-8"), str(path))
    except UnicodeDecodeError as exc:
        raise WorkflowError(f"{path} must be UTF-8") from exc


def load_json(path: Path, *, optional: bool = False) -> dict[str, Any]:
    if optional and not path.is_file():
        return {}
    try:
        value = json.loads(read_bounded(path, 2 * 1024 * 1024).decode("utf-8"))
    except FileNotFoundError:
        raise WorkflowError(f"missing required file: {path}")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorkflowError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise WorkflowError(f"JSON root must be an object: {path}")
    return value


def resolve_repo_path(relative: str) -> Path:
    candidate = (REPO_ROOT / relative).resolve()
    try:
        candidate.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise WorkflowError(f"profile path escapes the workspace: {relative}") from exc
    return candidate


def load_profile() -> tuple[dict[str, Any], str]:
    raw = read_bounded(PROFILE_PATH, 512 * 1024)
    try:
        profile = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorkflowError(f"invalid profile: {PROFILE_PATH}") from exc
    if not isinstance(profile, dict):
        raise WorkflowError("profile root must be an object")
    return profile, sha256_bytes(raw)


def doctor_report() -> dict[str, Any]:
    started = time.perf_counter()
    blockers: list[str] = []
    warnings: list[str] = []
    profile: dict[str, Any] = {}
    profile_sha256: str | None = None
    audit: dict[str, Any] = {}
    try:
        profile, profile_sha256 = load_profile()
        audit = audit_locked_profile(profile, REPO_ROOT)
    except (OSError, WorkflowError) as exc:
        blockers.append(str(exc))

    if not VALIDATOR.is_file():
        warnings.append("self-media content validator is missing")
    if not WECHAT_PUBLISHER.is_file():
        warnings.append("existing WeChat publisher is missing")
    node_path = shutil.which("node")
    if not node_path:
        blockers.append("Node.js is required for the locked extension renderer")

    verified = list(audit.get("verified_files", []))
    adapter_sha256 = audit.get("adapter_sha256")
    bridge_sha256 = audit.get("bridge_sha256")
    renderer_sha256 = audit.get("renderer_sha256")
    title_image_sha256 = audit.get("title_image_sha256")
    format_profile_sha256 = audit.get("format_profile_sha256")
    format_contract_sha256 = audit.get("format_contract_sha256")
    style_assertions_verified = bool(audit.get("style_assertions_verified"))
    style_version_verified = bool(audit.get("style_version_verified"))
    runtime_dependencies = dict(audit.get("runtime_dependencies", {}))
    markdown_parser_present = bool(runtime_dependencies)
    qualification_value = profile.get("qualification", {})
    qualification_issues: list[str] = []
    if isinstance(qualification_value, dict):
        qualification = qualification_value
    else:
        qualification = {}
        qualification_issues.append("qualification_record_invalid")
    scope_value = qualification.get("scope", {})
    evidence_value = qualification.get("evidence", {})
    if isinstance(scope_value, dict):
        scope = scope_value
    else:
        scope = {}
        qualification_issues.append("qualification_scope_invalid")
    if isinstance(evidence_value, dict):
        evidence = evidence_value
    else:
        evidence = {}
        qualification_issues.append("qualification_evidence_invalid")

    expected_scope = {
        "profile_id": profile.get("profile_id"),
        "format_contract_sha256": format_contract_sha256,
        "renderer_sha256": renderer_sha256,
        "delivery_mode": WECHAT_API_DELIVERY_MODE,
        "layout_profile": WECHAT_API_LAYOUT_PROFILE,
    }
    for field, expected in expected_scope.items():
        if scope.get(field) != expected:
            qualification_issues.append(f"qualification_{field}_mismatch")
    account_fingerprint = str(scope.get("wechat_account_fingerprint") or "").lower()
    if not SHA256_RE.fullmatch(account_fingerprint):
        qualification_issues.append("qualification_account_fingerprint_missing")

    evidence_id = evidence.get("record_id")
    if not isinstance(evidence_id, str) or not evidence_id.strip():
        qualification_issues.append("qualification_evidence_id_missing")
    evidence_sha256 = str(evidence.get("receipt_sha256") or "").lower()
    if not SHA256_RE.fullmatch(evidence_sha256):
        qualification_issues.append("qualification_evidence_hash_missing")
    qualified_at = evidence.get("qualified_at")
    try:
        parsed_qualified_at = datetime.fromisoformat(
            str(qualified_at).replace("Z", "+00:00")
        )
        if parsed_qualified_at.tzinfo is None:
            raise ValueError
    except (TypeError, ValueError):
        qualification_issues.append("qualification_timestamp_invalid")

    receipt_verified = False
    receipt_value = evidence.get("receipt_path")
    if not isinstance(receipt_value, str) or not receipt_value.strip():
        qualification_issues.append("qualification_receipt_path_missing")
    else:
        try:
            receipt_path = resolve_repo_path(receipt_value)
            receipt_raw = read_bounded(receipt_path, 2 * 1024 * 1024)
            if sha256_bytes(receipt_raw) != evidence_sha256:
                qualification_issues.append("qualification_receipt_hash_mismatch")
            receipt_data = json.loads(receipt_raw.decode("utf-8"))
            if not isinstance(receipt_data, dict):
                raise WorkflowError("qualification receipt root must be an object")
            expected_receipt = {
                **expected_scope,
                **{field: True for field in QUALIFICATION_CONFIRMATIONS},
                "wechat_account_fingerprint": account_fingerprint,
                "record_id": evidence_id,
                "qualified_at": qualified_at,
            }
            receipt_mismatches = [
                field
                for field, expected in expected_receipt.items()
                if (
                    field in QUALIFICATION_CONFIRMATIONS
                    and receipt_data.get(field) is not True
                )
                or (
                    field not in QUALIFICATION_CONFIRMATIONS
                    and receipt_data.get(field) != expected
                )
            ]
            if receipt_mismatches:
                qualification_issues.extend(
                    f"qualification_receipt_{field}_mismatch"
                    for field in receipt_mismatches
                )
            receipt_verified = (
                not receipt_mismatches and sha256_bytes(receipt_raw) == evidence_sha256
            )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, WorkflowError):
            qualification_issues.append("qualification_receipt_unreadable")

    for flag in (
        "local_fixture_qualified",
        "wechat_roundtrip_qualified",
        "production_qualified",
    ):
        if qualification.get(flag) is not True:
            qualification_issues.append(f"qualification_{flag}_false")
    production_qualified = not qualification_issues
    if not production_qualified:
        warnings.append(
            "exact account × format contract WeChat round-trip qualification is pending"
        )
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    feishu_executor_available = live_feishu_connector_available()
    wechat_adapter_available = live_wechat_draft_adapter_available()
    connectors = {"feishu_remote_mcp": feishu_remote_mcp_report()}
    return {
        "schema_version": SCHEMA_VERSION,
        "tool_version": TOOL_VERSION,
        "ok": not blockers,
        "workspace_root": str(REPO_ROOT),
        "runtime": {
            "python": sys.version.split()[0],
            "node_present": bool(node_path),
            "markdown_parser_present": markdown_parser_present,
            "locked_dependencies": runtime_dependencies,
        },
        "format": {
            "profile_id": profile.get("profile_id"),
            "profile_sha256": profile_sha256,
            "format_profile_sha256": format_profile_sha256,
            "adapter_sha256": adapter_sha256,
            "bridge_sha256": bridge_sha256,
            "renderer_sha256": renderer_sha256,
            "title_image_sha256": title_image_sha256,
            "format_contract_sha256": format_contract_sha256,
            "extension_version": profile.get("format_source", {}).get(
                "extension_version"
            ),
            "style_version": profile.get("format_source", {}).get("style_version"),
            "style_version_verified": style_version_verified,
            "style_assertions_verified": style_assertions_verified,
            "verified_files": verified,
        },
        "qualification": {
            "local_build_capable": not blockers,
            "local_fixture_qualified": bool(
                qualification.get("local_fixture_qualified", False)
            ),
            "wechat_roundtrip_qualified": bool(
                qualification.get("wechat_roundtrip_qualified", False)
            ),
            "production_qualified": production_qualified,
            "required_delivery_mode": scope.get("delivery_mode"),
            "required_layout_profile": scope.get("layout_profile"),
            "wechat_account_fingerprint": account_fingerprint or None,
            "evidence_id": evidence_id,
            "evidence_receipt_verified": receipt_verified,
            "binding_issues": sorted(set(qualification_issues)),
        },
        "capabilities": {
            "status": True,
            "local_build": not blockers,
            "feishu_protocol": True,
            "feishu_create_intent": True,
            "feishu_pull_intent": True,
            "feishu_connector_connected": feishu_executor_available,
            "feishu_trusted_dispatch_executor": feishu_executor_available,
            "feishu_safe_update": False,
            "feishu_pull": feishu_executor_available,
            "feishu_push": feishu_executor_available,
            "wechat_create_draft": wechat_adapter_available,
        },
        "connectors": connectors,
        "external_writes_performed": False,
        "blockers": blockers,
        "warnings": warnings,
        "elapsed_ms": elapsed_ms,
    }


def build_integrity(
    package: Path,
    build: dict[str, Any],
    draft_sha256: str,
    doctor: dict[str, Any],
) -> tuple[list[str], str | None]:
    if not build:
        return ["build_missing"], None

    format_state = doctor["format"]
    expected_fields = {
        "draft_sha256": draft_sha256,
        "profile_id": format_state.get("profile_id"),
        "format_profile_sha256": format_state.get("format_profile_sha256"),
        "adapter_sha256": format_state.get("adapter_sha256"),
        "bridge_sha256": format_state.get("bridge_sha256"),
        "renderer_sha256": format_state.get("renderer_sha256"),
        "title_image_sha256": format_state.get("title_image_sha256"),
        "format_contract_sha256": format_state.get("format_contract_sha256"),
        "style_version": format_state.get("style_version"),
        "html_path": HTML_RELATIVE_PATH.as_posix(),
    }
    issues = [
        f"build_{field}_mismatch"
        for field, expected in expected_fields.items()
        if build.get(field) != expected
    ]

    html_path = package / HTML_RELATIVE_PATH
    actual_html_sha256: str | None = None
    if not html_path.is_file():
        issues.append("build_html_missing")
    else:
        try:
            if html_path.stat().st_size > MAX_RENDERED_HTML_BYTES:
                issues.append("build_html_oversize")
            else:
                actual_html_sha256 = sha256_file(html_path)
                if build.get("html_sha256") != actual_html_sha256:
                    issues.append("build_html_hash_mismatch")
        except OSError:
            issues.append("build_html_unreadable")

    if actual_html_sha256:
        warning_codes = normalized_warning_codes(build.get("warning_codes"))
        if warning_codes is None:
            issues.append("build_warning_codes_invalid")
            warning_codes = []
        seal_material = {
            "draft_sha256": draft_sha256,
            "format_profile_sha256": format_state.get("format_profile_sha256"),
            "adapter_sha256": format_state.get("adapter_sha256"),
            "bridge_sha256": format_state.get("bridge_sha256"),
            "renderer_sha256": format_state.get("renderer_sha256"),
            "format_contract_sha256": format_state.get("format_contract_sha256"),
            "style_version": format_state.get("style_version"),
            "html_sha256": actual_html_sha256,
            "title_image_sha256": format_state.get("title_image_sha256"),
            "local_format_qualified": bool(build.get("local_format_qualified")),
            "warning_codes": warning_codes,
        }
        expected_seal = sha256_bytes(canonical_json(seal_material))
        if build.get("sealed_build_sha256") != expected_seal:
            issues.append("sealed_build_hash_mismatch")
    return sorted(set(issues)), actual_html_sha256


def current_feishu_preview_binding(
    package: Path,
    draft_sha256: str,
    doctor: dict[str, Any],
) -> dict[str, Any]:
    build = load_json(package / BUILD_RELATIVE_PATH, optional=True)
    issues, actual_html_sha256 = build_integrity(
        package, build, draft_sha256, doctor
    )
    if issues:
        raise WorkflowError(
            "Feishu online preview requires a fresh locked local build: "
            + ", ".join(issues)
        )
    if build.get("local_format_qualified") is not True:
        raise WorkflowError(
            "Feishu online preview requires local_format_qualified: true"
        )
    if actual_html_sha256 is None:
        raise WorkflowError("Feishu online preview HTML hash is unavailable")
    return {
        "delivery_surface": "feishu_online_document",
        "fidelity": "native_feishu_structure_with_locked_html_reference",
        "profile_id": required_string(build.get("profile_id"), "build.profile_id"),
        "build_path": BUILD_RELATIVE_PATH.as_posix(),
        "sealed_build_sha256": validated_sha256(
            build.get("sealed_build_sha256"), "build.sealed_build_sha256"
        ),
        "html_path": HTML_RELATIVE_PATH.as_posix(),
        "html_sha256": validated_sha256(actual_html_sha256, "build.html_sha256"),
    }


def resolve_package(value: str | None, cwd: Path | None = None) -> Path:
    current = (Path(value) if value else (cwd or Path.cwd())).resolve()
    if current.is_file():
        current = current.parent
    if value:
        package = current
    else:
        package = next(
            (
                candidate
                for candidate in [current, *current.parents]
                if (candidate / "draft.md").is_file()
            ),
            None,
        )
        if package is None:
            raise WorkflowError(
                "no content package found; pass a directory containing draft.md"
            )
    try:
        package.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise WorkflowError("content package must stay inside this workspace") from exc
    return package


PROTOCOL_PHASES = {
    "local_only",
    "push_prepared",
    "push_in_flight",
    "feishu_synced",
    "pull_prepared",
    "remote_dirty",
    "local_dirty",
    "pulled",
    "team_review_complete",
    "built",
    "sealed",
    "wechat_draft_created",
    "conflict",
    "result_unknown",
}


def json_document(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write(path, json_document(value))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validated_timestamp(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise WorkflowError(f"{field} must be an RFC3339 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise WorkflowError(f"{field} must be an RFC3339 timestamp") from exc
    if parsed.tzinfo is None:
        raise WorkflowError(f"{field} must include a timezone")
    return value


def required_string(value: Any, field: str, limit: int = 512) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise WorkflowError(f"{field} must be a non-empty bounded string")
    return value.strip()


def reject_unknown_keys(value: dict[str, Any], allowed: set[str], field: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise WorkflowError(
            f"{field} contains unsupported fields: {', '.join(unknown)}"
        )


def validated_sha256(value: Any, field: str) -> str:
    normalized = str(value or "").lower()
    if not SHA256_RE.fullmatch(normalized):
        raise WorkflowError(f"{field} must be a lowercase SHA-256")
    return normalized


def validated_opaque_id(value: Any, field: str) -> str:
    identifier = required_string(value, field, 256)
    if not re.fullmatch(r"[A-Za-z0-9_-]{4,256}", identifier):
        raise WorkflowError(f"{field} contains unsupported characters")
    return identifier


def validated_feishu_document_url(value: Any, field: str) -> str:
    document_url = required_string(value, field, 2048)
    try:
        parsed = urlsplit(document_url)
        port = parsed.port
    except ValueError as exc:
        raise WorkflowError(
            f"{field} must be a clean HTTPS Feishu docx or wiki URL"
        ) from exc
    hostname = (parsed.hostname or "").casefold()
    if (
        parsed.scheme != "https"
        or parsed.username is not None
        or parsed.password is not None
        or port not in {None, 443}
        or parsed.query
        or parsed.fragment
        or not hostname.endswith(".feishu.cn")
        or not re.fullmatch(r"/(?:docx|wiki)/[A-Za-z0-9_-]{4,256}/?", parsed.path)
    ):
        raise WorkflowError(
            f"{field} must be a clean HTTPS Feishu docx or wiki URL"
        )
    return document_url


def normalize_collaboration_text(value: str) -> str:
    normalized = unicodedata.normalize(
        "NFC", value.replace("\r\n", "\n").replace("\r", "\n")
    )
    if not normalized:
        return ""
    return normalized.rstrip("\n") + "\n"


def collaboration_assets(body: str, package: Path) -> list[dict[str, Any]]:
    try:
        from markdown_it import MarkdownIt
    except ImportError as exc:
        raise WorkflowError("markdown-it-py is required for Feishu intents") from exc

    tokens = MarkdownIt("commonmark", {"html": True}).enable("table").parse(body)
    assets: list[dict[str, Any]] = []
    total_bytes = 0
    for token in tokens:
        for child in token.children or []:
            if child.type != "image":
                continue
            source = child.attrGet("src") or ""
            image_path = safe_image_path(package, source)
            size = image_path.stat().st_size
            total_bytes += size
            if total_bytes > MAX_TOTAL_IMAGE_BYTES:
                raise WorkflowError(
                    f"article images exceed {MAX_TOTAL_IMAGE_BYTES} bytes"
                )
            assets.append(
                {
                    "order": len(assets) + 1,
                    "path": image_path.relative_to(package.resolve()).as_posix(),
                    "sha256": sha256_file(image_path),
                    "mime": SUPPORTED_IMAGE_MIMES[image_path.suffix.lower()],
                    "bytes": size,
                    "alt": unicodedata.normalize("NFC", child.content or ""),
                }
            )
    return assets


def collaboration_snapshot(
    package: Path,
    title_value: Any,
    body: str,
    *,
    draft_raw: bytes | None = None,
    validate_markdown: bool = False,
) -> dict[str, Any]:
    title = unicodedata.normalize(
        "NFC", required_string(title_value, "draft title", 500)
    )
    normalized_body = normalize_collaboration_text(body)
    if normalized_body.lstrip("\ufeff").startswith("---\n"):
        raise WorkflowError("Feishu collaboration body must not contain frontmatter")
    if validate_markdown:
        markdown_blocks(normalized_body, package, title, embed_images=False)
    assets = collaboration_assets(normalized_body, package)
    body_bytes = normalized_body.encode("utf-8")
    assets_bytes = canonical_json(assets)
    body_sha256 = sha256_bytes(body_bytes)
    assets_sha256 = sha256_bytes(assets_bytes)
    payload_sha256 = sha256_bytes(
        canonical_json(
            {
                "schema_version": 1,
                "title": title,
                "body_sha256": body_sha256,
                "assets_sha256": assets_sha256,
            }
        )
    )
    return {
        "title": title,
        "body": normalized_body,
        "body_bytes": body_bytes,
        "body_sha256": body_sha256,
        "assets": assets,
        "assets_bytes": assets_bytes,
        "assets_sha256": assets_sha256,
        "asset_count": len(assets),
        "payload_sha256": payload_sha256,
        "draft_sha256": sha256_bytes(draft_raw) if draft_raw is not None else None,
    }


def default_sync_state() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "protocol": FEISHU_PROTOCOL_VERSION,
        "provider": "feishu",
        "state_sequence": 0,
        "phase": "local_only",
        "tenant_fingerprint": None,
        "parent_fingerprint": None,
        "document_id": None,
        "document_fingerprint": None,
        "document_url": None,
        "base_sha256": None,
        "base_body_sha256": None,
        "base_assets_sha256": None,
        "remote_sha256": None,
        "remote_revision": None,
        "last_synced_at": None,
        "pending": None,
        "dispatch": None,
        "candidate": None,
        "last_receipt": None,
        "conflict": None,
        "result_unknown": None,
    }


def journal_file(package: Path) -> Path:
    package_relative = package.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    package_key = sha256_bytes(package_relative.encode("utf-8"))[:32]
    return JOURNAL_ROOT / package_key / "state.json"


def dispatch_claim_file(package: Path, operation_id: str) -> Path:
    validated_opaque_id(operation_id, "operation_id")
    return journal_file(package).parent / "claims" / f"{operation_id}.json"


def load_dispatch_claim(
    package: Path, pending: dict[str, Any], *, optional: bool
) -> dict[str, Any]:
    operation_id = required_string(
        pending.get("operation_id"), "pending.operation_id", 128
    )
    path = dispatch_claim_file(package, operation_id)
    if optional and not path.is_file():
        return {}
    claim = load_json(path)
    if claim.get("schema_version") != SCHEMA_VERSION:
        raise WorkflowError("dispatch claim schema_version mismatch")
    if claim.get("protocol") != FEISHU_PROTOCOL_VERSION:
        raise WorkflowError("dispatch claim protocol mismatch")
    if claim.get("operation_id") != operation_id:
        raise WorkflowError("dispatch claim operation mismatch")
    if claim.get("intent_sha256") != pending.get("intent_sha256"):
        raise WorkflowError("dispatch claim intent mismatch")
    if claim.get("idempotency_key") != pending.get("idempotency_key"):
        raise WorkflowError("dispatch claim idempotency mismatch")
    validated_sha256(
        claim.get("authorization_scope_sha256"),
        "dispatch.authorization_scope_sha256",
    )
    validated_timestamp(claim.get("claimed_at"), "dispatch.claimed_at")
    return claim


def overlay_dispatch_claim(package: Path, state: dict[str, Any]) -> dict[str, Any]:
    if not state or state.get("protocol") != FEISHU_PROTOCOL_VERSION:
        return state
    pending = state.get("pending")
    if not isinstance(pending, dict) or pending.get("kind") != "push_create":
        return state
    if state.get("phase") not in {
        "push_prepared",
        "push_in_flight",
        "result_unknown",
    }:
        return state
    claim = load_dispatch_claim(package, pending, optional=True)
    if not claim:
        if state.get("phase") == "push_in_flight":
            raise WorkflowError("push_in_flight state is missing its dispatch claim")
        return state
    if state.get("phase") == "push_prepared":
        recovered = dict(state)
        recovered["phase"] = "push_in_flight"
        recovered["dispatch"] = claim
        recovered["_claim_recovered"] = True
        validate_sync_state(recovered, "dispatch claim overlay")
        return recovered
    if state.get("phase") == "push_in_flight" and state.get("dispatch") != claim:
        raise WorkflowError("push_in_flight state and dispatch claim disagree")
    return state


def load_journal_state(package: Path) -> dict[str, Any]:
    path = journal_file(package)
    if not path.is_file():
        return {}
    wrapper = load_json(path)
    package_relative = package.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    if wrapper.get("schema_version") != SCHEMA_VERSION:
        raise WorkflowError("operation journal schema_version is unsupported")
    if wrapper.get("protocol") != FEISHU_PROTOCOL_VERSION:
        raise WorkflowError("operation journal protocol is unsupported")
    if wrapper.get("package_path") != package_relative:
        raise WorkflowError("operation journal package binding mismatch")
    state = wrapper.get("state")
    if not isinstance(state, dict):
        raise WorkflowError("operation journal state must be an object")
    return state


def validate_sync_state(state: dict[str, Any], source: str) -> None:
    if not state:
        return
    phase = state.get("phase")
    if not isinstance(phase, str) or phase not in PROTOCOL_PHASES:
        raise WorkflowError(f"{source} has an unsupported or missing phase")
    protocol = state.get("protocol")
    if protocol is None:
        if phase not in {"local_only", "conflict", "result_unknown"}:
            raise WorkflowError(
                f"{source} is legacy_untrusted and cannot prove Feishu lineage"
            )
        return
    if protocol != FEISHU_PROTOCOL_VERSION:
        raise WorkflowError(f"{source} uses an unsupported Feishu protocol")
    if state.get("schema_version") != SCHEMA_VERSION:
        raise WorkflowError(f"{source} schema_version is unsupported")
    if state.get("provider") != "feishu":
        raise WorkflowError(f"{source} provider must be feishu")
    sequence = state.get("state_sequence")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0:
        raise WorkflowError(f"{source} state_sequence must be a non-negative integer")
    pending = state.get("pending")
    if pending is not None and not isinstance(pending, dict):
        raise WorkflowError(f"{source} pending must be an object or null")
    if phase in {
        "push_prepared",
        "push_in_flight",
        "pull_prepared",
        "result_unknown",
    }:
        if not isinstance(pending, dict):
            raise WorkflowError(f"{source} phase {phase} requires pending")
        required_string(pending.get("operation_id"), "pending.operation_id", 128)
        if pending.get("kind") not in {"push_create", "pull_read"}:
            raise WorkflowError(f"{source} pending.kind is unsupported")
        if (
            phase in {"push_prepared", "push_in_flight"}
            and pending.get("kind") != "push_create"
        ):
            raise WorkflowError(
                f"{source} push phase requires pending.kind push_create"
            )
        if phase == "pull_prepared" and pending.get("kind") != "pull_read":
            raise WorkflowError(f"{source} pull phase requires pending.kind pull_read")
        validated_sha256(pending.get("idempotency_key"), "pending.idempotency_key")
        validated_sha256(pending.get("intent_sha256"), "pending.intent_sha256")
        required_string(pending.get("intent_path"), "pending.intent_path", 512)
        if pending.get("kind") == "push_create":
            validated_sha256(
                pending.get("authorization_scope_sha256"),
                "pending.authorization_scope_sha256",
            )
            if pending.get("sealed_build_sha256") is not None:
                validated_sha256(
                    pending.get("sealed_build_sha256"),
                    "pending.sealed_build_sha256",
                )
            if pending.get("html_sha256") is not None:
                validated_sha256(pending.get("html_sha256"), "pending.html_sha256")
    if phase == "push_in_flight":
        dispatch = state.get("dispatch")
        if not isinstance(dispatch, dict):
            raise WorkflowError(f"{source} push_in_flight requires dispatch")
        dispatch_scope = validated_sha256(
            dispatch.get("authorization_scope_sha256"),
            "dispatch.authorization_scope_sha256",
        )
        if dispatch_scope != pending.get("authorization_scope_sha256"):
            raise WorkflowError(f"{source} dispatch authorization scope mismatch")
        validated_timestamp(dispatch.get("claimed_at"), "dispatch.claimed_at")
    synchronized_phases = {
        "feishu_synced",
        "pull_prepared",
        "remote_dirty",
        "local_dirty",
        "pulled",
        "team_review_complete",
        "built",
        "sealed",
        "wechat_draft_created",
        "conflict",
    }
    if phase in synchronized_phases:
        validated_sha256(state.get("tenant_fingerprint"), "state.tenant_fingerprint")
        validated_opaque_id(state.get("document_id"), "state.document_id")
        if state.get("document_url") is not None:
            validated_feishu_document_url(
                state.get("document_url"), "state.document_url"
            )
        validated_sha256(state.get("base_sha256"), "state.base_sha256")
        required_string(state.get("remote_revision"), "state.remote_revision", 512)
    if phase == "remote_dirty" and not isinstance(state.get("candidate"), dict):
        raise WorkflowError(f"{source} remote_dirty phase requires candidate")
    if (
        phase == "conflict"
        and protocol is not None
        and not isinstance(state.get("conflict"), dict)
    ):
        raise WorkflowError(f"{source} conflict phase requires conflict details")
    if (
        phase == "result_unknown"
        and protocol is not None
        and not isinstance(state.get("result_unknown"), dict)
    ):
        raise WorkflowError(f"{source} result_unknown phase requires details")


def load_sync_state(package: Path) -> dict[str, Any]:
    state_path = package / STATE_RELATIVE_PATH
    file_state = load_json(state_path) if state_path.is_file() else {}
    journal_state = load_journal_state(package)
    validate_sync_state(file_state, "state.json")
    validate_sync_state(journal_state, "operation journal")
    if not file_state and not journal_state:
        return {}
    if not journal_state:
        if file_state.get("protocol") is not None:
            raise WorkflowError(
                "protocol state exists without its write-ahead operation journal; "
                "treat the remote result as unknown and reconcile before continuing"
            )
        selected_copy = dict(file_state)
    elif not file_state or file_state.get("protocol") is None:
        selected_copy = dict(journal_state)
        selected_copy["_recovered_from_journal"] = True
    else:
        file_sequence = int(file_state.get("state_sequence", 0))
        journal_sequence = int(journal_state.get("state_sequence", 0))
        if file_sequence == journal_sequence:
            if canonical_json(file_state) != canonical_json(journal_state):
                raise WorkflowError("state.json and operation journal disagree")
            selected_copy = dict(file_state)
        else:
            if file_sequence > journal_sequence:
                raise WorkflowError(
                    "state.json is newer than the write-ahead operation journal"
                )
            selected_copy = dict(journal_state)
            selected_copy["_recovered_from_journal"] = True
    return overlay_dispatch_claim(package, selected_copy)


def write_sync_state(package: Path, state: dict[str, Any]) -> None:
    existing = load_sync_state(package)
    persisted = {key: value for key, value in state.items() if not key.startswith("_")}
    persisted["schema_version"] = SCHEMA_VERSION
    persisted["protocol"] = FEISHU_PROTOCOL_VERSION
    persisted["provider"] = "feishu"
    proposed_sequence = persisted.get("state_sequence", 0)
    existing_sequence = existing.get("state_sequence", 0)
    for sequence in (proposed_sequence, existing_sequence):
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0:
            raise WorkflowError("state_sequence is invalid")
    if proposed_sequence != existing_sequence:
        raise WorkflowError("stale sync state write rejected")
    persisted["state_sequence"] = existing_sequence + 1
    package_relative = package.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    journal = {
        "schema_version": SCHEMA_VERSION,
        "protocol": FEISHU_PROTOCOL_VERSION,
        "package_path": package_relative,
        "state": persisted,
    }
    atomic_write_json(journal_file(package), journal)
    atomic_write_json(package / STATE_RELATIVE_PATH, persisted)
    state.clear()
    state.update(persisted)


def package_relative_path(package: Path, path: Path) -> str:
    return path.resolve().relative_to(package.resolve()).as_posix()


def operation_directory(package: Path, operation_id: str) -> Path:
    validated_opaque_id(operation_id, "operation_id")
    candidate = (package / OPS_RELATIVE_PATH / operation_id).resolve()
    candidate.relative_to((package / OPS_RELATIVE_PATH).resolve())
    return candidate


def resolve_operation_file(
    package: Path,
    operation_id: str,
    value: Any,
    field: str,
) -> Path:
    relative = required_string(value, field, 512)
    candidate_value = Path(relative)
    candidate = (
        candidate_value.resolve()
        if candidate_value.is_absolute()
        else (package / candidate_value).resolve()
    )
    try:
        candidate.relative_to(operation_directory(package, operation_id))
    except ValueError as exc:
        raise WorkflowError(
            f"{field} must stay inside its operation directory"
        ) from exc
    return candidate


def load_pending_intent(
    package: Path, state: dict[str, Any]
) -> tuple[dict[str, Any], Path, str]:
    pending = state.get("pending")
    if not isinstance(pending, dict):
        raise WorkflowError("no pending Feishu operation")
    operation_id = required_string(
        pending.get("operation_id"), "pending.operation_id", 128
    )
    intent_path = resolve_operation_file(
        package, operation_id, pending.get("intent_path"), "pending.intent_path"
    )
    actual_sha256 = sha256_file(intent_path)
    expected_sha256 = validated_sha256(
        pending.get("intent_sha256"), "pending.intent_sha256"
    )
    if actual_sha256 != expected_sha256:
        raise WorkflowError("pending Feishu intent hash mismatch")
    intent = load_json(intent_path)
    if intent.get("operation_id") != operation_id:
        raise WorkflowError("pending Feishu intent operation mismatch")
    if intent.get("protocol") != FEISHU_PROTOCOL_VERSION:
        raise WorkflowError("pending Feishu intent protocol mismatch")
    if intent.get("idempotency_key") != pending.get("idempotency_key"):
        raise WorkflowError("pending Feishu intent idempotency mismatch")
    return intent, intent_path, actual_sha256


def run_content_validator(package: Path) -> None:
    if not VALIDATOR.is_file():
        raise WorkflowError("self-media content validator is unavailable")
    process = subprocess.run(
        [sys.executable, str(VALIDATOR), str(package)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )
    if process.returncode != 0:
        raise WorkflowError(
            "content package validation failed; run the self-media validator for details"
        )


def prepared_operation_report(
    package: Path,
    intent: dict[str, Any],
    intent_path: Path,
    intent_sha256: str,
    *,
    replayed: bool,
    started: float,
) -> dict[str, Any]:
    content = intent.get("content", {})
    return {
        "schema_version": SCHEMA_VERSION,
        "tool_version": TOOL_VERSION,
        "ok": True,
        "protocol": FEISHU_PROTOCOL_VERSION,
        "operation_id": intent.get("operation_id"),
        "operation": intent.get("operation"),
        "idempotency_key": intent.get("idempotency_key"),
        "intent_path": package_relative_path(package, intent_path),
        "intent_sha256": intent_sha256,
        "receipt_template_path": intent.get("receipt_template_path"),
        "authorization_scope_sha256": intent.get("authorization_scope_sha256"),
        "payload_sha256": content.get(
            "payload_sha256", content.get("local_payload_sha256")
        ),
        "asset_count": content.get("asset_count", content.get("local_asset_count", 0)),
        "preview": content.get("preview"),
        "replayed": replayed,
        "external_writes_performed": False,
        "authorization_required_for_execution": intent.get("operation")
        == "push_create",
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
    }


def validate_push_operation_artifacts(
    package: Path,
    intent: dict[str, Any],
    intent_sha256: str,
    snapshot: dict[str, Any],
    preview_binding: dict[str, Any],
) -> None:
    operation_id = validated_opaque_id(
        intent.get("operation_id"), "intent.operation_id"
    )
    content = intent.get("content")
    if not isinstance(content, dict):
        raise WorkflowError("Feishu push intent content is missing")
    payload_path = resolve_operation_file(
        package, operation_id, content.get("payload_path"), "intent payload_path"
    )
    payload_raw = read_bounded(payload_path, MAX_MARKDOWN_BYTES)
    if sha256_bytes(payload_raw) != content.get("body_sha256"):
        raise WorkflowError("Feishu push payload body hash mismatch")
    if payload_raw != snapshot.get("body_bytes"):
        raise WorkflowError("Feishu push payload differs from the current draft")
    if content.get("preview") != preview_binding:
        raise WorkflowError("Feishu preview build binding differs from the current build")
    assets_path = resolve_operation_file(
        package, operation_id, content.get("assets_path"), "intent assets_path"
    )
    assets_raw = read_bounded(assets_path, 2 * 1024 * 1024)
    if sha256_bytes(assets_raw) != content.get("assets_sha256"):
        raise WorkflowError("Feishu push assets hash mismatch")
    if assets_raw != snapshot.get("assets_bytes"):
        raise WorkflowError("Feishu push assets differ from the current draft")
    try:
        assets = json.loads(assets_raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorkflowError("Feishu push assets must be valid UTF-8 JSON") from exc
    if not isinstance(assets, list) or len(assets) != content.get("asset_count"):
        raise WorkflowError("Feishu push asset count mismatch")
    receipt_template_path = resolve_operation_file(
        package,
        operation_id,
        intent.get("receipt_template_path"),
        "intent receipt_template_path",
    )
    receipt_template = load_json(receipt_template_path)
    if receipt_template.get("intent_sha256") != intent_sha256:
        raise WorkflowError("Feishu receipt template intent hash mismatch")
    if receipt_template.get("operation_id") != operation_id:
        raise WorkflowError("Feishu receipt template operation mismatch")
    if receipt_template.get("protocol") != FEISHU_PROTOCOL_VERSION:
        raise WorkflowError("Feishu receipt template protocol mismatch")


def feishu_prepare_push_report(
    package_value: str | None,
    tenant_fingerprint: str,
    parent_id: str | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    package = resolve_package(package_value)
    doctor = doctor_report()
    if not doctor["ok"]:
        raise WorkflowError(
            "doctor failed: " + "; ".join(str(item) for item in doctor["blockers"])
        )
    metadata, body, draft_raw = read_draft(package / "draft.md")
    publish = read_publish(package)
    publish_path = package / "publish.yml"
    if not publish_path.is_file():
        raise WorkflowError("Feishu create requires publish.yml")
    publish_sha256 = sha256_file(publish_path)
    if metadata.get("status") != "ready":
        raise WorkflowError("Feishu create requires draft status ready")
    if publish.get("project_adapter") != "appsso":
        raise WorkflowError("Feishu create requires project_adapter: appsso")
    tenant = validated_sha256(tenant_fingerprint, "tenant_fingerprint")
    parent = validated_opaque_id(
        parent_id or FEISHU_DEFAULT_PARENT_ID,
        "parent_id",
    )
    run_content_validator(package)
    snapshot = collaboration_snapshot(
        package,
        metadata.get("title"),
        body,
        draft_raw=draft_raw,
        validate_markdown=True,
    )
    preview_binding = current_feishu_preview_binding(
        package, str(snapshot["draft_sha256"]), doctor
    )
    profile, _profile_sha256 = load_profile()
    classification = required_string(
        profile.get("classification"), "profile.classification", 32
    )
    package_path = package.relative_to(REPO_ROOT.resolve()).as_posix()
    parent_fingerprint = sha256_bytes(parent.encode("utf-8"))
    semantic_intent = {
        "protocol": FEISHU_PROTOCOL_VERSION,
        "operation": "push_create",
        "package_path": package_path,
        "classification": classification,
        "tenant_fingerprint": tenant,
        "parent_fingerprint": parent_fingerprint,
        "draft_sha256": snapshot["draft_sha256"],
        "publish_sha256": publish_sha256,
        "payload_sha256": snapshot["payload_sha256"],
        "body_sha256": snapshot["body_sha256"],
        "assets_sha256": snapshot["assets_sha256"],
        "asset_count": snapshot["asset_count"],
        "sealed_build_sha256": preview_binding["sealed_build_sha256"],
        "html_sha256": preview_binding["html_sha256"],
    }
    idempotency_key = sha256_bytes(canonical_json(semantic_intent))
    operation_id = f"feishu-create-{idempotency_key[:24]}"
    state = load_sync_state(package)
    recovering_prepared = False
    if state.get("phase") == "push_prepared":
        pending = state.get("pending") or {}
        if pending.get("idempotency_key") != idempotency_key:
            raise WorkflowError(
                "a different Feishu operation is pending; inspect it before replacing"
            )
        pending_intent_path = resolve_operation_file(
            package,
            operation_id,
            pending.get("intent_path"),
            "pending.intent_path",
        )
        if pending_intent_path.is_file():
            try:
                existing, existing_path, existing_sha = load_pending_intent(
                    package, state
                )
                validate_push_operation_artifacts(
                    package, existing, existing_sha, snapshot, preview_binding
                )
            except (OSError, UnicodeDecodeError, json.JSONDecodeError, WorkflowError):
                recovering_prepared = True
            else:
                return prepared_operation_report(
                    package,
                    existing,
                    existing_path,
                    existing_sha,
                    replayed=True,
                    started=started,
                )
        else:
            recovering_prepared = True
    if (
        state
        and not recovering_prepared
        and state.get("phase") not in {None, "local_only"}
    ):
        raise WorkflowError(
            f"Feishu create is unavailable from phase {state.get('phase')}"
        )

    operation_dir = operation_directory(package, operation_id)
    body_path = operation_dir / "payload.md"
    assets_path = operation_dir / "assets.json"
    intent_path = operation_dir / "intent.json"
    atomic_write(body_path, snapshot["body_bytes"])
    atomic_write(assets_path, snapshot["assets_bytes"])
    authorization_material = {
        **semantic_intent,
        "operation_id": operation_id,
        "idempotency_key": idempotency_key,
    }
    authorization_scope_sha256 = sha256_bytes(canonical_json(authorization_material))
    intent = {
        "schema_version": SCHEMA_VERSION,
        "protocol": FEISHU_PROTOCOL_VERSION,
        "operation_id": operation_id,
        "operation": "push_create",
        "idempotency_key": idempotency_key,
        "prepared_at": utc_now(),
        "package_path": package_path,
        "classification": classification,
        "authorization_scope_sha256": authorization_scope_sha256,
        "target": {
            "mode": "create",
            "tenant_fingerprint": tenant,
            "parent_id": parent,
            "parent_kind": (
                FEISHU_DEFAULT_PARENT_KIND
                if parent == FEISHU_DEFAULT_PARENT_ID
                else "opaque_parent"
            ),
            "parent_fingerprint": parent_fingerprint,
        },
        "content": {
            "title": snapshot["title"],
            "draft_sha256": snapshot["draft_sha256"],
            "publish_sha256": publish_sha256,
            "payload_path": package_relative_path(package, body_path),
            "payload_sha256": snapshot["payload_sha256"],
            "body_sha256": snapshot["body_sha256"],
            "assets_path": package_relative_path(package, assets_path),
            "assets_sha256": snapshot["assets_sha256"],
            "asset_count": snapshot["asset_count"],
            "preview": preview_binding,
        },
        "connector_contract": {
            "provider": "feishu",
            "server_id": FEISHU_MCP_SERVER_ID,
            "write_tool": "create-doc",
            "write_target_parameter": (
                "wiki_space"
                if parent == FEISHU_DEFAULT_PARENT_ID
                else "parent_id"
            ),
            "read_tool": "fetch-doc",
            "readback_required": True,
            "automatic_retry_on_ambiguous_result": False,
        },
        "access_contract": {
            "tenant_must_match": True,
            "acl_must_be_verified": True,
            "public_access_must_be_false": True,
            "external_sharing_must_be_false": True,
        },
    }
    receipt_template_path = operation_dir / "receipt-template.json"
    readback_path = operation_dir / "readback.md"
    intent["receipt_template_path"] = package_relative_path(
        package, receipt_template_path
    )
    receipt_template = {
        "schema_version": SCHEMA_VERSION,
        "protocol": FEISHU_PROTOCOL_VERSION,
        "provider": "feishu",
        "operation": "push_create",
        "operation_id": operation_id,
        "intent_sha256": None,
        "idempotency_key": idempotency_key,
        "authorization_scope_sha256": authorization_scope_sha256,
        "outcome": None,
        "write_performed": None,
        "completed_at": None,
        "mcp": {
            "server_id": FEISHU_MCP_SERVER_ID,
            "write_tool": "create-doc",
            "write_call_id": None,
            "write_result_is_error": None,
            "write_response_sha256": None,
            "read_tool": "fetch-doc",
            "read_call_id": None,
            "read_result_is_error": None,
            "read_response_sha256": None,
        },
        "access": {
            "tenant_fingerprint": tenant,
            "parent_fingerprint": parent_fingerprint,
            "acl_verified": None,
            "public_access": None,
            "external_shared": None,
        },
        "observed": {
            "document_id": None,
            "document_url": None,
            "revision": None,
            "title": snapshot["title"],
            "body_path": package_relative_path(package, readback_path),
            "body_sha256": None,
            "asset_mappings": [
                {
                    "order": item["order"],
                    "source_sha256": item["sha256"],
                    "remote_token": None,
                    "resolved": None,
                }
                for item in snapshot["assets"]
            ],
        },
    }
    atomic_write_json(intent_path, intent)
    intent_sha256 = sha256_file(intent_path)
    receipt_template["intent_sha256"] = intent_sha256
    atomic_write_json(receipt_template_path, receipt_template)
    new_state = default_sync_state()
    new_state["state_sequence"] = int(state.get("state_sequence", 0))
    new_state.update(
        {
            "phase": "push_prepared",
            "pending": {
                "operation_id": operation_id,
                "kind": "push_create",
                "idempotency_key": idempotency_key,
                "intent_path": package_relative_path(package, intent_path),
                "intent_sha256": intent_sha256,
                "payload_sha256": snapshot["payload_sha256"],
                "draft_sha256": snapshot["draft_sha256"],
                "publish_sha256": publish_sha256,
                "sealed_build_sha256": preview_binding["sealed_build_sha256"],
                "html_sha256": preview_binding["html_sha256"],
                "authorization_scope_sha256": authorization_scope_sha256,
                "prepared_at": intent["prepared_at"],
            },
        }
    )
    write_sync_state(package, new_state)
    return prepared_operation_report(
        package,
        intent,
        intent_path,
        intent_sha256,
        replayed=False,
        started=started,
    )


def feishu_begin_push_report(
    package_value: str | None,
    operation_id_value: str,
    authorization_scope_value: str,
) -> dict[str, Any]:
    started = time.perf_counter()
    package = resolve_package(package_value)
    operation_id = validated_opaque_id(operation_id_value, "operation_id")
    authorization_scope_sha256 = validated_sha256(
        authorization_scope_value, "authorization_scope_sha256"
    )
    if not live_feishu_connector_available():
        raise WorkflowError(
            "trusted one-shot Feishu executor is unavailable; dispatch claim was not created"
        )
    state = load_sync_state(package)
    if state.get("phase") == "push_in_flight":
        raise WorkflowError(
            "Feishu create dispatch is already claimed; reconcile it instead of retrying"
        )
    if state.get("phase") != "push_prepared":
        raise WorkflowError("Feishu begin requires phase push_prepared")
    pending = state.get("pending") or {}
    if pending.get("operation_id") != operation_id:
        raise WorkflowError("Feishu begin operation_id mismatch")
    if pending.get("authorization_scope_sha256") != authorization_scope_sha256:
        raise WorkflowError("Feishu begin authorization scope mismatch")
    intent, intent_path, intent_sha256 = load_pending_intent(package, state)
    if intent.get("authorization_scope_sha256") != authorization_scope_sha256:
        raise WorkflowError("Feishu intent authorization scope mismatch")
    doctor = doctor_report()
    if not doctor["ok"]:
        raise WorkflowError(
            "doctor failed: " + "; ".join(str(item) for item in doctor["blockers"])
        )
    metadata, body, draft_raw = read_draft(package / "draft.md")
    publish = read_publish(package)
    publish_path = package / "publish.yml"
    if metadata.get("status") != "ready":
        raise WorkflowError("Feishu begin requires draft status ready")
    if publish.get("project_adapter") != "appsso":
        raise WorkflowError("Feishu begin requires project_adapter: appsso")
    if not publish_path.is_file():
        raise WorkflowError("Feishu begin requires publish.yml")
    run_content_validator(package)
    snapshot = collaboration_snapshot(
        package,
        metadata.get("title"),
        body,
        draft_raw=draft_raw,
        validate_markdown=True,
    )
    preview_binding = current_feishu_preview_binding(
        package, str(snapshot["draft_sha256"]), doctor
    )
    expected_content = intent.get("content") or {}
    current_values = {
        "draft_sha256": snapshot["draft_sha256"],
        "publish_sha256": sha256_file(publish_path),
        "payload_sha256": snapshot["payload_sha256"],
        "body_sha256": snapshot["body_sha256"],
        "assets_sha256": snapshot["assets_sha256"],
        "asset_count": snapshot["asset_count"],
    }
    mismatches = [
        field
        for field, actual in current_values.items()
        if expected_content.get(field) != actual
    ]
    if expected_content.get("preview") != preview_binding:
        mismatches.append("preview")
    if mismatches:
        raise WorkflowError(
            "Feishu intent is stale at dispatch boundary: " + ", ".join(mismatches)
        )
    validate_push_operation_artifacts(
        package, intent, intent_sha256, snapshot, preview_binding
    )
    claimed_at = utc_now()
    claim = {
        "schema_version": SCHEMA_VERSION,
        "protocol": FEISHU_PROTOCOL_VERSION,
        "operation_id": operation_id,
        "intent_sha256": intent_sha256,
        "idempotency_key": pending.get("idempotency_key"),
        "authorization_scope_sha256": authorization_scope_sha256,
        "claimed_at": claimed_at,
    }
    claim_path = dispatch_claim_file(package, operation_id)
    claim_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with claim_path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(json_document(claim).decode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise WorkflowError(
            "Feishu create dispatch was already claimed; reconcile before retry"
        ) from exc
    state["phase"] = "push_in_flight"
    state["dispatch"] = claim
    state["result_unknown"] = None
    write_sync_state(package, state)
    return {
        "schema_version": SCHEMA_VERSION,
        "tool_version": TOOL_VERSION,
        "ok": True,
        "phase": "push_in_flight",
        "operation_id": operation_id,
        "intent_path": package_relative_path(package, intent_path),
        "intent_sha256": intent_sha256,
        "receipt_template_path": intent.get("receipt_template_path"),
        "authorization_scope_sha256": authorization_scope_sha256,
        "dispatch_claimed": True,
        "external_writes_performed": False,
        "next_step": "call the exact MCP create-doc once, then fetch-doc and commit the normalized receipt",
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
    }


def validate_access_receipt(
    access: Any,
    tenant_fingerprint: str,
    parent_fingerprint: str | None = None,
) -> None:
    if not isinstance(access, dict):
        raise WorkflowError("receipt.access must be an object")
    reject_unknown_keys(
        access,
        {
            "tenant_fingerprint",
            "parent_fingerprint",
            "acl_verified",
            "public_access",
            "external_shared",
        },
        "receipt.access",
    )
    if access.get("tenant_fingerprint") != tenant_fingerprint:
        raise WorkflowError("receipt tenant fingerprint mismatch")
    if parent_fingerprint is not None and (
        access.get("parent_fingerprint") != parent_fingerprint
    ):
        raise WorkflowError("receipt parent fingerprint mismatch")
    if access.get("acl_verified") is not True:
        raise WorkflowError("receipt must confirm ACL verification")
    if access.get("public_access") is not False:
        raise WorkflowError("receipt must confirm public access is disabled")
    if access.get("external_shared") is not False:
        raise WorkflowError("receipt must confirm external sharing is disabled")


def validate_asset_mappings(
    expected_assets: list[dict[str, Any]], mappings: Any
) -> None:
    if not isinstance(mappings, list) or len(mappings) != len(expected_assets):
        raise WorkflowError("receipt asset mapping count mismatch")
    for expected, mapping in zip(expected_assets, mappings):
        if not isinstance(mapping, dict):
            raise WorkflowError("receipt asset mapping must be an object")
        reject_unknown_keys(
            mapping,
            {"order", "source_sha256", "remote_token", "resolved"},
            "receipt asset mapping",
        )
        if mapping.get("order") != expected.get("order"):
            raise WorkflowError("receipt asset mapping order mismatch")
        if mapping.get("source_sha256") != expected.get("sha256"):
            raise WorkflowError("receipt asset mapping hash mismatch")
        if mapping.get("resolved") is not True:
            raise WorkflowError("receipt asset mapping is unresolved")
        required_string(mapping.get("remote_token"), "asset remote_token", 512)


def validate_mcp_receipt(mcp: Any, intent: dict[str, Any], *, write: bool) -> None:
    if not isinstance(mcp, dict):
        raise WorkflowError("receipt.mcp must be an object")
    allowed_mcp_fields = {
        "server_id",
        "read_tool",
        "read_call_id",
        "read_result_is_error",
        "read_response_sha256",
    }
    if write:
        allowed_mcp_fields.update(
            {
                "write_tool",
                "write_call_id",
                "write_result_is_error",
                "write_response_sha256",
            }
        )
    reject_unknown_keys(mcp, allowed_mcp_fields, "receipt.mcp")
    contract = intent.get("connector_contract")
    if not isinstance(contract, dict):
        raise WorkflowError("intent connector contract is missing")
    if mcp.get("server_id") != contract.get("server_id"):
        raise WorkflowError("receipt MCP server_id mismatch")
    if mcp.get("read_tool") != contract.get("read_tool"):
        raise WorkflowError("receipt MCP read tool mismatch")
    read_call_id = required_string(
        mcp.get("read_call_id"), "receipt.mcp.read_call_id", 512
    )
    if mcp.get("read_result_is_error") is not False:
        raise WorkflowError("receipt MCP read result must report isError false")
    validated_sha256(
        mcp.get("read_response_sha256"), "receipt.mcp.read_response_sha256"
    )
    if write:
        if mcp.get("write_tool") != contract.get("write_tool"):
            raise WorkflowError("receipt MCP write tool mismatch")
        write_call_id = required_string(
            mcp.get("write_call_id"), "receipt.mcp.write_call_id", 512
        )
        if write_call_id == read_call_id:
            raise WorkflowError("receipt MCP write/read call IDs must differ")
        if mcp.get("write_result_is_error") is not False:
            raise WorkflowError("receipt MCP write result must report isError false")
        validated_sha256(
            mcp.get("write_response_sha256"),
            "receipt.mcp.write_response_sha256",
        )


def load_protocol_receipt(
    package: Path, operation_id: str, receipt_value: str
) -> tuple[dict[str, Any], Path, str]:
    receipt_path = resolve_operation_file(
        package, operation_id, receipt_value, "receipt path"
    )
    receipt_raw = read_bounded(receipt_path, 2 * 1024 * 1024)
    try:
        receipt = json.loads(receipt_raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorkflowError("invalid Feishu receipt JSON") from exc
    if not isinstance(receipt, dict):
        raise WorkflowError("Feishu receipt root must be an object")
    return receipt, receipt_path, sha256_bytes(receipt_raw)


def validate_receipt_binding(
    receipt: dict[str, Any],
    pending: dict[str, Any],
    operation: str,
    *,
    dispatch: dict[str, Any] | None = None,
) -> None:
    allowed_fields = {
        "schema_version",
        "protocol",
        "provider",
        "operation",
        "operation_id",
        "intent_sha256",
        "idempotency_key",
        "outcome",
        "write_performed",
        "completed_at",
        "mcp",
        "access",
        "observed",
    }
    if operation == "push_create":
        allowed_fields.add("authorization_scope_sha256")
    reject_unknown_keys(receipt, allowed_fields, "receipt")
    if receipt.get("schema_version") != SCHEMA_VERSION:
        raise WorkflowError("receipt schema_version mismatch")
    if receipt.get("protocol") != FEISHU_PROTOCOL_VERSION:
        raise WorkflowError("receipt protocol mismatch")
    if receipt.get("provider") != "feishu":
        raise WorkflowError("receipt provider mismatch")
    if receipt.get("operation") != operation:
        raise WorkflowError("receipt operation mismatch")
    expected_kind = "push_create" if operation == "push_create" else "pull_read"
    if pending.get("kind") != expected_kind:
        raise WorkflowError("pending operation kind mismatch")
    if receipt.get("operation_id") != pending.get("operation_id"):
        raise WorkflowError("receipt operation_id mismatch")
    if receipt.get("intent_sha256") != pending.get("intent_sha256"):
        raise WorkflowError("receipt intent hash mismatch")
    if receipt.get("idempotency_key") != pending.get("idempotency_key"):
        raise WorkflowError("receipt idempotency key mismatch")
    completed_at = validated_timestamp(
        receipt.get("completed_at"), "receipt.completed_at"
    )
    if operation == "push_create":
        pending_scope = pending.get("authorization_scope_sha256")
        if receipt.get("authorization_scope_sha256") != pending_scope:
            raise WorkflowError("receipt authorization scope mismatch")
        if not isinstance(dispatch, dict):
            raise WorkflowError("push receipt requires a durable dispatch claim")
        if dispatch.get("authorization_scope_sha256") != pending_scope:
            raise WorkflowError("dispatch authorization scope mismatch")
        claimed_at = validated_timestamp(
            dispatch.get("claimed_at"), "dispatch.claimed_at"
        )
        completed_time = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
        claimed_time = datetime.fromisoformat(claimed_at.replace("Z", "+00:00"))
        if completed_time < claimed_time:
            raise WorkflowError("push receipt predates the dispatch claim")


def mark_feishu_result_unknown(
    package: Path,
    state: dict[str, Any],
    *,
    reason_code: str,
    receipt_path: Path | None = None,
    receipt_sha256: str | None = None,
) -> None:
    pending = state.get("pending") or {}
    state["phase"] = "result_unknown"
    state["result_unknown"] = {
        "provider": "feishu",
        "operation_id": pending.get("operation_id"),
        "kind": pending.get("kind"),
        "reason_code": reason_code,
        "target_fingerprint": sha256_bytes(
            str(pending.get("operation_id") or "").encode("utf-8")
        ),
        "recorded_at": utc_now(),
    }
    if receipt_path is not None and receipt_sha256 is not None:
        state["last_receipt"] = {
            "operation_id": pending.get("operation_id"),
            "path": package_relative_path(package, receipt_path),
            "sha256": receipt_sha256,
            "recorded_at": utc_now(),
        }
    write_sync_state(package, state)


def feishu_commit_push_report(
    package_value: str | None, receipt_value: str
) -> dict[str, Any]:
    started = time.perf_counter()
    package = resolve_package(package_value)
    state = load_sync_state(package)
    if state.get("phase") == "feishu_synced":
        last_receipt = state.get("last_receipt") or {}
        operation_id = last_receipt.get("operation_id")
        if operation_id:
            receipt_path = resolve_operation_file(
                package, operation_id, receipt_value, "receipt path"
            )
            receipt_sha256 = sha256_file(receipt_path)
            if receipt_sha256 == last_receipt.get("sha256"):
                return {
                    "schema_version": SCHEMA_VERSION,
                    "tool_version": TOOL_VERSION,
                    "ok": True,
                    "phase": "feishu_synced",
                    "operation_id": operation_id,
                    "document_url": state.get("document_url"),
                    "replayed": True,
                    "external_writes_performed": False,
                    "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
                }
        raise WorkflowError("no matching committed Feishu push receipt")
    if state.get("phase") != "push_in_flight":
        raise WorkflowError("Feishu push commit requires phase push_in_flight")
    intent, _intent_path, _intent_sha256 = load_pending_intent(package, state)
    pending = state["pending"]
    receipt_path: Path | None = None
    receipt_sha256: str | None = None
    try:
        receipt, receipt_path, receipt_sha256 = load_protocol_receipt(
            package, pending["operation_id"], receipt_value
        )
        validate_receipt_binding(
            receipt, pending, "push_create", dispatch=state.get("dispatch")
        )
        outcome = receipt.get("outcome")
        if outcome == "result_unknown":
            mark_feishu_result_unknown(
                package,
                state,
                reason_code="connector_result_unknown",
                receipt_path=receipt_path,
                receipt_sha256=receipt_sha256,
            )
            return {
                "schema_version": SCHEMA_VERSION,
                "tool_version": TOOL_VERSION,
                "ok": False,
                "phase": "result_unknown",
                "operation_id": pending["operation_id"],
                "external_writes_performed": False,
                "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
            }
        if outcome != "confirmed":
            raise WorkflowError("push receipt outcome is not confirmed")
        if receipt.get("write_performed") is not True:
            raise WorkflowError("confirmed push must report write_performed true")
        validate_mcp_receipt(receipt.get("mcp"), intent, write=True)
        target = intent["target"]
        validate_access_receipt(
            receipt.get("access"),
            target["tenant_fingerprint"],
            target["parent_fingerprint"],
        )
        observed = receipt.get("observed")
        if not isinstance(observed, dict):
            raise WorkflowError("receipt.observed must be an object")
        reject_unknown_keys(
            observed,
            {
                "document_id",
                "document_url",
                "revision",
                "title",
                "body_path",
                "body_sha256",
                "asset_mappings",
            },
            "receipt.observed",
        )
        document_id = validated_opaque_id(
            observed.get("document_id"), "receipt document_id"
        )
        document_url = validated_feishu_document_url(
            observed.get("document_url"), "receipt document_url"
        )
        revision = required_string(observed.get("revision"), "receipt revision", 512)
        if observed.get("title") != intent["content"]["title"]:
            raise WorkflowError("Feishu readback title mismatch")
        body_path = resolve_operation_file(
            package,
            pending["operation_id"],
            observed.get("body_path"),
            "receipt observed.body_path",
        )
        body_raw = read_bounded(body_path, MAX_MARKDOWN_BYTES)
        try:
            body = normalize_collaboration_text(body_raw.decode("utf-8"))
        except UnicodeDecodeError as exc:
            raise WorkflowError("Feishu readback body must be UTF-8") from exc
        body_sha256 = sha256_bytes(body.encode("utf-8"))
        if observed.get("body_sha256") != body_sha256:
            raise WorkflowError("Feishu readback body receipt hash mismatch")
        readback = collaboration_snapshot(
            package,
            observed.get("title"),
            body,
            validate_markdown=True,
        )
        if readback["payload_sha256"] != intent["content"]["payload_sha256"]:
            raise WorkflowError("Feishu readback payload mismatch")
        assets_path = resolve_operation_file(
            package,
            pending["operation_id"],
            intent["content"]["assets_path"],
            "intent assets_path",
        )
        if sha256_file(assets_path) != intent["content"]["assets_sha256"]:
            raise WorkflowError("Feishu intent assets hash mismatch")
        expected_assets_value = json.loads(
            read_bounded(assets_path, 2 * 1024 * 1024).decode("utf-8")
        )
        if not isinstance(expected_assets_value, list):
            raise WorkflowError("Feishu intent assets must be an array")
        validate_asset_mappings(expected_assets_value, observed.get("asset_mappings"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, WorkflowError):
        mark_feishu_result_unknown(
            package,
            state,
            reason_code="push_receipt_rejected",
            receipt_path=receipt_path,
            receipt_sha256=receipt_sha256,
        )
        raise

    completed_at = receipt["completed_at"]
    new_state = default_sync_state()
    new_state["state_sequence"] = int(state.get("state_sequence", 0))
    new_state.update(
        {
            "phase": "feishu_synced",
            "tenant_fingerprint": target["tenant_fingerprint"],
            "parent_fingerprint": target["parent_fingerprint"],
            "document_id": document_id,
            "document_fingerprint": sha256_bytes(document_id.encode("utf-8")),
            "document_url": document_url,
            "base_sha256": intent["content"]["payload_sha256"],
            "base_body_sha256": intent["content"]["body_sha256"],
            "base_assets_sha256": intent["content"]["assets_sha256"],
            "remote_sha256": intent["content"]["payload_sha256"],
            "remote_revision": revision,
            "draft_sha256_at_sync": intent["content"]["draft_sha256"],
            "last_synced_at": completed_at,
            "last_receipt": {
                "operation_id": pending["operation_id"],
                "path": package_relative_path(package, receipt_path),
                "sha256": receipt_sha256,
                "recorded_at": completed_at,
            },
        }
    )
    write_sync_state(package, new_state)
    return {
        "schema_version": SCHEMA_VERSION,
        "tool_version": TOOL_VERSION,
        "ok": True,
        "phase": "feishu_synced",
        "operation_id": pending["operation_id"],
        "document_fingerprint": new_state["document_fingerprint"],
        "document_url": new_state["document_url"],
        "remote_revision_present": True,
        "payload_sha256": new_state["base_sha256"],
        "replayed": False,
        "external_writes_performed": False,
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
    }


def feishu_prepare_pull_report(package_value: str | None) -> dict[str, Any]:
    started = time.perf_counter()
    package = resolve_package(package_value)
    state = load_sync_state(package)
    if state.get("protocol") != FEISHU_PROTOCOL_VERSION:
        raise WorkflowError("Feishu pull requires a committed protocol state")
    if state.get("phase") == "pull_prepared":
        try:
            intent, intent_path, intent_sha256 = load_pending_intent(package, state)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, WorkflowError):
            pending = state.get("pending") or {}
            previous_phase = pending.get("previous_phase")
            if previous_phase not in {"feishu_synced", "local_dirty"}:
                raise WorkflowError("pull intent cannot be recovered safely")
            state["phase"] = previous_phase
            state["pending"] = None
        else:
            return prepared_operation_report(
                package,
                intent,
                intent_path,
                intent_sha256,
                replayed=True,
                started=started,
            )
    if state.get("phase") not in {"feishu_synced", "local_dirty"}:
        raise WorkflowError(
            f"Feishu pull is unavailable from phase {state.get('phase')}"
        )
    document_id = validated_opaque_id(state.get("document_id"), "state document_id")
    tenant_fingerprint = validated_sha256(
        state.get("tenant_fingerprint"), "state tenant_fingerprint"
    )
    base_sha256 = validated_sha256(state.get("base_sha256"), "state base_sha256")
    metadata, body, draft_raw = read_draft(package / "draft.md")
    snapshot = collaboration_snapshot(
        package,
        metadata.get("title"),
        body,
        draft_raw=draft_raw,
        validate_markdown=False,
    )
    document_fingerprint = sha256_bytes(document_id.encode("utf-8"))
    semantic_intent = {
        "protocol": FEISHU_PROTOCOL_VERSION,
        "operation": "pull_read",
        "package_path": package.relative_to(REPO_ROOT.resolve()).as_posix(),
        "document_fingerprint": document_fingerprint,
        "tenant_fingerprint": tenant_fingerprint,
        "base_sha256": base_sha256,
        "local_payload_sha256": snapshot["payload_sha256"],
        "expected_revision": state.get("remote_revision"),
    }
    idempotency_key = sha256_bytes(canonical_json(semantic_intent))
    operation_id = f"feishu-pull-{idempotency_key[:24]}"
    operation_dir = operation_directory(package, operation_id)
    local_path = operation_dir / "local-before-pull.md"
    assets_path = operation_dir / "local-assets.json"
    intent_path = operation_dir / "intent.json"
    atomic_write(local_path, snapshot["body_bytes"])
    atomic_write(assets_path, snapshot["assets_bytes"])
    intent = {
        "schema_version": SCHEMA_VERSION,
        "protocol": FEISHU_PROTOCOL_VERSION,
        "operation_id": operation_id,
        "operation": "pull_read",
        "idempotency_key": idempotency_key,
        "prepared_at": utc_now(),
        "package_path": semantic_intent["package_path"],
        "target": {
            "mode": "read",
            "tenant_fingerprint": tenant_fingerprint,
            "document_id": document_id,
            "document_fingerprint": document_fingerprint,
            "expected_revision": state.get("remote_revision"),
        },
        "content": {
            "title": snapshot["title"],
            "draft_sha256": snapshot["draft_sha256"],
            "local_path": package_relative_path(package, local_path),
            "local_payload_sha256": snapshot["payload_sha256"],
            "local_body_sha256": snapshot["body_sha256"],
            "local_assets_path": package_relative_path(package, assets_path),
            "local_assets_sha256": snapshot["assets_sha256"],
            "local_asset_count": snapshot["asset_count"],
            "base_sha256": base_sha256,
        },
        "connector_contract": {
            "provider": "feishu",
            "server_id": FEISHU_MCP_SERVER_ID,
            "read_tool": "fetch-doc",
            "write_forbidden": True,
        },
    }
    receipt_template_path = operation_dir / "receipt-template.json"
    readback_path = operation_dir / "readback.md"
    intent["receipt_template_path"] = package_relative_path(
        package, receipt_template_path
    )
    receipt_template = {
        "schema_version": SCHEMA_VERSION,
        "protocol": FEISHU_PROTOCOL_VERSION,
        "provider": "feishu",
        "operation": "pull_read",
        "operation_id": operation_id,
        "intent_sha256": None,
        "idempotency_key": idempotency_key,
        "outcome": None,
        "write_performed": False,
        "completed_at": None,
        "mcp": {
            "server_id": FEISHU_MCP_SERVER_ID,
            "read_tool": "fetch-doc",
            "read_call_id": None,
            "read_result_is_error": None,
            "read_response_sha256": None,
        },
        "access": {
            "tenant_fingerprint": tenant_fingerprint,
            "acl_verified": None,
            "public_access": None,
            "external_shared": None,
        },
        "observed": {
            "document_id": document_id,
            "revision": None,
            "title": snapshot["title"],
            "body_path": package_relative_path(package, readback_path),
            "body_sha256": None,
            "asset_mappings": [
                {
                    "order": item["order"],
                    "source_sha256": item["sha256"],
                    "remote_token": None,
                    "resolved": None,
                }
                for item in snapshot["assets"]
            ],
        },
    }
    atomic_write_json(intent_path, intent)
    intent_sha256 = sha256_file(intent_path)
    receipt_template["intent_sha256"] = intent_sha256
    atomic_write_json(receipt_template_path, receipt_template)
    state["phase"] = "pull_prepared"
    state["candidate"] = None
    state["conflict"] = None
    state["result_unknown"] = None
    state["pending"] = {
        "operation_id": operation_id,
        "kind": "pull_read",
        "idempotency_key": idempotency_key,
        "intent_path": package_relative_path(package, intent_path),
        "intent_sha256": intent_sha256,
        "payload_sha256": snapshot["payload_sha256"],
        "previous_phase": "local_dirty"
        if snapshot["payload_sha256"] != base_sha256
        else "feishu_synced",
        "prepared_at": intent["prepared_at"],
    }
    write_sync_state(package, state)
    return prepared_operation_report(
        package,
        intent,
        intent_path,
        intent_sha256,
        replayed=False,
        started=started,
    )


def set_sync_conflict(
    package: Path,
    state: dict[str, Any],
    *,
    operation_id: str,
    reason_code: str,
    local_sha256: str | None,
    remote_sha256: str | None,
    remote_revision: str | None,
    snapshot_path: Path | None,
) -> None:
    state["phase"] = "conflict"
    state["pending"] = None
    state["candidate"] = None
    state["conflict"] = {
        "operation_id": operation_id,
        "reason_code": reason_code,
        "base_sha256": state.get("base_sha256"),
        "local_sha256": local_sha256,
        "remote_sha256": remote_sha256,
        "remote_revision": remote_revision,
        "snapshot_path": package_relative_path(package, snapshot_path)
        if snapshot_path is not None
        else None,
        "detected_at": utc_now(),
    }
    write_sync_state(package, state)


def feishu_stage_pull_report(
    package_value: str | None, receipt_value: str
) -> dict[str, Any]:
    started = time.perf_counter()
    package = resolve_package(package_value)
    state = load_sync_state(package)
    if state.get("phase") != "pull_prepared":
        raise WorkflowError("Feishu pull staging requires phase pull_prepared")
    intent, _intent_path, _intent_sha256 = load_pending_intent(package, state)
    pending = state["pending"]
    receipt_path: Path | None = None
    receipt_sha256: str | None = None
    body_path: Path | None = None
    local_snapshot: dict[str, Any] | None = None
    remote_snapshot: dict[str, Any] | None = None
    remote_revision: str | None = None
    try:
        receipt, receipt_path, receipt_sha256 = load_protocol_receipt(
            package, pending["operation_id"], receipt_value
        )
        validate_receipt_binding(receipt, pending, "pull_read")
        if receipt.get("outcome") != "confirmed":
            mark_feishu_result_unknown(
                package,
                state,
                reason_code="pull_result_unavailable",
                receipt_path=receipt_path,
                receipt_sha256=receipt_sha256,
            )
            return {
                "schema_version": SCHEMA_VERSION,
                "tool_version": TOOL_VERSION,
                "ok": False,
                "phase": "result_unknown",
                "operation_id": pending["operation_id"],
                "external_writes_performed": False,
                "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
            }
        if receipt.get("write_performed") is not False:
            raise WorkflowError("pull receipt must report write_performed false")
        validate_mcp_receipt(receipt.get("mcp"), intent, write=False)
        target = intent["target"]
        validate_access_receipt(receipt.get("access"), target["tenant_fingerprint"])
        observed = receipt.get("observed")
        if not isinstance(observed, dict):
            raise WorkflowError("receipt.observed must be an object")
        reject_unknown_keys(
            observed,
            {
                "document_id",
                "revision",
                "title",
                "body_path",
                "body_sha256",
                "asset_mappings",
            },
            "receipt.observed",
        )
        if observed.get("document_id") != target["document_id"]:
            raise WorkflowError("pull receipt document_id mismatch")
        remote_revision = required_string(
            observed.get("revision"), "pull receipt revision", 512
        )
        body_path = resolve_operation_file(
            package,
            pending["operation_id"],
            observed.get("body_path"),
            "pull observed.body_path",
        )
        body_raw = read_bounded(body_path, MAX_MARKDOWN_BYTES)
        try:
            remote_body = normalize_collaboration_text(body_raw.decode("utf-8"))
        except UnicodeDecodeError as exc:
            raise WorkflowError("Feishu pull body must be UTF-8") from exc
        remote_body_sha256 = sha256_bytes(remote_body.encode("utf-8"))
        if observed.get("body_sha256") != remote_body_sha256:
            raise WorkflowError("Feishu pull body receipt hash mismatch")
        metadata, local_body, draft_raw = read_draft(package / "draft.md")
        local_snapshot = collaboration_snapshot(
            package,
            metadata.get("title"),
            local_body,
            draft_raw=draft_raw,
            validate_markdown=False,
        )
        if observed.get("title") != local_snapshot["title"]:
            set_sync_conflict(
                package,
                state,
                operation_id=pending["operation_id"],
                reason_code="remote_title_changed",
                local_sha256=local_snapshot["payload_sha256"],
                remote_sha256=None,
                remote_revision=remote_revision,
                snapshot_path=body_path,
            )
            return {
                "schema_version": SCHEMA_VERSION,
                "tool_version": TOOL_VERSION,
                "ok": False,
                "phase": "conflict",
                "reason_code": "remote_title_changed",
                "external_writes_performed": False,
                "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
            }
        remote_snapshot = collaboration_snapshot(
            package,
            observed.get("title"),
            remote_body,
            validate_markdown=True,
        )
        validate_asset_mappings(
            remote_snapshot["assets"], observed.get("asset_mappings")
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, WorkflowError):
        if state.get("phase") == "pull_prepared":
            set_sync_conflict(
                package,
                state,
                operation_id=pending["operation_id"],
                reason_code="remote_payload_unusable",
                local_sha256=(local_snapshot or {}).get("payload_sha256"),
                remote_sha256=(remote_snapshot or {}).get("payload_sha256"),
                remote_revision=remote_revision,
                snapshot_path=body_path,
            )
        raise

    assert receipt_path is not None
    assert receipt_sha256 is not None
    assert body_path is not None
    assert local_snapshot is not None
    assert remote_snapshot is not None
    base_sha256 = validated_sha256(state.get("base_sha256"), "state base_sha256")
    local_sha256 = local_snapshot["payload_sha256"]
    remote_sha256 = remote_snapshot["payload_sha256"]
    completed_at = receipt["completed_at"]
    state["remote_sha256"] = remote_sha256
    state["remote_revision"] = remote_revision
    state["last_receipt"] = {
        "operation_id": pending["operation_id"],
        "path": package_relative_path(package, receipt_path),
        "sha256": receipt_sha256,
        "recorded_at": completed_at,
    }
    state["pending"] = None
    state["result_unknown"] = None
    state["conflict"] = None
    state["candidate"] = None

    if local_sha256 == base_sha256 and remote_sha256 == base_sha256:
        state["phase"] = "feishu_synced"
        state["last_synced_at"] = completed_at
        outcome = "no_change"
    elif local_sha256 != base_sha256 and remote_sha256 == base_sha256:
        state["phase"] = "local_dirty"
        state["remote_checked_at"] = completed_at
        outcome = "local_only_change"
    elif local_sha256 == remote_sha256:
        state["phase"] = "feishu_synced"
        state["base_sha256"] = remote_sha256
        state["base_body_sha256"] = remote_snapshot["body_sha256"]
        state["base_assets_sha256"] = remote_snapshot["assets_sha256"]
        state["last_synced_at"] = completed_at
        outcome = "converged"
    elif local_sha256 == base_sha256:
        state["phase"] = "remote_dirty"
        state["candidate"] = {
            "operation_id": pending["operation_id"],
            "expected_local_sha256": local_sha256,
            "remote_sha256": remote_sha256,
            "remote_body_sha256": remote_snapshot["body_sha256"],
            "remote_assets_sha256": remote_snapshot["assets_sha256"],
            "assets_changed": remote_snapshot["assets_sha256"]
            != state.get("base_assets_sha256"),
            "body_path": package_relative_path(package, body_path),
            "receipt_path": package_relative_path(package, receipt_path),
            "receipt_sha256": receipt_sha256,
            "remote_revision": remote_revision,
            "staged_at": completed_at,
        }
        outcome = "remote_change_staged"
    else:
        set_sync_conflict(
            package,
            state,
            operation_id=pending["operation_id"],
            reason_code="both_sides_changed",
            local_sha256=local_sha256,
            remote_sha256=remote_sha256,
            remote_revision=remote_revision,
            snapshot_path=body_path,
        )
        return {
            "schema_version": SCHEMA_VERSION,
            "tool_version": TOOL_VERSION,
            "ok": False,
            "phase": "conflict",
            "reason_code": "both_sides_changed",
            "external_writes_performed": False,
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
        }
    write_sync_state(package, state)
    return {
        "schema_version": SCHEMA_VERSION,
        "tool_version": TOOL_VERSION,
        "ok": True,
        "phase": state["phase"],
        "outcome": outcome,
        "local_payload_sha256": local_sha256,
        "remote_payload_sha256": remote_sha256,
        "draft_modified": False,
        "external_writes_performed": False,
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
    }


def replace_frontmatter_values(
    draft_text: str, body: str, *, assets_changed: bool
) -> str:
    match = FRONTMATTER_RE.match(draft_text)
    if not match:
        raise WorkflowError("draft.md must contain YAML frontmatter")
    updates: dict[str, str] = {
        "status": "editorial_review",
        "fact_checked": "false",
        "copyedit_checked": "false",
        "copyedit_body_sha256": '""',
    }
    if assets_changed:
        updates["rights_checked"] = "false"
    lines = match.group("meta").splitlines()
    replaced: set[str] = set()
    output_lines: list[str] = []
    for line in lines:
        yaml_match = YAML_KEY_RE.match(line) if line and not line[0].isspace() else None
        key = yaml_match.group("key") if yaml_match else None
        if key in updates:
            output_lines.append(f"{key}: {updates[key]}")
            replaced.add(key)
        else:
            output_lines.append(line)
    for key, value in updates.items():
        if key not in replaced:
            output_lines.append(f"{key}: {value}")
    normalized_body = normalize_collaboration_text(body)
    return "---\n" + "\n".join(output_lines) + "\n---\n" + normalized_body


def feishu_accept_pull_report(package_value: str | None) -> dict[str, Any]:
    started = time.perf_counter()
    package = resolve_package(package_value)
    state = load_sync_state(package)
    if state.get("phase") != "remote_dirty":
        raise WorkflowError("Feishu pull accept requires phase remote_dirty")
    candidate = state.get("candidate")
    if not isinstance(candidate, dict):
        raise WorkflowError("Feishu pull candidate is missing")
    operation_id = required_string(
        candidate.get("operation_id"), "candidate.operation_id", 128
    )
    body_path = resolve_operation_file(
        package, operation_id, candidate.get("body_path"), "candidate.body_path"
    )
    body_raw = read_bounded(body_path, MAX_MARKDOWN_BYTES)
    try:
        remote_body = normalize_collaboration_text(body_raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise WorkflowError("Feishu candidate body must be UTF-8") from exc
    metadata, local_body, draft_raw = read_draft(package / "draft.md")
    local_snapshot = collaboration_snapshot(
        package,
        metadata.get("title"),
        local_body,
        draft_raw=draft_raw,
        validate_markdown=False,
    )
    expected_local_sha256 = validated_sha256(
        candidate.get("expected_local_sha256"),
        "candidate.expected_local_sha256",
    )
    if local_snapshot["payload_sha256"] != expected_local_sha256:
        set_sync_conflict(
            package,
            state,
            operation_id=operation_id,
            reason_code="local_changed_after_staging",
            local_sha256=local_snapshot["payload_sha256"],
            remote_sha256=candidate.get("remote_sha256"),
            remote_revision=candidate.get("remote_revision"),
            snapshot_path=body_path,
        )
        raise WorkflowError("local draft changed after Feishu pull staging")
    remote_snapshot = collaboration_snapshot(
        package,
        metadata.get("title"),
        remote_body,
        validate_markdown=True,
    )
    if remote_snapshot["payload_sha256"] != candidate.get("remote_sha256"):
        raise WorkflowError("Feishu candidate payload hash mismatch")
    if remote_snapshot["body_sha256"] != candidate.get("remote_body_sha256"):
        raise WorkflowError("Feishu candidate body hash mismatch")
    if remote_snapshot["assets_sha256"] != candidate.get("remote_assets_sha256"):
        raise WorkflowError("Feishu candidate asset hash mismatch")
    try:
        draft_text = draft_raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise WorkflowError("draft.md must be UTF-8") from exc
    updated_draft = replace_frontmatter_values(
        draft_text,
        remote_body,
        assets_changed=candidate.get("assets_changed") is True,
    )
    atomic_write(package / "draft.md", updated_draft.encode("utf-8"))
    updated_metadata, updated_body, updated_raw = read_draft(package / "draft.md")
    updated_snapshot = collaboration_snapshot(
        package,
        updated_metadata.get("title"),
        updated_body,
        draft_raw=updated_raw,
        validate_markdown=True,
    )
    if updated_snapshot["payload_sha256"] != remote_snapshot["payload_sha256"]:
        raise WorkflowError("accepted Feishu body did not preserve the staged payload")
    state["phase"] = "pulled"
    state["base_sha256"] = remote_snapshot["payload_sha256"]
    state["base_body_sha256"] = remote_snapshot["body_sha256"]
    state["base_assets_sha256"] = remote_snapshot["assets_sha256"]
    state["remote_sha256"] = remote_snapshot["payload_sha256"]
    state["remote_revision"] = candidate.get("remote_revision")
    state["draft_sha256_at_sync"] = updated_snapshot["draft_sha256"]
    state["last_synced_at"] = utc_now()
    state["pending"] = None
    state["candidate"] = None
    state["conflict"] = None
    state["result_unknown"] = None
    write_sync_state(package, state)
    return {
        "schema_version": SCHEMA_VERSION,
        "tool_version": TOOL_VERSION,
        "ok": True,
        "phase": "pulled",
        "payload_sha256": remote_snapshot["payload_sha256"],
        "draft_sha256": updated_snapshot["draft_sha256"],
        "lifecycle_state": updated_metadata.get("status"),
        "fact_checked": updated_metadata.get("fact_checked"),
        "rights_checked": updated_metadata.get("rights_checked"),
        "copyedit_checked": updated_metadata.get("copyedit_checked"),
        "draft_modified": True,
        "external_writes_performed": False,
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
    }


def configure_company_report(package_value: str | None) -> dict[str, Any]:
    started = time.perf_counter()
    package = resolve_package(package_value)
    publish_path = package / "publish.yml"
    existing_raw = (
        read_bounded(publish_path, 512 * 1024) if publish_path.is_file() else b""
    )
    try:
        existing_text = existing_raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise WorkflowError("publish.yml must be UTF-8") from exc
    existing = (
        parse_top_level_yaml(existing_text, str(publish_path)) if existing_text else {}
    )
    desired = {
        "project_adapter": "appsso",
        "delivery_mode": "manual_editor",
        "layout_profile": "default",
    }
    conflicts = [
        field
        for field, value in desired.items()
        if field in existing and existing.get(field) != value
    ]
    if conflicts:
        raise WorkflowError(
            "publish.yml already declares a conflicting company route: "
            + ", ".join(conflicts)
        )
    missing = [field for field in desired if field not in existing]
    if missing:
        prefix = existing_text
        if prefix and not prefix.endswith("\n"):
            prefix += "\n"
        if prefix and prefix.strip():
            prefix += "\n"
        additions = "".join(f'{field}: "{desired[field]}"\n' for field in missing)
        atomic_write(publish_path, (prefix + additions).encode("utf-8"))
    final_sha256 = sha256_file(publish_path)
    return {
        "schema_version": SCHEMA_VERSION,
        "tool_version": TOOL_VERSION,
        "ok": True,
        "operation": "configure_company",
        "package": str(package),
        "publish_path": package_relative_path(package, publish_path),
        "changed": bool(missing),
        "added_fields": missing,
        "route": desired,
        "publish_sha256": final_sha256,
        "external_writes_performed": False,
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
    }


def action(
    action_id: str,
    reason: str,
    *,
    implemented: bool,
    external_write: bool = False,
    authorization_required: bool = False,
    command: list[str] | None = None,
    command_template: list[str] | None = None,
    required_inputs: list[str] | None = None,
    handler: str | None = None,
    details: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": action_id,
        "implemented": implemented,
        "external_write": external_write,
        "authorization_required": authorization_required,
        "command": command,
        "command_template": command_template,
        "required_inputs": required_inputs or [],
        "handler": handler,
        "details": details or [],
        "reason": reason,
    }


def choose_next_action(
    package: Path,
    lifecycle: str | None,
    publish: dict[str, Any],
    sync: dict[str, Any],
    build: dict[str, Any],
    build_stale: bool,
    tool_ok: bool,
    feishu_connector_connected: bool = False,
    wechat_draft_adapter_available: bool = False,
) -> dict[str, Any]:
    if not tool_ok:
        return action(
            "repair_tool_integrity",
            "版式真源或本地运行依赖未通过 doctor。",
            implemented=True,
            command=[
                sys.executable,
                str(Path(__file__).resolve()),
                "doctor",
                "--json",
            ],
        )

    phase = str(sync.get("phase") or "local_only")
    package_argument = str(package)
    if phase == "result_unknown":
        unknown = sync.get("result_unknown") or {}
        provider = unknown.get("provider") or "feishu"
        return action(
            "reconcile_feishu_result",
            f"上次 {provider} 操作结果不明；禁止重试或新建第二份文档。",
            implemented=False,
            handler="$company-content-sync",
            details=[
                "只读检查精确 operation_id 对应的飞书目标。",
                "确认读回内容与授权 payload 完全一致后才能补记成功。",
            ],
        )
    if phase == "conflict":
        conflict = sync.get("conflict") or {}
        reason_code = conflict.get("reason_code") or "both_sides_changed"
        return action(
            "resolve_sync_conflict",
            f"本地稿与飞书候选不能安全合并（{reason_code}）。",
            implemented=False,
            handler="$company-content-sync",
            details=["保留本地稿与暂存候选；必须人工选择或合并。"],
        )
    if phase == "push_prepared":
        if sync.get("pending_source_changed"):
            return action(
                "inspect_stale_feishu_intent",
                "准备后的正文、发布配置或本地资产已变化，原授权范围失效。",
                implemented=False,
                handler="$company-content-sync",
                details=["先确认旧 operation 未被发送；不得直接生成第二个 create。"],
            )
        pending = sync.get("pending") or {}
        if sync.get("pending_intent_missing") or sync.get("pending_intent_invalid"):
            return action(
                "recover_feishu_intent",
                "一次性意图文件缺失；只能用原租户与父目录参数重建同一 operation，不能创建新文档。",
                implemented=True,
                command_template=[
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "feishu-prepare-push",
                    package_argument,
                    "--tenant-fingerprint",
                    "<tenant_fingerprint>",
                    "--json",
                ],
                required_inputs=["tenant_fingerprint"],
                handler="$company-content-sync",
            )
        if not feishu_connector_connected:
            return action(
                "integrate_trusted_feishu_executor",
                "本机尚无可信的一次性飞书执行器；不能消耗派发凭据。",
                implemented=False,
                external_write=False,
                authorization_required=False,
                handler="$company-content-sync",
                details=[
                    "仅安装 connector 不足够；host 必须把当前授权证明与 claim 原子绑定，并只放行 1 次 create-doc。",
                    "执行器还必须支持紧随其后的 fetch-doc 读回，并保存可验证的调用证据。",
                    "执行器不可用时停在 push_prepared；不得运行 feishu-begin-push。",
                ],
            )
        operation_id = str(pending.get("operation_id") or "")
        authorization_scope = str(pending.get("authorization_scope_sha256") or "")
        return action(
            "begin_feishu_create",
            "取得本次精确授权后，先生成不可重复的一次性派发凭据；成功后 Agent 才能调用飞书 MCP。",
            implemented=True,
            external_write=False,
            authorization_required=True,
            command=[
                sys.executable,
                str(Path(__file__).resolve()),
                "feishu-begin-push",
                package_argument,
                "--operation-id",
                operation_id,
                "--authorization-scope",
                authorization_scope,
                "--json",
            ],
            handler="$company-content-sync",
            details=[
                f"intent_path: {pending.get('intent_path')}",
                f"authorization_scope_sha256: {authorization_scope or 'missing'}",
                "begin 成功后只允许调用精确的 create-doc 1 次；超时或回执不完整必须转为结果未知，禁止自动重试。",
            ],
        )
    if phase == "push_in_flight":
        pending = sync.get("pending") or {}
        return action(
            "reconcile_feishu_result",
            "飞书 create 已被一次性派发；在合格回执落盘前一律按结果未知处理，禁止再次创建。",
            implemented=False,
            handler="$company-content-sync",
            details=[
                f"operation_id: {pending.get('operation_id')}",
                "只读查询目标租户与父目录，核对 operation 对应文档后再补记成功或明确失败。",
            ],
        )
    if phase == "pull_prepared":
        pending = sync.get("pending") or {}
        if sync.get("pending_intent_missing") or sync.get("pending_intent_invalid"):
            return action(
                "recover_feishu_pull_intent",
                "只读拉回意图缺失或损坏；重建确定性的读取意图后再继续。",
                implemented=True,
                command=[
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "feishu-prepare-pull",
                    package_argument,
                    "--json",
                ],
                handler="$company-content-sync",
            )
        if not feishu_connector_connected:
            return action(
                "integrate_trusted_feishu_executor",
                "本机尚无可信的飞书读取执行器；不能执行团队稿拉回。",
                implemented=False,
                external_write=False,
                authorization_required=False,
                handler="$company-content-sync",
                details=[
                    "Agent host 必须先确认官方 fetch-doc 可调用，并把响应绑定到当前 read intent。"
                ],
            )
        return action(
            "execute_feishu_pull",
            "只读拉回意图已准备；由 Agent 调用飞书 MCP 读取精确文档并生成白名单回执。",
            implemented=False,
            external_write=False,
            authorization_required=False,
            handler="$company-content-sync",
            details=[f"intent_path: {pending.get('intent_path')}"],
        )
    if phase == "remote_dirty":
        return action(
            "accept_feishu_pull",
            "飞书团队修改已进入本地暂存；显式接受后只替换正文，并重新打开事实与终校门禁。",
            implemented=True,
            command=[
                sys.executable,
                str(Path(__file__).resolve()),
                "feishu-accept-pull",
                package_argument,
                "--json",
            ],
        )
    if phase == "local_dirty_unverified":
        return action(
            "prepare_feishu_pull",
            "本地内容已偏离同步基线；先只读检查飞书是否也有变化。",
            implemented=True,
            command=[
                sys.executable,
                str(Path(__file__).resolve()),
                "feishu-prepare-pull",
                package_argument,
                "--json",
            ],
        )
    if phase == "local_dirty":
        return action(
            "safe_feishu_update_unavailable",
            "只有本地发生变化，但当前连接层没有 revision/CAS；禁止覆盖已有飞书文档。",
            implemented=False,
            handler="$company-content-sync",
            details=["可继续本地审校；如需回写，等待支持条件更新的连接器。"],
        )

    if lifecycle in {"published", "archived"}:
        return action(
            "none",
            f"内容状态为 {lifecycle}，本工具不自动重新进入交付流程。",
            implemented=True,
        )
    if lifecycle != "ready":
        return action(
            "complete_editorial_gates",
            "只有 ready 内容才能进入公司协作交付。",
            implemented=True,
            handler="$self-media-ops",
            details=[
                "按 self-media-ops 核对当前编辑阶段与精确正文校验。",
                "所有门禁通过后再把 draft.md frontmatter 状态推进到 ready。",
            ],
        )
    safe_route = {
        "project_adapter": "appsso",
        "delivery_mode": "manual_editor",
        "layout_profile": "default",
    }
    missing_route_fields = [field for field in safe_route if field not in publish]
    conflicting_safe_route_fields = [
        field
        for field, expected in safe_route.items()
        if field in publish and publish.get(field) != expected
    ]
    if missing_route_fields and conflicting_safe_route_fields:
        return action(
            "complete_company_route",
            "公司路由只有部分字段，且已有值不是安全的手工默认路线；需要显式补齐。",
            implemented=False,
            external_write=False,
            handler="$self-media-ops",
            details=[
                "missing: " + ", ".join(missing_route_fields),
                "existing non-default: " + ", ".join(conflicting_safe_route_fields),
                "不要用 configure-company 覆盖已有交付选择。",
            ],
        )
    if missing_route_fields:
        return action(
            "configure_company_route",
            "公司 APPSO 稿缺少明确路由；先补齐轻量的本地手工交付配置。",
            implemented=True,
            external_write=False,
            command=[
                sys.executable,
                str(Path(__file__).resolve()),
                "configure-company",
                package_argument,
                "--json",
            ],
            details=[
                "只补缺失字段，不覆盖已有冲突配置。",
                "默认 manual_editor + default；不会启用公众号 API 写入。",
            ],
        )
    if publish.get("project_adapter") != "appsso":
        return action(
            "select_company_adapter",
            "当前稿件已声明其他项目适配器，不能自动切到公司 APPSO 路线。",
            implemented=False,
            external_write=False,
            handler="$self-media-ops",
            details=["显式确认稿件归属后再修改 project_adapter。"],
        )
    if phase == "local_only" and (not build or build_stale):
        return action(
            "run_local_build",
            "先用锁定 Profile 验证排版，再生成飞书在线预览意图。",
            implemented=True,
            command=[
                sys.executable,
                str(Path(__file__).resolve()),
                "build",
                package_argument,
                "--json",
            ],
            details=[
                "本地 HTML 只作为确定性版式与保真凭据，不再作为默认用户预览交付面。"
            ],
        )
    if (
        phase == "local_only"
        and build
        and not build_stale
        and not build.get("local_format_qualified", False)
    ):
        warning_codes = ", ".join(build.get("warning_codes", [])) or "unknown"
        return action(
            "repair_local_build",
            f"飞书在线预览前的本地排版门未通过：{warning_codes}。",
            implemented=False,
        )
    if phase == "local_only":
        return action(
            "prepare_feishu_create",
            "本地排版门已通过；绑定公司 tenant 与目标文件夹，生成飞书在线预览意图。",
            implemented=True,
            external_write=False,
            authorization_required=False,
            command_template=[
                sys.executable,
                str(Path(__file__).resolve()),
                "feishu-prepare-push",
                package_argument,
                "--tenant-fingerprint",
                "<64-hex-company-tenant-fingerprint>",
                "--json",
            ],
            required_inputs=["tenant_fingerprint"],
            details=[
                "prepare 只写本地 journal 与 dist/content-sync/，不会访问飞书。",
                "真正 create 仍需对精确正文、图片、目录与授权范围单独确认。",
            ],
        )
    if phase == "feishu_synced":
        return action(
            "wait_for_team_review",
            "飞书在线排版预览已就绪；团队确认完成后显式运行只读 pull。",
            implemented=True,
            command=[
                sys.executable,
                str(Path(__file__).resolve()),
                "feishu-prepare-pull",
                package_argument,
                "--json",
            ],
            details=[
                f"preview_url: {sync.get('document_url') or 'missing'}",
                "飞书是在线协作预览面；锁定 HTML 仍是精确微信样式凭据。",
                "未收到团队完成信号时无需轮询。",
            ],
        )
    if phase in {"pulled", "team_review_complete", "built", "sealed"} and (
        not build or build_stale
    ):
        return action(
            "run_local_build",
            "飞书协作结果已回到本地，需要用锁定 Profile 生成密封 HTML。",
            implemented=True,
            command=[
                sys.executable,
                str(Path(__file__).resolve()),
                "build",
                package_argument,
                "--json",
            ],
        )
    if (
        phase in {"pulled", "team_review_complete", "built", "sealed"}
        and build
        and not build_stale
        and not build.get("local_format_qualified", False)
    ):
        warning_codes = ", ".join(build.get("warning_codes", [])) or "unknown"
        return action(
            "repair_local_build",
            f"本地构建未通过媒体或保真门禁：{warning_codes}。",
            implemented=False,
        )
    required_delivery_mode = str(
        build.get("required_delivery_mode") or WECHAT_API_DELIVERY_MODE
    )
    required_layout_profile = str(
        build.get("required_layout_profile") or WECHAT_API_LAYOUT_PROFILE
    )
    if (
        phase in {"pulled", "team_review_complete", "built", "sealed"}
        and build
        and not build_stale
        and (
            publish.get("delivery_mode") != required_delivery_mode
            or publish.get("layout_profile") != required_layout_profile
        )
    ):
        return action(
            "select_api_delivery_route",
            "当前交付模式不允许公众号 API 写入；需显式选择密封草稿路线后再继续。",
            implemented=False,
            handler="$self-media-ops",
            details=[
                f"required delivery_mode: {required_delivery_mode}",
                f"required layout_profile: {required_layout_profile}",
            ],
        )
    if (
        phase in {"pulled", "team_review_complete", "built", "sealed"}
        and build
        and not build_stale
        and not build.get("company_format_qualified", False)
    ):
        return action(
            "qualify_company_format",
            "本地构建已通过，但精确公众号账号 × Profile 尚未完成后台往返资格验证。",
            implemented=False,
            external_write=True,
            authorization_required=True,
            details=[
                "资格验证会在目标公众号创建测试草稿，必须取得本次账号与测试内容授权。",
                "验收回执必须绑定账号指纹、格式合同哈希、Profile 和验收时间。",
            ],
        )
    if (
        phase in {"pulled", "team_review_complete", "built", "sealed"}
        and build
        and not build_stale
        and build.get("company_format_qualified", False)
    ):
        if not wechat_draft_adapter_available:
            return action(
                "integrate_wechat_draft_adapter",
                "公司格式已通过，但现有微信发布器尚未绑定为可核验的一次性草稿执行器。",
                implemented=False,
                external_write=False,
                authorization_required=False,
                handler="$company-content-sync",
                details=[
                    "复用 微信公众号/tools/wechat_publish.py，不维护第二套 API 客户端。",
                    "执行器必须核对账号指纹、密封 HTML、图片与本次精确授权。",
                ],
            )
        return action(
            "wechat_create_draft",
            "本地 HTML 已密封；下一步只能在核对账号、正文和图片后显式创建 1 条微信草稿。",
            implemented=False,
            external_write=True,
            authorization_required=True,
            details=[
                "执行时必须核对本地凭据的非敏感账号指纹与资格回执一致。",
            ],
        )
    if phase == "wechat_draft_created":
        return action(
            "inspect_wechat_draft",
            "草稿已创建；需要人工检查后台和手机预览，本工具不会自动发布。",
            implemented=False,
        )
    return action(
        "repair_sync_state",
        f"不支持的同步阶段：{phase}",
        implemented=False,
    )


def status_report(package_value: str | None) -> dict[str, Any]:
    started = time.perf_counter()
    package = resolve_package(package_value)
    draft_path = package / "draft.md"
    if not draft_path.is_file():
        raise WorkflowError(f"missing draft.md in {package}")

    metadata, body, draft_raw = read_draft(draft_path)
    publish = read_publish(package)
    publish_path = package / "publish.yml"
    publish_sha256 = sha256_file(publish_path) if publish_path.is_file() else None
    doctor = doctor_report()
    sync = load_sync_state(package)
    build = load_json(package / BUILD_RELATIVE_PATH, optional=True)
    draft_sha256 = sha256_bytes(draft_raw)
    profile_sha256 = doctor["format"]["profile_sha256"]
    integrity_issues, actual_html_sha256 = build_integrity(
        package, build, draft_sha256, doctor
    )
    build_stale = bool(integrity_issues)
    current_company_format_qualified = bool(
        build
        and not build_stale
        and build.get("local_format_qualified")
        and doctor["qualification"]["production_qualified"]
        and publish.get("delivery_mode")
        == doctor["qualification"]["required_delivery_mode"]
        and publish.get("layout_profile")
        == doctor["qualification"]["required_layout_profile"]
    )
    build_for_route = dict(build)
    build_for_route["company_format_qualified"] = current_company_format_qualified
    build_for_route["required_delivery_mode"] = doctor["qualification"][
        "required_delivery_mode"
    ]
    build_for_route["required_layout_profile"] = doctor["qualification"][
        "required_layout_profile"
    ]

    blockers = list(doctor["blockers"])
    warnings = list(doctor["warnings"])
    if not publish:
        warnings.append("publish.yml is missing; collaboration routing is incomplete")
    if build_stale and build:
        warnings.append("local HTML build is stale")

    lifecycle = (
        str(metadata.get("status")) if metadata.get("status") is not None else None
    )
    workflow_blockers: list[str] = []
    if lifecycle not in {"ready", "published", "archived"}:
        workflow_blockers.append("lifecycle_not_ready")
    required_route_fields = ("project_adapter", "delivery_mode", "layout_profile")
    if lifecycle == "ready" and (
        publish.get("project_adapter") != "appsso"
        or any(field not in publish for field in required_route_fields)
    ):
        workflow_blockers.append("company_route_incomplete")

    stored_sync_phase = str(sync.get("phase") or "local_only")
    sync_for_route = dict(sync)
    sync_phase = stored_sync_phase
    local_payload_sha256: str | None = None
    current_snapshot: dict[str, Any] | None = None
    if sync.get("protocol") == FEISHU_PROTOCOL_VERSION:
        try:
            current_snapshot = collaboration_snapshot(
                package,
                metadata.get("title"),
                body,
                draft_raw=draft_raw,
                validate_markdown=False,
            )
            local_payload_sha256 = current_snapshot["payload_sha256"]
        except WorkflowError as exc:
            workflow_blockers.append("collaboration_payload_invalid")
            warnings.append(f"cannot compute collaboration payload: {exc}")
        if (
            stored_sync_phase == "feishu_synced"
            and local_payload_sha256
            and local_payload_sha256 != sync.get("base_sha256")
        ):
            sync_phase = "local_dirty_unverified"
        if stored_sync_phase == "push_prepared":
            pending = sync.get("pending") or {}
            pending_source_changed = bool(
                not local_payload_sha256
                or local_payload_sha256 != pending.get("payload_sha256")
                or draft_sha256 != pending.get("draft_sha256")
                or publish_sha256 != pending.get("publish_sha256")
                or lifecycle != "ready"
                or publish.get("project_adapter") != "appsso"
                or build_stale
                or build.get("sealed_build_sha256")
                != pending.get("sealed_build_sha256")
                or build.get("html_sha256") != pending.get("html_sha256")
            )
            pending_intent_missing = False
            pending_intent_invalid = False
            try:
                pending_intent_path = resolve_operation_file(
                    package,
                    pending.get("operation_id"),
                    pending.get("intent_path"),
                    "pending.intent_path",
                )
                pending_intent_missing = not pending_intent_path.is_file()
                if not pending_intent_missing:
                    if current_snapshot is None:
                        pending_intent_invalid = True
                    else:
                        pending_intent, _path, pending_intent_sha = load_pending_intent(
                            package, sync
                        )
                        preview_binding = current_feishu_preview_binding(
                            package, draft_sha256, doctor
                        )
                        validate_push_operation_artifacts(
                            package,
                            pending_intent,
                            pending_intent_sha,
                            current_snapshot,
                            preview_binding,
                        )
            except (OSError, UnicodeDecodeError, json.JSONDecodeError, WorkflowError):
                pending_intent_invalid = True
            sync_for_route["pending_intent_missing"] = pending_intent_missing
            sync_for_route["pending_intent_invalid"] = pending_intent_invalid
            sync_for_route["pending_source_changed"] = pending_source_changed
            if pending_source_changed:
                workflow_blockers.append("pending_source_changed")
            if pending_intent_missing or pending_intent_invalid:
                workflow_blockers.append("pending_intent_invalid")
        if stored_sync_phase == "pull_prepared":
            pending = sync.get("pending") or {}
            pending_intent_missing = False
            pending_intent_invalid = False
            try:
                pending_intent_path = resolve_operation_file(
                    package,
                    pending.get("operation_id"),
                    pending.get("intent_path"),
                    "pending.intent_path",
                )
                pending_intent_missing = not pending_intent_path.is_file()
                if not pending_intent_missing:
                    load_pending_intent(package, sync)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError, WorkflowError):
                pending_intent_invalid = True
            sync_for_route["pending_intent_missing"] = pending_intent_missing
            sync_for_route["pending_intent_invalid"] = pending_intent_invalid
            if pending_intent_missing or pending_intent_invalid:
                workflow_blockers.append("pending_intent_invalid")
        if stored_sync_phase == "remote_dirty":
            candidate = sync.get("candidate") or {}
            if not local_payload_sha256 or local_payload_sha256 != candidate.get(
                "expected_local_sha256"
            ):
                sync_phase = "conflict"
                sync_for_route["conflict"] = {
                    "reason_code": "local_changed_after_staging"
                }

    sync_for_route["phase"] = sync_phase
    if sync_phase == "conflict":
        workflow_blockers.append("sync_conflict")
    if sync_phase == "result_unknown":
        workflow_blockers.append("external_result_unknown")
    if sync_phase == "push_in_flight":
        workflow_blockers.append("feishu_dispatch_in_flight")
    if (
        sync_phase in {"push_prepared", "pull_prepared"}
        and not doctor["capabilities"]["feishu_connector_connected"]
        and not sync_for_route.get("pending_source_changed")
        and not sync_for_route.get("pending_intent_missing")
        and not sync_for_route.get("pending_intent_invalid")
    ):
        workflow_blockers.append("feishu_trusted_executor_unavailable")
    if sync_phase == "local_dirty":
        workflow_blockers.append("safe_feishu_update_unavailable")
    warning_codes = (
        normalized_warning_codes(build.get("warning_codes")) if build else []
    )
    if warning_codes is None:
        warning_codes = []
        workflow_blockers.append("build_warning_codes_invalid")
    if lifecycle not in {"published", "archived"} and build:
        workflow_blockers.extend(warning_codes)
    if lifecycle not in {"published", "archived"} and build and build_stale:
        workflow_blockers.extend(integrity_issues)
    if (
        lifecycle not in {"published", "archived"}
        and sync_phase in {"pulled", "team_review_complete", "built", "sealed"}
        and build
        and not build_stale
        and build.get("local_format_qualified")
        and publish.get("delivery_mode")
        == doctor["qualification"]["required_delivery_mode"]
        and publish.get("layout_profile")
        == doctor["qualification"]["required_layout_profile"]
        and not current_company_format_qualified
    ):
        workflow_blockers.append("company_format_not_qualified")
    if (
        lifecycle not in {"published", "archived"}
        and sync_phase in {"pulled", "team_review_complete", "built", "sealed"}
        and build
        and not build_stale
        and current_company_format_qualified
        and not doctor["capabilities"]["wechat_create_draft"]
    ):
        workflow_blockers.append("wechat_draft_adapter_unavailable")

    next_action = choose_next_action(
        package,
        lifecycle,
        publish,
        sync_for_route,
        build_for_route,
        build_stale,
        bool(doctor["ok"]),
        bool(doctor["capabilities"]["feishu_connector_connected"]),
        bool(doctor["capabilities"]["wechat_create_draft"]),
    )
    pending = sync.get("pending") if isinstance(sync.get("pending"), dict) else {}
    conflict = sync_for_route.get("conflict")
    if not isinstance(conflict, dict):
        conflict = {}
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    return {
        "schema_version": SCHEMA_VERSION,
        "tool_version": TOOL_VERSION,
        "ok": not blockers and not workflow_blockers,
        "operational_ok": not blockers,
        "workflow_ready": not workflow_blockers,
        "package": {
            "path": str(package),
            "title": metadata.get("title"),
            "platform": metadata.get("platform"),
            "lifecycle_state": metadata.get("status"),
            "fact_checked": metadata.get("fact_checked"),
            "rights_checked": metadata.get("rights_checked"),
            "copyedit_checked": metadata.get("copyedit_checked"),
            "draft_sha256": draft_sha256,
        },
        "routing": {
            "project_adapter": publish.get("project_adapter"),
            "delivery_mode": publish.get("delivery_mode"),
            "layout_profile": publish.get("layout_profile"),
            "execution_route": "company_agent",
            "preview_delivery": "feishu_online_document",
        },
        "sync": {
            "protocol": sync.get("protocol"),
            "stored_phase": stored_sync_phase,
            "phase": sync_phase,
            "base_sha256": sync.get("base_sha256"),
            "local_sha256": local_payload_sha256,
            "remote_sha256": sync.get("remote_sha256"),
            "remote_revision_present": bool(sync.get("remote_revision")),
            "document_fingerprint": sync.get("document_fingerprint"),
            "document_url": sync.get("document_url"),
            "last_synced_at": sync.get("last_synced_at"),
            "pending": {
                "operation_id": pending.get("operation_id"),
                "kind": pending.get("kind"),
                "intent_path": pending.get("intent_path"),
                "intent_sha256": pending.get("intent_sha256"),
                "authorization_scope_sha256": pending.get("authorization_scope_sha256"),
                "sealed_build_sha256": pending.get("sealed_build_sha256"),
                "html_sha256": pending.get("html_sha256"),
                "source_changed": bool(sync_for_route.get("pending_source_changed")),
                "intent_missing": bool(sync_for_route.get("pending_intent_missing")),
            }
            if pending
            else None,
            "candidate_present": isinstance(sync.get("candidate"), dict),
            "conflict_reason": conflict.get("reason_code"),
        },
        "build": {
            "present": bool(build),
            "stale": build_stale,
            "profile_id": doctor["format"]["profile_id"],
            "profile_sha256": profile_sha256,
            "html_sha256": build.get("html_sha256"),
            "actual_html_sha256": actual_html_sha256,
            "sealed_build_sha256": build.get("sealed_build_sha256"),
            "integrity_issues": integrity_issues,
            "local_format_qualified": bool(
                build and not build_stale and build.get("local_format_qualified")
            ),
            "warning_codes": warning_codes,
        },
        "qualification": {
            "operational_ok": not blockers,
            "company_format_qualified": current_company_format_qualified,
            "wechat_roundtrip_qualified": doctor["qualification"][
                "wechat_roundtrip_qualified"
            ],
            "required_delivery_mode": doctor["qualification"]["required_delivery_mode"],
            "required_layout_profile": doctor["qualification"][
                "required_layout_profile"
            ],
            "wechat_account_fingerprint": doctor["qualification"][
                "wechat_account_fingerprint"
            ],
            "evidence_id": doctor["qualification"]["evidence_id"],
            "evidence_receipt_verified": doctor["qualification"][
                "evidence_receipt_verified"
            ],
            "binding_issues": doctor["qualification"]["binding_issues"],
        },
        "capabilities": doctor["capabilities"],
        "external_writes_performed": False,
        "blockers": sorted(set([*blockers, *workflow_blockers])),
        "tool_blockers": blockers,
        "workflow_blockers": sorted(set(workflow_blockers)),
        "warnings": warnings,
        "next_action": next_action,
        "elapsed_ms": elapsed_ms,
    }


def build_report(package_value: str | None) -> dict[str, Any]:
    started = time.perf_counter()
    package = resolve_package(package_value)
    doctor = doctor_report()
    if not doctor["ok"]:
        raise WorkflowError(
            "doctor failed: " + "; ".join(str(item) for item in doctor["blockers"])
        )
    metadata, body, draft_raw = read_draft(package / "draft.md")
    publish = read_publish(package)
    title = str(metadata.get("title") or "").strip()
    if not title:
        raise WorkflowError("draft.md frontmatter title is required")
    if metadata.get("platform") != "wechat":
        raise WorkflowError("company HTML build currently supports platform: wechat")
    if publish.get("project_adapter") != "appsso":
        raise WorkflowError(
            "publish.yml must declare project_adapter: appsso for this company profile"
        )
    profile, profile_sha256 = load_profile()
    rendered = render_locked_article(
        package=package,
        repo_root=REPO_ROOT,
        profile=profile,
        title=title,
        body=body,
        draft_raw=draft_raw,
    )
    format_state = doctor["format"]
    executed_hashes = {
        "renderer_sha256": rendered["renderer_sha256"],
        "bridge_sha256": rendered["bridge_sha256"],
        "title_image_sha256": rendered["title_image_sha256"],
    }
    for field, actual in executed_hashes.items():
        if actual != format_state.get(field):
            raise WorkflowError(f"executed format source differs from doctor: {field}")
    fixture = rendered["fixture"]
    html_bytes = rendered["html_bytes"]
    html_sha256 = rendered["html_sha256"]
    draft_sha256 = rendered["draft_sha256"]
    fidelity_blockers = list(rendered["fidelity_blockers"])
    warning_codes = list(rendered["warning_codes"])
    local_format_qualified = bool(rendered["local_format_qualified"])
    seal_material = {
        "draft_sha256": draft_sha256,
        "format_profile_sha256": format_state["format_profile_sha256"],
        "adapter_sha256": format_state["adapter_sha256"],
        "bridge_sha256": format_state["bridge_sha256"],
        "renderer_sha256": format_state["renderer_sha256"],
        "format_contract_sha256": format_state["format_contract_sha256"],
        "style_version": format_state["style_version"],
        "html_sha256": html_sha256,
        "title_image_sha256": format_state["title_image_sha256"],
        "local_format_qualified": local_format_qualified,
        "warning_codes": warning_codes,
    }
    sealed_build_sha256 = sha256_bytes(canonical_json(seal_material))
    qualification = doctor["qualification"]
    company_format_qualified = bool(
        local_format_qualified
        and qualification.get("production_qualified", False)
        and publish.get("delivery_mode") == qualification.get("required_delivery_mode")
        and publish.get("layout_profile")
        == qualification.get("required_layout_profile")
    )
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "tool_version": TOOL_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "package": str(package),
        "title": title,
        "draft_sha256": draft_sha256,
        "profile_id": profile.get("profile_id"),
        "profile_sha256": profile_sha256,
        "format_profile_sha256": format_state["format_profile_sha256"],
        "adapter_sha256": format_state["adapter_sha256"],
        "bridge_sha256": format_state["bridge_sha256"],
        "format_contract_sha256": format_state["format_contract_sha256"],
        "renderer_sha256": format_state["renderer_sha256"],
        "title_image_sha256": format_state["title_image_sha256"],
        "style_version": format_state["style_version"],
        "html_path": HTML_RELATIVE_PATH.as_posix(),
        "html_sha256": html_sha256,
        "payload_sha256": rendered["payload_sha256"],
        "fixture_sha256": rendered["fixture_sha256"],
        "sealed_build_sha256": sealed_build_sha256,
        "block_count": fixture.get("blockCount"),
        "article_image_bytes": rendered["article_image_bytes"],
        "image_count": fixture.get("imageCount"),
        "gallery_count": fixture.get("galleryCount"),
        "text_fidelity": fixture.get("textFidelity"),
        "image_fidelity": fixture.get("imageFidelity"),
        "warning_counts": {
            "gif": len(fixture.get("gifWarnings", [])),
            "media": len(fixture.get("mediaWarnings", [])),
            "content": len(fixture.get("contentWarnings", [])),
        },
        "warning_codes": warning_codes,
        "local_format_qualified": local_format_qualified,
        "company_format_qualified": company_format_qualified,
        "qualification_blockers": [
            *fidelity_blockers,
            *([] if company_format_qualified else ["wechat_roundtrip_not_qualified"]),
            *qualification.get("binding_issues", []),
        ],
        "external_writes_performed": False,
    }
    atomic_write(package / HTML_RELATIVE_PATH, html_bytes)
    atomic_write(
        package / BUILD_RELATIVE_PATH,
        json.dumps(receipt, ensure_ascii=False, indent=2).encode("utf-8") + b"\n",
    )
    receipt["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 2)
    return receipt


def print_human(report: dict[str, Any], command: str) -> None:
    if command == "connector-doctor":
        connector = report["connectors"]["feishu_remote_mcp"]
        print(
            f"飞书 Remote MCP 配置："
            f"{'有效' if connector['config_valid'] else '未就绪'}；"
            f"凭据环境变量："
            f"{'已设置' if connector['credential_env_present'] else '未设置'}；"
            f"可信执行器："
            f"{'已接入' if connector['trusted_executor_available'] else '未接入'}"
        )
        return
    if command == "doctor":
        print(
            f"工具：{'可用' if report['ok'] else '阻断'}；"
            f"Profile：{report['format'].get('profile_id')}；"
            f"耗时：{report['elapsed_ms']} ms"
        )
        if report["blockers"]:
            for item in report["blockers"]:
                print(f"- 阻断：{item}")
        for item in report["warnings"]:
            print(f"- 提醒：{item}")
        return
    if command == "status":
        next_action = report["next_action"]
        print(
            f"{report['package'].get('title') or '未命名内容'} | "
            f"{report['package'].get('lifecycle_state') or 'unknown'} | "
            f"{report['sync'].get('phase')}"
        )
        print(f"下一步：{next_action['id']}——{next_action['reason']}")
        if next_action.get("command"):
            print("命令：" + json.dumps(next_action["command"], ensure_ascii=False))
        elif next_action.get("command_template"):
            print(
                "命令模板："
                + json.dumps(next_action["command_template"], ensure_ascii=False)
            )
        if report["sync"].get("document_url"):
            print(f"飞书预览：{report['sync']['document_url']}")
        print(f"耗时：{report['elapsed_ms']} ms")
        return
    if command == "configure-company":
        print(
            f"公司路由：{'已补齐' if report['changed'] else '已存在'}；"
            f"publish.yml：{report['publish_path']}；"
            f"耗时：{report['elapsed_ms']} ms"
        )
        return
    if command == "build":
        print(
            f"已生成：{report['html_path']}；"
            f"本地格式校验：{'通过' if report['local_format_qualified'] else '未通过'}；"
            f"耗时：{report['elapsed_ms']} ms"
        )
        if not report["company_format_qualified"]:
            print("生产资格：未取得；不得据此自动创建或发布公众号草稿。")
        return
    phase = report.get("phase")
    operation_id = report.get("operation_id")
    print(
        f"飞书协议：{phase or report.get('operation') or 'prepared'}；"
        f"operation：{operation_id or 'n/a'}；"
        f"耗时：{report.get('elapsed_ms')} ms"
    )
    if report.get("intent_path"):
        print(f"意图：{report['intent_path']}")
    if report.get("document_url"):
        print(f"飞书预览：{report['document_url']}")


def add_package_argument(command: argparse.ArgumentParser) -> None:
    command.add_argument(
        "package",
        nargs="?",
        help="内容包目录；省略时从当前目录向上寻找 draft.md",
    )
    command.add_argument("--json", action="store_true", dest="as_json")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description="公司内容协作与固定排版的轻量 Agent 入口"
    )
    command_help = {
        "status": "只读汇总并返回唯一下一动作",
        "build": "用锁定 Profile 生成本地密封 HTML",
        "configure-company": "只补安全的公司手工交付路由",
        "feishu-prepare-push": "生成不联网的飞书新建意图",
        "feishu-begin-push": "取得精确授权后消费一次性派发 claim",
        "feishu-commit-push": "验证飞书写入与读回白名单回执",
        "feishu-prepare-pull": "生成不联网的飞书读取意图",
        "feishu-stage-pull": "验证读回并暂存团队候选正文",
        "feishu-accept-pull": "显式接受候选正文并重开编辑门禁",
        "doctor": "验证本机依赖、格式真源和生产资格",
        "connector-doctor": "只读检查飞书 Remote MCP 本机配置",
    }
    subparsers = root.add_subparsers(dest="command", required=True)
    for name in (
        "status",
        "build",
        "configure-company",
        "feishu-prepare-pull",
        "feishu-accept-pull",
    ):
        add_package_argument(
            subparsers.add_parser(
                name, help=command_help[name], description=command_help[name]
            )
        )

    prepare_push = subparsers.add_parser(
        "feishu-prepare-push", help=command_help["feishu-prepare-push"]
    )
    add_package_argument(prepare_push)
    prepare_push.add_argument("--tenant-fingerprint", required=True)
    prepare_push.add_argument(
        "--parent-id",
        default=FEISHU_DEFAULT_PARENT_ID,
        help=(
            "Feishu create target. Defaults to my_library, which maps to "
            "create-doc wiki_space=my_library."
        ),
    )

    begin_push = subparsers.add_parser(
        "feishu-begin-push", help=command_help["feishu-begin-push"]
    )
    add_package_argument(begin_push)
    begin_push.add_argument("--operation-id", required=True)
    begin_push.add_argument("--authorization-scope", required=True)

    for name in ("feishu-commit-push", "feishu-stage-pull"):
        command = subparsers.add_parser(
            name, help=command_help[name], description=command_help[name]
        )
        add_package_argument(command)
        command.add_argument(
            "--receipt",
            required=True,
            help="对应 operation 目录内的白名单回执 JSON",
        )

    doctor = subparsers.add_parser(
        "doctor", help=command_help["doctor"], description=command_help["doctor"]
    )
    doctor.add_argument("--json", action="store_true", dest="as_json")
    connector_doctor = subparsers.add_parser(
        "connector-doctor",
        help=command_help["connector-doctor"],
        description=command_help["connector-doctor"],
    )
    connector_doctor.add_argument("--json", action="store_true", dest="as_json")
    return root


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    try:
        if arguments.command == "doctor":
            report = doctor_report()
        elif arguments.command == "connector-doctor":
            report = connector_doctor_report()
        elif arguments.command == "status":
            report = status_report(arguments.package)
        elif arguments.command == "build":
            report = build_report(arguments.package)
        elif arguments.command == "configure-company":
            report = configure_company_report(arguments.package)
        elif arguments.command == "feishu-prepare-push":
            report = feishu_prepare_push_report(
                arguments.package,
                arguments.tenant_fingerprint,
                arguments.parent_id,
            )
        elif arguments.command == "feishu-begin-push":
            report = feishu_begin_push_report(
                arguments.package,
                arguments.operation_id,
                arguments.authorization_scope,
            )
        elif arguments.command == "feishu-commit-push":
            report = feishu_commit_push_report(arguments.package, arguments.receipt)
        elif arguments.command == "feishu-prepare-pull":
            report = feishu_prepare_pull_report(arguments.package)
        elif arguments.command == "feishu-stage-pull":
            report = feishu_stage_pull_report(arguments.package, arguments.receipt)
        elif arguments.command == "feishu-accept-pull":
            report = feishu_accept_pull_report(arguments.package)
        else:
            raise WorkflowError(f"unsupported command: {arguments.command}")
    except (OSError, subprocess.SubprocessError, WorkflowError) as exc:
        error = {
            "schema_version": SCHEMA_VERSION,
            "tool_version": TOOL_VERSION,
            "ok": False,
            "error": str(exc),
            "external_writes_performed": False,
        }
        if getattr(arguments, "as_json", False):
            print(json.dumps(error, ensure_ascii=False, indent=2))
        else:
            print(f"阻断：{exc}", file=sys.stderr)
        return 2

    if getattr(arguments, "as_json", False):
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report, arguments.command)
    if arguments.command == "status":
        return 0 if report.get("operational_ok", False) else 1
    return 0 if report.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
