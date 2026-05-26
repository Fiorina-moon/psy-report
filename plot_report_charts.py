from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


ANXIETY_KEYS = [
    "家庭焦虑",
    "未来就业焦虑",
    "社交焦虑",
    "经济焦虑",
    "外貌焦虑",
    "学业焦虑",
    "AI学习焦虑",
    "AI替代焦虑",
]
MECH_KEYS = [
    "自我价值学业绑定",
    "他人评价条件化",
    "失败恐惧",
    "不确定性不耐受",
    "冒充者综合征",
]

GAD_LEVELS = [
    {"min": 0, "max": 4, "level": "轻微或无明显焦虑", "advice": "保持规律作息与运动，持续自我观察"},
    {"min": 5, "max": 9, "level": "轻度焦虑", "advice": "优先压力管理，尝试呼吸放松与任务拆解"},
    {"min": 10, "max": 14, "level": "中度焦虑", "advice": "建议主动寻求心理支持并稳定日常节律"},
    {"min": 15, "max": 21, "level": "中重度焦虑", "advice": "尽快联系专业心理服务，获得系统支持"},
]


def _setup_style() -> None:
    plt.rcParams.update(
        {
            "font.sans-serif": ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"],
            "axes.unicode_minus": False,
            "figure.facecolor": "#FAFBFD",
            "axes.facecolor": "#F7F9FC",
            "axes.edgecolor": "#C9D4E5",
            "axes.labelcolor": "#2F3A4A",
            "xtick.color": "#425066",
            "ytick.color": "#425066",
            "grid.color": "#DCE4F2",
            "grid.linestyle": "--",
            "grid.alpha": 0.55,
            "axes.titleweight": "bold",
        }
    )


def _load_scored(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"找不到计分结果：{path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _pick_student(data: dict[str, Any], row: int | None) -> dict[str, Any]:
    students: list[dict[str, Any]] = data["students"]
    if row is None:
        return sorted(students, key=lambda s: int(s["meta"]["row_index"]))[0]
    for s in students:
        if int(s["meta"]["row_index"]) == row:
            return s
    raise IndexError(f"未找到 row_index={row} 的学生")


def _safe_part(v: object) -> str:
    s = str(v or "").strip()
    if not s:
        return "未知"
    for ch in '<>:"/\\|?*':
        s = s.replace(ch, "_")
    return s


def _student_tag(student: dict[str, Any]) -> str:
    meta = student.get("meta", {})
    return f"{_safe_part(meta.get('姓名'))}_{_safe_part(meta.get('学号'))}"


def _cohort_means(data: dict[str, Any], key: str, labels: list[str]) -> list[float]:
    out: list[float] = []
    for lab in labels:
        vals = []
        for s in data["students"]:
            v = s["scales"][key].get(lab)
            if v is not None:
                vals.append(float(v))
        out.append(float(np.mean(vals)) if vals else np.nan)
    return out


def _radar(ax: plt.Axes, labels: list[str], cohort: list[float], student: list[float], title: str) -> None:
    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]
    c = cohort + cohort[:1]
    s = student + student[:1]

    ax.plot(angles, c, color="#7AA6D6", linewidth=2, label="全体均值")
    ax.fill(angles, c, color="#AFC8E8", alpha=0.25)
    ax.plot(angles, s, color="#D97B85", linewidth=2.2, label="我")
    ax.fill(angles, s, color="#EDB8BE", alpha=0.22)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_title(title, pad=18, fontsize=12, color="#2F3A4A")
    ax.grid(True)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.15), frameon=False, fontsize=9)


def _sort_by_student(
    labels: list[str], student: list[float], cohort: list[float] | None = None
) -> tuple[list[str], list[float], list[float] | None]:
    cohort_vals = cohort if cohort is not None else [np.nan] * len(labels)
    ranked = sorted(
        zip(labels, student, cohort_vals, strict=True),
        key=lambda t: float(t[1]) if not np.isnan(t[1]) else float("-inf"),
        reverse=True,
    )
    out_labels = [t[0] for t in ranked]
    out_student = [t[1] for t in ranked]
    out_cohort = [t[2] for t in ranked] if cohort is not None else None
    return out_labels, out_student, out_cohort


