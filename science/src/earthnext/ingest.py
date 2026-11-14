"""Ingest for the locked dataset only: MOD13C2 v061 (MOD/Terra Monthly NDVI CMG 0.05°).

Stage 2 scope:
  - Open a single MOD13C2 HDF-EOS granule (or a pre-staged NetCDF test fixture).
  - Subset to a lat/lon bounding box.
  - Decode fill values to NaN and apply the NDVI scale factor (0.0001).
  - Return an xarray.Dataset with coords (time, lat, lon) and variable `ndvi`.

Reading backend selection: MOD13C2 is distributed as HDF-EOS (HDF4). On Windows
we try pyhdf first (lightweight, pip-installable); callers get a clear error if
neither pyhdf nor a fallback is available.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

NDVI_FILL = -3000  # MOD13C2 NDVI fill sentinel (int16 storage)
NDVI_SCALE = 0.0001  # scale factor per MOD13 User Guide
NDVI_VALID_MIN = -2000  # per MOD13 spec
NDVI_VALID_MAX = 10000
NDVI_SUBDATASET = "CMG 0.05 Deg Monthly NDVI"


@dataclass(frozen=True)
class BBox:
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.min_lat, self.max_lat, self.min_lon, self.max_lon)


def _mod13c2_time_from_filename(path: Path) -> np.datetime64:
    """MOD13C2.AYYYYDDD...hdf — parse AYYYYDDD into a month midpoint."""
    stem = path.stem
    for part in stem.split("."):
        if part.startswith("A") and len(part) == 8 and part[1:].isdigit():
            year = int(part[1:5])
            doy = int(part[5:8])
            dt = datetime(year, 1, 1) + pd.Timedelta(days=doy - 1)
            return np.datetime64(dt.replace(day=15), "ns")
    raise ValueError(f"could not parse MOD13C2 date from filename: {path.name}")


def _open_mod13c2_hdf(path: Path) -> xr.Dataset:
    """Open one MOD13C2 .hdf file using pyhdf. Returns a Dataset with lat/lon coords."""
    try:
        from pyhdf.SD import SD, SDC  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            "pyhdf is required to read MOD13C2 HDF-EOS files. "
            "Install with: pip install pyhdf"
        ) from e

    sd = SD(str(path), SDC.READ)
    try:
        ds_hdf = sd.select(NDVI_SUBDATASET)
        data = ds_hdf.get().astype(np.int32)
        ds_hdf.attributes()
        ds_hdf.endaccess()
    finally:
        sd.end()

    ny, nx = data.shape
    # MOD13C2 CMG is a global 0.05° grid: 7200 cols × 3600 rows, center-of-pixel coords.
    lat = 90.0 - (np.arange(ny) + 0.5) * (180.0 / ny)
    lon = -180.0 + (np.arange(nx) + 0.5) * (360.0 / nx)

    arr = data.astype(np.float32)
    arr[arr == NDVI_FILL] = np.nan
    arr[(arr < NDVI_VALID_MIN) | (arr > NDVI_VALID_MAX)] = np.nan
    arr *= NDVI_SCALE

    t = _mod13c2_time_from_filename(path)

    return xr.Dataset(
        data_vars={
            "ndvi": (("time", "lat", "lon"), arr[np.newaxis, :, :], {
                "units": "1",
                "long_name": "Normalized Difference Vegetation Index (monthly mean)",
                "valid_range": [-0.2, 1.0],
                "source_subdataset": NDVI_SUBDATASET,
                "scale_applied": NDVI_SCALE,
                "fill_value_original": NDVI_FILL,
            }),
        },
        coords={
            "time": ("time", [t]),
            "lat": ("lat", lat.astype(np.float32), {"units": "degrees_north"}),
            "lon": ("lon", lon.astype(np.float32), {"units": "degrees_east"}),
        },
        attrs={"source_file": path.name, "product": "MOD13C2.061"},
    )


def _open_netcdf_fixture(path: Path) -> xr.Dataset:
    """Fallback opener for the SYNTHETIC test fixture (NetCDF, not HDF4)."""
    return xr.open_dataset(path)


def open_one(path: str | Path) -> xr.Dataset:
    """Open one MOD13C2 .hdf or a .nc test fixture; dispatches on suffix."""
    p = Path(path)
    if p.suffix.lower() == ".hdf":
        return _open_mod13c2_hdf(p)
    if p.suffix.lower() in {".nc", ".nc4", ".cdf"}:
        return _open_netcdf_fixture(p)
    raise ValueError(f"unsupported file extension: {p.suffix}")


def subset_bbox(ds: xr.Dataset, bbox: BBox) -> xr.Dataset:
    """Spatial subset to the bounding box (inclusive). Does not reorder lat."""
    lat_desc = ds["lat"].values[0] > ds["lat"].values[-1]
    if lat_desc:
        lat_slice = slice(bbox.max_lat, bbox.min_lat)
    else:
        lat_slice = slice(bbox.min_lat, bbox.max_lat)
    return ds.sel(lat=lat_slice, lon=slice(bbox.min_lon, bbox.max_lon))


def ingest_files(paths: list[Path], bbox: BBox) -> xr.Dataset:
    """Open N files, subset each to bbox, concat on time, sort time ascending."""
    if not paths:
        raise ValueError("ingest_files: paths is empty")
    parts = [subset_bbox(open_one(p), bbox) for p in paths]
    combined = xr.concat(parts, dim="time")
    return combined.sortby("time")
