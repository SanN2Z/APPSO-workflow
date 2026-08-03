# 微信公众号子项目

公众号文章按「一个选题一个内容包」管理。默认由一个执行者维护唯一 `draft.md`，到 `editorial_review` 再增加一次独立冷读；事实、版权或发布风险较高时才加载对应专家视角。可选协作方式见 `../.agents/skills/self-media-ops/references/wechat-team.md`。

## 目录

```text
微信公众号/
├─ AGENTS.md              # 平台硬规则，未经明确授权不改
├─ CONTEXT.md             # 读者、栏目与默认写法
├─ package.json           # 锁定 @wenyan-md/cli 版本
├─ requirements.txt       # 锁定 Python 发布适配器依赖
├─ themes/                # 受控版式 profile、自定义 CSS 与样本说明
├─ tools/                 # 内容包到 Wenyan 的安全适配层
├─ 知识库/                 # 可复用的编辑反馈、参考结构和研究结论
├─ 选题/                   # 详细选题卡；状态总表仍在 共享/运营/选题池.md
├─ 内容/YYYY/MM/slug/     # 每篇文章的唯一真源
└─ 发布记录/               # 只做索引；真实记录留在内容包 publish-record.md
```

## 内容包

```text
内容/YYYY/MM/slug/
├─ draft.md
├─ sources.md              # research 起增加
├─ brief.md                # 新长稿或结构重写
├─ review.md               # editorial_review 起增加
├─ copyedit.md             # ready 前增加
├─ asset-manifest.yml      # 首张图进入时增加
├─ publish.yml             # 预览或交付时增加
├─ publish-record.md       # 外部交接或发布时增加
├─ assets/、research/      # 按需
└─ dist/                   # 自动生成，Git 忽略
```

想法阶段只需要 `draft.md`。文件随状态增加；进入 `ready` 时再补齐事实、审校、终校、权利和平台门所需记录。详细规则见 [content-package.md](../.agents/skills/self-media-ops/references/content-package.md)。

不按 `draft/ready/published` 移动目录。结构性反馈保留在内容包；跨文章可复用的规律通过复盘晋升门进入 SOP。

## 排版预览与草稿箱

排版、图片上传和微信草稿 API 复用开源 [Wenyan CLI](https://github.com/caol64/wenyan-cli)，项目固定为 `@wenyan-md/cli@2.0.11`；本地适配层不重复实现渲染器和微信客户端。

用户只需选择 `company_browser`、`manual_editor` 或 `sealed_draft`。工具内部继续保留品牌、交付方式和视觉主题字段做严格校验。命令与失败处理见 [wechat-publishing.md](../.agents/skills/self-media-ops/references/wechat-publishing.md)，主题能力见 [themes/README.md](themes/README.md)。

APPSO／公司稿由 Agent 处理时，默认预览交付为飞书在线文档：从仓库根目录运行 `python tools/company_content_sync/company_content_sync.py status <内容包路径> --json`，按返回的唯一下一步先完成锁定排版校验，再新建并读回飞书文档。成功回执中的 `document_url` 才是在线预览链接；本地 HTML 保留为精确微信样式凭据。个人稿或用户明确接受的离线回退，才直接打开本机预览。

当前固定版本会把正文图片作为永久图片素材上传并缓存重复素材；自定义摘要暂不随 API 提交，需在公众号后台检查微信自动生成的摘要。`draft --execute` 只接受显式 `.env` 作为凭证真源并显示非敏感账号指纹；上传和建草稿不是原子事务，执行期失败后必须先检查目标账号后台和素材库，再决定是否重试。其余已知限制记录在发布参考文档中。

首次安装（从仓库根目录运行）：

```powershell
python -m pip install -r 微信公众号/requirements.txt
npm.cmd --prefix 微信公众号 install
Copy-Item 微信公众号/.env.example 微信公众号/.env
```

凭证只在本机填写到 `.env`，不要发到聊天中。

以下命令也从仓库根目录运行：

```powershell
# 本机手机宽诊断预览或明确接受的离线回退，不上传
python 微信公众号/tools/wechat_publish.py preview <内容包路径> --open

# 人工编辑交接，不上传；生成版本化复制页
python 微信公众号/tools/wechat_publish.py handoff <内容包路径> --open

# 草稿箱预检，默认 dry-run
python 微信公众号/tools/wechat_publish.py draft <内容包路径>

# 明确授权后：自动上传图片并创建一条公众号草稿
python 微信公众号/tools/wechat_publish.py draft <内容包路径> --execute
```

详细门禁和开发者配置见 [wechat-publishing.md](../.agents/skills/self-media-ops/references/wechat-publishing.md)。
