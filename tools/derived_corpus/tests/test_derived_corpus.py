from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "derived_corpus.py"
SPEC = importlib.util.spec_from_file_location("derived_corpus_under_test", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


PUBLIC_IP = "93.184.216.34"
SECRET_BODY = "这段正文绝不能出现在 JSON、日志或异常中。"


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0
        self.sleeps: list[float] = []

    def now(self) -> float:
        return self.value

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.value += seconds


class FakeClient:
    def __init__(self, responses: dict[str, object]) -> None:
        self.responses = responses
        self.calls: list[str] = []

    def get(
        self,
        url: str,
        *,
        user_agent: str,
        timeout_seconds: float,
        max_bytes: int,
        accept: str,
    ):
        self.calls.append(url)
        response = self.responses[url]
        if isinstance(response, list):
            if not response:
                raise AssertionError(f"no fake response left for {url}")
            response = response.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def response(
    status: int,
    body: bytes = b"",
    *,
    content_type: str | None = None,
    location: str | None = None,
):
    headers: dict[str, str] = {}
    if content_type is not None:
        headers["content-type"] = content_type
    if location is not None:
        headers["location"] = location
    return MODULE.HttpResult(status=status, headers=headers, body=body)


def synthetic_html(title: str = "一篇合成科技文章") -> bytes:
    html = f"""<!doctype html>
<html>
<head>
  <title>后备标题</title>
  <meta property="og:title" content="{title}">
  <meta property="article:published_time" content="2026-07-25T08:00:00+08:00">
  <meta name="author" content="测试作者">
  <meta property="article:section" content="人工智能">
  <script type="application/ld+json">{{
    "@type": "NewsArticle",
    "headline": "JSON-LD 标题",
    "datePublished": "2026-07-24",
    "author": {{"name": "JSON-LD 作者"}},
    "articleSection": "科技",
    "articleBody": "{SECRET_BODY}"
  }}</script>
</head>
<body>
  <nav>导航文字不应计入</nav>
  <article class="feature article-body">
    <p>第一句。第二句更长！</p>
    <h2>第一个小标题</h2>
    <p>第三段有<a href="https://example.com/ref">一个链接</a>。</p>
    <blockquote>引用结构</blockquote>
    <ul><li>列表一</li><li>列表二</li></ul>
    <figure><img src="not-fetched.jpg"><figcaption>合成图注</figcaption></figure>
    <script>{SECRET_BODY}</script>
    <h3>第二个小标题</h3>
    <p>结尾。</p>
  </article>
</body>
</html>"""
    return html.encode("utf-8")


class DerivedCorpusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir_obj = tempfile.TemporaryDirectory(prefix="衍生语料 测试 ")
        self.root = Path(self.temp_dir_obj.name)
        self.config = self.root / "policy.yml"
        self.urls = self.root / "urls.txt"
        self.output = self.root / "records.jsonl"
        self.write_policy()

    def tearDown(self) -> None:
        self.temp_dir_obj.cleanup()

    def write_policy(
        self,
        *,
        second_domain: str | None = None,
        min_delay: int = 1,
    ) -> None:
        domains = """
  - host: "example.com"
    scheme: "https"
    port: 443
    allowed_path_prefixes: ["/articles/"]
    article_container:
      tag: "article"
      class: "article-body"
"""
        if second_domain is not None:
            domains += f"""
  - host: "{second_domain}"
    scheme: "https"
    port: 443
    allowed_path_prefixes: ["/articles/"]
    article_container:
      tag: "article"
      class: "article-body"
"""
        self.config.write_text(
            f"""version: 1
user_agent: "TechMediaDerivedCorpusBot/0.1 (+https://example.org/bot)"
min_delay_seconds: {min_delay}
timeout_seconds: 10
max_pages_per_run: 10
domains:
{domains}""",
            encoding="utf-8",
            newline="\n",
        )

    def policy(self):
        return MODULE.load_policy(self.config)

    @staticmethod
    def public_resolver(host: str, port: int) -> list[str]:
        return [PUBLIC_IP]

    def collector(
        self,
        fake_client: FakeClient,
        *,
        resolver=None,
        clock: FakeClock | None = None,
    ):
        fake_clock = clock or FakeClock()
        return MODULE.Collector(
            self.policy(),
            client=fake_client,
            resolver=resolver or self.public_resolver,
            clock=fake_clock.now,
            sleeper=fake_clock.sleep,
        )

    def test_exact_host_userinfo_and_parent_path_are_rejected(self) -> None:
        policy = self.policy()
        bad_urls = [
            "https://example.com.evil.invalid/articles/1",
            "https://user:pass@example.com/articles/1",
            "https://example.com/articles/../admin",
            "https://example.com.evil.invalid/articles/1#x",
        ]
        for bad_url in bad_urls:
            with self.subTest(url=bad_url), self.assertRaises(MODULE.PolicyError):
                policy.domain_for_url(bad_url, require_article_path=True)

    def test_private_dns_is_rejected_before_http(self) -> None:
        page_url = "https://example.com/articles/1"
        client = FakeClient({})
        collector = self.collector(
            client,
            resolver=lambda host, port: ["127.0.0.1"],
        )
        with self.assertRaisesRegex(MODULE.PolicyError, "SSRF"):
            collector.collect_url(page_url)
        self.assertEqual(client.calls, [])

    def test_robots_disallow_blocks_article_request(self) -> None:
        page_url = "https://example.com/articles/private"
        robots_url = "https://example.com/robots.txt"
        client = FakeClient(
            {
                robots_url: response(
                    200,
                    b"User-agent: TechMediaDerivedCorpusBot\nDisallow: /articles/private\n",
                    content_type="text/plain",
                )
            }
        )
        collector = self.collector(client)
        with self.assertRaisesRegex(MODULE.PolicyError, "robots"):
            collector.collect_url(page_url)
        self.assertEqual(client.calls, [robots_url])

    def test_robots_500_is_conservative_deny(self) -> None:
        page_url = "https://example.com/articles/1"
        robots_url = "https://example.com/robots.txt"
        client = FakeClient({robots_url: response(500)})
        collector = self.collector(client)
        with self.assertRaisesRegex(MODULE.PolicyError, "保守拒绝"):
            collector.collect_url(page_url)
        self.assertEqual(client.calls, [robots_url])

    def test_robots_404_allows_collection_and_extracts_structure(self) -> None:
        page_url = "https://example.com/articles/1"
        robots_url = "https://example.com/robots.txt"
        client = FakeClient(
            {
                robots_url: response(404),
                page_url: response(
                    200,
                    synthetic_html(),
                    content_type="text/html; charset=utf-8",
                ),
            }
        )
        record = self.collector(client).collect_url(page_url)
        self.assertEqual(record["url"], page_url)
        self.assertEqual(record["title"], "一篇合成科技文章")
        self.assertEqual(record["published_date"], "2026-07-25")
        self.assertEqual(record["authors"], ["JSON-LD 作者"])
        self.assertEqual(record["column"], "科技")
        structure = record["structure"]
        self.assertEqual(structure["paragraph_count"], 3)
        self.assertEqual(structure["sentence_count"], 4)
        self.assertEqual(structure["heading_counts"], {"h1": 0, "h2": 1, "h3": 1})
        self.assertEqual(structure["heading_level_sequence"], [2, 3])
        self.assertEqual(structure["list_count"], 1)
        self.assertEqual(structure["list_item_count"], 2)
        self.assertEqual(structure["blockquote_count"], 1)
        self.assertEqual(structure["figure_count"], 1)
        self.assertEqual(structure["image_count"], 1)
        self.assertEqual(structure["caption_count"], 1)
        self.assertEqual(structure["link_count"], 1)
        MODULE.validate_record(record)

    def test_body_and_html_never_enter_serialized_record(self) -> None:
        page_url = "https://example.com/articles/1"
        client = FakeClient(
            {
                "https://example.com/robots.txt": response(404),
                page_url: response(
                    200,
                    synthetic_html(),
                    content_type="text/html; charset=utf-8",
                ),
            }
        )
        record = self.collector(client).collect_url(page_url)
        serialized = MODULE.serialize_records([record])
        self.assertNotIn(SECRET_BODY, serialized)
        self.assertNotIn("<article", serialized)
        self.assertNotIn("第一句", serialized)
        self.assertEqual(set(record), MODULE.TOP_LEVEL_RECORD_KEYS)

    def test_redirect_to_unallowlisted_host_is_blocked_before_second_get(self) -> None:
        start_url = "https://example.com/articles/start"
        robots_url = "https://example.com/robots.txt"
        client = FakeClient(
            {
                robots_url: response(404),
                start_url: response(
                    302,
                    location="https://evil.invalid/articles/end",
                ),
            }
        )
        collector = self.collector(client)
        with self.assertRaisesRegex(MODULE.PolicyError, "exact allowlist"):
            collector.collect_url(start_url)
        self.assertEqual(client.calls, [robots_url, start_url])

    def test_redirect_target_private_dns_is_blocked(self) -> None:
        self.write_policy(second_domain="target.example")
        start_url = "https://example.com/articles/start"
        target_url = "https://target.example/articles/end"
        client = FakeClient(
            {
                "https://example.com/robots.txt": response(404),
                start_url: response(302, location=target_url),
            }
        )

        def resolver(host: str, port: int) -> list[str]:
            return ["10.0.0.8"] if host == "target.example" else [PUBLIC_IP]

        collector = self.collector(client, resolver=resolver)
        with self.assertRaisesRegex(MODULE.PolicyError, "SSRF"):
            collector.collect_url(start_url)
        self.assertNotIn("https://target.example/robots.txt", client.calls)
        self.assertNotIn(target_url, client.calls)

    def test_two_pages_share_robots_cache_and_are_rate_limited(self) -> None:
        first = "https://example.com/articles/1"
        second = "https://example.com/articles/2"
        robots = "https://example.com/robots.txt"
        client = FakeClient(
            {
                robots: response(404),
                first: response(200, synthetic_html("第一篇"), content_type="text/html"),
                second: response(200, synthetic_html("第二篇"), content_type="text/html"),
            }
        )
        clock = FakeClock()
        collector = self.collector(client, clock=clock)
        collector.collect_url(first)
        collector.collect_url(second)
        self.assertEqual(client.calls, [robots, first, second])
        self.assertEqual(clock.sleeps, [1.0, 1.0])

    def test_response_over_two_mib_is_rejected_even_with_fake_transport(self) -> None:
        page_url = "https://example.com/articles/large"
        client = FakeClient(
            {
                "https://example.com/robots.txt": response(404),
                page_url: response(
                    200,
                    b"x" * (MODULE.MAX_RESPONSE_BYTES + 1),
                    content_type="text/html",
                ),
            }
        )
        with self.assertRaisesRegex(MODULE.NetworkError, "字节上限"):
            self.collector(client).collect_url(page_url)

    def test_missing_or_multiple_container_fails_loud(self) -> None:
        variants = [
            b"<html><head><meta property='og:title' content='x'></head><body><p>x</p></body></html>",
            b"<html><head><meta property='og:title' content='x'></head><body><article class='article-body'><p>x</p></article><article class='article-body'><p>y</p></article></body></html>",
        ]
        for index, body in enumerate(variants):
            with self.subTest(index=index):
                page_url = f"https://example.com/articles/{index}"
                client = FakeClient(
                    {
                        "https://example.com/robots.txt": response(404),
                        page_url: response(200, body, content_type="text/html"),
                    }
                )
                with self.assertRaises(MODULE.ExtractionError):
                    self.collector(client).collect_url(page_url)

    def test_collect_without_execute_is_zero_network_and_zero_write(self) -> None:
        self.urls.write_text(
            "https://example.com/articles/1\n",
            encoding="utf-8",
            newline="\n",
        )
        stdout = io.StringIO()
        with mock.patch.object(
            MODULE.BoundedHttpClient,
            "get",
            side_effect=AssertionError("dry-run attempted network"),
        ), contextlib.redirect_stdout(stdout):
            code = MODULE.main(
                [
                    "collect",
                    "--config",
                    str(self.config),
                    "--input",
                    str(self.urls),
                    "--output",
                    str(self.output),
                ]
            )
        self.assertEqual(code, 0)
        self.assertIn("[dry-run]", stdout.getvalue())
        self.assertFalse(self.output.exists())

    def test_validate_rejects_unknown_body_field(self) -> None:
        parser = MODULE.ArticleStatsParser(
            MODULE.ArticleContainer(tag="article", class_name="article-body")
        )
        parser.feed(synthetic_html().decode("utf-8"))
        parser.close()
        record = parser.record("https://example.com/articles/1")
        record["body"] = SECRET_BODY
        with self.assertRaisesRegex(MODULE.SchemaError, "未知字段"):
            MODULE.validate_record(record)

    def test_atomic_write_failure_preserves_existing_file(self) -> None:
        self.output.write_text("old\n", encoding="utf-8", newline="\n")
        with mock.patch.object(MODULE.os, "replace", side_effect=OSError("boom")):
            with self.assertRaises(MODULE.OutputError):
                MODULE.atomic_write_text(self.output, "new\n")
        self.assertEqual(self.output.read_text(encoding="utf-8"), "old\n")
        leftovers = list(self.root.glob(f".{self.output.name}.*.tmp"))
        self.assertEqual(leftovers, [])

    def test_validate_corpus_requires_sorted_unique_records(self) -> None:
        parser = MODULE.ArticleStatsParser(
            MODULE.ArticleContainer(tag="article", class_name="article-body")
        )
        parser.feed(synthetic_html("B").decode("utf-8"))
        parser.close()
        second = parser.record("https://example.com/articles/2")
        parser = MODULE.ArticleStatsParser(
            MODULE.ArticleContainer(tag="article", class_name="article-body")
        )
        parser.feed(synthetic_html("A").decode("utf-8"))
        parser.close()
        first = parser.record("https://example.com/articles/1")
        self.output.write_text(
            MODULE.serialize_records([second, first]),
            encoding="utf-8",
            newline="\n",
        )
        records = MODULE.read_corpus(self.output)
        self.assertEqual([record["url"] for record in records], [first["url"], second["url"]])
        self.output.write_text(
            MODULE.serialize_records([second, first]).splitlines()[1]
            + "\n"
            + MODULE.serialize_records([second, first]).splitlines()[0]
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        with self.assertRaisesRegex(MODULE.SchemaError, "升序"):
            MODULE.read_corpus(self.output)


if __name__ == "__main__":
    unittest.main()
