---
schema_version: 1
content_id: "hunt-good-2026-08-21"
title: "Stripe 要买 OpenRouter，数据中心走进选举｜周报"
platform: "wechat"
source_status: "ready"
review_kind: "delivery_feedback"
review_status: "closed"
created: 2026-08-21
updated: 2026-08-21
next_review_on: 2026-09-21
sop_promotions: 3
---

# 内容复盘：Stripe 要买 OpenRouter，数据中心走进选举｜周报

## 本轮结果

- 状态：内容包重新达到 `ready`；没有写入公众号草稿箱，也没有发布。
- 结构：7 条 News、3 个 Tools、3 个 Insights、1 个 Fun；彩蛋单独计算。
- 视觉：14 个正文条目全部有配图；11 条以官方／原作者／论文来源图为主，3 条使用插画信息图。Cursor、ChatGPT Ads 与 Agent Coordination 增加第二张证据图，正文共 19 张图。
- 重做：首版稀疏竖卡、旧封面与旧彩蛋全部判废；v2 横向文字卡仍因「纯文字」判废；最终只对 3 个关键机制使用由具体对象和动作承担叙事的插画信息图。
- 验收：用户指定 Prompt 与成功案例完成计划级绑定；6 个生成／修复任务 preflight 通过；原尺寸、约 390 px 手机宽度、整期 contact sheet 三层人工检查通过；内容包校验为 19 张 Markdown 图片、0 warning。

## 反馈台账

| ID | 来源 / 日期 | 阶段 | 反馈 | 根因 | 修复 | 验证 | 去向 |
|---|---|---|---|---|---|---|---|
| FB-001 | 用户 / 2026-08-21 | intake | 参考既有 Hunt Good 的格式、信息密度与生动配图 | 需要先锁定栏目合同 | 建立 7 / 3 / 3 / 1 正文 | 栏目计数通过 | case_only |
| FB-002 | 视觉自检 / 2026-08-21 | rendering | 首版竖封面副标题压住主标题 | 显式换行与自动换行冲突 | 固定坐标重渲染 | 原尺寸复核 | watch |
| FB-003 | 用户 / 2026-08-21 | delivery_feedback | 不可能全用自制图片，只有关键信息值得做信息图；要搜索高质量相关配图 | 把「每条有图」误执行为「每条自制」 | 逐条重做来源图／信息图判断，来源图作为默认 | 14 条均有决策，来源图占多数 | project_adapter |
| FB-004 | 用户 / 2026-08-21 | delivery_feedback | 使用桌面「公众号」里的制作方法和 APPSO 图片；固定 7 / 3 / 3 / 1 | 专项 SOP 仍有旧弹性，品牌资产没有进入硬门 | 核对同哈希规范与 Logo，更新结构和来源图合同 | 目录、Logo、manifest 通过 | project_adapter |
| FB-005 | 用户 / 2026-08-21 | delivery_feedback | 「信息图做的太丑，内容也不够丰富。视觉检验不过关。」 | 首轮验收只检查数量、Logo、manifest 和无溢出；5 张图复用稀疏竖卡骨架，研究观点用简化图标代替原始证据；正文只给结论，缺条件与反例 | 废弃 v1；3 张机制图重做为横向编辑卡；Model Hypnosis 与 Agent Coordination 改用论文图；补 ChatGPT Ads 置信区间与曝光阶段区别、Agent Coordination 缓存变化与反例 | 原尺寸、手机宽度、contact sheet、YAML、renderer、内容包校验全部通过 | project_adapter |
| FB-006 | 用户 / 2026-08-21 | delivery_feedback | 展示成功火箭信息图并指出「里面有图有文字，你做的这是啥啊，纯文字？」；追问「信息图有 prompt，你看了吗」 | 已读桌面规范，但只抽取排版规则，没有把受控 Prompt 与成功案例绑定进实际生图任务；v2 仍由白卡片和文字承担主叙事，插图缺席 | 新建 `appsso-hunt-good-illustrated-infographic-v1` 档案；把成功案例、Prompt、事实卡、输入顺序和约束写入计划与 receipt；Google／ZDR／Ads 改为插画叙事并逐字修正数字；确定性叠加登记版 Logo | 3 张原尺寸图、390 px 检查表、19 图 contact sheet、6 个 receipt 与内容包 validator 全部通过 | project_adapter |

