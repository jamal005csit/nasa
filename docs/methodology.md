# EARTH//NEXT — Methodology

**Audience:** judges, SMEs, and anyone wanting to reproduce or audit a number
we show in the UI. Every assumption here is also enforced in code or config.

**Scope at this version:** Stage 3. Covers the statistics engine
(`science/src/earthnext/trends.py`). Pipelines that consume it (export,
robustness, ESI) get their own sections at Stages 4 and 7.

---

## 1. Dataset

- **Product:** MODIS/Terra Vegetation Indices Monthly L3 Global 1 km SIN Grid V061
  (**MOD13A3.061**). Updated from the original Stage-0 lock of MOD13C2.061 after
  discovering that the CMG product (0.05°) is not distributed through AppEEARS;
  MOD13A3 is 5.6× finer spatially (1 km vs 5.6 km) with the same monthly cadence
  and the same 2000-02 → present record. See `docs/PROJECT_STATE.txt` for the
  change log.
- **Variable:** `_1_km_monthly_NDVI`, decoded from the native int16 storage with
  scale factor **0.0001** and `_FillValue` **-3000** → NaN. Validated min/max
  checked against the MOD13 User Guide: NDVI ∈ [-0.2, 1.0].
- **Regions:** two bounding boxes locked in Stage 0: Nile Delta
  (29.5–31.5°N, 30.0–32.0°E) and Sahara Interior / Western Desert
  (24.0–26.0°N, 26.0–28.0°E).
- **Time window:** 2000-02-01 → 2026-09-30 (~26.6 years of monthly means).

## 2. Processing order

Fixed sequence, per SPEC §3 rule 1: **inspect → validate → aggregate →
deseasonalize (if monthly) → estimate → test → correct → report**.

## 3. Seasonality handling

Two allowed modes, SPEC §3 rule 2:

- **Annual aggregation** (default): monthly → yearly mean per cell. A year's
  value is included **only if ≥ 9 of its 12 months are non-NaN**. Threshold
  configurable in `science/config/analysis.yaml:aggregation.min_valid_months_per_year`.
- **Seasonal Kendall** (optional, on raw monthly series): planned for the
  Robustness Panel at Stage 7.

Rationale: annual aggregation is the simplest honest transformation that
removes the 12-month cycle without model assumptions. The coverage rule
prevents a year's mean from being driven by two cloudy months.

## 4. Trend estimator

**Theil-Sen slope** (`scipy.stats.theilslopes`). Robust: resistant to up to
~29 % outlier contamination; no distributional assumption on residuals.

**95 % confidence interval** on the slope comes directly from `theilslopes`
(two-sided, rank-based). Confidence level configurable
(`trend.confidence_level`, default 0.95).

Total change over the record is `slope × (t_end − t_start)`, with CI bounds
propagated linearly.

## 5. Significance test

**Mann-Kendall**. Three variants are implemented; one is chosen per series
based on lag-1 autocorrelation:

| |lag-1 ρ| | Variant used | Why |
|---|---|---|
| < 0.10 (default threshold) | `pmk.original_test` | plain MK is unbiased on independent data |
| ≥ 0.10 | `pmk.hamed_rao_modification_test` (default) OR `pmk.pre_whitening_modification_test` (configurable) | plain MK's variance is too small for AR(1)-like series; both modifications inflate it appropriately |

The threshold and the choice between Hamed-Rao vs prewhitening live in
`science/config/analysis.yaml:trend.autocorr_threshold / autocorr_variant`.
The chosen variant is **recorded in the Provenance** for every result, so a
reader knows which test backed the p-value.

p-values are reported with the SPEC §3 convention: **`p < 0.001` is never
`0.000`**.

## 6. Multiple testing correction

When testing many cells (Signal Atlas grid) or many regions, p-values go
through **Benjamini-Hochberg FDR** (`statsmodels.stats.multitest.multipletests(method='fdr_bh')`).

