// DEMO data banner. Rendered only when summary.source.kind === "DEMO".
// Disappears automatically the moment real AppEEARS data is dropped in.

import type { SummaryT } from "@/lib/schemas";

export function DemoBanner({ summary }: { summary: SummaryT }) {
  if (summary.source.kind !== "DEMO") return null;
  return (
    <div
      role="status"
      className="bg-warn text-bg px-4 py-2 text-sm flex items-center justify-center gap-3 border-b border-bg/20"
      data-testid="demo-banner"
    >
      <span aria-hidden="true">⚠</span>
      <span className="font-semibold tracking-wide">DEMO DATA</span>
      <span className="opacity-80">—</span>
      <span>{summary.source.note}</span>
    </div>
  );
}
