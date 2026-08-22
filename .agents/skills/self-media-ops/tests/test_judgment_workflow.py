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
            "### 开场卡",
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
        self.assertIn("先独立冷读，再打开适用故事合同", review_template)
        self.assertIn("删具体、留抽象", review_template)

    def test_quicknews_prompt_contract_and_short_route(self):
        data = yaml.safe_load(
            (REFERENCE_DIR / "wechat-quicknews-prompt.yml").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(data["rule_id"], "PROJECT-WECHAT-QUICKNEWS-001")
        self.assertEqual(data["prompt_version"], "1.0")
        self.assertEqual(
            data["effectiveness_status"], "owner_binding_e0_unverified"
        )
        self.assertEqual(
            data["input_contract"]["defaults"]["target_length"],
            "shortest_complete",
        )
        self.assertEqual(
            set(data["input_contract"]["allowed_claim_types"]),
            {
                "verified_fact",
                "vendor_claim",
                "third_party_result",
                "author_judgment",
                "inference",
                "unknown",
            },
        )
        fact_packet_template = data["input_contract"]["fact_packet_template"]
        for required in ("source_id: S1", "claim_id: F1", "image_assets: []"):
            self.assertIn(required, fact_packet_template)

        prompt = data["writing_prompt"]["zh_v1_0"]
        for required in (
            "快讯事实包",
            "最短但完整",
            "内部事实回映",
            "STOP_RESEARCH",
            "不得凭空输出「图片」占位符",
            "不设置词库命中率",
        ):
            self.assertIn(required, prompt)
        for copied_stencil in (
            "量子位 | 公众号 QbitAI",
            "4 段话里有一个",
            "2000-2500",
        ):
            self.assertNotIn(copied_stencil, prompt)

        expected_routes = {
            case["expected"] for case in data["regression_cases"]
        }
        self.assertEqual(
            expected_routes,
            {
                "write_quicknews",
                "write_shortest_complete",
                "write_without_image_placeholder",
                "stop_research",
                "route_to_analytical_workflow",
            },
        )

        core = (ROOT / "共享/运营/SOP/内容工作流.md").read_text(
            encoding="utf-8"
        )
        skill = (ROOT / ".agents/skills/self-media-ops/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertEqual(
            core.count("### PROJECT-WECHAT-QUICKNEWS-001｜"), 1
        )
        self.assertIn("wechat-quicknews-prompt.yml", core)
        self.assertIn("wechat-quicknews-prompt.yml", skill)
        self.assertIn("| L1 factual |", skill)
        self.assertIn("Fact packet → one short draft → fact mapping", skill)
        self.assertIn("逐段事实回映", core)

    def test_four_lane_stage_routed_coauthor_contract(self):
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
        brief_template = (
            ROOT / "共享/模板/微信公众号内容包/brief.md"
        ).read_text(encoding="utf-8")
        review_template = (
            ROOT / "共享/模板/微信公众号内容包/review.md"
        ).read_text(encoding="utf-8")
        cowriting_template = (
            ROOT
            / "共享/模板/微信公众号内容包/research/co-writing-log.md"
        ).read_text(encoding="utf-8")
        draft_template = (
            ROOT / "共享/模板/微信公众号内容包/draft.md"
        ).read_text(encoding="utf-8")
        clumsy = yaml.safe_load(
            (REFERENCE_DIR / "wechat-clumsy-writing.yml").read_text(
                encoding="utf-8"
            )
        )

        for required in (
            "L0 局部任务",
            "L1 事实短稿",
            "L2 标准分析",
            "L3 多路线稿",
            "CORE-VALUE-001",
            "CORE-LANE-001",
            "CORE-STANDARD-001",
            "CORE-EVIDENCE-SEAM-001",
            "PROJECT-WECHAT-JUDGMENT-001",
            "PROJECT-WECHAT-PRAGMATIC-001",
            "PROJECT-WECHAT-AI-LEXICON-001",
            "CORE-ROUTE-001",
            "CORE-COAUTHOR-001",
            "CORE-TIME-001",
            "问题优先审稿",
            "确认锁定",
            "不值得写",
            "这是公众号分析稿默认档位",
        ):
            self.assertIn(required, core)
        self.assertIn("| L2 standard analysis |", skill)
        self.assertIn("staged co-writing log", skill)
        self.assertIn("| L3 multi-route |", skill)
        self.assertNotIn("Launch 3 isolated writing agents at the same time", skill)
        self.assertNotIn("minute 40", skill)
        self.assertNotIn("### 1. Free judgment layer", skill)
        self.assertLessEqual(len(skill.splitlines()), 80)
        self.assertIn("one human-directed canonical writer line", team)
        self.assertIn("the user selects", team)
        self.assertIn("issue-first cold reader", team)
        self.assertIn("never edit the canonical body concurrently", team)
        self.assertNotIn("3 isolated full-draft writers", team)
        self.assertNotIn("2 fresh selectors in parallel", team)
        self.assertIn("wall_clock_minutes", selection_template)
        self.assertIn("sla_status", selection_template)
        self.assertIn("story_contract_ref", frozen_template)
        self.assertIn("candidate_fact_boundary_check_required", frozen_template)
        self.assertIn("candidate_skeleton_difference_check_required", frozen_template)
        self.assertIn("chain_rule_id: CORE-CHAIN-001", frozen_template)
        self.assertIn("evidence_seam_rule_id: CORE-EVIDENCE-SEAM-001", frozen_template)
        self.assertIn("同名 `.audit.md` sidecar", frozen_template)
        self.assertNotIn("正文后用 HTML 注释", frozen_template)
        self.assertIn("narrative_engine:", frozen_template)
        self.assertIn("下一节为什么必须回答这个问题", frozen_template)
        self.assertIn("Pre-T0", frozen_template)
        self.assertIn("# 历史模板：L3 并行候选轮次", frozen_template)
        self.assertIn("CORE-COAUTHOR-001", frozen_template)
        self.assertIn("# 历史模板：L3 匿名候选评选", selection_template)
        self.assertIn("不让 AI 盲选完整终稿", selection_template)
        self.assertIn("跨题表演句", selection_template)
        self.assertIn("叙事链粗查", selection_template)
        self.assertIn("更像人", selection_template)
        self.assertNotIn("candidate_pragmatic_selfcheck_required", frozen_template)
        self.assertNotIn("candidate_lexicon_scan_required", frozen_template)
        self.assertIn("L3 多路线稿、中心结构性重写或用户明确共创", agents)
        self.assertNotIn("公众号分析长稿或结构重写", agents)
        for required in (
            "生产档位：L0 / L1 / L2 / L3",
            "`T_intake`",
            "`T_evidence_ready`",
            "L2 独立冷读",
            "L3 用户选定路线",
            "共写记录：`research/co-writing-log.md`",
        ):
            self.assertIn(required, brief_template)
        self.assertIn("故事合同来源", review_template)
        self.assertIn("声音锚点和锁定单元", review_template)
        self.assertIn("问题优先审稿与补丁决定", review_template)
        for required in (
            "workflow_rule: CORE-COAUTHOR-001",
            "human_first",
            "ai_candidate",
            "critique_only",
            "meaning_right_wording_wrong",
            "wrong_direction",
            "重开记录",
            "问题优先审稿与补丁",
        ):
            self.assertIn(required, cowriting_template)
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
        self.assertIn("### 具体性、声音锚点与锁定单元记录", review_template)

    def test_active_docs_use_core_rule_contracts_as_single_source(self):
        core = (ROOT / "共享/运营/SOP/内容工作流.md").read_text(
            encoding="utf-8"
        )
        active_files = [
            ROOT / ".agents/skills/self-media-ops/SKILL.md",
            REFERENCE_DIR / "content-package.md",
            REFERENCE_DIR / "wechat-quicknews-prompt.yml",
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
            ROOT
            / "共享/模板/微信公众号内容包/research/co-writing-log.md",
        ]
        rule_ids = (
            "CORE-CHAIN-001",
            "PROJECT-WECHAT-RHYTHM-001",
            "PROJECT-WECHAT-CONCRETE-001",
            "PROJECT-WECHAT-PRAGMATIC-001",
            "PROJECT-WECHAT-AI-LEXICON-001",
            "PROJECT-WECHAT-JUDGMENT-001",
            "PROJECT-WECHAT-QUICKNEWS-001",
            "CORE-ROUTE-001",
            "CORE-COAUTHOR-001",
            "CORE-LANE-001",
            "CORE-STANDARD-001",
            "CORE-EVIDENCE-SEAM-001",
        )
        for rule_id in rule_ids:
            self.assertEqual(core.count(f"### {rule_id}｜"), 1)
            for path in active_files:
                text = path.read_text(encoding="utf-8")
                self.assertNotIn(f"### {rule_id}｜", text, path.as_posix())

        trigger_sentence = "任何内容任务完成初步稿型识别后"
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
