"""End-to-end pipeline for `npm run process`:
   AppEEARS/DEMO NetCDFs → regional annual series → trend → JSON exports.

Prefers real AppEEARS data when present; falls back to DEMO files generated
by `scripts/make_demo_data.py`.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

# Windows default encoding (cp1252) chokes on Greek letters etc.
# Force UTF-8 on stdout so we can print "ρ" and "≥" without a UnicodeEncodeError.
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)

import yaml

from earthnext.appeears import gather_region_files, open_appeears
from earthnext.export import build_region_export, build_summary, write_all
from earthnext.schemas import BBox, RegionMeta, SourceLabel

ROOT = Path(__file__).resolve().parents[3]
APPEEARS_ROOT = ROOT / "science" / "data" / "raw" / "appeears"
CONFIG_PATH = ROOT / "science" / "config" / "analysis.yaml"
WEB_DATA_DIR = ROOT / "web" / "public" / "data"

DATASET_SHORT_NAME = "MOD13A3"
DATASET_VERSION = "061"
DATASET_SOURCE_URL = "https://lpdaac.usgs.gov/products/mod13a3v061/"
VARIABLE = "ndvi"

REGIONS = [
    RegionMeta(slug="nile_delta", name="Nile Delta",
               bbox=BBox(min_lat=29.5, max_lat=31.5, min_lon=30.0, max_lon=32.0)),
    RegionMeta(slug="sahara_interior", name="Sahara Interior (Western Desert, Egypt)",
               bbox=BBox(min_lat=24.0, max_lat=26.0, min_lon=26.0, max_lon=28.0)),
]


def _banner(s: str) -> None:
    print(f"\n{'=' * 70}\n  {s}\n{'=' * 70}")


def _is_demo(p) -> bool:
    return p.name.startswith("DEMO_")


def _detect_source() -> SourceLabel:
    """Source = 'NASA' iff EVERY region has at least one non-DEMO file.
    Otherwise 'DEMO'. Keeps the UI consistent while partial AppEEARS results
    trickle in (one region real, one region still DEMO → whole app stays DEMO).
    """
    per_region = {r.slug: gather_region_files(APPEEARS_ROOT, r.slug) for r in REGIONS}
    for slug, src in per_region.items():
        if not src.files:
            raise SystemExit(
                f"No NetCDF files under {APPEEARS_ROOT}/{slug}/.\n"
                "Either place AppEEARS output there, or run:\n"
                "  python scripts/make_demo_data.py"
            )
    all_regions_have_real = all(
        any(not _is_demo(p) for p in src.files) for src in per_region.values()
    )
    if all_regions_have_real:
        counts = ", ".join(
            f"{slug}={sum(1 for p in src.files if not _is_demo(p))}"
            for slug, src in per_region.items()
        )
        return SourceLabel(
            kind="NASA",
            note=f"MOD13A3.061 via NASA AppEEARS ({counts} monthly files).",
        )
    return SourceLabel(
        kind="DEMO",
        note="Illustrative — not NASA data. Awaiting AppEEARS MOD13A3.061 subset.",
    )


def _filter_by_source(src, source_kind: str):
    """Keep only files matching the chosen source kind so DEMO + real can safely
    coexist in the same folder during the swap-in window."""
    from earthnext.appeears import AppEEARSSource
    if source_kind == "DEMO":
        files = [p for p in src.files if _is_demo(p)]
    else:
        files = [p for p in src.files if not _is_demo(p)]
    return AppEEARSSource(region_slug=src.region_slug, region_name=src.region_name,
                          files=files)


def main() -> int:
    _banner("EARTH//NEXT Stage 4 export")
    source = _detect_source()
    print(f"  source: {source.kind} — {source.note}")

    config = yaml.safe_load(CONFIG_PATH.read_text())
    config["resolution_note"] = "MOD13A3 1 km monthly SIN (AppEEARS geographic re-grid)"

    region_exports = []
    for rmeta in REGIONS:
        src = _filter_by_source(gather_region_files(APPEEARS_ROOT, rmeta.slug), source.kind)
        print(f"\n  region {rmeta.slug}: {len(src.files)} file(s) ({source.kind})")
        ds = open_appeears(src)
        re = build_region_export(
            ds, rmeta,
            source=source,
            dataset_short_name=DATASET_SHORT_NAME,
            dataset_version=DATASET_VERSION,
            dataset_source_url=DATASET_SOURCE_URL,
            variable=VARIABLE,
            config=config,
        )
        region_exports.append(re)
        cov = re.coverage
        print(f"    years with valid annual mean : "
              f"{cov.n_valid_years}/{cov.n_total_years}")
        print(f"    slope / yr                   : {re.trend.slope_per_year:+.5f}  "
              f"(95% CI {re.trend.slope_ci95[0]:+.5f}, "
              f"{re.trend.slope_ci95[1]:+.5f})")
        rho = re.significance.lag1_autocorr
        rho_s = "n/a" if rho is None else f"{rho:+.2f}"
        print(f"    significance                 : {re.significance.p_display}  "
              f"({re.significance.test}, lag-1 rho={rho_s})")
        print(f"    trend direction              : "
              f"{re.significance.trend_direction}")

    summary = build_summary(
        region_exports, source=source,
        dataset_short_name=DATASET_SHORT_NAME,
        dataset_version=DATASET_VERSION,
        variable=VARIABLE,
    )

    written = write_all(region_exports, summary, WEB_DATA_DIR)
    _banner("wrote files")
    total_bytes = 0
    for p in written:
        size = p.stat().st_size
        total_bytes += size
        print(f"  {p.relative_to(ROOT).as_posix():<45} {size / 1024:>7.1f} KB")
    print(f"  {'TOTAL':<45} {total_bytes / 1024:>7.1f} KB")

    _banner("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
