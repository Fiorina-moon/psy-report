from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import os

PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")
EXAMPLE_SPLIT_MARK = "**期望模型输出的 JSON 结构示例：**"


def latest_report_json(output_dir: Path) -> Path:
    files = sorted(
        [p for p in output_dir.glob("*.json") if p.name != "scored_cohort.json"],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not files:
        raise FileNotFoundError(f"未找到报告 JSON：{output_dir / '*.json'}")
    return files[0]


def render_template(template_text: str, data: dict) -> tuple[str, list[str]]:
    missing: list[str] = []

    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in data:
            missing.append(key)
            return match.group(0)
        val = data[key]
        return "（暂无数据）" if val is None else str(val)

    return PLACEHOLDER_RE.sub(repl, template_text), sorted(set(missing))


def _parse_loose_flat_json(text: str) -> dict:
    """
    宽松解析器：用于 main 写出的“近似 JSON”文本（常见问题是字符串中未转义双引号）。
    仅支持当前报告结构这种扁平对象（key -> number/null/string）。
    """
    out: dict = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line in {"{", "}"}:
            continue
        m = re.match(r'^"([^"]+)"\s*:\s*(.+?)(,)?$', line)
        if not m:
            continue
        key, val_raw = m.group(1), m.group(2).strip()
        if val_raw == "null":
            out[key] = None
            continue
        if re.fullmatch(r"-?\d+(?:\.\d+)?", val_raw):
            out[key] = float(val_raw) if "." in val_raw else int(val_raw)
            continue
        if val_raw.startswith('"') and val_raw.endswith('"'):
            inner = val_raw[1:-1]
            # 将未转义的双引号统一转义，再按 JSON 字符串还原
            inner_fixed = re.sub(r'(?<!\\)"', r'\\"', inner)
            out[key] = json.loads(f'"{inner_fixed}"')
            continue
        out[key] = val_raw
    if not out:
        raise ValueError("宽松解析失败：未提取到任何键值")
    return out


def _safe_part(v: object) -> str:
    s = str(v or "").strip()
    if not s:
        return "未知"
    for ch in '<>:"/\\|?*':
        s = s.replace(ch, "_")
    return s


def _chart_map(root: Path, tag: str, output_parent: Path) -> dict[str, str]:
    """
    返回各图对应的 Markdown 相对路径（仅返回存在的文件）。
    """
    chart_files = {
        "图表展示：群体分数分布直方图": root / "output" / "charts" / f"1_cohort_distribution.png",
        "图表展示：焦虑程度参考对照表": root / "output" / "charts" / tag / f"{tag}_2_gad_reference.png",
        "图表展示：焦虑领域雷达图 & 排序条形图": root / "output" / "charts" / tag / f"{tag}_3_anxiety_types_overlay.png",
        "图表展示：心理机制雷达图 & 排序条形图": root / "output" / "charts" / tag / f"{tag}_4_mechanisms_overlay.png",
    }
    out: dict[str, str] = {}
    for k, p in chart_files.items():
        if p.is_file():
            rel = os.path.relpath(p, start=output_parent)
            out[k] = rel.replace("\\", "/")
    return out


def _inject_chart_images(rendered: str, chart_rel: dict[str, str]) -> str:
    lines = rendered.splitlines()
    new_lines: list[str] = []
    for line in lines:
        new_lines.append(line)
        for marker, rel in chart_rel.items():
            if marker in line:
                # 图片紧跟在图表占位提示后
                new_lines.append(f"![{marker}]({rel})")
                break
    return "\n".join(new_lines) + "\n"


def main() -> None:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="将 output 下学生 JSON 填充到 template/report.md")
    parser.add_argument("--json", type=Path, default=None, help="输入 JSON 文件路径；默认取 output 下最新 *.json")
    parser.add_argument("--template", type=Path, default=root / "template" / "report.md", help="报告模板路径")
    parser.add_argument("--output", type=Path, default=None, help="输出 Markdown 路径；默认写入 output/姓名_学号.md")
    parser.add_argument("--keep-example", action="store_true", help="保留模板中的 JSON 示例段")
    args = parser.parse_args()

    json_path = args.json.resolve() if args.json else latest_report_json(root / "output")
    template_path = args.template.resolve()

    if not template_path.is_file():
        raise FileNotFoundError(f"模板不存在: {template_path}")
    if not json_path.is_file():
        raise FileNotFoundError(f"JSON 不存在: {json_path}")

    raw_json_text = json_path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw_json_text)
    except json.JSONDecodeError:
        data = _parse_loose_flat_json(raw_json_text)
    template_text = template_path.read_text(encoding="utf-8")
    if not args.keep_example and EXAMPLE_SPLIT_MARK in template_text:
        template_text = template_text.split(EXAMPLE_SPLIT_MARK, 1)[0].rstrip() + "\n"

    rendered, missing = render_template(template_text, data)

    if args.output:
        output_path = args.output.resolve()
    else:
        stem = json_path.stem
        if "_" in stem:
            output_path = root / "output" / f"{stem}.md"
        else:
            # 回退：若输入 json 文件不是“姓名_学号”命名，尽量从内容中找
            name = _safe_part(data.get("姓名"))
            sid = _safe_part(data.get("学号"))
            output_path = root / "output" / f"{name}_{sid}.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tag = json_path.stem if "_" in json_path.stem else f"{_safe_part(data.get('姓名'))}_{_safe_part(data.get('学号'))}"
    chart_rel = _chart_map(root, tag, output_path.parent)
    rendered = _inject_chart_images(rendered, chart_rel)
    output_path.write_text(rendered, encoding="utf-8")

    print(f"模板: {template_path}")
    print(f"JSON: {json_path}")
    print(f"输出: {output_path}")
    if chart_rel:
        print("已拼接图表:")
        for k, rel in chart_rel.items():
            print(f"- {k} -> {rel}")
    else:
        print("提示: 未找到可拼接图表（请先运行 plot_report_charts.py 生成图片）")
    if missing:
        print("警告: 以下占位符在 JSON 中缺失，已原样保留:")
        print(", ".join(missing))


if __name__ == "__main__":
    main()
