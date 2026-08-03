from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch


PACKAGE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = PACKAGE_DIR / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

FONT_REGULAR = Path("C:/Windows/Fonts/msyh.ttc")
FONT_BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")
if FONT_REGULAR.exists():
    font_manager.fontManager.addfont(str(FONT_REGULAR))
if FONT_BOLD.exists():
    font_manager.fontManager.addfont(str(FONT_BOLD))

plt.rcParams["font.family"] = "Microsoft YaHei"
plt.rcParams["axes.unicode_minus"] = False

INK = "#17233C"
MUTED = "#667085"
BLUE = "#3F7CFF"
LIGHT_BLUE = "#EAF1FF"
ORANGE = "#F4A340"
LIGHT_ORANGE = "#FFF3DF"
GREEN = "#2BAA7B"
LIGHT_GREEN = "#E4F6EF"
RED = "#DF5F5F"
GRID = "#DDE3EC"
WHITE = "#FFFFFF"


def rounded_box(ax, xy, width, height, face, edge=GRID, radius=0.025, lw=1.5):
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle=f"round,pad=0.012,rounding_size={radius}",
        linewidth=lw,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(box)
    return box


def save(fig, filename):
    path = ASSETS_DIR / filename
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    print(path)


def render_timeline():
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor(WHITE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.06,
        0.91,
        "DeepSeek Harness 的公开时间线",
        fontsize=30,
        fontweight="bold",
        color=INK,
        va="center",
    )
    ax.text(
        0.06,
        0.855,
        "从组建团队、进入模型卡，到定向邀请开源作者内测",
        fontsize=16,
        color=MUTED,
        va="center",
    )

    y = 0.38
    ax.plot([0.12, 0.88], [y, y], color=GRID, linewidth=6, solid_capstyle="round")
    events = [
        {
            "x": 0.18,
            "date": "6 月 21 日",
            "tag": "团队公开招人",
            "body": "Tianyi Cui 称 Harness\n是新成立的部门，\n招聘研究员、工程师、产品经理",
            "color": ORANGE,
            "face": LIGHT_ORANGE,
        },
        {
            "x": 0.50,
            "date": "7 月 31 日",
            "tag": "进入 V4 模型卡",
            "body": "公开 Code Agent 任务\n使用 DeepSeek Harness minimal mode\n并标注「待发布」",
            "color": BLUE,
            "face": LIGHT_BLUE,
        },
        {
            "x": 0.82,
            "date": "8 月 1 日",
            "tag": "定向招募内测",
            "body": "只邀请开源 Harness 开发者，\n要求提交 GitHub ID\n与代表作",
            "color": GREEN,
            "face": LIGHT_GREEN,
        },
    ]

    for event in events:
        x = event["x"]
        ax.add_patch(
            Circle((x, y), 0.025, facecolor=event["color"], edgecolor=WHITE, linewidth=4)
        )
        rounded_box(
            ax,
            (x - 0.13, 0.50),
            0.26,
            0.27,
            event["face"],
            edge=event["color"],
            radius=0.02,
        )
        ax.text(
            x,
            0.72,
            event["date"],
            fontsize=22,
            fontweight="bold",
            color=INK,
            ha="center",
        )
        ax.text(
            x,
            0.665,
            event["tag"],
            fontsize=16,
            fontweight="bold",
            color=event["color"],
            ha="center",
        )
        ax.text(
            x,
            0.60,
            event["body"],
            fontsize=13.5,
            color=INK,
            ha="center",
            va="top",
            linespacing=1.35,
        )

    ax.text(
        0.06,
        0.12,
        "来源：Tianyi Cui 公开帖、DeepSeek-V4-Flash-0731 官方模型卡。图中只复述公开动作，不代表产品已正式发布。",
        fontsize=12.5,
        color=MUTED,
    )
    save(fig, "timeline-harness-public-signals.png")


