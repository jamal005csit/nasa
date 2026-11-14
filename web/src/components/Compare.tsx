// Compare / Region Duel — side-by-side region comparison with diff-of-slopes.
// SPEC §2 item 5. Template-driven, never invents claims.

"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { loadRegion } from "@/lib/data";
import type { RegionExportT } from "@/lib/schemas";
import { formatSlope, formatP } from "@/lib/format";
import { useSummary } from "@/lib/summary-context";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

export function Compare() {
  const sumState = useSummary();
  const [regA, setRegA] = useState<RegionExportT | null>(null);
  const [regB, setRegB] = useState<RegionExportT | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (sumState.kind !== "ready") return;
    let cancelled = false;
    (async () => {
      try {
        const a = await loadRegion("nile_delta");
        const b = await loadRegion("sahara_interior");
        if (!cancelled) { setRegA(a); setRegB(b); }
      } catch (e) {
        if (!cancelled) setErr(String(e));
      }
    })();
    return () => { cancelled = true; };
  }, [sumState]);

  if (sumState.kind === "loading") return <div className="p-8 text-muted">Loading…</div>;
  if (sumState.kind === "error") return <div className="p-8 text-negative">{sumState.message}</div>;
  if (err) return <div className="p-8 text-negative">{err}</div>;
  if (!regA || !regB) return <div className="p-8 text-muted">Loading regions…</div>;

  const slopeDiff = regA.trend.slope_per_year - regB.trend.slope_per_year;
  const isOpposite = (regA.trend.slope_per_year > 0) !== (regB.trend.slope_per_year > 0);
  const bothSignificant = regA.significance.significant_at_005 && regB.significance.significant_at_005;
  const oneSignificant = regA.significance.significant_at_005 !== regB.significance.significant_at_005;

  let verdict = "";
  if (bothSignificant && isOpposite) {
    verdict = `These two regions moved in opposite directions: ${regA.region.name} trended ${regA.significance.trend_direction} while ${regB.region.name} trended ${regB.significance.trend_direction}. The difference in slopes is ${formatSlope(slopeDiff)} NDVI/year.`;
  } else if (oneSignificant) {
    const sig = regA.significance.significant_at_005 ? regA : regB;
    const ns = regA.significance.significant_at_005 ? regB : regA;
    verdict = `${sig.region.name} shows a statistically detectable trend (${sig.significance.trend_direction}, ${sig.significance.p_display}), while ${ns.region.name} does not — no statistically detectable trend at α = 0.05 with this data.`;
  } else {
    verdict = `Neither region shows a statistically detectable trend at α = 0.05 with this data (${regA.region.name}: ${regA.significance.p_display}; ${regB.region.name}: ${regB.significance.p_display}).`;
  }

  return (
    <div className="p-6 space-y-6">
      <header>
        <p className="text-xs uppercase tracking-widest text-muted">Compare</p>
        <h1 className="text-2xl font-sans">Region Duel</h1>
        <p className="text-sm text-muted mt-1">{regA.region.name} vs {regB.region.name} · same variable, same method, same period</p>
      </header>

      <div className="rounded-xl border border-border bg-surface/60 p-4">
        <p className="text-sm" data-testid="compare-verdict">{verdict}</p>
        <p className="text-xs text-muted mt-2">
          Difference of slopes (Theil-Sen): {formatSlope(slopeDiff)} NDVI/year.
          Bootstrap CI not computed — interpret with caution. Non-overlapping individual CIs do not prove a difference.
        </p>
        <p className="text-xs text-warn mt-2">⚠ This comparison uses the same variable, method, and period. It does not imply causation or shared drivers.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RegionCard region={regA} label="Region A" />
        <RegionCard region={regB} label="Region B" />
      </div>

      <section className="rounded-xl border border-border bg-surface/60 p-4">
        <h3 className="text-sm text-muted uppercase tracking-widest mb-2">Side-by-side time series</h3>
        <div className="h-64">
          <ReactECharts option={chartOption(regA, regB)} notMerge style={{ height: "100%", width: "100%" }} />
        </div>
      </section>

      <footer className="text-xs text-muted border-t border-border pt-4">
        Want to explore one region in detail? Open the{" "}
        <Link href="/trend-lab?region=nile_delta" className="text-accent underline">Nile Delta</Link> or{" "}
        <Link href="/trend-lab?region=sahara_interior" className="text-accent underline">Sahara Interior</Link> case file.
      </footer>
    </div>
  );
}

