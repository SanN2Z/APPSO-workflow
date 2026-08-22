from __future__ import annotations

import hashlib
import importlib.util
import tempfile
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "capability_bundle.py"
SPEC = importlib.util.spec_from_file_location("capability_bundle", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def minimal_manifest() -> dict:
    return {
        "schema_version": 2,
        "contract_id": "CORE-PORTABILITY-001",
        "entrypoints": {"demo": "tools/demo.py"},
        "powershell_entrypoints": {},
        "local_config_templates": [
            {
                "id": "demo_config",
                "format": "dotenv",
                "template": ".env.example",
                "destination": ".env",
                "required_keys": ["DEMO_SECRET"],
            }
        ],
        "private_assets": [],
        "host_tools": [],
        "capability_bundles": [
            {
                "id": "demo",
                "bundle_status": "complete",
                "entrypoints": ["demo"],
                "tracked_paths": ["tools/demo.py"],
                "config_requirements": [
                    {"id": "demo_config", "keys": ["DEMO_SECRET"]}
                ],
                "private_asset_ids": [],
                "host_tool_ids": [],
            }
        ],
    }


def test_prepare_templates_is_idempotent_and_never_overwrites() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        (root / ".env.example").write_text(
            "DEMO_SECRET=<local-only>\n", encoding="utf-8"
        )
        manifest = minimal_manifest()

        first = MODULE.prepare_local_configs(manifest, root=root)
        assert first[0]["status"] == "created"
        destination = root / ".env"
        destination.write_text("DEMO_SECRET=live-value\n", encoding="utf-8")

        second = MODULE.prepare_local_configs(manifest, root=root)
        assert second[0]["status"] == "existing"
        assert destination.read_text(encoding="utf-8") == "DEMO_SECRET=live-value\n"


def test_bundle_report_separates_packaged_from_local_runtime_inputs() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        (root / "tools").mkdir()
        (root / "tools/demo.py").write_text("print('ok')\n", encoding="utf-8")
        (root / ".env.example").write_text(
            "DEMO_SECRET=<local-only>\n", encoding="utf-8"
        )
        manifest = minimal_manifest()

        report = MODULE.bundle_report(manifest, root=root)
        assert report["ok"] is True
        assert report["bundle_ok"] is True
        assert report["runtime_ready"] is False

        MODULE.prepare_local_configs(manifest, root=root)
        (root / ".env").write_text("DEMO_SECRET=ready\n", encoding="utf-8")
        strict = MODULE.bundle_report(manifest, root=root, strict_runtime=True)
        assert strict["ok"] is True
        assert strict["runtime_ready"] is True


def test_import_private_assets_hash_checks_and_refuses_wrong_source() -> None:
    prompt = "one exact governed prompt"
    expected_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "repo"
        source_root = Path(temp_dir) / "source"
        root.mkdir()
        source_root.mkdir()
        source = source_root / "governed.md"
        source.write_text(
            f"# Asset\n\n## Original Prompt\n\n> {prompt}\n", encoding="utf-8"
        )
        manifest = minimal_manifest()
        manifest["private_assets"] = [
            {
                "id": "governed",
                "source_filename": "governed.md",
                "destination": "private/governed.md",
                "prompt_heading": "## Original Prompt",
                "prompt_sha256": expected_hash,
            }
        ]

        imported = MODULE.import_private_assets(manifest, source_root, root=root)
        assert imported == [
            {
                "id": "governed",
                "status": "imported",
                "destination": "private/governed.md",
            }
        ]
        assert MODULE.private_asset_status(
            manifest["private_assets"][0], root=root
        )["valid"] is True

        source.write_text(
            "# Asset\n\n## Original Prompt\n\n> changed\n", encoding="utf-8"
        )
        (root / "private/governed.md").unlink()
        with pytest.raises(MODULE.CapabilityError, match="hash mismatch"):
            MODULE.import_private_assets(manifest, source_root, root=root)


def test_repository_manifest_registers_all_platform_and_host_routes() -> None:
    manifest = MODULE.load_manifest()
    commands = set(manifest["entrypoints"]) | set(manifest["powershell_entrypoints"])
    assert {
        "wechat",
        "company",
        "capabilities",
        "x-post",
        "x-trend-scan",
        "codex-company",
        "codex-company-feishu",
        "claude-ox",
        "openrouter",
        "image-preflight",
    } <= commands
    assert all(
        item["bundle_status"] == "complete"
        for item in manifest["capability_bundles"]
    )
    assert manifest["company_extension"]["load_path"].endswith("/extension")
