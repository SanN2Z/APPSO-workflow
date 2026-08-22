# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import hashlib
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_content_package.py"
WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
SPEC = importlib.util.spec_from_file_location("validate_content_package", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load validator: {SCRIPT_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)

PREFLIGHT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "preflight_image_generation.py"
)
PREFLIGHT_SPEC = importlib.util.spec_from_file_location(
    "preflight_image_generation_for_validator_tests",
    PREFLIGHT_PATH,
)
if PREFLIGHT_SPEC is None or PREFLIGHT_SPEC.loader is None:
    raise RuntimeError(f"Could not load image preflight: {PREFLIGHT_PATH}")
PREFLIGHT = importlib.util.module_from_spec(PREFLIGHT_SPEC)
sys.modules[PREFLIGHT_SPEC.name] = PREFLIGHT
PREFLIGHT_SPEC.loader.exec_module(PREFLIGHT)


class ProgressivePackageRequirementTests(unittest.TestCase):
    def make_package(self, root: Path, status: str) -> Path:
        package = root / "package"
        package.mkdir()
        draft = f"""---
title: "Lean package"
platform: wechat
status: {status}
created: 2026-07-25
updated: 2026-07-25
as_of: 2026-07-25
fact_checked: false
rights_checked: false
copyedit_checked: false
copyedit_body_sha256: ""
published_url: ""
---
# Lean package
"""
        (package / "draft.md").write_text(draft, encoding="utf-8")
        return package

    def add_sources(self, package: Path) -> None:
        (package / "sources.md").write_text(
            "- https://example.com — 访问日期：2026-07-25\n",
            encoding="utf-8",
        )

    def test_idea_only_requires_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(Path(temp_dir), "idea")
            errors, warnings, image_count = VALIDATOR.validate(package)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])
            self.assertEqual(image_count, 0)

    def test_draft_requires_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(Path(temp_dir), "draft")
            errors, _, _ = VALIDATOR.validate(package)
            self.assertIn("missing required file for draft: sources.md", errors)

    def test_draft_does_not_require_release_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(Path(temp_dir), "draft")
            self.add_sources(package)
            errors, warnings, _ = VALIDATOR.validate(package)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_ready_requires_release_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(Path(temp_dir), "ready")
            self.add_sources(package)
            errors, _, _ = VALIDATOR.validate(package)
            for name in ("review.md", "copyedit.md", "asset-manifest.yml"):
                self.assertIn(f"missing required file for ready: {name}", errors)


