#!/usr/bin/env python3
"""Bridge project content packages to the pinned Wenyan CLI.

Wenyan owns Markdown rendering, image uploads, and WeChat API calls. This file
adapts the project's content-package schema, builds a no-network manual-editor
handoff, and enforces local release gates. ``draft --execute`` is the only
command that can create an external WeChat draft.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import html
import io
import json
import mimetypes
import os
import re
import secrets
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Callable
from urllib.parse import unquote, urlparse

import yaml
from markdown_it import MarkdownIt
from PIL import Image, UnidentifiedImageError
from tinycss2 import parse_declaration_list, serialize


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
THEMES_ROOT = WECHAT_ROOT / "themes"
EDITORIAL_TIMEZONE = timezone(timedelta(hours=8), name="Asia/Shanghai")
MAX_FOOTER_REVIEW_DAYS = 365
MAX_HANDOFF_IMAGE_BYTES = 20 * 1024 * 1024
MAX_HANDOFF_TOTAL_ASSET_BYTES = 60 * 1024 * 1024
MAX_HANDOFF_COPY_HTML_BYTES = 64 * 1024 * 1024
MAX_HANDOFF_CONTENT_HTML_BYTES = 16 * 1024 * 1024
MAX_HANDOFF_DOCUMENT_BYTES = MAX_HANDOFF_COPY_HTML_BYTES + 8 * 1024 * 1024
MAX_HANDOFF_PLAN_BYTES = 2 * 1024 * 1024
MAX_CREDENTIAL_FILE_BYTES = 64 * 1024
MAX_HANDOFF_IMAGE_PIXELS = 40_000_000
MAX_HANDOFF_DECODED_FRAME_PIXELS = 400_000_000
MAX_HANDOFF_IMAGE_FRAMES = 2_000
MAX_HANDOFF_TOTAL_FRAMES = 5_000
MAX_INLINE_IMAGE_REFERENCES = 200
MAX_HANDOFF_OCCURRENCE_FRAMES = 10_000
MAX_HANDOFF_TOTAL_DECODED_FRAME_PIXELS = 800_000_000
MAX_HANDOFF_OCCURRENCE_DECODED_FRAME_PIXELS = 1_200_000_000

FRONTMATTER_RE = re.compile(r"\A---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)\Z", re.S)
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RELEASE_IMAGE_FORMATS = {
    ".gif": "GIF",
    ".jpeg": "JPEG",
    ".jpg": "JPEG",
    ".png": "PNG",
    ".webp": "WEBP",
}
BLOCKED_REMOTE_IMAGE = (
    "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="
)
ACTIVE_HTML_TAGS = {
    "audio",
    "area",
    "base",
    "button",
    "canvas",
    "details",
    "dialog",
    "embed",
    "form",
    "iframe",
    "input",
    "link",
    "map",
    "marquee",
    "meta",
    "object",
    "picture",
    "plaintext",
    "script",
    "select",
    "source",
    "style",
    "summary",
    "svg",
    "template",
    "textarea",
    "track",
    "video",
    "xmp",
    "noscript",
    "font",
    "center",
}
ACTIVE_BEHAVIOR_ATTRIBUTES = {
    "autofocus",
    "contenteditable",
    "download",
    "draggable",
    "hidden",
    "inert",
    "open",
    "popover",
    "spellcheck",
    "tabindex",
}
SCRIPTABLE_URL_ATTRIBUTES = {
    "action",
    "formaction",
    "href",
    "src",
    "srcdoc",
    "xlink:href",
}
ALLOWED_NAVIGATION_SCHEMES = {"http", "https", "mailto", "tel"}
CSS_RESOURCE_FUNCTIONS = {
    "-moz-element",
    "-webkit-cross-fade",
    "-webkit-image-set",
    "cross-fade",
    "element",
    "image",
    "image-set",
    "paint",
    "url",
}
MANUAL_PRESENTATION_TAGS = {"center", "font"}
MANUAL_ALLOWED_TAGS = {
    "a",
    "abbr",
    "article",
    "b",
    "blockquote",
    "br",
    "caption",
    "cite",
    "code",
    "col",
    "colgroup",
    "dd",
    "del",
    "div",
    "dl",
    "dt",
    "em",
    "figcaption",
    "figure",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "i",
    "img",
    "ins",
    "kbd",
    "li",
    "mark",
    "ol",
    "p",
    "pre",
    "q",
    "rp",
    "rt",
    "ruby",
    "s",
    "samp",
    "section",
    "small",
    "span",
    "strong",
    "sub",
    "sup",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "time",
    "tr",
    "u",
    "ul",
    "var",
}
MANUAL_GLOBAL_ATTRIBUTES = {"dir", "lang", "title"}
MANUAL_TAG_ATTRIBUTES = {
    "a": {"href", "id"},
    "blockquote": {"cite"},
    "col": {"span"},
    "colgroup": {"span"},
    "del": {"cite", "datetime"},
    "img": {"alt", "src"},
    "ins": {"cite", "datetime"},
    "li": {"id", "value"},
    "ol": {"start"},
    "p": {"id"},
    "q": {"cite"},
    "sup": {"id"},
    "td": {"colspan", "headers", "rowspan"},
    "th": {"abbr", "colspan", "headers", "rowspan", "scope"},
    "time": {"datetime"},
}
AUTHOR_GLOBAL_ATTRIBUTES = {"lang", "title"}
AUTHOR_TAG_ATTRIBUTES = {
    tag: attributes - {"id"} for tag, attributes in MANUAL_TAG_ATTRIBUTES.items()
}
MANUAL_BLOCKED_BEHAVIOR_ATTRIBUTES = {
    *ACTIVE_BEHAVIOR_ATTRIBUTES,
}
MANUAL_VOID_TAGS = {"br", "col", "hr", "img"}
MARKDOWN_PARSER = MarkdownIt("commonmark", {"html": True})

RELEASE_RIGHTS_STATUSES = {
    "cc0_verified",
    "licensed",
    "project_owned",
    "project_owned_with_cc0_component",
    "public_domain_verified",
    "user_confirmed_editorial_commentary",
    "user_confirmed_editorial_use",
}
WENYAN_NOTES = [
    "Wenyan CLI 2.0.11 does not forward a custom digest to draft/add; WeChat will derive it, so check or edit the digest in the backend.",
    "Wenyan CLI 2.0.11 uploads body images as permanent image materials and caches repeat uploads.",
    "WeChat draft creation is not atomic; after any execute-time failure, inspect the target account and material library before retrying.",
]


class WorkflowError(RuntimeError):
    """A user-actionable workflow failure."""


class UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects ambiguous duplicate mapping keys."""


