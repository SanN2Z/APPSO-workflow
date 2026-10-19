import importlib.util
import argparse
import json
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location("gemini_writer", Path(__file__).parents[1] / "gemini_writer.py")
WRITER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WRITER)


def stream(model="gemini-test", status="SUCCESS", response="原文", tool=None):
    events = [{"event": "init", "init": {"model": model}},
              {"event": "result", "result": {"status": status, "response": response}}]
    if tool:
        events.insert(1, {"event": "step_update", "step_update": {"step_type": "tool", "tool_name": tool}})
    return "\n".join(json.dumps(e) for e in events)


def test_different_or_missing_model_cannot_be_reported_as_gemini():
    for model in ("other", None):
        with pytest.raises(WRITER.WriterError, match="模型"):
            WRITER.inspect_stream(stream(model=model), "gemini-test")


def test_empty_or_non_success_output_is_not_a_completed_draft():
    for data in (stream(response=""), stream(status="WAITING"), "non-json"):
        with pytest.raises(WRITER.WriterError):
            WRITER.inspect_stream(data, "gemini-test")


def test_success_response_is_unchanged_and_tools_remain_visible():
    parsed, tools = WRITER.inspect_stream(stream(response="原文\n", tool="write_to_file"), "gemini-test")
    assert parsed["result"]["response"] == "原文\n"
    assert tools == ["write_to_file"]


def test_explicit_external_scope_required(tmp_path):
    handoff = tmp_path / "handoff.json"
    handoff.write_text(json.dumps({"prompt": "稿件"}), encoding="utf-8")
    with pytest.raises(WRITER.WriterError, match="外部"):
        WRITER.load_handoff(handoff)
    handoff.write_text(json.dumps({"prompt": "稿件", "external_shareable": True}), encoding="utf-8")
    assert WRITER.load_handoff(handoff)["prompt"] == "稿件"


def test_no_cli_substitution_or_permission_bypass(tmp_path):
    fake = tmp_path / "gemini.exe"
    fake.touch()
    with pytest.raises(WRITER.WriterError, match="原生 agy"):
        WRITER.resolve_agy(str(fake))
    args = WRITER.native_args("agy", "gemini-test", "high", tmp_path / "native.log", 60)
    assert "--dangerously-skip-permissions" not in args
    assert "--sandbox" in args
    assert args[args.index("--mode") + 1] == "plan"
    with pytest.raises(WRITER.WriterError, match="Gemini 模型"):
        WRITER.native_args("agy", "claude-test", "high", tmp_path / "native.log", 60)


def test_repair_uses_original_offsets_even_when_replacement_contains_other_old_text():
    allowed = [{"id": "1", "old": "甲段"}, {"id": "2", "old": "乙段"}]
    patches = [{"id": "2", "old": "乙段", "new": "改乙"},
               {"id": "1", "old": "甲段", "new": "乙段加说明"}]
    assert WRITER.assemble_patches("甲段\n乙段\n结尾", allowed, patches, ["结尾"]) == "乙段加说明\n改乙\n结尾"


def test_windows_newlines_preserve_locked_paragraphs_without_rewriting_other_bytes():
    result = WRITER.assemble_patches("旧正文\r\n结尾一\r\n\r\n结尾二",
        [{"id": "1", "old": "旧正文"}], [{"id": "1", "old": "旧正文", "new": "新正文"}],
        ["结尾一\n\n结尾二"])
    assert result == "新正文\r\n结尾一\r\n\r\n结尾二"


