from __future__ import annotations

import base64
import io
import importlib.util
import hashlib
import json
import os
import re
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
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
project_adapter: "generic"
delivery_mode: "sealed_draft"
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

    def register_body_image(self, package: Path) -> None:
        manifest_path = package / "asset-manifest.yml"
        manifest = manifest_path.read_text(encoding="utf-8")
        if 'file: "assets/body.png"' in manifest:
            return
        manifest_path.write_text(
            manifest
            + """  - file: "assets/body.png"
    used_in_draft: true
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
""",
            encoding="utf-8",
        )

    def enable_manual_editor(self, package: Path) -> None:
        publish_path = package / "publish.yml"
        publish_path.write_text(
            publish_path.read_text(encoding="utf-8").replace(
                'delivery_mode: "sealed_draft"',
                'delivery_mode: "manual_editor"',
            ),
            encoding="utf-8",
        )
        self.register_body_image(package)

    def enable_appsso_layout(
        self,
        package: Path,
        *,
        include_footer: bool = False,
        footer_valid_until: str | None = None,
    ) -> None:
        self.write_test_image(package / "assets" / "appsso-header.gif")
        publish = (package / "publish.yml").read_text(encoding="utf-8")
        publish = publish.replace(
            'project_adapter: "generic"', 'project_adapter: "appsso"'
        )
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

    def make_company_sealed_fixture(
        self, root: Path, name: str = "company-package"
    ) -> tuple[Path, Path, dict[str, str]]:
        package = self.make_package(root, name)
        self.register_body_image(package)
        publish_path = package / "publish.yml"
        publish_path.write_text(
            publish_path.read_text(encoding="utf-8").replace(
                'project_adapter: "generic"',
                'project_adapter: "appsso"',
            )
            + 'layout_profile: "appsso-article-v1"\n',
            encoding="utf-8",
        )
        title_path = package / "assets" / "locked-title.gif"
        self.write_test_image(title_path)
        title_payload = title_path.read_bytes()
        body_payload = (package / "assets" / "body.png").read_bytes()

        def data_uri(mime: str, payload: bytes) -> str:
            return f"data:{mime};base64," + base64.b64encode(payload).decode("ascii")

        html_payload = (
            '<section><img src="'
            + data_uri("image/gif", title_payload)
            + '" alt="title"><p>Body.</p><img src="'
            + data_uri("image/png", body_payload)
            + '" alt="body"></section>'
        ).encode("utf-8")
        state = {
            "profile_id": "company-appso-wechat-v1.10.0",
            "profile_sha256": "1" * 64,
            "format_profile_sha256": "2" * 64,
            "format_contract_sha256": "3" * 64,
            "adapter_sha256": "4" * 64,
            "bridge_sha256": "5" * 64,
            "renderer_sha256": "6" * 64,
            "title_image_sha256": hashlib.sha256(title_payload).hexdigest(),
            "style_version": "ifanr-wechat-compatible-v6-browser",
            "wechat_account_fingerprint": "7" * 64,
            "local_qualification_record_sha256": "8" * 64,
        }
        draft_sha256 = hashlib.sha256((package / "draft.md").read_bytes()).hexdigest()
        html_sha256 = hashlib.sha256(html_payload).hexdigest()
        seal_material = {
            "draft_sha256": draft_sha256,
            "format_profile_sha256": state["format_profile_sha256"],
            "adapter_sha256": state["adapter_sha256"],
            "bridge_sha256": state["bridge_sha256"],
            "renderer_sha256": state["renderer_sha256"],
            "format_contract_sha256": state["format_contract_sha256"],
            "style_version": state["style_version"],
            "html_sha256": html_sha256,
            "title_image_sha256": state["title_image_sha256"],
            "local_format_qualified": True,
            "warning_codes": [],
        }
        build = {
            "schema_version": 1,
            "tool_version": "0.2.0",
            "created_at": "2026-07-27T00:00:00+00:00",
            "package": str(package.resolve()),
            "title": "API title",
            "draft_sha256": draft_sha256,
            "profile_id": state["profile_id"],
            "profile_sha256": state["profile_sha256"],
            "format_profile_sha256": state["format_profile_sha256"],
            "adapter_sha256": state["adapter_sha256"],
            "bridge_sha256": state["bridge_sha256"],
            "format_contract_sha256": state["format_contract_sha256"],
            "renderer_sha256": state["renderer_sha256"],
            "title_image_sha256": state["title_image_sha256"],
            "style_version": state["style_version"],
            "html_path": "dist/content-sync/article.html",
            "html_sha256": html_sha256,
            "payload_sha256": "9" * 64,
            "fixture_sha256": "a" * 64,
            "sealed_build_sha256": hashlib.sha256(
                MODULE.canonical_json_bytes(seal_material)
            ).hexdigest(),
            "block_count": 2,
            "article_image_bytes": len(body_payload),
            "image_count": 2,
            "gallery_count": 0,
            "text_fidelity": {
                "confirmed": True,
                "sourceCharCount": 5,
                "renderedCharCount": 5,
                "sourceHash": "body",
                "renderedHash": "body",
            },
            "image_fidelity": {
                "confirmed": True,
                "sourceImageCount": 1,
                "renderedImageCount": 1,
                "placeholderCount": 0,
                "accountedImageCount": 1,
            },
            "warning_counts": {"gif": 0, "media": 0, "content": 0},
            "warning_codes": [],
            "local_format_qualified": True,
            "company_format_qualified": True,
            "qualification_blockers": [],
            "external_writes_performed": False,
        }
        output = package / "dist" / "content-sync"
        output.mkdir(parents=True)
        html_path = output / "article.html"
        build_path = output / "build.json"
        html_path.write_bytes(html_payload)
        build_path.write_text(
            json.dumps(build, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return package, build_path, state

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

    def test_appsso_body_components_are_independent_from_manual_delivery_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            self.enable_appsso_layout(package)
            publish_path = package / "publish.yml"
            publish_path.write_text(
                publish_path.read_text(encoding="utf-8")
                .replace(
                    'delivery_mode: "sealed_draft"',
                    'delivery_mode: "manual_editor"',
                )
                .replace(
                    'layout_profile: "appsso-article-v1"',
                    'layout_profile: "default"',
                ),
                encoding="utf-8",
            )
            source, metadata, config, body = MODULE.prepare_source(package)
            self.assertTrue(source.is_file())
            self.assertIn("appsso-body-header", body)
            self.assertEqual(
                MODULE.publication_blockers(package, metadata, config), []
            )

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

    def test_delivery_mode_project_adapter_and_layout_profile_are_independent_gates(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            missing_adapter = self.make_package(root, "missing-adapter")
            publish_path = missing_adapter / "publish.yml"
            publish_path.write_text(
                publish_path.read_text(encoding="utf-8").replace(
                    'project_adapter: "generic"\n', ""
                )
                + 'layout_profile: "appsso-article-v1"\n',
                encoding="utf-8",
            )
            metadata, _ = MODULE.load_draft(missing_adapter)
            config = MODULE.load_publish_config(missing_adapter, metadata)
            blockers = MODULE.publication_blockers(missing_adapter, metadata, config)
            self.assertIn(
                "publish.yml must explicitly set project_adapter to a registered adapter",
                blockers,
            )
            self.assertIn(
                "layout_profile appsso-article-v1 requires project_adapter appsso",
                blockers,
            )

            appsso_default = self.make_package(root, "appsso-default")
            appsso_publish = appsso_default / "publish.yml"
            appsso_publish.write_text(
                appsso_publish.read_text(encoding="utf-8").replace(
                    'project_adapter: "generic"',
                    'project_adapter: "appsso"',
                ),
                encoding="utf-8",
            )
            metadata, _ = MODULE.load_draft(appsso_default)
            config = MODULE.load_publish_config(appsso_default, metadata)
            blockers = MODULE.publication_blockers(appsso_default, metadata, config)
            self.assertIn(
                "project_adapter appsso with delivery_mode sealed_draft requires layout_profile appsso-article-v1",
                blockers,
            )

            manual_fixed = self.make_package(root, "manual-fixed")
            self.enable_appsso_layout(manual_fixed)
            manual_publish = manual_fixed / "publish.yml"
            manual_publish.write_text(
                manual_publish.read_text(encoding="utf-8")
                .replace(
                    'delivery_mode: "sealed_draft"',
                    'delivery_mode: "manual_editor"',
                )
                .replace('theme: "default"', 'theme: "nondefault"'),
                encoding="utf-8",
            )
            metadata, _ = MODULE.load_draft(manual_fixed)
            config = MODULE.load_publish_config(manual_fixed, metadata)
            blockers = MODULE.publication_blockers(manual_fixed, metadata, config)
            self.assertIn(
                "delivery_mode manual_editor requires layout_profile default; visual formatting belongs in the WeChat editor",
                blockers,
            )
            self.assertIn(
                "delivery_mode manual_editor requires theme default; visual formatting belongs in the WeChat editor",
                blockers,
            )
            self.assertIn(
                "layout_profile appsso-article-v1 requires delivery_mode sealed_draft",
                blockers,
            )

            manual_mac = self.make_package(root, "manual-mac")
            self.enable_manual_editor(manual_mac)
            manual_mac_publish = manual_mac / "publish.yml"
            manual_mac_publish.write_text(
                manual_mac_publish.read_text(encoding="utf-8")
                + "mac_style: true\n",
                encoding="utf-8",
            )
            metadata, _ = MODULE.load_draft(manual_mac)
            config = MODULE.load_publish_config(manual_mac, metadata)
            blockers = MODULE.publication_blockers(manual_mac, metadata, config)
            self.assertIn(
                "delivery_mode manual_editor requires mac_style false; visual formatting belongs in the WeChat editor",
                blockers,
            )

            sealed_knobs = self.make_package(root, "sealed-knobs")
            self.enable_appsso_layout(sealed_knobs)
            sealed_publish = sealed_knobs / "publish.yml"
            sealed_publish.write_text(
                sealed_publish.read_text(encoding="utf-8")
                .replace('theme: "default"', 'theme: "orange"')
                + 'highlight: "github"\nmac_style: true\n',
                encoding="utf-8",
            )
            metadata, _ = MODULE.load_draft(sealed_knobs)
            config = MODULE.load_publish_config(sealed_knobs, metadata)
            blockers = MODULE.publication_blockers(
                sealed_knobs, metadata, config
            )
            self.assertIn(
                "layout_profile appsso-article-v1 requires theme default", blockers
            )
            self.assertIn(
                "layout_profile appsso-article-v1 requires highlight solarized-light",
                blockers,
            )
            self.assertIn(
                "layout_profile appsso-article-v1 requires mac_style false", blockers
            )

    def test_default_profile_does_not_silently_accept_appsso_components(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            self.write_test_image(package / "assets" / "standalone-header.png")
            publish = (package / "publish.yml").read_text(encoding="utf-8")
            publish += 'header_image: "assets/standalone-header.png"\n'
            (package / "publish.yml").write_text(publish, encoding="utf-8")
            with self.assertRaisesRegex(MODULE.WorkflowError, "supports body components"):
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

    def test_manual_editor_mode_strips_style_attributes_but_keeps_structure_and_prose(self) -> None:
        config = MODULE.PublishConfig(
            title="Test",
            delivery_mode="manual_editor",
            layout_profile="default",
        )
        rendered = (
            '<section id="wenyan" style="font-size: 16px; line-height: 1.75">'
            '<h2 style="margin: 1em 0">标题</h2>'
            '<p STYLE=color:red>Use style="color:red" in prose.</p>'
            '<img src="assets/body.png" alt="图片" style="max-width: 100%">'
            '</section>'
        )

        handoff = MODULE.apply_delivery_mode(rendered, config)

        parser = MODULE.ManualHandoffHtmlParser()
        parser.feed(handoff)
        parser.close()
        self.assertEqual(parser.removed_style_attributes, 0)
        self.assertIn('<h2>标题</h2>', handoff)
        self.assertIn('Use style="color:red" in prose.', handoff)
        self.assertIn('src="assets/body.png"', handoff)

    def test_manual_editor_sanitizes_legacy_presentation_markup_only(self) -> None:
        config = MODULE.PublishConfig(
            title="Test",
            delivery_mode="manual_editor",
            layout_profile="default",
        )
        rendered = (
            '<section id="article" class="wenyan" data-tool="x" '
            'align="center" lang="zh-CN">'
            '<center><font color="#f00" size="4">'
            '<h2 STYLE="font-size:20px">标题 &amp; 判断</h2>'
            '<p bgcolor="#fff"><span style="color:red"><strong>正文</strong></span> '
            '<a href="https://example.com" title="来源">链接</a></p>'
            '<img src="assets/body.png" alt="图片" title="图注" '
            'width="640" height="480">'
            '</font></center></section>'
        )

        handoff = MODULE.apply_delivery_mode(rendered, config)

        self.assertIn('<section lang="zh-CN">', handoff)
        self.assertIn('<h2>标题 &amp; 判断</h2>', handoff)
        self.assertIn('<strong>正文</strong>', handoff)
        self.assertIn(
            '<a href="https://example.com" title="来源">链接</a>', handoff
        )
        self.assertIn(
            '<img src="assets/body.png" alt="图片" title="图注">', handoff
        )
        for forbidden in (
            "<font",
            "<center",
            "<span",
            " style=",
            " class=",
            " data-tool=",
            " align=",
            " bgcolor=",
            " width=",
            " height=",
        ):
            self.assertNotIn(forbidden, handoff.casefold())
        self.assertEqual(
            MODULE.raw_html_image_sources(rendered),
            MODULE.raw_html_image_sources(handoff),
        )
        verifier = MODULE.ManualHandoffHtmlParser()
        verifier.feed(handoff)
        verifier.close()
        self.assertEqual([], verifier.removed_attributes)
        self.assertEqual([], verifier.removed_tags)
        self.assertEqual([], verifier.blocked_attributes)
        self.assertEqual([], verifier.blocked_tags)

    def test_manual_editor_rejects_hidden_or_interactive_markup(self) -> None:
        config = MODULE.PublishConfig(
            title="Test",
            delivery_mode="manual_editor",
            layout_profile="default",
        )
        for fragment in (
            "<p hidden>不可见正文</p>",
            '<p contenteditable="false">不可编辑正文</p>',
            "<template><p>模板正文</p></template>",
            "<dialog open>遮罩正文</dialog>",
            "<details open><p>折叠正文</p></details>",
            "<input value=\"伪正文\">",
            "<button>按钮</button>",
        ):
            with self.subTest(fragment=fragment), self.assertRaisesRegex(
                MODULE.WorkflowError,
                "unsupported interactive or hidden markup",
            ):
                MODULE.apply_delivery_mode(fragment, config)

        cleaned = MODULE.apply_delivery_mode(
            '<p>正文 <span id="decorative">仍可见</span></p>', config
        )
        self.assertEqual("<p>正文 仍可见</p>", cleaned)

    def test_manual_editor_rejects_unbalanced_or_misnested_markup(self) -> None:
        config = MODULE.PublishConfig(
            title="Test",
            delivery_mode="manual_editor",
            layout_profile="default",
        )
        for fragment in (
            "</article><p>正文逃出复制区</p>",
            "<p><strong>错位</p></strong>",
            "<p>未闭合",
            "<p />",
            "<img src=\"assets/body.png\"></img>",
        ):
            with self.subTest(fragment=fragment), self.assertRaisesRegex(
                MODULE.WorkflowError, "invalid HTML structure"
            ):
                MODULE.apply_delivery_mode(fragment, config)

    def test_author_html_cannot_override_controlled_layout(self) -> None:
        MODULE.ensure_author_html_safe(
            "`<p style=\"position:fixed\">example</p>`\n\n"
            "```html\n<p class=\"demo\">example</p>\n```\n"
        )
        for markdown in (
            '<p style="color:red">正文</p>',
            '<p class="appsso-body-header">正文</p>',
            '<p hidden>正文</p>',
            '<template><p>正文</p></template>',
            '<p align="right">正文</p>',
            '<img src="assets/body.png" alt="图" width="1" height="1">',
            '<table border="99" bgcolor="red"><tr><td>正文</td></tr></table>',
            '<p dir="rtl">正文</p>',
            '<p id="footnotes">正文</p>',
        ):
            with self.subTest(markdown=markdown), self.assertRaisesRegex(
                MODULE.WorkflowError, "author-controlled HTML"
            ):
                MODULE.ensure_author_html_safe(markdown)

    def test_manual_editor_mode_is_handoff_ready_but_cannot_create_api_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            publish_path = package / "publish.yml"
            publish_path.write_text(
                publish_path.read_text(encoding="utf-8").replace(
                    'delivery_mode: "sealed_draft"',
                    'delivery_mode: "manual_editor"',
                ),
                encoding="utf-8",
            )
            metadata, _ = MODULE.load_draft(package)
            config = MODULE.load_publish_config(package, metadata)
            blockers = MODULE.publication_blockers(package, metadata, config)
            self.assertEqual(blockers, [])

            fake_build = SimpleNamespace(
                config=config,
                validator_ok=True,
                validator_report="",
                blockers=[],
            )
            args = SimpleNamespace(package=str(package), execute=True, env=None)
            with (
                mock.patch.object(MODULE, "build_preview", return_value=fake_build),
                mock.patch.object(MODULE.subprocess, "run") as subprocess_run,
                self.assertRaisesRegex(MODULE.WorkflowError, "cannot create a WeChat API draft"),
            ):
                MODULE.command_draft(args)
            subprocess_run.assert_not_called()

    def test_missing_and_unknown_delivery_mode_fail_before_external_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            publish_path = package / "publish.yml"
            publish_path.write_text(
                publish_path.read_text(encoding="utf-8").replace(
                    'delivery_mode: "sealed_draft"\n', ""
                ),
                encoding="utf-8",
            )
            metadata, _ = MODULE.load_draft(package)
            config = MODULE.load_publish_config(package, metadata)
            self.assertTrue(
                any(
                    "must explicitly set delivery_mode" in item
                    for item in MODULE.publication_blockers(package, metadata, config)
                )
            )
            with self.assertRaisesRegex(MODULE.WorkflowError, "must explicitly set delivery_mode"):
                MODULE.get_delivery_mode(config, require_explicit=True)

        unknown = MODULE.PublishConfig(title="Test", delivery_mode="unknown")
        with self.assertRaisesRegex(MODULE.WorkflowError, "unknown delivery_mode"):
            MODULE.get_delivery_mode(unknown)

    def test_duplicate_yaml_keys_block_draft_before_any_external_command(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            publish_path = package / "publish.yml"
            publish_path.write_text(
                publish_path.read_text(encoding="utf-8")
                + 'delivery_mode: "manual_editor"\n',
                encoding="utf-8",
            )
            args = SimpleNamespace(package=str(package), execute=True, env=None)
            with (
                mock.patch.object(MODULE.subprocess, "run") as subprocess_run,
                self.assertRaisesRegex(MODULE.WorkflowError, "duplicate YAML key"),
            ):
                MODULE.command_draft(args)
            subprocess_run.assert_not_called()

    def test_yaml_root_and_publish_field_types_are_strict(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for index, payload in enumerate(
                ("[]\n", "false\n", "0\n", '""\n', "null\n")
            ):
                package = self.make_package(root, f"root-{index}")
                (package / "publish.yml").write_text(payload, encoding="utf-8")
                metadata, _ = MODULE.load_draft(package)
                with self.subTest(payload=payload), self.assertRaisesRegex(
                    MODULE.WorkflowError, "YAML root must be an object"
                ):
                    MODULE.load_publish_config(package, metadata)

            for name, mutation, message in (
                (
                    "bool-string",
                    lambda value: value + 'mac_style: "false"\n',
                    "mac_style must be a YAML boolean",
                ),
                (
                    "theme-bool",
                    lambda value: value.replace('theme: "default"', "theme: false"),
                    "theme must be a YAML string",
                ),
                (
                    "unknown",
                    lambda value: value + "layuot_profile: default\n",
                    "unknown field",
                ),
                (
                    "non-string-key",
                    lambda value: value + "1: value\n",
                    "field names must be YAML strings",
                ),
                (
                    "alias-conflict",
                    lambda value: value
                    + 'source_url: "https://example.com/source"\n'
                    + 'content_source_url: "https://example.com/legacy"\n',
                    "must not declare both source_url and content_source_url",
                ),
            ):
                package = self.make_package(root, name)
                publish_path = package / "publish.yml"
                publish_path.write_text(
                    mutation(publish_path.read_text(encoding="utf-8")),
                    encoding="utf-8",
                )
                metadata, _ = MODULE.load_draft(package)
                with self.subTest(name=name), self.assertRaisesRegex(
                    MODULE.WorkflowError, message
                ):
                    MODULE.load_publish_config(package, metadata)

    def test_handoff_command_accepts_only_manual_editor_without_network(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            handoff_path = root / "wechat-handoff.html"
            handoff_path.write_text("<p>ready</p>", encoding="utf-8")
            manual_build = SimpleNamespace(
                config=MODULE.PublishConfig(
                    title="Test", delivery_mode="manual_editor"
                ),
                validator_ok=True,
                validator_report="",
                blockers=[],
                handoff_path=handoff_path,
            )
            args = SimpleNamespace(package=str(root), open=False)
            with (
                mock.patch.object(MODULE, "build_preview", return_value=manual_build),
                mock.patch.object(MODULE, "verify_handoff_artifact") as verify_handoff,
                mock.patch.object(MODULE.subprocess, "run") as subprocess_run,
                redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(MODULE.command_handoff(args), 0)
            subprocess_run.assert_not_called()
            verify_handoff.assert_called_once_with(manual_build)

            sealed_build = SimpleNamespace(
                config=MODULE.PublishConfig(
                    title="Test", delivery_mode="sealed_draft"
                ),
                validator_ok=True,
                validator_report="",
                blockers=[],
                handoff_path=None,
            )
            with (
                mock.patch.object(MODULE, "build_preview", return_value=sealed_build),
                self.assertRaisesRegex(MODULE.WorkflowError, "requires delivery_mode manual_editor"),
            ):
                MODULE.command_handoff(args)

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

    def test_author_raw_html_cannot_smuggle_alternate_image_sources(self) -> None:
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

            with self.assertRaisesRegex(
                MODULE.WorkflowError, "resource-loading attribute data-src"
            ):
                MODULE.prepare_source(package)

    def test_unquoted_html_src_is_safely_inlined(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            fragment = "<img data-src=lazy.png src=assets/body.png alt=body>"

            build_dir = MODULE.create_build_dir(package)
            MODULE.stage_asset_bytes(
                package / "assets" / "body.png", build_dir, "assets/body.png"
            )
            inlined = MODULE.inline_preview_images(fragment, build_dir)
            self.assertIn('data-src="lazy.png"', inlined)
            self.assertRegex(inlined, r'\ssrc="data:image/png;base64,[^"]+"')

    def test_parser_based_inline_handles_gt_inside_an_attribute(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            build_dir = MODULE.create_build_dir(package)
            MODULE.stage_asset_bytes(
                package / "assets" / "body.png", build_dir, "assets/body.png"
            )
            fragment = '<img alt=">" src="assets/body.png">'

            inlined = MODULE.inline_preview_images(fragment, build_dir)

            self.assertIn('alt="&gt;"', inlined)
            self.assertRegex(inlined, r'\ssrc="data:image/png;base64,[^"]+"')
            self.assertEqual(1, len(MODULE.raw_html_image_sources(inlined)))

    def test_inline_preflight_encodes_each_unique_image_once_and_fails_before_encoding(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            build_dir = MODULE.create_build_dir(package)
            MODULE.stage_asset_bytes(
                package / "assets" / "body.png", build_dir, "assets/body.png"
            )
            fragment = (
                '<p><img src="assets/body.png" alt="一"></p>'
                '<p><img src="assets/body.png" alt="二"></p>'
            )
            real_encode = MODULE.base64.b64encode
            with mock.patch.object(
                MODULE.base64, "b64encode", wraps=real_encode
            ) as encode:
                graph = MODULE.prepare_inline_image_graph(fragment, build_dir)
                inlined = MODULE.inline_preview_images(fragment, build_dir, graph)
            self.assertEqual(1, encode.call_count)
            self.assertEqual(2, graph.image_order.count("assets/body.png"))
            self.assertEqual(2, inlined.count("data:image/png;base64,"))

            with (
                mock.patch.object(MODULE, "MAX_HANDOFF_IMAGE_BYTES", 1),
                mock.patch.object(MODULE.base64, "b64encode") as blocked_encode,
                self.assertRaisesRegex(
                    MODULE.WorkflowError, "before encoding or handoff copy"
                ),
            ):
                MODULE.prepare_inline_image_graph(fragment, build_dir)
            blocked_encode.assert_not_called()

    def test_inline_preflight_applies_aggregate_byte_budget_while_reading(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            build_dir = MODULE.create_build_dir(package)
            first = build_dir / "assets" / "body.png"
            second = build_dir / "assets" / "second.png"
            MODULE.stage_asset_bytes(
                package / "assets" / "body.png", build_dir, "assets/body.png"
            )
            self.write_test_image(second)
            first_size = first.stat().st_size
            second_size = second.stat().st_size
            fragment = (
                '<img src="assets/body.png" alt="一">'
                '<img src="assets/second.png" alt="二">'
            )
            real_reader = MODULE.stable_file_bytes
            with (
                mock.patch.object(
                    MODULE,
                    "MAX_HANDOFF_IMAGE_BYTES",
                    max(first_size, second_size) + 1,
                ),
                mock.patch.object(
                    MODULE,
                    "MAX_HANDOFF_TOTAL_ASSET_BYTES",
                    first_size + second_size - 1,
                ),
                mock.patch.object(
                    MODULE, "stable_file_bytes", wraps=real_reader
                ) as reader,
                mock.patch.object(MODULE.base64, "b64encode") as blocked_encode,
                self.assertRaisesRegex(
                    MODULE.WorkflowError, "before encoding or handoff copy"
                ),
            ):
                MODULE.prepare_inline_image_graph(fragment, build_dir)
            self.assertEqual(2, reader.call_count)
            self.assertEqual(
                second_size - 1,
                reader.call_args_list[-1].kwargs["max_bytes"],
            )
            blocked_encode.assert_not_called()

    def test_animated_image_frame_scan_stops_at_the_internal_ceiling(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "animated.gif"
            frames = [
                Image.new("RGB", (2, 2), color=color)
                for color in ((255, 0, 0), (0, 255, 0), (0, 0, 255))
            ]
            try:
                frames[0].save(
                    path,
                    format="GIF",
                    save_all=True,
                    append_images=frames[1:],
                    duration=10,
                    loop=0,
                )
            finally:
                for frame in frames:
                    frame.close()
            with (
                mock.patch.object(MODULE, "MAX_HANDOFF_IMAGE_FRAMES", 2),
                self.assertRaisesRegex(
                    MODULE.WorkflowError, "frame or decoded-pixel ceiling"
                ),
            ):
                MODULE.image_payload_metadata(path, path.read_bytes())

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
            wrapper_publish = wrapper_package / "publish.yml"
            wrapper_publish.write_text(
                wrapper_publish.read_text(encoding="utf-8").replace(
                    'project_adapter: "generic"',
                    'project_adapter: "appsso"',
                ),
                encoding="utf-8",
            )
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
        self.assertIn(".phone img{display:block;max-width:100%;height:auto}", document)

    def test_manual_editor_build_creates_versioned_handoff_with_resolvable_images(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            publish_path = package / "publish.yml"
            publish_path.write_text(
                publish_path.read_text(encoding="utf-8").replace(
                    'delivery_mode: "sealed_draft"',
                    'delivery_mode: "manual_editor"',
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
            rendered = (
                '<section id="wenyan" style="font-size:16px">'
                '<h2 style="margin:1em 0">标题</h2>'
                '<p style="padding:0 16px">正文</p>'
                '<p><img src="assets/body.png" alt="图片" '
                'style="max-width:100%;height:auto"></p>'
                '</section>'
            )
            with (
                mock.patch.object(MODULE, "run_wenyan_render", return_value=rendered),
                mock.patch.object(MODULE, "validator_report", return_value=(True, "pass")),
            ):
                build = MODULE.build_preview(package)

            self.assertEqual(build.blockers, [])
            self.assertIsNotNone(build.handoff_path)
            handoff_path = build.handoff_path
            assert handoff_path is not None
            content_path = handoff_path.parent / "wechat-content.html"
            content = content_path.read_text(encoding="utf-8")
            style_parser = MODULE.ManualHandoffHtmlParser()
            style_parser.feed(content)
            style_parser.close()
            self.assertEqual(style_parser.removed_style_attributes, 0)
            self.assertTrue((content_path.parent / "assets" / "body.png").is_file())
            self.assertIn('src="assets/body.png"', content)

            handoff = handoff_path.read_text(encoding="utf-8")
            self.assertIn('id="copy-article"', handoff)
            self.assertIn(".wechat-handoff-content img", handoff)
            self.assertRegex(handoff, r'src="data:image/png;base64,[^"]+"')

            latest_content = (package / "dist" / "wechat-content.html").read_text(
                encoding="utf-8"
            )
            self.assertRegex(latest_content, r'src="data:image/png;base64,[^"]+"')
            latest_style_parser = MODULE.ManualHandoffHtmlParser()
            latest_style_parser.feed(latest_content)
            latest_style_parser.close()
            self.assertEqual(latest_style_parser.removed_style_attributes, 0)
            plan = json.loads(
                (handoff_path.parent / "publish-plan.json").read_text(encoding="utf-8")
            )
            MODULE.verify_handoff_artifact(build)
            self.assertEqual(plan["path_base"], "dist")
            self.assertEqual(plan["delivery"]["mode"], "manual_editor")
            self.assertFalse(plan["delivery"]["api_draft_allowed"])
            self.assertEqual(
                plan["delivery"]["handoff_asset_sha256"]["assets/body.png"],
                MODULE.file_sha256(package / "assets" / "body.png"),
            )
            self.assertEqual(
                plan["delivery"]["handoff_assets"]["assets/body.png"]["bytes"],
                (package / "assets" / "body.png").stat().st_size,
            )
            copy_payload = handoff_path.parent / "wechat-copy-payload.html"
            self.assertEqual(
                plan["delivery"]["copy_payload_sha256"],
                MODULE.file_sha256(copy_payload),
            )
            self.assertEqual(
                plan["delivery"]["handoff_document_sha256"],
                MODULE.file_sha256(handoff_path),
            )
            self.assertEqual(
                plan["delivery"]["handoff_content_bytes"],
                content_path.stat().st_size,
            )

    def test_manual_pipeline_unwraps_presentation_tags_before_global_gate(self) -> None:
        rendered = (
            '<center><font color="#f00"><p style="margin:1em">正文</p>'
            '</font></center><img src="assets/body.png" alt="图片">'
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manual_package = self.make_package(root, "manual")
            self.enable_manual_editor(manual_package)
            with (
                mock.patch.object(MODULE, "run_wenyan_render", return_value=rendered),
                mock.patch.object(MODULE, "validator_report", return_value=(True, "pass")),
            ):
                build = MODULE.build_preview(manual_package)
            assert build.handoff_path is not None
            content = (build.handoff_path.parent / "wechat-content.html").read_text(
                encoding="utf-8"
            )
            self.assertNotIn("<center", content)
            self.assertNotIn("<font", content)
            self.assertNotIn("style=", content)
            self.assertIn("<p>正文</p>", content)

            sealed_package = self.make_package(root, "sealed")
            with (
                mock.patch.object(MODULE, "run_wenyan_render", return_value=rendered),
                self.assertRaisesRegex(MODULE.WorkflowError, "unsafe for local preview"),
            ):
                MODULE.build_preview(sealed_package)

    def test_appsso_manual_build_gates_components_before_sanitizing_classes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            self.enable_appsso_layout(package, include_footer=True)
            self.register_body_image(package)
            publish_path = package / "publish.yml"
            publish_path.write_text(
                publish_path.read_text(encoding="utf-8")
                .replace(
                    'delivery_mode: "sealed_draft"',
                    'delivery_mode: "manual_editor"',
                )
                .replace(
                    'layout_profile: "appsso-article-v1"',
                    'layout_profile: "default"',
                ),
                encoding="utf-8",
            )
            rendered = (
                '<section class="appsso-body-header" style="width:100%">'
                '<img src="assets/appsso-header.gif" alt="头图" width="900">'
                '</section><h2 style="color:red">标题</h2>'
                '<p><img src="assets/body.png" alt="正文图"></p>'
                '<section class="appsso-body-footer" style="width:100%">'
                '<img src="assets/appsso-footer.jpg" alt="尾图" width="900">'
                '</section>'
            )
            with (
                mock.patch.object(MODULE, "run_wenyan_render", return_value=rendered),
                mock.patch.object(
                    MODULE, "validator_report", return_value=(True, "pass")
                ),
            ):
                build = MODULE.build_preview(package)
            self.assertEqual([], build.blockers)
            assert build.handoff_path is not None
            content = (
                build.handoff_path.parent / "wechat-content.html"
            ).read_text(encoding="utf-8")
            self.assertNotIn("appsso-body-header", content)
            self.assertNotIn("appsso-body-footer", content)
            self.assertNotIn(" style=", content.casefold())
            self.assertNotIn(" width=", content.casefold())
            self.assertLess(
                content.index("assets/appsso-header.gif"),
                content.index("assets/body.png"),
            )
            self.assertLess(
                content.index("assets/body.png"),
                content.index("assets/appsso-footer.jpg"),
            )
            plan = json.loads(
                build.handoff_plan_path.read_text(encoding="utf-8")
            )
            self.assertEqual(
                [
                    "assets/appsso-header.gif",
                    "assets/body.png",
                    "assets/appsso-footer.jpg",
                ],
                plan["delivery"]["handoff_image_order"],
            )
            MODULE.verify_handoff_artifact(build)

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

    def test_handoff_integrity_rejects_page_content_payload_asset_and_plan_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            self.enable_manual_editor(package)
            rendered = (
                '<section style="font-size:16px"><h2>标题</h2>'
                '<p>正文</p><img src="assets/body.png" alt="图片"></section>'
            )
            with (
                mock.patch.object(MODULE, "run_wenyan_render", return_value=rendered),
                mock.patch.object(
                    MODULE, "validator_report", return_value=(True, "pass")
                ),
            ):
                build = MODULE.build_preview(package)
            self.assertEqual([], build.blockers)
            MODULE.verify_handoff_artifact(build)
            assert build.handoff_path is not None
            assert build.handoff_plan_path is not None
            paths = {
                "document": build.handoff_path,
                "content": build.handoff_path.parent / "wechat-content.html",
                "copy payload": build.handoff_path.parent
                / "wechat-copy-payload.html",
                "asset": build.handoff_path.parent / "assets" / "body.png",
                "plan": build.handoff_plan_path,
            }
            originals = {name: path.read_bytes() for name, path in paths.items()}
            for name, path in paths.items():
                with self.subTest(artifact=name):
                    path.write_bytes(originals[name] + b"tampered")
                    with self.assertRaises(MODULE.WorkflowError):
                        MODULE.verify_handoff_artifact(build)
                    path.write_bytes(originals[name])
                    MODULE.verify_handoff_artifact(build)

            build.handoff_path.write_bytes(originals["document"] + b"tampered")
            args = SimpleNamespace(package=str(package), open=True)
            with (
                mock.patch.object(MODULE, "build_preview", return_value=build),
                mock.patch.object(MODULE.os, "startfile", create=True) as startfile,
                self.assertRaises(MODULE.WorkflowError),
            ):
                MODULE.command_handoff(args)
            startfile.assert_not_called()

    def test_handoff_resource_ceilings_are_inclusive_and_fail_above_limit(self) -> None:
        asset = {
            "assets/body.png": {
                "bytes": 10,
                "pixels_per_frame": 20,
                "frame_count": 1,
                "decoded_frame_pixels": 20,
            }
        }
        with (
            mock.patch.object(MODULE, "MAX_HANDOFF_IMAGE_BYTES", 10),
            mock.patch.object(MODULE, "MAX_HANDOFF_TOTAL_ASSET_BYTES", 10),
            mock.patch.object(MODULE, "MAX_HANDOFF_COPY_HTML_BYTES", 30),
            mock.patch.object(MODULE, "MAX_HANDOFF_IMAGE_PIXELS", 20),
            mock.patch.object(MODULE, "MAX_HANDOFF_DECODED_FRAME_PIXELS", 20),
        ):
            self.assertEqual([], MODULE.handoff_resource_blockers(asset, 30))
            asset["assets/body.png"]["bytes"] = 11
            asset["assets/body.png"]["pixels_per_frame"] = 21
            asset["assets/body.png"]["decoded_frame_pixels"] = 21
            blockers = MODULE.handoff_resource_blockers(asset, 31)
        self.assertEqual(5, len(blockers))

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
            '<p hidden>Hidden</p>',
            '<p contenteditable="false">Locked</p>',
            '<template><p>Template</p></template>',
            '<dialog open>Dialog</dialog>',
            '<details open><p>Details</p></details>',
            '<button>Button</button>',
            '<p style="position:fixed;z-index:999999">Overlay</p>',
            '<p style="display:none">Hidden style</p>',
            '</main><p>Escaped wrapper</p>',
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
                config=MODULE.PublishConfig(
                    title="Test", delivery_mode="sealed_draft"
                ),
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
            env_path.write_text(
                "WECHAT_APP_ID=test\nWECHAT_APP_SECRET=secret\n",
                encoding="utf-8",
            )
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
            env_path.write_text(
                "WECHAT_APP_ID=test\nWECHAT_APP_SECRET=secret\n",
                encoding="utf-8",
            )
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

    def test_execute_failure_reports_non_atomic_external_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = self.make_package(root)
            build = self.capture_preview_snapshot(package)
            env_path = root / ".env"
            env_path.write_text(
                "WECHAT_APP_ID=test\nWECHAT_APP_SECRET=secret\n",
                encoding="utf-8",
            )
            fake_wenyan = root / "wenyan.cmd"
            fake_wenyan.write_text("test", encoding="utf-8")
            args = SimpleNamespace(
                package=str(package), execute=True, env=str(env_path)
            )

            with (
                mock.patch.object(MODULE, "build_preview", return_value=build),
                mock.patch.object(MODULE, "WENYAN_CMD", fake_wenyan),
                mock.patch.object(
                    MODULE.subprocess,
                    "run",
                    return_value=SimpleNamespace(returncode=9),
                ) as subprocess_run,
                self.assertRaisesRegex(
                    MODULE.WorkflowError,
                    "permanent body/cover materials may already have been uploaded",
                ),
                redirect_stdout(io.StringIO()),
            ):
                MODULE.command_draft(args)
            subprocess_run.assert_called_once()

    def test_wenyan_environment_uses_only_the_explicit_credential_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            env_path = Path(temp) / ".env"
            env_path.write_text(
                'WECHAT_APP_ID="target-account"\n'
                "WECHAT_APP_SECRET='target-secret'\n",
                encoding="utf-8",
            )
            fingerprint, payload_hash = MODULE.wechat_credential_metadata(env_path)
            self.assertEqual(
                hashlib.sha256(b"target-account").hexdigest()[:12], fingerprint
            )
            self.assertEqual(hashlib.sha256(env_path.read_bytes()).hexdigest(), payload_hash)
            with mock.patch.dict(
                MODULE.os.environ,
                {
                    "WECHAT_APP_ID": "wrong-account",
                    "WECHAT_APP_SECRET": "wrong-secret",
                    "NODE_OPTIONS": "--env-file=wrong.env",
                    "NODE_PATH": "wrong-modules",
                },
                clear=False,
            ):
                environment = MODULE.wenyan_environment()
            for key in (
                "WECHAT_APP_ID",
                "WECHAT_APP_SECRET",
                "NODE_OPTIONS",
                "NODE_PATH",
            ):
                self.assertNotIn(key, environment)

    def test_execute_wraps_local_record_failure_as_possible_external_effect(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = self.make_package(root)
            build = self.capture_preview_snapshot(package)
            env_path = root / ".env"
            env_path.write_text(
                "WECHAT_APP_ID=test\nWECHAT_APP_SECRET=secret\n",
                encoding="utf-8",
            )
            fake_wenyan = root / "wenyan.cmd"
            fake_wenyan.write_text("test", encoding="utf-8")
            args = SimpleNamespace(
                package=str(package), execute=True, env=str(env_path)
            )
            with (
                mock.patch.object(MODULE, "build_preview", return_value=build),
                mock.patch.object(MODULE, "WENYAN_CMD", fake_wenyan),
                mock.patch.object(
                    MODULE.subprocess,
                    "run",
                    return_value=SimpleNamespace(returncode=0),
                ),
                mock.patch.object(
                    MODULE,
                    "atomic_write_text",
                    side_effect=OSError("local disk failure"),
                ),
                self.assertRaisesRegex(
                    MODULE.WorkflowError, "one draft may have been created"
                ),
                redirect_stdout(io.StringIO()),
            ):
                MODULE.command_draft(args)

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
            draft = package / "draft.md"
            draft.write_text(
                draft.read_text(encoding="utf-8") + "\ntransient change\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                MODULE.WorkflowError, "changed while sealing input: draft.md"
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

    def test_stable_file_bytes_enforces_expected_size_and_ceiling(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "artifact.bin"
            path.write_bytes(b"1234")
            self.assertEqual(
                b"1234",
                MODULE.stable_file_bytes(path, expected_size=4, max_bytes=4),
            )
            with self.assertRaisesRegex(MODULE.WorkflowError, "byte count mismatch"):
                MODULE.stable_file_bytes(path, expected_size=3, max_bytes=4)
            with self.assertRaisesRegex(MODULE.WorkflowError, "byte ceiling"):
                MODULE.stable_file_bytes(path, max_bytes=3)

    def test_stage_asset_enforces_ceiling_before_copying_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.png"
            source.write_bytes(b"1234")
            build_dir = root / "build"
            build_dir.mkdir()
            with (
                mock.patch.object(MODULE, "file_sha256") as hash_file,
                self.assertRaisesRegex(MODULE.WorkflowError, "byte ceiling"),
            ):
                MODULE.stage_asset_bytes(
                    source,
                    build_dir,
                    "assets/source.png",
                    max_bytes=3,
                )
            hash_file.assert_not_called()
            self.assertFalse((build_dir / "assets" / "source.png").exists())
            self.assertEqual([], list(build_dir.rglob("*.tmp")))

    def test_stable_copy_removes_installed_destination_after_hash_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.bin"
            destination = root / "destination.bin"
            source.write_bytes(b"payload")
            with (
                mock.patch.object(MODULE, "file_sha256", return_value="0" * 64),
                self.assertRaisesRegex(MODULE.WorkflowError, "destination hash mismatch"),
            ):
                MODULE.stable_copy_file(source, destination, max_bytes=7)
            self.assertFalse(destination.exists())
            self.assertEqual([], list(root.glob("*.tmp")))

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

    def test_first_concurrent_build_and_handoff_directory_allocation_is_unique(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            with ThreadPoolExecutor(max_workers=4) as executor:
                build_dirs = list(
                    executor.map(lambda _: MODULE.create_build_dir(package), range(4))
                )
                handoff_dirs = list(
                    executor.map(
                        lambda _: MODULE.create_handoff_dir(package), range(4)
                    )
                )
            self.assertEqual(4, len(set(build_dirs)))
            self.assertEqual(4, len(set(handoff_dirs)))
            self.assertTrue(all(path.is_dir() for path in build_dirs + handoff_dirs))

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
    def test_real_wenyan_manual_handoff_removes_presentation_markup(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            self.enable_manual_editor(package)
            source, _, config, _ = MODULE.prepare_source(package)
            raw = MODULE.run_wenyan_render(source, config)
            MODULE.ensure_passive_preview_html(raw)
            blockers = MODULE.rendered_image_gate_and_stage(
                package, source.parent, raw, config
            )
            cleaned = MODULE.apply_delivery_mode(raw, config)
            MODULE.ensure_passive_preview_html(cleaned)

        self.assertEqual([], blockers)
        self.assertIn("style=", raw.casefold())
        self.assertNotIn("style=", cleaned.casefold())
        self.assertEqual(
            MODULE.raw_html_image_sources(raw),
            MODULE.raw_html_image_sources(cleaned),
        )
        for tag in ("h2", "p", "img"):
            self.assertEqual(
                len(re.findall(fr"<{tag}\b", raw, re.I)),
                len(re.findall(fr"<{tag}\b", cleaned, re.I)),
            )
        verifier = MODULE.ManualHandoffHtmlParser()
        verifier.feed(cleaned)
        verifier.close()
        self.assertEqual([], verifier.removed_attributes)
        self.assertEqual([], verifier.removed_tags)

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

    def test_capability_is_local_and_does_not_read_credentials(self) -> None:
        with (
            mock.patch.object(MODULE.subprocess, "run") as subprocess_run,
            mock.patch.object(
                MODULE, "wechat_credential_metadata"
            ) as credential_metadata,
        ):
            report = MODULE.capability_report()

        self.assertTrue(report["ok"])
        self.assertTrue(report["capabilities"]["local_integrity_preflight"])
        self.assertTrue(report["capabilities"]["sealed_html_dry_run"])
        self.assertFalse(
            report["capabilities"]["trusted_production_qualification"]
        )
        self.assertFalse(report["capabilities"]["wechat_create_draft"])
        self.assertTrue(report["wenyan"]["available"])
        self.assertFalse(report["credentials_read"])
        self.assertFalse(report["network_accessed"])
        subprocess_run.assert_not_called()
        credential_metadata.assert_not_called()

    def test_local_preflight_capability_does_not_require_wenyan_install(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            missing = Path(temp) / "missing.json"
            with (
                mock.patch.object(MODULE, "WENYAN_PACKAGE_JSON", missing),
                mock.patch.object(MODULE, "WENYAN_PACKAGE_LOCK", missing),
                mock.patch.object(MODULE, "WENYAN_INSTALLED_PACKAGE_JSON", missing),
                mock.patch.object(MODULE, "WENYAN_CMD", Path(temp) / "missing.cmd"),
            ):
                report = MODULE.capability_report()

        self.assertTrue(report["ok"])
        self.assertTrue(report["capabilities"]["local_integrity_preflight"])
        self.assertFalse(report["wenyan"]["available"])
        self.assertTrue(report["wenyan"]["blockers"])
        self.assertEqual([], report["blockers"])

    def test_local_preflight_hash_and_package_path_contracts_are_strict(self) -> None:
        digest = "a" * 64
        self.assertEqual(digest, MODULE.required_sha256(digest, "digest"))
        for invalid in ("A" * 64, 1, None):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(
                MODULE.WorkflowError, "lowercase SHA-256"
            ):
                MODULE.required_sha256(invalid, "digest")

        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp) / "package"
            artifact = package / "dist" / "content-sync" / "build.json"
            artifact.parent.mkdir(parents=True)
            artifact.write_text("{}", encoding="utf-8")
            self.assertEqual(
                artifact.resolve(),
                MODULE.resolved_package_artifact(
                    package, Path("dist/content-sync/build.json"), "artifact"
                ),
            )
            with self.assertRaisesRegex(MODULE.WorkflowError, "escapes"):
                MODULE.resolved_package_artifact(
                    package, Path("../outside.json"), "artifact"
                )
            with (
                mock.patch.object(
                    MODULE,
                    "is_link_or_junction",
                    side_effect=lambda path: path.name == "content-sync",
                ),
                self.assertRaisesRegex(MODULE.WorkflowError, "symlink or junction"),
            ):
                MODULE.resolved_package_artifact(
                    package, Path("dist/content-sync/build.json"), "artifact"
                )

    def test_current_unqualified_company_profile_blocks_sealed_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package, build_path, _state = self.make_company_sealed_fixture(Path(temp))
            with self.assertRaisesRegex(
                MODULE.WorkflowError, "local company format round-trip record is incomplete"
            ):
                MODULE.sealed_draft_dry_run_report(package, build_path)

    def test_sealed_dry_run_is_deterministic_and_has_no_external_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package, build_path, state = self.make_company_sealed_fixture(Path(temp))
            with (
                mock.patch.object(
                    MODULE, "load_current_company_format_state", return_value=state
                ),
                mock.patch.object(MODULE.subprocess, "run") as subprocess_run,
                mock.patch.object(
                    MODULE, "wechat_credential_metadata"
                ) as credential_metadata,
            ):
                first = MODULE.sealed_draft_dry_run_report(package, build_path)
                second = MODULE.sealed_draft_dry_run_report(package, build_path)

        self.assertEqual(first["operation_id"], second["operation_id"])
        self.assertEqual(
            first["integrity_scope_sha256"],
            second["integrity_scope_sha256"],
        )
        self.assertEqual(
            hashlib.sha256(
                MODULE.canonical_json_bytes(first["integrity_scope"])
            ).hexdigest(),
            first["integrity_scope_sha256"],
        )
        for field in (
            "local_build_sha256",
            "build_receipt_sha256",
            "html_sha256",
            "format_contract_sha256",
            "materials_sha256",
        ):
            self.assertRegex(first[field], r"^[0-9a-f]{64}$")
        self.assertFalse(first["execute_available"])
        self.assertEqual("local_integrity_only", first["preflight_kind"])
        self.assertFalse(first["trusted_production_qualification"])
        self.assertFalse(first["authorization_ready"])
        self.assertFalse(first["credentials_read"])
        self.assertFalse(first["network_accessed"])
        subprocess_run.assert_not_called()
        credential_metadata.assert_not_called()

    def test_sealed_dry_run_rejects_html_and_material_changes(self) -> None:
        for mutation in ("html", "material"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temp:
                package, build_path, state = self.make_company_sealed_fixture(
                    Path(temp), f"company-{mutation}"
                )
                if mutation == "html":
                    html_path = package / "dist" / "content-sync" / "article.html"
                    html_path.write_bytes(html_path.read_bytes() + b" ")
                    expected = "HTML hash does not match"
                else:
                    with Image.new("RGB", (4, 3), color=(1, 2, 3)) as image:
                        image.save(package / "assets" / "body.png", format="PNG")
                    expected = "image graph does not exactly match"
                with (
                    mock.patch.object(
                        MODULE,
                        "load_current_company_format_state",
                        return_value=state,
                    ),
                    self.assertRaisesRegex(MODULE.WorkflowError, expected),
                ):
                    MODULE.sealed_draft_dry_run_report(package, build_path)

    def test_new_commands_preserve_old_parser_routes(self) -> None:
        parser = MODULE.make_parser()
        self.assertIs(
            parser.parse_args(["preview", "package"]).func,
            MODULE.command_preview,
        )
        self.assertIs(
            parser.parse_args(["handoff", "package"]).func,
            MODULE.command_handoff,
        )
        self.assertIs(
            parser.parse_args(["draft", "package"]).func,
            MODULE.command_draft,
        )
        self.assertIs(
            parser.parse_args(["capability", "--json"]).func,
            MODULE.command_capability,
        )
        sealed = parser.parse_args(
            ["sealed-draft-dry-run", "package", "--build", "build.json", "--json"]
        )
        self.assertIs(sealed.func, MODULE.command_sealed_draft_dry_run)
        self.assertFalse(hasattr(sealed, "execute"))


if __name__ == "__main__":
    unittest.main()
