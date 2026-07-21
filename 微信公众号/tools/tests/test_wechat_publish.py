from __future__ import annotations

import io
import importlib.util
import hashlib
import os
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import quote
from unittest import mock

from PIL import Image


MODULE_PATH = Path(__file__).resolve().parents[1] / "wechat_publish.py"
SPEC = importlib.util.spec_from_file_location("wechat_publish", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not import {MODULE_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class WechatPublishAdapterTests(unittest.TestCase):
    @staticmethod
    def write_test_image(path: Path) -> None:
        formats = {
            ".gif": "GIF",
            ".jpeg": "JPEG",
            ".jpg": "JPEG",
            ".png": "PNG",
            ".webp": "WEBP",
        }
        image_format = formats[path.suffix.casefold()]
        path.parent.mkdir(parents=True, exist_ok=True)
        with Image.new("RGB", (4, 3), color=(253, 70, 6)) as image:
            image.save(path, format=image_format)

    @staticmethod
    def next_footer_review_date(days: int = 30) -> str:
        editorial_today = datetime.now(MODULE.EDITORIAL_TIMEZONE).date()
        return (editorial_today + timedelta(days=days)).isoformat()

    def make_package(self, root: Path, name: str = "package") -> Path:
        package = root / name
        (package / "assets").mkdir(parents=True)
        self.write_test_image(package / "assets" / "body.png")
        self.write_test_image(package / "assets" / "cover.png")
        (package / "draft.md").write_text(
            """---
title: "Editorial title"
platform: wechat
status: ready
fact_checked: true
rights_checked: true
copyedit_checked: true
---

# Editorial title

Body.

## Section

Section body.

![caption](assets/body.png)
""",
            encoding="utf-8",
        )
        (package / "publish.yml").write_text(
            """title: "API title"
cover: "assets/cover.png"
theme: "default"
""",
            encoding="utf-8",
        )
        (package / "asset-manifest.yml").write_text(
            """assets:
  - file: "assets/cover.png"
    use: "wechat_cover"
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
""",
            encoding="utf-8",
        )
        return package

    def enable_appsso_layout(
        self,
        package: Path,
        *,
        include_footer: bool = False,
        footer_valid_until: str | None = None,
    ) -> None:
        self.write_test_image(package / "assets" / "appsso-header.gif")
        publish = (package / "publish.yml").read_text(encoding="utf-8")
        publish += (
            'layout_profile: "appsso-article-v1"\n'
            'header_image: "assets/appsso-header.gif"\n'
            'header_alt: "APPSO 灵感指南"\n'
        )
        manifest = (package / "asset-manifest.yml").read_text(encoding="utf-8")
        manifest += """  - file: "assets/appsso-header.gif"
    used_in_draft: false
    use: "wechat_body_header"
    source_type: "official_material"
    source: "APPSO internal brand asset"
    creator_or_rightsholder: "APPSO"
    obtained_on: "2026-07-21"
    modifications: "None"
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
    attribution: "APPSO"
"""
        if include_footer:
            self.write_test_image(package / "assets" / "appsso-footer.jpg")
            review_date = footer_valid_until or self.next_footer_review_date()
            publish += (
                'footer_image: "assets/appsso-footer.jpg"\n'
                'footer_alt: "APPSO 文末信息"\n'
                f'footer_valid_until: "{review_date}"\n'
            )
            manifest += """  - file: "assets/appsso-footer.jpg"
    used_in_draft: false
    use: "wechat_body_footer"
    source_type: "official_material"
    source: "APPSO internal brand asset"
    creator_or_rightsholder: "APPSO"
    obtained_on: "2026-07-21"
    modifications: "None"
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
    attribution: "APPSO"
"""
        (package / "publish.yml").write_text(publish, encoding="utf-8")
        (package / "asset-manifest.yml").write_text(manifest, encoding="utf-8")

    def capture_preview_snapshot(self, package: Path) -> object:
        source, metadata, config, _ = MODULE.prepare_source(package)
        theme_snapshot = MODULE.stage_layout_theme(source.parent, config)
        MODULE.stage_asset_bytes(
            package / "assets" / "body.png", source.parent, "assets/body.png"
        )
        MODULE.stage_asset_bytes(
            package / "assets" / "cover.png", source.parent, "assets/cover.png"
        )
        package_files = MODULE.package_input_hashes(package)
        snapshot = MODULE.capture_build_snapshot(
            package,
            source,
            theme_snapshot,
            config,
            package_files,
        )
        return MODULE.PreviewBuild(
            preview_path=MODULE.safe_dist(package) / "wechat-preview.html",
            source=source,
            theme_snapshot=theme_snapshot,
            metadata=metadata,
            config=config,
            blockers=[],
            validator_ok=True,
            validator_report="",
            snapshot=snapshot,
        )

    def test_prepare_source_uses_api_title_and_package_relative_images(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            source, metadata, config, body = MODULE.prepare_source(package)
            generated = source.read_text(encoding="utf-8")
            self.assertEqual(config.title, "API title")
            self.assertEqual(metadata["status"], "ready")
            self.assertNotIn("# Editorial title", body)
            self.assertIn("assets/body.png", generated)
            self.assertIn("cover: assets/cover.png", generated)
            self.assertNotIn("digest:", generated)

    def test_reference_style_images_remain_package_relative_for_staging(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            draft_path = package / "draft.md"
            draft_path.write_text(
                draft_path.read_text(encoding="utf-8").replace(
                    "![caption](assets/body.png)",
                    "![caption][body-ref]\n\n"
                    '[body-ref]: <assets/body.png> "Caption"\n\n'
                    "[section-link]: #section\n\n"
                    "[^1]: Footnote text.",
                ),
                encoding="utf-8",
            )

            source, _, _, _ = MODULE.prepare_source(package)
            generated = source.read_text(encoding="utf-8")

            self.assertIn('[body-ref]: <assets/body.png> "Caption"', generated)
            self.assertIn("[section-link]: #section", generated)
            self.assertIn("[^1]: Footnote text.", generated)

    def test_markdown_code_examples_are_not_rewritten_or_counted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            self.enable_appsso_layout(package)
            draft_path = package / "draft.md"
            code_example = """`![inline](assets/appsso-header.gif)`

```markdown
![fenced](assets/appsso-header.gif)
[fenced-ref]: assets/appsso-header.gif
<section class="appsso-body-header">Example</section>
<img src="assets/appsso-header.gif">
```
"""
            draft_path.write_text(
                draft_path.read_text(encoding="utf-8").replace(
                    "Body.", "Body.\n\n" + code_example
                ),
                encoding="utf-8",
            )

            source, _, _, _ = MODULE.prepare_source(package)
            generated = source.read_text(encoding="utf-8")
            self.assertIn("`![inline](assets/appsso-header.gif)`", generated)
            self.assertIn("![fenced](assets/appsso-header.gif)", generated)
            self.assertIn("[fenced-ref]: assets/appsso-header.gif", generated)
            self.assertIn(
                '<section class="appsso-body-header">Example</section>', generated
            )
            self.assertIn('<img src="assets/appsso-header.gif">', generated)
            self.assertIn("![caption](assets/body.png)", generated)

    def test_release_gate_accepts_registered_cleared_cover(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            metadata, _ = MODULE.load_draft(package)
            config = MODULE.load_publish_config(package, metadata)
            self.assertEqual(MODULE.publication_blockers(package, metadata, config), [])

    def test_cover_requires_explicit_release_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            manifest_path = package / "asset-manifest.yml"
            manifest = manifest_path.read_text(encoding="utf-8")
            manifest_path.write_text(
                manifest.replace('    use: "wechat_cover"\n', ""),
                encoding="utf-8",
            )
            metadata, _ = MODULE.load_draft(package)
            config = MODULE.load_publish_config(package, metadata)
            blockers = MODULE.publication_blockers(package, metadata, config)
            self.assertIn(
                "cover manifest must declare use: wechat_cover or used_as_cover: true",
                blockers,
            )

            manifest_path.write_text(
                manifest.replace(
                    '    use: "wechat_cover"', "    used_as_cover: true"
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                MODULE.publication_blockers(package, metadata, config), []
            )

    def test_release_gate_blocks_unresolved_cover_rights(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            manifest = (package / "asset-manifest.yml").read_text(encoding="utf-8")
            (package / "asset-manifest.yml").write_text(
                manifest.replace("project_owned", "needs_review"), encoding="utf-8"
            )
            metadata, _ = MODULE.load_draft(package)
            config = MODULE.load_publish_config(package, metadata)
            blockers = MODULE.publication_blockers(package, metadata, config)
            self.assertTrue(any("rights_status is not release-cleared" in item for item in blockers))

    def test_release_gate_blocks_unknown_cover_rights_label(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            manifest = (package / "asset-manifest.yml").read_text(encoding="utf-8")
            (package / "asset-manifest.yml").write_text(
                manifest.replace("project_owned", "looks_safe_but_unknown"),
                encoding="utf-8",
            )
            metadata, _ = MODULE.load_draft(package)
            config = MODULE.load_publish_config(package, metadata)
            blockers = MODULE.publication_blockers(package, metadata, config)
            self.assertTrue(any("looks_safe_but_unknown" in item for item in blockers))

    def test_release_gate_rejects_string_platform_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            manifest = (package / "asset-manifest.yml").read_text(encoding="utf-8")
            (package / "asset-manifest.yml").write_text(
                manifest.replace('["wechat"]', '"wechat"'), encoding="utf-8"
            )
            metadata, _ = MODULE.load_draft(package)
            config = MODULE.load_publish_config(package, metadata)
            blockers = MODULE.publication_blockers(package, metadata, config)
            self.assertTrue(any("not allowed for the wechat platform" in item for item in blockers))

    def test_release_gate_and_layout_prepare_reject_corrupted_images(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cover_package = self.make_package(root, "corrupt-cover")
            (cover_package / "assets" / "cover.png").write_bytes(b"not a PNG")
            metadata, _ = MODULE.load_draft(cover_package)
            config = MODULE.load_publish_config(cover_package, metadata)
            blockers = MODULE.publication_blockers(
                cover_package, metadata, config
            )
            self.assertTrue(
                any(
                    item.startswith(
                        "cover is not a valid release image: image cannot be decoded"
                    )
                    for item in blockers
                )
            )

            header_package = self.make_package(root, "corrupt-header")
            self.enable_appsso_layout(header_package)
            (header_package / "assets" / "appsso-header.gif").write_bytes(
                b"not a GIF"
            )
            with self.assertRaisesRegex(
                MODULE.WorkflowError,
                r"header_image is not a valid release image: image cannot be decoded",
            ):
                MODULE.prepare_source(header_package)

    def test_appsso_profile_injects_header_and_footer_around_body(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            self.enable_appsso_layout(package, include_footer=True)
            source, _, config, body = MODULE.prepare_source(package)
            generated = source.read_text(encoding="utf-8")
            self.assertEqual(config.layout_profile, "appsso-article-v1")
            self.assertLess(body.index("appsso-body-header"), body.index("Body."))
            self.assertGreater(body.index("appsso-body-footer"), body.index("assets/body.png"))
            self.assertIn('src="assets/appsso-header.gif"', generated)
            self.assertIn('src="assets/appsso-footer.jpg"', generated)

    def test_appsso_profile_uses_allowlisted_custom_theme_for_render_and_publish(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = self.make_package(root)
            self.enable_appsso_layout(package)
            metadata, _ = MODULE.load_draft(package)
            config = MODULE.load_publish_config(package, metadata)
            fake_wenyan = root / "wenyan.cmd"
            fake_wenyan.write_text("test", encoding="utf-8")
            source = package / "draft.md"
            with mock.patch.object(MODULE, "WENYAN_CMD", fake_wenyan):
                render_args = MODULE.wenyan_args("render", source, config)
                publish_args = MODULE.wenyan_args("publish", source, config)
            expected_theme = str(
                (MODULE.WECHAT_ROOT / "themes" / "appsso-article-v1.css").resolve()
            )
            self.assertIn("--custom-theme", render_args)
            self.assertEqual(
                render_args[render_args.index("--custom-theme") + 1], expected_theme
            )
            self.assertEqual(
                render_args[render_args.index("--custom-theme") :],
                publish_args[publish_args.index("--custom-theme") :],
            )

    def test_appsso_layout_assets_pass_release_gate_when_registered(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            self.enable_appsso_layout(package, include_footer=True)
            metadata, _ = MODULE.load_draft(package)
            config = MODULE.load_publish_config(package, metadata)
            self.assertEqual(MODULE.publication_blockers(package, metadata, config), [])

    def test_appsso_layout_blocks_missing_header_and_expired_footer(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            publish = (package / "publish.yml").read_text(encoding="utf-8")
            publish += 'layout_profile: "appsso-article-v1"\n'
            (package / "publish.yml").write_text(publish, encoding="utf-8")
            metadata, _ = MODULE.load_draft(package)
            config = MODULE.load_publish_config(package, metadata)
            blockers = MODULE.publication_blockers(package, metadata, config)
            self.assertTrue(any("requires a rights-cleared header_image" in item for item in blockers))

            (package / "publish.yml").write_text(
                publish.replace('layout_profile: "appsso-article-v1"\n', ""),
                encoding="utf-8",
            )
            self.enable_appsso_layout(
                package,
                include_footer=True,
                footer_valid_until="2000-01-01",
            )
            metadata, _ = MODULE.load_draft(package)
            config = MODULE.load_publish_config(package, metadata)
            blockers = MODULE.publication_blockers(package, metadata, config)
            self.assertTrue(
                any("footer_image review is overdue since 2000-01-01" in item for item in blockers)
            )

    def test_footer_review_window_accepts_365_days_and_rejects_366(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            fixed_now = datetime.now(MODULE.EDITORIAL_TIMEZONE)
            max_date = (fixed_now.date() + timedelta(days=365)).isoformat()
            over_date = (fixed_now.date() + timedelta(days=366)).isoformat()
            self.enable_appsso_layout(
                package,
                include_footer=True,
                footer_valid_until=max_date,
            )
            metadata, _ = MODULE.load_draft(package)

            with mock.patch.object(MODULE, "datetime") as mocked_datetime:
                mocked_datetime.now.return_value = fixed_now
                config = MODULE.load_publish_config(package, metadata)
                blockers = MODULE.publication_blockers(package, metadata, config)
                self.assertFalse(
                    any("365-day review window" in item for item in blockers)
                )

                publish_path = package / "publish.yml"
                publish_path.write_text(
                    publish_path.read_text(encoding="utf-8").replace(
                        max_date, over_date
                    ),
                    encoding="utf-8",
                )
                config = MODULE.load_publish_config(package, metadata)
                blockers = MODULE.publication_blockers(package, metadata, config)

            self.assertIn(
                "footer_valid_until exceeds the 365-day review window", blockers
            )

    def test_unknown_layout_profile_fails_loud(self) -> None:
        config = MODULE.PublishConfig(title="Test", layout_profile="unknown")
        with self.assertRaisesRegex(MODULE.WorkflowError, "unknown layout_profile"):
            MODULE.get_layout_profile(config)

    def test_default_profile_does_not_silently_accept_appsso_components(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            self.write_test_image(package / "assets" / "standalone-header.png")
            publish = (package / "publish.yml").read_text(encoding="utf-8")
            publish += 'header_image: "assets/standalone-header.png"\n'
            (package / "publish.yml").write_text(publish, encoding="utf-8")
            with self.assertRaisesRegex(MODULE.WorkflowError, "does not support"):
                MODULE.prepare_source(package)

    def test_default_profile_does_not_load_appsso_custom_theme(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fake_wenyan = root / "wenyan.cmd"
            fake_wenyan.write_text("test", encoding="utf-8")
            config = MODULE.PublishConfig(title="Hunt Good", layout_profile="default")
            with mock.patch.object(MODULE, "WENYAN_CMD", fake_wenyan):
                args = MODULE.wenyan_args("render", root / "draft.md", config)
            self.assertNotIn("--custom-theme", args)

    def test_url_encoded_local_image_with_chinese_space_and_ampersand(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            relative = "assets/中文 空格&符号.png"
            encoded = quote(relative, safe="/")
            self.write_test_image(package / relative)
            fragment = (
                '<img data-src="https://example.invalid/lazy.png" '
                'srcset="https://example.invalid/two.png 2x" '
                f'src="{encoded}" alt="特殊文件名">'
            )

            self.assertEqual(MODULE.raw_html_image_sources(fragment), [encoded])
            self.assertEqual(
                MODULE.canonical_package_relative_path(
                    encoded, "body image", require_assets=True
                ),
                relative,
            )
            build_dir = MODULE.create_build_dir(package)
            MODULE.stage_asset_bytes(package / relative, build_dir, relative)
            inlined = MODULE.inline_preview_images(fragment, build_dir)
            self.assertIn(
                'data-src="https://example.invalid/lazy.png"', inlined
            )
            self.assertIn(
                'srcset="https://example.invalid/two.png 2x"', inlined
            )
            self.assertRegex(inlined, r'\ssrc="data:image/png;base64,[^"]+"')

    def test_data_src_is_not_relocated_or_treated_as_duplicate_src(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            self.enable_appsso_layout(package)
            draft_path = package / "draft.md"
            draft_path.write_text(
                draft_path.read_text(encoding="utf-8").replace(
                    "![caption](assets/body.png)",
                    '<img data-src="assets/appsso-header.gif" '
                    'src="assets/body.png" alt="body">',
                ),
                encoding="utf-8",
            )

            _, _, _, body = MODULE.prepare_source(package)

            self.assertIn('data-src="assets/appsso-header.gif"', body)
            self.assertIn('src="assets/body.png"', body)
            self.assertNotIn('data-src="../assets/appsso-header.gif"', body)

    def test_unquoted_html_src_is_safely_inlined(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            fragment = "<img data-src=lazy.png src=assets/body.png alt=body>"

            build_dir = MODULE.create_build_dir(package)
            MODULE.stage_asset_bytes(
                package / "assets" / "body.png", build_dir, "assets/body.png"
            )
            inlined = MODULE.inline_preview_images(fragment, build_dir)
            self.assertIn("data-src=lazy.png", inlined)
            self.assertRegex(inlined, r'\ssrc="data:image/png;base64,[^"]+"')

    def test_rendered_gate_stages_only_registered_package_images(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            manifest_path = package / "asset-manifest.yml"
            manifest_path.write_text(
                manifest_path.read_text(encoding="utf-8")
                + """  - file: "assets/body.png"
    used_in_draft: true
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
""",
                encoding="utf-8",
            )
            metadata, _ = MODULE.load_draft(package)
            config = MODULE.load_publish_config(package, metadata)
            build_dir = MODULE.create_build_dir(package)
            blockers = MODULE.rendered_image_gate_and_stage(
                package,
                build_dir,
                '<blockquote><p><img src="assets/body.png" alt="body"></p></blockquote>',
                config,
            )
            self.assertEqual([], blockers)
            self.assertTrue((build_dir / "assets" / "body.png").is_file())
            self.assertTrue((build_dir / "assets" / "cover.png").is_file())

    def test_shared_dist_asset_cannot_satisfy_the_rendered_image_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            stale = package / "dist" / "assets" / "rogue.png"
            self.write_test_image(stale)
            metadata, _ = MODULE.load_draft(package)
            config = MODULE.load_publish_config(package, metadata)
            build_dir = MODULE.create_build_dir(package)
            blockers = MODULE.rendered_image_gate_and_stage(
                package,
                build_dir,
                '<blockquote><img src="assets/rogue.png" alt="rogue"></blockquote>',
                config,
            )
            self.assertTrue(
                any("does not exist in the content package" in item for item in blockers),
                blockers,
            )
            self.assertFalse((build_dir / "assets" / "rogue.png").exists())

    def test_each_prepare_uses_a_unique_build_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            first, _, _, _ = MODULE.prepare_source(package)
            second, _, _, _ = MODULE.prepare_source(package)
            builds = (package / "dist" / "builds").resolve()
            self.assertNotEqual(first.parent, second.parent)
            self.assertTrue(first.parent.resolve().is_relative_to(builds))
            self.assertTrue(second.parent.resolve().is_relative_to(builds))

    def test_windows_stream_separator_is_rejected_by_release_path_gate(self) -> None:
        for path in ("assets/base:cover.png", "assets/base%3Acover.png"):
            with self.subTest(path=path), self.assertRaisesRegex(
                MODULE.WorkflowError, "unsafe path segment"
            ):
                MODULE.canonical_package_relative_path(
                    path, "cover", require_assets=True
                )

    def test_rendered_gate_rejects_reserved_wrappers_and_duplicate_components(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            wrapper_package = self.make_package(root, "reserved-wrapper")
            metadata, _ = MODULE.load_draft(wrapper_package)
            wrapper_config = MODULE.load_publish_config(wrapper_package, metadata)
            wrapper_blockers = MODULE.rendered_image_gate_and_stage(
                wrapper_package,
                MODULE.create_build_dir(wrapper_package),
                '<section class="custom appsso-body-header">Body.</section>',
                wrapper_config,
            )
            self.assertTrue(
                any("appsso-body-header wrapper must appear 0" in item for item in wrapper_blockers),
                wrapper_blockers,
            )

            image_package = self.make_package(root, "duplicate-image")
            self.enable_appsso_layout(image_package)
            image_metadata, _ = MODULE.load_draft(image_package)
            image_config = MODULE.load_publish_config(image_package, image_metadata)
            duplicate_fragment = (
                '<section class="appsso-body-header">'
                '<img src="assets/appsso-header.gif" alt="header">'
                "</section>"
                '<p><img src="assets/appsso-header.gif" alt="duplicate"></p>'
            )
            image_blockers = MODULE.rendered_image_gate_and_stage(
                image_package,
                MODULE.create_build_dir(image_package),
                duplicate_fragment,
                image_config,
            )
            self.assertTrue(
                any("wechat_body_header must appear exactly once" in item for item in image_blockers),
                image_blockers,
            )

    def test_layout_images_require_alt_text_and_iso_footer_date(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            review_date = self.next_footer_review_date()
            self.enable_appsso_layout(
                package,
                include_footer=True,
                footer_valid_until=review_date,
            )
            publish_path = package / "publish.yml"
            publish = publish_path.read_text(encoding="utf-8")
            publish = publish.replace('header_alt: "APPSO 灵感指南"', 'header_alt: ""')
            publish = publish.replace('footer_alt: "APPSO 文末信息"', 'footer_alt: ""')
            publish = publish.replace(
                f'footer_valid_until: "{review_date}"',
                'footer_valid_until: "evergreen"',
            )
            publish_path.write_text(publish, encoding="utf-8")
            metadata, _ = MODULE.load_draft(package)
            config = MODULE.load_publish_config(package, metadata)
            blockers = MODULE.publication_blockers(package, metadata, config)
            self.assertIn("header_image requires non-empty header_alt", blockers)
            self.assertIn("footer_image requires non-empty footer_alt", blockers)
            self.assertIn("footer_valid_until must be YYYY-MM-DD", blockers)

    def test_layout_plan_records_theme_hash(self) -> None:
        config = MODULE.PublishConfig(
            title="Test", layout_profile="appsso-article-v1"
        )
        plan = MODULE.layout_plan(config)
        theme = MODULE.WECHAT_ROOT / "themes" / "appsso-article-v1.css"
        self.assertEqual(plan["profile"], "appsso-article-v1")
        self.assertEqual(
            plan["custom_theme_sha256"], hashlib.sha256(theme.read_bytes()).hexdigest()
        )

    def test_preview_exposes_375_and_390_pixel_checks(self) -> None:
        document = MODULE.preview_document("Test", "<p>Body</p>", True, "", [])
        self.assertIn('data-width="375"', document)
        self.assertIn('data-width="390"', document)
        self.assertIn('data-preview-width="390"', document)

    def test_preview_csp_blocks_network_and_binds_script_nonce(self) -> None:
        first = MODULE.preview_document("Test", "<p>Body</p>", True, "", [])
        second = MODULE.preview_document("Test", "<p>Body</p>", True, "", [])
        csp_match = re.search(
            r'<meta http-equiv="Content-Security-Policy" content="([^"]+)">',
            first,
        )
        self.assertIsNotNone(csp_match)
        csp = csp_match.group(1) if csp_match else ""
        for directive in (
            "default-src 'none'",
            "img-src data:",
            "connect-src 'none'",
            "frame-src 'none'",
            "object-src 'none'",
            "base-uri 'none'",
            "form-action 'none'",
        ):
            self.assertIn(directive, csp)
        self.assertNotIn("http:", csp)
        self.assertNotIn("https:", csp)

        nonce_match = re.search(r"script-src 'nonce-([^']+)'", csp)
        self.assertIsNotNone(nonce_match)
        nonce = nonce_match.group(1) if nonce_match else ""
        self.assertIn(f'<script nonce="{nonce}">', first)
        second_nonce = re.search(r"script-src 'nonce-([^']+)'", second)
        self.assertIsNotNone(second_nonce)
        self.assertNotEqual(nonce, second_nonce.group(1) if second_nonce else nonce)

    def test_preview_rejects_active_rendered_html(self) -> None:
        MODULE.ensure_passive_preview_html(
            "<pre><code>&lt;script&gt;example&lt;/script&gt;</code></pre>"
        )
        for fragment in (
            "<script>alert(1)</script>",
            '<p onclick="alert(1)">Body</p>',
            '<a href="java&#x09;script:alert(1)">Body</a>',
            '<a href="java%73cript:alert(1)">Body</a>',
            '<a href="data:text/html,unsafe">Body</a>',
            '<a href="file:///C:/unsafe.txt">Body</a>',
            '<img src="assets/body.png" srcset="https://example.invalid/x.png 2x">',
            '<img src="assets/body.png" data-src="https://example.invalid/x.png">',
            '<span style="background-image:url(https://example.invalid/x.png)">x</span>',
            '<span style="background-image:u\\72l(https://example.invalid/x.png)">x</span>',
            '<span style="background-image:image-set(\'https://example.invalid/x.png\' 1x)">x</span>',
        ):
            with self.subTest(fragment=fragment), self.assertRaisesRegex(
                MODULE.WorkflowError, "unsafe for local preview"
            ):
                MODULE.ensure_passive_preview_html(fragment)
        MODULE.ensure_passive_preview_html(
            '<p><a href="https://example.com">Web</a> '
            '<a href="mailto:test@example.com">Mail</a></p>'
        )

    def test_blocked_draft_dry_run_returns_nonzero_without_network(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fake_build = SimpleNamespace(
                validator_ok=True,
                validator_report="",
                blockers=["layout header is missing"],
            )
            stderr = io.StringIO()
            with (
                mock.patch.object(
                    sys,
                    "argv",
                    ["wechat_publish.py", "draft", temp],
                ),
                mock.patch.object(MODULE, "build_preview", return_value=fake_build),
                mock.patch.object(MODULE.subprocess, "run") as subprocess_run,
                redirect_stderr(stderr),
            ):
                result = MODULE.main()

            self.assertEqual(result, 1)
            self.assertIn("draft creation is blocked", stderr.getvalue())
            subprocess_run.assert_not_called()

    def test_execute_rechecks_staged_assets_before_network_call(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = self.make_package(root)
            build = self.capture_preview_snapshot(package)
            (build.source.parent / "assets" / "body.png").write_bytes(b"tampered")
            env_path = root / ".env"
            env_path.write_text("WECHAT_APP_ID=test\n", encoding="utf-8")
            fake_wenyan = root / "wenyan.cmd"
            fake_wenyan.write_text("test", encoding="utf-8")
            args = SimpleNamespace(
                package=str(package), execute=True, env=str(env_path)
            )
            with (
                mock.patch.object(MODULE, "build_preview", return_value=build),
                mock.patch.object(MODULE, "WENYAN_CMD", fake_wenyan),
                mock.patch.object(MODULE.subprocess, "run") as subprocess_run,
                self.assertRaisesRegex(
                    MODULE.WorkflowError, "sealed Wenyan build changed after preflight"
                ),
            ):
                MODULE.command_draft(args)
            subprocess_run.assert_not_called()

    def test_execute_reports_possible_draft_if_staged_asset_changes_during_upload(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = self.make_package(root)
            build = self.capture_preview_snapshot(package)
            env_path = root / ".env"
            env_path.write_text("WECHAT_APP_ID=test\n", encoding="utf-8")
            fake_wenyan = root / "wenyan.cmd"
            fake_wenyan.write_text("test", encoding="utf-8")
            args = SimpleNamespace(
                package=str(package), execute=True, env=str(env_path)
            )

            def mutate_staged_asset(*_args: object, **_kwargs: object) -> object:
                (build.source.parent / "assets" / "body.png").write_bytes(
                    b"changed during upload"
                )
                return SimpleNamespace(returncode=0)

            with (
                mock.patch.object(MODULE, "build_preview", return_value=build),
                mock.patch.object(MODULE, "WENYAN_CMD", fake_wenyan),
                mock.patch.object(
                    MODULE.subprocess, "run", side_effect=mutate_staged_asset
                ) as subprocess_run,
                self.assertRaisesRegex(
                    MODULE.WorkflowError, "one draft may have been created"
                ),
                redirect_stdout(io.StringIO()),
            ):
                MODULE.command_draft(args)
            subprocess_run.assert_called_once()

    def test_build_snapshot_detects_package_source_and_staged_theme_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

            package_drift = self.make_package(root, "package-drift")
            package_build = self.capture_preview_snapshot(package_drift)
            draft_path = package_drift / "draft.md"
            draft_path.write_text(
                draft_path.read_text(encoding="utf-8") + "\nChanged after preflight.\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                MODULE.WorkflowError, "content package changed after preflight"
            ):
                MODULE.verify_build_snapshot(package_drift, package_build)

            source_drift = self.make_package(root, "source-drift")
            source_build = self.capture_preview_snapshot(source_drift)
            source_build.source.write_text(
                source_build.source.read_text(encoding="utf-8")
                + "\nTampered generated source.\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                MODULE.WorkflowError, "generated Wenyan source changed after preflight"
            ):
                MODULE.verify_build_snapshot(source_drift, source_build)

            theme_drift = self.make_package(root, "theme-drift")
            self.enable_appsso_layout(theme_drift)
            theme_build = self.capture_preview_snapshot(theme_drift)
            self.assertIsNotNone(theme_build.theme_snapshot)
            if theme_build.theme_snapshot is not None:
                theme_build.theme_snapshot.write_text(
                    theme_build.theme_snapshot.read_text(encoding="utf-8")
                    + "\n/* tampered */\n",
                    encoding="utf-8",
                )
            with self.assertRaisesRegex(
                MODULE.WorkflowError, "sealed Wenyan build changed after preflight"
            ):
                MODULE.verify_build_snapshot(theme_drift, theme_build)

            asset_drift = self.make_package(root, "asset-drift")
            asset_build = self.capture_preview_snapshot(asset_drift)
            (asset_build.source.parent / "assets" / "body.png").write_bytes(
                b"tampered staged asset"
            )
            with self.assertRaisesRegex(
                MODULE.WorkflowError, "sealed Wenyan build changed after preflight"
            ):
                MODULE.verify_build_snapshot(asset_drift, asset_build)

    def test_sealed_package_snapshot_binds_reads_to_initial_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            expected = MODULE.package_input_hashes(package)
            real_reader = MODULE.stable_file_bytes

            def changed_draft(path: Path) -> bytes:
                payload = real_reader(path)
                if path == package / "draft.md":
                    return payload + b"\ntransient change\n"
                return payload

            with (
                mock.patch.object(
                    MODULE, "stable_file_bytes", side_effect=changed_draft
                ),
                self.assertRaisesRegex(
                    MODULE.WorkflowError, "changed while sealing input: draft.md"
                ),
            ):
                with MODULE.sealed_package_snapshot(package, expected):
                    self.fail("mismatched package bytes must not be yielded")

    def test_package_hash_rejects_hardlinked_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = self.make_package(root)
            source = root / "outside.png"
            self.write_test_image(source)
            hardlink = package / "assets" / "hardlink.png"
            try:
                os.link(source, hardlink)
            except OSError as exc:
                self.skipTest(f"hardlinks unavailable: {exc}")
            with self.assertRaisesRegex(MODULE.WorkflowError, "must not be a hardlink"):
                MODULE.package_input_hashes(package)

    def test_safe_dist_rejects_regular_file_and_link_indicator(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            file_package = self.make_package(root, "dist-file")
            (file_package / "dist").write_text("not a directory", encoding="utf-8")
            with self.assertRaisesRegex(
                MODULE.WorkflowError, "dist exists but is not a directory"
            ):
                MODULE.safe_dist(file_package)

            linked_package = self.make_package(root, "dist-link")
            linked_dist = linked_package / "dist"
            linked_dist.mkdir()
            real_link_check = MODULE.is_link_or_junction

            def mark_dist_as_link(path: Path) -> bool:
                return path == linked_dist or real_link_check(path)

            with (
                mock.patch.object(
                    MODULE,
                    "is_link_or_junction",
                    side_effect=mark_dist_as_link,
                ),
                self.assertRaisesRegex(
                    MODULE.WorkflowError, "dist must not be a symlink or junction"
                ),
            ):
                MODULE.safe_dist(linked_package)

    @unittest.skipUnless(MODULE.WENYAN_CMD.is_file(), "Wenyan is not installed")
    def test_real_wenyan_blockquote_reference_image_passes_rendered_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            draft_path = package / "draft.md"
            draft_path.write_text(
                draft_path.read_text(encoding="utf-8").replace(
                    "![caption](assets/body.png)",
                    "> ![caption][body-ref]\n>\n> [body-ref]: assets/body.png",
                ),
                encoding="utf-8",
            )
            manifest_path = package / "asset-manifest.yml"
            manifest_path.write_text(
                manifest_path.read_text(encoding="utf-8")
                + """  - file: "assets/body.png"
    used_in_draft: true
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
""",
                encoding="utf-8",
            )
            source, _, config, _ = MODULE.prepare_source(package)
            rendered = MODULE.run_wenyan_render(source, config)
            blockers = MODULE.rendered_image_gate_and_stage(
                package, source.parent, rendered, config
            )
        self.assertIn("<blockquote", rendered)
        self.assertEqual([], blockers)

    @unittest.skipUnless(MODULE.WENYAN_CMD.is_file(), "Wenyan is not installed")
    def test_real_wenyan_render_inlines_appsso_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            self.enable_appsso_layout(package)
            manifest_path = package / "asset-manifest.yml"
            manifest_path.write_text(
                manifest_path.read_text(encoding="utf-8")
                + """  - file: "assets/body.png"
    used_in_draft: true
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
""",
                encoding="utf-8",
            )
            source, _, config, _ = MODULE.prepare_source(package)
            rendered = MODULE.run_wenyan_render(source, config)
            blockers = MODULE.rendered_image_gate_and_stage(
                package, source.parent, rendered, config
            )

        paragraph = re.search(r"<p style=\"([^\"]+)\">Body\.</p>", rendered)
        heading = re.search(r"<h2 style=\"([^\"]+)\"", rendered)
        header = re.search(
            r'<section class="appsso-body-header" style="([^"]+)"', rendered
        )
        image_paragraph = re.search(
            r'<p style="([^"]+)"><img src="assets/body\.png"', rendered
        )
        self.assertIsNotNone(paragraph)
        self.assertIsNotNone(heading)
        self.assertIsNotNone(header)
        self.assertIsNotNone(image_paragraph)
        paragraph_style = paragraph.group(1) if paragraph else ""
        heading_style = heading.group(1) if heading else ""
        header_style = header.group(1) if header else ""
        image_paragraph_style = image_paragraph.group(1) if image_paragraph else ""
        self.assertIn("font-size: 15px", paragraph_style)
        self.assertIn("padding: 0px 16px", paragraph_style)
        self.assertIn("text-align: justify", paragraph_style)
        self.assertIn("font-size: 20px", heading_style)
        self.assertIn("font-weight: 600", heading_style)
        self.assertIn("color: rgb(253, 70, 6)", heading_style)
        self.assertIn("text-align: left", heading_style)
        self.assertIn("width: 100%", header_style)
        self.assertNotIn("padding: 0px 16px", header_style)
        self.assertIn("padding: 0px 16px", image_paragraph_style)
        self.assertEqual([], blockers)


if __name__ == "__main__":
    unittest.main()
