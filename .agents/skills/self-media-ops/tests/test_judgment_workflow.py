import hashlib
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[4]
REFERENCE_DIR = ROOT / ".agents/skills/self-media-ops/references"


class JudgmentWorkflowContractTests(unittest.TestCase):
    def test_clumsy_prompt_contract(self):
        data = yaml.safe_load(
            (REFERENCE_DIR / "wechat-clumsy-writing.yml").read_text(encoding="utf-8")
        )
        self.assertEqual(data["rule_id"], "PROJECT-CLUMSY-WRITING-001")
        self.assertEqual(data["prompt_version"], "0.1")
        self.assertEqual(data["effectiveness_status"], "unverified_hypothesis")
        prompt = data["writing_prompt"]["zh_v0_1"]
        self.assertTrue(prompt.startswith("把这篇稿子写得笨一点。"))
        self.assertTrue(prompt.endswith("把真正想说的话说出来就行。"))
        self.assertEqual(
            hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            data["prompt_sha256"],
        )
        self.assertEqual(
            set(data["modes"]),
            {"personal_visible", "company_restrained"},
        )
        prohibited = "\n".join(data["prohibited_degradation"])
        for required in ("事实错误", "逻辑断裂", "虚构", "专业术语"):
            self.assertIn(required, prohibited)

    def test_regression_has_allow_and_reject_cases(self):
        data = yaml.safe_load(
            (REFERENCE_DIR / "wechat-clumsy-writing-regression.yml").read_text(
                encoding="utf-8"
            )
        )
        outcomes = {case["expected"] for case in data["cases"]}
        modes = {case["mode"] for case in data["cases"]}
        self.assertEqual(outcomes, {"allow", "reject"})
        self.assertEqual(modes, {"personal_visible", "company_restrained"})
        self.assertEqual(data["evaluation"], "manual_semantic_review")

    def test_project_files_point_to_single_prompt_source(self):
        pointer_files = [
            ROOT / "AGENTS.md",
            ROOT / ".agents/skills/self-media-ops/SKILL.md",
            ROOT / "APPSO-数字资产/03-SOP/APPSO 内容生产 SOP.md",
        ]
        for path in pointer_files:
            text = path.read_text(encoding="utf-8")
            self.assertIn("wechat-clumsy-writing.yml", text)
            self.assertNotIn("把这篇稿子写得笨一点。", text)

    def test_judgment_gate_and_template_match(self):
        contract = (REFERENCE_DIR / "wechat-judgment-workshop.md").read_text(
            encoding="utf-8"
        )
        template = (
            ROOT
            / "共享/模板/微信公众号内容包/research/judgment-workshop.md"
        ).read_text(encoding="utf-8")
        for required in (
            "3–5 个候选判断",
            "3–5 个真实决策点",
            "一个普通读者可以复述的主判断",
            "2–4 个支撑判断",
            "`personal`",
            "`company`",
        ):
            self.assertIn(required, contract)
        for required in (
            "status: discussing",
            'voice_mode: ""',
            "decision_points_completed: 0",
            "user_confirmed: false",
            "## 共同处境",
            "## 主判断",
            "## 支撑判断",
            "## 放弃的方向",
            "## 读者带走什么",
        ):
            self.assertIn(required, template)


if __name__ == "__main__":
    unittest.main()
