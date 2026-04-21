"""
心理测评：读取离线计分结果，调用模型仅补充叙事字段，合并为报告占位符 JSON。

  python -m scoring --config config.yaml
  python main.py [--dry-run] [--row N]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from agent.loaders import (
    build_model_score_payload,
    get_student_by_row_index,
    get_student_default,
    load_config,
    load_scored_cohort,
    merge_report_json,
    parse_and_pretty,
)
from agent.report import build_system_prompt, build_user_prompt, chat_completion


def _project_root() -> Path:
    return Path(__file__).resolve().parent


def _pick_student(cfg, data: dict, row: int | None) -> dict:
    if row is not None:
        return get_student_by_row_index(data, row)
    col = cfg.data.respondent_id_column
    rid = cfg.data.respondent_id
    if col and rid is not None:
        for s in data["students"]:
            meta = s["meta"]
            if str(meta.get(col) or "") == str(rid):
                return s
        raise KeyError(f"在 scored_cohort 中未找到 {col}={rid!r}")
    return get_student_default(data)


def _safe_part(v: object) -> str:
    s = str(v or "").strip()
    if not s:
        return "未知"
    for ch in '<>:"/\\|?*':
        s = s.replace(ch, "_")
    return s


def _student_tag(student: dict) -> str:
    meta = student.get("meta", {})
    name = _safe_part(meta.get("姓名"))
    sid = _safe_part(meta.get("学号"))
    return f"{name}_{sid}"


def main() -> None:
    parser = argparse.ArgumentParser(description="离线计分 JSON + LLM -> 报告占位符 JSON")
    parser.add_argument("--config", type=Path, default=_project_root() / "config.yaml")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--row", type=int, default=None, help="scored_cohort 的 row_index")
    args = parser.parse_args()

    root = _project_root()
    load_dotenv(root / ".env")
    cfg = load_config(args.config.resolve())

    data = load_scored_cohort(cfg.paths.scored_cohort_json)
    student = _pick_student(cfg, data, args.row)

    prompts_dir = root / "prompts"
    template_text = cfg.paths.report_template.read_text(encoding="utf-8")
    score_json = json.dumps(
        build_model_score_payload(data, student), ensure_ascii=False, indent=2
    )

    system_prompt = build_system_prompt(prompts_dir / "system.md")
    user_prompt = build_user_prompt(prompts_dir / "user_report.md", template_text, score_json)

    cfg.paths.output_dir.mkdir(parents=True, exist_ok=True)
    tag = _student_tag(student)

    if args.dry_run:
        od = cfg.paths.output_dir
        (od / f"{tag}_system.md").write_text(system_prompt, encoding="utf-8")
        (od / f"{tag}_user.md").write_text(user_prompt, encoding="utf-8")
        print(f"已写入: {od}")
        return

    result = chat_completion(cfg.llm, system_prompt, user_prompt)
    body, ok = parse_and_pretty(result.content)
    if ok:
        body = json.dumps(
            merge_report_json(student["report_json_prefill"], json.loads(body)),
            ensure_ascii=False,
            indent=2,
        )

    out_file = cfg.paths.output_dir / f"{tag}.json"
    out_file.write_text(body + ("\n" if not body.endswith("\n") else ""), encoding="utf-8")
    print(f"已生成: {out_file}  (model={result.model})")
    if not ok:
        print("警告: 模型输出未能解析为 JSON，无法进行字段合并，已按原文写入。")


if __name__ == "__main__":
    main()
