# EARTH//NEXT — Sources and Attribution

Every third-party asset used anywhere in this project, with its license and
how it's used. This file is the source of truth for the **References** field
of the NASA Space Apps project submission form.

Rows added as the project grows. If an asset is here but no longer used, mark
it *(removed)* with the date rather than deleting the row.

---

## 1. Data

| Source | Short-name / version | How we use it | License / citation |
|---|---|---|---|
| **MODIS/Terra Vegetation Indices Monthly L3 Global 1 km SIN Grid** | MOD13A3.061 | **Primary dataset.** NDVI time series + pixel reliability for the Nile Delta and Sahara Interior regions, 2000-02 → 2026-09, requested via AppEEARS Area Sample. | NASA free use. Cite as: Didan, K. (2021). *MODIS/Terra Vegetation Indices Monthly L3 Global 1km SIN Grid V061.* NASA LP DAAC. https://doi.org/10.5067/MODIS/MOD13A3.061 |
| MODIS/Terra Vegetation Indices Monthly L3 Global 0.05° CMG | MOD13C2.061 | One granule (A2026274) downloaded via `earthaccess` to prove the Stage-2 HDF-EOS ingest path works on real NASA data. Not used in the shipped UI. | NASA free use. Cite as: Didan, K. (2021). *MODIS/Terra Vegetation Indices Monthly L3 Global 0.05Deg CMG V061.* NASA LP DAAC. https://doi.org/10.5067/MODIS/MOD13C2.061 |
| NASA AppEEARS (Application for Extracting and Exploring Analysis Ready Samples) | n/a | Service used to retrieve the pre-subsetted MOD13A3 NetCDF for our two region polygons. | NASA / LP DAAC service. AppEEARS Team (2026). *AppEEARS.* https://appeears.earthdatacloud.nasa.gov |

## 2. Fonts

| Font | Where used | License |
|---|---|---|
| Space Grotesk | UI text (`tailwind.config.ts` font-sans) | SIL Open Font License 1.1. Designer: Florian Karsten. https://fonts.google.com/specimen/Space+Grotesk |
| IBM Plex Mono | Numbers (`tabular-nums`) and monospace UI | SIL Open Font License 1.1. IBM. https://fonts.google.com/specimen/IBM+Plex+Mono |

## 3. Python packages (science/)

Listed when the package first enters the project. Versions pinned via `pip freeze` at Stage 11.

| Package | Role | License |
|---|---|---|
| numpy | arrays, math | BSD-3-Clause |
| pandas | time-indexed series, aggregation | BSD-3-Clause |
| xarray | labeled N-D arrays, NetCDF I/O | Apache-2.0 |
| scipy | `theilslopes`, stats | BSD-3-Clause |
| statsmodels | BH FDR via `multipletests` | BSD-3-Clause |
| pymannkendall | Mann-Kendall + Hamed-Rao + prewhitened variants | MIT |
| netCDF4 | NetCDF-4 I/O backend for xarray | MIT |
| pyhdf | HDF-EOS (HDF4) reader for the Stage-2 MOD13C2 ingest proof | MIT |
| pydantic | Provenance + ValidationReport models | MIT |
| pyyaml | read `science/config/analysis.yaml` | MIT |
| earthaccess | NASA Earthdata search + download | MIT |
| python-dateutil | date arithmetic | Apache-2.0 / BSD-3-Clause |
| pytest | test runner | MIT |
| ruff | linter | MIT |

## 4. JavaScript / web packages (web/)

| Package | Role | License |
|---|---|---|
| next | React App Router + static export | MIT |
| react, react-dom | UI runtime | MIT |
| tailwindcss | design-token-driven styling | MIT |
| postcss, autoprefixer | CSS pipeline | MIT |
| typescript | types | Apache-2.0 |
| vitest | test runner | MIT |
| @testing-library/react, jest-dom | DOM assertions in tests | MIT |
| @vitejs/plugin-react | React support in vitest | MIT |
| jsdom | DOM for vitest | MIT |

## 5. Super Intelligence (SI) tools

Mandatory disclosure per Participant FAQs p.12 ("Executive Order of 2026-09-29 renames AI to Super Intelligence (SI); each team's project submission must include a description of how SI tools were used").

| Tool | Provider | What it was used for | How it was supervised |
|---|---|---|---|
| Claude Opus 4.7 (`claude-opus-4-7`) | Anthropic | Drafted docs, scaffolded the project, wrote the stats engine, generated test cases against known synthetic series. Nothing SI-generated is shown in the UI; the Decision Brief is deterministic template + JSON fields only. | A human reviewed and approved each stage gate. SI never ran destructive operations without explicit approval. Full session log in `docs/ai-use-log.md`. Public-facing summary in `docs/ai-use-disclosure.md`. |

## 6. Images, icons, textures, sounds

| Asset | Where used | License / source |
|---|---|---|
| Blue Marble Earth texture (`web/public/textures/earth.jpg`, ~1.4 MB) | Mission Control 3D globe | NASA Visible Earth public-domain imagery, served via the three-globe examples repository (BSD-3-Clause). Downloaded once by `scripts/fetch_earth_texture.py`, bundled locally so the demo renders offline per SPEC §4. Attribution: NASA Earth Observatory / NASA Visible Earth. |

## 7. Pre-existing scratch files inside this repo

Kept for reference; **not shipped** in the deployed build. Each is listed because it exists in the repo even though nothing in the SPEC pipeline depends on it.

| File | Status | Note |
|---|---|---|
| `legacy_mockup/index.html` | Pre-existing design prototype, moved out of repo root 2026-11-14 so it stops getting served by accident. | Hardcoded regional numbers; uses NASA POWER + FIRMS + EONET via `server.js`. Not spec-aligned. May inform the Stage 10 design polish pass. |
| `legacy_mockup/server.js` | Pre-existing Express proxy for the prototype. | Not deployed; the shipped app has no backend. |
| `nasa_download.py` | Pre-existing Earthdata downloader (all four candidate datasets). | Superseded by `scripts/fetch_one_mod13c2.py` for the Stage-2 single-file fetch. Credentials now loaded from `.env`. |