- Default q-threshold: 0.05 (`multiple_testing.q_threshold`).
- The number of tests and the FDR rule are both displayed on the Signal Atlas
  per SPEC §2 item 2.

## 7. Area-weighted spatial means

When averaging values over a lat/lon grid (regional mean, zonal mean), each
cell's weight is **cos(latitude in radians)**. This corrects for the fact that
grid cells shrink in area as |latitude| → 90°.

- Implementation: `earthnext.trends.area_weighted_mean(field, lats_deg)`.
- NaN-aware: missing cells contribute zero weight, not zero value.
- Each result also carries a **valid-cell fraction**
  (`valid_cell_fraction(field)`) so a reader can tell a 100 %-coverage mean
  apart from a 15 %-coverage mean, which the SPEC requires.

## 8. Independent verification

Per SPEC §3 rule 12 ("Independent check: recompute one headline number with
a second implementation"):

- **Test:** `test_theil_sen_cross_check_against_scipy` in
  `science/tests/test_trends.py`.
- **What it does:** builds a known noisy linear series (slope 0.2, additive
  N(0, 0.3²) noise), computes slope + CI two ways: (a) via our wrapper
  `earthnext.trends.theil_sen_ci`, (b) via direct `scipy.stats.theilslopes`
  call on the same arrays.
- **Result:** both implementations agree exactly (same underlying function;
  the wrapper just NaN-filters, validates input, and packages the result).
  Test passes with `pytest.approx` at default tolerance.
- **What this does NOT test:** that `scipy.theilslopes` itself is correct.
  That's inherited from scipy's own test suite. Our contract is "we don't
  distort what scipy returns" and the test verifies exactly that.

A second independent check against **`pymannkendall.sens_slope`** is planned
for Stage 4 once we have the real AppEEARS series in hand — it will re-compute
the Nile-Delta headline slope under both libraries and record the numerical
agreement in this file.

## 9. Limits and honest caveats

- MOD13A3 is a **retrieval product**, not a reanalysis. NDVI is a vegetation
  proxy; it responds to canopy density, greenness and soil wetness, and is
  affected by cloud contamination and aerosols even after the product's own
  cloud screening. We do not treat NDVI as "vegetation biomass".
- Over hyper-arid surfaces (e.g. our Sahara box) NDVI values are small
  (~0.05–0.15); small absolute changes can look large relatively. We will
  always report the slope in native units (NDVI/yr), not as a percent change,
  to avoid that distortion.
- NDVI is **unitless** (ratio). We report slope in units of NDVI/yr.
- The Decision Lab's scenarios are **extrapolations of the observed slope** —
  they are labelled "Illustrative scenario — not a validated causal forecast"
  in the UI per SPEC §2 item 6.
- Statistical significance is not scientific importance, and is not causation.
  The UI's language rules are enforced by a lint test
  (`language.forbidden_phrases` in `analysis.yaml`) that will run at Stage 6.

## 10. Reproducibility

Every number produced by the pipeline carries a **Provenance record**
(`earthnext.provenance.Provenance`) with:

- the dataset short-name, version, source URL,
- the variable name and native units,
- the time range and spatial bounding box,
- the list of filters applied (fill→NaN, scale, subset …),
- the estimator / test / FDR method / alpha actually used,
- `n_valid`, `missing_pct`, `slope`, `slope_ci95`, `p`, `q`,
- a `script_commit` (git sha or `untracked`),
- a `config_hash` (sha256 of the thresholds in `analysis.yaml` that were in
  effect at computation time),
- a `data_checksum` (sha256 of the input file),
- `library_versions` for numpy / xarray / pandas / scipy / pyhdf /
  pymannkendall,
- a `generated_at` ISO-UTC timestamp.

Re-running `npm run process` against the same inputs regenerates identical
numbers if the code and config are unchanged; the config_hash makes
drift detectable.