def construct_unique_mapping(
    loader: UniqueKeySafeLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise WorkflowError(
                f"unhashable YAML mapping key at line {key_node.start_mark.line + 1}"
            ) from exc
        if duplicate:
            raise WorkflowError(
                f"duplicate YAML key {key!r} at line {key_node.start_mark.line + 1}"
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_unique_mapping,
)


@dataclass(frozen=True)
class LayoutProfile:
    profile_id: str
    custom_theme: Path | None = None
    required_header: bool = False
    required_theme: str | None = None
    required_highlight: str | None = None
    required_mac_style: bool | None = None


@dataclass(frozen=True)
class ProjectAdapter:
    adapter_id: str
    supports_body_components: bool = False
    component_class_prefix: str | None = None


@dataclass(frozen=True)
class DeliveryMode:
    mode_id: str
    strip_inline_styles: bool = False
    api_draft_allowed: bool = False
    produces_editor_handoff: bool = False


LAYOUT_PROFILES = {
    "default": LayoutProfile(
        profile_id="default",
        required_theme="default",
        required_highlight="solarized-light",
        required_mac_style=False,
    ),
    "appsso-article-v1": LayoutProfile(
        profile_id="appsso-article-v1",
        custom_theme=WECHAT_ROOT / "themes" / "appsso-article-v1.css",
        required_header=True,
        required_theme="default",
        required_highlight="solarized-light",
        required_mac_style=False,
    ),
}

PROJECT_ADAPTERS = {
    "generic": ProjectAdapter(adapter_id="generic"),
    "appsso": ProjectAdapter(
        adapter_id="appsso",
        supports_body_components=True,
        component_class_prefix="appsso-body",
    ),
}

DELIVERY_MODES = {
    "manual_editor": DeliveryMode(
        mode_id="manual_editor",
        strip_inline_styles=True,
        produces_editor_handoff=True,
    ),
    "sealed_draft": DeliveryMode(
        mode_id="sealed_draft",
        api_draft_allowed=True,
    ),
}
PUBLISH_CONFIG_FIELDS = {
    "author",
    "content_source_url",
    "cover",
    "delivery_mode",
    "digest",
    "footer_alt",
    "footer_image",
    "footer_valid_until",
    "footnote",
    "header_alt",
    "header_image",
    "highlight",
    "layout_profile",
    "mac_style",
    "need_open_comment",
    "only_fans_can_comment",
    "project_adapter",
    "source_url",
    "theme",
    "title",
}


@dataclass(frozen=True)
class PublishConfig:
    title: str
    author: str = ""
    digest: str = ""
    cover: str = ""
    source_url: str = ""
    project_adapter: str = ""
    delivery_mode: str = ""
    theme: str = "default"
    layout_profile: str = "default"
    highlight: str = "solarized-light"
    mac_style: bool = False
    footnote: bool = True
    need_open_comment: bool = False
    only_fans_can_comment: bool = False
    header_image: str = ""
    header_alt: str = ""
    footer_image: str = ""
    footer_alt: str = ""
    footer_valid_until: str = ""


@dataclass(frozen=True)
class BuildSnapshot:
    package_files: dict[str, str]
    package_sha256: str
    staged_files: dict[str, str]
    staged_sha256: str
    source_sha256: str
    theme_snapshot_sha256: str | None
    canonical_theme_sha256: str | None


@dataclass(frozen=True)
class PreviewBuild:
    preview_path: Path
    source: Path
    theme_snapshot: Path | None
    metadata: dict[str, Any]
    config: PublishConfig
    blockers: list[str]
    validator_ok: bool
    validator_report: str
    snapshot: BuildSnapshot
    handoff_path: Path | None = None
    handoff_plan_path: Path | None = None
    handoff_plan_sha256: str | None = None


@dataclass(frozen=True)
class PreparedInlineImage:
    path: str
    payload: bytes
    data_uri: str
    sha256: str
    width: int
    height: int
    pixels_per_frame: int
    frame_count: int
    decoded_frame_pixels: int


@dataclass(frozen=True)
class PreparedImageGraph:
    images: dict[str, PreparedInlineImage]
    image_order: list[str]
    projected_copy_payload_bytes: int
    source_sha256: str
    rendered_fragment: str


class ImageSourceParser(HTMLParser):
    """Extract rendered image sources and reserved APPSO component wrappers."""

    def __init__(self, component_class_prefix: str | None = None) -> None:
        super().__init__(convert_charrefs=True)
        self.sources: list[str] = []
        self.component_counts = {"header": 0, "footer": 0}
        self.component_class_prefix = component_class_prefix

    def inspect(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attribute_map: dict[str, str] = {}
        for name, value in attrs:
            attribute_map.setdefault(name.casefold(), value or "")
        if tag.casefold() == "section" and self.component_class_prefix:
            classes = set(attribute_map.get("class", "").split())
            for kind in self.component_counts:
                if f"{self.component_class_prefix}-{kind}" in classes:
                    self.component_counts[kind] += 1
        if tag.casefold() == "img" and "src" in attribute_map:
            self.sources.append(attribute_map["src"])

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.inspect(tag, attrs)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.inspect(tag, attrs)


class ImageRewriteHtmlParser(HTMLParser):
    """Reserialize HTML while replacing only parsed img src attribute values."""

    def __init__(self, replace_source: Callable[[str], str]) -> None:
        super().__init__(convert_charrefs=False)
        self.replace_source = replace_source
        self.parts: list[str] = []
        self.sources: list[str] = []

    def serialized_start_tag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
        *,
        self_closing: bool,
    ) -> str:
        serialized: list[str] = []
        source_replaced = False
        for name, value in attrs:
            if tag.casefold() == "img" and name.casefold() == "src":
                self.sources.append(value or "")
                value = self.replace_source(value or "")
                source_replaced = True
            if value is None:
                serialized.append(f" {name}")
            else:
                serialized.append(f' {name}="{html.escape(value, quote=True)}"')
        if tag.casefold() == "img" and not source_replaced:
            raise WorkflowError("rendered img has no src attribute during rewrite")
        close = " />" if self_closing else ">"
        return f"<{tag}{''.join(serialized)}{close}"

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.parts.append(
            self.serialized_start_tag(tag, attrs, self_closing=False)
        )

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.parts.append(
            self.serialized_start_tag(tag, attrs, self_closing=True)
        )

    def handle_endtag(self, tag: str) -> None:
        self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.parts.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        self.parts.append(f"<!--{data}-->")

    def handle_decl(self, decl: str) -> None:
        self.parts.append(f"<!{decl}>")

    def handle_pi(self, data: str) -> None:
        self.parts.append(f"<?{data}>")

    def rendered(self) -> str:
        return "".join(self.parts)


class PassiveHtmlParser(HTMLParser):
    """Reject active markup before a rendered fragment enters the local preview."""

    def __init__(
        self, allowed_presentation_tags: set[str] | None = None
    ) -> None:
        super().__init__(convert_charrefs=True)
        self.problems: list[str] = []
        self.open_tags: list[str] = []
        self.allowed_presentation_tags = {
            tag.casefold() for tag in (allowed_presentation_tags or set())
        }
        self.allowed_tags = MANUAL_ALLOWED_TAGS | self.allowed_presentation_tags

    def inspect(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        normalized_tag = tag.casefold()
        if (
            normalized_tag in ACTIVE_HTML_TAGS
            and normalized_tag not in self.allowed_presentation_tags
        ):
            self.problems.append(f"active HTML tag <{normalized_tag}> is not allowed")
        if normalized_tag not in self.allowed_tags:
            self.problems.append(
                f"unsupported article HTML tag <{normalized_tag}> is not allowed"
            )
        normalized_names = [name.casefold() for name, _ in attrs]
        if normalized_tag == "img":
            src_count = normalized_names.count("src")
            if src_count != 1:
                self.problems.append(
                    f"rendered img must contain exactly one src attribute; found {src_count}"
                )
        for raw_name, raw_value in attrs:
            name = raw_name.casefold()
            if name in ACTIVE_BEHAVIOR_ATTRIBUTES:
                self.problems.append(
                    f"interactive or hidden attribute {raw_name} is not allowed"
                )
            if name in {"background", "data-src", "poster", "srcset"}:
                self.problems.append(
                    f"resource-loading attribute {raw_name} is not allowed"
                )
            if name == "src" and normalized_tag != "img":
                self.problems.append(
                    f"resource-loading src on <{normalized_tag}> is not allowed"
                )
            if name.startswith("on"):
                self.problems.append(
                    f"event-handler attribute {raw_name} is not allowed"
                )
            if name == "style" and style_has_resource_reference(raw_value or ""):
                self.problems.append(
                    "resource reference in a rendered style attribute is not allowed"
                )
            if name == "style":
                dangerous = dangerous_style_behavior(raw_value or "")
                if dangerous is not None:
                    self.problems.append(
                        f"dangerous rendered style behavior is not allowed: {dangerous}"
                    )
            if raw_value is None or name not in SCRIPTABLE_URL_ATTRIBUTES:
                continue
            compact_value = re.sub(
                r"[\x00-\x20]+", "", unquote(raw_value)
            ).casefold()
            scheme_match = re.match(r"^([a-z][a-z0-9+.-]*):", compact_value)
            if scheme_match and scheme_match.group(1) not in ALLOWED_NAVIGATION_SCHEMES:
                self.problems.append(
                    f"URL scheme in attribute {raw_name} is not allowed"
                )

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.inspect(tag, attrs)
        normalized = tag.casefold()
        if normalized in self.allowed_tags and normalized not in MANUAL_VOID_TAGS:
            self.open_tags.append(normalized)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.inspect(tag, attrs)
        normalized = tag.casefold()
        if normalized in self.allowed_tags and normalized not in MANUAL_VOID_TAGS:
            self.problems.append(
                f"non-void article tag <{normalized}> must not be self-closing"
            )

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.casefold()
        if normalized not in self.allowed_tags:
            self.problems.append(
                f"unsupported article closing tag </{normalized}> is not allowed"
            )
            return
        if normalized in MANUAL_VOID_TAGS:
            self.problems.append(
                f"void article tag <{normalized}> must not have an end tag"
            )
            return
        if not self.open_tags:
            self.problems.append(f"unmatched article closing tag </{normalized}>")
            return
        expected = self.open_tags[-1]
        if expected != normalized:
            self.problems.append(
                f"misnested article closing tag </{normalized}>; expected </{expected}>"
            )
            return
        self.open_tags.pop()


class AuthorHtmlParser(HTMLParser):
    """Reject author-controlled presentation before adapter/theme rendering."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.inspector = PassiveHtmlParser()
        self.problems: list[str] = []

    def inspect(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.inspector.inspect(tag, attrs)
        normalized_tag = tag.casefold()
        allowed = AUTHOR_GLOBAL_ATTRIBUTES | AUTHOR_TAG_ATTRIBUTES.get(
            normalized_tag, set()
        )
        for name, _ in attrs:
            if name.casefold() not in allowed:
                self.problems.append(
                    f"author-controlled HTML attribute {name} on <{normalized_tag}> is not allowed; use Markdown or the selected layout profile"
                )

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.inspect(tag, attrs)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.inspect(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.casefold()
        if normalized not in MANUAL_ALLOWED_TAGS:
            self.problems.append(
                f"unsupported author HTML closing tag </{normalized}> is not allowed"
            )

    def all_problems(self) -> list[str]:
        return self.inspector.problems + self.problems


class ManualHandoffHtmlParser(HTMLParser):
    """Remove presentation markup while preserving semantic content and attributes."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.parts: list[str] = []
        self.removed_attributes: list[str] = []
        self.removed_tags: list[str] = []
        self.blocked_attributes: list[str] = []
        self.blocked_tags: list[str] = []
        self.open_tags: list[tuple[str, bool]] = []
        self.structural_problems: list[str] = []

    @property
    def removed_style_attributes(self) -> int:
        """Compatibility counter retained for existing checks and callers."""

        return sum(name == "style" for name in self.removed_attributes)

    def filtered_attributes(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> list[tuple[str, str | None]]:
        filtered: list[tuple[str, str | None]] = []
        allowed = MANUAL_GLOBAL_ATTRIBUTES | MANUAL_TAG_ATTRIBUTES.get(tag, set())
        for name, value in attrs:
            normalized = name.casefold()
            if normalized in MANUAL_BLOCKED_BEHAVIOR_ATTRIBUTES:
                self.blocked_attributes.append(normalized)
                continue
            if normalized not in allowed:
                self.removed_attributes.append(normalized)
                continue
            filtered.append((name, value))
        return filtered

    def serialized_start_tag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
        *,
        self_closing: bool,
    ) -> str:
        serialized_attrs: list[str] = []
        for name, value in attrs:
            if value is None:
                serialized_attrs.append(f" {name}")
            else:
                serialized_attrs.append(
                    f' {name}="{html.escape(value, quote=True)}"'
                )
        close = " />" if self_closing else ">"
        return f"<{tag}{''.join(serialized_attrs)}{close}"

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        normalized = tag.casefold()
        filtered = self.filtered_attributes(normalized, attrs)
        if normalized in MANUAL_PRESENTATION_TAGS:
            self.removed_tags.append(normalized)
            self.open_tags.append((normalized, False))
            return
        if normalized not in MANUAL_ALLOWED_TAGS:
            self.blocked_tags.append(normalized)
            return
        if normalized in MANUAL_VOID_TAGS:
            self.parts.append(
                self.serialized_start_tag(tag, filtered, self_closing=False)
            )
            return
        emit = True
        if normalized == "span":
            emit = bool(filtered)
            if not emit:
                self.removed_tags.append(normalized)
        self.open_tags.append((normalized, emit))
        if emit:
            self.parts.append(
                self.serialized_start_tag(tag, filtered, self_closing=False)
            )

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        normalized = tag.casefold()
        filtered = self.filtered_attributes(normalized, attrs)
        if normalized not in MANUAL_VOID_TAGS:
            self.structural_problems.append(
                f"non-void tag <{normalized}> must not be self-closing"
            )
        if normalized in MANUAL_PRESENTATION_TAGS:
            self.removed_tags.append(normalized)
            return
        if normalized not in MANUAL_ALLOWED_TAGS:
            self.blocked_tags.append(normalized)
            return
        if normalized == "span" and not filtered:
            self.removed_tags.append(normalized)
            return
        self.parts.append(self.serialized_start_tag(tag, filtered, self_closing=True))

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.casefold()
        if (
            normalized not in MANUAL_PRESENTATION_TAGS
            and normalized not in MANUAL_ALLOWED_TAGS
        ):
            self.blocked_tags.append(normalized)
            return
        if normalized in MANUAL_VOID_TAGS:
            self.structural_problems.append(
                f"void tag <{normalized}> must not have an end tag"
            )
            return
        if not self.open_tags:
            self.structural_problems.append(
                f"unmatched closing tag </{normalized}>"
            )
            return
        expected, emitted = self.open_tags[-1]
        if expected != normalized:
            self.structural_problems.append(
                f"misnested closing tag </{normalized}>; expected </{expected}>"
            )
            return
        self.open_tags.pop()
        if emitted:
            self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.parts.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        self.parts.append(f"<!--{data}-->")

    def handle_decl(self, decl: str) -> None:
        self.parts.append(f"<!{decl}>")

    def handle_pi(self, data: str) -> None:
        self.parts.append(f"<?{data}>")

    def rendered(self) -> str:
        return "".join(self.parts)


def css_tokens_have_resource(tokens: list[Any]) -> bool:
    for token in tokens:
        token_type = getattr(token, "type", "")
        if token_type in {"error", "url"}:
            return True
        if token_type == "function":
            if getattr(token, "lower_name", "") in CSS_RESOURCE_FUNCTIONS:
                return True
            if css_tokens_have_resource(list(getattr(token, "arguments", []))):
                return True
        content = getattr(token, "content", None)
        if content and css_tokens_have_resource(list(content)):
            return True
    return False


def style_has_resource_reference(style: str) -> bool:
    declarations = parse_declaration_list(
        html.unescape(unquote(style)), skip_comments=True, skip_whitespace=True
    )
    for declaration in declarations:
        if getattr(declaration, "type", "") == "error":
            return True
        if css_tokens_have_resource(list(getattr(declaration, "value", []))):
            return True
    return False


def dangerous_style_behavior(style: str) -> str | None:
    declarations = parse_declaration_list(
        html.unescape(unquote(style)), skip_comments=True, skip_whitespace=True
    )
    for declaration in declarations:
        if getattr(declaration, "type", "") != "declaration":
            continue
        name = str(getattr(declaration, "lower_name", ""))
        value = serialize(list(getattr(declaration, "value", []))).strip().casefold()
        compact = re.sub(r"\s+", "", value)
        if name == "position" and compact in {"fixed", "sticky"}:
            return f"position:{compact}"
        if name == "display" and compact == "none":
            return "display:none"
        if name == "visibility" and compact in {"hidden", "collapse"}:
            return f"visibility:{compact}"
        if name == "content-visibility" and compact == "hidden":
            return "content-visibility:hidden"
        if name in {"pointer-events", "user-select"} and compact == "none":
            return f"{name}:none"
        if name == "opacity" and re.fullmatch(r"(?:0+(?:\.0*)?|\.0+)", compact):
            return "opacity:0"
    return None


def is_link_or_junction(path: Path) -> bool:
    is_junction = getattr(os.path, "isjunction", lambda _: False)
    return path.is_symlink() or bool(is_junction(path))


def is_multiply_linked_file(path: Path) -> bool:
    return path.is_file() and path.stat().st_nlink != 1


def canonical_package_relative_path(
    raw_path: str,
    label: str,
    *,
    require_assets: bool = False,
) -> str:
    decoded = decode_image_target(raw_path).replace("\\", "/")
    parsed = urlparse(decoded)
    if (
        parsed.scheme
        or parsed.netloc
        or parsed.query
        or parsed.fragment
        or decoded.startswith("/")
        or re.match(r"^[A-Za-z]:", decoded)
    ):
        raise WorkflowError(f"{label} must be a package-relative local path")
    parts = PurePosixPath(decoded).parts
    if not parts or any(part in {"", ".", ".."} or ":" in part for part in parts):
        raise WorkflowError(
            f"{label} contains an unsafe path segment; '.', '..', and ':' are not allowed"
        )
    if require_assets and parts[0].casefold() != "assets":
        raise WorkflowError(f"{label} must be stored under the package assets/ directory")
    return PurePosixPath(*parts).as_posix()


def safe_dist(package: Path) -> Path:
    package_resolved = package.resolve()
    dist = package / "dist"
    try:
        dist.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        pass
    if is_link_or_junction(dist):
        raise WorkflowError(f"dist must not be a symlink or junction: {dist}")
    if not dist.is_dir():
        raise WorkflowError(f"dist exists but is not a directory: {dist}")
    try:
        dist.resolve().relative_to(package_resolved)
    except ValueError as exc:
        raise WorkflowError(f"dist escapes the content package: {dist}") from exc
    return dist


def create_build_dir(package: Path) -> Path:
    dist = safe_dist(package)
    builds = dist / "builds"
    try:
        builds.mkdir(exist_ok=False)
    except FileExistsError:
        pass
    if is_link_or_junction(builds) or not builds.is_dir():
        raise WorkflowError(f"dist/builds must be a regular directory: {builds}")
    for _ in range(8):
        candidate = builds / f"build-{secrets.token_hex(12)}"
        try:
            candidate.mkdir(exist_ok=False)
        except FileExistsError:
            continue
        return candidate
    raise WorkflowError("could not allocate a unique Wenyan build directory")


def create_handoff_dir(package: Path) -> Path:
    dist = safe_dist(package)
    handoffs = dist / "handoffs"
    try:
        handoffs.mkdir(exist_ok=False)
    except FileExistsError:
        pass
    if is_link_or_junction(handoffs) or not handoffs.is_dir():
        raise WorkflowError(f"dist/handoffs must be a regular directory: {handoffs}")
    for _ in range(8):
        candidate = handoffs / f"handoff-{secrets.token_hex(12)}"
        try:
            candidate.mkdir(exist_ok=False)
        except FileExistsError:
            continue
        return candidate
    raise WorkflowError("could not allocate a unique editor handoff directory")


def atomic_write_bytes(path: Path, data: bytes) -> None:
    if path.exists() or path.is_symlink():
        if is_link_or_junction(path):
            raise WorkflowError(f"generated output must not be a symlink or junction: {path}")
        if not path.is_file():
            raise WorkflowError(f"generated output is not a regular file: {path}")
    parent = path.parent
    if is_link_or_junction(parent):
        raise WorkflowError(f"generated output parent must not be a link: {parent}")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def atomic_write_text(path: Path, content: str) -> None:
    atomic_write_bytes(path, content.encode("utf-8"))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        before = os.fstat(handle.fileno())
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
        after = os.fstat(handle.fileno())
    fingerprint_before = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
    )
    fingerprint_after = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    )
    if fingerprint_before != fingerprint_after:
        raise WorkflowError(f"file changed while hashing: {path}")
    return digest.hexdigest()


