"""Pydantic models for every JSON exported to `web/public/data/`.

The matching Zod schemas live at `web/src/lib/schemas.ts`. A Stage-4 test
asserts that every exported file parses in BOTH schema languages. Keep the
two files in sync whenever a field is added, removed, or renamed.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from earthnext.provenance import Provenance

# ------------------------------------------------------------------
# small shared sub-models
# ------------------------------------------------------------------


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BBox(_Base):
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float


class RegionMeta(_Base):
    slug: str
    name: str
    bbox: BBox


class AnnualSeries(_Base):
    """Area-weighted regional annual-mean NDVI."""

    years: list[int]
    values: list[float | None]          # None for years that failed the coverage rule
    valid_months_per_year: list[int]


class TrendResult(_Base):
    estimator: Literal["theil_sen"]
    slope_per_year: float
    slope_ci95: tuple[float, float]
    slope_ci_excludes_zero: bool
    intercept: float
    n: int
    units: str                           # e.g. "NDVI / year"


class SignificanceResult(_Base):
    test: Literal["original", "hamed_rao", "prewhitened"]
    p: float
    z: float
    tau: float
    trend_direction: Literal["increasing", "decreasing", "no trend"]
    lag1_autocorr: float | None
    significant_at_005: bool
    p_display: str                       # "p < 0.001" or "p = 0.034" per SPEC §3 rule 13


class Coverage(_Base):
    n_valid_years: int
    n_total_years: int
    missing_pct: float                   # 0-100, pct of expected months that are NaN


# ------------------------------------------------------------------
# files written to web/public/data/
# ------------------------------------------------------------------


class SourceLabel(_Base):
    kind: Literal["DEMO", "NASA"] = Field(
        description="DEMO means synthetic placeholder; NASA means real AppEEARS output. "
                    "The UI shows a prominent banner when this is DEMO."
    )
    note: str


class ESIResultSchema(_Base):
    score: float
    grade: Literal["A", "B", "C", "D"]
    breakdown: dict[str, float]
    label: str


class RobustnessSchema(_Base):
    sign_stable_pct: float
    ts_ols_agree: bool
    loo_stable: bool
    loo_min_slope: float
    loo_max_slope: float
    windows_tested: int
    windows_same_sign: int
    min_window_years: int


class FeaturedFinding(_Base):
    region_slug: str
    sentence: str
    slope_per_year: float
    slope_ci95: tuple[float, float]
    p: float
    esi_grade: Literal["A", "B", "C", "D"] | None = None   # None until Stage 7


class Summary(_Base):
    """`web/public/data/summary.json` — one file, the index + featured finding."""

    source: SourceLabel
    generated_at: str                    # ISO UTC
    dataset_short_name: str
    dataset_version: str
    variable: str
    units: str
    time_range: tuple[str, str]          # "YYYY-MM"
    regions: list[RegionMeta]
    featured_finding: FeaturedFinding


class RegionExport(_Base):
    """`web/public/data/regions/<slug>.json` — one per region."""

    source: SourceLabel
    region: RegionMeta
    annual: AnnualSeries
    trend: TrendResult
    significance: SignificanceResult
    coverage: Coverage
    provenance: Provenance
    esi: ESIResultSchema | None = None
    robustness: RobustnessSchema | None = None
