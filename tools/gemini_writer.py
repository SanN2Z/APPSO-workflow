"""Bounded prose handoff to native agy; never edits the canonical article."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time


class WriterError(RuntimeError):
    pass


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def resolve_agy(explicit: str | None) -> str:
    runtime_file = Path(__file__).resolve().parents[1] / ".aris/runtime.local.json"
    local = json.loads(runtime_file.read_text(encoding="utf-8")) if runtime_file.is_file() else {}
    candidate = explicit or os.environ.get("AGY_BIN") or local.get("agy_bin") or shutil.which("agy")
    if not candidate or not Path(candidate).is_file():
        raise WriterError("agy 未找到。通过 --agy-bin 或 AGY_BIN 指定已安装的 agy；不自动换供应商。")
    if Path(candidate).stem.lower() != "agy":
        raise WriterError("入口必须是原生 agy，不使用其他 CLI 冒充 Gemini。")
    return str(Path(candidate).resolve())


def cli_version(binary: str, expected: str) -> str:
    result = subprocess.run([binary, "--version"], capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=20)
    version = result.stdout.strip()
    if result.returncode or version != expected:
        raise WriterError(f"agy 版本不匹配：要求 {expected}，实际 {version[:32] or '未返回'}。")
    return version


def load_handoff(path: Path) -> dict:
    handoff = json.loads(path.read_text(encoding="utf-8-sig"))
    if handoff.get("external_shareable") is not True:
        raise WriterError("先确认本次交接只含允许发给外部模型的材料：external_shareable=true。")
    if not isinstance(handoff.get("prompt"), str) or not handoff["prompt"].strip():
        raise WriterError("交接缺少 prompt。")
    if len(handoff["prompt"]) > 100_000:
        raise WriterError("交接过大，请收束到本轮必要事实和写作要求。")
    return handoff


def native_args(binary: str, model: str, effort: str, log: Path, seconds: int) -> list[str]:
    if not model.startswith("gemini-"):
        raise WriterError("Gemini 主笔必须显式选用 Gemini 模型。")
    return [binary, "--model", model, "--effort", effort, "--mode", "plan",
            "--sandbox", "--disable-slash-commands", "--input-format", "stream-json",
            "--output-format", "stream-json", "--print-timeout", f"{seconds}s",
            "--log-file", str(log)]


def inspect_stream(stream: str, requested: str) -> tuple[dict, list[str]]:
    events = []
    for line in stream.splitlines():
        if line.strip():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise WriterError("agy 返回了非 JSON 输出；原始输出保存在忽略目录，未伪报成功。") from exc
    init = next((e.get("init", {}) for e in events if e.get("event") == "init"), {})
    results = [e["result"] for e in events if e.get("event") == "result"]
    tools = sorted({e.get("step_update", {}).get("tool_name", "unknown") for e in events
                    if e.get("step_update", {}).get("step_type") == "tool"})
    if init.get("model") != requested:
        raise WriterError("实际返回的模型标识缺失或与指定模型不符；不自动降级。")
    if not results or results[-1].get("status") != "SUCCESS":
        raise WriterError("agy 未成功完成，不能把半截输出当成成稿。")
    result = results[-1]
    if not result.get("response", "").strip():
        raise WriterError("agy 返回空正文。")
    return {"init": init, "result": result}, tools


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def assemble_patches(source: str, allowed: list[dict], patches: list[dict],
                     locked: list[str]) -> str:
    """Apply only frozen, unique spans; offsets always refer to the first draft."""
    if source.lstrip("\ufeff").startswith("---\n") or source.lstrip("\ufeff").startswith("---\r\n"):
        raise WriterError("局部装配只接受无 frontmatter 的试写正文，避免沿用旧稿的发布状态。")
    for rows in (allowed, patches):
        if (not isinstance(rows, list) or not rows
                or any(not isinstance(p, dict) or not isinstance(p.get("id"), str)
                       or not p["id"] for p in rows)):
            raise WriterError("补丁与允许范围必须是带 id 的非空列表。")
        if len({p["id"] for p in rows}) != len(rows):
            raise WriterError("补丁 id 重复。")
    spans = {p["id"]: p for p in allowed}
    if set(spans) != {p["id"] for p in patches}:
        raise WriterError("补丁必须逐项对应冻结的允许范围，不能增加或遗漏。")
    edits = []
    for patch in patches:
        old, new = patch.get("old"), patch.get("new")
        if not isinstance(old, str) or not old or not isinstance(new, str):
            raise WriterError("每条补丁必须提供非空 old 和字符串 new。")
        if old != spans[patch["id"]].get("old") or source.count(old) != 1:
            raise WriterError("old 与冻结范围不一致，或在原稿中不存在／不唯一。")
        start = source.index(old)
        edits.append((start, start + len(old), new))
    edits.sort()
    previous = 0
    output = []
    for start, end, new in edits:
        if start < previous:
            raise WriterError("允许修改的原文范围相互重叠。")
        output.extend((source[previous:start], new))
        previous = end
    output.append(source[previous:])
    result = "".join(output)
    media = re.compile(r"!\[[^\]\n]*\](?:\([^\n]*?\)|\[[^\]\n]*\])?|"
                       r"<(?:img|video|source|picture)\b[^>]*>", re.IGNORECASE)
    if media.findall(source) != media.findall(result):
        raise WriterError("补丁改动了图片或视频标记及其顺序。")
    normalized_source, normalized_result = source.replace("\r\n", "\n"), result.replace("\r\n", "\n")
    if (not isinstance(locked, list) or any(not isinstance(fragment, str) or not fragment
            or normalized_source.count(fragment.replace("\r\n", "\n"))
            != normalized_result.count(fragment.replace("\r\n", "\n"))
            or fragment.replace("\r\n", "\n") not in normalized_source
            for fragment in locked)):
        raise WriterError("锁定段落缺失或被改动。")
    return result


def apply_patches(args: argparse.Namespace) -> dict:
    source_path, output = args.source.resolve(), args.output.resolve()
    source = source_path.read_bytes().decode("utf-8")
    if sha256(source) != args.source_sha256:
        raise WriterError("原稿哈希与审稿时冻结的版本不一致。")
    if output == source_path or output.name.lower() == "draft.md" or output.exists():
        raise WriterError("只装配成尚不存在的新文件，不覆盖原稿或 canonical draft.md。")
    allowed = json.loads(args.allowed_spans.read_text(encoding="utf-8-sig"))
    payload = json.loads(args.patches.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise WriterError("修复返回必须是包含 patches 的 JSON 对象。")
    locked = []
    if args.locked_handoff:
        locked = json.loads(args.locked_handoff.read_text(encoding="utf-8-sig")).get("locked_fragments", [])
    result = assemble_patches(source, allowed, payload.get("patches"), locked)
    # Exclusive creation also protects against a file appearing after validation.
    with output.open("x", encoding="utf-8", newline="") as stream:
        stream.write(result)
    return {"status": "ASSEMBLED", "source_sha256": sha256(source),
            "response_sha256": sha256(result), "patches": len(allowed),
            "media_preserved": True, "locked_fragments_preserved": True,
            "canonical_written": False, "external_model_called": False,
            "publication_checks": "not run; editorial review still required"}


def run_handoff(args: argparse.Namespace) -> dict:
    handoff = load_handoff(args.handoff.resolve())
    binary = resolve_agy(args.agy_bin)
    version = cli_version(binary, args.expected_version)
    output = args.output_dir.resolve()
    # Raw native diagnostics may contain account metadata. Keep them in an ignored,
    # dedicated directory; the tracked receipt is a deliberate allowlist instead.
    root = Path(__file__).resolve().parents[1]
    if not output.is_relative_to(root / ".tmp"):
        raise WriterError("运行输出必须位于本仓库 .tmp/，避免凭据或登录诊断进入 Git。")
    output.mkdir(parents=True, exist_ok=False)
    receipt = {"route": "native agy CLI", "cli_version": version,
               "requested_model": args.model, "requested_effort": args.effort,
               "prompt_sha256": sha256(handoff["prompt"]), "status": "STARTED",
               "provenance_limit": "CLI-reported metadata; not independent remote-model attestation.",
               "sandbox_requested": True, "canonical_written": False}
    write_json(output / "receipt.json", receipt)
    command = native_args(binary, args.model, args.effort, output / "native.log", args.timeout)
    prompt = ("你只负责写作。所需材料全部在下方，不调用工具、不读取文件、不联网、"
              "不创建或修改文件。直接在回复中返回正文。\n\n" + handoff["prompt"])
    payload = json.dumps({"event": "user", "message": {"content": prompt}}, ensure_ascii=False) + "\n"
    receipt["sent_prompt_sha256"] = sha256(prompt)
    started = time.monotonic()
    try:
        # No repository ancestors: native AGENTS/CLAUDE discovery must not import
        # unrelated company or scientific material into the writing session.
        with tempfile.TemporaryDirectory(prefix="content-agy-writer-") as workspace:
            completed = subprocess.run(command, input=payload, cwd=workspace,
                                       capture_output=True, text=True, encoding="utf-8",
                                       errors="replace", timeout=args.timeout + 45)
        (output / "native.stdout.log").write_text(completed.stdout, encoding="utf-8")
        (output / "native.stderr.log").write_text(completed.stderr, encoding="utf-8")
        receipt["exit_code"] = completed.returncode
        if completed.returncode:
            raise WriterError("agy 退出失败。请在本地查看忽略目录中的诊断；不向用户输出认证日志。")
        inspected, tools = inspect_stream(completed.stdout, args.model)
        result = inspected["result"]
        response = result["response"]
        (output / "response.md").write_text(response, encoding="utf-8")
        receipt.update({"reported_model": inspected["init"]["model"], "tool_calls": tools,
                        "usage": result.get("usage"), "response_sha256": sha256(response),
                        "native_duration_seconds": result.get("duration_seconds"),
                        "locked_fragments_preserved": all(fragment in response for fragment in
                                                          handoff.get("locked_fragments", []))})
        log = output / "native.log"
        if log.is_file():
            labels = re.findall(r'Propagating selected model override to backend: label="([^"]+)"',
                                log.read_text(encoding="utf-8", errors="replace"))
            receipt["selected_model_label_from_log"] = labels[-1] if labels else None
        if tools:
            raise WriterError("本轮写作发生了工具调用，超出纯文本交接约束；保留输出供核查。")
        if not receipt["locked_fragments_preserved"]:
            raise WriterError("Gemini 改动或遗漏锁定段落；保留原始输出，不覆盖原稿。")
        receipt["status"] = "SUCCESS"
    except (WriterError, subprocess.TimeoutExpired) as exc:
        receipt.update({"status": "FAILED", "error": str(exc) if isinstance(exc, WriterError)
                        else "agy 调用超时；没有自动重试或切换供应商。"})
    finally:
        receipt["wall_seconds"] = round(time.monotonic() - started, 3)
        write_json(output / "receipt.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["doctor", "draft", "apply-patches"])
    parser.add_argument("--agy-bin")
    parser.add_argument("--expected-version", default="1.4.2")
    parser.add_argument("--model")
    parser.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"])
    parser.add_argument("--handoff", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--source-sha256")
    parser.add_argument("--allowed-spans", type=Path)
    parser.add_argument("--patches", type=Path)
    parser.add_argument("--locked-handoff", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "apply-patches":
            if not all((args.source, args.source_sha256, args.allowed_spans, args.patches, args.output)):
                parser.error("apply-patches requires --source, --source-sha256, --allowed-spans, --patches and --output")
            result = apply_patches(args)
        elif not args.model or not args.effort:
            parser.error("doctor/draft requires explicit --model and --effort")
        elif args.command == "doctor":
            version = cli_version(resolve_agy(args.agy_bin), args.expected_version)
            result = {"cli_version": version, "requested_model": args.model,
                      "login_and_model_connectivity": "not probed", "status": "LOCAL_BINARY_OK"}
        else:
            if not args.handoff or not args.output_dir:
                parser.error("draft requires --handoff and --output-dir")
            result = run_handoff(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] != "FAILED" else 1
    except (WriterError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "FAILED", "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
