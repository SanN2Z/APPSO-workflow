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
        package_spec = (REFERENCE_DIR / "content-package.md").read_text(
            encoding="utf-8"
        )
        template = (
            ROOT
            / "共享/模板/微信公众号内容包/research/judgment-workshop.md"
        ).read_text(encoding="utf-8")
        for required in (
            "PROJECT-WECHAT-JUDGMENT-001",
            "主动提交写前共创包",
            "一句话故事主线",
            "四格叙事链表",
            "最强的反例或对手",
            "下一节为什么必须回答这个问题",
            "2—3 个标题",
            "拟定小标题",
            "小标题在节拍成立后再写",
            "一个普通读者可以复述的主判断",
            "2–4 个支撑判断",
            "2–3 张开场卡",
            "一个主要叙事发动机",
            "`personal`",
            "`company`",
        ):
            self.assertIn(required, contract)
        for required in (
            "status: discussing",
            'voice_mode: ""',
            "decision_points_completed: 0",
            "user_confirmed: false",
            "story_contract_version: 1",
            "pragmatic_rule_id: PROJECT-WECHAT-PRAGMATIC-001",
            "expression_calibrated: false",
            "## 共同处境",
            "## Codex 主动提交的写前共创包",
            "## 主判断",
            "## 小标题与逻辑框架",
            "## 支撑判断",
            "### 开场候选卡",
            "尚未解决的压力",
            "叙事发动机",
            "## 最强对手",
            "下一节为什么必须回答这个问题",
            "## 表达定调",
            "具体表达任务",
            "## 放弃的方向",
            "## 读者带走什么",
        ):
            self.assertIn(required, template)
        frontmatter_fields = {
            "status",
            "voice_mode",
            "decision_points_completed",
            "user_confirmed",
            "confirmed_on",
            "story_contract_version",
            "pragmatic_rule_id",
            "expression_calibrated",
            "reason",
        }
        for field in frontmatter_fields:
            self.assertIn(f"{field}:", template)
            self.assertIn(f"{field}:", package_spec)

    def test_hook_and_narrative_rules_reach_execution_gates(self):
        core = (ROOT / "共享/运营/SOP/内容工作流.md").read_text(
            encoding="utf-8"
        )
        human_voice = (REFERENCE_DIR / "wechat-human-voice-pass.md").read_text(
            encoding="utf-8"
        )
        ai_pattern = (REFERENCE_DIR / "wechat-ai-pattern-pass.md").read_text(
            encoding="utf-8"
        )
        editorial = (REFERENCE_DIR / "wechat-editorial-gates.md").read_text(
            encoding="utf-8"
        )
        copy_editor = (REFERENCE_DIR / "wechat-role-copy-editor.md").read_text(
            encoding="utf-8"
        )
        review_template = (
            ROOT / "共享/模板/微信公众号内容包/review.md"
        ).read_text(encoding="utf-8")

        for required in (
            "CORE-HOOK-001",
            "CORE-CHAIN-001",
            "PROJECT-WECHAT-RHYTHM-001",
            "PROJECT-WECHAT-CONCRETE-001",
            "纯事实快讯",
            "平行比较",
        ):
            self.assertIn(required, core)
        self.assertIn("Remove the visible scaffold first", human_voice)
        self.assertIn("news brief followed by an explainer and a slogan", human_voice)
        self.assertIn("RHY-TRIAD", ai_pattern)
        self.assertIn("RHY-DISCLAIMER", ai_pattern)
        self.assertIn("CORE-CHAIN-001", editorial)
        self.assertIn("PROJECT-WECHAT-PRAGMATIC-001", editorial)
        self.assertIn("PROJECT-WECHAT-AI-LEXICON-001", editorial)
        self.assertIn("HUMAN-RHY-*", copy_editor)
        self.assertIn("先独立冷读，再打开故事合同", review_template)
        self.assertIn("删具体、留抽象", review_template)

    def test_five_layer_parallel_selection_and_time_contract_is_default(self):
        core = (ROOT / "共享/运营/SOP/内容工作流.md").read_text(
            encoding="utf-8"
        )
        skill = (ROOT / ".agents/skills/self-media-ops/SKILL.md").read_text(
            encoding="utf-8"
        )
        team = (REFERENCE_DIR / "wechat-team.md").read_text(encoding="utf-8")
        selection_template = (
            ROOT
            / "共享/模板/微信公众号内容包/research/candidate-selection.md"
        ).read_text(encoding="utf-8")
        frozen_template = (
            ROOT
            / "共享/模板/微信公众号内容包/research/candidate-round-frozen-input.md"
        ).read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        draft_template = (
            ROOT / "共享/模板/微信公众号内容包/draft.md"
        ).read_text(encoding="utf-8")
        clumsy = yaml.safe_load(
            (REFERENCE_DIR / "wechat-clumsy-writing.yml").read_text(
                encoding="utf-8"
            )
        )

        for required in (
            "自由判断层",
            "写前定调层",
            "并行候选层",
            "匿名评选层",
            "硬门检查层",
            "CORE-VALUE-001",
            "PROJECT-WECHAT-JUDGMENT-001",
            "PROJECT-WECHAT-PRAGMATIC-001",
            "PROJECT-WECHAT-AI-LEXICON-001",
            "CORE-SELECTION-001",
            "CORE-TIME-001",
            "一篇都不要",
            "40 分钟文本出稿",
            "不值得写",
        ):
            self.assertIn(required, core)
        self.assertIn("Launch 3 isolated writing agents at the same time", skill)
        self.assertIn("launch 2 fresh reviewer agents in parallel", skill)
        self.assertIn("minute 40", skill)
        self.assertIn("3 isolated full-draft writers", team)
        self.assertIn("2 fresh selectors in parallel", team)
        self.assertIn("fact boundary", team)
        self.assertIn("ready-made skeleton", team)
        self.assertIn("wall_clock_minutes", selection_template)
        self.assertIn("sla_status", selection_template)
        self.assertIn("story_contract_ref", frozen_template)
        self.assertIn("candidate_fact_boundary_check_required", frozen_template)
        self.assertIn("candidate_skeleton_difference_check_required", frozen_template)
        self.assertIn("chain_rule_id: CORE-CHAIN-001", frozen_template)
        self.assertIn("narrative_engine:", frozen_template)
        self.assertIn("下一节为什么必须回答这个问题", frozen_template)
        self.assertIn("Pre-T0", frozen_template)
        self.assertIn("### 2. Prewriting calibration layer", skill)
        self.assertIn("checks only two things", skill)
        self.assertIn("跨题表演句", selection_template)
        self.assertIn("叙事链粗查", selection_template)
        self.assertIn("更像人", selection_template)
        self.assertNotIn("candidate_pragmatic_selfcheck_required", frozen_template)
        self.assertNotIn("candidate_lexicon_scan_required", frozen_template)
        self.assertIn("公众号分析长稿或结构重写", agents)
        self.assertNotIn("judgment_workshop:", draft_template)
        self.assertFalse(clumsy["default_invocation"])

    def test_pragmatic_naturalness_contract_and_regression(self):
        data = yaml.safe_load(
            (REFERENCE_DIR / "wechat-pragmatic-regression.yml").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(data["rule_id"], "PROJECT-WECHAT-PRAGMATIC-001")
        self.assertEqual(data["mode"], "manual_semantic_regression")
        self.assertEqual(
            set(data["forbidden_implementation"]),
            {
                "keyword_blacklist",
                "ai_detector_score",
                "generic_more_human_verdict",
                "forced_slang_typos_or_fragments",
            },
        )

        cases = data["cases"]
        self.assertEqual({case["expected"] for case in cases}, {"flag", "allow"})
        by_text = {case["text"]: case for case in cases}
        for text in (
            "能力的差距要如实写。",
            "张力恰恰在这里。",
            "企业的账算得很快。",
        ):
            self.assertEqual(by_text[text]["expected"], "flag")
        self.assertEqual(
            by_text["为山九仞，功亏一篑。"]["expected"],
            "allow",
        )
        required_fields = {
            "communication_job",
            "specific_referent",
            "transfer_test",
            "rhetoric_self_label",
            "deletion_test",
            "read_aloud_test",
            "repair_target",
        }
        for case in cases:
            self.assertTrue(required_fields.issubset(case))

        core = (ROOT / "共享/运营/SOP/内容工作流.md").read_text(
            encoding="utf-8"
        )
        ai_pattern = (REFERENCE_DIR / "wechat-ai-pattern-pass.md").read_text(
            encoding="utf-8"
        )
        human_voice = (REFERENCE_DIR / "wechat-human-voice-pass.md").read_text(
            encoding="utf-8"
        )
        review_template = (
            ROOT / "共享/模板/微信公众号内容包/review.md"
        ).read_text(encoding="utf-8")
        for text in (core, ai_pattern, human_voice, review_template):
            self.assertIn("PROJECT-WECHAT-PRAGMATIC-001", text)
        self.assertIn("跨题迁移", ai_pattern)
        self.assertIn("Pragmatic necessity", human_voice)
        self.assertIn("AI-pattern diagnostic", review_template)

    def test_rhythm_contract_regression_and_review_shape(self):
        data = yaml.safe_load(
            (REFERENCE_DIR / "wechat-rhythm-regression.yml").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(data["rule_id"], "PROJECT-WECHAT-RHYTHM-001")
        self.assertEqual(data["mode"], "manual_semantic_regression")
        self.assertEqual(
            set(data["categories"]),
            {
                "RHY-TRIAD",
                "RHY-SEMICOLON",
                "RHY-UPLIFT",
                "RHY-FLIP",
                "RHY-DISCLAIMER",
                "RHY-IMPORTANCE",
            },
        )
        cases = data["cases"]
        self.assertEqual({case["expected"] for case in cases}, {"flag", "allow"})
        self.assertGreaterEqual(
            len([case for case in cases if case["expected"] == "allow"]),
            3,
        )
        for case in cases:
            self.assertIn("deletion_test", case)
            self.assertIn("source", case)

        review_template = (
            ROOT / "共享/模板/微信公众号内容包/review.md"
        ).read_text(encoding="utf-8")
        editorial = (REFERENCE_DIR / "wechat-editorial-gates.md").read_text(
            encoding="utf-8"
        )
        for section in range(1, 7):
            self.assertIn(f"## {section}.", review_template)
            self.assertIn(f"## {section}.", editorial)
        self.assertLessEqual(review_template.count("- [ ]"), 15)
        self.assertNotIn("3–8", review_template)
        self.assertNotIn("### 表达候选库", review_template)
        self.assertIn("### 具体性守恒 diff", review_template)

    def test_active_docs_use_core_rule_contracts_as_single_source(self):
        core = (ROOT / "共享/运营/SOP/内容工作流.md").read_text(
            encoding="utf-8"
        )
        active_files = [
            ROOT / ".agents/skills/self-media-ops/SKILL.md",
            REFERENCE_DIR / "content-package.md",
            REFERENCE_DIR / "wechat-judgment-workshop.md",
            REFERENCE_DIR / "wechat-ai-pattern-pass.md",
            REFERENCE_DIR / "wechat-human-voice-pass.md",
            REFERENCE_DIR / "wechat-editorial-gates.md",
            REFERENCE_DIR / "wechat-team.md",
            REFERENCE_DIR / "wechat-role-feature-writer.md",
            REFERENCE_DIR / "wechat-role-managing-editor.md",
            REFERENCE_DIR / "wechat-role-release-auditor.md",
            REFERENCE_DIR / "wechat-role-copy-editor.md",
            ROOT / "共享/模板/微信公众号内容包/brief.md",
            ROOT / "共享/模板/微信公众号内容包/review.md",
            ROOT
            / "共享/模板/微信公众号内容包/research/judgment-workshop.md",
            ROOT
            / "共享/模板/微信公众号内容包/research/candidate-round-frozen-input.md",
            ROOT
            / "共享/模板/微信公众号内容包/research/candidate-selection.md",
        ]
        rule_ids = (
            "CORE-CHAIN-001",
            "PROJECT-WECHAT-RHYTHM-001",
            "PROJECT-WECHAT-CONCRETE-001",
            "PROJECT-WECHAT-PRAGMATIC-001",
            "PROJECT-WECHAT-AI-LEXICON-001",
            "PROJECT-WECHAT-JUDGMENT-001",
            "CORE-SELECTION-001",
        )
        for rule_id in rule_ids:
            self.assertEqual(core.count(f"### {rule_id}｜"), 1)
            for path in active_files:
                text = path.read_text(encoding="utf-8")
                self.assertNotIn(f"### {rule_id}｜", text, path.as_posix())

        trigger_sentence = (
            "公众号新分析稿与结构性重写，通过价值门后默认触发写前共创门。"
        )
        self.assertEqual(core.count(trigger_sentence), 1)
        for path in active_files:
            self.assertNotIn(
                trigger_sentence,
                path.read_text(encoding="utf-8"),
                path.as_posix(),
            )
        self.assertNotIn("CORE-NARRATIVE-001", core)


if __name__ == "__main__":
    unittest.main()
