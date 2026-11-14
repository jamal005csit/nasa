"""Stage 4 export: regional time series + trend + provenance → JSON files under
`web/public/data/`. One file per region plus a top-level summary.json.

Entry points:
    build_region_export(ds, region_meta, source_kind) -> RegionExport
    build_summary(region_exports, source_kind)       -> Summary
    write_all(exports, summary, web_data_dir)        -> list[Path]

The web app reads only these JSONs. Every number in the UI traces back to
exactly one field in one of these files.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import xarray as xr

from earthnext.provenance import (
    BoundingBox,
    Method,
    Provenance,
    git_commit,
    hash_config,
    library_versions,
    now_utc_iso,
    sha256_bytes,
)
from earthnext.schemas import (
    AnnualSeries,
    Coverage,
    FeaturedFinding,
    RegionExport,
    RegionMeta,
    SignificanceResult,
    SourceLabel,
    Summary,
    TrendResult,
)
from earthnext.trends import (
    aggregate_annual,
    area_weighted_mean,
    choose_mk_variant,
    theil_sen_ci,
)


def _format_p(p: float) -> str:
    """SPEC §3 rule 13: never '0.000', say 'p < 0.001'."""
    if p < 0.001:
        return "p < 0.001"
    return f"p = {p:.3f}"


def _region_area_weighted_annual(
    ds: xr.Dataset,
    *,
    min_valid_months: int,
) -> tuple[AnnualSeries, Coverage]:
    """Collapse (time, lat, lon) → (time,) via cos(lat) area-weighted mean per
    timestep, then aggregate to annual means with the coverage rule.
    """
    lat = ds["lat"].values
    monthly_series = np.array(
        [area_weighted_mean(ds["ndvi"].isel(time=i).values, lat)
         for i in range(ds.sizes["time"])]
    )
    times = ds["time"].values
    years, annual = aggregate_annual(times, monthly_series,
                                     min_valid_months=min_valid_months)

    # Per-year valid-month count
    import pandas as pd
    s = pd.Series(monthly_series, index=pd.to_datetime(times))
    s = s.sort_index()
    valid_months = s.groupby(s.index.year).apply(
        lambda g: int(np.sum(~np.isnan(g.values)))
    )
    valid_per_year = [int(valid_months.get(int(y), 0)) for y in years]

    n_total_expected = len(times)
    n_missing = int(np.sum(~np.isfinite(monthly_series)))
    missing_pct = 100.0 * n_missing / max(n_total_expected, 1)

    coverage = Coverage(
        n_valid_years=int(np.sum(~np.isnan(annual))),
        n_total_years=int(len(years)),
        missing_pct=float(missing_pct),
    )
    series = AnnualSeries(
        years=[int(y) for y in years],
        values=[None if np.isnan(v) else float(v) for v in annual],
        valid_months_per_year=valid_per_year,
    )
    return series, coverage


def _trend_and_significance(
    series: AnnualSeries,
    *,
    confidence: float,
    autocorr_threshold: float,
    autocorr_variant: str,
) -> tuple[TrendResult, SignificanceResult]:
    years = np.array(series.years, dtype=float)
    vals = np.array([np.nan if v is None else v for v in series.values], dtype=float)
    mask = np.isfinite(vals)
    y = vals[mask]
    x = years[mask]
    ts = theil_sen_ci(y, x=x, confidence=confidence)
    variant, mk, lag1 = choose_mk_variant(
        y, autocorr_threshold=autocorr_threshold,
        autocorr_variant=autocorr_variant,  # type: ignore[arg-type]
    )
    trend = TrendResult(
        estimator="theil_sen",
        slope_per_year=ts.slope,
        slope_ci95=(ts.slope_lo, ts.slope_hi),
        slope_ci_excludes_zero=ts.ci_excludes_zero(),
        intercept=ts.intercept,
        n=ts.n,
        units="NDVI / year",
    )
    sig = SignificanceResult(
        test=variant,  # type: ignore[arg-type]
        p=float(mk.p),
        z=float(mk.z),
        tau=float(mk.tau),
        trend_direction=mk.trend,  # type: ignore[arg-type]
        lag1_autocorr=None if np.isnan(lag1) else float(lag1),
        significant_at_005=bool(mk.p < 0.05),
        p_display=_format_p(float(mk.p)),
    )
    return trend, sig


def build_region_export(
    ds: xr.Dataset,
    region_meta: RegionMeta,
    *,
    source: SourceLabel,
    dataset_short_name: str,
    dataset_version: str,
    dataset_source_url: str,
    variable: str,
    config: dict,
) -> RegionExport:
    annual, coverage = _region_area_weighted_annual(
        ds, min_valid_months=config["aggregation"]["min_valid_months_per_year"],
    )
    trend, sig = _trend_and_significance(
        annual,
        confidence=config["trend"]["confidence_level"],
        autocorr_threshold=config["trend"]["autocorr_threshold"],
        autocorr_variant=config["trend"]["autocorr_variant"],
    )

    bbox_tuple = (region_meta.bbox.min_lat, region_meta.bbox.max_lat,
                  region_meta.bbox.min_lon, region_meta.bbox.max_lon)

    years_valid = [y for y, v in zip(annual.years, annual.values, strict=False) if v is not None]
    time_range = (f"{min(years_valid):04d}-01" if years_valid else "n/a",
                  f"{max(years_valid):04d}-12" if years_valid else "n/a")

    prov = Provenance(
        dataset=f"{dataset_short_name} {dataset_version}",
        source_url=dataset_source_url,
        variable=variable,
        units="1",
        time_range=time_range,
        spatial_extent=BoundingBox(
            min_lat=region_meta.bbox.min_lat,
            max_lat=region_meta.bbox.max_lat,
            min_lon=region_meta.bbox.min_lon,
            max_lon=region_meta.bbox.max_lon,
        ),
        resolution=config.get("resolution_note", "see dataset landing page"),
        filters_applied=[
            "fill(-3000)->NaN",
            "scale*0.0001",
            "pixel_reliability > 1 masked",
            f"cos(lat) area-weighted regional mean within bbox {bbox_tuple}",
            f"annual mean with ≥{config['aggregation']['min_valid_months_per_year']} valid months",
        ],
        method=Method(
            estimator="theil_sen",
            test=sig.test,
            fdr_method=config["multiple_testing"]["method"],
            alpha=config["trend"]["significance_alpha"],
        ),
        n_valid=coverage.n_valid_years,
        missing_pct=coverage.missing_pct,
        slope=trend.slope_per_year,
        slope_ci95=trend.slope_ci95,
        p=sig.p,
        q=None,                      # single test per region; FDR at Stage 7
        script_commit=git_commit(),
        config_hash=hash_config(config),
        data_checksum=sha256_bytes(
            json.dumps(annual.model_dump(), sort_keys=True).encode()
        ),
        library_versions=library_versions(
            ["numpy", "pandas", "xarray", "scipy", "statsmodels",
             "pymannkendall", "pydantic"]
        ),
        generated_at=now_utc_iso(),
    )
    return RegionExport(
        source=source,
        region=region_meta,
        annual=annual,
        trend=trend,
        significance=sig,
        coverage=coverage,
        provenance=prov,
    )


def _featured_sentence(r: RegionExport) -> str:
    dir_word = {
        "increasing": "increased",
        "decreasing": "decreased",
        "no trend": "showed no statistically detectable trend in",
    }[r.significance.trend_direction]
    if r.significance.trend_direction == "no trend":
        return (f"In the {r.region.name}, annual-mean NDVI "
                f"{dir_word} from {r.annual.years[0]} to {r.annual.years[-1]} "
                f"({r.significance.p_display}, {r.significance.test} test).")
    return (
        f"In the {r.region.name}, annual-mean NDVI {dir_word} at "
        f"{r.trend.slope_per_year:+.4f} per year "
        f"(95% CI {r.trend.slope_ci95[0]:+.4f} to {r.trend.slope_ci95[1]:+.4f}) "
        f"between {r.annual.years[0]} and {r.annual.years[-1]} "
        f"({r.significance.p_display}, {r.significance.test} test)."
    )


def build_summary(
    region_exports: list[RegionExport],
    *,
    source: SourceLabel,
    dataset_short_name: str,
    dataset_version: str,
    variable: str,
) -> Summary:
    # Featured finding: the region with the strongest significant trend, else
    # the one with the lowest p-value.
    picked = min(region_exports, key=lambda r: (not r.significance.significant_at_005,
                                                 r.significance.p))
    y0 = min(min(r.annual.years) for r in region_exports)
    y1 = max(max(r.annual.years) for r in region_exports)
    featured = FeaturedFinding(
        region_slug=picked.region.slug,
        sentence=_featured_sentence(picked),
        slope_per_year=picked.trend.slope_per_year,
        slope_ci95=picked.trend.slope_ci95,
        p=picked.significance.p,
        esi_grade=None,
    )
    return Summary(
        source=source,
        generated_at=now_utc_iso(),
        dataset_short_name=dataset_short_name,
        dataset_version=dataset_version,
        variable=variable,
        units="1",
        time_range=(f"{y0:04d}-01", f"{y1:04d}-12"),
        regions=[r.region for r in region_exports],
        featured_finding=featured,
    )


def write_all(
    region_exports: list[RegionExport],
    summary: Summary,
    web_data_dir: Path,
) -> list[Path]:
    """Write summary.json + one regions/<slug>.json per region. Returns paths."""
    web_data_dir.mkdir(parents=True, exist_ok=True)
    (web_data_dir / "regions").mkdir(exist_ok=True)
    written: list[Path] = []

    p = web_data_dir / "summary.json"
    p.write_text(summary.model_dump_json(indent=2), encoding="utf-8")
    written.append(p)

    for r in region_exports:
        p = web_data_dir / "regions" / f"{r.region.slug}.json"
        p.write_text(r.model_dump_json(indent=2), encoding="utf-8")
        written.append(p)

    return written
