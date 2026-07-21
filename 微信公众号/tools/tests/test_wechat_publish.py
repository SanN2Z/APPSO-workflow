from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "wechat_publish.py"
SPEC = importlib.util.spec_from_file_location("wechat_publish", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not import {MODULE_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class WechatPublishAdapterTests(unittest.TestCase):
    def make_package(self, root: Path) -> Path:
        package = root / "package"
        (package / "assets").mkdir(parents=True)
        (package / "assets" / "body.png").write_bytes(b"png")
        (package / "assets" / "cover.png").write_bytes(b"png")
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
    rights_status: "project_owned"
    allowed_platforms: ["wechat"]
""",
            encoding="utf-8",
        )
        return package

    def test_prepare_source_uses_api_title_and_relocates_images(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            source, metadata, config, body = MODULE.prepare_source(package)
            generated = source.read_text(encoding="utf-8")
            self.assertEqual(config.title, "API title")
            self.assertEqual(metadata["status"], "ready")
            self.assertNotIn("# Editorial title", body)
            self.assertIn("../assets/body.png", generated)
            self.assertIn("cover: ../assets/cover.png", generated)
            self.assertNotIn("digest:", generated)

    def test_release_gate_accepts_registered_cleared_cover(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            metadata, _ = MODULE.load_draft(package)
            config = MODULE.load_publish_config(package, metadata)
            self.assertEqual(MODULE.publication_blockers(package, metadata, config), [])

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
            self.assertTrue(any("rights_status is unresolved" in item for item in blockers))


if __name__ == "__main__":
    unittest.main()