class ContentPackageAssetManifestTests(unittest.TestCase):
    APPSO_PROMPT_SHA256 = (
        "6ba5e092a4f8d6fb2bd33602424ba4792715aa59f2bf5f916b90d8bb3f0bbd0a"
    )
    INVOCATION_PROMPT_SHA256 = "b" * 64
    APPSO_RECEIPT = "research/image-generation-runs/output-final-preflight.json"

    def make_package(
        self,
        root: Path,
        manifest: str,
        *,
        status: str = "ready",
        markdown_image: bool = True,
        project_adapter: str | None = "generic",
    ) -> Path:
        workspace = root / "workspace"
        (workspace / "AGENTS.md").parent.mkdir(parents=True, exist_ok=True)
        (workspace / "AGENTS.md").write_text("# Test workspace\n", encoding="utf-8")
        (workspace / "上下文").mkdir(exist_ok=True)
        (workspace / "共享").mkdir(exist_ok=True)
        (workspace / "config").mkdir(exist_ok=True)
        package = workspace / "package"
        (package / "assets").mkdir(parents=True)
        (package / "research" / "source-assets").mkdir(parents=True)
        if 'file: "assets/output.png"' in manifest:
            (package / "assets" / "output.png").write_bytes(b"test-image")
        if 'file: "research/source-assets/reference.png"' in manifest:
            (package / "research" / "source-assets" / "reference.png").write_bytes(
                b"test-reference"
            )

        body = "# Test\n"
        if markdown_image:
            body += "\n![AI test image](assets/output.png)\n"
        draft_template = """---
title: "Test"
platform: wechat
status: {status}
created: 2026-07-21
updated: 2026-07-21
as_of: 2026-07-21
fact_checked: {checked}
rights_checked: {checked}
copyedit_checked: {checked}
copyedit_body_sha256: "{declared_hash}"
published_url: ""
---
{body}"""
        checked = "true" if status in {"ready", "published"} else "false"
        preliminary = draft_template.format(
            status=status,
            checked=checked,
            declared_hash="",
            body=body,
        )
        body_hash = VALIDATOR.copyedit_body_sha256(preliminary)
        draft = draft_template.format(
            status=status,
            checked=checked,
            declared_hash=body_hash if checked == "true" else "",
            body=body,
        )
        (package / "draft.md").write_text(draft, encoding="utf-8")
        (package / "brief.md").write_text("# Brief\n", encoding="utf-8")
        (package / "sources.md").write_text(
            "- https://example.com — 访问日期：2026-07-21\n",
            encoding="utf-8",
        )
        (package / "review.md").write_text(
            "# Review\n\n"
            "## AI-pattern diagnostic\n\n"
            "- Skill: avoid-ai-writing test fixture\n"
            "- Mode: detect\n"
            "- Status: pass\n"
            "- Finding: none found\n",
            encoding="utf-8",
        )
        (package / "publish-record.md").write_text("# Publish record\n", encoding="utf-8")
        copyedit_status = "pass" if checked == "true" else "needs_fix"
        (package / "copyedit.md").write_text(
            "---\n"
            f"status: {copyedit_status}\n"
            'checked_at: "2026-07-21 12:00:00+09:00"\n'
            f'body_sha256: "{body_hash}"\n'
            'scope: "test"\n'
            "---\n",
            encoding="utf-8",
        )
        (package / "asset-manifest.yml").write_text(manifest, encoding="utf-8")
        if project_adapter is not None:
            (package / "publish.yml").write_text(
                f'project_adapter: "{project_adapter}"\nlayout_profile: "default"\n',
                encoding="utf-8",
            )
        return package

    def set_body(self, package: Path, body: str) -> None:
        draft_path = package / "draft.md"
        draft = draft_path.read_text(encoding="utf-8")
        _, old_body = VALIDATOR.split_frontmatter(draft, "draft.md")
        old_hash = VALIDATOR.parse_frontmatter(draft, "draft.md").get(
            "copyedit_body_sha256", ""
        )
        updated = draft[: len(draft) - len(old_body)] + body
        new_hash = VALIDATOR.copyedit_body_sha256(updated)
        updated = re.sub(
            r'(?m)^copyedit_body_sha256: "[^"]*"$',
            f'copyedit_body_sha256: "{new_hash}"',
            updated,
        )
        draft_path.write_text(updated, encoding="utf-8")

        copyedit_path = package / "copyedit.md"
        copyedit = copyedit_path.read_text(encoding="utf-8")
        if old_hash:
            copyedit = copyedit.replace(old_hash, new_hash)
        else:
            copyedit = re.sub(
                r'(?m)^body_sha256: "[^"]*"$',
                f'body_sha256: "{new_hash}"',
                copyedit,
            )
        copyedit_path.write_text(copyedit, encoding="utf-8")

    def write_appsso_receipt(
        self,
        package: Path,
        *,
        overrides: dict[str, object] | None = None,
    ) -> Path:
        receipt = {
            "schema_version": 1,
            "status": "pass",
            "stage": "final",
            "style_profile": "appsso-004",
            "prompt_ref": "appsso-004",
            "prompt_sha256": self.APPSO_PROMPT_SHA256,
            "invocation_prompt_sha256": self.INVOCATION_PROMPT_SHA256,
            "mode": "referenced_edit",
            "input_assets": ["research\\source-assets\\reference.png"],
            "output": "assets/output.png",
        }
        if overrides:
            receipt.update(overrides)
        receipt_path = package / self.APPSO_RECEIPT
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return receipt_path

    def install_generic_preflight_contract(
        self,
        package: Path,
        *,
        edit: bool,
    ) -> dict[str, object]:
        """Create a real preflight plan/registry/receipt, then bind the manifest."""

        profile_id = "generic-edit" if edit else "generic-direct"
        strategy = "reference_required" if edit else "direct"
        mode = "referenced_edit" if edit else "text_to_image"
        reference_strategy = "provided_local" if edit else "none"
        input_assets = ["research/source-assets/reference.png"] if edit else []
        workspace = package.parent
        registry = {
            "schema_version": 1,
            "profiles": {
                profile_id: {
                    "classification": "internal",
                    "requires_reference": edit,
                    "allowed_final_modes": [mode],
                    "new_image_strategy": strategy,
                    "forbidden_positive_terms": [],
                    "forbidden_avoid_terms": [],
                }
            },
        }
        (workspace / "config" / "profiles.json").write_text(
            json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        if edit:
            (package / "research" / "source-assets" / "reference.png").write_bytes(
                b"test-reference"
            )
            (package / "asset-manifest.yml").write_text(
                self.reference_manifest_record(),
                encoding="utf-8",
            )

        plan = {
            "schema_version": 1,
            "updated": "2026-07-22",
            "project_adapter": "generic",
            "profile_registry": "config/profiles.json",
            "style_policy": {
                "profile": profile_id,
                "scope": "task",
                "new_image_strategy": strategy,
                "allow_final_text_to_image": not edit,
            },
            "tasks": [
                {
                    "id": "cover",
                    "visual_type": "general_editorial",
                    "purpose": "Test the complete persisted generation contract.",
                    "reference_strategy": reference_strategy,
                    "final_stage": {
                        "mode": mode,
                        "prompt_ref": profile_id,
                        "input_assets": input_assets,
                        "output": "assets/output.png",
                        "receipt": (
                            "research/image-generation-runs/cover-final.json"
                        ),
                        "present_to_user": True,
                        "content_prompt": "Create a deliberately plain test image.",
                        "preserve": ["test subject"],
                        "output_constraints": ["16:9"],
                        "avoid": ["added text"],
                    },
                }
            ],
        }
        plan_path = package / "research" / "image-generation-plan.json"
        plan_path.write_text(
            json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        receipt, _, receipt_path = PREFLIGHT.build_request(
            package,
            "cover",
            "final",
        )
        PREFLIGHT.write_receipt(receipt, receipt_path)
        (package / "asset-manifest.yml").write_text(
            self.generic_ai_manifest(receipt, edit=edit),
            encoding="utf-8",
        )
        return receipt

    def install_rotated_appsso_preflight_contract(
        self,
        package: Path,
    ) -> dict[str, object]:
        """Prove that an adapter registry can rotate its governed prompt."""

        workspace = package.parent
        prompt = "A newly rotated adapter prompt used only for contract testing."
        prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        self.assertNotEqual(self.APPSO_PROMPT_SHA256, prompt_hash)
        (workspace / "internal").mkdir(exist_ok=True)
        (workspace / "internal" / "prompt.md").write_text(
            "# Test prompt\n\n## Original Prompt\n\n> " + prompt + "\n",
            encoding="utf-8",
        )
        registry = {
            "schema_version": 1,
            "profiles": {
                "appsso-004": {
                    "classification": "internal",
                    "prompt_source": "internal/prompt.md",
                    "prompt_heading": "## Original Prompt",
                    "prompt_sha256": prompt_hash,
                    "prompt_characters": len(prompt),
                    "requires_reference": True,
                    "allowed_final_modes": ["referenced_edit", "image_edit"],
                    "new_image_strategy": "two_stage_reference_then_redraw",
                    "forbidden_positive_terms": [],
                    "forbidden_avoid_terms": [],
                }
            },
        }
        (workspace / "config" / "profiles.json").write_text(
            json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        reference = package / "research" / "source-assets" / "reference.png"
        reference.write_bytes(b"test-reference")
        (package / "asset-manifest.yml").write_text(
            self.reference_manifest_record(),
            encoding="utf-8",
        )
        (package / "publish.yml").write_text(
            'project_adapter: "appsso"\nlayout_profile: "default"\n',
            encoding="utf-8",
        )
        plan = {
            "schema_version": 1,
            "updated": "2026-07-22",
            "project_adapter": "appsso",
            "profile_registry": "config/profiles.json",
            "style_policy": {
                "profile": "appsso-004",
                "scope": "all_ai_generated_editorial_images",
                "new_image_strategy": "two_stage_reference_then_redraw",
                "allow_final_text_to_image": False,
            },
            "tasks": [
                {
                    "id": "cover",
                    "visual_type": "ai_editorial_creative",
                    "purpose": "Test adapter-governed prompt rotation.",
                    "reference_strategy": "generated_base",
                    "reference_stage": {
                        "mode": "text_to_image",
                        "prompt_ref": "structure-reference-v1",
                        "output": "research/source-assets/reference.png",
                        "receipt": (
                            "research/image-generation-runs/cover-reference.json"
                        ),
                        "present_to_user": False,
                        "content_prompt": "Create a neutral structural reference.",
                        "output_constraints": ["16:9"],
                        "avoid": ["logos"],
                    },
                    "final_stage": {
                        "mode": "referenced_edit",
                        "prompt_ref": "appsso-004",
                        "prompt_sha256": prompt_hash,
                        "input_assets": [
                            "research/source-assets/reference.png"
                        ],
                        "output": "assets/output.png",
                        "receipt": (
                            "research/image-generation-runs/cover-final.json"
                        ),
                        "present_to_user": True,
                        "preserve": ["the test subject"],
                        "output_constraints": ["16:9"],
                        "avoid": ["logos"],
                    },
                }
            ],
        }
        plan_path = package / "research" / "image-generation-plan.json"
        plan_path.write_text(
            json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        receipt, _, receipt_path = PREFLIGHT.build_request(
            package,
            "cover",
            "final",
        )
        PREFLIGHT.write_receipt(receipt, receipt_path)
        (package / "asset-manifest.yml").write_text(
            self.generic_ai_manifest(receipt, edit=True),
            encoding="utf-8",
        )
        return receipt

    @staticmethod
    def reference_manifest_record() -> str:
        return '''version: 2
assets:
  - file: "research/source-assets/reference.png"
    used_in_draft: false
    source_type: "user_supplied"
    source: "Test fixture"
    creator_or_rightsholder: "User"
    obtained_on: "2026-07-21"
    modifications: "None"
    rights_status: "user_confirmed_derivative_use"
    allowed_platforms: []
    attribution: "Not for publication"
'''

    def generic_ai_manifest(
        self,
        receipt: dict[str, object],
        *,
        edit: bool,
    ) -> str:
        input_assets = (
            '["research/source-assets/reference.png"]' if edit else "[]"
        )
        reference_record = self.reference_manifest_record().split("assets:\n", 1)[1]
        manifest = f'''version: 2
assets:
  - file: "assets/output.png"
    used_in_draft: true
    source_type: "ai_generated"
    source: "Project generation"
    creator_or_rightsholder: "This project / AI-generated"
    obtained_on: "2026-07-22"
    generator: "Codex built-in image_gen"
    model: "gpt-image-2"
    generation_mode: "{receipt["mode"]}"
    prompt_ref: "{receipt["prompt_ref"]}"
    prompt_sha256: "{receipt["prompt_sha256"]}"
    preflight_receipt: "{receipt["receipt"]}"
    invocation_prompt_sha256: "{receipt["invocation_prompt_sha256"]}"
    generation_constraints: "16:9; no added text"
    input_assets: {input_assets}
    generated_on: "2026-07-22"
    modifications: "None"
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
    attribution: "AI 生成"
'''
        return manifest + (reference_record if edit else "")

    @staticmethod
    def local_image_manifest(file: str = "assets/output.png") -> str:
        return f'''version: 2
assets:
  - file: "{file}"
    used_in_draft: true
    source_type: "project_generated"
    source: "Test fixture"
    creator_or_rightsholder: "This project"
    obtained_on: "2026-07-21"
    modifications: "None"
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
    attribution: "None"
'''

    def test_v2_ready_referenced_generation_passes_with_full_provenance(self) -> None:
        for edit in (False, True):
            with self.subTest(edit=edit), tempfile.TemporaryDirectory() as temp_dir:
                package = self.make_package(
                    Path(temp_dir),
                    self.local_image_manifest(),
                )
                self.install_generic_preflight_contract(package, edit=edit)
                errors, warnings, _ = VALIDATOR.validate(package)
                self.assertEqual([], errors)
                self.assertEqual([], warnings)

    def test_wechat_release_states_require_ai_pattern_diagnostic(self) -> None:
        for status in ("ready", "published"):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as temp_dir:
                package = self.make_package(
                    Path(temp_dir),
                    "version: 2\nassets: []\n",
                    status=status,
                    markdown_image=False,
                )
                if status == "published":
                    draft_path = package / "draft.md"
                    draft_path.write_text(
                        draft_path.read_text(encoding="utf-8").replace(
                            'published_url: ""',
                            'published_url: "https://example.com/published"',
                        ),
                        encoding="utf-8",
                    )
                (package / "review.md").write_text("# Review\n", encoding="utf-8")
                errors, warnings, _ = VALIDATOR.validate(package)
            self.assertTrue(
                any("missing required AI-pattern diagnostic" in item for item in errors),
                errors,
            )
            self.assertFalse(
                any("missing required AI-pattern diagnostic" in item for item in warnings)
            )

    def test_wechat_release_requires_passing_ai_pattern_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                "version: 2\nassets: []\n",
                markdown_image=False,
            )
            (package / "review.md").write_text(
                "# Review\n\n"
                "## AI-pattern diagnostic\n\n"
                "- Mode: detect\n"
                "- Status: needs_fix\n",
                encoding="utf-8",
            )
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(
            any("Status must be pass, got: needs_fix" in item for item in errors),
            errors,
        )

    def test_wechat_release_rejects_open_major_ai_pattern_items(self) -> None:
        for title, status_field, severity_header in (
            ("AI-pattern diagnostic", "Status: pass", "Severity"),
            ("AI 痕迹诊断", "状态：pass", "级别"),
            ("AI 痕迹诊断", "Status：pass", "严重度"),
            ("AI 痕迹诊断", "**Status：** pass", "严重度"),
        ):
            for severity, item_id in (
                ("blocker", "HUMAN-AI-001"),
                ("major", "HUMAN-AI-001"),
                ("blocker", "HUMAN-RHY-001"),
                ("major", "HUMAN-RHY-001"),
            ):
                with (
                    self.subTest(
                        title=title,
                        status_field=status_field,
                        severity_header=severity_header,
                        severity=severity,
                        item_id=item_id,
                    ),
                    tempfile.TemporaryDirectory() as temp_dir,
                ):
                    package = self.make_package(
                        Path(temp_dir),
                        "version: 2\nassets: []\n",
                        markdown_image=False,
                    )
                    (package / "review.md").write_text(
                        "# Review\n\n"
                        f"## {title}\n\n"
                        "- Mode: detect\n"
                        f"- {status_field}\n\n"
                        f"| ID | {severity_header} | Evidence | 状态 |\n"
                        "|---|---|---|---|\n"
                        f"| {item_id} | {severity} | Exact pattern | open |\n",
                        encoding="utf-8",
                    )
                    errors, _, _ = VALIDATOR.validate(package)
                self.assertTrue(
                    any(
                        f"has open {severity} item: {item_id}" in item
                        for item in errors
                    ),
                    errors,
                )

    def test_ai_pattern_table_accepts_fullwidth_pipe_layout(self) -> None:
        review = (
            "# Review\n\n"
            "## AI 痕迹诊断\n\n"
            "- 状态：pass\n\n"
            "｜ ID ｜ 严重度 ｜ 状态 ｜\n"
            "｜---｜---｜---｜\n"
            "｜ HUMAN-AI-001 ｜ major ｜ open ｜\n"
        )
        self.assertEqual(
            [
                "review.md AI-pattern diagnostic has open major item: "
                "HUMAN-AI-001"
            ],
            VALIDATOR.validate_ai_pattern_review(review),
        )

    def test_wechat_release_allows_open_minor_ai_pattern_item(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                "version: 2\nassets: []\n",
                markdown_image=False,
            )
            (package / "review.md").write_text(
                "# Review\n\n"
                "## AI-pattern diagnostic\n\n"
                "- Mode: detect\n"
                "- Status: pass\n\n"
                "| ID | Severity | Evidence | Status |\n"
                "|---|---|---|---|\n"
                "| HUMAN-AI-001 | minor | Local rhythm | open |\n",
                encoding="utf-8",
            )
            errors, warnings, _ = VALIDATOR.validate(package)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

    def test_wechat_non_release_states_warn_for_missing_diagnostic(self) -> None:
        for status in ("draft", "editorial_review"):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as temp_dir:
                package = self.make_package(
                    Path(temp_dir),
                    "version: 2\nassets: []\n",
                    status=status,
                    markdown_image=False,
                )
                (package / "review.md").write_text("# Review\n", encoding="utf-8")
                errors, warnings, _ = VALIDATOR.validate(package)
            self.assertEqual([], errors)
            self.assertTrue(
                any(
                    "missing required AI-pattern diagnostic" in item
                    for item in warnings
                ),
                warnings,
            )

    def test_x_release_does_not_require_wechat_ai_pattern_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                "version: 2\nassets: []\n",
                markdown_image=False,
            )
            draft_path = package / "draft.md"
            draft_path.write_text(
                draft_path.read_text(encoding="utf-8").replace(
                    "platform: wechat", "platform: x"
                ),
                encoding="utf-8",
            )
            (package / "review.md").write_text("# Review\n", encoding="utf-8")
            errors, warnings, _ = VALIDATOR.validate(package)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

    def test_v2_ready_adapter_registry_can_rotate_governed_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                self.local_image_manifest(),
                project_adapter="appsso",
            )
            receipt = self.install_rotated_appsso_preflight_contract(package)
            errors, warnings, _ = VALIDATOR.validate(package)
        self.assertNotEqual(self.APPSO_PROMPT_SHA256, receipt["prompt_sha256"])
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

    def test_v2_ready_generic_direct_and_edit_require_preflight_receipt(self) -> None:
        for edit in (False, True):
            with self.subTest(edit=edit), tempfile.TemporaryDirectory() as temp_dir:
                package = self.make_package(
                    Path(temp_dir),
                    self.local_image_manifest(),
                )
                self.install_generic_preflight_contract(package, edit=edit)
                manifest_path = package / "asset-manifest.yml"
                manifest = manifest_path.read_text(encoding="utf-8")
                manifest_path.write_text(
                    "\n".join(
                        line
                        for line in manifest.splitlines()
                        if "preflight_receipt:" not in line
                    )
                    + "\n",
                    encoding="utf-8",
                )
                errors, _, _ = VALIDATOR.validate(package)
                self.assertTrue(
                    any(
                        "missing AI preflight field: preflight_receipt" in item
                        for item in errors
                    ),
                    errors,
                )

    def test_v2_ready_minimal_handwritten_receipt_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                self.local_image_manifest(),
            )
            receipt = self.install_generic_preflight_contract(package, edit=False)
            receipt_path = package / str(receipt["receipt"])
            minimal = {
                key: receipt[key]
                for key in (
                    "schema_version",
                    "status",
                    "stage",
                    "style_profile",
                    "prompt_ref",
                    "prompt_sha256",
                    "invocation_prompt_sha256",
                    "mode",
                    "input_assets",
                    "output",
                )
            }
            receipt_path.write_text(
                json.dumps(minimal, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(any("task_id must be a non-empty string" in item for item in errors))
        self.assertTrue(any("plan must be a non-empty string" in item for item in errors))
        self.assertTrue(any("input_fingerprints must be a list" in item for item in errors))

    def test_v2_ready_preflight_receipt_stales_on_contract_mutation(self) -> None:
        scenarios = (
            ("plan", "plan SHA-256 is stale"),
            ("registry", "profile_registry SHA-256 is stale"),
            ("input", "preflight input SHA-256 changed"),
        )
        for mutation, expected in scenarios:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temp_dir:
                package = self.make_package(
                    Path(temp_dir),
                    self.local_image_manifest(),
                )
                self.install_generic_preflight_contract(package, edit=True)
                if mutation == "plan":
                    target = package / "research" / "image-generation-plan.json"
                    target.write_text(
                        target.read_text(encoding="utf-8") + "\n",
                        encoding="utf-8",
                    )
                elif mutation == "registry":
                    target = package.parent / "config" / "profiles.json"
                    target.write_text(
                        target.read_text(encoding="utf-8") + "\n",
                        encoding="utf-8",
                    )
                else:
                    target = package / "research" / "source-assets" / "reference.png"
                    target.write_bytes(target.read_bytes() + b"-changed")
                errors, _, _ = VALIDATOR.validate(package)
                self.assertTrue(any(expected in item for item in errors), errors)

    def test_v2_ready_wechat_ai_asset_requires_matching_project_adapter(self) -> None:
        scenarios = (
            (None, None, "requires an independent publish.yml project_adapter"),
            ("generic", "appsso", "project_adapter does not match publish.yml"),
        )
        for initial_adapter, mutated_adapter, expected in scenarios:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as temp_dir:
                package = self.make_package(
                    Path(temp_dir),
                    self.local_image_manifest(),
                    project_adapter=initial_adapter,
                )
                self.install_generic_preflight_contract(package, edit=False)
                if mutated_adapter is not None:
                    (package / "publish.yml").write_text(
                        f'project_adapter: "{mutated_adapter}"\n',
                        encoding="utf-8",
                    )
                errors, _, _ = VALIDATOR.validate(package)
                self.assertTrue(any(expected in item for item in errors), errors)

    def test_v2_ready_final_receipt_must_be_presentable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                self.local_image_manifest(),
            )
            receipt = self.install_generic_preflight_contract(package, edit=False)
            receipt_path = package / str(receipt["receipt"])
            persisted = json.loads(receipt_path.read_text(encoding="utf-8"))
            persisted["present_to_user"] = False
            receipt_path.write_text(
                json.dumps(persisted, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(
            any("requires present_to_user=true" in item for item in errors),
            errors,
        )

    def test_v2_ready_appsso_generation_requires_receipt_and_invocation_hash(self) -> None:
        manifest = f'''version: 2
assets:
  - file: "assets/output.png"
    used_in_draft: true
    source_type: "ai_generated"
    source: "Project generation"
    creator_or_rightsholder: "This project / AI-generated"
    obtained_on: "2026-07-21"
    generator: "Codex built-in image_gen"
    model: "gpt-image-2"
    generation_mode: "referenced_edit"
    prompt_ref: "appsso-004"
    prompt_sha256: "{self.APPSO_PROMPT_SHA256}"
    generation_constraints: "16:9"
    input_assets: ["research/source-assets/reference.png"]
    generated_on: "2026-07-21"
    modifications: "None"
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
    attribution: "AI 生成"
  - file: "research/source-assets/reference.png"
    used_in_draft: false
    source_type: "user_supplied"
    source: "Test fixture"
    creator_or_rightsholder: "User"
    obtained_on: "2026-07-21"
    modifications: "None"
    rights_status: "user_confirmed_derivative_use"
    allowed_platforms: []
    attribution: "Not for publication"
'''
        for status in ("ready", "published"):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as temp_dir:
                package = self.make_package(Path(temp_dir), manifest, status=status)
                errors, warnings, _ = VALIDATOR.validate(package)
            self.assertEqual([], warnings)
            self.assertTrue(any("preflight_receipt" in item for item in errors))
            self.assertTrue(any("invocation_prompt_sha256" in item for item in errors))

    def test_v2_draft_appsso_generation_receipt_gaps_are_warnings(self) -> None:
        manifest = f'''version: 2
assets:
  - file: "assets/output.png"
    used_in_draft: true
    source_type: "ai_generated"
    source: "Project generation"
    creator_or_rightsholder: "This project / AI-generated"
    obtained_on: "2026-07-21"
    generator: "Codex built-in image_gen"
    model: "gpt-image-2"
    generation_mode: "referenced_edit"
    prompt_ref: "appsso-004"
    prompt_sha256: "{self.APPSO_PROMPT_SHA256}"
    generation_constraints: "16:9"
    input_assets: ["research/source-assets/reference.png"]
    generated_on: "2026-07-21"
    modifications: "None"
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
    attribution: "AI 生成"
  - file: "research/source-assets/reference.png"
    used_in_draft: false
    source_type: "user_supplied"
    source: "Test fixture"
    creator_or_rightsholder: "User"
    obtained_on: "2026-07-21"
    modifications: "None"
    rights_status: "user_confirmed_derivative_use"
    allowed_platforms: []
    attribution: "Not for publication"
'''
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(Path(temp_dir), manifest, status="draft")
            errors, warnings, _ = VALIDATOR.validate(package)
        self.assertEqual([], errors)
        self.assertTrue(any("preflight_receipt" in item for item in warnings))
        self.assertTrue(any("invocation_prompt_sha256" in item for item in warnings))

    def test_v2_ready_appsso_receipt_contract_mismatches_are_blocked(self) -> None:
        manifest = f'''version: 2
assets:
  - file: "assets/output.png"
    used_in_draft: true
    source_type: "ai_generated"
    source: "Project generation"
    creator_or_rightsholder: "This project / AI-generated"
    obtained_on: "2026-07-21"
    generator: "Codex built-in image_gen"
    model: "gpt-image-2"
    generation_mode: "referenced_edit"
    prompt_ref: "appsso-004"
    prompt_sha256: "{self.APPSO_PROMPT_SHA256}"
    preflight_receipt: "{self.APPSO_RECEIPT}"
    invocation_prompt_sha256: "{self.INVOCATION_PROMPT_SHA256}"
    generation_constraints: "16:9"
    input_assets: ["research/source-assets/reference.png"]
    generated_on: "2026-07-21"
    modifications: "None"
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
    attribution: "AI 生成"
  - file: "research/source-assets/reference.png"
    used_in_draft: false
    source_type: "user_supplied"
    source: "Test fixture"
    creator_or_rightsholder: "User"
    obtained_on: "2026-07-21"
    modifications: "None"
    rights_status: "user_confirmed_derivative_use"
    allowed_platforms: []
    attribution: "Not for publication"
'''
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(Path(temp_dir), manifest)
            self.write_appsso_receipt(
                package,
                overrides={
                    "status": "fail",
                    "stage": "reference",
                    "style_profile": "generic",
                    "prompt_ref": "custom",
                    "prompt_sha256": "a" * 64,
                    "invocation_prompt_sha256": "c" * 64,
                    "mode": "text_to_image",
                    "input_assets": [],
                    "output": "assets/other.png",
                    "prompt_payload": "must not be persisted",
                    "tool_request": {"prompt": "must not be persisted"},
                },
            )
            errors, _, _ = VALIDATOR.validate(package)
        for expected in (
            "must not contain prompt_payload",
            "must not contain tool_request",
            "status does not match",
            "requires a final-stage",
            "style_profile does not match",
            "prompt_ref does not match",
            "prompt_sha256 does not match",
            "invocation_prompt_sha256 does not match",
            "mode does not match",
            "output does not match",
            "input_assets do not match",
        ):
            with self.subTest(expected=expected):
                self.assertTrue(any(expected in item for item in errors), errors)

    def test_v2_ready_appsso_receipt_must_use_governed_package_directory(self) -> None:
        manifest = f'''version: 2
assets:
  - file: "assets/output.png"
    used_in_draft: true
    source_type: "ai_generated"
    source: "Project generation"
    creator_or_rightsholder: "This project / AI-generated"
    obtained_on: "2026-07-21"
    generator: "Codex built-in image_gen"
    model: "gpt-image-2"
    generation_mode: "referenced_edit"
    prompt_ref: "appsso-004"
    prompt_sha256: "{self.APPSO_PROMPT_SHA256}"
    preflight_receipt: "research/other/run.json"
    invocation_prompt_sha256: "{self.INVOCATION_PROMPT_SHA256}"
    generation_constraints: "16:9"
    input_assets: ["research/source-assets/reference.png"]
    generated_on: "2026-07-21"
    modifications: "None"
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
    attribution: "AI 生成"
  - file: "research/source-assets/reference.png"
    used_in_draft: false
    source_type: "user_supplied"
    source: "Test fixture"
    creator_or_rightsholder: "User"
    obtained_on: "2026-07-21"
    modifications: "None"
    rights_status: "user_confirmed_derivative_use"
    allowed_platforms: []
    attribution: "Not for publication"
'''
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(Path(temp_dir), manifest)
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(
            any("directly under research/image-generation-runs/" in item for item in errors)
        )

    def test_ai_generated_prefix_alias_cannot_bypass_provenance_validation(self) -> None:
        manifest = '''version: 2
assets:
  - file: "assets/output.png"
    used_in_draft: true
    source_type: "ai_generated_reference"
    source: "Project generation"
    creator_or_rightsholder: "This project / AI-generated"
    obtained_on: "2026-07-21"
    modifications: "None"
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
    attribution: "AI 生成"
'''
        for status, expected_channel in (("ready", "errors"), ("draft", "warnings")):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as temp_dir:
                package = self.make_package(Path(temp_dir), manifest, status=status)
                errors, warnings, _ = VALIDATOR.validate(package)
            actual = errors if expected_channel == "errors" else warnings
            self.assertTrue(any("non-standard AI source_type" in item for item in actual))
            self.assertTrue(any("missing AI generation field" in item for item in actual))
            if status == "draft":
                self.assertEqual([], errors)

    def test_v2_ready_reference_without_input_and_platform_is_blocked(self) -> None:
        manifest = """version: 2
assets:
  - file: "assets/output.png"
    used_in_draft: true
    source_type: "ai_generated"
    source: "Project generation"
    creator_or_rightsholder: "This project / AI-generated"
    obtained_on: "2026-07-21"
    generator: "Codex built-in image_gen"
    model: "gpt-image-2"
    generation_mode: "referenced_edit"
    prompt_ref: "appsso-004"
    prompt_sha256: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    generation_constraints: "16:9"
    input_assets: []
    generated_on: "2026-07-21"
    modifications: "None"
    rights_status: "project_owned"
    allowed_platforms: ["x"]
    attribution: "AI 生成"
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(Path(temp_dir), manifest)
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(any("does not allow platform wechat" in item for item in errors))
        self.assertTrue(any("requires input_assets" in item for item in errors))

    def test_v2_draft_missing_ai_metadata_warns_without_blocking(self) -> None:
        manifest = """version: 2
assets:
  - file: "assets/output.png"
    used_in_draft: true
    source_type: "ai_generated"
    source: "Project generation"
    creator_or_rightsholder: "This project / AI-generated"
    obtained_on: "2026-07-21"
    modifications: "None"
    rights_status: "needs_review"
    allowed_platforms: []
    attribution: "AI 生成"
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(Path(temp_dir), manifest, status="draft")
            errors, warnings, _ = VALIDATOR.validate(package)
        self.assertEqual([], errors)
        self.assertTrue(any("missing AI generation field" in item for item in warnings))
        self.assertTrue(any("does not allow platform wechat" in item for item in warnings))

    def test_v1_ready_ai_asset_remains_compatible(self) -> None:
        manifest = """version: 1
assets:
  - file: "assets/output.png"
    used_in_draft: true
    source_type: "ai_generated"
    source: "Historical Image2 generation"
    creator_or_rightsholder: "This project / AI-generated"
    obtained_on: "2026-07-13"
    modifications: "None"
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
    attribution: "AI 生成"
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(Path(temp_dir), manifest)
            errors, warnings, _ = VALIDATOR.validate(package)
        self.assertEqual([], errors)
        self.assertTrue(any(item.startswith("legacy manifest") for item in warnings))

    def test_v2_ready_unused_research_ai_asset_only_warns(self) -> None:
        manifest = """version: 2
assets:
  - file: "research/source-assets/reference.png"
    used_in_draft: false
    source_type: "ai_generated"
    source: "Rejected generation"
    creator_or_rightsholder: "This project / AI-generated"
    obtained_on: "2026-07-21"
    modifications: "Rejected for brand risk"
    rights_status: "needs_review"
    allowed_platforms: []
    attribution: "AI 生成"
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                manifest,
                markdown_image=False,
            )
            errors, warnings, _ = VALIDATOR.validate(package)
        self.assertEqual([], errors)
        self.assertTrue(any("missing AI generation field" in item for item in warnings))

    def test_v2_ready_cover_is_release_bound_even_when_not_in_draft(self) -> None:
        manifest = """version: 2
assets:
  - file: "assets/output.png"
    used_in_draft: false
    use: "wechat_cover"
    source_type: "ai_generated"
    source: "Project generation"
    creator_or_rightsholder: "This project / AI-generated"
    obtained_on: "2026-07-21"
    modifications: "None"
    rights_status: "needs_review"
    allowed_platforms: []
    attribution: "AI 生成"
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                manifest,
                markdown_image=False,
            )
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(any("missing AI generation field" in item for item in errors))
        self.assertTrue(any("rights_status is not release-cleared" in item for item in errors))

    def test_v2_ready_wechat_layout_assets_are_release_bound(self) -> None:
        for asset_use in (
            "wechat_body_header",
            "wechat_body_footer",
            "wechat_body_interactive",
        ):
            with self.subTest(asset_use=asset_use):
                manifest = f"""version: 2
assets:
  - file: "assets/output.png"
    used_in_draft: false
    use: "{asset_use}"
    source_type: "official_material"
    source: "APPSO internal brand asset"
    creator_or_rightsholder: "APPSO"
    obtained_on: "2026-07-21"
    modifications: "None"
    rights_status: "needs_review"
    allowed_platforms: []
    attribution: "APPSO"
"""
                with tempfile.TemporaryDirectory() as temp_dir:
                    package = self.make_package(
                        Path(temp_dir),
                        manifest,
                        markdown_image=False,
                    )
                    errors, _, _ = VALIDATOR.validate(package)
                self.assertTrue(
                    any("rights_status is not release-cleared" in item for item in errors)
                )
                self.assertTrue(
                    any("does not allow platform wechat" in item for item in errors)
                )

    def test_local_appsso_prompt_matches_adapter_registry_when_available(self) -> None:
        prompt_asset = (
            WORKSPACE_ROOT
            / "APPSO-数字资产"
            / "01-栏目与品牌"
            / "品牌视觉"
            / "生图-Prompt"
            / "笨拙涂鸦重绘.md"
        )
        if not prompt_asset.is_file():
            self.skipTest("internal local-only prompt asset is not present")
        text = prompt_asset.read_text(encoding="utf-8")
        prompt = next(line[2:] for line in text.splitlines() if line.startswith("> "))
        actual_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        registry_path = (
            WORKSPACE_ROOT
            / "APPSO-数字资产"
            / "04-模板"
            / "生图风格档案.json"
        )
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        expected_hash = registry["profiles"]["appsso-004"]["prompt_sha256"]
        self.assertEqual(expected_hash, actual_hash)

    def test_file_field_outside_assets_cannot_register_an_image(self) -> None:
        manifest = """version: 2
assets: []
file: "assets/output.png"
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(Path(temp_dir), manifest)
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(any("image is not registered" in item for item in errors))

    def test_future_manifest_version_is_blocked(self) -> None:
        manifest = """version: 3
assets: []
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                manifest,
                markdown_image=False,
            )
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(any("unsupported asset-manifest.yml version: 3" in item for item in errors))

    def test_malformed_generation_mode_is_reported_without_crashing(self) -> None:
        manifest = """version: 2
assets:
  - file: "assets/output.png"
    used_in_draft: true
    source_type: "ai_generated"
    source: "Project generation"
    creator_or_rightsholder: "This project / AI-generated"
    obtained_on: "2026-07-21"
    generator: "Codex built-in image_gen"
    model: "gpt-image-2"
    generation_mode: ["referenced_edit"]
    prompt_ref: "custom-prompt"
    prompt_sha256: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    generation_constraints: "16:9"
    input_assets: []
    generated_on: "2026-07-21"
    modifications: "None"
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
    attribution: "AI 生成"
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(Path(temp_dir), manifest)
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(any("generation_mode must be one of" in item for item in errors))

    def test_draft_reference_overrides_false_used_in_draft_flag(self) -> None:
        manifest = """version: 2
assets:
  - file: "assets/output.png"
    used_in_draft: false
    source_type: "ai_generated"
    source: "Project generation"
    creator_or_rightsholder: "This project / AI-generated"
    obtained_on: "2026-07-21"
    modifications: "None"
    rights_status: "needs_review"
    allowed_platforms: ["wechat"]
    attribution: "AI 生成"
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(Path(temp_dir), manifest)
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(any("referenced by draft.md" in item for item in errors))
        self.assertTrue(any("missing AI generation field" in item for item in errors))
        self.assertTrue(any("rights_status is not release-cleared" in item for item in errors))

    def test_unknown_rights_status_cannot_clear_release(self) -> None:
        manifest = """version: 2
assets:
  - file: "assets/output.png"
    used_in_draft: true
    source_type: "project_generated"
    source: "Project graphic"
    creator_or_rightsholder: "This project"
    obtained_on: "2026-07-21"
    modifications: "None"
    rights_status: "unverified"
    allowed_platforms: ["wechat"]
    attribution: "None"
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(Path(temp_dir), manifest)
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(any("rights_status is not release-cleared: unverified" in item for item in errors))

    def test_reference_input_must_be_cleared_for_derivative_use(self) -> None:
        manifest = """version: 2
assets:
  - file: "assets/output.png"
    used_in_draft: true
    source_type: "ai_generated"
    source: "Project generation"
    creator_or_rightsholder: "This project / AI-generated"
    obtained_on: "2026-07-21"
    generator: "Codex built-in image_gen"
    model: "gpt-image-2"
    generation_mode: "referenced_edit"
    prompt_ref: "appsso-004"
    prompt_sha256: "6ba5e092a4f8d6fb2bd33602424ba4792715aa59f2bf5f916b90d8bb3f0bbd0a"
    generation_constraints: "16:9"
    input_assets: ["research/source-assets/reference.png"]
    generated_on: "2026-07-21"
    modifications: "None"
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
    attribution: "AI 生成"
  - file: "research/source-assets/reference.png"
    used_in_draft: false
    source_type: "user_supplied"
    source: "Test fixture"
    creator_or_rightsholder: "User / rights unverified"
    obtained_on: "2026-07-21"
    modifications: "None"
    rights_status: "research_reference"
    allowed_platforms: []
    attribution: "Not for publication"
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(Path(temp_dir), manifest)
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(any("not cleared for derivative use" in item for item in errors))

    def test_conversation_input_must_be_persisted_before_ready(self) -> None:
        manifest = """version: 2
assets:
  - file: "assets/output.png"
    used_in_draft: true
    source_type: "ai_generated"
    source: "Project generation"
    creator_or_rightsholder: "This project / AI-generated"
    obtained_on: "2026-07-21"
    generator: "Codex built-in image_gen"
    model: "gpt-image-2"
    generation_mode: "referenced_edit"
    prompt_ref: "appsso-004"
    prompt_sha256: "6ba5e092a4f8d6fb2bd33602424ba4792715aa59f2bf5f916b90d8bb3f0bbd0a"
    generation_constraints: "16:9"
    input_assets: ["conversation:Image #1"]
    generated_on: "2026-07-21"
    modifications: "None"
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
    attribution: "AI 生成"
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(Path(temp_dir), manifest)
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(any("must be persisted and registered" in item for item in errors))

    def test_research_use_is_not_treated_as_release_bound(self) -> None:
        manifest = """version: 2
assets:
  - file: "research/source-assets/reference.png"
    used_in_draft: false
    use: "research_reference"
    source_type: "user_supplied"
    source: "Test fixture"
    creator_or_rightsholder: "User / rights unverified"
    obtained_on: "2026-07-21"
    modifications: "None"
    rights_status: "needs_review"
    allowed_platforms: []
    attribution: "Not for publication"
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                manifest,
                markdown_image=False,
            )
            errors, _, _ = VALIDATOR.validate(package)
        self.assertEqual([], errors)

    def test_reference_input_cannot_alias_the_output_itself(self) -> None:
        manifest = """version: 2
assets:
  - file: "assets/output.png"
    used_in_draft: true
    source_type: "ai_generated"
    source: "Project generation"
    creator_or_rightsholder: "This project / AI-generated"
    obtained_on: "2026-07-21"
    generator: "Codex built-in image_gen"
    model: "gpt-image-2"
    generation_mode: "referenced_edit"
    prompt_ref: "appsso-004"
    prompt_sha256: "6ba5e092a4f8d6fb2bd33602424ba4792715aa59f2bf5f916b90d8bb3f0bbd0a"
    generation_constraints: "16:9"
    input_assets: ["assets/./output.png"]
    generated_on: "2026-07-21"
    modifications: "None"
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
    attribution: "AI 生成"
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(Path(temp_dir), manifest)
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(any("asset input dependency cycle" in item for item in errors))
        self.assertTrue(any("cannot use itself as an input asset" in item for item in errors))

    def test_registered_local_html_image_participates_in_release_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                self.local_image_manifest(),
                markdown_image=False,
            )
            self.set_body(package, '# Test\n\n<img src="assets/output.png" alt="Test">\n')
            errors, warnings, image_count = VALIDATOR.validate(package)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)
        self.assertEqual(1, image_count)

    def test_html_image_must_be_registered_and_package_relative(self) -> None:
        for source, expected in (
            ('<img src="assets/unregistered.png">', "HTML image is not registered"),
            ('<img src="../outside.png">', "HTML image path escapes package"),
        ):
            with self.subTest(source=source), tempfile.TemporaryDirectory() as temp_dir:
                package = self.make_package(
                    Path(temp_dir),
                    "version: 2\nassets: []\n",
                    markdown_image=False,
                )
                if "unregistered" in source:
                    (package / "assets" / "unregistered.png").write_bytes(b"image")
                self.set_body(package, f"# Test\n\n{source}\n")
                errors, _, _ = VALIDATOR.validate(package)
            self.assertTrue(any(expected in item for item in errors), errors)

    def test_windows_absolute_image_path_is_always_a_hard_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                "version: 2\nassets: []\n",
                status="draft",
                markdown_image=False,
            )
            self.set_body(package, "# Test\n\n![unsafe](C:\\outside\\image.png)\n")
            errors, warnings, _ = VALIDATOR.validate(package)
        self.assertTrue(any("image path must be package-relative" in item for item in errors))
        self.assertFalse(any("is not packaged locally" in item for item in warnings))

    def test_reference_style_images_use_the_same_manifest_and_path_gate(self) -> None:
        reference_bodies = (
            "![Alt][asset]\n\n[asset]: assets/output.png",
            "![asset][]\n\n[asset]: assets/output.png",
            "![asset]\n\n[asset]: assets/output.png",
        )
        for body in reference_bodies:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as temp_dir:
                package = self.make_package(
                    Path(temp_dir),
                    self.local_image_manifest(),
                    markdown_image=False,
                )
                self.set_body(package, f"# Test\n\n{body}\n")
                errors, warnings, image_count = VALIDATOR.validate(package)
            self.assertEqual([], errors)
            self.assertEqual([], warnings)
            self.assertEqual(1, image_count)

        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                "version: 2\nassets: []\n",
                markdown_image=False,
            )
            (package / "assets" / "output.png").write_bytes(b"image")
            self.set_body(
                package,
                "# Test\n\n![asset][id]\n\n[id]: assets/output.png\n",
            )
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(any("Markdown image is not registered" in item for item in errors))

    def test_blockquote_reference_images_follow_the_semantic_manifest_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                self.local_image_manifest(),
                markdown_image=False,
            )
            self.set_body(
                package,
                "# Test\n\n> ![asset][id]\n>\n> [id]: assets/output.png\n",
            )
            errors, warnings, image_count = VALIDATOR.validate(package)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)
        self.assertEqual(1, image_count)

        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                "version: 2\nassets: []\n",
                markdown_image=False,
            )
            self.set_body(
                package,
                "# Test\n\n> ![asset][id]\n>\n> [id]: https://example.com/remote.png\n",
            )
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(any("is not packaged locally" in item for item in errors))

    def test_markdown_code_containers_do_not_create_image_references(self) -> None:
        bodies = (
            "# Test\n\n> ```md\n> ![example](https://example.com/code.png)\n> ```\n",
            "# Test\n\n``![example](https://example.com/code.png)\ncontinued``\n",
        )
        for body in bodies:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as temp_dir:
                package = self.make_package(
                    Path(temp_dir),
                    "version: 2\nassets: []\n",
                    markdown_image=False,
                )
                self.set_body(package, body)
                errors, warnings, image_count = VALIDATOR.validate(package)
            self.assertEqual([], errors)
            self.assertEqual([], warnings)
            self.assertEqual(0, image_count)

    def test_escaped_fence_does_not_hide_a_rendered_remote_image(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                "version: 2\nassets: []\n",
                markdown_image=False,
            )
            self.set_body(
                package,
                "# Test\n\n\\```md\n\n![remote](https://example.com/image.png)\n",
            )
            errors, _, image_count = VALIDATOR.validate(package)
        self.assertTrue(any("is not packaged locally" in item for item in errors))
        self.assertEqual(0, image_count)

    def test_windows_stream_separator_is_rejected_in_draft_and_manifest_paths(self) -> None:
        manifest = self.local_image_manifest("assets/base:cover.png")
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                manifest,
                markdown_image=False,
            )
            self.set_body(package, "# Test\n\n![asset](assets/base:cover.png)\n")
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(any("unsafe path segments" in item for item in errors), errors)
        self.assertTrue(any("image path escapes package" in item for item in errors), errors)

    def test_footnote_definition_is_not_parsed_as_a_link_definition(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                "version: 2\nassets: []\n",
                markdown_image=False,
            )
            self.set_body(
                package,
                "# Test\n\nFootnote.[^1]\n\n[^1]: javascript: is discussed as plain text.\n",
            )
            errors, warnings, image_count = VALIDATOR.validate(package)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)
        self.assertEqual(0, image_count)

    def test_release_states_reject_remote_and_data_images_from_markdown_and_html(self) -> None:
        bodies = (
            "![remote](https://example.com/image.png)",
            '<img src="https://example.com/image.png">',
            "![embedded](data:image/png;base64,AAAA)",
            '<img src="data:image/png;base64,AAAA">',
            "![remote][asset]\n\n[asset]: https://example.com/image.png",
            "![asset][]\n\n[asset]: data:image/png;base64,AAAA",
            "![asset]\n\n[asset]: https://example.com/image.png",
        )
        for status in ("ready", "published"):
            for body in bodies:
                with (
                    self.subTest(status=status, body=body),
                    tempfile.TemporaryDirectory() as temp_dir,
                ):
                    package = self.make_package(
                        Path(temp_dir),
                        "version: 2\nassets: []\n",
                        status=status,
                        markdown_image=False,
                    )
                    if status == "published":
                        draft_path = package / "draft.md"
                        draft_path.write_text(
                            draft_path.read_text(encoding="utf-8").replace(
                                'published_url: ""',
                                'published_url: "https://example.com/published"',
                            ),
                            encoding="utf-8",
                        )
                    self.set_body(package, f"# Test\n\n{body}\n")
                    errors, warnings, _ = VALIDATOR.validate(package)
                self.assertTrue(
                    any(
                        "is not packaged locally" in item
                        or "forbidden URL scheme" in item
                        for item in errors
                    ),
                    errors,
                )
                self.assertFalse(any("is not packaged locally" in item for item in warnings))

    def test_draft_remote_image_is_visible_as_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                "version: 2\nassets: []\n",
                status="draft",
                markdown_image=False,
            )
            self.set_body(package, '# Test\n\n<img src="https://example.com/image.png">\n')
            errors, warnings, _ = VALIDATOR.validate(package)
        self.assertEqual([], errors)
        self.assertTrue(any("HTML image is not packaged locally" in item for item in warnings))

    def test_active_html_tags_are_forbidden(self) -> None:
        markup_by_tag = {
            "script": "<script>alert(1)</script>",
            "iframe": '<iframe src="https://example.com"></iframe>',
            "object": '<object data="asset.bin"></object>',
            "embed": '<embed src="asset.bin">',
            "form": '<form action="/submit"></form>',
            "link": '<link rel="stylesheet" href="https://example.com/style.css">',
            "meta": '<meta http-equiv="refresh" content="0">',
            "style": "<style>body { color: red; }</style>",
        }
        for tag, markup in markup_by_tag.items():
            with self.subTest(tag=tag), tempfile.TemporaryDirectory() as temp_dir:
                package = self.make_package(
                    Path(temp_dir),
                    "version: 2\nassets: []\n",
                    markdown_image=False,
                )
                self.set_body(package, f"# Test\n\n{markup}\n")
                errors, _, _ = VALIDATOR.validate(package)
            self.assertTrue(
                any(f"forbidden HTML tag <{tag}>" in item for item in errors),
                errors,
            )

    def test_event_attributes_and_script_url_schemes_are_forbidden(self) -> None:
        body = """# Test

<p onclick="alert(1)">Unsafe event</p>
<a href="java&#x09;script:alert(1)">Unsafe HTML URL</a>
[Unsafe Markdown URL](vbscript:msgbox(1))
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                "version: 2\nassets: []\n",
                markdown_image=False,
            )
            self.set_body(package, body)
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(any("event attribute onclick" in item for item in errors))
        self.assertTrue(any("URL scheme in HTML attribute href" in item for item in errors))
        self.assertTrue(any("forbidden Markdown URL scheme" in item for item in errors))

    def test_renderer_accepted_dangerous_markdown_urls_are_always_rejected(self) -> None:
        cases = (
            ("[x](javascript:alert(1))", "forbidden Markdown URL scheme"),
            ("[x][id]\n\n[id]: vbscript:alert(1)", "forbidden Markdown URL scheme"),
            ("[id][]\n\n[id]: javascript:alert(1)", "forbidden Markdown URL scheme"),
            ("[id]\n\n[id]: vbscript:alert(1)", "forbidden Markdown URL scheme"),
            ("![x](javascript:alert(1))", "image contains a forbidden URL scheme"),
            ("![x][id]\n\n[id]: vbscript:alert(1)", "image contains a forbidden URL scheme"),
            ("![id][]\n\n[id]: javascript:alert(1)", "image contains a forbidden URL scheme"),
            ("![id]\n\n[id]: vbscript:alert(1)", "image contains a forbidden URL scheme"),
        )
        for body, expected in cases:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as temp_dir:
                package = self.make_package(
                    Path(temp_dir),
                    "version: 2\nassets: []\n",
                    markdown_image=False,
                )
                self.set_body(package, f"# Test\n\n{body}\n")
                errors, _, _ = VALIDATOR.validate(package)
            self.assertTrue(any(expected in item for item in errors), errors)

    def test_scriptable_images_are_hard_errors_even_in_draft_state(self) -> None:
        bodies = (
            "![x](javascript:alert(1))",
            "![x][id]\n\n[id]: vbscript:alert(1)",
        )
        for body in bodies:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as temp_dir:
                package = self.make_package(
                    Path(temp_dir),
                    "version: 2\nassets: []\n",
                    status="draft",
                    markdown_image=False,
                )
                self.set_body(package, f"# Test\n\n{body}\n")
                errors, warnings, _ = VALIDATOR.validate(package)
            self.assertTrue(
                any("image contains a forbidden URL scheme" in item for item in errors),
                errors,
            )
            self.assertFalse(
                any("is not packaged locally" in item for item in warnings), warnings
            )

    def test_navigation_scheme_allowlist_blocks_data_and_file_but_allows_web_and_mail(self) -> None:
        blocked = (
            "[inline](data:text/html,unsafe)",
            "[reference][id]\n\n[id]: file:///C:/unsafe.txt",
            '<a href="data:text/html,unsafe">raw</a>',
            '<a href="file:///C:/unsafe.txt">raw</a>',
        )
        for body in blocked:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as temp_dir:
                package = self.make_package(
                    Path(temp_dir),
                    "version: 2\nassets: []\n",
                    markdown_image=False,
                )
                self.set_body(package, f"# Test\n\n{body}\n")
                errors, _, _ = VALIDATOR.validate(package)
            self.assertTrue(any("forbidden" in item for item in errors), errors)

        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                "version: 2\nassets: []\n",
                markdown_image=False,
            )
            self.set_body(
                package,
                "# Test\n\n[Web](https://example.com) and [Mail](mailto:test@example.com).\n",
            )
            errors, warnings, _ = VALIDATOR.validate(package)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

    def test_raw_media_svg_and_css_resources_are_rejected(self) -> None:
        bodies = (
            '<base href="https://example.com/">',
            '<svg><image href="https://example.com/image.png"></image></svg>',
            '<video poster="https://example.com/poster.png"></video>',
            '<span style="background-image:url(https://example.com/image.png)">x</span>',
            '<span style="background-image:u\\72l(https://example.com/image.png)">x</span>',
            '<span style="background-image:image-set(\'https://example.com/image.png\' 1x)">x</span>',
        )
        for body in bodies:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as temp_dir:
                package = self.make_package(
                    Path(temp_dir),
                    "version: 2\nassets: []\n",
                    markdown_image=False,
                )
                self.set_body(package, f"# Test\n\n{body}\n")
                errors, _, _ = VALIDATOR.validate(package)
            self.assertTrue(errors, body)

    def test_html_srcset_is_rejected_instead_of_bypassing_image_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                self.local_image_manifest(),
                markdown_image=False,
            )
            self.set_body(
                package,
                '# Test\n\n<img src="assets/output.png" srcset="https://example.com/remote.png 2x">\n',
            )
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(any("resource attribute srcset" in item for item in errors))

    def test_duplicate_html_src_cannot_hide_a_remote_image(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                self.local_image_manifest(),
                markdown_image=False,
            )
            self.set_body(
                package,
                '# Test\n\n<img src="https://example.com/remote.png" src="assets/output.png">\n',
            )
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(any("duplicate HTML attribute src" in item for item in errors))
        self.assertTrue(any("HTML image is not packaged locally" in item for item in errors))

    def test_active_markup_inside_markdown_code_is_not_executed_or_rejected(self) -> None:
        body = """# Test

