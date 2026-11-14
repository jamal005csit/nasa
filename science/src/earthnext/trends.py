"""Statistics engine. Pure numeric functions; no I/O.

Implements, per AGENTS.md "Science rules" and STAGE_PROMPTS Stage 3:
  - annual aggregation with coverage rule
  - Theil-Sen slope + 95 % CI (two-sided)
  - Mann-Kendall test (plain + Hamed-Rao modified + prewhitened variants)
  - lag-1 autocorrelation check → variant chosen per config
  - cos(latitude) area-weighted spatial mean
  - Benjamini-Hochberg FDR over a set of p-values
  - one-call `trend_report` that returns the full result dict

Backed by scipy.stats.theilslopes (CI from a rank-based formula) and
pymannkendall (MK variants). The independent cross-check lives in
tests/test_trends.py (test_theil_sen_cross_check_against_scipy).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
import pymannkendall as pmk
from scipy import stats
from statsmodels.stats.multitest import multipletests

# ---------- aggregation ----------

def aggregate_annual(
    times: np.ndarray,
    values: np.ndarray,
    *,
    min_valid_months: int = 9,
) -> tuple[np.ndarray, np.ndarray]:
    """Monthly series → annual means with a coverage rule.

    A year's annual value is the mean of its valid months, but only if at
    least ``min_valid_months`` of 12 months are non-NaN. Otherwise the
    year's value is NaN.

    Parameters
    ----------
    times : array-like of datetime64[ns] or pandas DatetimeIndex, length N
    values : 1-D float array, length N

    Returns
    -------
    (years, annual_values) : (int array, float array) — years ordered ascending.
    """
    s = pd.Series(np.asarray(values, dtype=float), index=pd.to_datetime(times))
    s = s.sort_index()
    years = s.index.year
    n_valid = s.groupby(years).apply(lambda g: int(np.sum(~np.isnan(g.values))))
    means = s.groupby(years).mean()
    means[n_valid < min_valid_months] = np.nan
    return means.index.to_numpy(dtype=int), means.to_numpy(dtype=float)


# ---------- lag-1 autocorrelation ----------

def lag1_autocorr(y: np.ndarray) -> float:
    """Sample lag-1 autocorrelation of a 1-D series, NaN-aware.

    Returns NaN if fewer than 3 finite consecutive-pair observations exist.
    """
    y = np.asarray(y, dtype=float)
    finite_pairs = ~(np.isnan(y[:-1]) | np.isnan(y[1:]))
    a = y[:-1][finite_pairs]
    b = y[1:][finite_pairs]
    if a.size < 3:
        return float("nan")
    a_c = a - a.mean()
    b_c = b - b.mean()
    denom = np.sqrt((a_c**2).sum() * (b_c**2).sum())
    if denom == 0:
        return float("nan")
    return float((a_c * b_c).sum() / denom)


# ---------- Theil–Sen ----------

@dataclass(frozen=True)
class TheilSen:
    slope: float
    intercept: float
    slope_lo: float  # lower bound of CI
    slope_hi: float  # upper bound of CI
    confidence: float
    n: int

    def ci_excludes_zero(self) -> bool:
        return (self.slope_lo > 0) or (self.slope_hi < 0)


def theil_sen_ci(
    y: np.ndarray,
    x: np.ndarray | None = None,
    *,
    confidence: float = 0.95,
) -> TheilSen:
    """Theil-Sen slope with a two-sided confidence interval.

    Drops NaNs pair-wise. Requires ≥ 3 finite points, else raises ValueError.
    """
    y = np.asarray(y, dtype=float)
    x = np.arange(len(y), dtype=float) if x is None else np.asarray(x, dtype=float)
    mask = np.isfinite(y) & np.isfinite(x)
    yv, xv = y[mask], x[mask]
    if yv.size < 3:
        raise ValueError(f"theil_sen_ci: need ≥3 finite points, got {yv.size}")
    alpha = 1.0 - confidence
    slope, intercept, lo, hi = stats.theilslopes(yv, xv, alpha=alpha)
    return TheilSen(
        slope=float(slope), intercept=float(intercept),
        slope_lo=float(lo), slope_hi=float(hi),
        confidence=float(confidence), n=int(yv.size),
    )


# ---------- Mann-Kendall variants ----------

@dataclass(frozen=True)
class MKResult:
    test: str                 # 'original' | 'hamed_rao' | 'prewhitened'
    trend: str                # 'increasing' | 'decreasing' | 'no trend'
    p: float
    z: float
    tau: float
    s: float
    n: int

    @property
    def significant(self, alpha: float = 0.05) -> bool:  # pragma: no cover
        return self.p < alpha


def _wrap_mk(r, name: str, n: int) -> MKResult:
    # pymannkendall returns a namedtuple: trend, h, p, z, Tau, s, var_s, slope, intercept
    return MKResult(
        test=name,
        trend=str(r.trend),
        p=float(r.p),
        z=float(r.z),
        tau=float(r.Tau),
        s=float(r.s),
        n=int(n),
    )


def mann_kendall(y: np.ndarray) -> MKResult:
    """Plain Mann-Kendall. NaNs are dropped before the test."""
    y = np.asarray(y, dtype=float)
    yv = y[np.isfinite(y)]
    if yv.size < 4:
        raise ValueError(f"mann_kendall: need ≥4 finite points, got {yv.size}")
    return _wrap_mk(pmk.original_test(yv), "original", yv.size)


def mann_kendall_hamed_rao(y: np.ndarray) -> MKResult:
    """Hamed-Rao modified MK; variance is inflated when the series is autocorrelated."""
    y = np.asarray(y, dtype=float)
    yv = y[np.isfinite(y)]
    if yv.size < 4:
        raise ValueError(f"mann_kendall_hamed_rao: need ≥4 finite points, got {yv.size}")
    return _wrap_mk(pmk.hamed_rao_modification_test(yv), "hamed_rao", yv.size)


def mann_kendall_prewhitened(y: np.ndarray) -> MKResult:
    """Prewhitened MK (removes lag-1 AR before testing)."""
    y = np.asarray(y, dtype=float)
    yv = y[np.isfinite(y)]
    if yv.size < 4:
        raise ValueError(f"mann_kendall_prewhitened: need ≥4 finite points, got {yv.size}")
    return _wrap_mk(pmk.pre_whitening_modification_test(yv), "prewhitened", yv.size)


def choose_mk_variant(
    y: np.ndarray,
    *,
    autocorr_threshold: float = 0.10,
    autocorr_variant: Literal["hamed_rao", "prewhitened"] = "hamed_rao",
) -> tuple[str, MKResult, float]:
    """Pick the right MK variant based on |lag-1 autocorrelation|.

    Returns (variant_name, MKResult, lag1).
    """
    rho = lag1_autocorr(y)
    if np.isnan(rho) or abs(rho) < autocorr_threshold:
        return ("original", mann_kendall(y), float(rho) if not np.isnan(rho) else float("nan"))
    if autocorr_variant == "prewhitened":
        return ("prewhitened", mann_kendall_prewhitened(y), float(rho))
    return ("hamed_rao", mann_kendall_hamed_rao(y), float(rho))


# ---------- area weighting ----------

def area_weighted_mean(field: np.ndarray, lats_deg: np.ndarray) -> float:
    """cos(latitude)-weighted mean over a 2-D (lat, lon) array. NaN-aware.

    Weights are cos(lat in radians), broadcast across longitude. Returns NaN if
    no finite cell exists.
    """
    f = np.asarray(field, dtype=float)
    lat = np.asarray(lats_deg, dtype=float)
    if f.ndim != 2:
        raise ValueError(f"area_weighted_mean: field must be 2-D, got shape {f.shape}")
    if lat.shape[0] != f.shape[0]:
        raise ValueError(
            f"area_weighted_mean: lat length {lat.shape[0]} ≠ field.shape[0] {f.shape[0]}"
        )
    w_lat = np.cos(np.deg2rad(lat))
    w_lat = np.clip(w_lat, 0.0, None)           # guard against numeric drift past poles
    w = np.broadcast_to(w_lat[:, None], f.shape)
    mask = np.isfinite(f)
    wsum = (w * mask).sum()
    if wsum == 0:
        return float("nan")
    return float(np.where(mask, f, 0.0).sum() * 0.0 + (w * np.where(mask, f, 0.0)).sum() / wsum)


def valid_cell_fraction(field: np.ndarray) -> float:
    """Fraction of finite cells in a field. Returns 0 for an empty field."""
    f = np.asarray(field)
    if f.size == 0:
        return 0.0
    return float(np.isfinite(f).sum() / f.size)


# ---------- multiple testing ----------

def bh_fdr(
    pvalues: np.ndarray,
    *,
    alpha: float = 0.05,
) -> tuple[np.ndarray, np.ndarray]:
    """Benjamini-Hochberg FDR.

    Returns (rejected_bool, q_values). NaN p-values pass through as NaN q-values
    and False rejections.
    """
    p = np.asarray(pvalues, dtype=float).ravel()
    finite = np.isfinite(p)
    rej = np.zeros_like(p, dtype=bool)
    q = np.full_like(p, np.nan)
    if finite.sum() == 0:
        return rej, q
    r, pval_corr, _, _ = multipletests(p[finite], alpha=alpha, method="fdr_bh")
    rej[finite] = r
    q[finite] = pval_corr
    return rej, q


# ---------- one-call report ----------

def trend_report(
    y: np.ndarray,
    x: np.ndarray | None = None,
    *,
    confidence: float = 0.95,
    alpha: float = 0.05,
    autocorr_threshold: float = 0.10,
    autocorr_variant: Literal["hamed_rao", "prewhitened"] = "hamed_rao",
) -> dict:
    """Full per-series trend analysis.

    Returns a dict ready to be merged into a Provenance record.
    """
    ts = theil_sen_ci(y, x=x, confidence=confidence)
    variant, mk, rho = choose_mk_variant(
        y, autocorr_threshold=autocorr_threshold, autocorr_variant=autocorr_variant,
    )
    return {
        "n": ts.n,
        "slope": ts.slope,
        "slope_ci95": (ts.slope_lo, ts.slope_hi),
        "slope_ci_excludes_zero": ts.ci_excludes_zero(),
        "mk_test": mk.test,
        "mk_trend": mk.trend,
        "p": mk.p,
        "z": mk.z,
        "tau": mk.tau,
        "lag1_autocorr": rho,
        "significant": mk.p < alpha,
        "alpha": alpha,
        "confidence": confidence,
    }
