#!/usr/bin/env python3
"""Bridge project content packages to the pinned Wenyan CLI.

Wenyan owns Markdown rendering, image uploads, and WeChat API calls. This file
only adapts the project's content-package schema and enforces local release
gates. The default is preview/dry-run; ``draft --execute`` is the only command
that can create an external WeChat draft.
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
WECHAT_ROOT = Path(__file__).resolve().parents[1]
WENYAN_CMD = WECHAT_ROOT / "node_modules" / ".bin" / "wenyan.cmd"
VALIDATOR = (
    WORKSPACE_ROOT
    / ".agents"
    / "skills"
    / "self-media-ops"
    / "scripts"
    / "validate_content_package.py"
)
WENYAN_RUNTIME = WECHAT_ROOT / ".wenyan-runtime"

FRONTMATTER_RE = re.compile(r"\A---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)\Z", re.S)
MD_IMAGE_RE = re.compile(r"(!\[[^\]]*\]\()(?P<target><[^>]+>|[^)\s]+)(?P<tail>[^)]*\))")
HTML_IMAGE_RE = re.compile(r"(<img\b[^>]*\bsrc=[\"'])(?P<target>[^\"']+)([\"'])", re.I)

UNRESOLVED_RIGHTS = {
    "",
    "unknown",
    "needs_review",
    "editorial_use_needs_review",
    "user_confirmation_required",
    "research_reference",
}
WENYAN_NOTES = [
    "Wenyan CLI 2.0.11 does not forward a custom digest to draft/add; WeChat will derive it, so check or edit the digest in the backend.",
    "Wenyan CLI 2.0.11 uploads body images as permanent image materials and caches repeat uploads.",
]


class WorkflowError(RuntimeError):
    """A user-actionable workflow failure."""


@dataclass(frozen=True)
class PublishConfig:
    title: str
    author: str = ""
    digest: str = ""
    cover: str = ""
    source_url: str = ""
    theme: str = "default"
    highlight: str = "solarized-light"
    mac_style: bool = False
    footnote: bool = True
    need_open_comment: bool = False
    only_fans_can_comment: bool = False


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        raise WorkflowError(f"YAML root must be an object: {path}")
    return loaded


def load_draft(package: Path) -> tuple[dict[str, Any], str]:
    path = package / "draft.md"
    if not path.is_file():
        raise WorkflowError(f"draft not found: {path}")
    match = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if not match:
        raise WorkflowError(f"draft frontmatter is missing or malformed: {path}")
    metadata = yaml.safe_load(match.group(1)) or {}
    if not isinstance(metadata, dict):
        raise WorkflowError("draft frontmatter must be a YAML object")
    return metadata, match.group(2).strip() + "\n"


def strip_leading_h1(body: str) -> str:
    lines = body.splitlines()
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        if line.startswith("# "):
            lines.pop(index)
            while index < len(lines) and not lines[index].strip():
                lines.pop(index)
        break
    clean = "\n".join(lines).strip() + "\n"
    if not clean.strip():
        raise WorkflowError("draft body is empty after removing the editorial H1")
    return clean


def load_publish_config(package: Path, metadata: dict[str, Any]) -> PublishConfig:
    raw = load_yaml(package / "publish.yml")
    source_url = raw.get("source_url") or raw.get("content_source_url") or ""
    return PublishConfig(
        title=str(raw.get("title") or metadata.get("title") or "").strip(),
        author=str(raw.get("author") or "").strip(),
        digest=str(raw.get("digest") or "").strip(),
        cover=str(raw.get("cover") or "").strip(),
        source_url=str(source_url).strip(),
        theme=str(raw.get("theme") or "default").strip(),
        highlight=str(raw.get("highlight") or "solarized-light").strip(),
        mac_style=bool(raw.get("mac_style", False)),
        footnote=bool(raw.get("footnote", True)),
        need_open_comment=bool(raw.get("need_open_comment", False)),
        only_fans_can_comment=bool(raw.get("only_fans_can_comment", False)),
    )


def is_remote_or_special(target: str) -> bool:
    parsed = urlparse(target)
    return bool(parsed.scheme) or target.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:[\\/]", target) is not None


def relocate_target(target: str) -> str:
    wrapped = target.startswith("<") and target.endswith(">")
    clean = target[1:-1] if wrapped else target
    if is_remote_or_special(clean):
        return target
    moved = "../" + clean.replace("\\", "/").removeprefix("./")
    return f"<{moved}>" if wrapped else moved


def relocate_body_images(body: str) -> str:
    body = MD_IMAGE_RE.sub(
        lambda match: match.group(1) + relocate_target(match.group("target")) + match.group("tail"),
        body,
    )
    return HTML_IMAGE_RE.sub(
        lambda match: match.group(1) + relocate_target(match.group("target")) + match.group(3),
        body,
    )


def generated_frontmatter(config: PublishConfig) -> dict[str, Any]:
    frontmatter: dict[str, Any] = {"title": config.title}
    for key, value in (
        ("cover", relocate_target(config.cover) if config.cover else ""),
        ("author", config.author),
        ("source_url", config.source_url),
    ):
        if value:
            frontmatter[key] = value
    frontmatter["need_open_comment"] = config.need_open_comment
    frontmatter["only_fans_can_comment"] = config.only_fans_can_comment
    return frontmatter


def prepare_source(package: Path) -> tuple[Path, dict[str, Any], PublishConfig, str]:
    metadata, body = load_draft(package)
    config = load_publish_config(package, metadata)
    clean_body = relocate_body_images(strip_leading_h1(body))
    frontmatter = yaml.safe_dump(
        generated_frontmatter(config),
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    ).strip()
    dist = package / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    source_path = dist / "wenyan-source.md"
    source_path.write_text(f"---\n{frontmatter}\n---\n\n{clean_body}", encoding="utf-8")
    return source_path, metadata, config, clean_body


def wenyan_args(command: str, source: Path, config: PublishConfig) -> list[str]:
    if not WENYAN_CMD.is_file():
        raise WorkflowError(
            "Wenyan is not installed. Run `npm.cmd install` inside 微信公众号 first."
        )
    args = [str(WENYAN_CMD), command, "-f", str(source), "-t", config.theme, "-h", config.highlight]
    args.append("--mac-style" if config.mac_style else "--no-mac-style")
    args.append("--footnote" if config.footnote else "--no-footnote")
    return args


def wenyan_environment() -> dict[str, str]:
    """Keep Wenyan token/material caches private and local to this project."""
    environment = os.environ.copy()
    environment["XDG_CONFIG_HOME"] = str(WENYAN_RUNTIME)
    return environment


def run_wenyan_render(source: Path, config: PublishConfig) -> str:
    result = subprocess.run(
        wenyan_args("render", source, config),
        cwd=WECHAT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        env=wenyan_environment(),
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise WorkflowError(f"Wenyan render failed ({result.returncode}): {detail}")
    rendered = result.stdout.strip()
    if not rendered:
        raise WorkflowError("Wenyan render returned empty HTML")
    return rendered


def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def inline_preview_images(fragment: str, package: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        target = match.group("target")
        if is_remote_or_special(target):
            return match.group(0)
        resolved = (package / "dist" / target).resolve()
        try:
            resolved.relative_to(package.resolve())
        except ValueError as exc:
            raise WorkflowError(f"rendered image path escapes package: {target}") from exc
        if not resolved.is_file():
            raise WorkflowError(f"rendered local image is missing: {target}")
        return match.group(1) + data_uri(resolved) + match.group(3)

    return HTML_IMAGE_RE.sub(replace, fragment)


def validator_report(package: Path) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(package)],
        cwd=WORKSPACE_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    report = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
    return result.returncode == 0, report


def publication_blockers(package: Path, metadata: dict[str, Any], config: PublishConfig) -> list[str]:
    blockers: list[str] = []
    if not config.title:
        blockers.append("publish title is empty")
    if len(config.title) > 32:
        blockers.append(f"publish title has {len(config.title)} characters; WeChat API limit is 32")
    if len(config.author) > 16:
        blockers.append(f"author has {len(config.author)} characters; WeChat API limit is 16")
    if len(config.digest) > 128:
        blockers.append(f"digest has {len(config.digest)} characters; WeChat API limit is 128")
    if str(metadata.get("status") or "") != "ready":
        blockers.append(f"content status is {metadata.get('status') or 'missing'}, not ready")
    for flag in ("fact_checked", "rights_checked", "copyedit_checked"):
        if metadata.get(flag) is not True:
            blockers.append(f"draft frontmatter has {flag} != true")

    if not config.cover:
        blockers.append("publish.yml has no cover; an explicit rights-cleared cover is required")
        return blockers
    cover = (package / config.cover).resolve()
    try:
        cover.relative_to(package.resolve())
    except ValueError:
        blockers.append("cover path escapes the content package")
        return blockers
    if not cover.is_file():
        blockers.append(f"cover does not exist: {config.cover}")

    manifest = load_yaml(package / "asset-manifest.yml")
    assets = manifest.get("assets") or []
    entry = next(
        (
            item
            for item in assets
            if isinstance(item, dict)
            and str(item.get("file") or "").replace("\\", "/") == config.cover.replace("\\", "/")
        ),
        None,
    )
    if entry is None:
        blockers.append("cover is not registered in asset-manifest.yml")
    else:
        rights = str(entry.get("rights_status") or "").strip()
        platforms = entry.get("allowed_platforms") or []
        if rights in UNRESOLVED_RIGHTS:
            blockers.append(f"cover rights_status is unresolved: {rights or 'missing'}")
        if "wechat" not in platforms:
            blockers.append("cover asset is not allowed for the wechat platform")
    return blockers


def preview_document(title: str, fragment: str, validator_ok: bool, report: str, blockers: list[str]) -> str:
    status = "内容包校验通过" if validator_ok else "内容包校验未通过"
    issues = "".join(f"<li>{html.escape(item)}</li>" for item in blockers)
    blocker_box = f"<ul>{issues}</ul>" if issues else "<p>草稿箱门禁无阻塞项。</p>"
    notes = "".join(f"<li>{html.escape(item)}</li>" for item in WENYAN_NOTES)
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} - 公众号本机预览</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#eef1f5;color:#222;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}}
.bar{{position:sticky;top:0;z-index:2;padding:10px 16px;background:#20242a;color:#fff;text-align:center;font-size:13px}}
.gate{{width:min(720px,calc(100% - 24px));margin:16px auto;padding:12px 16px;border:1px solid #e1bb68;border-radius:8px;background:#fff8e8;font-size:13px;line-height:1.6}}
.gate pre{{white-space:pre-wrap;word-break:break-word;color:#666}}.gate ul{{margin:6px 0;padding-left:20px}}
.phone{{width:min(430px,100%);min-height:100vh;margin:18px auto 40px;padding:28px 22px 54px;background:#fff;box-shadow:0 12px 40px rgba(24,31,43,.15)}}
.title{{margin:0 0 22px;font-size:24px;line-height:1.4;color:#111}}@media(max-width:520px){{.phone{{margin:0;box-shadow:none}}}}
</style></head><body><div class="bar">本机预览 · Wenyan 渲染 · 不会上传</div>
<aside class="gate"><strong>{html.escape(status)}</strong>{blocker_box}<details><summary>查看 Wenyan 版本说明</summary><ul>{notes}</ul></details><details><summary>查看校验输出</summary><pre>{html.escape(report)}</pre></details></aside>
<main class="phone"><h1 class="title">{html.escape(title)}</h1>{fragment}</main></body></html>"""