```html
<script>alert(1)</script>
<img src="https://example.com/code-only.png">
```

`<iframe src="https://example.com/code-only"></iframe>`
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                "version: 2\nassets: []\n",
                markdown_image=False,
            )
            self.set_body(package, body)
            errors, warnings, image_count = VALIDATOR.validate(package)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)
        self.assertEqual(0, image_count)

    def test_indented_html_code_is_not_executed_or_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                "version: 2\nassets: []\n",
                markdown_image=False,
            )
            self.set_body(package, "# Test\n\n    <script>alert(1)</script>\n")
            errors, warnings, image_count = VALIDATOR.validate(package)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)
        self.assertEqual(0, image_count)

    def test_html_image_entities_are_normalized_and_data_src_is_rejected(self) -> None:
        manifest = self.local_image_manifest("assets/a&b.png")
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(
                Path(temp_dir),
                manifest,
                markdown_image=False,
            )
            (package / "assets" / "a&b.png").write_bytes(b"image")
            self.set_body(
                package,
                '# Test\n\n<img src="assets/a&amp;b.png" data-src="https://example.com/lazy.png">\n',
            )
            errors, warnings, image_count = VALIDATOR.validate(package)
        self.assertTrue(any("resource attribute data-src" in item for item in errors))
        self.assertEqual([], warnings)
        self.assertEqual(1, image_count)

    def test_whitespace_does_not_satisfy_required_provenance(self) -> None:
        manifest = """version: 2
assets:
  - file: "assets/output.png"
    used_in_draft: true
    source_type: "ai_generated"
    source: " "
    creator_or_rightsholder: " "
    obtained_on: "2026-07-21"
    generator: " "
    model: " "
    generation_mode: "text_to_image"
    prompt_ref: " "
    prompt_sha256: " "
    generation_constraints: " "
    input_assets: []
    generated_on: "2026-07-21"
    modifications: " "
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
    attribution: " "
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(Path(temp_dir), manifest)
            errors, _, _ = VALIDATOR.validate(package)
        self.assertTrue(any("missing required field" in item for item in errors))
        self.assertTrue(any("missing AI generation field" in item for item in errors))


class JudgmentWorkshopValidationTests(unittest.TestCase):
    def write_workshop(self, package: Path, frontmatter: str, body: str = "") -> None:
        path = package / "research" / "judgment-workshop.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\n{frontmatter}---\n{body}",
            encoding="utf-8",
        )

    def valid_locked_body(self) -> str:
        return """# 核心判断共创

