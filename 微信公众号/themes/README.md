# 微信公众号版式 profile

本目录只保存「可复现视觉主题」及其兼容能力，不是稿件正文，也不决定采用哪种交付方式。APPSO 的模式选择以 [`APPSO 内容生产 SOP`](<../../APPSO-数字资产/03-SOP/APPSO 内容生产 SOP.md#7-排版与交付>) 为真源，通用执行与安全边界以 [`wechat-publishing.md`](../../.agents/skills/self-media-ops/references/wechat-publishing.md) 为真源。

用户反馈、3 篇公开样本、计算样式和头尾图资源指纹只在 [APPSO 公众号版式反馈与样本证据](<../../APPSO-数字资产/02-方法与知识/视觉与排版/APPSO 公众号版式反馈与样本证据.md>)维护；本文件只保存当前可执行合同。

## `appsso-article-v1`

适用范围：`project_adapter: "appsso"` 且 `delivery_mode: "sealed_draft"` 的 APPSO 普通长文。人工编辑交接、Hunt Good 与个人公众号不适用。

截至 2026 年 7 月 22 日，该 profile 只完成本机 375 px / 390 px 预览，尚未完成真实后台往返验证。验证前，任何使用该 profile 创建的草稿都只能称为「资格验证草稿」；只有后台 round-trip 通过后，经过验证的精确公众号账号与主题版本组合才取得生产密封草稿资格。

唯一样式真源：[`appsso-article-v1.css`](appsso-article-v1.css)。当前合同为：正文 15 px、25 px 行高、左右各 16 px、两端对齐；二级小标题 20 px、`#FD4606`、字重 600、左对齐；正文和普通配图按块缩进，固定正文头图保持全宽。

## 正文头图参考

旧稿复用的「APPSO 灵感指南」GIF 作为正文头部品牌组件参考；样本 URL、尺寸、帧数、SHA-256 和结构测量以证据文件为准。生产稿不得热链微信 CDN。取得公司内部原件或确认可复用副本后，将文件放入当前内容包 `assets/`，在 manifest 登记 `use: "wechat_body_header"`、来源、权利和允许平台，再由 `header_image` 自动注入。组件保持全宽，不继承正文 16 px 缩进。

## 正文尾图参考

旧稿末尾复用的招聘长图只作为候选尾部组件；样本 URL、尺寸、SHA-256 和结构测量以证据文件为准。它包含具体岗位，不是永久品牌组件，默认不启用。使用时必须保存为内容包本地文件并登记 `use: "wechat_body_footer"`，再按 Asia/Shanghai 在 `publish.yml` 写入下一次复核截止日 `footer_valid_until`。该日期只表示内部素材复核门槛，不代表招聘或活动的真实截止日；从本次确认日起最长不得超过 365 天，复核逾期后必须重新确认或移除。

## Profile 能力合同

`appsso-article-v1` 只接受 `project_adapter: "appsso"` 与 `delivery_mode: "sealed_draft"` 的合法组合，并把 Wenyan 视觉旋钮锁定为 `theme: "default"`、`highlight: "solarized-light"`、`mac_style: false`，避免基础主题与受控 CSS 叠加漂移。它要求权利明确、已登记的 `header_image`；`footer_image` 可选，但启用后必须通过用途、平台、权利和复核日期门禁。模式的默认值和切换条件不在本文件维护。

头尾图组件由项目 adapter 提供，不由视觉主题推断。若人工交接稿未携带组件，只能由获授权编辑从权利已确认的公司素材库中在公众号后台补插；没有权利明确的内部原件时不得插入，也不得用公开 CDN 副本冒充已授权原件。

完整命令、manifest 门禁和预览方法见 [wechat-publishing.md](../../.agents/skills/self-media-ops/references/wechat-publishing.md)。

使用本 profile 时，发布适配器以 Wenyan 的实际渲染结果为准校验图片：远程图、未登记本地图、额外的 `srcset` / `data-src`、CSS 外部图源和重复头尾组件都会阻断密封草稿命令。只有 validator 与渲染门禁均无 blocker 的本次独立密封构建才允许进入 `--execute`；历史 `dist/assets/` 不会被复用。