def build_preview(package_arg: str | Path) -> tuple[Path, Path, dict[str, Any], PublishConfig, list[str]]:
    package = Path(package_arg).resolve()
    if not package.is_dir():
        raise WorkflowError(f"content package is not a directory: {package}")
    source, metadata, config, _ = prepare_source(package)
    rendered = run_wenyan_render(source, config)
    rendered_for_preview = inline_preview_images(rendered, package)
    validator_ok, report = validator_report(package)
    blockers = publication_blockers(package, metadata, config)
    dist = package / "dist"
    content_path = dist / "wechat-content.html"
    preview_path = dist / "wechat-preview.html"
    content_path.write_text(rendered, encoding="utf-8")
    preview_path.write_text(
        preview_document(config.title, rendered_for_preview, validator_ok, report, blockers),
        encoding="utf-8",
    )
    plan = {
        "renderer": "@wenyan-md/cli@2.0.11",
        "source": source.name,
        "preview": preview_path.name,
        "config": asdict(config),
        "content_status": metadata.get("status"),
        "validator_ok": validator_ok,
        "blockers": blockers,
        "known_limitations": WENYAN_NOTES,
        "external_effect": "none; local render only",
    }
    (dist / "publish-plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"[preview] {preview_path}")
    print(f"[renderer] Wenyan CLI 2.0.11; html_chars={len(rendered)}")
    if report:
        print(report)
    if blockers:
        print("[draft blockers]")
        for item in blockers:
            print(f"- {item}")
    for item in WENYAN_NOTES:
        print(f"[wenyan note] {item}")
    return preview_path, source, metadata, config, blockers


def command_preview(args: argparse.Namespace) -> int:
    preview_path, _, _, _, _ = build_preview(args.package)
    if args.open:
        if os.name != "nt":
            raise WorkflowError("--open is currently implemented for Windows only")
        os.startfile(preview_path)  # type: ignore[attr-defined]
    return 0


def command_draft(args: argparse.Namespace) -> int:
    _, source, metadata, config, blockers = build_preview(args.package)
    validator_ok, report = validator_report(Path(args.package).resolve())
    if not args.execute:
        print("[dry-run] no network call or external write was performed; add --execute to create one draft")
        return 0
    if not validator_ok:
        raise WorkflowError(f"content-package validator blocks draft creation:\n{report}")
    if blockers:
        raise WorkflowError("draft creation is blocked:\n- " + "\n- ".join(blockers))
    env_path = Path(args.env).resolve() if args.env else WECHAT_ROOT / ".env"
    if not env_path.is_file():
        raise WorkflowError(
            "credential file is missing. Copy 微信公众号/.env.example to 微信公众号/.env and fill it locally; never paste the secret into chat."
        )
    command = wenyan_args("publish", source, config) + ["--env-file", str(env_path)]
    print("[execute] invoking pinned Wenyan CLI to upload assets and create one WeChat draft")
    result = subprocess.run(command, cwd=WECHAT_ROOT, env=wenyan_environment(), check=False)
    if result.returncode != 0:
        raise WorkflowError(f"Wenyan publish failed with exit code {result.returncode}")
    record = {
        "renderer": "@wenyan-md/cli@2.0.11",
        "title": config.title,
        "external_effect": "created one WeChat draft; did not publish or mass-send",
    }
    dist = Path(args.package).resolve() / "dist"
    (dist / "wechat-draft-result.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("[done] one WeChat draft was created; nothing was published or mass-sent")
    return 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preview a content package with Wenyan and optionally create one WeChat draft."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    preview = subparsers.add_parser("preview", help="render a local phone-width preview")
    preview.add_argument("package", help="path to a WeChat content package")
    preview.add_argument("--open", action="store_true", help="open preview in the default browser")
    preview.set_defaults(func=command_preview)
    draft = subparsers.add_parser("draft", help="dry-run by default; --execute creates one draft")
    draft.add_argument("package", help="path to a WeChat content package")
    draft.add_argument("--execute", action="store_true", help="create one WeChat draft through Wenyan")
    draft.add_argument("--env", help="path to a local credential .env file")
    draft.set_defaults(func=command_draft)
    return parser


def main() -> int:
    args = make_parser().parse_args()
    try:
        return int(args.func(args))
    except WorkflowError as exc:
        print(f"[fail] {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"[fail] unexpected error: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
