from __future__ import annotations

import base64
import hashlib
import importlib.metadata
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

MAX_MARKDOWN_BYTES = 8 * 1024 * 1024
MAX_IMAGE_BYTES = 20 * 1024 * 1024
MAX_TOTAL_IMAGE_BYTES = 60 * 1024 * 1024
MAX_RENDERED_HTML_BYTES = 96 * 1024 * 1024
SUPPORTED_IMAGE_MIMES = {
    ".gif": "image/gif",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}
FRONTMATTER_RE = re.compile(
    r"\A---[ \t]*\r?\n(?P<meta>.*?)\r?\n---[ \t]*\r?\n(?P<body>.*)\Z",
    re.S,
)
YAML_KEY_RE = re.compile(r"^(?P<key>[A-Za-z_][A-Za-z0-9_-]*):(?:[ \t]*(?P<value>.*))?$")


class LockedFormatError(RuntimeError):
    """A format-contract violation that must stop rendering."""


WorkflowError = LockedFormatError


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def read_bounded(path: Path, limit: int) -> bytes:
    size = path.stat().st_size
    if size > limit:
        raise WorkflowError(f"{path.name} exceeds the {limit} byte local limit")
    return path.read_bytes()


def parse_scalar(raw: str | None) -> Any:
    if raw is None:
        return None
    value = raw.strip()
    if not value:
        return None
    if value.startswith('"') and value.endswith('"'):
        try:
            return json.loads(value)
        except json.JSONDecodeError as exc:
            raise WorkflowError(f"invalid quoted YAML scalar: {value}") from exc
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "~"}:
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def parse_top_level_yaml(text: str, source: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line or line[0].isspace() or line.lstrip().startswith("#"):
            continue
        match = YAML_KEY_RE.match(line)
        if not match:
            continue
        key = match.group("key")
        if key in result:
            raise WorkflowError(f"{source} declares {key!r} more than once")
        try:
            result[key] = parse_scalar(match.group("value"))
        except WorkflowError as exc:
            raise WorkflowError(f"{source}:{line_number}: {exc}") from exc
    return result


def read_draft(path: Path) -> tuple[dict[str, Any], str, bytes]:
    raw = read_bounded(path, MAX_MARKDOWN_BYTES)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise WorkflowError(f"{path} must be UTF-8") from exc
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise WorkflowError(f"{path} must contain YAML frontmatter")
    metadata = parse_top_level_yaml(match.group("meta"), str(path))
    return metadata, match.group("body"), raw


def append_run(runs: list[dict[str, Any]], text: str, style: dict[str, Any]) -> None:
    if not text:
        return
    run = {
        "text": text,
        "bold": bool(style["bold"]),
        "italic": bool(style["italic"]),
        "underline": False,
        "strike": False,
        "link": style["link"],
    }
    if runs and all(runs[-1].get(key) == run.get(key) for key in run if key != "text"):
        runs[-1]["text"] += text
    else:
        runs.append(run)


def inline_runs(children: list[Any]) -> tuple[str, list[dict[str, Any]]]:
    runs: list[dict[str, Any]] = []
    style = {"bold": 0, "italic": 0, "link": None}
    for child in children:
        token_type = child.type
        if token_type == "strong_open":
            style["bold"] += 1
        elif token_type == "strong_close":
            style["bold"] = max(0, style["bold"] - 1)
        elif token_type == "em_open":
            style["italic"] += 1
        elif token_type == "em_close":
            style["italic"] = max(0, style["italic"] - 1)
        elif token_type == "link_open":
            href = child.attrGet("href") or ""
            if not re.match(r"^https?://", href, re.I):
                raise WorkflowError(f"only http(s) inline links are supported: {href}")
            style["link"] = href
        elif token_type == "link_close":
            style["link"] = None
        elif token_type in {"text", "code_inline"}:
            append_run(runs, child.content, style)
        elif token_type in {"softbreak", "hardbreak"}:
            append_run(runs, "\n", style)
        else:
            raise WorkflowError(f"unsupported inline Markdown token: {token_type}")
    text = "".join(run["text"] for run in runs).strip()
    return text, runs


def safe_image_path(package: Path, source: str) -> Path:
    parsed = urlparse(source)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
        raise WorkflowError(f"only local image paths are supported: {source}")
    decoded = unquote(parsed.path)
    candidate = (package / Path(decoded.replace("/", os.sep))).resolve()
    try:
        candidate.relative_to(package.resolve())
    except ValueError as exc:
        raise WorkflowError(
            f"image path escapes the content package: {source}"
        ) from exc
    if not candidate.is_file():
        raise WorkflowError(f"missing local image: {source}")
    if candidate.suffix.lower() not in SUPPORTED_IMAGE_MIMES:
        raise WorkflowError(f"unsupported image type: {source}")
    if candidate.stat().st_size > MAX_IMAGE_BYTES:
        raise WorkflowError(f"image exceeds {MAX_IMAGE_BYTES} bytes: {source}")
    return candidate


def image_block(
    package: Path, child: Any, order: int, *, embed_images: bool = True
) -> tuple[dict[str, Any], int]:
    source = child.attrGet("src") or ""
    path = safe_image_path(package, source)
    size = path.stat().st_size
    data = path.read_bytes() if embed_images else b""
    mime = SUPPORTED_IMAGE_MIMES[path.suffix.lower()]
    image = {
        "token": path.stem,
        "sourceName": path.name,
        "alt": child.content or "",
        "mime": mime,
        "bytes": size,
        "originalBytes": size,
    }
    if embed_images:
        image["dataUri"] = (
            f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"
        )
    block = {
        "id": f"local-image-{order}",
        "order": order,
        "type": "image",
        "image": image,
    }
    return block, size


def markdown_blocks(
    body: str, package: Path, title: str, *, embed_images: bool = True
) -> tuple[list[dict[str, Any]], int]:
    try:
        from markdown_it import MarkdownIt
    except ImportError as exc:
        raise WorkflowError("markdown-it-py is required for local build") from exc

    tokens = MarkdownIt("commonmark", {"html": True}).enable("table").parse(body)
    blocks: list[dict[str, Any]] = []
    quote_depth = 0
    list_stack: list[bool] = []
    in_list_item = False
    item_paragraphs = 0
    image_bytes = 0
    order = 0
    index = 0

    while index < len(tokens):
        token = tokens[index]
        token_type = token.type
        if token_type == "blockquote_open":
            quote_depth += 1
            index += 1
            continue
        if token_type == "blockquote_close":
            quote_depth = max(0, quote_depth - 1)
            index += 1
            continue
        if token_type in {"bullet_list_open", "ordered_list_open"}:
            list_stack.append(token_type == "ordered_list_open")
            if len(list_stack) > 1:
                raise WorkflowError(
                    "nested Markdown lists are not supported by the locked profile"
                )
            index += 1
            continue
        if token_type in {"bullet_list_close", "ordered_list_close"}:
            list_stack.pop()
            index += 1
            continue
        if token_type == "list_item_open":
            in_list_item = True
            item_paragraphs = 0
            index += 1
            continue
        if token_type == "list_item_close":
            in_list_item = False
            index += 1
            continue
        if token_type == "heading_open":
            if index + 2 >= len(tokens) or tokens[index + 1].type != "inline":
                raise WorkflowError("malformed Markdown heading")
            level = int(token.tag[1:])
            text, runs = inline_runs(tokens[index + 1].children or [])
            order += 1
            blocks.append(
                {
                    "id": f"block-{order}",
                    "order": order,
                    "type": f"heading{level}",
                    "text": text,
                    "runs": runs,
                }
            )
            index += 3
            continue
        if token_type == "paragraph_open":
            if index + 2 >= len(tokens) or tokens[index + 1].type != "inline":
                raise WorkflowError("malformed Markdown paragraph")
            children = tokens[index + 1].children or []
            significant = [
                child
                for child in children
                if child.type not in {"softbreak", "hardbreak"}
            ]
            images = [child for child in significant if child.type == "image"]
            if images:
                if len(images) != len(significant) or quote_depth or in_list_item:
                    raise WorkflowError(
                        "images must occupy their own paragraph outside quotes and lists"
                    )
                for child in images:
                    order += 1
                    block, size = image_block(
                        package, child, order, embed_images=embed_images
                    )
                    blocks.append(block)
                    image_bytes += size
                    if image_bytes > MAX_TOTAL_IMAGE_BYTES:
                        raise WorkflowError(
                            f"article images exceed {MAX_TOTAL_IMAGE_BYTES} bytes"
                        )
            else:
                text, runs = inline_runs(children)
                if text:
                    if in_list_item:
                        item_paragraphs += 1
                        if item_paragraphs > 1:
                            raise WorkflowError(
                                "multi-paragraph list items are not supported"
                            )
                    order += 1
                    if in_list_item:
                        block_type = "ordered" if list_stack[-1] else "bullet"
                    elif quote_depth:
                        block_type = "quote"
                    else:
                        block_type = "text"
                    blocks.append(
                        {
                            "id": f"block-{order}",
                            "order": order,
                            "type": block_type,
                            "text": text,
                            "runs": runs,
                        }
                    )
            index += 3
            continue
        if token_type in {"fence", "code_block"}:
            if quote_depth or in_list_item:
                raise WorkflowError("nested code blocks are not supported")
            order += 1
            blocks.append(
                {
                    "id": f"block-{order}",
                    "order": order,
                    "type": "code",
                    "text": token.content.rstrip(),
                    "runs": [],
                }
            )
            index += 1
            continue
        if token_type == "hr":
            order += 1
            blocks.append(
                {
                    "id": f"block-{order}",
                    "order": order,
                    "type": "divider",
                }
            )
            index += 1
            continue
        if token_type in {"heading_close", "paragraph_close", "inline"}:
            index += 1
            continue
        raise WorkflowError(f"unsupported Markdown token: {token_type}")

    if blocks and blocks[0].get("type") == "heading1":
        if blocks[0].get("text", "").strip() != title.strip():
            raise WorkflowError("leading H1 must exactly match frontmatter title")
        blocks.pop(0)
        for new_order, block in enumerate(blocks, 1):
            block["order"] = new_order
            block["id"] = f"block-{new_order}"

    heading_types = {block.get("type") for block in blocks}
    if "heading1" in heading_types:
        raise WorkflowError("body H1 is unsupported; use frontmatter title")
    if any(
        heading in heading_types for heading in {"heading4", "heading5", "heading6"}
    ):
        raise WorkflowError("only Markdown H2 and H3 are supported in the body")
    seen_heading_2 = False
    for block in blocks:
        if block.get("type") == "heading2":
            seen_heading_2 = True
        elif block.get("type") == "heading3" and not seen_heading_2:
            raise WorkflowError(
                "Markdown H3 requires an H2 before it so heading mapping cannot drift"
            )
    return blocks, image_bytes


def unique_profile_entry(
    items: Any,
    key: str,
    value: str,
    label: str,
) -> dict[str, Any]:
    if not isinstance(items, list):
        raise WorkflowError(f"profile {label} collection must be an array")
    matches = [
        item for item in items if isinstance(item, dict) and item.get(key) == value
    ]
    if len(matches) != 1:
        raise WorkflowError(
            f"profile must declare exactly one {label} {value}; found {len(matches)}"
        )
    return matches[0]


def resolve_profile_path(repo_root: Path, relative: Any, field: str) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        raise WorkflowError(f"{field} path is missing")
    candidate = (repo_root / Path(relative)).resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise WorkflowError(f"{field} path escapes the workspace") from exc
    if not candidate.is_file():
        raise WorkflowError(f"{field} file is missing: {relative}")
    return candidate


def audit_locked_profile(profile: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    if profile.get("schema_version") != 2:
        raise WorkflowError("locked profile schema_version must be 2")

    source_files = profile.get("source_files")
    brand_assets = profile.get("brand_assets")
    if not isinstance(source_files, list):
        raise WorkflowError("profile source_files must be an array")
    if not isinstance(brand_assets, list):
        raise WorkflowError("profile brand_assets must be an array")

    def unique_index(
        items: list[Any], key: str, label: str
    ) -> dict[str, dict[str, Any]]:
        index: dict[str, dict[str, Any]] = {}
        for position, item in enumerate(items):
            if not isinstance(item, dict):
                raise WorkflowError(
                    f"profile {label} item {position} must be an object"
                )
            identifier = item.get(key)
            if not isinstance(identifier, str) or not identifier.strip():
                raise WorkflowError(f"profile {label} item {position} has no {key}")
            if identifier in index:
                raise WorkflowError(f"profile {label} {identifier} is duplicated")
            index[identifier] = item
        return index

    source_by_role = unique_index(source_files, "role", "source role")
    brand_by_id = unique_index(brand_assets, "id", "brand asset")
    for role in ("markdown_adapter", "renderer_bridge", "renderer_and_semantics"):
        if role not in source_by_role:
            raise WorkflowError(f"profile source role {role} is missing")
    if "appso_title" not in brand_by_id:
        raise WorkflowError("profile brand asset appso_title is missing")

    runtime_dependencies = profile.get("runtime_dependencies")
    if not isinstance(runtime_dependencies, dict):
        raise WorkflowError("profile runtime_dependencies must be an object")
    required_dependencies = {
        "markdown-it-py": "4.0.0",
        "mdurl": "0.1.2",
    }
    if runtime_dependencies != required_dependencies:
        raise WorkflowError(
            "profile runtime dependency lock is incomplete or unsupported"
        )
    actual_dependencies: dict[str, str] = {}
    for name, expected_version in required_dependencies.items():
        try:
            actual_version = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError as exc:
            raise WorkflowError(
                f"locked runtime dependency is missing: {name}"
            ) from exc
        actual_dependencies[name] = actual_version
        if actual_version != expected_version:
            raise WorkflowError(
                f"locked runtime dependency version mismatch: {name} "
                f"expected {expected_version}, found {actual_version}"
            )

    verified: list[dict[str, Any]] = []
    for identifier, item in [
        *source_by_role.items(),
        *brand_by_id.items(),
    ]:
        path = resolve_profile_path(
            repo_root, item.get("path"), f"profile source {identifier}"
        )
        expected = str(item.get("sha256") or "").lower()
        if not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise WorkflowError(f"profile source hash is invalid: {identifier}")
        actual = sha256_file(path)
        if actual != expected:
            raise WorkflowError(f"format source hash mismatch: {item.get('path')}")
        verified.append(
            {
                "role": identifier,
                "path": item.get("path"),
                "expected_sha256": expected,
                "actual_sha256": actual,
                "verified": True,
            }
        )

    adapter_path = resolve_profile_path(
        repo_root, source_by_role["markdown_adapter"].get("path"), "markdown adapter"
    )
    if adapter_path != Path(__file__).resolve():
        raise WorkflowError(
            "profile markdown_adapter is not the imported locked adapter"
        )
    renderer_path = resolve_profile_path(
        repo_root,
        source_by_role["renderer_and_semantics"].get("path"),
        "renderer",
    )
    renderer_source = renderer_path.read_text(encoding="utf-8")
    styles = profile.get("style_assertions")
    if not isinstance(styles, dict):
        raise WorkflowError("profile style_assertions must be an object")

    def renderer_style(name: str) -> dict[str, str]:
        match = re.search(
            rf"^\s*{re.escape(name)}:\s*'(?P<css>[^']*)'",
            renderer_source,
            re.M,
        )
        if not match:
            return {}
        return {
            key.strip(): value.strip()
            for declaration in match.group("css").split(";")
            if ":" in declaration
            for key, value in [declaration.split(":", 1)]
        }

    try:
        heading_1_style = renderer_style("heading1")
        heading_2_style = renderer_style("heading2")
        body_style = renderer_style("body")
        quote_style = renderer_style("quote")
        style_assertions_verified = all(
            (
                heading_1_style.get("font-size")
                == f"{styles['heading_1']['font_size_px']}px",
                heading_1_style.get("color") == styles["heading_1"]["color"],
                heading_1_style.get("line-height")
                == str(styles["heading_1"]["line_height"]),
                heading_2_style.get("font-size")
                == f"{styles['heading_2']['font_size_px']}px",
                heading_2_style.get("color") == styles["heading_2"]["color"],
                heading_2_style.get("line-height")
                == str(styles["heading_2"]["line_height"]),
                body_style.get("font-size") == f"{styles['body']['font_size_px']}px",
                body_style.get("margin")
                == f"0 {styles['body']['horizontal_margin_px']}px 24px",
                body_style.get("line-height") == str(styles["body"]["line_height"]),
                quote_style.get("font-size") == f"{styles['quote']['font_size_px']}px",
                quote_style.get("color") == styles["quote"]["color"],
                quote_style.get("border-left")
                == f"{styles['quote']['left_border_px']}px solid #D9D9D9",
            )
        )
    except (KeyError, TypeError) as exc:
        raise WorkflowError("profile style assertions are invalid") from exc
    if not style_assertions_verified:
        raise WorkflowError("profile style assertions do not match the locked renderer")
    style_version = profile.get("format_source", {}).get("style_version")
    if not isinstance(style_version, str) or style_version not in renderer_source:
        raise WorkflowError("profile style version does not match the locked renderer")

    format_profile_material = {
        key: profile.get(key)
        for key in (
            "schema_version",
            "profile_id",
            "format_source",
            "markdown_contract",
            "style_assertions",
            "runtime_dependencies",
            "source_files",
            "brand_assets",
        )
    }
    format_profile_sha256 = sha256_bytes(canonical_json(format_profile_material))
    verified_by_role = {item["role"]: item for item in verified}
    adapter_sha256 = verified_by_role["markdown_adapter"]["actual_sha256"]
    bridge_sha256 = verified_by_role["renderer_bridge"]["actual_sha256"]
    renderer_sha256 = verified_by_role["renderer_and_semantics"]["actual_sha256"]
    title_image_sha256 = verified_by_role["appso_title"]["actual_sha256"]
    contract_material = {
        "format_profile_sha256": format_profile_sha256,
        "adapter_sha256": adapter_sha256,
        "bridge_sha256": bridge_sha256,
        "verified_files": [
            {"path": item["path"], "sha256": item["actual_sha256"]} for item in verified
        ],
        "runtime_dependencies": actual_dependencies,
    }
    return {
        "format_profile_sha256": format_profile_sha256,
        "format_contract_sha256": sha256_bytes(canonical_json(contract_material)),
        "adapter_sha256": adapter_sha256,
        "bridge_sha256": bridge_sha256,
        "renderer_sha256": renderer_sha256,
        "title_image_sha256": title_image_sha256,
        "style_assertions_verified": True,
        "style_version_verified": True,
        "verified_files": verified,
        "runtime_dependencies": actual_dependencies,
    }


def render_locked_article(
    package: Path,
    repo_root: Path,
    profile: dict[str, Any],
    title: str,
    body: str,
    draft_raw: bytes,
) -> dict[str, Any]:
    blocks, article_image_bytes = markdown_blocks(
        body, package, title, embed_images=True
    )
    appso_asset = unique_profile_entry(
        profile.get("brand_assets"), "id", "appso_title", "brand asset"
    )
    renderer_item = unique_profile_entry(
        profile.get("source_files"),
        "role",
        "renderer_and_semantics",
        "source role",
    )
    bridge_item = unique_profile_entry(
        profile.get("source_files"), "role", "renderer_bridge", "source role"
    )
    title_image_path = resolve_profile_path(
        repo_root, appso_asset.get("path"), "AppSo title image"
    )
    renderer_path = resolve_profile_path(
        repo_root, renderer_item.get("path"), "renderer"
    )
    bridge_path = resolve_profile_path(
        repo_root, bridge_item.get("path"), "renderer bridge"
    )
    title_image_data = title_image_path.read_bytes()
    payload = {
        "title": title,
        "sourceUrl": (package / "draft.md").relative_to(repo_root).as_posix(),
        "blocks": blocks,
        "titleImage": {
            "dataUri": "data:image/gif;base64,"
            + base64.b64encode(title_image_data).decode("ascii"),
            "mime": "image/gif",
            "bytes": len(title_image_data),
            "originalBytes": len(title_image_data),
            "token": "appso-inspiration-guide",
            "sourceName": title_image_path.name,
            "alt": "AppSo 灵感指南",
            "brand": "appso",
            "brandLabel": "AppSo",
        },
        "titleImageSelection": {
            "brand": "appso",
            "preference": "appso",
            "mode": "manual",
            "reason": "locked-company-profile",
            "score": None,
            "signals": [],
        },
        "generatedAt": "1970-01-01T00:00:00.000Z",
        "capture": {
            "source": "local-markdown",
            "parser": "markdown-it-py",
            "profile": profile.get("profile_id"),
        },
    }
    output_dir = package / "dist" / "content-sync"
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_root = output_dir / f".render-{os.getpid()}-{time.time_ns()}"
    temp_root.mkdir()
    try:
        input_path = temp_root / "input.json"
        output_path = temp_root / "output.json"
        html_output_path = temp_root / "article.html"
        input_path.write_bytes(canonical_json(payload))
        process = subprocess.run(
            [
                shutil.which("node") or "node",
                str(bridge_path),
                str(renderer_path),
                str(input_path),
                str(output_path),
                str(html_output_path),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            check=False,
        )
        if process.returncode != 0:
            detail = (process.stderr or process.stdout).strip()[-1000:]
            raise WorkflowError(f"locked renderer failed: {detail}")
        fixture_raw = read_bounded(output_path, 2 * 1024 * 1024)
        try:
            fixture = json.loads(fixture_raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise WorkflowError(
                "locked renderer returned invalid fixture JSON"
            ) from exc
        if not isinstance(fixture, dict):
            raise WorkflowError("locked renderer fixture root must be an object")
        try:
            rendered_html = read_bounded(
                html_output_path, MAX_RENDERED_HTML_BYTES
            ).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise WorkflowError("locked renderer returned non-UTF-8 HTML") from exc
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)
    if not rendered_html:
        raise WorkflowError("locked renderer returned empty HTML")
    html_bytes = rendered_html.encode("utf-8")
    fidelity_blockers: list[str] = []
    if not fixture.get("textFidelity", {}).get("confirmed"):
        fidelity_blockers.append("text_fidelity_failed")
    if not fixture.get("imageFidelity", {}).get("confirmed"):
        fidelity_blockers.append("image_fidelity_failed")
    if fixture.get("mediaWarnings"):
        fidelity_blockers.append("media_warnings_present")
    if fixture.get("contentWarnings"):
        fidelity_blockers.append("content_warnings_present")
    if fixture.get("gifWarnings"):
        fidelity_blockers.append("gif_warnings_present")
    if fixture.get("styleVersion") != profile.get("format_source", {}).get(
        "style_version"
    ):
        fidelity_blockers.append("style_version_mismatch")
    warning_codes = sorted(
        {
            *(
                warning.get("code", "media-warning")
                for warning in fixture.get("mediaWarnings", [])
            ),
            *(
                warning.get("code", "content-warning")
                for warning in fixture.get("contentWarnings", [])
            ),
            *("gif-warning" for _warning in fixture.get("gifWarnings", [])),
        }
    )
    return {
        "title": title,
        "draft_sha256": sha256_bytes(draft_raw),
        "payload_sha256": sha256_bytes(canonical_json(payload)),
        "fixture_sha256": sha256_bytes(canonical_json(fixture)),
        "html_bytes": html_bytes,
        "html_sha256": sha256_bytes(html_bytes),
        "fixture": fixture,
        "article_image_bytes": article_image_bytes,
        "fidelity_blockers": fidelity_blockers,
        "warning_codes": warning_codes,
        "local_format_qualified": not fidelity_blockers,
        "renderer_sha256": sha256_file(renderer_path),
        "bridge_sha256": sha256_file(bridge_path),
        "title_image_sha256": sha256_file(title_image_path),
    }


__all__ = [
    "FRONTMATTER_RE",
    "YAML_KEY_RE",
    "LockedFormatError",
    "MAX_IMAGE_BYTES",
    "MAX_MARKDOWN_BYTES",
    "MAX_RENDERED_HTML_BYTES",
    "MAX_TOTAL_IMAGE_BYTES",
    "SUPPORTED_IMAGE_MIMES",
    "audit_locked_profile",
    "canonical_json",
    "markdown_blocks",
    "parse_scalar",
    "parse_top_level_yaml",
    "read_bounded",
    "read_draft",
    "render_locked_article",
    "safe_image_path",
    "sha256_bytes",
    "sha256_file",
    "unique_profile_entry",
]
