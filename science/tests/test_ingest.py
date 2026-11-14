"""Ingest tests. Synthetic fixture always runs; the real-file test skips cleanly
if no MOD13C2 .hdf has been downloaded yet.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from earthnext.ingest import BBox, ingest_files, open_one

FIXTURE = Path(__file__).parent / "fixtures" / "synthetic_ndvi.nc"
RAW_DIR = Path(__file__).parent.parent / "data" / "raw" / "MOD13C2"


def _ensure_fixture() -> Path:
    if not FIXTURE.exists():
        subprocess.run(
            [sys.executable, str(FIXTURE.parent / "make_synthetic_ndvi.py")],
            check=True,
        )
    return FIXTURE


def test_open_synthetic_fixture() -> None:
    ds = open_one(_ensure_fixture())
    assert "ndvi" in ds
    assert ds["ndvi"].dims == ("time", "lat", "lon")


def test_bbox_subset_on_synthetic_fixture() -> None:
    ds = open_one(_ensure_fixture())
    sub = ingest_files([_ensure_fixture()], BBox(30.0, 31.0, 30.5, 31.5))
    assert sub["ndvi"].shape[1] <= ds["ndvi"].shape[1]
    assert sub["ndvi"].shape[2] <= ds["ndvi"].shape[2]
    assert set(sub["ndvi"].dims) == {"time", "lat", "lon"}


def _find_real_mod13c2() -> Path | None:
    if not RAW_DIR.exists():
        return None
    hits = sorted(RAW_DIR.glob("MOD13C2.*.hdf"))
    return hits[0] if hits else None


@pytest.mark.skipif(_find_real_mod13c2() is None,
                    reason="no real MOD13C2 .hdf present yet (Stage 2 download step)")
def test_real_mod13c2_file_metadata() -> None:
    """Reads the metadata of ONE real MOD13C2 granule and checks the shape of
    what came back. This is the SPEC Stage-2 'read the real file's metadata' test.
    """
    path = _find_real_mod13c2()
    assert path is not None
    ds = open_one(path)
    assert "ndvi" in ds
    assert ds["ndvi"].dims == ("time", "lat", "lon")
    # Global CMG grid is 7200×3600
    assert ds.sizes["lat"] == 3600
    assert ds.sizes["lon"] == 7200
    assert ds["lat"].values[0] > ds["lat"].values[-1]  # lat descends in MODIS CMG
    assert float(ds["lat"].values[0]) == pytest.approx(89.975, abs=1e-3)
    assert float(ds["lon"].values[0]) == pytest.approx(-179.975, abs=1e-3)
    # Scale factor must have been applied -> values in [-0.2, 1.0] range (or NaN)
    import numpy as np
    arr = ds["ndvi"].values
    valid = arr[~np.isnan(arr)]
    assert valid.min() >= -0.2 - 1e-6
    assert valid.max() <= 1.0 + 1e-6
