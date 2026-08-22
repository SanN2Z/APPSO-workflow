# -*- coding: utf-8 -*-
from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[4]
CORE_PATH = ROOT / "共享/运营/SOP/内容工作流.md"
REGRESSION_PATH = (
    Path(__file__).resolve().parents[1]
    / "references"
    / "public-evidence-seam-regression.yml"
)
FROZEN_TEMPLATE_PATH = (
    ROOT
    / "共享/模板/微信公众号内容包/research/candidate-round-frozen-input.md"
)


class EvidenceSeamRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.core = CORE_PATH.read_text(encoding="utf-8")
        self.regression = yaml.safe_load(
            REGRESSION_PATH.read_text(encoding="utf-8")
        )
        self.frozen_template = FROZEN_TEMPLATE_PATH.read_text(
            encoding="utf-8"
        )

    def test_rule_has_one_authoritative_contract(self) -> None:
        self.assertEqual(
            self.core.count("### CORE-EVIDENCE-SEAM-001｜"),
            1,
        )
        rule_start = self.core.index("### CORE-EVIDENCE-SEAM-001｜")
        next_rule = self.core.index("\n### ", rule_start + 4)
        contract = self.core[rule_start:next_rule]
        for field in (
            "- 触发：",
            "- 动作：",
            "- 通过：",
            "- 失败：",
            "- 范围：",
            "- 回归：",
        ):
            self.assertIn(field, contract)

    def test_regression_covers_failures_and_counterexamples(self) -> None:
        self.assertEqual(
            self.regression["rule_id"],
            "CORE-EVIDENCE-SEAM-001",
        )
        cases = self.regression["cases"]
        self.assertEqual(len(cases), 6)
        self.assertEqual(
            sum(case["expected"] == "flag" for case in cases),
            3,
        )
        self.assertEqual(
            sum(case["expected"] == "allow" for case in cases),
            3,
        )
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["text"].strip())
                self.assertTrue(case["context"].strip())
                self.assertTrue(case["reason"].strip())
                if case["expected"] == "flag":
                    self.assertTrue(case["repair_target"].strip())

    def test_candidate_body_and_internal_mapping_are_separate(self) -> None:
        self.assertIn("同名 `.audit.md` sidecar", self.frozen_template)
        self.assertNotIn("正文后用 HTML 注释", self.frozen_template)
        self.assertIn(
            "evidence_seam_rule_id: CORE-EVIDENCE-SEAM-001",
            self.frozen_template,
        )


if __name__ == "__main__":
    unittest.main()
