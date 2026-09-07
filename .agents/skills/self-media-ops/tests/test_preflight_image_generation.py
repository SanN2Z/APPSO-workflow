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


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "preflight_image_generation.py"
)
SPEC = importlib.util.spec_from_file_location("preflight_image_generation", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load preflight script: {SCRIPT_PATH}")
PREFLIGHT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PREFLIGHT
SPEC.loader.exec_module(PREFLIGHT)


class ImageGenerationPreflightTests(unittest.TestCase):
    def make_workspace(self, root: Path) -> tuple[Path, dict[str, object]]:
        (root / "AGENTS.md").write_text("# Test workspace\n", encoding="utf-8")
        (root / "上下文").mkdir()
        (root / "共享").mkdir()
        (root / "config").mkdir()
        (root / "internal").mkdir()

        prompt = "A deliberately awkward dummy redraw prompt for contract testing."
        prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        (root / "internal" / "prompt.md").write_text(
            "# Dummy\n\n## Original Prompt\n\n> " + prompt + "\n",
            encoding="utf-8",
        )
        registry = {
            "schema_version": 1,
            "profiles": {
                "fixed-test": {
                    "classification": "internal",
                    "prompt_source": "internal/prompt.md",
                    "prompt_heading": "## Original Prompt",
                    "prompt_sha256": prompt_hash,
                    "prompt_characters": len(prompt),
                    "requires_reference": True,
                    "allowed_final_modes": ["referenced_edit", "image_edit"],
                    "new_image_strategy": "two_stage_reference_then_redraw",
                    "forbidden_positive_terms": [
                        "polished",
                        "clean vector",
                        "cinematic",
                        "高质量",
                        "矢量感",
                    ],
                    "forbidden_avoid_terms": [
                        "clumsy",
                        "white background",
                        "笨拙",
                    ],
                }
            },
        }
        registry["profiles"]["appsso-004"] = copy.deepcopy(
            registry["profiles"]["fixed-test"]
        )
        registry["profiles"]["generic-edit"] = {
            "classification": "internal",
            "requires_reference": True,
            "allowed_final_modes": ["referenced_edit", "image_edit"],
            "new_image_strategy": "reference_required",
            "forbidden_positive_terms": [],
            "forbidden_avoid_terms": [],
        }
        (root / "config" / "profiles.json").write_text(
            json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        package = root / "package"
        (package / "assets").mkdir(parents=True)
        (package / "research" / "source-assets").mkdir(parents=True)
        (package / "publish.yml").write_text(
            'project_adapter: "generic"\nlayout_profile: "default"\n',
            encoding="utf-8",
        )
        plan: dict[str, object] = {
            "schema_version": 1,
            "updated": "2026-07-22",
            "project_adapter": "generic",
            "profile_registry": "config/profiles.json",
            "style_policy": {
                "profile": "fixed-test",
                "scope": "all_ai_generated_editorial_images",
                "new_image_strategy": "two_stage_reference_then_redraw",
                "allow_final_text_to_image": False,
            },
            "tasks": [
                {
                    "id": "cover",
                    "visual_type": "general_editorial",
                    "purpose": "Show a system meeting reality and receiving feedback.",
                    "reference_strategy": "generated_base",
                    "reference_stage": {
                        "mode": "text_to_image",
                        "prompt_ref": "structure-reference-v1",
                        "output": "research/source-assets/reference.png",
                        "receipt": "research/image-generation-runs/cover-reference.json",
                        "present_to_user": False,
                        "content_prompt": "Create a neutral structural reference.",
                        "output_constraints": ["16:9"],
                        "avoid": ["logos"],
                    },
                    "final_stage": {
                        "mode": "referenced_edit",
                        "prompt_ref": "fixed-test",
                        "prompt_sha256": prompt_hash,
                        "input_assets": ["research/source-assets/reference.png"],
                        "output": "assets/output.png",
                        "receipt": "research/image-generation-runs/cover-final.json",
                        "present_to_user": True,
                        "preserve": ["the feedback loop"],
                        "output_constraints": ["16:9", "white background"],
                        "avoid": ["polished magazine finish"],
                    },
                }
            ],
        }
        self.write_plan(package, plan)
        self.write_manifest(package, rights_status="project_owned")
        return package, plan

    @staticmethod
    def write_plan(package: Path, plan: dict[str, object]) -> None:
        (package / "research" / "image-generation-plan.json").write_text(
            json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def write_manifest(
        package: Path,
        *,
        rights_status: str,
        version: int = 2,
    ) -> None:
        (package / "asset-manifest.yml").write_text(
            """version: %d
assets:
  - file: "research/source-assets/reference.png"
    used_in_draft: false
    use: "research_reference"
    source_type: "ai_generated"
    source: "Test structure reference"
    creator_or_rightsholder: "Test project"
    obtained_on: "2026-07-22"
    generator: "Codex built-in image_gen"
    model: "gpt-image-2"
    generation_mode: "text_to_image"
    prompt_ref: "structure-reference-v1"
    prompt_sha256: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    generation_constraints: "Test"
    input_assets: []
    generated_on: "2026-07-22"
    modifications: "None"
    rights_status: "%s"
    allowed_platforms: []
    attribution: "AI generated test"
"""
            % (version, rights_status),
            encoding="utf-8",
        )

    def test_reference_stage_passes_but_cannot_be_presented(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package, plan = self.make_workspace(Path(temp_dir))
            receipt, prompt, _ = PREFLIGHT.build_request(package, "cover", "reference")
            self.assertEqual("pass", receipt["status"])
            self.assertEqual("none", receipt["input_binding"])
            self.assertFalse(receipt["present_to_user"])
            self.assertIn("16:9", prompt)

            blocked = copy.deepcopy(plan)
            blocked["tasks"][0]["reference_stage"]["present_to_user"] = True
            self.write_plan(package, blocked)
            with self.assertRaisesRegex(PREFLIGHT.ContractError, "must not be presented"):
                PREFLIGHT.build_request(package, "cover", "reference")

    def test_template_plan_is_never_callable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package, plan = self.make_workspace(Path(temp_dir))
            plan["template_only"] = True
            self.write_plan(package, plan)
            with self.assertRaisesRegex(PREFLIGHT.ContractError, "template_only"):
                PREFLIGHT.build_request(package, "cover", "reference")

    def test_final_stage_blocks_until_reference_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package, _ = self.make_workspace(Path(temp_dir))
            with self.assertRaisesRegex(PREFLIGHT.ContractError, "does not exist"):
                PREFLIGHT.build_request(package, "cover", "final")

    def test_registered_local_reference_allows_final_stage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package, _ = self.make_workspace(Path(temp_dir))
            (package / "research" / "source-assets" / "reference.png").write_bytes(
                b"reference"
            )
            receipt, prompt, receipt_path = PREFLIGHT.build_request(
                package,
                "cover",
                "final",
                include_prompt=True,
            )
            self.assertEqual("referenced_image_paths", receipt["input_binding"])
            self.assertEqual("fixed-test", receipt["prompt_ref"])
            self.assertEqual(1, len(receipt["input_fingerprints"]))
            self.assertTrue(prompt.startswith("A deliberately awkward"))
            self.assertIn("prompt_payload", receipt)
            self.assertEqual(
                {
                    "prompt": prompt,
                    "referenced_image_paths": [
                        str(
                            (
                                package
                                / "research"
                                / "source-assets"
                                / "reference.png"
                            ).resolve()
                        )
                    ],
                },
                receipt["tool_request"],
            )

            PREFLIGHT.write_receipt(receipt, receipt_path)
            persisted = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertNotIn("prompt_payload", persisted)
            self.assertNotIn("tool_request", persisted)
            self.assertEqual(receipt["invocation_prompt_sha256"], persisted["invocation_prompt_sha256"])

    def test_fixed_profile_blocks_wrong_mode_and_positive_style_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package, plan = self.make_workspace(Path(temp_dir))
            (package / "research" / "source-assets" / "reference.png").write_bytes(
                b"reference"
            )

            wrong_mode = copy.deepcopy(plan)
            wrong_mode["tasks"][0]["final_stage"]["mode"] = "text_to_image"
            self.write_plan(package, wrong_mode)
            with self.assertRaisesRegex(PREFLIGHT.ContractError, "not allowed"):
                PREFLIGHT.build_request(package, "cover", "final")

            conflict = copy.deepcopy(plan)
            conflict["tasks"][0]["final_stage"]["output_constraints"].append(
                "Use CLEAN-vector geometry with cinematic depth"
            )
            self.write_plan(package, conflict)
            with self.assertRaisesRegex(PREFLIGHT.ContractError, "conflicts with"):
                PREFLIGHT.build_request(package, "cover", "final")

    def test_reference_stage_blocks_style_language_that_can_bleed_into_final(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package, plan = self.make_workspace(Path(temp_dir))
            blocked = copy.deepcopy(plan)
            blocked["tasks"][0]["reference_stage"]["content_prompt"] = (
                "Create a polished clean-vector cinematic technology-magazine cover."
            )
            self.write_plan(package, blocked)
            with self.assertRaisesRegex(PREFLIGHT.ContractError, "bleed into"):
                PREFLIGHT.build_request(package, "cover", "reference")

    def test_opposite_style_words_are_allowed_in_avoid_but_required_traits_are_not(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package, plan = self.make_workspace(Path(temp_dir))
            (package / "research" / "source-assets" / "reference.png").write_bytes(
                b"reference"
            )
            receipt, _, _ = PREFLIGHT.build_request(package, "cover", "final")
            self.assertEqual("pass", receipt["status"])

            blocked = copy.deepcopy(plan)
            blocked["tasks"][0]["final_stage"]["avoid"].append("No white-background look")
            self.write_plan(package, blocked)
            with self.assertRaisesRegex(PREFLIGHT.ContractError, "rejects required traits"):
                PREFLIGHT.build_request(package, "cover", "final")

    def test_uncleared_reference_rights_block_generation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package, _ = self.make_workspace(Path(temp_dir))
            (package / "research" / "source-assets" / "reference.png").write_bytes(
                b"reference"
            )
            self.write_manifest(package, rights_status="user_supplied")
            with self.assertRaisesRegex(PREFLIGHT.ContractError, "not cleared for derivative"):
                PREFLIGHT.build_request(package, "cover", "final")

    def test_version_3_manifest_allows_registered_reference_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package, _ = self.make_workspace(Path(temp_dir))
            (package / "research" / "source-assets" / "reference.png").write_bytes(
                b"reference"
            )
            self.write_manifest(
                package,
                rights_status="project_owned",
                version=3,
            )
            receipt, _, _ = PREFLIGHT.build_request(package, "cover", "final")
            self.assertEqual("pass", receipt["status"])
            self.assertEqual(
                "referenced_image_paths",
                receipt["input_binding"],
            )

    def test_final_output_cannot_overwrite_or_alias_local_input(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package, plan = self.make_workspace(Path(temp_dir))
            shared_path = package / "assets" / "Same.png"
            shared_path.write_bytes(b"reference")
            self.write_manifest(package, rights_status="project_owned")
            manifest_path = package / "asset-manifest.yml"
            manifest = manifest_path.read_text(encoding="utf-8").replace(
                "research/source-assets/reference.png",
                "assets/Same.png",
            )
            manifest_path.write_text(manifest, encoding="utf-8")
            blocked = copy.deepcopy(plan)
            blocked["tasks"][0]["reference_strategy"] = "provided_local"
            blocked["tasks"][0].pop("reference_stage")
            blocked["tasks"][0]["final_stage"]["input_assets"] = ["assets/Same.png"]
            blocked["tasks"][0]["final_stage"]["output"] = "assets/same.png"
            self.write_plan(package, blocked)
            with self.assertRaisesRegex(PREFLIGHT.ContractError, "must not overwrite"):
                PREFLIGHT.build_request(package, "cover", "final")

    def test_conversation_attachment_uses_only_num_last_images_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package, plan = self.make_workspace(Path(temp_dir))
            conversation = copy.deepcopy(plan)
            task = conversation["tasks"][0]
            task["reference_strategy"] = "conversation_attachment"
            task.pop("reference_stage")
            task["final_stage"]["input_assets"] = ["conversation:Image #1"]
            task["final_stage"]["num_last_images_to_include"] = 1
            task["final_stage"]["derivative_rights_confirmed"] = True
            self.write_plan(package, conversation)
            receipt, prompt, _ = PREFLIGHT.build_request(
                package,
                "cover",
                "final",
                include_prompt=True,
            )
            self.assertEqual("num_last_images_to_include", receipt["input_binding"])
            self.assertEqual(1, receipt["num_last_images_to_include"])
            self.assertEqual([], receipt["input_fingerprints"])
            self.assertEqual(
                {"prompt": prompt, "num_last_images_to_include": 1},
                receipt["tool_request"],
            )

            task["final_stage"]["derivative_rights_confirmed"] = False
            self.write_plan(package, conversation)
            with self.assertRaisesRegex(PREFLIGHT.ContractError, "derivative_rights_confirmed"):
                PREFLIGHT.build_request(package, "cover", "final")

    def test_explicit_generic_direct_profile_remains_a_valid_counterexample(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            package, plan = self.make_workspace(root)
            registry_path = root / "config" / "profiles.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["profiles"]["generic"] = {
                "classification": "internal",
                "requires_reference": False,
                "allowed_final_modes": ["text_to_image"],
                "new_image_strategy": "direct",
                "forbidden_positive_terms": [],
                "forbidden_avoid_terms": [],
            }
            registry_path.write_text(
                json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            generic = copy.deepcopy(plan)
            generic["style_policy"] = {
                "profile": "generic",
                "scope": "task",
                "new_image_strategy": "direct",
                "allow_final_text_to_image": True,
            }
            task = generic["tasks"][0]
            task["reference_strategy"] = "none"
            task.pop("reference_stage")
            task["final_stage"] = {
                "mode": "text_to_image",
                "prompt_ref": "generic",
                "input_assets": [],
                "output": "assets/generic.png",
                "receipt": "research/image-generation-runs/generic-final.json",
                "present_to_user": True,
                "content_prompt": "Create a simple abstract cover.",
                "output_constraints": ["16:9"],
                "avoid": ["logos"],
            }
            self.write_plan(package, generic)
            receipt, prompt, _ = PREFLIGHT.build_request(
                package,
                "cover",
                "final",
                include_prompt=True,
            )
            self.assertEqual("text_to_image", receipt["mode"])
            self.assertEqual("none", receipt["input_binding"])
            self.assertEqual("generic", receipt["prompt_ref"])
            self.assertEqual({"prompt": prompt}, receipt["tool_request"])

    def test_generic_reference_edit_is_executable_without_appsso_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package, plan = self.make_workspace(Path(temp_dir))
            (package / "research" / "source-assets" / "reference.png").write_bytes(
                b"reference"
            )
            generic_edit = copy.deepcopy(plan)
            generic_edit["style_policy"] = {
                "profile": "generic-edit",
                "scope": "task",
                "new_image_strategy": "reference_required",
                "allow_final_text_to_image": False,
            }
            task = generic_edit["tasks"][0]
            task["reference_strategy"] = "provided_local"
            task.pop("reference_stage")
            task["final_stage"] = {
                "mode": "image_edit",
                "prompt_ref": "generic-edit",
                "input_assets": ["research/source-assets/reference.png"],
                "output": "assets/generic-edit.png",
                "receipt": "research/image-generation-runs/generic-edit-final.json",
                "present_to_user": True,
                "content_prompt": "Remove the distracting object while preserving the subject.",
                "preserve": ["the main subject"],
                "output_constraints": ["16:9"],
                "avoid": ["logos"],
            }
            self.write_plan(package, generic_edit)
            receipt, prompt, _ = PREFLIGHT.build_request(package, "cover", "final")
            self.assertEqual("generic-edit", receipt["style_profile"])
            self.assertEqual("referenced_image_paths", receipt["input_binding"])
            self.assertTrue(prompt.startswith("Remove the distracting object"))
            self.assertNotIn("A deliberately awkward", prompt)

    def test_appsso_adapter_cannot_silently_select_generic_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            package, plan = self.make_workspace(root)
            registry_path = root / "config" / "profiles.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["profiles"]["generic"] = {
                "classification": "internal",
                "requires_reference": False,
                "allowed_final_modes": ["text_to_image"],
                "new_image_strategy": "direct",
                "forbidden_positive_terms": [],
                "forbidden_avoid_terms": [],
            }
            registry_path.write_text(
                json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            blocked = copy.deepcopy(plan)
            blocked["project_adapter"] = "appsso"
            (package / "publish.yml").write_text(
                'project_adapter: "appsso"\nlayout_profile: "default"\n',
                encoding="utf-8",
            )
            blocked["style_policy"] = {
                "profile": "appsso-004",
                "scope": "all_ai_generated_editorial_images",
                "new_image_strategy": "two_stage_reference_then_redraw",
                "allow_final_text_to_image": False,
            }
            task = blocked["tasks"][0]
            task["visual_type"] = "ai_editorial_creative"
            task["style_override"] = {
                "profile": "generic",
                "profile_registry": "config/profiles.json",
            }
            task["reference_strategy"] = "none"
            task.pop("reference_stage")
            task["final_stage"] = {
                "mode": "text_to_image",
                "prompt_ref": "generic",
                "input_assets": [],
                "output": "assets/generic.png",
                "receipt": "research/image-generation-runs/generic-final.json",
                "present_to_user": True,
                "content_prompt": "Create a simple abstract cover.",
                "output_constraints": ["16:9"],
                "avoid": ["logos"],
            }
            self.write_plan(package, blocked)
            with self.assertRaisesRegex(PREFLIGHT.ContractError, "override source"):
                PREFLIGHT.build_request(package, "cover", "final")

            task["style_override"] = {
                "profile": "generic",
                "profile_registry": "config/profiles.json",
                "source": "explicit_current_task_user",
                "reason": "The user explicitly requested a different style for this task.",
                "confirmed_on": "2026-07-22",
            }
            self.write_plan(package, blocked)
            receipt, _, _ = PREFLIGHT.build_request(package, "cover", "final")
            self.assertEqual("appsso", receipt["project_adapter"])
            self.assertEqual("generic", receipt["style_profile"])
            self.assertEqual("task", receipt["style_scope"])
            self.assertEqual(
                "explicit_current_task_user",
                receipt["style_override_source"],
            )

    def test_appsso_non_generatable_visual_type_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package, plan = self.make_workspace(Path(temp_dir))
            blocked = copy.deepcopy(plan)
            blocked["project_adapter"] = "appsso"
            (package / "publish.yml").write_text(
                'project_adapter: "appsso"\nlayout_profile: "default"\n',
                encoding="utf-8",
            )
            blocked["style_policy"]["profile"] = "appsso-004"
            blocked["tasks"][0]["visual_type"] = "precision_chart"
            self.write_plan(package, blocked)
            with self.assertRaisesRegex(PREFLIGHT.ContractError, "must not use image generation"):
                PREFLIGHT.build_request(package, "cover", "reference")

    def test_appsso_layout_profile_requires_appsso_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package, _ = self.make_workspace(Path(temp_dir))
            (package / "publish.yml").write_text(
                'project_adapter: "generic"\nlayout_profile: "appsso-article-v1"\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(PREFLIGHT.ContractError, "must be appsso"):
                PREFLIGHT.build_request(package, "cover", "reference")

    def test_appsso_adapter_requires_independent_publish_declaration(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package, plan = self.make_workspace(Path(temp_dir))
            appsso = copy.deepcopy(plan)
            appsso["project_adapter"] = "appsso"
            appsso["style_policy"]["profile"] = "appsso-004"
            appsso["tasks"][0]["visual_type"] = "ai_editorial_creative"
            self.write_plan(package, appsso)
            (package / "publish.yml").write_text(
                'layout_profile: "default"\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(PREFLIGHT.ContractError, "independent package"):
                PREFLIGHT.build_request(package, "cover", "reference")

    def test_schema_v2_requires_a_generated_visual_route(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package, plan = self.make_workspace(Path(temp_dir))
            blocked = copy.deepcopy(plan)
            blocked["schema_version"] = 2
            self.write_plan(package, blocked)
            with self.assertRaisesRegex(PREFLIGHT.ContractError, "visual_route"):
                PREFLIGHT.build_request(package, "cover", "reference")

    def test_appsso_infographic_uses_full_spec_and_registered_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            package, plan = self.make_workspace(root)
            full_spec = (
                "# APPSO infographic specification\r\n\r\n"
                "Use a 1080 x 1440 vertical canvas and the supplied logo.\r\n"
            )
            spec_path = root / "internal" / "infographic.md"
            spec_path.write_bytes(full_spec.encode("utf-8"))
            spec_hash = hashlib.sha256(full_spec.encode("utf-8")).hexdigest()

            registry_path = root / "config" / "profiles.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["profiles"]["appsso-infographic-v1"] = {
                "classification": "restricted",
                "prompt_source": "internal/infographic.md",
                "prompt_format": "full_file",
                "prompt_sha256": spec_hash,
                "requires_reference": True,
                "allowed_final_modes": ["referenced_edit", "image_edit"],
                "new_image_strategy": "reference_required",
                "forbidden_positive_terms": ["cinematic"],
                "forbidden_avoid_terms": ["vertical canvas"],
            }
            registry_path.write_text(
                json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            appsso = copy.deepcopy(plan)
            appsso["schema_version"] = 2
            appsso["project_adapter"] = "appsso"
            appsso["style_policy"]["profile"] = "appsso-004"
            task = appsso["tasks"][0]
            task["visual_type"] = "qualitative_explainer"
            task["visual_route"] = "infographic"
            task["style_override"] = {
                "profile": "appsso-infographic-v1",
                "profile_registry": "config/profiles.json",
                "source": "project_visual_route",
                "reason": "Fixed APPSO infographic route",
                "confirmed_on": "2026-08-25",
            }
            task["reference_strategy"] = "provided_local"
            task.pop("reference_stage")
            task["final_stage"] = {
                "mode": "referenced_edit",
                "prompt_ref": "appsso-infographic-v1",
                "prompt_sha256": spec_hash,
                "input_assets": ["research/source-assets/reference.png"],
                "output": "assets/infographic.png",
                "receipt": "research/image-generation-runs/infographic-final.json",
                "present_to_user": True,
                "preserve": ["three verified nodes and their order"],
                "output_constraints": ["1080 x 1440 mobile-readable graphic"],
                "avoid": ["invented numbers"],
            }
            (package / "publish.yml").write_text(
                'project_adapter: "appsso"\nlayout_profile: "default"\n',
                encoding="utf-8",
            )
            (package / "research" / "source-assets" / "reference.png").write_bytes(
                b"registered-logo-reference"
            )
            self.write_plan(package, appsso)

            receipt, prompt, _ = PREFLIGHT.build_request(
                package, "cover", "final"
            )
            self.assertEqual("infographic", receipt["visual_route"])
            self.assertEqual("appsso-infographic-v1", receipt["style_profile"])
            self.assertEqual("project_visual_route", receipt["style_override_source"])
            self.assertEqual("referenced_image_paths", receipt["input_binding"])
            self.assertTrue(prompt.startswith(full_spec))

    def test_project_visual_route_cannot_select_an_unrelated_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            package, plan = self.make_workspace(root)
            appsso = copy.deepcopy(plan)
            appsso["schema_version"] = 2
            appsso["project_adapter"] = "appsso"
            appsso["style_policy"]["profile"] = "appsso-004"
            task = appsso["tasks"][0]
            task["visual_type"] = "qualitative_explainer"
            task["visual_route"] = "infographic"
            task["style_override"] = {
                "profile": "generic-edit",
                "profile_registry": "config/profiles.json",
                "source": "project_visual_route",
                "reason": "Invalid route mapping",
                "confirmed_on": "2026-08-25",
            }
            task["reference_strategy"] = "provided_local"
            task.pop("reference_stage")
            task["final_stage"] = {
                "mode": "referenced_edit",
                "prompt_ref": "generic-edit",
                "input_assets": ["research/source-assets/reference.png"],
                "output": "assets/invalid.png",
                "receipt": "research/image-generation-runs/invalid-final.json",
                "present_to_user": True,
                "content_prompt": "Edit the reference.",
                "preserve": ["subject"],
                "output_constraints": ["vertical"],
                "avoid": ["logos"],
            }
            (package / "publish.yml").write_text(
                'project_adapter: "appsso"\nlayout_profile: "default"\n',
                encoding="utf-8",
            )
            (package / "research" / "source-assets" / "reference.png").write_bytes(
                b"reference"
            )
            self.write_plan(package, appsso)
            with self.assertRaisesRegex(
                PREFLIGHT.ContractError, "reserved for the APPSO infographic route"
            ):
                PREFLIGHT.build_request(package, "cover", "final")

    def test_windows_unsafe_ads_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package, plan = self.make_workspace(Path(temp_dir))
            blocked = copy.deepcopy(plan)
            blocked["tasks"][0]["final_stage"]["output"] = "assets/output.png:stream"
            self.write_plan(package, blocked)
            with self.assertRaisesRegex(PREFLIGHT.ContractError, "NTFS ADS"):
                PREFLIGHT.build_request(package, "cover", "reference")


if __name__ == "__main__":
    unittest.main()
