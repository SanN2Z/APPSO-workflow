# 事实卡

核查日期：2026-07-13（北京时间口径）

## 论文身份

- 标题：B-spline Policy: Accelerating Manipulation Policies via B-spline Action Representations
- arXiv：2607.09648，cs.RO
- 作者：Xiaoshen Han、Haoyu Xiong、Haonan Chen、Chaoqi Liu、Antonio Torralba、Yuke Zhu、Yilun Du
- 机构：Harvard、MIT、UT Austin
- v1 提交：2026-07-10 17:46:32 UTC，即北京时间 2026-07-11 01:46:32
- 列表位置：2026-07-13 的 arXiv cs.RO recent 批次第 1 位
- 论文状态：arXiv v1 预印本；论文页面未标注已被会议或期刊接收
- 配套材料：官方项目页、GitHub 代码和 Colab 已公开；GitHub 仓库显示 MIT License

## 方法

- 基线动作表示：策略一次输出固定长度的离散动作块。
- BSP：策略输出局部 B 样条的节点与控制点，用连续曲线表示未来动作。
- 演示转换：用自适应拟合把离散演示轨迹转成 B 样条；在重建误差最大的区段继续插入节点。
- 样条类型：三次 B 样条，论文表述为具有连续的速度和加速度曲线。
- 频率解耦：论文流程图给出的典型设置是策略 10Hz 推理、低层控制 100Hz 采样；附录确认真实机器人和仿真均以 100Hz 采样 B 样条动作。
- 时间缩放：改变真实时间到曲线参数的映射，保持命令轨迹的几何形状并更快走完。
- 片段对齐：在新预测片段中搜索与最近已执行动作最匹配的位置，从该位置开始执行，降低相邻片段的边界跳变。

## 真实机器人实验

- 机械臂：6-DoF ARX5；叠杯使用双臂，其余任务使用单臂。
- 任务：Cube Picking、Table Cleaning、Speed Stacking。
- 演示数量：分别为 200、300、200 条。
- 策略骨干：Diffusion Policy；ACT 式回归策略（论文表格称 Regression Policy）。
- 其他对比：直接提高执行频率，以及 DemoSpeedUp。
- 每个真实任务、每种设置：20 次 rollout，使用预先记录的固定测试布局。
- 平均完成时间：只在成功 rollout 上取平均。

## 关键结果

- 论文作者汇总：BSP 在 18 个真实实验设置中的 14 个设置里，成功率持平或提高。
- Table Cleaning / Regression / 目标 4X：
  - 基线：13/20，23.57 秒；
  - Reg.+BSP：14/20，11.80 秒。
- Speed Stacking / Fig. 5 代表性轨迹：
  - Diffusion Policy：20.5 秒；
  - Diffusion+BSP：9.6 秒；
  - 图中标注 2.14X faster。该图是定性案例，不是平均结果。
- Speed Stacking / 片段对齐消融：
  - 目标 1X：实现速度 1.0X→1.1X，成功率 35%→70%；
  - 目标 2X：实现速度 1.3X→1.8X，成功率 50%→75%；
  - 目标 4X：实现速度 1.7X→2.2X，成功率 15%→35%。
- Speed Stacking / Regression / 目标 4X：基线与 Reg.+BSP 均为 0/20。
- Push-T / 目标 4X：Diffusion+BSP 的平均分为 0.73，对比基线 0.59；完成时间 2.87 秒，对比基线 7.19 秒。论文解释为更快执行允许策略在最大 rollout 时限内做更多修正。

## 事实边界与编辑判断

- **事实**：表格数字、实验设置、方法结构、提交时间、项目页和代码状态。
- **作者自报**：方法“plug-and-play”、总体更平滑、硬件是极端速度失败的主要原因。
- **编辑判断**：这项工作的价值是改造模型到执行器之间的动作接口，而不是提升模型认知能力。
- **限制**：v1 预印本；真实实验每设置 20 次；平均时间只统计成功样本；没有独立复现；真实机器人只覆盖三类任务和同一类低成本机械臂平台。
- **相关工作边界**：BEAST 已在 2025 年使用 B 样条编码动作序列，并被 NeurIPS 2025 接收。BSP 的论文自述差别在于，它把 B 样条作为面向高速控制的连续动作表示和执行流水线，而不是主要作为动作 tokenizer。
