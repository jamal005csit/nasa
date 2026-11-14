// Top navigation bar: logo, planet switcher (Earth only for now), dataset chip,
// data-status dot. Design cues borrowed (visual only) from the pre-existing
// prototype under legacy_mockup/. Every number still reads from summary JSON.

"use client";

import type { SummaryT } from "@/lib/schemas";

export function TopNavigation({ summary }: { summary: SummaryT }) {
  const isReal = summary.source.kind === "NASA";
  const statusColor = isReal ? "bg-positive" : "bg-warn";
  const statusRing = isReal ? "dot-pulse-positive" : "dot-pulse-warn";
  const statusLabel = isReal ? "NASA data" : "DEMO data";

  return (
    <header className="h-16 border-b border-border bg-surface/90 backdrop-blur flex items-center px-6 gap-6 relative z-10">
      {/* Logo + brand */}
      <div className="flex items-center gap-3">
        <div
          aria-hidden="true"
          className="w-10 h-10 rounded-full grid place-items-center text-[10px] font-black text-white border-2 border-accent/60 shadow-[0_0_18px_rgba(56,215,255,0.35)]"
          style={{
            background:
              "radial-gradient(circle at 35% 35%, #60a5fa, #1d4ed8 55%, #020617)",
          }}
        >
          EN
        </div>
        <div>
          <h1 className="text-lg font-sans tracking-wide leading-tight">
            EARTH<span className="text-accent">//</span>NEXT
          </h1>
          <p className="text-[10px] text-muted uppercase tracking-widest">
            Signal · Place · Evidence · Robustness · Contrast · Decision
          </p>
        </div>
      </div>

      {/* Planet switcher — Earth only enabled for now. */}
      <nav aria-label="Planet" className="ml-6">
        <ul className="flex gap-1 text-sm">
          <li>
            <button
              aria-pressed="true"
              className="px-3 py-1.5 rounded-md border border-accent/60 bg-accent/10 text-accent"
            >
              🌍 Earth
            </button>
          </li>
          <li>
            <button
              aria-pressed="false"
              disabled
              title="Moon context arrives at Stage 10"
              className="px-3 py-1.5 rounded-md border border-border text-muted opacity-50 cursor-not-allowed"
            >
              Moon
            </button>
          </li>
          <li>
            <button
              aria-pressed="false"
              disabled
              title="Mars context arrives at Stage 10"
              className="px-3 py-1.5 rounded-md border border-border text-muted opacity-50 cursor-not-allowed"
            >
              Mars
            </button>
          </li>
        </ul>
      </nav>

      {/* Dataset chip + status dot */}
      <div className="ml-auto flex items-center gap-3 text-sm">
        <span
          className="pill-glass text-muted text-xs flex items-center gap-2"
          data-testid="dataset-chip"
        >
          <span className="text-accent">▣</span>
          {summary.dataset_short_name}&nbsp;v{summary.dataset_version} ·{" "}
          <span className="text-text">{summary.variable.toUpperCase()}</span>
        </span>
        <span
          className="pill-glass flex items-center gap-2"
          data-testid="status-pill"
        >
          <span
            aria-hidden="true"
            className={`w-2.5 h-2.5 rounded-full ${statusColor} ${statusRing}`}
            data-testid="status-dot"
          />
          <span className="text-xs text-muted" data-testid="status-label">
            {statusLabel}
          </span>
        </span>
      </div>
    </header>
  );
}
