# EARTH//NEXT — Team Handoff

**Snapshot taken: 2026-11-14 evening. Stages 0–6 of 11 are done on real NASA data.**
**Submission deadline: 2026-11-15 11:59 p.m. local time.**

This doc is what you read when you join. Everything else in `docs/` goes deeper.

---

## 1. Open it in 60 seconds

```bash
cd earth-next/
cp .env.example .env            # fill in the two EARTHDATA_* values (your own)
npm run setup                   # Python venv + pip + pnpm install   (~5 min first time)
npm test                        # 44 pytest + 26 vitest → "All tests PASS."
npm run dev                     # http://localhost:3000
```

If PowerShell refuses with "running scripts is disabled", prefix every `npm`
with `npm.cmd` or once-off: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`.

## 2. What's real right now

- **Three screens live, driven by real NASA data:** Mission Control (3D globe +
  featured finding), Signal Atlas (2D map with trend coloring + significance
  hatching), Trend Lab (4 answer cards + Theil-Sen time series + Evidence
  Receipt drawer).
- **Dataset:** MODIS/Terra MOD13A3.061 NDVI, monthly, 2000-02 → 2026-09,
  retrieved via NASA AppEEARS, clipped to two polygons.
- **Statistics:** Theil-Sen slope with 95% CI, Mann-Kendall p-value with
  Hamed-Rao autocorrelation correction when lag-1 ρ ≥ 0.10, cos(lat)
  area-weighted regional means, coverage rule ≥ 9 valid months per year.
- **Provenance** attached to every result: dataset DOI-equivalent URL, variable,
  filters applied, library versions, config hash, data checksum, git sha,
  timestamp.
- **Headline finding so far:** Nile Delta NDVI has a statistically detectable
  upward trend (+0.00079/yr, p < 0.001); the adjacent Sahara Interior does not
  (p = 0.183). Full method in `docs/methodology.md`.

## 3. What's NOT built yet — stages 7–11

Ordered by cost; the SPEC "cut order" tells you what to skip if time runs out.

| Stage | Title | Rough cost | Hard part |
|---|---|---|---|
| 7 | Robustness Panel + ESI grade A–D | 2–3 h | start/end-year sensitivity heatmap; ESI scoring from the YAML rubric |
| 8 | Compare / Region Duel | 1.5–2 h | bootstrap CI on difference-of-slopes |
| 9 | Decision Lab + Brief | 3–4 h | time-to-threshold + scenario fan chart + Markdown Brief export |
| 10 | Story Mode, Crosswalk, a11y, Frontier | 3–4 h | scripted 90-sec autoplay sequence |
| 11 | Release | 2–3 h | README (done), descriptions, Vercel deploy, clean-clone check |

Total realistic: **12–16 h with cuts**, well under the remaining submission
window. See `docs/PROJECT_STATE.txt` for the active checklist.

## 4. Where to look when something breaks

| Symptom | Where to look |
|---|---|
| Globe is a black sphere | `web/public/textures/earth.jpg` missing — rerun `python scripts/fetch_earth_texture.py` |
| "DEMO DATA" banner showing but you expected real data | At least one region's folder is missing its `MOD13A3.061_1km_aid*.nc` from AppEEARS. Check `science/data/raw/appeears/{nile_delta,sahara_interior}/`. Pipeline needs real files in ALL regions to switch to NASA mode. |
| Trend Lab region picker doesn't update other cards | State is shared via `AppStateProvider` in `web/src/lib/url-state.tsx`. Confirm it's in the root `layout.tsx` wrapping `AppShell`. |
| `/atlas` or `/trend-lab` returns 500 in dev | Stale `.next` cache after a lib/ rename. Fix: `rm -rf web/.next` and restart `npm run dev`. |
| pytest fails on a real-file test | You removed the one MOD13C2.hdf under `science/data/raw/MOD13C2/`. Test skips cleanly in that case — but if it ran and failed, re-download via `python scripts/fetch_one_mod13c2.py`. |
| `npm run process` crashes on calendar error | AppEEARS stamps its NetCDF with a Julian calendar. `appeears.py` manually decodes the time axis — if you touched that file, check the `decode_times=False` branch is still intact. |

## 5. Hard rules you'll be held to

- Never invent data. Unknown → `null` with a note.
- Every number in the UI reads from an exported JSON. No hand-typed numbers in
  components. Enforce via the test under `science/tests/test_export.py` and
  the TS schema tests under `web/src/__tests__/schemas.test.ts`.
- SPEC language rules are lint-checked by `web/src/__tests__/language-lint.test.ts`.
  Don't ship UI copy with "causes / due to / proves". For non-significant
  results use the exact phrase `No statistically detectable trend at α = 0.05
  with this data.`
- Scenarios (Stage 9) must carry the label `Illustrative scenario — not a
  validated causal forecast.`
- Moon/Mars (Stage 10) is context cards only. Never run the trend engine on them.
- SI (AI) use is disclosed in `docs/ai-use-disclosure.md`. Every meaningful AI
  session adds a row to `docs/ai-use-log.md`. This is a submission-form
  requirement, not a nicety.

## 6. If you're the one deploying

Stage 11 target: Vercel static deploy of `web/out/`. Prep:

```bash
npm run process && npm run build
# web/out/ is the static site; drag-drop to Vercel / Netlify, or:
#   vercel deploy --prod web/out
```

The site needs zero backend. No secrets reach the browser.

## 7. Pointers to deeper docs

- `AGENTS.md` — the hard rules, in full.
- `docs/SPEC.txt` — the original product spec. Unchanged since day 1. Source of truth.
- `docs/PROJECT_STATE.txt` — read first every session. Update last. Current
  decisions and open questions live here.
- `docs/methodology.md` — every statistical assumption and the independent
  cross-check result.
- `docs/resource-audit.md` — the dataset and challenge-requirements audit.
- `docs/crosswalk-source.md` — 41 numbered requirements traced to source files.
- `docs/sources-and-attribution.md` — the References-field content for the
  submission form.
- `docs/ai-use-disclosure.md` — the one-page SI-use disclosure for the submission form.
- `docs/ai-use-log.md` — the internal running log (update when you use AI).
