#!/usr/bin/env python3
"""Generate asset-manifest.yml for every image in the package.

Published assets carry their real origin URL, rightsholder and attribution.
Research candidates are registered as non-release references so the validator
can prove the chain from raw capture to published crop.

Rights note: `user_confirmed_editorial_commentary` is this repo's status for
"the article owner confirmed attributed editorial-commentary use". It is NOT a
claim that the rightsholder granted permission -- every third-party asset also
carries `permission_from_rightsholder: unconfirmed` so the distinction cannot
be lost on the way to `ready`.
"""

from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
RESEARCH = ROOT / "research" / "source-assets"
OBTAINED = "2026-08-07"

EDITORIAL_BASIS = (
    "Screenshot of a publicly accessible page, used as cited evidence in an "
    "attributed APPSO editorial article; not a general or commercial licence"
)

# slug (filename without the ordering prefix) -> (source_type, source_url,
# rightsholder, attribution, modifications). Keyed on slug so reordering the
# article can never silently detach an asset from its provenance.
PUBLISHED: dict[str, tuple[str, str, str, str, str]] = {
    "anthropic-x-post.png": (
        "social_post_screenshot", "https://x.com/AnthropicAI/status/2082965101083320543",
        "Anthropic PBC / X Corp.", "@AnthropicAI",
        "Element screenshot of the public post; no content edits"),
    "anthropic-incident1-database.png": (
        "official_page_screenshot", "https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals",
        "Anthropic PBC", "Anthropic",
        "Cropped to the Incident 1 passage; resized to 1080 px wide; no content edits"),
    "anthropic-incident2-pypi.png": (
        "official_page_screenshot", "https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals",
        "Anthropic PBC", "Anthropic",
        "Cropped to the Incident 2 (PyPI) passage; resized to 1080 px wide; no content edits"),
    "techcrunch-anthropic-headline.png": (
        "media_page_screenshot", "https://techcrunch.com/2026/07/30/anthropic-says-its-own-ai-models-breached-three-companies-during-security-tests/",
        "TechCrunch / Yahoo Inc.", "TechCrunch",
        "Cropped to the headline area; resized to 1080 px wide; no content edits"),
    "hf-intrusion-actions.png": (
        "official_page_screenshot", "https://huggingface.co/blog/agent-intrusion-technical-timeline",
        "Hugging Face, Inc.", "Hugging Face",
        "Cropped to the attacker-action count passage; no content edits"),
    "cnbc-muse-code.png": (
        "media_page_screenshot", "https://www.cnbc.com/2026/08/05/meta-debuts-muse-code-to-take-on-anthropic-and-openai-.html",
        "CNBC / NBCUniversal", "CNBC",
        "Cropped to the headline and dateline; resized to 1080 px wide; no content edits"),
    "macrumors-muse-contributor.png": (
        "media_page_screenshot", "https://www.macrumors.com/2026/08/05/meta-muse-code-for-mac/",
        "MacRumors", "MacRumors",
        "Cropped to the headline area; resized to 1080 px wide; no content edits"),
    "openai-price-x.png": (
        "social_post_screenshot", "https://x.com/OpenAI/status/2082878168764207230",
        "OpenAI / X Corp.", "@OpenAI",
        "Element screenshot of the public post; no content edits"),
    "openaidevs-fastmode-x.png": (
        "social_post_screenshot", "https://x.com/OpenAIDevs/status/2082878473409085654",
        "OpenAI / X Corp.", "@OpenAIDevs",
        "Element screenshot of the public post; no content edits"),
    "anthropic-sonnet-intro-price.png": (
        "official_page_screenshot", "https://www.anthropic.com/claude/sonnet",
        "Anthropic PBC", "Anthropic",
        "Cropped to the availability-and-pricing passage; no content edits"),
    "linuxdo-prompt-terminal.png": (
        "forum_post_screenshot", "https://linux.do/t/topic/2713360",
        "LINUX DO user CaiGbro / LINUX DO", "LINUX DO",
        "Cropped to the original post's prompt text and terminal capture; no content edits"),
    "linuxdo-22h-stuck.png": (
        "forum_post_screenshot", "https://linux.do/t/topic/2713360",
        "LINUX DO user CaiGbro / LINUX DO", "LINUX DO",
        "Cropped to the 22-hour report and terminal captures; no content edits"),
    "linuxdo-replies.png": (
        "forum_post_screenshot", "https://linux.do/t/topic/2713360",
        "LINUX DO users / LINUX DO", "LINUX DO",
        "Cropped to public replies; no content edits; no personal data beyond public display names"),
    "linuxdo-reversal-pi.png": (
        "forum_post_screenshot", "https://linux.do/t/topic/2713360",
        "LINUX DO user CaiGbro / LINUX DO", "LINUX DO",
        "Cropped to the poster's follow-up; no content edits"),
    "qwen-ecommerce-bench.png": (
        "official_page_screenshot", "https://qwen.ai/blog?id=qwen3.8",
        "Qwen Team / Alibaba Cloud", "Qwen",
        "Cropped to the E-Commerce Bench video poster; no content edits"),
    "ohmycli-repo.png": (
        "official_page_screenshot", "https://github.com/qwen-code-dev-bot/oh-my-cli",
        "GitHub, Inc. / qwen-code-dev-bot", "GitHub",
        "Cropped to the repository header; no content edits"),
    "ohmycli-commits.png": (
        "official_page_screenshot", "https://github.com/qwen-code-dev-bot/oh-my-cli/commits/main/",
        "GitHub, Inc. / qwen-code-dev-bot", "GitHub",
        "Cropped to the commit history list; no content edits"),
    "edgecity-village-x.png": (
        "social_post_screenshot", "https://x.com/JoinEdgeCity/status/2083246167073407316",
        "Edge City / X Corp.", "@JoinEdgeCity",
        "Element screenshot of the public post; no content edits"),
    "village-numbers.png": (
        "official_page_screenshot", "https://blog.cosmos-institute.org/p/we-gave-a-village-personal-ai-agents",
        "Cosmos Institute", "Cosmos Institute",
        "Cropped to the negotiation statistics passage; no content edits"),
    "rescript-showhn.png": (
        "forum_post_screenshot", "https://news.ycombinator.com/item?id=49065779",
        "Y Combinator / Hacker News", "Hacker News",
        "Cropped to the submission header; no content edits"),
    "rescript-ui.jpg": (
        "official_product_screenshot", "https://raw.githubusercontent.com/wassgha/rescript/main/screenshots/rescript.png",
        "Rescript project contributors", "Rescript / GitHub",
        "Downloaded from the official repository; resized to 1080 px wide and JPEG-encoded; no crop"),
    "liquidai-lfm-x.png": (
        "social_post_screenshot", "https://x.com/liquidai/status/2084640701669613906",
        "Liquid AI / X Corp.", "@liquidai",
        "Element screenshot of the public post; no content edits"),
    "lfm-benchmarks.png": (
        "official_page_screenshot", "https://huggingface.co/blog/LiquidAI/lfm2-5-2-6b",
        "Liquid AI / Hugging Face", "Liquid AI / Hugging Face",
        "Cropped to the model-capability passage; no content edits"),
    "ruview-demo.png": (
        "official_page_screenshot", "https://ruview.blog/",
        "RuView project (ruvnet)", "RuView",
        "Cropped to the live demo panel; no content edits"),
    "ruview-entities.png": (
        "official_page_screenshot", "https://github.com/ruvnet/RuView",
        "GitHub, Inc. / RuView project (ruvnet)", "RuView / GitHub",
        "Cropped to the README capability list; no content edits"),
    "naomi-bashkansky-x.png": (
        "social_post_screenshot", "https://x.com/NaomiBashkansky/status/2085043839589617918",
        "Naomi Bashkansky / X Corp.", "@NaomiBashkansky",
        "Element screenshot of the public post; no content edits"),
    "conduit-training-headset.jpg": (
        "official_blog_photo", "https://condu.it/thought/10k-hours/images/image3.jpg",
        "Conduit", "Conduit",
        "Downloaded from the official technical blog; JPEG re-encoded; no crop"),
    "conduit-booth.jpg": (
        "official_blog_photo", "https://condu.it/thought/10k-hours/images/image8.png",
        "Conduit", "Conduit",
        "Downloaded from the official technical blog; resized to 1080 px wide and JPEG-encoded; no crop"),
    "conduit-corridor.jpg": (
        "official_blog_photo", "https://condu.it/thought/10k-hours/images/image9.png",
        "Conduit", "Conduit",
        "Downloaded from the official technical blog; JPEG re-encoded; no crop"),
    "conduit-60hz-noise.png": (
        "official_blog_figure", "https://condu.it/thought/10k-hours/images/image2.png",
        "Conduit", "Conduit",
        "Downloaded from the official technical blog; no content edits; source labels it a generic MNE example, not their dataset"),
    "conduit-simple-keyboard.jpg": (
        "official_blog_photo", "https://condu.it/thought/10k-hours/images/image6.jpg",
        "Conduit", "Conduit",
        "Downloaded from the official technical blog; resized to 1080 px wide; no crop"),
    "transluce-x-post.png": (
        "social_post_screenshot", "https://x.com/TransluceAI/status/2085455114924638320",
        "Transluce AI / X Corp.", "@TransluceAI",
        "Element screenshot of the public post; no content edits"),
    "transluce-askell-shift.png": (
        "official_page_screenshot", "https://transluce.org/user-awareness",
        "Transluce AI", "Transluce",
        "Cropped to the individual-level results; no content edits"),
    "transluce-borderline.png": (
        "official_page_screenshot", "https://transluce.org/user-awareness",
        "Transluce AI", "Transluce",
        "Cropped to the task-design section; no content edits"),
    "teammate-paper-fig1.png": (
        "paper_figure_screenshot", "https://arxiv.org/html/2607.27179v1",
        "Paper authors (arXiv:2607.27179)", "arXiv:2607.27179",
        "Cropped to Figure 1 and its caption; no content edits"),
    "teammate-paper-fig2.png": (
        "paper_figure_screenshot", "https://arxiv.org/html/2607.27179v1",
        "Paper authors (arXiv:2607.27179)", "arXiv:2607.27179",
        "Cropped to Figure 2 and its caption; no content edits"),
    "gstack-roles.png": (
        "official_page_screenshot", "https://github.com/pattern-ai-labs/gstack-joins-meeting",
        "GitHub, Inc. / pattern-ai-labs", "pattern-ai-labs / GitHub",
        "Cropped to the README role table; no content edits"),
    "gstack-dashboard.jpg": (
        "official_product_screenshot", "https://raw.githubusercontent.com/pattern-ai-labs/gstack-joins-meeting/main/docs/dashboard.png",
        "pattern-ai-labs / gstack joins your meeting contributors", "pattern-ai-labs / GitHub",
        "Downloaded from the official repository; resized to 1080 px wide and JPEG-encoded; no crop"),
    "hf-glm-forensics.png": (
        "official_page_screenshot", "https://huggingface.co/blog/agent-intrusion-technical-timeline",
        "Hugging Face, Inc.", "Hugging Face",
        "Cropped to the forensic-model passage; no content edits"),
    # --- News 2: Google AI leadership shakeup ---
    "jeffdean-farewell-x.png": (
        "social_post_screenshot", "https://x.com/JeffDean/status/2085083442669318443",
        "Jeff Dean / X Corp.", "@JeffDean",
        "Element screenshot of the public post; no content edits"),
    "jeffdean-discoveryloop-x.png": (
        "social_post_screenshot", "https://x.com/JeffDean/status/2085034604172603724",
        "Jeff Dean / X Corp.", "@JeffDean",
        "Element screenshot of the public post; no content edits"),
    "hassabis-chair-x.png": (
        "social_post_screenshot", "https://x.com/demishassabis/status/2085034334914769203",
        "Demis Hassabis / X Corp.", "@demishassabis",
        "Element screenshot of the public post; no content edits"),
    "jiqizhixin-hassabis-rumor.png": (
        "media_page_screenshot", "https://mp.weixin.qq.com/s/05_d8bV01Rc9bbGOB7TJjA",
        "机器之心 / 微信公众号", "机器之心",
        "Cropped to the passage relaying the Pathfounders report; no content edits"),
    # --- News 4: Apple Intelligence x Qwen ---
    "ithome-apple-qwen.png": (
        "media_page_screenshot", "https://www.ithome.com/0/987/366.htm",
        "IT之家；页内引用图为苹果官网 Mac 使用手册页面（Apple Inc.）", "IT之家",
        "Mobile-layout page screenshot cropped to the headline, lede and the quoted Apple support page; no content edits"),
    "apple-qwen-requirements.png": (
        "media_page_screenshot", "https://www.ithome.com/0/987/366.htm",
        "IT之家", "IT之家",
        "Cropped to the eligibility and setup passage; no content edits"),
    "apple-qwen-siri.png": (
        "media_page_screenshot", "https://www.ithome.com/0/987/366.htm",
        "IT之家", "IT之家",
        "Cropped to the Siri example passage; no content edits"),
    "apple-cn-still-unavailable.png": (
        "official_page_screenshot", "https://support.apple.com/zh-cn/guide/mac-help-cn/mchlfc5cf131/mac",
        "Apple Inc.", "Apple",
        "Cropped to the availability note; no content edits"),
    "baidu-visual-search.png": (
        "media_page_screenshot", "https://finance.sina.com.cn/tech/digi/2026-06-27/doc-inieveqy4859661.shtml",
        "新浪财经（转载 IT之家）", "新浪财经 / IT之家",
        "Cropped to the firmware-component passage; no content edits"),
    # --- Tools: Claude Code cross-session messaging ---
    "claudedevs-crosssession-x.png": (
        "social_post_screenshot", "https://x.com/ClaudeDevs/status/2085817074816070014",
        "Anthropic PBC / X Corp.", "@ClaudeDevs",
        "Element screenshot of the public post including its embedded demo frame; no content edits"),
    "claude-docs-crosssession.png": (
        "official_page_screenshot", "https://code.claude.com/docs/en/cross-session-messaging",
        "Anthropic PBC", "Anthropic",
        "Cropped to the feature overview and version requirement; no content edits"),
    "claude-docs-usecases.png": (
        "official_page_screenshot", "https://code.claude.com/docs/en/cross-session-messaging",
        "Anthropic PBC", "Anthropic",
        "Cropped to the when-to-use section; no content edits"),
    "nbd-fangtaozi-report.png": (
        "media_page_screenshot", "https://m.nbd.com.cn/articles/2026-08-07/4535104.html",
        "每日经济新闻 / NBD；页内视频画面署名抖音用户 @方桃子", "每日经济新闻",
        "Mobile-layout page screenshot cropped below the app banner; no content edits"),
    "fangtaozi-price-tiers.png": (
        "media_page_screenshot", "https://finance.sina.com.cn/jjxw/2026-08-05/doc-inimffsr5293145.shtml",
        "新浪财经（转载扬子晚报）", "新浪财经 / 扬子晚报",
        "Cropped to the rate-card paragraph; no content edits"),
    "xinwaner-fangtaozi-removed.png": (
        "media_page_screenshot", "https://mp.weixin.qq.com/s?__biz=MzkzODM3OTAxMQ==&mid=2247513784&idx=1&sn=044838097e6c22401aa736ccf132e26c",
        "新腕儿 / 微信公众号", "新腕儿",
        "Cropped to the headline and lede; no content edits"),
    "nbd-fangtaozi-law.png": (
        "media_page_screenshot", "https://m.nbd.com.cn/articles/2026-08-07/4535104.html",
        "每日经济新闻 / NBD", "每日经济新闻",
        "Cropped to the legal-analysis passage; no content edits"),
    "nbd-fangtaozi-fine.png": (
        "media_page_screenshot", "https://m.nbd.com.cn/articles/2026-08-07/4535104.html",
        "每日经济新闻 / NBD", "每日经济新闻",
        "Cropped to the prior-penalty passage; no content edits"),
}

