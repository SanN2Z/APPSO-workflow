---
title: "DeepSeek 自研 Harness 开内测，门票先发给同行"
platform: wechat
status: draft
created: 2026-08-02
updated: 2026-08-02
as_of: "2026-08-02 16:30+09:00"
fact_checked: false
rights_checked: false
copyedit_checked: false
copyedit_body_sha256: ""
published_url: ""
---

# DeepSeek 自研 Harness 开内测，门票先发给同行

> X 上有人问：现在让 Fable 5 现搭一套，还赶得上报名吗？我也差点信了。直到看见报名条件：GitHub ID，外加一个已经做过的开源项目。

LinearUncle 转发 DeepSeek Harness 的内测帖时开了个玩笑：等一下，他现在去让 Fable 5 花一个小时搭一套，再回来报名。

我看到的第一反应也是：这门票好像还能现场打印。

![LinearUncle 转发 DeepSeek Harness 内测帖时表示准备使用 Fable 5 现场搭建](assets/x-linearuncle-fable5-joke.png)

*LinearUncle 转发内测帖时开玩笑，准备让 Fable 5 花一小时现场搭一个。截图：@LinearUncle、@tianyi / X*

但原帖要的不是一个刚建好的仓库。

8 月 1 日，DeepSeek Harness 团队成员 [Tianyi Cui](https://x.com/tianyi/status/2083519855203078320) 定向招募内测者。条件写得很短：做过 Agent Harness 相关开源项目，报名时附上 GitHub ID 和代表作。

真正的门槛藏在「代表作」三个字里。一个仓库只要能跑起来，就可以做演示；一套 Harness 得被真实任务折腾过，才会留下另一种东西：上下文压缩后忘了什么，工具调用卡在哪层权限，模型说「完成」以后，测试究竟过没过。

这批开发者手里不只有代码，还有失败记录。

我顺着帖子往前翻了一天。DeepSeek-V4-Flash-0731 的[官方模型卡](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731)已经写明，公开 Code Agent 任务使用待发布的 DeepSeek Harness minimal mode 评测。

这里需要提醒一句：这些成绩来自模型、Harness 和评测设置共同组成的系统；Harness 尚未发布，外界暂时不能在同一环境里复跑。

把这条脚注和第二天的招募放在一起，我猜 DeepSeek 目前想收的是可拆解的失败：哪一步丢了上下文，哪条工具调用被权限卡住，哪次「完成」其实没通过测试。

普通体验者能说「这里不好用」；做过 Harness 的人，往往还能继续往下拆，并拿自己的实现作对照。这很像一次「请同行来拆台」。

这是我的判断，不是 DeepSeek 公布的测试目标。也可能没那么复杂：新团队只是想找能报出具体 bug 的测试者，顺便看看有没有合适的人。

所以，Fable 5 花一小时现搭一套，到底来不来得及？

真准备报名，我不会再开一个新仓库。我会从旧项目里挑一段失败轨迹：它怎么坏过，后来改了什么，现在还剩哪道坎。这个东西比首页截图更像内测材料。

拿到一个 GitHub 地址，也许来得及。拿到这张门票需要的东西，大概来不及。

一个小时够新建仓库，不够积累反例。

