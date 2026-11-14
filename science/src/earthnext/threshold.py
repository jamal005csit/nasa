"""Decision Lab — time-to-threshold and scenario computations.

SPEC §2 item 6. All results are deterministic from slope + CI. Every output
carries the mandatory label.

Key contract:
  t* = t_end + (threshold - y_end) / slope
  Evaluated at slope, slope_lo, slope_hi.
  If CI includes 0 → "cannot be bounded" instead of a date.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeToThreshold:
    threshold: float
    end_year: int
    end_value: float
    slope: float
    slope_lo: float
    slope_hi: float

    def can_bound(self) -> bool:
        """True if the 95% CI does not cross zero."""
        return (self.slope_lo > 0) or (self.slope_hi < 0)

    def years_to(self, s: float) -> float | None:
        """Years from end_year to reach threshold at slope s. None if slope is zero
        or would never reach the threshold (moving away from it)."""
        if abs(s) < 1e-15:
            return None
        gap = self.threshold - self.end_value
        # If we're moving away from the threshold, can't bound
        if (gap > 0 and s < 0) or (gap < 0 and s > 0):
            return None
        return gap / s

    def summary(self) -> dict:
        yrs = self.years_to(self.slope)
        yrs_lo = self.years_to(self.slope_lo)
        yrs_hi = self.years_to(self.slope_hi)

        if not self.can_bound():
            return {
                "threshold": self.threshold,
                "end_year": self.end_year,
                "end_value": self.end_value,
                "boundable": False,
                "note": "Cannot be bounded — trend not established (95% CI includes zero).",
                "mandatory_label": "Illustrative scenario — not a validated causal forecast.",
            }

        def maybe_yr(y: float | None) -> int | None:
            if y is None:
                return None
            return self.end_year + max(0, int(round(y)))

        return {
            "threshold": self.threshold,
            "end_year": self.end_year,
            "end_value": self.end_value,
            "slope_per_year": self.slope,
            "slope_ci95": [self.slope_lo, self.slope_hi],
            "boundable": True,
            "years_to_threshold": yrs,
            "years_lo": yrs_lo,
            "years_hi": yrs_hi,
            "crossing_year": maybe_yr(yrs) if yrs is not None else None,
            "crossing_year_lo": maybe_yr(yrs_lo) if yrs_lo is not None else None,
            "crossing_year_hi": maybe_yr(yrs_hi) if yrs_hi is not None else None,
            "mandatory_label": "Illustrative scenario — not a validated causal forecast.",
        }


@dataclass(frozen=True)
class ScenarioFan:
    """Continuation scenarios at slope, slope_lo, slope_hi."""
    years: list[int]
    continuation: list[float]
    ci_lower: list[float]
    ci_upper: list[float]
    horizon: int

    def summary(self) -> dict:
        return {
            "horizon": self.horizon,
            "years": self.years,
            "continuation": self.continuation,
            "ci_lower": self.ci_lower,
            "ci_upper": self.ci_upper,
            "mandatory_label": "Illustrative scenario — not a validated causal forecast.",
        }


def compute_threshold(
    *,
    threshold: float,
    end_year: int,
    end_value: float,
    slope: float,
    slope_lo: float,
    slope_hi: float,
) -> TimeToThreshold:
    return TimeToThreshold(
        threshold=threshold,
        end_year=end_year,
        end_value=end_value,
        slope=slope,
        slope_lo=slope_lo,
        slope_hi=slope_hi,
    )


def scenario_fan(
    *,
    end_year: int,
    end_value: float,
    slope: float,
    slope_lo: float,
    slope_hi: float,
    horizon: int,
) -> ScenarioFan:
    """Generate continuation + CI fan from end_year to horizon."""
    years = list(range(end_year + 1, horizon + 1))
    cont = [end_value + slope * (y - end_year) for y in years]
    lo = [end_value + slope_lo * (y - end_year) for y in years]
    hi = [end_value + slope_hi * (y - end_year) for y in years]
    return ScenarioFan(years=years, continuation=cont, ci_lower=lo, ci_upper=hi, horizon=horizon)
