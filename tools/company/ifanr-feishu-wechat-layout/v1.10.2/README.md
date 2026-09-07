# 1.10.2｜页面连接恢复候选

restricted / private-repository-only。基于 1.10.1，保留头图 0 缩进与正文 16 px 的独立段落修复。

## 本次修复

- 读取飞书、写入公众号前，先检测对应版本的页面接收脚本。
- 缺失时用现有 scripting 与网站权限加载插件自带脚本，不访问增强服务或下载外部代码。
- 控制脚本使用局部作用域和安装标记，重复补载不重复注册消息处理器。
- 操作锁定原标签页的 documentId；页面跳转、目标不符或权限不足时不发送正文。
- 页面连接失败明确结束 processing 状态；发送后的断连提示先检查草稿，绝不自动重发写入。
- 不添加网站权限；最低 Chrome 106，用于按 documentId 定位。

## 使用

1. 在 chrome://extensions 停用旧版。
2. 加载本版本 extension 文件夹，确认版本 1.10.2。
3. 在飞书文档重新收录一次。新目录对应的扩展可能没有旧版暂存内容。
4. 回到唯一保留的公众号图文编辑页，打开插件并排版。
5. 真实稿件覆盖仍由用户选择目标并点击。保存后重开核对样式及手机预览。

不要求安装本机增强服务。本轮未操作真实公司草稿；不宣称真实公众号或冷克隆验收完成。既有稿件不会自动修复缩进。

## 验证

仓库根目录运行：

```text
node tools/company/ifanr-feishu-wechat-layout/tests/page-connection.cjs
node tools/company/ifanr-feishu-wechat-layout/tests/paragraph-editability.cjs 1.10.2
```

前者为 14 项模拟 Chrome API 的连接测试，包含真实页面脚本的重复执行与弹窗状态处理。后者为 20 项隔离 Chrome 的补图、段落边距与重新解析检查。二者均不访问真实账号。23 个扩展文件及 manifest 哈希见 local-validation.json。当前工具链仍锁定原版，候选需实际试用后再决定切换。

接口依据：[Chrome scripting 官方文档](https://developer.chrome.com/docs/extensions/reference/api/scripting)。
