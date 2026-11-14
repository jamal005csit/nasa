"""Validation pass for an ingested xarray Dataset.

Checks required by STAGE_PROMPTS Stage 2:
  - timestamps ordered and unique
  - units (matches expected)
  - fill values stripped (no suspicious sentinel values remain)
  - missing % (computed, no threshold enforced here — caller decides)
  - spatial bounds (within requested bbox, with small tolerance)

Returns a ValidationReport with one Finding per check. Nothing raises
on a failed check; the caller inspects `report.ok`.
"""

from __future__ import annotations

from typing import Literal

import numpy as np
import xarray as xr
from pydantic import BaseModel

Status = Literal["pass", "fail", "warn", "skip"]


class Finding(BaseModel):
    name: str
    status: Status
    detail: str
    value: float | int | str | None = None


class ValidationReport(BaseModel):
    dataset: str
    variable: str
    n_timestamps: int
    n_cells: int
    n_valid: int
    missing_pct: float
    findings: list[Finding]

    @property
    def ok(self) -> bool:
        return all(f.status in ("pass", "warn", "skip") for f in self.findings)


def _check_time_monotonic_unique(ds: xr.Dataset) -> Finding:
    if "time" not in ds.dims and "time" not in ds.coords:
        return Finding(name="time_monotonic_unique", status="skip",
                       detail="no 'time' coordinate")
    t = ds["time"].values
    if len(t) == 0:
        return Finding(name="time_monotonic_unique", status="fail",
                       detail="empty time axis", value=0)
    unique = len(set(t.tolist())) == len(t)
    monotonic = all(t[i] < t[i + 1] for i in range(len(t) - 1))
    if unique and monotonic:
        return Finding(name="time_monotonic_unique", status="pass",
                       detail=f"{len(t)} timestamps, strictly increasing, no duplicates",
                       value=len(t))
    return Finding(name="time_monotonic_unique", status="fail",
                   detail=f"unique={unique} monotonic={monotonic}", value=len(t))


def _check_units(ds: xr.Dataset, var: str, expected: str) -> Finding:
    if var not in ds:
        return Finding(name="units", status="fail", detail=f"variable '{var}' not in dataset")
    actual = ds[var].attrs.get("units", "")
    if actual == expected:
        return Finding(name="units", status="pass",
                       detail=f"units='{actual}' matches expected", value=actual)
    return Finding(name="units", status="fail",
                   detail=f"units='{actual}' expected='{expected}'", value=actual)


def _check_no_sentinel_fills(ds: xr.Dataset, var: str, sentinels: list[float]) -> Finding:
    """Confirms that known fill-value sentinels have been converted to NaN."""
    if var not in ds:
        return Finding(name="no_sentinel_fills", status="skip", detail=f"no '{var}'")
    da = ds[var]
    arr = np.asarray(da.values)
    hits: dict[float, int] = {}
    for s in sentinels:
        n = int(np.sum(arr == s))
        if n > 0:
            hits[s] = n
    if hits:
        return Finding(name="no_sentinel_fills", status="fail",
                       detail=f"found sentinel values still in data: {hits}")
    return Finding(name="no_sentinel_fills", status="pass",
                   detail=f"no sentinel values {sentinels} remain (should be NaN)")


def _check_spatial_bounds(
    ds: xr.Dataset,
    bbox: tuple[float, float, float, float],
    tol: float = 0.1,
) -> Finding:
    """bbox = (min_lat, max_lat, min_lon, max_lon)."""
    if not {"lat", "lon"}.intersection(set(ds.coords) | set(ds.dims)):
        return Finding(name="spatial_bounds", status="skip",
                       detail="no lat/lon coordinates")
    lat = ds["lat"].values if "lat" in ds.coords else ds["latitude"].values
    lon = ds["lon"].values if "lon" in ds.coords else ds["longitude"].values
    min_lat, max_lat, min_lon, max_lon = bbox
    if lat.size == 0 or lon.size == 0:
        return Finding(
            name="spatial_bounds", status="fail",
            detail=f"empty subset — no cells inside requested bbox "
                   f"lat=[{min_lat},{max_lat}] lon=[{min_lon},{max_lon}]",
        )
    inside = (
        float(lat.min()) >= min_lat - tol
        and float(lat.max()) <= max_lat + tol
        and float(lon.min()) >= min_lon - tol
        and float(lon.max()) <= max_lon + tol
    )
    detail = (f"actual lat=[{float(lat.min()):.3f},{float(lat.max()):.3f}] "
              f"lon=[{float(lon.min()):.3f},{float(lon.max()):.3f}] "
              f"requested lat=[{min_lat},{max_lat}] lon=[{min_lon},{max_lon}]")
    return Finding(name="spatial_bounds",
                   status="pass" if inside else "fail",
                   detail=detail)


def validate(
    ds: xr.Dataset,
    *,
    dataset_name: str,
    variable: str,
    expected_units: str,
    bbox: tuple[float, float, float, float],
    sentinels: list[float],
) -> ValidationReport:
    """Run all checks and return a report."""
    findings = [
        _check_time_monotonic_unique(ds),
        _check_units(ds, variable, expected_units),
        _check_no_sentinel_fills(ds, variable, sentinels),
        _check_spatial_bounds(ds, bbox),
    ]
    if variable in ds:
        arr = np.asarray(ds[variable].values)
        n_total = int(arr.size)
        n_valid = int(np.sum(~np.isnan(arr)))
        missing_pct = 100.0 * (n_total - n_valid) / max(n_total, 1)
    else:
        n_total = n_valid = 0
        missing_pct = 100.0
    n_t = len(ds["time"]) if "time" in ds.coords or "time" in ds.dims else 0
    return ValidationReport(
        dataset=dataset_name,
        variable=variable,
        n_timestamps=int(n_t),
        n_cells=n_total,
        n_valid=n_valid,
        missing_pct=missing_pct,
        findings=findings,
    )
