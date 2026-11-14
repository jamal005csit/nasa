# EARTH//NEXT — Stage 0 Resource Audit

**Prepared:** 2026-11-14 (Day 1, local morning). **Revised:** 2026-11-14 (evening) — see §3.3 revision note.
**Scope:** audit of (a) the four candidate NASA datasets staged in [`nasa_download.py`](../nasa_download.py), (b) every requirement and deliverable in `docs/official/`, and (c) what we don't yet know.
**Nothing was downloaded, computed, or claimed from analysis.** Every item below traces to a file in `docs/official/` or to the authoritative dataset landing page cited.

> **Dataset lock update (2026-11-14 evening):** Stage 0 locked MOD13C2.061 (0.05° CMG). At the Stage 3 AppEEARS step we discovered AppEEARS does not serve the CMG product family. The lock was revised to **MOD13A3.061 (1 km monthly SIN grid)** — same variable (NDVI), same monthly cadence, same 2000-02-01 → present record, 5.6× finer spatially. §3.3 of this document has been rewritten to audit MOD13A3; the original MOD13C2 subsection is retained at §3.3-bis as the record of the original research. See also `docs/methodology.md` §1 and `docs/PROJECT_STATE.txt` LOCKED DECISIONS.

---

## 1. Challenge summary (verbatim-in-spirit from `docs/official/challenge description.md`)

- **Title:** Be an Earth System Trend Detective!
- **Theme 2026:** *The Next Frontier*.
- **Problem statement (paraphrased):** satellite instruments and global models observe many Earth-system variables on land, in the atmosphere, and in the oceans. Trends — directional changes over time — indicate both the processes causing change and the processes responding to it. The challenge has two parts: (i) find variables that are trending, from simple ones (temperature, rainfall) to complex ones (evaporation, streamflow); (ii) analyse trends in particular regions, since most trends are not global.
- **Named example instruments and models:** MODIS, OMI, AIRS, GPM, MERRA-2, GLDAS.
- **Required elements** (all four must be present for "full scope"):
  1. Identify Earth-science variables of interest that can be investigated for potential trends.
  2. Acquire the data variables for a particular region.
  3. Generate and visualise a time series over a period long enough to allow statistical analysis.
  4. Perform a basic statistical analysis: rate of change, and test the trend's significance using methods such as a t-test, Mann-Kendall, or confidence intervals.
- **Audience (optional guidance):** high-school / college students and members of the public with some scientific background; provide simple definitions of variables; cast users as "data detectives".
- **Approach suggestions (optional):** a short Q&A flow to narrow down variable/region; one or two demo examples; SI (see §3) as a search aid; news-article or research-paper context; regional-character hooks (desert, rainforest, tidal estuary, atmosphere above a large city).
- **Data advice:** daily and monthly data are easiest to process at this scope; detecting linear trends is a great starting point; non-significant results are still interesting; non-linear and seasonality-corrected analyses are welcome but not required.

---

## 2. Submission rules, dates, and judging (from `docs/official/judging and awards guide.pdf` and `FAQs.pdf`)

### 2.1 Key dates
| Date | Event |
|---|---|
| 2026-11-14 09:00 local | Hackathon begins (submission form opens) |
| 2026-11-15 11:59 p.m. local | **Project submission deadline** |
| 2026-12-03 | Global Nominees announced |
| 2026-12-17 | Global Finalists + Honorable Mentions announced |
| 2027-01-??? | Global Winners announced |
| 2027-01-26 | Winner's Celebration (virtual) |

### 2.2 Minimum eligibility for Global Judging
- Respond to one official challenge.
- Local Event teams: 1–6 people. Universal Event teams: **2–6 people (minimum 2)**. All team members registered for the same Local Event (or the Universal Event). Team Owner registered with the Local Event.
- **Submit by Nov 15, 11:59 p.m. local time** via the project page on `spaceappschallenge.org`.
- Complete all required fields on the Project Submission page.
- Provide a short demo (either a slide presentation, **7-slide limit** including title/intro; or a **30-second video**).
- Use English in the submission page and in all linked materials; if the Project Demo is spoken in another language, it **must include English subtitles**.
- Tick the originality box: *"I confirm that the submitted project represents my team's original work and that all external resources including code, text and images (even if they are open source or freely available) used in the project are listed in the References field of the project submission form. In creating our solution, my team has not used any copyrighted materials (i.e., music, images, text, etc.) that we don't have permission to use."*
- Tick the T&C box: *"I have read and understand the project submission requirements as contained in the NASA Space Apps Project Submission Guide, and I agree to the Participant Terms and Conditions and Privacy Policy."*
- China funding restriction: teams with Chinese-government, Chinese-owned entity, or Hong Kong/Macau government affiliation undergo an eligibility review before Global Judging advancement.

