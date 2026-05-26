from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from agent.loaders import NARRATIVE_KEYS

PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")

# 与 template/report.typ 中 chart-box 占位一一对应（不转义，填入 image 代码）
CHART_SLOT_MARKERS: tuple[tuple[str, str], ...] = (
    ("chart_slot_1", "图表展示：群体分数分布直方图"),
    ("chart_slot_2", "图表展示：焦虑领域雷达图 & 排序条形图"),
    ("chart_slot_3", "图表展示：心理机制雷达图 & 排序条形图"),
)
CHART_SLOT_KEYS = frozenset(k for k, _ in CHART_SLOT_MARKERS)
RAW_TYPST_KEYS = CHART_SLOT_KEYS | frozenset({"cover_image"})
EXAMPLE_SPLIT_MARK = "**期望模型输出的 JSON 结构示例：**"

_TYPST_ESCAPES = (
    ("\\", "\\\\"),
    ("#", "\\#"),
    ("$", "\\$"),
    ("@", "\\@"),
    ("<", "\\<"),
    (">", "\\>"),
    ("*", "\\*"),
    ("_", "\\_"),
    ("`", "\\`"),
    ("[", "\\["),
    ("]", "\\]"),
)


def latest_report_json(output_dir: Path) -> Path:
    files = sorted(
        [p for p in output_dir.glob("*.json") if p.name != "scored_cohort.json"],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not files:
        raise FileNotFoundError(f"未找到报告 JSON：{output_dir / '*.json'}")
    return files[0]


def _escape_typst(text: str) -> str:
    out = text
    for old, new in _TYPST_ESCAPES:
        out = out.replace(old, new)
    return out


def _inline_markdown_to_typst(text: str) -> str:
    """将行内 **bold** 转为 Typst 的 *strong*。"""
    parts: list[str] = []
    pos = 0
    for m in re.finditer(r"\*\*(.+?)\*\*", text):
        if m.start() > pos:
            parts.append(_escape_typst(text[pos : m.start()]))
        parts.append("*" + _escape_typst(m.group(1)) + "*")
        pos = m.end()
    if pos < len(text):
        parts.append(_escape_typst(text[pos:]))
    return "".join(parts) if parts else _escape_typst(text)


def _markdown_to_typst(md: str) -> str:
    """将模型输出的简易 Markdown 转为 Typst 片段。"""
    lines = md.replace("\r\n", "\n").split("\n")
    blocks: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        hm = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if hm:
            level = len(hm.group(1))
            title = _inline_markdown_to_typst(hm.group(2).strip())
            # Markdown # 数量与 Typst 标题层级一致（=、==、=== …）
            prefix = "=" * level
            blocks.append(f"{prefix} {title}")
            i += 1
            continue

        if stripped.startswith(">"):
            quote_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                q = lines[i].strip()
                if q.startswith(">"):
                    q = q[1:].lstrip()
                quote_lines.append(_inline_markdown_to_typst(q))
                i += 1
            body = "\n\n".join(quote_lines)
            blocks.append(
                "#block(width: 100%, above: 0.35em, below: 0.35em)[\n"
                "  #set par(leading: 0.75em, spacing: 0.5em, first-line-indent: 2em)\n"
                + body
                + "\n]"
            )
            continue

        if re.match(r"^[-*]\s+", stripped):
            items: list[str] = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                item = re.sub(r"^[-*]\s+", "", lines[i].strip())
                items.append("- " + _inline_markdown_to_typst(item))
                i += 1
            blocks.append(
                "#block(width: 100%, above: 0.25em, below: 0.25em)[\n"
                + "\n".join(items)
                + "\n]"
            )
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                item = re.sub(r"^\d+\.\s+", "", lines[i].strip())
                items.append("+ " + _inline_markdown_to_typst(item))
                i += 1
            blocks.append(
                "#block(width: 100%, above: 0.25em, below: 0.25em)[\n"
                + "\n".join(items)
                + "\n]"
            )
            continue

        para: list[str] = []
        while i < len(lines):
            s = lines[i].strip()
            if not s:
                break
            if s.startswith("#") or s.startswith(">") or re.match(r"^[-*]\s+", s) or re.match(r"^\d+\.\s+", s):
                break
            para.append(_inline_markdown_to_typst(s))
            i += 1
        blocks.append("\n\n".join(para))
        continue

    return "\n\n".join(b for b in blocks if b.strip())


def _format_placeholder_value(key: str, val: object) -> str:
    if val is None:
        return "（暂无数据）"
    if key in RAW_TYPST_KEYS:
        return str(val)
    if isinstance(val, (int, float)) and not isinstance(val, bool):
        return str(val)
    text = str(val)
    if key in NARRATIVE_KEYS:
        return _markdown_to_typst(text)
    return _escape_typst(text)


def render_template(template_text: str, data: dict) -> tuple[str, list[str]]:
    missing: list[str] = []

    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in data:
            missing.append(key)
            return match.group(0)
        return _format_placeholder_value(key, data[key])

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
    """返回各图对应的相对路径（仅返回存在的文件）。"""
    chart_files = {
        "图表展示：群体分数分布直方图": root / "output" / "charts" / "1_cohort_distribution.png",
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


# 插入 chart-box 内，宽度与模板注释示例一致
_CHART_IMAGE_SPEC = "width: 92%, fit: \"contain\""


def _chart_slot_typst(rel: str) -> str:
    return f'#align(center)[#image("{rel}", {_CHART_IMAGE_SPEC})]'


def _chart_slot_missing() -> str:
    return '#align(center)[#text(size: 9pt, fill: rgb("#98A2B3"))[（请先运行 plot_report_charts.py 生成图表）]]'


def _resolve_cover_image(root: Path, output_parent: Path) -> str:
    """
    将封面复制到 output/cover.jpg，避免 Typst 以 output 为根目录时无法读取 ../template/...。
    """
    for candidate in (root / "cover.jpg", root / "template" / "cover.jpg"):
        if candidate.is_file():
            dest = output_parent / "cover.jpg"
            if not dest.exists() or candidate.stat().st_mtime > dest.stat().st_mtime:
                shutil.copy2(candidate, dest)
            return '#image("cover.jpg", width: 100%)'
    return '#text(size: 9pt, fill: rgb("#98A2B3"))[（未找到 cover.jpg，请放在项目根或 template/ 目录）]'


def _build_chart_slots(chart_rel: dict[str, str]) -> dict[str, str]:
    """为 template 中 {{ chart_slot_N }} 生成 Typst 插图片段。"""
    out: dict[str, str] = {}
    for slot_key, marker in CHART_SLOT_MARKERS:
        rel = chart_rel.get(marker)
        out[slot_key] = _chart_slot_typst(rel) if rel else _chart_slot_missing()
    return out


def compile_typst(typ_path: Path) -> Path:
    """调用 typst CLI 编译 PDF。"""
    pdf_path = typ_path.with_suffix(".pdf")
    try:
        subprocess.run(
            ["typst", "compile", str(typ_path), str(pdf_path)],
            check=True,
            cwd=typ_path.parent,
        )
    except FileNotFoundError as e:
        raise RuntimeError(
            "未找到 typst 命令。请安装 Typst：https://typst.app/open "
            "（Windows 可用 winget install --id Typst.Typst）"
        ) from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Typst 编译失败（退出码 {e.returncode}）") from e
    return pdf_path


def pdf_to_long_png(pdf_path: Path, dpi: int = 150) -> Path:
    """将 PDF 各页渲染后纵向拼接为一张 PNG 长图。"""
    try:
        import fitz  # PyMuPDF
    except ImportError as e:
        raise RuntimeError("导出长图需要 pymupdf，请运行: pip install pymupdf") from e
    try:
        from PIL import Image
    except ImportError as e:
        raise RuntimeError("导出长图需要 Pillow，请运行: pip install Pillow") from e

    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF 不存在: {pdf_path}")

    doc = fitz.open(pdf_path)
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    pages: list[Image.Image] = []
    for page in doc:
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        pages.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
    doc.close()

    if not pages:
        raise RuntimeError("PDF 无页面，无法导出长图")

    width = max(p.width for p in pages)
    total_height = sum(p.height for p in pages)
    long_img = Image.new("RGB", (width, total_height), "white")
    y = 0
    for page_img in pages:
        long_img.paste(page_img, ((width - page_img.width) // 2, y))
        y += page_img.height

    out_path = pdf_path.with_name(f"{pdf_path.stem}_long.png")
    long_img.save(out_path, format="PNG", optimize=True)
    return out_path


def main() -> None:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="将 output 下学生 JSON 填充到 template/report.typ")
    parser.add_argument("--json", type=Path, default=None, help="输入 JSON 文件路径；默认取 output 下最新 *.json")
    parser.add_argument("--template", type=Path, default=root / "template" / "report.typ", help="报告模板路径")
    parser.add_argument("--output", type=Path, default=None, help="输出 Typst 路径；默认写入 output/姓名_学号.typ")
    parser.add_argument("--compile", action="store_true", help="渲染后立即 typst compile 生成 PDF")
    parser.add_argument(
        "--long-image",
        action="store_true",
        help="编译 PDF 并导出纵向拼接长图（output/姓名_学号_long.png）",
    )
    parser.add_argument("--dpi", type=int, default=150, help="长图导出 DPI（默认 150，可设 200 更清晰）")
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

    if args.output:
        output_path = args.output.resolve()
    else:
        stem = json_path.stem
        if "_" in stem:
            output_path = root / "output" / f"{stem}.typ"
        else:
            name = _safe_part(data.get("姓名"))
            sid = _safe_part(data.get("学号"))
            output_path = root / "output" / f"{name}_{sid}.typ"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tag = json_path.stem if "_" in json_path.stem else f"{_safe_part(data.get('姓名'))}_{_safe_part(data.get('学号'))}"
    chart_rel = _chart_map(root, tag, output_path.parent)
    data.update(_build_chart_slots(chart_rel))
    data["cover_image"] = _resolve_cover_image(root, output_path.parent)

    rendered, missing = render_template(template_text, data)
    output_path.write_text(rendered, encoding="utf-8")

    print(f"模板: {template_path}")
    print(f"JSON: {json_path}")
    print(f"输出: {output_path}")
    if chart_rel:
        print("已插入图表:")
        for slot_key, marker in CHART_SLOT_MARKERS:
            if marker in chart_rel:
                print(f"- {slot_key} -> {chart_rel[marker]}")
    else:
        print("提示: 未找到可拼接图表（请先运行 plot_report_charts.py 生成图片）")

    need_pdf = args.compile or args.long_image
    if need_pdf:
        try:
            pdf_path = compile_typst(output_path)
            print(f"PDF: {pdf_path}")
            if args.long_image:
                png_path = pdf_to_long_png(pdf_path, dpi=args.dpi)
                print(f"长图: {png_path}")
        except RuntimeError as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)
    else:
        print(f"编译 PDF: typst compile {output_path}")
        print(f"导出长图: python render_report.py --json {json_path} --long-image")

    if missing:
        print("警告: 以下占位符在 JSON 中缺失，已原样保留:")
        print(", ".join(missing))


if __name__ == "__main__":
    main()
