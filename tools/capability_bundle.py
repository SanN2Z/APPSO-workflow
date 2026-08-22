#!/usr/bin/env python3
"""Prepare and inspect every repository-packaged workflow capability.

The bundle includes executable adapters, pinned dependencies, configuration
templates, versioned company tools, and safe import slots. Secret values,
browser sessions, and governed local-only source assets are injected locally
after cloning and are never printed by this tool.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = Path(__file__).with_name("workflow-toolchain.json")
PLACEHOLDER_MARKERS = (
    "<local-only>",
    "replace_with_",
    "your_",
    "changeme",
    "placeholder",
)


class CapabilityError(RuntimeError):
    """Raised when a capability bundle contract cannot be satisfied."""


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CapabilityError(f"expected JSON object: {path}")
    return value


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    manifest = read_json(path)
    if manifest.get("schema_version") != 2:
        raise CapabilityError("workflow-toolchain schema_version must be 2")
    return manifest


def repo_path(value: str, root: Path = REPO_ROOT) -> Path:
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise CapabilityError(f"path escapes repository: {value}") from exc
    return candidate


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def parse_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        key = key.strip()
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            values[key] = raw_value.strip().strip('"').strip("'")
    return values


def configured_value(value: str | None) -> bool:
    if not value:
        return False
    lowered = value.strip().lower()
    return bool(lowered) and not any(marker in lowered for marker in PLACEHOLDER_MARKERS)


def extract_prompt(path: Path, heading: str) -> str:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == heading)
    except StopIteration as exc:
        raise CapabilityError(f"missing governed prompt heading {heading!r}: {path}") from exc
    prompt_lines: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        stripped = line.strip()
        if not stripped:
            continue
        prompt_lines.append(re.sub(r"^>\s?", "", stripped))
    prompt = "\n".join(prompt_lines).strip()
    if not prompt:
        raise CapabilityError(f"governed prompt is empty: {path}")
    return prompt


def private_asset_status(
    asset: dict[str, Any], *, root: Path = REPO_ROOT
) -> dict[str, Any]:
    destination = repo_path(str(asset["destination"]), root)
    result: dict[str, Any] = {
        "id": str(asset["id"]),
        "present": destination.is_file(),
        "valid": False,
        "destination": str(asset["destination"]),
    }
    if not destination.is_file():
        return result
    try:
        prompt = extract_prompt(destination, str(asset["prompt_heading"]))
        actual = sha256_text(prompt)
        result["valid"] = actual == str(asset["prompt_sha256"]).lower()
    except (OSError, UnicodeError, CapabilityError):
        result["valid"] = False
    return result


def copy_template_if_missing(
    item: dict[str, Any], *, root: Path = REPO_ROOT
) -> dict[str, Any]:
    template = repo_path(str(item["template"]), root)
    destination = repo_path(str(item["destination"]), root)
    if not template.is_file():
        raise CapabilityError(f"configuration template is missing: {item['template']}")
    if destination.exists():
        return {"id": item["id"], "status": "existing", "path": item["destination"]}
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template, destination)
    return {"id": item["id"], "status": "created", "path": item["destination"]}


def prepare_local_configs(
    manifest: dict[str, Any], *, root: Path = REPO_ROOT
) -> list[dict[str, Any]]:
    return [
        copy_template_if_missing(item, root=root)
        for item in manifest["local_config_templates"]
    ]


def config_status(item: dict[str, Any], *, root: Path = REPO_ROOT) -> dict[str, Any]:
    destination = repo_path(str(item["destination"]), root)
    result: dict[str, Any] = {
        "id": str(item["id"]),
        "present": destination.is_file(),
        "configured": False,
        "path": str(item["destination"]),
        "required_keys": list(item.get("required_keys", [])),
        "configured_keys": [],
    }
    if not destination.is_file():
        return result
    if item.get("format") == "dotenv":
        values = parse_dotenv(destination)
        configured_keys = [
            key
            for key in item.get("required_keys", [])
            if configured_value(os.environ.get(key) or values.get(key))
        ]
        result["configured_keys"] = configured_keys
        result["configured"] = len(configured_keys) == len(item.get("required_keys", []))
    else:
        result["configured"] = True
    return result


def windows_browser_available() -> bool:
    if os.name != "nt":
        return bool(shutil.which("google-chrome") or shutil.which("chromium"))
    candidates: list[Path] = []
    for variable in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
        base = os.environ.get(variable)
        if not base:
            continue
        candidates.extend(
            [
                Path(base) / "Google/Chrome/Application/chrome.exe",
                Path(base) / "Microsoft/Edge/Application/msedge.exe",
            ]
        )
    return any(path.is_file() for path in candidates)


def host_tool_status(item: dict[str, Any], *, root: Path = REPO_ROOT) -> dict[str, Any]:
    kind = str(item["kind"])
    available: bool | None
    if kind == "local_binary":
        available = repo_path(str(item["path"]), root).is_file()
    elif kind == "windows_browser":
        available = windows_browser_available()
    elif kind == "agent_capability":
        available = None
    else:
        raise CapabilityError(f"unsupported host tool kind: {kind}")
    return {
        "id": str(item["id"]),
        "kind": kind,
        "available": available,
        "version": item.get("version"),
    }


def known_entrypoints(manifest: dict[str, Any]) -> set[str]:
    return set(manifest["entrypoints"]) | set(manifest["powershell_entrypoints"])


def bundle_report(
    manifest: dict[str, Any],
    *,
    root: Path = REPO_ROOT,
    include_runtime: bool = True,
    strict_runtime: bool = False,
) -> dict[str, Any]:
    entrypoints = known_entrypoints(manifest)
    configs = {
        item["id"]: config_status(item, root=root)
        for item in manifest["local_config_templates"]
    }
    private_assets = {
        item["id"]: private_asset_status(item, root=root)
        for item in manifest["private_assets"]
    }
    host_tools = {
        item["id"]: host_tool_status(item, root=root)
        for item in manifest["host_tools"]
    }
    capabilities: list[dict[str, Any]] = []
    for item in manifest["capability_bundles"]:
        missing_entrypoints = sorted(set(item.get("entrypoints", [])) - entrypoints)
        missing_paths = [
            value
            for value in item.get("tracked_paths", [])
            if not repo_path(str(value), root).exists()
        ]
        bundle_ok = (
            item.get("bundle_status") == "complete"
            and not missing_entrypoints
            and not missing_paths
        )
        config_items: list[dict[str, Any]] = []
        for requirement in item.get("config_requirements", []):
            config_item = dict(configs[requirement["id"]])
            required_keys = list(
                requirement.get("keys", config_item.get("required_keys", []))
            )
            config_item["required_keys"] = required_keys
            config_item["configured_keys"] = [
                key for key in config_item["configured_keys"] if key in required_keys
            ]
            config_item["configured"] = config_item["present"] and all(
                key in config_item["configured_keys"] for key in required_keys
            )
            config_items.append(config_item)
        private_items = [
            private_assets[value] for value in item.get("private_asset_ids", [])
        ]
        host_items = [host_tools[value] for value in item.get("host_tool_ids", [])]
        runtime_checks: list[bool] = [entry["configured"] for entry in config_items]
        runtime_checks.extend(entry["valid"] for entry in private_items)
        runtime_checks.extend(entry["available"] is True for entry in host_items)
        runtime_ready = bundle_ok and all(runtime_checks)
        capabilities.append(
            {
                "id": item["id"],
                "bundle_ok": bundle_ok,
                "runtime_ready": runtime_ready if include_runtime else None,
                "missing_entrypoints": missing_entrypoints,
                "missing_paths": missing_paths,
                "configs": config_items if include_runtime else [],
                "private_assets": private_items if include_runtime else [],
                "host_tools": host_items if include_runtime else [],
            }
        )
    bundle_ok = all(item["bundle_ok"] for item in capabilities)
    runtime_ready = all(item["runtime_ready"] for item in capabilities) if include_runtime else None
    return {
        "schema_version": 1,
        "contract_id": manifest["contract_id"],
        "ok": bool(runtime_ready) if strict_runtime else bundle_ok,
        "bundle_ok": bundle_ok,
        "runtime_ready": runtime_ready,
        "strict_runtime": strict_runtime,
        "capabilities": capabilities,
    }


def find_private_asset_source(source_root: Path, filename: str) -> Path:
    direct = source_root / filename
    if direct.is_file():
        return direct
    matches = [path for path in source_root.rglob(filename) if path.is_file()]
    if len(matches) != 1:
        raise CapabilityError(
            f"expected exactly one {filename!r} under {source_root}; found {len(matches)}"
        )
    return matches[0]


def import_private_assets(
    manifest: dict[str, Any], source_root: Path, *, root: Path = REPO_ROOT
) -> list[dict[str, Any]]:
    source_root = source_root.resolve()
    if not source_root.is_dir():
        raise CapabilityError(f"private asset source root does not exist: {source_root}")
    results: list[dict[str, Any]] = []
    for item in manifest["private_assets"]:
        source = find_private_asset_source(source_root, str(item["source_filename"]))
        prompt = extract_prompt(source, str(item["prompt_heading"]))
        actual = sha256_text(prompt)
        expected = str(item["prompt_sha256"]).lower()
        if actual != expected:
            raise CapabilityError(
                f"private asset hash mismatch for {item['id']}: expected {expected}; actual {actual}"
            )
        destination = repo_path(str(item["destination"]), root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.is_file():
            existing = sha256_text(extract_prompt(destination, str(item["prompt_heading"])))
            if existing != expected:
                raise CapabilityError(
                    f"existing private asset is different; refusing overwrite: {item['destination']}"
                )
            status = "existing"
        else:
            shutil.copy2(source, destination)
            status = "imported"
        results.append(
            {"id": item["id"], "status": status, "destination": item["destination"]}
        )
    return results


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def print_report(report: dict[str, Any]) -> None:
    for item in report["capabilities"]:
        bundle_label = "PACKED" if item["bundle_ok"] else "MISSING"
        runtime_label = (
            "ready"
            if item["runtime_ready"] is True
            else "local input needed"
            if item["runtime_ready"] is False
            else "not checked"
        )
        print(f"[{bundle_label}] {item['id']}: {runtime_label}")
    if report["bundle_ok"]:
        print("ALL CAPABILITY ADAPTERS PACKAGED")
    else:
        print("CAPABILITY BUNDLE INCOMPLETE")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="Create missing local config files from tracked templates.")
    prepare.add_argument("--json", action="store_true")

    doctor = subparsers.add_parser("doctor", help="Inspect packaged and locally configured capability status.")
    doctor.add_argument("--json", action="store_true")
    doctor.add_argument("--bundle-only", action="store_true")
    doctor.add_argument("--strict-runtime", action="store_true")

    listing = subparsers.add_parser("list", help="List all capability bundles without requiring local inputs.")
    listing.add_argument("--json", action="store_true")

    extension = subparsers.add_parser("extension-path", help="Print the tracked company Chrome extension path.")
    extension.add_argument("--json", action="store_true")

    importer = subparsers.add_parser("import-private-assets", help="Hash-check and import governed local-only assets.")
    importer.add_argument("--source-root", required=True)
    importer.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        manifest = load_manifest()
        if args.command == "prepare":
            result = {"ok": True, "configs": prepare_local_configs(manifest)}
            print_json(result) if args.json else [
                print(f"[{item['status'].upper()}] {item['id']}: {item['path']}")
                for item in result["configs"]
            ]
            return 0
        if args.command in {"doctor", "list"}:
            include_runtime = args.command == "doctor" and not args.bundle_only
            strict_runtime = bool(getattr(args, "strict_runtime", False))
            report = bundle_report(
                manifest,
                include_runtime=include_runtime,
                strict_runtime=strict_runtime,
            )
            print_json(report) if args.json else print_report(report)
            return 0 if report["ok"] else 1
        if args.command == "extension-path":
            path = repo_path(manifest["company_extension"]["load_path"])
            result = {"ok": path.is_dir(), "path": str(path)}
            print_json(result) if args.json else print(path)
            return 0 if result["ok"] else 1
        if args.command == "import-private-assets":
            imported = import_private_assets(manifest, Path(args.source_root))
            result = {"ok": True, "assets": imported}
            print_json(result) if args.json else [
                print(f"[{item['status'].upper()}] {item['id']}: {item['destination']}")
                for item in imported
            ]
            return 0
        raise CapabilityError(f"unsupported command: {args.command}")
    except Exception as exc:  # noqa: BLE001 - CLI must return a concise failure
        if getattr(args, "json", False):
            print_json({"ok": False, "error": str(exc)})
        else:
            print(f"[FAIL] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
