// Signal Atlas — 2D map with the two study regions drawn as rectangles,
// coloured by the sign+magnitude of the regional slope, with diagonal hatching
// where the region's trend is NOT statistically detectable at α = 0.05.
//
// We render regions as whole blocks because we only compute regional means at
// Stage 6; per-cell trend grids are a Stage-7 extension.

"use client";

import { useEffect, useState } from "react";
import { loadRegion } from "@/lib/data";
import type { RegionExportT } from "@/lib/schemas";
import { formatP, formatSlope } from "@/lib/format";
import { useSummary } from "@/lib/summary-context";

type RegionBlob = { slug: string; name: string; region: RegionExportT };

export function SignalAtlas() {
  const sumState = useSummary();
  const [regions, setRegions] = useState<RegionBlob[] | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (sumState.kind !== "ready") return;
    let cancelled = false;
    (async () => {
      try {
        const loaded = await Promise.all(
          sumState.summary.regions.map(async (r) => ({
            slug: r.slug, name: r.name, region: await loadRegion(r.slug),
          })),
        );
        if (!cancelled) setRegions(loaded);
      } catch (e) {
        if (!cancelled) setErr(String(e));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [sumState]);

  if (sumState.kind === "loading") return <div className="p-8 text-muted">Loading summary…</div>;
  if (sumState.kind === "error") {
    return (
      <div className="p-8 text-negative">
        Summary load failed: <small>{sumState.message}</small>
      </div>
    );
  }
  if (err) {
    return (
      <div className="p-8 text-negative">
        Region load failed: <small>{err}</small>
      </div>
    );
  }
  if (!regions) return <div className="p-8 text-muted">Loading regions…</div>;

  const alpha = 0.05;
  const nTests = regions.length;
  const maxAbs = Math.max(
    ...regions.map((r) => Math.abs(r.region.trend.slope_per_year)),
    1e-9,
  );

  return (
    <div className="p-6 space-y-6">
      <header className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <p className="text-xs uppercase tracking-widest text-muted">Signal Atlas</p>
          <h1 className="text-2xl font-sans">
            NDVI trend per region, {sumState.summary.time_range[0].slice(0, 4)}–
            {sumState.summary.time_range[1].slice(0, 4)}
          </h1>
        </div>
        <div className="text-xs text-muted text-right">
          <div data-testid="atlas-tests-count">Tests: {nTests}</div>
          <div>Multiple-testing: Benjamini–Hochberg (q &lt; {alpha})</div>
          <div>α = {alpha}</div>
        </div>
      </header>

      <section className="rounded-xl border border-border bg-surface/60 p-4">
        <svg
          viewBox="-180 -90 360 180"
          className="w-full h-auto"
          role="img"
          aria-label="World map with study regions coloured by trend sign and magnitude"
          data-testid="atlas-svg"
        >
          <defs>
            <pattern id="not-significant" patternUnits="userSpaceOnUse" width="2" height="2" patternTransform="rotate(45)">
              <line x1="0" y1="0" x2="0" y2="2" stroke="#8FA3BF" strokeWidth="0.4" />
            </pattern>
          </defs>
          <rect x="-180" y="-90" width="360" height="180" fill="#0E1624" stroke="#1C2A44" />
          <line x1="-180" y1="0" x2="180" y2="0" stroke="#1C2A44" strokeDasharray="2 2" />
          <line x1="0" y1="-90" x2="0" y2="90" stroke="#1C2A44" strokeDasharray="2 2" />

          {regions.map((r) => {
            const b = r.region.region.bbox;
            const slope = r.region.trend.slope_per_year;
            const sig = r.region.significance.significant_at_005;
            const fill = slopeToColor(slope, maxAbs);
            return (
              <g key={r.slug} data-testid={`atlas-region-${r.slug}`}>
                <rect
                  x={b.min_lon}
                  y={-b.max_lat}
                  width={b.max_lon - b.min_lon}
                  height={b.max_lat - b.min_lat}
                  fill={fill}
                  stroke="#EAF1FB"
                  strokeWidth={0.4}
                />
                {!sig ? (
                  <rect
                    x={b.min_lon}
                    y={-b.max_lat}
                    width={b.max_lon - b.min_lon}
                    height={b.max_lat - b.min_lat}
                    fill="url(#not-significant)"
                    data-testid={`atlas-hatch-${r.slug}`}
                  />
                ) : null}
                <text
                  x={(b.min_lon + b.max_lon) / 2}
                  y={-((b.min_lat + b.max_lat) / 2) - 3}
                  fontSize={3}
                  fill="#EAF1FB"
                  textAnchor="middle"
                  style={{ fontFamily: "sans-serif" }}
                >
                  {r.name}
                </text>
              </g>
            );
          })}
        </svg>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {regions.map((r) => {
          const sig = r.region.significance;
          const slope = r.region.trend.slope_per_year;
          return (
            <article
              key={r.slug}
              className="rounded-xl border border-border bg-surface/60 p-4 flex flex-col gap-2"
              data-testid={`atlas-card-${r.slug}`}
            >
              <header className="flex items-center justify-between">
                <span className="text-sm">{r.name}</span>
                <span
                  className="font-mono text-xs tabular-nums"
                  data-testid={`atlas-card-slope-${r.slug}`}
                >
                  {formatSlope(slope)} NDVI/yr
                </span>
              </header>
              <div className="text-xs text-muted flex justify-between">
                <span>95% CI {formatSlope(r.region.trend.slope_ci95[0])} to {formatSlope(r.region.trend.slope_ci95[1])}</span>
                <span data-testid={`atlas-card-p-${r.slug}`}>{formatP(sig.p)}</span>
              </div>
              <div className="text-xs">
                {sig.significant_at_005
                  ? <span className="text-positive">Detectable at α = 0.05</span>
                  : <span className="text-muted">No statistically detectable trend at α = 0.05 with this data.</span>}
              </div>
            </article>
          );
        })}
      </section>

      <footer className="text-xs text-muted border-t border-border pt-4">
        Color encodes slope sign (mint ↑ / coral ↓) and magnitude relative to the
        strongest-trending region on screen. Hatched fill means the regional trend is
        not statistically detectable at α = 0.05 with this data — see Methodology.
      </footer>
    </div>
  );
}

function slopeToColor(slope: number, maxAbs: number): string {
  const magnitude = Math.min(Math.abs(slope) / maxAbs, 1);
  const alpha = (0.2 + 0.7 * magnitude).toFixed(2);
  if (slope > 0) return `rgba(94, 230, 176, ${alpha})`;   // positive — mint
  if (slope < 0) return `rgba(255, 122, 107, ${alpha})`;  // negative — coral
  return "rgba(143, 163, 191, 0.3)";                      // zero — muted
}