@pytest.mark.parametrize("source,allowed,patches", [
    ("甲段", [{"id": "1", "old": "旧甲"}], [{"id": "1", "old": "甲段", "new": "新甲"}]),
    ("甲段甲段", [{"id": "1", "old": "甲段"}], [{"id": "1", "old": "甲段", "new": "新甲"}]),
    ("甲段", [{"id": "1", "old": "甲段"}], [{"id": "2", "old": "甲段", "new": "新甲"}]),
    ("甲段", [{"id": "1", "old": "甲段"}], [{"id": "1", "old": "甲段", "new": "新甲"}] * 2),
    ("甲乙丙", [{"id": "1", "old": "甲乙"}, {"id": "2", "old": "乙丙"}],
     [{"id": "1", "old": "甲乙", "new": "甲"}, {"id": "2", "old": "乙丙", "new": "丙"}]),
])
def test_out_of_scope_duplicate_or_overlapping_repair_is_rejected(source, allowed, patches):
    with pytest.raises(WRITER.WriterError):
        WRITER.assemble_patches(source, allowed, patches, [])


@pytest.mark.parametrize("source,new,locked", [
    ("![演示](first.gif)\n正文", "![演示](other.gif)\n正文", []),
    ("正文\n锁定结尾", "正文\n换个结尾", ["锁定结尾"]),
    ("---\nstatus: ready\n---\n正文", "正文", []),
])
def test_repair_cannot_change_media_locked_text_or_carry_publication_frontmatter(source, new, locked):
    with pytest.raises(WRITER.WriterError):
        WRITER.assemble_patches(source, [{"id": "1", "old": source}],
                                [{"id": "1", "old": source, "new": new}], locked)


def test_file_assembly_requires_frozen_source_and_new_output(tmp_path):
    source, output = tmp_path / "first.md", tmp_path / "repaired.md"
    source.write_text("正文\n结尾", encoding="utf-8")
    allowed, patches = tmp_path / "allowed.json", tmp_path / "patches.json"
    allowed.write_text(json.dumps([{"id": "1", "old": "正文"}]), encoding="utf-8")
    patches.write_text(json.dumps({"patches": [{"id": "1", "old": "正文", "new": "修后正文"}]}), encoding="utf-8")
    args = argparse.Namespace(source=source, output=output, source_sha256="stale",
                              allowed_spans=allowed, patches=patches, locked_handoff=None)
    with pytest.raises(WRITER.WriterError, match="哈希"):
        WRITER.apply_patches(args)
    assert not output.exists()
    args.source_sha256 = WRITER.sha256(source.read_bytes().decode("utf-8"))
    result = WRITER.apply_patches(args)
    assert output.read_text(encoding="utf-8") == "修后正文\n结尾"
    assert source.read_text(encoding="utf-8") == "正文\n结尾"
    assert result["external_model_called"] is False
    with pytest.raises(WRITER.WriterError, match="覆盖"):
        WRITER.apply_patches(args)
    args.output = tmp_path / "draft.md"
    with pytest.raises(WRITER.WriterError, match="canonical"):
        WRITER.apply_patches(args)


def test_internal_verification_notes_are_not_sent_to_writer(tmp_path, monkeypatch):
    monkeypatch.setattr(WRITER, "__file__", str(tmp_path / "tools/gemini_writer.py"))
    monkeypatch.setattr(WRITER, "resolve_agy", lambda explicit: "agy")
    monkeypatch.setattr(WRITER, "cli_version", lambda binary, expected: expected)
    captured = []

    def fake_run(command, **kwargs):
        captured.append(json.loads(kwargs["input"])["message"]["content"])
        return WRITER.subprocess.CompletedProcess(command, 0, stdout=stream(), stderr="")

    monkeypatch.setattr(WRITER.subprocess, "run", fake_run)
    handoff = tmp_path / "handoff.json"
    handoff.write_text(json.dumps({"prompt": "本轮正文材料", "external_shareable": True,
                                   "verification_notes": "仅内部可见的核查备注"}), encoding="utf-8")
    args = argparse.Namespace(handoff=handoff, agy_bin=None, expected_version="1.4.2",
                              output_dir=tmp_path / ".tmp/run", model="gemini-test", effort="high", timeout=60)
    assert WRITER.run_handoff(args)["status"] == "SUCCESS"
    assert "本轮正文材料" in captured[0]
    assert "仅内部可见" not in captured[0]