def _sorted_bar_chart(
    ax: plt.Axes,
    labels: list[str],
    student: list[float],
    cohort: list[float] | None,
    *,
    title: str,
    show_cohort_mean_line: bool,
    label_rotation: int,
) -> None:
    sort_labels, sort_student, sort_cohort = _sort_by_student(labels, student, cohort)
    x = np.arange(len(sort_labels))
    bar_w = 0.55
    ax.bar(x, sort_student, width=bar_w, color="#E7A9B1", edgecolor="white", linewidth=0.8)

    if show_cohort_mean_line and sort_cohort is not None:
        for i, mean in enumerate(sort_cohort):
            if np.isnan(mean):
                continue
            ax.plot(
                [i - bar_w / 2, i + bar_w / 2],
                [mean, mean],
                color="#7AA6D6",
                linewidth=2.2,
                linestyle="--",
                zorder=3,
            )
        legend_handles = [
            Patch(facecolor="#E7A9B1", edgecolor="white", label="我"),
            Line2D([0], [0], color="#7AA6D6", linewidth=2.2, linestyle="--", label="样本均值"),
        ]
    else:
        legend_handles = [Patch(facecolor="#E7A9B1", edgecolor="white", label="我")]

    ax.set_xticks(x)
    ax.set_xticklabels(sort_labels, rotation=label_rotation, ha="right")
    ax.set_title(title)
    ax.set_ylabel("得分")
    ax.grid(True, axis="y")
    ax.legend(handles=legend_handles, frameon=False)


def plot_1_cohort_distribution(data: dict[str, Any], out: Path) -> None:
    gad_vals = [s["scales"]["gad7_total"] for s in data["students"] if s["scales"]["gad7_total"] is not None]
    gad_vals = [float(v) for v in gad_vals]
    mean = data["cohort"]["gad7"]["mean"]
    fig = plt.figure(figsize=(11.5, 6.5), dpi=180)
    ax1 = fig.add_subplot(1, 1, 1)

    bins = np.arange(-0.5, 22.5, 1)
    ax1.hist(gad_vals, bins=bins, color="#8BB8E8", alpha=0.85, edgecolor="white")
    ax1.axvline(mean, color="#D06B76", linewidth=2.2, linestyle="--", label=f"均值 {mean:.2f}")
    ax1.set_title("图1｜全体学生焦虑总分分布（GAD-7）", fontsize=13)
    ax1.set_xlabel("总分")
    ax1.set_ylabel("人数")
    ax1.set_xlim(-0.5, 21.5)
    ax1.grid(True, axis="y")
    ax1.legend(frameon=False)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def _gad_level_row(score: float | None) -> int | None:
    if score is None:
        return None
    for i, r in enumerate(GAD_LEVELS):
        if r["min"] <= score <= r["max"]:
            return i
    return None


