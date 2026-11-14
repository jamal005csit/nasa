EARTH//NEXT - PROJECT STATE
LAST UPDATED: 2026-11-14, Day 1 night (Stages 7-8 + cleanup + git init)

CURRENT STAGE: Handoff-ready. Stages 0-8 done. Stage 9 (Decision Lab) engine done, UI TBD. Stage 10 (Crosswalk) page done. Stage 11 (Release) in progress.

LAST GATE PASSED: 58 pytest + 26 vitest + pnpm build green on 8 static routes.
  Routes: /, /atlas, /trend-lab, /compare, /crosswalk, /_not-found
  First-load JS: 87.5-125 kB per route.
  Data: NASA MOD13A3.061 NDVI via AppEEARS for Nile Delta + Sahara Interior.

--- LOCKED DECISIONS ---
Dataset: MODIS/Terra Vegetation Indices Monthly L3 Global 1km SIN Grid V061 (MOD13A3.061)
Variable + units: NDVI (unitless, scale 0.0001)
Time: 2000-02 to 2026-09, monthly
Primary: Nile Delta (29.5-31.5N, 30.0-32.0E)
Comparison: Sahara Interior (24.0-26.0N, 26.0-28.0E)
Question: "Over ~25 years, has NDVI in the Nile Delta trended in a statistically detectable direction, and has the surrounding desert done the same?"

--- STAGE CHECKLIST ---
[x] 0 Audit          gate: PASSED
[x] 1 Scaffold       gate: PASSED
[x] 2 Ingest+validate gate: PASSED
[x] 3 Stats engine   gate: PASSED
[x] 4 Export contract gate: PASSED
[x] 5 Mission Control gate: PASSED
[x] 6 Atlas+Trend Lab gate: PASSED
[x] 7 ESI+Robustness  gate: PASSED — 58/58 pytest + ESI badge on FeaturedFinding + RegionExport
[x] 8 Compare        gate: PASSED — Region Duel page with diff-of-slopes, verdict templates
[~] 9 Decision Lab   gate: engine done (threshold.py + 5 tests), UI page TBD
[~] 10 Crosswalk     gate: page exists, links all requirements to screens
[ ] 11 Release       gate: git init pending

--- KEY RESULTS (NASA data) ---
Nile Delta:    +0.00079 NDVI/yr (95% CI +0.00050, +0.00110) p<0.001 ESI A (10/10)
Sahara:         -0.000055 NDVI/yr (95% CI -0.000131, +0.000017) p=0.183 ESI C (5/10)
  "No statistically detectable trend at α = 0.05 with this data."

--- KNOWN ISSUES ---
- Root-level legacy files removed (index.html, server.js, EARTH_NEXT_BLUEPRINT_V2.md, etc.)
- legacy_mockup/ deleted. NASA download scripts removed.
- Python 3.13.3 (not 3.11/3.12), version check updated to <3.14
- No git repo yet — needs `git init` and first commit
- Decision Lab UI not built (just Python engine + tests)
- Story Mode, Frontier, Decision Studio not built (P1/P2)
- pnpm locked to single-thread vitest (Windows compat)
