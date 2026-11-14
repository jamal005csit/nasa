// Trend Lab — the four answer cards + time series + Evidence Receipt.
// Every number on screen is read from the RegionExport JSON.

"use client";

import { AnswerCard } from "./AnswerCard";
import { EvidenceReceipt } from "./EvidenceReceipt";
import { RegionPicker } from "./RegionPicker";
import { SignificanceBadge } from "./SignificanceBadge";
import { TimeSeriesChart } from "./TimeSeriesChart";
import { formatSlope } from "@/lib/format";
import { useSummary } from "@/lib/summary-context";
import { useRegion } from "@/lib/use-region";

export function TrendLab() {
  const sumState = useSummary();
  const regState = useRegion();

  if (sumState.kind !== "ready") return null;
  if (regState.kind === "loading") {
    return <div className="p-8 text-muted">Loading region…</div>;
  }
  if (regState.kind === "error") {
    return (
      <div className="p-8 text-negative">
        Could not load region JSON. <small>{regState.message}</small>
      </div>
    );
  }

  const region = regState.region;
  const { trend, significance, coverage } = region;
  const totalChange = trend.slope_per_year * (region.annual.years.length - 1);
  const [ciLoYrs, ciHiYrs] = [
    trend.slope_ci95[0] * (region.annual.years.length - 1),
    trend.slope_ci95[1] * (region.annual.years.length - 1),
  ];

  return (
    <div className="p-6 space-y-6">
      <header className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <p className="text-xs uppercase tracking-widest text-muted">Trend Lab</p>
          <h1 className="text-2xl font-sans">Case file: {region.region.name}</h1>
        </div>
        <div className="flex items-center gap-4">
          <RegionPicker summary={sumState.summary} />
          <EvidenceReceipt region={region} />
        </div>
      </header>

      {/* Four answer cards — SPEC §2 item 3 ordering */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        <AnswerCard
          testId="card-what"
          label="What"
          value={<span data-testid="card-what-value">{sumState.summary.variable.toUpperCase()}</span>}
          sub={<>Direction: <span data-testid="card-what-direction">{significance.trend_direction}</span></>}
          footer={<SignificanceBadge sig={significance} />}
        />

        <AnswerCard
          testId="card-where"
          label="Where"
          value={region.region.name}
          sub={
            <span className="font-mono text-xs">
              {region.region.bbox.min_lat}°–{region.region.bbox.max_lat}° N,{" "}
              {region.region.bbox.min_lon}°–{region.region.bbox.max_lon}° E
            </span>
          }
        />

        <AnswerCard
          testId="card-howmuch"
          label="How much"
          value={
            <span data-testid="card-howmuch-slope" className="font-mono tabular-nums">
              {formatSlope(trend.slope_per_year)}{" "}
              <span className="text-muted text-sm">{trend.units}</span>
            </span>
          }
          sub={
            <span data-testid="card-howmuch-ci" className="font-mono text-xs">
              95% CI {formatSlope(trend.slope_ci95[0])} to {formatSlope(trend.slope_ci95[1])}
            </span>
          }
          footer={
            <span className="text-xs text-muted" data-testid="card-howmuch-total">
              Total change over record: {formatSlope(totalChange)} NDVI
              <br />
              (95% CI {formatSlope(ciLoYrs)} to {formatSlope(ciHiYrs)})
            </span>
          }
        />

        <AnswerCard
          testId="card-significance"
          label="Is it significant?"
          value={
            <span className="font-mono tabular-nums" data-testid="card-sig-p">
              {significance.p_display}
            </span>
          }
          sub={
            <>
              Test: {significance.test}
              {significance.lag1_autocorr !== null ? (
                <> · lag-1 ρ = {significance.lag1_autocorr.toFixed(2)}</>
              ) : null}
            </>
          }
          footer={
            <span className="text-xs text-muted">
              {significance.significant_at_005
                ? `Below α = 0.05`
                : `No statistically detectable trend at α = 0.05 with this data.`}
              <br />
              Based on {coverage.n_valid_years}/{coverage.n_total_years} valid annual means
              ({coverage.missing_pct.toFixed(1)}% months missing).
            </span>
          }
        />
      </div>

      <section className="border border-border rounded-xl bg-surface/60 p-4">
        <TimeSeriesChart region={region} />
      </section>

      <footer className="text-xs text-muted border-t border-border pt-4">
        Numbers computed in <code>science/src/earthnext/trends.py</code>; inputs and
        methods recorded in the Evidence Receipt. Change the region in the URL:{" "}
        <code>?region=sahara_interior</code>.
      </footer>
    </div>
  );
}
