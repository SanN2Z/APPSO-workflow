# Git 提交与仓库整理 SOP

版本：1.2

更新日期：2026 年 9 月 7 日

## 目标

让内容、SOP 和知识库持续处于可恢复、可审计、可交接的状态，同时避免凭据、受限原件、临时素材和生成物进入远端。

## 仓库边界

- 本项目远端必须为 Private。
- `internal` 内容可以进入经授权的公司私有仓库。
- `restricted` 内容优先只建索引；原始文件、后台数据和授权凭证留在 Git 忽略区。
- 窄例外：用户或权利人明确授权、远端 Private 已核、且凭据与运行态审计通过的公司内部工具，可以按版本进入 `tools/company/`。这个例外不覆盖公司终稿、后台数据、授权凭证、浏览器 Profile、缓存或会话导出。
- `.env`、Cookie、Token、API Key、AppSecret、验证码、登录态和完整请求头永不提交。
- 用户已在 2026-09-07 明确授权本批流程、Prompt、设计规范和 Logo 统一进入当前私有仓库，精确文件与哈希见 `tools/workflow-source-assets.json`。对应忽略规则只对登记文件放行，不再重复请求分级确认。新增或修改输入时同步清单与使用入口，预检会核对原件哈希；不使用 `git add -f` 绕过规则。
- `output/`、`临时素材/`、`dist/`、浏览器记录、依赖目录和缓存不提交。

## 提交粒度

一个提交只表达一个可回退的工作单元：

- 一篇稿件的一轮调研或写作。
- 一次事实复核或逐句终校。
- 一套 SOP 的新增或升级。
- 一批同来源、同分级的数字资产入库。
- 一次仓库结构、工具或模板调整。

不要把无关平台、不同稿件和仓库维护混入同一提交。纯格式修复可单独提交，但不能借机改写历史正文。

## 提交格式

```text
type(scope): 中文摘要
```

建议类型：

| type | 用途 |
|---|---|
| `content` | 选题、调研、稿件、审校与发布记录 |
| `docs` | SOP、知识库、上下文和说明文档 |
| `assets` | 权利已核或内部可提交的素材与台账 |
| `fix` | 路径、状态、链接、脚本或数据错误修复 |
| `tools` | 验证、预览、发布和辅助脚本 |
| `ops` | 仓库结构、忽略规则和维护配置 |

常用 scope：`wechat`、`x`、`sop`、`appsso`、`repo`、具体内容包 slug。

示例：

```text
docs(sop): 增加 Git 提交与仓库整理流程
content(wechat): 完成 M7 Ultra 稿事实复核
assets(appsso): 登记 Hunt Good 视觉参考资产
fix(tibo-gpt56-quota): 修正图片相对路径
```

## 每次任务流程

### 1. 开始前

```powershell
git status --short
git branch --show-current
```

识别已有修改的归属。用户或其他任务留下的改动不得擅自覆盖、还原或混入本次提交。

### 2. 工作中

- 修改范围保持在当前任务内。
- 内容状态、事实门、图片权利和正文哈希按项目规则更新。
- 新反馈先写入案例或反馈库，确认跨稿有效后再升级为 SOP。
- 达成一个可验证节点后执行对应检查，不等所有工作混在一起再检查。

### 3. 提交前

```powershell
powershell -ExecutionPolicy Bypass -File tools/repository_preflight.ps1
git diff --stat
git diff --check
```

历史基线或外部抽取文本出现纯行尾空格时，先检查影响范围，再按需执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 normalize-text --staged --fix
git add -- <本次修复的文件>
```

该脚本只处理 `git diff --cached --check` 已报告的 UTF-8 文本，不修改文字内容。修复后仍需重跑预检。

随后按范围暂存，优先指定目录或文件：

```powershell
git add -- README.md CONTRIBUTING.md .gitignore
git diff --cached --stat
git diff --cached
```

确认无凭据、无受限原件、无临时产物、无无关改动后再提交。禁止使用 `git add -f`。

### 4. 提交与推送

```powershell
git commit -m "ops(repo): 整理私有知识库结构"
git push origin HEAD
```

只有远端确认为项目私有仓库、检查全部通过时才推送。推送不代表内容已发布，也不改变稿件的 `published` 状态。

## 固定节奏

### 每日

- 当天有实质改动时，至少形成一个可恢复提交。
- 任务跨天时，提交可运行或可理解的 checkpoint，并在 `上下文/当前重点.md` 写清阻塞项。
- 不提交半写入的二进制文件、损坏文件或含临时凭据的调试记录。

### 每周

- 清理 `output/`、`临时素材/`、浏览器记录和失效预览；保留仍在使用的本地材料。
- 更新 `上下文/当前重点.md`，移除已完成或失效的下一步。
- 运行 `content-retrospective` 到期审计，处理本周反馈与 SOP 候选。
- 检查 APPSO 资产台账、内部资产索引和变更记录是否同步。
- 检查内容包的状态、相对图片路径、发布记录和未解决权利问题。
- 查看仓库体积和大文件；单个大于 50 MB 的文件提交前单独评估，接近托管平台上限时改用对象存储或 Git LFS。
- 复查远端可见性、默认分支和协作者权限。

## 失败处理

- 预检失败：不暂存、不提交、不推送，先修复或明确记录阻塞。
- 远端可见性无法确认：可以保留本地提交，不推送。
- 误提交凭据：立即停止推送；若已推送，先轮换凭据，再清理历史，不能只删除最新文件。
- 内容包验证失败：不把稿件推进到 `ready`；仓库维护提交可以保留历史未完成稿，但必须避免把验证失败写成已完成。
