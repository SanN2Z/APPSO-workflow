# 微信公众号版式 profile

本目录保存「可复现的发布样式」，不是稿件正文。内容包通过 `publish.yml` 显式选择 profile；预览与草稿创建共用同一份 CSS，避免在公众号后台逐项重调。

用户反馈、3 篇公开样本、计算样式和头尾图资源指纹只在 [APPSO 公众号版式反馈与样本证据](<../../APPSO-数字资产/02-方法与知识/视觉与排版/APPSO 公众号版式反馈与样本证据.md>)维护；本文件只保存当前可执行合同。

## `appsso-article-v1`

适用范围：APPSO 普通公众号长文。Hunt Good 与个人公众号不适用。

唯一样式真源：[`appsso-article-v1.css`](appsso-article-v1.css)。当前合同为：正文 15 px、25 px 行高、左右各 16 px、两端对齐；二级小标题 20 px、`#FD4606`、字重 600、左对齐；正文和普通配图按块缩进，固定正文头图保持全宽。

## 正文头图参考

旧稿复用的「APPSO 灵感指南」GIF 作为正文头部品牌组件参考；样本 URL、尺寸、帧数、SHA-256 和结构测量以证据文件为准。生产稿不得热链微信 CDN。取得公司内部原件或确认可复用副本后，将文件放入当前内容包 `assets/`，在 manifest 登记 `use: "wechat_body_header"`、来源、权利和允许平台，再由 `header_image` 自动注入。组件保持全宽，不继承正文 16 px 缩进。

## 正文尾图参考

旧稿末尾复用的招聘长图只作为候选尾部组件；样本 URL、尺寸、SHA-256 和结构测量以证据文件为准。它包含具体岗位，不是永久品牌组件，默认不启用。使用时必须保存为内容包本地文件并登记 `use: "wechat_body_footer"`，再按 Asia/Shanghai 在 `publish.yml` 写入下一次复核截止日 `footer_valid_until`。该日期只表示内部素材复核门槛，不代表招聘或活动的真实截止日；从本次确认日起最长不得超过 365 天，复核逾期后必须重新确认或移除。

## 内容包入口

```yaml
layout_profile: "appsso-article-v1"
header_image: "assets/appsso-inspiration-guide.gif"
header_alt: "APPSO 灵感指南"
footer_image: ""
footer_alt: ""
footer_valid_until: ""
```

完整命令、manifest 门禁和预览方法见 [wechat-publishing.md](../../.agents/skills/self-media-ops/references/wechat-publishing.md)。

发布适配器以 Wenyan 的实际渲染结果为准校验图片：远程图、未登记本地图、额外的 `srcset` / `data-src`、CSS 外部图源和重复头尾组件都会阻断草稿创建。结构有效的包内图片可以暂存到本次独立构建目录供本机预览，但只有 validator 与渲染门禁均无 blocker 的密封构建才允许进入 `--execute`；历史 `dist/assets/` 不会被复用。
