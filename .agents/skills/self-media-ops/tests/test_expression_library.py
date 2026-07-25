# -*- coding: utf-8 -*-
from __future__ import annotations

import unittest
from pathlib import Path

import yaml


LIBRARY_PATH = (
    Path(__file__).resolve().parents[1]
    / "references"
    / "wechat-expression-library.yml"
)


class ExpressionLibraryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.library = yaml.safe_load(LIBRARY_PATH.read_text(encoding="utf-8"))

    def test_library_has_two_balanced_priority_passes(self) -> None:
        entries = self.library["entries"]
        self.assertEqual(len(entries), 20)
        self.assertEqual(
            sum(entry["action"] == "default_avoid" for entry in entries),
            10,
        )
        self.assertEqual(
            sum(entry["action"] == "semantic_review" for entry in entries),
            10,
        )
        self.assertEqual(
            {entry["priority"] for entry in entries},
            {"P0", "P1"},
        )

    def test_user_approved_groups_are_pinned_to_their_actions(self) -> None:
        expected_p0 = {
            "WX-EXPR-001": "注意力提示语",
            "WX-EXPR-002": "空泛权威",
            "WX-EXPR-003": "预制确定性",
            "WX-EXPR-004": "报告式总结",
            "WX-EXPR-005": "代替论证的显然性",
            "WX-EXPR-006": "万能时代背景",
            "WX-EXPR-007": "作者舞台指令",
            "WX-EXPR-008": "无条件绝对化",
            "WX-EXPR-009": "空对称框架",
            "WX-EXPR-010": "夸张意义判断",
        }
        expected_p1 = {
            "WX-EXPR-011": "问题层级升级",
            "WX-EXPR-012": "推断连接器",
            "WX-EXPR-013": "本质化框架",
            "WX-EXPR-014": "递进升级句",
            "WX-EXPR-015": "高显著否定对比",
            "WX-EXPR-016": "序号脚手架",
            "WX-EXPR-017": "背景连接器",
            "WX-EXPR-018": "解释框架词簇",
            "WX-EXPR-019": "业务抽象名词",
            "WX-EXPR-020": "非字面动作与隐喻链",
        }
        entries = {entry["id"]: entry for entry in self.library["entries"]}
        for entry_id, label in expected_p0.items():
            with self.subTest(entry=entry_id):
                self.assertEqual(entries[entry_id]["label"], label)
                self.assertEqual(entries[entry_id]["priority"], "P0")
                self.assertEqual(entries[entry_id]["action"], "default_avoid")
        for entry_id, label in expected_p1.items():
            with self.subTest(entry=entry_id):
                self.assertEqual(entries[entry_id]["label"], label)
                self.assertEqual(entries[entry_id]["priority"], "P1")
                self.assertEqual(entries[entry_id]["action"], "semantic_review")

    def test_every_entry_is_explainable_and_has_counterexample_boundary(self) -> None:
        required = {
            "id",
            "priority",
            "action",
            "label",
            "patterns",
            "mechanism",
            "repair",
            "allow",
        }
        for entry in self.library["entries"]:
            with self.subTest(entry=entry["id"]):
                self.assertEqual(set(entry), required)
                self.assertRegex(entry["id"], r"^WX-EXPR-\d{3}$")
                self.assertTrue(entry["patterns"])
                self.assertTrue(entry["mechanism"].strip())
                self.assertTrue(entry["repair"].strip())
                self.assertTrue(entry["allow"].strip())

    def test_ids_are_unique_and_ordered(self) -> None:
        ids = [entry["id"] for entry in self.library["entries"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(
            ids,
            [f"WX-EXPR-{index:03d}" for index in range(1, 21)],
        )

    def test_policy_rejects_keyword_blacklist_implementation(self) -> None:
        forbidden = self.library["policy"]["forbidden_implementation"]
        self.assertIn("正文关键词黑名单", forbidden)
        self.assertEqual(self.library["mode"], "semantic_candidate_library")


if __name__ == "__main__":
    unittest.main()
