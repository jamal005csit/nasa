import os
import json
import traceback
from pathlib import Path
import earthaccess

# Embed your credentials here to skip the interactive prompt
os.environ["EARTHDATA_USERNAME"] = "jamal005"
os.environ["EARTHDATA_PASSWORD"] = "-_R/ywng9^C*.WW"

DRY_RUN = False
START, END = "2020-01-01", "2026-06-05"
OUT_DIR = Path("nasa_data")

DATASETS = [
    ("M2TMNXSLV", "5.12.4", "MERRA-2 monthly T2M"),
    ("GPM_3IMERGM", "07", "IMERG monthly precipitation"),
    ("MOD13C2", "061", "MODIS Terra monthly NDVI"),
    ("GLDAS_NOAH025_M", "2.1", "GLDAS Noah monthly soil moisture / ET"),
]

def main():
    # Use the environment strategy to pick up the embedded credentials
    earthaccess.login(strategy="environment")
    OUT_DIR.mkdir(exist_ok=True)
    report = {}

    for short_name, version, label in DATASETS:
        key = f"{short_name} ({label})"
        try:
            results = earthaccess.search_data(
                short_name=short_name, version=version, temporal=(START, END)
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