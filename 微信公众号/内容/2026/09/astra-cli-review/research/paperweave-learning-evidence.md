# FB032｜学习、复杂任务与 Paperweave

核查日期：2026-09-05。本轮补末节前一节，并调整最后两段落点；开头、实测和跑分信息图不重开。

## 当前采用来源

- 印度科学理工学院 EECS 官方实录：https://eecs.iisc.ac.in/fireside-chat-sir-demis-hassabis-and-prof-govindan-rangarajan/ 。活动日期 2026-02-17，Google DeepMind 联合创始人兼 CEO Demis Hassabis 与校长 Govindan Rangarajan 对谈。正文引用 Audience person 2 与 Hassabis 的问答（实录末段），其中确有「learning to learn」，并建议理解适合自己的环境与学习方式。只引用该短语，其余用间接转述。原采访不是对 Astra 的评论。
- 官方应用介绍：https://openai.com/index/gpt-6-astra/ ，Advancing scientific discovery 段介绍用专业软件检查科研数据和探索结果。正文明确为官方介绍，不宣称本次小游戏验证了科研能力。
- 「复杂任务难用短 GIF 说明」「学得更多，提问更具体」为作者观点；加快文献整理与实验有机会促进科学发现，为条件性判断，不写成已取得发现。

按作者最新偏好撤掉原先候选教授引语及姓名；不将私人关系写进稿件、交接正文或来源表。替代引用只取与论点相关的一小段，不扩大人物介绍。

## 项目与配图核对

用户明确提供 D:/projects/AgentLab_Gpt 并要求截图或 GIF；相关产品为其下 paperweave。仅读产品 README、AGENTS、AGENT_GUIDE、REFERENCE 与演示截图相关代码，未检查其他科研资料。

产品文档支持文献画布、PDF 选文交给 CLI、带来源笔记和写作。Paperweave 提供 UI 与持久状态，模型能力来自接入的 CLI；不写成它自身是独立基础模型。用户未确认搭建所用模型、时间或轮次，不将它计为 Astra 专项实测，也不宣称一次生成或已加速科学发现。

capture_paperweave.mjs 从现有 dist 启动 loopback 实例，使用新建 OS 临时目录和项目原有 seedDemo 虚构数据。未读取作者真实研究库、私人论文、CLI 账户或凭据，未修改产品源码。实际执行隐藏空白终端、查看画布、拖动卡片和打开研究笔记。截图保留真实界面像素。

原图为 1150 × 780 CSS 像素、1.5 倍截图，逐张查看内容和敏感信息。关闭演示浏览器后 node-pty 清理子进程输出 AttachConsole failed，主截图流程 exit 0；不将截图成功当作产品完整测试通过。

- paperweave-map.png：放在工作台介绍后，展示论文与关系的空间组织；图注注明虚构演示数据。
- paperweave-notes.png：放在阅读与证据判断后，展示问题、来源与笔记；图内及图注均写明演示性质。
- paperweave-map-drag.png：作为交互过程核对，不在正文重复摆放。

手机复看后，全屏截图中的字过小。正文换成浏览器直接截取的 map-focus 与 notes-focus：前者保留两张完整卡片和关系线，后者保留笔记标题、演示声明、问题与来源。全屏原图继续留存；不重排原生界面，图注明确局部取景。

没有生成 GIF；本轮正文用两张 PNG。保持 draft，未将图片权利标为发布放行；仅刷新本地预览和素材包，不声称飞书已上传。
