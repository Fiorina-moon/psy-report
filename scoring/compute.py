from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from scoring import likert

# 问卷星导出列顺序（0-based iloc），与当前测评表一致
I = {
    "neg_events": 16,
    "phq": (19, 27),
    "gad": (28, 34),
    "atype": (35, 58),
    "aias": (59, 72),
    "csws": (73, 82),
    "incom": (83, 88),
    "pfai": (89, 93),
    "ius": (94, 98),
    "cips": (99, 104),
    "bfi": (105, 114),
}

ANXIETY_KEYS = (
    "家庭焦虑",
    "未来就业焦虑",
    "社交焦虑",
    "经济焦虑",
    "外貌焦虑",
    "学业焦虑",
    "考试焦虑",
    "AI使用焦虑",
)

MECH_KEYS = (
    "自我价值学业绑定",
    "社会比较倾向",
    "失败恐惧",
    "不确定性不耐受",
    "冒充者综合征",
)

MECH_INTERNAL = (
    "self_worth_academic",
    "social_comparison",
    "failure_fear",
    "intolerance_uncertainty",
    "impostor",
)

BFI_TRAIT_CN = {
    "extraversion": "外向性",
    "agreeableness": "宜人性",
    "conscientiousness": "尽责性",
    "neuroticism": "神经质",
    "openness": "开放性",
}


def _iloc_range(row: pd.Series, a: int, b: int) -> list[Any]:
    return [row.iloc[i] for i in range(a, b + 1)]


def gad7_total(row: pd.Series) -> float | None:
    a, b = I["gad"]
    vals = [likert.map_gad_phq(v) for v in _iloc_range(row, a, b)]
    if any(v is None for v in vals):
        return None
    return float(sum(vals))


def ai_mean(row: pd.Series) -> float | None:
    a, b = I["aias"]
    vals = [likert.map_aias_7(v) for v in _iloc_range(row, a, b)]
    return likert.nanmean(vals)


def anxiety_type_means(row: pd.Series) -> dict[str, float | None]:
    a, b = I["atype"]
    raw = [likert.map_anxiety_type_5(v) for v in _iloc_range(row, a, b)]
    if len(raw) != 24:
        return {k: None for k in ANXIETY_KEYS}
    ai_m = ai_mean(row)
    groups = [
        raw[0:4],
        raw[4:8],
        raw[8:13],
        raw[13:16],
        raw[16:20],
        raw[20:23],
        [raw[23]],
    ]
    out: dict[str, float | None] = {}
    for label, vs in zip(ANXIETY_KEYS[:-1], groups, strict=True):
        out[label] = likert.nanmean(vs)
    out["AI使用焦虑"] = ai_m
    return out


def csws_academic_mean(row: pd.Series) -> float | None:
    a, b = I["csws"]
    vals = [likert.map_csws_7(v) for v in _iloc_range(row, a, b)]
    if len(vals) != 10 or vals[0] is None:
        return None
    academic = [
        likert.reverse_1_7(vals[0]),
        vals[1],
        vals[2],
        vals[3],
        vals[4],
    ]
    return likert.nanmean(academic)


def incom_mean(row: pd.Series) -> float | None:
    a, b = I["incom"]
    vals = [likert.map_incom_5(v) for v in _iloc_range(row, a, b)]
    if len(vals) != 6 or vals[2] is None:
        return None
    adjusted = vals[:2] + [likert.reverse_1_5(vals[2])] + vals[3:6]
    return likert.nanmean(adjusted)


def pfai_sum(row: pd.Series) -> float | None:
    a, b = I["pfai"]
    vals = [likert.map_pfai(v) for v in _iloc_range(row, a, b)]
    return likert.nan_sum(vals)


def ius_mean(row: pd.Series) -> float | None:
    a, b = I["ius"]
    vals = [likert.map_ius_5(v) for v in _iloc_range(row, a, b)]
    return likert.nanmean(vals)


def cips_sum(row: pd.Series) -> float | None:
    a, b = I["cips"]
    vals = [likert.map_cips_7(v) for v in _iloc_range(row, a, b)]
    return likert.nan_sum(vals)


