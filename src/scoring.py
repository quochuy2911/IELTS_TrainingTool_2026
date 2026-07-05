from __future__ import annotations

import math
from typing import Iterable


def round_ielts_overall(scores: Iterable[float]) -> float:
    """IELTS overall band is the average of four skills rounded to the nearest 0.5."""
    valid_scores = [float(s) for s in scores if s is not None]
    if not valid_scores:
        return 0.0
    avg = sum(valid_scores) / len(valid_scores)
    return round(avg * 2) / 2


def safe_float(value, default=None):
    try:
        if value is None or value == "":
            return default
        if isinstance(value, float) and math.isnan(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def readiness_label(listening, reading, writing, speaking, target_overall=7.5, min_skill=6.5) -> str:
    scores = [safe_float(x, 0.0) for x in [listening, reading, writing, speaking]]
    overall = round_ielts_overall(scores)
    if all(s >= min_skill for s in scores) and overall >= target_overall:
        return "Ready"
    if all(s >= min_skill for s in scores) and overall >= target_overall - 0.5:
        return "Near Target"
    if min(scores) < min_skill:
        return "Skill Below Minimum"
    return "Building"
