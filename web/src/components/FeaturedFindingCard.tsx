// The one featured finding, computed in Python, read from summary.json here.
// Design borrowed from the legacy_mockup regional-intelligence card; data
// still comes exclusively from summary.featured_finding.*.

import type { SummaryT } from "@/lib/schemas";
import { formatCI, formatP, formatSlope } from "@/lib/format";

export function FeaturedFindingCard({ summary }: { summary: SummaryT }) {
  const f = summary.featured_finding;
  const region = summary.regions.find((r) => r.slug === f.region_slug);

  const isPositive = f.slope_per_year > 0;
  const symbol = f.slope_per_year > 0 ? "▲" : f.slope_per_year < 0 ? "▼" : "—";
  const valueColor =
    f.slope_per_year > 0 ? "text-positive"
    : f.slope_per_year < 0 ? "text-negative" : "text-muted";

  return (
    <article
      aria-label="Featured finding"
      className="rounded-xl border border-border bg-surface/85 backdrop-blur p-5 w-96 shadow-2xl shadow-black/50"
      data-testid="featured-finding"
    >
      <header className="flex items-center justify-between mb-3">
        <span className="text-[10px] uppercase tracking-widest text-muted">
          ✦ Featured finding
        </span>
        <span className="text-[10px] uppercase tracking-widest text-warn">
          ⚠ Attention
        </span>
      </header>

      <h2 className="text-xl font-sans leading-tight">
        {region?.name ?? f.region_slug}
      </h2>
      <p className="text-xs text-muted mb-4">
        {region
          ? `Lat ${region.bbox.min_lat}–${region.bbox.max_lat}, Lon ${region.bbox.min_lon}–${region.bbox.max_lon}`
          : null}
      </p>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <MiniCard
          label="Slope / yr"
          value={
            <span className={`${valueColor} font-mono tabular-nums`} data-testid="featured-slope">
              <span aria-hidden="true" className="mr-1">{symbol}</span>
              {formatSlope(f.slope_per_year)}
            </span>
          }
          sub="NDVI units"
        />
        <MiniCard
          label="Significance"
          value={
            <span className="font-mono tabular-nums" data-testid="featured-p">
              {formatP(f.p)}
            </span>
          }
          sub={isPositive ? "trend detected" : f.slope_per_year < 0 ? "trend detected" : "no trend"}
        />
      </div>

      <div className="text-xs text-muted mb-3">
        <span data-testid="featured-ci">{formatCI(f.slope_ci95)}</span>
      </div>

      <p
        className="text-sm text-text/90 border-t border-border pt-3 leading-snug"
        data-testid="featured-sentence"
      >
        {f.sentence}
      </p>
    </article>
  );
}

function MiniCard({
  label, value, sub,
}: { label: string; value: React.ReactNode; sub: string }) {
  return (
    <div className="rounded-lg border border-border bg-bg/60 p-3">
      <div className="text-[10px] uppercase tracking-widest text-muted mb-1">{label}</div>
      <div className="text-lg leading-none">{value}</div>
      <div className="text-[10px] text-muted mt-1">{sub}</div>
    </div>
  );
}
