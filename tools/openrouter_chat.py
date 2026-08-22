#!/usr/bin/env python3
"""OpenRouter 命令行调用脚本，默认接 stealth/ox-alpha。

零第三方依赖（只用标准库 urllib）。
key 读取顺序：环境变量 OPENROUTER_API_KEY -> 当前目录 .env -> 仓库根 .env。

仓库内文件默认拒绝上传；确认为可公开材料后，必须显式增加
``--allow-repository-file``。APPSO internal/restricted 材料不得使用该例外。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

API_BASE = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "stealth/ox-alpha"
REPO_ROOT = Path(__file__).resolve().parent.parent


def load_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    for env_path in (Path.cwd() / ".env", REPO_ROOT / ".env"):
        if not env_path.exists():
            continue
        for line in env_path.read_text(
            encoding="utf-8-sig", errors="replace"
        ).splitlines():
            line = line.strip()
            if line.startswith("OPENROUTER_API_KEY="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                if value:
                    return value
    raise SystemExit(
        "[fail] 没找到 OPENROUTER_API_KEY。二选一：\n"
        '  PowerShell 临时：$env:OPENROUTER_API_KEY = "<OPENROUTER_API_KEY>"\n'
        f"  或写进 {REPO_ROOT / '.env'}：OPENROUTER_API_KEY=<OPENROUTER_API_KEY>"
    )


def open_request(path: str, key: str, payload: dict | None = None):
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://local/self-media-ops",
        "X-Title": "self-media-ops",
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload else None
    request = urllib.request.Request(
        f"{API_BASE}{path}",
        data=data,
        headers=headers,
        method="POST" if data else "GET",
    )
    try:
        return urllib.request.urlopen(request, timeout=600)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        raise SystemExit(f"[fail] HTTP {exc.code} {path}\n{body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(
            f"[fail] 连不上 OpenRouter（{exc.reason}）。"
            "请检查当前网络与 HTTPS_PROXY 配置。"
        ) from exc


def check_key(key: str) -> None:
    with open_request("/key", key) as response:
        info = json.loads(response.read().decode("utf-8"))["data"]
    limit = info.get("limit")
    print("[ok] key 可用")
    print(f"  label       : {info.get('label')}")
    print(f"  已用额度    : ${info.get('usage', 0):.4f}")
    print(f"  额度上限    : {'无限制' if limit is None else f'${limit}'}")
    print(f"  是否免费 key：{info.get('is_free_tier')}")


def repository_relative(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError:
        return False
    return True


def read_prompt_file(raw_path: str, allow_repository_file: bool) -> str:
    path = Path(raw_path).resolve()
    if not path.is_file():
        raise SystemExit(f"[fail] 文件不存在：{path}")
    if path.name.casefold() == ".env" or path.suffix.casefold() in {".pem", ".key"}:
        raise SystemExit("[fail] 凭据文件不得作为模型输入")
    if repository_relative(path) and not allow_repository_file:
        raise SystemExit(
            "[fail] 默认不向外部匿名模型上传仓库文件。"
            "确认为公开材料后可加 --allow-repository-file；"
            "APPSO internal/restricted 材料不得使用该例外。"
        )
    return path.read_text(encoding="utf-8", errors="replace").strip()


def build_messages(args: argparse.Namespace) -> list[dict]:
    parts: list[str] = []
    if args.prompt:
        parts.append(args.prompt.strip())
    if args.file:
        parts.append(read_prompt_file(args.file, args.allow_repository_file))
    if not parts:
        raise SystemExit("[fail] 没有输入：给一个 prompt 或 -f 文件")

    messages: list[dict] = []
    if args.system:
        messages.append({"role": "system", "content": args.system})
    messages.append({"role": "user", "content": "\n\n".join(parts)})
    return messages


def run_stream(response, echo: bool) -> tuple[str, dict]:
    chunks: list[str] = []
    usage: dict = {}
    for raw in response:
        line = raw.decode("utf-8", "replace").strip()
        if not line or line.startswith(":"):
            continue
        if not line.startswith("data: "):
            continue
        data = line[6:]
        if data == "[DONE]":
            break
        try:
            event = json.loads(data)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"[fail] 无法解析 SSE 分片：{data[:200]}") from exc
        if event.get("usage"):
            usage = event["usage"]
        for choice in event.get("choices", []):
            piece = (choice.get("delta") or {}).get("content") or ""
            if piece:
                chunks.append(piece)
                if echo:
                    print(piece, end="", flush=True)
    if echo:
        print()
    return "".join(chunks), usage


def run_blocking(response) -> tuple[str, dict]:
    body = json.loads(response.read().decode("utf-8"))
    if not body.get("choices"):
        raise SystemExit(
            "[fail] 返回里没有 choices：\n"
            + json.dumps(body, ensure_ascii=False, indent=2)
        )
    return body["choices"][0]["message"]["content"], body.get("usage", {})


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="OpenRouter CLI（默认 stealth/ox-alpha）"
    )
    parser.add_argument("prompt", nargs="?", help="提示词")
    parser.add_argument("-f", "--file", help="把文件内容拼进 user message")
    parser.add_argument("-s", "--system", help="system prompt")
    parser.add_argument(
        "-m", "--model", default=DEFAULT_MODEL, help=f"模型 id，默认 {DEFAULT_MODEL}"
    )
    parser.add_argument("-o", "--out", help="把回答写到文件")
    parser.add_argument("-t", "--temperature", type=float, default=None)
    parser.add_argument("--max-tokens", type=int, default=None)
    parser.add_argument("--no-stream", action="store_true", help="关闭流式输出")
    parser.add_argument("--check", action="store_true", help="只检查 key，不发 prompt")
    parser.add_argument(
        "--allow-repository-file",
        action="store_true",
        help="确认文件可公开后，允许读取仓库内文件",
    )
    return parser


def main() -> None:
    args = make_parser().parse_args()
    key = load_key()
    if args.check:
        check_key(key)
        return

    payload: dict = {
        "model": args.model,
        "messages": build_messages(args),
        "stream": not args.no_stream,
    }
    if payload["stream"]:
        payload["stream_options"] = {"include_usage": True}
    if args.temperature is not None:
        payload["temperature"] = args.temperature
    if args.max_tokens is not None:
        payload["max_tokens"] = args.max_tokens

    print(f"[info] model={args.model} stream={payload['stream']}", file=sys.stderr)
    with open_request("/chat/completions", key, payload) as response:
        if payload["stream"]:
            text, usage = run_stream(response, echo=True)
        else:
            text, usage = run_blocking(response)
            print(text)

    if not text.strip():
        raise SystemExit(
            "[fail] 模型返回空内容（模型 id 失效、限流或服务端无有效输出）"
        )
    if usage:
        print(
            f"[usage] prompt={usage.get('prompt_tokens')} "
            f"completion={usage.get('completion_tokens')} "
            f"total={usage.get('total_tokens')} cost=${usage.get('cost', 0)}",
            file=sys.stderr,
        )
    if args.out:
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print(f"[ok] 已写入 {output}", file=sys.stderr)


if __name__ == "__main__":
    main()
