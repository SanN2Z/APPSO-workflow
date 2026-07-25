#!/usr/bin/env python3
"""Collect metadata-only, structure-only records from explicit article URLs.

The collector intentionally has no link discovery. Article HTML is bounded,
parsed in memory, projected into a closed schema, and never written or logged.
"""

from __future__ import annotations

import argparse
import codecs
import hashlib
import ipaddress
import json
import math
import os
import re
import socket
import statistics
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlparse, urlunparse
from urllib.request import (
    HTTPRedirectHandler,
    ProxyHandler,
    Request,
    build_opener,
)
from urllib.robotparser import RobotFileParser

import yaml


MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_ROBOTS_BYTES = 512 * 1024
MAX_CONFIG_BYTES = 512 * 1024
MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_CORPUS_BYTES = 64 * 1024 * 1024
MAX_JSON_LINE_BYTES = 1024 * 1024
MAX_JSON_LD_CHARS = 256 * 1024
MAX_REDIRECTS = 5
MAX_SLEEP_SECONDS = 60.0
MAX_URL_CHARS = 4096
MAX_TITLE_CHARS = 500
MAX_AUTHOR_CHARS = 200
MAX_COLUMN_CHARS = 200
MAX_AUTHORS = 20
MAX_STRUCTURE_COUNT = 10_000_000

REDIRECT_STATUSES = {301, 302, 303, 307, 308}
ROBOTS_ABSENT_STATUSES = {404, 410}
ALLOWED_PAGE_CONTENT_TYPES = {"text/html", "application/xhtml+xml"}
ALLOWED_CHARSETS = {"utf-8", "utf8", "gb18030", "gbk", "big5"}
VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
SKIP_STRUCTURE_TAGS = {
    "aside",
    "button",
    "canvas",
    "footer",
    "form",
    "nav",
    "noscript",
    "script",
    "style",
    "svg",
    "template",
}
SENTENCE_ENDINGS = set("。！？!?；;")
ARTICLE_JSONLD_TYPES = {
    "article",
    "blogposting",
    "newsarticle",
    "reportagenewsarticle",
    "techarticle",
}
PRODUCT_TOKEN_RE = re.compile(r"^[A-Za-z_-]+$")
TAG_RE = re.compile(r"^[a-z][a-z0-9-]*$")
CLASS_TOKEN_RE = re.compile(r"^[^\s\"'<>/=]+$")
ISO_PREFIX_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})(?:$|[Tt ])")
SLASH_DATE_RE = re.compile(r"^(\d{4})/(\d{1,2})/(\d{1,2})(?:$|\s)")
CHINESE_DATE_RE = re.compile(r"^(\d{4})年(\d{1,2})月(\d{1,2})日")
CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")

TOP_LEVEL_RECORD_KEYS = {
    "schema_version",
    "url",
    "title",
    "published_date",
    "authors",
    "column",
    "structure",
}
STRUCTURE_KEYS = {
    "visible_char_count",
    "paragraph_count",
    "sentence_count",
    "heading_counts",
    "heading_level_sequence",
    "list_count",
    "list_item_count",
    "blockquote_count",
    "figure_count",
    "image_count",
    "caption_count",
    "link_count",
    "paragraph_char_stats",
    "sentence_char_stats",
    "short_paragraph_bins",
    "lead_paragraph_chars",
    "closing_paragraph_chars",
    "image_position_quartiles",
}
HEADING_COUNT_KEYS = {"h1", "h2", "h3"}
PARAGRAPH_STAT_KEYS = {"min", "p25", "median", "mean", "p75", "max", "stddev"}
SENTENCE_STAT_KEYS = {"min", "median", "mean", "max"}
PARAGRAPH_BIN_KEYS = {"0_15", "16_40", "41_80", "81_plus"}


class DerivedCorpusError(RuntimeError):
    """Expected, sanitized workflow failure."""


class ConfigError(DerivedCorpusError):
    pass


class PolicyError(DerivedCorpusError):
    pass


class NetworkError(DerivedCorpusError):
    pass


class ExtractionError(DerivedCorpusError):
    pass


class SchemaError(DerivedCorpusError):
    pass


class OutputError(DerivedCorpusError):
    pass


class StrictYamlLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: StrictYamlLoader,
    node: yaml.nodes.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ConfigError(f"配置包含重复键：{key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


StrictYamlLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


@dataclass(frozen=True)
class ArticleContainer:
    tag: str
    class_name: str


@dataclass(frozen=True)
class DomainPolicy:
    host: str
    scheme: str
    port: int
    allowed_path_prefixes: tuple[str, ...]
    article_container: ArticleContainer

    @property
    def origin(self) -> str:
        default_port = 443 if self.scheme == "https" else 80
        netloc = self.host if self.port == default_port else f"{self.host}:{self.port}"
        return f"{self.scheme}://{netloc}"

    @property
    def origin_key(self) -> str:
        return self.origin


@dataclass(frozen=True)
class CollectionPolicy:
    user_agent: str
    product_token: str
    min_delay_seconds: float
    timeout_seconds: float
    max_pages_per_run: int
    domains: Mapping[str, DomainPolicy]

    def domain_for_url(
        self,
        raw_url: str,
        *,
        require_article_path: bool,
    ) -> tuple[str, DomainPolicy]:
        normalized, parsed_host, scheme, port, path = normalize_absolute_url(raw_url)
        domain = self.domains.get(parsed_host)
        if domain is None:
            raise PolicyError(f"URL host 不在 exact allowlist：{parsed_host}")
        if scheme != domain.scheme or port != domain.port:
            raise PolicyError(
                f"URL origin 与 allowlist 不一致：{safe_url_for_log(normalized)}"
            )
        if require_article_path and not any(
            path.startswith(prefix) for prefix in domain.allowed_path_prefixes
        ):
            raise PolicyError(
                f"URL path 不在允许范围：{safe_url_for_log(normalized)}"
            )
        return normalized, domain


@dataclass(frozen=True)
class HttpResult:
    status: int
    headers: Mapping[str, str]
    body: bytes


@dataclass(frozen=True)
class RobotsRules:
    allow_all: bool
    parser: RobotFileParser | None
    effective_delay_seconds: float

    def can_fetch(self, product_token: str, url: str) -> bool:
        if self.allow_all:
            return True
        if self.parser is None:
            return False
        return bool(self.parser.can_fetch(product_token, url))


class NoRedirectHandler(HTTPRedirectHandler):
    """Expose redirects to the policy layer instead of following automatically."""

    def redirect_request(
        self,
        req: Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        return None


class BoundedHttpClient:
    """urllib client with no ambient proxy, no automatic redirect, and byte caps."""

    RETAINED_HEADERS = {
        "content-encoding",
        "content-length",
        "content-type",
        "location",
        "retry-after",
    }

    def __init__(self) -> None:
        self.opener = build_opener(ProxyHandler({}), NoRedirectHandler())

    @classmethod
    def _selected_headers(cls, raw_headers: Any) -> dict[str, str]:
        selected: dict[str, str] = {}
        for name in cls.RETAINED_HEADERS:
            value = raw_headers.get(name)
            if value is not None:
                selected[name] = str(value)
        return selected

    def get(
        self,
        url: str,
        *,
        user_agent: str,
        timeout_seconds: float,
        max_bytes: int,
        accept: str,
    ) -> HttpResult:
        request = Request(
            url,
            headers={
                "Accept": accept,
                "Accept-Encoding": "identity",
                "User-Agent": user_agent,
            },
            method="GET",
        )
        try:
            with self.opener.open(request, timeout=timeout_seconds) as response:
                headers = self._selected_headers(response.headers)
                self._validate_transfer_headers(headers, max_bytes=max_bytes)
                body = response.read(max_bytes + 1)
                if len(body) > max_bytes:
                    raise NetworkError(
                        f"响应超过 {max_bytes} 字节上限：{safe_url_for_log(url)}"
                    )
                return HttpResult(
                    status=int(response.getcode()),
                    headers=headers,
                    body=body,
                )
        except HTTPError as exc:
            headers = self._selected_headers(exc.headers)
            try:
                return HttpResult(status=int(exc.code), headers=headers, body=b"")
            finally:
                exc.close()
        except (URLError, TimeoutError, OSError) as exc:
            reason = type(getattr(exc, "reason", exc)).__name__
            raise NetworkError(
                f"网络请求失败（{reason}）：{safe_url_for_log(url)}"
            ) from exc

    @staticmethod
    def _validate_transfer_headers(
        headers: Mapping[str, str],
        *,
        max_bytes: int,
    ) -> None:
        encoding = headers.get("content-encoding", "").strip().casefold()
        if encoding not in {"", "identity"}:
            raise NetworkError(f"不支持的 Content-Encoding：{encoding}")
        raw_length = headers.get("content-length")
        if raw_length is None:
            return
        try:
            length = int(raw_length)
        except ValueError as exc:
            raise NetworkError("Content-Length 不是有效整数") from exc
        if length < 0 or length > max_bytes:
            raise NetworkError(f"响应声明大小超过 {max_bytes} 字节上限")


class HostRateLimiter:
    """Single-process per-origin limiter; the collector itself is serial."""

    def __init__(
        self,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.clock = clock
        self.sleeper = sleeper
        self.last_request_at: dict[str, float] = {}

    def wait(self, origin: str, delay_seconds: float) -> None:
        previous = self.last_request_at.get(origin)
        if previous is None:
            return
        elapsed = self.clock() - previous
        remaining = max(0.0, delay_seconds - elapsed)
        if remaining > MAX_SLEEP_SECONDS:
            raise PolicyError(
                f"robots/策略要求等待 {remaining:.2f} 秒，超过单次运行上限"
            )
        if remaining > 0:
            self.sleeper(remaining)

    def mark(self, origin: str) -> None:
        self.last_request_at[origin] = self.clock()


def configure_utf8_stdio() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def ensure_exact_keys(
    value: Mapping[str, Any],
    allowed: set[str],
    label: str,
) -> None:
    unexpected = set(value) - allowed
    missing = allowed - set(value)
    if unexpected:
        raise SchemaError(f"{label} 含未知字段：{sorted(unexpected)}")
    if missing:
        raise SchemaError(f"{label} 缺少字段：{sorted(missing)}")


def ensure_config_keys(
    value: Mapping[str, Any],
    allowed: set[str],
    required: set[str],
    label: str,
) -> None:
    unexpected = set(value) - allowed
    missing = required - set(value)
    if unexpected:
        raise ConfigError(f"{label} 含未知字段：{sorted(unexpected)}")
    if missing:
        raise ConfigError(f"{label} 缺少字段：{sorted(missing)}")


def is_plain_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def is_plain_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def canonical_host(raw_host: str) -> str:
    host = raw_host.strip()
    if not host or host.endswith("."):
        raise PolicyError("host 为空或带有尾随点")
    try:
        canonical = host.encode("idna").decode("ascii").casefold()
    except UnicodeError as exc:
        raise PolicyError(f"host 无法做 IDNA 规范化：{host!r}") from exc
    try:
        ipaddress.ip_address(canonical)
    except ValueError:
        pass
    else:
        raise PolicyError("allowlist 只接受域名，不接受 IP literal")
    if not re.fullmatch(r"[a-z0-9.-]+", canonical):
        raise PolicyError(f"host 含不允许字符：{host!r}")
    if ".." in canonical or canonical.startswith("."):
        raise PolicyError(f"host 结构无效：{host!r}")
    return canonical


def normalize_absolute_url(raw_url: str) -> tuple[str, str, str, int, str]:
    if not isinstance(raw_url, str):
        raise PolicyError("URL 必须是字符串")
    value = raw_url.strip()
    if not value or len(value) > MAX_URL_CHARS or CONTROL_RE.search(value):
        raise PolicyError("URL 为空、过长或包含控制字符")
    parsed = urlparse(value)
    if parsed.scheme.casefold() not in {"http", "https"}:
        raise PolicyError("URL scheme 必须是 http 或 https")
    if parsed.username is not None or parsed.password is not None:
        raise PolicyError("URL 不得包含 userinfo")
    if parsed.hostname is None:
        raise PolicyError("URL 缺少 host")
    host = canonical_host(parsed.hostname)
    scheme = parsed.scheme.casefold()
    try:
        explicit_port = parsed.port
    except ValueError as exc:
        raise PolicyError("URL port 无效") from exc
    port = explicit_port or (443 if scheme == "https" else 80)
    path = parsed.path or "/"
    decoded_path = unquote(path)
    if "\x00" in decoded_path or any(part == ".." for part in decoded_path.split("/")):
        raise PolicyError("URL path 含不安全的父目录或 NUL")
    default_port = 443 if scheme == "https" else 80
    netloc = host if port == default_port else f"{host}:{port}"
    normalized = urlunparse((scheme, netloc, path, "", parsed.query, ""))
    return normalized, host, scheme, port, path


def safe_url_for_log(url: str) -> str:
    try:
        parsed = urlparse(url)
        return urlunparse(
            (parsed.scheme, parsed.netloc, parsed.path or "/", "", "", "")
        )
    except Exception:
        return "<invalid-url>"


def default_resolver(host: str, port: int) -> list[str]:
    try:
        answers = socket.getaddrinfo(
            host,
            port,
            family=socket.AF_UNSPEC,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise PolicyError(f"DNS 解析失败：{host}") from exc
    addresses: list[str] = []
    for answer in answers:
        address = str(answer[4][0])
        if address not in addresses:
            addresses.append(address)
    return addresses


def assert_public_resolution(
    domain: DomainPolicy,
    resolver: Callable[[str, int], Sequence[str]],
) -> None:
    addresses = list(resolver(domain.host, domain.port))
    if not addresses:
        raise PolicyError(f"DNS 没有返回地址：{domain.host}")
    for raw_address in addresses:
        try:
            address = ipaddress.ip_address(raw_address)
        except ValueError as exc:
            raise PolicyError(f"DNS 返回无效 IP：{domain.host}") from exc
        if not address.is_global:
            raise PolicyError(
                f"SSRF 门禁拒绝非公网地址：{domain.host} -> {address.compressed}"
            )


def read_bounded_text(path: Path, max_bytes: int, label: str) -> str:
    if path.is_symlink():
        raise ConfigError(f"{label} 不能是符号链接：{path}")
    try:
        stat = path.stat()
    except OSError as exc:
        raise ConfigError(f"无法读取{label}：{path}") from exc
    if not path.is_file() or stat.st_size > max_bytes:
        raise ConfigError(f"{label}不是普通文件或超过 {max_bytes} 字节")
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ConfigError(f"{label}必须是 UTF-8 文本：{path}") from exc


def load_policy(path: Path) -> CollectionPolicy:
    text = read_bounded_text(path, MAX_CONFIG_BYTES, "配置文件")
    try:
        raw = yaml.load(text, Loader=StrictYamlLoader)
    except ConfigError:
        raise
    except yaml.YAMLError as exc:
        raise ConfigError(f"YAML 解析失败：{path}") from exc
    if not isinstance(raw, dict):
        raise ConfigError("配置顶层必须是 mapping")
    ensure_config_keys(
        raw,
        {
            "version",
            "user_agent",
            "min_delay_seconds",
            "timeout_seconds",
            "max_pages_per_run",
            "domains",
        },
        {"version", "user_agent", "domains"},
        "配置",
    )
    if raw["version"] != 1:
        raise ConfigError("配置 version 必须是 1")
    user_agent = raw["user_agent"]
    if (
        not isinstance(user_agent, str)
        or not user_agent.strip()
        or len(user_agent) > 256
        or CONTROL_RE.search(user_agent)
    ):
        raise ConfigError("user_agent 必须是 1—256 字符的可见字符串")
    product_token = re.split(r"[/\s]", user_agent.strip(), maxsplit=1)[0]
    if not PRODUCT_TOKEN_RE.fullmatch(product_token):
        raise ConfigError(
            "user_agent 的 product token 只允许 ASCII 字母、下划线和连字符"
        )

    min_delay = raw.get("min_delay_seconds", 10)
    timeout = raw.get("timeout_seconds", 20)
    max_pages = raw.get("max_pages_per_run", 30)
    if not is_plain_number(min_delay) or not (1 <= float(min_delay) <= 3600):
        raise ConfigError("min_delay_seconds 必须在 1—3600 之间")
    if not is_plain_number(timeout) or not (1 <= float(timeout) <= 60):
        raise ConfigError("timeout_seconds 必须在 1—60 之间")
    if not is_plain_int(max_pages) or not (1 <= max_pages <= 100):
        raise ConfigError("max_pages_per_run 必须在 1—100 之间")

    raw_domains = raw["domains"]
    if not isinstance(raw_domains, list) or not raw_domains:
        raise ConfigError("domains 必须是非空列表")
    domains: dict[str, DomainPolicy] = {}
    for index, item in enumerate(raw_domains):
        label = f"domains[{index}]"
        if not isinstance(item, dict):
            raise ConfigError(f"{label} 必须是 mapping")
        ensure_config_keys(
            item,
            {
                "host",
                "scheme",
                "port",
                "allowed_path_prefixes",
                "article_container",
            },
            {"host", "article_container"},
            label,
        )
        if not isinstance(item["host"], str):
            raise ConfigError(f"{label}.host 必须是字符串")
        try:
            host = canonical_host(item["host"])
        except PolicyError as exc:
            raise ConfigError(str(exc)) from exc
        if host in domains:
            raise ConfigError(f"domains 重复 host：{host}")
        scheme = item.get("scheme", "https")
        if not isinstance(scheme, str) or scheme.casefold() not in {"http", "https"}:
            raise ConfigError(f"{label}.scheme 必须是 http 或 https")
        scheme = scheme.casefold()
        port = item.get("port", 443 if scheme == "https" else 80)
        if not is_plain_int(port) or not (1 <= port <= 65535):
            raise ConfigError(f"{label}.port 必须在 1—65535 之间")
        raw_prefixes = item.get("allowed_path_prefixes", ["/"])
        if (
            not isinstance(raw_prefixes, list)
            or not raw_prefixes
            or not all(isinstance(value, str) for value in raw_prefixes)
        ):
            raise ConfigError(f"{label}.allowed_path_prefixes 必须是非空字符串列表")
        prefixes: list[str] = []
        for prefix in raw_prefixes:
            if (
                not prefix.startswith("/")
                or CONTROL_RE.search(prefix)
                or any(part == ".." for part in unquote(prefix).split("/"))
            ):
                raise ConfigError(f"{label} 含不安全 path prefix：{prefix!r}")
            if prefix not in prefixes:
                prefixes.append(prefix)
        raw_container = item["article_container"]
        if not isinstance(raw_container, dict):
            raise ConfigError(f"{label}.article_container 必须是 mapping")
        ensure_config_keys(
            raw_container,
            {"tag", "class"},
            {"tag", "class"},
            f"{label}.article_container",
        )
        tag = raw_container["tag"]
        class_name = raw_container["class"]
        if not isinstance(tag, str) or not TAG_RE.fullmatch(tag.casefold()):
            raise ConfigError(f"{label}.article_container.tag 无效")
        if (
            not isinstance(class_name, str)
            or not CLASS_TOKEN_RE.fullmatch(class_name)
        ):
            raise ConfigError(
                f"{label}.article_container.class 必须是单个 class token"
            )
        domains[host] = DomainPolicy(
            host=host,
            scheme=scheme,
            port=port,
            allowed_path_prefixes=tuple(prefixes),
            article_container=ArticleContainer(
                tag=tag.casefold(),
                class_name=class_name,
            ),
        )
    return CollectionPolicy(
        user_agent=user_agent.strip(),
        product_token=product_token,
        min_delay_seconds=float(min_delay),
        timeout_seconds=float(timeout),
        max_pages_per_run=max_pages,
        domains=domains,
    )


def load_explicit_urls(path: Path, policy: CollectionPolicy) -> list[str]:
    text = read_bounded_text(path, MAX_INPUT_BYTES, "URL 输入文件")
    urls: list[str] = []
    seen: set[str] = set()
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            normalized, _ = policy.domain_for_url(
                line,
                require_article_path=True,
            )
        except PolicyError as exc:
            raise ConfigError(f"URL 输入第 {line_number} 行无效：{exc}") from exc
        if normalized in seen:
            raise ConfigError(f"URL 输入含重复项：{safe_url_for_log(normalized)}")
        seen.add(normalized)
        urls.append(normalized)
    if not urls:
        raise ConfigError("URL 输入文件没有有效 URL")
    if len(urls) > policy.max_pages_per_run:
        raise ConfigError(
            f"URL 数量 {len(urls)} 超过策略上限 {policy.max_pages_per_run}"
        )
    return urls


def _attrs_map(attrs: Sequence[tuple[str, str | None]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_name, raw_value in attrs:
        result.setdefault(raw_name.casefold(), raw_value or "")
    return result


def normalize_metadata_text(value: Any, max_chars: int) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = " ".join(value.split())
    if not normalized or CONTROL_RE.search(normalized):
        return None
    if len(normalized) > max_chars:
        return None
    return normalized


def normalize_publication_date(value: Any) -> str | None:
    normalized = normalize_metadata_text(value, 100)
    if normalized is None:
        return None
    match = ISO_PREFIX_RE.match(normalized)
    if match is None:
        match = SLASH_DATE_RE.match(normalized)
    if match is None:
        match = CHINESE_DATE_RE.match(normalized)
    if match is None:
        return None
    try:
        parsed = date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None
    return parsed.isoformat()


def _jsonld_types(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value.casefold()}
    if isinstance(value, list):
        return {
            item.casefold()
            for item in value
            if isinstance(item, str)
        }
    return set()


def _jsonld_author_names(value: Any) -> list[str]:
    candidates = value if isinstance(value, list) else [value]
    names: list[str] = []
    for candidate in candidates:
        raw_name: Any = None
        if isinstance(candidate, str):
            raw_name = candidate
        elif isinstance(candidate, dict):
            raw_name = candidate.get("name")
        name = normalize_metadata_text(raw_name, MAX_AUTHOR_CHARS)
        if name is not None and not name.casefold().startswith(("http://", "https://")):
            if name not in names:
                names.append(name)
        if len(names) >= MAX_AUTHORS:
            break
    return names


class ArticleStatsParser(HTMLParser):
    """Project an article page into metadata and integer-only structure stats."""

    def __init__(self, container: ArticleContainer) -> None:
        super().__init__(convert_charrefs=True)
        self.container = container
        self.container_matches = 0
        self.in_article = False
        self.article_closed = False
        self.article_stack: list[str] = []
        self.structure_errors: list[str] = []
        self.skip_depth = 0

        self.title_candidates: list[tuple[int, str]] = []
        self.date_candidates: list[tuple[int, str]] = []
        self.author_candidates: list[tuple[int, list[str]]] = []
        self.column_candidates: list[tuple[int, str]] = []
        self.title_capture = False
        self.title_parts: list[str] = []
        self.jsonld_capture = False
        self.jsonld_parts: list[str] = []
        self.jsonld_chars = 0
        self.jsonld_overflow = False

        self.visible_char_count = 0
        self.paragraph_lengths: list[int] = []
        self.sentence_lengths: list[int] = []
        self.heading_counts = {"h1": 0, "h2": 0, "h3": 0}
        self.heading_level_sequence: list[int] = []
        self.list_count = 0
        self.list_item_count = 0
        self.blockquote_count = 0
        self.figure_count = 0
        self.image_count = 0
        self.caption_count = 0
        self.link_count = 0
        self.image_char_positions: list[int] = []

        self.current_paragraph_len: int | None = None
        self.current_sentence_len = 0
        self.current_heading: tuple[int, int] | None = None
        self.current_caption_len: int | None = None

    def _is_container(
        self,
        tag: str,
        attrs: Sequence[tuple[str, str | None]],
    ) -> bool:
        if tag.casefold() != self.container.tag:
            return False
        classes = set(_attrs_map(attrs).get("class", "").split())
        return self.container.class_name in classes

    def _metadata_start(
        self,
        tag: str,
        attrs: Sequence[tuple[str, str | None]],
    ) -> None:
        attribute_map = _attrs_map(attrs)
        if tag == "title":
            self.title_capture = True
            self.title_parts = []
        if tag == "script" and attribute_map.get("type", "").casefold() == "application/ld+json":
            self.jsonld_capture = True
            self.jsonld_parts = []
            self.jsonld_chars = 0
            self.jsonld_overflow = False
        if tag == "meta":
            key = (
                attribute_map.get("property")
                or attribute_map.get("name")
                or attribute_map.get("itemprop")
                or ""
            ).casefold()
            content = attribute_map.get("content", "")
            if key == "og:title":
                self._add_title(10, content)
            elif key == "twitter:title":
                self._add_title(20, content)
            elif key in {"article:published_time", "datepublished"}:
                self._add_date(10, content)
            elif key in {"date", "pubdate"}:
                self._add_date(30, content)
            elif key in {"author", "article:author"}:
                name = normalize_metadata_text(content, MAX_AUTHOR_CHARS)
                if name and not name.casefold().startswith(("http://", "https://")):
                    self.author_candidates.append((20, [name]))
            elif key in {"article:section", "articlesection", "section"}:
                self._add_column(20, content)
        if tag == "time":
            value = attribute_map.get("datetime", "")
            itemprop = attribute_map.get("itemprop", "").casefold()
            self._add_date(20 if itemprop == "datepublished" else 40, value)

    def _metadata_end(self, tag: str) -> None:
        if tag == "title" and self.title_capture:
            self.title_capture = False
            self._add_title(50, "".join(self.title_parts))
            self.title_parts = []
        if tag == "script" and self.jsonld_capture:
            self.jsonld_capture = False
            if not self.jsonld_overflow:
                self._consume_jsonld("".join(self.jsonld_parts))
            self.jsonld_parts = []
            self.jsonld_chars = 0
            self.jsonld_overflow = False

    def _add_title(self, priority: int, value: Any) -> None:
        normalized = normalize_metadata_text(value, MAX_TITLE_CHARS)
        if normalized is not None:
            self.title_candidates.append((priority, normalized))

    def _add_date(self, priority: int, value: Any) -> None:
        normalized = normalize_metadata_text(value, 100)
        if normalized is not None:
            self.date_candidates.append((priority, normalized))

    def _add_column(self, priority: int, value: Any) -> None:
        normalized = normalize_metadata_text(value, MAX_COLUMN_CHARS)
        if normalized is not None:
            self.column_candidates.append((priority, normalized))

    def _consume_jsonld(self, raw_json: str) -> None:
        if not raw_json.strip():
            return
        try:
            payload = json.loads(raw_json)
        except (json.JSONDecodeError, RecursionError):
            return

        def visit(node: Any) -> None:
            if isinstance(node, list):
                for item in node[:100]:
                    visit(item)
                return
            if not isinstance(node, dict):
                return
            node_types = _jsonld_types(node.get("@type"))
            if node_types & ARTICLE_JSONLD_TYPES:
                self._add_title(15, node.get("headline"))
                self._add_date(15, node.get("datePublished"))
                names = _jsonld_author_names(node.get("author"))
                if names:
                    self.author_candidates.append((15, names))
                section = node.get("articleSection")
                if isinstance(section, list):
                    section = next(
                        (item for item in section if isinstance(item, str)),
                        None,
                    )
                self._add_column(15, section)
            graph = node.get("@graph")
            if isinstance(graph, (list, dict)):
                visit(graph)

        visit(payload)

    def _article_start(
        self,
        tag: str,
        attrs: Sequence[tuple[str, str | None]],
        *,
        self_closing: bool,
    ) -> None:
        if tag in SKIP_STRUCTURE_TAGS:
            if not self_closing:
                self.skip_depth += 1
            return
        if self.skip_depth:
            return
        attribute_map = _attrs_map(attrs)
        if tag == "p":
            if self.current_paragraph_len is not None:
                self.structure_errors.append("nested paragraph")
                self._finish_paragraph()
            self.current_paragraph_len = 0
            self.current_sentence_len = 0
        elif tag in {"h1", "h2", "h3"}:
            if self.current_heading is not None:
                self.structure_errors.append("nested heading")
                self._finish_heading()
            self.current_heading = (int(tag[1]), 0)
        elif tag == "figcaption":
            if self.current_caption_len is not None:
                self.structure_errors.append("nested figcaption")
                self._finish_caption()
            self.current_caption_len = 0
        elif tag in {"ul", "ol"}:
            self.list_count += 1
        elif tag == "li":
            self.list_item_count += 1
        elif tag == "blockquote":
            self.blockquote_count += 1
        elif tag == "figure":
            self.figure_count += 1
        elif tag == "img":
            self.image_count += 1
            self.image_char_positions.append(self.visible_char_count)
        elif tag == "a" and attribute_map.get("href"):
            self.link_count += 1

    def _article_end(self, tag: str) -> None:
        if tag in SKIP_STRUCTURE_TAGS:
            if self.skip_depth > 0:
                self.skip_depth -= 1
            return
        if self.skip_depth:
            return
        if tag == "p" and self.current_paragraph_len is not None:
            self._finish_paragraph()
        elif tag in {"h1", "h2", "h3"} and self.current_heading is not None:
            self._finish_heading()
        elif tag == "figcaption" and self.current_caption_len is not None:
            self._finish_caption()

    def _finish_paragraph(self) -> None:
        if self.current_paragraph_len is None:
            return
        if self.current_sentence_len > 0:
            self.sentence_lengths.append(self.current_sentence_len)
        if self.current_paragraph_len > 0:
            self.paragraph_lengths.append(self.current_paragraph_len)
        self.current_paragraph_len = None
        self.current_sentence_len = 0

    def _finish_heading(self) -> None:
        if self.current_heading is None:
            return
        level, length = self.current_heading
        if length > 0:
            key = f"h{level}"
            self.heading_counts[key] += 1
            self.heading_level_sequence.append(level)
        self.current_heading = None

    def _finish_caption(self) -> None:
        if self.current_caption_len is None:
            return
        if self.current_caption_len > 0:
            self.caption_count += 1
        self.current_caption_len = None

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        normalized_tag = tag.casefold()
        self._metadata_start(normalized_tag, attrs)
        is_container = self._is_container(normalized_tag, attrs)
        if is_container:
            self.container_matches += 1
            if self.in_article or self.article_closed:
                self.structure_errors.append("multiple article containers")
            elif normalized_tag in VOID_TAGS:
                self.structure_errors.append("article container is void")
            else:
                self.in_article = True
                self.article_stack = [normalized_tag]
            return
        if not self.in_article:
            return
        self._article_start(normalized_tag, attrs, self_closing=False)
        if normalized_tag not in VOID_TAGS:
            self.article_stack.append(normalized_tag)

    def handle_startendtag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        normalized_tag = tag.casefold()
        self._metadata_start(normalized_tag, attrs)
        self._metadata_end(normalized_tag)
        if self._is_container(normalized_tag, attrs):
            self.container_matches += 1
            self.structure_errors.append("article container is self-closing")
            return
        if self.in_article:
            self._article_start(normalized_tag, attrs, self_closing=True)

    def handle_endtag(self, tag: str) -> None:
        normalized_tag = tag.casefold()
        self._metadata_end(normalized_tag)
        if not self.in_article:
            return
        self._article_end(normalized_tag)
        if not self.article_stack:
            self.structure_errors.append("article stack underflow")
            return
        if self.article_stack[-1] != normalized_tag:
            self.structure_errors.append(
                f"misnested closing tag {normalized_tag}"
            )
            if normalized_tag not in self.article_stack:
                return
            while self.article_stack and self.article_stack[-1] != normalized_tag:
                self.article_stack.pop()
        if self.article_stack and self.article_stack[-1] == normalized_tag:
            self.article_stack.pop()
        if not self.article_stack:
            self.in_article = False
            self.article_closed = True
            self.skip_depth = 0

    def handle_data(self, data: str) -> None:
        if self.title_capture:
            current = sum(len(part) for part in self.title_parts)
            remaining = MAX_TITLE_CHARS + 1 - current
            if remaining > 0:
                self.title_parts.append(data[:remaining])
        if self.jsonld_capture and not self.jsonld_overflow:
            remaining = MAX_JSON_LD_CHARS - self.jsonld_chars
            if len(data) > remaining:
                self.jsonld_overflow = True
                self.jsonld_parts = []
            else:
                self.jsonld_parts.append(data)
                self.jsonld_chars += len(data)
        if not self.in_article or self.skip_depth:
            return
        visible_chars = [character for character in data if not character.isspace()]
        count = len(visible_chars)
        if count == 0:
            return
        self.visible_char_count += count
        if self.current_paragraph_len is not None:
            self.current_paragraph_len += count
            for character in visible_chars:
                self.current_sentence_len += 1
                if character in SENTENCE_ENDINGS:
                    self.sentence_lengths.append(self.current_sentence_len)
                    self.current_sentence_len = 0
        if self.current_heading is not None:
            level, length = self.current_heading
            self.current_heading = (level, length + count)
        if self.current_caption_len is not None:
            self.current_caption_len += count

    def close(self) -> None:
        super().close()
        if self.in_article or self.article_stack:
            self.structure_errors.append("article container not closed")
        if self.current_paragraph_len is not None:
            self._finish_paragraph()
        if self.current_heading is not None:
            self._finish_heading()
        if self.current_caption_len is not None:
            self._finish_caption()

    def _selected_title(self) -> str:
        if not self.title_candidates:
            raise ExtractionError("页面缺少可用标题元数据")
        return sorted(self.title_candidates, key=lambda item: item[0])[0][1]

    def _selected_date(self) -> str | None:
        for _, candidate in sorted(self.date_candidates, key=lambda item: item[0]):
            normalized = normalize_publication_date(candidate)
            if normalized is not None:
                return normalized
        return None

    def _selected_authors(self) -> list[str]:
        if not self.author_candidates:
            return []
        names = sorted(self.author_candidates, key=lambda item: item[0])[0][1]
        return names[:MAX_AUTHORS]

    def _selected_column(self) -> str | None:
        if not self.column_candidates:
            return None
        return sorted(self.column_candidates, key=lambda item: item[0])[0][1]

    def record(self, final_url: str) -> dict[str, Any]:
        if self.container_matches != 1:
            raise ExtractionError(
                f"article_container 命中 {self.container_matches} 次，必须恰好 1 次"
            )
        if self.structure_errors:
            unique = sorted(set(self.structure_errors))
            raise ExtractionError(
                "article_container 结构异常：" + ", ".join(unique[:5])
            )
        if self.visible_char_count <= 0:
            raise ExtractionError("article_container 没有可见文本")
        paragraph_stats = length_stats(self.paragraph_lengths, include_quartiles=True)
        sentence_stats = length_stats(self.sentence_lengths, include_quartiles=False)
        quartiles = [0, 0, 0, 0]
        for position in self.image_char_positions:
            index = min(
                3,
                int((position / max(1, self.visible_char_count)) * 4),
            )
            quartiles[index] += 1
        paragraphs = self.paragraph_lengths
        record = {
            "schema_version": 1,
            "url": final_url,
            "title": self._selected_title(),
            "published_date": self._selected_date(),
            "authors": self._selected_authors(),
            "column": self._selected_column(),
            "structure": {
                "visible_char_count": self.visible_char_count,
                "paragraph_count": len(paragraphs),
                "sentence_count": len(self.sentence_lengths),
                "heading_counts": dict(self.heading_counts),
                "heading_level_sequence": list(self.heading_level_sequence),
                "list_count": self.list_count,
                "list_item_count": self.list_item_count,
                "blockquote_count": self.blockquote_count,
                "figure_count": self.figure_count,
                "image_count": self.image_count,
                "caption_count": self.caption_count,
                "link_count": self.link_count,
                "paragraph_char_stats": paragraph_stats,
                "sentence_char_stats": sentence_stats,
                "short_paragraph_bins": {
                    "0_15": sum(1 for value in paragraphs if value <= 15),
                    "16_40": sum(1 for value in paragraphs if 16 <= value <= 40),
                    "41_80": sum(1 for value in paragraphs if 41 <= value <= 80),
                    "81_plus": sum(1 for value in paragraphs if value >= 81),
                },
                "lead_paragraph_chars": paragraphs[0] if paragraphs else 0,
                "closing_paragraph_chars": paragraphs[-1] if paragraphs else 0,
                "image_position_quartiles": quartiles,
            },
        }
        validate_record(record)
        return record


def percentile(values: Sequence[int], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    weight = position - lower
    return float(ordered[lower] * (1 - weight) + ordered[upper] * weight)


def compact_number(value: float) -> int | float:
    rounded = round(float(value), 2)
    if rounded.is_integer():
        return int(rounded)
    return rounded


def length_stats(
    values: Sequence[int],
    *,
    include_quartiles: bool,
) -> dict[str, int | float]:
    if not values:
        if include_quartiles:
            return {
                "min": 0,
                "p25": 0,
                "median": 0,
                "mean": 0,
                "p75": 0,
                "max": 0,
                "stddev": 0,
            }
        return {"min": 0, "median": 0, "mean": 0, "max": 0}
    result: dict[str, int | float] = {
        "min": min(values),
        "median": compact_number(statistics.median(values)),
        "mean": compact_number(statistics.fmean(values)),
        "max": max(values),
    }
    if include_quartiles:
        result["p25"] = compact_number(percentile(values, 0.25))
        result["p75"] = compact_number(percentile(values, 0.75))
        result["stddev"] = compact_number(statistics.pstdev(values))
        return {
            "min": result["min"],
            "p25": result["p25"],
            "median": result["median"],
            "mean": result["mean"],
            "p75": result["p75"],
            "max": result["max"],
            "stddev": result["stddev"],
        }
    return result


def media_type_and_charset(headers: Mapping[str, str]) -> tuple[str, str | None]:
    raw = headers.get("content-type", "")
    parts = [part.strip() for part in raw.split(";")]
    media_type = parts[0].casefold() if parts and parts[0] else ""
    charset: str | None = None
    for part in parts[1:]:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        if key.strip().casefold() == "charset":
            charset = value.strip().strip("\"'").casefold()
            break
    return media_type, charset


def decode_page_html(result: HttpResult, url: str) -> str:
    if len(result.body) > MAX_RESPONSE_BYTES:
        raise NetworkError(
            f"响应超过 {MAX_RESPONSE_BYTES} 字节上限：{safe_url_for_log(url)}"
        )
    media_type, declared_charset = media_type_and_charset(result.headers)
    if media_type not in ALLOWED_PAGE_CONTENT_TYPES:
        raise ExtractionError(
            f"页面 Content-Type 不是 HTML：{media_type or '<missing>'}"
        )
    encodings: list[str] = []
    if declared_charset:
        try:
            canonical = codecs.lookup(declared_charset).name
        except LookupError as exc:
            raise ExtractionError("页面声明了未知 charset") from exc
        if declared_charset not in ALLOWED_CHARSETS and canonical not in ALLOWED_CHARSETS:
            raise ExtractionError(f"页面 charset 不在允许列表：{declared_charset}")
        encodings.append(declared_charset)
    else:
        encodings.extend(["utf-8-sig", "utf-8", "gb18030"])
    for encoding in encodings:
        try:
            return result.body.decode(encoding, errors="strict")
        except UnicodeError:
            continue
    raise ExtractionError("页面无法按允许的 charset 严格解码")


class Collector:
    """Policy-enforcing collector with injectable transport, DNS, and clock."""

    def __init__(
        self,
        policy: CollectionPolicy,
        *,
        client: Any | None = None,
        resolver: Callable[[str, int], Sequence[str]] = default_resolver,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.policy = policy
        self.client = client or BoundedHttpClient()
        self.resolver = resolver
        self.limiter = HostRateLimiter(clock=clock, sleeper=sleeper)
        self.robots_cache: dict[str, RobotsRules] = {}

    def _request_once(
        self,
        url: str,
        domain: DomainPolicy,
        *,
        max_bytes: int,
        accept: str,
        delay_seconds: float,
    ) -> HttpResult:
        assert_public_resolution(domain, self.resolver)
        self.limiter.wait(domain.origin_key, delay_seconds)
        try:
            result = self.client.get(
                url,
                user_agent=self.policy.user_agent,
                timeout_seconds=self.policy.timeout_seconds,
                max_bytes=max_bytes,
                accept=accept,
            )
        finally:
            self.limiter.mark(domain.origin_key)
        if len(result.body) > max_bytes:
            raise NetworkError(
                f"响应超过 {max_bytes} 字节上限：{safe_url_for_log(url)}"
            )
        return result

    def _fetch_without_robots(
        self,
        start_url: str,
        *,
        max_bytes: int,
        accept: str,
    ) -> tuple[HttpResult, str]:
        current_url = start_url
        for redirect_count in range(MAX_REDIRECTS + 1):
            current_url, domain = self.policy.domain_for_url(
                current_url,
                require_article_path=False,
            )
            result = self._request_once(
                current_url,
                domain,
                max_bytes=max_bytes,
                accept=accept,
                delay_seconds=self.policy.min_delay_seconds,
            )
            if result.status not in REDIRECT_STATUSES:
                return result, current_url
            if redirect_count >= MAX_REDIRECTS:
                raise PolicyError("redirect 超过 5 次")
            location = result.headers.get("location", "")
            if not location or len(location) > MAX_URL_CHARS or CONTROL_RE.search(location):
                raise PolicyError("redirect Location 缺失、过长或含控制字符")
            current_url = urljoin(current_url, location)
        raise PolicyError("redirect 状态异常")

    def _robots_for(self, domain: DomainPolicy) -> RobotsRules:
        cached = self.robots_cache.get(domain.origin_key)
        if cached is not None:
            return cached
        robots_url = f"{domain.origin}/robots.txt"
        result, _ = self._fetch_without_robots(
            robots_url,
            max_bytes=MAX_ROBOTS_BYTES,
            accept="text/plain",
        )
        if result.status in ROBOTS_ABSENT_STATUSES:
            rules = RobotsRules(
                allow_all=True,
                parser=None,
                effective_delay_seconds=self.policy.min_delay_seconds,
            )
            self.robots_cache[domain.origin_key] = rules
            return rules
        if result.status != 200:
            raise PolicyError(
                f"robots 保守拒绝 HTTP {result.status}：{domain.origin}"
            )
        media_type, _ = media_type_and_charset(result.headers)
        if media_type and media_type not in {"text/plain", "application/octet-stream"}:
            raise PolicyError(
                f"robots Content-Type 不受支持：{media_type}"
            )
        try:
            text = result.body.decode("utf-8-sig", errors="strict")
        except UnicodeError as exc:
            raise PolicyError("robots 不是有效 UTF-8，保守拒绝") from exc
        parser = RobotFileParser()
        parser.parse(text.splitlines())
        delay_candidates = [self.policy.min_delay_seconds]
        crawl_delay = parser.crawl_delay(self.policy.product_token)
        if crawl_delay is not None:
            delay_candidates.append(float(crawl_delay))
        request_rate = parser.request_rate(self.policy.product_token)
        if request_rate is not None and request_rate.requests > 0:
            delay_candidates.append(
                float(request_rate.seconds) / float(request_rate.requests)
            )
        effective_delay = max(delay_candidates)
        if effective_delay > MAX_SLEEP_SECONDS:
            raise PolicyError(
                f"robots 要求 {effective_delay:.2f} 秒间隔，超过单次运行上限"
            )
        rules = RobotsRules(
            allow_all=False,
            parser=parser,
            effective_delay_seconds=effective_delay,
        )
        self.robots_cache[domain.origin_key] = rules
        return rules

    def _fetch_page(self, start_url: str) -> tuple[HttpResult, str, DomainPolicy]:
        current_url = start_url
        for redirect_count in range(MAX_REDIRECTS + 1):
            current_url, domain = self.policy.domain_for_url(
                current_url,
                require_article_path=True,
            )
            rules = self._robots_for(domain)
            if not rules.can_fetch(self.policy.product_token, current_url):
                raise PolicyError(
                    f"robots 禁止抓取：{safe_url_for_log(current_url)}"
                )
            result = self._request_once(
                current_url,
                domain,
                max_bytes=MAX_RESPONSE_BYTES,
                accept="text/html,application/xhtml+xml",
                delay_seconds=rules.effective_delay_seconds,
            )
            if result.status not in REDIRECT_STATUSES:
                return result, current_url, domain
            if redirect_count >= MAX_REDIRECTS:
                raise PolicyError("redirect 超过 5 次")
            location = result.headers.get("location", "")
            if not location or len(location) > MAX_URL_CHARS or CONTROL_RE.search(location):
                raise PolicyError("redirect Location 缺失、过长或含控制字符")
            current_url = urljoin(current_url, location)
        raise PolicyError("redirect 状态异常")

    def collect_url(self, url: str) -> dict[str, Any]:
        normalized, _ = self.policy.domain_for_url(
            url,
            require_article_path=True,
        )
        result, final_url, final_domain = self._fetch_page(normalized)
        if result.status != 200:
            raise NetworkError(
                f"页面返回 HTTP {result.status}：{safe_url_for_log(final_url)}"
            )
        html_text = decode_page_html(result, final_url)
        parser = ArticleStatsParser(final_domain.article_container)
        try:
            parser.feed(html_text)
            parser.close()
        except (AssertionError, RecursionError, ValueError) as exc:
            raise ExtractionError(
                f"HTML 解析失败：{safe_url_for_log(final_url)}"
            ) from exc
        finally:
            html_text = ""
        return parser.record(final_url)


def validate_short_text(
    value: Any,
    *,
    label: str,
    max_chars: int,
    nullable: bool,
) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str) or not value or len(value) > max_chars:
        raise SchemaError(f"{label} 必须是 1—{max_chars} 字符字符串")
    if CONTROL_RE.search(value):
        raise SchemaError(f"{label} 含控制字符")


def validate_count(value: Any, label: str) -> None:
    if not is_plain_int(value) or not (0 <= value <= MAX_STRUCTURE_COUNT):
        raise SchemaError(f"{label} 必须是非负整数")


def validate_numeric_map(
    value: Any,
    keys: set[str],
    label: str,
) -> None:
    if not isinstance(value, dict):
        raise SchemaError(f"{label} 必须是 mapping")
    ensure_exact_keys(value, keys, label)
    for key, item in value.items():
        if not is_plain_number(item) or not (0 <= float(item) <= MAX_STRUCTURE_COUNT):
            raise SchemaError(f"{label}.{key} 必须是非负有限数字")


def validate_record(record: Any) -> None:
    if not isinstance(record, dict):
        raise SchemaError("record 必须是 JSON object")
    ensure_exact_keys(record, TOP_LEVEL_RECORD_KEYS, "record")
    if record["schema_version"] != 1:
        raise SchemaError("schema_version 必须是 1")
    validate_short_text(
        record["url"],
        label="url",
        max_chars=MAX_URL_CHARS,
        nullable=False,
    )
    try:
        normalized_url, _, _, _, _ = normalize_absolute_url(record["url"])
    except PolicyError as exc:
        raise SchemaError(f"url 无效：{exc}") from exc
    if normalized_url != record["url"]:
        raise SchemaError("url 必须已经规范化且不含 fragment")
    validate_short_text(
        record["title"],
        label="title",
        max_chars=MAX_TITLE_CHARS,
        nullable=False,
    )
    published_date = record["published_date"]
    if published_date is not None:
        if (
            not isinstance(published_date, str)
            or normalize_publication_date(published_date) != published_date
        ):
            raise SchemaError("published_date 必须是 YYYY-MM-DD 或 null")
    authors = record["authors"]
    if not isinstance(authors, list) or len(authors) > MAX_AUTHORS:
        raise SchemaError("authors 必须是最多 20 项的列表")
    if len(authors) != len(set(authors)):
        raise SchemaError("authors 不得重复")
    for index, author in enumerate(authors):
        validate_short_text(
            author,
            label=f"authors[{index}]",
            max_chars=MAX_AUTHOR_CHARS,
            nullable=False,
        )
    validate_short_text(
        record["column"],
        label="column",
        max_chars=MAX_COLUMN_CHARS,
        nullable=True,
    )
    structure = record["structure"]
    if not isinstance(structure, dict):
        raise SchemaError("structure 必须是 mapping")
    ensure_exact_keys(structure, STRUCTURE_KEYS, "structure")
    for key in {
        "visible_char_count",
        "paragraph_count",
        "sentence_count",
        "list_count",
        "list_item_count",
        "blockquote_count",
        "figure_count",
        "image_count",
        "caption_count",
        "link_count",
        "lead_paragraph_chars",
        "closing_paragraph_chars",
    }:
        validate_count(structure[key], f"structure.{key}")
    heading_counts = structure["heading_counts"]
    if not isinstance(heading_counts, dict):
        raise SchemaError("structure.heading_counts 必须是 mapping")
    ensure_exact_keys(heading_counts, HEADING_COUNT_KEYS, "structure.heading_counts")
    for key, value in heading_counts.items():
        validate_count(value, f"structure.heading_counts.{key}")
    heading_sequence = structure["heading_level_sequence"]
    if (
        not isinstance(heading_sequence, list)
        or len(heading_sequence) > MAX_STRUCTURE_COUNT
        or any(not is_plain_int(value) or value not in {1, 2, 3} for value in heading_sequence)
    ):
        raise SchemaError("heading_level_sequence 只能包含 1、2、3")
    validate_numeric_map(
        structure["paragraph_char_stats"],
        PARAGRAPH_STAT_KEYS,
        "structure.paragraph_char_stats",
    )
    validate_numeric_map(
        structure["sentence_char_stats"],
        SENTENCE_STAT_KEYS,
        "structure.sentence_char_stats",
    )
    paragraph_bins = structure["short_paragraph_bins"]
    if not isinstance(paragraph_bins, dict):
        raise SchemaError("short_paragraph_bins 必须是 mapping")
    ensure_exact_keys(paragraph_bins, PARAGRAPH_BIN_KEYS, "short_paragraph_bins")
    for key, value in paragraph_bins.items():
        validate_count(value, f"short_paragraph_bins.{key}")
    quartiles = structure["image_position_quartiles"]
    if (
        not isinstance(quartiles, list)
        or len(quartiles) != 4
        or any(not is_plain_int(value) or value < 0 for value in quartiles)
    ):
        raise SchemaError("image_position_quartiles 必须是 4 个非负整数")
    if sum(quartiles) != structure["image_count"]:
        raise SchemaError("image_position_quartiles 之和必须等于 image_count")
    if sum(heading_counts.values()) != len(heading_sequence):
        raise SchemaError("heading_counts 必须与 heading_level_sequence 一致")
    if sum(paragraph_bins.values()) != structure["paragraph_count"]:
        raise SchemaError("short_paragraph_bins 之和必须等于 paragraph_count")


def reject_duplicate_json_keys(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SchemaError(f"JSON 含重复键：{key}")
        result[key] = value
    return result


def read_corpus(path: Path) -> list[dict[str, Any]]:
    if path.is_symlink():
        raise SchemaError("corpus 不能是符号链接")
    try:
        stat = path.stat()
    except OSError as exc:
        raise SchemaError(f"无法读取 corpus：{path}") from exc
    if not path.is_file() or stat.st_size > MAX_CORPUS_BYTES:
        raise SchemaError("corpus 不是普通文件或超过大小上限")
    records: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    previous_url: str | None = None
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                if len(raw_line.encode("utf-8")) > MAX_JSON_LINE_BYTES:
                    raise SchemaError(f"corpus 第 {line_number} 行超过大小上限")
                line = raw_line.strip()
                if not line:
                    raise SchemaError(f"corpus 第 {line_number} 行为空")
                try:
                    record = json.loads(
                        line,
                        object_pairs_hook=reject_duplicate_json_keys,
                    )
                except json.JSONDecodeError as exc:
                    raise SchemaError(
                        f"corpus 第 {line_number} 行不是有效 JSON"
                    ) from exc
                validate_record(record)
                url = record["url"]
                if url in seen_urls:
                    raise SchemaError(f"corpus URL 重复：{safe_url_for_log(url)}")
                if previous_url is not None and url < previous_url:
                    raise SchemaError("corpus 必须按 url 升序排列")
                seen_urls.add(url)
                previous_url = url
                records.append(record)
    except UnicodeError as exc:
        raise SchemaError("corpus 必须是有效 UTF-8") from exc
    if not records:
        raise SchemaError("corpus 不能为空")
    return records


def is_link_like(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        stat = path.lstat()
    except FileNotFoundError:
        return False
    attributes = getattr(stat, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse_flag)


def atomic_write_text(path: Path, content: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise OutputError(f"无法创建输出目录：{path.parent}") from exc
    for ancestor in (path.parent, *path.parent.parents):
        if is_link_like(ancestor):
            raise OutputError(f"输出路径祖先不能是 link/junction：{ancestor}")
    if path.exists() or path.is_symlink():
        if is_link_like(path) or not path.is_file():
            raise OutputError(f"输出目标必须是普通文件：{path}")
        if path.stat().st_nlink != 1:
            raise OutputError(f"输出目标不能是 hardlink：{path}")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    except OSError as exc:
        raise OutputError(f"无法原子写入：{path}") from exc
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass


def serialize_records(records: Sequence[Mapping[str, Any]]) -> str:
    if not records:
        raise SchemaError("不能写入空 corpus")
    ordered = sorted(records, key=lambda record: str(record["url"]))
    urls: set[str] = set()
    lines: list[str] = []
    for record in ordered:
        validate_record(record)
        url = str(record["url"])
        if url in urls:
            raise SchemaError(f"最终 URL 重复：{safe_url_for_log(url)}")
        urls.add(url)
        lines.append(
            json.dumps(
                record,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
    return "\n".join(lines) + "\n"


def policy_fingerprint(policy_path: Path) -> str:
    try:
        payload = policy_path.read_bytes()
    except OSError as exc:
        raise ConfigError(f"无法计算配置 hash：{policy_path}") from exc
    return hashlib.sha256(payload).hexdigest()


def plan_payload(
    policy: CollectionPolicy,
    urls: Sequence[str],
    *,
    policy_sha256: str,
    mode: str,
) -> dict[str, Any]:
    host_counts: dict[str, int] = {}
    for url in urls:
        _, domain = policy.domain_for_url(url, require_article_path=True)
        host_counts[domain.host] = host_counts.get(domain.host, 0) + 1
    return {
        "mode": mode,
        "network": "none",
        "policy_sha256": policy_sha256,
        "url_count": len(urls),
        "hosts": dict(sorted(host_counts.items())),
        "max_response_bytes": MAX_RESPONSE_BYTES,
        "min_delay_seconds": policy.min_delay_seconds,
        "urls": list(urls),
    }


def command_plan(args: argparse.Namespace) -> int:
    policy = load_policy(args.config)
    urls = load_explicit_urls(args.input, policy)
    payload = plan_payload(
        policy,
        urls,
        policy_sha256=policy_fingerprint(args.config),
        mode="plan",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def command_collect(args: argparse.Namespace) -> int:
    policy = load_policy(args.config)
    urls = load_explicit_urls(args.input, policy)
    if not args.execute:
        payload = plan_payload(
            policy,
            urls,
            policy_sha256=policy_fingerprint(args.config),
            mode="collect-dry-run",
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print("[dry-run] 未发起网络请求，未写入 corpus。添加 --execute 才会抓取。")
        return 0
    collector = Collector(policy)
    records = [collector.collect_url(url) for url in urls]
    serialized = serialize_records(records)
    atomic_write_text(args.output, serialized)
    print(f"[ok] 已写入 {len(records)} 条 metadata/structure-only 记录：{args.output}")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    records = read_corpus(args.corpus)
    print(f"[pass] corpus schema 有效：{len(records)} 条记录")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "从显式科技媒体 URL 生成只含 URL、标题、日期、作者、栏目和结构统计的衍生语料。"
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="本地校验策略和显式 URL；不联网")
    plan.add_argument("--config", type=Path, required=True, help="YAML 策略文件")
    plan.add_argument("--input", type=Path, required=True, help="每行一个 URL 的 UTF-8 文件")
    plan.set_defaults(handler=command_plan)

    collect = subparsers.add_parser(
        "collect",
        help="默认 dry-run；--execute 后才联网并原子写 corpus",
    )
    collect.add_argument("--config", type=Path, required=True, help="YAML 策略文件")
    collect.add_argument("--input", type=Path, required=True, help="每行一个 URL 的 UTF-8 文件")
    collect.add_argument("--output", type=Path, required=True, help="输出 JSONL corpus")
    collect.add_argument(
        "--execute",
        action="store_true",
        help="执行有界网络抓取；未提供时始终为零网络 dry-run",
    )
    collect.set_defaults(handler=command_collect)

    validate = subparsers.add_parser("validate", help="严格校验已有 JSONL corpus")
    validate.add_argument("--corpus", type=Path, required=True)
    validate.set_defaults(handler=command_validate)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    configure_utf8_stdio()
    args = build_parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except DerivedCorpusError as exc:
        print(f"[fail] {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("[fail] 操作被中断", file=sys.stderr)
        return 130
    except Exception as exc:
        print(
            f"[fail] unexpected {type(exc).__name__}; 未输出异常载荷",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
