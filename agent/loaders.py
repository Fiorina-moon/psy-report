from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class PathsConfig:
    results_xlsx: Path
    report_template: Path
    questionnaire_doc: Path | None
    output_dir: Path
    scored_cohort_json: Path


@dataclass
class DataConfig:
    sheet_name: str | int | None
    respondent_id_column: str | None
    respondent_id: str | None


@dataclass
class LLMConfig:
    api_key: str
    base_url: str
    model: str
    temperature: float
    max_tokens: int
    response_format_json: bool


@dataclass
class AppConfig:
    paths: PathsConfig
    data: DataConfig
    llm: LLMConfig


def _resolve(base: Path, p: str | Path) -> Path:
    path = Path(p)
    if not path.is_absolute():
        path = (base / path).resolve()
    return path


def _parse_model_list(raw: str) -> list[str]:
    return [m.strip() for m in raw.split(",") if m.strip()]


def _load_paratera_llm(llm_raw: dict[str, Any]) -> LLMConfig:
    api_key = os.environ.get("PARATERA_API_KEY", "").strip()
    base_url = (
        os.environ.get("PARATERA_BASE_URL", "https://llmapi.paratera.com/v1")
        .strip()
        .strip('"')
        .rstrip("/")
    )
    model = os.environ.get("PARATERA_MODEL", "").strip().strip('"')
    model_list_raw = os.environ.get("PARATERA_MODEL_LIST", "").strip().strip('"')

    if model_list_raw:
        allowed = _parse_model_list(model_list_raw)
        if model and allowed and model not in allowed:
            raise ValueError(
                f"PARATERA_MODEL={model!r} 不在 PARATERA_MODEL_LIST 允许列表中: {allowed}"
            )

    return LLMConfig(
        api_key=api_key,
        base_url=base_url or "https://llmapi.paratera.com/v1",
        model=model,
        temperature=float(llm_raw.get("temperature", 0.5)),
        max_tokens=int(llm_raw.get("max_tokens", 8192)),
        response_format_json=bool(llm_raw.get("response_format_json", True)),
    )


def load_config(config_path: Path) -> AppConfig:
    base = config_path.parent.resolve()
    raw: dict[str, Any] = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    paths_raw = raw.get("paths", {})
    data_raw = raw.get("data", {})
    llm_raw = raw.get("llm", {})

    q_doc = paths_raw.get("questionnaire_doc")
    paths = PathsConfig(
        results_xlsx=_resolve(base, paths_raw["results_xlsx"]),
        report_template=_resolve(base, paths_raw["report_template"]),
        questionnaire_doc=_resolve(base, q_doc) if q_doc else None,
        output_dir=_resolve(base, paths_raw.get("output_dir", "output")),
        scored_cohort_json=_resolve(
            base, paths_raw.get("scored_cohort_json", "output/scored/scored_cohort.json")
        ),
    )

    data = DataConfig(
        sheet_name=data_raw.get("sheet_name"),
        respondent_id_column=data_raw.get("respondent_id_column"),
        respondent_id=data_raw.get("respondent_id"),
    )

    llm = _load_paratera_llm(llm_raw)

    return AppConfig(paths=paths, data=data, llm=llm)


def load_scored_cohort(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(
            f"找不到计分结果文件: {path}\n请先运行: python -m scoring --config config.yaml"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def get_student_by_row_index(data: dict[str, Any], row_index: int) -> dict[str, Any]:
    students: list[dict[str, Any]] = data["students"]
    for s in students:
        if int(s["meta"]["row_index"]) == row_index:
            return s
    raise IndexError(f"scored_cohort 中无 row_index={row_index} 的记录（共 {len(students)} 人）")


def get_student_default(data: dict[str, Any]) -> dict[str, Any]:
    students = sorted(data["students"], key=lambda s: int(s["meta"]["row_index"]))
    if not students:
        raise ValueError("students 为空")
    return students[0]


def build_model_score_payload(data: dict[str, Any], student: dict[str, Any]) -> dict[str, Any]:
    return {
        "cohort": data["cohort"],
        "student": {
            "meta": student["meta"],
            "scales": student["scales"],
            "report_json_prefill": student["report_json_prefill"],
        },
    }


def strip_json_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t, count=1, flags=re.IGNORECASE)
        t = re.sub(r"\s*```\s*$", "", t, count=1)
    return t.strip()


def parse_and_pretty(text: str) -> tuple[str, bool]:
    raw = strip_json_fences(text)
    try:
        obj = json.loads(raw)
        return json.dumps(obj, ensure_ascii=False, indent=2), True
    except json.JSONDecodeError:
        return raw, False


REPORT_JSON_KEYS: tuple[str, ...] = (
    "total_score",
    "sample_mean",
    "relative_level",
    "percentile",
    "percentile_band",
    "negative_events_list",
    "sample_top_event_1",
    "sample_top_event_2",
    "top_anxiety_type_1",
    "top_anxiety_type_2",
    "top_anxiety_type_3",
    "top_mechanism_1",
    "top_mechanism_2",
    "top_mechanism_3",
    "personality_analysis_text",
    "prominent_personality_trait",
    "personalized_advice_list",
)

NARRATIVE_KEYS = frozenset({"personality_analysis_text", "personalized_advice_list"})


def merge_report_json(prefill: dict[str, Any], model_obj: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k in REPORT_JSON_KEYS:
        if k in NARRATIVE_KEYS:
            mv = model_obj.get(k)
            out[k] = mv if mv is not None else prefill.get(k)
        else:
            out[k] = prefill.get(k)
    return out
