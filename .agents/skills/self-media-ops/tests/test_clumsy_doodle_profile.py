# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = (
    WORKSPACE_ROOT
    / ".agents"
    / "skills"
    / "self-media-ops"
    / "scripts"
    / "preflight_image_generation.py"
)
SPEC = importlib.util.spec_from_file_location("clumsy_doodle_preflight", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load preflight script: {SCRIPT_PATH}")
PREFLIGHT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PREFLIGHT
SPEC.loader.exec_module(PREFLIGHT)


class ClumsyDoodleProfileTests(unittest.TestCase):
    def load_contract(self) -> tuple[dict[str, object], dict[str, object], str]:
        registry_path = WORKSPACE_ROOT / "共享" / "运营" / "SOP" / "笨拙涂鸦风格档案.json"
        template_path = (
            WORKSPACE_ROOT
            / "共享"
            / "模板"
            / "生图计划"
            / "笨拙涂鸦直出计划模板.json"
        )
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        template = json.loads(template_path.read_text(encoding="utf-8"))
        profile = registry["profiles"]["clumsy-doodle-v1"]
        prompt_path = WORKSPACE_ROOT / profile["prompt_source"]
        lines = prompt_path.read_text(encoding="utf-8").splitlines()
        heading_index = lines.index(profile["prompt_heading"])
        prompt_line = next(line for line in lines[heading_index + 1 :] if line.strip())
        self.assertTrue(prompt_line.startswith("> "))
        return profile, template, prompt_line[2:]

    def write_package(self, root: Path, plan: dict[str, object]) -> Path:
        package = root / "package"
        (package / "assets").mkdir(parents=True, exist_ok=True)
        (package / "research").mkdir(exist_ok=True)
        (package / "publish.yml").write_text(
            'project_adapter: "generic"\nlayout_profile: "default"\n',
            encoding="utf-8",
        )
        plan = copy.deepcopy(plan)
        plan.pop("template_only", None)
        (package / "research" / "image-generation-plan.json").write_text(
            json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return package

    def test_prompt_hash_template_and_image_budget_are_locked(self) -> None:
        profile, template, prompt = self.load_contract()
        prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        self.assertEqual(profile["prompt_sha256"], prompt_hash)
        self.assertEqual(profile["prompt_characters"], len(prompt))
        self.assertEqual("clumsy-doodle-v1", template["style_policy"]["profile"])
        self.assertEqual(6, template["image_budget"]["default_total_body_images_min"])
        self.assertEqual(10, template["image_budget"]["default_total_body_images_max"])
        final_stage = template["tasks"][0]["final_stage"]
        self.assertEqual(prompt_hash, final_stage["prompt_sha256"])
        self.assertNotIn("content_prompt", final_stage)
        self.assertTrue(final_stage["preserve"][0].startswith("本图只画："))

    def test_preflight_accepts_template_and_rejects_style_regressions(self) -> None:
        _, template, _ = self.load_contract()
        with tempfile.TemporaryDirectory(dir=WORKSPACE_ROOT) as temp_dir:
            package = self.write_package(Path(temp_dir), template)
            receipt, _, _ = PREFLIGHT.build_request(package, "doodle-01", "final")
            self.assertEqual("clumsy-doodle-v1", receipt["style_profile"])
            self.assertEqual("pass", receipt["status"])

            blocked = copy.deepcopy(template)
            blocked["tasks"][0]["final_stage"]["output_constraints"].append(
                "Use cinematic composition."
            )
            package = self.write_package(Path(temp_dir), blocked)
            with self.assertRaisesRegex(PREFLIGHT.ContractError, "conflicts"):
                PREFLIGHT.build_request(package, "doodle-01", "final")

            blocked = copy.deepcopy(template)
            blocked["tasks"][0]["final_stage"]["avoid"].append(
                "Avoid pixelated edges."
            )
            package = self.write_package(Path(temp_dir), blocked)
            with self.assertRaisesRegex(PREFLIGHT.ContractError, "rejects required traits"):
                PREFLIGHT.build_request(package, "doodle-01", "final")


if __name__ == "__main__":
    unittest.main()
