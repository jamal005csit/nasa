// Region picker. Writes selection into URL state so a page reload keeps it.

"use client";

import type { SummaryT } from "@/lib/schemas";
import { useAppState } from "@/lib/url-state";

export function RegionPicker({ summary }: { summary: SummaryT }) {
  const [state, update] = useAppState();
  return (
    <label className="flex items-center gap-2 text-sm">
      <span className="text-muted uppercase text-xs tracking-widest">Region</span>
      <select
        value={state.region}
        onChange={(e) => update({ region: e.target.value })}
        className="bg-surface border border-border rounded px-2 py-1 text-text"
        data-testid="region-picker"
      >
        {summary.regions.map((r) => (
          <option key={r.slug} value={r.slug}>{r.name}</option>
        ))}
      </select>
    </label>
  );
}