def render_benchmark():
    benchmarks = [
        "Terminal Bench 2.1",
        "NL2Repo",
        "Cybergym",
        "DeepSWE",
        "Toolathlon-Verified",
        "Agents' Last Exam",
        "AutomationBench Public",
    ]
    current = [82.7, 54.2, 76.7, 54.4, 70.3, 25.2, 25.1]
    preview = [61.8, 39.4, 38.7, 7.3, 49.7, 15.8, 10.8]

    fig, ax = plt.subplots(figsize=(16, 10))
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)

    y = list(range(len(benchmarks)))
    height = 0.34
    ax.barh(
        [i - height / 2 for i in y],
        current,
        height=height,
        color=BLUE,
        label="V4-Flash-0731",
    )
    ax.barh(
        [i + height / 2 for i in y],
        preview,
        height=height,
        color="#C7D4EA",
        label="V4-Flash Preview",
    )

    for i, value in enumerate(current):
        ax.text(
            value + 1.2,
            i - height / 2,
            f"{value:.1f}",
            va="center",
            fontsize=12.5,
            color=INK,
            fontweight="bold",
        )
    for i, value in enumerate(preview):
        ax.text(
            value + 1.2,
            i + height / 2,
            f"{value:.1f}",
            va="center",
            fontsize=12.5,
            color=MUTED,
        )

    ax.set_yticks(y)
    ax.set_yticklabels(benchmarks, fontsize=13.5, color=INK)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.tick_params(axis="x", labelsize=11.5, colors=MUTED)
    ax.grid(axis="x", color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.text(
        0.075,
        0.955,
        "DeepSeek 官方模型卡中的 Agent 基准变化",
        fontsize=28,
        fontweight="bold",
        color=INK,
    )
    fig.text(
        0.075,
        0.912,
        "DeepSeek-V4-Flash-0731 对比 Preview｜数值为厂商自报",
        fontsize=15,
        color=MUTED,
    )
    ax.legend(
        loc="lower right",
        frameon=False,
        fontsize=12.5,
        bbox_to_anchor=(1.0, -0.02),
        ncol=2,
    )
    fig.text(
        0.075,
        0.028,
        "注：图表仅重绘官方模型卡。官方说明，其中公开 Code Agent 任务使用待发布的 DeepSeek Harness minimal mode；\n模型卡未公开完整任务轨迹，不能把分数变化单独归因于 Harness。来源：DeepSeek-V4-Flash-0731 官方模型卡。",
        fontsize=11.5,
        color=MUTED,
        linespacing=1.5,
    )
    plt.subplots_adjust(left=0.22, right=0.95, top=0.85, bottom=0.15)
    save(fig, "benchmark-agent-scores.png")


def render_system_stack():
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor(WHITE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.06,
        0.91,
        "Harness 把模型接到真实任务上",
        fontsize=30,
        fontweight="bold",
        color=INK,
    )
    ax.text(
        0.06,
        0.855,
        "模型负责推理，运行框架负责准备条件、开放工具、限制权限，并检查结果",
        fontsize=16,
        color=MUTED,
    )

    rounded_box(ax, (0.39, 0.70), 0.22, 0.10, LIGHT_ORANGE, edge=ORANGE)
    ax.text(
        0.50,
        0.75,
        "模型",
        fontsize=22,
        fontweight="bold",
        color=INK,
        ha="center",
        va="center",
    )

    rounded_box(
        ax,
        (0.25, 0.24),
        0.50,
        0.38,
        LIGHT_BLUE,
        edge=BLUE,
        radius=0.03,
        lw=2.2,
    )
    ax.text(
        0.50,
        0.575,
        "HARNESS / 运行框架",
        fontsize=20,
        fontweight="bold",
        color=BLUE,
        ha="center",
    )

    items = [
        (0.29, 0.425, "上下文与记忆", "给模型看什么，忘掉什么"),
        (0.52, 0.425, "文件与工具", "终端、网络、API 怎样调用"),
        (0.29, 0.285, "权限与沙箱", "哪些动作必须停下来确认"),
        (0.52, 0.285, "重试与验收", "失败后怎么回来，完成后谁检查"),
    ]
    for x, y, title, subtitle in items:
        rounded_box(ax, (x, y), 0.19, 0.105, WHITE, edge="#B9C8E8", radius=0.015)
        ax.text(
            x + 0.095,
            y + 0.068,
            title,
            fontsize=15,
            fontweight="bold",
            color=INK,
            ha="center",
        )
        ax.text(
            x + 0.095,
            y + 0.032,
            subtitle,
            fontsize=10.5,
            color=MUTED,
            ha="center",
        )

    rounded_box(ax, (0.055, 0.37), 0.13, 0.12, LIGHT_GREEN, edge=GREEN)
    ax.text(
        0.12,
        0.445,
        "用户目标",
        fontsize=17,
        fontweight="bold",
        color=INK,
        ha="center",
    )
    ax.text(0.12, 0.405, "要完成什么", fontsize=12, color=MUTED, ha="center")

    rounded_box(ax, (0.815, 0.37), 0.13, 0.12, "#FDECEC", edge=RED)
    ax.text(
        0.88,
        0.445,
        "任务结果",
        fontsize=17,
        fontweight="bold",
        color=INK,
        ha="center",
    )
    ax.text(0.88, 0.405, "是否真的做完", fontsize=12, color=MUTED, ha="center")

    for start, end, color in [
        ((0.185, 0.43), (0.25, 0.43), GREEN),
        ((0.50, 0.70), (0.50, 0.62), ORANGE),
        ((0.75, 0.43), (0.815, 0.43), RED),
    ]:
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="-|>",
                mutation_scale=24,
                linewidth=3,
                color=color,
            )
        )

    ax.text(
        0.06,
        0.10,
        "图：编辑示意。不同 Harness 对上下文、工具、权限和验收的选择不同，同一模型的最终表现也可能不同。",
        fontsize=12.5,
        color=MUTED,
    )
    save(fig, "harness-system-stack.png")


if __name__ == "__main__":
    render_timeline()
    render_benchmark()
    render_system_stack()
