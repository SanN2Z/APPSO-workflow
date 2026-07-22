from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "insight_loop.py"
MODULE_SPEC = importlib.util.spec_from_file_location("insight_loop_under_test", SCRIPT)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
INSIGHT_LOOP = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(INSIGHT_LOOP)


class InsightLoopCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="洞察 测试 "))
        self.root = self.temp_dir / "中文 工作区" / "洞察实验室"

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def run_cli(self, *arguments: str, expected: int | None = None) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPT), *arguments],
            cwd=self.temp_dir,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            check=False,
        )
        if expected is not None:
            self.assertEqual(
                result.returncode,
                expected,
                msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
            )
        return result

    def new_insight(
        self,
        *,
        insight_id: str = "INSIGHT-001",
        slug: str = "feedback-loop",
        title: str = "反馈闭环能否形成复利",
        next_review_on: str = "2026-07-29",
        expected: int = 0,
    ) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "new",
            "--root",
            str(self.root),
            "--id",
            insight_id,
            "--slug",
            slug,
            "--title",
            title,
            "--statement",
            "结构化反馈闭环可能降低同类问题的复发率",
            "--scope",
            "同一操作者、同类公众号解释稿和相同质量门",
            "--owner",
            "内容负责人",
            "--today",
            "2026-07-22",
            "--next-review-on",
            next_review_on,
            expected=expected,
        )

    def load_registry(self) -> dict:
        return yaml.safe_load((self.root / "洞察台账.yml").read_text(encoding="utf-8"))

    def record_path(self, index: int = 0) -> Path:
        registry = self.load_registry()
        return self.root / Path(*registry["insights"][index]["record"].split("/"))

    def load_record(self, index: int = 0) -> dict:
        return yaml.safe_load(self.record_path(index).read_text(encoding="utf-8"))

    def write_yaml(self, path: Path, value: object) -> None:
        path.write_text(
            yaml.safe_dump(value, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
            newline="\n",
        )

    def freeze_record(self, record: dict, *, status: str) -> dict:
        record["status"] = status
        record["claim"]["mechanism"] = "结构化反馈会在交付前触发同机制回归检查。"
        record["falsifiability"]["prediction"] = "下一轮目标缺陷率应低于冻结基线 50%。"
        record["falsifiability"]["failure_condition"] = "未下降 50% 或质量护栏恶化即失败。"
        record["falsifiability"]["alternative_explanations"] = ["任务难度可能不同。"]
        record["next_action"] = "按冻结合同执行并记录结果。"
        experiment = record["experiments"][0]
        experiment["baseline"]["frozen_ref"] = "baseline-v1.yml"
        experiment["intervention"]["artifact_ref"] = "workflow.md"
        experiment["intervention"]["version_ref"] = "sha256:abc123"
        experiment["metrics"]["primary"]["success_threshold"] = "相对下降至少 50%。"
        experiment["end_condition"] = "完成一组冻结输入的配对盲审后结束。"
        return record

    def module_new_args(self, root: Path):
        return INSIGHT_LOOP.build_parser().parse_args(
            [
                "new",
                "--root",
                str(root),
                "--id",
                "INSIGHT-001",
                "--slug",
                "fault-test",
                "--title",
                "故障注入",
                "--statement",
                "故障后不应留下半事务",
                "--scope",
                "本地临时工作区",
                "--owner",
                "tester",
                "--today",
                "2026-07-22",
            ]
        )

    def test_happy_path_creates_valid_workspace(self) -> None:
        created = self.new_insight()
        self.assertIn("已创建洞察 INSIGHT-001", created.stdout)
        registry = self.load_registry()
        self.assertEqual(registry["wip_limit"], 1)
        self.assertEqual(registry["insights"][0]["status"], "captured")

        record = self.load_record()
        self.assertEqual(record["title"], "反馈闭环能否形成复利")
        self.assertEqual(record["experiments"][0]["status"], "planned")
        self.assertIsInstance(record["experiments"][0]["baseline"], dict)
        self.assertEqual(
            set(record["experiments"][0]["metrics"]["primary"]),
            {"id", "definition", "direction", "success_threshold", "baseline", "result"},
        )
        self.assertEqual(record["assetization"]["status"], "none")
        self.assertEqual(
            set(record["assetization"]),
            {
                "status",
                "type",
                "target",
                "authoritative_refs",
                "regression_check",
                "transfer_test",
                "retirement_condition",
                "portable_core",
                "adapter_boundary",
            },
        )
        checked = self.run_cli("validate", "--root", str(self.root), expected=0)
        self.assertIn("校验通过：1 条洞察", checked.stdout)

    def test_dry_run_has_zero_writes(self) -> None:
        result = self.run_cli(
            "new",
            "--root",
            str(self.root),
            "--id",
            "INSIGHT-001",
            "--slug",
            "dry-run",
            "--title",
            "只预览",
            "--statement",
            "这是一条待验证判断",
            "--scope",
            "测试范围",
            "--today",
            "2026-07-22",
            "--dry-run",
            expected=0,
        )
        self.assertIn("DRY-RUN", result.stdout)
        self.assertFalse(self.root.exists())
        self.assertEqual(list(self.temp_dir.rglob("*.tmp")), [])

    def test_duplicate_id_does_not_overwrite_anything(self) -> None:
        self.new_insight()
        registry_path = self.root / "洞察台账.yml"
        record_path = self.record_path()
        registry_before = registry_path.read_bytes()
        record_before = record_path.read_bytes()

        result = self.new_insight(slug="different", title="另一个标题", expected=1)
        self.assertIn("禁止覆盖", result.stderr)
        self.assertEqual(registry_path.read_bytes(), registry_before)
        self.assertEqual(record_path.read_bytes(), record_before)

    def test_duplicate_yaml_key_is_rejected(self) -> None:
        self.new_insight()
        record_path = self.record_path()
        original = record_path.read_text(encoding="utf-8")
        record_path.write_text(
            original + "status: captured\n", encoding="utf-8", newline="\n"
        )
        result = self.run_cli("validate", "--root", str(self.root), expected=1)
        self.assertIn("重复 YAML 键", result.stderr)

    def test_out_of_bounds_registry_path_is_rejected(self) -> None:
        self.new_insight()
        registry = self.load_registry()
        registry["insights"][0]["record"] = "../外部.yml"
        self.write_yaml(self.root / "洞察台账.yml", registry)

        result = self.run_cli("validate", "--root", str(self.root), expected=1)
        self.assertIn("不安全路径", result.stderr)

    def test_registry_record_mismatch_is_rejected(self) -> None:
        self.new_insight()
        registry = self.load_registry()
        registry["insights"][0]["title"] = "台账漂移标题"
        self.write_yaml(self.root / "洞察台账.yml", registry)

        result = self.run_cli("validate", "--root", str(self.root), expected=1)
        self.assertIn("与记录不一致", result.stderr)
        self.assertIn("title", result.stderr)

    def test_non_falsifiable_failure_condition_is_rejected(self) -> None:
        self.new_insight()
        record = self.load_record()
        record["falsifiability"]["failure_condition"] = "没有什么结果会推翻它"
        self.write_yaml(self.record_path(), record)

        result = self.run_cli("validate", "--root", str(self.root), expected=1)
        self.assertIn("没有可检验内容", result.stderr)
        self.assertIn("failure_condition", result.stderr)

    def test_e1_requires_decisive_not_only_neutral_evidence(self) -> None:
        self.new_insight()
        registry = self.load_registry()
        record = self.load_record()
        registry["insights"][0]["evidence_level"] = "E1"
        record["evidence_level"] = "E1"
        record["evidence"]["neutral"] = [
            {
                "relation": "neutral",
                "ref": "case.md",
                "note": "这条材料只说明背景，不决定预测。",
            }
        ]
        self.write_yaml(self.record_path(), record)
        self.write_yaml(self.root / "洞察台账.yml", registry)

        result = self.run_cli("validate", "--root", str(self.root), expected=1)
        self.assertIn("supporting 或 contradicting evidence 不能为空", result.stderr)

    def test_assetized_state_requires_complete_asset_contract(self) -> None:
        self.new_insight()
        registry = self.load_registry()
        record = self.load_record()
        registry["insights"][0]["status"] = "assetized"
        record["status"] = "assetized"
        self.write_yaml(self.record_path(), record)
        self.write_yaml(self.root / "洞察台账.yml", registry)

        result = self.run_cli("validate", "--root", str(self.root), expected=1)
        self.assertIn("assetization.type 在 assetized 状态下必须是非空字符串", result.stderr)
        self.assertIn("assetization.authoritative_refs", result.stderr)

    def test_default_scaffold_cannot_be_promoted_to_test_ready(self) -> None:
        self.new_insight()
        registry = self.load_registry()
        record = self.load_record()
        registry["insights"][0]["status"] = "test_ready"
        record["status"] = "test_ready"
        self.write_yaml(self.record_path(), record)
        self.write_yaml(self.root / "洞察台账.yml", registry)

        result = self.run_cli("validate", "--root", str(self.root), expected=1)
        self.assertIn("不能保留 new 默认模板", result.stderr)
        self.assertIn("至少需要一个已冻结实验", result.stderr)

    def test_e2_requires_two_independent_cases(self) -> None:
        self.new_insight()
        registry = self.load_registry()
        record = self.load_record()
        registry["insights"][0]["evidence_level"] = "E2"
        record["evidence_level"] = "E2"
        record["evidence"]["supporting"] = [
            {
                "relation": "supports",
                "ref": "case-1/result.yml",
                "note": "首个案例达到冻结阈值。",
                "case_id": "CASE-001",
            }
        ]
        self.write_yaml(self.record_path(), record)
        self.write_yaml(self.root / "洞察台账.yml", registry)

        result = self.run_cli("validate", "--root", str(self.root), expected=1)
        self.assertIn("至少需要 2 个不同 case_id", result.stderr)

    def test_e3_requires_prospective_and_counterexample_or_transfer(self) -> None:
        self.new_insight()
        registry = self.load_registry()
        record = self.load_record()
        registry["insights"][0]["evidence_level"] = "E3"
        record["evidence_level"] = "E3"
        record["evidence"]["supporting"] = [
            {
                "relation": "supports",
                "ref": f"case-{index}/result.yml",
                "note": "独立案例达到阈值。",
                "case_id": f"CASE-{index:03d}",
            }
            for index in (1, 2)
        ]
        self.write_yaml(self.record_path(), record)
        self.write_yaml(self.root / "洞察台账.yml", registry)

        result = self.run_cli("validate", "--root", str(self.root), expected=1)
        self.assertIn("prospective", result.stderr)
        self.assertIn("counterexample 或 transfer_test", result.stderr)

    def test_supported_scoped_requires_supporting_evidence(self) -> None:
        self.new_insight()
        registry = self.load_registry()
        record = self.freeze_record(self.load_record(), status="supported_scoped")
        registry["insights"][0]["status"] = "supported_scoped"
        registry["insights"][0]["evidence_level"] = "E1"
        record["evidence_level"] = "E1"
        record["evidence"]["contradicting"] = [
            {
                "relation": "contradicts",
                "ref": "case-1/result.yml",
                "note": "结果未达到阈值。",
            }
        ]
        self.write_yaml(self.record_path(), record)
        self.write_yaml(self.root / "洞察台账.yml", registry)
        result = self.run_cli("validate", "--root", str(self.root), expected=1)
        self.assertIn("supported_scoped 状态至少需要一条 supports 证据", result.stderr)

    def test_rejected_requires_contradicting_evidence(self) -> None:
        self.new_insight()
        registry = self.load_registry()
        record = self.freeze_record(self.load_record(), status="rejected")
        registry["insights"][0]["status"] = "rejected"
        registry["insights"][0]["evidence_level"] = "E1"
        record["evidence_level"] = "E1"
        record["evidence"]["supporting"] = [
            {
                "relation": "supports",
                "ref": "case-1/result.yml",
                "note": "结果达到阈值。",
            }
        ]
        self.write_yaml(self.record_path(), record)
        self.write_yaml(self.root / "洞察台账.yml", registry)
        result = self.run_cli("validate", "--root", str(self.root), expected=1)
        self.assertIn("rejected 状态至少需要一条 contradicts 证据", result.stderr)

    def test_global_running_experiment_wip_limit_is_enforced(self) -> None:
        self.new_insight()
        self.new_insight(
            insight_id="INSIGHT-002",
            slug="second-loop",
            title="第二条反馈闭环",
        )
        registry = self.load_registry()
        for index, entry in enumerate(registry["insights"]):
            record = self.freeze_record(self.load_record(index), status="running")
            record["experiments"][0]["status"] = "running"
            self.write_yaml(self.record_path(index), record)
            entry["status"] = "running"
        self.write_yaml(self.root / "洞察台账.yml", registry)

        result = self.run_cli("validate", "--root", str(self.root), expected=1)
        self.assertIn("超过 wip_limit 1", result.stderr)

    def test_status_lists_due_items_and_default_exit_is_zero(self) -> None:
        self.new_insight(next_review_on="2026-07-22")
        result = self.run_cli(
            "status",
            "--root",
            str(self.root),
            "--as-of",
            "2026-07-22",
            expected=0,
        )
        self.assertIn("captured: 1", result.stdout)
        self.assertIn("INSIGHT-001 | captured | 2026-07-22", result.stdout)
        self.assertIn("反馈闭环能否形成复利", result.stdout)

    def test_status_lists_future_active_insight_and_next_action(self) -> None:
        self.new_insight(next_review_on="2026-08-01")
        registry = self.load_registry()
        record = self.freeze_record(self.load_record(), status="running")
        record["experiments"][0]["status"] = "running"
        registry["insights"][0]["status"] = "running"
        self.write_yaml(self.record_path(), record)
        self.write_yaml(self.root / "洞察台账.yml", registry)

        result = self.run_cli(
            "status",
            "--root",
            str(self.root),
            "--as-of",
            "2026-07-22",
            expected=0,
        )
        self.assertIn("当前项：", result.stdout)
        self.assertIn("INSIGHT-001 | running", result.stdout)
        self.assertIn("实验：EXP-001", result.stdout)
        self.assertIn("下一步：按冻结合同执行并记录结果。", result.stdout)
        self.assertIn("到期项：\n- 无", result.stdout)

    def test_status_fail_on_due_returns_two_for_actionable_due(self) -> None:
        self.new_insight(next_review_on="2026-07-22")
        result = self.run_cli(
            "status",
            "--root",
            str(self.root),
            "--as-of",
            "2026-07-22",
            "--fail-on-due",
            expected=2,
        )
        self.assertIn("到期门禁失败", result.stderr)

    def test_status_fail_on_due_ignores_archived(self) -> None:
        self.new_insight(next_review_on="2026-07-22")
        registry = self.load_registry()
        record = self.load_record()
        registry["insights"][0]["status"] = "archived"
        record["status"] = "archived"
        self.write_yaml(self.record_path(), record)
        self.write_yaml(self.root / "洞察台账.yml", registry)

        self.run_cli(
            "status",
            "--root",
            str(self.root),
            "--as-of",
            "2026-07-22",
            "--fail-on-due",
            expected=0,
        )

    def test_chinese_and_space_path_round_trips_exactly(self) -> None:
        self.new_insight(title="中文 标题与路径")
        record = self.load_record()
        self.assertEqual(record["title"], "中文 标题与路径")
        result = self.run_cli("validate", "--root", str(self.root), expected=0)
        self.assertNotIn("�", result.stdout + result.stderr)

    def test_schema_version_must_be_an_integer(self) -> None:
        self.new_insight()
        record = self.load_record()
        record["schema_version"] = 1.0
        self.write_yaml(self.record_path(), record)
        result = self.run_cli("validate", "--root", str(self.root), expected=1)
        self.assertIn("schema_version 必须是整数 1", result.stderr)

    def test_unknown_critical_field_is_rejected(self) -> None:
        self.new_insight()
        record = self.load_record()
        record["unreviewed_extension"] = True
        self.write_yaml(self.record_path(), record)
        result = self.run_cli("validate", "--root", str(self.root), expected=1)
        self.assertIn("包含未知字段 unreviewed_extension", result.stderr)

    def test_recursive_yaml_alias_is_rejected_without_traceback(self) -> None:
        self.new_insight()
        record = self.load_record()
        recursive: list = []
        recursive.append(recursive)
        record["experiments"][0]["metrics"]["primary"]["baseline"] = recursive
        self.write_yaml(self.record_path(), record)
        result = self.run_cli("validate", "--root", str(self.root), expected=1)
        self.assertIn("不允许 YAML alias", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_orphan_record_is_rejected(self) -> None:
        self.new_insight()
        orphan_dir = self.root / "insights" / "INSIGHT-099-orphan"
        orphan_dir.mkdir()
        shutil.copyfile(self.record_path(), orphan_dir / "insight.yml")
        result = self.run_cli("validate", "--root", str(self.root), expected=1)
        self.assertIn("未登记的孤立洞察记录", result.stderr)

    def test_concurrent_new_commands_preserve_both_registry_entries(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONIOENCODING"] = "utf-8"

        def command(insight_id: str, slug: str, title: str) -> list[str]:
            return [
                sys.executable,
                "-X",
                "utf8",
                str(SCRIPT),
                "new",
                "--root",
                str(self.root),
                "--id",
                insight_id,
                "--slug",
                slug,
                "--title",
                title,
                "--statement",
                "并发写入不得丢失台账条目",
                "--scope",
                "临时并发测试",
                "--owner",
                "tester",
                "--today",
                "2026-07-22",
            ]

        processes = [
            subprocess.Popen(
                command("INSIGHT-001", "first", "第一条"),
                cwd=self.temp_dir,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
            ),
            subprocess.Popen(
                command("INSIGHT-002", "second", "第二条"),
                cwd=self.temp_dir,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
            ),
        ]
        results = [process.communicate(timeout=20) for process in processes]
        for process, (stdout, stderr) in zip(processes, results):
            self.assertEqual(process.returncode, 0, msg=f"stdout:\n{stdout}\nstderr:\n{stderr}")
        registry = self.load_registry()
        self.assertEqual(
            [entry["id"] for entry in registry["insights"]],
            ["INSIGHT-001", "INSIGHT-002"],
        )
        self.run_cli("validate", "--root", str(self.root), expected=0)

    def test_keyboard_interrupt_after_each_write_rolls_back(self) -> None:
        for interrupted_name in ("insight.yml", "洞察台账.yml"):
            with self.subTest(interrupted_name=interrupted_name):
                root = self.temp_dir / f"interrupt-{interrupted_name}"
                args = self.module_new_args(root)
                original_write = INSIGHT_LOOP.atomic_write_text

                def interrupting_write(path: Path, text: str) -> None:
                    original_write(path, text)
                    if path.name == interrupted_name:
                        raise KeyboardInterrupt

                with mock.patch.object(
                    INSIGHT_LOOP, "atomic_write_text", side_effect=interrupting_write
                ):
                    with contextlib.redirect_stdout(io.StringIO()):
                        with self.assertRaises(KeyboardInterrupt):
                            INSIGHT_LOOP.command_new(args)
                self.assertFalse(root.exists())

    def test_readback_failure_rolls_back_both_files(self) -> None:
        root = self.temp_dir / "readback-failure"
        args = self.module_new_args(root)
        with mock.patch.object(
            INSIGHT_LOOP,
            "validate_workspace",
            side_effect=INSIGHT_LOOP.WorkspaceError("injected readback failure"),
        ):
            with self.assertRaises(INSIGHT_LOOP.WorkspaceError):
                INSIGHT_LOOP.command_new(args)
        self.assertFalse(root.exists())

    def test_symbolic_link_record_is_rejected_when_supported(self) -> None:
        self.new_insight()
        real_record = self.record_path()
        external = self.temp_dir / "external.yml"
        shutil.copyfile(real_record, external)
        real_record.unlink()
        try:
            real_record.symlink_to(external)
        except (OSError, NotImplementedError):
            self.skipTest("当前环境不允许创建符号链接")
        result = self.run_cli("validate", "--root", str(self.root), expected=1)
        self.assertIn("符号链接", result.stderr)


if __name__ == "__main__":
    unittest.main()
