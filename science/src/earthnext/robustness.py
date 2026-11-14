"""Robustness checks: start/end sensitivity, method agreement, leave-one-out.

All functions are pure (no I/O). Tests cover known series.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats

from earthnext.trends import theil_sen_ci, mann_kendall


@dataclass(frozen=True)
class RobustnessResult:
    sign_stable_pct: float   # % of start/end windows where Theil-Sen sign == full-series sign
    ts_ols_agree: bool        # Theil-Sen slope sign == OLS slope sign
    loo_stable: bool          # Leave-one-year-out sign unchanged
    loo_min_slope: float
    loo_max_slope: float
    min_window_years: int
    windows_tested: int
    windows_same_sign: int
    full_slope_sign: int  # +1, -1, or 0


def _sign(v: float) -> int:
    return 1 if v > 0 else -1 if v < 0 else 0


def start_end_sensitivity(
    y: np.ndarray,
    x: np.ndarray | None = None,
    *,
    min_window_years: int = 15,
    confidence: float = 0.95,
) -> tuple[float, int, int]:
    """Slide start and end year windows and count % where Theil-Sen sign matches
    the full-series sign.

    Returns (sign_stable_pct, windows_tested, windows_same_sign).
    """
    y = np.asarray(y, dtype=float)
    x = np.arange(len(y), dtype=float) if x is None else np.asarray(x, dtype=float)
    mask = np.isfinite(y) & np.isfinite(x)
    yv, xv = y[mask], x[mask]

    if yv.size < min_window_years:
        return 0.0, 0, 0

    full = theil_sen_ci(yv, xv, confidence=confidence)
    full_sign = _sign(full.slope)

    n = len(yv)
    same = 0
    total = 0
    for start in range(0, n - min_window_years + 1):
        for end in range(start + min_window_years, n + 1):
            total += 1
            try:
                ts = theil_sen_ci(yv[start:end], xv[start:end], confidence=confidence)
                if _sign(ts.slope) == full_sign:
                    same += 1
            except ValueError:
                pass  # too few points after NaN filtering

    pct = 100.0 * same / max(total, 1)
    return pct, total, same


def method_agreement(y: np.ndarray, x: np.ndarray | None = None) -> bool:
    """Check whether Theil-Sen slope sign matches OLS slope sign."""
    y = np.asarray(y, dtype=float)
    x = np.arange(len(y), dtype=float) if x is None else np.asarray(x, dtype=float)
    mask = np.isfinite(y) & np.isfinite(x)
    yv, xv = y[mask], x[mask]
    if yv.size < 3:
        return False

    ts = theil_sen_ci(yv, xv)
    ols_result = stats.linregress(xv, yv)
    return _sign(ts.slope) == _sign(ols_result.slope)


def leave_one_out(y: np.ndarray, x: np.ndarray | None = None) -> tuple[bool, float, float]:
    """Leave one year out: recompute Theil-Sen slope N times, dropping one year
    each iteration.

    Returns (sign_stable, min_slope, max_slope).
    """
    y = np.asarray(y, dtype=float)
    x = np.arange(len(y), dtype=float) if x is None else np.asarray(x, dtype=float)
    mask = np.isfinite(y) & np.isfinite(x)
    yv, xv = y[mask], x[mask]
    if yv.size < 4:
        return False, 0.0, 0.0

    full_sign = _sign(theil_sen_ci(yv, xv).slope)
    slopes: list[float] = []
    for i in range(len(yv)):
        yi = np.delete(yv, i)
        xi = np.delete(xv, i)
        try:
            ts = theil_sen_ci(yi, xi)
            slopes.append(ts.slope)
        except ValueError:
            pass

    if not slopes:
        return True, 0.0, 0.0

    all_same = all(_sign(s) == full_sign for s in slopes)
    return all_same, float(min(slopes)), float(max(slopes))


def robustness_report(
    y: np.ndarray,
    x: np.ndarray | None = None,
    *,
    min_window_years: int = 15,
    confidence: float = 0.95,
) -> RobustnessResult:
    """Full robustness check for a single series."""
    y = np.asarray(y, dtype=float)
    x = np.arange(len(y), dtype=float) if x is None else np.asarray(x, dtype=float)
    mask = np.isfinite(y) & np.isfinite(x)
    yv, xv = y[mask], x[mask]

    if yv.size < 3:
        return RobustnessResult(
            sign_stable_pct=0.0, ts_ols_agree=False, loo_stable=False,
            loo_min_slope=0.0, loo_max_slope=0.0,
            min_window_years=min_window_years, windows_tested=0,
            windows_same_sign=0, full_slope_sign=0,
        )

    full_slope_sign = _sign(theil_sen_ci(yv, xv, confidence=confidence).slope)

    sign_stable_pct, windows_tested, windows_same_sign = start_end_sensitivity(
        yv, xv, min_window_years=min_window_years, confidence=confidence,
    )
    ts_ols = method_agreement(yv, xv)
    loo_stable, loo_min, loo_max = leave_one_out(yv, xv)

    return RobustnessResult(
        sign_stable_pct=sign_stable_pct,
        ts_ols_agree=ts_ols,
        loo_stable=loo_stable,
        loo_min_slope=loo_min,
        loo_max_slope=loo_max,
        min_window_years=min_window_years,
        windows_tested=windows_tested,
        windows_same_sign=windows_same_sign,
        full_slope_sign=full_slope_sign,
    )
