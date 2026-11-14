"""Evidence Strength Index (ESI) — project-defined heuristic per SPEC §3.

Score 0–10 from the rubric in science/config/analysis.yaml. Disclosed as a
heuristic; describes evidence quality for a monotonic trend, NOT importance,
cause, or risk.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np


@dataclass(frozen=True)
class ESIResult:
    score: float
    grade: Literal["A", "B", "C", "D"]
    breakdown: dict[str, float]  # category → points earned
    max_possible: int = 10

    def grade_label(self) -> str:
        labels = {
            "A": "Strong evidence — robust to method and time-window choices",
            "B": "Moderate evidence — trend is detectable but sensitive to some assumptions",
            "C": "Weak evidence — signal is fragile; interpret cautiously",
            "D": "Insufficient evidence — cannot distinguish signal from noise with this data",
        }
        return labels[self.grade]


def compute_esi(
    *,
    n_valid_years: int,
    missing_pct: float,
    p: float,
    q: float | None,
    slope_ci_excludes_zero: bool,
    sign_stable_pct: float,
    theil_sen_ols_agree: bool,
    leave_one_out_stable: bool,
    config: dict,
) -> ESIResult:
    """Score per the ESI rubric in analysis.yaml.  Thresholds come from config,
    not from code.
    """
    rubric = config["esi"]["points"]
    grade_cuts = config["esi"]["grades"]

    breakdown: dict[str, float] = {}

    # 1.  ≥ 15 years of valid annual data — 2 pts
    breakdown["years_ge_15"] = float(rubric["years_ge_15"] if n_valid_years >= 15 else 0)

    # 2.  Missing fraction ≤ 10% — 1 pt
    breakdown["missing_pct_le_10"] = float(rubric["missing_pct_le_10"] if missing_pct <= 10.0 else 0)

    # 3.  q (or p if single test) < 0.05 — 2 pts
    effective = q if q is not None else p
    breakdown["pq_lt_005"] = float(rubric["pq_lt_005"] if effective < 0.05 else 0)

    # 4.  95% slope CI excludes 0 — 1 pt
    breakdown["slope_ci_excludes_zero"] = float(rubric["slope_ci_excludes_zero"] if slope_ci_excludes_zero else 0)

    # 5.  Sign unchanged in ≥ 90% of start/end windows — 2 pts
    breakdown["sign_stable_90pct"] = float(rubric["sign_stable_90pct"] if sign_stable_pct >= 90.0 else 0)

    # 6.  Theil-Sen and OLS-HAC agree in sign — 1 pt
    breakdown["theil_sen_ols_agree"] = float(rubric["theil_sen_ols_agree"] if theil_sen_ols_agree else 0)

    # 7.  Leave-one-year-out sign unchanged — 1 pt
    breakdown["leave_one_out_stable"] = float(rubric["leave_one_out_stable"] if leave_one_out_stable else 0)

    score = sum(breakdown.values())
    score = float(np.clip(score, 0.0, 10.0))

    # Determine grade from inclusive-lower bounds
    grade: Literal["A", "B", "C", "D"] = "D"
    sorted_cuts = sorted(grade_cuts.items(), key=lambda x: x[1], reverse=True)
    for g, lower in sorted_cuts:
        if score >= lower:
            grade = g  # type: ignore[assignment]
            break

    return ESIResult(score=score, grade=grade, breakdown=breakdown)
