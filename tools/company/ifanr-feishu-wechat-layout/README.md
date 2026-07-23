# 爱范儿一键排版扩展

这是公司飞书定稿到微信公众号草稿的 Chrome 扩展规范入口。源码和内嵌品牌素材经用户于 2026 年 7 月 23 日明确授权，按 `restricted`、`private-repository-only` 保存到当前私有仓库。

## 当前版本

- 版本：`1.10.0`
- 源码目录：[`v1.10.0/`](<v1.10.0/>)
- Chrome 加载目录：`tools/company/ifanr-feishu-wechat-layout/v1.10.0/extension`
- 上游来源：用户提供的公司工具包
- 原始文件：22 个，共 3,347,963 bytes
- `manifest.json` SHA-256：`AA4E61E879FDE34DDB09383F51AB0B99DB373BEACB89EEC456D4CFAF4F635396`
- 原始文件树 SHA-256：`50E9DE945BECBCAE5EAA1A068A4E3CEE63EB5CCAF3F983E40150877C07068862`

文件树指纹口径：按 POSIX 相对路径排序；每行写入「相对路径、Tab、对应文件 SHA-256 大写值、LF」，再对完整 UTF-8 文本计算 SHA-256。

## 使用

1. 在 `chrome://extensions` 打开开发者模式。
2. 选择「加载已解压的扩展程序」。
3. 加载 `v1.10.0/extension/`。
4. 按[公司飞书到公众号浏览器排版 SOP](<../../../APPSO-数字资产/03-SOP/公司飞书到公众号浏览器排版 SOP.md>)完成资格验证和正式执行。

仓库根目录中的原始交付副本继续作为本地归档忽略。完成切换后，应让 Chrome 指向这里的版本目录，避免两份源码漂移。

## 入库审计

- 11 个 JavaScript 文件通过 `node --check`。
- `manifest.json` 可解析，引用的本地资源存在。
- 未发现硬编码密钥、Token、Cookie、个人路径、浏览器 Profile、账号导出、第三方遥测、远程脚本或动态 `eval`。
- 未发现 `node_modules`、构建目录、缓存、日志、`.crx` 或重复发行包。
- 当前包没有 `LICENSE` 或 `NOTICE`；进入私有仓库不改变其权利边界，也不构成公开许可。
- 当前包没有附带 `127.0.0.1:43127` 增强服务。浏览器页面直读失败时，不得下载来源不明的替代程序。

## 已知问题

- 扩展会把飞书 URL、标题、正文 HTML、Base64 图片和写入状态暂存到 `chrome.storage.local`。
- v1.10.0 的「清除」会移除主要内容包，但不会完整清除 `ifanrWechatPageStatus`；该键可能继续保留草稿 ID 或标题。
- 在代码修复并完成回归前，必须使用公司专用 Chrome Profile。处理敏感稿、离开共享设备或停用 Profile 前，还要在扩展调试页清空该扩展的本地存储。

## 更新规则

新版本放入新的 `v<version>/` 目录，重新执行凭据扫描、JavaScript 语法检查、manifest 与文件树哈希登记，再按空白资格验证草稿完成真实公众号后台往返。不得直接覆盖 v1.10.0。
