# EARTH//NEXT — Super Intelligence (SI) Use Disclosure

**For:** the NASA Space Apps 2026 Project Submission form.
**Written for:** the SI-use description field on the submission page.
**This is the short, public-facing version.** The full session log is in `docs/ai-use-log.md`.

Per Executive Order of 2026-09-29 and the 2026 Participant FAQs (p.12), NASA
renames "AI / Artificial Intelligence" to "Super Intelligence / SI"; each team
must disclose how SI tools were used in the project.

---

## 1. Tool used

**Claude Opus 4.7** (model id `claude-opus-4-7`), by **Anthropic**, accessed
via the Claude Code agent interface running locally on the team's machine.
No other SI/LLM tool was used.

## 2. What the SI tool did

In rough order of appearance:

1. **Project audit (Stage 0).** Read the official NASA Space Apps 2026 challenge
   statement, Participant FAQs, Judging & Awards Guide, Team Formation Guide,
   and Space Apps Connect Guide. Produced `docs/resource-audit.md` (dataset
   audit + submission requirements + Unknowns) and `docs/crosswalk-source.md`
   (41 numbered requirements) by extracting content directly from those PDFs.
2. **Repository scaffold (Stage 1).** Generated Next.js 14 + TypeScript + Tailwind
   front-end skeleton under `web/` with the project's design tokens, and a
   Python 3.11 package under `science/` with pytest + ruff.
3. **Dataset ingest + validate (Stage 2).** Wrote the Python modules
   (`ingest.py`, `validate.py`, `provenance.py`, `cli_ingest.py`) that read a
   MODIS NDVI granule and emit a validation report with real counts.
4. **Statistics engine (Stage 3).** Wrote `trends.py` (Theil–Sen slope with CI,
   Mann-Kendall + autocorrelation-aware variants, BH-FDR, cos(lat)-weighted
   regional means, annual-aggregation with coverage rule), 24 synthetic-series
   tests with known answers, and `docs/methodology.md` describing every
   assumption.
5. **Documentation.** Drafted all `docs/*.md` files, including this one.

## 3. What the SI tool did NOT do

- **No numbers in the shipped UI are SI-generated.** Every value shown in the
  app comes from a JSON file produced by a tested Python script that runs on
  real NASA data. The Decision Brief is a deterministic template filled from
  JSON fields — no free-form text is generated at runtime.
- **No scientific findings are SI-generated.** Statistical analysis is
  performed by scipy and pymannkendall; the SI tool wrote the wrappers and
  the tests that verify the wrappers do not distort the underlying
  computations (see `docs/methodology.md` §8, independent cross-check).
- **No NASA data was fabricated.** All datasets are retrieved from NASA
  Earthdata / LP DAAC with provenance recorded per result (dataset short-name,
  version, DOI-equivalent landing URL, filters applied, data checksum,
  library versions, timestamp, git commit).
- **The SI tool did not act unsupervised.** Every stage's output was reviewed
  and explicitly approved by the human team member before the next stage
  began. Destructive operations (git, file deletions, network downloads
  beyond the single Stage-2 proof file) required explicit per-action approval.

## 4. How we supervised the SI tool

- **Hard rules file** (`AGENTS.md`): nine rules the SI tool is required to
  follow in every session, including "never invent data" and "no hand-typed
  numbers in components".
- **Rolling state file** (`docs/PROJECT_STATE.txt`): read at the start of
  every session, updated at the end; records locked decisions, deviations,
  and open questions.
- **Per-session SI-use log** (`docs/ai-use-log.md`): one row per working
  session with date, task, output, and what a human verified.
- **Stage-gate tests**: each stage has an explicit test gate
  (`pytest` + `pnpm --dir web build`) that must pass before the next stage
  begins. The SI tool cannot mark a stage done without the gate passing.
- **Independent cross-check** for one headline statistical result, per our
  methodology document.

## 5. Contact for questions

Team contact details appear on the project submission page.
