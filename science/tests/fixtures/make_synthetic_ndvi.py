"""Generate a tiny SYNTHETIC NDVI NetCDF fixture for unit tests. Deterministic.

Output mimics the POST-ingest structure of MOD13C2 (variable name, dims, units,
scale, NaN-filled gaps) so that validate.py can be tested without real NASA data.
Not a real NASA file. Not for analysis. Not for the UI.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import xarray as xr

HERE = Path(__file__).parent
OUT = HERE / "synthetic_ndvi.nc"


def build() -> xr.Dataset:
    rng = np.random.default_rng(seed=42)

    # 5 monthly timestamps, tiny 4x4 grid roughly placed over the Nile Delta
    time = np.array(
        ["2020-06-15", "2020-07-15", "2020-08-15", "2020-09-15", "2020-10-15"],
        dtype="datetime64[ns]",
    )
    lat = np.linspace(31.25, 29.75, 4, dtype=np.float32)   # descending, like MODIS CMG
    lon = np.linspace(30.25, 31.75, 4, dtype=np.float32)   # ascending

    ndvi = 0.55 + 0.05 * rng.standard_normal((len(time), len(lat), len(lon)))
    ndvi = ndvi.astype(np.float32)

    # Inject two deliberate NaN gaps to exercise the missing% check.
    ndvi[0, 0, 0] = np.nan
    ndvi[3, 2, 1] = np.nan

    ds = xr.Dataset(
        data_vars={
            "ndvi": (("time", "lat", "lon"), ndvi, {
                "units": "1",
                "long_name": "SYNTHETIC NDVI (test fixture, NOT NASA data)",
                "scale_applied": 0.0001,
                "fill_value_original": -3000,
            }),
        },
        coords={
            "time": ("time", time),
            "lat": ("lat", lat, {"units": "degrees_north"}),
            "lon": ("lon", lon, {"units": "degrees_east"}),
        },
        attrs={"source": "SYNTHETIC test fixture", "product": "MOD13C2.061 (mimicked)"},
    )
    return ds


if __name__ == "__main__":
    ds = build()
    ds.to_netcdf(OUT)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