def bfi_trait_means(row: pd.Series) -> dict[str, float | None]:
    a, b = I["bfi"]
    v = [likert.map_bfi_5(x) for x in _iloc_range(row, a, b)]
    if len(v) != 10 or any(x is None for x in v):
        return {k: None for k in BFI_TRAIT_CN}
    q1, q2, q3, q4, q5, q6, q7, q8, q9, q10 = v
    extra = likert.nanmean([likert.reverse_1_5(q1), q6])
    agree = likert.nanmean([q2, likert.reverse_1_5(q7)])
    consc = likert.nanmean([likert.reverse_1_5(q3), q8])
    neuro = likert.nanmean([likert.reverse_1_5(q4), q9])
    open_ = likert.nanmean([likert.reverse_1_5(q5), q10])
    return {
        "extraversion": extra,
        "agreeableness": agree,
        "conscientiousness": consc,
        "neuroticism": neuro,
        "openness": open_,
    }


def parse_negative_events(cell: Any) -> list[str]:
    if pd.isna(cell):
        return []
    s = str(cell).strip()
    if not s:
        return []
    parts = [p.strip() for p in s.replace("｜", "┋").split("┋")]
    return [p for p in parts if p and p != likert.SKIP]


def negative_events_string(cell: Any) -> str:
    ev = parse_negative_events(cell)
    return "、".join(ev) if ev else ""


def prominent_trait_phrase(bfi: dict[str, float | None]) -> str:
    pairs = [(BFI_TRAIT_CN[k], v) for k, v in bfi.items() if v is not None]
    if len(pairs) < 2:
        return "（人格维度数据不足）"
    pairs.sort(key=lambda x: -x[1])
    (a, _), (b, _) = pairs[0], pairs[1]
    return f"{a}、{b} 相对突出"


def rank_top_keys(scores: dict[str, float | None], labels: tuple[str, ...], k: int = 3) -> list[str]:
    items = [(lab, scores.get(lab)) for lab in labels]
    items = [(a, b) for a, b in items if b is not None]
    items.sort(key=lambda x: -x[1])
    return [a for a, _ in items[:k]]


def mechanism_vector(row: pd.Series) -> dict[str, float | None]:
    return {
        "self_worth_academic": csws_academic_mean(row),
        "social_comparison": incom_mean(row),
        "failure_fear": pfai_sum(row),
        "intolerance_uncertainty": ius_mean(row),
        "impostor": cips_sum(row),
    }


def rank_mechanisms_by_z(
    mech_row: dict[str, float | None], cohort_mechs: list[dict[str, float | None]]
) -> list[str]:
    label_by_key = dict(zip(MECH_INTERNAL, MECH_KEYS, strict=True))
    ranks: list[tuple[str, float]] = []
    for key in MECH_INTERNAL:
        v = mech_row.get(key)
        if v is None:
            continue
        arr = np.array(
            [float(m[key]) for m in cohort_mechs if m.get(key) is not None],
            dtype=float,
        )
        if arr.size < 2:
            z = 0.0
        else:
            mu, sig = float(arr.mean()), float(arr.std(ddof=0))
            z = 0.0 if sig == 0 else (float(v) - mu) / sig
        ranks.append((label_by_key[key], z))
    ranks.sort(key=lambda x: -x[1])
    return [a for a, _ in ranks[:3]]


def _col_index(df: pd.DataFrame, needle: str, default: int) -> int:
    for i, c in enumerate(df.columns):
        if needle in str(c):
            return i
    return default


