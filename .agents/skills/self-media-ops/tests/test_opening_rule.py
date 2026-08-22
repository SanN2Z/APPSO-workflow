from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[4]
SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SKILL_ROOT / "scripts" / "check_wechat_opening.py"
REGRESSION_PATH = SKILL_ROOT / "references" / "wechat-opening-regression.yml"
WORKFLOW_PATH = ROOT / "共享" / "运营" / "SOP" / "内容工作流.md"
CO_WRITING_TEMPLATE_PATH = (
    ROOT
    / "共享"
    / "模板"
    / "微信公众号内容包"
    / "research"
    / "co-writing-log.md"
)

SPEC = importlib.util.spec_from_file_location("check_wechat_opening", SCRIPT_PATH)
assert SPEC and SPEC.loader
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


class OpeningRuleTests(unittest.TestCase):
    def test_regression_cases(self) -> None:
        regression = yaml.safe_load(REGRESSION_PATH.read_text(encoding="utf-8"))
        outcomes = set()
        for case in regression["cases"]:
            result = CHECKER.evaluate_opening(
                case["text"],
                content_type=case["content_type"],
                exception_reason=case.get("exception_reason", ""),
            )
            outcomes.add(result.status)
            self.assertEqual(case["expected"], result.status, case["id"])
        self.assertEqual({"allow", "flag"}, outcomes)

    def test_authoritative_rule_contract_is_unique_and_complete(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        marker = "### PROJECT-WECHAT-OPENING-001"
        self.assertEqual(1, workflow.count(marker))
        block = workflow.split(marker, 1)[1].split("\n### ", 1)[0]
        for field in ("触发：", "动作：", "通过：", "失败：", "范围：", "回归："):
            self.assertIn(field, block)
        self.assertIn("FB-005", block)
        self.assertIn("time_first_exception", block)

    def test_co_writing_log_carries_opening_decision(self) -> None:
        template = CO_WRITING_TEMPLATE_PATH.read_text(encoding="utf-8")
        for field in (
            "opening_rule_id: PROJECT-WECHAT-OPENING-001",
            "开场发动机：",
            "开场压力：",
            "`time_first_exception`：",
            "check_wechat_opening.py",
        ):
            self.assertIn(field, template)


if __name__ == "__main__":
    unittest.main()
