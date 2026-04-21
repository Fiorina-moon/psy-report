from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

SKIP = "(跳过)"


def _is_skip(v: Any) -> bool:
    if pd.isna(v):
        return True
    s = str(v).strip()
    return s == SKIP or s == ""


def map_gad_phq(v: Any) -> float | None:
    if _is_skip(v):
        return None
    s = str(v).strip()
    m = {
        "完全不会": 0.0,
        "几天": 1.0,
        "一半以上的日子": 2.0,
        "几乎每天": 3.0,
    }
    return m.get(s)


def map_anxiety_type_5(v: Any) -> float | None:
    if _is_skip(v):
        return None
    s = str(v).strip()
    m = {"从不": 1.0, "偶尔": 2.0, "有时": 3.0, "经常": 4.0, "总是": 5.0}
    return m.get(s)


def map_aias_7(v: Any) -> float | None:
    if _is_skip(v):
        return None
    s = str(v).strip()
    m = {
        "非常不同意": 1.0,
        "不同意": 2.0,
        "比较不同意": 3.0,
        "一般": 4.0,
        "比较同意": 5.0,
        "同意": 6.0,
        "非常同意": 7.0,
    }
    return m.get(s)


def map_csws_7(v: Any) -> float | None:
    if _is_skip(v):
        return None
    s = str(v).strip()
    m = {
        "非常不同意": 1.0,
        "不同意": 2.0,
        "有点不同意": 3.0,
        "中立": 4.0,
        "有点同意": 5.0,
        "同意": 6.0,
        "非常同意": 7.0,
    }
    return m.get(s)


def map_incom_5(v: Any) -> float | None:
    if _is_skip(v):
        return None
    s = str(v).strip()
    m = {
        "完全不同意": 1.0,
        "不太同意": 2.0,
        "不确定": 3.0,
        "比较同意": 4.0,
        "完全同意": 5.0,
    }
    return m.get(s)


def map_pfai(v: Any) -> float | None:
    if _is_skip(v):
        return None
    s = str(v).strip()
    m = {
        "从不这样认为": -2.0,
        "很少这样认为": -1.0,
        "半数时间这样认为": 0.0,
        "经常这样认为": 1.0,
        "完全这样认为": 2.0,
    }
    return m.get(s)


def map_ius_5(v: Any) -> float | None:
    if _is_skip(v):
        return None
    s = str(v).strip()
    m = {
        "很不符合": 1.0,
        "不符合": 2.0,
        "一般": 3.0,
        "符合": 4.0,
        "很符合": 5.0,
    }
    return m.get(s)


def map_cips_7(v: Any) -> float | None:
    if _is_skip(v):
        return None
    s = str(v).strip()
    m = {
        "从不": 1.0,
        "很少": 2.0,
        "偶尔": 3.0,
        "有时": 4.0,
        "经常": 5.0,
        "通常": 6.0,
        "总是": 7.0,
    }
    return m.get(s)


def map_bfi_5(v: Any) -> float | None:
    if _is_skip(v):
        return None
    s = str(v).strip()
    m = {
        "很不同意": 1.0,
        "不同意": 2.0,
        "一般": 3.0,
        "同意": 4.0,
        "很同意": 5.0,
    }
    return m.get(s)


def reverse_1_5(x: float) -> float:
    return 6.0 - x


def reverse_1_7(x: float) -> float:
    return 8.0 - x


def nanmean(vals: list[float | None]) -> float | None:
    arr = np.array([v for v in vals if v is not None], dtype=float)
    if arr.size == 0:
        return None
    return float(np.nanmean(arr))


def nan_sum(vals: list[float | None]) -> float | None:
    if any(v is None for v in vals):
        return None
    return float(sum(v for v in vals if v is not None))
