"""Generate DEMO AppEEARS-style NDVI NetCDFs for the two locked regions.

Purpose: unblock Stages 4+ while real AppEEARS data is still processing.

Every file produced here is clearly SYNTHETIC. The exported JSON that downstream
code produces will carry `source.kind = "DEMO"` and the UI will show a visible
"DEMO DATA" banner. When real AppEEARS NetCDFs land under
`science/data/raw/appeears/<region>/`, delete these files and re-run the pipeline.
Nothing in code assumes the DEMO data is real.

Deterministic (seeded). Parameters chosen to be visually plausible:
  - Nile Delta: baseline NDVI ~0.55, slight positive trend (~+0.0015/yr),
    strong seasonal cycle, ~2% months missing.
  - Sahara:     baseline NDVI ~0.08, essentially flat trend (~+0.0001/yr),
    weak seasonal cycle, <1% missing.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

ROOT = Path(__file__).resolve().parents[1]
DEMO_ROOT = ROOT / "science" / "data" / "raw" / "appeears"

START = "2000-02-01"
END = "2026-09-30"
GRID = 20   # 20x20 cells per region (tiny, fast; real AppEEARS = ~200x200 at 1km)


@dataclass(frozen=True)
class DemoRegion:
    slug: str
    name: str
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float
    baseline: float      # typical NDVI
    slope_per_year: float
    seasonal_amp: float
    noise_sd: float
    missing_pct: float


DEMO_REGIONS = [
    DemoRegion("nile_delta", "Nile Delta",
               29.5, 31.5, 30.0, 32.0,
               baseline=0.55, slope_per_year=0.0015,
               seasonal_amp=0.08, noise_sd=0.03, missing_pct=2.0),
    DemoRegion("sahara_interior", "Sahara Interior (Western Desert, Egypt)",
               24.0, 26.0, 26.0, 28.0,
               baseline=0.08, slope_per_year=0.0001,
               seasonal_amp=0.015, noise_sd=0.008, missing_pct=0.5),
]


def build_one(region: DemoRegion, seed: int) -> xr.Dataset:
    rng = np.random.default_rng(seed)
    times = pd.date_range(START, END, freq="MS")
    lats = np.linspace(region.max_lat - 0.05, region.min_lat + 0.05, GRID, dtype=np.float32)
    lons = np.linspace(region.min_lon + 0.05, region.max_lon - 0.05, GRID, dtype=np.float32)

    years_float = (times - pd.Timestamp("2000-01-01")).days / 365.25
    trend = region.slope_per_year * years_float.values                       # (T,)
    seasonal = region.seasonal_amp * np.sin(2 * np.pi * np.arange(len(times)) / 12.0)  # (T,)
    ndvi_time = region.baseline + trend + seasonal                           # (T,)

    # Per-cell spatial variation (small) + per-sample noise
    field = (ndvi_time[:, None, None]
             + 0.02 * rng.standard_normal((1, GRID, GRID))
             + region.noise_sd * rng.standard_normal((len(times), GRID, GRID)))
    field = np.clip(field, -0.2, 1.0).astype(np.float32)

    # Punch missing months (whole month -> NaN everywhere for that time)
    n_missing = int(round(len(times) * region.missing_pct / 100))
    missing_idx = rng.choice(len(times), size=n_missing, replace=False)
    field[missing_idx, :, :] = np.nan

    # Encode back to int16 with -3000 fill + scale 1e-4, to match the real
    # AppEEARS NetCDF shape exactly.
    encoded = np.where(np.isnan(field), -3000, np.round(field / 0.0001)).astype(np.int16)

    ds = xr.Dataset(
        data_vars={
            "ndvi": (("time", "lat", "lon"), encoded, {
                "long_name": f"DEMO NDVI for {region.name} (SYNTHETIC)",
                "scale_factor": 0.0001,
                "_FillValue": np.int16(-3000),
                "valid_range": [np.int16(-2000), np.int16(10000)],
                "note": "SYNTHETIC. Not NASA data. Replace with AppEEARS output.",
            }),
            "pixel_reliability": (("time", "lat", "lon"),
                                   np.zeros_like(encoded, dtype=np.int8),
                                   {"long_name": "all cells marked reliable=0 (good)"}),
        },
        coords={
            "time": ("time", times.values),
            "lat": ("lat", lats, {"units": "degrees_north"}),
            "lon": ("lon", lons, {"units": "degrees_east"}),
        },
        attrs={
            "source": "SYNTHETIC — EARTH//NEXT DEMO generator",
            "region_slug": region.slug,
            "region_name": region.name,
            "disclaimer": "Illustrative — not NASA data.",
        },
    )
    return ds


def main() -> None:
    DEMO_ROOT.mkdir(parents=True, exist_ok=True)
    for i, r in enumerate(DEMO_REGIONS):
        out_dir = DEMO_ROOT / r.slug
        out_dir.mkdir(exist_ok=True)
        out = out_dir / f"DEMO_{r.slug}_2000_2026.nc"
        ds = build_one(r, seed=42 + i)
        encoding = {
            "ndvi": {"zlib": True, "complevel": 4},
            "pixel_reliability": {"zlib": True, "complevel": 4},
        }
        ds.to_netcdf(out, encoding=encoding)
        print(f"wrote {out.relative_to(ROOT)}  ({out.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