## 共同处境

第一次找工作的年轻人发现初级岗位正在减少。

## 主判断

AI 对就业的早期影响可能先表现为岗位不再被创造。

## 支撑判断

1. 离职岗位可能不再补人。
2. 初级任务更容易先被自动化。

## 放弃的方向

不把个别裁员直接写成整个行业已经被 AI 替代。

## 读者带走什么

除了裁员数字，还要观察招聘和补员是否减少。
"""

    def test_historical_package_without_pointer_is_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            issues = VALIDATOR.validate_judgment_workshop(
                Path(temp_dir),
                {},
                "ready",
            )
        self.assertEqual([], issues)

    def test_discussing_workshop_blocks_draft_but_not_research(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir)
            self.write_workshop(
                package,
                "status: discussing\n"
                'voice_mode: ""\n'
                "decision_points_completed: 0\n"
                "user_confirmed: false\n"
                'confirmed_on: ""\n'
                'reason: ""\n',
            )
            metadata = {
                "judgment_workshop": VALIDATOR.JUDGMENT_WORKSHOP_POINTER
            }
            draft_issues = VALIDATOR.validate_judgment_workshop(
                package,
                metadata,
                "draft",
            )
            research_issues = VALIDATOR.validate_judgment_workshop(
                package,
                metadata,
                "research",
            )
        self.assertTrue(any("cannot use a discussing" in item for item in draft_issues))
        self.assertEqual([], research_issues)

    def test_valid_locked_workshop_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir)
            self.write_workshop(
                package,
                "status: locked\n"
                "voice_mode: company\n"
                "decision_points_completed: 4\n"
                "user_confirmed: true\n"
                'confirmed_on: "2026-07-25"\n'
                'reason: ""\n',
                self.valid_locked_body(),
            )
            issues = VALIDATOR.validate_judgment_workshop(
                package,
                {"judgment_workshop": VALIDATOR.JUDGMENT_WORKSHOP_POINTER},
                "draft",
            )
        self.assertEqual([], issues)

    def test_legacy_rounds_completed_remains_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir)
            self.write_workshop(
                package,
                "status: locked\n"
                "voice_mode: company\n"
                "rounds_completed: 3\n"
                "user_confirmed: true\n"
                'confirmed_on: "2026-07-25"\n'
                'reason: ""\n',
                self.valid_locked_body(),
            )
            issues = VALIDATOR.validate_judgment_workshop(
                package,
                {"judgment_workshop": VALIDATOR.JUDGMENT_WORKSHOP_POINTER},
                "draft",
            )
        self.assertEqual([], issues)

    def test_locked_workshop_rejects_invalid_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir)
            self.write_workshop(
                package,
                "status: locked\n"
                "voice_mode: brand\n"
                "decision_points_completed: 2\n"
                "user_confirmed: false\n"
                'confirmed_on: "25/07/2026"\n'
                'reason: ""\n',
                "## 共同处境\n\n只有这一节。\n",
            )
            issues = VALIDATOR.validate_judgment_workshop(
                package,
                {"judgment_workshop": VALIDATOR.JUDGMENT_WORKSHOP_POINTER},
                "editorial_review",
            )
        joined = "\n".join(issues)
        self.assertIn("voice_mode", joined)
        self.assertIn("decision_points_completed", joined)
        self.assertIn("user_confirmed", joined)
        self.assertIn("confirmed_on", joined)
        self.assertIn("主判断", joined)
        self.assertIn("支撑判断", joined)
        self.assertIn("放弃的方向", joined)
        self.assertIn("读者带走什么", joined)

    def test_locked_workshop_rejects_template_placeholders(self) -> None:
        placeholder_body = """# 核心判断共创

