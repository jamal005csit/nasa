"""Stage 2 helper: fetch ONE recent MOD13C2 monthly granule for the real-file test.

Strategy:
  1. Load Earthdata credentials from .env.
  2. Search for the most recent available monthly granule (walking back from
     the current month until CMR returns results — product has ~1–2 month lag).
  3. Print the granule summary (dry-run view).
  4. Download the single most recent granule to science/data/raw/MOD13C2/.

Hard safety: refuses to download more than ONE granule or anything larger
than 200 MB. See the two `assert`s below.
"""

from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "science" / "data" / "raw" / "MOD13C2"

MAX_FILES = 1
MAX_BYTES = 200 * 1024 * 1024  # 200 MB hard cap


def load_env() -> None:
    env = ROOT / ".env"
    if not env.exists():
        sys.exit("Missing .env — copy .env.example and fill Earthdata creds.")
    for ln in env.read_text().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#") or "=" not in ln:
            continue
        k, v = ln.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def main() -> int:
    load_env()
    if not os.environ.get("EARTHDATA_USERNAME") or not os.environ.get("EARTHDATA_PASSWORD"):
        sys.exit("EARTHDATA_USERNAME / EARTHDATA_PASSWORD not set")

    import earthaccess

    earthaccess.login(strategy="environment")
    print("logged in to Earthdata.")

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Walk backwards from the start of the current month in 1-month steps.
    today = date.today()
    y, m = today.year, today.month
    results = None
    for _ in range(6):
        m -= 1
        if m == 0:
            m = 12
            y -= 1
        start = f"{y:04d}-{m:02d}-01"
        end_m = m + 1
        end_y = y
        if end_m == 13:
            end_m = 1
            end_y += 1
        end = f"{end_y:04d}-{end_m:02d}-01"
        print(f"searching MOD13C2.061 for {start} .. {end} ...", end=" ")
        results = earthaccess.search_data(
            short_name="MOD13C2", version="061", temporal=(start, end),
        )
        print(f"{len(results)} granule(s)")
        if results:
            break
    if not results:
        sys.exit("no MOD13C2 granules found in the last 6 months — check connectivity.")

    chosen = results[:MAX_FILES]
    # Compute reported byte size from granule metadata (may be approximate).
    total_bytes = 0
    for g in chosen:
        try:
            sz = g.size()  # MB
            total_bytes += int(sz * 1024 * 1024) if sz else 0
        except Exception:
            pass
    print(f"\nabout to download {len(chosen)} granule(s), ~{total_bytes / 1_048_576:.1f} MB")

    assert len(chosen) <= MAX_FILES, f"safety: would download {len(chosen)} > {MAX_FILES}"
    assert total_bytes == 0 or total_bytes <= MAX_BYTES, (
        f"safety: would download {total_bytes} B > {MAX_BYTES} B cap"
    )

    paths = earthaccess.download(chosen, str(RAW_DIR))
    print(f"\nwrote {len(paths)} file(s) under {RAW_DIR}:")
    for p in paths:
        p = Path(p)
        print(f"  {p.name}  ({p.stat().st_size / 1_048_576:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
