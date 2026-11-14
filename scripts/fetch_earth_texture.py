"""Download a Blue-Marble-style Earth texture for the Mission Control globe.

Source: the three-globe examples repo (BSD license). ~1.2 MB. Bundled locally
under web/public/textures/earth.jpg so the demo renders offline per SPEC §4.
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "web" / "public" / "textures" / "earth.jpg"

URL = "https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists() and OUT.stat().st_size > 100_000:
        print(f"already present: {OUT} ({OUT.stat().st_size // 1024} KB)")
        return
    print(f"downloading {URL} -> {OUT.relative_to(ROOT)}")
    req = urllib.request.Request(URL, headers={"User-Agent": "earthnext/0.0.0"})
    with urllib.request.urlopen(req, timeout=30) as r, open(OUT, "wb") as f:
        f.write(r.read())
    print(f"wrote {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
