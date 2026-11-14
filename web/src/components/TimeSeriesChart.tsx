// ECharts time-series with trend line + 95% CI band.
// Also powers the "View as table" alternative view.

"use client";

import dynamic from "next/dynamic";
import { useMemo, useState } from "react";
import type { RegionExportT } from "@/lib/schemas";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

type Props = { region: RegionExportT };

export function TimeSeriesChart({ region }: Props) {
  const [view, setView] = useState<"chart" | "table">("chart");
  const option = useMemo(() => buildOption(region), [region]);

  return (
    <div data-testid="time-series">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-sm text-muted uppercase tracking-widest">
          Annual mean NDVI — {region.region.name}
        </h3>
        <div className="flex gap-1 text-xs">
          <ViewToggle current={view} value="chart" onClick={setView}>Chart</ViewToggle>
          <ViewToggle current={view} value="table" onClick={setView}>Table</ViewToggle>
        </div>
      </div>

      {view === "chart" ? (
        <div className="h-72">
          <ReactECharts option={option} notMerge style={{ height: "100%", width: "100%" }} />
        </div>
      ) : (
        <SeriesTable region={region} />
      )}
    </div>
  );
}

function buildOption(region: RegionExportT) {
  const { annual, trend } = region;
  const years = annual.years;
  const values = annual.values;
  const trendLine = years.map((y) => trend.intercept + trend.slope_per_year * (y - years[0]));
  const ciLo = years.map((y) => trend.intercept + trend.slope_ci95[0] * (y - years[0]));
  const ciHi = years.map((y) => trend.intercept + trend.slope_ci95[1] * (y - years[0]));
  const bandLo = ciLo;
  const bandWidth = ciHi.map((hi, i) => hi - ciLo[i]);

  return {
    textStyle: { color: "#EAF1FB" },
    grid: { left: 48, right: 24, top: 16, bottom: 32 },
    xAxis: { type: "category", data: years, axisLine: { lineStyle: { color: "#8FA3BF" } } },
    yAxis: {
      type: "value", scale: true,
      axisLine: { lineStyle: { color: "#8FA3BF" } },
      splitLine: { lineStyle: { color: "rgba(160,190,230,0.12)" } },
    },
    tooltip: { trigger: "axis", backgroundColor: "#0E1624", borderColor: "#1C2A44",
               textStyle: { color: "#EAF1FB" } },
    series: [
      // 95% CI band (stacked area trick)
      { name: "CI lo", type: "line", data: bandLo, stack: "ci", symbol: "none",
        lineStyle: { opacity: 0 }, areaStyle: { color: "transparent" } },
      { name: "95% CI", type: "line", data: bandWidth, stack: "ci", symbol: "none",
        lineStyle: { opacity: 0 }, areaStyle: { color: "rgba(56,215,255,0.18)" } },
      // Annual means
      { name: "Annual mean NDVI", type: "line", data: values,
        symbol: "circle", symbolSize: 6,
        itemStyle: { color: "#38D7FF" }, lineStyle: { color: "#38D7FF", width: 1.5 },
        connectNulls: false },
      // Theil-Sen trend line
      { name: "Theil-Sen trend", type: "line", data: trendLine,
        symbol: "none", lineStyle: { color: "#FFB547", width: 2, type: "dashed" } },
    ],
    legend: { show: false },
  };
}

function ViewToggle({
  current, value, onClick, children,
}: {
  current: "chart" | "table";
  value: "chart" | "table";
  onClick: (v: "chart" | "table") => void;
  children: React.ReactNode;
}) {
  const active = current === value;
  return (
    <button
      aria-pressed={active}
      onClick={() => onClick(value)}
      className={`px-2 py-1 rounded border ${
        active ? "border-accent text-accent bg-accent/10"
               : "border-border text-muted hover:text-text"
      }`}
    >
      {children}
    </button>
  );
}

function SeriesTable({ region }: Props) {
  return (
    <div className="max-h-72 overflow-auto text-xs font-mono">
      <table className="w-full">
        <thead className="sticky top-0 bg-surface text-muted border-b border-border">
          <tr>
            <th className="text-left py-1 px-2">Year</th>
            <th className="text-right py-1 px-2">Annual NDVI</th>
            <th className="text-right py-1 px-2">Valid months</th>
          </tr>
        </thead>
        <tbody>
          {region.annual.years.map((y, i) => (
            <tr key={y} className="border-b border-border/40">
              <td className="py-1 px-2">{y}</td>
              <td
                className="py-1 px-2 text-right tabular-nums"
                data-testid={`table-value-${y}`}
              >
                {region.annual.values[i] === null
                  ? <span className="text-muted">—</span>
                  : region.annual.values[i]?.toFixed(4)}
              </td>
              <td className="py-1 px-2 text-right">
                {region.annual.valid_months_per_year[i]}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
