"""Stage-4 round-trip tests: every exported JSON validates via pydantic,
and together they tell a self-consistent story (region slugs match, etc.).

The companion TypeScript test (web/src/__tests__/schemas.test.ts) validates
the same files via zod to ensure the two schema languages stay in sync.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from earthnext.schemas import RegionExport, Summary

ROOT = Path(__file__).resolve().parents[2]
WEB_DATA_DIR = ROOT / "web" / "public" / "data"


def _ensure_exports_exist() -> None:
    """Regenerate DEMO exports if they don't exist."""
    missing = [
        WEB_DATA_DIR / "summary.json",
        WEB_DATA_DIR / "regions" / "nile_delta.json",
        WEB_DATA_DIR / "regions" / "sahara_interior.json",
    ]
    if all(p.exists() for p in missing):
        return
    # make DEMO data (idempotent)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "make_demo_data.py")], check=True)
    subprocess.run([sys.executable, "-m", "earthnext.pipeline"], check=True, cwd=ROOT)


@pytest.fixture(scope="module", autouse=True)
def exports_ready() -> None:
    _ensure_exports_exist()


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def test_summary_json_validates() -> None:
    summary = Summary.model_validate(_load(WEB_DATA_DIR / "summary.json"))
    assert summary.source.kind in ("DEMO", "NASA")
    assert len(summary.regions) >= 2
    slugs = {r.slug for r in summary.regions}
    assert summary.featured_finding.region_slug in slugs


@pytest.mark.parametrize("slug", ["nile_delta", "sahara_interior"])
def test_region_json_validates(slug: str) -> None:
    r = RegionExport.model_validate(_load(WEB_DATA_DIR / "regions" / f"{slug}.json"))
    assert r.region.slug == slug
    # Series dimensions line up
    assert len(r.annual.years) == len(r.annual.values)
    assert len(r.annual.years) == len(r.annual.valid_months_per_year)
    # Trend is internally consistent
    assert r.trend.slope_ci95[0] <= r.trend.slope_per_year <= r.trend.slope_ci95[1]
    # p_display matches p per SPEC §3 rule 13
    if r.significance.p < 0.001:
        assert r.significance.p_display == "p < 0.001"
    else:
        assert r.significance.p_display.startswith("p = ")
    # Coverage counts are sane
    assert 0 <= r.coverage.missing_pct <= 100
    assert r.coverage.n_valid_years <= r.coverage.n_total_years


def test_demo_label_is_visible() -> None:
    """If this test fails, the UI will NOT show the DEMO banner — data loss risk."""
    summary = Summary.model_validate(_load(WEB_DATA_DIR / "summary.json"))
    if summary.source.kind == "DEMO":
        assert "not NASA data" in summary.source.note.lower() or \
               "illustrative" in summary.source.note.lower()


def test_featured_region_exists_in_regions_list() -> None:
    summary = Summary.model_validate(_load(WEB_DATA_DIR / "summary.json"))
    slugs = {r.slug for r in summary.regions}
    assert summary.featured_finding.region_slug in slugs


def test_file_sizes_under_cap() -> None:
    """SPEC §4 data-contract: each file < 1-2 MB, hard max 5 MB."""
    for p in WEB_DATA_DIR.rglob("*.json"):
        size_mb = p.stat().st_size / (1024 * 1024)
        assert size_mb < 5.0, f"{p.name} is {size_mb:.2f} MB (>5 MB hard cap)"
