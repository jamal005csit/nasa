"""Provenance record for every analysis result.

SPEC science rule 10 + AGENTS.md "Provenance contract" fix the schema:
`dataset`, `source_url`, `variable`, `units`, `time_range`, `spatial_extent`,
`resolution`, `filters_applied`, `method`, `n_valid`, `missing_pct`, `slope`,
`slope_ci95`, `p`, `q`, `script_commit`, `config_hash`, `data_checksum`,
`library_versions`, `generated_at`.

Stage-2 results fill the ingest-side fields and leave stats fields None;
Stage-3+ fills the rest.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class Method(BaseModel):
    estimator: str | None = None
    test: str | None = None
    fdr_method: str | None = None
    alpha: float | None = None


class BoundingBox(BaseModel):
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float


class Provenance(BaseModel):
    """One-result provenance record. Fields unknown at this stage stay None."""

    dataset: str
    source_url: str
    variable: str
    units: str
    time_range: tuple[str, str]
    spatial_extent: BoundingBox
    resolution: str
    filters_applied: list[str] = Field(default_factory=list)
    method: Method = Field(default_factory=Method)
    n_valid: int | None = None
    missing_pct: float | None = None
    slope: float | None = None
    slope_ci95: tuple[float, float] | None = None
    p: float | None = None
    q: float | None = None
    script_commit: str
    config_hash: str
    data_checksum: str
    library_versions: dict[str, str]
    generated_at: str


def sha256_file(path: str | Path, chunk: int = 1 << 20) -> str:
    """SHA-256 of a file, streamed. Returns hex digest."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_config(cfg: dict[str, Any]) -> str:
    """Deterministic hash of a config dict (sorted JSON)."""
    return sha256_bytes(json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode())


def git_commit(cwd: str | Path | None = None) -> str:
    """Current git HEAD sha or the sentinel 'untracked' if not a git repo."""
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "untracked"


def library_versions(pkgs: list[str]) -> dict[str, str]:
    """Version string for each installed package; 'unknown' if not found."""
    out: dict[str, str] = {}
    for p in pkgs:
        try:
            out[p] = importlib.metadata.version(p)
        except importlib.metadata.PackageNotFoundError:
            out[p] = "unknown"
    return out


def now_utc_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