# Research captures: name prefix -> (origin URL, rightsholder)
RESEARCH_ORIGIN = {
    "x-anthropic-incidents": ("https://x.com/AnthropicAI/status/2082965101083320543", "Anthropic PBC / X Corp."),
    "x-openai-price": ("https://x.com/OpenAI/status/2082878168764207230", "OpenAI / X Corp."),
    "x-openaidevs-fastmode": ("https://x.com/OpenAIDevs/status/2082878473409085654", "OpenAI / X Corp."),
    "x-qwen-38max": ("https://x.com/Alibaba_Qwen/status/2084100707423289643", "Alibaba Qwen / X Corp."),
    "x-liquidai-lfm25": ("https://x.com/liquidai/status/2084640701669613906", "Liquid AI / X Corp."),
    "x-transluce-awareness": ("https://x.com/TransluceAI/status/2085455114924638320", "Transluce AI / X Corp."),
    "x-naomi-conduit": ("https://x.com/NaomiBashkansky/status/2085043839589617918", "Naomi Bashkansky / X Corp."),
    "x-edgecity-village": ("https://x.com/JoinEdgeCity/status/2083246167073407316", "Edge City / X Corp."),
    "anthropic-report": ("https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals", "Anthropic PBC"),
    "anthropic-sonnet": ("https://www.anthropic.com/claude/sonnet", "Anthropic PBC"),
    "openai-hf-incident": ("https://openai.com/index/hugging-face-model-evaluation-security-incident/", "OpenAI"),
    "hf-incident-disclosure": ("https://huggingface.co/blog/security-incident-july-2026", "Hugging Face, Inc."),
    "hf-timeline": ("https://huggingface.co/blog/agent-intrusion-technical-timeline", "Hugging Face, Inc."),
    "aisi-kimi": ("https://www.aisi.gov.uk/blog/preliminary-assessment-of-kimi-k3s-cyber-capabilities", "UK AI Security Institute"),
    "techcrunch-anthropic": ("https://techcrunch.com/2026/07/30/anthropic-says-its-own-ai-models-breached-three-companies-during-security-tests/", "TechCrunch / Yahoo Inc."),
    "linuxdo": ("https://linux.do/t/topic/2713360", "LINUX DO users / LINUX DO"),
    "hf-deepseek-card": ("https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731", "DeepSeek / Hugging Face"),
    "qwen-": ("https://qwen.ai/blog?id=qwen3.8", "Qwen Team / Alibaba Cloud"),
    "ohmycli": ("https://github.com/qwen-code-dev-bot/oh-my-cli", "GitHub, Inc. / qwen-code-dev-bot"),
    "transluce": ("https://transluce.org/user-awareness", "Transluce AI"),
    "arxiv-teammate": ("https://arxiv.org/html/2607.27179v1", "Paper authors (arXiv:2607.27179)"),
    "rescript-hn": ("https://news.ycombinator.com/item?id=49065779", "Y Combinator / Hacker News"),
    "rescript-gh": ("https://github.com/wassgha/rescript", "GitHub, Inc. / Rescript project contributors"),
    "lfm-hf": ("https://huggingface.co/blog/LiquidAI/lfm2-5-2-6b", "Liquid AI / Hugging Face"),
    "gstack": ("https://github.com/pattern-ai-labs/gstack-joins-meeting", "GitHub, Inc. / pattern-ai-labs"),
    "cosmos-village": ("https://blog.cosmos-institute.org/p/we-gave-a-village-personal-ai-agents", "Cosmos Institute"),
    "cnbc-muse-code": ("https://www.cnbc.com/2026/08/05/meta-debuts-muse-code-to-take-on-anthropic-and-openai-.html", "CNBC / NBCUniversal"),
    "macrumors-muse": ("https://www.macrumors.com/2026/08/05/meta-muse-code-for-mac/", "MacRumors"),
    "engadget-muse": ("https://www.engadget.com/2231285/meta-introduces-muse-code-its-take-on-a-coding-agent/", "Engadget / Yahoo Inc."),
    "muse-code-official": ("https://muse-code.dev/", "muse-code.dev (independent site, self-declared not affiliated with Meta)"),
    "meetily-repo": ("https://github.com/Zackriya-Solutions/meetily", "GitHub, Inc. / Zackriya Solutions"),
    "ruview": ("https://github.com/ruvnet/RuView", "GitHub, Inc. / RuView project (ruvnet)"),
    "conduit-": ("https://condu.it/thought/10k-hours", "Conduit"),
    "x-jeffdean-farewell": ("https://x.com/JeffDean/status/2085083442669318443", "Jeff Dean / X Corp."),
    "x-jeffdean-discoveryloop": ("https://x.com/JeffDean/status/2085034604172603724", "Jeff Dean / X Corp."),
    "x-hassabis-chair": ("https://x.com/demishassabis/status/2085034334914769203", "Demis Hassabis / X Corp."),
    "x-pichai-deepmind": ("https://x.com/sundarpichai/status/2085033425736745093", "Sundar Pichai / X Corp."),
    "x-claudedevs-crosssession": ("https://x.com/ClaudeDevs/status/2085817074816070014", "Anthropic PBC / X Corp."),
    "cnbc-google-shakeup": ("https://www.cnbc.com/2026/08/05/google-chief-scientist-jeff-dean-leaving-company-after-27-years.html", "CNBC / NBCUniversal"),
    "wx-jiqizhixin": ("https://mp.weixin.qq.com/s/05_d8bV01Rc9bbGOB7TJjA", "机器之心"),
    "claude-docs": ("https://code.claude.com/docs/en/cross-session-messaging", "Anthropic PBC"),
    "9to5mac-crosssession": ("https://9to5mac.com/2026/08/07/claude-code-now-lets-sessions-talk-to-each-other-on-macos/", "9to5Mac"),
    "ithome-apple-qwen": ("https://www.ithome.com/0/987/366.htm", "IT之家"),
    "sina-baidu": ("https://finance.sina.com.cn/tech/digi/2026-06-27/doc-inieveqy4859661.shtml", "新浪财经 / IT之家"),
    "itbear-baidu-visualsearch": ("https://www.itbear.com.cn/html/2026-06/1416049.html", "ITBear 科技资讯"),
    "techcrunch-apple-china": ("https://techcrunch.com/2026/07/16/apple-intelligence-approved-for-launch-in-china-with-alibabas-qwen-ai/", "TechCrunch / Yahoo Inc."),
    "apple-cn-still": ("https://support.apple.com/zh-cn/guide/mac-help-cn/mchlfc5cf131/mac", "Apple Inc."),
    "apple-qwen-support": ("https://support.apple.com/zh-cn/guide/mac-help/mchl46b3ab20/mac", "Apple Inc."),
    "zhidx-apple-qwen": ("https://zhidx.com/p/583346.html", "智东西"),
    "sina-apple-qwen": ("https://finance.sina.com.cn/tech/digi/2026-08-08/doc-inimqyim2551429.shtml", "新浪科技"),
    "m-nbd-fangtaozi": ("https://m.nbd.com.cn/articles/2026-08-07/4535104.html", "每日经济新闻 / NBD"),
    "nbd-fangtaozi": ("https://www.nbd.com.cn/articles/2026-08-07/4535104.html", "每日经济新闻 / NBD"),
    "m-sina-fangtaozi": ("https://finance.sina.com.cn/jjxw/2026-08-05/doc-inimffsr5293145.shtml", "新浪财经 / 扬子晚报"),
    "sina-fangtaozi": ("https://finance.sina.com.cn/jjxw/2026-08-05/doc-inimffsr5293145.shtml", "新浪财经 / 扬子晚报"),
    "wx-xinwaner-fangtaozi": ("https://mp.weixin.qq.com/s?__biz=MzkzODM3OTAxMQ==&mid=2247513784&idx=1&sn=044838097e6c22401aa736ccf132e26c", "新腕儿"),
    "sohu-fangtaozi": ("https://www.sohu.com/a/1058701675_121448078", "搜狐"),
    "qq-fangtaozi": ("https://view.inews.qq.com/a/20260804A0CHOZ00", "腾讯新闻"),
    "bjd-ai-endorse": ("https://xinwen.bjd.com.cn/content/s6a72a627e4b0e45f3fd5a3f8.html", "北京日报"),
    "adomate-og": ("https://www.adomate.com/og-image-2026.png", "Adomate"),
    "webhound-og": ("https://webhound.ai/logo-16-10.png", "Webhound"),
    "deepseek-v4-flash-hf-card": ("https://cdn-thumbnails.huggingface.co/social-thumbnails/models/deepseek-ai/DeepSeek-V4-Flash-0731.png", "DeepSeek / Hugging Face"),
    "gstack-dashboard": ("https://raw.githubusercontent.com/pattern-ai-labs/gstack-joins-meeting/main/docs/dashboard.png", "pattern-ai-labs"),
    "ioai-": ("https://ioai-official.org/ai-model-track/", "International Olympiad in AI"),
    "rescript-ui": ("https://raw.githubusercontent.com/wassgha/rescript/main/screenshots/rescript.png", "Rescript project contributors"),
    "anthropic-cyber-evals-og": ("https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals", "Anthropic PBC"),
}