function RegionCard({ region, label }: { region: RegionExportT; label: string }) {
  const { trend, significance, coverage, esi } = region;
  const dirColor = trend.slope_per_year > 0 ? "text-positive" : trend.slope_per_year < 0 ? "text-negative" : "text-muted";
  return (
    <article className="rounded-xl border border-border bg-surface/60 p-4 space-y-3" data-testid={`compare-card-${region.region.slug}`}>
      <header className="flex justify-between items-center">
        <span className="text-sm font-sans">{label}: {region.region.name}</span>
        {esi ? <span className="pill-glass text-xs" title={esi.label}>ESI {esi.grade}</span> : null}
      </header>
      <div className="grid grid-cols-2 gap-3">
        <Mini label="Slope / yr" value={<span className={`font-mono tabular-nums ${dirColor}`}>{formatSlope(trend.slope_per_year)}</span>} sub="NDVI units" />
        <Mini label="Significance" value={<span className="font-mono tabular-nums">{formatP(significance.p)}</span>} sub={`${significance.test} test`} />
      </div>
      <div className="text-xs text-muted">
        95% CI {formatSlope(trend.slope_ci95[0])} to {formatSlope(trend.slope_ci95[1])} · {coverage.n_valid_years}/{coverage.n_total_years} valid years
      </div>
      <div className="text-xs">
        {significance.significant_at_005
          ? <span className="text-positive">Detectable at α = 0.05</span>
          : <span className="text-muted">No statistically detectable trend at α = 0.05 with this data.</span>}
      </div>
    </article>
  );
}

function Mini({ label, value, sub }: { label: string; value: React.ReactNode; sub: string }) {
  return (
    <div className="rounded-lg border border-border bg-bg/60 p-3">
      <div className="text-[10px] uppercase tracking-widest text-muted mb-1">{label}</div>
      <div className="text-lg leading-none">{value}</div>
      <div className="text-[10px] text-muted mt-1">{sub}</div>
    </div>
  );
}

function chartOption(a: RegionExportT, b: RegionExportT) {
  const ya = a.annual.years;
  const yb = b.annual.years;
  return {
    textStyle: { color: "#EAF1FB" },
    grid: { left: 48, right: 24, top: 16, bottom: 32 },
    legend: { data: [a.region.name, b.region.name], textStyle: { color: "#8FA3BF" } },
    xAxis: { type: "category", data: ya, axisLine: { lineStyle: { color: "#8FA3BF" } } },
    yAxis: { type: "value", scale: true, axisLine: { lineStyle: { color: "#8FA3BF" } }, splitLine: { lineStyle: { color: "rgba(160,190,230,0.12)" } } },
    tooltip: { trigger: "axis", backgroundColor: "#0E1624", borderColor: "#1C2A44", textStyle: { color: "#EAF1FB" } },
    series: [
      { name: a.region.name, type: "line", data: a.annual.values, symbol: "circle", symbolSize: 5,
        itemStyle: { color: "#38D7FF" }, lineStyle: { color: "#38D7FF", width: 1.5 }, connectNulls: false },
      { name: b.region.name, type: "line", data: b.annual.values, symbol: "diamond", symbolSize: 5,
        itemStyle: { color: "#FFB547" }, lineStyle: { color: "#FFB547", width: 1.5 }, connectNulls: false },
    ],
  };
}