### 2.3 Judging criteria (five, each 1–5; applied at every level from Local to Executive)
1. **Impact** — reach, effect, inspiration; quality & quantity of benefit.
2. **Creativity** — originality, novel concept, inventive execution.
3. **Validity** — technical / scientific soundness, feasibility, completeness, usability, user-friendliness, refinement.
4. **Relevance** — thorough + direct engagement with the chosen challenge; meaningful NASA data integration as a **core** component, not superficial.
5. **Presentation** — clarity, storytelling, organisation; demo plus full project both evaluated.

### 2.4 Judging phases
- **Phase 1: Local/Universal** — Local judges pick Global Nominees from each Local Event; Universal Event is judged by SMEs.
- **Phase 2: Global Judging** — expert panel reviews all Global Nominees → "Global Finalists" (Dec 17) and "Honorable Mentions".
- **Phase 3: Global Winners** — executive committee from NASA + Space Agency Partners picks one winner per award (10 awards, listed below). Announced early 2027.

### 2.5 Ten Global Awards (project gets at most one)
Best Use of Science · Best Use of Data · Best Use of Technology · Galactic Impact · Best Mission Concept · Most Inspirational · Best Storytelling · Global Connection · Art & Technology · Local Impact.

### 2.6 "Super Intelligence" (SI) use policy — **binding**
Per Executive Order of 2026-09-29, NASA renames "AI/Artificial Intelligence" to "Super Intelligence/SI" throughout challenge materials. SI tools (LLMs, chat assistants, image/video/code generation) **may** be used to accelerate innovation. **Each team's project submission MUST include a description of how SI tools were used in the development of the project** (FAQs p.12). Treat this as a required submission field.

### 2.7 Team formation facts (from `team formation.pdf`)
- One team member creates the team and is "Team Owner"; the Team Owner's Local Event determines where the team is judged in Phase 1.
- A person can be on only one team and may submit a project for only one challenge.
- Universal Event teams **must** have ≥ 2 members for global-judging eligibility; Local Event solo entries (1 person) are fine for Local, but need ≥ 2 to advance globally.
- All projects submitted by 2026-11-15 11:59 p.m. local time.

---

## 3. Dataset audit — the four candidates in `nasa_download.py`

For every row below, the **Source** column links to the authoritative NASA dataset landing page. Fields marked "see §5" are honestly uncertain and parked in Unknowns until verified from those landing pages before the Stage 2 ingest.

### 3.1 MERRA-2 M2TMNXSLV v5.12.4 — monthly single-level atmospheric diagnostics
| Field | Value |
|---|---|
| Full name | MERRA-2 `tavgM_2d_slv_Nx`: 2-D Monthly Mean, Single-Level Diagnostics |
| Short name / version | `M2TMNXSLV` / `5.12.4` |
| Producer | NASA Global Modeling and Assimilation Office (GMAO) |
| Distributor | NASA GES DISC |
| Landing page (source of truth) | https://disc.gsfc.nasa.gov/datasets/M2TMNXSLV_5.12.4/summary |
| Variables we'd likely use | `T2M` (2-metre air temperature). Other included variables: T2MMAX, T2MMIN, QV2M (2-m specific humidity), U10M/V10M (10-m wind), PS (surface pressure), SLP (sea-level pressure), many others |
| Units | T2M in **Kelvin** (confirm) |
| Time coverage | 1980-01-01 → present, monthly means, ~1 month publication lag |
| Spatial resolution | 0.5° latitude × 0.625° longitude, global |
| Format | NetCDF-4, one file per month |
| Approx. per-file size | 35–50 MB (global) |
| Fill value | see §5 |
| Access method | `earthaccess.search_data(short_name="M2TMNXSLV", version="5.12.4", temporal=..., bounding_box=...)` — requires Earthdata login |
| Reanalysis caveat | MERRA-2 is a **reanalysis** (model assimilating observations), not direct instrument retrievals; treat it as a derived product and say so in the UI |
| License | NASA free-use / cite per GES DISC citation statement |

