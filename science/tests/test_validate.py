"""Unit tests for earthnext.validate against the SYNTHETIC fixture."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import xarray as xr

from earthnext.validate import validate

FIXTURE = Path(__file__).parent / "fixtures" / "synthetic_ndvi.nc"
BBOX = (29.5, 31.5, 30.0, 32.0)  # Nile-Delta-ish


def _ensure_fixture() -> Path:
    if not FIXTURE.exists():
        subprocess.run(
            [sys.executable, str(FIXTURE.parent / "make_synthetic_ndvi.py")],
            check=True,
        )
    return FIXTURE


@pytest.fixture(scope="module")
def ds() -> xr.Dataset:
    p = _ensure_fixture()
    return xr.open_dataset(p)


def test_synthetic_fixture_all_checks_pass(ds: xr.Dataset) -> None:
    report = validate(
        ds,
        dataset_name="SYNTHETIC",
        variable="ndvi",
        expected_units="1",
        bbox=BBOX,
        sentinels=[-3000.0],
    )
    assert report.ok, [f for f in report.findings if f.status == "fail"]
    assert report.n_timestamps == 5
    assert report.n_cells == 5 * 4 * 4
    assert report.n_valid == 5 * 4 * 4 - 2  # two NaNs injected by the fixture
    assert report.missing_pct == pytest.approx(100 * 2 / 80)


def test_wrong_units_fails(ds: xr.Dataset) -> None:
    report = validate(
        ds, dataset_name="SYNTHETIC", variable="ndvi", expected_units="K",
        bbox=BBOX, sentinels=[-3000.0],
    )
    assert not report.ok
    assert any(f.name == "units" and f.status == "fail" for f in report.findings)


def test_spatial_bounds_outside_fails(ds: xr.Dataset) -> None:
    report = validate(
        ds, dataset_name="SYNTHETIC", variable="ndvi", expected_units="1",
        bbox=(-10.0, -5.0, -10.0, -5.0), sentinels=[-3000.0],
    )
    assert any(f.name == "spatial_bounds" and f.status == "fail" for f in report.findings)


def test_sentinel_still_present_fails() -> None:
    # Build a tiny ds where the fill sentinel was NOT converted to NaN
    import numpy as np
    bad = xr.Dataset(
        data_vars={"ndvi": (("time", "lat", "lon"),
                            np.array([[[-3000.0]]], dtype=np.float32),
                            {"units": "1"})},
        coords={"time": [np.datetime64("2020-01-15")], "lat": [30.0], "lon": [31.0]},
    )
    report = validate(
        bad, dataset_name="BAD", variable="ndvi", expected_units="1",
        bbox=BBOX, sentinels=[-3000.0],
    )
    assert any(
        f.name == "no_sentinel_fills" and f.status == "fail" for f in report.findings
    )