def yaml_str(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def dimensions(path: Path) -> str:
    with Image.open(path) as im:
        return f"{im.size[0]}x{im.size[1]}"


def research_origin(stem: str) -> tuple[str, str]:
    for prefix, value in sorted(RESEARCH_ORIGIN.items(), key=lambda kv: -len(kv[0])):
        if stem.startswith(prefix):
            return value
    raise SystemExit(f"[fail] no registered origin for research capture: {stem}")


lines = [
    "# 图片资产台账",
    "#",
    "# rights_status 说明：user_confirmed_editorial_commentary 表示「本文作者确认",
    "# 用于署名的编辑评论」，不代表权利人已授权。第三方素材另有",
    "# permission_from_rightsholder: unconfirmed 字段如实记录权利状态。",
    "# 本期未使用任何 AI 生成图，也未使用自制信息卡。",
    "version: 2",
    f'updated: "{OBTAINED}"',
    "assets:",
]

published_files = sorted(p.name for p in ASSETS.iterdir() if p.suffix.lower() in {".png", ".jpg"})
def slug_of(name: str) -> str:
    return re.sub(r"^\d{2}-", "", name)


unknown = [name for name in published_files if slug_of(name) not in PUBLISHED]
if unknown:
    raise SystemExit(f"[fail] published assets missing metadata: {unknown}")

for name in published_files:
    source_type, source, holder, attribution, modifications = PUBLISHED[slug_of(name)]
    lines += [
        f'  - file: "assets/{name}"',
        "    used_in_draft: true",
        '    use: "wechat_body_header"',
        f"    source_type: {yaml_str(source_type)}",
        f"    source: {yaml_str(source)}",
        f"    creator_or_rightsholder: {yaml_str(holder)}",
        f'    obtained_on: "{OBTAINED}"',
        f'    dimensions: "{dimensions(ASSETS / name)}"',
        f"    modifications: {yaml_str(modifications)}",
        '    rights_status: "user_confirmed_editorial_commentary"',
        f"    rights_basis: {yaml_str(EDITORIAL_BASIS)}",
        '    permission_from_rightsholder: "unconfirmed"',
        '    allowed_platforms: ["wechat"]',
        f"    attribution: {yaml_str(attribution)}",
    ]

research_files = sorted(
    p.relative_to(ROOT).as_posix()
    for p in RESEARCH.rglob("*")
    if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".avif"}
)
for rel in research_files:
    stem = Path(rel).stem
    source, holder = research_origin(stem)
    lines += [
        f'  - file: "{rel}"',
        "    used_in_draft: false",
        '    use: "research_reference"',
        '    source_type: "research_capture"',
        f"    source: {yaml_str(source)}",
        f"    creator_or_rightsholder: {yaml_str(holder)}",
        f'    obtained_on: "{OBTAINED}"',
        f'    dimensions: "{dimensions(ROOT / rel)}"',
        '    modifications: "Captured or downloaded without content edits for internal visual selection"',
        '    rights_status: "research_reference"',
        '    permission_from_rightsholder: "unconfirmed"',
        "    allowed_platforms: []",
        f"    attribution: {yaml_str(holder)}",
    ]

(ROOT / "asset-manifest.yml").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"[ok] wrote asset-manifest.yml: {len(published_files)} published, {len(research_files)} research")
