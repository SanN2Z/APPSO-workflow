from __future__ import annotations

import hashlib
import importlib.util
import tempfile
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "verify_clone_ready.py"
SPEC = importlib.util.spec_from_file_location("verify_clone_ready", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_requirements_include_graph_and_duplicate_equal_pins() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        (root / "component.txt").write_text(
            "PyYAML==6.0.2\nmarkdown-it-py==4.0.0\n", encoding="utf-8"
        )
        (root / "requirements.txt").write_text(
            "-r component.txt\nPyYAML==6.0.2\npytest==9.0.3\n", encoding="utf-8"
        )
        packages, visited = MODULE.parse_requirements(root / "requirements.txt")

        assert {name: item[0] for name, item in packages.items()} == {
            "markdown-it-py": "4.0.0",
            "pytest": "9.0.3",
            "pyyaml": "6.0.2",
        }
        assert visited == {
            (root / "requirements.txt").resolve(),
            (root / "component.txt").resolve(),
        }


def test_requirements_reject_conflicting_or_unpinned_entries() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        conflict = root / "conflict.txt"
        conflict.write_text("PyYAML==6.0.1\nPyYAML==6.0.2\n", encoding="utf-8")
        try:
            MODULE.parse_requirements(conflict)
        except ValueError as exc:
            assert "conflicting pins" in str(exc)
        else:
            raise AssertionError("a conflicting pin must fail")

        unpinned = root / "unpinned.txt"
        unpinned.write_text("PyYAML>=6\n", encoding="utf-8")
        try:
            MODULE.parse_requirements(unpinned)
        except ValueError as exc:
            assert "unpinned or unsupported" in str(exc)
        else:
            raise AssertionError("an unpinned requirement must fail")


def test_absolute_path_scan_flags_machine_paths_only() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        good = root / "good.md"
        bad = root / "bad.md"
        good.write_text(
            "Use tools/workflow.ps1 or https://example.com/path.\n", encoding="utf-8"
        )
        bad.write_text(
            "Do not pin C:\\Users\\USER\\repo or /home/name/repo.\n", encoding="utf-8"
        )

        assert MODULE.absolute_path_findings(root, ["good.md"]) == []
        findings = MODULE.absolute_path_findings(root, ["bad.md"])
        assert len(findings) == 1
        assert findings[0].startswith("bad.md:1:")


def test_git_nul_paths_preserve_unicode_without_quote_parsing() -> None:
    output = "微信公众号/tools/wechat_publish.py\0共享/运营/SOP/内容工作流.md\0"
    assert MODULE.parse_git_nul_paths(output) == {
        "微信公众号/tools/wechat_publish.py",
        "共享/运营/SOP/内容工作流.md",
    }


def test_git_attribute_nul_parser_groups_triplets() -> None:
    output = "path/file.js\0text\0set\0path/file.js\0eol\0lf\0"
    assert MODULE.parse_git_attr_nul(output) == {
        "path/file.js": {"text": "set", "eol": "lf"}
    }


def test_tree_fingerprint_uses_posix_paths_uppercase_hashes_and_lf() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        (root / "nested").mkdir()
        (root / "b.txt").write_bytes(b"b")
        (root / "nested" / "a.txt").write_bytes(b"a")

        files, total_bytes, actual = MODULE.tree_fingerprint(root)
        lines = "".join(
            f"{path.relative_to(root).as_posix()}\t"
            f"{hashlib.sha256(path.read_bytes()).hexdigest().upper()}\n"
            for path in files
        ).encode("utf-8")

        assert total_bytes == 2
        assert actual == hashlib.sha256(lines).hexdigest().upper()


def test_repository_source_contract_passes() -> None:
    manifest = MODULE.read_json(MODULE.MANIFEST_PATH)
    report = MODULE.build_report(manifest, source_only=True)
    failures = [item for item in report["checks"] if not item["ok"]]
    assert failures == []