## 因果复盘

```text
来源图配比、Logo 和文件台账通过
→ 被误当成视觉质量通过
→ 稀疏模板卡仍进入交付，研究段也只有结论没有足够证据层
→ 用户在真实阅读尺度上直接判定「太丑、内容不够丰富」
→ 视觉门从合规检查升级为原尺寸／手机／整期三层成品检查
→ v2 又把「内容丰富」误执行为增加文字与卡片，仍没有让插画承担叙事
→ 用户用成功案例明确纠正，并追问 Prompt 是否实际执行
→ 生图门增加 Prompt／参考图计划级绑定；插画信息图必须由具体对象、动作、编号和箭头讲清主流程
→ 信息图同时保留主判断、关系、数字或条件与边界；论文证据可用时优先原图
```

## 已固化的窄范围配置

- `HG-STRUCTURE-001`：Hunt Good 默认 7 / 3 / 3 / 1，只有主编锁题前明确调整才偏离。
- `HG-VISUAL-001`：逐条先搜一手高质量相关图；信息图是有门槛的例外；自制图带 APPSO 标识并登记权利。
- `HG-VISUAL-QUALITY-001`：进入 `ready` 前必须查看原尺寸、约 390 px 手机宽度和整期 contact sheet；当前任务指定 Prompt／成功案例必须绑定到生图计划与 receipt；插画信息图由具体图像承担主叙事，纯文字卡不能冒充；只做数量／Logo／manifest 检查不能判 pass。

三条均为主理人明确偏好的 E0 项目配置，只作用于 APPSO Hunt Good，不外推为所有公众号稿的通用规则。

## SOP 变更

| 规则 ID | 真源 | 触发 | 通过标准 | 来源案例 | 结果 |
|---|---|---|---|---|---|
| HG-STRUCTURE-001 | `APPSO-数字资产/03-SOP/Hunt Good 周报专项 SOP.md` | 新一期选题、写作或复核 | 目录与正文为 7 / 3 / 3 / 1，或有明确调整记录 | FB-004 | promoted_e0 |
| HG-VISUAL-001 | 同上 | 条目入池、锁题、视觉制作或发布前 | 14 条有决策；来源图默认；信息图有必要性、Logo 与权利记录 | FB-003—004 | promoted_e0 |
| HG-VISUAL-QUALITY-001 | 同上 | 视觉准备进入 `ready` | Prompt／成功案例有计划级绑定；原尺寸、手机、contact sheet 三层均看过；插画对象承担主叙事，自制图有证据层且无重复模板感 | FB-005—006 | promoted_e0 |

## 下一轮动作

- [ ] 锁题表直接创建 14 条视觉决策，先找来源图再判断是否做信息图。
- [ ] 制图前先写图的「一句主判断 + 两项证据／条件 + 边界」，写不出来就不做信息图。
- [ ] 用户提供 Prompt 或成功案例时，把两者写入生图计划、固定输入顺序并取得 pass receipt；禁止只读规范后凭摘要执行。
- [ ] 选用插画信息图时，为每个主要步骤指定一个具体对象、动作或场景；遮住说明文字仍应能看出流程。
- [ ] 发稿前保存并人工打开原尺寸、手机宽度和整期 contact sheet；任一层未看，不得写视觉 pass。
- [ ] 2026-09-21 复核三层检查是否减少返工，以及读者是否仍认为论文图在手机端过小。
- [ ] 只有用户明确授权本次账号、正文、图片和动作后，才进入公众号草稿或发布流程。

## 证据清单

- 成稿：`draft.md`
- 事实与图片来源：`sources.md`
- 逐图决策：`research/visual-notes.md`
- 生图 Prompt 与计划：`APPSO-数字资产/01-栏目与品牌/品牌视觉/生图-Prompt/Hunt Good 插画信息图.md`、`research/image-generation-plan.json`、`research/image-generation-runs/`
- 可复现收尾与预览：`research/finalize_illustrated_infographics.py`、`research/render_visual_checks_v3.py`
- 视觉总览：`research/contact-sheet-v3.png`、`research/mobile-visual-check-v3.png`
- 权利台账：`asset-manifest.yml`
- 编辑与终校：`review.md`、`copyedit.md`
- 发布记录：无。
