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
REGRESSION_PATH = (
    Path(__file__).resolve().parents[1]
    / "references"
    / "wechat-expression-ban-regression.yml"
)
RED_BLACK_PATH = (
    Path(__file__).resolve().parents[1]
    / "references"
    / "wechat-red-black-corpus.yml"
)
RED_REGRESSION_PATH = (
    Path(__file__).resolve().parents[1]
    / "references"
    / "wechat-red-corpus-regression.yml"
)


class ExpressionLibraryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.library = yaml.safe_load(LIBRARY_PATH.read_text(encoding="utf-8"))
        self.regression = yaml.safe_load(
            REGRESSION_PATH.read_text(encoding="utf-8")
        )
        self.red_black = yaml.safe_load(
            RED_BLACK_PATH.read_text(encoding="utf-8")
        )
        self.red_regression = yaml.safe_load(
            RED_REGRESSION_PATH.read_text(encoding="utf-8")
        )

    def test_library_keeps_original_appso_scope_and_adds_wechat_entries(self) -> None:
        entries = self.library["entries"]
        self.assertEqual(len(entries), 24)
        self.assertEqual(
            sum(entry["action"] == "default_avoid" for entry in entries),
            10,
        )
        self.assertEqual(
            sum(entry["action"] == "semantic_review" for entry in entries),
            14,
        )
        self.assertEqual(
            {entry["priority"] for entry in entries},
            {"P0", "P1"},
        )
        appso_ids = self.library["project_adapters"]["appso"]["entry_ids"]
        self.assertEqual(
            appso_ids,
            [f"WX-EXPR-{index:03d}" for index in range(1, 21)],
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
            "WX-EXPR-021": "万能未来收束",
            "WX-EXPR-022": "聊天机器人服务残留",
            "WX-EXPR-023": "洞察揭晓与金句槽位",
            "WX-EXPR-024": "罐装共情与假亲密",
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
            [f"WX-EXPR-{index:03d}" for index in range(1, 25)],
        )

    def test_wechat_adapter_is_an_explicit_project_ban_with_waivers(self) -> None:
        adapter = self.library["project_adapters"]["wechat_analytical"]
        banned = set(adapter["ban_entry_ids"])
        reviewed = set(adapter["review_entry_ids"])
        all_ids = {entry["id"] for entry in self.library["entries"]}
        self.assertFalse(banned & reviewed)
        self.assertEqual(banned | reviewed, all_ids)
        self.assertEqual(banned, all_ids)
        self.assertFalse(reviewed)
        self.assertEqual(len(banned), 24)
        self.assertGreaterEqual(len(adapter["waiver_types"]), 5)
        self.assertIn(
            "字面事实或具体对象名称，词语按本义使用且改写会损失准确性",
            adapter["waiver_types"],
        )
        self.assertIn("不用于断言文本由 AI 生成", adapter["authorship_boundary"])

    def test_user_feedback_is_the_first_expression_loss(self) -> None:
        basis = self.library["evidence_basis"]
        self.assertTrue(
            basis["decision_order"][0].startswith(
                "用户在真实稿件中的修改意见"
            )
        )
        self.assertIn("最小化用户反馈 loss", basis["project_principle"])
        self.assertIn("一次明确厌恶即可形成禁用", basis["project_principle"])
        self.assertIn("无需第二案例", basis["project_principle"])

    def test_policy_rejects_authorship_inference_and_unscoped_raw_deletion(self) -> None:
        forbidden = self.library["policy"]["forbidden_implementation"]
        self.assertIn("把模式命中用作 AI 作者身份、代写或诚信判定", forbidden)
        self.assertIn(
            "其他项目未采用公众号 adapter 时，未读取上下文便自动删除 semantic_review 条目",
            forbidden,
        )
        self.assertEqual(self.library["mode"], "semantic_candidate_library")

    def test_manual_regression_covers_bans_and_narrow_waivers(self) -> None:
        self.assertEqual(
            self.regression["rule_id"],
            "PROJECT-WECHAT-AI-LEXICON-001",
        )
        cases = self.regression["cases"]
        self.assertEqual(len(cases), 20)
        self.assertEqual(
            sum(case["expected"] == "flag" for case in cases),
            13,
        )
        self.assertEqual(
            sum(case["expected"] == "allow_with_waiver" for case in cases),
            7,
        )
        flagged_ids = {
            case["entry_id"]
            for case in cases
            if case["expected"] == "flag"
        }
        self.assertTrue(
            {
                "WX-EXPR-012",
                "WX-EXPR-013",
                "WX-EXPR-017",
                "WX-EXPR-018",
                "WX-EXPR-019",
                "WX-EXPR-020",
            }
            <= flagged_ids
        )
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["entry_id"].startswith("WX-EXPR-"))
                self.assertTrue(case["basis"].strip())
                self.assertTrue(case["reason"].strip())
                if case["expected"] == "flag":
                    self.assertTrue(case["repair_target"].strip())
                else:
                    self.assertTrue(case["waiver_type"].strip())
        self.assertIn(
            "authorship_or_integrity_inference",
            self.regression["forbidden_implementation"],
        )

    def test_red_black_corpus_reuses_the_authoritative_black_adapter(self) -> None:
        black = self.red_black["black"]
        adapter = self.library["project_adapters"]["wechat_analytical"]
        self.assertEqual(
            self.red_black["corpus_id"],
            "WECHAT-RED-BLACK-CORPUS-001",
        )
        self.assertEqual(black["rule_id"], adapter["rule_id"])
        self.assertEqual(black["source"], "wechat-expression-library.yml")
        self.assertEqual(black["adapter"], "wechat_analytical")
        self.assertEqual(black["entry_ids"], adapter["ban_entry_ids"])
        self.assertEqual(len(black["entry_ids"]), 24)

    def test_red_entries_are_contextual_moves_not_a_phrase_quota(self) -> None:
        red = self.red_black["red"]
        entries = red["entries"]
        self.assertEqual(red["rule_id"], "PROJECT-WECHAT-RED-CORPUS-001")
        self.assertEqual(red["minimum_required_per_article"], 0)
        self.assertEqual(len(entries), 18)
        self.assertEqual(
            [entry["id"] for entry in entries],
            [f"WX-RED-{index:03d}" for index in range(1, 19)],
        )
        required = {
            "id",
            "label",
            "communication_job",
            "use_when",
            "derived_examples",
            "anti_stencil",
            "failure_signal",
            "source_ids",
        }
        banned_example_fragments = {
            "值得注意的是",
            "关键在于",
            "这意味着",
            "换句话说",
            "不是 A，而是 B",
            "底层逻辑",
            "流程闭环",
            "交卷",
            "账单",
        }
        for entry in entries:
            with self.subTest(entry=entry["id"]):
                self.assertEqual(set(entry), required)
                self.assertTrue(entry["communication_job"].strip())
                self.assertTrue(entry["use_when"].strip())
                self.assertGreaterEqual(len(entry["derived_examples"]), 2)
                self.assertTrue(entry["anti_stencil"].strip())
                self.assertTrue(entry["failure_signal"].strip())
                self.assertTrue(entry["source_ids"])
                for example in entry["derived_examples"]:
                    self.assertTrue(example.strip())
                    for fragment in banned_example_fragments:
                        self.assertNotIn(fragment, example)

        forbidden = self.red_black["policy"]["forbidden_implementation"]
        self.assertTrue(any("必用词" in item for item in forbidden))
        self.assertTrue(any("虚构第一人称" in item for item in forbidden))
        self.assertTrue(any("机械替换" in item for item in forbidden))

    def test_red_sources_are_traceable_without_storing_third_party_bodies(self) -> None:
        sources = self.red_black["source_catalog"]
        source_ids = {source["id"] for source in sources}
        self.assertEqual(len(sources), 16)
        self.assertEqual(len(source_ids), len(sources))
        forbidden_fields = {
            "body",
            "html",
            "excerpt",
            "quote",
            "comment_text",
            "article_body",
        }
        for source in sources:
            with self.subTest(source=source["id"]):
                self.assertTrue(
                    {"id", "kind", "observed_for", "rights_use"}
                    <= set(source)
                )
                self.assertEqual(sum(key in source for key in ("url", "ref")), 1)
                self.assertFalse(forbidden_fields & set(source))
                if source.get("url"):
                    self.assertTrue(source["url"].startswith("https://"))

        for entry in self.red_black["red"]["entries"]:
            self.assertTrue(set(entry["source_ids"]) <= source_ids)

    def test_red_regression_rewards_real_jobs_and_rejects_new_stencils(self) -> None:
        self.assertEqual(
            self.red_regression["rule_id"],
            "PROJECT-WECHAT-RED-CORPUS-001",
        )
        cases = self.red_regression["cases"]
        self.assertEqual(len(cases), 16)
        self.assertEqual(
            sum(case["expected"] == "encourage" for case in cases),
            10,
        )
        self.assertEqual(
            sum(case["expected"] == "reject_as_stencil" for case in cases),
            6,
        )
        red_ids = {entry["id"] for entry in self.red_black["red"]["entries"]}
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertIn(case["entry_id"], red_ids)
                self.assertTrue(case["text"].strip())
                self.assertTrue(case["context"].strip())
                self.assertTrue(case["basis"].strip())
                self.assertTrue(case["reason"].strip())
                if case["expected"] == "encourage":
                    self.assertTrue(case["communication_job"].strip())
                else:
                    self.assertTrue(case["repair_target"].strip())
        self.assertIn(
            "minimum_red_hit_count",
            self.red_regression["forbidden_implementation"],
        )


if __name__ == "__main__":
    unittest.main()
