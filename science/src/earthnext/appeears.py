"""Reader for AppEEARS-style NetCDF output (or the DEMO equivalent).

AppEEARS Area Sample delivers one NetCDF file per time step, each already
clipped to the requested polygon. We also accept a single multi-time NetCDF
(what the DEMO generator produces) — behaviour is identical: we always end
up with an xarray Dataset with dims (time, lat, lon) and a variable `ndvi`.

Fill-value handling, int→float conversion, and NDVI scale factor are the same
as the HDF ingest path in ingest.py. Pixel reliability (if present) is used
to mask values whose reliability is worse than 1 (good / marginal).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import xarray as xr

NDVI_FILL = -3000
NDVI_SCALE = 0.0001
NDVI_VALID_MIN = -2000
NDVI_VALID_MAX = 10000


@dataclass(frozen=True)
class AppEEARSSource:
    region_slug: str
    region_name: str
    files: list[Path]


def _decode_ndvi(raw: xr.DataArray) -> xr.DataArray:
    """Clip and label.

    xarray's default `decode_cf=True` has already applied `_FillValue` → NaN
    and multiplied by `scale_factor` when opening the file. Our job here is
    just to (a) clip stray out-of-range values and (b) attach documentation.
    """
    arr = raw.astype("float32")
    arr = arr.where((arr >= -0.2) & (arr <= 1.0))
    arr.attrs = {**raw.attrs, "units": "1"}
    return arr


def _mask_bad_reliability(ndvi: xr.DataArray, reliab: xr.DataArray) -> xr.DataArray:
    """Mask cells where pixel reliability > 1 (worse than 'marginal data').
    Reliability code: 0=good, 1=marginal, 2=snow/ice, 3=cloudy, -1=fill.
    """
    r = reliab.values
    bad = (r > 1) | (r < 0)
    out = ndvi.copy()
    out.values = np.where(bad, np.nan, out.values)
    return out


def open_appeears(source: AppEEARSSource) -> xr.Dataset:
    """Open one or more AppEEARS NetCDFs and return a (time, lat, lon) Dataset
    with a decoded `ndvi` variable. Multi-file inputs are concatenated on time.
    """
    if not source.files:
        raise ValueError(f"open_appeears: no files for region {source.region_slug}")

    datasets = []
    for p in sorted(source.files):
        # Open with decode_times=False so we can decode the Julian-calendar
        # time axis ourselves into datetime64 (xarray refuses to do this
        # automatically and cftime→pandas doesn't work either). All our dates
        # (2000–2026) fall after the Julian/Gregorian divergence era, so a
        # straight "seconds since reference" conversion is correct.
        ds = xr.open_dataset(p, mask_and_scale=True, decode_times=False)
        if "time" in ds.variables and ds["time"].attrs.get("units", "").startswith(
            "seconds since"
        ):
            import re

            m = re.match(
                r"seconds since\s+(\d{4}-\d{2}-\d{2})",
                ds["time"].attrs["units"],
            )
            if m:
                ref = np.datetime64(m.group(1))
                secs = ds["time"].values.astype("int64")
                ds = ds.assign_coords(
                    time=("time", ref + secs * np.timedelta64(1, "s"))
                )
        ndvi_name = _find_var(ds, ["ndvi", "_1_km_monthly_NDVI",
                                    "CMG_0_05_Deg_Monthly_NDVI"])
        reliab_name = _find_var(
            ds, ["pixel_reliability", "_1_km_monthly_pixel_reliability",
                 "CMG_0_05_Deg_Monthly_pixel_reliability"], required=False,
        )
        ndvi = _decode_ndvi(ds[ndvi_name])
        if reliab_name is not None:
            ndvi = _mask_bad_reliability(ndvi, ds[reliab_name])

        # Normalise dim and coord names
        ndvi = ndvi.rename({
            d: new for d, new in [
                ("lat", "lat"), ("latitude", "lat"),
                ("lon", "lon"), ("longitude", "lon"),
            ] if d in ndvi.dims
        })

        if "time" not in ndvi.dims and "time" not in ndvi.coords:
            # single-timestep file: add the coord
            raise ValueError(f"{p.name}: no time coordinate — not a valid AppEEARS file")

        datasets.append(ndvi.to_dataset(name="ndvi"))

    combined = xr.concat(datasets, dim="time").sortby("time") \
        if len(datasets) > 1 else datasets[0]
    combined.attrs = {
        "region_slug": source.region_slug,
        "region_name": source.region_name,
        "source_files": [p.name for p in source.files],
    }
    return combined


def _find_var(ds: xr.Dataset, candidates: list[str], *, required: bool = True) -> str | None:
    for c in candidates:
        if c in ds.variables:
            return c
    if required:
        raise KeyError(f"none of the expected variables found; looked for {candidates}, "
                       f"have {list(ds.variables)}")
    return None


def gather_region_files(root: Path, region_slug: str) -> AppEEARSSource:
    """Find all .nc files under `root/<region_slug>/` (recursive one level)."""
    dir_ = root / region_slug
    if not dir_.exists():
        return AppEEARSSource(region_slug=region_slug, region_name=region_slug, files=[])
    return AppEEARSSource(
        region_slug=region_slug,
        region_name=region_slug,
        files=sorted(dir_.glob("*.nc")),
    )