def compute_student_block(
    row: pd.Series,
    df: pd.DataFrame,
    cohort_gad: list[float],
    cohort_mechs: list[dict[str, float | None]],
    top_events: list[tuple[str, int]],
) -> dict[str, Any]:
    gad = gad7_total(row)
    atype = anxiety_type_means(row)
    mech = mechanism_vector(row)
    bfi = bfi_trait_means(row)
    neg_cell = row.iloc[I["neg_events"]]
    neg_str = negative_events_string(neg_cell)

    n = len(cohort_gad)
    sample_mean = float(np.mean(cohort_gad)) if n else None
    if gad is None or sample_mean is None:
        rel = None
        pct = None
        band = None
    else:
        rel = "高于" if gad > sample_mean else "低于" if gad < sample_mean else "等于"
        below = sum(1 for x in cohort_gad if x < gad)
        pct = int(round(100 * below / n)) if n else None
        # 与报告文案一致：焦虑偏高用「前 X%」；偏低用「后 X%」（均相对样本内排序）
        if pct is not None:
            if pct > 50:
                band = f"前 {max(1, min(99, 100 - pct))}%"
            elif pct < 50:
                band = f"后 {max(1, min(99, 100 - pct))}%"
            else:
                band = "约中位附近"
        else:
            band = None

    top_m = rank_mechanisms_by_z(mech, cohort_mechs)
    while len(top_m) < 3:
        top_m.append(top_m[-1] if top_m else "（数据不足）")

    top_a = rank_top_keys(atype, ANXIETY_KEYS, 3)
    while len(top_a) < 3:
        top_a.append(top_a[-1] if top_a else "（数据不足）")

    ste1 = top_events[0][0] if len(top_events) > 0 else None
    ste2 = top_events[1][0] if len(top_events) > 1 else None

    prefill = {
        "total_score": gad,
        "sample_mean": round(sample_mean, 2) if sample_mean is not None else None,
        "relative_level": rel,
        "percentile": pct,
        "percentile_band": band,
        "negative_events_list": neg_str or "（本次未勾选具体事件）",
        "sample_top_event_1": ste1,
        "sample_top_event_2": ste2,
        "top_anxiety_type_1": top_a[0],
        "top_anxiety_type_2": top_a[1],
        "top_anxiety_type_3": top_a[2],
        "top_mechanism_1": top_m[0],
        "top_mechanism_2": top_m[1],
        "top_mechanism_3": top_m[2],
        "personality_analysis_text": None,
        "prominent_personality_trait": prominent_trait_phrase(bfi),
        "personalized_advice_list": None,
    }

    scales = {
        "gad7_total": gad,
        "anxiety_types": atype,
        "mechanisms": {MECH_KEYS[i]: mech[MECH_INTERNAL[i]] for i in range(5)},
        "bfi": {BFI_TRAIT_CN[k]: v for k, v in bfi.items()},
    }

    ix_学号 = _col_index(df, "学号", 10)
    ix_姓名 = _col_index(df, "姓名", 9)
    ix_序号 = _col_index(df, "序号", 0)

    meta = {
        "row_index": int(row.name) if isinstance(row.name, (int, np.integer)) else None,
        "序号": row.iloc[ix_序号],
        "学号": row.iloc[ix_学号],
        "姓名": row.iloc[ix_姓名],
    }

    return {
        "meta": meta,
        "scales": scales,
        "report_json_prefill": prefill,
    }


def run_scoring(xlsx: Path, out_json: Path) -> None:
    df = pd.read_excel(xlsx, sheet_name=0)
    df.columns = [str(c).strip() for c in df.columns]
    ncols = len(df.columns)
    need = I["bfi"][1] + 1
    if ncols < need:
        raise ValueError(f"Excel 列数不足：需要至少 {need} 列，当前 {ncols} 列。")

    event_counter: Counter[str] = Counter()
    for _, row in df.iterrows():
        for e in parse_negative_events(row.iloc[I["neg_events"]]):
            event_counter[e] += 1
    top_events = event_counter.most_common(20)

    cohort_gad: list[float] = []
    cohort_mechs: list[dict[str, float | None]] = []
    for _, row in df.iterrows():
        g = gad7_total(row)
        if g is not None:
            cohort_gad.append(g)
        cohort_mechs.append(mechanism_vector(row))

    students: list[dict[str, Any]] = []
    for idx, row in df.iterrows():
        block = compute_student_block(row, df, cohort_gad, cohort_mechs, top_events)
        block["meta"]["row_index"] = int(idx)
        students.append(block)

    cohort_summary = {
        "n_students": int(len(df)),
        "gad7": {
            "mean": round(float(np.mean(cohort_gad)), 3) if cohort_gad else None,
            "std": round(float(np.std(cohort_gad, ddof=0)), 3) if cohort_gad else None,
            "min": float(min(cohort_gad)) if cohort_gad else None,
            "max": float(max(cohort_gad)) if cohort_gad else None,
        },
        "negative_events_top": [
            {"label": lab, "count": c, "p": round(c / len(df), 4)} for lab, c in top_events[:10]
        ],
    }

    payload = {
        "schema_version": 1,
        "cohort": cohort_summary,
        "students": students,
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