## 共同处境

- 待讨论

## 主判断

- 待锁定

## 支撑判断

1. （待锁定）
2. （待锁定）

## 放弃的方向

- （待记录）

## 读者带走什么

- （待锁定）
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir)
            self.write_workshop(
                package,
                "status: locked\n"
                "voice_mode: personal\n"
                "decision_points_completed: 3\n"
                "user_confirmed: true\n"
                'confirmed_on: "2026-07-25"\n'
                'reason: ""\n',
                placeholder_body,
            )
            issues = VALIDATOR.validate_judgment_workshop(
                package,
                {"judgment_workshop": VALIDATOR.JUDGMENT_WORKSHOP_POINTER},
                "draft",
            )
        joined = "\n".join(issues)
        for title in VALIDATOR.JUDGMENT_WORKSHOP_LOCKED_SECTIONS:
            self.assertIn(title, joined)

    def test_not_required_workshop_needs_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir)
            self.write_workshop(
                package,
                "status: not_required\n"
                'voice_mode: ""\n'
                "decision_points_completed: 0\n"
                "user_confirmed: false\n"
                'confirmed_on: ""\n'
                'reason: ""\n',
            )
            issues = VALIDATOR.validate_judgment_workshop(
                package,
                {"judgment_workshop": VALIDATOR.JUDGMENT_WORKSHOP_POINTER},
                "draft",
            )
        self.assertTrue(any("non-empty reason" in item for item in issues))

    def test_current_locked_workshop_requires_chain_opponent_and_schema(self) -> None:
        current_body = self.valid_locked_body() + """

## 开场与叙事路径

- 叙事发动机：问题升级

| 本节新增的事实或动作 | 它让局面发生了什么变化 | 它留下了什么未解决的问题 | 下一节为什么必须回答这个问题 |
|---|---|---|---|
| 招聘数量下降 | 裁员不再是唯一信号 | 岗位为什么没有被补回 | 下一节必须检查补员决策 |

## 最强对手

- 对手是什么：招聘下降也可能来自宏观周期。
- 证据：同期非 AI 岗位也在下降。
- 在第几拍正面接它：第 2 拍。
- 若无法建立对手，降级为什么稿型：
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir)
            self.write_workshop(
                package,
                "status: locked\n"
                "voice_mode: company\n"
                "decision_points_completed: 4\n"
                "user_confirmed: true\n"
                'confirmed_on: "2026-08-03"\n'
                "story_contract_version: 1\n"
                "pragmatic_rule_id: PROJECT-WECHAT-PRAGMATIC-001\n"
                "expression_calibrated: true\n"
                'reason: ""\n',
                current_body,
            )
            issues = VALIDATOR.validate_judgment_workshop(
                package,
                {"judgment_workshop": VALIDATOR.JUDGMENT_WORKSHOP_POINTER},
                "draft",
            )
        self.assertEqual([], issues)

    def test_current_workshop_rejects_field_drift_and_incomplete_chain(self) -> None:
        body = self.valid_locked_body() + """

