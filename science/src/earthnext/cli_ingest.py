"""`npm run process` entry point for Stage 2: validate the ingest pipeline on
whatever MOD13C2 .hdf files are present under science/data/raw/MOD13C2/.

Falls back to the SYNTHETIC fixture (with a loud banner) when no real files are
present so the command still prints a real validation report early on.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from earthnext.ingest import BBox, ingest_files
from earthnext.provenance import (
    BoundingBox,
    Provenance,
    git_commit,
    hash_config,
    library_versions,
    now_utc_iso,
    sha256_file,
)
from earthnext.validate import validate

ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "science" / "data" / "raw" / "MOD13C2"
PROCESSED_DIR = ROOT / "science" / "data" / "processed"
FIXTURE = ROOT / "science" / "tests" / "fixtures" / "synthetic_ndvi.nc"

# Locked Stage-0 regions
NILE_DELTA = BBox(min_lat=29.5, max_lat=31.5, min_lon=30.0, max_lon=32.0)
SAHARA = BBox(min_lat=24.0, max_lat=26.0, min_lon=26.0, max_lon=28.0)


def _print_banner(msg: str) -> None:
    print(f"\n{'='*70}\n  {msg}\n{'='*70}")


def _ensure_fixture() -> Path:
    if not FIXTURE.exists():
        subprocess.run([sys.executable, str(FIXTURE.parent / "make_synthetic_ndvi.py")],
                       check=True)
    return FIXTURE


def _format_report(label: str, report) -> None:
    print(f"\n  region: {label}")
    print(f"    timestamps        : {report.n_timestamps}")
    print(f"    cells (total)     : {report.n_cells}")
    print(f"    cells (valid)     : {report.n_valid}")
    print(f"    missing %         : {report.missing_pct:.2f}")
    print(f"    overall ok        : {report.ok}")
    for f in report.findings:
        mark = {"pass": "OK", "fail": "!!", "warn": "~~", "skip": "--"}[f.status]
        print(f"    [{mark}] {f.name:<24} {f.detail}")


def main() -> int:
    _print_banner("EARTH//NEXT Stage 2 ingest check")

    hdf_files = sorted(RAW_DIR.glob("MOD13C2.*.hdf")) if RAW_DIR.exists() else []

    if hdf_files:
        source = "REAL (MOD13C2.061)"
        files = hdf_files
        dataset_name = "MOD13C2.061"
        expected_units = "1"
        time_range_hint = (files[0].name, files[-1].name)
    else:
        source = "SYNTHETIC fixture (no real MOD13C2 .hdf under science/data/raw/)"
        files = [_ensure_fixture()]
        dataset_name = "SYNTHETIC-MOD13C2"
        expected_units = "1"
        time_range_hint = ("fixture", "fixture")

    print(f"  source     : {source}")
    print(f"  file count : {len(files)}")
    print(f"  first      : {files[0].name}")
    print(f"  last       : {files[-1].name}")

    for label, bbox in [("Nile Delta", NILE_DELTA), ("Sahara Interior", SAHARA)]:
        try:
            ds = ingest_files(files, bbox)
        except Exception as e:
            print(f"\n  region {label}: INGEST FAILED: {type(e).__name__}: {e}")
            continue

        report = validate(
            ds,
            dataset_name=dataset_name,
            variable="ndvi",
            expected_units=expected_units,
            bbox=bbox.as_tuple(),
            sentinels=[-3000.0],
        )
        _format_report(label, report)

        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        # Save the validation report + provenance per region
        prov = Provenance(
            dataset=dataset_name,
            source_url="https://lpdaac.usgs.gov/products/mod13c2v061/",
            variable="ndvi",
            units="1",
            time_range=time_range_hint,
            spatial_extent=BoundingBox(
                min_lat=bbox.min_lat, max_lat=bbox.max_lat,
                min_lon=bbox.min_lon, max_lon=bbox.max_lon,
            ),
            resolution="0.05deg CMG (monthly)",
            filters_applied=["fill(-3000)->NaN", "scale*0.0001", f"bbox subset {bbox.as_tuple()}"],
            n_valid=report.n_valid,
            missing_pct=report.missing_pct,
            script_commit=git_commit(ROOT),
            config_hash=hash_config({"bbox": bbox.as_tuple(), "variable": "ndvi"}),
            data_checksum=sha256_file(files[0]) if files[0].exists() else "n/a",
            library_versions=library_versions(
                ["numpy", "xarray", "pandas", "scipy", "pyhdf", "pymannkendall"]
            ),
            generated_at=now_utc_iso(),
        )
        label_slug = label.lower().replace(" ", "_")
        out_json = PROCESSED_DIR / f"ingest_report.{label_slug}.json"
        payload = {
            "provenance": prov.model_dump(),
            "report": report.model_dump(),
        }
        out_json.write_text(json.dumps(payload, indent=2, default=str))
        print(f"    written  : {out_json.relative_to(ROOT)}")

    _print_banner("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