### 3.2 GPM IMERG monthly v07 (GPM_3IMERGM)
| Field | Value |
|---|---|
| Full name | GPM IMERG Final Precipitation L3 Monthly 0.1° × 0.1° V07 |
| Short name / version | `GPM_3IMERGM` / `07` |
| Producer | NASA GSFC + JAXA (GPM mission) |
| Distributor | NASA GES DISC |
| Landing page | https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGM_07/summary |
| Variable we'd use | `precipitation` (monthly-mean rate) |
| Units | mm/hr monthly mean (×24×days-in-month → mm/month); confirm which the v07 monthly file stores natively, see §5 |
| Time coverage | 2000-06-01 → present; Final product lag ~3–4 months |
| Spatial resolution | 0.1° × 0.1°, 90°S–90°N (full accuracy typically 60°S–60°N, see §5) |
| Format | NetCDF-4 / HDF5, one file per month |
| Approx. per-file size | 20–30 MB (global) |
| Quality fields | includes a probability-of-liquid-precip index and random-error estimate (variable names, see §5) |
| License | NASA free-use / cite |

### 3.3 MODIS/Terra MOD13A3 v061 — monthly vegetation indices (1 km SIN) **← LOCKED**
| Field | Value |
|---|---|
| Full name | MODIS/Terra Vegetation Indices Monthly L3 Global 1 km SIN Grid V061 |
| Short name / version | `MOD13A3` / `061` |
| Producer | NASA MODIS Land team |
| Distributor | NASA LP DAAC (regional subsets via **NASA AppEEARS**: https://appeears.earthdatacloud.nasa.gov) |
| Landing page | https://lpdaac.usgs.gov/products/mod13a3v061/ |
| Variables we use | `_1_km_monthly_NDVI` (primary) + `_1_km_monthly_pixel_reliability` (QA field: 0=good, 1=marginal, 2=snow/ice, 3=cloudy, fill elsewhere) |
| Units / scaling | NDVI unitless, stored as int16, scale factor **0.0001** (valid range -2000 … +10000) |
| Time coverage | 2000-02-01 → present, monthly, ~1–2 month lag |
| Spatial resolution | **1 km** on the MODIS Sinusoidal grid; AppEEARS re-grids to geographic 0.00892857° (~1 km) output |
| Format | AppEEARS output: **NetCDF-4** per month, already clipped to the requested polygon (~tens of KB each, few MB total per region) |
| Fill values | NDVI **-3000** = fill; pixel_reliability -1 = fill |
| Access path | Stage 2 proved the ingest works on the direct LP DAAC HDF-EOS format; Stage 4+ reads the AppEEARS NetCDF-4 output instead |
| License | NASA / USGS free use with citation (see `docs/sources-and-attribution.md`) |

### 3.3-bis MODIS/Terra MOD13C2 v061 — monthly vegetation indices (0.05° CMG) — *superseded 2026-11-14 evening*
| Field | Value |
|---|---|
| Full name | MODIS/Terra Vegetation Indices Monthly L3 Global 0.05° CMG V061 |
| Short name / version | `MOD13C2` / `061` |
| Why superseded | AppEEARS does not serve the CMG product family. Switching to MOD13A3 preserves every property we care about (variable, cadence, record length) and gives us 5.6× finer spatial resolution. |
| Still referenced by | `nasa_download.py` (kept as scratch; functional but no longer the primary access path); `science/tests/test_ingest.py::test_real_mod13c2_file_metadata` (one real MOD13C2.A2026274 file lives under `science/data/raw/MOD13C2/`, used to prove the pyhdf HDF-EOS ingest path works end-to-end on a real NASA granule — Stage 2 gate). |
| Landing page (for reference) | https://lpdaac.usgs.gov/products/mod13c2v061/ |

### 3.4 GLDAS Noah monthly 0.25° v2.1 (GLDAS_NOAH025_M)
| Field | Value |
|---|---|
| Full name | GLDAS Noah Land Surface Model L4 Monthly 0.25° × 0.25° V2.1 |
| Short name / version | `GLDAS_NOAH025_M` / `2.1` |
| Producer | NASA GSFC Hydrological Sciences Laboratory |
| Distributor | NASA GES DISC |
| Landing page | https://disc.gsfc.nasa.gov/datasets/GLDAS_NOAH025_M_2.1/summary |
| Variables we'd use | `SoilMoi0_10cm_inst`, `SoilMoi10_40cm_inst`, `SoilMoi40_100cm_inst`, `SoilMoi100_200cm_inst` (soil moisture content by layer); `Evap_tavg` (total evapotranspiration); `Rainf_tavg`; others |
| Units | Soil moisture: **kg/m²** (equivalent to mm of water). ET: **kg/m²/s** (needs conversion to mm/day or mm/month via named function) |
| Time coverage | 2000-01-01 → present, monthly, ~1–2 month lag. (v2.0 extends back to 1948; a mixed v2.0+v2.1 pipeline is non-trivial and we will not do it at hackathon scope) |
| Spatial resolution | 0.25° × 0.25°, **land-only** (ocean cells are masked) |
| Format | NetCDF-4, one file per month |
| Approx. per-file size | 20–30 MB (global, land-only mask) |
| Fill value | standard `_FillValue` (see §5) |
| Modelling caveat | GLDAS is a land-surface model driven by observations; same caveat as MERRA-2 — it is a derived product, not a direct retrieval |
| License | NASA free-use / cite |

### 3.5 Summary table — the five we audited in one view
| Dataset | Earliest | Res (spatial) | Res (temporal) | Per-month file | Native unit (primary var) | Land/Atmo/Both |
|---|---|---|---|---|---|---|
| **MOD13A3 v061 (LOCKED)** | **2000-02** | **1 km SIN** | **monthly** | **few MB / region via AppEEARS** | **NDVI × 10⁴** | **land** |
| MOD13C2 v061 (superseded) | 2000-02 | 0.05° CMG | monthly | 60–100 MB | NDVI × 10⁴ | land |
| M2TMNXSLV v5.12.4 | 1980-01 | 0.5°×0.625° | monthly | 35–50 MB | K | atmosphere (reanalysis) |
| GPM_3IMERGM v07 | 2000-06 | 0.1°×0.1° | monthly | 20–30 MB | mm/hr (mean rate) | atmosphere/surface |
| GLDAS_NOAH025_M v2.1 | 2000-01 | 0.25°×0.25° | monthly | 20–30 MB | kg/m² (SM), kg/m²/s (ET) | land |

---

## 4. Data use & budget reality check

- **Full-global, all-four download:** ~65–70 GB cumulative (see earlier conversation; calculated as per-file × months). **Not planned.**
- **Approved hard budget:** 600 MB total disk + bandwidth for this project.
- **How we stay under 600 MB:** lock exactly one variable + one region pair at the end of Stage 0, then at Stage 2 use `earthaccess.search_data(bounding_box=…)` to retrieve only files that intersect the region's bounding box, or OPeNDAP to spatially subset server-side. For a MENA-sized bounding box (~10° × 10°) at the resolutions above, a 25-year monthly series lands in the **50–300 MB** range. We will run a DRY_RUN granule count first and verify the predicted on-disk size before flipping `DRY_RUN = False`.
- Current `nasa_download.py` is DRY_RUN=True — safe default until variable+region approved.

---

## 5. Unknowns (verify before Stage 2 ingest; do not fabricate in the meantime)

1. **Exact `_FillValue`, scale-factor, and valid-range** for each named variable in each product. Pull from the landing-page documentation / the first granule's `ncdump -h` header during Stage 2.
2. **Exact DOI strings** for each product (I know the general DOI pattern but have not opened the landing pages in this session; cite from the landing page, not from memory).
3. **IMERG monthly units in v07** — whether the `precipitation` variable stores mm/hr mean rate or mm/day mean rate. Trivial to confirm from the file metadata; important for correct conversions.
4. **MOD13C2 v061 exact file size per month** — the 60–100 MB range is approximate; one real granule in Stage 2 will fix the number.
5. **Whether `pymannkendall` is appropriate for our chosen variable's autocorrelation profile.** Decide after a lag-1 check on the real series; may need Hamed-Rao modified MK or prewhitening.
6. **Sahara NDVI quality** — MOD13C2 over hyper-arid surfaces returns very low NDVI with occasional high retrieval-quality issues due to BRDF effects on bright sand; usable but caveat the fraction-of-good-pixels.
7. **IMERG 60°N / 60°S edge** — IMERG combines PMW + IR retrievals; accuracy and sampling degrade outside ~60°N/60°S. Not relevant for a MENA scope, but note it before claiming "global" anywhere in the UI.
8. **Egyptian vs MENA framing** — whether the project should be pitched as "Egypt-local" (ties to Local Impact award, Local Event ties) or "MENA/global contrast" (ties to Global Connection, Best Use of Data). Pick per Decision Lab language; technical path is the same.
9. **Local Event location + Team composition** — not stated anywhere in the repo; affects submission form fields but not the technical build.
10. **SI-use disclosure** — this doc, the audit itself, was drafted by an SI tool (Claude Opus 4.7). We must log that here *and* in `docs/ai-use-log.md` + `docs/ai-use-disclosure.md` + the submission form's SI-use description.

---

## 6. Smallest valid P0 data path — proposal

**Single variable, single contrast-pair, single dataset family. Everything else can be added later without refactoring.**

- **Variable:** NDVI (vegetation index) — MOD13C2 v061.
  - Why NDVI over temperature/precip: (a) longest usable monotonic series for a vegetated-vs-desert contrast; (b) MOD13C2 ships with per-pixel reliability flags which makes the provenance audit cleaner than reanalysis variables; (c) the vegetation story has strong public-facing legibility (greener/browner is read correctly by a non-scientist), which helps Presentation and Impact scores.
- **Record:** 2000-02 → 2026-09 (26.6 years).
- **Aggregation to annual series** (per SPEC): monthly → annual mean per cell using the ≥ 9/12-valid-month coverage rule (configurable in `science/config/analysis.yaml`).
- **Statistics:** Theil-Sen slope + 95 % CI; Mann-Kendall p-value; lag-1 autocorrelation check → modified MK (Hamed-Rao) or prewhitening fallback; BH FDR across cells.
- **Independent check:** recompute one headline slope with `scipy.stats.theilslopes` and compare to `pymannkendall.sens_slope`; record agreement in `docs/methodology.md`.
- **Secondary variable (P1 stretch, NOT downloaded in Stage 2):** MERRA-2 T2M for the same region, same aggregation — allows a Compare-page correlation view ("NDVI trend associated with T2M trend") without any extra P0 scope.

---

## 7. Two candidate region pairs (scored on the Stage 0 rubric)

**Rubric (from `STAGE_PROMPTS.txt` → STAGE 0):** time span ≥ 15 yr ×3 · regional contrast likely ×3 · processing cost fits 6 h ×3 · quality flags clear ×2 · Egypt/MENA relevance ×2 · second related variable available ×2 · globe visual appeal ×1. Max = **16**.

### Pair A — **Nile Delta vs Sahara Interior (NDVI)**
Bounding boxes (approximate, to be snapped to MOD13C2 0.05° CMG grid in Stage 2):
- **Nile Delta:** 29.5–31.5°N, 30.0–32.0°E — intensively irrigated agriculture, among the densest in the world.
- **Sahara Interior (Western Desert, Egypt):** 24.0–26.0°N, 26.0–28.0°E — hyper-arid, essentially vegetation-free baseline.

| Criterion | Weight | Score | Reasoning (traced to files) |
|---|---|---|---|
| Time span ≥ 15 yr | ×3 | 3 | MOD13C2 record 2000-02 → 2026-09 = **26.6 yr** (§3.3). |
| Regional contrast likely | ×3 | 3 | Irrigated delta vs hyper-arid interior is the maximum possible NDVI contrast on one country's territory. Both the sign and the magnitude of their long-term trends are worth testing (delta likely flat-to-decline from salinisation & urban sprawl; desert may show slight greening from CO₂ fertilisation / shifting marginal rainfall). |
| Processing fits 6 h | ×3 | 3 | Two bounding boxes, each ~2°×2° → <5 % of a global monthly granule per region. Monthly = ~320 files × very small subset ≈ well under 600 MB total. |
| Quality flags clear | ×2 | 2 | MOD13C2 ships both `pixel reliability` (0=good … 3=cloudy, else fill) and a bit-packed `VI Quality` layer (§3.3). |
| Egypt / MENA relevance | ×2 | 2 | Both regions are inside Egypt. Nile-Delta food security and Sahara monitoring are both locally meaningful. |
| Second related variable | ×2 | 2 | MERRA-2 T2M (§3.1) and GLDAS soil moisture (§3.4) both cover the same bounding boxes; later stages can add a correlation panel without a new variable lock. |
| Globe visual appeal | ×1 | 1 | Nile Delta + Western Desert is one of the most iconic satellite shots on Earth (green fan on a brown field). |
| **Total** |  | **16 / 16** | |

**Confidence note:** Scores 2 and 3 above assume the IMERG/MERRA-2 bounding-box subset actually fits our 600 MB budget. The DRY_RUN run in Stage 2 will verify granule counts before any download.

### Pair B — **Egyptian Nile Basin vs Ethiopian Highlands (IMERG precipitation)**
- **Egyptian Nile Valley / Lake Nasser:** 22.5–27.0°N, 30.0–33.0°E — near-zero precipitation.
- **Ethiopian Highlands (Blue Nile headwaters):** 8.0–13.0°N, 36.0–40.0°E — monsoon-driven highland rainfall; source of ~85 % of Nile flow.

| Criterion | Weight | Score | Reasoning |
|---|---|---|---|
| Time span ≥ 15 yr | ×3 | 3 | IMERG monthly record 2000-06 → 2026-09 = **26.3 yr** (§3.2). |
| Regional contrast likely | ×3 | 3 | ~0 mm vs hundreds of mm per rainy season — enormous contrast, with real downstream policy stakes (Nile water security, GERD context). |
| Processing fits 6 h | ×3 | 3 | Two moderate bounding boxes at 0.1° resolution subset to ~100 MB total under budget. |
| Quality flags clear | ×2 | 2 | IMERG monthly ships per-cell random-error and liquid-precipitation-probability fields (§3.2, exact names in §5). |
| Egypt / MENA relevance | ×2 | **1** | Egyptian valley is MENA core; Ethiopian Highlands are Horn of Africa, not formally MENA — gives one half of the pair strong relevance, the other half tangential. The hydrological linkage is strong, but the award category it most appeals to shifts from Local Impact toward Global Connection. |
| Second related variable | ×2 | 2 | MERRA-2 T2M available for both; GLDAS soil-moisture/ET too. |
| Globe visual appeal | ×1 | 1 | Blue Nile source + arid Egypt is a visually striking globe fly-to. |
| **Total** |  | **15 / 16** | |

### Recommendation
**Pair A (Nile Delta vs Sahara, NDVI).** Highest-scoring; fully-Egyptian framing means it also clears a crisper "Local Impact" award narrative; least downstream risk because the variable has per-pixel QA flags that we can honestly show on the Evidence Receipt.

Pair B is a strong Plan B and could become the **Compare-page second case** at P1 scope without changing the Stage-2 dataset lock (IMERG would be the second download, still within budget).

---

## 8. What this audit does **not** do

- No code written.
- No data downloaded.
- No findings, no statistics, no preview UI claims.
- No mocked numbers — the earlier `index.html` demo's hard-coded `+1.4°C` / `92% confidence` values are explicitly rejected here; every number the shipped product displays will come from an exported JSON produced by a tested Python script against the real NASA dataset locked at the end of this stage.

---

## 9. Approval request — STOP here per Stage 0 gate

Please confirm:

1. **Variable:** NDVI from MOD13C2 v061.  ☐ approve  ☐ change to: ______
2. **Region pair:** Nile Delta (29.5–31.5°N, 30.0–32.0°E) vs Sahara Interior (24.0–26.0°N, 26.0–28.0°E).  ☐ approve  ☐ change to: ______
3. **Time window:** 2000-02-01 → 2026-09-30 (full MOD13C2 record, ~26.6 yr).  ☐ approve  ☐ change to: ______
4. **Second variable (deferred to P1 stretch, not downloaded in Stage 2):** MERRA-2 T2M for the same bounding boxes.  ☐ approve  ☐ change to: ______

On approval, the next step is Stage 1 (scaffold Next.js + Python env + Make targets) — still no downloads — and only at Stage 2 do we DRY_RUN the MOD13C2 regional subset to confirm actual on-disk size before fetching.
