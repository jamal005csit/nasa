"""Tests for Decision Lab: time-to-threshold and scenario fan."""

import math
import pytest

from earthnext.threshold import compute_threshold, scenario_fan


def test_time_to_threshold_positive_slope():
    ttt = compute_threshold(
        threshold=0.40, end_year=2026, end_value=0.3708,
        slope=0.00079, slope_lo=0.00050, slope_hi=0.00110,
    )
    assert ttt.can_bound() is True
    s = ttt.summary()
    assert s["boundable"] is True
    assert s["crossing_year"] is not None
    assert s["crossing_year"] > 2026
    assert "Illustrative scenario" in s["mandatory_label"]


def test_time_to_threshold_negative_slope_crosses_zero():
    ttt = compute_threshold(
        threshold=0.090, end_year=2026, end_value=0.0948,
        slope=-0.000055, slope_lo=-0.000131, slope_hi=0.000017,
    )
    assert ttt.can_bound() is False
    s = ttt.summary()
    assert s["boundable"] is False
    assert "Cannot be bounded" in s["note"]


def test_time_to_threshold_moving_away():
    """Threshold is above end value but slope is negative — can't reach."""
    ttt = compute_threshold(
        threshold=0.40, end_year=2026, end_value=0.30,
        slope=-0.001, slope_lo=-0.002, slope_hi=-0.0005,
    )
    assert ttt.can_bound() is True
    assert ttt.years_to(ttt.slope) is None  # Moving away


def test_scenario_fan():
    fan = scenario_fan(
        end_year=2026, end_value=0.37,
        slope=0.0008, slope_lo=0.0005, slope_hi=0.0011,
        horizon=2050,
    )
    s = fan.summary()
    assert s["horizon"] == 2050
    assert len(s["years"]) == 2050 - 2026
    assert s["continuation"][-1] == pytest.approx(0.37 + 0.0008 * 24, abs=1e-4)
    assert "Illustrative scenario" in s["mandatory_label"]


def test_threshold_zero_slope():
    ttt = compute_threshold(
        threshold=0.40, end_year=2026, end_value=0.30,
        slope=0.0, slope_lo=-0.001, slope_hi=0.001,
    )
    assert ttt.can_bound() is False