def stable_file_bytes(
    path: Path,
    *,
    expected_size: int | None = None,
    max_bytes: int | None = None,
) -> bytes:
    if is_link_or_junction(path):
        raise WorkflowError(f"input must not be a symlink or junction: {path}")
    for value, label in ((expected_size, "expected size"), (max_bytes, "byte ceiling")):
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool) or value < 0
        ):
            raise WorkflowError(f"invalid {label} for input: {path}")
    if expected_size is not None and max_bytes is not None and expected_size > max_bytes:
        raise WorkflowError(f"input exceeds its byte ceiling: {path}")
    with path.open("rb") as handle:
        before = os.fstat(handle.fileno())
        if before.st_nlink != 1:
            raise WorkflowError(f"input must not be a hardlink: {path}")
        if expected_size is not None and before.st_size != expected_size:
            raise WorkflowError(f"input byte count mismatch: {path}")
        if max_bytes is not None and before.st_size > max_bytes:
            raise WorkflowError(f"input exceeds its byte ceiling: {path}")
        read_ceiling = expected_size if expected_size is not None else max_bytes
        payload = (
            handle.read(read_ceiling + 1)
            if read_ceiling is not None
            else handle.read()
        )
        after = os.fstat(handle.fileno())
    fingerprint_before = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
    )
    fingerprint_after = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    )
    if fingerprint_before != fingerprint_after:
        raise WorkflowError(f"file changed while reading: {path}")
    if len(payload) != after.st_size:
        raise WorkflowError(f"file byte count changed while reading: {path}")
    if read_ceiling is not None and len(payload) > read_ceiling:
        raise WorkflowError(f"input exceeds its byte ceiling: {path}")
    return payload


def stable_copy_file(
    source: Path,
    destination: Path,
    *,
    expected_hash: str | None = None,
    max_bytes: int | None = None,
) -> tuple[int, str]:
    """Copy one regular file in bounded chunks while binding its source identity."""

    if is_link_or_junction(source):
        raise WorkflowError(f"input must not be a symlink or junction: {source}")
    if max_bytes is not None and (
        not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes < 0
    ):
        raise WorkflowError(f"invalid byte ceiling for input: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=destination.parent,
    )
    temporary_path = Path(temporary_name)
    digest = hashlib.sha256()
    total = 0
    destination_installed = False
    try:
        with source.open("rb") as source_handle, os.fdopen(
            descriptor, "wb"
        ) as destination_handle:
            descriptor = -1
            before = os.fstat(source_handle.fileno())
            if before.st_nlink != 1:
                raise WorkflowError(f"input must not be a hardlink: {source}")
            if max_bytes is not None and before.st_size > max_bytes:
                raise WorkflowError(f"input exceeds its byte ceiling: {source}")
            for chunk in iter(lambda: source_handle.read(1024 * 1024), b""):
                total += len(chunk)
                if max_bytes is not None and total > max_bytes:
                    raise WorkflowError(f"input exceeds its byte ceiling: {source}")
                digest.update(chunk)
                destination_handle.write(chunk)
            after = os.fstat(source_handle.fileno())
            destination_handle.flush()
            os.fsync(destination_handle.fileno())
        fingerprint_before = (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
        )
        fingerprint_after = (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        )
        if fingerprint_before != fingerprint_after or total != after.st_size:
            raise WorkflowError(f"file changed while copying: {source}")
        actual_hash = digest.hexdigest()
        if expected_hash is not None and actual_hash != expected_hash:
            raise WorkflowError(f"input hash mismatch while copying: {source}")
        os.replace(temporary_path, destination)
        destination_installed = True
        if file_sha256(destination) != actual_hash:
            raise WorkflowError(f"destination hash mismatch after copying: {destination}")
        return total, actual_hash
    except BaseException:
        if descriptor >= 0:
            os.close(descriptor)
        temporary_path.unlink(missing_ok=True)
        if destination_installed:
            destination.unlink(missing_ok=True)
        raise


