import os
import json
import traceback
from pathlib import Path
import earthaccess

# Load credentials from .env (see .env.example). Never commit .env.
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _k, _v = _line.split("=", 1)
        os.environ.setdefault(_k.strip(), _v.strip())

if not os.environ.get("EARTHDATA_USERNAME") or not os.environ.get("EARTHDATA_PASSWORD"):
    raise SystemExit(
        "Missing EARTHDATA_USERNAME / EARTHDATA_PASSWORD. "
        "Copy .env.example to .env and fill in your credentials."
    )

# Flip to True to list granule counts WITHOUT downloading.
# Recommended for the first run so you see how big the pull will be.
DRY_RUN = True
END = "2026-09-30"  # monthly products lag ~1-4 months; this is a safe recent cutoff
OUT_DIR = Path("nasa_data")

# Per-dataset earliest start (full available record). Stage 0 will pick ONE of
# these as the locked variable; the others can then be removed to save disk.
DATASETS = [
    ("M2TMNXSLV",       "5.12.4", "1980-01-01", "MERRA-2 monthly T2M"),
    ("GPM_3IMERGM",     "07",     "2000-06-01", "IMERG monthly precipitation"),
    ("MOD13C2",         "061",    "2000-02-01", "MODIS Terra monthly NDVI"),
    ("GLDAS_NOAH025_M", "2.1",    "2000-01-01", "GLDAS Noah monthly soil moisture / ET"),
]

def main():
    # Use the environment strategy to pick up the embedded credentials
    earthaccess.login(strategy="environment")
    OUT_DIR.mkdir(exist_ok=True)
    report = {}

    for short_name, version, start, label in DATASETS:
        key = f"{short_name} ({label})"
        try:
            results = earthaccess.search_data(
                short_name=short_name, version=version, temporal=(start, END)
            )
            n = len(results)
            if n == 0:
                report[key] = "FAILED: no granules found (wrong name/version or no access)"
                continue
            if DRY_RUN:
                report[key] = f"DRY RUN: {n} files found"
                continue
            folder = OUT_DIR / short_name
            folder.mkdir(exist_ok=True)
            files = earthaccess.download(results, str(folder))
            report[key] = f"OK: {len(files)}/{n} files downloaded"
            if len(files) < n:
                report[key] = f"PARTIAL: {len(files)}/{n} files downloaded"
        except Exception as e:
            traceback.print_exc()
            report[key] = f"FAILED: {type(e).__name__}: {e}"

    print("\n===== SUMMARY =====")
    for k, v in report.items():
        print(f"{k}: {v}")
    (OUT_DIR / "download_report.json").write_text(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()