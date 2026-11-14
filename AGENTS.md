# AGENTS.md — EARTH//NEXT

## Identity
You are building EARTH//NEXT for the NASA Space Apps 2026 challenge "Be An Earth System Trend Detective!". Hackathon: Nov 14–15, 2026. Quality and honesty beat feature count.
Read `docs/PROJECT_STATE.md` first (rolling state), and update it last after each completed stage.

## Hard rules (never violate)
1. Never invent data, findings, citations, units, or metadata. Unknown = `null` with a note.
2. Real NASA resource-pack data drives every finding. Synthetic fixtures exist only under `science/tests/fixtures/` and are labeled DEMO/SYNTHETIC.
3. Every number shown in the UI comes from exported JSON produced by a script. No hand-typed numbers in components.
4. Scenario outputs always carry the label: "Illustrative scenario — not a validated causal forecast."
5. Moon/Mars never run through the Earth trend pipeline. Planetary context cards only with a citable source and license.
6. No NASA logos/insignia. No secrets in the browser. No network call needed to render the demo (offline-first, cached JSON).
7. No dead buttons: every control changes state or is removed.
8. Add a dependency only after stating why the project needs it.
9. Do not mark a stage done until its gate passes (tests green, commands run, output shown).

## Science rules
- Real NASA data only; synthetic fixtures only in tests.
- Seasonality: annual aggregation or deseasonalized series — document the choice.
- Trend: Theil–Sen slope with 95% CI. Test: Mann–Kendall (or a justified alternative). Check lag-1 autocorrelation; use a modified/prewhitened variant if material, and say which was used.
- Grid-wide / region-set testing: Benjamini–Hochberg FDR; report q-values; state the number of tests.
- Report slope/yr with units, 95% CI, p (show `p < 0.001`, never `0.000`), q, N valid, missing %.
- Non-significant ≠ no change. Significant ≠ important. Trend ≠ cause.
- Area-weighted spatial means (cos latitude) when aggregating; report valid-cell fraction.
- Preserve source units; conversions are named functions with tests.
- Independent check: recompute one headline number with a second implementation (e.g., scipy `theilslopes` vs pyMannKendall) and record agreement in `docs/methodology.md`.

## Language rules (enforced in UI)
- Non-significant → "No statistically detectable trend at α = 0.05 with this data." Never "no change."
- Never "causes", "due to", "proves". Use "is associated with" only in correlation views.
- Direction chips pair a symbol + word, never color alone.
- No free-form generated claims; briefs/summaries are deterministic templates fed by JSON fields.

## Provenance contract (every analysis result carries this)
`dataset`, `source_url`, `variable`, `units`, `time_range`, `spatial_extent`, `resolution`, `filters_applied`, `method {estimator, test, fdr_method, alpha}`, `n_valid`, `missing_pct`, `slope`, `slope_ci95`, `p`, `q`, `script_commit`, `config_hash`, `data_checksum`, `library_versions`, `generated_at`.
Thresholds and weights live in `science/config/analysis.yaml`, not in code.

## Data + result contract
- Export from Python to `web/public/data/*.json` (per file < 2 MB; keep < 1 MB where possible) + trend-grid GeoJSON for the map.
- Matching Zod schemas in `web/src/lib/schemas.ts`; a test must validate every exported file in both Python (pydantic) and TS (zod).
- The web app renders only from these JSON files.

## Stack
Next.js App Router + TypeScript + Tailwind (static export, `output: 'export'`); react-globe.gl (three) lazy-loaded with 2D map fallback; ECharts; Zustand; Zod; Framer Motion.
Python 3.12: numpy, pandas, scipy, statsmodels, xarray (+netCDF4 if needed), pymannkendall (only if its assumptions check out), pytest, ruff.

## Layout
```
science/{config,data/raw,data/processed,src/earthnext,tests}
web/{public/data,src}
docs/{official,resource-audit.md,methodology.md,sources-and-attribution.md,ai-use-log.md,PROJECT_STATE.md}
```

## Working style
- Small verified increments. After each: run tests, report PASS/FAIL and what's next.
- Show diffs summary, not full file dumps.
- When blocked or ambiguous about the challenge data: STOP and ask; do not guess.
- Keep a running `docs/ai-use-log.md`: date, task, what the AI produced, what a human verified.
- Commit after every stage gate.

## Definition of done (per stage)
The stage gate listed in the stage prompt is satisfied AND `pytest`, `pnpm test`, and `pnpm build` all pass.

## Feature priority and cut order
P0 (never cut): real NASA data pipeline, trend + significance + CI, Region Duel, Evidence Receipts, Decision Studio basics, working static public deploy, disclosures.
P1: Story Mode, Robustness Panel (start/end sensitivity, method agreement, leave-one-out), Evidence Strength Index (ESI grade A–D per rubric in `analysis.yaml`, disclosed as a heuristic), Crosswalk page, scenario fan + Decision Brief export.
Cut order: i18n toggle → Frontier "same question" cards → Moon/Mars beyond textured globe + info panel → extra variables → shareable URL.

## Design tokens
bg #070B14, surface #0E1626, line #1C2A44, text #E8EEF8, muted #8FA0BA, accent cyan #35E0FF, warn amber #FFB84D, neg coral #FF7A7A, pos mint #6EE7B7.
Fonts: Space Grotesk (UI), IBM Plex Mono (numbers, `tabular-nums`).
Always pair color with a symbol or label. 4.5:1 contrast minimum. Respect `prefers-reduced-motion`.
Layout first-class at 1440px and 1280×720.