def package_input_hashes(package: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(package.rglob("*"), key=lambda item: item.as_posix().casefold()):
        relative = path.relative_to(package)
        if relative.parts and relative.parts[0].casefold() == "dist":
            continue
        if is_link_or_junction(path):
            raise WorkflowError(f"content package input must not be a link: {relative.as_posix()}")
        if path.is_file():
            if is_multiply_linked_file(path):
                raise WorkflowError(
                    f"content package input must not be a hardlink: {relative.as_posix()}"
                )
            hashes[relative.as_posix()] = file_sha256(path)
    return hashes


def build_input_hashes(build_dir: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(build_dir.rglob("*"), key=lambda item: item.as_posix().casefold()):
        relative = path.relative_to(build_dir)
        if is_link_or_junction(path):
            raise WorkflowError(f"staged build input must not be a link: {relative.as_posix()}")
        if path.is_file():
            if is_multiply_linked_file(path):
                raise WorkflowError(
                    f"staged build input must not be a hardlink: {relative.as_posix()}"
                )
            hashes[relative.as_posix()] = file_sha256(path)
    return hashes


@contextmanager
def sealed_package_snapshot(
    package: Path, expected_hashes: dict[str, str]
):
    """Yield a temporary package copy whose bytes match the initial preflight hash."""

    with tempfile.TemporaryDirectory(prefix="wechat-package-snapshot-") as temp_dir:
        snapshot = Path(temp_dir) / "package"
        snapshot.mkdir()
        for relative, expected_hash in expected_hashes.items():
            relative_path = Path(relative)
            if any(part.casefold() == ".env" for part in relative_path.parts):
                continue
            source = package / relative_path
            destination = snapshot / relative_path
            try:
                stable_copy_file(
                    source,
                    destination,
                    expected_hash=expected_hash,
                )
            except WorkflowError as exc:
                raise WorkflowError(
                    f"content package changed while sealing input: {relative}"
                ) from exc
        yield snapshot


@contextmanager
def exclusive_publish_lock(package: Path):
    lock_path = safe_dist(package) / ".wechat-publish.lock"
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise WorkflowError(
            "another WeChat draft operation holds the package publish lock"
        ) from exc
    try:
        os.write(descriptor, f"pid={os.getpid()}\n".encode("ascii"))
        os.fsync(descriptor)
        yield
    finally:
        os.close(descriptor)
        if lock_path.exists():
            lock_path.unlink()


def combined_hash(items: dict[str, str]) -> str:
    payload = json.dumps(items, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def decode_image_target(target: str) -> str:
    clean = html.unescape(target.strip())
    if clean.startswith("<") and clean.endswith(">"):
        clean = clean[1:-1]
    return unquote(clean)


def raw_html_image_sources(fragment: str) -> list[str]:
    parser = ImageSourceParser()
    parser.feed(fragment)
    parser.close()
    return parser.sources


def ensure_author_html_safe(markdown: str) -> None:
    parser = AuthorHtmlParser()

    def inspect_tokens(tokens: list[Any]) -> None:
        for token in tokens:
            if token.type in {"html_block", "html_inline"}:
                parser.feed(token.content)
            if token.children:
                inspect_tokens(token.children)

    inspect_tokens(MARKDOWN_PARSER.parse(markdown))
    parser.close()
    problems = list(dict.fromkeys(parser.all_problems()))
    if problems:
        raise WorkflowError(
            "draft contains author-controlled HTML that is unsafe for a controlled WeChat layout:\n- "
            + "\n- ".join(problems)
        )


def ensure_passive_preview_html(
    fragment: str,
    *,
    allowed_presentation_tags: set[str] | None = None,
) -> None:
    parser = PassiveHtmlParser(allowed_presentation_tags)
    parser.feed(fragment)
    parser.close()
    parser.problems.extend(
        f"unclosed article tag <{tag}>" for tag in reversed(parser.open_tags)
    )
    if parser.problems:
        unique = list(dict.fromkeys(parser.problems))
        raise WorkflowError(
            "rendered content contains active HTML that is unsafe for local preview:\n- "
            + "\n- ".join(unique)
        )


def image_file_problem(path: Path) -> str | None:
    expected_format = RELEASE_IMAGE_FORMATS.get(path.suffix.casefold())
    if expected_format is None:
        allowed = ", ".join(sorted(RELEASE_IMAGE_FORMATS))
        return f"unsupported image extension {path.suffix or '(none)'}; allowed: {allowed}"
    try:
        with Image.open(path) as image:
            actual_format = image.format
            width, height = image.size
            image.verify()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        return f"image cannot be decoded: {type(exc).__name__}"
    if actual_format != expected_format:
        return f"image format {actual_format or 'unknown'} does not match {path.suffix}"
    if width <= 0 or height <= 0:
        return "image dimensions must be positive"
    return None


def parse_yaml_mapping(payload: str, label: str) -> dict[str, Any]:
    try:
        loaded = yaml.load(payload, Loader=UniqueKeySafeLoader)
    except WorkflowError as exc:
        raise WorkflowError(f"invalid YAML in {label}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise WorkflowError(f"invalid YAML in {label}: {exc}") from exc
    if loaded is None:
        if payload.strip():
            raise WorkflowError(f"YAML root must be an object: {label}")
        loaded = {}
    if not isinstance(loaded, dict):
        raise WorkflowError(f"YAML root must be an object: {label}")
    return loaded


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return parse_yaml_mapping(path.read_text(encoding="utf-8"), str(path))


def load_draft(package: Path) -> tuple[dict[str, Any], str]:
    path = package / "draft.md"
    if not path.is_file():
        raise WorkflowError(f"draft not found: {path}")
    match = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if not match:
        raise WorkflowError(f"draft frontmatter is missing or malformed: {path}")
    metadata = parse_yaml_mapping(match.group(1), f"{path} frontmatter")
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
    non_string_fields = [repr(key) for key in raw if type(key) is not str]
    if non_string_fields:
        raise WorkflowError(
            "publish.yml field names must be YAML strings: "
            + ", ".join(non_string_fields)
        )
    unknown_fields = sorted(set(raw) - PUBLISH_CONFIG_FIELDS)
    if unknown_fields:
        raise WorkflowError(
            "publish.yml contains unknown field(s): " + ", ".join(unknown_fields)
        )
    if "source_url" in raw and "content_source_url" in raw:
        raise WorkflowError(
            "publish.yml must not declare both source_url and content_source_url"
        )

    def strict_string(field: str, default: str = "") -> str:
        if field not in raw:
            return default
        value = raw[field]
        if type(value) is not str:
            raise WorkflowError(
                f"publish.yml field {field} must be a YAML string, not {type(value).__name__}"
            )
        return value.strip()

    source_url_field = (
        "source_url" if "source_url" in raw else "content_source_url"
    )
    source_url = strict_string(source_url_field) if source_url_field in raw else ""
    publish_title = strict_string("title")
    if not publish_title:
        metadata_title = metadata.get("title") or ""
        if type(metadata_title) is not str:
            raise WorkflowError("draft frontmatter title must be a YAML string")
        publish_title = metadata_title.strip()

    def strict_bool(field: str, default: bool) -> bool:
        if field not in raw:
            return default
        value = raw[field]
        if type(value) is not bool:
            raise WorkflowError(
                f"publish.yml field {field} must be a YAML boolean, not {type(value).__name__}"
            )
        return value

    return PublishConfig(
        title=publish_title,
        author=strict_string("author"),
        digest=strict_string("digest"),
        cover=strict_string("cover"),
        source_url=source_url,
        project_adapter=strict_string("project_adapter"),
        delivery_mode=strict_string("delivery_mode"),
        theme=strict_string("theme", "default"),
        layout_profile=strict_string("layout_profile", "default"),
        highlight=strict_string("highlight", "solarized-light"),
        mac_style=strict_bool("mac_style", False),
        footnote=strict_bool("footnote", True),
        need_open_comment=strict_bool("need_open_comment", False),
        only_fans_can_comment=strict_bool("only_fans_can_comment", False),
        header_image=strict_string("header_image"),
        header_alt=strict_string("header_alt"),
        footer_image=strict_string("footer_image"),
        footer_alt=strict_string("footer_alt"),
        footer_valid_until=strict_string("footer_valid_until"),
    )


def get_project_adapter(config: PublishConfig) -> ProjectAdapter | None:
    if not config.project_adapter:
        return None
    adapter = PROJECT_ADAPTERS.get(config.project_adapter)
    if adapter is None:
        choices = ", ".join(sorted(PROJECT_ADAPTERS))
        raise WorkflowError(
            f"unknown project_adapter {config.project_adapter!r}; choose one of: {choices}"
        )
    return adapter


def get_delivery_mode(
    config: PublishConfig, *, require_explicit: bool = False
) -> DeliveryMode | None:
    if not config.delivery_mode:
        if require_explicit:
            choices = ", ".join(sorted(DELIVERY_MODES))
            raise WorkflowError(
                "publish.yml must explicitly set delivery_mode before handoff or draft; "
                f"choose one of: {choices}"
            )
        return None
    mode = DELIVERY_MODES.get(config.delivery_mode)
    if mode is None:
        choices = ", ".join(sorted(DELIVERY_MODES))
        raise WorkflowError(
            f"unknown delivery_mode {config.delivery_mode!r}; choose one of: {choices}"
        )
    return mode


def get_layout_profile(config: PublishConfig) -> LayoutProfile:
    profile = LAYOUT_PROFILES.get(config.layout_profile)
    if profile is None:
        choices = ", ".join(sorted(LAYOUT_PROFILES))
        raise WorkflowError(
            f"unknown layout_profile {config.layout_profile!r}; choose one of: {choices}"
        )
    if profile.custom_theme is not None:
        if is_link_or_junction(profile.custom_theme):
            raise WorkflowError(
                f"layout theme must not be a symlink or junction: {profile.custom_theme}"
            )
        if not profile.custom_theme.is_file():
            raise WorkflowError(
                f"layout theme is missing for {profile.profile_id}: {profile.custom_theme}"
            )
        try:
            profile.custom_theme.resolve().relative_to(THEMES_ROOT.resolve())
        except ValueError as exc:
            raise WorkflowError(
                f"layout theme escapes the allowlisted themes directory: {profile.custom_theme}"
            ) from exc
    return profile


def is_remote_or_special(target: str) -> bool:
    parsed = urlparse(target)
    return bool(parsed.scheme) or target.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:[\\/]", target) is not None


def resolve_layout_asset(package: Path, raw_path: str, field: str) -> Path:
    normalized = canonical_package_relative_path(
        raw_path, field, require_assets=True
    )
    resolved = (package / normalized).resolve()
    try:
        resolved.relative_to(package.resolve())
    except ValueError as exc:
        raise WorkflowError(f"{field} path escapes the content package") from exc
    if not resolved.is_file():
        raise WorkflowError(f"{field} does not exist: {raw_path}")
    if is_link_or_junction(resolved) or is_multiply_linked_file(resolved):
        raise WorkflowError(f"{field} must not be a symlink, junction, or hardlink")
    problem = image_file_problem(resolved)
    if problem is not None:
        raise WorkflowError(f"{field} is not a valid release image: {problem}")
    return resolved


def layout_image_section(
    package: Path,
    raw_path: str,
    alt: str,
    kind: str,
    class_prefix: str,
) -> str:
    field = f"{kind}_image"
    resolve_layout_asset(package, raw_path, field)
    target = html.escape(
        canonical_package_relative_path(raw_path, field, require_assets=True),
        quote=True,
    )
    escaped_alt = html.escape(alt, quote=True)
    return (
        f'<section class="{class_prefix}-{kind}">'
        f'<img src="{target}" alt="{escaped_alt}">'
        "</section>"
    )


def apply_layout_components(package: Path, body: str, config: PublishConfig) -> str:
    get_layout_profile(config)
    adapter = get_project_adapter(config)
    if (
        config.header_image or config.footer_image
    ) and (adapter is None or not adapter.supports_body_components):
        raise WorkflowError(
            "header_image and footer_image require a project_adapter that supports body components"
        )
    class_prefix = adapter.component_class_prefix if adapter is not None else None
    if adapter is not None and adapter.supports_body_components and not class_prefix:
        raise WorkflowError(
            f"project_adapter {adapter.adapter_id} has no component class prefix"
        )
    parts: list[str] = []
    if config.header_image:
        parts.append(
            layout_image_section(
                package,
                config.header_image,
                config.header_alt,
                "header",
                class_prefix or "",
            )
        )
    parts.append(body.strip())
    if config.footer_image:
        parts.append(
            layout_image_section(
                package,
                config.footer_image,
                config.footer_alt,
                "footer",
                class_prefix or "",
            )
        )
    return "\n\n".join(parts).strip() + "\n"


def generated_frontmatter(config: PublishConfig) -> dict[str, Any]:
    frontmatter: dict[str, Any] = {"title": config.title}
    for key, value in (
        ("cover", config.cover),
        ("author", config.author),
        ("source_url", config.source_url),
    ):
        if value:
            frontmatter[key] = value
    frontmatter["need_open_comment"] = config.need_open_comment
    frontmatter["only_fans_can_comment"] = config.only_fans_can_comment
    return frontmatter


def prepare_source(
    package: Path, build_dir: Path | None = None
) -> tuple[Path, dict[str, Any], PublishConfig, str]:
    metadata, body = load_draft(package)
    config = load_publish_config(package, metadata)
    ensure_author_html_safe(body)
    stripped_body = strip_leading_h1(body)
    layout_body = apply_layout_components(package, stripped_body, config)
    frontmatter = yaml.safe_dump(
        generated_frontmatter(config),
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    ).strip()
    selected_build_dir = build_dir or create_build_dir(package)
    source_path = selected_build_dir / "wenyan-source.md"
    atomic_write_text(source_path, f"---\n{frontmatter}\n---\n\n{layout_body}")
    return source_path, metadata, config, layout_body


def stage_layout_theme(dist: Path, config: PublishConfig) -> Path | None:
    profile = get_layout_profile(config)
    if profile.custom_theme is None:
        return None
    snapshot = dist / "layout-theme.css"
    atomic_write_bytes(snapshot, profile.custom_theme.read_bytes())
    return snapshot


def wenyan_args(
    command: str,
    source: Path,
    config: PublishConfig,
    custom_theme_path: Path | None = None,
) -> list[str]:
    if not WENYAN_CMD.is_file():
        raise WorkflowError(
            "Wenyan is not installed. Run `npm.cmd install` inside 微信公众号 first."
        )
    profile = get_layout_profile(config)
    args = [str(WENYAN_CMD), command, "-f", str(source), "-t", config.theme, "-h", config.highlight]
    selected_theme = custom_theme_path or profile.custom_theme
    if selected_theme is not None:
        if is_link_or_junction(selected_theme) or not selected_theme.is_file():
            raise WorkflowError(f"selected custom theme is not a regular file: {selected_theme}")
        args.extend(["--custom-theme", str(selected_theme.resolve())])
    args.append("--mac-style" if config.mac_style else "--no-mac-style")
    args.append("--footnote" if config.footnote else "--no-footnote")
    return args


def wenyan_environment() -> dict[str, str]:
    """Keep caches local and make the explicit env file the credential source."""
    blocked = {
        "wechat_app_id",
        "wechat_app_secret",
        "node_options",
        "node_path",
    }
    environment = {
        key: value
        for key, value in os.environ.items()
        if key.casefold() not in blocked
    }
    environment["XDG_CONFIG_HOME"] = str(WENYAN_RUNTIME)
    return environment


def wechat_credential_metadata(env_path: Path) -> tuple[str, str]:
    """Validate the explicit env file and return non-secret identity metadata."""

    payload = stable_file_bytes(env_path, max_bytes=MAX_CREDENTIAL_FILE_BYTES)
    try:
        content = payload.decode("utf-8-sig")
    except UnicodeError as exc:
        raise WorkflowError("credential file must be UTF-8") from exc
    values: dict[str, str] = {}
    required = {"WECHAT_APP_ID", "WECHAT_APP_SECRET"}
    for line_number, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        key = key.strip()
        if key not in required:
            continue
        if key in values:
            raise WorkflowError(
                f"credential file contains duplicate {key} at line {line_number}"
            )
        value = raw_value.strip()
        if value.startswith(("'", '"')):
            quote = value[0]
            if len(value) < 2 or not value.endswith(quote):
                raise WorkflowError(
                    f"credential file contains an unterminated quoted {key}"
                )
            value = value[1:-1]
        elif " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        if not value or any(character in value for character in "\r\n\x00"):
            raise WorkflowError(f"credential file contains an invalid {key}")
        values[key] = value
    missing = sorted(required - values.keys())
    if missing:
        raise WorkflowError(
            "credential file must explicitly define " + " and ".join(missing)
        )
    account_fingerprint = hashlib.sha256(
        values["WECHAT_APP_ID"].encode("utf-8")
    ).hexdigest()[:12]
    return account_fingerprint, hashlib.sha256(payload).hexdigest()


def run_wenyan_render(
    source: Path, config: PublishConfig, custom_theme_path: Path | None = None
) -> str:
    result = subprocess.run(
        wenyan_args("render", source, config, custom_theme_path),
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


def strip_inline_style_attributes(rendered: str) -> str:
    """Remove presentation markup; prose containing ``style=`` is unchanged."""

    parser = ManualHandoffHtmlParser()
    parser.feed(rendered)
    parser.close()
    if parser.structural_problems or parser.open_tags:
        structure = list(parser.structural_problems)
        structure.extend(
            f"unclosed tag <{tag}>" for tag, _ in reversed(parser.open_tags)
        )
        raise WorkflowError(
            "manual editor handoff contains invalid HTML structure: "
            + "; ".join(dict.fromkeys(structure))
        )
    if parser.blocked_tags or parser.blocked_attributes:
        blocked = sorted(
            set(parser.blocked_tags + parser.blocked_attributes)
        )
        raise WorkflowError(
            "manual editor handoff contains unsupported interactive or hidden markup: "
            + ", ".join(blocked)
        )
    cleaned = parser.rendered()
    verifier = ManualHandoffHtmlParser()
    verifier.feed(cleaned)
    verifier.close()
    if (
        verifier.removed_attributes
        or verifier.removed_tags
        or verifier.blocked_attributes
        or verifier.blocked_tags
        or verifier.structural_problems
        or verifier.open_tags
    ):
        leftovers = sorted(
            set(
                verifier.removed_attributes
                + verifier.removed_tags
                + verifier.blocked_attributes
                + verifier.blocked_tags
                + verifier.structural_problems
                + [tag for tag, _ in verifier.open_tags]
            )
        )
        raise WorkflowError(
            "manual editor handoff still contains presentation markup: "
            + ", ".join(leftovers)
        )
    return cleaned


def apply_delivery_mode(rendered: str, config: PublishConfig) -> str:
    """Adapt rendered HTML for its delivery mode without changing semantic content."""

    mode = get_delivery_mode(config)
    if mode is not None and mode.strip_inline_styles:
        return strip_inline_style_attributes(rendered)
    return rendered


def image_payload_metadata(
    path: Path,
    payload: bytes,
    *,
    frame_ceiling: int | None = None,
    decoded_pixel_ceiling: int | None = None,
) -> dict[str, int | str]:
    expected_format = RELEASE_IMAGE_FORMATS.get(path.suffix.casefold())
    if expected_format is None:
        raise WorkflowError(f"unsupported inline image extension: {path.suffix}")
    allowed_frames = (
        MAX_HANDOFF_IMAGE_FRAMES if frame_ceiling is None else frame_ceiling
    )
    allowed_decoded_pixels = (
        MAX_HANDOFF_DECODED_FRAME_PIXELS
        if decoded_pixel_ceiling is None
        else decoded_pixel_ceiling
    )
    try:
        with Image.open(io.BytesIO(payload)) as image:
            actual_format = image.format
            width, height = image.size
            image.verify()
        if actual_format != expected_format:
            raise WorkflowError(
                f"inline image format {actual_format or 'unknown'} does not match {path.suffix}"
            )
        pixels_per_frame = width * height
        if width <= 0 or height <= 0:
            raise WorkflowError("inline image dimensions must be positive")
        if pixels_per_frame > MAX_HANDOFF_IMAGE_PIXELS:
            raise WorkflowError(
                f"inline image exceeds the internal {MAX_HANDOFF_IMAGE_PIXELS}-pixel ceiling: {path}"
            )
        effective_frame_ceiling = min(
            allowed_frames,
            allowed_decoded_pixels // pixels_per_frame,
        )
        if effective_frame_ceiling < 1:
            raise WorkflowError(
                f"inline image exceeds the remaining frame or decoded-pixel budget: {path}"
            )
        with Image.open(io.BytesIO(payload)) as image:
            frame_count = 1
            while frame_count <= effective_frame_ceiling:
                try:
                    image.seek(frame_count)
                except EOFError:
                    break
                frame_count += 1
        if frame_count > effective_frame_ceiling:
            raise WorkflowError(
                f"inline image exceeds the internal frame or decoded-pixel ceiling: {path}"
            )
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise WorkflowError(
            f"inline image cannot be decoded ({path.name}): {type(exc).__name__}"
        ) from exc
    return {
        "width": width,
        "height": height,
        "pixels_per_frame": pixels_per_frame,
        "frame_count": frame_count,
        "decoded_frame_pixels": pixels_per_frame * frame_count,
    }


def handoff_resource_blockers(
    assets: dict[str, dict[str, Any]], copy_payload_bytes: int
) -> list[str]:
    """Apply internal safety ceilings before allocating inline image payloads."""

    blockers: list[str] = []
    total_asset_bytes = sum(int(item["bytes"]) for item in assets.values())
    total_frames = sum(int(item.get("frame_count", 1)) for item in assets.values())
    image_references = sum(int(item.get("occurrences", 1)) for item in assets.values())
    occurrence_frames = sum(
        int(item.get("frame_count", 1)) * int(item.get("occurrences", 1))
        for item in assets.values()
    )
    total_decoded_pixels = sum(
        int(
            item.get(
                "decoded_frame_pixels",
                int(item["pixels_per_frame"]) * int(item.get("frame_count", 1)),
            )
        )
        for item in assets.values()
    )
    occurrence_decoded_pixels = sum(
        int(
            item.get(
                "decoded_frame_pixels",
                int(item["pixels_per_frame"]) * int(item.get("frame_count", 1)),
            )
        )
        * int(item.get("occurrences", 1))
        for item in assets.values()
    )
    if total_asset_bytes > MAX_HANDOFF_TOTAL_ASSET_BYTES:
        blockers.append(
            "inline image bytes exceed the internal "
            f"{MAX_HANDOFF_TOTAL_ASSET_BYTES}-byte ceiling"
        )
    if copy_payload_bytes > MAX_HANDOFF_COPY_HTML_BYTES:
        blockers.append(
            "inline HTML payload exceeds the internal "
            f"{MAX_HANDOFF_COPY_HTML_BYTES}-byte ceiling"
        )
    if total_frames > MAX_HANDOFF_TOTAL_FRAMES:
        blockers.append(
            "inline image frames exceed the internal "
            f"{MAX_HANDOFF_TOTAL_FRAMES}-frame aggregate ceiling"
        )
    if image_references > MAX_INLINE_IMAGE_REFERENCES:
        blockers.append(
            "inline image references exceed the internal "
            f"{MAX_INLINE_IMAGE_REFERENCES}-reference ceiling"
        )
    if occurrence_frames > MAX_HANDOFF_OCCURRENCE_FRAMES:
        blockers.append(
            "inline image occurrences exceed the internal "
            f"{MAX_HANDOFF_OCCURRENCE_FRAMES}-frame ceiling"
        )
    if total_decoded_pixels > MAX_HANDOFF_TOTAL_DECODED_FRAME_PIXELS:
        blockers.append(
            "inline images exceed the internal "
            f"{MAX_HANDOFF_TOTAL_DECODED_FRAME_PIXELS}-decoded-pixel aggregate ceiling"
        )
    if occurrence_decoded_pixels > MAX_HANDOFF_OCCURRENCE_DECODED_FRAME_PIXELS:
        blockers.append(
            "inline image occurrences exceed the internal "
            f"{MAX_HANDOFF_OCCURRENCE_DECODED_FRAME_PIXELS}-decoded-pixel ceiling"
        )
    for path, item in assets.items():
        if int(item["bytes"]) > MAX_HANDOFF_IMAGE_BYTES:
            blockers.append(
                f"inline image exceeds the internal {MAX_HANDOFF_IMAGE_BYTES}-byte ceiling: {path}"
            )
        if int(item["pixels_per_frame"]) > MAX_HANDOFF_IMAGE_PIXELS:
            blockers.append(
                f"inline image exceeds the internal {MAX_HANDOFF_IMAGE_PIXELS}-pixel ceiling: {path}"
            )
        frame_count = int(item.get("frame_count", 1))
        if frame_count > MAX_HANDOFF_IMAGE_FRAMES:
            blockers.append(
                f"inline image exceeds the internal {MAX_HANDOFF_IMAGE_FRAMES}-frame ceiling: {path}"
            )
        decoded_frame_pixels = int(
            item.get(
                "decoded_frame_pixels",
                int(item["pixels_per_frame"]) * frame_count,
            )
        )
        if decoded_frame_pixels > MAX_HANDOFF_DECODED_FRAME_PIXELS:
            blockers.append(
                "inline animation exceeds the internal "
                f"{MAX_HANDOFF_DECODED_FRAME_PIXELS}-decoded-pixel ceiling: {path}"
            )
    return blockers


def prepare_inline_image_graph(
    fragment: str, image_base: Path
) -> PreparedImageGraph:
    """Validate budgets, then encode each unique local image exactly once."""

    source_parser = ImageSourceParser()
    source_parser.feed(fragment)
    source_parser.close()
    image_order: list[str] = []
    unique_targets: dict[str, str] = {}
    raw_images: dict[str, tuple[Path, bytes, dict[str, int | str]]] = {}
    image_base_resolved = image_base.resolve()
    for raw_target in source_parser.sources:
        target = decode_image_target(raw_target)
        if target.startswith("data:") or is_remote_or_special(target):
            continue
        normalized = canonical_package_relative_path(
            target, "rendered inline image", require_assets=True
        )
        image_order.append(normalized)
        unique_targets.setdefault(normalized, target)

    occurrence_counts = {
        normalized: image_order.count(normalized) for normalized in unique_targets
    }
    running_asset_bytes = 0
    running_frames = 0
    running_occurrence_frames = 0
    running_decoded_pixels = 0
    running_occurrence_decoded_pixels = 0
    for normalized, target in unique_targets.items():
        resolved = (image_base / Path(normalized)).resolve()
        try:
            resolved.relative_to(image_base_resolved)
        except ValueError as exc:
            raise WorkflowError(
                f"rendered image path escapes staged build: {target}"
            ) from exc
        if not resolved.is_file():
            raise WorkflowError(f"rendered local image is missing: {target}")
        remaining_asset_bytes = max(
            0, MAX_HANDOFF_TOTAL_ASSET_BYTES - running_asset_bytes
        )
        read_ceiling = min(MAX_HANDOFF_IMAGE_BYTES, remaining_asset_bytes)
        try:
            payload = stable_file_bytes(resolved, max_bytes=read_ceiling)
        except WorkflowError as exc:
            raise WorkflowError(
                "inline image resource preflight failed before encoding or handoff copy:\n- "
                f"{exc}"
            ) from exc
        occurrences = occurrence_counts[normalized]
        remaining_frames = max(0, MAX_HANDOFF_TOTAL_FRAMES - running_frames)
        remaining_occurrence_frames = max(
            0, MAX_HANDOFF_OCCURRENCE_FRAMES - running_occurrence_frames
        )
        frame_ceiling = min(
            MAX_HANDOFF_IMAGE_FRAMES,
            remaining_frames,
            remaining_occurrence_frames // occurrences,
        )
        remaining_decoded_pixels = max(
            0,
            MAX_HANDOFF_TOTAL_DECODED_FRAME_PIXELS - running_decoded_pixels,
        )
        remaining_occurrence_decoded_pixels = max(
            0,
            MAX_HANDOFF_OCCURRENCE_DECODED_FRAME_PIXELS
            - running_occurrence_decoded_pixels,
        )
        decoded_pixel_ceiling = min(
            MAX_HANDOFF_DECODED_FRAME_PIXELS,
            remaining_decoded_pixels,
            remaining_occurrence_decoded_pixels // occurrences,
        )
        metadata = image_payload_metadata(
            resolved,
            payload,
            frame_ceiling=frame_ceiling,
            decoded_pixel_ceiling=decoded_pixel_ceiling,
        )
        raw_images[normalized] = (
            resolved,
            payload,
            metadata,
        )
        running_asset_bytes += len(payload)
        running_frames += int(metadata["frame_count"])
        running_occurrence_frames += int(metadata["frame_count"]) * occurrences
        running_decoded_pixels += int(metadata["decoded_frame_pixels"])
        running_occurrence_decoded_pixels += (
            int(metadata["decoded_frame_pixels"]) * occurrences
        )

    asset_details: dict[str, dict[str, Any]] = {}
    for normalized, (_, payload, metadata) in raw_images.items():
        asset_details[normalized] = {
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
            **metadata,
            "occurrences": occurrence_counts[normalized],
        }

    projected_upper_bound = len(fragment.encode("utf-8")) * 6
    for raw_target in source_parser.sources:
        target = decode_image_target(raw_target)
        if target.startswith("data:"):
            continue
        if is_remote_or_special(target):
            replacement_length = len(BLOCKED_REMOTE_IMAGE)
        else:
            normalized = canonical_package_relative_path(
                target, "rendered inline image", require_assets=True
            )
            resolved, payload, _ = raw_images[normalized]
            mime = mimetypes.guess_type(resolved.name)[0] or "application/octet-stream"
            replacement_length = len(f"data:{mime};base64,") + 4 * (
                (len(payload) + 2) // 3
            )
        projected_upper_bound += replacement_length

    blockers = handoff_resource_blockers(asset_details, projected_upper_bound)
    if blockers:
        raise WorkflowError(
            "inline image resource preflight failed before encoding or handoff copy:\n- "
            + "\n- ".join(blockers)
        )

    prepared: dict[str, PreparedInlineImage] = {}
    for normalized, (resolved, payload, metadata) in raw_images.items():
        mime = mimetypes.guess_type(resolved.name)[0] or "application/octet-stream"
        encoded = base64.b64encode(payload).decode("ascii")
        prepared[normalized] = PreparedInlineImage(
            path=normalized,
            payload=payload,
            data_uri=f"data:{mime};base64,{encoded}",
            sha256=hashlib.sha256(payload).hexdigest(),
            width=int(metadata["width"]),
            height=int(metadata["height"]),
            pixels_per_frame=int(metadata["pixels_per_frame"]),
            frame_count=int(metadata["frame_count"]),
            decoded_frame_pixels=int(metadata["decoded_frame_pixels"]),
        )
    rewritten_order: list[str] = []

    def replace_source(raw_target: str) -> str:
        target = decode_image_target(raw_target)
        if target.startswith("data:"):
            return raw_target
        if is_remote_or_special(target):
            return BLOCKED_REMOTE_IMAGE
        normalized = canonical_package_relative_path(
            target, "rendered inline image", require_assets=True
        )
        rewritten_order.append(normalized)
        image = prepared.get(normalized)
        if image is None:
            raise WorkflowError(
                f"rendered inline image was not bound by resource preflight: {target}"
            )
        return image.data_uri

    rewriter = ImageRewriteHtmlParser(replace_source)
    rewriter.feed(fragment)
    rewriter.close()
    rendered_fragment = rewriter.rendered()
    if rewriter.sources != source_parser.sources or rewritten_order != image_order:
        raise WorkflowError(
            "parsed image order changed while preparing the inline preview"
        )
    actual_bytes = len(rendered_fragment.encode("utf-8"))
    actual_blockers = handoff_resource_blockers(asset_details, actual_bytes)
    if actual_blockers:
        raise WorkflowError(
            "inline image resource preflight changed after HTML rewrite:\n- "
            + "\n- ".join(actual_blockers)
        )
    return PreparedImageGraph(
        images=prepared,
        image_order=image_order,
        projected_copy_payload_bytes=actual_bytes,
        source_sha256=hashlib.sha256(fragment.encode("utf-8")).hexdigest(),
        rendered_fragment=rendered_fragment,
    )


def inline_preview_images(
    fragment: str,
    image_base: Path,
    prepared_graph: PreparedImageGraph | None = None,
) -> str:
    graph = prepared_graph or prepare_inline_image_graph(fragment, image_base)
    if hashlib.sha256(fragment.encode("utf-8")).hexdigest() != graph.source_sha256:
        raise WorkflowError(
            "rendered HTML changed after inline image resource preflight"
        )
    if len(graph.rendered_fragment.encode("utf-8")) != graph.projected_copy_payload_bytes:
        raise WorkflowError("inline image payload size no longer matches its graph")
    return graph.rendered_fragment


def copy_handoff_images(
    graph: PreparedImageGraph, handoff_dir: Path
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Copy every local body image beside the versioned handoff source."""

    copied: dict[str, dict[str, Any]] = {}
    for normalized, prepared in graph.images.items():
        destination = handoff_dir / Path(normalized)
        destination.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_bytes(destination, prepared.payload)
        if hashlib.sha256(stable_file_bytes(destination)).hexdigest() != prepared.sha256:
            raise WorkflowError(f"handoff image copy hash mismatch: {normalized}")
        copied[normalized] = {
            "sha256": prepared.sha256,
            "bytes": len(prepared.payload),
            "width": prepared.width,
            "height": prepared.height,
            "pixels_per_frame": prepared.pixels_per_frame,
            "frame_count": prepared.frame_count,
            "decoded_frame_pixels": prepared.decoded_frame_pixels,
            "occurrences": graph.image_order.count(normalized),
        }
    return copied, list(graph.image_order)


def stage_asset_bytes(
    source: Path,
    build_dir: Path,
    relative_path: str,
    *,
    max_bytes: int | None = None,
) -> int:
    if is_link_or_junction(source) or is_multiply_linked_file(source):
        raise WorkflowError(
            f"release asset must not be a symlink, junction, or hardlink: {relative_path}"
        )
    destination = build_dir / Path(relative_path)
    try:
        destination.resolve().relative_to(build_dir.resolve())
    except ValueError as exc:
        raise WorkflowError(f"staged asset path escapes build: {relative_path}") from exc
    byte_ceiling = MAX_HANDOFF_IMAGE_BYTES if max_bytes is None else max_bytes
    try:
        copied_bytes, _ = stable_copy_file(
            source,
            destination,
            max_bytes=byte_ceiling,
        )
    except WorkflowError as exc:
        raise WorkflowError(
            f"release asset staging failed for {relative_path}: {exc}"
        ) from exc
    return copied_bytes


def rendered_image_gate_and_stage(
    package: Path,
    build_dir: Path,
    rendered: str,
    config: PublishConfig,
) -> list[str]:
    """Audit the actual Wenyan image graph, then copy approved inputs to this build."""

    blockers: list[str] = []
    adapter = get_project_adapter(config)
    component_prefix = (
        adapter.component_class_prefix if adapter is not None else None
    )
    rendered_parser = ImageSourceParser(component_prefix)
    rendered_parser.feed(rendered)
    rendered_parser.close()
    manifest = load_yaml(package / "asset-manifest.yml")
    raw_assets = manifest.get("assets") or []
    assets = [item for item in raw_assets if isinstance(item, dict)]
    manifest_by_path: dict[str, dict[str, Any]] = {}
    for entry in assets:
        raw_file = str(entry.get("file") or "").strip()
        if not raw_file:
            continue
        try:
            normalized = canonical_package_relative_path(
                raw_file, "manifest asset", require_assets=True
            )
        except WorkflowError:
            continue
        manifest_by_path.setdefault(normalized, entry)

    component_uses: dict[str, str] = {}
    for raw_path, expected_use, label in (
        (config.header_image, "wechat_body_header", "header_image"),
        (config.footer_image, "wechat_body_footer", "footer_image"),
    ):
        if not raw_path:
            continue
        try:
            normalized = canonical_package_relative_path(
                raw_path, label, require_assets=True
            )
        except WorkflowError as exc:
            blockers.append(str(exc))
        else:
            component_uses[normalized] = expected_use

    rendered_counts: dict[str, int] = {}
    staged: set[str] = set()
    staged_asset_bytes = 0
    for raw_target in rendered_parser.sources:
        label = f"rendered body image {raw_target!r}"
        try:
            normalized = canonical_package_relative_path(
                raw_target, label, require_assets=True
            )
        except WorkflowError as exc:
            blockers.append(str(exc))
            continue
        rendered_counts[normalized] = rendered_counts.get(normalized, 0) + 1
        source = (package / normalized).resolve()
        try:
            source.relative_to(package.resolve())
        except ValueError:
            blockers.append(f"{label} escapes the content package")
            continue
        if not source.is_file():
            blockers.append(f"{label} does not exist in the content package")
            continue
        if is_link_or_junction(source) or is_multiply_linked_file(source):
            blockers.append(f"{label} must not be a symlink, junction, or hardlink")
            continue
        problem = image_file_problem(source)
        if problem is not None:
            blockers.append(f"{label} is not a valid release image: {problem}")
            continue

        entry = manifest_by_path.get(normalized)
        if entry is None:
            blockers.append(f"{label} is not registered in asset-manifest.yml")
        else:
            rights = str(entry.get("rights_status") or "").strip()
            platforms = entry.get("allowed_platforms") or []
            if rights not in RELEASE_RIGHTS_STATUSES:
                blockers.append(
                    f"{label} rights_status is not release-cleared: {rights or 'missing'}"
                )
            if not isinstance(platforms, list) or "wechat" not in platforms:
                blockers.append(f"{label} is not allowed for the wechat platform")
            expected_component_use = component_uses.get(normalized)
            if expected_component_use is not None:
                if str(entry.get("use") or "") != expected_component_use:
                    blockers.append(
                        f"{label} manifest use must be {expected_component_use}"
                    )
            elif entry.get("used_in_draft") is not True:
                blockers.append(
                    f"{label} manifest must declare used_in_draft: true"
                )

        if normalized not in staged:
            remaining_bytes = max(
                0, MAX_HANDOFF_TOTAL_ASSET_BYTES - staged_asset_bytes
            )
            staged_asset_bytes += stage_asset_bytes(
                source,
                build_dir,
                normalized,
                max_bytes=min(MAX_HANDOFF_IMAGE_BYTES, remaining_bytes),
            )
            staged.add(normalized)

    for normalized, expected_use in component_uses.items():
        count = rendered_counts.get(normalized, 0)
        if count != 1:
            blockers.append(
                f"{expected_use} must appear exactly once after Wenyan render; found {count}"
            )

    for kind, configured_path in (
        ("header", config.header_image),
        ("footer", config.footer_image),
    ):
        expected_count = 1 if configured_path else 0
        actual_count = rendered_parser.component_counts[kind]
        if actual_count != expected_count:
            blockers.append(
                f"{component_prefix or 'body-component'}-{kind} wrapper must appear "
                f"{expected_count} time(s) "
                f"after Wenyan render; found {actual_count}"
            )

    if config.cover:
        try:
            normalized_cover = canonical_package_relative_path(
                config.cover, "cover", require_assets=True
            )
            cover_source = (package / normalized_cover).resolve()
            cover_source.relative_to(package.resolve())
            if not cover_source.is_file():
                raise WorkflowError(f"cover does not exist: {config.cover}")
            if image_file_problem(cover_source) is not None:
                raise WorkflowError(f"cover is not a valid release image: {config.cover}")
            if normalized_cover not in staged:
                remaining_bytes = max(
                    0, MAX_HANDOFF_TOTAL_ASSET_BYTES - staged_asset_bytes
                )
                staged_asset_bytes += stage_asset_bytes(
                    cover_source,
                    build_dir,
                    normalized_cover,
                    max_bytes=min(MAX_HANDOFF_IMAGE_BYTES, remaining_bytes),
                )
        except (ValueError, WorkflowError) as exc:
            message = str(exc)
            if message and message not in blockers:
                blockers.append(message)

    return list(dict.fromkeys(blockers))


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

    manifest = load_yaml(package / "asset-manifest.yml")
    assets = manifest.get("assets") or []
    if not isinstance(assets, list):
        assets = []

    def asset_entry(raw_path: str) -> dict[str, Any] | None:
        try:
            normalized = canonical_package_relative_path(
                raw_path, "manifest asset", require_assets=True
            )
        except WorkflowError:
            return None
        return next(
            (
                item
                for item in assets
                if isinstance(item, dict)
                and _manifest_path_matches(item, normalized)
            ),
            None,
        )

    def _manifest_path_matches(item: dict[str, Any], expected: str) -> bool:
        try:
            candidate = canonical_package_relative_path(
                str(item.get("file") or ""),
                "manifest asset",
                require_assets=True,
            )
        except WorkflowError:
            return False
        return candidate == expected

    def check_release_asset(
        raw_path: str,
        label: str,
        expected_use: str | None = None,
        allow_cover_flag: bool = False,
    ) -> None:
        try:
            normalized = canonical_package_relative_path(
                raw_path, label, require_assets=True
            )
        except WorkflowError as exc:
            blockers.append(str(exc))
            return
        path = (package / normalized).resolve()
        try:
            path.relative_to(package.resolve())
        except ValueError:
            blockers.append(f"{label} path escapes the content package")
            return
        if not path.is_file():
            blockers.append(f"{label} does not exist: {raw_path}")
        elif is_link_or_junction(path) or is_multiply_linked_file(path):
            blockers.append(
                f"{label} must not be a symlink, junction, or hardlink"
            )
        else:
            problem = image_file_problem(path)
            if problem is not None:
                blockers.append(f"{label} is not a valid release image: {problem}")
        entry = asset_entry(normalized)
        if entry is None:
            blockers.append(f"{label} is not registered in asset-manifest.yml")
            return
        rights = str(entry.get("rights_status") or "").strip()
        platforms = entry.get("allowed_platforms") or []
        if rights not in RELEASE_RIGHTS_STATUSES:
            blockers.append(
                f"{label} rights_status is not release-cleared: {rights or 'missing'}"
            )
        if not isinstance(platforms, list) or "wechat" not in platforms:
            blockers.append(f"{label} asset is not allowed for the wechat platform")
        if expected_use is not None and str(entry.get("use") or "") != expected_use:
            if not (allow_cover_flag and entry.get("used_as_cover") is True):
                blockers.append(
                    f"{label} manifest must declare use: {expected_use}"
                    + (" or used_as_cover: true" if allow_cover_flag else "")
                )

    if not config.cover:
        blockers.append("publish.yml has no cover; an explicit rights-cleared cover is required")
    else:
        check_release_asset(
            config.cover,
            "cover",
            "wechat_cover",
            allow_cover_flag=True,
        )

    profile = get_layout_profile(config)
    adapter = get_project_adapter(config)
    mode = get_delivery_mode(config)
    if adapter is None:
        blockers.append(
            "publish.yml must explicitly set project_adapter to a registered adapter"
        )
    if mode is None:
        blockers.append(
            "publish.yml must explicitly set delivery_mode to manual_editor or sealed_draft"
        )
    elif mode.produces_editor_handoff:
        if config.theme != "default":
            blockers.append(
                "delivery_mode manual_editor requires theme default; visual formatting belongs in the WeChat editor"
            )
        if config.mac_style:
            blockers.append(
                "delivery_mode manual_editor requires mac_style false; visual formatting belongs in the WeChat editor"
            )
        if profile.profile_id != "default":
            blockers.append(
                "delivery_mode manual_editor requires layout_profile default; visual formatting belongs in the WeChat editor"
            )
    if profile.required_theme is not None and config.theme != profile.required_theme:
        blockers.append(
            f"layout_profile {profile.profile_id} requires theme {profile.required_theme}"
        )
    if (
        profile.required_highlight is not None
        and config.highlight != profile.required_highlight
    ):
        blockers.append(
            f"layout_profile {profile.profile_id} requires highlight {profile.required_highlight}"
        )
    if (
        profile.required_mac_style is not None
        and config.mac_style is not profile.required_mac_style
    ):
        expected = str(profile.required_mac_style).lower()
        blockers.append(
            f"layout_profile {profile.profile_id} requires mac_style {expected}"
        )
    if profile.profile_id == "appsso-article-v1":
        if adapter is None or adapter.adapter_id != "appsso":
            blockers.append(
                "layout_profile appsso-article-v1 requires project_adapter appsso"
            )
        if mode is None or mode.mode_id != "sealed_draft":
            blockers.append(
                "layout_profile appsso-article-v1 requires delivery_mode sealed_draft"
            )
    if (
        adapter is not None
        and adapter.adapter_id == "appsso"
        and mode is not None
        and mode.mode_id == "sealed_draft"
        and profile.profile_id != "appsso-article-v1"
    ):
        blockers.append(
            "project_adapter appsso with delivery_mode sealed_draft requires layout_profile appsso-article-v1"
        )
    if profile.required_header and not config.header_image:
        blockers.append(
            f"layout_profile {profile.profile_id} requires a rights-cleared header_image"
        )
    if config.header_image:
        check_release_asset(config.header_image, "header_image", "wechat_body_header")
        if not config.header_alt:
            blockers.append("header_image requires non-empty header_alt")
    if config.footer_image:
        check_release_asset(config.footer_image, "footer_image", "wechat_body_footer")
        if not config.footer_alt:
            blockers.append("footer_image requires non-empty footer_alt")
        if not config.footer_valid_until:
            blockers.append("footer_image requires footer_valid_until as YYYY-MM-DD")
        elif not ISO_DATE_RE.fullmatch(config.footer_valid_until):
            blockers.append("footer_valid_until must be YYYY-MM-DD")
        else:
            try:
                valid_until = date.fromisoformat(config.footer_valid_until)
            except ValueError:
                blockers.append("footer_valid_until must be YYYY-MM-DD")
            else:
                editorial_today = datetime.now(EDITORIAL_TIMEZONE).date()
                if valid_until < editorial_today:
                    blockers.append(
                        f"footer_image review is overdue since {config.footer_valid_until}; reconfirm or remove it"
                    )
                elif valid_until > editorial_today + timedelta(
                    days=MAX_FOOTER_REVIEW_DAYS
                ):
                    blockers.append(
                        f"footer_valid_until exceeds the {MAX_FOOTER_REVIEW_DAYS}-day review window"
                    )
    return blockers


def layout_plan(
    config: PublishConfig, theme_snapshot: Path | None = None
) -> dict[str, Any]:
    profile = get_layout_profile(config)
    custom_theme = profile.custom_theme
    if custom_theme is None:
        theme_path = None
        theme_sha256 = None
    else:
        theme_path = custom_theme.relative_to(WECHAT_ROOT).as_posix()
        theme_sha256 = hashlib.sha256(custom_theme.read_bytes()).hexdigest()
    return {
        "profile": profile.profile_id,
        "project_adapter": config.project_adapter or None,
        "custom_theme": theme_path,
        "custom_theme_sha256": theme_sha256,
        "theme_snapshot": theme_snapshot.name if theme_snapshot else None,
        "theme_snapshot_sha256": (
            file_sha256(theme_snapshot) if theme_snapshot else None
        ),
        "header_image": config.header_image or None,
        "footer_image": config.footer_image or None,
        "footer_valid_until": config.footer_valid_until or None,
    }


def capture_build_snapshot(
    package: Path,
    source: Path,
    theme_snapshot: Path | None,
    config: PublishConfig,
    package_files: dict[str, str],
) -> BuildSnapshot:
    profile = get_layout_profile(config)
    canonical_theme_sha256 = (
        file_sha256(profile.custom_theme) if profile.custom_theme else None
    )
    staged_files = build_input_hashes(source.parent)
    return BuildSnapshot(
        package_files=package_files,
        package_sha256=combined_hash(package_files),
        staged_files=staged_files,
        staged_sha256=combined_hash(staged_files),
        source_sha256=file_sha256(source),
        theme_snapshot_sha256=(
            file_sha256(theme_snapshot) if theme_snapshot else None
        ),
        canonical_theme_sha256=canonical_theme_sha256,
    )


def verify_build_snapshot(package: Path, build: PreviewBuild) -> None:
    current_package_files = package_input_hashes(package)
    if current_package_files != build.snapshot.package_files:
        raise WorkflowError(
            "content package changed after preflight; rebuild the preview before creating a draft"
        )
    if file_sha256(build.source) != build.snapshot.source_sha256:
        raise WorkflowError(
            "generated Wenyan source changed after preflight; rebuild before creating a draft"
        )
    current_staged_files = build_input_hashes(build.source.parent)
    if current_staged_files != build.snapshot.staged_files:
        raise WorkflowError(
            "sealed Wenyan build changed after preflight; rebuild before creating a draft"
        )
    if build.theme_snapshot is not None:
        if (
            file_sha256(build.theme_snapshot)
            != build.snapshot.theme_snapshot_sha256
        ):
            raise WorkflowError(
                "staged layout theme changed after preflight; rebuild before creating a draft"
            )
    profile = get_layout_profile(build.config)
    current_theme_sha256 = (
        file_sha256(profile.custom_theme) if profile.custom_theme else None
    )
    if current_theme_sha256 != build.snapshot.canonical_theme_sha256:
        raise WorkflowError(
            "canonical layout theme changed after preflight; rebuild before creating a draft"
        )


def handoff_document(
    title: str,
    fragment: str,
    validator_ok: bool,
    report: str,
    blockers: list[str],
    image_order: list[str] | None = None,
    copy_payload_bytes: int = 0,
) -> str:
    ready = validator_ok and not blockers
    status = "人工编辑交接已通过本地门禁" if ready else "人工编辑交接尚未通过本地门禁"
    issues = "".join(f"<li>{html.escape(item)}</li>" for item in blockers)
    blocker_box = f"<ul>{issues}</ul>" if issues else "<p>本地交接门禁无阻塞项。</p>"
    ordered_images = image_order or []
    fallback_items = "".join(
        f"<li>{index}. <code>{html.escape(path)}</code></li>"
        for index, path in enumerate(ordered_images, start=1)
    )
    fallback_box = (
        "<ol>" + fallback_items + "</ol>"
        if fallback_items
        else "<p>本稿没有正文图片。</p>"
    )
    disabled = "" if ready else " disabled"
    nonce = secrets.token_urlsafe(18)
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'nonce-{nonce}'; connect-src 'none'; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} - 公众号人工编辑交接</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#eef1f5;color:#222;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}}
.toolbar{{position:sticky;top:0;z-index:2;padding:12px 16px;background:#20242a;color:#fff;text-align:center}}.toolbar button{{padding:8px 16px;border:0;border-radius:6px;background:#fd4606;color:#fff;font-weight:600;cursor:pointer}}.toolbar button:disabled{{background:#777;cursor:not-allowed}}.toolbar span{{margin-left:10px;font-size:13px}}
.gate{{width:min(720px,calc(100% - 24px));margin:16px auto;padding:12px 16px;border:1px solid #e1bb68;border-radius:8px;background:#fff8e8;font-size:13px;line-height:1.6}}.gate pre{{white-space:pre-wrap;word-break:break-word;color:#666}}.gate ul,.gate ol{{margin:6px 0;padding-left:20px}}.gate code{{word-break:break-all}}
.sheet{{width:min(760px,100%);margin:16px auto 40px;padding:28px 16px 54px;background:#fff}}.sheet h1{{margin:0 0 24px;font-size:24px;line-height:1.4}}.wechat-handoff-content img{{display:block;max-width:100%;height:auto}}.wechat-handoff-content pre{{max-width:100%;overflow:auto;white-space:pre-wrap;word-break:break-word}}
</style></head><body><div class="toolbar"><button id="copy-article" type="button"{disabled}>复制正文</button><span id="copy-status">请使用按钮复制，不要复制本页门禁说明。</span></div>
<aside class="gate"><strong>{html.escape(status)}</strong>{blocker_box}<p>复制载荷：{copy_payload_bytes} 字节。本机复制成功不代表公众号后台已验收；粘贴后仍须检查图片、修改、保存并重开。</p><details><summary>图片未随正文粘贴时的降级顺序</summary><p>只从本次版本化交接目录上传下列已登记文件，并按正文顺序插入：</p>{fallback_box}</details><details><summary>查看校验输出</summary><pre>{html.escape(report)}</pre></details></aside>
<main class="sheet"><h1>{html.escape(title)}</h1><article id="wechat-handoff-content" class="wechat-handoff-content">{fragment}</article></main>
<script nonce="{nonce}">(function(){{var button=document.getElementById('copy-article');var article=document.getElementById('wechat-handoff-content');var status=document.getElementById('copy-status');if(!button||button.disabled)return;button.addEventListener('click',function(){{var onCopy=function(event){{event.clipboardData.setData('text/html',article.innerHTML);event.clipboardData.setData('text/plain',article.innerText);event.preventDefault();}};document.addEventListener('copy',onCopy,{{once:true}});var copied=document.execCommand('copy');status.textContent=copied?'正文已复制；请粘贴到公众号后台并完成编辑检查。':'浏览器未允许自动复制；请只选中正文区域手动复制。';}});}})();</script></body></html>"""


def preview_document(
    title: str,
    fragment: str,
    validator_ok: bool,
    report: str,
    blockers: list[str],
) -> str:
    status = "内容包校验通过" if validator_ok else "内容包校验未通过"
    issues = "".join(f"<li>{html.escape(item)}</li>" for item in blockers)
    blocker_box = f"<ul>{issues}</ul>" if issues else "<p>草稿箱门禁无阻塞项。</p>"
    notes = "".join(f"<li>{html.escape(item)}</li>" for item in WENYAN_NOTES)
    nonce = secrets.token_urlsafe(18)
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'nonce-{nonce}'; connect-src 'none'; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} - 公众号本机预览</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#eef1f5;color:#222;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}}
.bar{{position:sticky;top:0;z-index:2;padding:10px 16px;background:#20242a;color:#fff;text-align:center;font-size:13px}}
.gate{{width:min(720px,calc(100% - 24px));margin:16px auto;padding:12px 16px;border:1px solid #e1bb68;border-radius:8px;background:#fff8e8;font-size:13px;line-height:1.6}}
.gate pre{{white-space:pre-wrap;word-break:break-word;color:#666}}.gate ul{{margin:6px 0;padding-left:20px}}
.viewport{{display:flex;justify-content:center;gap:8px;margin:12px auto 0;font-size:13px}}.viewport button{{padding:5px 10px;border:1px solid #c8cdd4;border-radius:6px;background:#fff;color:#333;cursor:pointer}}
.phone{{width:390px;max-width:100%;min-height:100vh;margin:18px auto 40px;padding:28px 0 54px;background:#fff;box-shadow:0 12px 40px rgba(24,31,43,.15)}}
.title{{margin:0 16px 22px;font-size:24px;line-height:1.4;color:#111}}.phone img{{display:block;max-width:100%;height:auto}}.phone pre{{max-width:100%;overflow:auto;white-space:pre-wrap;word-break:break-word}}@media(max-width:520px){{.phone{{margin:0 auto;box-shadow:none}}}}
</style></head><body><div class="bar">本机预览 · Wenyan 渲染 · 不会上传</div>
<aside class="gate"><strong>{html.escape(status)}</strong>{blocker_box}<details><summary>查看 Wenyan 版本说明</summary><ul>{notes}</ul></details><details><summary>查看校验输出</summary><pre>{html.escape(report)}</pre></details></aside>
<nav class="viewport" aria-label="预览宽度"><button type="button" data-width="375">375 px</button><button type="button" data-width="390">390 px</button></nav>
<main class="phone" id="phone-preview" data-preview-width="390"><h1 class="title">{html.escape(title)}</h1>{fragment}</main>
<script nonce="{nonce}">(function(){{var phone=document.getElementById('phone-preview');function setWidth(width){{if(width!=='375'&&width!=='390')return;phone.style.width=width+'px';phone.setAttribute('data-preview-width',width);}}document.querySelectorAll('[data-width]').forEach(function(button){{button.addEventListener('click',function(){{setWidth(button.getAttribute('data-width'));}});}});setWidth(new URLSearchParams(window.location.search).get('width'));}})();</script></body></html>"""


def build_preview(package_arg: str | Path) -> PreviewBuild:
    package = Path(package_arg).resolve()
    if not package.is_dir():
        raise WorkflowError(f"content package is not a directory: {package}")
    initial_package_files = package_input_hashes(package)
    build_dir = create_build_dir(package)
    dist = safe_dist(package)
    with sealed_package_snapshot(package, initial_package_files) as sealed_package:
        source, metadata, config, _ = prepare_source(sealed_package, build_dir)
        profile = get_layout_profile(config)
        delivery_mode = get_delivery_mode(config)
        canonical_theme_before = (
            file_sha256(profile.custom_theme) if profile.custom_theme else None
        )
        theme_snapshot = stage_layout_theme(build_dir, config)
        source_before_render = file_sha256(source)
        theme_snapshot_before_render = (
            file_sha256(theme_snapshot) if theme_snapshot else None
        )
        raw_rendered = run_wenyan_render(source, config, theme_snapshot)
        if file_sha256(source) != source_before_render:
            raise WorkflowError(
                "generated Wenyan source changed while rendering; run the command again"
            )
        if theme_snapshot is not None and (
            file_sha256(theme_snapshot) != theme_snapshot_before_render
        ):
            raise WorkflowError(
                "staged layout theme changed while rendering; run the command again"
            )
        raw_presentation_tags = (
            MANUAL_PRESENTATION_TAGS
            if delivery_mode is not None and delivery_mode.strip_inline_styles
            else None
        )
        ensure_passive_preview_html(
            raw_rendered,
            allowed_presentation_tags=raw_presentation_tags,
        )
        validator_ok, report = validator_report(sealed_package)
        blockers = publication_blockers(sealed_package, metadata, config)
        blockers.extend(
            rendered_image_gate_and_stage(
                sealed_package, build_dir, raw_rendered, config
            )
        )
        blockers = list(dict.fromkeys(blockers))
        rendered = apply_delivery_mode(raw_rendered, config)
        ensure_passive_preview_html(rendered)
        prepared_images = prepare_inline_image_graph(rendered, build_dir)
        rendered_for_preview = inline_preview_images(
            rendered, build_dir, prepared_images
        )
    final_package_files = package_input_hashes(package)
    if final_package_files != initial_package_files:
        raise WorkflowError(
            "content package changed while building the preview; run the command again"
        )
    canonical_theme_after = (
        file_sha256(profile.custom_theme) if profile.custom_theme else None
    )
    if canonical_theme_after != canonical_theme_before:
        raise WorkflowError(
            "layout theme changed while building the preview; run the command again"
        )
    if theme_snapshot is not None and (
        file_sha256(theme_snapshot) != canonical_theme_before
    ):
        raise WorkflowError("staged layout theme does not match the canonical theme")
    snapshot = capture_build_snapshot(
        package,
        source,
        theme_snapshot,
        config,
        final_package_files,
    )
    if snapshot.source_sha256 != source_before_render:
        raise WorkflowError(
            "generated Wenyan source changed while recording the build; run the command again"
        )
    if snapshot.canonical_theme_sha256 != canonical_theme_before:
        raise WorkflowError(
            "canonical layout theme changed while recording the build; run the command again"
        )
    content_path = dist / "wechat-content.html"
    preview_path = dist / "wechat-preview.html"
    handoff_path: Path | None = None
    handoff_content_path: Path | None = None
    handoff_copy_payload_path: Path | None = None
    handoff_plan_path: Path | None = None
    handoff_plan_sha256: str | None = None
    handoff_asset_hashes: dict[str, str] = {}
    handoff_asset_details: dict[str, dict[str, Any]] = {}
    handoff_image_order: list[str] = []
    copy_payload_bytes = 0
    if delivery_mode is not None and delivery_mode.produces_editor_handoff:
        handoff_dir = create_handoff_dir(package)
        handoff_asset_details, handoff_image_order = copy_handoff_images(
            prepared_images, handoff_dir
        )
        handoff_asset_hashes = {
            path: str(item["sha256"])
            for path, item in handoff_asset_details.items()
        }
        handoff_content_path = handoff_dir / "wechat-content.html"
        handoff_copy_payload_path = handoff_dir / "wechat-copy-payload.html"
        handoff_path = handoff_dir / "wechat-handoff.html"
        atomic_write_text(handoff_content_path, rendered)
        atomic_write_text(handoff_copy_payload_path, rendered_for_preview)
        copy_payload_bytes = handoff_copy_payload_path.stat().st_size
        blockers.extend(
            handoff_resource_blockers(
                handoff_asset_details, copy_payload_bytes
            )
        )
        blockers = list(dict.fromkeys(blockers))
        atomic_write_text(
            handoff_path,
            handoff_document(
                config.title,
                rendered_for_preview,
                validator_ok,
                report,
                blockers,
                handoff_image_order,
                copy_payload_bytes,
            ),
        )
    atomic_write_text(content_path, rendered_for_preview)
    atomic_write_text(
        preview_path,
        preview_document(
            config.title, rendered_for_preview, validator_ok, report, blockers
        ),
    )
    plan = {
        "renderer": "@wenyan-md/cli@2.0.11",
        "path_base": "dist",
        "source": source.relative_to(dist).as_posix(),
        "preview": preview_path.name,
        "content": content_path.name,
        "config": asdict(config),
        "delivery": {
            "mode": (
                delivery_mode.mode_id
                if delivery_mode is not None
                else "legacy_unspecified"
            ),
            "api_draft_allowed": bool(
                delivery_mode is not None and delivery_mode.api_draft_allowed
            ),
            "handoff": (
                handoff_path.relative_to(dist).as_posix()
                if handoff_path is not None
                else None
            ),
            "handoff_content": (
                handoff_content_path.relative_to(dist).as_posix()
                if handoff_content_path is not None
                else None
            ),
            "handoff_content_sha256": (
                file_sha256(handoff_content_path)
                if handoff_content_path is not None
                else None
            ),
            "handoff_content_bytes": (
                handoff_content_path.stat().st_size
                if handoff_content_path is not None
                else None
            ),
            "handoff_document_sha256": (
                file_sha256(handoff_path)
                if handoff_path is not None
                else None
            ),
            "handoff_document_bytes": (
                handoff_path.stat().st_size if handoff_path is not None else None
            ),
            "copy_payload": (
                handoff_copy_payload_path.relative_to(dist).as_posix()
                if handoff_copy_payload_path is not None
                else None
            ),
            "copy_payload_sha256": (
                file_sha256(handoff_copy_payload_path)
                if handoff_copy_payload_path is not None
                else None
            ),
            "copy_payload_bytes": (
                copy_payload_bytes
                if handoff_copy_payload_path is not None
                else None
            ),
            "copy_payload_hash_scope": (
                "HTML supplied to the handoff page before browser DOM normalization"
                if handoff_copy_payload_path is not None
                else None
            ),
            "handoff_asset_path_base": (
                "handoff" if handoff_path is not None else None
            ),
            "handoff_asset_sha256": handoff_asset_hashes,
            "handoff_assets": handoff_asset_details,
            "handoff_image_order": handoff_image_order,
            "handoff_resource_summary": (
                {
                    "image_references": len(handoff_image_order),
                    "unique_images": len(handoff_asset_details),
                    "unique_asset_bytes": sum(
                        int(item["bytes"])
                        for item in handoff_asset_details.values()
                    ),
                    "largest_image_bytes": max(
                        (
                            int(item["bytes"])
                            for item in handoff_asset_details.values()
                        ),
                        default=0,
                    ),
                    "total_frames": sum(
                        int(item["frame_count"])
                        for item in handoff_asset_details.values()
                    ),
                    "occurrence_frames": sum(
                        int(item["frame_count"]) * int(item["occurrences"])
                        for item in handoff_asset_details.values()
                    ),
                    "total_decoded_frame_pixels": sum(
                        int(item["decoded_frame_pixels"])
                        for item in handoff_asset_details.values()
                    ),
                    "occurrence_decoded_frame_pixels": sum(
                        int(item["decoded_frame_pixels"])
                        * int(item["occurrences"])
                        for item in handoff_asset_details.values()
                    ),
                    "internal_limits": {
                        "image_bytes": MAX_HANDOFF_IMAGE_BYTES,
                        "total_asset_bytes": MAX_HANDOFF_TOTAL_ASSET_BYTES,
                        "copy_html_bytes": MAX_HANDOFF_COPY_HTML_BYTES,
                        "content_html_bytes": MAX_HANDOFF_CONTENT_HTML_BYTES,
                        "handoff_document_bytes": MAX_HANDOFF_DOCUMENT_BYTES,
                        "handoff_plan_bytes": MAX_HANDOFF_PLAN_BYTES,
                        "pixels_per_frame": MAX_HANDOFF_IMAGE_PIXELS,
                        "decoded_frame_pixels": MAX_HANDOFF_DECODED_FRAME_PIXELS,
                        "frames_per_image": MAX_HANDOFF_IMAGE_FRAMES,
                        "total_frames": MAX_HANDOFF_TOTAL_FRAMES,
                        "image_references": MAX_INLINE_IMAGE_REFERENCES,
                        "occurrence_frames": MAX_HANDOFF_OCCURRENCE_FRAMES,
                        "total_decoded_frame_pixels": MAX_HANDOFF_TOTAL_DECODED_FRAME_PIXELS,
                        "occurrence_decoded_frame_pixels": MAX_HANDOFF_OCCURRENCE_DECODED_FRAME_PIXELS,
                    },
                }
                if handoff_path is not None
                else None
            ),
            "wechat_backend_roundtrip": (
                "pending"
                if delivery_mode is not None
                else "not_configured"
            ),
        },
        "layout": layout_plan(config, theme_snapshot),
        "snapshot": {
            "package_sha256": snapshot.package_sha256,
            "package_file_count": len(snapshot.package_files),
            "staged_sha256": snapshot.staged_sha256,
            "staged_file_count": len(snapshot.staged_files),
            "source_sha256": snapshot.source_sha256,
            "theme_snapshot_sha256": snapshot.theme_snapshot_sha256,
            "canonical_theme_sha256": snapshot.canonical_theme_sha256,
        },
        "content_status": metadata.get("status"),
        "validator_ok": validator_ok,
        "blockers": blockers,
        "known_limitations": WENYAN_NOTES,
        "external_effect": "none; local render only",
    }
    serialized_plan = json.dumps(plan, ensure_ascii=False, indent=2) + "\n"
    atomic_write_text(dist / "publish-plan.json", serialized_plan)
    if handoff_path is not None:
        handoff_plan_path = handoff_path.parent / "publish-plan.json"
        atomic_write_text(handoff_plan_path, serialized_plan)
        handoff_plan_sha256 = file_sha256(handoff_plan_path)
    print(f"[preview] {preview_path}")
    if handoff_path is not None:
        print(f"[editor handoff] {handoff_path}")
    print(f"[renderer] Wenyan CLI 2.0.11; html_chars={len(rendered)}")
    if report:
        print(report)
    if blockers:
        print("[delivery blockers]")
        for item in blockers:
            print(f"- {item}")
    for item in WENYAN_NOTES:
        print(f"[wenyan note] {item}")
    return PreviewBuild(
        preview_path=preview_path,
        source=source,
        theme_snapshot=theme_snapshot,
        metadata=metadata,
        config=config,
        blockers=blockers,
        validator_ok=validator_ok,
        validator_report=report,
        snapshot=snapshot,
        handoff_path=handoff_path,
        handoff_plan_path=handoff_plan_path,
        handoff_plan_sha256=handoff_plan_sha256,
    )


def verify_handoff_artifact(build: PreviewBuild) -> None:
    """Recheck every handoff artifact's verify-time integrity before opening it."""

    if build.handoff_path is None or build.handoff_plan_path is None:
        raise WorkflowError("editor handoff artifact or plan is missing")
    if not build.handoff_plan_sha256:
        raise WorkflowError("editor handoff plan has no build-time integrity hash")
    handoff_path = build.handoff_path
    handoff_dir = handoff_path.parent
    dist = handoff_dir.parent.parent

    def regular_file(path: Path, label: str) -> None:
        if not path.is_file():
            raise WorkflowError(f"{label} is missing: {path}")
        if is_link_or_junction(path) or is_multiply_linked_file(path):
            raise WorkflowError(f"{label} must not be a symlink, junction, or hardlink")

    def verified_bytes(
        path: Path,
        expected_hash: Any,
        label: str,
        expected_size: Any = None,
        max_bytes: int | None = None,
    ) -> bytes:
        regular_file(path, label)
        if expected_size is not None and (
            not isinstance(expected_size, int)
            or isinstance(expected_size, bool)
            or expected_size < 0
        ):
            raise WorkflowError(f"{label} has an invalid byte count")
        payload = stable_file_bytes(
            path,
            expected_size=expected_size,
            max_bytes=max_bytes,
        )
        if (
            not isinstance(expected_hash, str)
            or hashlib.sha256(payload).hexdigest() != expected_hash
        ):
            raise WorkflowError(f"{label} hash mismatch")
        if expected_size is not None and len(payload) != expected_size:
            raise WorkflowError(f"{label} byte count mismatch")
        return payload

    plan_payload = verified_bytes(
        build.handoff_plan_path,
        build.handoff_plan_sha256,
        "editor handoff plan",
        max_bytes=MAX_HANDOFF_PLAN_BYTES,
    )
    try:
        plan = json.loads(plan_payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise WorkflowError("editor handoff plan cannot be read as JSON") from exc
    if not isinstance(plan, dict) or plan.get("path_base") != "dist":
        raise WorkflowError("editor handoff plan must declare path_base dist")
    delivery = plan.get("delivery")
    if not isinstance(delivery, dict) or delivery.get("mode") != "manual_editor":
        raise WorkflowError("editor handoff plan does not describe manual_editor")

    def resolve_under(root: Path, raw: Any, label: str) -> Path:
        if not isinstance(raw, str) or not raw:
            raise WorkflowError(f"editor handoff plan has no {label} path")
        normalized = canonical_package_relative_path(raw, label)
        resolved = (root / Path(normalized)).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError as exc:
            raise WorkflowError(f"editor handoff {label} path escapes its base") from exc
        return resolved

    planned_handoff = resolve_under(dist, delivery.get("handoff"), "handoff")
    if planned_handoff != handoff_path.resolve():
        raise WorkflowError("editor handoff path does not match its build result")
    handoff_document_payload = verified_bytes(
        planned_handoff,
        delivery.get("handoff_document_sha256"),
        "editor handoff document",
        delivery.get("handoff_document_bytes"),
        MAX_HANDOFF_DOCUMENT_BYTES,
    )

    content_path = resolve_under(
        dist, delivery.get("handoff_content"), "handoff content"
    )
    content_payload = verified_bytes(
        content_path,
        delivery.get("handoff_content_sha256"),
        "editor handoff content",
        delivery.get("handoff_content_bytes"),
        MAX_HANDOFF_CONTENT_HTML_BYTES,
    )
    copy_payload_path = resolve_under(
        dist, delivery.get("copy_payload"), "copy payload"
    )
    copy_payload = verified_bytes(
        copy_payload_path,
        delivery.get("copy_payload_sha256"),
        "editor handoff copy payload",
        delivery.get("copy_payload_bytes"),
        MAX_HANDOFF_COPY_HTML_BYTES,
    )

    assets = delivery.get("handoff_assets")
    legacy_hashes = delivery.get("handoff_asset_sha256")
    if not isinstance(assets, dict) or not isinstance(legacy_hashes, dict):
        raise WorkflowError("editor handoff plan has invalid asset metadata")
    if delivery.get("handoff_asset_path_base") != "handoff":
        raise WorkflowError("editor handoff plan has an invalid asset path base")
    expected_hashes: dict[str, str] = {}
    for raw_path, item in assets.items():
        if not isinstance(raw_path, str) or not isinstance(item, dict):
            raise WorkflowError("editor handoff plan has malformed asset metadata")
        normalized = canonical_package_relative_path(
            raw_path, "handoff asset", require_assets=True
        )
        asset_path = (handoff_dir / Path(normalized)).resolve()
        try:
            asset_path.relative_to(handoff_dir.resolve())
        except ValueError as exc:
            raise WorkflowError("editor handoff asset path escapes its base") from exc
        expected_hash = item.get("sha256")
        verified_bytes(
            asset_path,
            expected_hash,
            f"editor handoff asset {normalized}",
            item.get("bytes"),
            MAX_HANDOFF_IMAGE_BYTES,
        )
        expected_hashes[normalized] = str(expected_hash)
    if legacy_hashes != expected_hashes:
        raise WorkflowError("editor handoff asset hash indexes disagree")

    actual_asset_files = {
        path.relative_to(handoff_dir).as_posix()
        for path in (handoff_dir / "assets").rglob("*")
        if path.is_file()
    } if (handoff_dir / "assets").is_dir() else set()
    if actual_asset_files != set(expected_hashes):
        raise WorkflowError("editor handoff asset directory does not match its plan")

    image_order = delivery.get("handoff_image_order")
    if not isinstance(image_order, list) or not all(
        isinstance(item, str) for item in image_order
    ):
        raise WorkflowError("editor handoff plan has an invalid image order")
    try:
        content_fragment = content_payload.decode("utf-8")
        copy_fragment = copy_payload.decode("utf-8")
        handoff_document_text = handoff_document_payload.decode("utf-8")
    except UnicodeError as exc:
        raise WorkflowError("editor handoff HTML is not valid UTF-8") from exc
    normalized_content_order = [
        canonical_package_relative_path(
            decode_image_target(target),
            "handoff content image",
            require_assets=True,
        )
        for target in raw_html_image_sources(content_fragment)
    ]
    if normalized_content_order != image_order:
        raise WorkflowError("editor handoff content image order does not match its plan")
    occurrence_counts = {
        path: normalized_content_order.count(path) for path in set(normalized_content_order)
    }
    for path, item in assets.items():
        if item.get("occurrences") != occurrence_counts.get(path, 0):
            raise WorkflowError(
                f"editor handoff asset occurrence count mismatch: {path}"
            )

    copy_sources = raw_html_image_sources(copy_fragment)
    if len(copy_sources) != len(image_order):
        raise WorkflowError("editor handoff copy payload image count mismatch")
    for index, (target, planned_path) in enumerate(
        zip(copy_sources, image_order, strict=True), start=1
    ):
        match = re.fullmatch(
            r"data:[^;,]+;base64,(?P<payload>[A-Za-z0-9+/=]+)", target
        )
        if match is None:
            raise WorkflowError(
                f"editor handoff copy payload image {index} is not embedded data"
            )
        try:
            payload = base64.b64decode(match.group("payload"), validate=True)
        except (binascii.Error, ValueError) as exc:
            raise WorkflowError(
                f"editor handoff copy payload image {index} has invalid base64"
            ) from exc
        if hashlib.sha256(payload).hexdigest() != expected_hashes.get(planned_path):
            raise WorkflowError(
                f"editor handoff copy payload image {index} hash mismatch"
            )

    expected_article = (
        '<article id="wechat-handoff-content" class="wechat-handoff-content">'
        + copy_fragment
        + "</article>"
    )
    if expected_article not in handoff_document_text:
        raise WorkflowError("editor handoff document does not embed its copy payload")


def command_preview(args: argparse.Namespace) -> int:
    build = build_preview(args.package)
    if args.open:
        if os.name != "nt":
            raise WorkflowError("--open is currently implemented for Windows only")
        os.startfile(build.preview_path)  # type: ignore[attr-defined]
    return 0


def command_handoff(args: argparse.Namespace) -> int:
    build = build_preview(args.package)
    mode = get_delivery_mode(build.config, require_explicit=True)
    if mode is None or not mode.produces_editor_handoff:
        raise WorkflowError(
            "handoff command requires delivery_mode manual_editor"
        )
    if not build.validator_ok:
        raise WorkflowError(
            f"content-package validator blocks editor handoff:\n{build.validator_report}"
        )
    if build.blockers:
        raise WorkflowError(
            "editor handoff is blocked:\n- " + "\n- ".join(build.blockers)
        )
    if build.handoff_path is None or not build.handoff_path.is_file():
        raise WorkflowError("editor handoff artifact was not created")
    verify_handoff_artifact(build)
    print(f"[handoff ready] {build.handoff_path}")
    if args.open:
        if os.name != "nt":
            raise WorkflowError("--open is currently implemented for Windows only")
        os.startfile(build.handoff_path)  # type: ignore[attr-defined]
    return 0


def command_draft(args: argparse.Namespace) -> int:
    package = Path(args.package).resolve()
    build = build_preview(package)
    mode = get_delivery_mode(build.config, require_explicit=True)
    if mode is None or not mode.api_draft_allowed:
        raise WorkflowError(
            "delivery_mode manual_editor cannot create a WeChat API draft; use the handoff command"
        )
    if not build.validator_ok:
        raise WorkflowError(
            f"content-package validator blocks draft creation:\n{build.validator_report}"
        )
    if build.blockers:
        raise WorkflowError(
            "draft creation is blocked:\n- " + "\n- ".join(build.blockers)
        )
    if not args.execute:
        print(
            "[dry-run pass] preflight passed; no network call or external write was performed; "
            "add --execute to create one draft"
        )
        return 0
    env_path = Path(args.env).resolve() if args.env else WECHAT_ROOT / ".env"
    if not env_path.is_file():
        raise WorkflowError(
            "credential file is missing. Copy 微信公众号/.env.example to 微信公众号/.env and fill it locally; never paste the secret into chat."
        )
    account_fingerprint, credential_file_sha256 = wechat_credential_metadata(env_path)
    command = wenyan_args(
        "publish", build.source, build.config, build.theme_snapshot
    ) + ["--env-file", str(env_path)]
    external_attempt_started = False
    try:
        with exclusive_publish_lock(package):
            verify_build_snapshot(package, build)
            current_fingerprint, current_credential_hash = wechat_credential_metadata(
                env_path
            )
            if (
                current_fingerprint != account_fingerprint
                or current_credential_hash != credential_file_sha256
            ):
                raise WorkflowError(
                    "credential file changed after preflight; run the command again"
                )
            print(
                "[account] explicit credential file selected; "
                f"app_id_sha256={account_fingerprint}"
            )
            print(
                "[execute] invoking pinned Wenyan CLI to upload assets and create one WeChat draft"
            )
            external_attempt_started = True
            result = subprocess.run(
                command,
                cwd=WECHAT_ROOT,
                env=wenyan_environment(),
                check=False,
            )
            if result.returncode != 0:
                raise WorkflowError(
                    f"Wenyan publish failed with exit code {result.returncode}"
                )
            verify_build_snapshot(package, build)
            _, final_credential_hash = wechat_credential_metadata(env_path)
            if final_credential_hash != credential_file_sha256:
                raise WorkflowError("credential file changed during upload")
            record = {
                "renderer": "@wenyan-md/cli@2.0.11",
                "title": build.config.title,
                "wechat_account_fingerprint": account_fingerprint,
                "package_sha256": build.snapshot.package_sha256,
                "source_sha256": build.snapshot.source_sha256,
                "theme_sha256": build.snapshot.theme_snapshot_sha256,
                "external_effect": "created one WeChat draft; did not publish or mass-send",
            }
            dist = safe_dist(package)
            atomic_write_text(
                dist / "wechat-draft-result.json",
                json.dumps(record, ensure_ascii=False, indent=2) + "\n",
            )
    except (Exception, KeyboardInterrupt) as exc:
        if external_attempt_started:
            raise WorkflowError(
                "the WeChat draft attempt did not complete locally; permanent body/cover "
                "materials may already have been uploaded and one draft may have been created. "
                "Inspect the target account backend and material library before retrying. "
                f"Local cause: {exc}"
            ) from exc
        raise
    print("[done] one WeChat draft was created; nothing was published or mass-sent")
    return 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preview, hand off, or create one sealed WeChat draft from a content package."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    preview = subparsers.add_parser("preview", help="render a local phone-width preview")
    preview.add_argument("package", help="path to a WeChat content package")
    preview.add_argument("--open", action="store_true", help="open preview in the default browser")
    preview.set_defaults(func=command_preview)
    handoff = subparsers.add_parser(
        "handoff", help="build an editable, no-network WeChat editor handoff"
    )
    handoff.add_argument("package", help="path to a WeChat content package")
    handoff.add_argument(
        "--open", action="store_true", help="open the editor handoff in the default browser"
    )
    handoff.set_defaults(func=command_handoff)
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
