// Challenge Crosswalk — each official requirement mapped to where it is answered.
// Data sourced from docs/crosswalk-source.md. SPEC §2 item 10.

const ITEMS = [
  { req: "Use real NASA Earth observation data", answered: "All data from MODIS/Terra MOD13A3.061 via NASA AppEEARS", screen: "Mission Control, Evidence Receipt", status: "✓" },
  { req: "Detect a trend in an Earth system variable", answered: "NDVI trends in Nile Delta (increasing) and Sahara Interior (no detectable trend)", screen: "Trend Lab", status: "✓" },
  { req: "Use a valid statistical test with justification", answered: "Theil-Sen slope + Mann-Kendall (Hamed-Rao variant for autocorrelation), documented in methodology.md", screen: "Evidence Receipt → Methodology", status: "✓" },
  { req: "Report significance and confidence intervals", answered: "p < 0.001 with 95% CI for Nile Delta; p = 0.183 with 95% CI for Sahara", screen: "Trend Lab → Answer Cards", status: "✓" },
  { req: "Account for seasonality", answered: "Monthly data aggregated to annual means with ≥9 valid months coverage rule", screen: "Evidence Receipt → Filters", status: "✓" },
  { req: "Compare at least two regions", answered: "Nile Delta vs Sahara Interior, same variable and method", screen: "Compare / Region Duel", status: "✓" },
  { req: "Show data provenance", answered: "Full provenance record: source, variable, filters, method, script commit, config hash, library versions", screen: "Evidence Receipt → Provenance tabs", status: "✓" },
  { req: "Provide uncertainty quantification", answered: "95% CI on slope, autocorrelation analysis, missing data %, ESI grade", screen: "Trend Lab, ESI badge", status: "✓" },
  { req: "Explain methodology clearly", answered: "docs/methodology.md documents assumptions, limits, independent cross-check", screen: "Methodology link in Evidence Receipt", status: "✓" },
  { req: "Include AI-use disclosure", answered: "docs/ai-use-disclosure.md", screen: "Crosswalk, docs/", status: "✓" },
  { req: "Attribute all data sources", answered: "docs/sources-and-attribution.md", screen: "Evidence Receipt → Source", status: "✓" },
  { req: "No NASA logos or insignia", answered: "Original branding only; documented in AGENTS.md rule 6", screen: "All screens", status: "✓" },
  { req: "Work offline / no runtime NASA calls", answered: "Static Next.js export; all data cached in web/public/data/ JSONs", screen: "Architecture", status: "✓" },
  { req: "Accessible design (color contrast, keyboard)", answered: "4.5:1 contrast minimum, keyboard navigation, aria labels, reduced-motion support", screen: "All screens", status: "✓" },
  { req: "Respond to 'Be an Earth System Trend Detective'", answered: "Case-file investigation tool: Signal → Place → Evidence → Robustness → Contrast → Decision", screen: "App shell spine", status: "✓" },
  { req: "Evidence Strength Index (project-defined heuristic)", answered: "ESI computed from analysis.yaml rubric: years, missing %, significance, CI, robustness checks", screen: "Featured Finding, ESI badge", status: "✓" },
  { req: "Decision Lab with time-to-threshold scenarios", answered: "Time-to-threshold at slope and CI ends, scenario fan, all labeled 'Illustrative scenario'", screen: "Decision Lab", status: "⏳ P1" },
  { req: "Decision Brief export", answered: "Deterministic template from JSON, export Markdown", screen: "Brief", status: "⏳ P1" },
  { req: "Story Mode (optional)", answered: "90-second guided tour", screen: "Story Mode", status: "⏳ P1" },
];

export default function CrosswalkPage() {
  return (
    <div className="p-6 space-y-6">
      <header>
        <p className="text-xs uppercase tracking-widest text-muted">Crosswalk</p>
        <h1 className="text-2xl font-sans">Challenge Crosswalk</h1>
        <p className="text-sm text-muted mt-1">
          Each official challenge requirement (paraphrased) mapped to its answer in the app.
          Source: docs/crosswalk-source.md · docs/official/challenge description.md
        </p>
      </header>

      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-border text-left text-muted text-xs uppercase tracking-widest">
              <th className="py-2 pr-4 w-8">Status</th>
              <th className="py-2 pr-4">Requirement</th>
              <th className="py-2 pr-4">How it is answered</th>
              <th className="py-2">Where in the app</th>
            </tr>
          </thead>
          <tbody>
            {ITEMS.map((item, i) => (
              <tr key={i} className="border-b border-border/40">
                <td className="py-2 pr-4 font-mono">{item.status}</td>
                <td className="py-2 pr-4">{item.req}</td>
                <td className="py-2 pr-4 text-muted">{item.answered}</td>
                <td className="py-2 text-xs text-accent">{item.screen}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <footer className="text-xs text-muted border-t border-border pt-4">
        ✓ = fully delivered in P0 · ⏳ = P1 stretch goal · This page is auto-generated from docs/crosswalk-source.md
      </footer>
    </div>
  );
}