def plot_2_gad_reference_table(student: dict[str, Any], out: Path) -> None:
    score = student["report_json_prefill"].get("total_score")
    row_idx = _gad_level_row(score)
    fig, ax = plt.subplots(figsize=(11.5, 4.8), dpi=180)
    ax.axis("off")

    col_labels = ["分数区间", "程度描述", "行动建议"]
    rows = [[f"{x['min']}–{x['max']}", x["level"], x["advice"]] for x in GAD_LEVELS]
    table = ax.table(
        cellText=rows,
        colLabels=col_labels,
        loc="center",
        cellLoc="left",
        colLoc="center",
        colWidths=[0.12, 0.28, 0.56],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.0)

    # header style
    for c in range(len(col_labels)):
        cell = table[(0, c)]
        cell.set_facecolor("#DCE8F7")
        cell.set_text_props(weight="bold", color="#2E3A4C")

    # highlight student's level row
    if row_idx is not None:
        tr = row_idx + 1
        for c in range(len(col_labels)):
            cell = table[(tr, c)]
            cell.set_facecolor("#F7DDE1")
            cell.set_edgecolor("#D06B76")
            cell.set_linewidth(1.5)

    txt = f"我的总分：{score}" if score is not None else "我的总分：暂无"
    ax.set_title(f"图2｜焦虑程度参考对照表\n{txt}", fontsize=13, color="#2F3A4A", pad=12)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def plot_3_anxiety_overlay(data: dict[str, Any], student: dict[str, Any], out: Path) -> None:
    cohort_anx = _cohort_means(data, "anxiety_types", ANXIETY_KEYS)
    stu_anx = [float(student["scales"]["anxiety_types"].get(k) or np.nan) for k in ANXIETY_KEYS]

    fig = plt.figure(figsize=(13.5, 6.5), dpi=180)
    ax1 = fig.add_subplot(1, 2, 1, projection="polar")
    ax2 = fig.add_subplot(1, 2, 2)
    _radar(ax1, ANXIETY_KEYS, cohort_anx, stu_anx, "焦虑领域雷达图")
    _sorted_bar_chart(
        ax2,
        ANXIETY_KEYS,
        stu_anx,
        cohort_anx,
        title="焦虑领域排序条形图",
        show_cohort_mean_line=True,
        label_rotation=30,
    )
    fig.suptitle("图3｜焦虑领域雷达图 & 排序条形图", fontsize=14, color="#2D3748", y=1.02)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def plot_4_mechanism_overlay(data: dict[str, Any], student: dict[str, Any], out: Path) -> None:
    cohort_mech = _cohort_means(data, "mechanisms", MECH_KEYS)
    mech = student["scales"]["mechanisms"]
    stu_mech = [float(mech.get(k) or np.nan) for k in MECH_KEYS]

    fig = plt.figure(figsize=(13.5, 6.5), dpi=180)
    ax1 = fig.add_subplot(1, 2, 1, projection="polar")
    ax2 = fig.add_subplot(1, 2, 2)
    _radar(ax1, MECH_KEYS, cohort_mech, stu_mech, "心理机制雷达图")
    _sorted_bar_chart(
        ax2,
        MECH_KEYS,
        stu_mech,
        cohort_mech,
        title="心理机制排序条形图",
        show_cohort_mean_line=True,
        label_rotation=20,
    )

    fig.suptitle("图4｜心理机制雷达图 & 排序条形图", fontsize=14, color="#2D3748", y=1.02)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 report.typ 对应的 4 张图")
    parser.add_argument("--scored", type=Path, default=Path("output/scored/scored_cohort.json"))
    parser.add_argument("--row", type=int, default=None, help="学生 row_index，默认最小 row_index")
    parser.add_argument("--outdir", type=Path, default=Path("output/charts"))
    args = parser.parse_args()

    _setup_style()
    data = _load_scored(args.scored)
    student = _pick_student(data, args.row)
    tag = _student_tag(student)
    subdir = args.outdir / tag

    # 图1：全体分布图（一次生成即可；不需要叠加个体）
    p1 = args.outdir / f"1_cohort_distribution.png"
    # 图2-4：叠加个人数据
    p2 = subdir / f"{tag}_2_gad_reference.png"
    p3 = subdir / f"{tag}_3_anxiety_types_overlay.png"
    p4 = subdir / f"{tag}_4_mechanisms_overlay.png"
    plot_1_cohort_distribution(data, p1)
    plot_2_gad_reference_table(student, p2)
    plot_3_anxiety_overlay(data, student, p3)
    plot_4_mechanism_overlay(data, student, p4)

    print(f"已生成图表目录: {args.outdir.resolve()}")
    print(f"- {p1.name}")
    print(f"- {p2.name}")
    print(f"- {p3.name}")
    print(f"- {p4.name}")


if __name__ == "__main__":
    main()

