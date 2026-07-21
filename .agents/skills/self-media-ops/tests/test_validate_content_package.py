# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import hashlib
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

    def test_v2_ready_wechat_layout_assets_are_release_bound(self) -> None:
        for asset_use in ("wechat_body_header", "wechat_body_footer"):
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


if __name__ == "__main__":
    unittest.main()
