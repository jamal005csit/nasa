"""Stats engine tests — written against synthetic series with known answers.

SPEC §3 test list:
  - pure linear: slope recovered
  - zero-trend noise: rejection rate ~ alpha over many seeds
  - step change: trend detected
  - strong seasonality: annual aggregation removes false trend
  - AR(1): modified MK less liberal than plain MK
  - missing-data patterns: coverage rule enforced
  - independent check: scipy.theilslopes vs our wrapper
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from scipy import stats as sp

from earthnext.trends import (
    aggregate_annual,
    area_weighted_mean,
    bh_fdr,
    choose_mk_variant,
    lag1_autocorr,
    mann_kendall,
    mann_kendall_hamed_rao,
    theil_sen_ci,
    trend_report,
    valid_cell_fraction,
)

# ---------- aggregation ----------

def test_aggregate_annual_coverage_rule_strict() -> None:
    times = pd.date_range("2000-01-01", periods=24, freq="MS")
    values = np.arange(24, dtype=float)
    # drop 4 months of year 2000 -> coverage = 8, below threshold 9
    values[0:4] = np.nan
    years, annual = aggregate_annual(times, values, min_valid_months=9)
    assert years.tolist() == [2000, 2001]
    assert np.isnan(annual[0])            # year 2000 excluded by coverage rule
    assert annual[1] == np.mean(values[12:24])


def test_aggregate_annual_all_valid() -> None:
    times = pd.date_range("2000-01-01", periods=36, freq="MS")
    values = np.arange(36, dtype=float)
    years, annual = aggregate_annual(times, values)
    assert years.tolist() == [2000, 2001, 2002]
    assert annual[0] == np.mean(values[0:12])
    assert annual[1] == np.mean(values[12:24])
    assert annual[2] == np.mean(values[24:36])


def test_aggregate_annual_removes_seasonality_so_no_false_trend() -> None:
    """A pure 12-month sine + zero long-term drift should produce
    annual means ≈ 0, hence no detectable trend."""
    t = np.arange(20 * 12)
    y = np.sin(2 * np.pi * t / 12)        # period 12 months, mean 0 per year
    times = pd.date_range("2000-01-01", periods=len(y), freq="MS")
    _, annual = aggregate_annual(times, y)
    assert np.all(np.abs(annual) < 1e-10)   # seasonality collapsed exactly
    # Plain MK on the annual means: not significant (there is literally no trend)
    mk = mann_kendall(annual)
    assert mk.trend == "no trend"
    assert mk.p > 0.05


# ---------- Theil-Sen ----------

def test_theil_sen_recovers_pure_linear_slope_exactly() -> None:
    x = np.arange(30, dtype=float)
    y = 0.5 * x + 3.0
    ts = theil_sen_ci(y, x=x)
    assert ts.slope == pytest.approx(0.5, abs=1e-12)
    assert ts.intercept == pytest.approx(3.0, abs=1e-12)
    assert ts.ci_excludes_zero()


def test_theil_sen_ci_contains_true_slope_for_noisy_linear() -> None:
    rng = np.random.default_rng(0)
    x = np.arange(100, dtype=float)
    y = 0.1 * x + rng.standard_normal(100)
    ts = theil_sen_ci(y, x=x)
    assert ts.slope_lo < 0.1 < ts.slope_hi


def test_theil_sen_requires_three_points() -> None:
    with pytest.raises(ValueError):
        theil_sen_ci(np.array([1.0, 2.0]))


def test_theil_sen_cross_check_against_scipy() -> None:
    """Independent check per SPEC §3 rule 12: our wrapper's result must equal
    the direct scipy.stats.theilslopes call on the same data."""
    rng = np.random.default_rng(123)
    x = np.arange(50, dtype=float)
    y = 0.2 * x + 5.0 + rng.standard_normal(50) * 0.3
    ours = theil_sen_ci(y, x=x)
    sp_s, sp_i, sp_lo, sp_hi = sp.theilslopes(y, x, alpha=0.05)
    assert ours.slope == pytest.approx(sp_s)
    assert ours.intercept == pytest.approx(sp_i)
    assert ours.slope_lo == pytest.approx(sp_lo)
    assert ours.slope_hi == pytest.approx(sp_hi)


# ---------- Mann-Kendall ----------

def test_mk_pure_linear_is_significant_increasing() -> None:
    y = np.arange(30, dtype=float)
    mk = mann_kendall(y)
    assert mk.trend == "increasing"
    assert mk.p < 0.001


def test_mk_zero_trend_noise_rejection_rate_near_alpha() -> None:
    """Over many seeds of pure noise, plain MK should reject H0 at roughly alpha.
    With 500 trials this is tight but noisy; we allow a generous band."""
    rng = np.random.default_rng(2026)
    alpha = 0.05
    trials = 500
    rejects = 0
    for _ in range(trials):
        y = rng.standard_normal(30)
        try:
            mk = mann_kendall(y)
        except ValueError:
            continue
        if mk.p < alpha:
            rejects += 1
    rate = rejects / trials
    # Expect ~0.05; accept 0.02–0.10 to keep flake rate near zero.
    assert 0.02 <= rate <= 0.10, f"empirical rejection rate {rate:.3f}"


def test_mk_step_change_is_significant() -> None:
    y = np.concatenate([np.zeros(15), np.ones(15)]).astype(float)
    mk = mann_kendall(y)
    assert mk.trend == "increasing"
    assert mk.p < 0.01


def test_hamed_rao_is_less_liberal_than_plain_mk_on_ar1() -> None:
    """Build strongly AR(1) series with ρ ≈ 0.7. Plain MK will reject too often;
    Hamed-Rao should reject less often (its p-values are inflated vs plain MK
    whenever positive autocorrelation is present)."""
    rng = np.random.default_rng(7)
    trials = 400
    alpha = 0.05
    plain_rej = 0
    hr_rej = 0
    for _ in range(trials):
        n = 40
        rho = 0.7
        e = rng.standard_normal(n)
        y = np.zeros(n)
        for i in range(1, n):
            y[i] = rho * y[i - 1] + e[i]
        if mann_kendall(y).p < alpha:
            plain_rej += 1
        if mann_kendall_hamed_rao(y).p < alpha:
            hr_rej += 1
    assert plain_rej > hr_rej, (
        f"plain MK should over-reject vs Hamed-Rao on AR(1): "
        f"plain={plain_rej}/{trials}, hr={hr_rej}/{trials}"
    )


def test_choose_mk_variant_picks_hamed_rao_on_autocorrelated_series() -> None:
    rng = np.random.default_rng(11)
    n = 60
    rho = 0.6
    e = rng.standard_normal(n)
    y = np.zeros(n)
    for i in range(1, n):
        y[i] = rho * y[i - 1] + e[i]
    variant, mk, lag1 = choose_mk_variant(y, autocorr_threshold=0.10)
    assert variant == "hamed_rao"
    assert abs(lag1) >= 0.10


def test_choose_mk_variant_picks_plain_on_uncorrelated_series() -> None:
    # White noise's sample lag-1 autocorr has SE ≈ 1/sqrt(n); n=2000 keeps it well
    # below the 0.10 threshold so the branch choice is deterministic.
    rng = np.random.default_rng(12)
    y = rng.standard_normal(2000)
    variant, mk, lag1 = choose_mk_variant(y, autocorr_threshold=0.10)
    assert variant == "original"
    assert abs(lag1) < 0.10


def test_mk_with_missing_data_pattern() -> None:
    y = np.arange(30, dtype=float)
    y[::5] = np.nan
    mk = mann_kendall(y)
    assert mk.trend == "increasing"
    assert mk.n == 24


# ---------- lag-1 ----------

def test_lag1_autocorr_recovers_known_rho() -> None:
    rng = np.random.default_rng(99)
    rho = 0.6
    n = 5000
    e = rng.standard_normal(n)
    y = np.zeros(n)
    for i in range(1, n):
        y[i] = rho * y[i - 1] + e[i]
    assert lag1_autocorr(y) == pytest.approx(rho, abs=0.05)


def test_lag1_autocorr_on_pure_noise_near_zero() -> None:
    rng = np.random.default_rng(100)
    y = rng.standard_normal(10000)
    assert abs(lag1_autocorr(y)) < 0.05


# ---------- area weighting ----------

def test_area_weighted_mean_equals_arithmetic_at_equator() -> None:
    field = np.array([[1.0, 2.0, 3.0]])
    assert area_weighted_mean(field, np.array([0.0])) == pytest.approx(2.0)


def test_area_weighted_mean_higher_latitude_gets_less_weight() -> None:
    field = np.array([[10.0, 10.0, 10.0],
                      [0.0, 0.0, 0.0]])
    # row 0 at the equator (weight cos(0)=1), row 1 near pole (weight cos(89.999°) ≈ 1.75e-5).
    # Weighted mean collapses to row 0's value (10) within ~2e-4.
    out = area_weighted_mean(field, np.array([0.0, 89.999]))
    assert out == pytest.approx(10.0, abs=1e-3)


def test_area_weighted_mean_matches_hand_computed_value() -> None:
    # Explicit formula sanity check: at lat 60°, cos(60°)=0.5; at lat 0°, cos(0°)=1.
    # Field has value v0 at row 0 (eq), v1 at row 1 (60°).
    # Weighted mean = (v0 * 1 + v1 * 0.5) / (1 + 0.5) per column; same each column.
    field = np.array([[2.0, 2.0], [8.0, 8.0]])
    expected = (2.0 * 1.0 + 8.0 * 0.5) / (1.0 + 0.5)
    out = area_weighted_mean(field, np.array([0.0, 60.0]))
    assert out == pytest.approx(expected)


def test_area_weighted_mean_handles_nans() -> None:
    field = np.array([[np.nan, 2.0], [4.0, np.nan]])
    out = area_weighted_mean(field, np.array([0.0, 0.0]))
    assert out == pytest.approx(3.0)


def test_valid_cell_fraction() -> None:
    assert valid_cell_fraction(np.array([1.0, np.nan, 3.0])) == pytest.approx(2 / 3)


# ---------- BH FDR ----------

def test_bh_fdr_known_example() -> None:
    p = np.array([0.001, 0.008, 0.039, 0.041, 0.042, 0.06, 0.074, 0.205, 0.212, 0.216])
    rej, q = bh_fdr(p, alpha=0.05)
    # Recompute with statsmodels directly for the expected result
    from statsmodels.stats.multitest import multipletests
    exp_rej, exp_q, _, _ = multipletests(p, alpha=0.05, method="fdr_bh")
    assert rej.tolist() == exp_rej.tolist()
    assert np.allclose(q, exp_q)


def test_bh_fdr_nan_passthrough() -> None:
    p = np.array([0.01, np.nan, 0.5])
    rej, q = bh_fdr(p)
    assert rej[1] == False  # noqa: E712
    assert np.isnan(q[1])


# ---------- trend_report ----------

def test_trend_report_on_known_linear_series() -> None:
    x = np.arange(30, dtype=float)
    y = 0.1 * x + 5.0
    r = trend_report(y, x=x)
    assert r["slope"] == pytest.approx(0.1, abs=1e-12)
    assert r["significant"] is True
    assert r["slope_ci_excludes_zero"] is True
    assert r["mk_trend"] == "increasing"
