// Significance badge. Pairs color with a symbol + word (SPEC design rule).

import type { RegionExportT } from "@/lib/schemas";

export function SignificanceBadge({ sig, alpha = 0.05 }:
  { sig: RegionExportT["significance"]; alpha?: number }) {
  if (!sig.significant_at_005) {
    return (
      <span
        className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full border border-border bg-surface-2 text-muted text-xs"
        data-testid="sig-badge"
        role="status"
      >
        <span aria-hidden="true">●</span>
        <span>Not detectable at α = {alpha}</span>
      </span>
    );
  }
  const color =
    sig.trend_direction === "increasing" ? "bg-positive/20 text-positive border-positive/40"
    : sig.trend_direction === "decreasing" ? "bg-negative/20 text-negative border-negative/40"
    : "bg-surface-2 text-muted border-border";
  const symbol =
    sig.trend_direction === "increasing" ? "▲"
    : sig.trend_direction === "decreasing" ? "▼" : "—";
  return (
    <span
      className={`inline-flex items-center gap-2 px-2.5 py-1 rounded-full border text-xs font-mono ${color}`}
      data-testid="sig-badge"
      role="status"
    >
      <span aria-hidden="true">{symbol}</span>
      <span>{sig.trend_direction} ({sig.p_display})</span>
    </span>
  );
}
