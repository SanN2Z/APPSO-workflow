# APPSO 公众号版式反馈与样本证据

记录日期：2026 年 7 月 21 日

分级：用户反馈部分为 `internal`；公开页面测量为 `public-derived`。本文只保存排版事实与资源指纹，不复制参考文章正文。

## `LAYOUT-FB-001`：用户反馈

用户指出 APPSO 公众号稿每次进入后台都要手工调整排版，并指定普通长文的新合同：

- 小标题 20 px、橙色、加粗、左对齐。
- 正文 15 px。
- 正文块左右各缩进 16 px；不是首行缩进。
- 头图和尾图参考 APPSO 旧稿。

目标不是生成另一份需粘贴后再修的 HTML，而是让本机预览与草稿创建使用同一个可版本化 profile。

## `LAYOUT-SAMPLE-001`：3 篇公开样本

访问日期均为 2026 年 7 月 21 日：

1. [用户给出的样本](http://mp.weixin.qq.com/s?__biz=MjM5MjAyNDUyMA==&mid=2651098136&idx=1&sn=2c55dfe2dd2c3886d2a950cd940bd9d8&chksm=bc74f3a7c3472f0441d40f0a93df94f645f853e5e83eae69a62d642b9683301c1502f1cc8576&scene=0&xtrack=1&subscene=90#rd)
2. [复用核对样本 2](https://mp.weixin.qq.com/s/lwSJHjP3KCpBdu7rTMlrXw)
3. [复用核对样本 3](https://mp.weixin.qq.com/s/YZdoqo4eWbO1oqcCDujxBA)

样本 1 的正文段落计算样式为 `font-size: 15px`、`line-height: 25px`、`color: #222222`、`text-align: justify`、`padding: 0 15px`、`margin: 27px 0`。二级小标题为 `font-size: 21px`、`line-height: 29px`、`font-weight: 600`、`color: #FD4606`、`text-align: justify`、`padding: 0 15px`、`margin: 65px 0 27px`。

旧样本与用户新合同冲突的 3 项是小标题 21 → 20 px、对齐 justify → left、块级左右 15 → 16 px；实现一律以 `LAYOUT-FB-001` 为准，旧稿仅提供颜色、行高、间距与头尾结构参考。

## `LAYOUT-ASSET-001`：固定正文头图

3 篇样本的第一张正文图 URL 相同，是红底白字「APPSO 灵感指南」GIF：

- [公开原图](https://mmbiz.qpic.cn/mmbiz_gif/dCG7OC48IfIFGzbtia3FrZ8NMM5Y0b8Mo9uLMiaftBUD5xWbhAn931IVXgZRULx3wuYbU0SnBVV45H8AkiaERlNC1ggHWrF4EMVwSLOkj72Zlc/0?wx_fmt=gif&from=appmsg)
- 800 × 325 px；50 帧；约 4.25 秒。
- SHA-256：`df3a798b79526017666cec983077d1bacf76cc3d0395498397ac4a636aed4f97`
- 页面结构：全宽、圆角 10 px、容器行高 0，不继承正文块缩进。

该记录只能证明公开样本复用，不能代替公司内部原件或平台使用授权。生产包仍需本地文件、manifest 权利记录和 `wechat_body_header` 用途；当前仓库没有可直接发布的内部原件。

## `LAYOUT-ASSET-002`：固定正文尾图

3 篇样本的最后一张正文图 URL 相同，是「WE ARE HIRING / AI 方向编辑（APPSO）」招聘长图：

- [公开原图](https://mmbiz.qpic.cn/mmbiz_jpg/dCG7OC48IfJEkBSvibnp043w2NhQZzwDQQKb8MRnJcsjIOL5paicbJC9wW94ZbIH2zsx0fSTZJic0UkOTGrL5ksP97Mda498JK6U0kKj37ARg8/0?wx_fmt=jpeg&from=appmsg)
- 1200 × 1600 px。
- SHA-256：`a932807a6df317b58a65ec4feb544b42fd4e4511db8e1c03ef7679c427ff2b5c`
- 页面结构：正文末尾，顶部 24 px，左右各 16 px。

招聘信息有时效性，因此只作为候选尾部组件，默认不启用。生产包必须登记 `wechat_body_footer`，并按 Asia/Shanghai 填写下一次复核截止日。该日期是内部重新确认素材的门槛，不是招聘或活动的真实截止日；从本次确认日起最长不得超过 365 天，复核逾期后重新确认或移除。

## 实现与验证状态

- 数值样式真源：[`微信公众号/themes/appsso-article-v1.css`](<../../../微信公众号/themes/appsso-article-v1.css>)。
- 完整 profile 合同：[`微信公众号/themes/README.md`](<../../../微信公众号/themes/README.md>)。
- 本轮用临时测试包完成真实 Wenyan 渲染和 Edge 375 px / 390 px 人工检查；检查环境为 Edge `150.0.4078.83`，CSS SHA-256 为 `1e942c101bddb50be8940792bfef50a82560da3adf30d7c4dbbf0fcf10089a2f`。截图是可丢弃生成物，未作为知识资产入库。复现时在仓库根目录运行 `python 微信公众号/tools/wechat_publish.py preview <content-package> --open`，再在预览页依次切换 375 px 与 390 px。
- 尚未执行公众号草稿箱 round-trip；当前任务没有对外创建草稿的授权。
- Hunt Good 的 24 px 栏目名来自其专项培训资料；本轮只验证它不会自动继承普通长文 profile，没有声称已完成 Hunt Good 专项渲染。
