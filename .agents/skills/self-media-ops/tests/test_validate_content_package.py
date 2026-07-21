# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import hashlib
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


class ContentPackageAssetManifestTests(unittest.TestCase):
    def make_package(
        self,
        root: Path,
        manifest: str,
        *,
        status: str = "ready",
        markdown_image: bool = True,
    ) -> Path:
        package = root / "package"
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
        (package / "review.md").write_text("# Review\n", encoding="utf-8")
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
        return package

    def test_v2_ready_referenced_generation_passes_with_full_provenance(self) -> None:
        manifest = """version: 2
updated: "2026-07-21"
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
    generation_constraints: "16:9; no added text"
    input_assets: ["research/source-assets/reference.png"]
    generated_on: "2026-07-21"
    modifications: "Original-resolution review"
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
    rights_status: "user_confirmed_derivative_use"
    allowed_platforms: []
    attribution: "Not for publication"
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            package = self.make_package(Path(temp_dir), manifest)
            errors, warnings, _ = VALIDATOR.validate(package)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

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
        self.assertTrue(any("does not match governed prompt appsso-004" in item for item in errors))

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

    def test_local_appsso_prompt_matches_governed_hash_when_available(self) -> None:
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
        self.assertEqual(VALIDATOR.GOVERNED_PROMPT_HASHES["appsso-004"], actual_hash)

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


if __name__ == "__main__":
    unittest.main()