## 开场与叙事路径

- 叙事发动机：问题升级 / 实验验证

| 本节新增的事实或动作 | 它让局面发生了什么变化 | 它留下了什么未解决的问题 | 下一节为什么必须回答这个问题 |
|---|---|---|---|
| 只有第一格 |  |  |  |

## 最强对手

- 对手是什么：
- 若无法建立对手，降级为什么稿型：
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir)
            self.write_workshop(
                package,
                "status: locked\n"
                "voice_mode: personal\n"
                "decision_points_completed: 4\n"
                "user_confirmed: true\n"
                'confirmed_on: "2026-08-03"\n'
                "pragmatic_rule_id: PROJECT-WECHAT-PRAGMATIC-001\n"
                'reason: ""\n',
                body,
            )
            issues = VALIDATOR.validate_judgment_workshop(
                package,
                {"judgment_workshop": VALIDATOR.JUDGMENT_WORKSHOP_POINTER},
                "draft",
            )
        joined = "\n".join(issues)
        self.assertIn("story_contract_version", joined)
        self.assertIn("expression_calibrated", joined)
        self.assertIn("selected narrative engine", joined)
        self.assertIn("all four cells", joined)
        self.assertIn("strongest opponent", joined)


class CandidateFrozenInputValidationTests(unittest.TestCase):
    def write_frozen(self, package: Path, text: str) -> None:
        path = package / "research" / "candidates" / "round-01" / "frozen-input.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_current_frozen_input_passes_with_engine_and_complete_chain(self) -> None:
        frozen = """# 并行候选轮次

---
chain_rule_id: CORE-CHAIN-001
narrative_engine: 问题升级
candidate_fact_boundary_check_required: true
candidate_skeleton_difference_check_required: true
---

## 锁定叙事链表

| 本节新增的事实或动作 | 它让局面发生了什么变化 | 它留下了什么未解决的问题 | 下一节为什么必须回答这个问题 |
|---|---|---|---|
| 出现一个失败样本 | 原有判断变弱 | 失败来自模型还是工具 | 下一节必须拆分两个变量 |
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir)
            self.write_frozen(package, frozen)
            issues = VALIDATOR.validate_candidate_frozen_inputs(package)
        self.assertEqual([], issues)

    def test_current_frozen_input_rejects_missing_engine_and_chain_cells(self) -> None:
        frozen = """# 并行候选轮次

---
chain_rule_id: CORE-CHAIN-001
narrative_engine: ''
candidate_fact_boundary_check_required: true
candidate_skeleton_difference_check_required: false
---

| 本节新增的事实或动作 | 它让局面发生了什么变化 | 它留下了什么未解决的问题 | 下一节为什么必须回答这个问题 |
|---|---|---|---|
| 只有事实 |  |  |  |
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir)
            self.write_frozen(package, frozen)
            issues = VALIDATOR.validate_candidate_frozen_inputs(package)
        joined = "\n".join(issues)
        self.assertIn("selected narrative_engine", joined)
        self.assertIn("candidate_skeleton_difference_check_required", joined)
        self.assertIn("all four cells", joined)


if __name__ == "__main__":
    unittest.main()
