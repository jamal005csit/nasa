"""Unit tests for earthnext.provenance."""

from __future__ import annotations

from pathlib import Path

from earthnext.provenance import (
    BoundingBox,
    Method,
    Provenance,
    hash_config,
    library_versions,
    now_utc_iso,
    sha256_bytes,
    sha256_file,
)


def test_hash_config_is_deterministic_and_order_independent() -> None:
    a = hash_config({"alpha": 0.05, "estimator": "theil_sen"})
    b = hash_config({"estimator": "theil_sen", "alpha": 0.05})
    assert a == b
    assert len(a) == 64


def test_sha256_bytes_known_value() -> None:
    assert sha256_bytes(b"") == (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )


def test_sha256_file_matches_bytes(tmp_path: Path) -> None:
    p = tmp_path / "x.bin"
    p.write_bytes(b"hello world")
    assert sha256_file(p) == sha256_bytes(b"hello world")


def test_library_versions_returns_known_pkg() -> None:
    v = library_versions(["pytest", "no_such_package_xyz"])
    assert v["pytest"] != "unknown"
    assert v["no_such_package_xyz"] == "unknown"


def test_provenance_round_trip() -> None:
    p = Provenance(
        dataset="MOD13C2.061",
        source_url="https://lpdaac.usgs.gov/products/mod13c2v061/",
        variable="ndvi",
        units="1",
        time_range=("2020-06-15", "2020-10-15"),
        spatial_extent=BoundingBox(min_lat=29.5, max_lat=31.5, min_lon=30.0, max_lon=32.0),
        resolution="0.05deg",
        filters_applied=["fill→NaN", "scale×0.0001"],
        method=Method(estimator="theil_sen", test="mann_kendall", fdr_method="bh", alpha=0.05),
        script_commit="deadbee",
        config_hash=hash_config({"a": 1}),
        data_checksum="0" * 64,
        library_versions={"numpy": "2.0.0"},
        generated_at=now_utc_iso(),
    )
    parsed = Provenance.model_validate_json(p.model_dump_json())
    assert parsed.dataset == "MOD13C2.061"
    assert parsed.method.estimator == "theil_sen"
