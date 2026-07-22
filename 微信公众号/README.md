# 微信公众号子项目

公众号文章按「一个选题一个内容包」管理。项目采用六角色写作团队：主编、证据编辑、特稿主笔、语法终校、视觉版权编辑和独立终审；运行规则见 `../.agents/skills/self-media-ops/references/wechat-team.md`。

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
├─ brief.md
├─ draft.md
├─ sources.md
├─ copyedit.md
├─ review.md
├─ asset-manifest.yml
├─ publish.yml
├─ assets/
├─ research/
├─ tools/
├─ dist/                   # 自动生成，本地预览和上传输入
└─ publish-record.md
```

`draft.md` 保存当前可编辑正文，`sources.md` 记录证据，`copyedit.md` 记录最终正文的逐句语法签字和哈希，`asset-manifest.yml` 记录图片权利和来源，`publish-record.md` 只写真实发布结果。

不按 `draft/ready/published` 移动目录。结构性反馈放入内容包 `research/` 并同步 `review.md`；跨文章可复用的规律再提炼到 `知识库/`。

## 本机预览与草稿箱

排版、图片上传和微信草稿 API 复用开源 [Wenyan CLI](https://github.com/caol64/wenyan-cli)，项目固定为 `@wenyan-md/cli@2.0.11`；本地适配层不重复实现渲染器和微信客户端。配置把品牌 `project_adapter`、交付方式 `delivery_mode` 与视觉主题 `layout_profile` 分开；APPSO、Hunt Good 与个人公众号不得互相猜测或继承。交付模式、命令和安全边界见 [wechat-publishing.md](../.agents/skills/self-media-ops/references/wechat-publishing.md)，主题能力与精确样式见 [themes/README.md](themes/README.md)。

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
# 本机手机宽预览，不上传
python 微信公众号/tools/wechat_publish.py preview <内容包路径> --open

# 人工编辑交接，不上传；生成版本化复制页
python 微信公众号/tools/wechat_publish.py handoff <内容包路径> --open

# 草稿箱预检，默认 dry-run
python 微信公众号/tools/wechat_publish.py draft <内容包路径>

# 明确授权后：自动上传图片并创建一条公众号草稿
python 微信公众号/tools/wechat_publish.py draft <内容包路径> --execute
```

详细门禁和开发者配置见 [wechat-publishing.md](../.agents/skills/self-media-ops/references/wechat-publishing.md)。
