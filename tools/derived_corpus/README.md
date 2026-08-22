# 科技媒体衍生语料抓取器

这个工具只处理人工明确列出的公开文章 URL，并把页面投影为：

- URL；
- 标题；
- 发布日期；
- 作者；
- 栏目；
- 段落、句子、小标题、列表、引用、图片等结构统计。

它不发现链接，不递归爬取，不执行 JavaScript，不登录，不携带 Cookie，不下载图片，也不保存、打印或写入文章正文、原始 HTML、摘要、引语、关键词和标题之外的段落文本。

## 安装

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/bootstrap.ps1
```

正式依赖只有固定版本的 `PyYAML`；HTTP、robots 和 HTML 流式解析使用 Python 标准库。

## 配置

策略文件必须是 UTF-8 YAML。未知字段、重复键、重复 host 和不安全 path 会直接失败。

```yaml
version: 1
user_agent: "TechMediaDerivedCorpusBot/0.1 (+https://example.org/crawler-info)"
min_delay_seconds: 10
timeout_seconds: 20
max_pages_per_run: 30
domains:
  - host: "www.example.com"
    scheme: "https"
    port: 443
    allowed_path_prefixes:
      - "/articles/"
    article_container:
      tag: "article"
      class: "article-body"
```

`host` 使用 exact match。`www.example.com.evil.invalid` 不会命中 `www.example.com`。一个 adapter 只声明正文容器的 HTML tag 与一个 class token，不接受 CSS selector，也不会在 adapter 失败时退回整页 `<body>`。

生产来源应使用 HTTPS。`http` 只在策略显式声明时可用，用于确实仍以 HTTP 公开提供的来源；它不会自动降级。

URL 输入文件每行一个 URL，可以有空行和以 `#` 开头的注释：

```text
https://www.example.com/articles/100
https://www.example.com/articles/101
```

工具保留 query，删除 fragment，不自动猜测哪些 query 参数是跟踪参数。

## 本项目入口

APPSO 公开媒体研究的当前实例位于：

- 策略：`APPSO-数字资产/02-方法与知识/写作与结构/公开科技媒体衍生语料/policy.yml`
- 显式 URL：`APPSO-数字资产/02-方法与知识/写作与结构/公开科技媒体衍生语料/pilot-urls.txt`
- 预期输出：`APPSO-数字资产/02-方法与知识/写作与结构/公开科技媒体衍生语料/records.jsonl`
- 运行审计：`APPSO-数字资产/02-方法与知识/写作与结构/公开科技媒体衍生语料/run-receipts/`

先运行 `plan`，再运行不带 `--execute` 的 `collect`；确认策略、域名和输出后，才执行真实请求。2026 年 7 月 25 日首轮真实采集被非公网 DNS 门禁阻断，处理决定是保留门禁，不以代理或 allowlist 例外绕过。

## 命令

先做零网络计划：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 corpus plan `
  --config 共享/研究/衍生语料/科技媒体/policy.yml `
  --input 共享/研究/衍生语料/科技媒体/urls.txt
```

`collect` 默认仍是零网络 dry-run，也不会创建输出文件：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 corpus collect `
  --config 共享/研究/衍生语料/科技媒体/policy.yml `
  --input 共享/研究/衍生语料/科技媒体/urls.txt `
  --output 共享/研究/衍生语料/科技媒体/records.jsonl
```

只有显式提供 `--execute` 才会发起 GET 请求并在全部 URL 成功后原子替换输出：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 corpus collect `
  --config 共享/研究/衍生语料/科技媒体/policy.yml `
  --input 共享/研究/衍生语料/科技媒体/urls.txt `
  --output 共享/研究/衍生语料/科技媒体/records.jsonl `
  --execute
```

校验已有 corpus：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 corpus validate `
  --corpus 共享/研究/衍生语料/科技媒体/records.jsonl
```

## 网络与合规边界

每个 origin 在访问文章前都会获取 `/robots.txt`：

- `200`：遵守可解析的 `Allow` / `Disallow`，并尊重可解析的 `Crawl-delay` 与 `Request-rate`；
- `404` / `410`：视为没有 robots 规则；
- `401` / `403`、其他 `4xx`、`5xx`、DNS / TLS / 网络失败、非 UTF-8 robots：保守拒绝；
- robots 和文章重定向最多 5 次，每一跳都重新检查 exact allowlist 和 DNS；
- 任何解析到 loopback、private、link-local、reserved 等非公网 IP 的 host 都被 SSRF 门禁拒绝；
- 每个 host 串行请求，实际间隔取本地最小间隔与 robots 声明中的较大值；
- 页面响应最多 2 MiB，robots 最多 512 KiB；
- 禁用环境代理、自动重定向和压缩响应，不提供忽略 robots、关闭 TLS、伪装浏览器或提升上限的开关。

robots 是站点对自动访问的公开指示，不是内容授权。即使 robots 允许，仍不得用这个工具访问登录后、付费、未公开或没有合法使用基础的内容。

## 输出合同

`records.jsonl` 每行一个 JSON object。顶层字段严格固定为：

```text
schema_version
url
title
published_date
authors
column
structure
```

`structure` 只含整数、有限数值和小标题级别序列，不含任何句子、段落、小标题文字、图片 URL 或链接目标。验证器会拒绝任何未知字段；因此新增 `body`、`html`、`excerpt`、`summary`、`description`、`articleBody`、`paragraphs` 等字段会直接失败。

元数据按以下顺序选择：

- 标题：Open Graph、JSON-LD、Twitter meta、HTML `<title>`；
- 日期：文章 meta、JSON-LD、`<time datetime>`；
- 作者和栏目：JSON-LD 或标准 meta。

日期、作者或栏目无法可靠取得时分别写 `null` / `[]` / `null`；标题、正文容器和可见正文是必需项。正文容器缺失、命中多个、结构失衡或为空时整批失败，旧 corpus 保持不变。

`HTMLParser` 不是完整浏览器 DOM。站点改版或依赖 JavaScript 渲染时，应更新 adapter 和合成测试，不能切换到浏览器自动化或保存网页排查。

## 测试

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 test tools/derived_corpus/tests/test_derived_corpus.py
```

测试全部使用人工合成 HTML 和可注入的假 HTTP 响应，不访问互联网，也不会把第三方 HTML 带进仓库。
