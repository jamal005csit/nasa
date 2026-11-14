"""Tests for ESI scoring and robustness checks on known series."""

import numpy as np
import pytest

from earthnext.esi import compute_esi
from earthnext.robustness import (
    leave_one_out,
    method_agreement,
    robustness_report,
    start_end_sensitivity,
)


# ---- ESI tests ----

def test_esi_perfect_score():
    """All conditions met → grade A with max points."""
    cfg = _config()
    result = compute_esi(
        n_valid_years=20,
        missing_pct=2.0,
        p=0.001,
        q=None,
        slope_ci_excludes_zero=True,
        sign_stable_pct=95.0,
        theil_sen_ols_agree=True,
        leave_one_out_stable=True,
        config=cfg,
    )
    assert result.grade == "A"
    assert result.score == 10.0


def test_esi_grade_d_when_nothing_works():
    cfg = _config()
    result = compute_esi(
        n_valid_years=10,
        missing_pct=30.0,
        p=0.5,
        q=None,
        slope_ci_excludes_zero=False,
        sign_stable_pct=40.0,
        theil_sen_ols_agree=False,
        leave_one_out_stable=False,
        config=cfg,
    )
    assert result.grade == "D"
    assert result.score == 0.0


def test_esi_grade_b_boundary():
    """Score at 6 → grade B (inclusive lower bound)."""
    cfg = _config()
    result = compute_esi(
        n_valid_years=20,        # +2
        missing_pct=5.0,         # +1
        p=0.01,                  # +2 (q=None, use p)
        q=None,
        slope_ci_excludes_zero=True,  # +1
        sign_stable_pct=70.0,    # +0 (below 90%)
        theil_sen_ols_agree=True,     # +1 (but actually needs to check)
        leave_one_out_stable=False,   # +0
        config=cfg,
    )
    assert result.grade == "B"
    assert 6 <= result.score < 8


def test_esi_breakdown_keys():
    cfg = _config()
    result = compute_esi(
        n_valid_years=20, missing_pct=5.0, p=0.01, q=None,
        slope_ci_excludes_zero=True, sign_stable_pct=95.0,
        theil_sen_ols_agree=True, leave_one_out_stable=True,
        config=cfg,
    )
    expected_keys = {
        "years_ge_15", "missing_pct_le_10", "pq_lt_005",
        "slope_ci_excludes_zero", "sign_stable_90pct",
        "theil_sen_ols_agree", "leave_one_out_stable",
    }
    assert set(result.breakdown.keys()) == expected_keys


def test_esi_with_q():
    """When q is provided, use q instead of p for the pq_lt_005 check."""
    cfg = _config()
    # p is significant but q is not → should lose those 2 points
    result = compute_esi(
        n_valid_years=20, missing_pct=5.0, p=0.001, q=0.08,
        slope_ci_excludes_zero=True, sign_stable_pct=95.0,
        theil_sen_ols_agree=True, leave_one_out_stable=True,
        config=cfg,
    )
    assert result.breakdown["pq_lt_005"] == 0.0


# ---- Robustness tests ----

def test_start_end_sensitivity_pure_linear():
    """Pure positive trend → 100% sign stability."""
    rng = np.random.default_rng(42)
    x = np.arange(20, dtype=float)
    y = 2.0 + 0.5 * x + rng.normal(0, 0.1, 20)
    pct, total, same = start_end_sensitivity(y, x, min_window_years=10)
    assert total > 0
    assert pct == 100.0
    assert same == total


def test_method_agreement_on_linear():
    """Theil-Sen and OLS should agree on a clean linear series."""
    rng = np.random.default_rng(42)
    x = np.arange(25, dtype=float)
    y = 3.0 + 0.2 * x + rng.normal(0, 0.05, 25)
    assert method_agreement(y, x) is True


def test_method_agreement_on_negative():
    """Both methods detect negative trend."""
    rng = np.random.default_rng(42)
    x = np.arange(25, dtype=float)
    y = 5.0 - 0.3 * x + rng.normal(0, 0.1, 25)
    assert method_agreement(y, x) is True


def test_leave_one_out_linear():
    """LOO should keep the same sign for a strong trend."""
    rng = np.random.default_rng(42)
    x = np.arange(20, dtype=float)
    y = 1.0 + 0.1 * x + rng.normal(0, 0.02, 20)
    stable, lo, hi = leave_one_out(y, x)
    assert stable is True
    assert lo > 0
    assert hi > 0


def test_robustness_report_returns_dataclass():
    rng = np.random.default_rng(42)
    y = rng.normal(0, 1, 20)
    report = robustness_report(y, min_window_years=10)
    assert report.full_slope_sign in (-1, 0, 1)
    assert report.windows_tested > 0
    assert 0.0 <= report.sign_stable_pct <= 100.0


# ---- helpers ----

def _config() -> dict:
    import yaml
    from pathlib import Path

    cfg_path = Path(__file__).resolve().parents[2] / "science" / "config" / "analysis.yaml"
    return yaml.safe_load(cfg_path.read_text())
